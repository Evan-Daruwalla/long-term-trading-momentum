"""Candidate #5: turn-of-month + T-bill carry.

Rule: hold SPY over the last trading day of each month + the first 3 trading
days of the next month (~4 exposure days/month, ~20% of days); earn the cash
(T-bill) rate the rest of the time. One round trip per month.

This is a SINGLE-ASSET TIMING strategy, not a cross-sectional ranker, so it
uses its own tiny daily simulator rather than factor_backtest. Idle days earn
config.CASH_INTEREST_APY (4.5%) — that IS the T-bill carry leg (BIL ~= cash
rate), so no BIL fetch is needed.

Compared against SPY buy-and-hold (the relevant benchmark for a market-timing
sleeve) on both frozen windows.

Success bar (from research doc): in-sample Sharpe > 0.7, beats SPY-Sharpe AND
beats the cash rate on CAGR, effect not concentrated in <30% of months.
"""
from __future__ import annotations

import json
import sqlite3
import statistics
from datetime import date
from pathlib import Path

from trading_bot import config
from trading_bot.config import DB_PATH

OUT_PATH = Path("var/data_audit/turn_of_month.json")
STARTING_CASH = 100_000.0
HALF_SPREAD_BPS = 2.0      # SPY is tight; 2bps half-spread is conservative
CASH_APY = config.CASH_INTEREST_APY

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]


def _spy_closes() -> list[tuple[str, float]]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT key_date, price FROM price_cache "
        "WHERE ticker='SPY' AND kind='close' ORDER BY key_date",
    ).fetchall()
    conn.close()
    return [(d, p) for d, p in rows if p is not None and p > 0]


def _tom_exposure_flags(dates: list[str]) -> list[bool]:
    """For each date, True if it's the last trading day of its month OR one of
    the first 3 trading days of its month."""
    # group by year-month, track index within month
    flags = [False] * len(dates)
    # first-3: position within month <= 3
    month_counts: dict[str, int] = {}
    for i, d in enumerate(dates):
        ym = d[:7]
        month_counts[ym] = month_counts.get(ym, 0) + 1
        if month_counts[ym] <= 3:
            flags[i] = True
    # last trading day of month: next date is a different month (or end)
    for i, d in enumerate(dates):
        ym = d[:7]
        is_last = (i == len(dates) - 1) or (dates[i + 1][:7] != ym)
        if is_last:
            flags[i] = True
    return flags


def _max_drawdown(curve):
    peak = curve[0][1]
    mdd = 0.0
    for _, v in curve:
        if v > peak:
            peak = v
        if peak > 0:
            dd = (v / peak - 1.0) * 100
            if dd < mdd:
                mdd = dd
    return mdd


def _sharpe_by_year(curve, risk_free_apy=0.045):
    by_year: dict[str, list[float]] = {}
    pv = py = None
    for iso, v in curve:
        y = iso[:4]
        if pv and pv > 0 and y == py:
            by_year.setdefault(y, []).append(v / pv - 1.0)
        pv, py = v, y
    rf = risk_free_apy / 252
    out = {}
    for y, rets in by_year.items():
        if len(rets) < 20:
            continue
        sd = statistics.pstdev(rets)
        if sd > 0:
            out[y] = ((statistics.fmean(rets) - rf) / sd) * (252 ** 0.5)
    return out


def simulate(closes, since, until, tom_only: bool):
    """If tom_only: TOM timing. Else: SPY buy-and-hold (benchmark).
    Returns (equity_curve, n_round_trips, exposure_frac)."""
    win = [(d, p) for d, p in closes if since.isoformat() <= d <= until.isoformat()]
    dates = [d for d, _ in win]
    prices = [p for _, p in win]
    flags = _tom_exposure_flags(dates) if tom_only else [True] * len(dates)
    cash_daily = CASH_APY / 252
    hs = HALF_SPREAD_BPS / 10000.0
    nav = STARTING_CASH
    curve = [(dates[0], nav)]
    prev_invested = False
    round_trips = 0
    exposure_days = 0
    for i in range(1, len(dates)):
        invested = flags[i]
        if invested:
            exposure_days += 1
            r = prices[i] / prices[i - 1] - 1.0
            nav *= (1.0 + r)
        else:
            nav *= (1.0 + cash_daily)
        # transaction cost when entering or exiting the SPY position
        if invested != prev_invested:
            nav *= (1.0 - hs)        # one leg (SPY) each switch
            if invested:
                round_trips += 0.5   # entry
            else:
                round_trips += 0.5   # exit
        prev_invested = invested
        curve.append((dates[i], nav))
    return curve, int(round_trips), exposure_days / max(1, len(dates) - 1)


def _metrics(curve, since, until):
    cagr = ((curve[-1][1] / curve[0][1]) ** (365.25 / (until - since).days) - 1) * 100
    sh = _sharpe_by_year(curve)
    return {
        "cagr_pct": cagr,
        "mean_sharpe": statistics.fmean(sh.values()) if sh else 0.0,
        "max_dd_pct": _max_drawdown(curve),
    }


def main() -> int:
    closes = _spy_closes()
    print("TURN-OF-MONTH vs SPY buy-and-hold")
    print("=" * 80)
    runs = []
    for wl, since, until in WINDOWS:
        tom_curve, rt, expo = simulate(closes, since, until, tom_only=True)
        spy_curve, _, _ = simulate(closes, since, until, tom_only=False)
        tom = _metrics(tom_curve, since, until)
        spy = _metrics(spy_curve, since, until)
        tom.update({"window": wl, "config": "turn_of_month",
                    "round_trips": rt, "exposure_frac": expo})
        spy.update({"window": wl, "config": "spy_buyhold"})
        runs += [tom, spy]
        print(f"\n  {wl.upper()}  (exposure {expo*100:.0f}% of days, {rt} round trips)")
        print(f"  {'config':<18} {'CAGR':>8} {'Sharpe':>8} {'maxDD':>9}")
        print("  " + "-" * 48)
        for r in (tom, spy):
            print(f"  {r['config']:<18} {r['cagr_pct']:>+7.2f}% "
                  f"{r['mean_sharpe']:>+7.3f} {r['max_dd_pct']:>+8.2f}%")
        print(f"  -> TOM dCAGR {tom['cagr_pct']-spy['cagr_pct']:+.2f}pp  "
              f"dSharpe {tom['mean_sharpe']-spy['mean_sharpe']:+.3f}  "
              f"dDD {tom['max_dd_pct']-spy['max_dd_pct']:+.2f}pp")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
