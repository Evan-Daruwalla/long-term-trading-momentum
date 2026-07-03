"""Transaction-cost sensitivity for the momentum baseline.

Runs the held-out window at 5/15/30 bps half-spread to bracket what realistic
broker friction does to the headline +53% return. 5bps was the original
backtest assumption; 15bps is closer to IBKR/Schwab on mid-caps; 30bps is
realistic for the smaller-cap names momentum often picks.

Held-out only (~3 min per run) — in-sample is 9yr and 15 min each so we
extrapolate from the held-out turnover-per-year.
"""
from __future__ import annotations

from datetime import date

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum


def run_at(half_spread_bps: float) -> dict:
    factor_backtest.HALF_SPREAD_BPS = half_spread_bps
    r = factor_backtest.run_factor_backtest(
        since=date(2024, 1, 1), until=date(2026, 5, 1),
        top_n=100, starting_cash=100_000.0,
        rank_fn=momentum.rank_universe,
    )
    curve = r.equity_curve
    return {
        "half_spread_bps": half_spread_bps,
        "round_trip_bps":  half_spread_bps * 2,
        "total_pnl_pct":   (curve[-1][1] / curve[0][1] - 1) * 100,
        "closed":          r.closed_count,
        "open":            r.open_count,
        "end_equity":      curve[-1][1],
    }


def main() -> None:
    print("Momentum held-out (2024-2026) TC sensitivity")
    print("-" * 60)
    rows = []
    for bps in [5.0, 15.0, 30.0]:
        print(f"\n>>> Running with HALF_SPREAD_BPS={bps}")
        rows.append(run_at(bps))

    print("\n" + "=" * 60)
    print(f"{'half-spread':>14} {'round-trip':>14} {'total %':>12} "
          f"{'closed':>8} {'end equity':>14}")
    base = rows[0]["total_pnl_pct"]
    for r in rows:
        delta = r["total_pnl_pct"] - base
        print(f"{r['half_spread_bps']:>11.0f}bps {r['round_trip_bps']:>11.0f}bps "
              f"{r['total_pnl_pct']:>+11.2f}% {r['closed']:>8} "
              f"${r['end_equity']:>12,.0f}  (delta {delta:+.2f}pp)")
    # Persist for later reading even if console encoding chokes
    import json
    from pathlib import Path
    Path("var/tc_sensitivity.json").write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
