"""Momentum filtered through quality screen.

Different combination scheme than sleeves: instead of running mom and quality
as separate sleeves with split capital, use quality as a FILTER on momentum's
universe. The fund stays 100% in momentum picks but only picks momentum
names that ALSO pass a quality threshold.

Algorithm for `rank_universe`:
  1. Rank universe by momentum (rank_mom)
  2. Compute quality_xbrl_v2 score for all tickers
  3. Keep only mom-top-200 picks that have quality score >= median
  4. From that intersection, return top-N by momentum rank

Why this might work where sleeves didn't:
  - Capital stays 100% in momentum (no dilution from low-Sharpe quality sleeve)
  - Quality acts as a "buy what doesn't suck" filter
  - Reduces momentum's exposure to junk names (penny stock biotechs etc.)

Why this might NOT work:
  - Could filter out the actual high-momentum names (those biotechs ARE where
    mom's premium lives, per the volume-filter experiment)
  - Quality scores aren't available for all tickers (~75% coverage at best)
  - Adding a filter on top of momentum could just be re-implementing the
    universe-narrowing tradeoff that already failed for volume/CEF filters
"""
from __future__ import annotations

from datetime import date

from trading_bot.factors import momentum, quality_xbrl_v2

MOM_TOP_N = 200    # consider the top-N momentum picks for filtering
QUALITY_PERCENTILE = 0.50    # keep names above this percentile of quality


def rank_universe(tickers: list[str], as_of: date
                  ) -> list[tuple[str, float]]:
    """Returns momentum-ranked tickers that ALSO pass the quality screen.
    The score returned is the momentum score (so downstream sorting picks
    highest-momentum names from the quality-passing set)."""
    # Step 1: Rank by momentum, get top-200
    mom_ranked = momentum.rank_universe(tickers, as_of)
    mom_top = mom_ranked[:MOM_TOP_N]
    mom_top_tickers = {t for t, _ in mom_top}
    mom_score_by_t = {t: s for t, s in mom_top}

    # Step 2: Rank by quality (on the full universe so the percentile cut
    # is computed against the broad cross-section, not just mom-top-200)
    q_ranked = quality_xbrl_v2.rank_universe(tickers, as_of)
    if not q_ranked:
        # No quality data available — return mom ranking unfiltered
        return mom_ranked

    # Step 3: Take quality names above the median (top 50% by quality score)
    n_keep = int(len(q_ranked) * (1 - QUALITY_PERCENTILE))
    q_passing = {t for t, _ in q_ranked[:n_keep]}

    # Step 4: Intersection — mom-top-200 ∩ quality-above-median
    intersection = mom_top_tickers & q_passing

    # Return them ordered by momentum score (so factor_backtest picks the
    # highest-momentum names from the intersection)
    out = [(t, mom_score_by_t[t]) for t in intersection]
    out.sort(key=lambda r: r[1], reverse=True)
    return out
