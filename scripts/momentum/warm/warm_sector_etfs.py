"""Warm price_cache with the 11 SPDR sector ETFs for sector_top4_paper sleeve.

Run once initially. After that, daily_price_refresh.py auto-includes any
ticker already in price_cache, so these will get refreshed daily alongside
the stock universe.

Inserts close + (optionally) volume into price_cache table with kind='close'.
Idempotent: re-running upserts.
"""
from __future__ import annotations

import sys
import time
from datetime import date

import yfinance as yf

from trading_bot.db import connect

SECTOR_ETFS = ["XLE", "XLF", "XLI", "XLB", "XLK", "XLP", "XLU", "XLV", "XLY", "XLC", "XLRE"]
START = "2014-06-01"
END   = "2026-12-31"


def main() -> int:
    t0 = time.time()
    total_rows = 0
    with connect() as conn:
        for tk in SECTOR_ETFS:
            df = yf.Ticker(tk).history(start=START, end=END, auto_adjust=False)
            n = 0
            for ts, row in df.iterrows():
                iso = ts.date().isoformat()
                close = float(row["Close"]) if row["Close"] == row["Close"] else None
                if close is None or close <= 0: continue
                conn.execute(
                    "INSERT OR REPLACE INTO price_cache (ticker, kind, key_date, price) "
                    "VALUES (?, 'close', ?, ?)",
                    (tk, iso, close))
                n += 1
            print(f"  {tk}: {n} rows inserted", flush=True)
            total_rows += n
        conn.commit()
    print(f"\nDone. {total_rows} rows across {len(SECTOR_ETFS)} ETFs in {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
