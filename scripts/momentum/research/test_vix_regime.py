"""VIX term structure regime filter for mom_v2 + mom_roa_6535.

NEW DATA EXPERIMENT (using data not previously cached).
Fetches ^VIX (1-month implied vol) and ^VXV (3-month implied vol) from
yfinance, then uses the ratio as a regime signal:

  VIX/VXV >= 1.0 (backwardation / stress) -> scale exposure DOWN
  VIX/VXV <  1.0 (contango / calm)         -> full exposure

Documented behavior: VIX term-structure inversion precedes crashes
(2008, 2011, 2018-Q4, 2020-03, 2022). Theory: when investors pay more
for near-term protection than 3-month, they expect imminent stress.

Sweep:
  - Base strategy: mom_v2 and mom_roa_6535
  - Regime scaling: {hard cutoff (0 or 1.0), graded (linear scale)}
  - Threshold: 1.0 (canonical), 0.95 (more sensitive), 1.05 (less sensitive)

For first pass: just test the canonical 1.0 hard-cutoff version on both
strategies, both windows = 4 runs. If promising, refine.

Output: vs baseline mom_v2 and baseline mom_roa_6535 on both windows.
"""
from __future__ import annotations

import json
import math
import statistics
import time
from datetime import date, timedelta
from pathlib import Path

import yfinance as yf

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum, mom_roa_zscore
from trading_bot.strategies import mom_roa_6535

OUT_PATH = Path("var/data_audit/vix_regime.json")
VIX_CACHE_PATH = Path("var/data_audit/vix_vxv_cache.json")
STARTING_CASH = 100_000.0
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]

BASELINES = {
    "mom_v2": {
        "in_sample": {"cagr": 2.72, "max_dd": -55.26, "sharpe": 0.167},
        "holdout":   {"cagr": 28.81, "max_dd": -33.86, "sharpe": 0.903},
    },
    "mom_roa_6535": {
        "in_sample": {"cagr": 4.73, "max_dd": -44.28, "sharpe": 0.241},
        "holdout":   {"cagr": 36.45, "max_dd": -30.43, "sharpe": 1.111},
    },
}


def _fetch_vix_vxv() -> dict[str, dict[str, float]]:
    """Returns {iso_date: {'vix': float, 'vxv': float}}. Caches to disk."""
    if VIX_CACHE_PATH.exists():
        print(f"  [cache] loading VIX/VXV from {VIX_CACHE_PATH}", flush=True)
        return json.loads(VIX_CACHE_PATH.read_text())

    print(f"  [fetch] downloading ^VIX + ^VIX3M from yfinance (2014-2026)...", flush=True)
    t0 = time.time()
    out: dict[str, dict[str, float]] = {}
    # ^VXV was renamed to ^VIX3M by Cboe in 2017. ^VIX3M is the live ticker.
    for ticker, key in [("^VIX", "vix"), ("^VIX3M", "vxv")]:
        df = yf.Ticker(ticker).history(start="2014-06-01", end="2026-05-31",
                                         auto_adjust=False)
        for ts, row in df.iterrows():
            iso = ts.date().isoformat()
            close = float(row["Close"])
            if iso not in out:
                out[iso] = {}
            out[iso][key] = close
    # Drop dates missing either
    out = {d: v for d, v in out.items() if "vix" in v and "vxv" in v}
    VIX_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    VIX_CACHE_PATH.write_text(json.dumps(out, indent=2))
    print(f"  [fetch] {len(out)} days with both VIX+VXV, "
          f"{time.time()-t0:.1f}s", flush=True)
    return out


_VIX_VXV: dict[str, dict[str, float]] = {}


def make_vix_regime_scaler(threshold: float = 1.0, hard_cutoff: bool = True):
    """Returns position_scale_fn that scales based on VIX/VXV ratio.

    hard_cutoff=True: scale = 0 if VIX/VXV >= threshold, else 1
    hard_cutoff=False: scale = clamp(1 - max(0, (ratio - threshold) * 5), 0, 1)
                        i.e. graded reduction when ratio exceeds threshold
    """
    def scaler(as_of: date) -> float:
        # Look back up to 7 days to find a valid VIX/VXV reading
        for back in range(7):
            iso = (as_of - timedelta(days=back)).isoformat()
            row = _VIX_VXV.get(iso)
            if row:
                ratio = row["vix"] / row["vxv"]
                if hard_cutoff:
                    return 0.0 if ratio >= threshold else 1.0
                else:
                    excess = max(0.0, ratio - threshold)
                    return max(0.0, 1.0 - excess * 5.0)
        return 1.0  # no data — default to full exposure
    return scaler


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


CONFIGS = [
    # (strategy_name, rank_fn_factory, base_label)
    ("mom_v2",       lambda: momentum.rank_universe,                          "mom_v2"),
    ("mom_roa_6535", lambda: mom_roa_zscore.make_rank_fn(0.65, 0.35),         "mom_roa_6535"),
]
REGIME_VARIANTS = [
    # (label, threshold, hard_cutoff)
    ("vix_hard_1.0",  1.00, True),
    ("vix_hard_0.95", 0.95, True),
    ("vix_grad_1.0",  1.00, False),
]


def run_one(strat_label, rank_fn_factory, window_label, since, until,
            regime_label, threshold, hard_cutoff):
    label = f"{strat_label}_{regime_label}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N, starting_cash=STARTING_CASH,
        rank_fn=rank_fn_factory(),
        rebalance_freq="M",
        position_scale_fn=make_vix_regime_scaler(threshold, hard_cutoff),
    )
    curve = r.equity_curve
    total_pct = (curve[-1][1]/curve[0][1] - 1) * 100
    years = (until - since).days/365.25
    cagr = ((curve[-1][1]/curve[0][1]) ** (1/years) - 1) * 100
    sh = _sharpe_by_year(curve)
    mean_sh = statistics.fmean(sh.values()) if sh else 0.0
    return {
        "label": label, "strategy": strat_label, "window": window_label,
        "regime": regime_label, "threshold": threshold, "hard": hard_cutoff,
        "total_pct": total_pct, "cagr_pct": cagr,
        "mean_sharpe": mean_sh, "max_dd_pct": _max_drawdown(curve),
        "closed": r.closed_count, "elapsed_sec": round(time.time()-t0, 1),
    }


def main() -> int:
    global _VIX_VXV
    _VIX_VXV = _fetch_vix_vxv()

    # Quick stats on the VIX/VXV signal
    ratios = [v["vix"]/v["vxv"] for v in _VIX_VXV.values()]
    pct_inverted = sum(1 for r in ratios if r >= 1.0) / len(ratios) * 100
    print(f"  VIX/VXV stats: {len(ratios)} days, median {statistics.median(ratios):.3f}, "
          f"{pct_inverted:.1f}% inverted (>=1.0)", flush=True)

    print(f"\n{len(CONFIGS)} strategies x {len(REGIME_VARIANTS)} regime variants "
          f"x {len(WINDOWS)} windows = {len(CONFIGS)*len(REGIME_VARIANTS)*len(WINDOWS)} runs")
    print("=" * 70, flush=True)
    runs = []
    for strat_label, rank_fn_factory, _ in CONFIGS:
        for window_label, since, until in WINDOWS:
            for regime_label, threshold, hard in REGIME_VARIANTS:
                runs.append(run_one(strat_label, rank_fn_factory,
                                     window_label, since, until,
                                     regime_label, threshold, hard))

    # Report grouped by strategy + window
    print("\n" + "=" * 100)
    print("  VIX TERM-STRUCTURE REGIME FILTER  vs  base strategies")
    print("=" * 100)
    for strat_label in [c[0] for c in CONFIGS]:
        for window_label, _, _ in WINDOWS:
            b = BASELINES[strat_label][window_label]
            print(f"\n  [{strat_label}] {window_label.upper()}")
            print(f"  {'config':<32} {'CAGR':>8} {'Sharpe':>8} {'maxDD':>9} "
                  f"{'d_cagr':>8} {'d_dd':>8} {'d_sharpe':>10}")
            print("  " + "-" * 80)
            print(f"  {'baseline (no overlay)':<32} {b['cagr']:>+7.2f}% "
                  f"{b['sharpe']:>+7.3f} {b['max_dd']:>+8.2f}%   (reference)")
            for r in runs:
                if r["strategy"] != strat_label or r["window"] != window_label:
                    continue
                d_c = r["cagr_pct"] - b["cagr"]
                d_d = r["max_dd_pct"] - b["max_dd"]
                d_s = r["mean_sharpe"] - b["sharpe"]
                print(f"  {r['label']:<32} {r['cagr_pct']:>+7.2f}% "
                      f"{r['mean_sharpe']:>+7.3f} {r['max_dd_pct']:>+8.2f}%  "
                      f"{d_c:>+7.2f}pp {d_d:>+7.2f}pp {d_s:>+9.3f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
