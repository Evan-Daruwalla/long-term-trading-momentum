"""Generic cross-sectional Z-score combiner.

Generalizes mom_roa_zscore to any set of (score_fn, weight) pairs. A ticker is
dropped if it's missing ANY component score. Each component is Z-scored across
the surviving universe (mean 0, std 1), then combined as sum(w_i * Z_i).

    rank_fn = zcombo.make_rank_fn([
        (residual_momentum.residual_momentum_score, 0.65),
        (roa.roa_score, 0.35),
    ])

Why Z-scores not percentile ranks: percentile-rank composites destroyed
in-sample CAGR in early multi-factor attempts (they discard magnitude). See
mom_roa_zscore.py for the original rationale.
"""
from __future__ import annotations

import statistics
from datetime import date
from typing import Callable

ScoreFn = Callable[[str, date], float | None]


def _zscore(values: list[float]) -> list[float]:
    if len(values) < 2:
        return [0.0] * len(values)
    mean = statistics.fmean(values)
    sd = statistics.pstdev(values)
    if sd <= 0:
        return [0.0] * len(values)
    return [(v - mean) / sd for v in values]


def make_rank_fn(components: list[tuple[ScoreFn, float]]):
    """components: list of (score_fn, weight). Weights need not sum to 1."""
    def _ranker(tickers: list[str], as_of: date) -> list[tuple[str, float]]:
        rows: list[tuple[str, list[float]]] = []
        for t in tickers:
            scores = [fn(t, as_of) for fn, _ in components]
            if any(s is None for s in scores):
                continue
            rows.append((t, scores))  # type: ignore[arg-type]
        if not rows:
            return []
        n_comp = len(components)
        zs = [_zscore([r[1][k] for r in rows]) for k in range(n_comp)]
        weights = [w for _, w in components]
        combined = []
        for idx, (t, _) in enumerate(rows):
            score = sum(weights[k] * zs[k][idx] for k in range(n_comp))
            combined.append((t, score))
        combined.sort(key=lambda r: r[1], reverse=True)
        return combined
    names = "_".join(f"{w:.2f}" for _, w in components)
    _ranker.__name__ = f"zcombo_{names}"
    return _ranker
