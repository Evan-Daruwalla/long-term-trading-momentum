"""Tests for fill-provenance capture (record CU). Fixture DB only; live DB untouched.

Covers the two halves separately:
  1. The migration turns an OLD-schema paper_positions into the new one, is
     idempotent, and leaves existing rows intact with NULL provenance.
  2. A real buy() and sell() through paper_trader persist ref_close/ref_date -
     and, critically, still compute identical prices, qty, cash and P&L. These
     columns are provenance; if they changed any arithmetic they would be a bug.

Run:
    python -m scripts.momentum.test_fill_reference
"""
from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import date
from pathlib import Path

from scripts import add_fill_reference_columns as mig

OLD_SCHEMA = """
CREATE TABLE paper_positions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  strategy_name TEXT NOT NULL, ticker TEXT NOT NULL, status TEXT NOT NULL,
  qty REAL NOT NULL, entry_price REAL NOT NULL, entry_value REAL NOT NULL,
  entry_date TEXT NOT NULL, entry_score REAL, sector TEXT,
  exit_price REAL, exit_value REAL, exit_date TEXT, exit_reason TEXT,
  realized_pnl REAL, realized_pnl_pct REAL
);
"""


def test_migration() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="fillref_")) / "old.db"
    c = sqlite3.connect(tmp)
    c.executescript(OLD_SCHEMA)
    c.execute("INSERT INTO paper_positions (strategy_name, ticker, status, qty, "
              "entry_price, entry_value, entry_date) "
              "VALUES ('s','AAA','open',10,100.0,1000.0,'2026-07-07')")
    c.commit()
    c.close()

    assert "entry_ref_close" not in mig.existing_columns(sqlite3.connect(tmp))
    sys.argv = ["x", "--db", str(tmp)]
    assert mig.main() == 0                       # dry run
    assert "entry_ref_close" not in mig.existing_columns(sqlite3.connect(tmp)), \
        "dry run must not write"
    print("  [OK  ] migration: dry run changes nothing")

    sys.argv = ["x", "--db", str(tmp), "--execute"]
    assert mig.main() == 0
    con = sqlite3.connect(tmp)
    cols = mig.existing_columns(con)
    for c_ in ("entry_ref_close", "entry_ref_date", "exit_ref_close", "exit_ref_date"):
        assert c_ in cols, c_
    row = con.execute("SELECT entry_price, entry_ref_close FROM paper_positions").fetchone()
    assert row == (100.0, None), row      # pre-existing row intact, provenance NULL
    con.close()
    print("  [OK  ] migration: 4 columns added, existing row intact, provenance NULL")

    assert mig.main() == 0                       # re-run
    print("  [OK  ] migration: idempotent on re-run")


def test_capture_and_no_arithmetic_change() -> None:
    from trading_bot import db as dbmod
    from trading_bot.execution import paper_trader

    tmp = Path(tempfile.mkdtemp(prefix="fillref_live_"))
    dbmod.close_thread_connection()
    dbmod.DB_PATH = tmp / "trades.db"
    dbmod.VAR_DIR = tmp
    dbmod.init_db()

    paper_trader.init("t_paper", starting_cash=100_000.0)
    ref_close, ref_dt = 250.00, date(2026, 8, 3)
    fill_buy = ref_close * 1.0005                       # what paper_rebalance does
    pid = paper_trader.buy(strategy_name="t_paper", ticker="AAA", qty=4.0,
                           fill_price=fill_buy, as_of=date(2026, 8, 4),
                           ref_close=ref_close, ref_date=ref_dt)

    with dbmod.connect() as conn:
        r = conn.execute("SELECT * FROM paper_positions WHERE id=?", (pid,)).fetchone()
    assert r["entry_ref_close"] == 250.00, r["entry_ref_close"]
    assert r["entry_ref_date"] == "2026-08-03", r["entry_ref_date"]
    # ref_date is the CLOSE's date, deliberately NOT the fill date.
    assert r["entry_date"] == "2026-08-04"
    assert abs(r["entry_price"] - 250.125) < 1e-9, r["entry_price"]
    assert abs(r["entry_value"] - 1000.50) < 1e-9, r["entry_value"]
    assert abs(paper_trader.get("t_paper").cash - (100_000.0 - 1000.50)) < 1e-9
    print("  [OK  ] buy: provenance stored; price/value/cash unchanged")

    # The round-trip that matters: the stored reference reproduces the fill.
    assert abs(r["entry_ref_close"] * 1.0005 - r["entry_price"]) < 1e-9
    print("  [OK  ] buy: ref_close x (1+5bps) reproduces entry_price exactly")

    sell_ref, sell_dt = 260.00, date(2026, 8, 10)
    fill_sell = sell_ref * 0.9995
    realized = paper_trader.sell(position_id=pid, qty=4.0, fill_price=fill_sell,
                                 as_of=date(2026, 8, 11), strategy_name="t_paper",
                                 ref_close=sell_ref, ref_date=sell_dt)
    with dbmod.connect() as conn:
        r2 = conn.execute("SELECT * FROM paper_positions WHERE id=?", (pid,)).fetchone()
    assert r2["exit_ref_close"] == 260.00 and r2["exit_ref_date"] == "2026-08-10"
    assert abs(r2["exit_ref_close"] * 0.9995 - r2["exit_price"]) < 1e-9
    assert abs(realized - (fill_sell - fill_buy) * 4.0) < 1e-9, realized
    assert r2["status"] == "closed"
    print("  [OK  ] sell: provenance stored; ref x (1-5bps) reproduces exit_price; "
          "P&L unchanged")

    # Omitting the new args must still work — every legacy caller does.
    pid2 = paper_trader.buy(strategy_name="t_paper", ticker="BBB", qty=1.0,
                            fill_price=10.0, as_of=date(2026, 8, 4))
    with dbmod.connect() as conn:
        r3 = conn.execute("SELECT * FROM paper_positions WHERE id=?", (pid2,)).fetchone()
    assert r3["entry_ref_close"] is None and r3["entry_ref_date"] is None
    assert abs(r3["entry_price"] - 10.0) < 1e-9
    print("  [OK  ] legacy call without ref args still works, stores NULL")

    dbmod.close_thread_connection()


def main() -> int:
    print("Running fill-reference tests...")
    test_migration()
    test_capture_and_no_arithmetic_change()
    print("\nAll fill-reference tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
