"""Detect tickers with continuously-bogus historical data.

For each ticker:
  - Get its 'stable_price' = median of last N closes (default 60)
  - Any historical close > MULT x stable_price is flagged as bogus
    (yfinance reverse-split-adjustment failures cause pre-split prices
    to remain at huge inflated values)

This catches what find_price_spikes.py missed: tickers with whole-period
bogus data (not just isolated Friday spikes) like ARSC ($8000 closes
from 2010-2016 when real price was $0.10).

Companion to find_price_spikes.py. Run BOTH (this catches the bulk, the
spike detector catches isolated artifacts).

Dry-run by default; --apply to null bad rows.
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import defaultdict
from pathlib import Path

from trading_bot.db import connect

OUT_DIR = Path("var/data_audit")
DEFAULT_MULT = 100.0    # 100x the stable price = clear data corruption
STABLE_LOOKBACK = 60    # use median of last 60 closes as the "real" reference
MIN_STABLE_PRICE = 0.0001  # need some signal to compute ratio


def find_stale(mult: float) -> dict:
    t0 = time.time()
    with connect() as conn:
        all_rows = conn.execute(
            "SELECT ticker, key_date, price FROM price_cache "
            "WHERE kind='close' AND price > 0 ORDER BY ticker, key_date"
        ).fetchall()
    print(f"Scanned {len(all_rows):,} close-price rows in {time.time()-t0:.1f}s")

    by_ticker: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for r in all_rows:
        by_ticker[r["ticker"]].append((r["key_date"], r["price"]))

    flagged: dict[str, dict] = {}
    for tk, series in by_ticker.items():
        if len(series) < STABLE_LOOKBACK:
            continue
        recent_prices = [p for _, p in series[-STABLE_LOOKBACK:]]
        stable = statistics.median(recent_prices)
        if stable < MIN_STABLE_PRICE:
            continue
        bad = [(d, px) for d, px in series if px > stable * mult]
        if bad:
            flagged[tk] = {
                "stable_price": stable,
                "bad_rows": [{"date": d, "price": px, "ratio": px/stable} for d, px in bad],
            }
    return flagged


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mult", type=float, default=DEFAULT_MULT,
                        help=f"Bogus-if-ratio-above (default {DEFAULT_MULT}x stable)")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Detecting stale/bogus history: close >= {args.mult}x median of last {STABLE_LOOKBACK}")
    flagged = find_stale(args.mult)

    total_bad = sum(len(v["bad_rows"]) for v in flagged.values())
    print(f"\nFlagged {total_bad:,} bad rows across {len(flagged):,} tickers")

    # Top 20 by bad row count
    top = sorted(flagged.items(), key=lambda kv: -len(kv[1]["bad_rows"]))[:20]
    print(f"\nTop 20 by row count:")
    print(f"  {'ticker':<10} {'bad_rows':>9} {'stable':>10} {'max_ratio':>12}")
    for tk, info in top:
        max_ratio = max(b["ratio"] for b in info["bad_rows"])
        print(f"  {tk:<10} {len(info['bad_rows']):>9} {info['stable_price']:>10,.4f} {max_ratio:>10,.0f}x")

    report = {
        "params": {"mult": args.mult, "stable_lookback": STABLE_LOOKBACK},
        "total_bad_rows": total_bad,
        "tickers_affected": len(flagged),
        "flagged": flagged,
    }
    (OUT_DIR / "stale_history.json").write_text(json.dumps(report, indent=2))
    print(f"\nReport -> {OUT_DIR / 'stale_history.json'}")

    if args.apply:
        print(f"\nAPPLY: nulling {total_bad:,} rows...")
        with connect() as conn:
            for tk, info in flagged.items():
                for b in info["bad_rows"]:
                    conn.execute(
                        "UPDATE price_cache SET price=NULL "
                        "WHERE ticker=? AND kind='close' AND key_date=?",
                        (tk, b["date"]))
            conn.commit()
        print("Done.")
    else:
        print("\n(dry-run; --apply to actually null)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
