"""Residual (idiosyncratic) momentum — Blitz, Huij & Martens (2011).

Standard 12-1 momentum ranks on TOTAL return, which loads heavily on market
beta — that beta exposure is what produces "momentum crashes" (Daniel &
Moskowitz 2016): in a sharp market rebound the past-loser cohort (high beta)
rips and the long-only winner cohort lags. Residual momentum strips the market
component out first, then ranks on the leftover stock-specific drift.

Per rebalance, for each ticker:
  1. Take daily returns over the 12-1 formation window (252 trading days
     ending `skip`=21 days before as_of — same window as momentum.py).
  2. Regress stock daily returns on SPY daily returns (OLS, market model):
     r_stock = alpha + beta*r_mkt + residual.
  3. Residual momentum score = alpha / stdev(residual) — the appraisal/
     information ratio of the idiosyncratic return. alpha is the mean
     idiosyncratic daily return (the drift NOT explained by market beta);
     standardizing by residual vol is the form Blitz et al. use, which
     delivers ~2x the risk-adjusted return of total-return momentum.

     NOTE: we use the regression INTERCEPT (alpha), not the mean of the
     residuals — OLS with an intercept forces mean(residual)=0 by
     construction, so mean(residual)/sd is always ~0. alpha captures the
     idiosyncratic drift that mean(residual) cancels out.

Returns None when there isn't enough overlapping history (IPO'd recently,
yfinance gaps) or residual variance is degenerate.

NOTE: this is heavier than momentum.py (an OLS per ticker per rebalance vs a
2-price lookup), but at ~4k tickers x ~250 points x ~136 monthly rebalances it
is still a few seconds per window. SPY returns are cached once.
"""
from __future__ import annotations

import sqlite3
from datetime import date
from functools import lru_cache

import numpy as np

from trading_bot.config import DB_PATH
from trading_bot.factors import universe as _u

LOOKBACK_TRADING_DAYS = 252      # ~12 months
SKIP_TRADING_DAYS = 21           # ~1 month (excludes short-term reversal)
MIN_OVERLAP = 120                # need at least this many aligned daily returns
MARKET_TICKER = "SPY"


@lru_cache(maxsize=1)
def _market_returns() -> dict[str, float]:
    """{date_iso: daily_return} for the market proxy. Cached for the process."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT key_date, price FROM price_cache "
        "WHERE ticker=? AND kind='close' ORDER BY key_date",
        (MARKET_TICKER,),
    ).fetchall()
    conn.close()
    closes = [(d, p) for d, p in rows if p is not None and p > 0]
    out: dict[str, float] = {}
    for i in range(1, len(closes)):
        prev = closes[i - 1][1]
        if prev > 0:
            out[closes[i][0]] = closes[i][1] / prev - 1.0
    return out


def residual_momentum_score(ticker: str, as_of: date,
                            lookback: int = LOOKBACK_TRADING_DAYS,
                            skip: int = SKIP_TRADING_DAYS) -> float | None:
    if ticker == MARKET_TICKER:
        return None   # regressing the market on itself is degenerate
    _u._build_index()
    if ticker not in _u._TICKER_INDEX:
        return None
    dates, prices = _u._TICKER_INDEX[ticker]
    iso = as_of.isoformat()
    import bisect
    i = bisect.bisect_left(dates, iso)
    if i >= len(dates) or dates[i] != iso:
        i -= 1
        if i < 0:
            return None
    end = i - skip                       # last day of formation window
    start = end - lookback               # first close used (returns start at start+1)
    if start < 1:
        return None
    mkt = _market_returns()
    y: list[float] = []   # stock daily returns
    x: list[float] = []   # market daily returns
    for j in range(start + 1, end + 1):
        p0, p1 = prices[j - 1], prices[j]
        if p0 is None or p1 is None or p0 <= 0:
            continue
        m = mkt.get(dates[j])
        if m is None:
            continue
        y.append(p1 / p0 - 1.0)
        x.append(m)
    if len(y) < MIN_OVERLAP:
        return None
    xa = np.asarray(x)
    ya = np.asarray(y)
    # OLS market model: y = a + b*x. polyfit returns [b, a] (slope, intercept).
    b, a = np.polyfit(xa, ya, 1)
    resid = ya - (b * xa + a)
    sd = resid.std()
    # Floor: a near-market index clone (e.g. VOO, an S&P ETF) has ~0 residual
    # vol, which would explode alpha/sd into a spurious top rank. No real
    # single stock has daily idiosyncratic vol below ~0.1%.
    if sd < 1e-3:
        return None
    # alpha (intercept) = mean idiosyncratic daily return, standardized by
    # residual vol = information ratio. (mean(resid) is mechanically ~0.)
    return float(a / sd)


def rank_universe(tickers: list[str], as_of: date,
                  lookback: int = LOOKBACK_TRADING_DAYS,
                  skip: int = SKIP_TRADING_DAYS) -> list[tuple[str, float]]:
    scored: list[tuple[str, float]] = []
    for t in tickers:
        s = residual_momentum_score(t, as_of, lookback=lookback, skip=skip)
        if s is not None:
            scored.append((t, s))
    scored.sort(key=lambda r: r[1], reverse=True)
    return scored


def make_rank_fn(lookback: int = LOOKBACK_TRADING_DAYS,
                 skip: int = SKIP_TRADING_DAYS):
    def _ranker(tickers, as_of):
        return rank_universe(tickers, as_of, lookback=lookback, skip=skip)
    _ranker.__name__ = f"residual_momentum_{lookback}_{skip}"
    return _ranker
