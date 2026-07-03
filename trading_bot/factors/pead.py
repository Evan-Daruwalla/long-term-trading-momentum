"""Post-Earnings Announcement Drift (PEAD) factor.

For each ticker, the PEAD signal is the EPS surprise (%) of its most
recent past earnings within a configurable lookback window (default 60
trading days ~ 1 quarter). PEAD literature documents 30-90 days of drift
after a surprise.

Data source: yfinance earnings_dates via
`scripts/data_audit/fetch_earnings_dates.py`. Cached at
`var/data_audit/earnings_dates_cache.json`. Coverage: ~2020-2026.
Tickers/dates outside that range return None (signal unavailable).

Signal direction: HIGH surprise (positive % beat) = higher score
(buy the post-beat drift). Negative surprises score negatively (drift down).
"""
from __future__ import annotations

import bisect
import json
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

CACHE_PATH = Path("var/data_audit/earnings_dates_cache.json")
DEFAULT_LOOKBACK_DAYS = 60


@lru_cache(maxsize=1)
def _load_cache() -> dict[str, list[dict]]:
    """ {ticker: [{date, surprise_pct, eps_actual, eps_est}, ...]} sorted by date."""
    if not CACHE_PATH.exists():
        return {}
    data = json.loads(CACHE_PATH.read_text())
    # Ensure each ticker's entries are sorted by date
    for tk in data:
        data[tk] = sorted(data[tk], key=lambda e: e["date"])
    return data


@lru_cache(maxsize=1)
def _date_lookups() -> dict[str, list[str]]:
    """{ticker: [iso_dates_sorted]} - parallel to _load_cache for bisect."""
    cache = _load_cache()
    return {tk: [e["date"] for e in entries] for tk, entries in cache.items()}


def pead_score(ticker: str, as_of: date,
               lookback_days: int = DEFAULT_LOOKBACK_DAYS) -> float | None:
    """Returns the surprise_pct of the most recent earnings within
    `lookback_days` calendar days before as_of (exclusive of as_of itself).
    Returns None if no recent earnings or surprise data missing."""
    dates = _date_lookups().get(ticker)
    if not dates:
        return None
    cache = _load_cache()
    entries = cache[ticker]
    cutoff_iso = as_of.isoformat()
    earliest_iso = (as_of - timedelta(days=lookback_days)).isoformat()
    # Find rightmost date strictly before as_of (no lookahead)
    i = bisect.bisect_left(dates, cutoff_iso) - 1
    if i < 0:
        return None
    if dates[i] < earliest_iso:
        return None
    entry = entries[i]
    sp = entry.get("surprise_pct")
    if sp is None:
        return None
    return float(sp)


def rank_universe(tickers: list[str], as_of: date,
                  lookback_days: int = DEFAULT_LOOKBACK_DAYS
                  ) -> list[tuple[str, float]]:
    """Rank by PEAD score descending. Tickers without recent earnings dropped.
    Use only as a SOLO test — for combination, see mom_roa_pead_zscore."""
    scored = []
    for t in tickers:
        s = pead_score(t, as_of, lookback_days)
        if s is not None:
            scored.append((t, s))
    scored.sort(key=lambda r: r[1], reverse=True)
    return scored
