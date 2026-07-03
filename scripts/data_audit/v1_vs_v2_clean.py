"""Side-by-side comparison of mom_v1 vs mom_v2 on CLEAN data.

After audit: mom_v1 in-sample CAGR (4.72%) > mom_v2 in-sample (2.72%).
But mom_v2 holdout (28.81%) > mom_v1 holdout (22.08%).

Question: is v2 still the right choice? Diversification (100 names) vs
concentration (50 names) — which wins on risk-adjusted basis?

Outputs the full risk/return profile for both, then a single side-by-side
decision table.
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum

OUT_PATH = Path("var/data_audit/v1_vs_v2_clean.json")
STARTING_CASH = 100_000.0

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
CONFIGS = [
    ("mom_v1", 100),
    ("mom_v2", 50),
]


def _max_drawdown(curve):
    peak = curve[0][1]
    max_dd = 0.0
    for _, val in curve:
        if val > peak: peak = val
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


def _calmar(cagr_pct, max_dd_pct):
    """CAGR / |max DD| — risk-adjusted return"""
    if max_dd_pct >= 0: return float('inf')
    return cagr_pct / abs(max_dd_pct)


def run_one(strat_label, top_n, window_label, since, until):
    print(f"  >>> {strat_label}_{window_label}", flush=True)
    factor_backtest.HALF_SPREAD_BPS = 5.0
    t0 = time.time()
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=top_n, starting_cash=STARTING_CASH,
        rank_fn=momentum.rank_universe, rebalance_freq="M",
    )
    curve = r.equity_curve
    total_pct = (curve[-1][1]/curve[0][1] - 1) * 100
    years = (until - since).days/365.25
    cagr = ((curve[-1][1]/curve[0][1]) ** (1/years) - 1) * 100
    sh = _sharpe_by_year(curve)
    mean_sh = statistics.fmean(sh.values()) if sh else 0.0
    max_dd = _max_drawdown(curve)
    return {
        "strategy": strat_label, "top_n": top_n,
        "window": window_label,
        "total_pct": total_pct, "cagr_pct": cagr,
        "max_dd_pct": max_dd,
        "mean_sharpe": mean_sh, "calmar": _calmar(cagr, max_dd),
        "closed": r.closed_count, "elapsed_sec": round(time.time()-t0,1),
    }


def main() -> int:
    print(f"MOM_V1 vs MOM_V2 (CLEAN DATA)")
    print("=" * 70, flush=True)
    runs = []
    for strat_label, top_n in CONFIGS:
        for window_label, since, until in WINDOWS:
            runs.append(run_one(strat_label, top_n, window_label, since, until))

    print("\n" + "=" * 95)
    print("  DECISION TABLE: v1 vs v2 (clean data, 5bps half-spread)")
    print("=" * 95)
    print(f"\n  {'window':<11} {'strategy':<10} {'CAGR':>8} {'Sharpe':>8} "
          f"{'maxDD':>8} {'Calmar':>8} {'trades':>8}")
    print("  " + "-" * 70)
    for window_label, _, _ in WINDOWS:
        for r in runs:
            if r["window"] != window_label: continue
            print(f"  {window_label:<11} {r['strategy']:<10} {r['cagr_pct']:>+7.2f}% "
                  f"{r['mean_sharpe']:>+7.3f} {r['max_dd_pct']:>+7.2f}% "
                  f"{r['calmar']:>+7.3f} {r['closed']:>7}")
        print("  " + "-" * 70)

    # Pairwise diffs per window
    print(f"\n  v2 minus v1 (positive = v2 better):")
    print(f"  {'window':<11} {'d_CAGR':>9} {'d_Sharpe':>10} {'d_maxDD':>10} {'d_Calmar':>10}")
    print("  " + "-" * 60)
    for window_label, _, _ in WINDOWS:
        v1 = next(r for r in runs if r["window"] == window_label and r["strategy"] == "mom_v1")
        v2 = next(r for r in runs if r["window"] == window_label and r["strategy"] == "mom_v2")
        print(f"  {window_label:<11} "
              f"{v2['cagr_pct']-v1['cagr_pct']:>+7.2f}pp "
              f"{v2['mean_sharpe']-v1['mean_sharpe']:>+9.3f} "
              f"{v2['max_dd_pct']-v1['max_dd_pct']:>+9.2f}pp "
              f"{v2['calmar']-v1['calmar']:>+9.3f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
