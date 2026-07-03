"""Short-term reversal factor.

Signal: -1 × return over past N trading days.
Direction: LONG recent losers, SHORT recent winners (long-only here = LONG losers).

Why this might combine with momentum where 8 prior factors failed:
  - Anti-correlated BY CONSTRUCTION: mom's 12-1 lookback uses days [-252, -21].
    Reversal's 21-day lookback uses days [-21, 0]. They look at disjoint
    windows of the price series.
  - Different driver: reversal is microstructure / liquidity overreaction,
    not value or quality.

Why it might still fail:
  - High-frequency signal at monthly cadence may miss the actual reversal
    window (signal mean-reverts within 1-4 weeks per literature)
  - 5 bps half-spread × 12 rebal/yr = 60 bps/yr drag; with weekly rebal
    that becomes ~260 bps which dominates the signal
  - Reversal often picks DROPPED stocks that drop further (catching the
    falling knife) — drawdowns can be severe

Default lookback = 21 trading days (~1 calendar month). Configurable
for sweep testing.
"""
from __future__ import annotations

from datetime import date

from trading_bot.factors.universe import close_at_offset

LOOKBACK_TRADING_DAYS = 21    # ~1 month


def reversal_score(ticker: str, as_of: date,
                   lookback: int = LOOKBACK_TRADING_DAYS) -> float | None:
    """Returns -(price_now / price_lookback_ago - 1).
    Higher score = bigger recent loser = better candidate for reversal."""
    p_old = close_at_offset(ticker, as_of, -lookback)
    p_now = close_at_offset(ticker, as_of, 0)
    if p_old is None or p_now is None or p_old <= 0:
        return None
    return -(p_now / p_old - 1.0)


def rank_universe(tickers: list[str], as_of: date,
                  lookback: int = LOOKBACK_TRADING_DAYS
                  ) -> list[tuple[str, float]]:
    """Rank tickers by reversal signal (most-negative recent return ranked
    highest). Drops tickers with insufficient history."""
    scored: list[tuple[str, float]] = []
    for t in tickers:
        s = reversal_score(t, as_of, lookback=lookback)
        if s is not None:
            scored.append((t, s))
    scored.sort(key=lambda r: r[1], reverse=True)
    return scored


def make_rank_fn(lookback: int = LOOKBACK_TRADING_DAYS):
    """Build a rank_fn closure for sweep testing different lookbacks."""
    def _ranker(tickers, as_of):
        return rank_universe(tickers, as_of, lookback=lookback)
    _ranker.__name__ = f"reversal_{lookback}d"
    return _ranker
