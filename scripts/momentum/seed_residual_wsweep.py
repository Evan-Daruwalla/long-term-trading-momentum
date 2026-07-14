"""Seed the residual weight-sweep forward-test family by 05-01 REPLAY (record BW).

Ten paper sleeves differing ONLY in the residual-momentum/ROA blend weight, all
seeded on the champions' epoch (2026-05-01, $100k) by deterministic replay on the
cached prices — the same method that seeded residual_roa_6535_paper itself
(backdated 06-09) and the 06-13 re-inception. Interleaved replay per sleeve:

    rebalance 2026-05-01 -> MTM each settled trading day -> rebalance 2026-06-03
    -> MTM ... -> rebalance 2026-07-01 -> MTM ... through --end (last settled day)

(Interleaving matters: paper_mtm.compute_nav prices CURRENT open positions, so
each window's NAVs must be written BEFORE the next rebalance changes positions.)
Rebalance dates match the May champions' actual dates (05-01, 06-03, 07-01).

HONESTY DEMARCATION: rows written by this script are deterministic REPLAY
(simulation on cached closes), clearly recorded as such in Appendix BW. Live
forward data begins 2026-07-14. The backtest sweep that motivated the ladder
(BU/BV) used data only through 2026-05-01, so the replayed 05-01->07-10 segment
is post-selection data — a mini-holdout, though tiny (2-3 rebalances).

After each sleeve's replay, last_rebalanced_at is set to the last REPLAY
rebalance date (07-01) instead of the wall-clock stamp mark_rebalanced() wrote —
otherwise mtm_catchup's pre-rebalance guard would refuse to mark 07-13+ for the
new sleeves tonight and verify_run would fail the daily task.

SAFETY:
- Refuses to touch a sleeve that already exists (re-running a 05-01 rebalance on
  a sleeve holding July positions would liquidate it at May prices).
- --db points everything at a copy (test-first); without --execute it is a plan
  print, no writes. Sequential by construction.

Usage:
  python -m scripts.momentum.seed_residual_wsweep                       # dry plan
  python -m scripts.momentum.seed_residual_wsweep --db var/trades_seedtest.db --execute
  python -m scripts.momentum.seed_residual_wsweep --execute             # LIVE
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from datetime import date
from pathlib import Path

WEIGHTS = [(50, 50), (55, 45), (60, 40), (65, 35), (70, 30),
           (75, 25), (80, 20), (85, 15), (90, 10), (95, 5)]

REBALANCE_DATES = [date(2026, 5, 1), date(2026, 6, 3), date(2026, 7, 1)]
STARTING_CASH = 100_000.0
TOP_N = 50
HALF_SPREAD_BPS = 5.0
SETTLED_FLOOR = 5000   # same hard floor as check_coverage


def _name(mm: int, rr: int) -> str:
    return f"residual_w{mm:02d}{rr:02d}_paper"


def _calendar(db_path: Path, start: date, end: date) -> list[str]:
    """Settled trading days (>= SETTLED_FLOOR closes) in [start, end]."""
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    rows = conn.execute(
        "SELECT key_date, COUNT(*) n FROM price_cache "
        "WHERE kind='close' AND price IS NOT NULL AND key_date BETWEEN ? AND ? "
        "GROUP BY key_date ORDER BY key_date",
        (start.isoformat(), end.isoformat())).fetchall()
    conn.close()
    return [d for d, n in rows if n >= SETTLED_FLOOR]


def _last_settled(db_path: Path) -> date:
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    rows = conn.execute(
        "SELECT key_date, COUNT(*) n FROM price_cache "
        "WHERE kind='close' AND price IS NOT NULL "
        "GROUP BY key_date ORDER BY key_date DESC LIMIT 10").fetchall()
    conn.close()
    for d, n in rows:
        if n >= SETTLED_FLOOR:
            return date.fromisoformat(d)
    raise SystemExit("no settled trading day found")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=None, help="DB path (default live). Use a copy to test.")
    ap.add_argument("--execute", action="store_true",
                    help="Actually write. Without it: print the plan only.")
    ap.add_argument("--end", default=None,
                    help="Last replay MTM date (default: last settled trading day).")
    args = ap.parse_args()

    import trading_bot.db as _db
    if args.db:
        _db.close_thread_connection()
        _db.DB_PATH = Path(args.db)
        print(f"DB pointed at COPY: {args.db}")
    db_path = _db.DB_PATH

    from scripts.momentum import paper_rebalance, paper_mtm
    from trading_bot.db import connect

    end = date.fromisoformat(args.end) if args.end else _last_settled(db_path)
    cal = _calendar(db_path, REBALANCE_DATES[0], end)
    for rd in REBALANCE_DATES:
        if rd.isoformat() not in cal:
            raise SystemExit(f"rebalance date {rd} not a settled trading day in cache")

    # Existing-sleeve guard: never replay over a live sleeve.
    with connect() as conn:
        existing = [r["strategy_name"] for r in conn.execute(
            "SELECT strategy_name FROM paper_portfolio WHERE strategy_name LIKE 'residual_w%'")]
    if existing:
        raise SystemExit(f"REFUSING: sleeves already exist: {existing}. "
                         "Replay must start from a clean slate.")

    mode = "EXECUTE (writing)" if args.execute else "DRY PLAN (no writes)"
    print(f"REPLAY-SEED residual weight ladder — {mode}")
    print(f"  epoch {REBALANCE_DATES[0]} .. {end}  ({len(cal)} settled trading days, "
          f"rebalances {[d.isoformat() for d in REBALANCE_DATES]})")
    print(f"  {len(WEIGHTS)} sleeves x ${STARTING_CASH:,.0f}, top-{TOP_N}, "
          f"{HALF_SPREAD_BPS} bps, broker-realistic\n" + "=" * 74)
    if not args.execute:
        for mm, rr in WEIGHTS:
            print(f"  would seed {_name(mm, rr)}  ({mm}/{rr})")
        print("\nDRY PLAN complete — nothing written. Re-run with --execute.")
        return 0

    t_all = time.time()
    summary = []
    for mm, rr in WEIGHTS:
        name = _name(mm, rr)
        t0 = time.time()
        print(f"\n>>> {name}  ({mm}/{rr})", flush=True)
        for i, rd in enumerate(REBALANCE_DATES):
            nxt = REBALANCE_DATES[i + 1].isoformat() if i + 1 < len(REBALANCE_DATES) \
                else (end.isoformat() + "z")   # 'z' sorts after any date: include end
            n = paper_rebalance.rebalance(
                as_of=rd, strategy_name=name, starting_cash=STARTING_CASH,
                top_n=TOP_N, half_spread_bps=HALF_SPREAD_BPS,
                dry_run=False, broker_realistic=True,
            )
            window = [d for d in cal if rd.isoformat() <= d < nxt]
            for d in window:
                as_of = date.fromisoformat(d)
                nav = paper_mtm.compute_nav(name, as_of)
                paper_mtm.write_nav(name, as_of, nav)
            print(f"    rebalance {rd}: {n} changes; MTM'd {len(window)} days "
                  f"({window[0]}..{window[-1]})", flush=True)
        # Stamp last_rebalanced_at with the last REPLAY rebalance date (see docstring).
        with connect() as conn:
            conn.execute("UPDATE paper_portfolio SET last_rebalanced_at=? "
                         "WHERE strategy_name=?",
                         (REBALANCE_DATES[-1].isoformat() + "T00:00:00+00:00", name))
        final = paper_mtm.compute_nav(name, end)
        pct = (final["total_nav"] / STARTING_CASH - 1) * 100
        print(f"    {name}: NAV@{end} ${final['total_nav']:,.2f}  ({pct:+.2f}% since 05-01, "
              f"{final['n_open']} open)  [{time.time()-t0:.0f}s]", flush=True)
        summary.append((name, final["total_nav"], pct))

    print("\n" + "=" * 74 + f"\n  REPLAY SUMMARY (05-01 -> {end}, deterministic on cached closes)")
    for name, nav, pct in sorted(summary, key=lambda x: -x[1]):
        print(f"  {name:<24} NAV ${nav:>11,.2f}  {pct:+7.2f}%")
    print(f"\nTotal elapsed: {(time.time()-t_all)/60:.1f} min")
    return 0


if __name__ == "__main__":
    sys.exit(main())
