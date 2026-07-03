"""Low-volatility factor.

For each ticker compute realized volatility of daily returns over the
last `WINDOW` trading days; rank with LOWEST vol first (higher score).
Returns None when there isn't enough history.

Classic low-vol effect (Frazzini-Pedersen 2014 "Betting Against Beta"
and many predecessors): low-volatility stocks deliver a higher risk-
adjusted return than CAPM predicts. Long-only low-vol gives up some
upside in big bull runs but materially reduces drawdowns; combined with
momentum (which is high-beta by nature) the two factors are
anti-correlated and the multi-factor portfolio's Sharpe typically
exceeds either factor alone.
"""
from __future__ import annotations

import statistics
from datetime import date

from trading_bot.factors.universe import close_at_offset

WINDOW = 60      # trading days, ~3 months
# Min daily-stdev floor (1.0%/day). Below this, "low-vol" picks are
# dominated by:
#   - closed-end bond funds (NXJ/NAD/FRA, ~0.3-0.7%/day, mechanically
#     low-vol because they're fixed-income wrappers)
#   - mortgage REITs and equity-income CEFs (~0.7-1.0%/day, pseudo-bonds)
# At 1.0%/day floor, picks become real stable large-caps: ATO/IEX/WMB/
# KMI/KR/NOC/WFC/AFL/PFE etc. — the classic low-vol equity universe.
# Verified consistent across 2015-2024 (see smoke tests on this commit).
MIN_DAILY_STDEV = 0.010


def low_vol_score(ticker: str, as_of: date, window: int = WINDOW
                  ) -> float | None:
    """-1 * realized stdev of daily returns over `window` trading days.
    Negative so higher score = lower vol = better (matches the
    higher-is-better convention of momentum_score)."""
    closes: list[float] = []
    for offset in range(-window, 1):
        p = close_at_offset(ticker, as_of, offset)
        if p is None or p <= 0:
            return None
        closes.append(p)
    rets = [closes[i] / closes[i - 1] - 1.0 for i in range(1, len(closes))]
    if len(rets) < window // 2:
        return None
    return -statistics.pstdev(rets)


def rank_universe(tickers: list[str], as_of: date,
                  min_daily_stdev: float = MIN_DAILY_STDEV
                  ) -> list[tuple[str, float]]:
    """Rank tickers by low-vol (lowest stdev = best score).

    `min_daily_stdev` excludes names whose daily-return stdev falls below
    the floor — the bond-CEF filter. Default 0.7%/day matches the CEF
    elbow in the empirical distribution. Pass 0 to disable.
    """
    scored: list[tuple[str, float]] = []
    for t in tickers:
        s = low_vol_score(t, as_of)
        if s is None:
            continue
        # s = -stdev, so -s = stdev. Drop names below the floor.
        if -s < min_daily_stdev:
            continue
        scored.append((t, s))
    scored.sort(key=lambda r: r[1], reverse=True)   # higher = lower vol = better
    return scored
