"""Regression test: the LLM decision logs are append-only (record DA finding 4 / DG).

Until 2026-08-18 `llm_overlay.record_decision` / `sector_overlay.record_decision`
used INSERT OR REPLACE against a UNIQUE(decision_date, ticker) key. In SQLite,
REPLACE on a UNIQUE hit DELETES the old row and inserts a new one with a fresh
AUTOINCREMENT id - so re-logging a same-day decision silently destroyed the
original. Three real decisions were lost that way (llm_overlay_log ids 4, 5, 9;
sqlite_sequence=16 with 13 rows).

Two layers now enforce append-only, and this test proves BOTH, on a throwaway
fixture DB (never the live one):
  1. POSITIVE CONTROL - the exact old statement (INSERT OR REPLACE) against a
     schema WITHOUT the triggers destroys the row and burns an id. Proves the
     test can see the failure it guards against (record CQ.4 standard).
  2. The Python writers now raise sqlite3.IntegrityError on a same-(date,ticker)
     re-log, and the original row + id survive untouched.
  3. The SCHEMA triggers block UPDATE and DELETE from ANY writer (raw SQL).
  4. A legitimately NEW (date, ticker) still inserts - the fix is not a lockout.

Run:
    python -m scripts.momentum.test_decision_log_append_only
"""
from __future__ import annotations

import shutil
import sqlite3
import sys
import tempfile
from datetime import date
from pathlib import Path

from trading_bot import db as dbmod
from trading_bot.strategies import llm_overlay, sector_overlay


def _fixture() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="decision_log_"))
    dbmod.close_thread_connection()
    dbmod.DB_PATH = tmp / "trades.db"
    dbmod.VAR_DIR = tmp
    dbmod.init_db()                       # applies SCHEMA incl. the new triggers
    llm_overlay.DB_PATH = dbmod.DB_PATH   # both modules bind DB_PATH at import
    sector_overlay.DB_PATH = dbmod.DB_PATH
    return tmp


def _rows(table: str) -> list[tuple]:
    with dbmod.connect() as c:
        return [tuple(r) for r in c.execute(
            f"SELECT id, decision_date, ticker, verdict FROM {table} ORDER BY id")]


def _seq(table: str) -> int:
    with dbmod.connect() as c:
        r = c.execute("SELECT seq FROM sqlite_sequence WHERE name=?", (table,)).fetchone()
        return r[0] if r else 0


def main() -> int:
    tmp = _fixture()
    fails: list[str] = []

    def check(cond: bool, msg: str) -> None:
        print(("  [OK  ] " if cond else "  [FAIL] ") + msg)
        if not cond:
            fails.append(msg)

    try:
        d = date(2026, 8, 3)

        # ---- 1. POSITIVE CONTROL: the old statement, on a trigger-less table ----
        # Build a sibling table with the SAME shape but no triggers, run the exact
        # pre-fix SQL twice, and show the id burns and the first row is gone.
        with dbmod.connect() as c:
            c.execute("CREATE TABLE ctrl_log (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                      "decision_date TEXT NOT NULL, ticker TEXT NOT NULL, verdict TEXT NOT NULL, "
                      "UNIQUE (decision_date, ticker))")
            c.execute("INSERT OR REPLACE INTO ctrl_log (decision_date, ticker, verdict) "
                      "VALUES ('2026-08-03', 'WDC', 'BUY')")
            c.execute("INSERT OR REPLACE INTO ctrl_log (decision_date, ticker, verdict) "
                      "VALUES ('2026-08-03', 'WDC', 'VETO')")
            ctrl = [tuple(r) for r in c.execute("SELECT id, verdict FROM ctrl_log ORDER BY id")]
            ctrl_seq = c.execute("SELECT seq FROM sqlite_sequence WHERE name='ctrl_log'").fetchone()[0]
        check(ctrl == [(2, "VETO")] and ctrl_seq == 2,
              f"positive control: INSERT OR REPLACE destroyed id=1 and burned the id "
              f"(rows={ctrl}, seq={ctrl_seq}) - the old bug is reproducible")

        # ---- 2. Python writers refuse a same-(date,ticker) re-log ----
        llm_overlay.record_decision(decision_date=d, ticker="WDC", score=6.0,
                                    verdict="BUY", invalidation_level=100.0,
                                    rationale="first")
        before = _rows("llm_overlay_log")
        raised = False
        try:
            llm_overlay.record_decision(decision_date=d, ticker="WDC", score=2.0,
                                        verdict="VETO", invalidation_level=None,
                                        rationale="re-log attempt")
        except sqlite3.IntegrityError:
            raised = True
        check(raised, "llm_overlay.record_decision: same-day re-log raises IntegrityError")
        check(_rows("llm_overlay_log") == before == [(1, "2026-08-03", "WDC", "BUY")],
              f"llm_overlay_log: original row and id=1 survive ({_rows('llm_overlay_log')})")
        check(_seq("llm_overlay_log") == 1,
              f"llm_overlay_log: no id burned (seq={_seq('llm_overlay_log')})")

        sector_overlay.record_decision(decision_date=d, ticker="XLK", score=7.0,
                                       verdict="HOLD", invalidation_level=None,
                                       rationale="first")
        raised = False
        try:
            sector_overlay.record_decision(decision_date=d, ticker="XLK", score=1.0,
                                           verdict="VETO", invalidation_level=None,
                                           rationale="re-log attempt")
        except sqlite3.IntegrityError:
            raised = True
        check(raised, "sector_overlay.record_decision: same-day re-log raises IntegrityError")
        check(_rows("sector_overlay_log") == [(1, "2026-08-03", "XLK", "HOLD")],
              f"sector_overlay_log: original row survives ({_rows('sector_overlay_log')})")

        # ---- 3. Triggers block UPDATE / DELETE from raw SQL, on both tables ----
        for table in ("llm_overlay_log", "sector_overlay_log"):
            for stmt in (f"UPDATE {table} SET verdict='VETO' WHERE id=1",
                         f"DELETE FROM {table} WHERE id=1",
                         # REPLACE is INSERT + implicit DELETE, so the delete trigger
                         # must stop even a future writer that reintroduces it.
                         f"INSERT OR REPLACE INTO {table} (decision_date, ticker, verdict, "
                         f"created_at) VALUES ('2026-08-03', "
                         f"'{'WDC' if table == 'llm_overlay_log' else 'XLK'}', 'VETO', 'x')"):
                blocked = False
                try:
                    with dbmod.connect() as c:
                        c.execute(stmt)
                except sqlite3.IntegrityError as e:
                    blocked = "append-only" in str(e)
                check(blocked, f"trigger blocks raw `{stmt.split(' WHERE')[0][:48]}...`")
            check(_rows(table)[0][3] in ("BUY", "HOLD"),
                  f"{table}: row 1 verdict unchanged after blocked writes")

        # ---- 4. A genuinely new (date, ticker) still inserts ----
        llm_overlay.record_decision(decision_date=date(2026, 9, 1), ticker="WDC", score=5.0,
                                    verdict="BUY", invalidation_level=90.0, rationale="next month")
        llm_overlay.record_decision(decision_date=d, ticker="BE", score=4.0,
                                    verdict="VETO", invalidation_level=None, rationale="other name")
        check(len(_rows("llm_overlay_log")) == 3 and _seq("llm_overlay_log") == 3,
              f"new (date,ticker) pairs insert normally ({_rows('llm_overlay_log')})")

    finally:
        dbmod.close_thread_connection()
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = 0
    print()
    if fails:
        print(f"RESULT: FAIL ({len(fails)} check(s) failed)")
        return 1
    print("RESULT: PASS (decision logs are append-only at both the writer and the DB layer)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
