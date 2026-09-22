"""Regression test: compute_nav marks a PAST date with that date's cash + positions.

Record DV (2026-09-22). `compute_nav` read cash from `paper_portfolio.cash` and
the open set from `list_open()` -- both TODAY's. Re-marking a past date the
sleeve had traded since therefore paired today's book with that date's closes:
17 weekly-ladder sleeves' 2026-09-17 rows carry the 09-21 cash and n_open
(53 -> 61) after a hand re-mark on 09-22. The fix replays the ledger
(historical_state.state_at) when there is activity after as_of.

Fixture: one sleeve, $100k start. 07-01 buys A (100 @ $50). 07-10 sells A
(@ $55) and buys B (10 @ $100). Live cash = 100000 - 5000 + 5500 - 1000 = 99500.
  1. mark 07-05 (traded since) -> cash 95000, holds A only, NAV 95000 + 100*52.
  2. mark 07-10 (nothing after) -> live path unchanged: cash 99500, holds B.

No live DB, no network.

Run:
    python -m scripts.momentum.test_compute_nav_asof
"""
from __future__ import annotations

import sys
import tempfile
from datetime import date
from pathlib import Path

from trading_bot import db as dbmod
from trading_bot.execution import market_data

S = "asof_sleeve"


def _fixture() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="pm_navasof_"))
    dbmod.close_thread_connection()
    dbmod.DB_PATH = tmp / "trades.db"
    dbmod.VAR_DIR = tmp
    dbmod.init_db()
    market_data._ensure_cache_schema()
    with dbmod.connect() as c:
        c.execute("INSERT INTO paper_portfolio "
                  "(strategy_name, starting_cash, cash, initialized_at) "
                  "VALUES (?, 100000, 99500, '2026-07-01T00:00:00+00:00')", (S,))
        c.execute("INSERT INTO paper_positions "
                  "(strategy_name, ticker, status, qty, entry_price, entry_value, "
                  " entry_date, exit_price, exit_value, exit_date) "
                  "VALUES (?, 'AAA', 'closed', 100, 50, 5000, '2026-07-01', "
                  "        55, 5500, '2026-07-10')", (S,))
        c.execute("INSERT INTO paper_positions "
                  "(strategy_name, ticker, status, qty, entry_price, entry_value, "
                  " entry_date) "
                  "VALUES (?, 'BBB', 'open', 10, 100, 1000, '2026-07-10')", (S,))
        for t, d, px in (("AAA", "2026-07-05", 52.0), ("AAA", "2026-07-10", 55.0),
                         ("BBB", "2026-07-10", 100.0)):
            c.execute("INSERT INTO price_cache (ticker, kind, key_date, price) "
                      "VALUES (?, 'close', ?, ?)", (t, d, px))
    return tmp


def main() -> int:
    from scripts.momentum import paper_mtm

    _fixture()
    failures: list[str] = []

    def check(cond, msg):
        print(f"  [{'OK  ' if cond else 'FAIL'}] {msg}")
        if not cond:
            failures.append(msg)

    print("Running compute_nav as-of tests...")

    nav = paper_mtm.compute_nav(S, date(2026, 7, 5))
    check(abs(nav["cash"] - 95_000) < 1e-9,
          f"past date (traded since) uses as-of cash $95,000 (got ${nav['cash']:,.2f})")
    check(nav["n_open"] == 1 and abs(nav["positions_value"] - 5_200) < 1e-9,
          f"past date holds AAA only, 100 x $52 (got n_open {nav['n_open']}, "
          f"pv ${nav['positions_value']:,.2f})")
    check(abs(nav["total_nav"] - 100_200) < 1e-9,
          f"past-date NAV $100,200.00 (got ${nav['total_nav']:,.2f})")

    nav = paper_mtm.compute_nav(S, date(2026, 7, 10))
    check(nav["cash"] == 99_500 and nav["n_open"] == 1,
          f"no later activity -> live cash $99,500 exactly (got ${nav['cash']:,.2f})")
    check(abs(nav["total_nav"] - 100_500) < 1e-9,
          f"latest-date NAV $100,500.00 (got ${nav['total_nav']:,.2f})")

    dbmod.close_thread_connection()
    print(f"\n{'PASS' if not failures else 'FAIL'}: "
          f"{5 - len(failures)}/5 checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
