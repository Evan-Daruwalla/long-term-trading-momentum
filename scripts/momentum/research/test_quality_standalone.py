"""Test quality_xbrl_v2 as a STANDALONE strategy (not combined with momentum).

Question: is quality_xbrl_v2 strong enough to be its own deployable
strategy parallel to mom_v2? Earlier sleeves runs showed quality
delivered +7.4%/yr in-sample and +13.0%/yr held-out, but those were
with $50K (half the capital) and top_n=100 (twice the concentration of
mom_v2). For an apples-to-apples comparison we re-run at the same
params as mom_v2: top_n=50, $100K, monthly.

Also sweep top_n (25/50/75/100) since quality's optimal concentration
may differ from momentum's. Quality is a sticky/buy-and-hold factor,
so might want more concentration than momentum (or less, hard to say).

Outputs comparison table with mom_v2 + benchmarks.
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

import yfinance as yf

from trading_bot.execution import factor_backtest
from trading_bot.factors import quality_xbrl_v2

OUT_PATH = Path("var/momentum/quality_standalone_test.json")
STARTING_CASH = 100_000.0

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
TOP_NS = [25, 50, 75, 100]

# Baselines (from frozen v2 spec + earlier diagnose_alpha runs)
MOM_V2 = {
    "in_sample": {"cagr": 21.00, "sharpe": 0.230},
    "holdout":   {"cagr": 26.47, "sharpe": 0.868},
}


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


def _max_drawdown(curve) -> tuple[float, str, str]:
    """Returns (max_dd_pct, peak_date, trough_date)."""
    peak = curve[0][1]
    peak_date = curve[0][0]
    max_dd = 0.0
    trough_date = peak_date
    pk_for_trough = peak_date
    for iso, val in curve:
        if val > peak:
            peak = val
            peak_date = iso
        dd = (val / peak - 1.0) * 100
        if dd < max_dd:
            max_dd = dd
            trough_date = iso
            pk_for_trough = peak_date
    return max_dd, pk_for_trough, trough_date


def _bench_total_return(ticker: str, start: str, end: str) -> float | None:
    df = yf.download(ticker, start=start, end=end, auto_adjust=True,
                     progress=False, group_by="ticker", actions=False)
    if df is None or df.empty:
        return None
    closes = df[ticker]["Close"].dropna() if ticker in df.columns.get_level_values(0) \
             else df["Close"].dropna()
    return (float(closes.iloc[-1]) / float(closes.iloc[0]) - 1) * 100


def run_one(window_label: str, since: date, until: date, top_n: int) -> dict:
    label = f"qxv2_top{top_n}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=top_n, starting_cash=STARTING_CASH,
        rank_fn=quality_xbrl_v2.rank_universe,
        rebalance_freq="M",
    )
    curve = r.equity_curve
    years = (until - since).days / 365.25
    total_pct = (curve[-1][1] / curve[0][1] - 1) * 100
    cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
    sh = _sharpe_by_year(curve)
    max_dd, peak, trough = _max_drawdown(curve)
    return {
        "label":          label,
        "window":         window_label,
        "top_n":          top_n,
        "total_pnl_pct":  total_pct,
        "cagr_pct":       cagr,
        "mean_sharpe":    statistics.fmean(sh.values()) if sh else 0.0,
        "yearly_sharpe":  {y: round(s, 3) for y, s in sh.items()},
        "max_dd_pct":     max_dd,
        "max_dd_peak":    peak,
        "max_dd_trough":  trough,
        "closed":         r.closed_count,
        "open":           r.open_count,
        "elapsed_sec":    round(time.time() - t0, 1),
    }


def main() -> int:
    print(f"QUALITY_XBRL_V2 STANDALONE: {len(TOP_NS)} top_n x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)

    runs: list[dict] = []
    for window_label, since, until in WINDOWS:
        print(f"\n--- WINDOW: {window_label}  ({since} -> {until}) ---")
        for top_n in TOP_NS:
            runs.append(run_one(window_label, since, until, top_n))

    # ---- Benchmarks ----
    print("\n--- BENCHMARKS ---")
    bench = {}
    for w_label, since, until in WINDOWS:
        bench[w_label] = {}
        for t in ["SPY", "RSP", "IWM"]:
            try:
                r = _bench_total_return(t, since.isoformat(), until.isoformat())
                bench[w_label][t] = r
                years = (until - since).days / 365.25
                cagr = ((1 + r / 100) ** (1 / years) - 1) * 100
                print(f"  {w_label}/{t}: total {r:+.2f}%  CAGR {cagr:+.2f}%/yr")
            except Exception as e:
                print(f"  {w_label}/{t}: FAILED {e}")
                bench[w_label][t] = None

    # ---- Comparison table ----
    print("\n" + "=" * 90)
    print(f"  QUALITY_XBRL_V2 STANDALONE — vs mom_v2 baseline")
    print("=" * 90)
    for window_label, since, until in WINDOWS:
        years = (until - since).days / 365.25
        print(f"\n  {window_label.upper()}  ({since} -> {until}, {years:.1f} yrs)")
        print(f"  {'config':<22} {'total %':>10} {'CAGR %':>9} {'mean Shrp':>10} "
              f"{'max DD':>8} {'closed':>7}")
        print("  " + "-" * 76)
        for r in runs:
            if r["window"] != window_label:
                continue
            print(f"  {r['label']:<22} {r['total_pnl_pct']:>+9.2f}% "
                  f"{r['cagr_pct']:>+8.2f}% {r['mean_sharpe']:>+10.3f} "
                  f"{r['max_dd_pct']:>+7.2f}% {r['closed']:>7}")
        # Mom_v2 baseline row
        v2_total = ((1 + MOM_V2[window_label]['cagr']/100) ** years - 1) * 100
        print(f"  {'mom_v2 (baseline)':<22} {v2_total:>+9.2f}% "
              f"{MOM_V2[window_label]['cagr']:>+8.2f}% "
              f"{MOM_V2[window_label]['sharpe']:>+10.3f}  "
              f"   (n/a)   (n/a)")
        # Benchmarks
        for t, val in bench[window_label].items():
            if val is None:
                continue
            cagr = ((1 + val / 100) ** (1 / years) - 1) * 100
            print(f"  {t+' (bench)':<22} {val:>+9.2f}% {cagr:>+8.2f}% "
                  f"{'(n/a)':>10}    (n/a)  (n/a)")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs, "benchmarks": bench}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
