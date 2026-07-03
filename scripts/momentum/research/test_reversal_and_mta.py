"""Combined test: reversal standalone + mom_then_accruals combination.

Runs 4 backtests sequentially (no parallel DB collisions):
  1. reversal-21d top-50 in-sample
  2. reversal-21d top-50 held-out
  3. mom_then_accruals top-50 in-sample
  4. mom_then_accruals top-50 held-out

Comparison points: mom_v2 (in-sample +21.0%, held-out +26.5%), SPY benchmarks.

Reversal hypothesis: anti-correlated to mom by construction, might be a real
short-term effect even with monthly rebal drag.

mom_then_accruals hypothesis: filter mom-top-100 by accruals (keep profitable
strong-cashflow names), might preserve mom's edge while reducing junk-mom
drawdowns.

Both predicted likely to fail (long-only reversal hurt by falling-knife risk;
mom_then_accruals fundamentally same pattern as mom_quality_screen).
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import reversal, mom_then_accruals

OUT_PATH = Path("var/momentum/reversal_and_mta_test.json")
STARTING_CASH = 100_000.0
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]

FACTORS = [
    ("reversal_21d", reversal.rank_universe),
    ("mom_then_accruals", mom_then_accruals.rank_universe),
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


def run_one(factor_label: str, rank_fn, window_label: str, since: date, until: date) -> dict:
    label = f"{factor_label}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N, starting_cash=STARTING_CASH,
        rank_fn=rank_fn, rebalance_freq="M",
    )
    curve = r.equity_curve
    years = (until - since).days / 365.25
    total_pct = (curve[-1][1] / curve[0][1] - 1) * 100
    cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
    sh = _sharpe_by_year(curve)
    max_dd = _max_drawdown(curve)
    return {
        "label":         label,
        "factor":        factor_label,
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
    print("REVERSAL + MOM_THEN_ACCRUALS — 4 backtests, sequential")
    print("=" * 70, flush=True)
    runs: list[dict] = []
    for factor_label, rank_fn in FACTORS:
        for window_label, since, until in WINDOWS:
            runs.append(run_one(factor_label, rank_fn, window_label, since, until))

    print("\n" + "=" * 80)
    print("  RESULTS vs mom_v2 baseline")
    print("=" * 80)
    for window_label, since, until in WINDOWS:
        years = (until - since).days / 365.25
        print(f"\n  {window_label.upper()}  ({since} -> {until}, {years:.1f} yrs)")
        print(f"  {'config':<28} {'total %':>10} {'CAGR %':>9} {'mean Shrp':>10} "
              f"{'max DD':>8}")
        print("  " + "-" * 70)
        for r in runs:
            if r["window"] != window_label:
                continue
            print(f"  {r['label']:<28} {r['total_pnl_pct']:>+9.2f}% "
                  f"{r['cagr_pct']:>+8.2f}% {r['mean_sharpe']:>+10.3f} "
                  f"{r['max_dd_pct']:>+7.2f}%")
        v2 = MOM_V2[window_label]
        print(f"  {'mom_v2 (baseline)':<28} {v2['total']:>+9.2f}% "
              f"{v2['cagr']:>+8.2f}% {v2['sharpe']:>+10.3f}     (n/a)")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
