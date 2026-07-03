"""Quality factor — yfinance-proxy version.

Quality in the factor literature loads on profitable, stable, low-leverage,
high-margin firms (Asness/Frazzini/Pedersen 2013 "Quality Minus Junk").

This is the QUICK proxy version reading from sqlite `fundamentals_cache`
populated by `scripts.momentum.warm.warm_fundamentals`. The cache is a CURRENT
SNAPSHOT — no point-in-time — so this factor is valid only for held-out
tests on recent dates. For a real production version, replace with SEC
XBRL pipeline (point-in-time, multi-period, no lookahead).

Composite score (each component z-scored then averaged):
  + returnOnEquity       (higher = better, profitable)
  + grossMargins         (higher = better, pricing power)
  + operatingMargins     (higher = better, operational efficiency)
  - debtToEquity         (lower  = better, less leverage)

Tickers missing any field are scored None and excluded from ranking.
"""
from __future__ import annotations

import sqlite3
import statistics
from datetime import date
from functools import lru_cache

from trading_bot.config import DB_PATH

POSITIVE_FIELDS = ("returnOnEquity", "grossMargins", "operatingMargins")
NEGATIVE_FIELDS = ("debtToEquity",)
# Sanity-bound filters applied BEFORE ranking. Excludes:
#   - Closed-end funds (CEFs like AEF/GAM/BCV/CII/UTG) which have huge
#     passive asset portfolios with no productive use → ROA ~0.003-0.012
#   - Unprofitable biotechs (VIR, ARVN) → negative ROA
#   - Garbage reports (VIR's reported OM=4592x revenue) → operatingMargins
#     bound prevents these dominating the ranking
# Real businesses (MA, V, KO, FTNT, APP, EXEL, ALNY) sail through with
# ROA = 0.05-0.45.
MIN_RETURN_ON_ASSETS = 0.08
OPERATING_MARGIN_BOUNDS = (-1.0, 1.0)    # exclude inverted/blown-out reports


@lru_cache(maxsize=1)
def _load_all() -> dict[str, dict[str, float]]:
    """{ticker: {field: value}} from sqlite. Cached process-wide.
    Cache invalidates only on process restart — fine since warm is a
    separate step."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT ticker, field, value FROM fundamentals_cache "
        "WHERE value IS NOT NULL"
    ).fetchall()
    conn.close()
    out: dict[str, dict[str, float]] = {}
    for ticker, field, value in rows:
        out.setdefault(ticker, {})[field] = value
    return out


def quality_score(ticker: str, as_of: date = None) -> float | None:  # noqa: ARG001
    """Composite quality score. as_of is ignored (current snapshot)."""
    fund = _load_all().get(ticker)
    if not fund:
        return None
    # Need every component to produce a score (no partial scoring)
    required = POSITIVE_FIELDS + NEGATIVE_FIELDS
    if any(f not in fund for f in required):
        return None
    # We can't z-score a single ticker — rank_universe handles cross-section.
    # quality_score returns the raw "higher is better" composite, leaving
    # normalization to rank_universe.
    return (
        fund["returnOnEquity"]
        + fund["grossMargins"]
        + fund["operatingMargins"]
        - fund["debtToEquity"] / 100.0    # debtToEquity is reported as pct
                                          # (79.5 = 79.5%) so /100 to match scale
    )


def rank_universe(tickers: list[str], as_of: date  # noqa: ARG001
                  ) -> list[tuple[str, float]]:
    """Rank tickers by composite quality (higher = better).

    Uses cross-sectional z-scoring per component so units don't matter:
    a high-ROE-low-margin firm and a low-ROE-high-margin firm get fair
    treatment. Ranks ONLY tickers with all components present (no partial
    scoring — quality is a multi-dimensional claim that all components must
    support) AND passing the sanity-bound filters (ROA + OM bounds).
    """
    fund_all = _load_all()
    have = []
    raw = {f: [] for f in POSITIVE_FIELDS + NEGATIVE_FIELDS}
    om_lo, om_hi = OPERATING_MARGIN_BOUNDS
    required = POSITIVE_FIELDS + NEGATIVE_FIELDS + ("returnOnAssets",)
    for t in tickers:
        f = fund_all.get(t)
        if not f or any(k not in f for k in required):
            continue
        # Sanity-bound filters — exclude CEFs (low ROA) and garbage reports
        # (out-of-bound OM). Real businesses pass cleanly.
        if f["returnOnAssets"] < MIN_RETURN_ON_ASSETS:
            continue
        if not (om_lo < f["operatingMargins"] < om_hi):
            continue
        have.append(t)
        for k in raw:
            raw[k].append(f[k])

    if not have:
        return []

    # Z-score each component cross-sectionally
    z = {}
    for k, vals in raw.items():
        mu = statistics.fmean(vals)
        sd = statistics.pstdev(vals)
        if sd == 0:
            z[k] = [0.0] * len(vals)
        else:
            z[k] = [(v - mu) / sd for v in vals]

    # Composite: sum of positive z, minus sum of negative z
    scored = []
    for i, t in enumerate(have):
        pos = sum(z[k][i] for k in POSITIVE_FIELDS)
        neg = sum(z[k][i] for k in NEGATIVE_FIELDS)
        scored.append((t, pos - neg))
    scored.sort(key=lambda r: r[1], reverse=True)
    return scored
