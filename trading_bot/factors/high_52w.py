"""52-week-high momentum — George & Hwang (2004).

Rank stocks by how close their current price is to its trailing 52-week high:
    score = close(as_of) / max(close over trailing `lookback` trading days)
A score near 1.0 means the stock is at/near its 52-week high. George & Hwang
found this "nearness to the 52-week high" predicts returns better than
Jegadeesh-Titman total-return momentum and is more crash-resistant, because
the anchor (the 52-week high) is a hard reference point rather than a
path-dependent cumulative return.

We only cache daily CLOSES (not intraday highs), so the 52-week high is
approximated by the max close over the window — the standard retail proxy.

Returns None with insufficient history.
"""
from __future__ import annotations

import bisect
from datetime import date

from trading_bot.factors import universe as _u

LOOKBACK_TRADING_DAYS = 252      # ~52 weeks


def high_52w_score(ticker: str, as_of: date,
                   lookback: int = LOOKBACK_TRADING_DAYS) -> float | None:
    _u._build_index()
    if ticker not in _u._TICKER_INDEX:
        return None
    dates, prices = _u._TICKER_INDEX[ticker]
    iso = as_of.isoformat()
    i = bisect.bisect_left(dates, iso)
    if i >= len(dates) or dates[i] != iso:
        i -= 1
        if i < 0:
            return None
    px_now = prices[i]
    if px_now is None or px_now <= 0:
        return None
    start = i - lookback
    if start < 0:
        return None
    window = [p for p in prices[start:i + 1] if p is not None and p > 0]
    if len(window) < lookback // 2:
        return None
    hi = max(window)
    if hi <= 0:
        return None
    return px_now / hi


def rank_universe(tickers: list[str], as_of: date,
                  lookback: int = LOOKBACK_TRADING_DAYS) -> list[tuple[str, float]]:
    scored: list[tuple[str, float]] = []
    for t in tickers:
        s = high_52w_score(t, as_of, lookback=lookback)
        if s is not None:
            scored.append((t, s))
    scored.sort(key=lambda r: r[1], reverse=True)
    return scored


def make_rank_fn(lookback: int = LOOKBACK_TRADING_DAYS):
    def _ranker(tickers, as_of):
        return rank_universe(tickers, as_of, lookback=lookback)
    _ranker.__name__ = f"high_52w_{lookback}"
    return _ranker
