"""Mono-factor momentum optimization sweep.

Tests momentum variants beyond what's already locked in v2 (top-50 monthly):

Axes:
  - lookback / skip:  (252,21) [12-1, current]
                      (126,21) [6-1]
                      (189,21) [9-1]
                      (63, 21)  [3-1]
  - top_n:            30, 50 (v2 baseline), 75

Runs both in-sample (2015-2023) and held-out (2024-2026) so we can
identify configs that win on BOTH windows (robust, not overfit).

Writes results to var/momentum/mono_factor_sweep.json plus a printed
comparison table. Compares against mom_v2 baseline.

Usage:
  python -m scripts.momentum.mono_factor_sweep
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum

OUT_PATH = Path("var/momentum/mono_factor_sweep.json")
STARTING_CASH = 100_000.0

WINDOWS = [
    ("in_sample", date(2015, 1, 1),  date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1),  date(2026, 5, 1)),
]

# (lookback, skip, label) — Jegadeesh-Titman conventional configurations
LOOKBACKS = [
    (252, 21,  "12-1"),    # baseline (v2)
    (189, 21,  "9-1"),
    (126, 21,  "6-1"),
    (63,  21,  "3-1"),
]
TOP_NS = [30, 50, 75]


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


def run_one(window_label: str, since: date, until: date,
            lookback: int, skip: int, lb_label: str, top_n: int) -> dict:
    label = f"{lb_label}_top{top_n}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=top_n, starting_cash=STARTING_CASH,
        rank_fn=momentum.make_rank_fn(lookback=lookback, skip=skip),
        rebalance_freq="M",
    )
    elapsed = time.time() - t0
    curve = r.equity_curve
    years = (until - since).days / 365.25
    cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
    sharpe_y = _sharpe_by_year(curve)
    return {
        "label":         label,
        "window":        window_label,
        "lookback":      lookback,
        "skip":          skip,
        "lb_label":      lb_label,
        "top_n":         top_n,
        "total_pnl_pct": (curve[-1][1] / curve[0][1] - 1) * 100,
        "cagr_pct":      cagr,
        "mean_sharpe":   statistics.fmean(sharpe_y.values()) if sharpe_y else 0.0,
        "closed":        r.closed_count,
        "elapsed_sec":   round(elapsed, 1),
    }


def main() -> int:
    print(f"MOMENTUM MONO-FACTOR SWEEP: "
          f"{len(LOOKBACKS)} lookbacks x {len(TOP_NS)} top_n x {len(WINDOWS)} windows")
    print(f"  = {len(LOOKBACKS) * len(TOP_NS) * len(WINDOWS)} backtests total")
    print("=" * 70, flush=True)

    runs: list[dict] = []
    for window_label, since, until in WINDOWS:
        print(f"\n----- WINDOW: {window_label}  ({since} -> {until}) -----")
        for lookback, skip, lb_label in LOOKBACKS:
            for top_n in TOP_NS:
                runs.append(run_one(window_label, since, until,
                                    lookback, skip, lb_label, top_n))

    # ---- Print pivot tables ----
    for window_label, _, _ in WINDOWS:
        print(f"\n========== {window_label.upper()} ==========")
        # Two tables: CAGR and Sharpe
        for metric, fmt in [("cagr_pct", "{:+7.2f}"), ("mean_sharpe", "{:+7.3f}")]:
            print(f"\n  {metric}")
            print(f"  {'lookback':<10} " + "".join(f"{f'top{n}':>10}" for n in TOP_NS))
            print("  " + "-" * (10 + 10 * len(TOP_NS)))
            for lookback, skip, lb_label in LOOKBACKS:
                row = f"  {lb_label:<10} "
                for top_n in TOP_NS:
                    r = next(rr for rr in runs
                             if rr["window"] == window_label
                             and rr["lookback"] == lookback
                             and rr["top_n"] == top_n)
                    row += f"{fmt.format(r[metric]):>10}"
                print(row)

    # ---- Find configs that win both windows ----
    print(f"\n========== ROBUST CONFIGS (beat v2 on BOTH windows) ==========")
    print(f"  Baseline mom_v2 (12-1, top50): in-sample +21.0%/yr, held-out +26.5%/yr\n")
    in_runs = {(r["lb_label"], r["top_n"]): r
               for r in runs if r["window"] == "in_sample"}
    ho_runs = {(r["lb_label"], r["top_n"]): r
               for r in runs if r["window"] == "holdout"}
    V2_IS = 21.0
    V2_HO = 26.5
    for key in sorted(in_runs):
        if key == ("12-1", 50):
            continue   # skip the baseline itself
        i, h = in_runs[key], ho_runs[key]
        wins_is = i["cagr_pct"] > V2_IS
        wins_ho = h["cagr_pct"] > V2_HO
        if wins_is and wins_ho:
            print(f"  {key[0]:<6} top{key[1]:<3}: in-sample {i['cagr_pct']:+.2f}%/yr "
                  f"(v2 {V2_IS}%), held-out {h['cagr_pct']:+.2f}%/yr (v2 {V2_HO}%)  "
                  f"<- ROBUST WIN")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
