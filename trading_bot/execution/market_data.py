"""Free market-data wrapper around yfinance, with a persistent SQLite cache.

We need three things:
  * `next_open_price(ticker, after)`  — the next available open price after `after`
  * `latest_price(ticker)`            — the latest available close (for monitoring)
  * `price_on_date(ticker, on)`       — the close price on a specific date
  * `sector(ticker)`                  — sector classification (for the 20% cap)

yfinance scrapes Yahoo Finance. It's free, requires no key, and is good
enough for a paper-trading bot — but Yahoo enforces a per-IP rate limit
(observed ~1500-2000 req/hour). On a 2-year backtest the lru_cache (4096
entries) is far too small, and re-running the same window for multiple
profiles re-hits yfinance for every (ticker, date) pair.

The persistent cache below stores all successful fetches in `price_cache`
and `sector_cache`. Past historical prices and sectors are immutable, so
cached values never expire. Transient failures ("Too Many Requests",
network errors) return None without caching, so a future call can retry.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import date, timedelta

import yfinance as yf

from trading_bot.db import connect


log = logging.getLogger(__name__)


# Sentinel distinguishes "key not in cache" from "key cached as None
# (permanent miss)". Without this we couldn't tell the two apart.
_MISS = object()
_TRANSIENT_HINTS = ("too many requests", "rate limit", "timed out", "timeout")


# Strict cache mode (env: STRICT_CACHE=1) makes any cache miss raise instead
# of silently falling through to a yfinance call. Use it once the warm
# scripts have populated everything: any miss is a real bug we should fix
# rather than a network failure to silently degrade through. Off by default
# so dev / live flows still work.
STRICT_CACHE = os.environ.get("STRICT_CACHE") == "1"


class CacheMiss(RuntimeError):
    """Raised in strict mode when a value isn't in the persistent cache."""
    pass


def _strict_miss(label: str) -> None:
    if STRICT_CACHE:
        raise CacheMiss(label)

# In-memory mirror of the persistent caches. Backtest runs do hundreds of
# thousands of price_cache / sector_cache lookups; one bulk SELECT into RAM
# at start replaces ~500K SQL roundtrips with O(1) dict lookups. Writes go
# to both layers so freshly-fetched yfinance values are visible immediately.
_MEM_PRICE: dict[tuple[str, str, str], float | None] = {}
_MEM_SECTOR: dict[str, str | None] = {}
_MEM_LOADED = False


def preload_caches() -> None:
    """Bulk-load price_cache + sector_cache into RAM. Idempotent."""
    global _MEM_LOADED
    if _MEM_LOADED:
        return
    log.info("preload_caches: loading price_cache + sector_cache into RAM")
    with connect() as conn:
        for ticker, kind, key_date, price in conn.execute(
            "SELECT ticker, kind, key_date, price FROM price_cache"
        ):
            _MEM_PRICE[(ticker, kind, key_date)] = price
        for ticker, sec in conn.execute(
            "SELECT ticker, sector FROM sector_cache"
        ):
            _MEM_SECTOR[ticker] = sec
    _MEM_LOADED = True
    log.info("preload_caches: %d price rows, %d sector rows",
             len(_MEM_PRICE), len(_MEM_SECTOR))


def _ensure_cache_schema() -> None:
    """Create cache tables if missing. Safe to call repeatedly."""
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS price_cache (
              ticker   TEXT NOT NULL,
              kind     TEXT NOT NULL,    -- 'close' or 'next_open'
              key_date TEXT NOT NULL,
              price    REAL,             -- NULL = cached miss (weekend/delisted)
              PRIMARY KEY (ticker, kind, key_date)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sector_cache (
              ticker TEXT PRIMARY KEY,
              sector TEXT
            )
            """
        )


_ensure_cache_schema()


def _cache_get(ticker: str, kind: str, key_date: str):
    if _MEM_LOADED:
        key = (ticker, kind, key_date)
        if key in _MEM_PRICE:
            return _MEM_PRICE[key]
        return _MISS
    with connect() as conn:
        row = conn.execute(
            "SELECT price FROM price_cache WHERE ticker=? AND kind=? AND key_date=?",
            (ticker, kind, key_date),
        ).fetchone()
    return _MISS if row is None else row[0]


def _cache_set(ticker: str, kind: str, key_date: str, price: float | None) -> None:
    if _MEM_LOADED:
        _MEM_PRICE[(ticker, kind, key_date)] = price
    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO price_cache (ticker, kind, key_date, price) "
            "VALUES (?, ?, ?, ?)",
            (ticker, kind, key_date, price),
        )


def _is_transient(exc: BaseException) -> bool:
    """Return True if the error looks like a rate limit / network blip we
    should retry later, not a permanent miss we should cache."""
    msg = str(exc).lower()
    return any(hint in msg for hint in _TRANSIENT_HINTS)


def next_open_price(ticker: str, after: date) -> float | None:
    """Open price on the first trading day strictly after `after`.

    Returns None if data isn't available (e.g. for a date in the future).
    Cached persistently per (ticker, after).
    """
    key = after.isoformat()
    cached = _cache_get(ticker, "next_open", key)
    if cached is not _MISS:
        return cached  # may legitimately be None for a permanent miss
    _strict_miss(f"next_open_price({ticker}, {key})")

    try:
        t = yf.Ticker(ticker)
        hist = t.history(
            start=after + timedelta(days=1),
            end=after + timedelta(days=11),
            auto_adjust=False,
        )
        price = float(hist.iloc[0]["Open"]) if not hist.empty else None
    except Exception as e:
        if _is_transient(e):
            log.warning("next_open_price(%s, %s) transient: %s", ticker, after, e)
            return None  # do not cache; let next caller retry
        log.warning("next_open_price(%s, %s) failed: %s", ticker, after, e)
        price = None  # cache the permanent miss

    _cache_set(ticker, "next_open", key, price)
    return price


def next_open_volume(ticker: str, after: date) -> float | None:
    """Volume on the first trading day strictly after `after`.

    Used by the broker's liquidity guard. Same lookahead window and caching
    as `next_open_price` so backtest replays are deterministic.
    """
    key = after.isoformat()
    cached = _cache_get(ticker, "next_open_vol", key)
    if cached is not _MISS:
        return cached
    _strict_miss(f"next_open_volume({ticker}, {key})")

    try:
        t = yf.Ticker(ticker)
        hist = t.history(
            start=after + timedelta(days=1),
            end=after + timedelta(days=11),
            auto_adjust=False,
        )
        vol = float(hist.iloc[0]["Volume"]) if not hist.empty else None
    except Exception as e:
        if _is_transient(e):
            log.warning("next_open_volume(%s, %s) transient: %s", ticker, after, e)
            return None
        log.warning("next_open_volume(%s, %s) failed: %s", ticker, after, e)
        vol = None

    _cache_set(ticker, "next_open_vol", key, vol)
    return vol


def next_open_range(ticker: str, after: date) -> float | None:
    """Intraday H-L range of the first trading day after `after`, expressed
    as a fraction of that day's open. Used to estimate the bid-ask spread
    via the Corwin-Schultz convention (half-spread ≈ 5% of H-L range).

    Returns None if data isn't available.
    """
    key = after.isoformat()
    cached = _cache_get(ticker, "next_open_range", key)
    if cached is not _MISS:
        return cached
    _strict_miss(f"next_open_range({ticker}, {key})")

    try:
        t = yf.Ticker(ticker)
        hist = t.history(
            start=after + timedelta(days=1),
            end=after + timedelta(days=11),
            auto_adjust=False,
        )
        if hist.empty:
            rng = None
        else:
            row = hist.iloc[0]
            o = float(row["Open"])
            rng = (float(row["High"]) - float(row["Low"])) / o if o > 0 else None
    except Exception as e:
        if _is_transient(e):
            log.warning("next_open_range(%s, %s) transient: %s", ticker, after, e)
            return None
        log.warning("next_open_range(%s, %s) failed: %s", ticker, after, e)
        rng = None

    _cache_set(ticker, "next_open_range", key, rng)
    return rng


def latest_price(ticker: str) -> float | None:
    """Most recent close (or last intraday print).

    Not cached persistently because "latest" changes daily; the call only
    fires as a fallback when next_open_price is unavailable.
    """
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d", auto_adjust=False)
        if hist.empty:
            return None
        return float(hist.iloc[-1]["Close"])
    except Exception as e:
        log.warning("latest_price(%s) failed: %s", ticker, e)
        return None


def price_on_date(ticker: str, target_date: date) -> float | None:
    """Closing price on `target_date`. None if non-trading day or no data.

    Cached persistently per (ticker, target_date).
    """
    key = target_date.isoformat()
    cached = _cache_get(ticker, "close", key)
    if cached is not _MISS:
        return cached
    _strict_miss(f"price_on_date({ticker}, {key})")

    try:
        t = yf.Ticker(ticker)
        hist = t.history(
            start=target_date,
            end=target_date + timedelta(days=1),
            auto_adjust=False,
        )
        price = float(hist.iloc[-1]["Close"]) if not hist.empty else None
    except Exception as e:
        if _is_transient(e):
            log.warning("price_on_date(%s, %s) transient: %s", ticker, target_date, e)
            return None
        log.warning("price_on_date(%s, %s) failed: %s", ticker, target_date, e)
        price = None

    _cache_set(ticker, "close", key, price)
    return price


def last_close_on_or_before(ticker: str, as_of: date
                            ) -> tuple[float | None, date | None]:
    """Most-recent cached close on `as_of` or the nearest prior trading day.

    Returns (price, date_of_that_price), or (None, None) if no close exists
    at-or-before `as_of`. This is the carry-forward lookup the live paper
    sim uses for fills (rebalance) and mark-to-market (NAV) — distinct from
    `price_on_date`, which is strict to the exact date. Reads price_cache
    directly (not the in-memory mirror) since it needs a range scan.
    """
    with connect() as conn:
        row = conn.execute(
            "SELECT price, key_date FROM price_cache "
            "WHERE ticker=? AND kind='close' AND key_date<=? "
            "ORDER BY key_date DESC LIMIT 1",
            (ticker, as_of.isoformat()),
        ).fetchone()
    if not row:
        return (None, None)
    return (row[0], date.fromisoformat(row[1]))


def dividends_per_share(ticker: str, since: date, until: date) -> float:
    """Sum of per-share cash dividends with ex-date in (since, until].

    Used by the broker at close_position to credit dividends earned during
    a holding period. Without this, strategies on dividend-paying tickers
    (utilities, REITs, financials) under-report ~25-50bps per 60-day hold.

    Lookup order mirrors split_ratio(): warmed dividends_json first
    (O(1)), legacy per-period cache, then cold yfinance. Returns 0.0 on
    transient errors (fail-conservative: missing dividends bias PnL down,
    never up).
    """
    if since >= until:
        return 0.0

    # Path 1: warmed dividends_json
    cached_json = _cache_get(ticker, "dividends_json", "all")
    if cached_json is not _MISS and cached_json is not None:
        try:
            events = json.loads(cached_json) if isinstance(cached_json, str) else []
        except (TypeError, ValueError):
            events = []
        total = 0.0
        for iso_d, amt in events:
            d = date.fromisoformat(iso_d)
            if since < d <= until and amt and amt > 0:
                total += float(amt)
        return total

    # Path 2: legacy per-period cache
    key = f"{since.isoformat()}|{until.isoformat()}"
    cached = _cache_get(ticker, "dividends_total", key)
    if cached is not _MISS:
        return float(cached) if cached is not None else 0.0
    # Strict mode is permissive here: missing dividends get treated as $0
    # rather than raising. Missed dividends bias PnL down (conservative);
    # missed prices would bias PnL toward fictional gains. Strict applies
    # to the dangerous calls, not this one.
    if STRICT_CACHE:
        return 0.0

    # Path 3: cold yfinance
    total = 0.0
    try:
        divs = yf.Ticker(ticker).dividends
        if divs is not None and len(divs) > 0:
            for ts, amt in divs.items():
                d = ts.date() if hasattr(ts, "date") else ts
                if since < d <= until and amt and amt > 0:
                    total += float(amt)
    except Exception as e:
        if _is_transient(e):
            log.warning("dividends_per_share(%s, %s, %s) transient: %s",
                        ticker, since, until, e)
            return 0.0
        log.warning("dividends_per_share(%s, %s, %s) failed: %s",
                    ticker, since, until, e)

    _cache_set(ticker, "dividends_total", key, total)
    return total


def split_ratio(ticker: str, since: date, until: date) -> float:
    """Cumulative split factor between `since` (exclusive) and `until` (inclusive).

    Returns the multiplier to apply to a pre-`since` share count to obtain
    the post-`until` share count. Forward 2:1 split → 2.0; reverse 1:5
    split → 0.2; multiple events compose multiplicatively.

    Lookup order:
      1. In-memory splits_json cache (warmed by scripts/warm_splits.py) —
         O(1) lookup for the ticker's full split history, then a tiny in-
         Python pass over the (typically 0-2) events in the period.
      2. Persistent (ticker, since|until) cache for legacy entries.
      3. Cold yfinance call as last resort.

    Returns 1.0 on transient errors so a missed split biases PnL toward
    zero rather than toward fictional gains.
    """
    if since >= until:
        return 1.0

    # Path 1: warmed splits_json. price column holds a JSON string for this
    # kind; SQLite's flexible typing lets us reuse the table.
    cached_json = _cache_get(ticker, "splits_json", "all")
    if cached_json is not _MISS and cached_json is not None:
        try:
            events = json.loads(cached_json) if isinstance(cached_json, str) else []
        except (TypeError, ValueError):
            events = []
        ratio = 1.0
        for iso_d, r in events:
            d = date.fromisoformat(iso_d)
            if since < d <= until and r and r > 0:
                ratio *= float(r)
        return ratio

    # Path 2: legacy per-period cache (preserves existing entries).
    key = f"{since.isoformat()}|{until.isoformat()}"
    cached = _cache_get(ticker, "split_ratio", key)
    if cached is not _MISS:
        return float(cached) if cached is not None else 1.0
    _strict_miss(f"split_ratio({ticker}, {since}, {until})")

    # Path 3: cold yfinance.
    ratio = 1.0
    try:
        splits = yf.Ticker(ticker).splits
        if splits is not None and len(splits) > 0:
            for ts, r in splits.items():
                d = ts.date() if hasattr(ts, "date") else ts
                if since < d <= until and r and r > 0:
                    ratio *= float(r)
    except Exception as e:
        if _is_transient(e):
            log.warning("split_ratio(%s, %s, %s) transient: %s",
                        ticker, since, until, e)
            return 1.0
        log.warning("split_ratio(%s, %s, %s) failed: %s",
                    ticker, since, until, e)

    _cache_set(ticker, "split_ratio", key, ratio)
    return ratio


def atr_pct(ticker: str, as_of: date, window: int = 20) -> float | None:
    """Average True Range over `window` trading days ending on `as_of`,
    expressed as a fraction of the close on `as_of`.

    Used by monitor.py to size stops by realized volatility instead of a
    fixed -X% rule. Cached per (ticker, as_of, window) under
    `kind=f"atr_pct_{window}"` in price_cache. Returns None for insufficient
    history or transient yfinance errors.
    """
    kind = f"atr_pct_{window}"
    key = as_of.isoformat()
    cached = _cache_get(ticker, kind, key)
    if cached is not _MISS:
        return cached
    _strict_miss(f"atr_pct({ticker}, {key}, {window})")

    try:
        # Need `window` TR values, which requires window+1 daily bars (TR
        # uses the prior close). 1.7x calendar buffer for weekends/holidays.
        start = as_of - timedelta(days=int((window + 1) * 1.7) + 5)
        hist = yf.Ticker(ticker).history(
            start=start, end=as_of + timedelta(days=1), auto_adjust=False
        )
        if hist.empty or len(hist) < window + 1:
            result: float | None = None
        else:
            tail = hist.tail(window + 1)
            highs = tail["High"].astype(float)
            lows = tail["Low"].astype(float)
            closes = tail["Close"].astype(float)
            prev_closes = closes.shift(1)
            # True Range = max(H-L, |H - prev_close|, |L - prev_close|)
            tr = (highs - lows).combine(
                (highs - prev_closes).abs(), max
            ).combine((lows - prev_closes).abs(), max).iloc[1:]
            atr = float(tr.mean())
            last_close = float(closes.iloc[-1])
            result = atr / last_close if last_close > 0 else None
    except Exception as e:
        if _is_transient(e):
            log.warning("atr_pct(%s, %s, %d) transient: %s",
                        ticker, as_of, window, e)
            return None  # don't cache transient
        log.warning("atr_pct(%s, %s, %d) failed: %s",
                    ticker, as_of, window, e)
        result = None

    _cache_set(ticker, kind, key, result)
    return result


def is_above_ma(ticker: str, as_of: date, window: int = 50) -> bool | None:
    """True if `as_of`'s close is above the `window`-day moving average.

    Returns None when there's insufficient history (delisted, sparse data,
    new listing) or a transient API error. Caller decides how to treat None
    — runner.py treats it as "pass" so yfinance flakiness doesn't penalize
    real signals.

    Cached per (ticker, as_of, window) under `kind=f"above_ma_{window}"` in
    the existing price_cache table: 1.0 = True, 0.0 = False, NULL = None.
    Past MAs are immutable so the cache never expires.
    """
    kind = f"above_ma_{window}"
    key = as_of.isoformat()
    cached = _cache_get(ticker, kind, key)
    if cached is not _MISS:
        return None if cached is None else bool(cached)
    _strict_miss(f"is_above_ma({ticker}, {key}, {window})")

    try:
        # Calendar days covering ~window trading days plus a margin. 1.7x
        # accounts for weekends + the occasional holiday.
        start = as_of - timedelta(days=int(window * 1.7) + 5)
        hist = yf.Ticker(ticker).history(
            start=start, end=as_of + timedelta(days=1), auto_adjust=False
        )
        if hist.empty:
            result: bool | None = None
        else:
            closes = hist["Close"].dropna()
            if len(closes) < window:
                result = None
            else:
                ma = float(closes.tail(window).mean())
                current = float(closes.iloc[-1])
                result = current > ma
    except Exception as e:
        if _is_transient(e):
            log.warning("is_above_ma(%s, %s, %d) transient: %s", ticker, as_of, window, e)
            return None  # don't cache transient
        log.warning("is_above_ma(%s, %s, %d) failed: %s", ticker, as_of, window, e)
        result = None

    _cache_set(ticker, kind, key,
               None if result is None else float(result))
    return result


def sector(ticker: str) -> str | None:
    """Sector classification from yfinance's .info dict.

    Cached persistently per ticker.
    """
    if _MEM_LOADED and ticker in _MEM_SECTOR:
        return _MEM_SECTOR[ticker]
    with connect() as conn:
        row = conn.execute(
            "SELECT sector FROM sector_cache WHERE ticker=?", (ticker,)
        ).fetchone()
    if row is not None:
        if _MEM_LOADED:
            _MEM_SECTOR[ticker] = row[0]
        return row[0]
    _strict_miss(f"sector({ticker})")

    try:
        info = yf.Ticker(ticker).info
        sec = info.get("sector") or None
    except Exception as e:
        if _is_transient(e):
            log.warning("sector(%s) transient: %s", ticker, e)
            return None  # don't cache transient
        log.warning("sector(%s) failed: %s", ticker, e)
        sec = None

    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO sector_cache (ticker, sector) VALUES (?, ?)",
            (ticker, sec),
        )
    if _MEM_LOADED:
        _MEM_SECTOR[ticker] = sec
    return sec
