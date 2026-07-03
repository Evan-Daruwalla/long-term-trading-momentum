"""Test mom_v2 with daily stop-loss between rebalances.

Question: does adding a -X% intra-rebalance stop preserve mom_v2's CAGR
while reducing the -33.9% held-out max drawdown noted in the dashboard's
v2_holdout equity curve (Feb-Mar 2025 and Nov 2024-Apr 2025 events)?

Sweep stop_pct in {-0.10, -0.15, -0.20, -0.25} × {in_sample, holdout}.
Tighter stops fire more often (higher TC drag, more cash-idle time
between rebalances) but cap drawdowns harder.

Success criteria:
  - In-sample CAGR within 2 pp of baseline +21%/yr
  - Held-out max drawdown < -25% (improves on -33.9%)
  - Held-out CAGR >= +20%/yr (preserves most upside)

8 backtests sequential (~2 min total with warm cache).
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum

OUT_PATH = Path("var/momentum/mom_v2_stops_test.json")
STARTING_CASH = 100_000.0
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
STOP_LEVELS = [-0.10, -0.15, -0.20, -0.25]

MOM_V2 = {  # POST-AUDIT (2026-05-28) clean-data baselines
    "in_sample": {"cagr": 2.72, "total": 27.28, "max_dd": -55.26},
    "holdout":   {"cagr": 28.81, "total": 80.37, "max_dd": -33.86},
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


def run_one(window_label: str, since: date, until: date, stop_pct: float) -> dict:
    label = f"mom_v2_stop{abs(int(stop_pct*100))}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N, starting_cash=STARTING_CASH,
        rank_fn=momentum.rank_universe,
        rebalance_freq="M",
        stop_loss_pct=stop_pct,
    )
    curve = r.equity_curve
    years = (until - since).days / 365.25
    total_pct = (curve[-1][1] / curve[0][1] - 1) * 100
    cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
    sh = _sharpe_by_year(curve)
    max_dd = _max_drawdown(curve)
    return {
        "label":         label,
        "window":        window_label,
        "stop_pct":      stop_pct,
        "total_pnl_pct": total_pct,
        "cagr_pct":      cagr,
        "mean_sharpe":   statistics.fmean(sh.values()) if sh else 0.0,
        "max_dd_pct":    max_dd,
        "closed":        r.closed_count,
        "open":          r.open_count,
        "elapsed_sec":   round(time.time() - t0, 1),
    }


def main() -> int:
    print(f"MOM_V2 WITH STOP-LOSS: {len(STOP_LEVELS)} levels x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)
    runs: list[dict] = []
    for window_label, since, until in WINDOWS:
        for stop_pct in STOP_LEVELS:
            runs.append(run_one(window_label, since, until, stop_pct))

    print("\n" + "=" * 80)
    print("  MOM_V2 + STOP-LOSS vs baseline (no stops)")
    print("=" * 80)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        print(f"  {'config':<26} {'total %':>10} {'CAGR %':>9} {'mean Shrp':>10} "
              f"{'max DD':>8}")
        print("  " + "-" * 70)
        v2 = MOM_V2[window_label]
        print(f"  {'mom_v2 (no stop)':<26} {v2['total']:>+9.2f}% "
              f"{v2['cagr']:>+8.2f}%   (baseline)  {v2['max_dd']:>+7.1f}%")
        for r in runs:
            if r["window"] != window_label:
                continue
            d_cagr = r["cagr_pct"] - v2["cagr"]
            d_dd = r["max_dd_pct"] - v2["max_dd"]
            print(f"  {r['label']:<26} {r['total_pnl_pct']:>+9.2f}% "
                  f"{r['cagr_pct']:>+8.2f}% {r['mean_sharpe']:>+10.3f} "
                  f"{r['max_dd_pct']:>+7.2f}%   d_cagr={d_cagr:+.1f}pp  d_dd={d_dd:+.1f}pp")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
