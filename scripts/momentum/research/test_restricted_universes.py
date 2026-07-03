"""Test mom_v2 on restricted universes — does the edge hold up?

Tests:
  1. Top-500 by market cap (S&P 500 proxy)     — universe = ~500 largest US stocks
  2. Top-1000 by market cap (Russell 1000)     — universe = ~1000 largest
  3. Ex-tech (exclude Technology sector)       — universe = current default minus tech

Each run uses mom_v2 params (top_n=50, monthly, $100K) but with the
universe restricted to the named subset.

If alpha holds across universes -> deployment confidence increases
If alpha collapses -> strategy needs the small-cap tail (and we know to
                      avoid concentrating large-cap-only buckets)
"""
from __future__ import annotations

import json
import sqlite3
import statistics
import time
from datetime import date
from pathlib import Path

import yfinance as yf

from trading_bot.config import DB_PATH
from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum

OUT_PATH = Path("var/momentum/restricted_universes_test.json")
STARTING_CASH = 100_000.0
TOP_N = 50    # mom_v2's top_n

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]


def _top_n_by_marketcap(n: int) -> set[str]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT ticker FROM fundamentals_cache "
        "WHERE field='marketCap' AND value IS NOT NULL "
        "ORDER BY value DESC LIMIT ?",
        (n,)
    ).fetchall()
    conn.close()
    return {r[0] for r in rows}


def _ex_sector_tickers(excluded_sector: str) -> set[str]:
    """Return tickers whose sector is NOT the excluded one. Tickers without
    cached sector data are KEPT (assume not excluded — conservative)."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT ticker, sector FROM sectors_cache"
    ).fetchall()
    conn.close()
    excluded = {t for t, s in rows if s == excluded_sector}
    # We need to start from the full ticker list and remove excluded
    conn = sqlite3.connect(DB_PATH)
    all_tickers = conn.execute(
        "SELECT DISTINCT ticker FROM price_cache WHERE kind='close'"
    ).fetchall()
    conn.close()
    return {r[0] for r in all_tickers if r[0] not in excluded}


def _make_restricted_rank_fn(rank_fn, allowed: set[str]):
    def wrapper(tickers, as_of):
        filtered = [t for t in tickers if t in allowed]
        return rank_fn(filtered, as_of)
    wrapper.__name__ = f"{rank_fn.__name__}_restricted"
    return wrapper


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


def _bench_total_return(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, auto_adjust=True,
                     progress=False, group_by="ticker", actions=False)
    if df is None or df.empty:
        return None
    closes = df[ticker]["Close"].dropna() if ticker in df.columns.get_level_values(0) \
             else df["Close"].dropna()
    return (float(closes.iloc[-1]) / float(closes.iloc[0]) - 1) * 100


def run_one(label: str, since: date, until: date, allowed: set[str]) -> dict:
    print(f"  >>> {label}  (universe={len(allowed)} tickers)", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N, starting_cash=STARTING_CASH,
        rank_fn=_make_restricted_rank_fn(momentum.rank_universe, allowed),
        rebalance_freq="M",
    )
    curve = r.equity_curve
    years = (until - since).days / 365.25
    cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
    sh = _sharpe_by_year(curve)
    return {
        "label":         label,
        "universe_size": len(allowed),
        "total_pnl_pct": (curve[-1][1] / curve[0][1] - 1) * 100,
        "cagr_pct":      cagr,
        "mean_sharpe":   statistics.fmean(sh.values()) if sh else 0.0,
        "yearly_sharpe": {y: round(s, 3) for y, s in sh.items()},
        "closed":        r.closed_count,
        "elapsed_sec":   round(time.time() - t0, 1),
    }


def main() -> int:
    print("MOM_V2 RESTRICTED-UNIVERSE TEST")
    print("=" * 70)

    # Build the restricted universes
    print("\nBuilding restricted universe sets...")
    top500 = _top_n_by_marketcap(500)
    top1000 = _top_n_by_marketcap(1000)
    ex_tech = _ex_sector_tickers("Technology")
    print(f"  top500:  {len(top500)}")
    print(f"  top1000: {len(top1000)}")
    print(f"  ex-tech: {len(ex_tech)}")

    universes = [
        ("top500",  top500),
        ("top1000", top1000),
        ("ex_tech", ex_tech),
    ]

    runs: list[dict] = []
    for window_label, since, until in WINDOWS:
        print(f"\n--- {window_label}  ({since} -> {until}) ---")
        for uni_label, allowed in universes:
            runs.append(run_one(
                f"{uni_label}_{window_label}", since, until, allowed))

    # Benchmarks
    print("\n--- BENCHMARKS ---")
    bench = {}
    for w_label, since, until in WINDOWS:
        bench[w_label] = {}
        for t in ["SPY", "RSP", "IWM"]:
            try:
                bench[w_label][t] = _bench_total_return(
                    t, since.isoformat(), until.isoformat())
            except Exception:
                bench[w_label][t] = None

    # Comparison
    print("\n" + "=" * 90)
    print("  MOM_V2 ACROSS RESTRICTED UNIVERSES (top_n=50, $100K, monthly)")
    print("=" * 90)
    MOM_V2 = {
        "in_sample": {"cagr": 21.00, "sharpe": 0.230, "total": 455.6},
        "holdout":   {"cagr": 26.47, "sharpe": 0.868, "total":  72.8},
    }
    for window_label, since, until in WINDOWS:
        years = (until - since).days / 365.25
        print(f"\n  {window_label.upper()}  ({since} -> {until}, {years:.1f} yrs)")
        print(f"  {'universe':<20} {'total %':>10} {'CAGR %':>9} {'mean Shrp':>10} {'closed':>7}")
        print("  " + "-" * 60)
        for r in runs:
            if not r["label"].endswith(f"_{window_label}"):
                continue
            print(f"  {r['label']:<20} {r['total_pnl_pct']:>+9.2f}% "
                  f"{r['cagr_pct']:>+8.2f}% {r['mean_sharpe']:>+10.3f} "
                  f"{r['closed']:>7}")
        # mom_v2 default-universe row
        v2 = MOM_V2[window_label]
        print(f"  {'mom_v2 (default)':<20} {v2['total']:>+9.2f}% "
              f"{v2['cagr']:>+8.2f}% {v2['sharpe']:>+10.3f}   (n/a)")
        for t, val in bench[window_label].items():
            if val is None:
                continue
            cagr = ((1 + val / 100) ** (1 / years) - 1) * 100
            print(f"  {t+' (bench)':<20} {val:>+9.2f}% {cagr:>+8.2f}% "
                  f"{'(n/a)':>10}   (n/a)")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs, "benchmarks": bench}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
