"""Backfill daily-volume rows for every ticker that has cached closes
but no cached volumes. Same yf.download flow as warm_resilient.py but
only emits `kind='volume'` rows (the close cache is already done, no
need to re-write).

Volume is stored as raw shares-per-day. Dollar volume is computed on
the fly at universe-filter time as `close * volume`.

Idempotent. Safe to interrupt and resume — gap detection skips tickers
that already have substantial volume coverage.

Usage:
  python -m scripts.warm_volumes --since 2010-01-01 --until 2026-05-01
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
import time
from datetime import date

import pandas as pd
import yfinance as yf

from trading_bot.config import DB_PATH

BATCH_SIZE  = 50
BATCH_DELAY = 5.0
LONG_PAUSE  = 120.0
TICKER_RE   = re.compile(r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$")


def _valid(t: str) -> bool:
    return bool(TICKER_RE.match(t))


def _is_rate_limit(exc: BaseException) -> bool:
    s = str(exc).lower()
    return "too many requests" in s or "rate limit" in s


def _expected_volume_rows(dl_start: str, dl_end: str) -> int:
    d0 = date.fromisoformat(dl_start); d1 = date.fromisoformat(dl_end)
    calendar_days = max(1, (d1 - d0).days + 1)
    return int(calendar_days * 0.50 * (252 / 365))


def _missing_tickers_for_volume(conn: sqlite3.Connection,
                                dl_start: str, dl_end: str) -> list[str]:
    """Tickers that have close-cache coverage in [dl_start, dl_end] but
    insufficient volume coverage. Below the threshold = need re-warm."""
    threshold = _expected_volume_rows(dl_start, dl_end)
    rows = conn.execute(
        """
        SELECT c.ticker,
               COUNT(v.key_date) AS n_vol
        FROM (SELECT DISTINCT ticker FROM price_cache
              WHERE kind='close' AND key_date BETWEEN ? AND ?) c
        LEFT JOIN price_cache v
          ON v.ticker=c.ticker AND v.kind='volume'
          AND v.key_date BETWEEN ? AND ?
        GROUP BY c.ticker
        HAVING n_vol < ?
        """,
        (dl_start, dl_end, dl_start, dl_end, threshold),
    ).fetchall()
    return sorted({t for (t, _n) in rows if _valid(t)})


def _bulk_insert(rows: list[tuple]) -> None:
    if not rows:
        return
    conn = sqlite3.connect(DB_PATH)
    conn.executemany(
        "INSERT OR IGNORE INTO price_cache (ticker, kind, key_date, price) "
        "VALUES (?,?,?,?)",
        rows,
    )
    conn.commit()
    conn.close()


def _download(tickers: list[str], start: str, end: str) -> pd.DataFrame | None:
    for attempt in range(5):
        try:
            return yf.download(
                tickers, start=start, end=end, auto_adjust=False,
                progress=False, group_by="ticker", actions=False,
            )
        except Exception as e:
            if _is_rate_limit(e):
                pause = LONG_PAUSE * (attempt + 1)
                print(f"  rate-limited; sleeping {pause:.0f}s "
                      f"(attempt {attempt+1}/5)", flush=True)
                time.sleep(pause)
                continue
            print(f"  download error: {e}", flush=True)
            return None
    return None


def _emit_volume_rows(ticker: str, df: pd.DataFrame) -> list[tuple]:
    if df is None or df.empty or "Volume" not in df.columns:
        return []
    vols = df["Volume"].dropna()
    return [(ticker, "volume",
             (ts.date() if hasattr(ts, "date") else ts).isoformat(),
             float(v))
            for ts, v in vols.items()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2010-01-01")
    ap.add_argument("--until", default="2026-05-01")
    args = ap.parse_args()

    print(f"Volume warm: [{args.since}..{args.until}]", flush=True)
    conn = sqlite3.connect(DB_PATH)
    todo = _missing_tickers_for_volume(conn, args.since, args.until)
    conn.close()
    print(f"  Tickers needing volume backfill: {len(todo):,}", flush=True)
    if not todo:
        print("Nothing missing. Volume cache is full.", flush=True)
        return 0

    batches = [todo[i:i + BATCH_SIZE] for i in range(0, len(todo), BATCH_SIZE)]
    print(f"  {len(batches)} batches of up to {BATCH_SIZE}\n", flush=True)

    started = time.time()
    written = 0
    for i, batch in enumerate(batches, 1):
        t0 = time.time()
        df = _download(batch, args.since, args.until)
        rows: list[tuple] = []
        if df is not None and not df.empty:
            if len(batch) == 1:
                df = pd.concat({batch[0]: df}, axis=1)
            for ticker in batch:
                try:
                    sub = df[ticker].dropna(how="all").sort_index()
                except KeyError:
                    continue
                if sub.empty:
                    continue
                rows.extend(_emit_volume_rows(ticker, sub))
        if rows:
            _bulk_insert(rows)
            written += len(rows)
        elapsed = time.time() - t0
        total_elapsed = time.time() - started
        pct = 100 * i / len(batches)
        eta = (total_elapsed / max(i, 1)) * (len(batches) - i)
        print(f"  [{i:3d}/{len(batches)}] {pct:5.1f}%  +{len(rows):5d} rows  "
              f"{elapsed:5.1f}s  (ETA {eta/60:.1f} min, written {written:,})",
              flush=True)
        if i < len(batches):
            time.sleep(BATCH_DELAY)

    print(f"\nDone in {(time.time() - started)/60:.1f} min. "
          f"{written:,} rows written.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
