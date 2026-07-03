"""Detect and report price spikes in price_cache.

A "spike" = a close price that is >= MULT x the median of its 5 nearest
neighbors (excluding itself). Tested against the known yfinance Friday-2017
anomaly which inflated some tickers' prices 5,000-10,000x on isolated days.

Dry-run by default: writes a report to var/data_audit/price_spikes.json.
Use --apply to actually null out the bad rows (sets price=NULL, so MTM
falls back to entry_price per backtest._mark_to_market).
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
DEFAULT_MULT = 10.0   # 10x is conservative; real intraday moves rarely exceed 5x
NEIGHBOR_DAYS = 5     # 5 neighbors on each side


def find_spikes(mult: float) -> dict:
    """Scan price_cache for spikes. Returns {ticker: [(date, price, median)]}."""
    t0 = time.time()
    with connect() as conn:
        all_rows = conn.execute(
            "SELECT ticker, key_date, price FROM price_cache "
            "WHERE kind='close' AND price > 0 ORDER BY ticker, key_date"
        ).fetchall()

    print(f"Scanned {len(all_rows):,} close-price rows in {time.time()-t0:.1f}s")

    # Group by ticker, then scan each ticker's timeline
    by_ticker: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for r in all_rows:
        by_ticker[r["ticker"]].append((r["key_date"], r["price"]))

    spikes: dict[str, list[tuple[str, float, float]]] = {}
    for tk, series in by_ticker.items():
        # series is sorted by date
        ticker_spikes = []
        for i, (d, px) in enumerate(series):
            lo, hi = max(0, i - NEIGHBOR_DAYS), min(len(series), i + NEIGHBOR_DAYS + 1)
            nbrs = [series[j][1] for j in range(lo, hi) if j != i]
            if len(nbrs) < 3:
                continue
            med = statistics.median(nbrs)
            if med <= 0:
                continue
            ratio = px / med
            if ratio >= mult:
                ticker_spikes.append((d, px, med, ratio))
        if ticker_spikes:
            spikes[tk] = ticker_spikes

    return spikes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mult", type=float, default=DEFAULT_MULT,
                        help=f"Spike threshold (default {DEFAULT_MULT}x)")
    parser.add_argument("--apply", action="store_true",
                        help="Actually null out the bad rows (default dry-run)")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Detecting spikes >= {args.mult}x neighbor median ({NEIGHBOR_DAYS} days each side)")
    spikes = find_spikes(args.mult)

    total_spikes = sum(len(v) for v in spikes.values())
    print(f"\nFound {total_spikes:,} spike-rows across {len(spikes):,} tickers")

    # Top 20 worst offenders by row count
    top = sorted(spikes.items(), key=lambda kv: -len(kv[1]))[:20]
    print(f"\nTop 20 tickers by spike count:")
    print(f"  {'ticker':<10} {'spikes':>7} {'worst_ratio':>14} {'sample_date':>13}")
    for tk, sps in top:
        worst = max(sps, key=lambda x: x[3])
        print(f"  {tk:<10} {len(sps):>7} {worst[3]:>13,.1f}x {worst[0]:>13}")

    # Save report
    report = {
        "params": {"mult": args.mult, "neighbor_days": NEIGHBOR_DAYS},
        "total_spike_rows": total_spikes,
        "tickers_affected": len(spikes),
        "by_ticker": {
            tk: [{"date": d, "price": px, "neighbor_median": med, "ratio": ratio}
                 for d, px, med, ratio in sps]
            for tk, sps in spikes.items()
        },
    }
    report_path = OUT_DIR / "price_spikes.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f"\nReport written -> {report_path}")

    if args.apply:
        # Null out the spike rows
        print(f"\nAPPLY: setting price=NULL on {total_spikes:,} spike rows...")
        with connect() as conn:
            for tk, sps in spikes.items():
                for d, _, _, _ in sps:
                    conn.execute(
                        "UPDATE price_cache SET price=NULL WHERE ticker=? AND kind='close' AND key_date=?",
                        (tk, d))
            conn.commit()
        print(f"Done. Backup recommended before this; report is at {report_path}.")
    else:
        print(f"\n(dry-run; re-run with --apply to actually null these rows)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
