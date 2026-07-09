"""Regression test for the pre-inception NAV guard in paper_mtm (record M3.1).

Builds a tiny fixture DB (temp file), points the DB layer at it, and asserts:
  1. inception_date = min(date(initialized_at), earliest entry_date) for the two
     real-world sleeve shapes — backdated (init later than history) and the
     07-06 cohort (positions fill the next open, after inception).
  2. MTM for a date BEFORE inception writes NO paper_nav row (SKIP pre-inception).
  3. MTM for the inception day and a later live date DO write a row (unchanged
     behavior for live sleeves).

No live DB, no price_cache needed (the write cases use a cash-only sleeve).

Run:
    python -m scripts.momentum.test_inception_guard
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

from trading_bot import db as dbmod


def _fixture():
    tmp = Path(tempfile.mkdtemp(prefix="pm_inception_"))
    dbmod.close_thread_connection()
    dbmod.DB_PATH = tmp / "trades.db"
    dbmod.VAR_DIR = tmp
    dbmod.init_db()

    def add_portfolio(name, initialized_at):
        with dbmod.connect() as c:
            c.execute("INSERT INTO paper_portfolio "
                      "(strategy_name, starting_cash, cash, initialized_at) "
                      "VALUES (?, 100000, 100000, ?)", (name, initialized_at))

    def add_position(name, ticker, entry_date):
        with dbmod.connect() as c:
            c.execute("INSERT INTO paper_positions "
                      "(strategy_name, ticker, status, qty, entry_price, entry_value, "
                      " entry_date) VALUES (?, ?, 'open', 10, 100, 1000, ?)",
                      (name, ticker, entry_date))

    # A) backdated: init 2026-06-13, but a position back at 2026-05-01.
    add_portfolio("backdated_sleeve", "2026-06-13T18:00:00+00:00")
    add_position("backdated_sleeve", "AAA", "2026-05-01")
    # B) cohort: init 2026-07-06, first fill at the next open 2026-07-07.
    add_portfolio("cohort_sleeve", "2026-07-06T00:00:00+00:00")
    add_position("cohort_sleeve", "BBB", "2026-07-07")
    # C) cash-only: init 2026-07-06, no positions (drives the MTM write cases).
    add_portfolio("cash_sleeve", "2026-07-06T00:00:00+00:00")
    return tmp


def _nav_rows(strategy, d):
    with dbmod.connect() as c:
        return c.execute("SELECT COUNT(*) FROM paper_nav WHERE strategy_name=? AND nav_date=?",
                         (strategy, d)).fetchone()[0]


def main() -> int:
    # Import paper_mtm AFTER we can patch the DB layer; it reads dbmod globals at
    # call time, so patching before calling main() is enough.
    from scripts.momentum import paper_mtm

    tmp = _fixture()
    failures: list[str] = []

    def run_mtm(strategy, as_of):
        # paper_mtm.main() parses sys.argv, so drive it through argv.
        saved = sys.argv
        sys.argv = ["paper_mtm", "--strategy", strategy, "--as-of", as_of]
        try:
            return paper_mtm.main()
        finally:
            sys.argv = saved

    def check(cond, msg):
        print(f"  [{'OK  ' if cond else 'FAIL'}] {msg}")
        if not cond:
            failures.append(msg)

    print("Running pre-inception guard tests...")

    # 1. inception_date for the two shapes.
    inc_back = paper_mtm.inception_date("backdated_sleeve")
    inc_cohort = paper_mtm.inception_date("cohort_sleeve")
    inc_cash = paper_mtm.inception_date("cash_sleeve")
    check(inc_back == date(2026, 5, 1),
          f"backdated inception = 2026-05-01 (got {inc_back})")
    check(inc_cohort == date(2026, 7, 6),
          f"cohort inception = 2026-07-06, not first-fill 07-07 (got {inc_cohort})")
    check(inc_cash == date(2026, 7, 6),
          f"cash-only inception = 2026-07-06 (got {inc_cash})")

    # 2. Pre-inception date -> skipped, no row.
    rc = run_mtm("cash_sleeve", "2026-07-03")
    check(rc == 0 and _nav_rows("cash_sleeve", "2026-07-03") == 0,
          "MTM 2026-07-03 (pre-inception) writes NO nav row")

    # 3. Inception day -> written (as_of == inception is allowed).
    rc = run_mtm("cash_sleeve", "2026-07-06")
    check(rc == 0 and _nav_rows("cash_sleeve", "2026-07-06") == 1,
          "MTM 2026-07-06 (inception day) writes a nav row")

    # 4. Later live date -> written (unchanged behavior).
    rc = run_mtm("cash_sleeve", "2026-07-09")
    check(rc == 0 and _nav_rows("cash_sleeve", "2026-07-09") == 1,
          "MTM 2026-07-09 (live date) writes a nav row")

    dbmod.close_thread_connection()
    try:
        shutil.rmtree(tmp)
    except OSError:
        pass  # temp dir; harmless if Windows holds a handle

    if failures:
        print(f"\nFAILED: {len(failures)} guard regression(s)")
        return 1
    print("\nAll pre-inception guard tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
