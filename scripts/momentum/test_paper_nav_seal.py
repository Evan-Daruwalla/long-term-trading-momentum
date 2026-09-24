"""Regression test: paper_nav is narrowly append-only (audit stage 5, record DX).

A row is SEALED once its sleeve has a newer row. The daily pipeline must keep
working untouched -- gap-fill (insert a missing older day) and same-day re-mark
(rewrite the LATEST row) -- while any restatement of a sealed row is refused
unless a paper_nav_restatement row for that (sleeve, date) was logged in the
last 10 minutes. The restatement log is itself append-only.

Builds a fixture DB (temp file) and writes through paper_mtm.write_nav, the one
production writer, plus raw SQL for UPDATE/DELETE. No live DB, no network.

Run:
    python -m scripts.momentum.test_paper_nav_seal
"""
from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import date
from pathlib import Path

from trading_bot import db as dbmod

S = "seal_sleeve"


def _nav(total: float) -> dict:
    return {"cash": 1.0, "positions_value": total - 1.0, "total_nav": total, "n_open": 1}


def main() -> int:
    from scripts.momentum import paper_mtm

    tmp = Path(tempfile.mkdtemp(prefix="pm_navseal_"))
    dbmod.close_thread_connection()
    dbmod.DB_PATH = tmp / "trades.db"
    dbmod.VAR_DIR = tmp
    dbmod.init_db()
    failures: list[str] = []
    passed: list[str] = []

    def check(cond, msg):
        print(f"  [{'OK  ' if cond else 'FAIL'}] {msg}")
        (passed if cond else failures).append(msg)

    def refused(fn) -> bool:
        try:
            fn()
        except sqlite3.IntegrityError as e:
            return "sealed" in str(e) or "append-only" in str(e)
        return False

    def stored(d: str) -> float | None:
        with dbmod.connect() as c:
            r = c.execute("SELECT total_nav FROM paper_nav WHERE strategy_name=? "
                          "AND nav_date=?", (S, d)).fetchone()
        return r[0] if r else None

    def sql(q, *a):
        with dbmod.connect() as c:
            c.execute(q, a)

    print("Running paper_nav seal tests...")
    d1, d2, d3 = date(2026, 9, 14), date(2026, 9, 15), date(2026, 9, 16)
    paper_mtm.write_nav(S, d1, _nav(100.0))
    paper_mtm.write_nav(S, d3, _nav(300.0))

    # Pipeline paths that must keep working.
    paper_mtm.write_nav(S, d2, _nav(200.0))                       # gap-fill
    check(stored("2026-09-15") == 200.0, "gap-fill of a missing older day is allowed")
    paper_mtm.write_nav(S, d3, _nav(301.0))                       # same-day re-mark
    check(stored("2026-09-16") == 301.0, "re-marking the LATEST row is allowed")
    sql("UPDATE paper_nav SET total_nav=302 WHERE strategy_name=? AND nav_date=?",
        S, "2026-09-16")
    check(stored("2026-09-16") == 302.0, "UPDATE of the latest row is allowed")

    # Restating a sealed row is refused on every path.
    check(refused(lambda: paper_mtm.write_nav(S, d1, _nav(999.0))),
          "INSERT OR REPLACE of a sealed row is refused (write_nav path)")
    check(refused(lambda: sql("UPDATE paper_nav SET total_nav=999 WHERE "
                              "strategy_name=? AND nav_date=?", S, "2026-09-14")),
          "UPDATE of a sealed row is refused")
    check(refused(lambda: sql("DELETE FROM paper_nav WHERE strategy_name=? "
                              "AND nav_date=?", S, "2026-09-14")),
          "DELETE of a sealed row is refused")
    check(stored("2026-09-14") == 100.0, "the sealed row is unchanged after all three")

    # A stale restatement (11 min old) does not unseal; a fresh one does.
    sql("INSERT INTO paper_nav_restatement (strategy_name, nav_date, reason, created_at) "
        "VALUES (?, ?, 'stale', datetime('now', '-11 minutes'))", S, "2026-09-14")
    check(refused(lambda: paper_mtm.write_nav(S, d1, _nav(999.0))),
          "a restatement logged 11 minutes ago does NOT unseal")
    sql("INSERT INTO paper_nav_restatement (strategy_name, nav_date, reason) "
        "VALUES (?, ?, 'fresh')", S, "2026-09-14")
    paper_mtm.write_nav(S, d1, _nav(101.0))
    check(stored("2026-09-14") == 101.0, "a fresh restatement row unseals that row")
    check(refused(lambda: paper_mtm.write_nav(S, d2, _nav(999.0))),
          "...and ONLY that row (09-15 still sealed)")

    # The restatement log is append-only.
    check(refused(lambda: sql("UPDATE paper_nav_restatement SET reason='x'")),
          "paper_nav_restatement UPDATE is refused")
    check(refused(lambda: sql("DELETE FROM paper_nav_restatement")),
          "paper_nav_restatement DELETE is refused")

    dbmod.close_thread_connection()
    n = len(passed) + len(failures)
    print(f"\n{'PASS' if not failures else 'FAIL'}: {len(passed)}/{n} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
