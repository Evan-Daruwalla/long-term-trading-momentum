"""Insider cluster buying — solo and as 3rd factor in mom+ROA+cluster combo.

NEW FRAMING: uses existing Form 4 data (2.3M cached rows) with a
cluster-aggregation lens. Phase 1 single-insider copy was decisively
closed (form4_verdict.md); this tests if AGGREGATED cluster signal works.

Configs (each x 2 windows = 12 runs total):
  - cluster_solo (top-50 by cluster_score, no momentum filter)
  - mom_cluster_50_50 (Z-score combo of mom + cluster)
  - mom_roa_cluster_55_30_15 (mom+ROA+cluster Z-score)
  - mom_roa_cluster_50_25_25 (heavier cluster)
  - mom_roa_cluster_60_25_15 (mom-dominant + balanced quality+cluster)
  - mom_roa_cluster_50_30_20 (parallel to best 3-factor accruals test)

Hypothesis: cluster buying is fundamentally orthogonal to both price-
momentum and earnings-quality. If insider conviction adds info, this
combo should improve mom_roa_6535 on Sharpe or DD.
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum, roa, insider_cluster

OUT_PATH = Path("var/data_audit/insider_cluster_sweep.json")
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


def _zscore(values):
    if len(values) < 2: return [0.0] * len(values)
    mean = statistics.fmean(values); sd = statistics.pstdev(values)
    return [(v - mean) / sd for v in values] if sd > 0 else [0.0] * len(values)


def make_mom_cluster(w_mom: float, w_cluster: float):
    def _ranker(tickers, as_of):
        rows = []
        for t in tickers:
            m = momentum.momentum_score(t, as_of)
            c = insider_cluster.cluster_score(t, as_of)
            if m is not None:
                rows.append((t, m, float(c)))
        if not rows: return []
        mz = _zscore([r[1] for r in rows])
        cz = _zscore([r[2] for r in rows])
        combined = [(rows[i][0], w_mom*mz[i] + w_cluster*cz[i]) for i in range(len(rows))]
        combined.sort(key=lambda r: r[1], reverse=True)
        return combined
    return _ranker


def make_mom_roa_cluster(w_mom: float, w_roa: float, w_cluster: float):
    def _ranker(tickers, as_of):
        rows = []
        for t in tickers:
            m = momentum.momentum_score(t, as_of)
            r = roa.roa_score(t, as_of)
            c = insider_cluster.cluster_score(t, as_of)
            if m is not None and r is not None:
                rows.append((t, m, r, float(c)))
        if not rows: return []
        mz = _zscore([x[1] for x in rows])
        rz = _zscore([x[2] for x in rows])
        cz = _zscore([x[3] for x in rows])
        combined = [(rows[i][0],
                     w_mom*mz[i] + w_roa*rz[i] + w_cluster*cz[i])
                    for i in range(len(rows))]
        combined.sort(key=lambda r: r[1], reverse=True)
        return combined
    return _ranker


CONFIGS = [
    ("cluster_solo",         lambda: insider_cluster.rank_universe),
    ("mom_cluster_50_50",    lambda: make_mom_cluster(0.5, 0.5)),
    ("mrc_55_30_15",         lambda: make_mom_roa_cluster(0.55, 0.30, 0.15)),
    ("mrc_50_25_25",         lambda: make_mom_roa_cluster(0.50, 0.25, 0.25)),
    ("mrc_60_25_15",         lambda: make_mom_roa_cluster(0.60, 0.25, 0.15)),
    ("mrc_50_30_20",         lambda: make_mom_roa_cluster(0.50, 0.30, 0.20)),
]


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


def run_one(window_label, since, until, cfg_label, cfg_factory):
    label = f"{cfg_label}_{window_label}"
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
        "label": label, "window": window_label, "config": cfg_label,
        "total_pct": total_pct, "cagr_pct": cagr,
        "mean_sharpe": mean_sh, "max_dd_pct": _max_drawdown(curve),
        "closed": r.closed_count, "elapsed_sec": round(time.time()-t0, 1),
    }


def main() -> int:
    print(f"INSIDER CLUSTER SWEEP: {len(CONFIGS)} configs x {len(WINDOWS)} windows = {len(CONFIGS)*len(WINDOWS)} runs")
    print("=" * 70, flush=True)
    runs = []
    for window_label, since, until in WINDOWS:
        for cfg_label, cfg_factory in CONFIGS:
            runs.append(run_one(window_label, since, until, cfg_label, cfg_factory))

    print("\n" + "=" * 110)
    print("  INSIDER CLUSTER  vs  mom_v2 + mom_roa_6535")
    print("=" * 110)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        v2 = BASELINES["mom_v2"][window_label]
        roa_b = BASELINES["mom_roa_6535"][window_label]
        print(f"  {'config':<24} {'CAGR':>8} {'Sharpe':>8} {'maxDD':>9} "
              f"{'d_v2_CAGR':>10} {'d_roa_CAGR':>11} {'d_roa_Shrp':>11}")
        print("  " + "-" * 90)
        print(f"  {'mom_v2 (baseline)':<24} {v2['cagr']:>+7.2f}% {v2['sharpe']:>+7.3f} {v2['max_dd']:>+8.2f}%   (vs v2 ref)")
        print(f"  {'mom_roa_6535 (winner)':<24} {roa_b['cagr']:>+7.2f}% {roa_b['sharpe']:>+7.3f} {roa_b['max_dd']:>+8.2f}%   "
              f"{roa_b['cagr']-v2['cagr']:>+8.2f}pp (vs roa ref)")
        for r in runs:
            if r["window"] != window_label: continue
            d_v2 = r["cagr_pct"] - v2["cagr"]
            d_roa_c = r["cagr_pct"] - roa_b["cagr"]
            d_roa_s = r["mean_sharpe"] - roa_b["sharpe"]
            print(f"  {r['label']:<24} {r['cagr_pct']:>+7.2f}% {r['mean_sharpe']:>+7.3f} {r['max_dd_pct']:>+8.2f}%  "
                  f"{d_v2:>+8.2f}pp {d_roa_c:>+9.2f}pp {d_roa_s:>+10.3f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
