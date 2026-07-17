"""Single-process monthly rebalance + mark-to-market for the SYSTEMATIC sleeves.

WHY ONE PROCESS (audit 2026-07-17, fix #3; record Appendix CG)
--------------------------------------------------------------
rebalance.bat used to shell out one OS process per sleeve: ~29
`python -m scripts.momentum.paper_rebalance` calls + ~30 `paper_mtm --force`
calls. Every fresh Python process re-runs `market_data.preload_caches()`, which
loads the whole price_cache (~37.5M rows) into RAM — about 44s each. Across ~59
processes that is ~25 min of pure re-preload waste on the monthly run, doing no
useful work. This dispatcher runs the SAME sleeves, SAME args, SAME order in ONE
process. `preload_caches()` is idempotent (guarded by market_data._MEM_LOADED),
so the cache is loaded ONCE up front and every sleeve reuses the warm copy.

SCOPE — what this replaces, and what it deliberately does NOT
------------------------------------------------------------
Replaces the systematic-family blocks of rebalance.bat only:
  * the 6 May systematic sleeves (mom_v1/v2, mom_roa_6535, residual_roa_6535,
    sector_top4, sector_top4_full),
  * the 4 07-01-cohort duplicates (`_0701`),
  * the 19-point residual weight ladder (MONTHLY cadence; names come straight
    from seed_residual_cadence_ladder so this list can never drift from the seed),
  * the spy_benchmark_paper mark (buy-and-hold: MTM only, never rebalanced).

Left in rebalance.bat, untouched, and run OUTSIDE this process:
  * daily_price_refresh (+ its abort guard), verify_run, stamp_rebalance_log,
    alpaca_sync — orchestration the bat owns,
  * the LLM-experiment sleeves (llm_overlay_ops / sector_overlay_ops /
    llm_cascade_ops rebalances AND their `paper_mtm --force` marks): those
    rebalance through the *_ops modules and each MTM depends on its ops step,
    so they must stay in the bat and run AFTER this dispatcher,
  * spy_benchmark_0701_paper (seeded by seed_spy_benchmark, not marked here),
  * the WEEKLY / BIWEEKLY residual ladders (ladder_forward_rebalance.py owns those).

BEHAVIOUR MIRRORED FROM THE BAT LINES
-------------------------------------
  * rebalance == `paper_rebalance --strategy X --top-n N --broker-realistic`:
    as_of=today, starting_cash + half_spread_bps = paper_rebalance's own defaults
    (momentum_v2.STARTING_CASH / .HALF_SPREAD_BPS), broker_realistic=True.
  * MTM == `paper_mtm --strategy X --force`: compute_nav + write_nav with the
    coverage gate bypassed (on a rebalance day held names are guaranteed present,
    record BQ). The weekend + pre-inception guards that --force does NOT bypass
    are kept (they protect against holiday / StartWhenAvailable pollution rows).
  * a per-sleeve failure is logged loudly and the loop CONTINUES — a failed
    `paper_rebalance` line never aborted the bat. The process exits NONZERO if
    any sleeve failed so the bat can print a warning.

DEVIATION FROM THE OLD BAT: a sleeve named here but missing from paper_portfolio
is loudly skipped (counted as a failure), NOT silently created at $100k/today.
Every current sleeve is pre-seeded (backdated replay), so this changes nothing
today; it just refuses to mint a wrong-inception sleeve and keeps --dry-run a
pure read.

ROSTER: REBALANCE_SLEEVES + MTM_SLEEVES below are the authority for the monthly
systematic run and MUST stay in sync with the sleeve roster in HANDOFF.md.

Usage:
  python -m scripts.momentum.monthly_rebalance --dry-run   # plan + dry rebalances, no writes
  python -m scripts.momentum.monthly_rebalance             # LIVE (the monthly scheduled task)
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import date

from scripts.momentum.seed_residual_cadence_ladder import WEIGHTS, CADENCES

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("monthly_rebalance")

# --- Sleeve roster (keep in sync with HANDOFF.md) ---------------------------

# (strategy_name, top_n) — top_n is the ONLY per-sleeve arg the bat lines vary;
# every line also passes --broker-realistic and relies on paper_rebalance's
# default starting_cash / half_spread_bps.
SYSTEMATIC_SLEEVES: list[tuple[str, int]] = [
    ("mom_v1_paper", 100),
    ("mom_v2_paper", 50),
    ("mom_roa_6535_paper", 50),
    ("residual_roa_6535_paper", 50),
    ("sector_top4_paper", 4),
    ("sector_top4_full_paper", 4),
    ("mom_v1_0701_paper", 100),
    ("mom_v2_0701_paper", 50),
    ("mom_roa_6535_0701_paper", 50),
    ("residual_roa_6535_0701_paper", 50),
]

# 19-point residual weight ladder, MONTHLY cadence, top-50. Names generated from
# the same WEIGHTS/CADENCES the ladder was seeded with, so the list cannot drift.
LADDER_NAME = CADENCES["monthly"][1]   # lambda mm, rr -> "residual_w{mm}{rr}_paper"
LADDER_SLEEVES: list[str] = [LADDER_NAME(mm, rr) for mm, rr in WEIGHTS]

# Rebalance phase: 10 systematic/cohort + 19 ladder = 29 sleeves (bat order).
REBALANCE_SLEEVES: list[tuple[str, int]] = (
    SYSTEMATIC_SLEEVES + [(name, 50) for name in LADDER_SLEEVES]
)

# MTM phase: spy_benchmark_paper first (bat marks it before the systematic MTMs),
# then the 10 systematic/cohort, then the 19 ladder = 30 sleeves (bat order).
MTM_SLEEVES: list[str] = (
    ["spy_benchmark_paper"]
    + [name for name, _ in SYSTEMATIC_SLEEVES]
    + LADDER_SLEEVES
)


def _print_plan(as_of: date, dry_run: bool) -> None:
    log.info("MONTHLY REBALANCE DISPATCHER — %s — as_of=%s",
             "DRY RUN (no writes)" if dry_run else "LIVE", as_of)
    log.info("REBALANCE PHASE: %d sleeves", len(REBALANCE_SLEEVES))
    for name, top_n in REBALANCE_SLEEVES:
        log.info("    rebalance  %-32s top-%-3d broker_realistic=True", name, top_n)
    log.info("MTM PHASE: %d sleeves (paper_mtm --force equivalent)", len(MTM_SLEEVES))
    for name in MTM_SLEEVES:
        log.info("    mtm        %s", name)


def _rebalance_phase(as_of, dry_run, paper_rebalance, momentum_v2, existing) -> list[str]:
    """paper_rebalance.rebalance() for every REBALANCE_SLEEVES entry. Missing
    sleeves + exceptions are logged loudly and counted; the loop never stops."""
    failures: list[str] = []
    for name, top_n in REBALANCE_SLEEVES:
        if name not in existing:
            log.error("REBALANCE SKIP: sleeve %r not in paper_portfolio — roster "
                      "drift; refusing to create it. Fix REBALANCE_SLEEVES / seed "
                      "the sleeve.", name)
            failures.append(name)
            continue
        try:
            log.info("=== REBALANCE %s (top-%d)%s ===",
                     name, top_n, " [DRY]" if dry_run else "")
            n = paper_rebalance.rebalance(
                as_of=as_of, strategy_name=name,
                starting_cash=momentum_v2.STARTING_CASH,
                top_n=top_n, half_spread_bps=momentum_v2.HALF_SPREAD_BPS,
                dry_run=dry_run, broker_realistic=True,
            )
            log.info("    %s: %d position change(s)%s",
                     name, n, " (dry-run, nothing written)" if dry_run else "")
        except Exception:
            log.exception("REBALANCE FAILED: %s — continuing to next sleeve", name)
            failures.append(name)
    return failures


def _mtm_phase(as_of, dry_run, paper_mtm, existing) -> list[str]:
    """`paper_mtm --force` equivalent for every MTM_SLEEVES entry: compute_nav +
    write_nav with the coverage gate bypassed. Keeps the weekend + pre-inception
    guards that --force does NOT bypass. Failures logged loudly, loop continues."""
    failures: list[str] = []
    weekend = as_of.weekday() >= 5
    for name in MTM_SLEEVES:
        if name not in existing:
            log.error("MTM SKIP: sleeve %r not in paper_portfolio — roster drift.", name)
            failures.append(name)
            continue
        try:
            if weekend:
                log.info("MTM %s: %s is a weekend — skipping (matches paper_mtm).",
                         name, as_of)
                continue
            inc = paper_mtm.inception_date(name)
            if as_of < inc:
                log.warning("MTM %s: as_of %s < inception %s — skipping "
                            "(matches paper_mtm).", name, as_of, inc)
                continue
            nav = paper_mtm.compute_nav(name, as_of)
            if dry_run:
                log.info("[DRY] MTM %s: NAV@%s $%.2f (%d open) — not written",
                         name, as_of, nav["total_nav"], nav["n_open"])
            else:
                paper_mtm.write_nav(name, as_of, nav)
                log.info("MTM %s: NAV@%s $%.2f (%d open)",
                         name, as_of, nav["total_nav"], nav["n_open"])
        except Exception:
            log.exception("MTM FAILED: %s — continuing to next sleeve", name)
            failures.append(name)
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="Plan + dry rebalances + NAV compute; write NOTHING.")
    ap.add_argument("--as-of", default=None,
                    help="Override today (ISO date), for testing. Default: today.")
    args = ap.parse_args()

    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()

    # Deferred heavy imports (mirror ladder_forward_rebalance / seed_* pattern).
    from scripts.momentum import paper_rebalance, paper_mtm
    from trading_bot.execution import market_data
    from trading_bot.strategies import momentum_v2
    from trading_bot.db import connect

    # Preload the price/sector cache ONCE — the whole point of this dispatcher.
    # Idempotent, so paper_rebalance's own internal preload calls become no-ops.
    market_data.preload_caches()

    with connect() as conn:
        existing = {r["strategy_name"] for r in conn.execute(
            "SELECT strategy_name FROM paper_portfolio")}

    _print_plan(as_of, args.dry_run)

    t0 = time.time()
    reb_fail = _rebalance_phase(as_of, args.dry_run, paper_rebalance, momentum_v2, existing)
    mtm_fail = _mtm_phase(as_of, args.dry_run, paper_mtm, existing)
    elapsed = time.time() - t0

    failures = reb_fail + mtm_fail
    log.info("=" * 60)
    log.info("DISPATCHER DONE (%s) in %.0fs — %d rebalance + %d mtm sleeves, "
             "%d failure(s)%s",
             "DRY" if args.dry_run else "LIVE", elapsed,
             len(REBALANCE_SLEEVES), len(MTM_SLEEVES), len(failures),
             (": " + ", ".join(failures)) if failures else "")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
