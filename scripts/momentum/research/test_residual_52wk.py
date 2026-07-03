"""Candidate #3 from docs/research_2026-06-09_algo_candidates.md:
residual (idiosyncratic) momentum + 52-week-high momentum.

Tests whether an alternative CONSTRUCTION of the momentum signal beats the
current champion mom_roa_6535 — specifically whether it cuts the in-sample
momentum-crash drawdown (-44% for mom_roa, -55% for mom_v2) while keeping
held-out CAGR.

Configs (6) x windows (2) = 12 backtests:
  - mom_v2          (reference, top-50 total-return momentum)
  - mom_roa_6535    (CHAMPION reference, must be beaten on BOTH windows)
  - residual_solo   (residual momentum alone, top-50)
  - high52w_solo    (52-week-high alone, top-50)
  - residual_roa_6535  (residual mom 65% + ROA 35%, Z-combo)
  - high52w_roa_6535   (52wk-high 65% + ROA 35%, Z-combo)

References are re-run LIVE (not read from docstrings) so the comparison is on
current post-BKGM-fix data.

Success bar (project rule): beat mom_roa_6535 on BOTH windows on CAGR AND
mean-yearly Sharpe, OR clearly cut in-sample DD with no held-out CAGR loss.
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import (
    momentum, roa, mom_roa_zscore, residual_momentum, high_52w, zcombo,
)

OUT_PATH = Path("var/data_audit/residual_52wk_sweep.json")
STARTING_CASH = 100_000.0
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]

CONFIGS = [
    ("mom_v2",            lambda: momentum.rank_universe),
    ("mom_roa_6535",      lambda: mom_roa_zscore.make_rank_fn(0.65, 0.35)),
    ("residual_solo",     lambda: residual_momentum.rank_universe),
    ("high52w_solo",      lambda: high_52w.rank_universe),
    ("residual_roa_6535", lambda: zcombo.make_rank_fn(
        [(residual_momentum.residual_momentum_score, 0.65), (roa.roa_score, 0.35)])),
    ("high52w_roa_6535",  lambda: zcombo.make_rank_fn(
        [(high_52w.high_52w_score, 0.65), (roa.roa_score, 0.35)])),
]


def _max_drawdown(curve):
    peak = curve[0][1]
    max_dd = 0.0
    for _, val in curve:
        if val > peak:
            peak = val
        if peak > 0:
            dd = (val / peak - 1.0) * 100
            if dd < max_dd:
                max_dd = dd
    return max_dd


def _sharpe_by_year(curve, risk_free_apy=0.045):
    by_year: dict[str, list[float]] = {}
    pv = py = None
    for iso, v in curve:
        y = iso[:4]
        if pv and pv > 0 and y == py:
            by_year.setdefault(y, []).append(v / pv - 1.0)
        pv, py = v, y
    out = {}
    rf = risk_free_apy / 252
    for y, rets in by_year.items():
        if len(rets) < 20:
            continue
        sd = statistics.pstdev(rets)
        if sd > 0:
            out[y] = ((statistics.fmean(rets) - rf) / sd) * (252 ** 0.5)
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
    cagr = ((curve[-1][1] / curve[0][1]) ** (365.25 / (until - since).days) - 1) * 100
    sh = _sharpe_by_year(curve)
    mean_sh = statistics.fmean(sh.values()) if sh else 0.0
    res = {
        "label": label, "window": window_label, "config": cfg_name,
        "cagr_pct": cagr, "mean_sharpe": mean_sh,
        "max_dd_pct": _max_drawdown(curve),
        "closed": r.closed_count, "elapsed_sec": round(time.time() - t0, 1),
    }
    print(f"      CAGR {cagr:+.2f}%  Sharpe {mean_sh:+.3f}  DD {res['max_dd_pct']:+.2f}%  "
          f"({res['elapsed_sec']}s)", flush=True)
    return res


def main() -> int:
    print(f"RESIDUAL + 52WK SWEEP: {len(CONFIGS)} configs x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)
    runs = []
    for window_label, since, until in WINDOWS:
        for cfg_name, cfg_factory in CONFIGS:
            runs.append(run_one(window_label, since, until, cfg_name, cfg_factory))

    print("\n" + "=" * 95)
    print("  RESIDUAL / 52WK MOMENTUM  vs  mom_roa_6535 champion (both run live)")
    print("=" * 95)
    for window_label, _, _ in WINDOWS:
        champ = next(r for r in runs
                     if r["window"] == window_label and r["config"] == "mom_roa_6535")
        print(f"\n  {window_label.upper()}  (champion mom_roa_6535: "
              f"{champ['cagr_pct']:+.2f}% / Sh {champ['mean_sharpe']:+.3f} / "
              f"DD {champ['max_dd_pct']:+.2f}%)")
        print(f"  {'config':<22} {'CAGR':>8} {'Sharpe':>8} {'maxDD':>9} "
              f"{'dCAGR':>8} {'dSharpe':>9} {'dDD':>8}")
        print("  " + "-" * 80)
        for r in runs:
            if r["window"] != window_label:
                continue
            dc = r["cagr_pct"] - champ["cagr_pct"]
            ds = r["mean_sharpe"] - champ["mean_sharpe"]
            dd = r["max_dd_pct"] - champ["max_dd_pct"]
            print(f"  {r['config']:<22} {r['cagr_pct']:>+7.2f}% {r['mean_sharpe']:>+7.3f} "
                  f"{r['max_dd_pct']:>+8.2f}% {dc:>+7.2f}pp {ds:>+8.3f} {dd:>+7.2f}pp")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
