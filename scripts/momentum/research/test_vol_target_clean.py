"""Vol-target sweep on CLEAN data (post 2026-05-28 audit).

Phase 4 of audit. Previous vol-target test (test_mom_v2_preemptive.py)
ran on contaminated data; results were polluted by spike artifacts.
This re-runs vol-target with cleaned data + max_hist_ratio universe filter.

Sweep: target_vol in {12%, 14%, 16%, 18%, 20%, 22%, 25%} x 2 windows.
14 runs, ~5 min.

Hypothesis from prior tests: vol-target preserves CAGR while improving
Sharpe by scaling positions down BEFORE realized vol spikes. Target ~20%
(close to mom's natural vol) only kicks in during real crises. Target ~12%
kicks in continuously, costing CAGR.

Success criteria:
  - Some target in {12-25} produces better Sharpe than baseline on BOTH windows
  - Without large CAGR regression (<= -2pp)
"""
from __future__ import annotations

import json
import math
import statistics
import time
from datetime import date
from functools import lru_cache
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum
from trading_bot.factors.universe import close_at_offset

OUT_PATH = Path("var/data_audit/vol_target_clean.json")
STARTING_CASH = 100_000.0
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
TARGETS = [0.12, 0.14, 0.16, 0.18, 0.20, 0.22, 0.25]

# Baseline (post-cleanup, with universe filter) for diff columns
BASELINE = {
    "in_sample": {"cagr": 2.72, "max_dd": -55.26, "sharpe": 0.167},
    "holdout":   {"cagr": 28.81, "max_dd": -33.86, "sharpe": 0.903},
}


@lru_cache(maxsize=8192)
def _spy_close(as_of_iso: str, offset: int) -> float | None:
    return close_at_offset("SPY", date.fromisoformat(as_of_iso), offset)


def _spy_realized_vol(as_of: date, lookback: int = 21) -> float | None:
    iso = as_of.isoformat()
    closes = []
    for i in range(lookback + 1):
        c = _spy_close(iso, -i)
        if c is None: return None
        closes.append(c)
    closes.reverse()
    rets = [closes[i+1]/closes[i] - 1.0 for i in range(len(closes)-1)]
    if len(rets) < 5: return None
    sd = statistics.pstdev(rets)
    return sd * math.sqrt(252)


def make_vol_target_scaler(target_vol: float):
    def scaler(as_of: date) -> float:
        rv = _spy_realized_vol(as_of)
        if rv is None or rv <= 0:
            return 1.0
        return min(1.0, target_vol / rv)
    return scaler


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


def run_one(window_label, since, until, target_vol):
    label = f"voltgt{int(target_vol*100)}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N, starting_cash=STARTING_CASH,
        rank_fn=momentum.rank_universe, rebalance_freq="M",
        position_scale_fn=make_vol_target_scaler(target_vol),
    )
    curve = r.equity_curve
    total_pct = (curve[-1][1]/curve[0][1] - 1) * 100
    years = (until - since).days/365.25
    cagr = ((curve[-1][1]/curve[0][1]) ** (1/years) - 1) * 100
    sh = _sharpe_by_year(curve)
    mean_sh = statistics.fmean(sh.values()) if sh else 0.0
    return {
        "label": label, "window": window_label, "target_vol": target_vol,
        "total_pct": total_pct, "cagr_pct": cagr,
        "mean_sharpe": mean_sh, "max_dd_pct": _max_drawdown(curve),
        "closed": r.closed_count, "elapsed_sec": round(time.time()-t0,1),
    }


def main() -> int:
    print(f"VOL-TARGET CLEAN-DATA SWEEP: {len(TARGETS)} targets x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)
    runs = []
    for window_label, since, until in WINDOWS:
        for tv in TARGETS:
            runs.append(run_one(window_label, since, until, tv))

    print("\n" + "=" * 92)
    print("  VOL-TARGET (clean data) vs baseline mom_v2")
    print("=" * 92)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        b = BASELINE[window_label]
        print(f"  {'config':<22} {'CAGR %':>9} {'max DD':>9} {'mean Shrp':>10}  "
              f"{'d_cagr':>8} {'d_dd':>8} {'d_sharpe':>10}")
        print("  " + "-" * 85)
        print(f"  {'baseline (no overlay)':<22} {b['cagr']:>+8.2f}% {b['max_dd']:>+8.2f}% {b['sharpe']:>+10.3f}    (reference)")
        for r in runs:
            if r["window"] != window_label: continue
            d_c = r["cagr_pct"] - b["cagr"]
            d_d = r["max_dd_pct"] - b["max_dd"]
            d_s = r["mean_sharpe"] - b["sharpe"]
            print(f"  {r['label']:<22} {r['cagr_pct']:>+8.2f}% {r['max_dd_pct']:>+8.2f}% "
                  f"{r['mean_sharpe']:>+10.3f}  {d_c:>+7.1f}pp {d_d:>+7.1f}pp {d_s:>+9.3f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
