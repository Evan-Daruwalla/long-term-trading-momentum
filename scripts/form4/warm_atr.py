"""Pre-warm price_cache with kind='atr_pct_20' for the R11 backtest.

Mirrors warm_cache.py but writes one row per (ticker, entry_date), where
entry_date = the next trading day after each signal's transaction_date.
ATR is the rolling mean of True Range over the 20 bars ending on that
day, expressed as a fraction of close.

ATR is fully determined by pre-entry bars, so the value is stable forever
and we INSERT OR IGNORE — re-running is free. Run before R11 backtest.
"""
from __future__ import annotations

import re
import sqlite3
import time
from datetime import date

import pandas as pd
import yfinance as yf

from trading_bot.config import DB_PATH

BATCH_SIZE = 200
DL_START   = "2020-06-01"   # 7+ months of buffer for ATR(20) warmup
DL_END     = "2026-05-01"
SIG_START  = "2021-05-01"
TICKER_RE  = re.compile(r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$")
ATR_WINDOW = 20
KIND       = f"atr_pct_{ATR_WINDOW}"


def _valid(t: str) -> bool:
    return bool(TICKER_RE.match(t))


def _load_signal_pairs() -> dict[str, list[str]]:
    """{ticker: [sorted signal-date strings]} for pairs that don't yet have
    an atr_pct_20 row keyed by the next-trading-day."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """
        SELECT DISTINCT s.ticker, substr(s.transaction_date, 1, 10)
        FROM signals s
        WHERE s.filed_at >= ?
          AND s.transaction_date >= '2020-01-01'
          AND s.transaction_date <= '2026-12-31'
        ORDER BY s.ticker, s.transaction_date
        """,
        (SIG_START,),
    ).fetchall()
    conn.close()

    pairs: dict[str, list[str]] = {}
    for ticker, dt in rows:
        if _valid(ticker):
            pairs.setdefault(ticker, []).append(dt)
    return pairs


def _bulk_insert(rows: list[tuple]) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.executemany(
        "INSERT OR IGNORE INTO price_cache (ticker, kind, key_date, price) VALUES (?,?,?,?)",
        rows,
    )
    conn.commit()
    conn.close()


def _process_batch(tickers: list[str], pairs: dict[str, list[str]]) -> int:
    raw = None
    for attempt in range(3):
        try:
            raw = yf.download(
                tickers,
                start=DL_START, end=DL_END,
                auto_adjust=False, progress=False,
                group_by="ticker",
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
        if ticker not in pairs:
            continue
        try:
            df = raw[ticker].dropna(how="all").sort_index()
        except KeyError:
            # Delisted/missing — write NULLs keyed by signal_date itself
            # (good enough — atr_pct() falls back to STOP_LOSS_PCT on None).
            for sig in pairs[ticker]:
                out.append((ticker, KIND, sig, None))
            continue
        if df.empty or len(df) < ATR_WINDOW + 1:
            for sig in pairs[ticker]:
                out.append((ticker, KIND, sig, None))
            continue

        # Compute ATR%(20) per trading day in the series
        highs  = df["High"].astype(float)
        lows   = df["Low"].astype(float)
        closes = df["Close"].astype(float)
        prev_c = closes.shift(1)
        tr = pd.concat([highs - lows,
                        (highs - prev_c).abs(),
                        (lows  - prev_c).abs()], axis=1).max(axis=1)
        atr   = tr.rolling(window=ATR_WINDOW, min_periods=ATR_WINDOW).mean()
        atr_p = atr / closes

        idx_dates = [d.date() if hasattr(d, "date") else d for d in df.index]
        date_to_pos = {d: i for i, d in enumerate(idx_dates)}

        for sig in pairs[ticker]:
            sig_d = date.fromisoformat(sig)
            # Find the next trading day strictly after sig_d
            next_pos = next((i for i, d in enumerate(idx_dates) if d > sig_d), None)
            if next_pos is None:
                out.append((ticker, KIND, sig_d.isoformat(), None))
                continue
            entry_d = idx_dates[next_pos]
            v = atr_p.iloc[next_pos]
            val = float(v) if pd.notna(v) else None
            out.append((ticker, KIND, entry_d.isoformat(), val))

    if out:
        _bulk_insert(out)
    return len(out)


def main() -> None:
    print("Loading signal pairs...", flush=True)
    pairs = _load_signal_pairs()
    tickers = sorted(pairs)
    n_pairs = sum(len(v) for v in pairs.values())
    print(f"  {len(tickers)} tickers, {n_pairs} (ticker, signal_date) pairs", flush=True)

    batches = [tickers[i:i+BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]
    print(f"  {len(batches)} batches of up to {BATCH_SIZE}", flush=True)

    total = 0
    for i, batch in enumerate(batches, 1):
        t0 = time.time()
        n = _process_batch(batch, pairs)
        total += n
        print(f"  [{i:3d}/{len(batches)}] +{n:6d} rows  {time.time()-t0:5.1f}s  "
              f"(total {total:,})", flush=True)
        if i < len(batches):
            time.sleep(1.0)

    print(f"\nDone. {total:,} ATR rows written.", flush=True)


if __name__ == "__main__":
    main()
