"""Crash-fix sweep for long-short vol-target momentum (candidate #1).

Attempt 16 (2026-05-28) found vol-target-on-spread gave the best held-out
risk-adjusted result in the project (Sharpe ~1.3) BUT still BUST in-sample: a
21-day vol lookback reacted too slowly to the 2022 momentum crash, and even at
avg scale ~0.6-0.7 the 1.2-1.4x gross + simultaneous long/short loss sent NAV
negative before recovering.

This sweep tests the proposed fix (3 levers):
  1. FASTER vol signal: 5-day lookback (reacts within a week, not a month).
  2. LOWER target vol: 8% (cuts exposure harder when vol rises).
  3. HARD GROSS CAP: gross exposure (long$+short$)/NAV <= max_gross, i.e.
     per-leg scale <= max_gross/2. Caps leverage even in calm regimes so a
     sudden crash can't catch the book at full 2x.

Success = NO in-sample bust AND held-out mean Sharpe stays > 1.1.

Reuses the Attempt-16 engine helpers; only the scale computation changes
(adds the max_gross cap + configurable lookback).
"""
from __future__ import annotations

import json
import math
import statistics
import time
from datetime import date, timedelta
from pathlib import Path

from trading_bot.execution import market_data
from trading_bot.factors.universe import _build_index
from trading_bot.execution.factor_backtest import _trading_calendar, _rebalance_dates
from scripts.momentum.research.test_long_short_voltgt import (
    _mtm, _compute_realized_vol, _rebalance, _max_drawdown, _sharpe_by_year,
    STARTING_CASH, TOP_N, BOTTOM_N, HALF_SPREAD_BPS, BORROW_APY,
)

OUT_PATH = Path("var/data_audit/long_short_voltgt_crashfix.json")

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
# (label, vol_lookback, target_vol, max_gross)
CONFIGS = [
    ("full_fix_5d_t8_cap15",   5,  0.08, 1.5),
    ("fix_5d_t10_cap15",       5,  0.10, 1.5),
    ("fix_5d_t8_nocap",        5,  0.08, 2.0),   # isolate lookback (cap ~off)
    ("fix_21d_t8_cap15",      21,  0.08, 1.5),   # isolate cap (slow lookback)
]


def run_capped(*, since, until, vol_lookback, target_vol, max_gross,
               top_n=TOP_N, bottom_n=BOTTOM_N, starting_cash=STARTING_CASH,
               borrow_apy=BORROW_APY, half_spread_bps=HALF_SPREAD_BPS,
               rebalance_freq="M"):
    market_data.preload_caches()
    _build_index()
    calendar = _trading_calendar(since, until)
    rebal_set = set(d.isoformat() for d in _rebalance_dates(calendar, freq=rebalance_freq))
    half_spread_frac = half_spread_bps / 10_000.0
    borrow_daily = borrow_apy / 252.0
    scale_cap = max_gross / 2.0      # gross = 2*scale; cap scale to bound gross

    positions: dict = {}
    cash = starting_cash
    equity_curve = []
    daily_returns: list[float] = []
    scale_history: list[float] = []
    prev_nav = starting_cash
    bust_flag = 0
    total_rebals = 0

    cur = since
    while cur <= until:
        if cur in calendar:
            iso = cur.isoformat()
            if iso in rebal_set:
                pre_nav = cash + _mtm(positions, cur)
                if pre_nav <= 0:
                    bust_flag = 1
                    equity_curve.append((iso, pre_nav))
                    cur += timedelta(days=1)
                    continue
                realized_vol = _compute_realized_vol(daily_returns, vol_lookback)
                if realized_vol is None or realized_vol <= 0:
                    scale = scale_cap        # not enough history: start capped, not full 2x
                else:
                    scale = min(scale_cap, target_vol / realized_vol)
                scale_history.append(scale)
                per_leg = pre_nav * scale
                positions, cash, _, _ = _rebalance(
                    as_of=cur, positions=positions, cash=cash,
                    top_n=top_n, bottom_n=bottom_n,
                    half_spread_frac=half_spread_frac,
                    long_dollar=per_leg, short_dollar=per_leg,
                )
                total_rebals += 1
            short_notional = sum(abs(p["qty"] * p["entry_price"])
                                 for p in positions.values() if p["qty"] < 0)
            cash -= short_notional * borrow_daily
            nav = cash + _mtm(positions, cur)
            equity_curve.append((iso, nav))
            if prev_nav > 0:
                daily_returns.append(nav / prev_nav - 1.0)
            prev_nav = nav
        cur += timedelta(days=1)

    return {
        "equity_curve": equity_curve,
        "ending_nav": cash + _mtm(positions, until),
        "scale_history": scale_history,
        "bust": bool(bust_flag),
        "total_rebals": total_rebals,
    }


def run_one(window_label, since, until, label, lookback, target, max_gross):
    print(f"  >>> {label}_{window_label}", flush=True)
    t0 = time.time()
    r = run_capped(since=since, until=until, vol_lookback=lookback,
                   target_vol=target, max_gross=max_gross)
    curve = r["equity_curve"]
    years = (until - since).days / 365.25
    start_v, end_v = curve[0][1], curve[-1][1]
    bust = end_v <= 0 or r["bust"] or min(v for _, v in curve) <= 0
    cagr = ((end_v / start_v) ** (1 / years) - 1) * 100 if not bust else None
    sh = _sharpe_by_year(curve)
    mean_sh = statistics.fmean(sh.values()) if sh else 0.0
    avg_scale = statistics.fmean(r["scale_history"]) if r["scale_history"] else 0.0
    min_nav = min(v for _, v in curve)
    res = {
        "label": label, "window": window_label, "lookback": lookback,
        "target_vol": target, "max_gross": max_gross,
        "cagr_pct": cagr, "mean_sharpe": mean_sh,
        "max_dd_pct": _max_drawdown(curve), "bust": bust,
        "min_nav": min_nav, "ending_nav": r["ending_nav"],
        "avg_scale": avg_scale, "elapsed_sec": round(time.time() - t0, 1),
    }
    tag = "BUST" if bust else f"{cagr:+.2f}%"
    print(f"      {tag}  Sharpe {mean_sh:+.3f}  DD {res['max_dd_pct']:+.1f}%  "
          f"minNAV ${min_nav:,.0f}  avgScale {avg_scale:.2f}  ({res['elapsed_sec']}s)",
          flush=True)
    return res


def main() -> int:
    print("LONG-SHORT VOL-TARGET — CRASH-FIX SWEEP (5d lookback / low target / gross cap)")
    print(f"  {len(CONFIGS)} configs x {len(WINDOWS)} windows")
    print("=" * 80, flush=True)
    runs = []
    for wl, since, until in WINDOWS:
        for label, lb, tv, mg in CONFIGS:
            runs.append(run_one(wl, since, until, label, lb, tv, mg))

    print("\n" + "=" * 100)
    print("  CRASH-FIX RESULTS (goal: NO in-sample bust AND held-out Sharpe > 1.1)")
    print("  Reference: Attempt-16 21d/t10-16 BUST in-sample; held-out Sharpe ~1.3")
    print("=" * 100)
    for wl, _, _ in WINDOWS:
        print(f"\n  {wl.upper()}")
        print(f"  {'config':<24} {'CAGR':>9} {'Sharpe':>8} {'maxDD':>9} "
              f"{'minNAV':>12} {'avgScale':>9}")
        print("  " + "-" * 80)
        for r in runs:
            if r["window"] != wl:
                continue
            cagr = "BUST" if r["bust"] else f"{r['cagr_pct']:+.2f}%"
            print(f"  {r['label']:<24} {cagr:>9} {r['mean_sharpe']:>+7.3f} "
                  f"{r['max_dd_pct']:>+8.2f}% {r['min_nav']:>11,.0f} {r['avg_scale']:>8.2f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2, default=str))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
