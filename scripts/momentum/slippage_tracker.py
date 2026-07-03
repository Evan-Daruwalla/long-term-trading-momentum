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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, help="CSV of real broker fills to ingest")
    ap.add_argument("--strategy", help="default strategy name if CSV doesn't have strategy_hint")
    ap.add_argument("--report", action="store_true", help="print summary")
    args = ap.parse_args()

    ensure_schema()
    if args.csv:
        n = ingest_csv(args.csv, args.strategy)
        print(f"\nIngested {n} pairings.")
    if args.report:
        report()
    if not args.csv and not args.report:
        print("Nothing to do. Use --csv FILE or --report.")
        print("Schema is initialized. Run with --report any time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
