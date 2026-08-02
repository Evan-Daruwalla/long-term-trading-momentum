"""One-time migration: add the price_cache date index (audit 2026-07-28).

WHY. price_cache (37.5M rows) carried only its PK autoindex on
(ticker, kind, key_date). Every date-oriented query -- "how many closes landed
on day D", "what were the last N trading days" -- therefore scanned the whole
table. That is the shape the nightly pipeline runs constantly: check_coverage,
mtm_catchup, verify_run's calendar, and ladder_forward_rebalance's due-ness
check all ask date questions, and the 2026-07-27 daily run spent ~90s doing it
(var/last_daily_run.log stage stamps 17:16:45 -> 17:18:15).

MEASURED on a full-size copy of the live DB (4.77 GB, 37,580,576 rows), never
on the live DB:

    query                          before     after
    coverage_by_date GROUP BY      8.258s     0.005s   SCAN -> USING INDEX
    count_for_one_date             4.415s     0.001s   SCAN -> SEARCH (key_date=?)
    prior_days range               9.170s     0.016s   SCAN -> SEARCH (key_date<?)

    build 16.2s, +308 MB, and all three queries returned byte-identical results.

The index is PARTIAL (kind='close' AND price IS NOT NULL) because that is the
predicate every one of those callers uses; a full index would cost roughly
double the disk to answer the same questions.

SAFETY. Adding an index changes no row and no query result -- it only gives the
planner a cheaper path. It is fully reversible:
    DROP INDEX idx_pc_close_date;
Run the frozen regression tests afterwards regardless (project rule: any change,
however "obviously unrelated", must leave d=+/-0.0000pp).

Usage:
  python -m scripts.add_price_cache_date_index            # dry run: report only
  python -m scripts.add_price_cache_date_index --execute  # create the index
"""
from __future__ import annotations

import argparse
import logging
import time

from trading_bot.db import connect

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("add_price_cache_date_index")

INDEX_NAME = "idx_pc_close_date"
INDEX_SQL = (f"CREATE INDEX IF NOT EXISTS {INDEX_NAME} ON price_cache(key_date) "
             f"WHERE kind='close' AND price IS NOT NULL")

# The query the nightly coverage gate runs; used to prove the planner picks the
# index up after creation.
PROBE_SQL = ("SELECT key_date, COUNT(*) FROM price_cache WHERE kind='close' "
             "AND price IS NOT NULL GROUP BY key_date ORDER BY key_date DESC LIMIT 10")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true",
                    help="Actually create the index (default: report only).")
    args = ap.parse_args()

    with connect() as conn:
        existing = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
            (INDEX_NAME,)).fetchone()
        if existing:
            log.info("%s already exists; nothing to do.", INDEX_NAME)
            plan = conn.execute("EXPLAIN QUERY PLAN " + PROBE_SQL).fetchall()
            log.info("probe plan: %s", " | ".join(str(p[-1]) for p in plan))
            return 0

        plan = conn.execute("EXPLAIN QUERY PLAN " + PROBE_SQL).fetchall()
        log.info("BEFORE plan: %s", " | ".join(str(p[-1]) for p in plan))

        if not args.execute:
            log.info("DRY RUN. Re-run with --execute to create %s.", INDEX_NAME)
            return 0

        t = time.perf_counter()
        conn.execute(INDEX_SQL)
        log.info("created %s in %.1fs", INDEX_NAME, time.perf_counter() - t)

    # Reopen so the planner reflects the committed index.
    with connect() as conn:
        plan = conn.execute("EXPLAIN QUERY PLAN " + PROBE_SQL).fetchall()
        detail = " | ".join(str(p[-1]) for p in plan)
        log.info("AFTER plan: %s", detail)
        if INDEX_NAME not in detail:
            log.error("index created but planner is NOT using it - investigate.")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
