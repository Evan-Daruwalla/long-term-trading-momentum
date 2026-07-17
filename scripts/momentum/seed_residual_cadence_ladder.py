"""Seed the residual weight-ladder CADENCE experiment by 05-01 REPLAY (record CD).

Extends the monthly weight ladder (record BW) into a 3-cadence experiment: the
SAME 19-point residual-momentum/ROA blend ladder rebalanced monthly, weekly, and
biweekly, to forward-test whether rebalance FREQUENCY changes where on the blend
ladder the edge lives. All seeded on the champions' epoch (2026-05-01, $100k) by
the same deterministic replay that seeded residual_roa_6535_paper (06-09 backdate),
the 06-13 re-inception, and the BW ladder.

Sleeves ($100k, top-50, 5 bps, broker-realistic; ONLY blend weight + cadence vary):
  monthly   residual_w<MM><RR>_paper      rebalanced 05-01, 06-03, 07-01     (BW; 10 exist, 9 new)
  weekly    residual_w<MM><RR>_wk_paper   rebalanced first settled day each week (12 dates)
  biweekly  residual_w<MM><RR>_2wk_paper  rebalanced every other week from 05-01 (6 dates)

Interleaved replay per sleeve (identical to seed_residual_wsweep):

    rebalance rd0 -> MTM each settled trading day in [rd0, rd1) -> rebalance rd1
    -> MTM ... -> rebalance rdN -> MTM ... through --end (last settled day)

(Interleaving matters: paper_mtm.compute_nav prices CURRENT open positions, so each
window's NAVs must be written BEFORE the next rebalance changes positions.)

After each sleeve's replay, last_rebalanced_at is set to the last REPLAY rebalance
date (not the wall-clock mark_rebalanced() stamp) so mtm_catchup's pre-rebalance
guard marks forward days and verify_run treats them as live.

HONESTY DEMARCATION: replayed rows are deterministic SIMULATION on cached closes
(like BW), NOT live fills. Live forward begins after each cadence's last replay
rebalance (weekly 07-13, biweekly 07-06, monthly 07-01). The weekly/biweekly grids
share the monthly 05-01 epoch so all three cadences are directly comparable.

SAFETY:
- SKIPS any sleeve that already exists (re-running a 05-01 rebalance on a sleeve
  holding July positions would liquidate it at May prices). So the monthly cadence
  seeds only the 9 new blends; the existing 10 are left untouched.
- --db points everything at a COPY (test-first); without --execute it is a plan
  print, no writes. Sequential by construction (never concurrent factor_backtest).

Usage:
  python -m scripts.momentum.seed_residual_cadence_ladder --cadence all                 # dry plan
  python -m scripts.momentum.seed_residual_cadence_ladder --cadence all --db var/trades_seedtest.db --execute
  python -m scripts.momentum.seed_residual_cadence_ladder --cadence all --execute        # LIVE
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from datetime import date
from pathlib import Path

# Full 19-point ladder: (residual-momentum weight %, ROA weight %).
WEIGHTS = [(5, 95), (10, 90), (15, 85), (20, 80), (25, 75), (30, 70), (35, 65),
           (40, 60), (45, 55), (50, 50), (55, 45), (60, 40), (65, 35), (70, 30),
           (75, 25), (80, 20), (85, 15), (90, 10), (95, 5)]

MONTHLY_DATES = [date(2026, 5, 1), date(2026, 6, 3), date(2026, 7, 1)]
# First settled trading day of each ISO week from 05-01 (holiday-aware; 05-25,
# 06-19, 07-03 were market holidays and are not rebalance days).
WEEKLY_DATES = [date(2026, 5, 1), date(2026, 5, 4), date(2026, 5, 11), date(2026, 5, 18),
                date(2026, 5, 26), date(2026, 6, 1), date(2026, 6, 8), date(2026, 6, 15),
                date(2026, 6, 22), date(2026, 6, 29), date(2026, 7, 6), date(2026, 7, 13)]
# Every other week from 05-01.
BIWEEKLY_DATES = [date(2026, 5, 1), date(2026, 5, 11), date(2026, 5, 26),
                  date(2026, 6, 8), date(2026, 6, 22), date(2026, 7, 6)]

CADENCES = {
    "monthly":  (MONTHLY_DATES,  lambda mm, rr: f"residual_w{mm:02d}{rr:02d}_paper"),
    "weekly":   (WEEKLY_DATES,   lambda mm, rr: f"residual_w{mm:02d}{rr:02d}_wk_paper"),
    "biweekly": (BIWEEKLY_DATES, lambda mm, rr: f"residual_w{mm:02d}{rr:02d}_2wk_paper"),
}

STARTING_CASH = 100_000.0
TOP_N = 50
HALF_SPREAD_BPS = 5.0
SETTLED_FLOOR = 5000   # same hard floor as check_coverage


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


def _seed_one(name, rebalance_dates, cal, end, paper_rebalance, paper_mtm, connect):
    """Replay one sleeve across its cadence's rebalance dates. Returns (nav, pct)."""
    for i, rd in enumerate(rebalance_dates):
        nxt = rebalance_dates[i + 1].isoformat() if i + 1 < len(rebalance_dates) \
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
        conn.execute("UPDATE paper_portfolio SET last_rebalanced_at=? WHERE strategy_name=?",
                     (rebalance_dates[-1].isoformat() + "T00:00:00+00:00", name))
    final = paper_mtm.compute_nav(name, end)
    pct = (final["total_nav"] / STARTING_CASH - 1) * 100
    return final, pct


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=None, help="DB path (default live). Use a copy to test.")
    ap.add_argument("--execute", action="store_true",
                    help="Actually write. Without it: print the plan only.")
    ap.add_argument("--cadence", default="all", choices=["all", "monthly", "weekly", "biweekly"])
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
    cal = _calendar(db_path, MONTHLY_DATES[0], end)
    cal_set = set(cal)

    selected = ["monthly", "weekly", "biweekly"] if args.cadence == "all" else [args.cadence]

    # Validate every rebalance date is a settled trading day (fail fast).
    for cad in selected:
        dates, _ = CADENCES[cad]
        for rd in dates:
            if rd.isoformat() not in cal_set:
                raise SystemExit(f"{cad} rebalance date {rd} is not a settled trading day in cache")

    # Build the work list, skipping sleeves that already exist.
    with connect() as conn:
        existing = {r["strategy_name"] for r in conn.execute(
            "SELECT strategy_name FROM paper_portfolio WHERE strategy_name LIKE 'residual_w%'")}

    plan, skipped = [], []
    for cad in selected:
        dates, name_fn = CADENCES[cad]
        for mm, rr in WEIGHTS:
            name = name_fn(mm, rr)
            (skipped if name in existing else plan).append((cad, name, dates, mm, rr))

    mode = "EXECUTE (writing)" if args.execute else "DRY PLAN (no writes)"
    print(f"REPLAY-SEED residual cadence ladder — {mode}")
    print(f"  epoch {MONTHLY_DATES[0]} .. {end}  ({len(cal)} settled trading days)")
    print(f"  cadences: {selected}   to-seed: {len(plan)}   skip-existing: {len(skipped)}")
    for cad in selected:
        dates, _ = CADENCES[cad]
        print(f"    {cad:<9} {len(dates)} rebalances {[d.isoformat() for d in dates]}")
    if skipped:
        print(f"  SKIP (already exist): {[n for _, n, _, _, _ in skipped]}")
    print("=" * 78)

    if not args.execute:
        for cad, name, dates, mm, rr in plan:
            print(f"  would seed {name:<26} ({cad}, {mm}/{rr}, {len(dates)} rebalances)")
        print(f"\nDRY PLAN complete — nothing written. {len(plan)} sleeves. Re-run with --execute.")
        return 0

    t_all = time.time()
    summary = []
    for k, (cad, name, dates, mm, rr) in enumerate(plan, 1):
        t0 = time.time()
        print(f"\n>>> [{k}/{len(plan)}] {name}  ({cad}, {mm}/{rr})", flush=True)
        final, pct = _seed_one(name, dates, cal, end, paper_rebalance, paper_mtm, connect)
        print(f"    {name}: NAV@{end} ${final['total_nav']:,.2f}  ({pct:+.2f}% since 05-01, "
              f"{final['n_open']} open)  [{time.time()-t0:.0f}s]", flush=True)
        summary.append((cad, name, final["total_nav"], pct))

    print("\n" + "=" * 78 + f"\n  REPLAY SUMMARY (05-01 -> {end}, deterministic on cached closes)")
    for cad, name, nav, pct in sorted(summary, key=lambda x: (x[0], -x[2])):
        print(f"  {cad:<9} {name:<26} NAV ${nav:>11,.2f}  {pct:+7.2f}%")
    print(f"\nSeeded {len(summary)} sleeves. Total elapsed: {(time.time()-t_all)/60:.1f} min")
    return 0


if __name__ == "__main__":
    sys.exit(main())
