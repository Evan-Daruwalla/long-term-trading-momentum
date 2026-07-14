"""Experiment B (prereg 2026-07-14): weight / top-N sweep on the two CHAMPION
sleeves, post-backfill CLEAN data.

The original mom_roa weight sweep (which chose 65/35 from a 60-70%% broad peak)
ran PRE-backfill; this re-runs the grid on the clean cache to check whether the
peak MOVED. Grid per strategy: signal weight {80/20 .. 50/50 by 5} at top-50,
plus top-N {25, 75, 100} at 65/35. Baselines = 2026-06-13 clean revalidation.

Pre-registered replacement rule (docs/prereg_2026-07-14_champs_tweaks.md): the
frozen 65/35 top-50 stands unless a variant beats the clean baseline on BOTH
windows with holdout margin >= +5pp AND in_sample >= baseline. Sub-threshold
winners are reported as noise, not adopted.

SEQUENTIAL by construction — one process, one factor_backtest at a time.

Usage: .venv\\Scripts\\python.exe -m scripts.momentum.research.sweep_champs_weights_clean
Output: var/momentum/champs_weight_sweep_clean.json
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
    _sharpe_by_year, _max_drawdown,
)

OUT_PATH = Path("var/momentum/champs_weight_sweep_clean.json")
BASELINE_PATH = Path("var/data_audit/revalidate_2026-06-13.json")
STARTING_CASH = 100_000.0

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]

WEIGHTS = [0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50]   # signal weight (ROA = 1-w)
TOP_NS = [25, 75, 100]                                  # at 65/35; 50 covered above


def _mom_roa_rank(w: float):
    return mom_roa_zscore.make_rank_fn(w, round(1.0 - w, 2))


def _residual_rank(w: float):
    return zcombo.make_rank_fn([
        (residual_momentum.residual_momentum_score, w),
        (roa.roa_score, round(1.0 - w, 2)),
    ])


STRATEGIES = [
    ("mom_roa_6535", _mom_roa_rank),
    ("residual_roa_6535", _residual_rank),
]


def configs():
    """(config_label, weight, top_n) — 65/35@50 IS the baseline config, included
    as a self-check that the harness reproduces the 06-13 revalidation."""
    out = [(f"w{int(w*100)}{int(round((1-w)*100))}_n50", w, 50) for w in WEIGHTS]
    out += [(f"w6535_n{n}", 0.65, n) for n in TOP_NS]
    return out


def load_baselines() -> dict:
    data = json.loads(BASELINE_PATH.read_text())
    return {(r["strategy"], r["window"]): {"cagr": r["cagr_pct"], "dd": r["max_dd_pct"],
                                           "sharpe": r["mean_sharpe"]}
            for r in data["runs"] if "error" not in r}


def run_one(strategy: str, rank_factory, label: str, w: float, top_n: int,
            window_label: str, since: date, until: date) -> dict:
    print(f"  >>> {strategy}_{label}_{window_label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=top_n, starting_cash=STARTING_CASH,
        rank_fn=rank_factory(w),
        rebalance_freq="M",
    )
    curve = r.equity_curve
    years = (until - since).days / 365.25
    cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
    sh = _sharpe_by_year(curve)
    out = {
        "strategy": strategy, "config": label, "weight": w, "top_n": top_n,
        "window": window_label,
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
    cfgs = configs()
    print(f"CHAMPS WEIGHT/TOP-N SWEEP (clean data): "
          f"{len(STRATEGIES)} strategies x {len(cfgs)} configs x {len(WINDOWS)} windows")
    print("=" * 74, flush=True)
    runs: list[dict] = []
    for strategy, rank_factory in STRATEGIES:
        for label, w, top_n in cfgs:
            for window_label, since, until in WINDOWS:
                runs.append(run_one(strategy, rank_factory, label, w, top_n,
                                    window_label, since, until))

    print("\n" + "=" * 96)
    print("  SWEEP vs 2026-06-13 CLEAN baselines (docs/prereg_2026-07-14_champs_tweaks.md)")
    print("=" * 96)
    winners = []
    for strategy, _ in STRATEGIES:
        for window_label, _s, _u in WINDOWS:
            b = base[(strategy, window_label)]
            print(f"\n  {strategy} / {window_label}   "
                  f"baseline(65/35@50): CAGR {b['cagr']:+.2f}%  Shrp {b['sharpe']:+.3f}  DD {b['dd']:+.1f}%")
            print(f"  {'config':<14} {'CAGR %':>9} {'d_cagr':>9} {'Sharpe':>8} {'maxDD %':>9}")
            print("  " + "-" * 55)
            for r in runs:
                if r["strategy"] != strategy or r["window"] != window_label:
                    continue
                print(f"  {r['config']:<14} {r['cagr_pct']:>+8.2f}% "
                      f"{r['cagr_pct']-b['cagr']:>+8.2f}p {r['mean_sharpe']:>+8.3f} "
                      f"{r['max_dd_pct']:>+8.2f}%")
    for strategy, _ in STRATEGIES:
        bi, bo = base[(strategy, "in_sample")], base[(strategy, "holdout")]
        for label, w, top_n in cfgs:
            hi = next(r for r in runs if r["strategy"] == strategy
                      and r["config"] == label and r["window"] == "in_sample")
            ho = next(r for r in runs if r["strategy"] == strategy
                      and r["config"] == label and r["window"] == "holdout")
            if (ho["cagr_pct"] >= bo["cagr"] + 5.0 and hi["cagr_pct"] >= bi["cagr"]):
                winners.append(f"{strategy}+{label}")
    print("\n  PRE-REGISTERED VERDICT (replacement candidates >= +5pp holdout, "
          ">= baseline in-sample): " + (", ".join(winners) if winners else "NONE"))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(
        {"runs": runs, "baselines_used": {f"{k[0]}/{k[1]}": v for k, v in base.items()},
         "replacement_candidates": winners}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
