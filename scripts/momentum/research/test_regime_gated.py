"""Test the regime-gated factor: switches between mom_v2 and mom_then_accruals
based on SPY-vs-RSP 6-month relative performance.

2 backtests (in-sample + held-out) at top-50, $100K, monthly — matching
mom_v2 spec exactly so results are directly comparable.

Success criteria (per regime_gated.py docstring):
  - In-sample CAGR ≥ +21%/yr (mom_v2 baseline) — must NOT regress
  - Held-out CAGR > +26.5%/yr (mom_v2 baseline) — should capture mega-cap alpha
  - Both windows ≥ baseline = real regime-conditional alpha
  - Only held-out ≥ baseline = overfit to 2024-26, not deployable
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import regime_gated

OUT_PATH = Path("var/momentum/regime_gated_test.json")
STARTING_CASH = 100_000.0
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]

MOM_V2 = {
    "in_sample": {"cagr": 21.00, "sharpe": 0.230, "total": 455.6},
    "holdout":   {"cagr": 26.47, "sharpe": 0.868, "total":  72.8},
}


def _sharpe_by_year(curve, risk_free_apy=0.045):
    by_year: dict[str, list[float]] = {}
    prev_val = prev_year = None
    for iso, val in curve:
        y = iso[:4]
        if prev_val and prev_val > 0 and y == prev_year:
            by_year.setdefault(y, []).append(val / prev_val - 1.0)
        prev_val, prev_year = val, y
    out = {}
    rf = risk_free_apy / 252.0
    for y, rets in by_year.items():
        if len(rets) < 20:
            continue
        sd = statistics.pstdev(rets)
        out[y] = ((statistics.fmean(rets) - rf) / sd) * (252 ** 0.5) if sd > 0 else 0.0
    return out


def _max_drawdown(curve):
    peak = curve[0][1]
    max_dd = 0.0
    for _, val in curve:
        if val > peak:
            peak = val
        dd = (val / peak - 1.0) * 100
        if dd < max_dd:
            max_dd = dd
    return max_dd


def run_one(window_label: str, since: date, until: date) -> dict:
    print(f"  >>> regime_gated_{window_label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N, starting_cash=STARTING_CASH,
        rank_fn=regime_gated.rank_universe,
        rebalance_freq="M",
    )
    curve = r.equity_curve
    years = (until - since).days / 365.25
    total_pct = (curve[-1][1] / curve[0][1] - 1) * 100
    cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
    sh = _sharpe_by_year(curve)
    max_dd = _max_drawdown(curve)
    return {
        "label":         f"regime_gated_{window_label}",
        "window":        window_label,
        "total_pnl_pct": total_pct,
        "cagr_pct":      cagr,
        "mean_sharpe":   statistics.fmean(sh.values()) if sh else 0.0,
        "yearly_sharpe": {y: round(s, 3) for y, s in sh.items()},
        "max_dd_pct":    max_dd,
        "closed":        r.closed_count,
        "open":          r.open_count,
        "elapsed_sec":   round(time.time() - t0, 1),
    }


def main() -> int:
    print("REGIME-GATED FACTOR (mom_v2 / mom_then_accruals on SPY-vs-RSP gate)")
    print("=" * 70, flush=True)
    runs: list[dict] = []
    for window_label, since, until in WINDOWS:
        runs.append(run_one(window_label, since, until))

    print("\n" + "=" * 80)
    print("  REGIME-GATED vs mom_v2 baseline")
    print("=" * 80)
    for window_label, since, until in WINDOWS:
        years = (until - since).days / 365.25
        print(f"\n  {window_label.upper()}  ({since} -> {until}, {years:.1f} yrs)")
        print(f"  {'config':<24} {'total %':>10} {'CAGR %':>9} {'mean Shrp':>10} {'max DD':>8}")
        print("  " + "-" * 70)
        for r in runs:
            if r["window"] != window_label:
                continue
            v2 = MOM_V2[window_label]
            delta = r["cagr_pct"] - v2["cagr"]
            print(f"  {r['label']:<24} {r['total_pnl_pct']:>+9.2f}% "
                  f"{r['cagr_pct']:>+8.2f}% {r['mean_sharpe']:>+10.3f} "
                  f"{r['max_dd_pct']:>+7.2f}%   delta_cagr={delta:+.2f}pp")
        v2 = MOM_V2[window_label]
        print(f"  {'mom_v2 (baseline)':<24} {v2['total']:>+9.2f}% "
              f"{v2['cagr']:>+8.2f}% {v2['sharpe']:>+10.3f}     (n/a)")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
