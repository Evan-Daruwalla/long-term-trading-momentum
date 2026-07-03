"""Keep the volume cache fresh for the names the sleeves actually HOLD.

Why this exists: daily_price_refresh writes closes every day but never persists
volume, so the volume cache drifts stale (it freezes at the last warm). The only
consumer of volume is the ADV/liquidity diagnostic (universe.median_dollar_volume
over held names) -- MIN_DOLLAR_VOL=0, so the live universe build does NOT read
volume. We therefore warm volume only for currently-held names over the recent
ADV-lookback window, not the whole 5,800-name universe (that would be ~21 min and
rate-limit-prone for data nothing reads). If MIN_DOLLAR_VOL is ever turned on,
switch to the universe-wide scripts/momentum/warm/warm_volumes.py instead.

Manual BACKSTOP only (no longer wired into rebalance.bat): daily_price_refresh
now persists volume alongside closes, so the volume cache stays fresh daily for
the whole universe. Keep this for ad-hoc top-ups if a refresh is skipped.
Idempotent (INSERT OR IGNORE), best-effort: never raises.

Standalone usage: python -m scripts.momentum.warm.warm_held_volumes
"""
from __future__ import annotations

import sqlite3
import sys
import time
from datetime import date, timedelta

import pandas as pd

from trading_bot.config import DB_PATH
from trading_bot.factors import universe
from scripts.momentum.warm.warm_volumes import (
    _download, _emit_volume_rows, _bulk_insert,
)

# Calendar days back to cover the 60-trading-day ADV lookback with headroom
# (60 trading days ~= 84 calendar days; 130 leaves slack for holidays/gaps).
LOOKBACK_CAL_DAYS = 130
BATCH_SIZE = 50


def _held_tickers() -> list[str]:
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT DISTINCT ticker FROM paper_positions WHERE status='open'"
        ).fetchall()
    finally:
        conn.close()
    return sorted({t for (t,) in rows})


def main() -> int:
    today = date.today()
    since = (today - timedelta(days=LOOKBACK_CAL_DAYS)).isoformat()
    until = (today + timedelta(days=1)).isoformat()  # yf end is exclusive

    held = _held_tickers()
    if not held:
        print("warm_held_volumes: no open positions; nothing to warm.", flush=True)
        return 0
    print(f"warm_held_volumes: {len(held)} held names [{since}..{today}]", flush=True)

    written = 0
    for i in range(0, len(held), BATCH_SIZE):
        batch = held[i:i + BATCH_SIZE]
        try:
            df = _download(batch, since, until)
            rows: list[tuple] = []
            if df is not None and not df.empty:
                if len(batch) == 1:
                    df = pd.concat({batch[0]: df}, axis=1)
                for tk in batch:
                    try:
                        sub = df[tk].dropna(how="all").sort_index()
                    except KeyError:
                        continue
                    if not sub.empty:
                        rows.extend(_emit_volume_rows(tk, sub))
            if rows:
                _bulk_insert(rows)
                written += len(rows)
            print(f"  batch {i // BATCH_SIZE + 1}: +{len(rows)} rows "
                  f"(total {written})", flush=True)
        except Exception as e:  # best-effort: never abort the rebalance batch
            print(f"  batch {i // BATCH_SIZE + 1}: WARN {e}", flush=True)
        time.sleep(3)

    # Sanity: how many held names now have a full ADV window? (informational)
    universe._build_index()
    full = sum(1 for tk in held
               if universe.median_dollar_volume(tk, today) is not None)
    print(f"warm_held_volumes: done, {written} rows; "
          f"{full}/{len(held)} held names have a full {universe.VOL_LOOKBACK}d "
          f"ADV window.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
