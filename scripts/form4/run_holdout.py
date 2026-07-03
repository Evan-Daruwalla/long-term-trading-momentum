"""Held-out (out-of-sample) test for an optimizer-selected R15 config.

The optimizer (scripts/optimize_r15.py) picks a winning RiskProfile on the
TRAIN window. This script runs that exact config on a later, untouched
TEST window — the honest measure of whether the tuning generalizes or was
just overfitting the train period.

Defaults to optimizer run 20260520-202001's winner (trial-09) and the
May-2025..May-2026 test window. Override via flags.

Usage:
  python -m scripts.run_holdout
  python -m scripts.run_holdout --since 2025-05-01 --until 2026-05-01
"""
from __future__ import annotations

import argparse
import sys
from datetime import date

from trading_bot.execution import backtest as bt_mod
from trading_bot.profiles import NORMAL, RiskProfile, use_profile

# Winner of optimizer run 20260520-202001 (train window 2010-2018):
# trial-09, ranked #1 of 15 by total_pnl_pct among trials with >=30 closed.
WINNER = dict(
    trade_threshold=7,
    stop_loss_pct=-20.0,
    take_profit_pct=50.0,
    time_exit_days=45,
    standard_position_pct=7.0,
)


def _winner_profile() -> RiskProfile:
    """trial-09 as a RiskProfile. Non-searched fields inherit from NORMAL;
    the two dependent fields follow the optimizer's own conventions
    (HC threshold = threshold+2, HC size = 2x standard)."""
    from dataclasses import fields
    overrides = dict(WINNER)
    overrides["name"] = "holdout-trial-09"
    overrides["high_conviction_threshold"] = WINNER["trade_threshold"] + 2
    overrides["high_conviction_position_pct"] = WINNER["standard_position_pct"] * 2.0
    for f in fields(NORMAL):
        if f.name not in overrides:
            overrides[f.name] = getattr(NORMAL, f.name)
    return RiskProfile(**overrides)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2025-05-01")
    ap.add_argument("--until", default="2026-05-01")
    ap.add_argument("--cash", type=float, default=100_000.0)
    args = ap.parse_args()

    since = date.fromisoformat(args.since)
    until = date.fromisoformat(args.until)
    profile = _winner_profile()

    print(f"Held-out test: {since} -> {until}")
    print(f"Config (trial-09): th={profile.trade_threshold} "
          f"sl={profile.stop_loss_pct} tp={profile.take_profit_pct} "
          f"te={profile.time_exit_days} pos={profile.standard_position_pct}",
          flush=True)

    with use_profile(profile):
        r = bt_mod.run_backtest(since=since, until=until, starting_cash=args.cash)

    print()
    print("=" * 60)
    print(f"  HELD-OUT TEST RESULT  {since} -> {until}")
    print("=" * 60)
    print(f"  Total P&L            : {r.total_pnl_pct:+.2f}%")
    print(f"  Worst-case P&L       : {r.worst_case_pnl_pct:+.2f}%  "
          f"(assume every untradeable signal = -100%)")
    print(f"  Closed positions     : {r.closed_count}")
    print(f"  Open positions       : {r.open_count}")
    print(f"  Realized P&L         : ${r.realized_pnl:,.0f}")
    print(f"  Data coverage        : {r.coverage_pct:.1f}%  "
          f"({r.signals_tradeable:,}/{r.signals_total:,} signals tradeable)")
    print("=" * 60, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
