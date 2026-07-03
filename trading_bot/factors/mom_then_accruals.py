"""Non-sleeve combination: momentum-then-accruals (quality refinement of mom winners).

Algorithm for rank_universe:
  1. Rank by 12-1 momentum, take top-MOM_TOP (default 100)
  2. Within those mom-winners, compute accruals score
  3. Re-rank by accruals (high score = low accruals = high earnings quality)
  4. Return ordered by accruals; downstream backtest picks top-50

Different from sleeves (no capital split) and different from `mom_quality_screen`
(uses accruals not quality_xbrl_v2; uses re-rank not threshold-filter).

Hypothesis: among the 100 strongest momentum names, removing the ones with
junk earnings (high accruals, where reported NI is inflated by non-cash items
that will mean-revert) might preserve mom's edge while reducing drawdowns from
"momentum winners that are quality losers about to collapse" — the WeWork /
Nikola / Carvana-type names that show high momentum on the way up but have
terrible cash conversion underneath.

Why this differs from mom_quality_screen (which failed):
  - mom_quality_screen used quality_xbrl_v2's 8-component composite as the
    filter; that ranks by ROE/OM/leverage which correlates with mom's own
    biases. The screen cut 83% of mom picks because most mom-winners are
    high-growth low-quality names.
  - Accruals is uncorrelated with mom by construction (we just confirmed via
    sleeves test — same conclusion as state-doc prediction).
  - Pure accruals filter on mom-top-100 should drop ~50% (top half by
    accruals), preserving momentum's universe rather than gutting it.

What "win" looks like:
  - In-sample CAGR >= mom_v2's 21%/yr (or close, with better max DD)
  - Held-out CAGR >= mom_v2's 26.5%/yr (or close, with better Sharpe)
  - At least ONE window strictly better than mom_v2 solo

What "fail" looks like (most likely):
  - Filter removes mom's small-cap moonshots (only profitable firms get
    accruals scores at all — 55% of universe), capping the alpha tail.
  - Combined return < mom_v2 solo on both windows, like mom_quality_screen.
"""
from __future__ import annotations

from datetime import date

from trading_bot.factors import momentum, accruals

MOM_TOP_N = 100    # consider the top-N momentum picks for accruals filtering


def rank_universe(tickers: list[str], as_of: date
                  ) -> list[tuple[str, float]]:
    """Returns mom-top-100 re-ranked by accruals (best first).
    Score returned is the accruals score (so downstream picks lowest-accruals
    names from the mom-top-100 set)."""
    # Step 1: Rank by momentum, take top-100
    mom_ranked = momentum.rank_universe(tickers, as_of)
    mom_top = mom_ranked[:MOM_TOP_N]
    mom_top_tickers = [t for t, _ in mom_top]

    if not mom_top_tickers:
        return []

    # Step 2: Re-rank those by accruals (only profitable firms with valid
    # accruals data; others get dropped)
    accr_ranked = accruals.rank_universe(mom_top_tickers, as_of)

    # If accruals filter dropped everything (e.g. early-period coverage gaps),
    # fall back to raw mom ranking so the backtest doesn't crash
    if not accr_ranked:
        return mom_top

    return accr_ranked
