"""Test ROA (Novy-Marx profitability) standalone + combined with momentum
via cross-sectional Z-score.

SUBSTITUTION NOTE: original plan B was value+momentum (P/B + 12-1 momentum).
Shares-outstanding data not cached (dei: namespace not warmed). ROA
substituted because it (a) uses only cached data, (b) is a fundamental
quality/profitability factor in the same spirit, (c) has known academic
support (Novy-Marx 2013). Same question being tested: can a fundamental
factor combine with momentum cross-sectionally to beat mom_v2 alone?

Sweep (10 runs):
  - roa_solo (top-50 by ROA alone)               x in/out
  - mom_solo (= mom_v2, reference)               x in/out  [SKIP, use known]
  - mom_roa_5050 (w_mom=0.5, w_roa=0.5)          x in/out
  - mom_roa_7030 (w_mom=0.7, w_roa=0.3)          x in/out
  - mom_roa_3070 (w_mom=0.3, w_roa=0.7)          x in/out

8 actual backtests (mom_solo already known: +2.72/+28.81). ~5-8 min.

Success criteria: any variant beats mom_v2 on BOTH windows on CAGR or
Sharpe, without major DD regression.
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import roa, mom_roa_zscore

OUT_PATH = Path("var/data_audit/mom_roa_zscore_sweep.json")
STARTING_CASH = 100_000.0
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
BASELINE_MOM_V2 = {
    "in_sample": {"cagr": 2.72, "max_dd": -55.26, "sharpe": 0.167},
    "holdout":   {"cagr": 28.81, "max_dd": -33.86, "sharpe": 0.903},
}

CONFIGS = [
    ("roa_solo",        lambda: roa.rank_universe),
    ("mom_roa_5050",    lambda: mom_roa_zscore.make_rank_fn(0.5, 0.5)),
    ("mom_roa_7030",    lambda: mom_roa_zscore.make_rank_fn(0.7, 0.3)),
    ("mom_roa_3070",    lambda: mom_roa_zscore.make_rank_fn(0.3, 0.7)),
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


def run_one(window_label, since, until, cfg_name, cfg_factory):
    label = f"{cfg_name}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    rank_fn = cfg_factory()
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
        "label": label, "window": window_label, "config": cfg_name,
        "total_pct": total_pct, "cagr_pct": cagr,
        "mean_sharpe": mean_sh, "max_dd_pct": _max_drawdown(curve),
        "closed": r.closed_count, "elapsed_sec": round(time.time()-t0, 1),
    }


def main() -> int:
    print(f"MOM x ROA Z-SCORE SWEEP: {len(CONFIGS)} configs x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)
    runs = []
    for window_label, since, until in WINDOWS:
        for cfg_name, cfg_factory in CONFIGS:
            runs.append(run_one(window_label, since, until, cfg_name, cfg_factory))

    print("\n" + "=" * 95)
    print("  MOM x ROA  vs  mom_v2 baseline")
    print("=" * 95)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        b = BASELINE_MOM_V2[window_label]
        print(f"  {'config':<24} {'CAGR':>8} {'Sharpe':>8} {'maxDD':>9} "
              f"{'d_cagr':>8} {'d_dd':>8} {'d_sharpe':>10}")
        print("  " + "-" * 80)
        print(f"  {'mom_v2 baseline':<24} {b['cagr']:>+7.2f}% "
              f"{b['sharpe']:>+7.3f} {b['max_dd']:>+8.2f}%   (reference)")
        for r in runs:
            if r["window"] != window_label: continue
            d_c = r["cagr_pct"] - b["cagr"]
            d_d = r["max_dd_pct"] - b["max_dd"]
            d_s = r["mean_sharpe"] - b["sharpe"]
            print(f"  {r['label']:<24} {r['cagr_pct']:>+7.2f}% "
                  f"{r['mean_sharpe']:>+7.3f} {r['max_dd_pct']:>+8.2f}%  "
                  f"{d_c:>+7.2f}pp {d_d:>+7.2f}pp {d_s:>+9.3f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
