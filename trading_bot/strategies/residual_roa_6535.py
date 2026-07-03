"""Residual-momentum x ROA Z-score 65/35 — top-50 monthly (locked 2026-06-09).

The SECOND strategy (after mom_roa_6535) to clear the project's deployment
bar: beat mom_v2 on BOTH windows on return AND Sharpe. Discovered via the
2026-06-09 algo-research sweep (candidate #3 of docs/research_2026-06-09).

================================================================
WHY THIS STRATEGY
================================================================
Standard 12-1 momentum (mom_v2) ranks on TOTAL return, which loads on market
beta — the beta exposure that drives "momentum crashes" (Daniel & Moskowitz
2016). Residual momentum (Blitz-Huij-Martens 2011) strips the market component
out first (regress stock daily returns on SPY, rank by the standardized
idiosyncratic drift alpha/resid_sd), keeping only stock-specific trend. We then
combine it 65/35 with ROA (same recipe that made mom_roa_6535 work) to prune
junk.

The result is materially more crash-resistant than mom_roa_6535 (much smaller
drawdowns on both windows) at a small cost to held-out CAGR.

================================================================
VALIDATED METRICS (live run 2026-06-09, post-BKGM-fix clean data, 5 bps)
================================================================
In-sample 2015-01-01 -> 2023-12-31 (9 yrs):
  CAGR:               +8.86%/yr   (mom_v2 +3.51, champion mom_roa_6535 +5.07)
  Mean yearly Sharpe: +0.419      (mom_v2 +0.206, mom_roa_6535 +0.254)
  Max DD:             -37.62%     (mom_v2 -55.25, mom_roa_6535 -43.55)
  -> beats BOTH mom_v2 and the champion on every in-sample metric.

Held-out 2024-01-01 -> 2026-05-01 (~2.4 yrs):
  CAGR:               +30.84%/yr  (mom_v2 +27.98, champion mom_roa_6535 +36.45)
  Mean yearly Sharpe: +1.065      (mom_v2 +0.887, mom_roa_6535 +1.111)
  Max DD:             -20.28%     (mom_v2 -33.80, mom_roa_6535 -30.43)
  -> beats mom_v2 on return AND Sharpe AND DD. Vs the champion: lower CAGR
     (-5.61pp) and ~tied Sharpe (-0.046), but MUCH better DD (+10.15pp).

POSITIONING: this is NOT a replacement for mom_roa_6535 (champion still wins
held-out CAGR). It is a lower-drawdown sibling — deployed as a parallel sleeve
to gather forward evidence on whether the residual construction's crash
resistance holds out of sample.

CAVEATS (honest):
  - The residual signal = regression INTERCEPT (alpha) / residual stdev, an
    information-ratio form. Market proxy = SPY. Near-market index clones are
    excluded (residual vol floor 1e-3) to avoid spurious top ranks.
  - No TC sweep yet (deployed at 5 bps like its siblings). Residual momentum
    may turn over faster than plain momentum; watch realized slippage.
  - Single live run; no walk-forward. Forward paper evidence is the real test.

================================================================
DEPLOYMENT
================================================================
Parallel paper-trade sleeve. Strategy name: residual_roa_6535_paper.
Inception 2026-05-01 (backdated 2026-06-09 to match mom_roa_6535's start +
elapsed time for a clean head-to-head; deterministic on cached prices, same
method the original sleeves were seeded by). Rebalanced 2026-05-01 + 2026-06-03,
daily MTM backfilled 5/01->6/09. Forward live data accrues from here.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from trading_bot.execution import factor_backtest
from trading_bot.factors import residual_momentum, roa, zcombo
from trading_bot.factors.universe import (
    MIN_PRICE_USD as _UNIVERSE_MIN_PRICE,
    MIN_HISTORY_DAYS as _UNIVERSE_MIN_HISTORY,
)


# ---------- Frozen params (do NOT change) ----------
TOP_N            = 50
STARTING_CASH    = 100_000.0
HALF_SPREAD_BPS  = 5.0
W_RESID          = 0.65
W_ROA            = 0.35
MIN_PRICE_USD    = 5.0
MIN_HISTORY      = 252
REBALANCE_FREQ   = "M"
FACTOR_NAME      = "residual_roa_zscore_65_35"
WEIGHTING        = "equal-weight"

_EXPECTED_UNIVERSE_MIN_PRICE   = 5.0
_EXPECTED_UNIVERSE_MIN_HISTORY = 252

assert _UNIVERSE_MIN_PRICE == _EXPECTED_UNIVERSE_MIN_PRICE, (
    f"residual_roa_6535 expects universe.MIN_PRICE_USD={_EXPECTED_UNIVERSE_MIN_PRICE}, "
    f"got {_UNIVERSE_MIN_PRICE}.")
assert _UNIVERSE_MIN_HISTORY == _EXPECTED_UNIVERSE_MIN_HISTORY, (
    f"residual_roa_6535 expects universe.MIN_HISTORY_DAYS={_EXPECTED_UNIVERSE_MIN_HISTORY}, "
    f"got {_UNIVERSE_MIN_HISTORY}.")


@dataclass(frozen=True)
class StrategySpec:
    name:            str = "residual_roa_6535"
    version:         str = "1.0.0"
    locked:          str = "2026-06-09"
    factor:          str = FACTOR_NAME
    w_resid:         float = W_RESID
    w_roa:           float = W_ROA
    top_n:           int = TOP_N
    starting_cash:   float = STARTING_CASH
    half_spread_bps: float = HALF_SPREAD_BPS
    min_price_usd:   float = MIN_PRICE_USD
    min_history:     int = MIN_HISTORY
    rebalance:       str = REBALANCE_FREQ
    weighting:       str = WEIGHTING


SPEC = StrategySpec()


def rank_fn():
    """Return the rank_fn closure with frozen weights."""
    return zcombo.make_rank_fn([
        (residual_momentum.residual_momentum_score, W_RESID),
        (roa.roa_score, W_ROA),
    ])


def run(*, since: date, until: date):
    """Run residual_roa_6535 with frozen params. Returns a BacktestResult."""
    factor_backtest.HALF_SPREAD_BPS = HALF_SPREAD_BPS
    return factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N,
        starting_cash=STARTING_CASH,
        rank_fn=rank_fn(),
        rebalance_freq=REBALANCE_FREQ,
    )
