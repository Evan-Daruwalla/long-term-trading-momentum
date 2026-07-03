"""Backfill the 2019->present daily-close hole for gappy-history tickers.

Root cause (discovered 2026-06-12, record Appendix AA): ~800 tickers were warmed
with only OLD history (2010-2018) + a recent 2026 burst, leaving a multi-year
hole. Their 12-1 momentum is computed against a pre-gap (2018) bar -> phantom
hundreds-to-thousands of % -> they phantom-rank into the sleeves (CIEN/FN/AAPL
all affected). yfinance HAS the missing data (verified), so we backfill it.

Strategy: for every ticker that has a 2026 close but is missing a recent year,
re-fetch 2019-01-01 -> today with auto_adjust=False (the price_cache convention,
via daily_price_refresh._process_batch) and INSERT OR REPLACE. This FILLS the
hole and refreshes recent bars; it does NOT touch the audit-cleaned 2010-2018
data (we never fetch before 2019). Run the spike detector afterward to clean any
newly-introduced artifacts in the backfilled span.

Read targets, write closes. Usage:
  python -m scripts.data_audit.backfill_history_gaps [--dry-run] [--batch N]
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import time
from datetime import date, timedelta

from trading_bot.config import DB_PATH
from scripts.momentum import daily_price_refresh as dpr

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("backfill_gaps")

BACKFILL_START = date(2019, 1, 1)
MIN_YEAR_ROWS = 200   # a continuous year has ~250 sessions; <200 in 2024 or 2025 = gappy


def target_tickers() -> list[str]:
    """Tickers with a 2026 close but an incomplete 2024 OR 2025 (the recent
    hole that corrupts a 2026-as_of momentum lookback)."""
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT ticker, "
            " SUM(CASE WHEN key_date>='2026-01-01' THEN 1 ELSE 0 END) AS y26, "
            " SUM(CASE WHEN key_date>='2024-01-01' AND key_date<'2025-01-01' THEN 1 ELSE 0 END) AS y24, "
            " SUM(CASE WHEN key_date>='2025-01-01' AND key_date<'2026-01-01' THEN 1 ELSE 0 END) AS y25 "
            "FROM price_cache WHERE kind='close' AND price>0 GROUP BY ticker"
        ).fetchall()
    finally:
        conn.close()
    out = [tk for tk, y26, y24, y25 in rows
           if y26 > 0 and (y24 < MIN_YEAR_ROWS or y25 < MIN_YEAR_ROWS)]
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="list targets, don't fetch")
    ap.add_argument("--batch", type=int, default=100)
    args = ap.parse_args()

    end = date.today() + timedelta(days=1)   # yfinance end exclusive
    targets = target_tickers()
    log.info("Gappy targets: %d tickers. Backfill range %s -> %s.",
             len(targets), BACKFILL_START, date.today())
    if args.dry_run:
        log.info("DRY-RUN sample (first 30): %s", targets[:30])
        return 0
    if not targets:
        log.info("Nothing to backfill.")
        return 0

    batches = [targets[i:i + args.batch] for i in range(0, len(targets), args.batch)]
    log.info("%d batches of up to %d (wide 7yr pull; ~min/batch).", len(batches), args.batch)
    total = 0
    started = time.time()
    for i, batch in enumerate(batches, 1):
        t0 = time.time()
        n = dpr._process_batch(batch, BACKFILL_START, end)
        total += n
        log.info("  [%2d/%2d] +%7d rows  %5.1fs  (total %d)",
                 i, len(batches), n, time.time() - t0, total)
        if i < len(batches):
            time.sleep(dpr.INTER_BATCH_SLEEP_SEC)
    log.info("Done. %d close rows upserted in %.1f min.", total, (time.time() - started) / 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
