"""Pre-warm price_cache for the R9 backtest universe.

Uses yf.download() in batches of BATCH_SIZE tickers to fetch the full
OHLCV history in one API call per batch instead of one call per
(ticker, date) pair. For 7K tickers this shrinks ~232K individual API
calls down to ~35 batch calls — well within Yahoo's rate limit.

Writes to price_cache:
  - next_open      — open on the first trading day after signal date
  - next_open_vol  — volume on that same day
  - next_open_range — (High-Low)/Open on that same day
  - above_ma_50    — 1.0/0.0/NULL per is_above_ma logic

Run once before the backtest; idempotent (uses INSERT OR IGNORE).
"""
from __future__ import annotations

import re
import sqlite3
import sys
import time
from datetime import date, timedelta

import pandas as pd
import yfinance as yf

from trading_bot.config import DB_PATH

# --- config ---
BATCH_SIZE   = 200        # tickers per yf.download call
DL_START     = "2020-06-01"   # extra buffer for 50-day MA warmup
DL_END       = "2026-05-01"
SIG_START    = "2021-05-01"   # only warm for signals we'll actually use
TICKER_RE    = re.compile(r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$')
MA_WINDOW    = 50

KINDS = ("next_open", "next_open_vol", "next_open_range", f"above_ma_{MA_WINDOW}")


def _valid(ticker: str) -> bool:
    return bool(TICKER_RE.match(ticker))


def _load_signal_pairs() -> dict[str, list[str]]:
    """Return {ticker: [sorted date strings]} for uncached pairs."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """
        SELECT DISTINCT s.ticker, s.transaction_date
        FROM signals s
        WHERE s.filed_at  >= ?
          AND s.transaction_date >= '2020-01-01'
          AND s.transaction_date <= '2026-12-31'
          AND NOT EXISTS (
              SELECT 1 FROM price_cache p
              WHERE p.ticker = s.ticker
                AND p.kind   = 'next_open'
                AND p.key_date = substr(s.transaction_date, 1, 10)
          )
        ORDER BY s.ticker, s.transaction_date
        """,
        (SIG_START,),
    ).fetchall()
    conn.close()

    pairs: dict[str, list[str]] = {}
    for ticker, dt in rows:
        if _valid(ticker):
            pairs.setdefault(ticker, []).append(dt[:10])
    return pairs


def _bulk_insert(rows: list[tuple]) -> None:
    """INSERT OR IGNORE rows into price_cache. rows = (ticker, kind, key_date, price)."""
    conn = sqlite3.connect(DB_PATH)
    conn.executemany(
        "INSERT OR IGNORE INTO price_cache (ticker, kind, key_date, price) VALUES (?,?,?,?)",
        rows,
    )
    conn.commit()
    conn.close()


def _process_batch(
    tickers: list[str],
    pairs: dict[str, list[str]],
) -> int:
    """Download OHLCV for tickers and compute + store cache rows. Returns rows written."""
    raw = None
    for attempt in range(3):
        try:
            raw = yf.download(
                tickers,
                start=DL_START,
                end=DL_END,
                auto_adjust=False,
                progress=False,
                group_by="ticker",
            )
            break
        except Exception as e:
            print(f"  download error (attempt {attempt+1}): {e}", flush=True)
            if attempt < 2:
                time.sleep(30)

    if raw is None or raw.empty:
        return 0

    # Normalise to multi-level even when only 1 ticker
    if len(tickers) == 1:
        raw = pd.concat({tickers[0]: raw}, axis=1)

    cache_rows: list[tuple] = []

    for ticker in tickers:
        if ticker not in pairs:
            continue
        try:
            df = raw[ticker].dropna(how="all")
        except KeyError:
            # Ticker absent from download (delisted/not found) — cache all its
            # pairs as permanent misses so the backtest doesn't retry them live.
            for key_date_str in pairs[ticker]:
                for kind in KINDS:
                    cache_rows.append((ticker, kind, key_date_str, None))
            continue
        if df.empty:
            for key_date_str in pairs[ticker]:
                for kind in KINDS:
                    cache_rows.append((ticker, kind, key_date_str, None))
            continue

        df = df.sort_index()
        # Convert index to date objects for lookups
        idx_dates = [d.date() if hasattr(d, 'date') else d for d in df.index]
        idx_series = pd.Series(range(len(df)), index=idx_dates)

        # 50-day rolling MA on Close (need at least window rows)
        closes = df["Close"]
        ma50 = closes.rolling(window=MA_WINDOW, min_periods=MA_WINDOW).mean()

        for key_date_str in pairs[ticker]:
            key_date = date.fromisoformat(key_date_str[:10])

            # Find the next trading day after key_date in the index
            # (the first date in idx_dates that is strictly > key_date)
            next_idx = None
            for i, d in enumerate(idx_dates):
                if d > key_date:
                    next_idx = i
                    break

            if next_idx is None:
                # No data after key_date — permanent miss
                for kind in KINDS:
                    cache_rows.append((ticker, kind, key_date_str, None))
                continue

            row = df.iloc[next_idx]
            open_price = float(row["Open"]) if pd.notna(row["Open"]) else None
            volume     = float(row["Volume"]) if pd.notna(row["Volume"]) else None

            if open_price and open_price > 0:
                high = float(row["High"]) if pd.notna(row["High"]) else None
                low  = float(row["Low"])  if pd.notna(row["Low"])  else None
                rng  = ((high - low) / open_price
                        if high is not None and low is not None else None)
            else:
                rng = None

            # above_ma_50: use close on key_date (not next_open day), matching
            # is_above_ma() which checks as_of's close against its own MA.
            # Find key_date in index
            if key_date in idx_series.index:
                idx_on = idx_series[key_date]
                ma_val = ma50.iloc[idx_on]
                close_val = closes.iloc[idx_on]
                if pd.notna(ma_val) and pd.notna(close_val):
                    above = float(close_val > ma_val)  # 1.0 or 0.0
                else:
                    above = None
            else:
                above = None

            cache_rows.append((ticker, "next_open",       key_date_str, open_price))
            cache_rows.append((ticker, "next_open_vol",   key_date_str, volume))
            cache_rows.append((ticker, "next_open_range", key_date_str, rng))
            cache_rows.append((ticker, f"above_ma_{MA_WINDOW}", key_date_str, above))

    if cache_rows:
        _bulk_insert(cache_rows)

    return len(cache_rows)


def main() -> None:
    print("Loading uncached signal pairs...", flush=True)
    pairs = _load_signal_pairs()
    tickers = sorted(pairs)
    print(f"  {len(tickers)} tickers, {sum(len(v) for v in pairs.values())} pairs to warm", flush=True)

    batches = [tickers[i:i+BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]
    print(f"  {len(batches)} batches of up to {BATCH_SIZE}", flush=True)

    total_rows = 0
    for i, batch in enumerate(batches, 1):
        t0 = time.time()
        rows = _process_batch(batch, pairs)
        elapsed = time.time() - t0
        total_rows += rows
        pct = 100 * i / len(batches)
        print(
            f"  [{i:3d}/{len(batches)}] {pct:5.1f}%  "
            f"+{rows:6d} rows  {elapsed:5.1f}s  "
            f"(total {total_rows:,})",
            flush=True,
        )
        # Brief pause between batches to avoid hammering Yahoo
        if i < len(batches):
            time.sleep(1.0)

    print(f"\nDone. {total_rows:,} rows written to price_cache.", flush=True)


if __name__ == "__main__":
    main()
