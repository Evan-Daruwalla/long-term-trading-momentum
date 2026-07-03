"""12-1 month momentum factor (Jegadeesh-Titman 1993, academic standard).

For each ticker, compute the return from `LOOKBACK_TRADING_DAYS` before
`as_of` to `SKIP_TRADING_DAYS` before `as_of`. The 1-month skip excludes
the most recent month, which is dominated by short-term reversal effects.

Returns None when there isn't enough cached history (typically because
the ticker IPO'd less than the lookback period before as_of, or yfinance
has gaps).

`rank_universe` and `momentum_score` accept lookback/skip overrides so
robustness sweeps can test 6-1, 9-1, etc. without monkeypatching.
"""
from __future__ import annotations

from datetime import date

from trading_bot.factors.universe import close_at_offset

LOOKBACK_TRADING_DAYS = 252      # ~12 months
SKIP_TRADING_DAYS = 21           # ~1 month


def momentum_score(ticker: str, as_of: date,
                   lookback: int = LOOKBACK_TRADING_DAYS,
                   skip: int = SKIP_TRADING_DAYS) -> float | None:
    p_old = close_at_offset(ticker, as_of, -lookback)
    p_recent = close_at_offset(ticker, as_of, -skip)
    if p_old is None or p_recent is None or p_old <= 0:
        return None
    return p_recent / p_old - 1.0


def rank_universe(tickers: list[str], as_of: date,
                  lookback: int = LOOKBACK_TRADING_DAYS,
                  skip: int = SKIP_TRADING_DAYS
                  ) -> list[tuple[str, float]]:
    """Rank `tickers` by momentum at `as_of`, descending. Drops tickers
    with insufficient history. lookback/skip override the module defaults
    for parameter sweeps."""
    scored: list[tuple[str, float]] = []
    for t in tickers:
        s = momentum_score(t, as_of, lookback=lookback, skip=skip)
        if s is not None:
            scored.append((t, s))
    scored.sort(key=lambda r: r[1], reverse=True)
    return scored


def make_rank_fn(lookback: int = LOOKBACK_TRADING_DAYS,
                 skip: int = SKIP_TRADING_DAYS):
    """Build a rank_fn closure for `factor_backtest.run_factor_backtest`
    with specific lookback/skip params. Used by mono-factor sweeps."""
    def _ranker(tickers, as_of):
        return rank_universe(tickers, as_of, lookback=lookback, skip=skip)
    _ranker.__name__ = f"momentum_{lookback}_{skip}"
    return _ranker
