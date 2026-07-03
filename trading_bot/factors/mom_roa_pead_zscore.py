"""Cross-sectional Z-score combo of mom + ROA + PEAD.

Like mom_roa_zscore.py but adds PEAD as a 3rd factor. Key difference from
mom_roa_acc: PEAD data only exists post-2020, so for pre-2020 ticker/dates
the PEAD score is treated as 0 (NEUTRAL) rather than missing - so the
strategy still works during 2015-2019 (just without the PEAD edge).

Per rebalance:
  1. For each ticker: compute mom + ROA + PEAD scores
  2. Drop tickers missing mom or ROA. If PEAD missing, treat as 0.
  3. Z-score each factor cross-sectionally (PEAD Z'd only over non-zeros).
  4. Combined = w_mom*Z_mom + w_roa*Z_roa + w_pead*Z_pead
"""
from __future__ import annotations

import statistics
from datetime import date

from trading_bot.factors import momentum, roa, pead


def _zscore(values: list[float]) -> list[float]:
    if len(values) < 2:
        return [0.0] * len(values)
    mean = statistics.fmean(values)
    sd = statistics.pstdev(values)
    if sd <= 0:
        return [0.0] * len(values)
    return [(v - mean) / sd for v in values]


def make_rank_fn(w_mom: float, w_roa: float, w_pead: float,
                 pead_lookback_days: int = 60):
    def _ranker(tickers: list[str], as_of: date) -> list[tuple[str, float]]:
        rows: list[tuple[str, float, float, float | None]] = []
        for t in tickers:
            m = momentum.momentum_score(t, as_of)
            r = roa.roa_score(t, as_of)
            if m is None or r is None:
                continue
            p = pead.pead_score(t, as_of, lookback_days=pead_lookback_days)
            rows.append((t, m, r, p))
        if not rows:
            return []

        mom_z = _zscore([r[1] for r in rows])
        roa_z = _zscore([r[2] for r in rows])

        # PEAD: Z-score only among tickers WITH PEAD data; assign 0 to others
        pead_vals = [r[3] for r in rows if r[3] is not None]
        pead_z_lookup: dict[int, float] = {}
        if len(pead_vals) >= 2:
            sd = statistics.pstdev(pead_vals)
            mean = statistics.fmean(pead_vals)
            if sd > 0:
                idx_with_pead = 0
                for i, r in enumerate(rows):
                    if r[3] is not None:
                        pead_z_lookup[i] = (r[3] - mean) / sd
                        idx_with_pead += 1
        # Build pead_z list with 0 fallback for missing PEAD
        pead_z = [pead_z_lookup.get(i, 0.0) for i in range(len(rows))]

        combined = [(rows[i][0],
                     w_mom * mom_z[i] + w_roa * roa_z[i] + w_pead * pead_z[i])
                    for i in range(len(rows))]
        combined.sort(key=lambda r: r[1], reverse=True)
        return combined
    _ranker.__name__ = f"mom_roa_pead_z_{w_mom:.2f}_{w_roa:.2f}_{w_pead:.2f}"
    return _ranker
