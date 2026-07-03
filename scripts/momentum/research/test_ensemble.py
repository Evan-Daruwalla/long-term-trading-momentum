"""Cross-strategy ensemble — meta-level voting between v1, v2, mom_roa_6535.

Tests if AGREEMENT between strategies signals higher conviction.

Variants (each x 2 windows = 8 runs):
  - intersection (3-way agreement, very selective ~5-20 picks)
  - majority (2+ of 3, moderate selectivity)
  - union (any pick, broad)
  - weighted (all picks, ranked by vote count, top_n=50)

Top-N for ensemble = 50 (same as mom_v2 / mom_roa). For variants with
fewer qualified candidates (intersection), the engine just buys however
many qualify.
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import ensemble

OUT_PATH = Path("var/data_audit/ensemble_sweep.json")
STARTING_CASH = 100_000.0
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]

BASELINES = {
    "mom_v2":       {"in_sample": {"cagr": 2.72, "sharpe": 0.167, "max_dd": -55.26},
                     "holdout":   {"cagr": 28.81, "sharpe": 0.903, "max_dd": -33.86}},
    "mom_roa_6535": {"in_sample": {"cagr": 4.73, "sharpe": 0.241, "max_dd": -44.28},
                     "holdout":   {"cagr": 36.45, "sharpe": 1.111, "max_dd": -30.43}},
}

MODES = ["intersection", "majority", "weighted", "union"]


def _max_drawdown(curve):
    peak = curve[0][1]; max_dd = 0.0
    for _, val in curve:
        if val > peak: peak = val
        if peak > 0:
            dd = (val/peak - 1.0) * 100
            if dd < max_dd: max_dd = dd
    return max_dd


def _sharpe_by_year(curve, risk_free_apy=0.045):
    by_year = {}
    pv = py = None
    for iso, v in curve:
        y = iso[:4]
        if pv and pv > 0 and y == py:
            by_year.setdefault(y, []).append(v/pv - 1.0)
        pv, py = v, y
    out = {}
    rf = risk_free_apy/252
    for y, rets in by_year.items():
        if len(rets) < 20: continue
        sd = statistics.pstdev(rets)
        if sd > 0:
            out[y] = ((statistics.fmean(rets)-rf)/sd) * (252**0.5)
    return out


def run_one(window_label, since, until, mode):
    label = f"ens_{mode}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    rank_fn = ensemble.make_ensemble_rank_fn(mode=mode)
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N, starting_cash=STARTING_CASH,
        rank_fn=rank_fn, rebalance_freq="M",
    )
    curve = r.equity_curve
    total_pct = (curve[-1][1]/curve[0][1] - 1) * 100
    years = (until - since).days/365.25
    cagr = ((curve[-1][1]/curve[0][1]) ** (1/years) - 1) * 100
    sh = _sharpe_by_year(curve)
    mean_sh = statistics.fmean(sh.values()) if sh else 0.0
    return {
        "label": label, "window": window_label, "mode": mode,
        "total_pct": total_pct, "cagr_pct": cagr,
        "mean_sharpe": mean_sh, "max_dd_pct": _max_drawdown(curve),
        "closed": r.closed_count, "elapsed_sec": round(time.time()-t0, 1),
    }


def main() -> int:
    print(f"ENSEMBLE SWEEP: {len(MODES)} modes x {len(WINDOWS)} windows = {len(MODES)*len(WINDOWS)} runs")
    print("=" * 70, flush=True)
    runs = []
    for window_label, since, until in WINDOWS:
        for mode in MODES:
            runs.append(run_one(window_label, since, until, mode))

    print("\n" + "=" * 110)
    print("  CROSS-STRATEGY ENSEMBLE (v1+v2+mom_roa_6535 voting) vs single-strategy baselines")
    print("=" * 110)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        v2 = BASELINES["mom_v2"][window_label]
        roa = BASELINES["mom_roa_6535"][window_label]
        print(f"  {'config':<24} {'CAGR':>8} {'Sharpe':>8} {'maxDD':>9} "
              f"{'d_v2_CAGR':>10} {'d_roa_CAGR':>11} {'d_roa_Shrp':>11}")
        print("  " + "-" * 90)
        print(f"  {'mom_v2 (baseline)':<24} {v2['cagr']:>+7.2f}% {v2['sharpe']:>+7.3f} {v2['max_dd']:>+8.2f}%   (vs v2 ref)")
        print(f"  {'mom_roa_6535 (winner)':<24} {roa['cagr']:>+7.2f}% {roa['sharpe']:>+7.3f} {roa['max_dd']:>+8.2f}%   "
              f"{roa['cagr']-v2['cagr']:>+8.2f}pp (vs roa ref)")
        for r in runs:
            if r["window"] != window_label: continue
            d_v2 = r["cagr_pct"] - v2["cagr"]
            d_roa_c = r["cagr_pct"] - roa["cagr"]
            d_roa_s = r["mean_sharpe"] - roa["sharpe"]
            print(f"  {r['label']:<24} {r['cagr_pct']:>+7.2f}% {r['mean_sharpe']:>+7.3f} {r['max_dd_pct']:>+8.2f}%  "
                  f"{d_v2:>+8.2f}pp {d_roa_c:>+9.2f}pp {d_roa_s:>+10.3f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
