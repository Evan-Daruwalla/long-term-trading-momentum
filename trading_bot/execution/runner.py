"""Trade execution runner: turn tradeable scores into broker orders.

Per-ticker rules enforced here:
  * Skip if we already have an open position in the ticker.
  * Skip if cash on hand can't cover the position.
  * Skip if the trade would push the ticker's sector over the 20% cap.
  * Skip if the price is below its N-day moving average (trend filter,
    config.TREND_FILTER_ENABLED).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta

from trading_bot import config
from trading_bot.execution import market_data, portfolio, survivorship
from trading_bot.execution.broker import BrokerSimulator
from trading_bot.scoring import scorer


log = logging.getLogger(__name__)

SECTOR_CAP_PCT = 20.0  # never more than 20% of total portfolio in one sector

# Regime gate: when SPY < its 200-day moving average, skip all new entries.
# Existing positions still get their normal stop/take-profit treatment.
# Hypothesis: across R14-R16 the strategy lost money 2021-2023 (small-cap
# bear) and made money 2024+ (uptrending market). Gating entries on the
# market regime should preserve the working post-2024 behavior while
# avoiding the systematic drawdown in hostile regimes.
# Defaults permissive on data miss — yfinance flakiness shouldn't quietly
# block a year of trading.
REGIME_GATE_ENABLED = True
REGIME_TICKER = "SPY"
REGIME_MA_WINDOW = 200


@dataclass
class ExecutionStats:
    considered: int = 0
    placed: int = 0
    skipped_already_open: int = 0
    skipped_no_cash: int = 0
    skipped_sector_cap: int = 0
    skipped_trend_filter: int = 0
    skipped_liquidity: int = 0
    skipped_no_price: int = 0
    skipped_delisting_imminent: int = 0
    skipped_regime: int = 0  # whole-day skip when market regime hostile
    errors: int = 0


def execute_pending(
    *, as_of: date | None = None, window_days: int = 30
) -> ExecutionStats:
    """Score signals as of `as_of`, then place buys for all tradeable tickers."""
    as_of = as_of or date.today()
    stats = ExecutionStats()

    scores = scorer.tradeable(scorer.score_all(window_days=window_days, as_of=as_of))
    stats.considered = len(scores)
    if not scores:
        return stats

    # Regime gate: short-circuit the whole day's entries when the broad
    # market is below its long MA. Exits are unaffected (they're handled
    # by monitor.check_exits, not here).
    if REGIME_GATE_ENABLED:
        spy_above = market_data.is_above_ma(REGIME_TICKER, as_of, window=REGIME_MA_WINDOW)
        if spy_above is False:
            log.debug("Regime gate: SPY < %d-DMA on %s, skipping %d entries",
                      REGIME_MA_WINDOW, as_of, len(scores))
            stats.skipped_regime = len(scores)
            return stats

    pf = portfolio.get_portfolio()
    sector_exposure = portfolio.open_position_value_by_sector()
    broker = BrokerSimulator()

    for s in scores:
        if portfolio.has_open_position(s.ticker):
            stats.skipped_already_open += 1
            continue

        # Survivorship: skip entries on tickers we know will delist within
        # 30 days. We have no edge on a stub-period sale and the broker
        # would force-close it almost immediately anyway. (When delistings
        # haven't been ingested, get_delisting returns None and this is a
        # no-op.)
        delist = survivorship.get_delisting(s.ticker)
        if delist is not None and delist[0] - as_of <= timedelta(days=30):
            stats.skipped_delisting_imminent += 1
            continue

        # Position dollar size = position_size_pct of total portfolio value.
        dollar_amount = pf.total_value * (s.position_size_pct / 100.0)

        if dollar_amount > pf.cash:
            log.debug(
                "Skip %s — need $%.0f, only $%.0f cash",
                s.ticker, dollar_amount, pf.cash,
            )
            stats.skipped_no_cash += 1
            continue

        sec = market_data.sector(s.ticker) or "UNKNOWN"
        sector_after = sector_exposure.get(sec, 0.0) + dollar_amount
        sector_cap_dollars = pf.total_value * (SECTOR_CAP_PCT / 100.0)
        if sector_after > sector_cap_dollars:
            log.debug(
                "Skip %s — sector %s would hit $%.0f, cap $%.0f",
                s.ticker, sec, sector_after, sector_cap_dollars,
            )
            stats.skipped_sector_cap += 1
            continue

        # Trend filter: only enter if the entry day's close is above its
        # N-day moving average. None (insufficient history / transient
        # error) is treated as "pass" so we don't silently exclude valid
        # signals on yfinance flakiness.
        if config.TREND_FILTER_ENABLED:
            above = market_data.is_above_ma(
                s.ticker, as_of, window=config.TREND_FILTER_WINDOW
            )
            if above is False:
                log.debug(
                    "Skip %s — below %d-day MA at %s",
                    s.ticker, config.TREND_FILTER_WINDOW, as_of,
                )
                stats.skipped_trend_filter += 1
                continue

        if config.LIQUIDITY_FILTER_ENABLED:
            op = market_data.next_open_price(s.ticker, as_of)
            vol = market_data.next_open_volume(s.ticker, as_of)
            if op and vol and (op * vol) < config.LIQUIDITY_MIN_DOLLAR_VOLUME:
                log.debug(
                    "Skip %s — dollar volume $%.1fM < $%.1fM floor",
                    s.ticker, op*vol/1e6,
                    config.LIQUIDITY_MIN_DOLLAR_VOLUME/1e6,
                )
                stats.skipped_liquidity += 1
                continue

        position = broker.place_buy(
            ticker=s.ticker,
            dollar_amount=dollar_amount,
            score=s,
            as_of=as_of,
        )
        if position is None:
            stats.skipped_no_price += 1
            continue

        # Update local view of cash + sector exposure for next iteration so
        # the second buy in this run sees the first buy's effect.
        pf = portfolio.get_portfolio()
        sector_exposure[sec] = sector_after
        stats.placed += 1

    return stats
