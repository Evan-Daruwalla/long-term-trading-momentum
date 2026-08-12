"""Slippage tracker — compares simulated paper fills to real broker fills.

DEFERRED USE: this becomes active when the user turns 18 and opens a real
brokerage. Until then it's a placeholder that records the SIM fill price
for each paper trade so the simulator-vs-real comparison has a baseline.

Workflow (post-live):
  1. Each rebalance: paper_rebalance.py already records sim fill_price in
     paper_positions.entry_price.
  2. User executes the same trades in real brokerage; records broker fill
     price (e.g. via broker export).
  3. Run this script with a CSV of (ticker, broker_fill, broker_dt) →
     it pairs each broker fill with the corresponding paper position,
     computes slippage in bps, appends to a `slippage_log` table.
  4. After 20+ paired fills, compute mean/median/p95 slippage by sector
     or ticker-liquidity bucket. If significantly > 5 bps half-spread,
     bump HALF_SPREAD_BPS in factor_backtest to recalibrate.
     WARNING (added 2026-08-11, record CT.4/CU.3): step 4 is only valid if the
     broker fill and the sim's reference price are CONTEMPORANEOUS. If the sim
     books at a close and the fill lands hours later, the difference is DRIFT,
     not spread, and recalibrating HALF_SPREAD_BPS off it corrupts every
     backtest in the project. That is exactly what happened on the Alpaca path
     below; do not let it happen here at 18 either.

For now, the script just creates the table schema and ingests a CSV if
provided. The pairing logic is the only non-trivial part.

Usage (after going live):
  python -m scripts.momentum.slippage_tracker --csv real_fills.csv \\
      --strategy mom_roa_6535_paper

CSV format expected:
  ticker,broker_fill_price,broker_filled_at,strategy_hint
  AAPL,178.43,2026-06-02T09:31:15-04:00,mom_v2_paper
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

from trading_bot.db import connect


SCHEMA = """
CREATE TABLE IF NOT EXISTS slippage_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_name   TEXT NOT NULL,
    ticker          TEXT NOT NULL,
    paper_pos_id    INTEGER,
    paper_fill      REAL NOT NULL,
    paper_filled_at TEXT NOT NULL,
    broker_fill     REAL NOT NULL,
    broker_filled_at TEXT NOT NULL,
    slippage_bps    REAL NOT NULL,
    direction       TEXT NOT NULL,   -- 'buy' or 'sell'
    note            TEXT,
    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_pos_id) REFERENCES paper_positions(id)
);
CREATE INDEX IF NOT EXISTS idx_slippage_strategy
    ON slippage_log(strategy_name, broker_filled_at);
"""


def ensure_schema() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def ingest_csv(csv_path: Path, strategy_name: str | None) -> int:
    """Pair each row in CSV against the nearest paper_positions entry by
    (ticker, time). Computes slippage_bps and inserts into slippage_log."""
    ensure_schema()
    n_paired = n_unpaired = 0
    with open(csv_path) as f, connect() as conn:
        reader = csv.DictReader(f)
        for row in reader:
            ticker = row["ticker"]
            broker_fill = float(row["broker_fill_price"])
            broker_dt = row["broker_filled_at"]
            strat = row.get("strategy_hint") or strategy_name
            if not strat:
                print(f"  SKIP {ticker}: no strategy hint or --strategy flag")
                n_unpaired += 1
                continue
            # Find the paper position with closest entry_time and matching ticker
            cur = conn.execute("""
                SELECT id, qty, entry_price, entry_time
                FROM paper_positions
                WHERE strategy_name=? AND ticker=?
                ORDER BY ABS(julianday(entry_time) - julianday(?)) ASC
                LIMIT 1
            """, (strat, ticker, broker_dt))
            r = cur.fetchone()
            if not r:
                print(f"  UNPAIRED {ticker}: no paper position for {strat}")
                n_unpaired += 1
                continue
            paper_fill = r["entry_price"]
            direction = "buy" if r["qty"] > 0 else "sell"
            # Slippage in bps relative to paper fill (positive = real cost > sim cost)
            slippage_bps = (broker_fill / paper_fill - 1.0) * 10_000
            # Direction matters: for SELLS, lower real price = positive slippage
            if direction == "sell":
                slippage_bps = -slippage_bps
            conn.execute("""
                INSERT INTO slippage_log
                  (strategy_name, ticker, paper_pos_id, paper_fill,
                   paper_filled_at, broker_fill, broker_filled_at,
                   slippage_bps, direction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (strat, ticker, r["id"], paper_fill, r["entry_time"],
                  broker_fill, broker_dt, slippage_bps, direction))
            n_paired += 1
            print(f"  PAIRED {ticker} {direction} paper=${paper_fill:.4f} "
                  f"broker=${broker_fill:.4f}  slippage={slippage_bps:+.1f}bps")
    return n_paired


# ---------------------------------------------------------------------------
# M6.2 — Alpaca PAPER mirror pairing (record CS/CT). Separate from ingest_csv
# above, which stays as-is for the real-brokerage path at 18: that one takes a
# different CSV shape and derives direction from `qty > 0`, which is ALWAYS
# "buy" in a long-only sim. The Alpaca CSV carries the real `side`, so this path
# uses it instead of re-deriving it wrongly.
#
# THIS PATH MEASURES IMPLEMENTATION SHORTFALL, NOT EXECUTION SLIPPAGE.
# (M6 redefined 2026-08-11 by Evan; rationale in records CT.4 / CU.3 / CV.5 and
# in the M6 banner of PRD_ROADMAP.md.)
#
#   shortfall = realised mirror fill price  vs  the sim's BOOKED reference price
#               (paper_positions.entry_price / exit_price), drift INCLUDED
#
# The sim books at a CLOSE; the mirror filled intraday (14:20 ET) in July and at
# the NEXT session's open in August. The sim therefore never books at a price the
# mirror ever transacted at, so the gap between them is drift — real cost, wrong
# name. "Slippage" is the name that nearly recalibrated HALF_SPREAD_BPS 5 -> 100.
#
# The table is still called `slippage_log` and its column is still
# `slippage_bps`: renaming a live table shared with the deferred real-brokerage
# path buys nothing. Every row this path writes carries `note` starting
# "implementation-shortfall" so the metric is never ambiguous at read time.
# ---------------------------------------------------------------------------

# alpaca submitted_at date -> the sim rebalance date it belongs to. Alpaca's
# submitted_at is a QUEUE-RELEASE time, not our submission time (record CS.3):
# the 132 August orders were POSTed 2026-08-03T23:24Z and released 08-04.
BATCH_TO_REBALANCE = {"2026-07-07": "2026-07-07", "2026-08-04": "2026-08-03"}


def _sim_leg(conn, sleeve: str, ticker: str, side: str, rebalance: str):
    """The sim row this mirror fill corresponds to, or None.

    Joined on (sleeve, ticker, rebalance date) EXPLICITLY. The legacy path above
    uses `ORDER BY ABS(julianday(entry_time) - ...) LIMIT 1`, which always
    returns something -- it cannot report an unpaired fill, and with a ticker
    held across two rebalances it can silently pick the wrong leg.

    A BUY pairs to entry_price; a SELL pairs to exit_price. Pairing a sell
    against entry_price would compare two unrelated trades.
    """
    if side == "buy":
        return conn.execute(
            "SELECT id, entry_price AS px, entry_date AS dt FROM paper_positions "
            "WHERE strategy_name=? AND ticker=? AND entry_date=?",
            (sleeve, ticker, rebalance)).fetchone()
    return conn.execute(
        "SELECT id, exit_price AS px, exit_date AS dt FROM paper_positions "
        "WHERE strategy_name=? AND ticker=? AND exit_date=?",
        (sleeve, ticker, rebalance)).fetchone()


def _sim_leg_dates(conn, sleeve: str, ticker: str, side: str) -> list[str]:
    """Dates on which the sim DID have a leg of this side, for this name.

    Only used to explain an unpaired fill honestly. Never used to pair.
    """
    col = "entry_date" if side == "buy" else "exit_date"
    return [r[0] for r in conn.execute(
        f"SELECT DISTINCT {col} FROM paper_positions WHERE strategy_name=? "
        f"AND ticker=? AND {col} IS NOT NULL ORDER BY {col}", (sleeve, ticker))]


def shortfall_bps(sim_px: float, broker_px: float, side: str) -> float:
    """Implementation shortfall in bps. Positive = the mirror did WORSE.

    Buy:  paying more than the sim assumed is a cost.
    Sell: receiving less than the sim assumed is a cost, so the sign flips.

    The arithmetic is the same as an execution-slippage calculation; what
    differs is the claim being made about it. This compares the sim's booked
    price to the realised fill and attributes NOTHING to spread — the two prices
    are hours apart, so most of the difference is drift.
    """
    raw = (broker_px / sim_px - 1.0) * 10_000
    return raw if side == "buy" else -raw


def pair_alpaca_csv(csv_path: Path, conn) -> tuple[list[dict], list[dict]]:
    """-> (paired, unpaired). Read-only; no writes."""
    paired: list[dict] = []
    unpaired: list[dict] = []
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            batch = str(row["submitted_at"])[:10]
            rebalance = BATCH_TO_REBALANCE.get(batch)
            broker_px = float(row["filled_avg_price"])
            if rebalance is None:
                unpaired.append({**row, "reason": f"unknown batch date {batch}"})
                continue
            r = _sim_leg(conn, row["sleeve"], row["ticker"], row["side"], rebalance)
            if r is None or r["px"] is None:
                # NOT an error, but there are TWO reasons and they are not the
                # same finding, so the report must not give one canned answer:
                #  - no leg of that side at ANY date -> the mirror reconciles to
                #    TARGET WEIGHTS, so it trims/tops-up names the sim merely
                #    holds at a different qty. Nothing to pair against, by design.
                #  - a leg of that side EXISTS on a different date -> a date
                #    mismatch. Reported, deliberately NOT paired across dates:
                #    loose date matching is the legacy path's defect (record CT.1).
                other = _sim_leg_dates(conn, row["sleeve"], row["ticker"], row["side"])
                reason = (
                    f"date mismatch: sim {row['side']} leg exists on "
                    f"{','.join(other)}, mirror fill maps to rebalance {rebalance}"
                    if other else
                    "no sim leg: mirror weight adjustment on a name the sim did "
                    "not open/close at this rebalance")
                unpaired.append({**row, "reason": reason})
                continue
            paired.append({
                "sleeve": row["sleeve"], "ticker": row["ticker"],
                "side": row["side"], "batch": batch, "rebalance": rebalance,
                "sim_px": r["px"], "broker_px": broker_px,
                "bps": shortfall_bps(r["px"], broker_px, row["side"]),
                "pos_id": r["id"], "sim_dt": r["dt"],
                "broker_dt": row["filled_at"], "order_id": row["order_id"],
            })
    return paired, unpaired


def _stats(vals: list[float]) -> dict:
    v = sorted(vals)
    n = len(v)
    return {"n": n, "mean": sum(v) / n, "median": v[n // 2],
            "p95": v[min(n - 1, int(round(0.95 * (n - 1))))],
            "min": v[0], "max": v[-1]}


def report() -> None:
    with connect() as conn:
        rows = conn.execute("""
            SELECT strategy_name, COUNT(*) n,
                   AVG(slippage_bps) avg_bps,
                   MIN(slippage_bps) min_bps,
                   MAX(slippage_bps) max_bps
            FROM slippage_log GROUP BY strategy_name
        """).fetchall()
        if not rows:
            print("No slippage records yet.")
            return
        n_sf = conn.execute(
            "SELECT COUNT(*) FROM slippage_log "
            "WHERE note LIKE 'implementation-shortfall%'").fetchone()[0]
        print(f"{'strategy':<22} {'n':>6} {'avg_bps':>10} {'min':>8} {'max':>8}")
        for r in rows:
            print(f"{r['strategy_name']:<22} {r['n']:>6} "
                  f"{r['avg_bps']:>+9.1f}bp {r['min_bps']:>+7.1f}bp "
                  f"{r['max_bps']:>+7.1f}bp")
        if n_sf:
            print(f"\nWARNING: {n_sf} of these rows are IMPLEMENTATION SHORTFALL "
                  "(drift included),\nnot execution slippage - see the note column. "
                  "This flat view POOLS batches,\nwhich shortfall rows must never be. "
                  "Use --alpaca-csv for the per-batch report.")


# What each batch's shortfall is actually COMPOSED of. A batch with no entry here
# is reported without a composition claim rather than with a guessed one.
BATCH_COMPOSITION = {
    "2026-07-07": ("sim CLOSE reference vs a 14:20 ET INTRADAY fill "
                   "-> ~1h40m of intraday drift (record CT.4)"),
    "2026-08-03": ("sim CLOSE reference vs the NEXT session's OPEN "
                   "(09:30-09:36 ET on 08-04) -> an OVERNIGHT GAP (record CS.4)"),
}


def report_alpaca(paired: list[dict], unpaired: list[dict]) -> None:
    """Per (sleeve x batch x side). NEVER pooled across batches - see record CS.4."""
    print("\n=== SIM vs ALPACA PAPER MIRROR - IMPLEMENTATION SHORTFALL in bps "
          "(positive = mirror did WORSE than the sim) ===")
    print("PAPER-venue fills. Indicative, NOT proof of real-money execution.")
    print("SHORTFALL, NOT SLIPPAGE: the sim books at a CLOSE and the mirror fills")
    print("hours later, so these numbers INCLUDE drift. They are NOT a spread")
    print("measurement and MUST NOT be used to recalibrate HALF_SPREAD_BPS.\n")

    groups: dict[tuple, list[float]] = {}
    for p in paired:
        groups.setdefault((p["rebalance"], p["sleeve"], p["side"]), []).append(p["bps"])

    print(f"{'rebalance':<12} {'sleeve':<30} {'side':<5} {'n':>4} "
          f"{'mean':>9} {'median':>9} {'p95':>9} {'min':>9} {'max':>9}")
    for k in sorted(groups):
        s = _stats(groups[k])
        print(f"{k[0]:<12} {k[1]:<30} {k[2]:<5} {s['n']:>4} "
              f"{s['mean']:>+8.1f} {s['median']:>+8.1f} {s['p95']:>+8.1f} "
              f"{s['min']:>+8.1f} {s['max']:>+8.1f}")

    for reb in sorted({p["rebalance"] for p in paired}):
        vals = [p["bps"] for p in paired if p["rebalance"] == reb]
        s = _stats(vals)
        tag = BATCH_COMPOSITION.get(
            reb, "composition NOT characterised for this batch - do not interpret")
        print(f"\n  {reb} ALL SLEEVES: n={s['n']} mean={s['mean']:+.1f}bps "
              f"median={s['median']:+.1f}bps p95={s['p95']:+.1f}bps")
        print(f"    -> {tag}")
    print("\n  The two batches above are NOT comparable to each other and must")
    print("  NEVER be pooled into one number: they differ in fill mechanics")
    print("  (intraday vs overnight), not in execution quality.")

    print(f"\nUNPAIRED: {len(unpaired)} of {len(paired) + len(unpaired)} fills.")
    reasons: dict[str, int] = {}
    for u in unpaired:
        reasons[u["reason"]] = reasons.get(u["reason"], 0) + 1
    for r, n in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print(f"  {n:>4}  {r}")
    print("  (An unpaired mirror fill is EXPECTED, not an error: alpaca_sync\n"
          "   reconciles each account to TARGET WEIGHTS, so it trims or tops up\n"
          "   names the sim simply holds at a different qty. Those fills have no\n"
          "   sim entry/exit leg to compare against.)")


def write_slippage_log(paired: list[dict], conn) -> tuple[int, int]:
    """Append paired fills to slippage_log -> (written, skipped_as_duplicate).

    Caller owns the transaction.

    Re-running is a no-op instead of a doubling. This is a live-DB write Evan
    runs by hand, so "he ran it twice" is a realistic accident, and duplicated
    rows would silently halve every later mean without failing anything.
    (strategy_name, ticker, direction, broker_filled_at) identifies a fill:
    one order fills at one timestamp.
    """
    conn.executescript(SCHEMA)
    n = skipped = 0
    for p in paired:
        dup = conn.execute(
            "SELECT 1 FROM slippage_log WHERE strategy_name=? AND ticker=? "
            "AND direction=? AND broker_filled_at=? LIMIT 1",
            (p["sleeve"], p["ticker"], p["side"], p["broker_dt"])).fetchone()
        if dup:
            skipped += 1
            continue
        conn.execute("""
            INSERT INTO slippage_log
              (strategy_name, ticker, paper_pos_id, paper_fill, paper_filled_at,
               broker_fill, broker_filled_at, slippage_bps, direction, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (p["sleeve"], p["ticker"], p["pos_id"], p["sim_px"], str(p["sim_dt"]),
              p["broker_px"], p["broker_dt"], p["bps"], p["side"],
              f"implementation-shortfall alpaca-paper-mirror "
              f"rebalance={p['rebalance']} order={p['order_id']}"))
        n += 1
    return n, skipped


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, help="CSV of real broker fills to ingest")
    ap.add_argument("--strategy", help="default strategy name if CSV doesn't have strategy_hint")
    ap.add_argument("--report", action="store_true", help="print summary")
    ap.add_argument("--alpaca-csv", type=Path,
                    help="CSV from fetch_alpaca_fills (M6.2): per-batch "
                         "IMPLEMENTATION SHORTFALL. Read-only unless --execute.")
    ap.add_argument("--execute", action="store_true",
                    help="With --alpaca-csv: actually append to slippage_log.")
    ap.add_argument("--db", default=None, help="DB path (default: live var/trades.db).")
    args = ap.parse_args()

    if args.alpaca_csv:
        # Read-only by default, matching backadjust_split / remark_nav_day.
        import sqlite3
        from trading_bot.config import DB_PATH
        db = Path(args.db) if args.db else DB_PATH
        ro = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
        ro.row_factory = sqlite3.Row
        paired, unpaired = pair_alpaca_csv(args.alpaca_csv, ro)
        ro.close()
        report_alpaca(paired, unpaired)
        if not args.execute:
            print(f"\nDRY RUN - {len(paired)} row(s) would be appended to "
                  f"slippage_log. Re-run with --execute to write.")
            return 0
        if args.db:
            w = sqlite3.connect(db)
            n, skipped = write_slippage_log(paired, w)
            w.commit()
            w.close()
        else:
            with connect() as conn:
                n, skipped = write_slippage_log(paired, conn)
        print(f"\nAppended {n} row(s) to slippage_log in {db}"
              f"{f' ({skipped} already present, skipped)' if skipped else ''}.")
        print("Every row is IMPLEMENTATION SHORTFALL (note column says so), not "
              "execution slippage.")
        return 0

    ensure_schema()
    if args.csv:
        n = ingest_csv(args.csv, args.strategy)
        print(f"\nIngested {n} pairings.")
    if args.report:
        report()
    if not args.csv and not args.report:
        print("Nothing to do. Use --csv FILE, --alpaca-csv FILE, or --report.")
        print("Schema is initialized. Run with --report any time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
