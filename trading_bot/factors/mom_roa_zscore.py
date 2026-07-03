"""Cross-sectional Z-score combo of momentum + ROA.

AQR-style "Value + Momentum Everywhere" framing applied to (momentum, ROA)
since canonical value signals require shares-outstanding data we don't have.

Algorithm per rebalance:
  1. For each ticker: compute momentum score AND ROA score
  2. Drop tickers missing EITHER signal
  3. Z-score each factor cross-sectionally (mean=0, std=1 across the universe)
  4. Combined score = w_mom * Z_mom + w_roa * Z_roa
  5. Sort descending, return as rank for factor_backtest

Why Z-scores (not percentile ranks)?
  - Percentile-rank composite was Attempt 1 of multi-factor research and
    DESTROYED in-sample CAGR (-15.6pp). Z-scores preserve magnitude info
    (a 4-stdev signal counts more than a 1-stdev one), which percentile
    ranks discard.

Why this might succeed where prior attempts failed:
  - Different combination math (Z not percentile)
  - ROA fundamentally uncorrelated with momentum at cross-section
  - User-configurable weights allow sensitivity tuning

Configure weights via `make_rank_fn(w_mom, w_roa)` factory.
"""
from __future__ import annotations

import statistics
from datetime import date

from trading_bot.factors import momentum, roa


def _zscore(values: list[float]) -> list[float]:
    if len(values) < 2:
        return [0.0] * len(values)
    mean = statistics.fmean(values)
    sd = statistics.pstdev(values)
    if sd <= 0:
        return [0.0] * len(values)
    return [(v - mean) / sd for v in values]


def make_rank_fn(w_mom: float = 0.5, w_roa: float = 0.5):
    """Build a rank_fn for factor_backtest. Weights need not sum to 1
    (they're applied to Z-scores which are already comparable)."""
    def _ranker(tickers: list[str], as_of: date) -> list[tuple[str, float]]:
        # Compute both scores; drop tickers missing either
        rows: list[tuple[str, float, float]] = []  # (ticker, mom, roa)
        for t in tickers:
            m = momentum.momentum_score(t, as_of)
            r = roa.roa_score(t, as_of)
            if m is not None and r is not None:
                rows.append((t, m, r))
        if not rows:
            return []
        mom_z = _zscore([r[1] for r in rows])
        roa_z = _zscore([r[2] for r in rows])
        combined = [(rows[i][0], w_mom * mom_z[i] + w_roa * roa_z[i])
                    for i in range(len(rows))]
        combined.sort(key=lambda r: r[1], reverse=True)
        return combined
    _ranker.__name__ = f"mom_roa_z_{w_mom:.2f}_{w_roa:.2f}"
    return _ranker
