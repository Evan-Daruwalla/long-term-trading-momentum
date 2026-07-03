"""Stress-test momentum-v1 baseline along three axes:

  1. Top-N sweep:     25, 50, 75, 100, 200, 300
  2. Rebalance freq:  weekly, monthly (baseline), quarterly
  3. Monthly bucket:  break held-out into monthly returns vs SPY/RSP/IWM

Goal: find whether the +0.72 held-out mean Sharpe is robust to parameter
choices, or whether top-100 / monthly was a lucky local optimum.

Cheap version — uses cached prices + benchmarks. Writes results to
var/momentum/robustness_test.json + prints a comparison table.

Usage:
  python -m scripts.momentum.robustness_test
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

import yfinance as yf

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum

DEFAULT_OUT = Path("var/momentum/robustness_test.json")
STARTING_CASH = 100_000.0
# Globals set in main() — referenced by run_one() & helpers.
SINCE: date = date(2024, 1, 1)
UNTIL: date = date(2026, 5, 1)


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
        if sd == 0:
            out[y] = 0.0
        else:
            out[y] = ((statistics.fmean(rets) - rf) / sd) * (252 ** 0.5)
    return out


def _annualized_return(curve, years):
    return (curve[-1][1] / curve[0][1]) ** (1 / years) - 1


def _bench_yearly(ticker: str, start: str, end: str) -> dict[str, float]:
    """yfinance-backed annual returns for ETF."""
    df = yf.download(ticker, start=start, end=end, auto_adjust=True,
                     progress=False, group_by="ticker", actions=False)
    if df is None or df.empty:
        return {}
    closes = df[ticker]["Close"].dropna() if ticker in df.columns.get_level_values(0) \
             else df["Close"].dropna()
    # Synthetic equity curve at $100K
    px0 = float(closes.iloc[0])
    curve = [(ts.date().isoformat(), float(p) / px0 * 100_000)
             for ts, p in closes.items()]
    by_year: dict[str, tuple[float, float]] = {}
    for iso, val in curve:
        y = iso[:4]
        if y not in by_year:
            by_year[y] = (val, val)
        else:
            by_year[y] = (by_year[y][0], val)
    return {y: (e / s - 1) * 100 for y, (s, e) in by_year.items()}


def _monthly_returns(curve) -> list[tuple[str, float]]:
    """First-of-month to first-of-next-month, in pct."""
    by_month: dict[str, list[tuple[str, float]]] = {}
    for iso, val in curve:
        by_month.setdefault(iso[:7], []).append((iso, val))
    out = []
    keys = sorted(by_month)
    for k in keys:
        pts = by_month[k]
        if len(pts) < 2:
            continue
        out.append((k, (pts[-1][1] / pts[0][1] - 1.0) * 100))
    return out


def run_one(top_n: int, freq: str, label: str) -> dict:
    print(f"\n>>> {label:<30}  top_n={top_n:>4}  freq={freq}", flush=True)
    t0 = time.time()
    # Always use momentum_v1's HALF_SPREAD_BPS (5.0)
    factor_backtest.HALF_SPREAD_BPS = 5.0
    r = factor_backtest.run_factor_backtest(
        since=SINCE, until=UNTIL,
        top_n=top_n, starting_cash=STARTING_CASH,
        rank_fn=momentum.rank_universe,
        rebalance_freq=freq,
    )
    elapsed = time.time() - t0
    curve = r.equity_curve
    years = (UNTIL - SINCE).days / 365.25
    cagr = _annualized_return(curve, years) * 100
    sharpe_by_y = _sharpe_by_year(curve)
    mean_sharpe = statistics.fmean(sharpe_by_y.values()) if sharpe_by_y else 0.0
    return {
        "label":          label,
        "top_n":          top_n,
        "freq":           freq,
        "total_pnl_pct":  (curve[-1][1] / curve[0][1] - 1) * 100,
        "cagr_pct":       cagr,
        "closed":         r.closed_count,
        "open":           r.open_count,
        "yearly_sharpe":  {y: round(s, 3) for y, s in sharpe_by_y.items()},
        "mean_sharpe":    mean_sharpe,
        "elapsed_sec":    round(elapsed, 1),
        "equity_curve":   curve,
    }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--since",  default="2024-01-01")
    ap.add_argument("--until",  default="2026-05-01")
    ap.add_argument("--label",  default="holdout",
                    help="filename tag, e.g. 'in_sample' or 'holdout'")
    args = ap.parse_args()
    global SINCE, UNTIL
    SINCE = date.fromisoformat(args.since)
    UNTIL = date.fromisoformat(args.until)
    out_path = DEFAULT_OUT.parent / f"robustness_{args.label}.json"

    print(f"MOMENTUM-V1 ROBUSTNESS TEST — {SINCE} -> {UNTIL}  ({args.label})")
    print("=" * 70)

    runs: list[dict] = []

    # ---- 1. Top-N sweep at monthly ----
    print("\n----- TOP-N SWEEP (monthly rebal) -----")
    for n in [25, 50, 75, 100, 200, 300]:
        runs.append(run_one(top_n=n, freq="M", label=f"top{n}_monthly"))

    # ---- 2. Rebalance frequency sweep at top-100 ----
    print("\n----- FREQUENCY SWEEP (top_n=100) -----")
    for f in ["W", "Q"]:    # M is already covered above at top_n=100
        runs.append(run_one(top_n=100, freq=f, label=f"top100_{f}"))

    # ---- 3. Benchmarks ----
    print("\n----- BENCHMARKS (yfinance) -----")
    bench_yrs = {}
    for t in ["SPY", "RSP", "IWM"]:
        try:
            bench_yrs[t] = _bench_yearly(
                t, SINCE.isoformat(), UNTIL.isoformat())
            print(f"  {t}: {bench_yrs[t]}")
        except Exception as e:
            print(f"  {t}: FAILED {e}")
            bench_yrs[t] = {}

    # ---- 4. Monthly consistency on top100_monthly baseline ----
    baseline = next(r for r in runs if r["label"] == "top100_monthly")
    monthly = _monthly_returns(baseline["equity_curve"])

    # ---- Output: table ----
    print("\n" + "=" * 90)
    print(f"{'config':<22} {'total %':>10} {'CAGR %':>9} {'mean Shrp':>10} "
          f"{'closed':>7} {'time(s)':>8}")
    print("-" * 90)
    for r in runs:
        print(f"{r['label']:<22} {r['total_pnl_pct']:>+9.2f}% "
              f"{r['cagr_pct']:>+8.2f}% {r['mean_sharpe']:>+10.3f} "
              f"{r['closed']:>7} {r['elapsed_sec']:>8.1f}")

    print(f"\n----- Monthly returns ({len(monthly)} months, baseline) -----")
    print(f"  {'month':<10} {'mom %':>8}")
    pos = neg = 0
    for m, v in monthly:
        marker = "+" if v > 0 else "-"
        print(f"  {m:<10} {v:>+8.2f}  {marker}")
        if v > 0: pos += 1
        else: neg += 1
    print(f"  Hit rate: {pos}/{pos+neg} months positive ({100*pos/(pos+neg):.0f}%)")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "since": SINCE.isoformat(),
        "until": UNTIL.isoformat(),
        "runs": [{k: v for k, v in r.items() if k != "equity_curve"} for r in runs],
        "benchmarks_yearly": bench_yrs,
        "baseline_monthly_returns": monthly,
    }
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nWritten -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
