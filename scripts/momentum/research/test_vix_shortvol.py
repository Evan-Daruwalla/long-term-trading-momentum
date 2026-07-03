"""Candidate #2: VIX-term-structure-gated short-volatility sleeve.

Hold SVXY (inverse short-term VIX futures) ONLY when both:
  (a) VIX term structure in contango: VIX <= VIX3M (front below back) — the
      ~80%-of-the-time state where the roll yield favors short-vol, AND
  (b) SPY > its long SMA (200 or 275 day) — risk-on equity regime.
Else hold cash (T-bill rate). Decided at the prior close, applied next day.

Single-asset timing sim. Uses ACTUAL SVXY closes.

CAVEAT: SVXY was -1x until Feb 2018, then -0.5x. The 2015-2023 in-sample
mixes both leverage regimes (pre-2018 ~2x the magnitude). The Feb-5-2018
-90% day IS in the data and is the canonical stress test for whether the gate
exits in time. Interpret in-sample accordingly; the held-out window (2024-26)
is clean -0.5x.

Success bar (research doc): gated version beats SPY on Sharpe over the window
AND no single-day loss beyond the modeled worst case (if the gate misses a
spike, that's the kill signal). Honest prior: a tradeable but tail-heavy
sleeve; deploy small if at all.
"""
from __future__ import annotations

import json
import sqlite3
import statistics
from datetime import date
from pathlib import Path

from trading_bot import config
from trading_bot.config import DB_PATH

OUT_PATH = Path("var/data_audit/vix_shortvol.json")
STARTING_CASH = 100_000.0
HALF_SPREAD_BPS = 5.0       # SVXY wider than SPY
CASH_APY = config.CASH_INTEREST_APY

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]


def _closes(ticker: str) -> dict[str, float]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT key_date, price FROM price_cache "
        "WHERE ticker=? AND kind='close' ORDER BY key_date", (ticker,)).fetchall()
    conn.close()
    return {d: p for d, p in rows if p is not None and p > 0}


def _sma_series(closes: dict[str, float], n: int) -> dict[str, float]:
    items = sorted(closes.items())
    dates = [d for d, _ in items]; px = [p for _, p in items]
    out = {}
    for i in range(len(dates)):
        if i + 1 >= n:
            out[dates[i]] = sum(px[i + 1 - n:i + 1]) / n
    return out


def _max_drawdown(curve):
    peak = curve[0][1]; mdd = 0.0
    for _, v in curve:
        if v > peak: peak = v
        if peak > 0:
            dd = (v / peak - 1.0) * 100
            if dd < mdd: mdd = dd
    return mdd


def _worst_day(curve):
    worst = 0.0
    for i in range(1, len(curve)):
        if curve[i - 1][1] > 0:
            r = curve[i][1] / curve[i - 1][1] - 1.0
            if r < worst: worst = r
    return worst * 100


def _sharpe_by_year(curve, rf_apy=0.045):
    by_year: dict[str, list[float]] = {}
    pv = py = None
    for iso, v in curve:
        y = iso[:4]
        if pv and pv > 0 and y == py:
            by_year.setdefault(y, []).append(v / pv - 1.0)
        pv, py = v, y
    rf = rf_apy / 252; out = {}
    for y, rets in by_year.items():
        if len(rets) < 20: continue
        sd = statistics.pstdev(rets)
        if sd > 0:
            out[y] = ((statistics.fmean(rets) - rf) / sd) * (252 ** 0.5)
    return out


def _metrics(curve, since, until):
    cagr = ((curve[-1][1] / curve[0][1]) ** (365.25 / (until - since).days) - 1) * 100
    sh = _sharpe_by_year(curve)
    return {"cagr_pct": cagr,
            "mean_sharpe": statistics.fmean(sh.values()) if sh else 0.0,
            "max_dd_pct": _max_drawdown(curve),
            "worst_day_pct": _worst_day(curve)}


def simulate(svxy, vix, vix3m, spy, sma, since, until, mode):
    """mode: 'gated' / 'svxy_bh' / 'spy_bh'."""
    base = svxy if mode != "spy_bh" else spy
    dates = sorted(d for d in base
                   if since.isoformat() <= d <= until.isoformat())
    cash_daily = CASH_APY / 252
    hs = HALF_SPREAD_BPS / 10000.0
    nav = STARTING_CASH
    curve = [(dates[0], nav)]
    prev_in = True
    switches = 0; exposure = 0
    for i in range(1, len(dates)):
        d, dprev = dates[i], dates[i - 1]
        if mode == "gated":
            v, v3 = vix.get(dprev), vix3m.get(dprev)
            sp, sm = spy.get(dprev), sma.get(dprev)
            contango = (v is not None and v3 is not None and v <= v3)
            riskon = (sp is not None and sm is not None and sp > sm)
            in_mkt = contango and riskon
        else:
            in_mkt = True
        px = svxy if mode != "spy_bh" else spy
        if in_mkt and (d in px) and (dprev in px):
            nav *= px[d] / px[dprev]; exposure += 1
        else:
            nav *= (1.0 + cash_daily)
        if in_mkt != prev_in:
            nav *= (1.0 - hs); switches += 1
        prev_in = in_mkt
        curve.append((d, nav))
    return curve, switches, exposure / max(1, len(dates) - 1)


SMA_VARIANTS = [200, 275]


def main() -> int:
    svxy = _closes("SVXY"); vix = _closes("^VIX"); vix3m = _closes("^VIX3M")
    spy = _closes("SPY")
    if not svxy or not vix or not vix3m:
        print("MISSING DATA — run warm_vol_letf_etfs first.")
        print(f"  SVXY={len(svxy)} ^VIX={len(vix)} ^VIX3M={len(vix3m)}")
        return 1
    print(f"Data: SVXY={len(svxy)} (range {min(svxy)}..{max(svxy)}), "
          f"^VIX={len(vix)}, ^VIX3M={len(vix3m)}")
    runs = []
    print("\nVIX-GATED SHORT-VOL vs buy-hold")
    print("=" * 90)
    for wl, since, until in WINDOWS:
        print(f"\n  {wl.upper()}")
        print(f"  {'config':<16} {'CAGR':>9} {'Sharpe':>8} {'maxDD':>9} "
              f"{'worstDay':>9} {'expo':>6} {'sw':>5}")
        print("  " + "-" * 70)
        for mode, label in [("spy_bh", "SPY_buyhold"), ("svxy_bh", "SVXY_buyhold")]:
            c, _, _ = simulate(svxy, vix, vix3m, spy, {}, since, until, mode)
            m = _metrics(c, since, until); m.update({"window": wl, "config": label})
            runs.append(m)
            print(f"  {label:<16} {m['cagr_pct']:>+8.2f}% {m['mean_sharpe']:>+7.3f} "
                  f"{m['max_dd_pct']:>+8.2f}% {m['worst_day_pct']:>+8.2f}% {'-':>6} {'-':>5}")
        for nsma in SMA_VARIANTS:
            sma = _sma_series(spy, nsma)
            c, sw, expo = simulate(svxy, vix, vix3m, spy, sma, since, until, "gated")
            m = _metrics(c, since, until)
            m.update({"window": wl, "config": f"gated_sma{nsma}", "switches": sw,
                      "exposure_frac": expo})
            runs.append(m)
            print(f"  {'gated_sma'+str(nsma):<16} {m['cagr_pct']:>+8.2f}% {m['mean_sharpe']:>+7.3f} "
                  f"{m['max_dd_pct']:>+8.2f}% {m['worst_day_pct']:>+8.2f}% "
                  f"{expo*100:>5.0f}% {sw:>5}")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
