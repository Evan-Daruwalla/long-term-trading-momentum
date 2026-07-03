"""Sector momentum factor — 12-1 momentum on 11 SPDR sector ETFs.

Distinct from `momentum.py` (which works on individual stocks): this
operates on a fixed 11-ETF universe and ignores the tradeable_universe
stock filter. Provides:
  - SECTOR_UNIVERSE: the 11 SPDR sector ETF tickers
  - rank_universe(tickers, as_of): standard rank_fn signature for use
    with factor_backtest.run_factor_backtest. Ignores the passed tickers
    arg and ranks SECTOR_UNIVERSE directly.

Used by:
  - `strategies/sector_top4.py` (frozen spec, top-4 rotation)
  - `scripts/momentum/research/test_sector_momentum.py` (research sweep)

Data: requires the 11 ETFs to be in price_cache. Run
`scripts/momentum/warm/warm_sector_etfs.py` once to populate; afterward
`daily_price_refresh.py` keeps them updated alongside the stock universe.
"""
from __future__ import annotations

from datetime import date

from trading_bot.factors.universe import close_at_offset

SECTOR_UNIVERSE = [
    "XLE", "XLF", "XLI", "XLB", "XLK",
    "XLP", "XLU", "XLV", "XLY", "XLC", "XLRE",
]
# yfinance .info has no "sector" for ETFs, so paper_rebalance falls back
# to this map for sector_top4_paper holdings (otherwise dashboard shows "?").
SECTOR_NAMES = {
    "XLE": "Energy", "XLF": "Financials", "XLI": "Industrials",
    "XLB": "Materials", "XLK": "Technology", "XLP": "Consumer Staples",
    "XLU": "Utilities", "XLV": "Health Care", "XLY": "Consumer Discretionary",
    "XLC": "Communication Services", "XLRE": "Real Estate",
}
LOOKBACK_TRADING_DAYS = 252  # 12 months
SKIP_TRADING_DAYS = 21       # 1 month


def momentum_score(ticker: str, as_of: date) -> float | None:
    p_old = close_at_offset(ticker, as_of, -LOOKBACK_TRADING_DAYS)
    p_recent = close_at_offset(ticker, as_of, -SKIP_TRADING_DAYS)
    if p_old is None or p_recent is None or p_old <= 0:
        return None
    return p_recent / p_old - 1.0


def rank_universe(tickers: list[str] | None, as_of: date) -> list[tuple[str, float]]:
    """Rank the SECTOR ETF universe (ignores `tickers` arg).
    Same signature as momentum.rank_universe so factor_backtest can swap in.

    The engine's _rebalance calls this with the stock universe as `tickers`;
    we intentionally substitute SECTOR_UNIVERSE because this strategy doesn't
    use the stock filter.
    """
    scored: list[tuple[str, float]] = []
    for t in SECTOR_UNIVERSE:
        s = momentum_score(t, as_of)
        if s is not None:
            scored.append((t, s))
    scored.sort(key=lambda r: r[1], reverse=True)
    return scored
