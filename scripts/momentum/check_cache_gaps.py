"""Cache-gap auditor (read-only) — the 815-ticker-class detector.

Targets the failure class from record Appendix AA (2026-06-13): ~815 tickers had
a multi-year hole in their cached history, so 12-1 momentum was measured across a
discontinuity and phantom-ranked stale names into half of every momentum sleeve.
That specific hole was backfilled; this script re-checks, on demand, that every
currently-rankable name has continuous history over the window the strategies
actually read (12-1 momentum needs ~13 months), so a new partial-warm hole can't
silently re-open the same wound.

Reads price_cache READ-ONLY. Writes nothing to the DB; appends a dated report to
var/cache_gap_report.log. Finding a gap is a REPORT, not a license to backfill —
backfilling is Evan's call (standing order).

Method:
  trading calendar = distinct close dates in the window with >= MIN_TRADING_DAY_COUNT
                     tickers (real trading days; excludes market-closed noise days).
  rankable         = tickers with a close on any of the last 3 calendar days.
  For each rankable ticker: within its own first..last close inside the window,
  find the longest run of consecutive calendar trading days with no close. Flag if
  that run > --max-gap (default 5).

Usage:
  python -m scripts.momentum.check_cache_gaps
  python -m scripts.momentum.check_cache_gaps --months 13 --max-gap 5 --top 30
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from datetime import date, datetime, timedelta

from trading_bot.config import DB_PATH, VAR_DIR

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("check_cache_gaps")

MIN_TRADING_DAY_COUNT = 1000
REPORT_PATH = VAR_DIR / "cache_gap_report.log"


def _ro_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _trading_calendar(conn: sqlite3.Connection, start: str) -> list[str]:
    """Sorted (asc) real trading days on/after `start`."""
    rows = conn.execute(
        "SELECT key_date, COUNT(*) AS c FROM price_cache "
        "WHERE kind='close' AND price IS NOT NULL AND key_date >= ? "
        "GROUP BY key_date ORDER BY key_date ASC",
        (start,),
    ).fetchall()
    return [r["key_date"] for r in rows if r["c"] >= MIN_TRADING_DAY_COUNT]


def audit(conn: sqlite3.Connection, months: int, max_gap: int) -> dict:
    latest_row = conn.execute(
        "SELECT MAX(key_date) AS d FROM price_cache WHERE kind='close' AND price IS NOT NULL"
    ).fetchone()
    latest = latest_row["d"]
    if latest is None:
        raise SystemExit("price_cache has no closes.")
    start = (date.fromisoformat(latest) - timedelta(days=int(months * 30.5) + 10)).isoformat()

    calendar = _trading_calendar(conn, start)
    cal_index = {d: i for i, d in enumerate(calendar)}
    recent = set(calendar[-3:])

    # Bulk-load every close in the window: ticker -> set of calendar indices.
    rows = conn.execute(
        "SELECT ticker, key_date FROM price_cache "
        "WHERE kind='close' AND price IS NOT NULL AND key_date >= ?",
        (start,),
    ).fetchall()
    present: dict[str, set[int]] = {}
    rankable: set[str] = set()
    for r in rows:
        idx = cal_index.get(r["key_date"])
        if idx is None:  # a close on a non-trading (noise) day; ignore for continuity
            continue
        present.setdefault(r["ticker"], set()).add(idx)
        if r["key_date"] in recent:
            rankable.add(r["ticker"])

    flagged: list[tuple[str, int, str, str, int]] = []  # ticker, worst_gap, gap_start, gap_end, coverage
    for tk in rankable:
        idxs = sorted(present.get(tk, ()))
        if len(idxs) < 2:
            continue
        first, last = idxs[0], idxs[-1]
        have = set(idxs)
        worst = 0
        worst_span = (first, first)
        run = 0
        run_start = None
        for i in range(first, last + 1):
            if i in have:
                run = 0
                run_start = None
            else:
                if run == 0:
                    run_start = i
                run += 1
                if run > worst:
                    worst = run
                    worst_span = (run_start, i)
        if worst > max_gap:
            span_days = last - first + 1
            flagged.append((tk, worst, calendar[worst_span[0]], calendar[worst_span[1]],
                            len(idxs) * 100 // span_days))

    flagged.sort(key=lambda x: x[1], reverse=True)
    return {
        "latest": latest, "window_start": start, "n_calendar": len(calendar),
        "n_rankable": len(rankable), "flagged": flagged,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=13,
                    help="Lookback window in months (default 13, the 12-1 momentum need).")
    ap.add_argument("--max-gap", type=int, default=5,
                    help="Flag a ticker whose longest missing run exceeds this many "
                         "consecutive trading days (default 5).")
    ap.add_argument("--top", type=int, default=30,
                    help="How many worst offenders to list (default 30).")
    args = ap.parse_args()

    conn = _ro_connect()
    res = audit(conn, args.months, args.max_gap)

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"=== {stamp} | cache-gap audit  window={res['window_start']}..{res['latest']}  "
        f"trading_days={res['n_calendar']}  rankable={res['n_rankable']}  "
        f"max_gap>{args.max_gap} ===",
        f"flagged: {len(res['flagged'])} of {res['n_rankable']} rankable tickers have an "
        f"internal hole > {args.max_gap} consecutive trading days.",
    ]
    for tk, worst, gstart, gend, cov in res["flagged"][:args.top]:
        lines.append(f"  {tk:8s} worst_gap={worst:3d}d  {gstart}..{gend}  window_coverage={cov}%")
    if len(res["flagged"]) > args.top:
        lines.append(f"  ... and {len(res['flagged']) - args.top} more (see --top).")

    for ln in lines:
        log.info(ln) if ln.startswith("===") or ln.startswith("flagged") else log.warning(ln)

    VAR_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n\n")

    log.info("Report appended to %s", REPORT_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
