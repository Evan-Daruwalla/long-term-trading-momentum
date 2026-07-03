"""Rerun mom_v2 in-sample after spike cleanup and report clean max DD."""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum


def _max_drawdown(curve):
    peak = curve[0][1]
    max_dd = 0.0
    trough_iso = peak_iso = None
    cur_peak_iso = curve[0][0]
    for iso, val in curve:
        if val > peak:
            peak, cur_peak_iso = val, iso
        dd = (val/peak - 1.0) * 100
        if dd < max_dd:
            max_dd, trough_iso, peak_iso = dd, iso, cur_peak_iso
    return max_dd, peak_iso, trough_iso


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
        out[y] = ((statistics.fmean(rets)-rf)/sd) * (252**0.5) if sd > 0 else 0.0
    return out


WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]


def main() -> int:
    all_results = {}
    factor_backtest.HALF_SPREAD_BPS = 5.0
    for window_label, since, until in WINDOWS:
        print(f"\nRe-running mom_v2 {window_label} post-spike-cleanup...")
        t0 = time.time()
        r = factor_backtest.run_factor_backtest(
            since=since, until=until,
            top_n=50, starting_cash=100_000.0,
            rank_fn=momentum.rank_universe,
            rebalance_freq="M",
        )
        elapsed = time.time() - t0
        curve = r.equity_curve
        total_pct = (curve[-1][1]/curve[0][1] - 1) * 100
        years = (until - since).days/365.25
        cagr = ((curve[-1][1]/curve[0][1]) ** (1/years) - 1) * 100
        max_dd, peak_d, trough_d = _max_drawdown(curve)
        sh = _sharpe_by_year(curve)
        mean_sh = statistics.fmean(sh.values()) if sh else 0.0

        print(f"\nBASELINE mom_v2 {window_label} (POST-CLEANUP):")
        print(f"  total return: {total_pct:+.2f}%")
        print(f"  CAGR:         {cagr:+.2f}%/yr")
        print(f"  max DD:       {max_dd:.2f}% (peak {peak_d}, trough {trough_d})")
        print(f"  mean Sharpe:  {mean_sh:+.3f}")
        print(f"  closed trades: {r.closed_count}")
        print(f"  elapsed:      {elapsed:.0f}s")

        all_results[window_label] = {
            "total_pct": total_pct, "cagr_pct": cagr,
            "max_dd_pct": max_dd, "peak": peak_d, "trough": trough_d,
            "mean_sharpe": mean_sh, "yearly_sharpe": sh,
            "closed": r.closed_count, "elapsed_sec": elapsed,
            "equity_curve": curve,
        }

    print(f"\n=== SUMMARY: PRE vs POST CLEANUP ===")
    print(f"in_sample: PRE +455%/+21%CAGR  ->  POST {all_results['in_sample']['total_pct']:+.1f}%/{all_results['in_sample']['cagr_pct']:+.2f}%CAGR")
    print(f"holdout:   PRE  +76%/+27%CAGR  ->  POST {all_results['holdout']['total_pct']:+.1f}%/{all_results['holdout']['cagr_pct']:+.2f}%CAGR")

    Path("var/data_audit").mkdir(parents=True, exist_ok=True)
    Path("var/data_audit/mom_v2_post_cleanup.json").write_text(
        json.dumps(all_results, indent=2))
    print(f"\nWritten -> var/data_audit/mom_v2_post_cleanup.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
