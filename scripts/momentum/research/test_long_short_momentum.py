"""Long-short market-neutral momentum (academic AQR-style).

Long top-50 by 12-1 momentum, short bottom-50 by same signal. Same
universe (tradeable_universe with $5 + max_hist_ratio filter applies
to BOTH legs). Equal-weight within each leg, dollar-neutral
(long $ = short $ = starting_cash), so 2x gross / 0 net.

Borrow fee on short leg applied daily (default 2%/yr — middle of the
range for momentum-loser cohort; can be 5-50% for microcap names).

Standalone — does NOT use the production factor_backtest engine or
the paper-trade DB. Tracks positions in an in-memory dict.

Output: equity curve, total return, CAGR, max DD, mean yearly Sharpe.

Sweep: borrow_apy in {1, 2, 5}% x 2 windows = 6 runs, ~3 min.
"""
from __future__ import annotations

import json
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

OUT_PATH = Path("var/data_audit/long_short_momentum.json")
STARTING_CASH = 100_000.0
TOP_N = 50
BOTTOM_N = 50
HALF_SPREAD_BPS = 5.0

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
BORROW_APYS = [0.01, 0.02, 0.05]

# Baselines for diff columns (long-only mom_v2, clean data)
LONG_ONLY = {
    "in_sample": {"cagr": 2.72, "max_dd": -55.26, "sharpe": 0.167},
    "holdout":   {"cagr": 28.81, "max_dd": -33.86, "sharpe": 0.903},
}


def _close_on(ticker: str, as_of: date) -> float | None:
    _, px = _ticker_close_on(ticker, as_of)
    return px if (px is not None and px > 0) else None


def _mtm(positions: dict, as_of: date) -> float:
    """Sum qty * close (qty can be negative for shorts). Falls back to
    entry_price if no close available (rare on clean data)."""
    total = 0.0
    for ticker, pos in positions.items():
        px = _close_on(ticker, as_of)
        if px is None:
            px = pos["entry_price"]
        total += pos["qty"] * px
    return total


def _rebalance(*, as_of: date, positions: dict, cash: float,
               top_n: int, bottom_n: int, half_spread_frac: float,
               long_target_dollar: float, short_target_dollar: float
               ) -> tuple[dict, float, int, int]:
    """Returns (new_positions, new_cash, n_changes_long, n_changes_short).

    Closes all existing positions at today's close +/- spread, then opens
    new long top-N and short bottom-N at today's close +/- spread.
    Equal $ within each leg.
    """
    # 1) Close everything
    for ticker, pos in list(positions.items()):
        px = _close_on(ticker, as_of)
        if px is None:
            continue
        if pos["qty"] > 0:        # long position - sell at close*(1-spread)
            fill = px * (1.0 - half_spread_frac)
            cash += pos["qty"] * fill
        else:                     # short position - cover at close*(1+spread)
            fill = px * (1.0 + half_spread_frac)
            cash += pos["qty"] * fill   # qty is negative; this DEDUCTS from cash
    positions = {}

    # 2) Rank universe
    universe = tradeable_universe(as_of)
    scored = momentum.rank_universe(universe, as_of)
    if len(scored) < top_n + bottom_n:
        return positions, cash, 0, 0
    longs = [t for t, _ in scored[:top_n]]
    shorts = [t for t, _ in scored[-bottom_n:]]

    # 3) Open longs (equal $)
    n_long = 0
    dollar_per_long = long_target_dollar / top_n
    for ticker in longs:
        px = _close_on(ticker, as_of)
        if px is None:
            continue
        fill = px * (1.0 + half_spread_frac)
        qty = dollar_per_long / fill
        if qty <= 0:
            continue
        positions[ticker] = {"qty": qty, "entry_price": fill, "side": "long"}
        cash -= qty * fill
        n_long += 1

    # 4) Open shorts (equal $, negative qty)
    n_short = 0
    dollar_per_short = short_target_dollar / bottom_n
    for ticker in shorts:
        px = _close_on(ticker, as_of)
        if px is None:
            continue
        fill = px * (1.0 - half_spread_frac)   # selling short, hits the bid
        qty = -dollar_per_short / fill         # negative qty
        if qty >= 0:
            continue
        positions[ticker] = {"qty": qty, "entry_price": fill, "side": "short"}
        cash -= qty * fill   # qty is negative, so this ADDS cash (short proceeds)
        n_short += 1

    return positions, cash, n_long, n_short


def run_long_short(*, since: date, until: date,
                   top_n: int, bottom_n: int,
                   starting_cash: float,
                   borrow_apy: float,
                   half_spread_bps: float,
                   rebalance_freq: str = "M") -> dict:
    """One long-short backtest. Returns dict with equity_curve, totals."""
    market_data.preload_caches()
    _build_index()
    calendar = _trading_calendar(since, until)
    if not calendar:
        raise RuntimeError("No trading days cached in range")
    rebal_set = set(d.isoformat() for d in _rebalance_dates(calendar, freq=rebalance_freq))

    half_spread_frac = half_spread_bps / 10_000.0
    borrow_daily = borrow_apy / 252.0  # apply on trading days; ~252/yr

    positions: dict = {}
    cash = starting_cash
    equity_curve: list[tuple[str, float]] = []
    total_long_buys = total_short_sells = total_rebals = 0

    cur = since
    while cur <= until:
        is_trading = cur in calendar
        if is_trading:
            iso = cur.isoformat()
            if iso in rebal_set:
                # NAV before rebal = current MTM
                pre_nav = cash + _mtm(positions, cur)
                # Each leg sized to current NAV (2x gross / 0 net)
                positions, cash, nl, ns = _rebalance(
                    as_of=cur, positions=positions, cash=cash,
                    top_n=top_n, bottom_n=bottom_n,
                    half_spread_frac=half_spread_frac,
                    long_target_dollar=pre_nav,
                    short_target_dollar=pre_nav,
                )
                total_long_buys += nl
                total_short_sells += ns
                total_rebals += 1
            # Apply borrow fee on short leg notional (sum of |qty| * entry for shorts)
            short_notional = sum(abs(p["qty"] * p["entry_price"])
                                 for p in positions.values() if p["qty"] < 0)
            cash -= short_notional * borrow_daily
            # Record NAV
            equity_curve.append((iso, cash + _mtm(positions, cur)))
        cur += timedelta(days=1)

    final_nav = cash + _mtm(positions, until)
    return {
        "equity_curve": equity_curve,
        "starting_cash": starting_cash,
        "ending_nav": final_nav,
        "total_rebals": total_rebals,
        "total_long_buys": total_long_buys,
        "total_short_sells": total_short_sells,
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


def run_one(window_label, since, until, borrow_apy):
    label = f"ls_borrow{int(borrow_apy*100)}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    r = run_long_short(
        since=since, until=until,
        top_n=TOP_N, bottom_n=BOTTOM_N,
        starting_cash=STARTING_CASH,
        borrow_apy=borrow_apy,
        half_spread_bps=HALF_SPREAD_BPS,
    )
    curve = r["equity_curve"]
    years = (until - since).days/365.25
    start_v = curve[0][1]
    end_v = curve[-1][1]
    total_pct = (end_v/start_v - 1) * 100
    if end_v <= 0:
        # Strategy went bust during this window. Report as -100% CAGR for
        # comparability — the actual number is undefined (negative^(1/y)).
        cagr = float("nan")
        bust = True
    else:
        cagr = ((end_v/start_v) ** (1/years) - 1) * 100
        bust = False
    sh = _sharpe_by_year(curve)
    mean_sh = statistics.fmean(sh.values()) if sh else 0.0
    return {
        "label": label, "window": window_label, "borrow_apy": borrow_apy,
        "total_pct": total_pct,
        "cagr_pct": cagr if not bust else None,
        "bust": bust,
        "mean_sharpe": mean_sh, "max_dd_pct": _max_drawdown(curve),
        "n_rebals": r["total_rebals"],
        "n_long_buys": r["total_long_buys"],
        "n_short_sells": r["total_short_sells"],
        "ending_nav": r["ending_nav"],
        "elapsed_sec": round(time.time()-t0, 1),
    }


def main() -> int:
    print(f"LONG-SHORT MOMENTUM: {len(BORROW_APYS)} borrow levels x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)
    runs = []
    for window_label, since, until in WINDOWS:
        for ba in BORROW_APYS:
            runs.append(run_one(window_label, since, until, ba))

    print("\n" + "=" * 95)
    print("  LONG-SHORT MOMENTUM  vs  mom_v2 long-only baseline")
    print("=" * 95)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        b = LONG_ONLY[window_label]
        print(f"  {'config':<24} {'CAGR':>8} {'Sharpe':>8} {'maxDD':>9} "
              f"{'d_cagr':>8} {'d_dd':>8} {'d_sharpe':>10}")
        print("  " + "-" * 80)
        print(f"  {'mom_v2 long-only':<24} {b['cagr']:>+7.2f}% "
              f"{b['sharpe']:>+7.3f} {b['max_dd']:>+8.2f}%   (reference)")
        for r in runs:
            if r["window"] != window_label: continue
            if r["bust"]:
                print(f"  {r['label']:<24}  BUST (ending NAV {r['ending_nav']:+,.0f}, "
                      f"total {r['total_pct']:+.1f}%, max DD {r['max_dd_pct']:+.1f}%) "
                      f"-- 2x leverage + momentum crash = capital wiped")
                continue
            d_c = r["cagr_pct"] - b["cagr"]
            d_d = r["max_dd_pct"] - b["max_dd"]
            d_s = r["mean_sharpe"] - b["sharpe"]
            print(f"  {r['label']:<24} {r['cagr_pct']:>+7.2f}% "
                  f"{r['mean_sharpe']:>+7.3f} {r['max_dd_pct']:>+8.2f}%  "
                  f"{d_c:>+7.2f}pp {d_d:>+7.2f}pp {d_s:>+9.3f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # cagr_pct is None for bust runs; default JSON handles None fine
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2, default=str))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
