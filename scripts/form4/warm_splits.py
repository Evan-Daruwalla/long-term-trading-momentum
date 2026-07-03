"""Pre-warm split + dividend history for every signal ticker via bulk download.

`market_data.split_ratio()` and `market_data.dividends_per_share()` each
get called once per close_position. Both pull from the same
yfinance bulk download (actions=True), so we warm them together to avoid
re-downloading.

Stored as JSON in price_cache:
  - kind='splits_json',    key_date='all', price=JSON list of [iso_date, ratio]
  - kind='dividends_json', key_date='all', price=JSON list of [iso_date, amount]

Both lookups become O(1) at backtest time. Idempotent.
"""
from __future__ import annotations

import json
import re
import sqlite3
import time

import pandas as pd
import yfinance as yf

from trading_bot.config import DB_PATH

BATCH_SIZE = 200
DL_START   = "2020-01-01"   # cover all relevant splits (most happen pre-hold)
DL_END     = "2026-05-08"
TICKER_RE  = re.compile(r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$")
KIND       = "splits_json"


def _valid(t: str) -> bool:
    return bool(TICKER_RE.match(t))


def _load_universe() -> list[str]:
    """Resume support: skip tickers that have BOTH splits_json AND
    dividends_json already cached. A ticker missing either kind needs
    re-fetching."""
    conn = sqlite3.connect(DB_PATH)
    all_t = {r[0] for r in conn.execute(
        "SELECT DISTINCT ticker FROM signals WHERE transaction_code='P'"
    ).fetchall()}
    have_splits = {r[0] for r in conn.execute(
        "SELECT ticker FROM price_cache WHERE kind='splits_json' AND key_date='all'"
    ).fetchall()}
    have_divs = {r[0] for r in conn.execute(
        "SELECT ticker FROM price_cache WHERE kind='dividends_json' AND key_date='all'"
    ).fetchall()}
    conn.close()
    fully_warmed = have_splits & have_divs
    todo = sorted({t for t in all_t if _valid(t)} - fully_warmed)
    print(f"  resume: {len(fully_warmed)} already warmed (both kinds), "
          f"{len(todo)} to fetch", flush=True)
    return todo


def _bulk_insert(rows: list[tuple]) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.executemany(
        "INSERT OR REPLACE INTO price_cache (ticker, kind, key_date, price) "
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
                actions=True,  # include Splits + Dividends columns
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
            df = raw[ticker]
        except KeyError:
            continue
        if df.empty:
            continue

        # SPLITS — only write if column actually present. If missing, this
        # batch was likely rate-limited (actions=True silently dropped); a
        # later re-run will pick it up.
        if "Stock Splits" in df.columns:
            split_events = []
            for ts, r in df["Stock Splits"].dropna().items():
                r = float(r)
                if r and r > 0 and r != 1.0:
                    d = ts.date() if hasattr(ts, "date") else ts
                    split_events.append([d.isoformat(), r])
            out.append((ticker, "splits_json", "all", json.dumps(split_events)))

        # DIVIDENDS — same conservative policy as splits. An empty list
        # gets written for legitimately-no-dividend tickers (we have OHLC
        # AND a Dividends column with no entries) but never for missing-
        # column failure modes.
        if "Dividends" in df.columns:
            div_events = []
            for ts, amt in df["Dividends"].dropna().items():
                amt = float(amt)
                if amt and amt > 0:
                    d = ts.date() if hasattr(ts, "date") else ts
                    div_events.append([d.isoformat(), amt])
            out.append((ticker, "dividends_json", "all", json.dumps(div_events)))
    if out:
        _bulk_insert(out)
    return len(out) // 2  # ticker-rows written


def main() -> None:
    todo = _load_universe()
    if not todo:
        print("Nothing to do — all tickers already warmed.", flush=True)
        return
    batches = [todo[i:i+BATCH_SIZE] for i in range(0, len(todo), BATCH_SIZE)]
    print(f"  {len(batches)} batches of up to {BATCH_SIZE}", flush=True)

    total = 0
    for i, batch in enumerate(batches, 1):
        t0 = time.time()
        n = _process_batch(batch)
        total += n
        print(f"  [{i:3d}/{len(batches)}] +{n:5d} tickers  {time.time()-t0:5.1f}s  "
              f"(total {total:,})", flush=True)
        if i < len(batches):
            time.sleep(1.0)
    print(f"\nDone. {total:,} ticker split histories warmed.", flush=True)


if __name__ == "__main__":
    main()
