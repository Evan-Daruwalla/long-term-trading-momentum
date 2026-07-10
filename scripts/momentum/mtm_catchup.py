"""Catch-up mark-to-market (PRD amendment M3.5, option A — 2026-07-09).

Fixes the recurring gap the coverage gate creates. Same-day yfinance data is
incomplete when the 17:15 task runs, so the daily gate skips marking and leaves a
NAV hole until the data settles (record Appendix BH). This step marks every real
trading day <= today that:
  (a) is MISSING a paper_nav row for a sleeve,
  (b) has SETTLED to the coverage floor (same coverage_status() the gate uses),
  (c) is on/after the sleeve's inception, AND
  (d) is on/after the sleeve's last rebalance — so a past day is never back-marked
      with positions that have since changed (that would fabricate a wrong NAV).
Days still below the floor are left PENDING for a later run; the history
self-heals within a day.

Writes paper_nav through paper_mtm.compute_nav/write_nav (the only sanctioned
write). The M3.1 pre-inception guarantee is preserved by guard (c).

Exit codes (daily.bat branches on these):
  0  the latest trading day is settled and now marked (or already had a row)
  2  the latest trading day's coverage is still PENDING — normal, not a failure;
     every settled day that could be marked was
  1  error

Usage:
  python -m scripts.momentum.mtm_catchup
  python -m scripts.momentum.mtm_catchup --dry-run
  python -m scripts.momentum.mtm_catchup --window 15
  python -m scripts.momentum.mtm_catchup --db path/to/copy.db   # test-only
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from datetime import date
from pathlib import Path

from trading_bot.config import DB_PATH
from scripts.momentum import paper_mtm
from scripts.momentum.check_coverage import coverage_status, MIN_TRADING_DAY_COUNT

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("mtm_catchup")

WINDOW = 10  # trading days to look back


def _plan_conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _trading_calendar(conn: sqlite3.Connection, window: int) -> list[str]:
    rows = conn.execute(
        "SELECT key_date, COUNT(*) AS n FROM price_cache "
        "WHERE kind='close' AND price IS NOT NULL "
        "GROUP BY key_date ORDER BY key_date DESC LIMIT ?", (window * 3,)).fetchall()
    days = [r["key_date"] for r in rows if r["n"] >= MIN_TRADING_DAY_COUNT][:window]
    return sorted(days)  # ascending


def _last_rebalance(conn: sqlite3.Connection, strategy: str, inception: date) -> date:
    row = conn.execute("SELECT last_rebalanced_at FROM paper_portfolio WHERE strategy_name=?",
                       (strategy,)).fetchone()
    if row and row["last_rebalanced_at"]:
        try:
            return date.fromisoformat(str(row["last_rebalanced_at"])[:10])
        except ValueError:
            pass
    return inception


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=WINDOW,
                    help="Trading days back to consider (default 10).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the plan; write no NAV rows.")
    ap.add_argument("--db", default=None, help="DB path (default live). Test-only.")
    args = ap.parse_args()

    db_path = Path(args.db) if args.db else DB_PATH
    if args.db:
        # Point the write path (paper_mtm -> trading_bot.db.connect) at the copy too.
        import trading_bot.db as _db
        _db.close_thread_connection()
        _db.DB_PATH = db_path

    conn = _plan_conn(db_path)
    calendar = _trading_calendar(conn, args.window)
    if not calendar:
        log.error("No real trading days in the price_cache window.")
        return 1
    latest = calendar[-1]
    cov = {d: coverage_status(conn, d) for d in calendar}

    sleeves = [r["strategy_name"] for r in conn.execute(
        "SELECT strategy_name FROM paper_portfolio ORDER BY strategy_name")]
    meta: dict[str, tuple[date, date, set]] = {}
    for s in sleeves:
        inc = paper_mtm.inception_date(s)
        lr = _last_rebalance(conn, s, inc)
        navs = {r["nav_date"] for r in conn.execute(
            "SELECT nav_date FROM paper_nav WHERE strategy_name=?", (s,))}
        meta[s] = (inc, lr, navs)
    conn.close()  # planning done; the write loop uses paper_mtm's own connection

    marked = 0
    skipped_reb = 0
    pending = [d for d in calendar if not cov[d]["ok"]]
    for d in calendar:  # oldest first
        st = cov[d]
        if not st["ok"]:
            log.info("PENDING %s: coverage %d < floor %d — leaving unmarked (heals later).",
                     d, st["count"], st["floor"])
            continue
        for s in sleeves:
            inc, lr, navs = meta[s]
            if d < inc.isoformat() or d in navs:
                continue
            if d < lr.isoformat():
                log.warning("SKIP %s %s: before last rebalance %s (positions changed) — "
                            "back-mark by hand if this is a real gap.", s, d, lr)
                skipped_reb += 1
                continue
            if args.dry_run:
                log.info("[dry-run] would MTM %s as-of %s", s, d)
                marked += 1
                continue
            as_of = date.fromisoformat(d)
            nav = paper_mtm.compute_nav(s, as_of)
            paper_mtm.write_nav(s, as_of, nav)
            log.info("MARKED %s as-of %s: NAV $%.2f", s, d, nav["total_nav"])
            marked += 1

    today_ok = cov[latest]["ok"]
    log.info("catch-up done: marked=%d skipped_pre_rebalance=%d latest=%s coverage_ok=%s pending=%s",
             marked, skipped_reb, latest, today_ok, ",".join(pending) or "none")
    return 0 if today_ok else 2


if __name__ == "__main__":
    sys.exit(main())
