"""Insider cluster buying factor — uses cached Form 4 data with NEW framing.

Phase 1 (Form 4 standalone copy strategy) was decisively closed at
+0% alpha (memory/form4_verdict.md). This factor tests a DIFFERENT
question: when multiple insiders independently buy in a short window,
does that AGGREGATED signal contain alpha?

Academic basis: Cohen et al. (2012) "Decoding Inside Information" shows
"opportunistic" insider trades (multiple buyers, no schedule) have
significantly higher subsequent returns than "routine" (single, scheduled).

Signal definition:
  cluster_score(ticker, as_of) = number of distinct filer_cik values that
  filed Form 4 'P' (open-market purchase) with acquired_disposed='A'
  for `ticker` in the last LOOKBACK_DAYS calendar days ending at as_of,
  where each purchase had total_value >= MIN_VALUE_USD.

Direction: higher cluster_score = more conviction = bullish overlay.

Use as:
  - Standalone (filter universe to ticker with cluster_score >= 3)
  - Z-score combiner alongside mom + ROA (4-factor combo)
"""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from functools import lru_cache

from trading_bot.config import DB_PATH

LOOKBACK_DAYS = 30
MIN_VALUE_USD = 10_000.0   # filter out tiny "compensation" transactions


@lru_cache(maxsize=2)
def _load_all_buys() -> dict[str, list[tuple[str, str]]]:
    """One-time load: {ticker: [(filed_at, filer_cik), ...]} sorted by date.

    Only includes 'P' (open-market purchase), 'A' (acquired), total_value
    above MIN_VALUE_USD. Cached for the process lifetime.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT ticker, filed_at, filer_cik
        FROM signals
        WHERE transaction_code='P' AND acquired_disposed='A'
          AND total_value >= ?
          AND ticker IS NOT NULL AND filer_cik IS NOT NULL
        ORDER BY ticker, filed_at
    """, (MIN_VALUE_USD,)).fetchall()
    conn.close()
    out: dict[str, list[tuple[str, str]]] = {}
    for r in rows:
        out.setdefault(r["ticker"], []).append((r["filed_at"], r["filer_cik"]))
    return out


def cluster_score(ticker: str, as_of: date) -> int:
    """Count distinct insider buyers (filer_cik) in last LOOKBACK_DAYS
    ending at as_of. Returns 0 if no qualifying buys."""
    buys = _load_all_buys().get(ticker, [])
    if not buys:
        return 0
    cutoff_lo = (as_of - timedelta(days=LOOKBACK_DAYS)).isoformat()
    cutoff_hi = as_of.isoformat()
    distinct = set()
    # buys are sorted by filed_at; iterate filtering by date window
    for filed_at, filer_cik in buys:
        if filed_at < cutoff_lo:
            continue
        if filed_at > cutoff_hi:
            break  # sorted, can stop
        distinct.add(filer_cik)
    return len(distinct)


def rank_universe(tickers: list[str], as_of: date,
                  min_cluster: int = 2) -> list[tuple[str, float]]:
    """Rank tickers by cluster_score descending. Drops tickers below
    min_cluster (default 2 = at least 2 distinct buyers required to be
    considered "clustered")."""
    scored: list[tuple[str, float]] = []
    for t in tickers:
        s = cluster_score(t, as_of)
        if s >= min_cluster:
            scored.append((t, float(s)))
    scored.sort(key=lambda r: r[1], reverse=True)
    return scored
