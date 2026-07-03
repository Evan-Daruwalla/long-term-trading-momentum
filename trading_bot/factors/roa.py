"""ROA (Return on Assets) factor — Novy-Marx (2013) profitability anomaly.

Used as a SUBSTITUTE for canonical value (P/B, P/E) since shares-outstanding
data is not in xbrl_facts (dei: namespace not warmed). ROA is a related
fundamental-quality factor that uses only cached data:

  ROA = NetIncomeLoss (TTM) / avg(Assets_now, Assets_1y_ago)

Direction (long-only): higher ROA = better (more profitable firms outperform
on a risk-adjusted basis per Novy-Marx).

Data requirements (all PIT, filed-date lagged 60d, same as accruals.py):
  - NetIncomeLoss (TTM)
  - Assets (stock)

Why ROA might combine with momentum where 7+ prior attempts failed:
  - Fundamental driver (no price input - different signal source than momentum)
  - Low turnover (~annual rebalance natural)
  - Largely uncorrelated with momentum cross-sectionally
  - Profitability anomaly has held up better than value over the last decade

Why it might still fail (consistent with prior multi-factor failures):
  - Similar drawdown synchrony with mom in crashes (2018, 2022)
  - Lower Sharpe than momentum drags any combo
"""
from __future__ import annotations

from datetime import date, timedelta

from trading_bot.factors.quality_xbrl_v2 import (
    _load_facts, _latest_stock_value, _ttm_value,
)

FILING_LAG_DAYS = 60


def roa_score(ticker: str, as_of: date) -> float | None:
    """Returns NI_TTM / avg(Assets_now, Assets_1y_ago), or None if missing."""
    facts = _load_facts().get(ticker)
    if not facts:
        return None
    cutoff_now = (as_of - timedelta(days=FILING_LAG_DAYS)).isoformat()
    cutoff_1y  = (as_of - timedelta(days=FILING_LAG_DAYS + 365)).isoformat()

    ni = _ttm_value(facts, ("NetIncomeLoss",), cutoff_now)
    assets_now = _latest_stock_value(facts, ("Assets",), cutoff_now)
    assets_1y  = _latest_stock_value(facts, ("Assets",), cutoff_1y)

    if ni is None or not assets_now or assets_now <= 0:
        return None

    avg_assets = (assets_now + assets_1y) / 2.0 if assets_1y and assets_1y > 0 else assets_now
    r = ni / avg_assets

    # Sanity bound: real ROA is typically in [-1, +1]. Beyond that =
    # data errors (e.g. IPO-era tiny Assets value blowing the ratio).
    if abs(r) > 1.0:
        return None
    return r


def rank_universe(tickers: list[str], as_of: date) -> list[tuple[str, float]]:
    """Rank tickers by ROA, descending (high ROA = best)."""
    scored: list[tuple[str, float]] = []
    for t in tickers:
        s = roa_score(t, as_of)
        if s is not None:
            scored.append((t, s))
    scored.sort(key=lambda r: r[1], reverse=True)
    return scored
