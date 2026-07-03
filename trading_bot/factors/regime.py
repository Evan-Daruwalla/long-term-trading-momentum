"""Market regime detection — mega-cap vs broad-market leadership.

Signal:
  SPY (market-cap-weighted) outperforming RSP (equal-weighted) over the
  trailing N months indicates mega-cap leadership. When small/mid-caps
  lead, SPY underperforms RSP.

This matters for factor selection per `memory/sleeves_verdict.md` attempt
10 (mom_then_accruals):
  - 2024-26 was a mega-cap regime; mom_then_accruals beat mom_v2 by
    +6.8 pp/yr held-out by filtering mom-winners through accruals quality
  - 2015-23 was a broader regime where mom's small-cap tail drove alpha;
    mom_then_accruals lost by -14.3 pp/yr in-sample

Goal: switch between mom_v2 (default) and mom_then_accruals (when
mega-cap regime detected) based on this gate.

Data: SPY + RSP closes, cached in price_cache via the inline warm we just
did (2014-06-02 onward, 3002 rows each). No lookahead — gate at date `d`
only uses prices through `d`.
"""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from functools import lru_cache

from trading_bot.config import DB_PATH

LOOKBACK_TRADING_DAYS = 126    # ~6 months


@lru_cache(maxsize=2)
def _load_closes(ticker: str) -> list[tuple[str, float]]:
    """Return sorted [(date_iso, close), ...] for one ticker."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT key_date, price FROM price_cache "
        "WHERE ticker=? AND kind='close' "
        "ORDER BY key_date",
        (ticker,),
    ).fetchall()
    conn.close()
    return [(d, p) for d, p in rows if p is not None]


def _trailing_return(ticker: str, as_of: date, lookback: int) -> float | None:
    """Return over the trailing `lookback` trading days ending at-or-before
    `as_of`. None if insufficient history."""
    closes = _load_closes(ticker)
    if not closes:
        return None
    iso = as_of.isoformat()
    # Find last close at-or-before as_of
    i_now = -1
    for i, (d, _) in enumerate(closes):
        if d <= iso:
            i_now = i
        else:
            break
    if i_now < lookback:
        return None
    p_now = closes[i_now][1]
    p_old = closes[i_now - lookback][1]
    if p_old <= 0:
        return None
    return p_now / p_old - 1.0


def is_mega_cap_regime(as_of: date,
                       lookback: int = LOOKBACK_TRADING_DAYS) -> bool | None:
    """True if SPY trailing return > RSP trailing return over `lookback`
    trading days. Returns None if either ticker lacks history."""
    spy = _trailing_return("SPY", as_of, lookback)
    rsp = _trailing_return("RSP", as_of, lookback)
    if spy is None or rsp is None:
        return None
    return spy > rsp
