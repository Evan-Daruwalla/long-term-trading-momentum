"""3-factor combo sweep: mom + ROA + accruals (Z-score).

Tests whether adding accruals as a 3rd factor improves on mom_roa_6535
(current deployed winner). Several weight combinations around the proven
mom-dominant region.

Sweep configs (preserving mom-dominance):
  - 60/30/10: most weight to mom, ROA dominant 2nd, accruals tiebreaker
  - 60/20/20: equal split between ROA and accruals
  - 55/25/20: lighter mom, more on quality
  - 50/30/20: equal weight ROA and accruals lift
  - 65/25/10: tight to current winner with light accruals add
  - 70/15/15: most mom, equal small quality contributions

6 configs x 2 windows = 12 runs, ~6-8 min.

Success criteria: any combo that beats mom_roa_6535 on BOTH windows on
CAGR or Sharpe. Bar is higher now (mom_roa is itself a strong baseline).
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import mom_roa_acc_zscore

OUT_PATH = Path("var/data_audit/mom_roa_acc_sweep.json")
STARTING_CASH = 100_000.0
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]

BASELINES = {
    "mom_v2": {
        "in_sample": {"cagr": 2.72, "sharpe": 0.167, "max_dd": -55.26},
        "holdout":   {"cagr": 28.81, "sharpe": 0.903, "max_dd": -33.86},
    },
    "mom_roa_6535": {
        "in_sample": {"cagr": 4.73, "sharpe": 0.241, "max_dd": -44.28},
        "holdout":   {"cagr": 36.45, "sharpe": 1.111, "max_dd": -30.43},
    },
}

# (label, w_mom, w_roa, w_acc)
WEIGHTS = [
    ("60_30_10",  0.60, 0.30, 0.10),
    ("60_20_20",  0.60, 0.20, 0.20),
    ("55_25_20",  0.55, 0.25, 0.20),
    ("50_30_20",  0.50, 0.30, 0.20),
    ("65_25_10",  0.65, 0.25, 0.10),
    ("70_15_15",  0.70, 0.15, 0.15),
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


def run_one(window_label, since, until, cfg_label, w_mom, w_roa, w_acc):
    label = f"mra_{cfg_label}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    rank_fn = mom_roa_acc_zscore.make_rank_fn(w_mom, w_roa, w_acc)
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
        "label": label, "window": window_label, "config": cfg_label,
        "w_mom": w_mom, "w_roa": w_roa, "w_acc": w_acc,
        "total_pct": total_pct, "cagr_pct": cagr,
        "mean_sharpe": mean_sh, "max_dd_pct": _max_drawdown(curve),
        "closed": r.closed_count, "elapsed_sec": round(time.time()-t0, 1),
    }


def main() -> int:
    print(f"MOM x ROA x ACC SWEEP: {len(WEIGHTS)} weights x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)
    runs = []
    for window_label, since, until in WINDOWS:
        for cfg_label, w_m, w_r, w_a in WEIGHTS:
            runs.append(run_one(window_label, since, until,
                                 cfg_label, w_m, w_r, w_a))

    print("\n" + "=" * 105)
    print("  3-FACTOR (mom+ROA+accruals) vs mom_v2 baseline + mom_roa_6535 (current winner)")
    print("=" * 105)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        b = BASELINES["mom_v2"][window_label]
        c = BASELINES["mom_roa_6535"][window_label]
        print(f"  {'config':<24} {'CAGR':>8} {'Sharpe':>8} {'maxDD':>9} "
              f"{'d_v2_CAGR':>10} {'d_roa_CAGR':>11} {'d_roa_Shrp':>11}")
        print("  " + "-" * 85)
        print(f"  {'mom_v2 (baseline)':<24} {b['cagr']:>+7.2f}% "
              f"{b['sharpe']:>+7.3f} {b['max_dd']:>+8.2f}%   (vs v2 ref)")
        print(f"  {'mom_roa_6535 (winner)':<24} {c['cagr']:>+7.2f}% "
              f"{c['sharpe']:>+7.3f} {c['max_dd']:>+8.2f}%   "
              f"{c['cagr']-b['cagr']:>+8.2f}pp (vs roa ref)")
        for r in runs:
            if r["window"] != window_label: continue
            d_v2 = r["cagr_pct"] - b["cagr"]
            d_roa_c = r["cagr_pct"] - c["cagr"]
            d_roa_s = r["mean_sharpe"] - c["sharpe"]
            print(f"  {r['label']:<24} {r['cagr_pct']:>+7.2f}% "
                  f"{r['mean_sharpe']:>+7.3f} {r['max_dd_pct']:>+8.2f}%  "
                  f"{d_v2:>+8.2f}pp {d_roa_c:>+9.2f}pp {d_roa_s:>+10.3f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
