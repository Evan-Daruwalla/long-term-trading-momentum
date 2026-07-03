"""Daily incremental price refresh for the paper-trade universe.

Downloads the last ~N trading days of closes AND volumes for every ticker
already in price_cache, INSERT OR REPLACE so re-running is safe. Volume comes
free in the same yfinance frame, so persisting it here keeps the volume cache
fresh daily (the ADV/liquidity diagnostic depends on it) and removes the need
for a separate volume-warm pass in rebalance.bat.

Why N days (not just yesterday): tolerant of missed days (weekends, holidays,
script-not-run days) without needing complex gap detection. yfinance bulk
download cost is similar for 1 day vs 30 days at batch size 200.

Usage:
  python -m scripts.momentum.daily_price_refresh           # last 30 days
  python -m scripts.momentum.daily_price_refresh --days 7  # tight refresh

Cost: ~5-8 min for the full ~4,200-ticker universe at 200/batch with 1s
between batches (yfinance rate-limit friendly).
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
import time
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import yfinance as yf

from trading_bot.config import DB_PATH, VAR_DIR

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("daily_refresh")

BATCH_SIZE = 200
INTER_BATCH_SLEEP_SEC = 1.0


def _load_known_tickers() -> list[str]:
    """All tickers with any cached close history — these are the names we
    have committed to tracking. Don't try to add new ones here."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT DISTINCT ticker FROM price_cache WHERE kind='close' "
        "ORDER BY ticker"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


def _bulk_upsert(rows: list[tuple]) -> int:
    if not rows:
        return 0
    conn = sqlite3.connect(DB_PATH)
    conn.executemany(
        "INSERT OR REPLACE INTO price_cache (ticker, kind, key_date, price) "
        "VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()
    return len(rows)


def _process_batch(tickers: list[str], start: date, end: date) -> int:
    """Download closes for `tickers` between [start, end], upsert. Returns rowcount."""
    raw = None
    for attempt in range(3):
        try:
            # auto_adjust=False is the price_cache CONVENTION: every other
            # writer (scripts/shared/warm_*, market_data fetch-on-miss, the
            # ETF warm scripts) stores split-adjusted but dividend-UNadjusted
            # closes. This was True until 2026-06-09, which silently stamped
            # dividend-adjusted values over the trailing 30d of every ticker
            # daily (≤~1% low on div payers near ex-div — audit 2026-06-09).
            raw = yf.download(
                tickers, start=start.isoformat(), end=end.isoformat(),
                auto_adjust=False, progress=False, group_by="ticker",
                actions=False,
            )
            break
        except Exception as e:
            log.warning("download error attempt %d: %s", attempt + 1, e)
            if attempt < 2:
                time.sleep(15)
    if raw is None or raw.empty:
        return 0
    if len(tickers) == 1:
        raw = pd.concat({tickers[0]: raw}, axis=1)

    out: list[tuple] = []
    for ticker in tickers:
        try:
            df = raw[ticker].dropna(subset=["Close"]).sort_index()
        except KeyError:
            continue
        if df.empty:
            continue
        for ts, close in df["Close"].items():
            d = ts.date() if hasattr(ts, "date") else ts
            out.append((ticker, "close", d.isoformat(), float(close)))
        # Volume is already in the same frame — persist it (split-unadjusted
        # raw shares, same convention as warm_volumes) so the volume cache
        # stays fresh daily. Free: no extra download.
        if "Volume" in df.columns:
            for ts, vol in df["Volume"].dropna().items():
                if vol > 0:
                    d = ts.date() if hasattr(ts, "date") else ts
                    out.append((ticker, "volume", d.isoformat(), float(vol)))
    return _bulk_upsert(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30,
                    help="Days of history to refresh (default: 30)")
    args = ap.parse_args()

    today = date.today()
    start = today - timedelta(days=args.days)
    end = today + timedelta(days=1)    # yfinance end is exclusive

    tickers = _load_known_tickers()
    log.info("Refreshing %d tickers, range %s to %s",
             len(tickers), start, today)

    batches = [tickers[i:i + BATCH_SIZE]
               for i in range(0, len(tickers), BATCH_SIZE)]
    log.info("%d batches of up to %d tickers", len(batches), BATCH_SIZE)

    total = 0
    started = time.time()
    for i, batch in enumerate(batches, 1):
        t0 = time.time()
        n = _process_batch(batch, start, end)
        total += n
        log.info("  [%3d/%3d] +%6d rows  %5.1fs  (total %d)",
                 i, len(batches), n, time.time() - t0, total)
        if i < len(batches):
            time.sleep(INTER_BATCH_SLEEP_SEC)

    elapsed = time.time() - started
    log.info("Done. %d close+volume rows upserted in %.1f min", total, elapsed / 60)
    # Stamp completion time so the dashboard can show "data refreshed N ago".
    try:
        (VAR_DIR / "last_price_refresh.txt").write_text(
            datetime.now(timezone.utc).isoformat())
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
