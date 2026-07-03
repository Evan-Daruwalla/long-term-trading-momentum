"""Fetch yfinance 'sector' for tickers, store in fundamentals_cache.

Quick targeted fetch — by default only refreshes the top-N tickers by
market cap (sufficient for sector-restricted universe tests). Stores
sector as a string in fundamentals_cache.value column? No — value is
REAL. We need a separate column or table.

Schema: new sectors_cache table (ticker, sector, fetched_at).
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from datetime import datetime, timezone

import yfinance as yf

from trading_bot.config import DB_PATH


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS sectors_cache (
            ticker     TEXT PRIMARY KEY,
            sector     TEXT,
            industry   TEXT,
            fetched_at TEXT NOT NULL
        )"""
    )


def _candidates(conn: sqlite3.Connection, limit: int) -> list[str]:
    """Top N tickers by current marketCap that aren't already in sectors_cache."""
    rows = conn.execute(
        """SELECT f.ticker FROM fundamentals_cache f
           WHERE f.field='marketCap' AND f.value IS NOT NULL
             AND f.ticker NOT IN (SELECT ticker FROM sectors_cache)
           ORDER BY f.value DESC
           LIMIT ?""",
        (limit,)
    ).fetchall()
    return [r[0] for r in rows]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=1500,
                    help="Refresh top-N tickers by current market cap")
    ap.add_argument("--rate", type=float, default=0.15)
    args = ap.parse_args()

    conn = sqlite3.connect(DB_PATH)
    _ensure_table(conn)
    todo = _candidates(conn, args.top)
    print(f"To fetch: {len(todo)} tickers", flush=True)
    if not todo:
        print("Nothing to fetch.")
        return 0

    started = time.time()
    fetched_at = datetime.now(timezone.utc).isoformat()
    ok = fail = 0
    for i, t in enumerate(todo, 1):
        try:
            info = yf.Ticker(t).info
            sector = info.get("sector")
            industry = info.get("industry")
            conn.execute(
                "INSERT OR REPLACE INTO sectors_cache "
                "(ticker, sector, industry, fetched_at) VALUES (?,?,?,?)",
                (t, sector, industry, fetched_at)
            )
            conn.commit()
            if sector:
                ok += 1
            else:
                fail += 1
        except Exception:
            fail += 1
        if i % 50 == 0 or i == len(todo):
            el = time.time() - started
            rate = i / el
            eta = (len(todo) - i) / rate
            print(f"  [{i:5d}/{len(todo)}]  ok={ok}  fail={fail}  "
                  f"{rate:.1f}/s  ETA {eta/60:.1f} min", flush=True)
        time.sleep(args.rate)

    conn.close()
    print(f"\nDone in {(time.time()-started)/60:.1f} min. ok={ok}, fail={fail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
