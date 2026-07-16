"""LLM-overlay experiment — discretionary veto on the top systematic pick.

================================================================
WHAT THIS IS (and is NOT)
================================================================
This is NOT a believed-in alpha source. It's a FALSIFIABLE TEST of the
hypothesis "an LLM equity-analysis overlay improves on just buying the
top systematic pick." The honest prior (see the 5-angle analysis in the
project record, 2026-05-30) is that it does NOT — no information edge,
un-walk-forwardable, re-derives factors we already own. We build it so the
idea gets tested instead of argued about, with a pre-committed kill switch.

================================================================
DESIGN — two parallel single-name sleeves
================================================================
Both start at $100k, hold ONE name, rebalance monthly. Candidate selection
is identical and mechanical: the #1 ranked name by mom_roa_6535's frozen
Z-score (0.65*Z_mom + 0.35*Z_roa) over the tradeable universe.

  mom_roa_top1_paper  (CONTROL)   — always buy the candidate. No veto.
  llm_overlay_mom_roa_top1_paper (TREATMENT) — buy the candidate ONLY if logged
                                     LLM decision is BUY; if VETO, hold cash.
                                     A pre-committed invalidation price is
                                     stored; if the daily close breaks it,
                                     exit to cash (the prompt-3 stop).

Isolating CONTROL vs TREATMENT is the only way to measure the LLM's
contribution. Same candidate, same costs, same dates — the ONLY difference
is the discretionary veto + stop.

================================================================
HOW A DECISION IS MADE (human / Claude in the loop)
================================================================
The LLM decision is an INPUT, not auto-generated inside the scheduled job
(we have no LLM API wired into the .bat pipeline, and pretending a stale
model has "current data" would be dishonest). Procedure each rebalance:

  1. `llm_overlay_ops.py candidate`  -> prints the candidate + the 3 prompts.
  2. Run the 3 prompts (deep dive / peer comp / devil's advocate) against
     CURRENT data (web tools).
  3. `llm_overlay_ops.py decide --ticker X --score N --verdict BUY|VETO
        --invalidation PRICE --rationale "..."`  -> logs it.
  4. `llm_overlay_ops.py rebalance --mode overlay`  -> acts on the decision.

If no decision is logged for the period, the overlay rebalance refuses to
trade (stays as-is) and warns — it will NOT silently degrade to the control.

================================================================
PRE-COMMITTED KILL SWITCH (the experiment's own invalidation)
================================================================
Run for 12 months / >=30 independent picks. KILL the overlay if EITHER:
  (a) LLM scores show no positive rank-correlation with forward 3-month
      returns (the scores carry no information), OR
  (b) llm_overlay_mom_roa_top1_paper does not beat mom_roa_top1_paper net of costs
      (the veto/stop adds no value over just holding the systematic pick).
Same bar that closed Form 4. Written down now so it can't be moved later.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timezone

from trading_bot.config import DB_PATH
from trading_bot.factors import mom_roa_zscore
from trading_bot.factors.universe import tradeable_universe
from trading_bot.strategies import mom_roa_6535


# ---------- Frozen params ----------
STARTING_CASH    = 100_000.0
HALF_SPREAD_BPS  = 5.0
REBALANCE_FREQ   = "M"
TOP_N            = 1                       # single most-concentrated name
W_MOM            = mom_roa_6535.W_MOM      # selection inherits the deployed weights
W_ROA            = mom_roa_6535.W_ROA

CONTROL_STRATEGY = "mom_roa_top1_paper"
OVERLAY_STRATEGY = "llm_overlay_mom_roa_top1_paper"


@dataclass(frozen=True)
class StrategySpec:
    name:            str = "llm_overlay"
    version:         str = "1.0.0"
    locked:          str = "2026-05-31"
    selection:       str = "top-1 by mom_roa_6535 Z-score (0.65 mom / 0.35 roa)"
    control_sleeve:  str = CONTROL_STRATEGY
    overlay_sleeve:  str = OVERLAY_STRATEGY
    starting_cash:   float = STARTING_CASH
    half_spread_bps: float = HALF_SPREAD_BPS
    rebalance:       str = REBALANCE_FREQ


SPEC = StrategySpec()


def candidate(as_of: date) -> tuple[str, float] | None:
    """The mechanical candidate: #1 name by mom_roa_6535 ranking at `as_of`.
    Returns (ticker, z_score) or None if the universe is empty."""
    universe = tradeable_universe(as_of)
    if not universe:
        return None
    ranker = mom_roa_zscore.make_rank_fn(W_MOM, W_ROA)
    scored = ranker(universe, as_of)
    if not scored:
        return None
    return scored[0]


def record_decision(*, decision_date: date, ticker: str, score: float | None,
                    verdict: str, invalidation_level: float | None,
                    rationale: str | None) -> None:
    """Insert (or replace) the pre-committed LLM decision for a rebalance date."""
    verdict = verdict.upper()
    if verdict not in ("BUY", "VETO"):
        raise ValueError(f"verdict must be BUY or VETO, got {verdict!r}")
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT OR REPLACE INTO llm_overlay_log "
            "(decision_date, ticker, score, verdict, invalidation_level, "
            " rationale, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (decision_date.isoformat(), ticker, score, verdict,
             invalidation_level, rationale, now),
        )
        conn.commit()
    finally:
        conn.close()


def latest_decision(as_of: date) -> dict | None:
    """Most recent logged decision with decision_date <= as_of, or None."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM llm_overlay_log WHERE decision_date <= ? "
            "ORDER BY decision_date DESC, id DESC LIMIT 1",
            (as_of.isoformat(),)).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def latest_decision_for(ticker: str, as_of: date) -> dict | None:
    """Most recent decision for one ticker with decision_date <= as_of.
    Use this (not latest_decision) whenever the caller has a specific held
    name: the cascade sleeve logs OTHER tickers into this same table, so a
    ticker-blind LIMIT 1 can pair a position with a different name's stop.
    Mirror of sector_overlay.latest_decision_for."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM llm_overlay_log WHERE ticker = ? "
            "AND decision_date <= ? ORDER BY decision_date DESC, id DESC LIMIT 1",
            (ticker.upper(), as_of.isoformat())).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def decision_for(decision_date: date) -> dict | None:
    """The decision logged for an exact rebalance date, or None."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM llm_overlay_log WHERE decision_date = ? LIMIT 1",
            (decision_date.isoformat(),)).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def decision_for_ticker(decision_date: date, ticker: str) -> dict | None:
    """The decision logged for an exact (rebalance date, ticker), or None.
    Use this when multiple names may be logged per date (the cascade sleeve
    evaluates several) so a consumer gets the decision for its OWN candidate
    rather than an arbitrary LIMIT-1 row."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM llm_overlay_log WHERE decision_date = ? AND ticker = ? "
            "ORDER BY id DESC LIMIT 1",
            (decision_date.isoformat(), ticker.upper())).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def all_decisions() -> list[dict]:
    """Full decision log, newest first (for the dashboard)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM llm_overlay_log ORDER BY decision_date DESC, id DESC"
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]
