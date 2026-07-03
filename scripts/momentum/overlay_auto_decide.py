"""Option B (fully-unattended): auto-generate the monthly LLM overlay decisions
via the Anthropic API, so a scheduled job can run the whole rebalance with no
human in the loop.

================================================================================
STATUS: SCAFFOLD — UNTESTED pending a credential. Activation needs BOTH:
  1. pip install anthropic            (into .venv)
  2. set ANTHROPIC_API_KEY            (Console key; per-run cost ~once a month)
Neither was present on this machine when this was written (2026-06-13), so the
API path has NOT been executed end-to-end. Run it once with --dry-run after
setting the key and eyeball the logged decisions before trusting the scheduler.
See docs/overlay_decision_runbook.md "Option B activation".
================================================================================

What it does (mirrors the in-session Option A flow, but headless):
  - SECTOR overlay: for each of the 4 candidate sectors, runs the 4 macro prompts
    against the live web (web_search server tool), then a structured HOLD/VETO
    verdict, and logs it via sector_overlay.record_decision.
  - STOCK overlay: only when the #1 mom_roa name CHANGED from the held name —
    runs the 3 analyst prompts + structured BUY/VETO, logs via
    llm_overlay.record_decision.

SAFE-FAIL: if the API key is missing, the import fails, or any decision can't be
produced, it logs NOTHING and exits non-zero. rebalance.bat then REFUSES the
overlay rebalance (it requires decisions), so a broken auto-decide can never
cause a bad trade — it just leaves the overlays un-rebalanced for a human.

Two-step LLM call per decision (research -> decide) keeps the web-search server
loop separate from the structured-output constraint.

Usage: python -m scripts.momentum.overlay_auto_decide [--as-of YYYY-MM-DD] [--dry-run]
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date

from trading_bot.execution import market_data, paper_trader
from trading_bot.factors import sector_momentum
from trading_bot.strategies import llm_overlay, sector_overlay

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("overlay_auto_decide")

MODEL = "claude-opus-4-8"
WEB_TOOL = {"type": "web_search_20260209", "name": "web_search"}

SECTOR_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["verdict", "score", "invalidation", "rationale"],
    "properties": {
        "verdict": {"type": "string", "enum": ["HOLD", "VETO"]},
        "score": {"type": "integer"},      # 1-10 conviction it beats cash next month
        "invalidation": {"type": ["number", "null"]},
        "rationale": {"type": "string"},
    },
}
STOCK_SCHEMA = {**SECTOR_SCHEMA, "properties": {**SECTOR_SCHEMA["properties"],
    "verdict": {"type": "string", "enum": ["BUY", "VETO"]}}}

STOCK_PROMPTS = [
    "1) Equity-analyst deep dive: business model, financials (growth, margins, debt, "
    "cash flow), forward outlook, valuation vs its own history, catalysts + risks (6-18mo).",
    "2) Compare to 3-4 closest competitors on growth, margins, valuation multiples. "
    "Cheap / fair / expensive? Value or trap?",
    "3) Devil's advocate on a LONG: hardest bear case, what's priced in, what I'm ignoring. "
    "Give an exact invalidation price.",
]


def _client():
    import anthropic  # lazy: only needed when actually running the API path
    return anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env


def _decide(client, header: str, prompts: list[str], schema: dict) -> dict:
    """Two-step: (1) live-web research brief, (2) structured verdict."""
    research_msg = (header + "\n\nRun these prompts against CURRENT web data and write "
                    "a tight findings brief (cite datapoints):\n" + "\n".join(prompts))
    # Step 1 — research with the web_search server tool (handle pause_turn loop).
    messages = [{"role": "user", "content": research_msg}]
    for _ in range(6):
        resp = client.messages.create(
            model=MODEL, max_tokens=8000, thinking={"type": "adaptive"},
            tools=[WEB_TOOL], messages=messages)
        if resp.stop_reason == "pause_turn":
            messages = [messages[0], {"role": "assistant", "content": resp.content}]
            continue
        break
    brief = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    # Step 2 — structured verdict from the brief (no tools).
    dec = client.messages.create(
        model=MODEL, max_tokens=1500,
        output_config={"format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content":
                   f"{header}\n\nFindings brief:\n{brief}\n\nReturn the decision per the schema. "
                   "Score = 1-10 conviction it beats CASH over the next ~1 month. "
                   "Be honest; do not manufacture a veto."}])
    import json
    return json.loads(next(b.text for b in dec.content if getattr(b, "type", "") == "text"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=date.today().isoformat())
    ap.add_argument("--dry-run", action="store_true", help="decide + print, don't log")
    args = ap.parse_args()
    as_of = date.fromisoformat(args.as_of)

    try:
        client = _client()
    except Exception as e:
        log.error("Anthropic client unavailable (%s). Install `anthropic` + set "
                  "ANTHROPIC_API_KEY. Logging nothing; rebalance will refuse the "
                  "overlays. See runbook Option B activation.", e)
        return 1

    market_data.preload_caches()
    owed = 0
    try:
        # ---- SECTOR overlay: all 4 candidates each rebalance ----
        cands = sector_overlay.candidates(as_of)
        decided = sector_overlay.decisions_for(as_of)
        for ticker, _ in cands:
            if ticker in decided:
                continue
            name = sector_momentum.SECTOR_NAMES.get(ticker, ticker)
            d = _decide(client, f"Macro risk-veto on sector ETF {ticker} ({name}).",
                        sector_overlay.prompts(ticker), SECTOR_SCHEMA)
            log.info("SECTOR %s -> %s score=%s", ticker, d["verdict"], d["score"])
            if not args.dry_run:
                sector_overlay.record_decision(
                    decision_date=as_of, ticker=ticker, score=d["score"],
                    verdict=d["verdict"], invalidation_level=d["invalidation"],
                    rationale=d["rationale"])
            owed += 1

        # ---- STOCK overlay: only on a name change ----
        cand = llm_overlay.candidate(as_of)
        if cand:
            ticker = cand[0]
            held = paper_trader.list_open(llm_overlay.CONTROL_STRATEGY)
            held_t = held[0]["ticker"] if held else None
            if ticker != held_t and llm_overlay.decision_for(as_of) is None:
                d = _decide(client, f"Single-name long thesis on {ticker}.",
                            [p.replace("deep dive", f"deep dive on {ticker}") for p in STOCK_PROMPTS],
                            STOCK_SCHEMA)
                log.info("STOCK %s -> %s score=%s", ticker, d["verdict"], d["score"])
                if not args.dry_run:
                    llm_overlay.record_decision(
                        decision_date=as_of, ticker=ticker, score=d["score"],
                        verdict=d["verdict"], invalidation_level=d["invalidation"],
                        rationale=d["rationale"])
                owed += 1
    except Exception as e:
        log.error("Auto-decide failed mid-run (%s). Some decisions may be missing; "
                  "rebalance will refuse those overlays. Re-run or decide by hand.", e)
        return 1

    log.info("Auto-decide done: %d decision(s) %s.", owed,
             "previewed" if args.dry_run else "logged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
