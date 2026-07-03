"""Run a momentum factor portfolio backtest and report per-year Sharpe.

Defaults to the in-sample window (2015-2023). Held-out test should be
run with --since 2024-01-01 --until 2026-05-01.

Usage:
  python -m scripts.run_momentum
  python -m scripts.run_momentum --since 2024-01-01 --until 2026-05-01 --label holdout
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum, low_vol
from trading_bot.factors.composite import composite_rank

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")

OUTPUT_DIR = Path("var/momentum/runs")

RANK_FNS = {
    "momentum": momentum.rank_universe,
    "low_vol":  low_vol.rank_universe,
    "multi":    composite_rank([momentum.rank_universe, low_vol.rank_universe]),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2015-01-01")
    ap.add_argument("--until", default="2023-12-31")
    ap.add_argument("--top-n", type=int, default=100)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--label", default="momentum")
    ap.add_argument("--factor", choices=list(RANK_FNS), default="momentum",
                    help="momentum | low_vol | multi (mom+low_vol composite)")
    args = ap.parse_args()
    rank_fn = RANK_FNS[args.factor]

    since = date.fromisoformat(args.since)
    until = date.fromisoformat(args.until)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_path = OUTPUT_DIR / f"{run_id}_{args.label}.json"

    print(f"Factor portfolio [{args.factor}]: {since} -> {until}  top_n={args.top_n}")
    print(f"Results -> {out_path}\n", flush=True)

    t0 = time.time()
    r = factor_backtest.run_factor_backtest(
        since=since, until=until, top_n=args.top_n,
        starting_cash=args.cash, rank_fn=rank_fn)
    elapsed = time.time() - t0

    yearly = r.sharpe_by_year()
    print()
    print("=" * 60)
    print(f"  MOMENTUM PORTFOLIO  {since} -> {until}")
    print("=" * 60)
    print(f"  Total return (MTM): {r.mtm_total_pnl_pct:+.2f}%")
    print(f"  Total return (book): {r.total_pnl_pct:+.2f}%  "
          f"(book lags MTM for held positions; MTM is the real number)")
    print(f"  Closed positions : {r.closed_count}")
    print(f"  Open positions   : {r.open_count}")
    print(f"  Equity-curve pts : {len(r.equity_curve)}")
    print(f"  Elapsed          : {elapsed/60:.1f} min")
    print()
    print("  Per-year Sharpe:")
    for y in sorted(yearly):
        print(f"    {y}: {yearly[y]:+.3f}")
    print("=" * 60, flush=True)

    out_path.write_text(json.dumps({
        "run_id": run_id, "since": args.since, "until": args.until,
        "top_n": args.top_n, "starting_cash": args.cash,
        "elapsed_seconds": round(elapsed, 1),
        "total_pnl_pct": round(r.total_pnl_pct, 3),
        "closed_count": r.closed_count, "open_count": r.open_count,
        "ending_cash": r.ending_cash,
        "open_positions_value": r.open_positions_value,
        "yearly_sharpe": {y: round(s, 4) for y, s in yearly.items()},
        "equity_curve": r.equity_curve,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
