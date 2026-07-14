"""EXPLORATORY (post-hoc, NON-prereg, NON-deployment) — extend the residual_roa
weight sweep past the grid edge to find where the holdout CAGR gradient tops out.

Context: the pre-registered sweep (Appendix BU, docs/prereg_2026-07-14_champs_tweaks.md)
found residual_roa holdout CAGR MONOTONE in residual-momentum weight, maxing at the
grid edge w80/20 (+37.15%). That rising-at-the-edge shape is a classic sample-fit
tell. This runs w80/85/90/95 to see whether the gradient keeps climbing (=> the
"optimum" is just "minimize the ROA leg", which UNDERCUTS the 80/20 finding) or peaks.

THIS IS DATA-SNOOPING BY CONSTRUCTION (grid chosen AFTER seeing w80 win). Per the
prereg it can ONLY inform a future new-research-sleeve decision (Evan's call); it can
NEVER justify deployment. Stops at w95 (ROA weight 0.05): w100 would drop the ROA-data
requirement and change the universe, breaking apples-to-apples with the sweep.

Usage: .venv\\Scripts\\python.exe -m scripts.momentum.research.sweep_residual_hiw_ext
Output: var/momentum/residual_hiw_ext.json
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import residual_momentum, roa, zcombo
from scripts.momentum.research.test_mom_v2_preemptive import (
    _sharpe_by_year, _max_drawdown,
)

OUT_PATH = Path("var/momentum/residual_hiw_ext.json")
STARTING_CASH = 100_000.0
TOP_N = 50
WEIGHTS = [0.80, 0.85, 0.90, 0.95]   # residual weight; ROA = 1-w (w80 = self-check vs sweep)
WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
# Clean baseline (65/35@50) from the 06-13 revalidation, for the delta column.
BASE = {"in_sample": {"cagr": 9.47}, "holdout": {"cagr": 32.07}}


def run_one(w: float, window_label: str, since: date, until: date) -> dict:
    print(f"  >>> residual_w{int(w*100)}{int(round((1-w)*100)):02d}_{window_label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    rank_fn = zcombo.make_rank_fn([
        (residual_momentum.residual_momentum_score, w),
        (roa.roa_score, round(1.0 - w, 2)),
    ])
    r = factor_backtest.run_factor_backtest(
        since=since, until=until, top_n=TOP_N,
        starting_cash=STARTING_CASH, rank_fn=rank_fn, rebalance_freq="M",
    )
    curve = r.equity_curve
    years = (until - since).days / 365.25
    cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
    sh = _sharpe_by_year(curve)
    out = {
        "weight": w, "window": window_label,
        "cagr_pct": round(cagr, 4),
        "mean_sharpe": round(statistics.fmean(sh.values()) if sh else 0.0, 4),
        "max_dd_pct": round(_max_drawdown(curve), 4),
        "closed": r.closed_count, "elapsed_sec": round(time.time() - t0, 1),
    }
    print(f"      CAGR {out['cagr_pct']:+.2f}%  Sharpe {out['mean_sharpe']:+.3f}  "
          f"maxDD {out['max_dd_pct']:+.1f}%  ({out['elapsed_sec']}s)", flush=True)
    return out


def main() -> int:
    print("EXPLORATORY residual hi-weight extension (post-hoc, non-deployment)")
    print("=" * 74, flush=True)
    runs = [run_one(w, wl, s, u) for wl, s, u in WINDOWS for w in WEIGHTS]

    print("\n" + "=" * 72)
    for wl, _s, _u in WINDOWS:
        print(f"\n  residual / {wl}   (65/35 baseline CAGR {BASE[wl]['cagr']:+.2f}%)")
        print(f"  {'weight':<8} {'CAGR %':>9} {'vs 65/35':>9} {'Sharpe':>8} {'maxDD %':>9}")
        print("  " + "-" * 50)
        prev = None
        for r in runs:
            if r["window"] != wl:
                continue
            arrow = "" if prev is None else ("  UP" if r["cagr_pct"] > prev else "  DOWN")
            print(f"  {int(r['weight']*100)}/{int(round((1-r['weight'])*100)):02d}   "
                  f"{r['cagr_pct']:>+8.2f}% {r['cagr_pct']-BASE[wl]['cagr']:>+8.2f}p "
                  f"{r['mean_sharpe']:>+8.3f} {r['max_dd_pct']:>+8.2f}%{arrow}")
            prev = r["cagr_pct"]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs, "note": "post-hoc exploratory, non-deployment"},
                                   indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
