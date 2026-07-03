"""Multi-factor composite ranking.

Combines multiple single-factor `rank_universe` functions by averaging
each ticker's percentile rank across the factors. Only tickers that have
a non-None score in EVERY factor are eligible — partial scoring would
bias comparisons (a ticker missing from one factor would only be summed
over the others).

Percentile ranks (not raw scores) because factors have totally different
scales: momentum is a return ratio (~-0.5 to +5.0), low-vol is
-stdev (~-0.06 to -0.01). Summing raw values would let one factor
dominate. Percentile ranks normalise each to [0, 1].
"""
from __future__ import annotations

from datetime import date
from typing import Callable


RankFn = Callable[[list[str], date], list[tuple[str, float]]]


def composite_rank(rank_fns: list[RankFn]) -> RankFn:
    """Returns a rank_fn that combines `rank_fns` via avg percentile rank.
    A ticker must appear in EVERY input ranking to be eligible."""
    if not rank_fns:
        raise ValueError("composite_rank requires at least one rank_fn")

    def combined(universe: list[str], as_of: date) -> list[tuple[str, float]]:
        sums: dict[str, float] = {}
        counts: dict[str, int] = {}
        for rf in rank_fns:
            ranked = rf(universe, as_of)
            n = len(ranked)
            if n == 0:
                continue
            # i=0 is the best-ranked, so its percentile should be highest.
            for i, (t, _) in enumerate(ranked):
                pct = (n - i) / n
                sums[t] = sums.get(t, 0.0) + pct
                counts[t] = counts.get(t, 0) + 1
        n_required = len(rank_fns)
        eligible = [(t, sums[t] / n_required) for t in sums
                    if counts[t] == n_required]
        eligible.sort(key=lambda r: r[1], reverse=True)
        return eligible
    return combined
