"""Sector momentum rotation — entirely different universe.

11 SPDR sector ETFs (XLE, XLF, XLI, XLB, XLK, XLP, XLU, XLV, XLY, XLC, XLRE).
For each monthly rebal: compute 12-1 momentum on each ETF, equal-weight
hold top-N sectors. Rotate monthly.

Standalone: doesn't touch tradeable_universe / price_cache. Fetches ETF
closes from yfinance once, caches to JSON, runs in-memory backtest.

Compares to:
- mom_v2 baseline (top-50 stocks)
- mom_roa_6535 baseline (top-50 mom+ROA)
- buy-and-hold SPY (cached)

Sweep: top-N in {2, 3, 4, 5} sectors x 2 windows = 8 runs.

Hypothesis: lower CAGR than stock-picking momentum but potentially
better Sharpe + much lower DD (sector diversification). If sector momentum
has uncorrelated returns to mom_roa_6535, it could be a useful 4th sleeve.
"""
from __future__ import annotations

import json
import math
import statistics
import time
from datetime import date, timedelta
from pathlib import Path

import yfinance as yf

from trading_bot.db import connect

CACHE_PATH = Path("var/data_audit/sector_etf_cache.json")
OUT_PATH = Path("var/data_audit/sector_momentum.json")
STARTING_CASH = 100_000.0
HALF_SPREAD_BPS = 5.0

SECTORS = ["XLE", "XLF", "XLI", "XLB", "XLK", "XLP", "XLU", "XLV", "XLY", "XLC", "XLRE"]
# XLC inception 2018-06; XLRE inception 2015-10. Pre-inception we use available subset.
# SPY for buy-and-hold benchmark.

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
TOP_NS = [2, 3, 4, 5]
LOOKBACK_TD = 252  # 12 months
SKIP_TD = 21       # 1 month skip

# Reference baselines on the stock-level strategies (5bps TC, clean data)
BASELINES = {
    "mom_v2":        {"in_sample": {"cagr": 2.72, "max_dd": -55.26, "sharpe": 0.167},
                      "holdout":   {"cagr": 28.81, "max_dd": -33.86, "sharpe": 0.903}},
    "mom_roa_6535":  {"in_sample": {"cagr": 4.73, "max_dd": -44.28, "sharpe": 0.241},
                      "holdout":   {"cagr": 36.45, "max_dd": -30.43, "sharpe": 1.111}},
}


def _fetch_etfs() -> dict[str, dict[str, float]]:
    """Returns {iso_date: {ticker: close}}. Caches to disk."""
    if CACHE_PATH.exists():
        print(f"  [cache] loading from {CACHE_PATH}", flush=True)
        return json.loads(CACHE_PATH.read_text())
    print(f"  [fetch] downloading {len(SECTORS)} SPDR sector ETFs (2014-2026)...", flush=True)
    t0 = time.time()
    out: dict[str, dict[str, float]] = {}
    for tk in SECTORS:
        df = yf.Ticker(tk).history(start="2014-06-01", end="2026-05-31", auto_adjust=False)
        for ts, row in df.iterrows():
            iso = ts.date().isoformat()
            close = float(row["Close"])
            if close <= 0: continue
            out.setdefault(iso, {})[tk] = close
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"  [fetch] {len(out)} days cached, {time.time()-t0:.1f}s", flush=True)
    return out


_PRICES: dict[str, dict[str, float]] = {}
_SORTED_DATES: list[str] = []


def _build_calendar(start: date, end: date) -> list[date]:
    """Trading days = dates with at least 1 sector close."""
    s, e = start.isoformat(), end.isoformat()
    return [date.fromisoformat(d) for d in _SORTED_DATES if s <= d <= e]


def _rebalance_dates(calendar: list[date]) -> set[str]:
    """First trading day of each calendar month."""
    out: set[str] = set()
    last_key = None
    for d in calendar:
        key = (d.year, d.month)
        if key != last_key:
            out.add(d.isoformat())
            last_key = key
    return out


def _close_at(ticker: str, iso: str) -> float | None:
    row = _PRICES.get(iso)
    return row.get(ticker) if row else None


def _close_at_offset(ticker: str, as_of_iso: str, offset_td: int) -> float | None:
    """Close `offset_td` trading days before as_of (negative = past)."""
    import bisect
    i = bisect.bisect_right(_SORTED_DATES, as_of_iso) - 1
    if i < 0: return None
    target = i + offset_td  # offset_td is negative
    if target < 0 or target >= len(_SORTED_DATES): return None
    return _PRICES[_SORTED_DATES[target]].get(ticker)


def _momentum_score(ticker: str, as_of_iso: str) -> float | None:
    p_recent = _close_at_offset(ticker, as_of_iso, -SKIP_TD)
    p_old = _close_at_offset(ticker, as_of_iso, -LOOKBACK_TD)
    if p_old is None or p_recent is None or p_old <= 0:
        return None
    return p_recent / p_old - 1.0


def _max_drawdown(curve):
    peak = curve[0][1]
    max_dd = 0.0
    for _, val in curve:
        if val > peak: peak = val
        if peak > 0:
            dd = (val/peak - 1.0) * 100
            if dd < max_dd: max_dd = dd
    return max_dd


def _sharpe_by_year(curve, risk_free_apy=0.045):
    by_year: dict[str, list[float]] = {}
    pv = py = None
    for iso, v in curve:
        y = iso[:4]
        if pv and pv > 0 and y == py:
            by_year.setdefault(y, []).append(v/pv - 1.0)
        pv, py = v, y
    out = {}
    rf = risk_free_apy/252
    for y, rets in by_year.items():
        if len(rets) < 20: continue
        sd = statistics.pstdev(rets)
        if sd > 0:
            out[y] = ((statistics.fmean(rets)-rf)/sd) * (252**0.5)
    return out


def run_sector_momentum(since: date, until: date, top_n: int) -> dict:
    calendar = _build_calendar(since, until)
    if not calendar:
        raise RuntimeError(f"No sector data in [{since}, {until}]")
    rebal_set = _rebalance_dates(calendar)
    half_spread = HALF_SPREAD_BPS / 10_000.0

    cash = STARTING_CASH
    positions: dict[str, float] = {}  # ticker -> qty
    entry_px: dict[str, float] = {}   # ticker -> entry price (for MTM not needed but kept)
    curve = []
    n_rebals = 0

    for d in calendar:
        iso = d.isoformat()
        if iso in rebal_set:
            # Rank sectors with valid momentum
            ranked = []
            for tk in SECTORS:
                s = _momentum_score(tk, iso)
                if s is not None:
                    ranked.append((tk, s))
            ranked.sort(key=lambda r: r[1], reverse=True)
            targets = {t for t, _ in ranked[:top_n]}

            # Sell anything not in targets
            for tk in list(positions.keys()):
                if tk not in targets:
                    px = _close_at(tk, iso)
                    if px is None: continue
                    fill = px * (1 - half_spread)
                    cash += positions[tk] * fill
                    del positions[tk]
                    entry_px.pop(tk, None)

            # Buy new entries equal-weight
            new_buys = [t for t in targets if t not in positions]
            if new_buys:
                per = max(0.0, cash * 0.999) / len(new_buys)
                for tk in new_buys:
                    px = _close_at(tk, iso)
                    if px is None: continue
                    fill = px * (1 + half_spread)
                    qty = per / fill
                    if qty <= 0: continue
                    positions[tk] = qty
                    entry_px[tk] = fill
                    cash -= qty * fill
            n_rebals += 1

        # MTM
        mtm = cash
        for tk, qty in positions.items():
            px = _close_at(tk, iso) or entry_px.get(tk, 0)
            mtm += qty * px
        curve.append((iso, mtm))

    return {"equity_curve": curve, "rebals": n_rebals, "final_nav": curve[-1][1]}


def run_one(window_label, since, until, top_n):
    label = f"sector_top{top_n}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    r = run_sector_momentum(since, until, top_n)
    curve = r["equity_curve"]
    total_pct = (curve[-1][1]/curve[0][1] - 1) * 100
    years = (until - since).days/365.25
    cagr = ((curve[-1][1]/curve[0][1]) ** (1/years) - 1) * 100
    sh = _sharpe_by_year(curve)
    mean_sh = statistics.fmean(sh.values()) if sh else 0.0
    return {
        "label": label, "window": window_label, "top_n": top_n,
        "total_pct": total_pct, "cagr_pct": cagr,
        "mean_sharpe": mean_sh, "max_dd_pct": _max_drawdown(curve),
        "n_rebals": r["rebals"], "elapsed_sec": round(time.time()-t0, 1),
    }


def _spy_buy_hold(since: date, until: date) -> dict | None:
    """Buy-and-hold SPY benchmark using cached price_cache."""
    with connect() as conn:
        s = conn.execute("SELECT price FROM price_cache WHERE ticker='SPY' AND kind='close' "
                         "AND key_date>=? ORDER BY key_date LIMIT 1", (since.isoformat(),)).fetchone()
        e = conn.execute("SELECT price FROM price_cache WHERE ticker='SPY' AND kind='close' "
                         "AND key_date<=? ORDER BY key_date DESC LIMIT 1", (until.isoformat(),)).fetchone()
    if not s or not e: return None
    years = (until - since).days/365.25
    cagr = ((e[0]/s[0]) ** (1/years) - 1) * 100
    return {"cagr": cagr, "total": (e[0]/s[0] - 1) * 100}


def main() -> int:
    global _PRICES, _SORTED_DATES
    _PRICES = _fetch_etfs()
    _SORTED_DATES = sorted(_PRICES.keys())
    print(f"Cached sector data: {len(_SORTED_DATES)} dates", flush=True)

    print(f"\nSECTOR MOMENTUM SWEEP: {len(TOP_NS)} top-N x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)
    runs = []
    for window_label, since, until in WINDOWS:
        for n in TOP_NS:
            runs.append(run_one(window_label, since, until, n))

    print("\n" + "=" * 100)
    print("  SECTOR MOMENTUM ROTATION  vs  stock-picking strategies + SPY buy-hold")
    print("=" * 100)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        v2 = BASELINES["mom_v2"][window_label]
        roa = BASELINES["mom_roa_6535"][window_label]
        spy = _spy_buy_hold(since, until)
        print(f"  {'config':<24} {'CAGR':>8} {'Sharpe':>8} {'maxDD':>9} {'note':<30}")
        print("  " + "-" * 80)
        if spy:
            print(f"  {'SPY buy-and-hold':<24} {spy['cagr']:>+7.2f}%   --        --      (benchmark)")
        print(f"  {'mom_v2 (50 stocks)':<24} {v2['cagr']:>+7.2f}% {v2['sharpe']:>+7.3f} {v2['max_dd']:>+8.2f}%  (stock-level)")
        print(f"  {'mom_roa_6535 (50 stocks)':<24} {roa['cagr']:>+7.2f}% {roa['sharpe']:>+7.3f} {roa['max_dd']:>+8.2f}%  (current winner)")
        for r in runs:
            if r["window"] != window_label: continue
            print(f"  {r['label']:<24} {r['cagr_pct']:>+7.2f}% {r['mean_sharpe']:>+7.3f} {r['max_dd_pct']:>+8.2f}%  "
                  f"({r['n_rebals']} rebals)")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
