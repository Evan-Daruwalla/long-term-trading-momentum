"""Position monitoring + exit triggers (Phase 4).

For each open position, evaluate the exit rules and close any that fire.
If multiple rules fire, priority is:

  stop_loss  >  breakeven_stop  >  signal_reversal  >  trailing_stop
              >  take_profit    >  time_60d

Stop_loss wins because capital protection is paramount. breakeven_stop
sits next: once a trade has been profitable enough, we never let it
round-trip back into the red. signal_reversal beats trailing/take_profit
because an insider unloading is a stronger signal than hitting an
arbitrary gain target. trailing_stop sits above take_profit so we let
winners run past the hard TP threshold while still locking gains on a
material reversal from the peak.

The breakeven_stop and trailing_stop rules are configured per-profile
via `RiskProfile`; setting their trigger to 0 disables them (legacy
behavior).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta

from trading_bot.db import connect
from trading_bot.execution import market_data, survivorship
from trading_bot.execution.broker import BrokerSimulator


log = logging.getLogger(__name__)

STOP_LOSS_PCT = -15.0       # exit if drawdown reaches -15%
TAKE_PROFIT_PCT = 30.0      # exit if gain reaches +30%
TIME_EXIT_DAYS = 60         # forced exit after this many calendar days
SIGNAL_LOOKBACK_DAYS = 30   # window used to identify "original" buying insiders

# Loss-prevention extensions — overridden via profiles.use_profile().
# 0 = disabled (legacy behavior).
BREAKEVEN_TRIGGER_PCT = 0.0   # raise stop to entry once unrealized gain >= this %
TRAILING_TRIGGER_PCT = 0.0    # arm trailing stop once unrealized gain >= this %
TRAILING_DISTANCE_PCT = 0.0   # exit if close drops > this many pp below peak

# R11 (Tier 1.3): volatility-scaled stop.
# When VOL_STOP_ATR_MULT > 0, the stop for each position is sized by that
# stock's own realized volatility at entry: stop_pct = -mult * ATR%(20),
# clipped to [VOL_STOP_MIN_PCT, VOL_STOP_MAX_PCT]. Replaces the fixed
# STOP_LOSS_PCT for that position. Falls back to STOP_LOSS_PCT when ATR is
# unavailable (delisted/sparse history) so we never run with no stop.
VOL_STOP_ATR_MULT = 0.0
VOL_STOP_MIN_PCT = -5.0       # tightest allowed (low-vol names)
VOL_STOP_MAX_PCT = -30.0      # loosest allowed (high-vol names)

# R11 (Tier 1.3): regime-conditional time exit.
# In trending-up regimes (SPY > 200DMA) we let winners run longer; in
# downtrend / chop we exit faster. Multiplier of 1.0 = unchanged behavior.
TIME_EXIT_UPTREND_MULT = 1.0
TIME_EXIT_DOWNTREND_MULT = 1.0


@dataclass
class MonitorStats:
    checked: int = 0
    no_price: int = 0
    held: int = 0
    closed_stop_loss: int = 0
    closed_take_profit: int = 0
    closed_time_60d: int = 0
    closed_signal_reversal: int = 0
    closed_breakeven_stop: int = 0
    closed_trailing_stop: int = 0
    closed_delisted: int = 0


def monitor_positions(*, as_of: date | None = None) -> MonitorStats:
    """Evaluate every open position once. Closes any that hit an exit rule."""
    as_of = as_of or date.today()
    stats = MonitorStats()
    broker = BrokerSimulator()

    with connect() as conn:
        positions = conn.execute(
            "SELECT * FROM positions WHERE status='open'"
        ).fetchall()

    for p in positions:
        stats.checked += 1
        # Survivorship check first: if the ticker delisted on or before
        # today, force-close at last known price (or 0 — total wipeout) and
        # skip the normal exit evaluation. This corrects the bug where
        # delisted positions stayed open forever, never booking the loss.
        delist = survivorship.get_delisting(p["ticker"])
        if delist is not None and as_of >= delist[0]:
            last_price = delist[1] if delist[1] is not None else 0.0
            result = broker.close_position(
                position_id=p["id"], reason="delisted", as_of=as_of,
                force_fill_price=last_price,
            )
            if result is not None:
                stats.closed_delisted += 1
            continue
        reason = _evaluate_exit(dict(p), as_of)
        if reason is None:
            stats.held += 1
            continue
        result = broker.close_position(
            position_id=p["id"], reason=reason, as_of=as_of
        )

        if result is None:
            # close_position couldn't get a fill price; we'll retry next pass.
            stats.no_price += 1
            continue
        attr = f"closed_{reason}"
        setattr(stats, attr, getattr(stats, attr) + 1)

    return stats


def _evaluate_exit(position: dict, as_of: date) -> str | None:
    """Return the exit reason, or None if the position should still be held.

    Has the side effect of updating `peak_close_price` on the row when the
    current close prints a new high since entry. Peak is tracked off
    close-of-day prices to stay consistent with the rest of the monitor
    logic (no intraday data dependency).
    """
    position_id = position["id"]
    ticker = position["ticker"]
    entry_price = position["entry_price"]
    entry_date_str = position["entry_date"]
    peak = position.get("peak_close_price") or entry_price

    # `price_on_date` returns the close on `as_of`. If it can't (rate-limited
    # / sparse history), we used to fall back to `latest_price` — but in a
    # backtest that returns today's wall-clock price, silently injecting
    # look-ahead bias (we'd evaluate a 2022 stop using a 2026 quote). Treat
    # an unavailable price as "can't evaluate; hold" so the worst case is a
    # one-day delay rather than a correctness bug.
    current = market_data.price_on_date(ticker, as_of)

    # Update peak first so trailing logic sees today's high if applicable.
    # We persist the bump immediately; if the eval fires an exit, the row
    # gets a final UPDATE downstream and the extra column write is harmless.
    if current is not None and current > peak:
        peak = current
        with connect() as conn:
            conn.execute(
                "UPDATE positions SET peak_close_price=? WHERE id=?",
                (peak, position_id),
            )

    pct_change = None
    peak_pct = None
    if current is not None and entry_price > 0:
        pct_change = (current - entry_price) / entry_price * 100.0
        peak_pct = (peak - entry_price) / entry_price * 100.0

    # 1. Stop-loss (highest priority).
    # When VOL_STOP_ATR_MULT > 0, size the stop by entry-day ATR. ATR is a
    # function of pre-entry bars, so the value is stable forever — safe to
    # recompute on each evaluation pass.
    stop_pct = STOP_LOSS_PCT
    if VOL_STOP_ATR_MULT > 0:
        entry_d_for_atr = date.fromisoformat(entry_date_str)
        atr_frac = market_data.atr_pct(ticker, entry_d_for_atr, window=20)
        if atr_frac is not None:
            vol_stop = -VOL_STOP_ATR_MULT * atr_frac * 100.0
            stop_pct = max(VOL_STOP_MAX_PCT, min(VOL_STOP_MIN_PCT, vol_stop))
    if pct_change is not None and pct_change <= stop_pct:
        return "stop_loss"

    # 2. Breakeven stop: once we've printed >= breakeven_trigger gain, we
    # never let the position close back below entry. Disabled when
    # BREAKEVEN_TRIGGER_PCT == 0.
    if (
        BREAKEVEN_TRIGGER_PCT > 0
        and peak_pct is not None
        and pct_change is not None
        and peak_pct >= BREAKEVEN_TRIGGER_PCT
        and current is not None
        and current <= entry_price
    ):
        return "breakeven_stop"

    # 3. Signal reversal — any original buyer has since sold this ticker.
    if _has_signal_reversal(ticker, entry_date_str, as_of):
        return "signal_reversal"

    # 4. Trailing stop: once we've printed >= trailing_trigger gain, exit if
    # the close has fallen more than `distance` pp below the peak. Disabled
    # when TRAILING_TRIGGER_PCT == 0.
    if (
        TRAILING_TRIGGER_PCT > 0
        and peak_pct is not None
        and pct_change is not None
        and peak_pct >= TRAILING_TRIGGER_PCT
        and (peak_pct - pct_change) >= TRAILING_DISTANCE_PCT
    ):
        return "trailing_stop"

    # 5. Take-profit.
    if pct_change is not None and pct_change >= TAKE_PROFIT_PCT:
        return "take_profit"

    # 6. Time-based exit. Compute against `as_of` (backtest date) and
    # `entry_date` (the simulated trading day stamped at order time). Using
    # entry_time here would silently break in backtests — entry_time is
    # wall-clock when the row was inserted, which is the future relative to
    # historical `as_of`, so days_held would be negative.
    #
    # R11 (Tier 1.3): in trending-up regimes (SPY > 200DMA at as_of) the
    # horizon is stretched by TIME_EXIT_UPTREND_MULT; in downtrend / chop
    # it's compressed by TIME_EXIT_DOWNTREND_MULT. Both default to 1.0 so
    # legacy profiles see no change. Unknown regime (None) keeps the base
    # horizon.
    entry_d = date.fromisoformat(entry_date_str)
    days_held = (as_of - entry_d).days
    horizon = TIME_EXIT_DAYS
    if TIME_EXIT_UPTREND_MULT != 1.0 or TIME_EXIT_DOWNTREND_MULT != 1.0:
        regime_up = market_data.is_above_ma("SPY", as_of, window=200)
        if regime_up is True:
            horizon = int(TIME_EXIT_DAYS * TIME_EXIT_UPTREND_MULT)
        elif regime_up is False:
            horizon = int(TIME_EXIT_DAYS * TIME_EXIT_DOWNTREND_MULT)
    if days_held >= horizon:
        return "time_60d"

    return None


def _has_signal_reversal(ticker: str, entry_date_str: str, as_of: date) -> bool:
    """True if any insider who bought this ticker in the 30 days before
    entry has subsequently filed a sale visible by `as_of`."""
    entry_d = date.fromisoformat(entry_date_str)
    lookback_start = (entry_d - timedelta(days=SIGNAL_LOOKBACK_DAYS)).isoformat()
    entry_iso = entry_d.isoformat()
    as_of_iso = as_of.isoformat()

    with connect() as conn:
        buyer_ciks = [
            r["filer_cik"]
            for r in conn.execute(
                """
                SELECT DISTINCT filer_cik FROM signals
                WHERE ticker = ? AND transaction_code = 'P'
                  AND transaction_date BETWEEN ? AND ?
                  AND filer_cik IS NOT NULL
                """,
                (ticker, lookback_start, entry_iso),
            )
        ]
        if not buyer_ciks:
            return False

        placeholders = ",".join("?" * len(buyer_ciks))
        row = conn.execute(
            f"""
            SELECT 1 FROM signals
            WHERE ticker = ? AND transaction_code = 'S'
              AND filer_cik IN ({placeholders})
              AND transaction_date > ?
              AND filed_at <= ?
            LIMIT 1
            """,
            [ticker, *buyer_ciks, entry_iso, as_of_iso],
        ).fetchone()
    return row is not None
