"""Rotating backup of var/trades.db (PRD M5.1).

Uses SQLite ``VACUUM INTO`` for a transactionally-consistent snapshot — a bare
file copy of a live WAL database can catch a torn write, so we never do that.
Keeps the N most recent ``var/backups/trades_YYYY-MM-DD.db`` and deletes older
ones. NEVER touches ``var/trades.db.bak_pre_spike_cleanup`` (the frozen founding
backup) — it lives in ``var/``, not ``var/backups/``, and does not match the
``trades_*.db`` glob, so it is safe by construction; the guard below is belt-and-
suspenders. Aborts if free disk is under 2x the DB size.

WRITE-VALIDATE-RENAME (audit 2026-08-05, finding E6). Rotation counts files by
NAME, so a half-written backup used to count as a good generation and evict a
real one — and because its name carries today's date it sorted NEWEST, so it
would be retained while the good copies aged out. Two more Sundays of that and
all three generations are junk, discovered only during a restore. Worse, the
same-day-rerun path unlinked the existing backup BEFORE starting the new VACUUM,
so a failure there destroyed a good generation and produced nothing.
Now: VACUUM into ``<name>.db.part`` (which the ``trades_*.db`` glob cannot
match), validate it, and only then atomically replace the target. A failed or
invalid write leaves every existing generation untouched and exits nonzero
WITHOUT rotating.

Usage:
  python -m scripts.backup_trades_db
  python -m scripts.backup_trades_db --keep 3
  python -m scripts.backup_trades_db --dry-run     # show plan, write/delete nothing
"""
from __future__ import annotations

import argparse
import logging
import os
import shutil
import sqlite3
import sys
from datetime import date
from pathlib import Path

from trading_bot.config import DB_PATH, VAR_DIR

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("backup_trades_db")

BACKUP_DIR = VAR_DIR / "backups"
FROZEN_BACKUP = "trades.db.bak_pre_spike_cleanup"  # never delete this
# Cheapest content check that proves the snapshot holds the track record and not
# just a structurally-valid empty file. paper_nav is the sacred table.
VALIDATE_TABLE = "paper_nav"


def validate_backup(path: Path, expect_rows: int) -> str | None:
    """Return None if `path` is a sound backup, else a reason string.

    Structural check + a content check, because they fail differently: a torn
    write trips integrity_check, while a VACUUM that ran against the wrong
    source produces a perfectly valid database with the wrong rows in it.
    """
    # shortcut: full integrity_check is O(db size) (~minutes on the 5 GB live
    # DB). Fine for a weekly Sunday-9am task with nothing else scheduled; switch
    # to PRAGMA quick_check if this ever runs more often than daily.
    try:
        conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    except sqlite3.Error as e:
        return f"cannot open: {e}"
    try:
        row = conn.execute("PRAGMA integrity_check").fetchone()
        if not row or row[0] != "ok":
            return f"integrity_check: {row[0] if row else 'no result'}"
        n = conn.execute(f"SELECT COUNT(*) FROM {VALIDATE_TABLE}").fetchone()[0]
    except sqlite3.Error as e:
        return f"unreadable: {e}"
    finally:
        conn.close()
    if n != expect_rows:
        return f"{VALIDATE_TABLE} row count {n} != source {expect_rows}"
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", type=int, default=3,
                    help="How many most-recent daily backups to retain (default 3).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the plan and the rotation deletions without writing.")
    args = ap.parse_args()

    if not DB_PATH.exists():
        log.error("No DB at %s", DB_PATH)
        return 1
    db_size = DB_PATH.stat().st_size
    free = shutil.disk_usage(VAR_DIR).free
    if free < 2 * db_size:
        log.error("ABORT: free disk %.1f GB < 2x DB size %.1f GB.",
                  free / 1e9, 2 * db_size / 1e9)
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    out = BACKUP_DIR / f"trades_{date.today().isoformat()}.db"

    log.info("DB %.2f GB, free %.1f GB. Target: %s", db_size / 1e9, free / 1e9, out.name)

    # `.part` cannot match the trades_*.db rotation glob, so a failed write is
    # invisible to rotation by construction rather than by a filter.
    part = out.parent / (out.name + ".part")

    if args.dry_run:
        log.info("[dry-run] would VACUUM INTO %s, validate, then rename to %s",
                 part.name, out.name)
    else:
        src = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
        try:
            expect_rows = src.execute(
                f"SELECT COUNT(*) FROM {VALIDATE_TABLE}").fetchone()[0]
            if part.exists():
                part.unlink()  # leftover from an earlier failed run
            src.execute(f"VACUUM INTO '{part.as_posix()}'")
        except sqlite3.Error as e:
            log.error("ABORT: VACUUM INTO failed: %s. Existing backups untouched.", e)
            part.unlink(missing_ok=True)
            return 1
        finally:
            src.close()

        reason = validate_backup(part, expect_rows)
        if reason is not None:
            log.error("ABORT: %s is not a sound backup (%s). Deleting it and "
                      "leaving every existing generation in place — NOT rotating.",
                      part.name, reason)
            part.unlink(missing_ok=True)
            return 1

        # Only now is it safe to displace the same-day target: os.replace is
        # atomic within a volume, so `out` is never absent nor half-written.
        os.replace(part, out)
        log.info("Wrote %s (%.2f GB), validated: integrity ok, %s %d rows",
                 out, out.stat().st_size / 1e9, VALIDATE_TABLE, expect_rows)

    # Rotation: keep the newest --keep daily backups, delete older ones. Reached
    # ONLY after a validated write, so it can never evict a good generation in
    # favour of a truncated one.
    backups = sorted(BACKUP_DIR.glob("trades_*.db"))
    to_delete = backups[:-args.keep] if len(backups) > args.keep else []
    for b in to_delete:
        if b.name == FROZEN_BACKUP:  # never; also not in this dir, but be explicit
            continue
        if args.dry_run:
            log.info("[dry-run] would delete old backup %s", b.name)
        else:
            b.unlink()
            log.info("Deleted old backup %s", b.name)

    kept = sorted(BACKUP_DIR.glob("trades_*.db"))
    log.info("Retained %d backup(s): %s", len(kept), ", ".join(b.name for b in kept))
    return 0


if __name__ == "__main__":
    sys.exit(main())
