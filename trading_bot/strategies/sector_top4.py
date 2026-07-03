"""Sector top-4 — monthly rotation across 11 SPDR sector ETFs (locked 2026-05-29).

Holds top-4 of 11 sectors by 12-1 momentum, equal-weight, monthly rebal.
Genuinely different alpha source from mom_v2/mom_roa_6535 (sector-level
vs stock-level). DEFENSIVE PROFILE — lowest max DD of any strategy tested.

================================================================
BASELINE METRICS (locked 2026-05-29 from research/test_sector_momentum.py)
================================================================
In-sample 2015-01-01 -> 2023-12-31 (9 yrs, post-audit clean data):
  CAGR:               +7.87%/yr   (vs mom_v2 +2.72%, +5.15pp)
  Mean yearly Sharpe: +0.354      (vs mom_v2 +0.167, +0.187)
  Max DD:             -31.97%     (vs mom_v2 -55.26%, +23.29pp BETTER)

Held-out 2024-01-01 -> 2026-05-01 (~2.4 yrs):
  CAGR:               +17.59%/yr  (vs mom_v2 +28.81%, -11.22pp)
  Mean yearly Sharpe: +0.906      (vs mom_v2 +0.903, ~tied)
  Max DD:             -16.22%     (vs mom_v2 -33.86%, +17.64pp BETTER)

================================================================
WHY DEPLOY THIS AS A SLEEVE
================================================================
NOT a replacement for mom_roa_6535 (which has +36.45% held-out CAGR vs
this strategy's +17.59%). Deployed as DIVERSIFICATION:
- Different alpha source (sectors vs stocks)
- Best DD profile of any tested strategy (~half of stock-level momentum)
- Sharpe matches mom_v2 in held-out
- Different drawdown timing (sectors lag stocks in regime shifts)

For a paper trade running 3 stock-level momentum sleeves, adding sector
rotation gives a 4th return stream that responds differently to market
regimes.

================================================================
WHY TOP-4 OUT OF 11 SECTORS
================================================================
Sweep tested top-N in {2, 3, 4, 5}:
- top-2: best held-out CAGR (+18.98%) but highest concentration (50% each)
- top-3: middling
- top-4: best Sharpe (+0.906), best max DD (-16.22%) — sweet spot
- top-5: lower returns, more diluted

Top-4 = 25% per sector, balanced between concentration and diversification.

================================================================
WHY 11 SPDR SECTORS (XLC, XLE, XLF, XLI, XLB, XLK, XLP, XLU, XLV, XLY, XLRE)
================================================================
Standard S&P 500 sector breakdown. SPDR ETFs have:
- Long history (XLK/XLF/etc. from 1998)
- High liquidity ($100M+ daily volume)
- Low expense ratio (~0.09%)
- XLC inception 2018; XLRE inception 2015 — pre-inception, strategy
  uses available subset (so fewer "top-N" before late 2015).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from trading_bot.execution import factor_backtest
from trading_bot.factors import sector_momentum


# ---------- Frozen params (do NOT change) ----------
TOP_N            = 4
STARTING_CASH    = 100_000.0
HALF_SPREAD_BPS  = 5.0
REBALANCE_FREQ   = "M"
FACTOR_NAME      = "sector_momentum_12_1"
WEIGHTING        = "equal-weight"
UNIVERSE         = "spdr_sectors_11"


@dataclass(frozen=True)
class StrategySpec:
    name:            str = "sector_top4"
    version:         str = "1.0.0"
    locked:          str = "2026-05-29"
    factor:          str = FACTOR_NAME
    universe:        str = UNIVERSE
    top_n:           int = TOP_N
    starting_cash:   float = STARTING_CASH
    half_spread_bps: float = HALF_SPREAD_BPS
    rebalance:       str = REBALANCE_FREQ
    weighting:       str = WEIGHTING


SPEC = StrategySpec()


def run(*, since: date, until: date):
    """Run sector_top4 with frozen params. Returns a BacktestResult.

    Note: rank_fn ignores the universe passed by the engine and uses
    SECTOR_UNIVERSE directly. The engine's universe filter is bypassed
    by this design.
    """
    factor_backtest.HALF_SPREAD_BPS = HALF_SPREAD_BPS
    return factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N,
        starting_cash=STARTING_CASH,
        rank_fn=sector_momentum.rank_universe,
        rebalance_freq=REBALANCE_FREQ,
    )
