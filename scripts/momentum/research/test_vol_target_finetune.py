"""Fine-tune vol-target: test portfolio-vol signal + shorter/longer lookbacks.

After the original vol-target sweep showed minimal benefit (-0.3 to -0.4pp
CAGR for +0.7 to +3.3pp DD), the question is whether the SIGNAL itself is
suboptimal. Specifically:

1. SPY-vol underestimates momentum portfolio vol (mom ~ 1.5-2x SPY).
   If we use portfolio's OWN realized vol, the scaler can target the
   actual risk rather than a proxy.

2. 21-day lookback might be too slow. Shorter (10-day) reacts faster to
   vol spikes; longer (60-day) is smoother.

Variants:
  A. SPY-vol 10d  @ target 16%   (faster reaction, SPY signal)
  B. SPY-vol 21d  @ target 16%   (current default — known result)
  C. SPY-vol 60d  @ target 16%   (smoother, SPY signal)
  D. Port-vol 10d @ target 25%   (faster reaction, port signal)
  E. Port-vol 21d @ target 25%   (current lookback, port signal)
  F. Port-vol 60d @ target 25%   (smoother, port signal)

6 configs x 2 windows = 12 runs, ~10 min total.

Portfolio-vol lookup: pre-computed from a baseline mom_v2 run; cached so
the sweep only does one pre-pass.

Success criteria:
  - Any variant beats baseline mom_v2 (+2.72% in / +28.81% hold CAGR)
    on BOTH windows simultaneously by >=1pp CAGR or >=5pp DD reduction
  - Otherwise: confirm prior verdict that vol-target tweaks don't matter
"""
from __future__ import annotations

import json
import math
import statistics
import time
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum
from trading_bot.factors.universe import close_at_offset

OUT_PATH = Path("var/data_audit/vol_target_finetune.json")
STARTING_CASH = 100_000.0
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]

BASELINE = {
    "in_sample": {"cagr": 2.72, "max_dd": -55.26, "sharpe": 0.167},
    "holdout":   {"cagr": 28.81, "max_dd": -33.86, "sharpe": 0.903},
}


# --- SPY-vol helpers (same as test_vol_target_clean.py) ----------------------

@lru_cache(maxsize=16384)
def _spy_close(as_of_iso: str, offset: int) -> float | None:
    return close_at_offset("SPY", date.fromisoformat(as_of_iso), offset)


def _spy_realized_vol(as_of: date, lookback: int) -> float | None:
    iso = as_of.isoformat()
    closes = []
    for i in range(lookback + 1):
        c = _spy_close(iso, -i)
        if c is None: return None
        closes.append(c)
    closes.reverse()
    rets = [closes[i+1]/closes[i] - 1.0 for i in range(len(closes)-1)]
    if len(rets) < 5: return None
    sd = statistics.pstdev(rets)
    return sd * math.sqrt(252)


def make_spy_vol_scaler(target_vol: float, lookback: int):
    def scaler(as_of: date) -> float:
        rv = _spy_realized_vol(as_of, lookback)
        if rv is None or rv <= 0:
            return 1.0
        return min(1.0, target_vol / rv)
    return scaler


# --- Portfolio-vol: pre-pass run to get the strategy's own daily returns -----

_PORT_RET_BY_DATE: dict[str, float] | None = None
_PORT_DATES_SORTED: list[str] | None = None


def _build_portfolio_returns():
    """One-time: run baseline mom_v2 (no overlay), extract daily returns.
    Populates module-level dicts used by port_vol_scaler."""
    global _PORT_RET_BY_DATE, _PORT_DATES_SORTED
    if _PORT_RET_BY_DATE is not None:
        return
    print("  [pre-pass] running baseline mom_v2 for portfolio-vol lookup...",
          flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    # Use the FULL span (in-sample start through held-out end) so we have
    # vol data covering both windows.
    r = factor_backtest.run_factor_backtest(
        since=date(2014, 6, 1),   # start ~6mo earlier so 252-day vol lookbacks work from 2015
        until=date(2026, 5, 1),
        top_n=TOP_N, starting_cash=STARTING_CASH,
        rank_fn=momentum.rank_universe, rebalance_freq="M",
    )
    curve = r.equity_curve
    _PORT_RET_BY_DATE = {}
    prev_val = None
    for iso, val in curve:
        if prev_val is not None and prev_val > 0:
            _PORT_RET_BY_DATE[iso] = val / prev_val - 1.0
        prev_val = val
    _PORT_DATES_SORTED = sorted(_PORT_RET_BY_DATE.keys())
    print(f"  [pre-pass] {len(_PORT_RET_BY_DATE)} daily returns captured, "
          f"{time.time()-t0:.0f}s", flush=True)


def _port_realized_vol(as_of: date, lookback: int) -> float | None:
    """Portfolio's own realized vol over the past `lookback` trading days."""
    if _PORT_DATES_SORTED is None:
        return None
    iso = as_of.isoformat()
    # Find the last date in our lookup that's <= as_of
    import bisect
    i = bisect.bisect_right(_PORT_DATES_SORTED, iso) - 1
    if i < lookback:
        return None
    rets = [_PORT_RET_BY_DATE[_PORT_DATES_SORTED[j]]
            for j in range(i - lookback + 1, i + 1)]
    if len(rets) < 5:
        return None
    sd = statistics.pstdev(rets)
    return sd * math.sqrt(252)


def make_port_vol_scaler(target_vol: float, lookback: int):
    def scaler(as_of: date) -> float:
        rv = _port_realized_vol(as_of, lookback)
        if rv is None or rv <= 0:
            return 1.0
        return min(1.0, target_vol / rv)
    return scaler


# --- Sweep mechanics --------------------------------------------------------

def _max_drawdown(curve):
    peak = curve[0][1]
    max_dd = 0.0
    for _, val in curve:
        if val > peak: peak = val
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


# config: (label, scaler_factory, target, lookback)
CONFIGS = [
    ("spy_10d_t16",  "spy",  0.16, 10),
    ("spy_21d_t16",  "spy",  0.16, 21),
    ("spy_60d_t16",  "spy",  0.16, 60),
    ("port_10d_t25", "port", 0.25, 10),
    ("port_21d_t25", "port", 0.25, 21),
    ("port_60d_t25", "port", 0.25, 60),
]


def run_one(window_label, since, until, cfg_name, signal_src, target, lookback):
    label = f"{cfg_name}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0

    if signal_src == "spy":
        scaler = make_spy_vol_scaler(target, lookback)
    elif signal_src == "port":
        scaler = make_port_vol_scaler(target, lookback)
    else:
        raise ValueError(signal_src)

    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N, starting_cash=STARTING_CASH,
        rank_fn=momentum.rank_universe, rebalance_freq="M",
        position_scale_fn=scaler,
    )
    curve = r.equity_curve
    total_pct = (curve[-1][1]/curve[0][1] - 1) * 100
    years = (until - since).days/365.25
    cagr = ((curve[-1][1]/curve[0][1]) ** (1/years) - 1) * 100
    sh = _sharpe_by_year(curve)
    mean_sh = statistics.fmean(sh.values()) if sh else 0.0
    max_dd = _max_drawdown(curve)
    return {
        "label": label, "window": window_label,
        "signal": signal_src, "target_vol": target, "lookback": lookback,
        "total_pct": total_pct, "cagr_pct": cagr,
        "mean_sharpe": mean_sh, "max_dd_pct": max_dd,
        "closed": r.closed_count, "elapsed_sec": round(time.time()-t0, 1),
    }


def main() -> int:
    print(f"VOL-TARGET FINE-TUNE: {len(CONFIGS)} configs x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)

    _build_portfolio_returns()

    runs = []
    for window_label, since, until in WINDOWS:
        for cfg_name, signal_src, target, lookback in CONFIGS:
            runs.append(run_one(window_label, since, until,
                                cfg_name, signal_src, target, lookback))

    print("\n" + "=" * 95)
    print("  VOL-TARGET FINE-TUNE  vs  baseline mom_v2 (no overlay)")
    print("=" * 95)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        b = BASELINE[window_label]
        print(f"  {'config':<24} {'CAGR':>8} {'Sharpe':>8} {'maxDD':>9} "
              f"{'d_cagr':>8} {'d_dd':>8} {'d_sharpe':>10}")
        print("  " + "-" * 80)
        print(f"  {'baseline (no overlay)':<24} {b['cagr']:>+7.2f}% "
              f"{b['sharpe']:>+7.3f} {b['max_dd']:>+8.2f}%   (reference)")
        for r in runs:
            if r["window"] != window_label: continue
            d_c = r["cagr_pct"] - b["cagr"]
            d_d = r["max_dd_pct"] - b["max_dd"]
            d_s = r["mean_sharpe"] - b["sharpe"]
            print(f"  {r['label']:<24} {r['cagr_pct']:>+7.2f}% "
                  f"{r['mean_sharpe']:>+7.3f} {r['max_dd_pct']:>+8.2f}%  "
                  f"{d_c:>+7.2f}pp {d_d:>+7.2f}pp {d_s:>+9.3f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
