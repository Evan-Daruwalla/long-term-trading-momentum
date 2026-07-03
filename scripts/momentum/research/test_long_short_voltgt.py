"""Long-short momentum with vol-target-on-spread (Barroso & Santa-Clara 2015).

Academic fix for momentum crashes. At each rebal:
  scale = min(1.0, target_vol / realized_spread_vol_21d)
  deploy: long $ = short $ = scale * NAV

When realized spread vol is calm (~10-12%), scale=1, full 2x leverage.
When spread vol spikes (crash warning), scale drops to 0.3-0.5, exposure cut.

Hypothesis: this should AVOID the in-sample bust while preserving most of
the held-out edge.

Sweep: target_vol in {0.10, 0.12, 0.16} x 2 windows = 6 runs.
Borrow fixed at 2%/yr.

Tracks spread returns in memory as the backtest runs (no pre-pass needed,
unlike portfolio-vol fine-tune — here we track the LIVE strategy's own returns).
"""
from __future__ import annotations

import json
import math
import statistics
import time
from datetime import date, timedelta
from pathlib import Path

from trading_bot.execution import market_data
from trading_bot.factors import momentum
from trading_bot.factors.universe import (
    _build_index, _ticker_close_on, tradeable_universe,
)
from trading_bot.execution.factor_backtest import (
    _trading_calendar, _rebalance_dates,
)

OUT_PATH = Path("var/data_audit/long_short_voltgt.json")
STARTING_CASH = 100_000.0
TOP_N = 50
BOTTOM_N = 50
HALF_SPREAD_BPS = 5.0
BORROW_APY = 0.02
VOL_LOOKBACK = 21

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
TARGET_VOLS = [0.10, 0.12, 0.16]

# Long-only baseline
LONG_ONLY = {
    "in_sample": {"cagr": 2.72, "max_dd": -55.26, "sharpe": 0.167},
    "holdout":   {"cagr": 28.81, "max_dd": -33.86, "sharpe": 0.903},
}
# Plain long-short (no vol-target) for comparison
LS_PLAIN = {
    "in_sample": {"status": "BUST", "max_dd": -106.3},
    "holdout":   {"cagr": 45.58, "max_dd": -51.11, "sharpe": 1.039},
}


def _close_on(ticker, as_of):
    _, px = _ticker_close_on(ticker, as_of)
    return px if (px is not None and px > 0) else None


def _mtm(positions, as_of):
    total = 0.0
    for ticker, pos in positions.items():
        px = _close_on(ticker, as_of)
        if px is None:
            px = pos["entry_price"]
        total += pos["qty"] * px
    return total


def _compute_realized_vol(daily_returns: list[float], lookback: int) -> float | None:
    """Annualized stdev of last `lookback` daily returns. None if insufficient."""
    if len(daily_returns) < lookback:
        return None
    tail = daily_returns[-lookback:]
    sd = statistics.pstdev(tail)
    return sd * math.sqrt(252)


def _rebalance(*, as_of, positions, cash, top_n, bottom_n, half_spread_frac,
               long_dollar, short_dollar):
    """Close all, open longs at long_dollar / top_n each, shorts at short_dollar / bottom_n.
    Returns new (positions, cash, n_longs_opened, n_shorts_opened)."""
    # Close existing
    for ticker, pos in list(positions.items()):
        px = _close_on(ticker, as_of)
        if px is None:
            continue
        if pos["qty"] > 0:
            fill = px * (1.0 - half_spread_frac)
            cash += pos["qty"] * fill
        else:
            fill = px * (1.0 + half_spread_frac)
            cash += pos["qty"] * fill
    positions = {}

    if long_dollar <= 0 and short_dollar <= 0:
        # vol-target=0: stay flat for this rebal period
        return positions, cash, 0, 0

    universe = tradeable_universe(as_of)
    scored = momentum.rank_universe(universe, as_of)
    if len(scored) < top_n + bottom_n:
        return positions, cash, 0, 0
    longs = [t for t, _ in scored[:top_n]]
    shorts = [t for t, _ in scored[-bottom_n:]]

    n_long = n_short = 0
    if long_dollar > 0:
        per = long_dollar / top_n
        for ticker in longs:
            px = _close_on(ticker, as_of)
            if px is None: continue
            fill = px * (1.0 + half_spread_frac)
            qty = per / fill
            if qty <= 0: continue
            positions[ticker] = {"qty": qty, "entry_price": fill, "side": "long"}
            cash -= qty * fill
            n_long += 1

    if short_dollar > 0:
        per = short_dollar / bottom_n
        for ticker in shorts:
            px = _close_on(ticker, as_of)
            if px is None: continue
            fill = px * (1.0 - half_spread_frac)
            qty = -per / fill
            if qty >= 0: continue
            positions[ticker] = {"qty": qty, "entry_price": fill, "side": "short"}
            cash -= qty * fill
            n_short += 1

    return positions, cash, n_long, n_short


def run_ls_voltgt(*, since, until, top_n, bottom_n, starting_cash,
                  target_vol, vol_lookback, borrow_apy, half_spread_bps,
                  rebalance_freq="M"):
    market_data.preload_caches()
    _build_index()
    calendar = _trading_calendar(since, until)
    if not calendar:
        raise RuntimeError("No trading days")
    rebal_set = set(d.isoformat() for d in _rebalance_dates(calendar, freq=rebalance_freq))

    half_spread_frac = half_spread_bps / 10_000.0
    borrow_daily = borrow_apy / 252.0

    positions: dict = {}
    cash = starting_cash
    equity_curve = []
    daily_returns: list[float] = []  # for realized vol calc
    scale_history: list[tuple[str, float, float | None]] = []  # (date, scale, realized_vol)
    prev_nav = starting_cash
    total_long = total_short = total_rebals = bust_flag = 0

    cur = since
    while cur <= until:
        is_trading = cur in calendar
        if is_trading:
            iso = cur.isoformat()
            if iso in rebal_set:
                pre_nav = cash + _mtm(positions, cur)
                if pre_nav <= 0:
                    # Already bust, no more trading possible
                    bust_flag = 1
                    equity_curve.append((iso, pre_nav))
                    cur += timedelta(days=1)
                    continue
                # Compute scale from realized spread vol
                realized_vol = _compute_realized_vol(daily_returns, vol_lookback)
                if realized_vol is None or realized_vol <= 0:
                    scale = 1.0  # not enough history yet, full deploy
                else:
                    scale = min(1.0, target_vol / realized_vol)
                scale_history.append((iso, scale, realized_vol))
                target_per_leg = pre_nav * scale
                positions, cash, nl, ns = _rebalance(
                    as_of=cur, positions=positions, cash=cash,
                    top_n=top_n, bottom_n=bottom_n,
                    half_spread_frac=half_spread_frac,
                    long_dollar=target_per_leg, short_dollar=target_per_leg,
                )
                total_long += nl
                total_short += ns
                total_rebals += 1
            # Borrow fee on short notional
            short_notional = sum(abs(p["qty"] * p["entry_price"])
                                 for p in positions.values() if p["qty"] < 0)
            cash -= short_notional * borrow_daily
            # NAV
            nav = cash + _mtm(positions, cur)
            equity_curve.append((iso, nav))
            # Track daily return for vol calc
            if prev_nav > 0:
                daily_returns.append(nav / prev_nav - 1.0)
            prev_nav = nav
        cur += timedelta(days=1)

    return {
        "equity_curve": equity_curve,
        "scale_history": scale_history,
        "starting_cash": starting_cash,
        "ending_nav": cash + _mtm(positions, until),
        "total_rebals": total_rebals,
        "n_long": total_long, "n_short": total_short,
        "bust": bool(bust_flag),
    }


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


def run_one(window_label, since, until, target_vol):
    label = f"ls_voltgt{int(target_vol*100)}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    r = run_ls_voltgt(
        since=since, until=until,
        top_n=TOP_N, bottom_n=BOTTOM_N,
        starting_cash=STARTING_CASH,
        target_vol=target_vol, vol_lookback=VOL_LOOKBACK,
        borrow_apy=BORROW_APY, half_spread_bps=HALF_SPREAD_BPS,
    )
    curve = r["equity_curve"]
    years = (until - since).days/365.25
    start_v, end_v = curve[0][1], curve[-1][1]
    total_pct = (end_v/start_v - 1) * 100
    bust = end_v <= 0 or r["bust"]
    cagr = ((end_v/start_v) ** (1/years) - 1) * 100 if not bust else None
    sh = _sharpe_by_year(curve)
    mean_sh = statistics.fmean(sh.values()) if sh else 0.0
    avg_scale = statistics.fmean(s for _, s, _ in r["scale_history"]) if r["scale_history"] else 1.0
    min_scale = min((s for _, s, _ in r["scale_history"]), default=1.0)
    return {
        "label": label, "window": window_label, "target_vol": target_vol,
        "total_pct": total_pct, "cagr_pct": cagr, "bust": bust,
        "mean_sharpe": mean_sh, "max_dd_pct": _max_drawdown(curve),
        "avg_scale": avg_scale, "min_scale": min_scale,
        "n_rebals": r["total_rebals"], "ending_nav": r["ending_nav"],
        "elapsed_sec": round(time.time()-t0, 1),
    }


def main() -> int:
    print(f"LONG-SHORT MOMENTUM + VOL-TARGET-SPREAD (Barroso-Santa-Clara fix)")
    print(f"  {len(TARGET_VOLS)} targets x {len(WINDOWS)} windows = {len(TARGET_VOLS)*len(WINDOWS)} runs")
    print("=" * 70, flush=True)
    runs = []
    for window_label, since, until in WINDOWS:
        for tv in TARGET_VOLS:
            runs.append(run_one(window_label, since, until, tv))

    print("\n" + "=" * 100)
    print("  LONG-SHORT + VOL-TGT vs (long-only baseline / plain LS / new variant)")
    print("=" * 100)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        lo = LONG_ONLY[window_label]
        ls = LS_PLAIN[window_label]
        print(f"  {'config':<26} {'CAGR':>8} {'Sharpe':>8} {'maxDD':>9} "
              f"{'avgScale':>10} {'minScale':>10}")
        print("  " + "-" * 80)
        print(f"  {'mom_v2 long-only':<26} {lo['cagr']:>+7.2f}% "
              f"{lo['sharpe']:>+7.3f} {lo['max_dd']:>+8.2f}%   --         --")
        if ls.get("status") == "BUST":
            print(f"  {'ls plain (no voltgt)':<26}    BUST                "
                  f"{ls['max_dd']:>+8.2f}%   --         --")
        else:
            print(f"  {'ls plain (no voltgt)':<26} {ls['cagr']:>+7.2f}% "
                  f"{ls['sharpe']:>+7.3f} {ls['max_dd']:>+8.2f}%   --         --")
        for r in runs:
            if r["window"] != window_label: continue
            if r["bust"]:
                print(f"  {r['label']:<26}  BUST (NAV {r['ending_nav']:+,.0f})  "
                      f"DD {r['max_dd_pct']:+.1f}%  avgScale {r['avg_scale']:.2f}")
            else:
                print(f"  {r['label']:<26} {r['cagr_pct']:>+7.2f}% "
                      f"{r['mean_sharpe']:>+7.3f} {r['max_dd_pct']:>+8.2f}%   "
                      f"{r['avg_scale']:>9.2f}  {r['min_scale']:>9.2f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2, default=str))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
