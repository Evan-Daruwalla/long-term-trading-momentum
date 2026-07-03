"""Random-search optimizer for R15 risk-profile parameters.

Picks N random candidates from a hand-picked search space, runs a full
backtest for each, ranks by total_pnl_pct (with a min-trade-count filter
to avoid statistical noise), prints the top K and writes a JSON report.

This is NOT a true ML optimizer:
  - Single in-sample period (no K-fold cross-validation).
  - Random search, not Bayesian — overspends compute but is dead-simple
    and produces results immediately usable.
  - Scores by total return (not Sharpe) because Sharpe requires a daily
    equity curve we don't currently archive per trial.

Use the output's best config to manually run on a held-out test period
(walk_forward.py for the slice, or a fresh backtest on a later window).

Usage:
  python -m scripts.optimize_r15 --since 2010-01-01 --until 2018-12-31 --trials 15
  python -m scripts.optimize_r15 --since 2021-05-01 --until 2024-12-31 --trials 20 --seed 0

Coverage / survivorship: each trial's result includes coverage_pct (% of
signals actually trade-able given price-cache state) and worst_case_pnl_pct
(headline minus hypothetical -100% loss on every skipped-no-price signal).
Report both alongside the headline so the winner can't hide behind
survivorship bias.
"""
from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import time
from dataclasses import asdict
from datetime import date, datetime, timezone
from pathlib import Path

from trading_bot.execution import backtest as bt_mod
from trading_bot.profiles import NORMAL, RiskProfile, use_profile

# Route backtest.log INFO messages (incl. "backtest progress: D/T days") to
# the optimizer's stdout so the dashboard can render within-trial progress.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


# Search space. Each list is sampled uniformly per trial. Keep small —
# the curse of dimensionality kills random search above ~6 dims.
SEARCH_SPACE: dict[str, list] = {
    "trade_threshold":       [5, 6, 7, 8, 9, 10],
    "stop_loss_pct":         [-8.0, -10.0, -12.0, -15.0, -20.0],
    "take_profit_pct":       [25.0, 35.0, 50.0, 70.0, 100.0],
    "time_exit_days":        [45, 60, 90, 120, 180, 240],
    "standard_position_pct": [3.0, 4.0, 5.0, 7.0, 10.0],
}

MIN_TRADES_FOR_VALID = 30  # below this the result is noise, exclude from ranking
OUTPUT_DIR = Path("var/form4/optimizer")


def _sample_profile(rng: random.Random, base: RiskProfile, idx: int) -> RiskProfile:
    """One random RiskProfile drawn from SEARCH_SPACE, otherwise = `base`."""
    overrides = {k: rng.choice(v) for k, v in SEARCH_SPACE.items()}
    # high_conviction_threshold tracks trade_threshold to keep the ratio
    # sensible (HC is always >= trade_threshold; don't search the dependency).
    overrides["high_conviction_threshold"] = overrides["trade_threshold"] + 2
    # high_conviction_position_pct = 2x standard, same convention as the
    # hand-picked profiles.
    overrides["high_conviction_position_pct"] = overrides["standard_position_pct"] * 2.0
    # Inject the trial index into the name so logs/archives are distinguishable.
    overrides["name"] = f"trial-{idx:02d}"
    # Carry through fields we're NOT searching from the base profile.
    from dataclasses import fields
    for f in fields(base):
        if f.name not in overrides:
            overrides[f.name] = getattr(base, f.name)
    return RiskProfile(**overrides)


def _trial(profile: RiskProfile, since: date, until: date, cash: float) -> dict:
    """Run a single backtest, return a JSON-serializable result dict."""
    t0 = time.time()
    with use_profile(profile):
        result = bt_mod.run_backtest(since=since, until=until, starting_cash=cash)
    elapsed = time.time() - t0
    return {
        "profile_name": profile.name,
        "elapsed_seconds": round(elapsed, 1),
        "params": {k: getattr(profile, k) for k in SEARCH_SPACE},
        "total_pnl_pct": round(result.total_pnl_pct, 3),
        "worst_case_pnl_pct": round(result.worst_case_pnl_pct, 3),
        "coverage_pct": round(result.coverage_pct, 2),
        "signals_placed": result.signals_placed,
        "signals_tradeable": result.signals_tradeable,
        "signals_total": result.signals_total,
        "closed_count": result.closed_count,
        "open_count": result.open_count,
        "realized_pnl": round(result.realized_pnl, 2),
    }


def _print_table(rows: list[dict], top_k: int = 10) -> None:
    """Console-friendly leaderboard."""
    print()
    print("=" * 110)
    print(f"  {'Rank':<5}{'Trial':<10}{'TPnl%':>8}{'Worst%':>9}{'Cov%':>7}"
          f"{'Closed':>8}{'Skipped':>9}  {'Params'}")
    print("-" * 110)
    for rank, r in enumerate(rows[:top_k], 1):
        p = r["params"]
        params_str = (f"th={p['trade_threshold']:<2} sl={p['stop_loss_pct']:>5.1f} "
                      f"tp={p['take_profit_pct']:>5.1f} te={p['time_exit_days']:<3} "
                      f"pos={p['standard_position_pct']:.1f}")
        print(f"  {rank:<5}{r['profile_name']:<10}"
              f"{r['total_pnl_pct']:>8.2f}{r['worst_case_pnl_pct']:>9.2f}"
              f"{r['coverage_pct']:>7.1f}{r['closed_count']:>8}"
              f"{r['signals_no_price']:>9}  {params_str}")
    print("=" * 110)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True, help="Train period start (YYYY-MM-DD)")
    ap.add_argument("--until", required=True, help="Train period end (YYYY-MM-DD)")
    ap.add_argument("--trials", type=int, default=15, help="How many random configs to try")
    ap.add_argument("--seed", type=int, default=42, help="RNG seed for reproducibility")
    ap.add_argument("--cash", type=float, default=100_000.0, help="Starting cash per trial")
    ap.add_argument("--label", default="r15-optimize", help="Output directory tag")
    args = ap.parse_args()

    since = date.fromisoformat(args.since)
    until = date.fromisoformat(args.until)
    rng = random.Random(args.seed)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_path = OUTPUT_DIR / f"{run_id}_{args.label}.json"

    results: list[dict] = []
    print(f"Optimizer: {args.trials} trials, {since} -> {until}, seed={args.seed}")
    print(f"Results will write to {out_path}")
    print(f"Search space: {SEARCH_SPACE}")
    print()

    started = time.time()
    for i in range(args.trials):
        profile = _sample_profile(rng, NORMAL, i)
        print(f"[{i+1:>3}/{args.trials}] running trial-{i:02d}: "
              f"th={profile.trade_threshold} sl={profile.stop_loss_pct} "
              f"tp={profile.take_profit_pct} te={profile.time_exit_days} "
              f"pos={profile.standard_position_pct}", flush=True)
        try:
            r = _trial(profile, since, until, args.cash)
        except Exception as e:
            print(f"  trial-{i:02d} crashed: {e}", flush=True)
            r = {"profile_name": profile.name, "error": str(e),
                 "params": {k: getattr(profile, k) for k in SEARCH_SPACE}}
        results.append(r)
        print(f"  -> tpnl={r.get('total_pnl_pct','?')}% "
              f"worst={r.get('worst_case_pnl_pct','?')}% "
              f"cov={r.get('coverage_pct','?')}% "
              f"closed={r.get('closed_count','?')} "
              f"({r.get('elapsed_seconds','?')}s)", flush=True)
        # Persist after each trial so an early crash doesn't lose work.
        out_path.write_text(json.dumps({
            "run_id": run_id, "since": args.since, "until": args.until,
            "seed": args.seed, "search_space": SEARCH_SPACE,
            "min_trades_for_valid": MIN_TRADES_FOR_VALID,
            "elapsed_seconds": round(time.time() - started, 1),
            "completed_trials": i + 1, "total_trials": args.trials,
            "results": results,
        }, indent=2))

    # Rank by total_pnl_pct, filter out under-sampled trials.
    valid = [r for r in results
             if "total_pnl_pct" in r and r.get("closed_count", 0) >= MIN_TRADES_FOR_VALID]
    valid.sort(key=lambda r: r["total_pnl_pct"], reverse=True)
    print(f"\n{len(valid)}/{len(results)} trials had >= {MIN_TRADES_FOR_VALID} closed trades.")
    _print_table(valid, top_k=10)

    if valid:
        best = valid[0]
        print(f"\nBest config:")
        for k, v in best["params"].items():
            print(f"  {k:<22} = {v}")
        print(f"\nNext step: run that config on a held-out test period to check "
              f"out-of-sample performance.")
    print(f"\nFull results written to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
