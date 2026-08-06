"""LLM-cascade overlays — the 'always invested' variant (the 3rd sleeve pair).

================================================================
WHAT THIS IS (and how it differs from the cash overlays)
================================================================
The cash overlays (llm_overlay / sector_overlay) treat a VETO as 'step aside to
CASH'. These cascade sleeves instead treat a VETO as 'skip to the next-best
candidate' and stay FULLY INVESTED. So they test the LLM as an ACTIVE SELECTOR
(does LLM-approved re-selection beat the raw momentum pick?) rather than as a
binary risk-veto. Built 2026-06-30 at the user's request as a THIRD experiment,
run alongside (not replacing) the cash overlays so the clean veto-vs-cash signal
is preserved.

Controls are SHARED with the cash overlays:
  stock  : control = mom_roa_top1_paper , cascade = llm_cascade_top1_paper
  sector : control = sector_top4_paper  , cascade = llm_cascade_sector4_paper

DECISIONS ARE SHARED with the cash overlays' logs (llm_overlay_log /
sector_overlay_log) — a BUY/VETO judgment on a name is the same regardless of
which sleeve consumes it, so we never double-log. The cascade just reads MORE of
the ranking (the cash sleeves only need #1 / the top-4).

ALWAYS-INVESTED FALLBACKS (so a sleeve is never idle):
  stock : hold the first BUY walking down the top-CASCADE_DEPTH names; if none
          is approved, fall back to the raw #1.
  sector: hold the first 4 HOLDs walking down all 11 sectors; if fewer than 4
          are approved, fill the remaining slots with the highest-momentum
          sectors (regardless of veto).

NO STOP ENFORCEMENT — BY DESIGN (decided by Evan 2026-08-05, record CR):
  These two sleeves have no `check-invalidation` path and `daily.bat` does not
  run one for them. That is deliberate, not an omission. The invalidation stop
  exits a position to CASH; "always invested" is this arm's entire distinction
  from the cash overlays, so bolting a stop-to-cash onto it would make it a
  hybrid of the two treatments and destroy the clean three-way comparison
  (control / veto-to-cash / cascade-to-next-name). The decisions these sleeves
  read DO carry an `invalidation_level` — it is written for, and consumed by,
  the cash-overlay sleeve only; the cascade ignores that column.

  THE COST, STATED PLAINLY: these sleeves have no downside control of any kind.
  A cascade pick rides to zero. Their drawdowns are therefore NOT comparable to
  the cash overlays' on a risk-adjusted basis, and any read of the experiment
  must say so. A stop-to-CASCADE (stop fires, walk to the next candidate) would
  preserve always-invested AND add downside control, but it is a new strategy
  rule mid-experiment and needs a mid-month re-pick rule that does not exist —
  considered and NOT taken on 2026-08-05.

  This was found by the 2026-08-05 audit (finding E1/6) as an undocumented gap,
  after being flagged twice in `daily_report.md` and never promoted to a spec.
  It is documented here, in `HANDOFF.md`, and in `docs/overlay_decision_runbook.md`
  so it can never again read as an oversight.

Honest prior: the bar is HIGH. Control already holds the momentum #1 / top-4, so
the cascade can only differ by replacing a high-momentum name with a LOWER one
the LLM prefers — i.e. it must out-PICK raw momentum, a harder claim than the
cash version's "cash beats a name I distrust". Same 12mo / >=30-pick kill switch.
"""
from __future__ import annotations

from datetime import date

from trading_bot.factors import mom_roa_zscore, sector_momentum
from trading_bot.factors.universe import tradeable_universe
from trading_bot.strategies import llm_overlay, sector_overlay

STARTING_CASH = 100_000.0
HALF_SPREAD_BPS = 5.0
CASCADE_DEPTH = 10          # max ranks to walk for the stock cascade
SECTOR_SLOTS = sector_overlay.TOP_N   # 4

STOCK_CASCADE_STRATEGY = "llm_cascade_top1_paper"
SECTOR_CASCADE_STRATEGY = "llm_cascade_sector4_paper"


# ---------------- stock cascade ----------------

def stock_ranking(as_of: date, n: int = CASCADE_DEPTH) -> list[tuple[str, float]]:
    """Top-`n` names by the mom_roa_6535 Z-score (same selection the cash
    overlay's #1 comes from), in rank order."""
    universe = tradeable_universe(as_of)
    if not universe:
        return []
    ranker = mom_roa_zscore.make_rank_fn(llm_overlay.W_MOM, llm_overlay.W_ROA)
    return ranker(universe, as_of)[:n]


def stock_pick(as_of: date) -> tuple[str, float, bool] | None:
    """The cascade's chosen name: the first name (walking down the top-DEPTH)
    with a logged BUY decision. If none is approved, fall back to the raw #1.
    Returns (ticker, score, is_fallback) or None if the universe is empty."""
    ranked = stock_ranking(as_of)
    if not ranked:
        return None
    for ticker, z in ranked:
        dec = llm_overlay.decision_for_ticker(as_of, ticker)
        if dec and dec["verdict"] == "BUY":
            return ticker, z, False
    ticker, z = ranked[0]
    return ticker, z, True


# ---------------- sector cascade ----------------

def sector_ranking(as_of: date) -> list[tuple[str, float]]:
    """All SPDR sectors by 12-1 momentum, rank order."""
    return sector_momentum.rank_universe(None, as_of)


def sector_picks(as_of: date, k: int = SECTOR_SLOTS) -> tuple[list[str], list[str]]:
    """The cascade's chosen `k` sectors: the first `k` (walking down momentum)
    with a logged HOLD decision; if fewer than `k` are approved, fill the rest
    with the highest-momentum sectors (regardless of veto) so it stays fully
    invested. Returns (picks, approved) where `approved` are the HOLD-backed
    ones (the rest are momentum fallback)."""
    ranked = sector_ranking(as_of)
    if not ranked:
        return [], []
    decisions = sector_overlay.decisions_for(as_of)
    approved = []
    for t, _score in ranked:
        d = decisions.get(t)
        if d and d["verdict"] == "HOLD":
            approved.append(t)
            if len(approved) == k:
                break
    picks = list(approved)
    if len(picks) < k:
        for t, _score in ranked:
            if t not in picks:
                picks.append(t)
                if len(picks) == k:
                    break
    return picks[:k], approved
