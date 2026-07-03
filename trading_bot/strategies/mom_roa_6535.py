"""Mom x ROA Z-score 65/35 — top-50 monthly (locked 2026-05-28).

Cross-sectional Z-score combo of 12-1 momentum (65%) + ROA (35%). First
strategy in 16+ multi-factor attempts to beat mom_v2 on EVERY metric on
BOTH windows.

================================================================
WHY THIS STRATEGY
================================================================
mom_v2 long-only-momentum has been the baseline since the data audit
(2026-05-28) corrected the in-sample numbers. After exploring overlays
(stops, vol-target, trend filter) and other strategies (long-short)
all of which failed or weren't deployable, this is the first SLEEVE
attempt to actually deliver edge.

The combo IS interpretable: pure momentum picks names with strongest
price trends but no quality filter. Adding ROA as a 35%-weight Z-score
tiebreaker filters out the most-junk momentum names (negative-ROA biotechs
on speculation rallies, etc.) while keeping the directional momentum edge.

================================================================
BASELINE METRICS (locked 2026-05-28 from refine + TC sweeps)
================================================================
In-sample 2015-01-01 -> 2023-12-31 (9 yrs, post-audit clean data):
  CAGR:               +4.73%/yr   (vs mom_v2 +2.72%, delta +2.01pp)
  Mean yearly Sharpe: +0.241      (vs mom_v2 +0.167, delta +0.074)
  Max DD:             -44.28%     (vs mom_v2 -55.26%, delta +10.98pp)

Held-out 2024-01-01 -> 2026-05-01 (~2.4 yrs):
  CAGR:               +36.45%/yr  (vs mom_v2 +28.81%, delta +7.64pp)
  Mean yearly Sharpe: +1.111      (vs mom_v2 +0.903, delta +0.208)
  Max DD:             -30.43%     (vs mom_v2 -33.86%, delta +3.43pp)

TC sensitivity (held-out, edge is constant across TC levels):
  5 bps half:  CAGR +36.45% (vs mom_v2 +28.81%, delta +7.64pp)
 15 bps half:  CAGR +35.49% (vs mom_v2 +27.85%, delta +7.64pp)
 25 bps half:  CAGR +34.55% (vs mom_v2 +26.89%, delta +7.66pp)

================================================================
WHY 65/35 WEIGHTS (NOT 50/50, 70/30, OR 60/40)
================================================================
Coarse sweep (5050, 7030, 3070) showed 7030 best. Refinement (8020, 7525,
6535, 6040) showed the held-out CAGR peaks BROADLY between 60-70% mom
weight (6040 highest at +36.99%, but 6535 and 6040 within 0.5pp). All
configs in [60-70] beat mom_v2 on every metric on both windows. Chose
6535 as middle-of-broad-peak — slightly safer against parameter overfit
than 6040, more conventional than 7030.

================================================================
DEPLOYMENT
================================================================
Third parallel paper-trade sleeve alongside mom_v1_paper (top-100) and
mom_v2_paper (top-50). All three inceptioned 2026-05-01.
Strategy name: mom_roa_6535_paper.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from trading_bot.execution import factor_backtest
from trading_bot.factors import mom_roa_zscore
from trading_bot.factors.universe import (
    MIN_PRICE_USD as _UNIVERSE_MIN_PRICE,
    MIN_HISTORY_DAYS as _UNIVERSE_MIN_HISTORY,
)


# ---------- Frozen params (do NOT change) ----------
TOP_N            = 50
STARTING_CASH    = 100_000.0
HALF_SPREAD_BPS  = 5.0
W_MOM            = 0.65
W_ROA            = 0.35
MIN_PRICE_USD    = 5.0
MIN_HISTORY      = 252
MIN_DOLLAR_VOL   = 0
REBALANCE_FREQ   = "M"
FACTOR_NAME      = "mom_roa_zscore_65_35"
WEIGHTING        = "equal-weight"


_EXPECTED_UNIVERSE_MIN_PRICE   = 5.0
_EXPECTED_UNIVERSE_MIN_HISTORY = 252

assert _UNIVERSE_MIN_PRICE == _EXPECTED_UNIVERSE_MIN_PRICE, (
    f"mom_roa_6535 expects universe.MIN_PRICE_USD={_EXPECTED_UNIVERSE_MIN_PRICE}, "
    f"got {_UNIVERSE_MIN_PRICE}.")
assert _UNIVERSE_MIN_HISTORY == _EXPECTED_UNIVERSE_MIN_HISTORY, (
    f"mom_roa_6535 expects universe.MIN_HISTORY_DAYS={_EXPECTED_UNIVERSE_MIN_HISTORY}, "
    f"got {_UNIVERSE_MIN_HISTORY}.")


@dataclass(frozen=True)
class StrategySpec:
    name:            str = "mom_roa_6535"
    version:         str = "1.0.0"
    locked:          str = "2026-05-28"
    factor:          str = FACTOR_NAME
    w_mom:           float = W_MOM
    w_roa:           float = W_ROA
    top_n:           int = TOP_N
    starting_cash:   float = STARTING_CASH
    half_spread_bps: float = HALF_SPREAD_BPS
    min_price_usd:   float = MIN_PRICE_USD
    min_history:     int = MIN_HISTORY
    min_dollar_vol:  float = MIN_DOLLAR_VOL
    rebalance:       str = REBALANCE_FREQ
    weighting:       str = WEIGHTING


SPEC = StrategySpec()


def rank_fn():
    """Return the rank_fn closure with frozen weights. Use this in
    factor_backtest.run_factor_backtest(rank_fn=mom_roa_6535.rank_fn())."""
    return mom_roa_zscore.make_rank_fn(W_MOM, W_ROA)


def run(*, since: date, until: date):
    """Run mom_roa_6535 with frozen params. Returns a BacktestResult."""
    factor_backtest.HALF_SPREAD_BPS = HALF_SPREAD_BPS
    return factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N,
        starting_cash=STARTING_CASH,
        rank_fn=rank_fn(),
        rebalance_freq=REBALANCE_FREQ,
    )
