"""Survivorship-bias correction for backtests.

Reads the `delistings` table populated by scripts/ingest_form25.py and
exposes a single lookup the simulator uses to:

  - Force-close positions whose ticker has stopped trading by `as_of`,
    fixing the "delisted ticker stays open forever" bug in earlier sims.
  - Skip new entries on tickers we already know are about to delist.

Past delistings are immutable, so we cache the whole table in memory at
first use. ~5K-10K rows; trivial.
"""
from __future__ import annotations

from datetime import date

from trading_bot.db import connect


_CACHE: dict[str, tuple[date, float | None, str | None]] = {}
_LOADED = False


def _ensure_loaded() -> None:
    global _LOADED
    if _LOADED:
        return
    with connect() as conn:
        # Table may not exist if ingest_form25 hasn't been run yet — degrade
        # gracefully: the simulator just behaves as before (no survivorship
        # correction) instead of crashing.
        try:
            rows = conn.execute(
                "SELECT ticker, delist_date, last_price, reason FROM delistings"
            ).fetchall()
        except Exception:
            rows = []
    for r in rows:
        _CACHE[r["ticker"]] = (
            date.fromisoformat(r["delist_date"]),
            r["last_price"],
            r["reason"],
        )
    _LOADED = True


def get_delisting(ticker: str) -> tuple[date, float | None, str | None] | None:
    """Return (delist_date, last_price, reason) if ticker is known delisted,
    else None. Idempotent / cheap to call repeatedly."""
    _ensure_loaded()
    return _CACHE.get(ticker)


def is_delisted_by(ticker: str, as_of: date) -> bool:
    """Convenience: True if ticker has a known delist_date <= as_of."""
    info = get_delisting(ticker)
    return info is not None and info[0] <= as_of
