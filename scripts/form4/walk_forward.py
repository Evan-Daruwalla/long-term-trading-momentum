"""Post-hoc train/test split on a completed backtest run.

Walk-forward validation is essential because every R-iteration in this
project tunes parameters on the same 2021-2026 window. To know whether
the strategy's "edge" is real or fitted, we need to see whether
performance on the latest unseen years matches earlier years.

This script doesn't re-run the simulator — it slices an existing
{run_id}/{profile}.json by entry_date and reports separate metrics for:
  TRAIN: positions entered before --split-date
  TEST:  positions entered on/after --split-date

Usage:
  python -m scripts.walk_forward 20260507-094340 --split 2024-07-01

Caveat: this is a lightweight slice, not a true walk-forward. True walk-
forward would re-train profile params on TRAIN only, then run TEST with
locked params. We don't (yet) have a parameter-search loop, so this
script approximates by partitioning the same single-config backtest.
The signal it gives: if TEST returns are sharply different from TRAIN,
the headline number doesn't generalize.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from statistics import mean

ARCHIVE_DIR = Path("var/form4/archive/runs")


def _stats(vals: list[float]) -> str:
    if not vals:
        return "n=0"
    wins = sum(1 for v in vals if v > 0)
    return (f"n={len(vals):3d}  win%={100*wins/len(vals):4.1f}  "
            f"avg%={mean(vals):+5.1f}  sum%={sum(vals):+7.1f}")


def _slice(closed: list[dict], split_date: date) -> tuple[list[dict], list[dict]]:
    train = [p for p in closed if date.fromisoformat(p["entry_date"][:10]) < split_date]
    test  = [p for p in closed if date.fromisoformat(p["entry_date"][:10]) >= split_date]
    return train, test


def _by_year(positions: list[dict]) -> dict[str, list[float]]:
    out: dict[str, list[float]] = defaultdict(list)
    for p in positions:
        out[p["entry_date"][:4]].append(p["realized_pnl_pct"])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id", help="run_id directory under var/form4/archive/runs/")
    ap.add_argument("--split", default="2024-07-01",
                    help="ISO date — entries before = train, on/after = test")
    args = ap.parse_args()

    run_dir = ARCHIVE_DIR / args.run_id
    if not run_dir.is_dir():
        raise SystemExit(f"No such run: {run_dir}")
    split_date = date.fromisoformat(args.split)

    print(f"\nWalk-forward analysis of {args.run_id}")
    print(f"Split: {split_date}\n")

    for prof in ("conservative", "normal", "aggressive"):
        path = run_dir / f"{prof}.json"
        if not path.exists():
            continue
        d = json.loads(path.read_text())
        starting = d["starting_cash"]
        closed = d["closed_positions"]
        train, test = _slice(closed, split_date)

        # Realized $ contribution per slice
        train_real = sum(p["realized_pnl"] for p in train)
        test_real  = sum(p["realized_pnl"]  for p in test)

        print(f"=" * 72)
        print(f"  {prof.upper()}")
        print(f"=" * 72)
        print(f"  Headline (full window): {d['total_pnl_pct']:+.2f}%  "
              f"closed={len(closed)}")
        print(f"  TRAIN  ({len(train):3d} closed): "
              f"realized=${train_real:+,.0f}  ({100*train_real/starting:+.2f}% of NAV)")
        print(f"  TEST   ({len(test):3d} closed): "
              f"realized=${test_real:+,.0f}  ({100*test_real/starting:+.2f}% of NAV)")

        # Edge by year — does P&L distribution shift after split?
        print(f"\n  Per-year (TRAIN years above split, TEST below):")
        by_year = _by_year(closed)
        for y in sorted(by_year):
            tag = "TRAIN" if int(y) < split_date.year else "TEST"
            print(f"    {y} [{tag:5}]  {_stats(by_year[y])}")

        # Per-trade win rate comparison (the core question)
        if train and test:
            train_winrate = 100 * sum(1 for p in train if p["realized_pnl"] > 0) / len(train)
            test_winrate  = 100 * sum(1 for p in test  if p["realized_pnl"] > 0) / len(test)
            train_avg     = mean(p["realized_pnl_pct"] for p in train)
            test_avg      = mean(p["realized_pnl_pct"] for p in test)
            print(f"\n  GENERALIZATION:")
            print(f"    win% : train={train_winrate:.1f}  test={test_winrate:.1f}  "
                  f"delta={test_winrate-train_winrate:+.1f}pp")
            print(f"    avg% : train={train_avg:+.2f}  test={test_avg:+.2f}  "
                  f"delta={test_avg-train_avg:+.2f}pp")
            # Verdict semantics: a TRAIN > TEST gap means the strategy does
            # worse out-of-sample → fitted. TEST > TRAIN means out-of-sample
            # is *better* → not overfit (could be regime-favorable, but not
            # a generalization failure). Within ~1pp = generalizes cleanly.
            delta_avg = test_avg - train_avg
            if abs(delta_avg) < 1.0:
                verdict = "test generalizes cleanly"
            elif delta_avg > 0:
                verdict = "test outperforms train (regime-favorable, not overfit)"
            else:
                verdict = "test underperforms train (overfit / edge degrading)"
            print(f"    verdict: {verdict}")
        print()


if __name__ == "__main__":
    main()
