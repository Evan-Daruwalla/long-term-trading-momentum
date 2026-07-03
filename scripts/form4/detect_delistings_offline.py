"""Detect delistings using only the warmed close cache — no yfinance.

For each ticker that has data in price_cache(kind='close'), find the last
cached date. If that's more than DEAD_AFTER_DAYS before TODAY, mark the
ticker as delisted at that date. This catches every ticker that yfinance
served us OHLC for but stopped serving — the most reliable delisting
signal we have.

Tickers absent from the close cache (rate-limited during warm or yfinance
never knew them) are NOT marked here — they'd be false-positive-prone.
Re-run scripts/ingest_form25.py later for those.

Idempotent. Run any time after warm_close.py.
"""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta

from trading_bot.config import DB_PATH

# 180d cutoff: live tickers rate-limited during warm may have their last
# bar weeks-to-months stale. 6 months catches genuine delistings while
# rejecting recent rate-limit artifacts.
DEAD_AFTER_DAYS = 180
# Require substantial coverage. A ticker rate-limited during warm typically
# has 20-100 cached bars (one or two yfinance calls' worth). A genuinely
# tracked ticker with at least ~2 years of history has 500+ bars. This is
# the threshold that distinguishes UNH (54 bars, alive) from PETS (>500
# bars, actually delisted Aug 2025).
MIN_BARS = 500


def main() -> None:
    today = date.today()
    cutoff = today - timedelta(days=DEAD_AFTER_DAYS)
    print(f"Detecting delistings: last close < {cutoff} "
          f"({DEAD_AFTER_DAYS}d ago)", flush=True)

    conn = sqlite3.connect(DB_PATH)
    # ensure table exists (created by ingest_form25 on prior run)
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

    # Per ticker: max key_date AND total bar count. We need both to filter
    # out partial-coverage tickers that look fake-delisted.
    rows = conn.execute(
        """
        SELECT pc.ticker, MAX(pc.key_date) AS last_d, COUNT(*) AS n_bars
        FROM price_cache pc
        WHERE pc.kind = 'close' AND pc.price IS NOT NULL
        GROUP BY pc.ticker
        """
    ).fetchall()
    print(f"  {len(rows):,} tickers in close cache "
          f"(filtering: last < {cutoff} AND bars >= {MIN_BARS})", flush=True)

    new_delistings: list[tuple] = []
    skipped_partial = 0
    for ticker, last_d, n_bars in rows:
        if last_d is None:
            continue
        try:
            last_date = date.fromisoformat(last_d)
        except ValueError:
            continue
        if last_date >= cutoff:
            continue
        if n_bars < MIN_BARS:
            skipped_partial += 1
            continue
        last_price_row = conn.execute(
            "SELECT price FROM price_cache "
            "WHERE ticker=? AND kind='close' AND key_date=?",
            (ticker, last_d),
        ).fetchone()
        last_price = float(last_price_row[0]) if last_price_row and last_price_row[0] is not None else None
        new_delistings.append((ticker, last_d, last_price, "data_gap_offline"))
    print(f"  skipped {skipped_partial} stale-but-partial tickers (likely "
          f"rate-limit gaps, not delistings)", flush=True)

    if new_delistings:
        conn.executemany(
            "INSERT OR REPLACE INTO delistings "
            "(ticker, delist_date, last_price, reason) VALUES (?, ?, ?, ?)",
            new_delistings,
        )
        conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM delistings").fetchone()[0]
    conn.close()
    print(f"\n{len(new_delistings):,} new delistings detected. "
          f"Total in delistings table: {total:,}", flush=True)


if __name__ == "__main__":
    main()
