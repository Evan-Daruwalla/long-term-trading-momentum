"""Re-mark ONE already-existing paper_nav day for every sleeve. Dry-run by default.

WHY THIS EXISTS (2026-08-02, records CK/CL/CM). Two independent events left the
2026-07-31 NAV rows stale, and neither self-heals:

  1. The M7.3 KLAC repair (record CL) corrected 31 sleeves' `paper_portfolio.cash`
     by +$85,779.95. Their newest NAV row still carries the pre-repair cash.
  2. The record CI yfinance rate limit dropped the 07-30/07-31 closes, so those days
     were marked on CARRY-FORWARD prices; the backfill restored the real closes
     afterwards, leaving ~10 more sleeves' stored `total_nav` stale against the cache.

`mtm_catchup.py` cannot fix either: it only marks days that are MISSING for a sleeve,
and these rows exist. `paper_mtm --as-of` fixes one sleeve per process launch. This is
the 76-sleeve equivalent, in one process.

SCOPE, deliberately narrow: it rewrites exactly ONE date. It is NOT the M7.4 history
rewrite that record CK ruled out -- re-marking a broad span would silently restate NAV
for unrelated price revisions (price_cache is mutable by design: daily_price_refresh
re-downloads 30 days nightly with INSERT OR REPLACE). Re-marking a single recent day
whose staleness has a KNOWN, named cause is a different act, and the dry run proves
per sleeve which rows actually move before anything is written.

Guards match `paper_mtm` / `monthly_rebalance._mtm_phase` exactly: weekend skip,
pre-inception skip, and the coverage gate (a day below the publication floor is refused
unless --force, so this can never re-mark onto a partial bar).

Usage:
  python -m scripts.data_audit.remark_nav_day --date 2026-07-31
  python -m scripts.data_audit.remark_nav_day --date 2026-07-31 --execute
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date

from trading_bot.db import connect
from scripts.momentum import paper_mtm
from scripts.momentum.check_coverage import coverage_status

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("remark_nav_day")

# Below this the stored row is treated as already correct and left untouched, so a
# re-mark only ever rewrites rows that genuinely move.
CHANGE_TOL = 0.005


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="ISO date of the single day to re-mark.")
    ap.add_argument("--execute", action="store_true", help="Apply (default: dry run).")
    ap.add_argument("--force", action="store_true",
                    help="Re-mark even if that day's coverage is below the floor.")
    args = ap.parse_args()

    as_of = date.fromisoformat(args.date)
    if as_of.weekday() >= 5:
        log.error("%s is a weekend - no trading day to re-mark.", as_of)
        return 1

    with connect() as conn:
        cov = coverage_status(conn, as_of.isoformat())
        sleeves = [r["strategy_name"] for r in conn.execute(
            "SELECT strategy_name FROM paper_portfolio ORDER BY strategy_name")]
        stored = {r["strategy_name"]: r["total_nav"] for r in conn.execute(
            "SELECT strategy_name, total_nav FROM paper_nav WHERE nav_date=?",
            (as_of.isoformat(),))}

    log.info("coverage %s: %d closes vs floor %d -> %s",
             as_of, cov["count"], cov["floor"], "OK" if cov["ok"] else "BELOW FLOOR")
    if not cov["ok"] and not args.force:
        log.error("COVERAGE FAIL: refusing to re-mark %s on a partial bar "
                  "(pass --force to override).", as_of)
        return 2

    changed, unchanged, missing, skipped, failures = [], 0, [], 0, []
    for name in sleeves:
        try:
            inc = paper_mtm.inception_date(name)
            if as_of < inc:
                log.warning("SKIP pre-inception: %s (inception %s)", name, inc)
                skipped += 1
                continue
            nav = paper_mtm.compute_nav(name, as_of)
            old = stored.get(name)
            if old is None:
                missing.append((name, nav))
            elif abs(nav["total_nav"] - old) > CHANGE_TOL:
                changed.append((name, old, nav))
            else:
                unchanged += 1
                continue
            if args.execute:
                paper_mtm.write_nav(name, as_of, nav)
        except Exception:
            log.exception("FAILED: %s - continuing", name)
            failures.append(name)

    verb = "re-marked" if args.execute else "would change"
    for name, old, nav in changed:
        log.info("  %s %-32s $%12.2f -> $%12.2f  (%+.2f)",
                 verb, name, old, nav["total_nav"], nav["total_nav"] - old)
    for name, nav in missing:
        log.info("  %s %-32s   (no row) -> $%12.2f", verb, name, nav["total_nav"])

    log.info("%s %s: %d changed, %d new row(s), %d already correct, %d pre-inception "
             "skip(s), %d failure(s) - total net NAV delta $%+.2f",
             "RE-MARKED" if args.execute else "DRY RUN", as_of,
             len(changed), len(missing), unchanged, skipped, len(failures),
             sum(n["total_nav"] - o for _s, o, n in changed))
    if not args.execute:
        log.info("Nothing was written. Re-run with --execute to apply.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
