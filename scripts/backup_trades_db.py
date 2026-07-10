"""Rotating backup of var/trades.db (PRD M5.1).

Uses SQLite ``VACUUM INTO`` for a transactionally-consistent snapshot — a bare
file copy of a live WAL database can catch a torn write, so we never do that.
Keeps the N most recent ``var/backups/trades_YYYY-MM-DD.db`` and deletes older
ones. NEVER touches ``var/trades.db.bak_pre_spike_cleanup`` (the frozen founding
backup) — it lives in ``var/``, not ``var/backups/``, and does not match the
``trades_*.db`` glob, so it is safe by construction; the guard below is belt-and-
suspenders. Aborts if free disk is under 2x the DB size.

Usage:
  python -m scripts.backup_trades_db
  python -m scripts.backup_trades_db --keep 3
  python -m scripts.backup_trades_db --dry-run     # show plan, write/delete nothing
"""
from __future__ import annotations

import argparse
import logging
import shutil
import sqlite3
import sys
from datetime import date

from trading_bot.config import DB_PATH, VAR_DIR

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("backup_trades_db")

BACKUP_DIR = VAR_DIR / "backups"
FROZEN_BACKUP = "trades.db.bak_pre_spike_cleanup"  # never delete this


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

    if args.dry_run:
        log.info("[dry-run] would VACUUM INTO %s", out)
    else:
        if out.exists():
            out.unlink()  # VACUUM INTO fails if the target exists; same-day rerun overwrites
        src = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
        try:
            src.execute(f"VACUUM INTO '{out.as_posix()}'")
        finally:
            src.close()
        log.info("Wrote %s (%.2f GB)", out, out.stat().st_size / 1e9)

    # Rotation: keep the newest --keep daily backups, delete older ones.
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
