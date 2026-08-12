"""Tests that a factor backtest cannot write the live positions / portfolio_state.

Audit finding CQ.2 #2: the frozen regression tests ARE a `factor_backtest`, and
`_wipe_state()` did `DELETE FROM positions` / `portfolio_state` through a
read-WRITE connection on the live 5 GB DB -- so the check `CLAUDE.md` mandates
after every Python change was the second-writer operation it separately forbids.
The fix shadows those two tables with per-connection TEMP copies (record CZ).

What is actually asserted here, in the order that matters:

  1. The live rows SURVIVE a full `_wipe_state()`. That is the finding.
  2. `price_cache` is NOT shadowed. Redirecting the whole connection to a
     scratch DB would have taken the 37.7M-row cache with it, which is exactly
     why the auditor's proposed fix did not hold.
  3. The shadow's columns match the live table's, INCLUDING the ones added by
     `init_db()`'s defensive ALTERs rather than declared in `SCHEMA`. A shadow
     built from `SCHEMA` would silently be missing them.

Run:
    python -m scripts.momentum.test_backtest_state_isolation
"""
from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path


def _fresh_db() -> Path:
    """A real DB at a temp path, with one sentinel row in each backtest table."""
    from trading_bot import db as dbmod

    tmp = Path(tempfile.mkdtemp(prefix="btstate_"))
    dbmod.close_thread_connection()
    dbmod.DB_PATH = tmp / "trades.db"
    dbmod.VAR_DIR = tmp
    dbmod.init_db()
    with dbmod.connect() as conn:
        conn.execute("INSERT INTO positions (ticker, status, qty, entry_price, "
                     "entry_value, entry_time) VALUES "
                     "('SENTINEL','open',1,1.0,1.0,'2026-08-11T00:00:00Z')")
        conn.execute("INSERT INTO portfolio_state (id, starting_cash, cash, "
                     "initialized_at, updated_at) VALUES "
                     "(1, 12345.0, 12345.0, '2026-08-11', '2026-08-11')")
        conn.execute("CREATE TABLE IF NOT EXISTS price_cache (ticker TEXT, "
                     "kind TEXT, key_date TEXT, price REAL)")
        conn.execute("INSERT INTO price_cache VALUES ('SPY','close','2026-08-11',600.0)")
    dbmod.close_thread_connection()
    return dbmod.DB_PATH


def test_wipe_state_leaves_the_live_rows_alone() -> None:
    from trading_bot import db as dbmod
    from trading_bot.execution import factor_backtest

    db_path = _fresh_db()

    # The real thing: _wipe_state() is what runs first in every backtest.
    factor_backtest._wipe_state()

    with dbmod.connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM positions").fetchone()[0] == 0, \
            "the backtest's own view must start empty"
        live_pos = [r[0] for r in conn.execute("SELECT ticker FROM main.positions")]
        live_cash = conn.execute(
            "SELECT cash FROM main.portfolio_state WHERE id=1").fetchone()[0]
    assert live_pos == ["SENTINEL"], f"live positions were written: {live_pos}"
    assert live_cash == 12345.0, f"live portfolio_state was written: {live_cash}"
    print("  [OK  ] _wipe_state(): backtest view empty, live rows untouched")

    # And the isolation holds for WRITES, not just the wipe.
    with dbmod.connect() as conn:
        conn.execute("INSERT INTO positions (ticker, status, qty, entry_price, "
                     "entry_value, entry_time) VALUES "
                     "('BACKTEST','open',5,10.0,50.0,'2026-08-11T00:00:01Z')")
    with dbmod.connect() as conn:
        assert [r[0] for r in conn.execute("SELECT ticker FROM positions")] == \
            ["BACKTEST"]
        assert [r[0] for r in conn.execute("SELECT ticker FROM main.positions")] == \
            ["SENTINEL"], "a backtest insert reached the live table"
    print("  [OK  ] a backtest INSERT lands in temp, not in the live table")

    # Nothing survives the connection: reopening the FILE shows only the sentinel.
    dbmod.close_thread_connection()
    raw = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    on_disk = [r[0] for r in raw.execute("SELECT ticker FROM positions")]
    raw.close()
    assert on_disk == ["SENTINEL"], f"backtest state persisted to disk: {on_disk}"
    print("  [OK  ] nothing persisted to the DB file")


def test_price_cache_is_not_shadowed() -> None:
    """The reason a scratch-DB redirect was the WRONG fix."""
    from trading_bot import db as dbmod

    _fresh_db()
    dbmod.shadow_backtest_state()
    with dbmod.connect() as conn:
        shadowed = {r[0] for r in conn.execute(
            "SELECT name FROM temp.sqlite_master WHERE type='table'")}
        px = conn.execute(
            "SELECT price FROM price_cache WHERE ticker='SPY'").fetchone()[0]
    assert "price_cache" not in shadowed, shadowed
    assert px == 600.0, f"price_cache no longer readable: {px}"
    print("  [OK  ] price_cache is NOT shadowed and still reads from the live DB")
    dbmod.close_thread_connection()


def test_shadow_matches_live_columns_and_is_idempotent() -> None:
    from trading_bot import db as dbmod

    _fresh_db()
    first = dbmod.shadow_backtest_state()
    assert set(first) == set(dbmod.BACKTEST_STATE_TABLES), first
    second = dbmod.shadow_backtest_state()
    assert second == (), f"re-shadowing must be a no-op, got {second}"
    print("  [OK  ] shadow is idempotent")

    with dbmod.connect() as conn:
        for table in dbmod.BACKTEST_STATE_TABLES:
            live = dbmod._columns(conn, "main", table)
            temp = dbmod._columns(conn, "temp", table)
            assert live == temp, f"{table}: live={live} temp={temp}"
        # The specific trap: these columns come from init_db()'s ALTERs, NOT
        # from SCHEMA, so a shadow built off SCHEMA would be missing them.
        cols = dbmod._columns(conn, "temp", "positions")
        for c in ("peak_close_price", "split_ratio_at_exit", "dividends_received"):
            assert c in cols, f"{c} missing from the shadow: {cols}"
    print("  [OK  ] shadow columns match live, including the ALTER-added ones")

    dropped = dbmod.unshadow_backtest_state()
    assert set(dropped) == set(dbmod.BACKTEST_STATE_TABLES), dropped
    with dbmod.connect() as conn:
        assert [r[0] for r in conn.execute("SELECT ticker FROM positions")] == \
            ["SENTINEL"], "unshadow did not restore the live view"
    print("  [OK  ] unshadow restores the live view")
    dbmod.close_thread_connection()


def main() -> int:
    print("Running backtest-state isolation tests (fixture DB only)...")
    test_wipe_state_leaves_the_live_rows_alone()
    test_price_cache_is_not_shadowed()
    test_shadow_matches_live_columns_and_is_idempotent()
    print("\nAll backtest-state isolation tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
