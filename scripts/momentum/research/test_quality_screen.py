"""Test mom_quality_screen (final combination scheme).

Pattern: keep mom-top-200 intersected with quality_xbrl_v2 > median,
then take top-50 by momentum from that intersection. Different from
sleeves because capital stays 100% in momentum (no sleeve dilution).

Hypothesis: screen out junk-momentum names without sacrificing premium.
Reality (from smoke test): screen cuts 83% of mom picks; only 34 names
pass; the cuts include all the moonshots (BKGM +6567%, etc.).

Likely to underperform mom_v2 but worth running to close the question
definitively.
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import mom_quality_screen

OUT_PATH = Path("var/momentum/quality_screen_test.json")
STARTING_CASH = 100_000.0

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]


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


def main() -> int:
    runs = []
    for window_label, since, until in WINDOWS:
        print(f"\n>>> {window_label}  ({since} -> {until})", flush=True)
        t0 = time.time()
        factor_backtest.HALF_SPREAD_BPS = 5.0
        r = factor_backtest.run_factor_backtest(
            since=since, until=until,
            top_n=50, starting_cash=STARTING_CASH,
            rank_fn=mom_quality_screen.rank_universe,
            rebalance_freq="M",
        )
        curve = r.equity_curve
        years = (until - since).days / 365.25
        cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
        sh = _sharpe_by_year(curve)
        runs.append({
            "label":         window_label,
            "total_pnl_pct": (curve[-1][1] / curve[0][1] - 1) * 100,
            "cagr_pct":      cagr,
            "mean_sharpe":   statistics.fmean(sh.values()) if sh else 0.0,
            "closed":        r.closed_count,
            "open":          r.open_count,
            "elapsed_sec":   round(time.time() - t0, 1),
        })
        print(f"  tpnl={runs[-1]['total_pnl_pct']:+.2f}%  cagr={cagr:+.2f}%/yr  "
              f"shrp={runs[-1]['mean_sharpe']:+.3f}  closed={r.closed_count}")

    print("\n" + "=" * 70)
    print("  MOM_QUALITY_SCREEN vs mom_v2 BASELINE")
    print("=" * 70)
    print(f"  {'window':<12} {'mom_qscreen %':>14} {'mom_qscreen CAGR':>18} "
          f"{'mom_v2 CAGR':>14} {'delta':>10}")
    V2 = {"in_sample": 21.0, "holdout": 26.47}
    for r in runs:
        delta = r["cagr_pct"] - V2[r["label"]]
        print(f"  {r['label']:<12} {r['total_pnl_pct']:>+13.2f}%  "
              f"{r['cagr_pct']:>+16.2f}%  {V2[r['label']]:>+13.2f}%  "
              f"{delta:>+9.2f}pp")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
