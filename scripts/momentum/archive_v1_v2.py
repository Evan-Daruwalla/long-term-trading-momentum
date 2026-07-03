"""Archive mom_v1 + mom_v2 standalone runs for the dashboard.

Generates 4 JSONs in var/momentum/sleeves/ matching the schema expected by
`_load_sleeves_runs()`: { run_id, since, until, top_n_per_sleeve,
cash_per_sleeve, elapsed_seconds, combined_total_pnl_pct,
combined_yearly_sharpe, per_sleeve{ momentum: { ... } }, combined_equity_curve }.

For a single-strategy backtest, combined values equal the single sleeve's values.
Labels: mom_v1_in_sample, mom_v1_holdout, mom_v2_in_sample, mom_v2_holdout.

Sequential — DB writes from concurrent backtests can corrupt state (see
sleeves_verdict.md attempt 8 notes).
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date, datetime, timezone
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum

OUT_DIR = Path("var/momentum/sleeves")
STARTING_CASH = 100_000.0
HALF_SPREAD_BPS = 5.0

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]

# (label, top_n) — matches the frozen strategy specs
STRATEGIES = [
    ("mom_v1", 100),   # momentum_v1.py: top-100 monthly
    ("mom_v2", 50),    # momentum_v2.py: top-50 monthly
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
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    factor_backtest.HALF_SPREAD_BPS = HALF_SPREAD_BPS
    started_all = time.time()

    for strat_label, top_n in STRATEGIES:
        for window_label, since, until in WINDOWS:
            label = f"{strat_label}_{window_label}"
            run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            out_path = OUT_DIR / f"{run_id}_{label}.json"
            print(f"\n=== {label}  ({since} -> {until}, top_n={top_n}) ===", flush=True)
            t0 = time.time()
            r = factor_backtest.run_factor_backtest(
                since=since, until=until,
                top_n=top_n, starting_cash=STARTING_CASH,
                rank_fn=momentum.rank_universe,
                rebalance_freq="M",
            )
            elapsed = time.time() - t0
            curve = r.equity_curve
            total_pct = (curve[-1][1] / curve[0][1] - 1) * 100
            years = (until - since).days / 365.25
            cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
            yr_sharpe = _sharpe_by_year(curve)

            # Per-sleeve and combined are identical for single-strategy runs
            sleeve_data = {
                "total_pnl_pct": round(total_pct, 3),
                "closed_count": r.closed_count,
                "open_count": r.open_count,
                "elapsed_seconds": round(elapsed, 1),
                "yearly_sharpe": {y: round(s, 4) for y, s in yr_sharpe.items()},
            }
            output = {
                "run_id": run_id,
                "since": since.isoformat(),
                "until": until.isoformat(),
                "top_n_per_sleeve": top_n,
                "cash_per_sleeve": STARTING_CASH,
                "elapsed_seconds": round(elapsed, 1),
                "combined_total_pnl_pct": round(total_pct, 3),
                "combined_yearly_sharpe": {y: round(s, 4) for y, s in yr_sharpe.items()},
                "per_sleeve": {"momentum": sleeve_data},
                "combined_equity_curve": curve,
            }
            out_path.write_text(json.dumps(output, indent=2))
            print(f"  total={total_pct:+.2f}%  cagr={cagr:+.2f}%/yr  "
                  f"closed={r.closed_count}  elapsed={elapsed/60:.1f}min")
            print(f"  -> {out_path}")

    print(f"\nAll 4 runs done in {(time.time()-started_all)/60:.1f} min total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
