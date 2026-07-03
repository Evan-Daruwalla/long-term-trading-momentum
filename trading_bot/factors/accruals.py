"""Accruals factor — Sloan (1996) anomaly.

Companies whose earnings are inflated by non-cash accruals (NI > CFO)
mean-revert to lower earnings; companies where cash flow exceeds earnings
(NI < CFO) tend to outperform.

Signal:
  accruals = (NI - CFO) / avg(Assets_now, Assets_1y_ago)

Direction (long-only):
  Lower accruals = better. Score returned is NEGATED accruals so that
  factor_backtest's "top by score" picks lowest-accrual names.

Data requirements (all PIT, filed-date lagged 60d):
  - NetIncomeLoss                                 (TTM, 4,157 tickers)
  - NetCashProvidedByUsedInOperatingActivities    (TTM, 4,174 tickers)
  - Assets                                        (stock, 4,182 tickers)

Why this might combine with momentum where 7 prior attempts failed:
  - Fundamental driver (no price input — different signal source)
  - Low turnover (~annual rebalance natural; ~20%/yr from academic studies)
  - Largely uncorrelated with momentum at the cross-sectional level

Why it might still fail:
  - Coverage is annual at best (TTM updates 4x/yr)
  - Same 2018/2022 drawdown synchrony as quality factors
  - Sloan's original alpha (~10%/yr in 1962-91) has decayed in post-1996
    literature; held-out alpha now estimated 2-5%/yr
"""
from __future__ import annotations

import statistics
from datetime import date, timedelta

from trading_bot.factors.quality_xbrl_v2 import (
    _load_facts, _latest_stock_value, _ttm_value,
)

FILING_LAG_DAYS = 60


def accruals_score(ticker: str, as_of: date) -> float | None:
    """Returns (NI - CFO) / avg(Assets_now, Assets_1y_ago), or None if missing."""
    facts = _load_facts().get(ticker)
    if not facts:
        return None
    cutoff_now = (as_of - timedelta(days=FILING_LAG_DAYS)).isoformat()
    cutoff_1y  = (as_of - timedelta(days=FILING_LAG_DAYS + 365)).isoformat()

    ni  = _ttm_value(facts, ("NetIncomeLoss",), cutoff_now)
    cfo = _ttm_value(facts,
                     ("NetCashProvidedByUsedInOperatingActivities",),
                     cutoff_now)
    assets_now = _latest_stock_value(facts, ("Assets",), cutoff_now)
    assets_1y  = _latest_stock_value(facts, ("Assets",), cutoff_1y)

    if ni is None or cfo is None or not assets_now or assets_now <= 0:
        return None

    # Sloan-filter: the accrual anomaly applies to PROFITABLE firms. On
    # money-losing companies the signal flips its meaning — "very negative
    # accruals" just means "very negative NI with somewhat-less-negative
    # CFO," which is bankruptcy-track not high-quality. Modern Sloan
    # implementations all filter NI > 0; this matches the academic consensus
    # since Hribar & Collins 2002 / Richardson et al. 2005.
    if ni <= 0:
        return None

    # Use average if 1y available, else current. Two-period average is the
    # standard Sloan denominator; falling back to current avoids dropping
    # young companies with <1yr of filings.
    avg_assets = (assets_now + assets_1y) / 2.0 if assets_1y and assets_1y > 0 else assets_now
    a = (ni - cfo) / avg_assets

    # Sanity bound: accruals scaled by assets should be in [-1, 1] for any
    # economically real firm — total non-cash items can't exceed total assets.
    # Beyond that we're seeing data errors (e.g. EWCZ had Assets=$100 in an
    # IPO-era filing while NI/CFO were in $M, blowing the ratio to ~800k).
    if abs(a) > 1.0:
        return None
    return a


def rank_universe(tickers: list[str], as_of: date
                  ) -> list[tuple[str, float]]:
    """Rank tickers by NEGATED accruals (low accruals = high score = better).

    No z-scoring needed — accruals ratios are already normalized to scale-free
    units, and the relative ordering is what matters for top-N selection.
    Tickers with insufficient data are dropped.
    """
    scored: list[tuple[str, float]] = []
    for t in tickers:
        a = accruals_score(t, as_of)
        if a is None:
            continue
        scored.append((t, -a))    # negate: lower accruals = higher score
    scored.sort(key=lambda r: r[1], reverse=True)
    return scored
