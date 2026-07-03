"""Transaction-cost sensitivity sweep for mom_v2 baseline.

Current default: HALF_SPREAD_BPS=5.0 (10bp round-trip). Realistic for
the small-mid cap universe mom_v2 trades is probably 15-25bps half-spread
(30-50bp round-trip). This sweep quantifies the strategy's TC fragility.

Sweep: half_spread in {5, 10, 15, 20, 30} x {in_sample, holdout}.
10 runs, ~7 min.
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum

OUT_PATH = Path("var/data_audit/tc_sensitivity.json")
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
TC_LEVELS = [5.0, 10.0, 15.0, 20.0, 30.0]


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


def run_one(window_label, since, until, half_bps):
    factor_backtest.HALF_SPREAD_BPS = half_bps
    t0 = time.time()
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N, starting_cash=100_000.0,
        rank_fn=momentum.rank_universe, rebalance_freq="M",
    )
    curve = r.equity_curve
    total_pct = (curve[-1][1]/curve[0][1] - 1) * 100
    years = (until - since).days/365.25
    cagr = ((curve[-1][1]/curve[0][1]) ** (1/years) - 1) * 100
    sh = _sharpe_by_year(curve)
    mean_sh = statistics.fmean(sh.values()) if sh else 0.0
    return {
        "window": window_label, "half_bps": half_bps,
        "total_pct": total_pct, "cagr_pct": cagr,
        "mean_sharpe": mean_sh, "max_dd_pct": _max_drawdown(curve),
        "closed": r.closed_count, "elapsed_sec": round(time.time()-t0,1),
    }


def main() -> int:
    print(f"TC SENSITIVITY: {len(TC_LEVELS)} half-spread levels x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)
    runs = []
    for window_label, since, until in WINDOWS:
        for bps in TC_LEVELS:
            print(f"  >>> {window_label} half_bps={bps}", flush=True)
            runs.append(run_one(window_label, since, until, bps))

    print("\n" + "=" * 80)
    print("  TC SENSITIVITY (mom_v2 baseline)")
    print("=" * 80)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        print(f"  {'half_bps':>9} {'roundtrip':>10} {'total %':>10} {'CAGR %':>9} "
              f"{'mean Shrp':>10} {'max DD':>9}")
        print("  " + "-" * 65)
        for r in runs:
            if r["window"] != window_label: continue
            print(f"  {r['half_bps']:>8.0f}  {r['half_bps']*2:>9.0f}bp  "
                  f"{r['total_pct']:>+9.2f}% {r['cagr_pct']:>+8.2f}% "
                  f"{r['mean_sharpe']:>+10.3f} {r['max_dd_pct']:>+8.2f}%")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
