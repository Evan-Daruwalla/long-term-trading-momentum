"""Detect delisted tickers via yfinance data-gap heuristic.

Form 25 (the actual SEC delisting notice) parsing is brittle — the form is
free-form HTML, ticker fields are inconsistent, and EDGAR full-index
filtering for form=25 returns thousands of issuer-CIKs that don't map cleanly
to tickers we hold. The heuristic below is empirically more reliable for our
backtest universe:

  For each ticker in signals.ticker (filtered to our backtest window), bulk-
  download daily OHLCV from yfinance for 2020-2026. If the last available
  bar is older than DEAD_AFTER_DAYS days before TODAY, classify the ticker
  as delisted on its last bar's date.

This catches the cases that actually matter for survivorship correction:
real delistings (zeros, M&A absorptions, regulatory boots) — yfinance stops
serving data shortly after delisting in all three cases. False positives
are rare; a healthy ticker with one missing bar still has bars later.

Outputs to a new SQLite table:
  delistings(ticker TEXT PRIMARY KEY, delist_date TEXT, last_price REAL, reason TEXT)

Run once before any backtest; idempotent (INSERT OR REPLACE).
"""
from __future__ import annotations

import re
import sqlite3
import time
from datetime import date, datetime, timedelta

import pandas as pd
import yfinance as yf

from trading_bot.config import DB_PATH

BATCH_SIZE = 200
DL_START = "2020-06-01"
DL_END   = "2026-05-08"   # one day past TODAY's likely run
TICKER_RE = re.compile(r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$")
# A ticker is "dead" if its last bar is more than this many days before
# the download window's end. 60 days catches genuine delistings while
# tolerating tickers with brief data outages.
DEAD_AFTER_DAYS = 60


def _ensure_schema() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS delistings (
          ticker      TEXT PRIMARY KEY,
          delist_date TEXT NOT NULL,
          last_price  REAL,
          reason      TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def _load_universe() -> list[str]:
    """All distinct tickers from signals (the universe the strategy could
    have entered). We only care about delistings for tickers we'd trade."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT DISTINCT ticker FROM signals WHERE transaction_code='P'"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows if TICKER_RE.match(r[0])]


def _process_batch(tickers: list[str], cutoff: date) -> list[tuple]:
    """Return (ticker, delist_date, last_price, reason) for newly-detected
    delistings in `tickers`. Skips tickers whose last bar is on/after cutoff."""
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
        return []
    if len(tickers) == 1:
        raw = pd.concat({tickers[0]: raw}, axis=1)

    out: list[tuple] = []
    for ticker in tickers:
        try:
            df = raw[ticker].dropna(how="all").sort_index()
        except KeyError:
            # Ticker is absent from the response. Could be a real delisting
            # OR a rate-limit failure for this specific ticker. We can't
            # distinguish by output alone — yfinance reports both as a
            # KeyError. Conservatively: skip. False negatives (missed
            # delistings) become survivorship bias we don't correct, but
            # false positives (recording IBM as delisted because yfinance
            # rate-limited that batch) would corrupt the backtest.
            continue
        if df.empty:
            # Same reasoning — empty df is ambiguous. Skip rather than
            # falsely brand the ticker as delisted at DL_START.
            continue

        last_idx = df.index[-1]
        last_date = last_idx.date() if hasattr(last_idx, "date") else last_idx
        if last_date < cutoff:
            # We DID get data, and it stops well before today. Genuine
            # delisting (or M&A / sufficient gap to treat as one).
            last_close = df["Close"].iloc[-1]
            last_price = float(last_close) if pd.notna(last_close) else None
            out.append((ticker, last_date.isoformat(), last_price, "data_gap"))
    return out


def main() -> None:
    _ensure_schema()
    today = date.today()
    cutoff = today - timedelta(days=DEAD_AFTER_DAYS)
    print(f"Detecting delistings: ticker last_bar < {cutoff} ({DEAD_AFTER_DAYS}d ago)",
          flush=True)

    tickers = _load_universe()
    print(f"  universe: {len(tickers)} tickers", flush=True)

    batches = [tickers[i:i+BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]
    print(f"  {len(batches)} batches of up to {BATCH_SIZE}", flush=True)

    all_delistings: list[tuple] = []
    for i, batch in enumerate(batches, 1):
        t0 = time.time()
        delistings = _process_batch(batch, cutoff)
        all_delistings.extend(delistings)
        print(f"  [{i:3d}/{len(batches)}] +{len(delistings):4d} delisted  "
              f"{time.time()-t0:5.1f}s  (total {len(all_delistings):,})",
              flush=True)
        if i < len(batches):
            time.sleep(1.0)

    conn = sqlite3.connect(DB_PATH)
    conn.executemany(
        "INSERT OR REPLACE INTO delistings (ticker, delist_date, last_price, reason) "
        "VALUES (?, ?, ?, ?)",
        all_delistings,
    )
    conn.commit()
    conn.close()
    print(f"\nDone. {len(all_delistings):,} delistings written.", flush=True)


if __name__ == "__main__":
    main()
