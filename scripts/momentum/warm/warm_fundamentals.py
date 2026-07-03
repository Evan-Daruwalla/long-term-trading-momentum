"""Bulk-fetch yfinance fundamentals for all tickers with cached prices.

Stores in sqlite `fundamentals_cache` (ticker, field, value, fetched_at).
This is a SNAPSHOT — yfinance .info returns current values only, no
point-in-time. Use only for held-out tests where lookahead bias is small
(recent fundamentals ~= valid for recent dates).

For a real production quality factor, replace with SEC XBRL pipeline
(see sleeves_verdict.md "Open path: quality factor"). This is the quick
1-day test alternative.

Fields fetched (yfinance .info keys):
  returnOnEquity, debtToEquity, grossMargins, operatingMargins,
  profitMargins, returnOnAssets, marketCap, currentRatio

Usage:
  python -m scripts.momentum.warm_fundamentals --limit 100  # smoke
  python -m scripts.momentum.warm_fundamentals              # all tickers
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from datetime import datetime, timezone

import yfinance as yf

from trading_bot.config import DB_PATH

FIELDS = [
    "returnOnEquity", "debtToEquity", "grossMargins", "operatingMargins",
    "profitMargins", "returnOnAssets", "marketCap", "currentRatio",
]


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS fundamentals_cache (
            ticker      TEXT NOT NULL,
            field       TEXT NOT NULL,
            value       REAL,
            fetched_at  TEXT NOT NULL,
            PRIMARY KEY (ticker, field)
        )"""
    )


def _all_cached_tickers(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT DISTINCT ticker FROM price_cache WHERE kind='close' ORDER BY ticker"
    ).fetchall()
    return [r[0] for r in rows]


def _already_fetched(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        "SELECT DISTINCT ticker FROM fundamentals_cache"
    ).fetchall()
    return {r[0] for r in rows}


def fetch_one(ticker: str) -> dict[str, float | None]:
    """Returns {field: value_or_None}. Catches all errors so the loop
    keeps going on individual ticker failures."""
    try:
        info = yf.Ticker(ticker).info
    except Exception:
        return {f: None for f in FIELDS}
    out: dict[str, float | None] = {}
    for f in FIELDS:
        v = info.get(f)
        try:
            out[f] = float(v) if v is not None else None
        except (TypeError, ValueError):
            out[f] = None
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None,
                    help="Limit to first N tickers (smoke testing).")
    ap.add_argument("--rate", type=float, default=0.15,
                    help="Seconds between requests (default 0.15 = ~6.6/sec).")
    args = ap.parse_args()

    conn = sqlite3.connect(DB_PATH)
    _ensure_table(conn)
    all_tickers = _all_cached_tickers(conn)
    done = _already_fetched(conn)
    todo = [t for t in all_tickers if t not in done]
    if args.limit:
        todo = todo[: args.limit]

    print(f"Total cached tickers: {len(all_tickers):,}", flush=True)
    print(f"Already in fundamentals_cache: {len(done):,}", flush=True)
    print(f"To fetch this run: {len(todo):,}", flush=True)
    if not todo:
        print("Nothing to do.", flush=True)
        return 0

    started = time.time()
    fetched_at = datetime.now(timezone.utc).isoformat()
    n_ok = 0
    n_fail = 0
    for i, t in enumerate(todo, 1):
        vals = fetch_one(t)
        has_any = any(v is not None for v in vals.values())
        rows = [(t, f, vals[f], fetched_at) for f in FIELDS]
        conn.executemany(
            "INSERT OR REPLACE INTO fundamentals_cache (ticker, field, value, fetched_at) "
            "VALUES (?,?,?,?)",
            rows,
        )
        conn.commit()
        if has_any:
            n_ok += 1
        else:
            n_fail += 1
        if i % 50 == 0 or i == len(todo):
            elapsed = time.time() - started
            rate = i / elapsed
            eta = (len(todo) - i) / rate
            print(f"  [{i:5d}/{len(todo)}]  ok={n_ok:5d} fail={n_fail:5d}  "
                  f"{rate:.1f}/s  ETA {eta/60:.1f} min", flush=True)
        time.sleep(args.rate)

    conn.close()
    print(f"\nDone in {(time.time()-started)/60:.1f} min. "
          f"{n_ok} fetched OK, {n_fail} no fundamentals.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
