"""PEAD test: standalone, vs baselines, combined with mom_roa.

NEW DATA: uses yfinance earnings_dates surprise data fetched 2026-05-28.
Coverage ~2020-2026 (24 quarters per ticker).

Configs (10 runs):
  - pead_solo (top-50 by most-positive recent surprise)
  - mom_pead_50_50  (50% mom + 50% pead Z)
  - mom_pead_70_30
  - mom_roa_pead_60_30_10 (mostly mom, some ROA, light PEAD boost)
  - mom_roa_pead_55_25_20
  - mom_roa_pead_65_20_15
  - mom_roa_pead_50_30_20

Compared to mom_v2 baseline AND mom_roa_6535 (current winner).

Hypothesis: in-sample 2015-19 has NO PEAD data; signal effectively
disabled for half the in-sample period. So in-sample improvement (if
any) is concentrated in 2020-2023. Held-out 2024-26 should show full
PEAD effect if there's an edge.
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import pead, mom_roa_pead_zscore, mom_roa_zscore

OUT_PATH = Path("var/data_audit/pead_sweep.json")
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


def _mom_pead_combiner(w_mom, w_pead):
    """A 2-factor mom+PEAD Z combiner (no ROA)."""
    from trading_bot.factors import momentum
    import statistics
    def _ranker(tickers, as_of):
        rows = []
        for t in tickers:
            m = momentum.momentum_score(t, as_of)
            if m is None:
                continue
            p = pead.pead_score(t, as_of)
            rows.append((t, m, p))
        if not rows: return []
        # Z mom
        mom_vals = [r[1] for r in rows]
        m_mean = statistics.fmean(mom_vals); m_sd = statistics.pstdev(mom_vals)
        mom_z = [(v - m_mean) / m_sd if m_sd > 0 else 0 for v in mom_vals]
        # Z pead (only non-None values; others get 0)
        pead_vals = [r[2] for r in rows if r[2] is not None]
        if len(pead_vals) >= 2:
            p_mean = statistics.fmean(pead_vals); p_sd = statistics.pstdev(pead_vals)
        else:
            p_mean = p_sd = 0
        pead_z = []
        for r in rows:
            if r[2] is None or p_sd <= 0:
                pead_z.append(0.0)
            else:
                pead_z.append((r[2] - p_mean) / p_sd)
        combined = [(rows[i][0], w_mom * mom_z[i] + w_pead * pead_z[i])
                    for i in range(len(rows))]
        combined.sort(key=lambda r: r[1], reverse=True)
        return combined
    return _ranker


CONFIGS = [
    ("pead_solo",        lambda: pead.rank_universe),
    ("mom_pead_70_30",   lambda: _mom_pead_combiner(0.7, 0.3)),
    ("mom_pead_50_50",   lambda: _mom_pead_combiner(0.5, 0.5)),
    ("mrp_60_30_10",     lambda: mom_roa_pead_zscore.make_rank_fn(0.60, 0.30, 0.10)),
    ("mrp_55_25_20",     lambda: mom_roa_pead_zscore.make_rank_fn(0.55, 0.25, 0.20)),
    ("mrp_65_20_15",     lambda: mom_roa_pead_zscore.make_rank_fn(0.65, 0.20, 0.15)),
    ("mrp_50_30_20",     lambda: mom_roa_pead_zscore.make_rank_fn(0.50, 0.30, 0.20)),
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
    by_year = {}; pv = py = None
    for iso, v in curve:
        y = iso[:4]
        if pv and pv > 0 and y == py:
            by_year.setdefault(y, []).append(v/pv - 1.0)
        pv, py = v, y
    out = {}; rf = risk_free_apy/252
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
    # Sanity check: PEAD data loaded
    cache = pead._load_cache()
    print(f"PEAD cache: {len(cache)} tickers, "
          f"{sum(len(v) for v in cache.values()):,} earnings events")

    print(f"\n{len(CONFIGS)} configs x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)
    runs = []
    for window_label, since, until in WINDOWS:
        for cfg_name, cfg_factory in CONFIGS:
            runs.append(run_one(window_label, since, until, cfg_name, cfg_factory))

    print("\n" + "=" * 105)
    print("  PEAD SWEEP vs mom_v2 baseline + mom_roa_6535 (current winner)")
    print("=" * 105)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        b = BASELINES["mom_v2"][window_label]
        c = BASELINES["mom_roa_6535"][window_label]
        print(f"  {'config':<22} {'CAGR':>8} {'Sharpe':>8} {'maxDD':>9} "
              f"{'d_v2_CAGR':>10} {'d_roa_CAGR':>11} {'d_roa_Shrp':>11}")
        print("  " + "-" * 85)
        print(f"  {'mom_v2 (baseline)':<22} {b['cagr']:>+7.2f}% "
              f"{b['sharpe']:>+7.3f} {b['max_dd']:>+8.2f}%   (vs v2 ref)")
        print(f"  {'mom_roa_6535 (winner)':<22} {c['cagr']:>+7.2f}% "
              f"{c['sharpe']:>+7.3f} {c['max_dd']:>+8.2f}%   "
              f"{c['cagr']-b['cagr']:>+8.2f}pp (vs roa ref)")
        for r in runs:
            if r["window"] != window_label: continue
            d_v2 = r["cagr_pct"] - b["cagr"]
            d_roa_c = r["cagr_pct"] - c["cagr"]
            d_roa_s = r["mean_sharpe"] - c["sharpe"]
            print(f"  {r['label']:<22} {r['cagr_pct']:>+7.2f}% "
                  f"{r['mean_sharpe']:>+7.3f} {r['max_dd_pct']:>+8.2f}%  "
                  f"{d_v2:>+8.2f}pp {d_roa_c:>+9.2f}pp {d_roa_s:>+10.3f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
