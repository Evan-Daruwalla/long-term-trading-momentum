"""Price-coverage gate for the daily flow (read-only).

Guards against the "incomplete yfinance publication" failure class (record
Appendix AU): a trading day's closes can arrive for only ~4,400 of ~5,200
tickers and never settle that evening. If MTM runs on that partial data the
NAVs and ranks are silently wrong. This script is the gate the 07-06 deploy
enforced by hand ("coverage >= 5,000 closes"), now scripted so daily.bat can
fail loudly instead of MTM-ing on a partial day.

Reads price_cache READ-ONLY (file:...?mode=ro). Never writes.

Logic:
  target date   = the latest key_date with kind='close' (default), or --date.
  count         = non-NULL closes on the target date.
  baseline      = median non-NULL close count over the prior 10 *trading* days
                  (dates with count >= MIN_TRADING_DAY_COUNT, so market-closed
                  days that leave ~200 stray closes don't drag the median down).
  floor         = max(HARD_FLOOR, BASELINE_FRACTION * baseline), or --floor.
  exit 0 if count >= floor, else exit 1 with a COVERAGE FAIL line.

Usage:
  python -m scripts.momentum.check_coverage
  python -m scripts.momentum.check_coverage --date 2026-07-07
  python -m scripts.momentum.check_coverage --floor 5000
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import statistics
import sys

from trading_bot.config import DB_PATH

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("check_coverage")

# A live trading day caches ~5,200 closes; a market-closed day (holiday) leaves
# only a couple hundred stray closes. Dates below this are not trading days and
# are excluded from the baseline so they can't deflate the median.
MIN_TRADING_DAY_COUNT = 1000
# The 07-06 deploy's hard abort floor (Appendix AV): never MTM below this.
HARD_FLOOR = 5000
# Relative floor: also flag a day that is well short of its own recent baseline.
BASELINE_FRACTION = 0.90
BASELINE_WINDOW = 10


def _ro_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def coverage_by_date(conn: sqlite3.Connection, limit: int) -> list[tuple[str, int]]:
    """(key_date, non-NULL close count) for the most recent `limit` dates, desc."""
    rows = conn.execute(
        "SELECT key_date, COUNT(*) AS n FROM price_cache "
        "WHERE kind='close' AND price IS NOT NULL "
        "GROUP BY key_date ORDER BY key_date DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [(r["key_date"], r["n"]) for r in rows]


def coverage_status(conn: sqlite3.Connection, target_date: str | None = None,
                    floor_override: int | None = None) -> dict:
    """Compute coverage for one date. Shared by the daily gate (this module's
    main) and mtm_catchup so both use IDENTICAL floor logic — if they diverged, a
    day could pass one and fail the other. Returns
    {date, count, baseline, floor, ok, n_baseline, floor_src}; `ok=None` and
    `date=None` when price_cache has no closes at all.
    """
    if target_date is not None:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM price_cache "
            "WHERE kind='close' AND price IS NOT NULL AND key_date=?",
            (target_date,)).fetchone()
        count = row["n"]
        prior = conn.execute(
            "SELECT key_date, COUNT(*) AS n FROM price_cache "
            "WHERE kind='close' AND price IS NOT NULL AND key_date < ? "
            "GROUP BY key_date ORDER BY key_date DESC LIMIT ?",
            (target_date, BASELINE_WINDOW * 3)).fetchall()
        baseline_days = [r["n"] for r in prior if r["n"] >= MIN_TRADING_DAY_COUNT][:BASELINE_WINDOW]
    else:
        recent = coverage_by_date(conn, (BASELINE_WINDOW + 1) * 3)
        if not recent:
            return {"date": None, "count": 0, "baseline": 0, "floor": 0,
                    "ok": None, "n_baseline": 0, "floor_src": "no closes"}
        target_date, count = recent[0]
        baseline_days = [n for (_d, n) in recent[1:] if n >= MIN_TRADING_DAY_COUNT][:BASELINE_WINDOW]

    baseline = int(statistics.median(baseline_days)) if baseline_days else 0
    if floor_override is not None:
        floor = floor_override
        floor_src = f"--floor {floor_override}"
    else:
        rel = int(BASELINE_FRACTION * baseline)
        floor = max(HARD_FLOOR, rel)
        floor_src = f"max({HARD_FLOOR}, {int(BASELINE_FRACTION*100)}%*{baseline}={rel})"
    return {"date": target_date, "count": count, "baseline": baseline, "floor": floor,
            "ok": count >= floor, "n_baseline": len(baseline_days), "floor_src": floor_src}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None,
                    help="Target date (ISO). Default: latest cached close date.")
    ap.add_argument("--floor", type=int, default=None,
                    help="Override the computed floor with a fixed close count.")
    args = ap.parse_args()

    st = coverage_status(_ro_connect(), args.date, args.floor)
    if st["ok"] is None:
        log.error("COVERAGE FAIL: price_cache has no 'close' rows at all.")
        return 1

    log.info("Coverage check: date=%s  closes=%d  baseline(median of %d)=%d  floor=%d [%s]",
             st["date"], st["count"], st["n_baseline"], st["baseline"], st["floor"], st["floor_src"])
    if st["ok"]:
        log.info("COVERAGE PASS: %d closes on %s (>= floor %d).",
                 st["count"], st["date"], st["floor"])
        return 0
    log.error("COVERAGE FAIL: only %d closes on %s (< floor %d). "
              "Likely incomplete publication (record Appendix AU) - do NOT MTM on this data.",
              st["count"], st["date"], st["floor"])
    return 1


if __name__ == "__main__":
    sys.exit(main())
