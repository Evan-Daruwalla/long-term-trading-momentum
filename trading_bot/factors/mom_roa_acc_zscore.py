"""3-factor cross-sectional Z-score: momentum + ROA + accruals.

Extension of mom_roa_zscore.py adding Sloan (1996) accruals as a 3rd input.

Hypothesis: ROA captures HIGH profitability; accruals captures EARNINGS
QUALITY (NI > CFO = inflated by non-cash, mean-reverting). Together they
might filter mom picks more effectively than either alone.

Per rebalance:
  1. For each ticker: compute mom + ROA + accruals scores
  2. Drop tickers missing ANY of the 3
  3. Z-score each factor cross-sectionally
  4. Combined = w_mom * Z_mom + w_roa * Z_roa + w_acc * Z_acc
  5. Sort descending

Note: accruals are NEGATED in the Z-score (low accruals = better quality
in Sloan's framing). roa is NOT negated (high ROA = better).
"""
from __future__ import annotations

import statistics
from datetime import date

from trading_bot.factors import momentum, roa, accruals


def _zscore(values: list[float]) -> list[float]:
    if len(values) < 2:
        return [0.0] * len(values)
    mean = statistics.fmean(values)
    sd = statistics.pstdev(values)
    if sd <= 0:
        return [0.0] * len(values)
    return [(v - mean) / sd for v in values]


def make_rank_fn(w_mom: float, w_roa: float, w_acc: float):
    def _ranker(tickers: list[str], as_of: date) -> list[tuple[str, float]]:
        rows: list[tuple[str, float, float, float]] = []
        for t in tickers:
            m = momentum.momentum_score(t, as_of)
            r = roa.roa_score(t, as_of)
            a = accruals.accruals_score(t, as_of)  # already filtered NI>0, |a|<=1
            if m is not None and r is not None and a is not None:
                # Accruals: high accruals = low quality. Negate so high score = better.
                rows.append((t, m, r, -a))
        if not rows:
            return []
        mom_z = _zscore([r[1] for r in rows])
        roa_z = _zscore([r[2] for r in rows])
        acc_z = _zscore([r[3] for r in rows])  # already negated; high z = good
        combined = [(rows[i][0],
                     w_mom * mom_z[i] + w_roa * roa_z[i] + w_acc * acc_z[i])
                    for i in range(len(rows))]
        combined.sort(key=lambda r: r[1], reverse=True)
        return combined
    _ranker.__name__ = f"mom_roa_acc_z_{w_mom:.2f}_{w_roa:.2f}_{w_acc:.2f}"
    return _ranker
