"""Momentum v1 — frozen baseline strategy (locked 2026-05-26).

This is the canonical, working momentum-solo strategy. Frozen for
regression-testing and as the comparison baseline for any future
factor-combination experiments. Do NOT modify parameters here — if you
want to test a variant, copy this to `momentum_v2.py` and bump the
version.

================================================================
SPEC
================================================================
- Factor:          12-1 month momentum (Jegadeesh-Titman academic standard)
                   ret = close[t-21] / close[t-252] - 1
- Universe:        cached US-listed tickers with
                     - close on rebalance date >= $5
                     - >=252 prior trading-day closes
                     - close on day-252-ago >= $5 (anti reverse-split)
                     - NO dollar-volume filter (filter destroyed alpha — see
                       sleeves_verdict.md)
- Selection:       top 100 by momentum score
- Weighting:       equal-weight (1/100 of NAV per position)
- Sizing:          fractional shares (qty = dollar_target / fill_price)
- Rebalance:       monthly, first trading day of month
- Fill model:      close ± 5 bps half-spread (10 bps round-trip)
- Starting cash:   $100,000

================================================================
BASELINE METRICS (frozen 2026-05-26)
================================================================
In-sample 2015-01-01 -> 2023-12-31 (9 yrs):
  Total return:           +398.23%
  CAGR:                   +19.61%/yr
  Closed trades:          3,408
  Mean yearly Sharpe:     +0.27
  Alpha vs SPY (cap-w):   +7.8%/yr
  Alpha vs RSP (eq-w):    +9.8%/yr
  Alpha vs IWM (small):   +12.1%/yr
  (Caveat: 2017 alone was +381% return; without 2017 alpha is much smaller.
   Strategy has lumpy outlier-driven returns.)

Held-out 2024-01-01 -> 2026-05-01 (~2.4 yrs):
  Total return:           +53.20%
  CAGR:                   +19.5%/yr
  Closed trades:          910
  Mean yearly Sharpe:     +0.72
  Alpha vs SPY:           -2.0%/yr (mega-cap era)
  Alpha vs RSP:           +4.0%/yr (real, vs eq-weight benchmark)
  Alpha vs IWM:           +1.9%/yr

Transaction-cost sensitivity (held-out):
  5  bps half-spread: +54.5% total (baseline)
  15 bps:             +52.3% (realistic retail broker)
  30 bps:             +48.9% (pessimistic small-cap)
  → alpha vs RSP survives even at 30bps: +5.4%/yr

================================================================
USAGE
================================================================
    from trading_bot.strategies import momentum_v1
    result = momentum_v1.run(since=date(2024,1,1), until=date(2026,5,1))
    print(f"Return: {result.mtm_total_pnl_pct:+.2f}%")

================================================================
WHY FROZEN
================================================================
Three multi-factor experiments (naive composite, volume-gated sleeves,
stdev-floor sleeves) all underperformed this baseline. A fourth
(mom+quality with yfinance proxy) is the only one that improved Sharpe
(+8%) but at a -8% return cost. Until a strategy demonstrably beats
v1 on both held-out total return AND Sharpe, this is THE strategy.

Don't break it by tuning. Don't combine it with another factor unless
the combination has been independently validated on a separate held-out.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum
from trading_bot.factors.universe import (
    MIN_PRICE_USD as _UNIVERSE_MIN_PRICE,
    MIN_HISTORY_DAYS as _UNIVERSE_MIN_HISTORY,
)


# ---------- Frozen params (do NOT change) ----------
TOP_N           = 100
STARTING_CASH   = 100_000.0
HALF_SPREAD_BPS = 5.0
MIN_PRICE_USD   = 5.0
MIN_HISTORY     = 252
MIN_DOLLAR_VOL  = 0          # opt-OUT of volume filter (it destroyed momentum)
FACTOR_NAME     = "momentum_12_1"
REBALANCE       = "monthly"
WEIGHTING       = "equal-weight"


# Sanity assertions: if the underlying defaults change out from under us,
# fail loudly rather than silently producing different results.
_EXPECTED_UNIVERSE_MIN_PRICE   = 5.0
_EXPECTED_UNIVERSE_MIN_HISTORY = 252
_EXPECTED_HALF_SPREAD_BPS      = 5.0

assert _UNIVERSE_MIN_PRICE == _EXPECTED_UNIVERSE_MIN_PRICE, (
    f"momentum_v1 expects universe.MIN_PRICE_USD={_EXPECTED_UNIVERSE_MIN_PRICE}, "
    f"got {_UNIVERSE_MIN_PRICE}. Either revert the universe constant, or "
    f"bump to momentum_v2 with the new value.")
assert _UNIVERSE_MIN_HISTORY == _EXPECTED_UNIVERSE_MIN_HISTORY, (
    f"momentum_v1 expects universe.MIN_HISTORY_DAYS={_EXPECTED_UNIVERSE_MIN_HISTORY}, "
    f"got {_UNIVERSE_MIN_HISTORY}.")


@dataclass(frozen=True)
class StrategySpec:
    """Immutable snapshot of every parameter that affects results.
    Useful for logging into result files so you know later exactly which
    config produced a given equity curve."""
    name:            str = "momentum_v1"
    version:         str = "1.0.0"
    locked:          str = "2026-05-26"
    factor:          str = FACTOR_NAME
    top_n:           int = TOP_N
    starting_cash:   float = STARTING_CASH
    half_spread_bps: float = HALF_SPREAD_BPS
    min_price_usd:   float = MIN_PRICE_USD
    min_history:     int = MIN_HISTORY
    min_dollar_vol:  float = MIN_DOLLAR_VOL
    rebalance:       str = REBALANCE
    weighting:       str = WEIGHTING


SPEC = StrategySpec()


def run(*, since: date, until: date):
    """Run momentum v1 with frozen params. Returns a BacktestResult.

    Sets factor_backtest.HALF_SPREAD_BPS explicitly so concurrent code
    using different bps doesn't leak in.
    """
    factor_backtest.HALF_SPREAD_BPS = HALF_SPREAD_BPS
    return factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N,
        starting_cash=STARTING_CASH,
        rank_fn=momentum.rank_universe,
    )
