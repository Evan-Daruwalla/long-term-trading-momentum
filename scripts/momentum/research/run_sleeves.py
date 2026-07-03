"""Separate-sleeve multi-factor portfolio.

Naive percentile-rank composite (factors/composite.py) killed momentum's
in-sample CAGR from 19.6%/yr to 4.0%/yr — the low-vol filter excluded
the very high-vol names where momentum's premium lives. This script
tries the opposite combining approach: run each factor as an
INDEPENDENT sleeve with its own capital, its own rebalances, its own
top-N basket. Then sum the daily equity curves.

That way each factor captures its full single-factor return; the
"diversification" comes from holding both sleeves, not from filtering
one through the other.

Each sleeve is a separate run_factor_backtest call (the backtest WIPES
state each time, so we serialize). The two equity curves are saved
in-memory and recombined here.

Usage:
  python -m scripts.run_sleeves --since 2015-01-01 --until 2023-12-31 --label sleeves_in_sample
  python -m scripts.run_sleeves --since 2024-01-01 --until 2026-05-01 --label sleeves_holdout
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

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum, low_vol, quality, quality_xbrl, quality_xbrl_v2, mom_quality_screen, accruals

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")

OUTPUT_DIR = Path("var/momentum/sleeves")

# Default sleeves = momentum + low_vol. Override via --sleeves on CLI.
# Available:
#   momentum         — 12-1 month momentum
#   low_vol          — 60-day stdev with 1%/day floor
#   quality          — yfinance-proxy (lookahead-biased, held-out only)
#   quality_xbrl     — SEC XBRL PIT, 3-component (ROE/OM/D/E)
#   quality_xbrl_v2  — SEC XBRL PIT, 8-component (adds FCF, current ratio,
#                       asset growth, persistence, dilution)
#   accruals         — Sloan (1996): (NI-CFO)/avg-Assets, NI>0 filter
SLEEVE_REGISTRY = {
    "momentum":           momentum.rank_universe,
    "low_vol":            low_vol.rank_universe,
    "quality":            quality.rank_universe,
    "quality_xbrl":       quality_xbrl.rank_universe,
    "quality_xbrl_v2":    quality_xbrl_v2.rank_universe,
    "mom_quality_screen": mom_quality_screen.rank_universe,
    "accruals":           accruals.rank_universe,
}
SLEEVES = [
    ("momentum", momentum.rank_universe),
    ("low_vol",  low_vol.rank_universe),
]


def _sharpe_by_year(equity_curve: list[tuple[str, float]],
                    risk_free_apy: float = 0.045) -> dict[str, float]:
    """Annualized Sharpe per calendar year from a daily equity series.
    Same logic as BacktestResult.sharpe_by_year but on a passed curve."""
    by_year: dict[str, list[float]] = {}
    prev_val = None
    prev_year = None
    for iso, val in equity_curve:
        year = iso[:4]
        if prev_val is not None and prev_val > 0 and year == prev_year:
            by_year.setdefault(year, []).append(val / prev_val - 1.0)
        prev_val, prev_year = val, year
    out: dict[str, float] = {}
    daily_rf = risk_free_apy / 252.0
    for year, rets in by_year.items():
        if len(rets) < 20:
            continue
        sd = statistics.pstdev(rets)
        if sd == 0:
            out[year] = 0.0
            continue
        excess = statistics.fmean(rets) - daily_rf
        out[year] = (excess / sd) * (252 ** 0.5)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2015-01-01")
    ap.add_argument("--until", default="2023-12-31")
    ap.add_argument("--top-n", type=int, default=100,
                    help="positions per sleeve (not total)")
    ap.add_argument("--cash-per-sleeve", type=float, default=50_000.0)
    ap.add_argument("--label", default="sleeves")
    ap.add_argument("--sleeves", default="momentum,low_vol",
                    help="Comma-separated sleeve names from SLEEVE_REGISTRY "
                         "(momentum, low_vol, quality)")
    args = ap.parse_args()

    # Resolve sleeve list from CLI flag
    global SLEEVES
    SLEEVES = [(name.strip(), SLEEVE_REGISTRY[name.strip()])
               for name in args.sleeves.split(",")]

    since = date.fromisoformat(args.since)
    until = date.fromisoformat(args.until)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_path = OUTPUT_DIR / f"{run_id}_{args.label}.json"

    print(f"Sleeves backtest: {since} -> {until}")
    print(f"  Sleeves: {[s[0] for s in SLEEVES]}")
    print(f"  Each: ${args.cash_per_sleeve:,.0f} starting, top_n={args.top_n}")
    print(f"Results -> {out_path}\n", flush=True)

    per_sleeve: dict[str, dict] = {}
    started = time.time()

    for name, rank_fn in SLEEVES:
        print(f"\n=== Sleeve: {name} ===", flush=True)
        t0 = time.time()
        r = factor_backtest.run_factor_backtest(
            since=since, until=until, top_n=args.top_n,
            starting_cash=args.cash_per_sleeve, rank_fn=rank_fn)
        elapsed = time.time() - t0
        per_sleeve[name] = {
            "total_pnl_pct": round(r.mtm_total_pnl_pct, 3),
            "closed_count": r.closed_count,
            "open_count": r.open_count,
            "elapsed_seconds": round(elapsed, 1),
            "yearly_sharpe": {y: round(s, 4) for y, s in r.sharpe_by_year().items()},
            "equity_curve": r.equity_curve,
        }
        print(f"  -> MTM tpnl={r.mtm_total_pnl_pct:+.2f}%  closed={r.closed_count}  "
              f"({elapsed/60:.1f} min)", flush=True)

    # Combine: align by date, sum equity values
    by_date: dict[str, dict[str, float]] = {}
    for name, data in per_sleeve.items():
        for iso, val in data["equity_curve"]:
            by_date.setdefault(iso, {})[name] = val
    combined_curve: list[tuple[str, float]] = []
    for iso in sorted(by_date):
        slots = by_date[iso]
        if len(slots) == len(SLEEVES):     # only include dates present in both
            combined_curve.append((iso, sum(slots.values())))

    combined_start = combined_curve[0][1]
    combined_end = combined_curve[-1][1]
    combined_tpnl_pct = (combined_end / combined_start - 1.0) * 100.0
    combined_sharpe_by_yr = _sharpe_by_year(combined_curve)

    print(f"\n{'=' * 60}")
    print(f"  COMBINED SLEEVES  {since} -> {until}")
    print(f"{'=' * 60}")
    print(f"  Combined start    : ${combined_start:>11,.0f}")
    print(f"  Combined end      : ${combined_end:>11,.0f}")
    print(f"  Combined return   : {combined_tpnl_pct:+.2f}%")
    print()
    print("  Per-year Sharpe (combined):")
    for y in sorted(combined_sharpe_by_yr):
        print(f"    {y}: {combined_sharpe_by_yr[y]:+.3f}")
    print()
    print("  Per-sleeve individual returns:")
    for name, d in per_sleeve.items():
        print(f"    {name:<10}: {d['total_pnl_pct']:+.2f}%")
    print(f"  Total elapsed: {(time.time()-started)/60:.1f} min")
    print("=" * 60, flush=True)

    out_path.write_text(json.dumps({
        "run_id": run_id, "since": args.since, "until": args.until,
        "top_n_per_sleeve": args.top_n,
        "cash_per_sleeve": args.cash_per_sleeve,
        "elapsed_seconds": round(time.time() - started, 1),
        "combined_total_pnl_pct": round(combined_tpnl_pct, 3),
        "combined_yearly_sharpe": {y: round(s, 4) for y, s in combined_sharpe_by_yr.items()},
        "per_sleeve": {k: {kk: vv for kk, vv in v.items() if kk != "equity_curve"}
                       for k, v in per_sleeve.items()},
        "combined_equity_curve": combined_curve,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
