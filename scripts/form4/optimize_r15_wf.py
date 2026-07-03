"""Walk-forward / regime-robust optimizer for R15.

The single-window raw-return optimizer (optimize_r15.py) overfit badly:
its 2010-2018 winner returned +128% in-sample but -7.5% on a 2025-2026
held-out year (while SPY did +29%). This version fixes the methodology:

  * Objective is risk-adjusted, not raw return: each config is scored by
    its portfolio Sharpe ratio bucketed PER CALENDAR YEAR.
  * Selection rewards CONSISTENCY across regimes, not in-sample fit. The
    score is mean(yearly Sharpe) - std(yearly Sharpe): a config that's
    spectacular in a bull run but blows up in the 2021-2023 dead zone is
    penalised by the std term and loses to a steadier config.
  * The scoring window (2015-2024) spans a normal bull (2015-19), the
    COVID crash (2020), the dead zone (2021-23) and recovery (2024). A
    config that survives all four is far likelier to generalise.

The winner should still be confirmed on the untouched 2025-2026 window
via scripts/run_holdout.py before anyone trusts it.

Usage:
  python -m scripts.optimize_r15_wf --since 2015-01-01 --until 2024-12-31 --trials 12
"""
from __future__ import annotations

import argparse
import json
import logging
import statistics
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

from trading_bot.db import connect
from trading_bot.execution import backtest as bt_mod
from trading_bot.profiles import NORMAL, use_profile
# Reuse the exact search space + sampler from the v1 optimizer so the two
# runs are comparable.
from scripts.form4.optimize_r15 import SEARCH_SPACE, _sample_profile

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")

MIN_TRADES_PER_YEAR = 8        # a year with fewer closed trades is low-confidence
OUTPUT_DIR = Path("var/form4/optimizer")


def _trades_by_year() -> dict[str, int]:
    """Closed-trade count per entry-year, read straight after a backtest
    (before the next run wipes the positions table)."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT substr(entry_date,1,4) y, COUNT(*) n FROM positions "
            "WHERE status='closed' GROUP BY y"
        ).fetchall()
    return {r["y"]: r["n"] for r in rows}


def _score(yearly_sharpe: dict[str, float]) -> dict:
    """Consistency score: mean - std of the per-year Sharpes. Higher is
    better. Also returns the diagnostic spread so the report is legible."""
    vals = [s for s in yearly_sharpe.values()]
    if not vals:
        return {"score": -999.0, "mean": 0.0, "std": 0.0, "min": 0.0,
                "n_positive": 0, "n_years": 0}
    mean = statistics.fmean(vals)
    std = statistics.pstdev(vals) if len(vals) > 1 else 0.0
    return {
        "score": round(mean - std, 4),
        "mean": round(mean, 4),
        "std": round(std, 4),
        "min": round(min(vals), 4),
        "n_positive": sum(1 for v in vals if v > 0),
        "n_years": len(vals),
    }


def _trial(profile, since: date, until: date, cash: float) -> dict:
    t0 = time.time()
    with use_profile(profile):
        result = bt_mod.run_backtest(since=since, until=until, starting_cash=cash)
    elapsed = time.time() - t0
    yearly_sharpe = result.sharpe_by_year()
    trades_yr = _trades_by_year()
    # Drop years with too few trades — their Sharpe is noise.
    trusted = {y: s for y, s in yearly_sharpe.items()
               if trades_yr.get(y, 0) >= MIN_TRADES_PER_YEAR}
    score = _score(trusted)
    return {
        "profile_name": profile.name,
        "elapsed_seconds": round(elapsed, 1),
        "params": {k: getattr(profile, k) for k in SEARCH_SPACE},
        "total_pnl_pct": round(result.total_pnl_pct, 3),
        "coverage_pct": round(result.coverage_pct, 2),
        "closed_count": result.closed_count,
        "yearly_sharpe": {y: round(s, 3) for y, s in yearly_sharpe.items()},
        "trades_by_year": trades_yr,
        "trusted_years": sorted(trusted),
        **score,
    }


def _print_leaderboard(rows: list[dict], years: list[str], top_k: int = 12) -> None:
    print("\n" + "=" * (44 + 7 * len(years)))
    hdr = f"  {'Rank':<5}{'Trial':<10}{'Score':>8}{'Mean':>7}{'Std':>7}{'Min':>7}  "
    hdr += "".join(f"{y[2:]:>6}" for y in years)
    print(hdr)
    print("-" * (44 + 7 * len(years)))
    for rank, r in enumerate(rows[:top_k], 1):
        line = (f"  {rank:<5}{r['profile_name']:<10}{r['score']:>8.3f}"
                f"{r['mean']:>7.2f}{r['std']:>7.2f}{r['min']:>7.2f}  ")
        for y in years:
            sh = r["yearly_sharpe"].get(y)
            line += f"{sh:>6.2f}" if sh is not None else f"{'-':>6}"
        print(line)
    print("=" * (44 + 7 * len(years)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2015-01-01")
    ap.add_argument("--until", default="2024-12-31")
    ap.add_argument("--trials", type=int, default=12)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--cash", type=float, default=100_000.0)
    ap.add_argument("--label", default="r15-walkforward")
    args = ap.parse_args()

    since = date.fromisoformat(args.since)
    until = date.fromisoformat(args.until)
    import random
    rng = random.Random(args.seed)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_path = OUTPUT_DIR / f"{run_id}_{args.label}.json"

    print(f"Walk-forward optimizer: {args.trials} trials, {since} -> {until}")
    print(f"Objective: mean(yearly Sharpe) - std(yearly Sharpe)  [consistency]")
    print(f"Results -> {out_path}\n", flush=True)

    results: list[dict] = []
    started = time.time()
    for i in range(args.trials):
        profile = _sample_profile(rng, NORMAL, i)
        print(f"[{i+1:>3}/{args.trials}] trial-{i:02d}: "
              f"th={profile.trade_threshold} sl={profile.stop_loss_pct} "
              f"tp={profile.take_profit_pct} te={profile.time_exit_days} "
              f"pos={profile.standard_position_pct}", flush=True)
        try:
            r = _trial(profile, since, until, args.cash)
            print(f"  -> score={r['score']:+.3f} "
                  f"(mean={r['mean']:+.2f} std={r['std']:.2f} min={r['min']:+.2f} "
                  f"pos-years={r['n_positive']}/{r['n_years']}) "
                  f"tpnl={r['total_pnl_pct']:+.1f}% closed={r['closed_count']} "
                  f"({r['elapsed_seconds']:.0f}s)", flush=True)
        except Exception as e:
            print(f"  trial-{i:02d} crashed: {e}", flush=True)
            r = {"profile_name": profile.name, "error": str(e),
                 "params": {k: getattr(profile, k) for k in SEARCH_SPACE},
                 "score": -999.0, "yearly_sharpe": {}}
        results.append(r)
        out_path.write_text(json.dumps({
            "run_id": run_id, "since": args.since, "until": args.until,
            "seed": args.seed, "objective": "mean(yearly_sharpe)-std(yearly_sharpe)",
            "search_space": SEARCH_SPACE, "min_trades_per_year": MIN_TRADES_PER_YEAR,
            "completed_trials": i + 1, "total_trials": args.trials,
            "elapsed_seconds": round(time.time() - started, 1),
            "results": results,
        }, indent=2))

    valid = [r for r in results if r.get("score", -999.0) > -900.0
             and r.get("n_years", 0) >= 3]
    valid.sort(key=lambda r: r["score"], reverse=True)
    all_years = sorted({y for r in results for y in r.get("yearly_sharpe", {})})
    _print_leaderboard(valid, all_years)

    if valid:
        best = valid[0]
        print(f"\nMost regime-robust config: {best['profile_name']}")
        for k, v in best["params"].items():
            print(f"  {k:<22} = {v}")
        print(f"  consistency score      = {best['score']:+.3f} "
              f"(mean {best['mean']:+.2f}, std {best['std']:.2f})")
        print(f"\nConfirm on the untouched 2025-2026 window before trusting it:")
        p = best["params"]
        print(f"  (edit scripts/run_holdout.py WINNER to "
              f"th={p['trade_threshold']} sl={p['stop_loss_pct']} "
              f"tp={p['take_profit_pct']} te={p['time_exit_days']} "
              f"pos={p['standard_position_pct']}, then run it)")
    print(f"\nFull results: {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
