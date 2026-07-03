"""Local broker simulator.

Implements the same minimal interface a real broker client (AlpacaBroker,
IBKRBroker, etc.) will when we swap one in. Two methods today:

  place_buy(ticker, dollar_amount, score, as_of) -> Position | None
  close_position(position_id, reason, as_of)     -> Position | None

Fills happen at the next-available open price after `as_of`. If no next-open
price is available (delisted, sparse data, weekend past the lookahead
window), the trade is skipped — we don't peek at later prices.

Each fill applies slippage + half-spread (against us) and the sell leg also
pays SEC/TAF fees. The bps are configured in `trading_bot.config`.
"""
from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass
from datetime import date, datetime, timezone

from trading_bot import config
from trading_bot.db import connect
from trading_bot.execution import market_data, portfolio
from trading_bot.scoring.scorer import TickerScore


log = logging.getLogger(__name__)


@dataclass
class Position:
    id: int
    ticker: str
    status: str
    qty: float
    entry_price: float
    entry_value: float
    entry_time: str
    sector: str | None
    exit_price: float | None = None
    exit_value: float | None = None
    exit_time: str | None = None
    exit_reason: str | None = None
    realized_pnl: float | None = None
    realized_pnl_pct: float | None = None


class BrokerSimulator:
    """Simulated broker. Same surface area we'll need from a real one."""

    def place_buy(
        self,
        *,
        ticker: str,
        dollar_amount: float,
        score: TickerScore,
        as_of: date,
    ) -> Position | None:
        raw_price = _resolve_fill_price(ticker, as_of)
        if raw_price is None or raw_price <= 0:
            log.warning("No fill price for %s at %s — skipping buy", ticker, as_of)
            return None

        # Cross the spread to the ask side. Half-spread is estimated from
        # that ticker's actual next-open intraday H-L range (Corwin-Schultz
        # convention) so each name pays a realistic spread for its real
        # liquidity profile rather than a hand-picked global constant.
        half_spread = _estimate_half_spread(ticker, as_of)
        price = raw_price * (1.0 + half_spread)

        # Whole-share quantity. Round down so we never overspend.
        qty = math.floor(dollar_amount / price)
        if qty <= 0:
            log.warning(
                "Dollar amount $%.2f below 1 share of %s @ $%.2f — skipping",
                dollar_amount, ticker, price,
            )
            return None

        # Liquidity guard: a $10K order on a name with 50K daily volume is
        # 20% of ADV — unrealistic to fill at the open without moving the
        # market. Skip rather than overstate ability to enter.
        if config.MAX_VOLUME_FRACTION:
            vol = market_data.next_open_volume(ticker, as_of)
            if vol and qty / vol > config.MAX_VOLUME_FRACTION:
                log.debug(
                    "Skip %s — qty=%d > %.0f%% of next-open volume %.0f",
                    ticker, qty, config.MAX_VOLUME_FRACTION * 100, vol,
                )
                return None

        actual_value = qty * price
        sec = market_data.sector(ticker)
        now = datetime.now(timezone.utc).isoformat()

        with connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO positions (
                  ticker, status, qty, entry_price, entry_value, entry_time, entry_date,
                  entry_score, entry_components, sector
                ) VALUES (?, 'open', ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ticker, qty, price, actual_value, now, as_of.isoformat(),
                    score.score, json.dumps(score.components), sec,
                ),
            )
            position_id = cur.lastrowid

        portfolio.adjust_cash(-actual_value)

        log.info(
            "BUY  %s qty=%d @ $%.2f = $%.2f (score=%d, sector=%s)",
            ticker, qty, price, actual_value, score.score, sec or "?",
        )
        return self._load(position_id)

    def close_position(
        self, *, position_id: int, reason: str, as_of: date,
        force_fill_price: float | None = None,
    ) -> Position | None:
        """Close an open position.

        `force_fill_price`: bypass next-open lookup and use this price as the
        raw fill. Used by the survivorship path to close delisted positions
        at their last known close (or 0.0 if unknown — total wipeout).
        """
        with connect() as conn:
            row = conn.execute(
                "SELECT * FROM positions WHERE id=? AND status='open'",
                (position_id,),
            ).fetchone()
        if row is None:
            log.warning("close_position: %d is not open", position_id)
            return None

        if force_fill_price is not None:
            raw_price = force_fill_price
        elif reason == "stop_loss":
            # Pessimistic stop-loss execution. Real stop-market orders
            # trigger intraday on the move down and fill at whatever the
            # bid is at trigger time — frequently below the stop level on
            # a gap-down. Without intraday data we approximate with
            # min(today's close, tomorrow's open). This captures most of
            # the gap-down risk a real fill would eat. Without this, the
            # backtest is materially optimistic about stops.
            today_close = market_data.price_on_date(row["ticker"], as_of)
            tomorrow_open = _resolve_fill_price(row["ticker"], as_of)
            candidates = [p for p in (today_close, tomorrow_open)
                          if p is not None and p > 0]
            raw_price = min(candidates) if candidates else None
        else:
            raw_price = _resolve_fill_price(row["ticker"], as_of)
        if raw_price is None or raw_price < 0:
            log.warning("No fill price for %s at %s — skipping sell", row["ticker"], as_of)
            return None

        # Sell leg: cross to bid side (half-spread estimated from intraday
        # H-L range; same convention as the buy side) and pay SEC + FINRA
        # TAF on the proceeds. SEC fee is the published 2.78 bps rate;
        # TAF is a fixed per-share charge.
        half_spread = _estimate_half_spread(row["ticker"], as_of)
        price = raw_price * (1.0 - half_spread)
        # Adjust qty for any splits between entry and exit. yfinance's raw
        # OHLC is unadjusted, so a 2:1 split halved `price` while we still
        # held twice the shares — multiply qty by the split ratio to get
        # the actual shares we'd sell. ratio=1.0 when no splits.
        entry_d = date.fromisoformat(row["entry_date"]) if row["entry_date"] else as_of
        ratio = market_data.split_ratio(row["ticker"], entry_d, as_of)
        qty = row["qty"] * ratio
        # Cash dividends earned during the holding period. Booked as part
        # of exit proceeds so it lands in realized_pnl. Use the post-split
        # qty for shares-on-record on each ex-date — close enough since
        # most splits and divs don't overlap in a short window.
        div_per_share = market_data.dividends_per_share(row["ticker"], entry_d, as_of)
        dividends_received = qty * div_per_share
        gross_value = qty * price
        sec_fee = gross_value * (config.SEC_FEE_BPS / 10000.0)
        taf_fee = qty * config.TAF_PER_SHARE
        exit_value = gross_value - sec_fee - taf_fee + dividends_received
        pnl = exit_value - row["entry_value"]
        pnl_pct = (pnl / row["entry_value"]) * 100.0 if row["entry_value"] else 0.0
        now = datetime.now(timezone.utc).isoformat()

        with connect() as conn:
            conn.execute(
                """
                UPDATE positions SET
                  status='closed', exit_price=?, exit_value=?, exit_time=?, exit_date=?,
                  exit_reason=?, realized_pnl=?, realized_pnl_pct=?,
                  split_ratio_at_exit=?, dividends_received=?
                WHERE id=?
                """,
                (price, exit_value, now, as_of.isoformat(), reason, pnl, pnl_pct,
                 ratio, dividends_received, position_id),
            )

        portfolio.adjust_cash(exit_value)

        log.info(
            "SELL %s qty=%.0f @ $%.2f = $%.2f (P&L $%.2f / %+.1f%%, reason=%s)",
            row["ticker"], qty, price, exit_value, pnl, pnl_pct, reason,
        )
        return self._load(position_id)

    def _load(self, position_id: int) -> Position:
        with connect() as conn:
            r = conn.execute("SELECT * FROM positions WHERE id=?", (position_id,)).fetchone()
        return Position(
            id=r["id"], ticker=r["ticker"], status=r["status"], qty=r["qty"],
            entry_price=r["entry_price"], entry_value=r["entry_value"],
            entry_time=r["entry_time"], sector=r["sector"],
            exit_price=r["exit_price"], exit_value=r["exit_value"],
            exit_time=r["exit_time"], exit_reason=r["exit_reason"],
            realized_pnl=r["realized_pnl"], realized_pnl_pct=r["realized_pnl_pct"],
        )


def _resolve_fill_price(ticker: str, as_of: date) -> float | None:
    """Next-day open after `as_of`, or None if unavailable.

    Earlier versions fell back to `market_data.latest_price()` here, but
    `latest_price` returns the most recent wall-clock close, which in a
    backtest is *future* data — fills under that fallback were peeking
    months ahead. If we can't find a next-day open within the lookahead
    window, the trade is skipped, mirroring the real-world reality that
    delisted / illiquid names sometimes can't be filled.
    """
    return market_data.next_open_price(ticker, as_of)


# Floor for the H-L estimator. Even very tight large-cap names pay some
# crossing cost, and on a freak quiet day H-L can collapse to near zero.
# 5 bps half-spread is the realistic minimum for any real fill.
_MIN_HALF_SPREAD = 0.0005


def _estimate_half_spread(ticker: str, as_of: date) -> float:
    """Half bid-ask spread estimated from the next-open day's H-L range.

    Returns a fraction (0.0050 = 50 bps). When range data isn't available,
    falls back to the floor — we never assume a free fill.
    """
    rng = market_data.next_open_range(ticker, as_of)
    if rng is None or rng <= 0:
        return _MIN_HALF_SPREAD
    return max(_MIN_HALF_SPREAD, config.SPREAD_RANGE_FACTOR * rng)
