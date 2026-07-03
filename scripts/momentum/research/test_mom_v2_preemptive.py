"""Test mom_v2 with PREEMPTIVE risk overlays (Trend Filter and Vol-Target).

After Attempts 12 (plain stops) and 13 (stops + reentry) both failed,
this tests the two structural alternatives:

1. Trend filter (SPY > 200-DMA): when SPY closes below its 200-day SMA on
   a rebal day, return empty target set -> sell all, hold cash. Re-deploy
   on next rebal where SPY is back above the SMA. Cuts exposure to bear
   markets entirely (Faber 2007 "Quantitative Approach to Tactical AA").

2. Vol-target (Moreira & Muir 2017): scale position size by
   min(1, target_vol / realized_spy_vol_21d). When realized vol rises
   above target, hold less equity; when calm, hold full top-50.

Both are PREEMPTIVE (size cut BEFORE losses materialize) rather than
REACTIVE (stops after losses). The hypothesis is that vol rises BEFORE
crashes (vol clustering), so this catches the move where stops can't.

Sweep: 4 configs x 2 windows = 8 runs:
  - trend filter alone
  - vol-target 16% (long-run SPY vol)
  - vol-target 20% (close to mom's natural vol -> only cuts in extremes)
  - combined: trend filter + vol-target 16%

Success criteria:
  - In-sample CAGR within 2pp of baseline +21%/yr (no big regression)
  - Held-out CAGR within 2pp of baseline +26.47%/yr
  - At least one config: max DD < -25% on BOTH windows (improves -36/-34)
"""
from __future__ import annotations

import json
import math
import statistics
import time
from datetime import date
from functools import lru_cache
from pathlib import Path

from trading_bot.execution import factor_backtest
from trading_bot.factors import momentum
from trading_bot.factors.universe import close_at_offset

OUT_PATH = Path("var/momentum/mom_v2_preemptive_test.json")
STARTING_CASH = 100_000.0
TOP_N = 50

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]

# Baseline references for diff columns — POST-AUDIT clean values (2026-05-28)
MOM_V2 = {
    "in_sample": {"cagr": 2.72, "max_dd": -55.26},
    "holdout":   {"cagr": 28.81, "max_dd": -33.86},
}


@lru_cache(maxsize=4096)
def _spy_close(as_of_iso: str, offset: int) -> float | None:
    return close_at_offset("SPY", date.fromisoformat(as_of_iso), offset)


def _spy_sma(as_of: date, lookback: int = 200) -> float | None:
    iso = as_of.isoformat()
    closes = []
    for i in range(lookback):
        c = _spy_close(iso, -i)
        if c is None:
            return None
        closes.append(c)
    return sum(closes) / len(closes)


def _spy_realized_vol(as_of: date, lookback: int = 21) -> float | None:
    """Annualized realized vol from last `lookback` daily returns."""
    iso = as_of.isoformat()
    closes = []
    for i in range(lookback + 1):  # need N+1 closes for N returns
        c = _spy_close(iso, -i)
        if c is None:
            return None
        closes.append(c)
    closes.reverse()  # oldest first
    rets = [closes[i+1] / closes[i] - 1.0 for i in range(len(closes) - 1)]
    if len(rets) < 5:
        return None
    sd = statistics.pstdev(rets)
    return sd * math.sqrt(252)


def make_trend_filtered_ranker(base_rank_fn, sma_days: int = 200):
    """Wraps a rank_fn. When SPY < SMA on as_of, returns []."""
    def filtered(tickers, as_of):
        spy_today = _spy_close(as_of.isoformat(), 0)
        sma = _spy_sma(as_of, sma_days)
        if spy_today is None or sma is None:
            return base_rank_fn(tickers, as_of)  # fail open if no data
        if spy_today < sma:
            return []
        return base_rank_fn(tickers, as_of)
    filtered.__name__ = f"{base_rank_fn.__name__}_trend{sma_days}"
    return filtered


def make_vol_target_scaler(target_vol: float, lookback: int = 21):
    """Returns a position_scale_fn that scales by min(1, target/realized)."""
    def scaler(as_of: date) -> float:
        rv = _spy_realized_vol(as_of, lookback)
        if rv is None or rv <= 0:
            return 1.0  # fail open
        return min(1.0, target_vol / rv)
    scaler.__name__ = f"voltgt_{int(target_vol*100)}pct"
    return scaler


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


def _max_drawdown(curve):
    peak = curve[0][1]
    max_dd = 0.0
    for _, val in curve:
        if val > peak:
            peak = val
        dd = (val / peak - 1.0) * 100
        if dd < max_dd:
            max_dd = dd
    return max_dd


CONFIGS = [
    ("trend200",       lambda: dict(rank_fn=make_trend_filtered_ranker(momentum.rank_universe, 200))),
    ("voltgt16",       lambda: dict(rank_fn=momentum.rank_universe,
                                    position_scale_fn=make_vol_target_scaler(0.16))),
    ("voltgt20",       lambda: dict(rank_fn=momentum.rank_universe,
                                    position_scale_fn=make_vol_target_scaler(0.20))),
    ("trend200_vt16",  lambda: dict(rank_fn=make_trend_filtered_ranker(momentum.rank_universe, 200),
                                    position_scale_fn=make_vol_target_scaler(0.16))),
]


def run_one(window_label: str, since: date, until: date,
            cfg_name: str, cfg_factory) -> dict:
    label = f"mom_v2_{cfg_name}_{window_label}"
    print(f"  >>> {label}", flush=True)
    t0 = time.time()
    factor_backtest.HALF_SPREAD_BPS = 5.0
    kw = cfg_factory()
    r = factor_backtest.run_factor_backtest(
        since=since, until=until,
        top_n=TOP_N, starting_cash=STARTING_CASH,
        rebalance_freq="M",
        **kw,
    )
    curve = r.equity_curve
    years = (until - since).days / 365.25
    total_pct = (curve[-1][1] / curve[0][1] - 1) * 100
    cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
    sh = _sharpe_by_year(curve)
    max_dd = _max_drawdown(curve)
    return {
        "label":         label,
        "window":        window_label,
        "config":        cfg_name,
        "total_pnl_pct": total_pct,
        "cagr_pct":      cagr,
        "mean_sharpe":   statistics.fmean(sh.values()) if sh else 0.0,
        "max_dd_pct":    max_dd,
        "closed":        r.closed_count,
        "open":          r.open_count,
        "elapsed_sec":   round(time.time() - t0, 1),
    }


def main() -> int:
    print(f"MOM_V2 PREEMPTIVE OVERLAYS: {len(CONFIGS)} configs x {len(WINDOWS)} windows")
    print("=" * 70, flush=True)
    runs: list[dict] = []
    for window_label, since, until in WINDOWS:
        for cfg_name, cfg_factory in CONFIGS:
            runs.append(run_one(window_label, since, until, cfg_name, cfg_factory))

    print("\n" + "=" * 90)
    print("  MOM_V2 + PREEMPTIVE RISK OVERLAYS  vs  baseline (no overlay)")
    print("=" * 90)
    for window_label, since, until in WINDOWS:
        print(f"\n  {window_label.upper()}")
        print(f"  {'config':<28} {'total %':>10} {'CAGR %':>9} {'mean Shrp':>10} "
              f"{'max DD':>9}")
        print("  " + "-" * 75)
        v2 = MOM_V2[window_label]
        print(f"  {'mom_v2 (no overlay)':<28} {'':>10} {v2['cagr']:>+8.2f}%   "
              f"(baseline) {v2['max_dd']:>+8.1f}%")
        for r in runs:
            if r["window"] != window_label:
                continue
            d_cagr = r["cagr_pct"] - v2["cagr"]
            d_dd = r["max_dd_pct"] - v2["max_dd"]
            print(f"  {r['label']:<28} {r['total_pnl_pct']:>+9.2f}% "
                  f"{r['cagr_pct']:>+8.2f}% {r['mean_sharpe']:>+10.3f} "
                  f"{r['max_dd_pct']:>+8.2f}%   d_cagr={d_cagr:+.1f}pp  d_dd={d_dd:+.1f}pp")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
