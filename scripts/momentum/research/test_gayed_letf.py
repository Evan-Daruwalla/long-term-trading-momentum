"""Candidate #4: Gayed "Leverage for the Long Run" LETF trend rotation.

Hold a leveraged index ETF while the UNDERLYING index closes above its
200-day SMA; rotate to cash (T-bill rate) when below. The MA doesn't predict
returns — it predicts volatility regime, and leveraged ETFs' daily-reset decay
is worst in high-vol/choppy regimes, which is exactly when the filter sits out.

Single-asset timing (own daily sim, not factor_backtest). Uses ACTUAL LETF
closes so daily-reset decay + leverage are captured realistically. Signal is
decided at the prior close and applied the next day (no lookahead).

Configs:
  SSO  (2x S&P) / UPRO (3x S&P)   gated on SPY 200-DMA
  QLD  (2x NDX) / TQQQ (3x NDX)   gated on QQQ 200-DMA
Benchmarks: SPY buy-hold, QQQ buy-hold, and buy-hold of each LETF (un-gated).

Success bar (research doc): beat the underlying index (SPY/QQQ) buy-hold on
CAGR on BOTH windows net of cost, with max DD not worse than -65%.
NOTE re redundancy with the failed 'trend200' overlay: that gated a
cross-sectional STOCK portfolio on SPY's MA (signal != asset). Here the gated
asset IS the index, so signal and asset coincide — a different mechanism.
"""
from __future__ import annotations

import json
import sqlite3
import statistics
from datetime import date
from pathlib import Path

from trading_bot import config
from trading_bot.config import DB_PATH

OUT_PATH = Path("var/data_audit/gayed_letf.json")
STARTING_CASH = 100_000.0
HALF_SPREAD_BPS = 3.0       # LETFs slightly wider than SPY
CASH_APY = config.CASH_INTEREST_APY
SMA_DAYS = 200

WINDOWS = [
    ("in_sample", date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",   date(2024, 1, 1), date(2026, 5, 1)),
]
# (config label, traded LETF, underlying index for the 200-DMA signal)
CONFIGS = [
    ("SSO_rot",  "SSO",  "SPY"),
    ("UPRO_rot", "UPRO", "SPY"),
    ("QLD_rot",  "QLD",  "QQQ"),
    ("TQQQ_rot", "TQQQ", "QQQ"),
]


def _closes(ticker: str) -> dict[str, float]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT key_date, price FROM price_cache "
        "WHERE ticker=? AND kind='close' ORDER BY key_date", (ticker,)).fetchall()
    conn.close()
    return {d: p for d, p in rows if p is not None and p > 0}


def _sma_series(index_closes: dict[str, float], n: int) -> dict[str, float]:
    """200-DMA keyed by date (the SMA of the trailing n closes ending that day)."""
    items = sorted(index_closes.items())
    dates = [d for d, _ in items]
    px = [p for _, p in items]
    out: dict[str, float] = {}
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
            "max_dd_pct": _max_drawdown(curve)}


def simulate(letf_px, index_px, sma, since, until, gated: bool):
    """Daily sim over the window. gated=False -> buy-and-hold the LETF."""
    dates = sorted(d for d in letf_px
                   if since.isoformat() <= d <= until.isoformat())
    cash_daily = CASH_APY / 252
    hs = HALF_SPREAD_BPS / 10000.0
    nav = STARTING_CASH
    curve = [(dates[0], nav)]
    prev_in = True
    switches = 0
    for i in range(1, len(dates)):
        d, dprev = dates[i], dates[i - 1]
        if gated:
            # signal from the PRIOR close (no lookahead): index > its SMA
            sig_px = index_px.get(dprev)
            sig_sma = sma.get(dprev)
            in_mkt = (sig_px is not None and sig_sma is not None and sig_px > sig_sma)
        else:
            in_mkt = True
        if in_mkt and (d in letf_px) and (dprev in letf_px):
            nav *= letf_px[d] / letf_px[dprev]
        else:
            nav *= (1.0 + cash_daily)
        if in_mkt != prev_in:
            nav *= (1.0 - hs)
            switches += 1
        prev_in = in_mkt
        curve.append((d, nav))
    return curve, switches


def main() -> int:
    spy = _closes("SPY"); qqq = _closes("QQQ")
    sma_spy = _sma_series(spy, SMA_DAYS); sma_qqq = _sma_series(qqq, SMA_DAYS)
    idx_px = {"SPY": spy, "QQQ": qqq}
    idx_sma = {"SPY": sma_spy, "QQQ": sma_qqq}
    runs = []
    print("GAYED LETF ROTATION (200-DMA) vs buy-hold")
    print("=" * 80)
    for wl, since, until in WINDOWS:
        print(f"\n  {wl.upper()}")
        print(f"  {'config':<16} {'CAGR':>9} {'Sharpe':>8} {'maxDD':>9} {'switches':>9}")
        print("  " + "-" * 58)
        # index benchmarks
        for idx in ("SPY", "QQQ"):
            c, _ = simulate(idx_px[idx], idx_px[idx], idx_sma[idx], since, until, gated=False)
            m = _metrics(c, since, until); m.update({"window": wl, "config": f"{idx}_buyhold"})
            runs.append(m)
            print(f"  {idx+'_buyhold':<16} {m['cagr_pct']:>+8.2f}% {m['mean_sharpe']:>+7.3f} "
                  f"{m['max_dd_pct']:>+8.2f}% {'-':>9}")
        for label, letf, idx in CONFIGS:
            lpx = _closes(letf)
            if not lpx:
                print(f"  {label:<16} NO DATA for {letf}"); continue
            # un-gated LETF buy-hold
            cbh, _ = simulate(lpx, idx_px[idx], idx_sma[idx], since, until, gated=False)
            mbh = _metrics(cbh, since, until)
            mbh.update({"window": wl, "config": f"{letf}_buyhold"}); runs.append(mbh)
            # gated rotation
            cg, sw = simulate(lpx, idx_px[idx], idx_sma[idx], since, until, gated=True)
            mg = _metrics(cg, since, until)
            mg.update({"window": wl, "config": label, "switches": sw}); runs.append(mg)
            print(f"  {letf+'_buyhold':<16} {mbh['cagr_pct']:>+8.2f}% {mbh['mean_sharpe']:>+7.3f} "
                  f"{mbh['max_dd_pct']:>+8.2f}% {'-':>9}")
            print(f"  {label:<16} {mg['cagr_pct']:>+8.2f}% {mg['mean_sharpe']:>+7.3f} "
                  f"{mg['max_dd_pct']:>+8.2f}% {sw:>9}")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs}, indent=2))
    print(f"\nWritten -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
