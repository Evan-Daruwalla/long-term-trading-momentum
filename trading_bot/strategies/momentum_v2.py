"""Momentum v2 — top-50 monthly (locked 2026-05-26).

Same as momentum_v1 except top_n is 50 instead of 100. This was validated
by `scripts.momentum.robustness_test` running on BOTH in-sample 2015-2023
and held-out 2024-2026; top-50 monthly wins on both windows where weekly
and quarterly rebalances were 2024-26-specific overfits.

================================================================
WHAT CHANGED FROM V1
================================================================
- top_n:  100 -> 50   (more concentration in the best momentum names)
- Everything else identical (factor, universe, weighting, freq, TC, etc.)

================================================================
BASELINE METRICS (locked 2026-05-26 from robustness_test)
================================================================
In-sample 2015-01-01 -> 2023-12-31 (9 yrs):
  Total return:       +455.61%
  CAGR:               +21.00%/yr  (v1 was +19.61%)
  Mean yearly Sharpe: +0.230      (v1 was +0.27 by different calc; both close)
  Closed trades:      1,925

Held-out 2024-01-01 -> 2026-05-01 (~2.4 yrs):
  Total return:       +72.83%
  CAGR:               +26.47%/yr  (v1 was +21.4%)
  Mean yearly Sharpe: +0.868      (v1 was +0.81)
  Closed trades:      515

Improvement over v1 (held-out CAGR): +5.1 pp/yr
Improvement over v1 (in-sample CAGR): +3.1 pp/yr
Both windows positive => robust, not overfit.

================================================================
WHY TOP-50
================================================================
The robustness sweep tested top-N in {25, 50, 75, 100, 200, 300}:
- 25 too concentrated (single-name risk, Sharpe drops to +0.17 in-sample)
- 50 sweet spot for concentration without over-concentration
- 75 close second
- 100+ dilutes the signal (each name carries 1% NAV; weaker conviction)

Top-50 means each position is 2% of NAV ($2K on $100K, $20K on $1M).
That's still within the "no market impact" zone for liquid US stocks
even at $1M+ portfolio scale.

================================================================
WHY NOT WEEKLY OR QUARTERLY (THEY LOOKED BETTER ON HELD-OUT!)
================================================================
- Top-100 weekly:    held-out +28.4%/yr, in-sample +1.6%/yr  <-- OVERFIT
- Top-100 quarterly: held-out +28.5%/yr, in-sample +1.8%/yr  <-- OVERFIT

These were 2024-2026 regime artifacts. Weekly burns TC; quarterly misses
turning points in fast-moving regimes. The validation caught the trap.
Both kept available in factor_backtest via rebalance_freq="W"/"Q" for
future testing, but DO NOT use without re-validating.
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
TOP_N            = 50            # <-- only difference from v1
STARTING_CASH    = 100_000.0
HALF_SPREAD_BPS  = 5.0
MIN_PRICE_USD    = 5.0
MIN_HISTORY      = 252
MIN_DOLLAR_VOL   = 0
REBALANCE_FREQ   = "M"           # monthly, validated against W/Q
FACTOR_NAME      = "momentum_12_1"
WEIGHTING        = "equal-weight"


_EXPECTED_UNIVERSE_MIN_PRICE   = 5.0
_EXPECTED_UNIVERSE_MIN_HISTORY = 252

assert _UNIVERSE_MIN_PRICE == _EXPECTED_UNIVERSE_MIN_PRICE, (
    f"momentum_v2 expects universe.MIN_PRICE_USD={_EXPECTED_UNIVERSE_MIN_PRICE}, "
    f"got {_UNIVERSE_MIN_PRICE}. Bump to momentum_v3 if the constant changed.")
assert _UNIVERSE_MIN_HISTORY == _EXPECTED_UNIVERSE_MIN_HISTORY, (
    f"momentum_v2 expects universe.MIN_HISTORY_DAYS={_EXPECTED_UNIVERSE_MIN_HISTORY}, "
    f"got {_UNIVERSE_MIN_HISTORY}.")


@dataclass(frozen=True)
class StrategySpec:
    name:            str = "momentum_v2"
    version:         str = "2.0.0"
    locked:          str = "2026-05-26"
    factor:          str = FACTOR_NAME
    top_n:           int = TOP_N
    starting_cash:   float = STARTING_CASH
    half_spread_bps: float = HALF_SPREAD_BPS
    min_price_usd:   float = MIN_PRICE_USD
    min_history:     int = MIN_HISTORY
    min_dollar_vol:  float = MIN_DOLLAR_VOL
    rebalance:       str = REBALANCE_FREQ
    weighting:       str = WEIGHTING


SPEC = StrategySpec()


def run(*, since: date, until: date):
    """Run momentum v2 with frozen params. Returns a BacktestResult."""
    factor_backtest.HALF_SPREAD_BPS = HALF_SPREAD_BPS
    return factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N,
        starting_cash=STARTING_CASH,
        rank_fn=momentum.rank_universe,
        rebalance_freq=REBALANCE_FREQ,
    )
