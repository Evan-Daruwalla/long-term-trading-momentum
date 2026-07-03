"""Alpaca asset tradability cache, shared by alpaca_sync (the mirror) and
paper_rebalance (the DB sim) so both agree on how a name can actually be bought.

Alpaca rejects a FRACTIONAL order on a non-fractionable asset, and can't trade a
delisted/inactive one at all. The DB sim holds fractional qty of everything, so
without this it silently diverges from the paper accounts (record Appendix on the
2026-07-01 mirror gap: XOM/SLGL/DMAA etc. never bought).

Design:
  - One tiny cache table `alpaca_asset_meta(ticker, tradable, fractionable,
    updated_at)`. `refresh(tickers, client)` fills it from Alpaca on demand.
  - `classify(tickers)` is a CACHE-ONLY read: unknown tickers default to
    tradable+fractionable, i.e. NO behavior change. So backtests / frozen specs
    (which never populate the cache and never pass a client) are unaffected —
    the whole-share/skip logic only kicks in for names we've actually looked up.
"""
from __future__ import annotations

from datetime import datetime, timezone

from trading_bot.db import connect

STALE_DAYS = 30  # re-query an asset's flags at most monthly


def _ensure_table(conn) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS alpaca_asset_meta ("
        " ticker TEXT PRIMARY KEY, tradable INTEGER, fractionable INTEGER,"
        " updated_at TEXT)")


def refresh(tickers, client) -> None:
    """Fetch tradable/fractionable for any tickers missing or stale in the cache.
    Needs a live AlpacaClient. A per-ticker lookup failure (e.g. unknown symbol)
    is recorded as untradable+non-fractionable rather than aborting the batch."""
    if not tickers or client is None:
        return
    now = datetime.now(timezone.utc)
    with connect() as conn:
        _ensure_table(conn)
        have = {r[0]: r[1] for r in conn.execute(
            "SELECT ticker, updated_at FROM alpaca_asset_meta")}
    fresh_cut = now.timestamp() - STALE_DAYS * 86400
    todo = []
    for t in set(tickers):
        u = have.get(t)
        if u is None:
            todo.append(t)
            continue
        try:
            if datetime.fromisoformat(u).timestamp() < fresh_cut:
                todo.append(t)
        except ValueError:
            todo.append(t)
    if not todo:
        return
    rows = []
    for t in todo:
        try:
            a = client.get_asset(t)
            rows.append((t, int(bool(a.get("tradable"))),
                         int(bool(a.get("fractionable"))), now.isoformat()))
        except Exception:  # unknown/removed symbol -> treat as untradable
            rows.append((t, 0, 0, now.isoformat()))
    with connect() as conn:
        _ensure_table(conn)
        conn.executemany(
            "INSERT INTO alpaca_asset_meta (ticker, tradable, fractionable, updated_at) "
            "VALUES (?,?,?,?) ON CONFLICT(ticker) DO UPDATE SET "
            "tradable=excluded.tradable, fractionable=excluded.fractionable, "
            "updated_at=excluded.updated_at", rows)


def classify(tickers) -> tuple[set[str], set[str]]:
    """CACHE-ONLY. Return (nonfractionable, untradable) among `tickers`.
    Unknown tickers are omitted from both sets (treated as fully tradable +
    fractionable) so nothing changes unless we've explicitly cached a flag."""
    tickers = set(tickers)
    if not tickers:
        return set(), set()
    nonfrac, untradable = set(), set()
    with connect() as conn:
        _ensure_table(conn)
        qs = ",".join("?" * len(tickers))
        for tk, tradable, fractionable in conn.execute(
                f"SELECT ticker, tradable, fractionable FROM alpaca_asset_meta "
                f"WHERE ticker IN ({qs})", tuple(tickers)):
            if not tradable:
                untradable.add(tk)
            elif not fractionable:
                nonfrac.add(tk)
    return nonfrac, untradable
