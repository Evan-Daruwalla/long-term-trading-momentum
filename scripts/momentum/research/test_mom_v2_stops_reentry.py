"""Test mom_v2 with stop-loss + same-name re-entry on rebound (Option C).

Building on test_mom_v2_stops.py which showed plain stops were catastrophic
in-sample (max DD -36% -> -87% from 2020-03 momentum-crash whipsaw).
Option C re-enters the SAME ticker once its close recovers to
stop_fill * (1 + reentry_buffer), capping idle-cash drag during V-rebounds.

Sweep stop_pct=-0.15 (best held-out from prior sweep) x reentry_buffer
{0.0, 0.02, 0.05} x {in_sample, holdout}.

Expected: in-sample DD better than plain stops (-87%) and possibly better
than no-stop (-36%) because each stopped name caps its drawdown at one
round-trip. CAGR likely slightly below baseline +21% due to choppy-market
whipsaw. Held-out should be in the ballpark of plain stop15 (+28.79% CAGR,
-30.7% DD) - probably similar.

6 backtests sequential (~2 min total).
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum

OUT_PATH = Path("var/momentum/mom_v2_stops_reentry_test.json")
STARTING_CASH = 100_000.0
TOP_N = 50
STOP_PCT = -0.15

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
REENTRY_BUFFERS = [0.00, 0.02, 0.05]

# Baseline references for diff columns — POST-AUDIT (2026-05-28) clean
MOM_V2 = {
    "in_sample": {"cagr": 2.72, "max_dd": -55.26},
    "holdout":   {"cagr": 28.81, "max_dd": -33.86},
}
# stop15 (no reentry) — will be re-computed by stops sweep after audit;
# values below are placeholders that get overwritten in the printed comparison
# table only if both stops + reentry sweeps run sequentially. Updated 2026-05-28
# AFTER stops sweep rerun completed. Pre-audit values: in-sample +17.01/-87.08,
# holdout +28.79/-30.72.
STOP15 = {
    "in_sample": {"cagr": None, "max_dd": None},  # to be filled from rerun
    "holdout":   {"cagr": None, "max_dd": None},
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


def run_one(window_label: str, since: date, until: date, buf: float) -> dict:
    label = f"mom_v2_stop15_buf{int(buf*100):02d}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N, starting_cash=STARTING_CASH,
        rank_fn=momentum.rank_universe,
        rebalance_freq="M",
        stop_loss_pct=STOP_PCT,
        reentry_buffer=buf,
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
        "reentry_buf":   buf,
        "total_pnl_pct": total_pct,
        "cagr_pct":      cagr,
        "mean_sharpe":   statistics.fmean(sh.values()) if sh else 0.0,
        "max_dd_pct":    max_dd,
        "closed":        r.closed_count,
        "open":          r.open_count,
        "elapsed_sec":   round(time.time() - t0, 1),
    }


def main() -> int:
    print(f"MOM_V2 + STOP{int(STOP_PCT*100)}% + REENTRY: "
          f"{len(REENTRY_BUFFERS)} buffers x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)
    runs: list[dict] = []
    for window_label, since, until in WINDOWS:
        for buf in REENTRY_BUFFERS:
            runs.append(run_one(window_label, since, until, buf))

    print("\n" + "=" * 90)
    print("  MOM_V2 + STOP-LOSS + RE-ENTRY  vs  baseline (no stop)")
    print("=" * 90)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        print(f"  {'config':<32} {'total %':>10} {'CAGR %':>9} {'mean Shrp':>10} "
              f"{'max DD':>9}")
        print("  " + "-" * 80)
        v2 = MOM_V2[window_label]
        print(f"  {'mom_v2 (no stop)':<32} {'':>10} {v2['cagr']:>+8.2f}%   "
              f"(baseline)  {v2['max_dd']:>+8.1f}%")
        for r in runs:
            if r["window"] != window_label:
                continue
            d_cagr_vs_base = r["cagr_pct"] - v2["cagr"]
            d_dd_vs_base = r["max_dd_pct"] - v2["max_dd"]
            print(f"  {r['label']:<32} {r['total_pnl_pct']:>+9.2f}% "
                  f"{r['cagr_pct']:>+8.2f}% {r['mean_sharpe']:>+10.3f} "
                  f"{r['max_dd_pct']:>+8.2f}%   "
                  f"vs_base d_cagr={d_cagr_vs_base:+.1f}pp d_dd={d_dd_vs_base:+.1f}pp")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
