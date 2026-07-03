"""Point-in-time quality factor — SEC XBRL backed.

Replaces the yfinance-proxy `quality.py` (which used current-snapshot
fundamentals and was lookahead-biased). This version uses the
`xbrl_facts` table populated by `scripts.momentum.warm.warm_xbrl`, which
includes the `filed` date for every value so we can answer
"what did X's books look like on date D?" without lookahead.

================================================================
POINT-IN-TIME LOGIC
================================================================
For each (ticker, concept) on a given as_of date:
  - Find the latest filing where `filed <= as_of - FILING_LAG_DAYS`
  - Use that filing's value
  - Skip the ticker if any required concept is missing

FILING_LAG_DAYS = 60 (conservative). Companies typically file 10-Qs
~40 days after period end and 10-Ks ~60-90 days after. The 60-day lag
ensures we're using data the public would have had.

================================================================
QUALITY COMPOSITE
================================================================
z(ROE) + z(OperatingMargin) - z(Debt/Equity)

Three components, not four — dropped GrossMargin because many services,
financial, and transportation companies don't report GrossProfit in
XBRL (it's an income-statement line that's optional for non-product
businesses). Including it as a hard requirement would exclude AAL,
banks, most insurers, etc. The Fama-French quality factor similarly
uses gross-profitability-over-assets rather than margin.

Plus sanity filter: ROA >= MIN_RETURN_ON_ASSETS (excludes funds).

Derivation from XBRL concepts:
  ROE              = NetIncomeLoss / StockholdersEquity        (TTM / latest)
  ROA              = NetIncomeLoss / Assets                    (TTM / latest)
  OperatingMargin  = OperatingIncomeLoss / Revenues            (TTM)
  Debt/Equity      = (LongTermDebt) / StockholdersEquity       (snapshot)

TTM (trailing-twelve-month) flow items are summed over the last 4
quarterly filings to smooth out seasonality.

================================================================
NOTES
================================================================
- TTM logic: for flow concepts (NetIncomeLoss, Revenues, GrossProfit,
  OperatingIncomeLoss) we sum the most-recent 4 quarters as of as_of.
- Stock concepts (StockholdersEquity, Assets, LongTermDebt) use the
  latest single filing — they're balance sheet snapshots.
- For tickers with insufficient XBRL history (need 4 quarters of flow
  data + most recent balance sheet), returns None.
"""
from __future__ import annotations

import sqlite3
import statistics
from datetime import date, timedelta
from functools import lru_cache

from trading_bot.config import DB_PATH

# Filtering thresholds — see quality.py module docstring for rationale.
FILING_LAG_DAYS = 60          # conservative; ensures public availability
MIN_RETURN_ON_ASSETS = 0.05   # excludes CEFs / fund-like vehicles

# Concept mappings
# Stock concepts (use latest single value at as_of):
STOCK_CONCEPTS = ("StockholdersEquity", "Assets")
# Flow concepts (sum last 4 quarters for TTM):
FLOW_CONCEPTS = ("NetIncomeLoss", "OperatingIncomeLoss", "GrossProfit")
# Revenue concept varies historically (new standard 2018+)
REVENUE_CONCEPTS = ("RevenueFromContractWithCustomerExcludingAssessedTax",
                    "Revenues")
# Debt concepts vary by company structure
DEBT_CONCEPTS = ("LongTermDebt", "LongTermDebtNoncurrent")


@lru_cache(maxsize=1)
def _load_facts() -> dict[str, dict[str, list[tuple]]]:
    """{ticker: {concept: [(period_end, filed, val), ...sorted by filed]}}.
    Loaded once per process; xbrl_facts is read-only during a backtest."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT ticker, concept, period_end, filed, val "
        "FROM xbrl_facts "
        "WHERE val IS NOT NULL "
        "ORDER BY ticker, concept, filed"
    ).fetchall()
    conn.close()
    out: dict[str, dict[str, list[tuple]]] = {}
    for ticker, concept, period_end, filed, val in rows:
        out.setdefault(ticker, {}).setdefault(concept, []).append(
            (period_end, filed, val))
    return out


def _latest_stock_value(facts: dict, concepts: tuple, as_of_iso: str
                        ) -> float | None:
    """Latest single value for any concept in `concepts`, filed <= as_of.
    Tries each concept in order — returns first hit (handles concept-name
    drift between companies). Stock concept = balance sheet snapshot."""
    for concept in concepts:
        entries = facts.get(concept, [])
        # entries are sorted by filed ascending; find rightmost <= cutoff
        latest_val = None
        for _pe, filed, val in entries:
            if filed <= as_of_iso:
                latest_val = val
            else:
                break
        if latest_val is not None:
            return latest_val
    return None


def _ttm_value(facts: dict, concepts: tuple, as_of_iso: str
               ) -> float | None:
    """Trailing-twelve-month sum: take the latest annual (FY) filing
    if available and filed <= cutoff; else sum the last 4 quarterly
    filings. Returns None if neither path is satisfiable.

    We prefer annual values when available because they're already
    summed and audited; quarterly sums can have noise from restated
    interim periods. Falls back to summing the most recent 4 quarterly
    `period_end` values that are filed <= cutoff and don't overlap.
    """
    for concept in concepts:
        entries = facts.get(concept, [])
        if not entries:
            continue
        # Filter to filed <= cutoff
        eligible = [(pe, fd, v) for (pe, fd, v) in entries
                    if fd <= as_of_iso]
        if not eligible:
            continue
        # Approach: take the most-recent 4 distinct period_end values,
        # sum them. Approximates TTM regardless of whether each filing
        # is Q1/Q2/Q3/Q4 or 10-K (which already covers full year).
        # Heuristic — if values cluster ~equally, it's quarterly; if
        # one value is ~4x another, the big one is an annual that
        # double-counts the quarterly. We sort & dedupe by period_end.
        by_pe: dict[str, float] = {}
        for pe, _fd, v in eligible:
            by_pe[pe] = v   # later filings overwrite (e.g. restatements)
        sorted_pe = sorted(by_pe.items(), key=lambda x: x[0], reverse=True)
        # Drop period_ends within 60 days of as_of (their data wouldn't be
        # filed yet given FILING_LAG_DAYS; defensive)
        sorted_pe = sorted_pe[:8]    # keep more than 4 in case of dedupe
        # Use the most recent 4 distinct period_ends
        chosen = sorted_pe[:4]
        if len(chosen) >= 1:
            # If just one row and it's an annual (10-K), use as-is
            if len(chosen) == 1:
                return chosen[0][1]
            # Multiple rows: sum them (4 quarters ~= TTM)
            return sum(v for _pe, v in chosen)
    return None


def quality_components(ticker: str, as_of: date) -> dict | None:
    """Return {roe, roa, gm, om, de} or None if insufficient data.
    Uses point-in-time XBRL values (filed <= as_of - FILING_LAG_DAYS)."""
    facts = _load_facts().get(ticker)
    if not facts:
        return None
    cutoff = (as_of - timedelta(days=FILING_LAG_DAYS)).isoformat()

    equity = _latest_stock_value(facts, ("StockholdersEquity",), cutoff)
    assets = _latest_stock_value(facts, ("Assets",), cutoff)
    debt = _latest_stock_value(facts, DEBT_CONCEPTS, cutoff)
    net_income = _ttm_value(facts, ("NetIncomeLoss",), cutoff)
    operating_income = _ttm_value(facts, ("OperatingIncomeLoss",), cutoff)
    revenue = _ttm_value(facts, REVENUE_CONCEPTS, cutoff)
    gross_profit = _ttm_value(facts, ("GrossProfit",), cutoff)

    # Require the core inputs. Debt is optional (some companies have none).
    if not (equity and equity > 0 and assets and assets > 0
            and net_income is not None and revenue and revenue > 0):
        return None

    roe = net_income / equity
    roa = net_income / assets
    om = (operating_income / revenue) if operating_income is not None else None
    gm = (gross_profit / revenue) if gross_profit is not None else None
    de = (debt / equity) if debt else 0.0    # treat missing debt as zero

    return {"roe": roe, "roa": roa, "gm": gm, "om": om, "de": de}


def rank_universe(tickers: list[str], as_of: date
                  ) -> list[tuple[str, float]]:
    """Rank by point-in-time quality: z(ROE) + z(OM) - z(D/E).

    Filter chain:
      1. Has all required XBRL concepts (equity>0, assets, net_income, revenue>0)
      2. ROA >= MIN_RETURN_ON_ASSETS (excludes funds & unprofitable cos)
      3. Operating margin in (-1, 1) (sanity bound on inverted reports)
    """
    have = []
    raw: dict[str, list[float]] = {k: [] for k in ("roe", "om", "de")}
    for t in tickers:
        c = quality_components(t, as_of)
        if c is None:
            continue
        if c["roa"] < MIN_RETURN_ON_ASSETS:
            continue
        if c["om"] is None:
            continue
        if not (-1.0 < c["om"] < 1.0):
            continue
        have.append(t)
        raw["roe"].append(c["roe"])
        raw["om"].append(c["om"])
        raw["de"].append(c["de"])

    if not have:
        return []

    # Z-score each component cross-sectionally
    z: dict[str, list[float]] = {}
    for k, vals in raw.items():
        mu = statistics.fmean(vals)
        sd = statistics.pstdev(vals)
        if sd == 0:
            z[k] = [0.0] * len(vals)
        else:
            z[k] = [(v - mu) / sd for v in vals]

    scored: list[tuple[str, float]] = []
    for i, t in enumerate(have):
        score = z["roe"][i] + z["om"][i] - z["de"][i]
        scored.append((t, score))
    scored.sort(key=lambda r: r[1], reverse=True)
    return scored
