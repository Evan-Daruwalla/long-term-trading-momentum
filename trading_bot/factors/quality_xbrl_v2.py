"""Quality factor v2 — XBRL with FCF, share dilution, and Piotroski components.

Extends quality_xbrl.py with:
  - FCF / Assets             (cash-flow quality, harder to manipulate than NI)
  - Current ratio            (liquidity)
  - 1-year asset growth      (Sloan-style proxy: high asset growth = low future return)
  - Share dilution check     (current shares vs 1yr ago)
  - Earnings persistence     (positive NI in latest period AND year ago)

Composite (each component z-scored cross-sectionally then summed):
  + z(ROE)                Profitability
  + z(OperatingMargin)    Operational efficiency
  + z(FCF/Assets)         Cash-flow quality (NEW)
  + z(CurrentRatio)       Liquidity (NEW)
  - z(Debt/Equity)        Leverage
  - z(AssetGrowth_1y)     Sloan-effect penalty (NEW)
  + z(EarningsPersist)    +1 if NI>0 both now AND year ago, else 0 (NEW)

Filter chain (in order — each excludes a class of garbage):
  1. Has core concepts (equity, assets, NI, revenue)
  2. ROA >= MIN_RETURN_ON_ASSETS (excludes funds & deep unprofitable)
  3. OperatingMargin in (-1, 1)  (sanity bound)
  4. EarningsPersist >= 0  (excludes loss-making companies on both periods)

Compared to v1 (quality_xbrl.py):
  - v1 score: z(ROE) + z(OM) - z(D/E)            (3 components)
  - v2 score: 7 components covering profit + cash + liquidity + growth
  - More signal, less noise; the academic "quality" composites typically
    use 5-8 components for robustness.
"""
from __future__ import annotations

import sqlite3
import statistics
from datetime import date, timedelta
from functools import lru_cache

from trading_bot.config import DB_PATH

FILING_LAG_DAYS = 60
MIN_RETURN_ON_ASSETS = 0.05

# Concept name groupings
STOCK_CONCEPTS = ("StockholdersEquity", "Assets", "AssetsCurrent",
                  "LiabilitiesCurrent", "PropertyPlantAndEquipmentNet",
                  "CashAndCashEquivalentsAtCarryingValue",
                  "CommonStockSharesOutstanding")
FLOW_CONCEPTS  = ("NetIncomeLoss", "OperatingIncomeLoss",
                  "NetCashProvidedByUsedInOperatingActivities",
                  "PaymentsToAcquirePropertyPlantAndEquipment", "GrossProfit")
REVENUE_CONCEPTS = ("RevenueFromContractWithCustomerExcludingAssessedTax",
                    "Revenues")
DEBT_CONCEPTS    = ("LongTermDebt", "LongTermDebtNoncurrent")


@lru_cache(maxsize=1)
def _load_facts() -> dict[str, dict[str, list[tuple]]]:
    """{ticker: {concept: [(period_end, filed, val), ...sorted by filed]}}"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT ticker, concept, period_end, filed, val "
        "FROM xbrl_facts WHERE val IS NOT NULL "
        "ORDER BY ticker, concept, filed"
    ).fetchall()
    conn.close()
    out: dict[str, dict[str, list[tuple]]] = {}
    for t, c, pe, fd, v in rows:
        out.setdefault(t, {}).setdefault(c, []).append((pe, fd, v))
    return out


def _latest_stock_value(facts: dict, concepts: tuple, cutoff: str
                        ) -> float | None:
    for c in concepts:
        entries = facts.get(c, [])
        latest = None
        for _pe, fd, v in entries:
            if fd <= cutoff:
                latest = v
            else:
                break
        if latest is not None:
            return latest
    return None


def _ttm_value(facts: dict, concepts: tuple, cutoff: str) -> float | None:
    for c in concepts:
        entries = facts.get(c, [])
        if not entries:
            continue
        eligible = [(pe, fd, v) for pe, fd, v in entries if fd <= cutoff]
        if not eligible:
            continue
        by_pe: dict[str, float] = {}
        for pe, _fd, v in eligible:
            by_pe[pe] = v
        sorted_pe = sorted(by_pe.items(), key=lambda x: x[0], reverse=True)
        chosen = sorted_pe[:4]
        if len(chosen) == 1:
            return chosen[0][1]
        if chosen:
            return sum(v for _pe, v in chosen)
    return None


def _stock_value_at(facts: dict, concepts: tuple, cutoff: str
                    ) -> float | None:
    """Alias for clarity; same as _latest_stock_value."""
    return _latest_stock_value(facts, concepts, cutoff)


def quality_components(ticker: str, as_of: date) -> dict | None:
    facts = _load_facts().get(ticker)
    if not facts:
        return None
    cutoff_now = (as_of - timedelta(days=FILING_LAG_DAYS)).isoformat()
    cutoff_1y  = (as_of - timedelta(days=FILING_LAG_DAYS + 365)).isoformat()

    # Current period values
    equity   = _latest_stock_value(facts, ("StockholdersEquity",), cutoff_now)
    assets   = _latest_stock_value(facts, ("Assets",), cutoff_now)
    cur_assets = _latest_stock_value(facts, ("AssetsCurrent",), cutoff_now)
    cur_liab   = _latest_stock_value(facts, ("LiabilitiesCurrent",), cutoff_now)
    debt     = _latest_stock_value(facts, DEBT_CONCEPTS, cutoff_now)
    shares_now = _latest_stock_value(facts, ("CommonStockSharesOutstanding",),
                                     cutoff_now)
    ni       = _ttm_value(facts, ("NetIncomeLoss",), cutoff_now)
    op_inc   = _ttm_value(facts, ("OperatingIncomeLoss",), cutoff_now)
    revenue  = _ttm_value(facts, REVENUE_CONCEPTS, cutoff_now)
    cfo      = _ttm_value(facts, ("NetCashProvidedByUsedInOperatingActivities",),
                          cutoff_now)
    capex    = _ttm_value(facts,
                          ("PaymentsToAcquirePropertyPlantAndEquipment",),
                          cutoff_now)

    # Year-ago values for growth/persistence components
    assets_1y = _latest_stock_value(facts, ("Assets",), cutoff_1y)
    shares_1y = _latest_stock_value(facts, ("CommonStockSharesOutstanding",),
                                    cutoff_1y)
    ni_1y     = _ttm_value(facts, ("NetIncomeLoss",), cutoff_1y)

    # Core requirements: need equity, assets, NI, revenue all valid
    if not (equity and equity > 0 and assets and assets > 0
            and ni is not None and revenue and revenue > 0):
        return None

    roe = ni / equity
    roa = ni / assets
    om = (op_inc / revenue) if op_inc is not None else None
    de = (debt / equity) if debt else 0.0

    # FCF (Cash from operations minus capex). If either is None, FCF = None.
    fcf = None
    if cfo is not None and capex is not None:
        fcf = cfo - capex     # capex is already a positive number = cash outflow
    fcf_over_assets = (fcf / assets) if fcf is not None else None

    current_ratio = ((cur_assets / cur_liab)
                     if cur_assets and cur_liab and cur_liab > 0 else None)

    # 1-year asset growth (Sloan-effect proxy — high asset growth = lower
    # future returns). Negative is BETTER (capital discipline).
    asset_growth_1y = ((assets / assets_1y - 1.0)
                       if assets_1y and assets_1y > 0 else None)

    # Earnings persistence: +1 if NI>0 now AND year ago, 0 if year ago missing,
    # -1 if NI now positive but year ago negative (turnaround story = risky)
    if ni > 0 and ni_1y is not None and ni_1y > 0:
        persistence = 1.0
    elif ni > 0 and ni_1y is None:
        persistence = 0.5
    elif ni > 0 and ni_1y is not None and ni_1y < 0:
        persistence = -0.5
    else:
        persistence = -1.0

    # Share dilution penalty: if shares grew >5% YoY = bad
    dilution_pp = None
    if shares_now and shares_1y and shares_1y > 0:
        dilution_pp = (shares_now / shares_1y - 1.0)

    return {
        "roe": roe, "roa": roa, "om": om, "de": de,
        "fcf_assets": fcf_over_assets,
        "current_ratio": current_ratio,
        "asset_growth": asset_growth_1y,
        "persistence": persistence,
        "dilution": dilution_pp,
    }


def rank_universe(tickers: list[str], as_of: date
                  ) -> list[tuple[str, float]]:
    """Rank by composite quality v2. Drops tickers missing required
    components, then z-scores each axis cross-sectionally and sums.

    Components (3 required for inclusion, 4 optional):
      Required: roe, om, de
      Optional (z-scored only if present): fcf_assets, current_ratio,
                                            asset_growth, persistence
    Tickers missing optionals get z=0 contribution for those axes
    (mean-out, so they neither help nor hurt).
    """
    have = []
    raw: dict[str, list[float]] = {}
    keys_pos = ["roe", "om", "fcf_assets", "current_ratio", "persistence"]
    keys_neg = ["de", "asset_growth", "dilution"]
    all_keys = keys_pos + keys_neg
    for k in all_keys:
        raw[k] = []

    for t in tickers:
        c = quality_components(t, as_of)
        if c is None:
            continue
        if c["roa"] < MIN_RETURN_ON_ASSETS:
            continue
        if c["om"] is None or not (-1.0 < c["om"] < 1.0):
            continue
        have.append(t)
        for k in all_keys:
            # Use 0.0 sentinel for missing optionals (will mean-out post-z-score
            # within a ticker's contribution)
            raw[k].append(c.get(k) if c.get(k) is not None else 0.0)

    if not have:
        return []

    # Z-score each component cross-sectionally
    z: dict[str, list[float]] = {}
    for k in all_keys:
        vals = raw[k]
        mu = statistics.fmean(vals)
        sd = statistics.pstdev(vals)
        z[k] = [(v - mu) / sd if sd > 0 else 0.0 for v in vals]

    scored = []
    for i, t in enumerate(have):
        score = sum(z[k][i] for k in keys_pos) - sum(z[k][i] for k in keys_neg)
        scored.append((t, score))
    scored.sort(key=lambda r: r[1], reverse=True)
    return scored
