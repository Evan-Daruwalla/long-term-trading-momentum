"""Pre-warm price_cache with kind='close' for every (ticker, trading_day)
the simulator might evaluate during a backtest.

Why: monitor.price_on_date() is called once per (open_position, day) inside
the day-loop. Without a warm cache, every miss hits yfinance, which hands
back rate-limit errors that cascade into non-deterministic stop-fill
delays (see R11 vs R12: same code, ~35pp swing in headline P&L because
different yfinance calls happened to succeed each run).

After this script runs, every close lookup the backtest needs is an O(1)
in-memory dict hit (preload_caches loads the whole price_cache table at
backtest start).

Strategy: for each unique ticker in signals.ticker, bulk-download daily
OHLCV for the entire backtest range once, then write one `close` row per
trading day. Idempotent (INSERT OR IGNORE).
"""
from __future__ import annotations

import re
import sqlite3
import time

import pandas as pd
import yfinance as yf

from trading_bot.config import DB_PATH

BATCH_SIZE = 200
DL_START   = "2020-06-01"   # buffer so the first signal day has prior history
DL_END     = "2026-05-08"   # one day past TODAY
SIG_START  = "2021-05-01"
TICKER_RE  = re.compile(r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$")
KIND       = "close"


def _valid(t: str) -> bool:
    return bool(TICKER_RE.match(t))


def _load_universe() -> list[str]:
    """All buy-tickers we might enter into, MINUS any that already have a
    substantial close history cached (resume support). The threshold of
    >=500 cached rows means we've completed a full bulk download for that
    ticker — anything less and we re-download to fill gaps."""
    conn = sqlite3.connect(DB_PATH)
    all_tickers = {r[0] for r in conn.execute(
        "SELECT DISTINCT ticker FROM signals "
        "WHERE transaction_code='P' AND filed_at >= ?",
        (SIG_START,),
    ).fetchall()}
    done = {r[0] for r in conn.execute(
        "SELECT ticker FROM price_cache WHERE kind='close' "
        "GROUP BY ticker HAVING COUNT(*) >= 500"
    ).fetchall()}
    conn.close()
    todo = sorted({t for t in all_tickers if _valid(t)} - done)
    print(f"  resume: {len(done)} already warmed, {len(todo)} to fetch", flush=True)
    return todo


def _bulk_insert(rows: list[tuple]) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.executemany(
        "INSERT OR IGNORE INTO price_cache (ticker, kind, key_date, price) "
        "VALUES (?,?,?,?)",
        rows,
    )
    conn.commit()
    conn.close()


def _process_batch(tickers: list[str]) -> int:
    raw = None
    for attempt in range(3):
        try:
            raw = yf.download(
                tickers, start=DL_START, end=DL_END,
                auto_adjust=False, progress=False, group_by="ticker",
            )
            break
        except Exception as e:
            print(f"  download error (attempt {attempt+1}): {e}", flush=True)
            if attempt < 2:
                time.sleep(30)
    if raw is None or raw.empty:
        return 0
    if len(tickers) == 1:
        raw = pd.concat({tickers[0]: raw}, axis=1)

    out: list[tuple] = []
    for ticker in tickers:
        try:
            df = raw[ticker].dropna(subset=["Close"]).sort_index()
        except KeyError:
            # Rate-limited / delisted — skip rather than write None rows
            # (would conflate "yfinance didn't answer" with "ticker had no
            # bar that day", and the strict-cache mode below relies on
            # presence == answered).
            continue
        if df.empty:
            continue
        for ts, close in df["Close"].items():
            d = ts.date() if hasattr(ts, "date") else ts
            out.append((ticker, KIND, d.isoformat(), float(close)))
    if out:
        _bulk_insert(out)
    return len(out)


def main() -> None:
    tickers = _load_universe()
    print(f"Universe: {len(tickers)} buy-tickers", flush=True)
    batches = [tickers[i:i+BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]
    print(f"  {len(batches)} batches of up to {BATCH_SIZE}", flush=True)

    total = 0
    for i, batch in enumerate(batches, 1):
        t0 = time.time()
        n = _process_batch(batch)
        total += n
        print(f"  [{i:3d}/{len(batches)}] +{n:7,d} rows  {time.time()-t0:5.1f}s  "
              f"(total {total:,})", flush=True)
        if i < len(batches):
            time.sleep(1.0)
    print(f"\nDone. {total:,} close rows written.", flush=True)


if __name__ == "__main__":
    main()
