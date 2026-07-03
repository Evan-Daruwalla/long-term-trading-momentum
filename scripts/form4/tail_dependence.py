"""Quantify a strategy's tail-dependence by stripping top-N contributors.

CABA-randomness across R10/R11/R12 showed the headline P&L flips by 35pp
based on whether a single trade fires. This script reports, for any
backtest archive:

  - reported total P&L
  - P&L stripping top-1 contributor (single-trade dependency)
  - P&L stripping top-3, top-5, top-10
  - Median per-trade %
  - Per-trade % distribution percentiles (p10 / p25 / p50 / p75 / p90)
  - Sharpe of the per-trade % series (annualized assuming 60-day holds)

A strategy with real edge has positive Sharpe and survives strip-top-1.
A strategy that flips negative when you remove one trade is a lottery
ticket detector, not edge.

Usage:
  python -m scripts.tail_dependence 20260507-094340
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, median, stdev

ARCHIVE_DIR = Path("var/form4/archive/runs")


def _percentile(vals: list[float], p: float) -> float:
    if not vals:
        return float("nan")
    s = sorted(vals)
    k = (len(s) - 1) * p
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] * (c - k) + s[c] * (k - f)


def _strip_top(closed: list[dict], n: int) -> float:
    """Sum of realized_pnl after removing top-n contributors."""
    pnls = sorted([p["realized_pnl"] for p in closed], reverse=True)
    return sum(pnls[n:])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id")
    args = ap.parse_args()
    run_dir = ARCHIVE_DIR / args.run_id
    if not run_dir.is_dir():
        raise SystemExit(f"No such run: {run_dir}")

    print(f"\nTail-dependence analysis of {args.run_id}\n")

    for prof in ("conservative", "normal", "aggressive"):
        path = run_dir / f"{prof}.json"
        if not path.exists():
            continue
        d = json.loads(path.read_text())
        closed = d["closed_positions"]
        if not closed:
            continue
        starting = d["starting_cash"]
        pcts = [p["realized_pnl_pct"] for p in closed]

        print(f"=" * 72)
        print(f"  {prof.upper()}  closed={len(closed)}  "
              f"reported={d['total_pnl_pct']:+.2f}%")
        print(f"=" * 72)

        # Strip-top contributions
        total_real = sum(p["realized_pnl"] for p in closed)
        for n in (0, 1, 3, 5, 10):
            stripped = _strip_top(closed, n)
            label = "as reported" if n == 0 else f"strip top-{n}"
            print(f"  {label:<14}: realized=${stripped:+,.0f} "
                  f"({100*stripped/starting:+.2f}% of NAV)")

        # Per-trade distribution
        print(f"\n  Per-trade % distribution:")
        print(f"    mean    : {mean(pcts):+.2f}")
        print(f"    median  : {median(pcts):+.2f}")
        print(f"    stdev   : {stdev(pcts) if len(pcts) > 1 else 0:.2f}")
        for p in (0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99):
            print(f"    p{int(p*100):2d}     : {_percentile(pcts, p):+.2f}")

        # Naive trade-Sharpe (assumes ~60-day holds → ~6 holds/yr,
        # so annualized stdev = stdev × sqrt(6); annualized mean = mean × 6)
        if len(pcts) > 1:
            sd = stdev(pcts)
            if sd > 0:
                trade_sharpe = mean(pcts) / sd
                ann_sharpe = trade_sharpe * (6 ** 0.5)
                print(f"\n  Per-trade Sharpe : {trade_sharpe:+.3f}")
                print(f"  Annualized Sharpe: {ann_sharpe:+.3f}  "
                      f"(assumes ~60-day holds, 6 turnover/yr)")

        # Concentration metric: how much of P&L is in top-N trades?
        sorted_pnl = sorted([p["realized_pnl"] for p in closed], reverse=True)
        if total_real > 0:
            top1_share = 100 * sorted_pnl[0] / total_real
            top5_share = 100 * sum(sorted_pnl[:5]) / total_real
            print(f"\n  Concentration (% of total realized $):")
            print(f"    top 1 trade : {top1_share:.1f}%")
            print(f"    top 5 trades: {top5_share:.1f}%")

        # The verdict
        strip1 = _strip_top(closed, 1)
        if total_real > 0 and strip1 < 0:
            verdict = "[FRAGILE] flips negative on single-trade removal"
        elif total_real > 0 and strip1 > 0 and strip1 < total_real * 0.5:
            verdict = "[HALF-LOTTERY] top trade is >50% of headline"
        elif total_real > 0:
            verdict = "[ROBUST] survives top-trade strip"
        else:
            verdict = "[n/a] strategy already negative"
        print(f"\n  Verdict: {verdict}\n")


if __name__ == "__main__":
    main()
