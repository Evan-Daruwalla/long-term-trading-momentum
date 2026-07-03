"""Fetch earnings dates + EPS surprises from yfinance.

For each ticker in price_cache with recent activity, fetches past ~6 years
of earnings via Ticker.earnings_dates. Each entry: date + EPS estimate +
reported EPS + surprise%. Cached as:

  {ticker: [{"date": "2024-01-30", "surprise_pct": 3.5, "eps_actual": 2.01,
            "eps_est": 1.94}, ...]}

Requires lxml package (yfinance uses it to parse HTML).
Resumable: re-running only fetches tickers not in cache.

Rate-limited at 0.5s per ticker => ~30-50 min for ~3000 tickers.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import yfinance as yf

from trading_bot.db import connect

CACHE_PATH = Path("var/data_audit/earnings_dates_cache.json")
SLEEP_SEC = 0.5
SAVE_EVERY = 50


def _load_cache() -> dict[str, list[str]]:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text())
    except Exception:
        return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True))


def _get_universe() -> list[str]:
    """All tickers with recent close >= $5 (the actual tradeable universe)."""
    with connect() as conn:
        rows = conn.execute('''
            SELECT ticker FROM price_cache
            WHERE kind='close' AND key_date >= '2026-05-01' AND price >= 5
            GROUP BY ticker
            ORDER BY ticker
        ''').fetchall()
    return [r["ticker"] for r in rows]


def fetch_one(ticker: str) -> list[dict] | None:
    """Returns list of {date, surprise_pct, eps_actual, eps_est} dicts.
    Drops rows with no reported EPS (future scheduled earnings).
    None on failure; empty list = no data."""
    try:
        import math
        t = yf.Ticker(ticker)
        df = t.earnings_dates
        if df is None or len(df) == 0:
            return []
        out = []
        for ts, row in df.iterrows():
            actual = row.get("Reported EPS")
            est = row.get("EPS Estimate")
            surprise = row.get("Surprise(%)")
            # Only keep PAST earnings (have actual reported EPS)
            if actual is None or (isinstance(actual, float) and math.isnan(actual)):
                continue
            entry = {"date": ts.date().isoformat()}
            entry["eps_actual"] = float(actual) if actual is not None and not (isinstance(actual, float) and math.isnan(actual)) else None
            entry["eps_est"] = float(est) if est is not None and not (isinstance(est, float) and math.isnan(est)) else None
            entry["surprise_pct"] = float(surprise) if surprise is not None and not (isinstance(surprise, float) and math.isnan(surprise)) else None
            out.append(entry)
        out.sort(key=lambda x: x["date"])
        return out
    except Exception as e:
        return None


def main() -> int:
    cache = _load_cache()
    universe = _get_universe()
    print(f"Universe size: {len(universe)} tickers", flush=True)
    print(f"Already cached: {len(cache)}", flush=True)
    remaining = [t for t in universe if t not in cache]
    print(f"To fetch: {len(remaining)}", flush=True)
    if not remaining:
        print("Nothing to do.")
        return 0

    t0 = time.time()
    n_ok = n_empty = n_fail = 0
    for i, ticker in enumerate(remaining):
        result = fetch_one(ticker)
        if result is None:
            n_fail += 1
            cache[ticker] = []  # mark as attempted but failed so we don't retry
        elif not result:
            n_empty += 1
            cache[ticker] = []
        else:
            n_ok += 1
            cache[ticker] = result

        if (i + 1) % SAVE_EVERY == 0:
            _save_cache(cache)
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            eta_min = (len(remaining) - i - 1) / rate / 60
            print(f"  [{i+1}/{len(remaining)}] ok={n_ok} empty={n_empty} fail={n_fail}  "
                  f"rate={rate:.2f}/s  ETA={eta_min:.1f} min", flush=True)

        time.sleep(SLEEP_SEC)

    _save_cache(cache)
    print(f"\nDONE. {len(remaining)} attempted: ok={n_ok}, empty={n_empty}, fail={n_fail}")
    print(f"Elapsed: {(time.time()-t0)/60:.1f} min")
    print(f"Cache written to {CACHE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
