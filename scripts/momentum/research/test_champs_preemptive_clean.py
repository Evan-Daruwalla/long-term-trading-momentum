"""Experiment A (prereg 2026-07-14): preemptive risk overlays on the two CHAMPION
sleeves, post-backfill CLEAN data.

Re-tests the trend-filter / vol-target overlay family (which FAILED on mom_v2
pre-backfill — record Appendices B/G/R) against mom_roa_6535 and
residual_roa_6535 on the clean cache. Same four configs as
test_mom_v2_preemptive.py for apples-to-apples; baselines = the 2026-06-13
clean revalidation (var/data_audit/revalidate_2026-06-13.json).

Pre-registered deployment-candidate rule (docs/prereg_2026-07-14_champs_tweaks.md,
ALL must hold): holdout maxDD >= +5pp better; holdout CAGR >= baseline-3pp;
in_sample CAGR >= baseline-2pp; Sharpe not worse on both windows.

SEQUENTIAL by construction — one process, one factor_backtest at a time.

Usage: .venv\\Scripts\\python.exe -m scripts.momentum.research.test_champs_preemptive_clean
Output: var/momentum/champs_preemptive_clean.json
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import mom_roa_zscore, residual_momentum, roa, zcombo
from scripts.momentum.research.test_mom_v2_preemptive import (
    make_trend_filtered_ranker, make_vol_target_scaler,
    _sharpe_by_year, _max_drawdown,
)

OUT_PATH = Path("var/momentum/champs_preemptive_clean.json")
BASELINE_PATH = Path("var/data_audit/revalidate_2026-06-13.json")
STARTING_CASH = 100_000.0
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]


def _mom_roa_rank():
    return mom_roa_zscore.make_rank_fn(0.65, 0.35)


def _residual_rank():
    return zcombo.make_rank_fn([
        (residual_momentum.residual_momentum_score, 0.65),
        (roa.roa_score, 0.35),
    ])


STRATEGIES = [
    ("mom_roa_6535", _mom_roa_rank),
    ("residual_roa_6535", _residual_rank),
]

# (name, overlay_factory(base_rank_fn) -> run_factor_backtest kwargs)
CONFIGS = [
    ("trend200",      lambda base: dict(rank_fn=make_trend_filtered_ranker(base, 200))),
    ("voltgt16",      lambda base: dict(rank_fn=base,
                                        position_scale_fn=make_vol_target_scaler(0.16))),
    ("voltgt20",      lambda base: dict(rank_fn=base,
                                        position_scale_fn=make_vol_target_scaler(0.20))),
    ("trend200_vt16", lambda base: dict(rank_fn=make_trend_filtered_ranker(base, 200),
                                        position_scale_fn=make_vol_target_scaler(0.16))),
]


def load_baselines() -> dict:
    """{(strategy, window): {cagr, dd, sharpe}} from the 06-13 clean revalidation."""
    data = json.loads(BASELINE_PATH.read_text())
    out = {}
    for r in data["runs"]:
        if "error" in r:
            continue
        out[(r["strategy"], r["window"])] = {
            "cagr": r["cagr_pct"], "dd": r["max_dd_pct"], "sharpe": r["mean_sharpe"],
        }
    return out


def run_one(strategy: str, rank_factory, cfg_name: str, cfg_factory,
            window_label: str, since: date, until: date) -> dict:
    label = f"{strategy}_{cfg_name}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    kw = cfg_factory(rank_factory())
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N, starting_cash=STARTING_CASH,
        rebalance_freq="M",
        **kw,
    )
    curve = r.equity_curve
    years = (until - since).days / 365.25
    cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
    sh = _sharpe_by_year(curve)
    out = {
        "strategy": strategy, "config": cfg_name, "window": window_label,
        "total_pct": round((curve[-1][1] / curve[0][1] - 1) * 100, 4),
        "cagr_pct": round(cagr, 4),
        "mean_sharpe": round(statistics.fmean(sh.values()) if sh else 0.0, 4),
        "max_dd_pct": round(_max_drawdown(curve), 4),
        "closed": r.closed_count,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    print(f"      CAGR {out['cagr_pct']:+.2f}%  Sharpe {out['mean_sharpe']:+.3f}  "
          f"maxDD {out['max_dd_pct']:+.1f}%  ({out['elapsed_sec']}s)", flush=True)
    return out


def main() -> int:
    base = load_baselines()
    print(f"CHAMPS + PREEMPTIVE OVERLAYS (clean data): "
          f"{len(STRATEGIES)} strategies x {len(CONFIGS)} configs x {len(WINDOWS)} windows")
    print("=" * 74, flush=True)
    runs: list[dict] = []
    for strategy, rank_factory in STRATEGIES:
        for cfg_name, cfg_factory in CONFIGS:
            for window_label, since, until in WINDOWS:
                runs.append(run_one(strategy, rank_factory, cfg_name, cfg_factory,
                                    window_label, since, until))

    # Report + pre-registered verdicts.
    print("\n" + "=" * 96)
    print("  RESULTS vs 2026-06-13 CLEAN baselines (docs/prereg_2026-07-14_champs_tweaks.md)")
    print("=" * 96)
    candidates = []
    for strategy, _ in STRATEGIES:
        for window_label, _s, _u in WINDOWS:
            b = base[(strategy, window_label)]
            print(f"\n  {strategy} / {window_label}   "
                  f"baseline: CAGR {b['cagr']:+.2f}%  Shrp {b['sharpe']:+.3f}  DD {b['dd']:+.1f}%")
            print(f"  {'config':<16} {'CAGR %':>9} {'d_cagr':>9} {'Sharpe':>8} {'maxDD %':>9} {'d_dd':>8}")
            print("  " + "-" * 64)
            for r in runs:
                if r["strategy"] != strategy or r["window"] != window_label:
                    continue
                print(f"  {r['config']:<16} {r['cagr_pct']:>+8.2f}% "
                      f"{r['cagr_pct']-b['cagr']:>+8.2f}p {r['mean_sharpe']:>+8.3f} "
                      f"{r['max_dd_pct']:>+8.2f}% {r['max_dd_pct']-b['dd']:>+7.2f}p")
    for strategy, _ in STRATEGIES:
        for cfg_name, _f in CONFIGS:
            hi = next(r for r in runs if r["strategy"] == strategy
                      and r["config"] == cfg_name and r["window"] == "in_sample")
            ho = next(r for r in runs if r["strategy"] == strategy
                      and r["config"] == cfg_name and r["window"] == "holdout")
            bi, bo = base[(strategy, "in_sample")], base[(strategy, "holdout")]
            ok = (ho["max_dd_pct"] >= bo["dd"] + 5.0
                  and ho["cagr_pct"] >= bo["cagr"] - 3.0
                  and hi["cagr_pct"] >= bi["cagr"] - 2.0
                  and ho["mean_sharpe"] >= bo["sharpe"]
                  and hi["mean_sharpe"] >= bi["sharpe"])
            if ok:
                candidates.append(f"{strategy}+{cfg_name}")
    print("\n  PRE-REGISTERED VERDICT (overlay deployment candidates): "
          + (", ".join(candidates) if candidates else "NONE"))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(
        {"runs": runs, "baselines_used": {f"{k[0]}/{k[1]}": v for k, v in base.items()},
         "candidates": candidates}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
