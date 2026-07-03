"""Point-in-time tradeable universe for factor portfolios.

A ticker is in the universe on date D iff, from cached `close` data:
  - It has a close price on D (was trading)
  - It has >=MIN_HISTORY_DAYS prior cached closes (enough history for
    factor calcs + a minimum quality bar)
  - Close on D >= MIN_PRICE_USD (penny-stock filter; bid-ask spreads on
    sub-$5 names eat the factor and reverse-splits distort momentum)

Volume / dollar-volume is intentionally NOT enforced here (v1
limitation, see MOMENTUM_DESIGN.md §11). The MIN_PRICE filter excludes
the most-toxic micro-caps; bulk-warmed volume can be added later.

Survivorship caveat: this only knows about tickers yfinance still serves.
Tickers delisted before today are absent entirely. The price filter +
point-in-time presence handles the "alive on D but dead by today" case
correctly, but the "dead before we ever cached it" case can't be fixed
without a different data source.

Builds a per-ticker sorted-date index once on first call (lazy), then
all subsequent calls are O(log n) per ticker lookup.
"""
from __future__ import annotations

import bisect
import statistics
from datetime import date

from trading_bot.execution import market_data

MIN_PRICE_USD = 5.0
MIN_HISTORY_DAYS = 252       # ~1 trading year, matches the 12-month momentum lookback

# Non-stock tickers warmed into price_cache for OTHER strategies (sector
# rotation, regime detection, the VIX/LETF research candidates). They must NOT
# enter the STOCK tradeable_universe — a momentum/ROA stock sleeve should never
# hold SPY, a 3x ETF, or VIX. Without this, warming e.g. TQQQ (huge 2023
# momentum, ranks ~#115) silently changed momentum_v1's top-100 and broke the
# frozen regression (2026-06-09). sector_top4 uses its own SECTOR_UNIVERSE list
# and residual_momentum reads SPY directly, so excluding these here is safe.
# Any "^"-prefixed index ticker is also excluded (see tradeable_universe).
NON_STOCK_TICKERS = frozenset({
    "SPY", "RSP", "QQQ", "DIA", "IWM", "VOO", "VTI",          # broad-index ETFs
    "XLE", "XLF", "XLI", "XLB", "XLK", "XLP", "XLU", "XLV",   # SPDR sectors
    "XLY", "XLC", "XLRE",
    "SSO", "UPRO", "QLD", "TQQQ", "SPXL", "SQQQ", "SPXU",     # leveraged
    "SVXY", "VIXY", "UVXY", "VXX",                            # volatility ETPs
})
# DEFAULT min_dollar_vol is 0 — see memory/sleeves_verdict.md (2026-05-26):
# the $1M ADV filter killed momentum's premium (-92% of in-sample return,
# 345% -> 29%) by excluding the high-vol small-caps where the premium lives.
# Callers that want an equity-liquidity filter should opt in explicitly.
MIN_DOLLAR_VOL = 0
VOL_LOOKBACK = 60            # trading days for median-ADV calc (when filter enabled)

# Data quality filter (2026-05-28 — see memory/data_audit_2026-05-28.md):
# Reject tickers whose historical price on as_of is >MAX_HIST_RATIO x their
# current stable price (median of last STABLE_LOOKBACK closes). This catches
# yfinance unadjusted-reverse-split corruption where pre-split prices remain
# inflated. E.g. ARSC shows $8000 closes in 2010-2016 but current price is
# $0.10 (80,000x ratio) — clearly corrupt. Without this filter, the strategy
# buys these tickers in the in-sample period (passes $5 min_price), earning
# phantom MTM gains, then loses everything when the corruption resolves.
MAX_HIST_RATIO = 100.0       # historical/stable price > this -> reject
STABLE_LOOKBACK_DAYS = 60    # window for "current stable" price (median)

# Upper-price sanity filter (2026-06-01 — see docs/audit_2026-06-01.md L1):
# MAX_HIST_RATIO catches "historical >> current" ghosts but NOT ghosts whose
# CURRENT price is the corrupt one (e.g. BKGM ~$10,000, SFI ~$23k, VCI ~$47k —
# yfinance forward-split / bad-tick artifacts that sit at an absurd current
# level). A price > MAX_PRICE_USD on as_of is rejected UNLESS the ticker is a
# known genuinely-high-priced US equity. A bare threshold can't separate BKGM
# ($10k ghost) from NVR (real, ATH ~$9.9k), so the allowlist is required.
# Set max_price=0 to disable.
MAX_PRICE_USD = 5000.0
HIGH_PRICE_ALLOWLIST = frozenset({
    "NVR",        # NVR Inc — homebuilder, ~$6k-$9.9k, genuinely this high
    "SEB",        # Seaboard Corp — ~$3k-$5k
    "BKNG",       # Booking Holdings — ~$4k-$5.5k
    "BRK-A", "BRK.A", "BRKA",  # Berkshire A — ~$600k, if ever present
    "AZO",        # AutoZone — ~$3k (under cap, harmless to allowlist)
    "MELI",       # MercadoLibre — ~$1.7k-$2.5k
})


# {ticker: ([sorted_dates_iso], [aligned_prices])}. Built lazily from the
# preloaded _MEM_PRICE on first universe query. Cached for the process lifetime
# (price_cache is read-only during a backtest).
_TICKER_INDEX: dict[str, tuple[list[str], list[float | None]]] = {}
# Parallel index for volume (raw shares per day). Same date-list shape as
# _TICKER_INDEX so the same i-offset works for both.
_VOLUME_INDEX: dict[str, list[float | None]] = {}
_INDEX_BUILT = False


def _build_index() -> None:
    """Populate _TICKER_INDEX + _VOLUME_INDEX from market_data._MEM_PRICE.
    Both share the same date axis per ticker so callers can use the same
    index `i` for either. Idempotent."""
    global _INDEX_BUILT
    if _INDEX_BUILT:
        return
    if not market_data._MEM_LOADED:
        market_data.preload_caches()
    close_by_t: dict[str, list[tuple[str, float | None]]] = {}
    vol_by_t: dict[str, dict[str, float | None]] = {}
    for (ticker, kind, key_date), val in market_data._MEM_PRICE.items():
        if kind == "close":
            close_by_t.setdefault(ticker, []).append((key_date, val))
        elif kind == "volume":
            vol_by_t.setdefault(ticker, {})[key_date] = val
    for ticker, rows in close_by_t.items():
        rows.sort()
        dates = [r[0] for r in rows]
        prices = [r[1] for r in rows]
        _TICKER_INDEX[ticker] = (dates, prices)
        vmap = vol_by_t.get(ticker, {})
        _VOLUME_INDEX[ticker] = [vmap.get(d) for d in dates]
    _INDEX_BUILT = True


# {ticker: stable_price} computed lazily once after _build_index runs.
# Stable = median of last STABLE_LOOKBACK_DAYS non-None closes. Used by the
# consistency filter in tradeable_universe.
_STABLE_PRICE: dict[str, float | None] = {}
_STABLE_BUILT = False


def _build_stable_prices() -> None:
    """One-shot: compute median-of-recent close per ticker. Tickers with
    fewer than 10 recent closes get None (insufficient data -> reject)."""
    global _STABLE_BUILT
    if _STABLE_BUILT:
        return
    _build_index()
    for tk, (dates, prices) in _TICKER_INDEX.items():
        recent = [p for p in prices[-STABLE_LOOKBACK_DAYS:] if p is not None and p > 0]
        if len(recent) >= 10:
            _STABLE_PRICE[tk] = statistics.median(recent)
        else:
            _STABLE_PRICE[tk] = None
    _STABLE_BUILT = True


def _ticker_close_on(ticker: str, as_of: date) -> tuple[int, float | None]:
    """Return (index_in_dates, price) for the close on as_of, or
    (insertion_point, None) if no close on as_of. Trading-day strict."""
    if ticker not in _TICKER_INDEX:
        return (0, None)
    dates, prices = _TICKER_INDEX[ticker]
    iso = as_of.isoformat()
    i = bisect.bisect_left(dates, iso)
    if i < len(dates) and dates[i] == iso:
        return (i, prices[i])
    return (i, None)


def median_dollar_volume(ticker: str, as_of: date,
                          lookback: int = VOL_LOOKBACK) -> float | None:
    """Median of close*volume over the last `lookback` trading days
    ending on `as_of`. Returns None if volume coverage is incomplete."""
    _build_index()
    if ticker not in _TICKER_INDEX:
        return None
    dates, closes = _TICKER_INDEX[ticker]
    vols = _VOLUME_INDEX.get(ticker, [])
    i = bisect.bisect_left(dates, as_of.isoformat())
    if i >= len(dates) or dates[i] != as_of.isoformat():
        i -= 1
        if i < 0:
            return None
    if i + 1 - lookback < 0:
        return None
    dollar_vols: list[float] = []
    for j in range(i + 1 - lookback, i + 1):
        c = closes[j]
        v = vols[j] if j < len(vols) else None
        if c is None or v is None or c <= 0 or v <= 0:
            return None
        dollar_vols.append(c * v)
    return statistics.median(dollar_vols)


def tradeable_universe(as_of: date,
                       min_price: float = MIN_PRICE_USD,
                       min_history_days: int = MIN_HISTORY_DAYS,
                       min_dollar_vol: float = MIN_DOLLAR_VOL,
                       max_hist_ratio: float = MAX_HIST_RATIO,
                       max_price: float = MAX_PRICE_USD) -> list[str]:
    """Return tickers passing all filters on date `as_of`.

    Filters:
      - cached close on `as_of`
      - >=min_history_days prior trading-day closes
      - close >= min_price both on `as_of` AND at the start of the
        momentum lookback window (kills reverse-split / pump artifacts)
      - >=$min_dollar_vol median 60-day dollar volume (kills illiquid
        quasi-OTC names that show low vol from nobody-trades-them, not
        from being stable companies; required for low-vol/quality to work)
      - close on `as_of` / current_stable_price <= max_hist_ratio (data
        quality: rejects tickers whose historical close is wildly inflated
        vs their current price, indicating unadjusted reverse-split
        corruption — e.g. ARSC showing $8000 closes in 2010-2016 when
        current is $0.10). Set max_hist_ratio=0 to disable.
      - close on `as_of` <= max_price unless in HIGH_PRICE_ALLOWLIST (data
        quality: rejects current-price ghosts like BKGM ~$10k that
        max_hist_ratio misses; allowlist exempts real high-price equities
        like NVR/BKNG). Set max_price=0 to disable.

    When volume data isn't cached for a ticker, it's EXCLUDED (conservative
    default). Run scripts/warm_volumes.py first to populate.
    """
    _build_index()
    if max_hist_ratio > 0:
        _build_stable_prices()
    out: list[str] = []
    for ticker in _TICKER_INDEX:
        if ticker in NON_STOCK_TICKERS or ticker.startswith("^"):
            continue  # ETFs / indices warmed for other strategies; not stocks
        i, px = _ticker_close_on(ticker, as_of)
        if px is None or px < min_price:
            continue
        if (max_price > 0 and px > max_price
                and ticker not in HIGH_PRICE_ALLOWLIST):
            continue  # current-price ghost (e.g. BKGM ~$10k); not a real equity
        if i < min_history_days:
            continue
        dates, prices = _TICKER_INDEX[ticker]
        old_px = prices[i - min_history_days]
        if old_px is None or old_px < min_price:
            continue
        if max_hist_ratio > 0:
            stable = _STABLE_PRICE.get(ticker)
            if stable is None or stable <= 0:
                continue  # insufficient recent data -> exclude
            if px / stable > max_hist_ratio or old_px / stable > max_hist_ratio:
                continue
        if min_dollar_vol > 0:
            adv = median_dollar_volume(ticker, as_of)
            if adv is None or adv < min_dollar_vol:
                continue
        out.append(ticker)
    out.sort()
    return out


def close_at_offset(ticker: str, as_of: date, trading_day_offset: int
                    ) -> float | None:
    """Close price `trading_day_offset` trading days from `as_of`.
    Negative = past, 0 = as_of itself, positive = future (rarely useful).
    Returns None if out of bounds or no cached close at that offset."""
    _build_index()
    if ticker not in _TICKER_INDEX:
        return None
    dates, prices = _TICKER_INDEX[ticker]
    iso = as_of.isoformat()
    i = bisect.bisect_left(dates, iso)
    if i >= len(dates) or dates[i] != iso:
        # as_of itself wasn't a trading day for this ticker; treat the
        # next-earlier cached date as the reference. Common at month
        # boundaries that land on weekends.
        i -= 1
        if i < 0:
            return None
    target = i + trading_day_offset
    if target < 0 or target >= len(dates):
        return None
    return prices[target]
