"""Sector-overlay experiment — MACRO/top-down LLM veto on sector_top4.

================================================================
WHAT THIS IS (and the honest prior)
================================================================
A SECOND, parallel falsifiable test to the stock-level llm_overlay. Same
structure (pre-committed, logged, control-vs-treatment), but applied to the
sector_top4 sleeve: the LLM may VETO any of the 4 momentum-picked SPDR sector
ETFs to cash, based on a MACRO/top-down read (rate regime, sector
valuation/crowding, earnings breadth) rather than single-stock fundamentals.

Honest prior (recorded 2026-06-05): this is a WEAKER test than the stock
overlay. The decision is a macro/relative call, and macro forecasting is where
an LLM has the least information edge. The defensible use is a RISK VETO (step
aside from a sector that is narrow, expensive, and fighting the rate regime),
not alpha-seeking. Operationally it is the cheapest overlay to run (4 ETFs,
monthly, low turnover). Expect it to fail its kill switch; run it to test, not
because we believe it.

================================================================
DESIGN — one treatment sleeve vs the existing control
================================================================
  sector_top4_paper             (CONTROL)   — existing sleeve, no veto. Run by
                                              paper_rebalance / rebalance.bat.
  llm_overlay_sector_top4_paper (TREATMENT) — holds the same top-4 sectors at
                                              25% each EXCEPT sectors the LLM
                                              VETOs, whose 25% slot stays cash.
                                              Per-name invalidation price → exit
                                              that sector to cash on a daily
                                              close breach.

Veto => CASH (not redeployed into survivors) so the ONLY difference from the
control is the veto itself — same candidates, sizing, costs, dates.

================================================================
HOW A DECISION IS MADE (human / Claude in the loop, MACRO prompts)
================================================================
Each monthly rebalance, for EACH of the 4 candidate sectors:
  1. `sector_overlay_ops.py candidate`  -> prints the 4 sectors + macro prompts.
  2. Run the prompts vs CURRENT data (web + internal breadth), per sector.
  3. `sector_overlay_ops.py decide --ticker XLK --score N --verdict HOLD|VETO
        --invalidation PRICE --rationale "..."`  (once per sector).
  4. `sector_overlay_ops.py rebalance`  -> acts (refuses unless all 4 decided).

================================================================
PRE-COMMITTED KILL SWITCH
================================================================
Run 12 months / >=30 sector-decisions. KILL if EITHER (a) scores show no
positive rank-correlation with forward 1-month sector returns, OR (b) the
treatment does not beat sector_top4_paper net of costs.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timezone

from trading_bot.config import DB_PATH
from trading_bot.factors import sector_momentum
from trading_bot.strategies import sector_top4


# ---------- Frozen params (inherit the control's spec) ----------
STARTING_CASH     = sector_top4.STARTING_CASH
HALF_SPREAD_BPS   = sector_top4.HALF_SPREAD_BPS
TOP_N             = sector_top4.TOP_N          # 4
REBALANCE_FREQ    = "M"

CONTROL_STRATEGY   = "sector_top4_paper"
TREATMENT_STRATEGY = "llm_overlay_sector_top4_paper"


@dataclass(frozen=True)
class StrategySpec:
    name:            str = "sector_overlay"
    version:         str = "1.0.0"
    locked:          str = "2026-06-05"
    selection:       str = "top-4 of 11 SPDR sectors by 12-1 momentum"
    control_sleeve:  str = CONTROL_STRATEGY
    overlay_sleeve:  str = TREATMENT_STRATEGY
    starting_cash:   float = STARTING_CASH
    half_spread_bps: float = HALF_SPREAD_BPS
    top_n:           int = TOP_N
    rebalance:       str = REBALANCE_FREQ


SPEC = StrategySpec()


def candidates(as_of: date) -> list[tuple[str, float]]:
    """The top-TOP_N sector ETFs by 12-1 momentum at `as_of` (the same
    selection the control sleeve makes). Returns [(ticker, score), ...]."""
    scored = sector_momentum.rank_universe(None, as_of)
    return scored[:TOP_N]


def prompts(ticker: str) -> list[str]:
    """The 4 macro/top-down prompts for a sector go/no-go (see module docstring
    + the 2026-06-05 design). Each ends feeding a score / verdict / stop."""
    name = sector_momentum.SECTOR_NAMES.get(ticker, ticker)
    s = f"{ticker} ({name})"
    return [
        f"1) MACRO & RATE REGIME — {s}: current 10Y/2Y Treasury yields and "
        f"their 1-month direction; Fed cut/hold/hike odds; USD trend (and oil "
        f"if energy). Given {ticker}'s rate sensitivity "
        f"(long-duration vs rate-beneficiary vs cyclical), is the macro "
        f"backdrop a TAILWIND / NEUTRAL / HEADWIND for the next 1-3 months? "
        f"Cite the datapoints.",
        f"2) VALUATION & CROWDING — {s}: forward P/E vs its own 5-10yr "
        f"percentile; recent ETF fund flows; how CONCENTRATED recent gains are "
        f"(broad, or 2-3 mega-caps?); overbought signals (RSI, % above "
        f"200-DMA). Cheap/fair/expensive? Is the up-move broad or "
        f"narrow/fragile?",
        f"3) FUNDAMENTAL TREND — {s}: direction of forward earnings-estimate "
        f"REVISIONS, analyst breadth, and the single sector-specific catalyst "
        f"or risk that matters most this month. Are fundamentals CONFIRMING or "
        f"DIVERGING from the price momentum?",
        f"4) BEAR CASE + INVALIDATION — {s}: hardest near-term bear case for "
        f"holding a month; what's priced in; and an exact {ticker} price level "
        f"(e.g. close below 50-DMA, or -X%) at which the momentum thesis is "
        f"broken -> exit to cash.",
    ]


def record_decision(*, decision_date: date, ticker: str, score: float | None,
                    verdict: str, invalidation_level: float | None,
                    rationale: str | None) -> None:
    """Insert (or replace) one pre-committed sector decision for a date."""
    verdict = verdict.upper()
    if verdict not in ("HOLD", "VETO"):
        raise ValueError(f"verdict must be HOLD or VETO, got {verdict!r}")
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT OR REPLACE INTO sector_overlay_log "
            "(decision_date, ticker, score, verdict, invalidation_level, "
            " rationale, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (decision_date.isoformat(), ticker.upper(), score, verdict,
             invalidation_level, rationale, now),
        )
        conn.commit()
    finally:
        conn.close()


def decisions_for(decision_date: date) -> dict[str, dict]:
    """All decisions logged for an exact rebalance date, keyed by ticker."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM sector_overlay_log WHERE decision_date = ?",
            (decision_date.isoformat(),)).fetchall()
    finally:
        conn.close()
    return {r["ticker"]: dict(r) for r in rows}


def latest_decision_for(ticker: str, as_of: date) -> dict | None:
    """Most recent decision for one ticker with decision_date <= as_of."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM sector_overlay_log WHERE ticker = ? "
            "AND decision_date <= ? ORDER BY decision_date DESC, id DESC LIMIT 1",
            (ticker.upper(), as_of.isoformat())).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def all_decisions() -> list[dict]:
    """Full decision log, newest first (for the dashboard)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM sector_overlay_log "
            "ORDER BY decision_date DESC, ticker"
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]
