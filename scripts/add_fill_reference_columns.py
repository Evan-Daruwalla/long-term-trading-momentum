"""Add fill-provenance columns to paper_positions (record CU). Dry-run by default.

WHY. A fill's reference price is currently unrecoverable after about a month.
`paper_rebalance` prices every fill as `last_close_on_or_before(ticker, as_of) *
(1 +/- half_spread)` and persists only the spread-adjusted result, so the raw
close has to be re-derived from `price_cache` later. But `price_cache` is
deliberately mutable — `daily_price_refresh` re-downloads the last 30 days for
every ticker with INSERT OR REPLACE by design (record CK). Measured 2026-08-05:
2-day-old fills reproduce their close 34/34 exactly; 29-day-old fills reproduce
it 0/98, matching NO stored close on ANY date, mean absolute divergence 1.384%
and up to 5.92%. So slippage was only ever measurable for about a month after a
rebalance, and nobody knew.

These four columns record the reference AT FILL TIME instead. `*_ref_date` is
kept as well as the price because `last_close_on_or_before` CARRIES FORWARD —
the close a fill used is not always the rebalance date's.

Purely additive: four nullable columns, no existing column touched, no row
rewritten, no arithmetic changed. Existing rows stay NULL forever (July is gone;
nothing recovers it). ALTER TABLE ADD COLUMN on SQLite is a metadata-only
operation — it does not rewrite the 5 GB file.

Usage:
    python -m scripts.add_fill_reference_columns                 # dry run
    python -m scripts.add_fill_reference_columns --execute
    python -m scripts.add_fill_reference_columns --db copy.db --execute
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from trading_bot.config import DB_PATH

COLUMNS = [
    ("entry_ref_close", "REAL"),
    ("entry_ref_date", "TEXT"),
    ("exit_ref_close", "REAL"),
    ("exit_ref_date", "TEXT"),
]


def existing_columns(conn) -> set[str]:
    return {r[1] for r in conn.execute("PRAGMA table_info(paper_positions)")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=None, help="DB path (default: live var/trades.db).")
    ap.add_argument("--execute", action="store_true", help="Actually apply.")
    args = ap.parse_args()

    db = Path(args.db) if args.db else DB_PATH
    if not db.exists():
        print(f"ERROR: {db} does not exist.")
        return 2

    # Read-only probe first, so a dry run never opens the live DB for writing.
    ro = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    have = existing_columns(ro)
    n_rows = ro.execute("SELECT COUNT(*) FROM paper_positions").fetchone()[0]
    ro.close()

    todo = [(c, t) for c, t in COLUMNS if c not in have]
    print(f"DB: {db}")
    print(f"paper_positions: {n_rows} row(s), {len(have)} column(s)")
    for c, t in COLUMNS:
        print(f"  {c:<16} {t:<5} {'ALREADY PRESENT' if c in have else 'WILL ADD'}")

    if not todo:
        print("\nNothing to do - all four columns already present (idempotent).")
        return 0
    if not args.execute:
        print(f"\nDRY RUN - {len(todo)} column(s) would be added. "
              f"Re-run with --execute to apply.")
        return 0

    w = sqlite3.connect(db)
    for c, t in todo:
        w.execute(f"ALTER TABLE paper_positions ADD COLUMN {c} {t}")
        print(f"  ADDED {c}")
    w.commit()
    after = existing_columns(w)
    w.close()
    missing = [c for c, _ in COLUMNS if c not in after]
    if missing:
        print(f"\nFAILED - still missing: {missing}")
        return 1
    print(f"\nApplied. paper_positions now has {len(after)} columns; "
          f"{n_rows} existing row(s) carry NULL provenance (expected).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
