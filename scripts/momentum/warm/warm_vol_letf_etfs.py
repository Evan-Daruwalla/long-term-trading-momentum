"""Warm price_cache with volatility + leveraged-ETF tickers for research
candidates #2 (VIX-gated short-vol) and #4 (Gayed leveraged-ETF rotation).

  ^VIX, ^VIX3M : VIX spot + 3-month VIX (term-structure gate for #2)
  SVXY, VIXY   : inverse / long short-term VIX-futures ETPs (#2 tradeable)
  SSO, UPRO    : 2x / 3x S&P 500 (#4)
  QLD, TQQQ    : 2x / 3x Nasdaq-100 (#4)
  QQQ          : Nasdaq-100 1x (200-DMA signal for the Nasdaq LETFs in #4)

CAVEAT (documented for #2): SVXY was -1x until Feb 2018 "Volmageddon", then
ProShares re-levered it to -0.5x. yfinance prices reflect whatever leverage
applied at the time, so a 2015-2026 SVXY backtest mixes two regimes. Pre-2018
magnitudes are ~2x post-2018. Interpret in-sample short-vol results with that
in mind.

Idempotent upsert. After this, daily_price_refresh auto-includes them.
"""
from __future__ import annotations

import sys
import time

import yfinance as yf

from trading_bot.db import connect

TICKERS = ["^VIX", "^VIX3M", "SVXY", "VIXY", "SSO", "UPRO", "QLD", "TQQQ", "QQQ"]
START = "2014-06-01"
END   = "2026-12-31"


def main() -> int:
    t0 = time.time()
    total = 0
    with connect() as conn:
        for tk in TICKERS:
            try:
                df = yf.Ticker(tk).history(start=START, end=END, auto_adjust=False)
            except Exception as e:
                print(f"  {tk}: FETCH FAILED {e}", flush=True)
                continue
            n = 0
            for ts, row in df.iterrows():
                iso = ts.date().isoformat()
                close = float(row["Close"]) if row["Close"] == row["Close"] else None
                if close is None or close <= 0:
                    continue
                conn.execute(
                    "INSERT OR REPLACE INTO price_cache (ticker, kind, key_date, price) "
                    "VALUES (?, 'close', ?, ?)",
                    (tk, iso, close))
                n += 1
            print(f"  {tk}: {n} rows", flush=True)
            total += n
        conn.commit()
    print(f"\nDone. {total} rows across {len(TICKERS)} tickers in {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
