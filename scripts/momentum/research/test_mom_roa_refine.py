"""Refinement sweep around mom_roa_7030 winner.

Prior coarse sweep showed mom_roa_7030 beats baseline mom_v2 on both
windows on every metric (+7.27pp held-out CAGR, +0.195 Sharpe, +2.95pp DD).

This narrows: test 80/20, 75/25, 65/35, 60/40 to find true peak around 7030.

8 backtests, ~5-6 min.
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import mom_roa_zscore

OUT_PATH = Path("var/data_audit/mom_roa_refine.json")
STARTING_CASH = 100_000.0
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
BASELINE = {
    "in_sample": {"cagr": 2.72, "max_dd": -55.26, "sharpe": 0.167},
    "holdout":   {"cagr": 28.81, "max_dd": -33.86, "sharpe": 0.903},
}
# Prior sweep result for 7030 (for reference)
PRIOR_7030 = {
    "in_sample": {"cagr": 3.93, "max_dd": -46.63, "sharpe": 0.201},
    "holdout":   {"cagr": 36.08, "max_dd": -30.91, "sharpe": 1.098},
}

# Refined weights around 7030
WEIGHTS = [
    (0.80, 0.20),
    (0.75, 0.25),
    (0.65, 0.35),
    (0.60, 0.40),
]


def _max_drawdown(curve):
    peak = curve[0][1]
    max_dd = 0.0
    for _, val in curve:
        if val > peak: peak = val
        if peak > 0:
            dd = (val/peak - 1.0) * 100
            if dd < max_dd: max_dd = dd
    return max_dd


def _sharpe_by_year(curve, risk_free_apy=0.045):
    by_year: dict[str, list[float]] = {}
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


def run_one(window_label, since, until, w_mom, w_roa):
    label = f"mom_roa_{int(w_mom*100):02d}{int(w_roa*100):02d}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    rank_fn = mom_roa_zscore.make_rank_fn(w_mom, w_roa)
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
        "label": label, "window": window_label,
        "w_mom": w_mom, "w_roa": w_roa,
        "total_pct": total_pct, "cagr_pct": cagr,
        "mean_sharpe": mean_sh, "max_dd_pct": _max_drawdown(curve),
        "closed": r.closed_count, "elapsed_sec": round(time.time()-t0, 1),
    }


def main() -> int:
    print(f"MOM x ROA REFINEMENT: {len(WEIGHTS)} weights x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)
    runs = []
    for window_label, since, until in WINDOWS:
        for w_m, w_r in WEIGHTS:
            runs.append(run_one(window_label, since, until, w_m, w_r))

    print("\n" + "=" * 100)
    print("  MOM x ROA WEIGHT-REFINEMENT  vs  mom_v2 baseline (and prior 7030)")
    print("=" * 100)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        b = BASELINE[window_label]
        p70 = PRIOR_7030[window_label]
        print(f"  {'config':<26} {'CAGR':>8} {'Sharpe':>8} {'maxDD':>9} "
              f"{'d_cagr':>8} {'d_dd':>8} {'d_sharpe':>10}")
        print("  " + "-" * 80)
        print(f"  {'mom_v2 baseline':<26} {b['cagr']:>+7.2f}% "
              f"{b['sharpe']:>+7.3f} {b['max_dd']:>+8.2f}%   (reference)")
        print(f"  {'mom_roa_7030 (prior)':<26} {p70['cagr']:>+7.2f}% "
              f"{p70['sharpe']:>+7.3f} {p70['max_dd']:>+8.2f}%   "
              f"{p70['cagr']-b['cagr']:>+7.2f}pp {p70['max_dd']-b['max_dd']:>+7.2f}pp "
              f"{p70['sharpe']-b['sharpe']:>+9.3f}")
        for r in runs:
            if r["window"] != window_label: continue
            d_c = r["cagr_pct"] - b["cagr"]
            d_d = r["max_dd_pct"] - b["max_dd"]
            d_s = r["mean_sharpe"] - b["sharpe"]
            print(f"  {r['label']:<26} {r['cagr_pct']:>+7.2f}% "
                  f"{r['mean_sharpe']:>+7.3f} {r['max_dd_pct']:>+8.2f}%  "
                  f"{d_c:>+7.2f}pp {d_d:>+7.2f}pp {d_s:>+9.3f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
