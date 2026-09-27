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

Cost: ~2 min for ~5,900 tickers at 200/batch with 1s between batches, plus up
to ~7 min of retry cooldowns when yfinance rate-limits the run (record DZ).
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import yfinance as yf

from trading_bot.config import VAR_DIR
from trading_bot.db import connect

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("daily_refresh")

BATCH_SIZE = 200
INTER_BATCH_SLEEP_SEC = 1.0
# Fraction of wholly-empty batches (with other batches succeeding) that turns a
# run into a nonzero exit. 0.10 catches a real rate-limit (2026-08-02: 6/30 = 20%)
# without letting normal partial publication abort the monthly rebalance.
EMPTY_BATCH_FAIL_FRACTION = 0.10
# Record DY/DZ (2026-09-23): the rate limit also comes PER TICKER inside a batch
# that still returns rows - from ~batch 15 of 30 every run, so 09-22 had 94% of
# A-J closes but 46% of K-Z and neither guard above fired. Recently-traded names
# that come back with NO rows are retried after these cooldowns, and the run
# fails if this fraction of them is still missing at the end.
RETRY_COOLDOWNS_SEC = (60, 120, 240)
MISSING_LIVE_FAIL_FRACTION = 0.05


def _load_known_tickers() -> list[str]:
    """All tickers with any cached close history — these are the names we
    have committed to tracking. Don't try to add new ones here."""
    # trading_bot.db.connect (not raw sqlite3.connect): it sets busy_timeout=30s,
    # so colliding with another writer WAITS instead of dying on "database is
    # locked" (audit 2026-07-17, record CG). Every other writer goes through it.
    with connect() as conn:
        rows = conn.execute(
            "SELECT DISTINCT ticker FROM price_cache WHERE kind='close' "
            "ORDER BY ticker"
        ).fetchall()
    return [r[0] for r in rows]


def _load_live_tickers(start: date) -> set[str]:
    """Tickers with a cached close inside the refresh window - names that traded
    recently and so SHOULD return rows. A delisted name ages out of the window,
    so it is neither retried nor counted as missing."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT DISTINCT ticker FROM price_cache WHERE kind='close' "
            "AND key_date >= ?", (start.isoformat(),)).fetchall()
    return {r[0] for r in rows}


def _bulk_upsert(rows: list[tuple]) -> int:
    if not rows:
        return 0
    with connect() as conn:   # busy_timeout=30s writer; commits on exit
        conn.executemany(
            "INSERT OR REPLACE INTO price_cache (ticker, kind, key_date, price) "
            "VALUES (?, ?, ?, ?)",
            rows,
        )
    return len(rows)


def _process_batch(tickers: list[str], start: date, end: date,
                   failed_sizes: list[int] | None = None,
                   empty_sizes: list[int] | None = None,
                   got: set[str] | None = None) -> int:
    """Download closes for `tickers` between [start, end], upsert. Returns rowcount.

    A batch that loses ALL 3 attempts drops ~200 tickers silently; when
    `failed_sizes` is passed, its size is appended there so the caller can exit
    nonzero instead of reporting success. `empty_sizes` does the same for batches
    that come back EMPTY rather than raising - the shape a yfinance rate-limit
    takes. Both are optional (not required args) so
    scripts/data_audit/backfill_history_gaps.py's 3-arg call still works.
    `got`, when passed, collects every ticker that returned at least one close.
    """
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
    if raw is None:
        # All retries exhausted with an EXCEPTION = a LOST batch. Record it so
        # main() exits nonzero.
        if failed_sizes is not None:
            failed_sizes.append(len(tickers))
        return 0
    if raw.empty:
        # An empty frame is ambiguous, and the ambiguity matters: yfinance swallows
        # YFRateLimitError internally and hands back an EMPTY FRAME rather than
        # raising, so a rate-limited batch is indistinguishable here from a genuine
        # "no bars in range" (a weekend, or a batch of all-delisted names).
        # 2026-08-02: that gap silently dropped two full trading days (07-30, 07-31)
        # while this function still returned exit 0. main() disambiguates by looking
        # at the whole run: wholly-empty batches only mean failure when OTHER batches
        # in the same run did return rows.
        if empty_sizes is not None:
            empty_sizes.append(len(tickers))
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
        if got is not None:
            got.add(ticker)
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
    live = _load_live_tickers(start)
    log.info("Refreshing %d tickers, range %s to %s",
             len(tickers), start, today)

    batches = [tickers[i:i + BATCH_SIZE]
               for i in range(0, len(tickers), BATCH_SIZE)]
    log.info("%d batches of up to %d tickers", len(batches), BATCH_SIZE)

    total = 0
    failed_sizes: list[int] = []
    empty_sizes: list[int] = []
    got: set[str] = set()
    started = time.time()
    for i, batch in enumerate(batches, 1):
        t0 = time.time()
        n = _process_batch(batch, start, end, failed_sizes, empty_sizes, got)
        total += n
        log.info("  [%3d/%3d] +%6d rows  %5.1fs  (total %d)",
                 i, len(batches), n, time.time() - t0, total)
        if i < len(batches):
            time.sleep(INTER_BATCH_SLEEP_SEC)

    missing = sorted(live - got)
    for rnd, cooldown in enumerate(RETRY_COOLDOWNS_SEC, 1):
        if not missing:
            break
        log.warning("Retry %d: %d recently-traded ticker(s) returned no rows "
                    "(rate-limit shape) - waiting %ds, then re-downloading.",
                    rnd, len(missing), cooldown)
        time.sleep(cooldown)
        for i in range(0, len(missing), BATCH_SIZE):
            total += _process_batch(missing[i:i + BATCH_SIZE], start, end, got=got)
            time.sleep(INTER_BATCH_SLEEP_SEC)
        still = sorted(live - got)
        log.info("Retry %d recovered %d ticker(s); %d still missing.",
                 rnd, len(missing) - len(still), len(still))
        missing = still

    elapsed = time.time() - started
    log.info("Done. %d close+volume rows upserted in %.1f min", total, elapsed / 60)
    # Stamp completion time so the dashboard can show "data refreshed N ago".
    try:
        (VAR_DIR / "last_price_refresh.txt").write_text(
            datetime.now(timezone.utc).isoformat())
    except Exception:
        pass
    # A batch that lost every retry used to be invisible: warnings only, exit 0,
    # so ~200 tickers could vanish while daily.bat/rebalance.bat's
    # `if errorlevel 1` never fired and downstream ranks/marks silently used
    # stale prices. Surface it as a nonzero exit.
    if failed_sizes:
        log.error("REFRESH INCOMPLETE: %d batch(es) exhausted all 3 download "
                  "attempts, leaving %d ticker(s) unrefreshed (batch sizes: %s). "
                  "Prices for those names are STALE.",
                  len(failed_sizes), sum(failed_sizes),
                  ", ".join(str(s) for s in failed_sizes))
        return 1

    # Wholly-EMPTY batches (the yfinance rate-limit shape - it swallows
    # YFRateLimitError and returns an empty frame instead of raising). Empty is
    # only evidence of failure when OTHER batches in the same run DID return
    # rows: on a weekend or holiday every batch is legitimately empty, and that
    # must stay exit 0 or the morning task would fail every Saturday.
    #
    # The threshold is deliberate. rebalance.bat HARD-ABORTS the monthly rebalance
    # on errorlevel 1, and partial same-day publication (~4,400 of ~5,200 closes at
    # 17:33) is NORMAL on a rebalance day - but that shows up as fewer rows per
    # ticker, never as wholly-empty batches. Requiring a meaningful FRACTION of
    # batches to come back empty keeps normal partial publication from aborting the
    # rebalance, while still catching a real rate-limit (2026-08-02: 6 of 30 batches
    # empty, two full trading days lost, exit still 0).
    # `total > 0` (audit 2026-08-04, finding 11 / E7): a TOTAL outage - every
    # batch empty, so total == 0 - skipped this guard entirely and returned 0.
    # The partial case (2026-08-02, record CI) was caught; the complete one was
    # classified as success. If nothing at all came back, that is never normal.
    if total == 0:
        log.error("REFRESH INCOMPLETE: NOT ONE ticker returned data across %d "
                  "batch(es). That is a total feed/rate-limit outage, not a "
                  "market holiday (a holiday still returns rows for prior days).",
                  len(batches))
        return 1
    if empty_sizes and total > 0:
        frac = len(empty_sizes) / len(batches)
        msg = ("%d of %d batch(es) returned NO data (%d ticker(s)) while other "
               "batches did - this is the yfinance rate-limit signature, not a "
               "market holiday.")
        args = (len(empty_sizes), len(batches), sum(empty_sizes))
        if frac >= EMPTY_BATCH_FAIL_FRACTION:
            log.error("REFRESH INCOMPLETE: " + msg + " Prices for those names are "
                      "STALE; re-run once the limit clears.", *args)
            return 1
        log.warning(msg + " Below the %.0f%% failure threshold, so exit stays 0.",
                    *args, EMPTY_BATCH_FAIL_FRACTION * 100)
    if missing:
        frac = len(missing) / len(live)
        msg = ("%d of %d recently-traded ticker(s) (%.1f%%) returned no rows even "
               "after %d retry round(s), first few: %s.")
        args = (len(missing), len(live), frac * 100, len(RETRY_COOLDOWNS_SEC),
                ", ".join(missing[:10]))
        if frac >= MISSING_LIVE_FAIL_FRACTION:
            log.error("REFRESH INCOMPLETE: " + msg + " Prices for those names are "
                      "STALE; re-run once the limit clears.", *args)
            return 1
        log.warning(msg + " Below the %.0f%% failure threshold, so exit stays 0.",
                    *args, MISSING_LIVE_FAIL_FRACTION * 100)
    return 0


if __name__ == "__main__":
    sys.exit(main())
