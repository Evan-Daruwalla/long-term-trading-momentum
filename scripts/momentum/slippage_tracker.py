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


def slippage_bps(sim_px: float, broker_px: float, side: str) -> float:
    """Positive bps = the mirror did WORSE than the sim (a real cost).

    Buy:  paying more than the sim assumed is a cost.
    Sell: receiving less than the sim assumed is a cost, so the sign flips.
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
                # NOT an error. The mirror reconciles to TARGET WEIGHTS, so it
                # trims/tops-up names the sim merely holds at a different qty -
                # those fills have no sim leg to pair against, by construction.
                unpaired.append({**row, "reason": (
                    "no sim leg: mirror weight adjustment on a name the sim did "
                    "not open/close at this rebalance")})
                continue
            paired.append({
                "sleeve": row["sleeve"], "ticker": row["ticker"],
                "side": row["side"], "batch": batch, "rebalance": rebalance,
                "sim_px": r["px"], "broker_px": broker_px,
                "bps": slippage_bps(r["px"], broker_px, row["side"]),
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
        print(f"{'strategy':<22} {'n':>6} {'avg_bps':>10} {'min':>8} {'max':>8}")
        for r in rows:
            print(f"{r['strategy_name']:<22} {r['n']:>6} "
                  f"{r['avg_bps']:>+9.1f}bp {r['min_bps']:>+7.1f}bp "
                  f"{r['max_bps']:>+7.1f}bp")


def report_alpaca(paired: list[dict], unpaired: list[dict]) -> None:
    """Per (sleeve x batch x side). NEVER pooled across batches - see record CS.4."""
    print("\n=== SIM vs ALPACA PAPER MIRROR - slippage in bps "
          "(positive = mirror did WORSE than the sim) ===")
    print("PAPER-venue fills. Indicative, NOT proof of real-money execution.\n")

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
        tag = ("INTRADAY - a real execution-quality measurement"
               if reb == "2026-07-07" else
               "NOT SLIPPAGE - filled at the NEXT session open (record CS.4); "
               "this is dominated by the OVERNIGHT GAP")
        print(f"\n  {reb} ALL SLEEVES: n={s['n']} mean={s['mean']:+.1f}bps "
              f"median={s['median']:+.1f}bps p95={s['p95']:+.1f}bps")
        print(f"    -> {tag}")

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


def write_slippage_log(paired: list[dict], conn) -> int:
    """Append paired fills to slippage_log. Caller owns the transaction."""
    conn.executescript(SCHEMA)
    n = 0
    for p in paired:
        conn.execute("""
            INSERT INTO slippage_log
              (strategy_name, ticker, paper_pos_id, paper_fill, paper_filled_at,
               broker_fill, broker_filled_at, slippage_bps, direction, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (p["sleeve"], p["ticker"], p["pos_id"], p["sim_px"], str(p["sim_dt"]),
              p["broker_px"], p["broker_dt"], p["bps"], p["side"],
              f"alpaca-paper-mirror rebalance={p['rebalance']} "
              f"order={p['order_id']}"))
        n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, help="CSV of real broker fills to ingest")
    ap.add_argument("--strategy", help="default strategy name if CSV doesn't have strategy_hint")
    ap.add_argument("--report", action="store_true", help="print summary")
    ap.add_argument("--alpaca-csv", type=Path,
                    help="CSV from fetch_alpaca_fills (M6.2). Read-only unless --execute.")
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
            n = write_slippage_log(paired, w)
            w.commit()
            w.close()
        else:
            with connect() as conn:
                n = write_slippage_log(paired, conn)
        print(f"\nAppended {n} row(s) to slippage_log in {db}.")
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
