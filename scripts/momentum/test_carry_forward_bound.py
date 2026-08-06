"""Regression test for the carry-forward staleness bound (audit finding 12).

`compute_nav` marks a held name with no close on `as_of` using its most recent
prior close, walking back arbitrarily far. That is the right VALUATION choice
(refusing would tear a hole in NAV continuity), but until 2026-08-05 it was
silent in every production path: `paper_mtm.main()` printed the staleness
counters and NOTHING ELSE called main() -- `mtm_catchup` (the daily path since
M3.5), `ladder_forward_rebalance`, `monthly_rebalance`, `remark_nav_day` and the
seeders all call compute_nav/write_nav directly and dropped them on the floor.
So a delisted holding marked at its last-ever close indefinitely, and
`verify_run`'s cash recon could not catch it: recon recomputes positions_value
by the same carry-forward, so it reconciles to $0.00 against a fossil price.

Builds a tiny fixture DB (temp file), points the DB layer at it, and asserts:
  1. a fresh price (1d old) produces NO stale flag.
  2. a price older than MAX_CARRY_FORWARD_DAYS IS flagged, with the ticker and
     its age named -- and the NAV still gets computed (no refusal to mark).
  3. the flag survives the call path that actually runs nightly: compute_nav
     called directly, the way mtm_catchup calls it -- not via main().
  4. a held name with NO close at all still falls back to entry_price.

No live DB, no network.

Run:
    python -m scripts.momentum.test_carry_forward_bound
"""
from __future__ import annotations

import logging
import shutil
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

from trading_bot import db as dbmod
from trading_bot.execution import market_data

AS_OF = date(2026, 8, 5)


def _fixture() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="pm_carryfwd_"))
    dbmod.close_thread_connection()
    dbmod.DB_PATH = tmp / "trades.db"
    dbmod.VAR_DIR = tmp
    dbmod.init_db()
    # price_cache is NOT in db.SCHEMA — market_data owns its DDL.
    market_data._ensure_cache_schema()

    def portfolio(name):
        with dbmod.connect() as c:
            c.execute("INSERT INTO paper_portfolio "
                      "(strategy_name, starting_cash, cash, initialized_at) "
                      "VALUES (?, 100000, 50000, '2026-07-01T00:00:00+00:00')",
                      (name,))

    def position(name, ticker):
        with dbmod.connect() as c:
            c.execute("INSERT INTO paper_positions "
                      "(strategy_name, ticker, status, qty, entry_price, "
                      " entry_value, entry_date) "
                      "VALUES (?, ?, 'open', 100, 50, 5000, '2026-07-01')",
                      (name, ticker))

    def close_px(ticker, d, price):
        with dbmod.connect() as c:
            c.execute("INSERT INTO price_cache (ticker, kind, key_date, price) "
                      "VALUES (?, 'close', ?, ?)", (ticker, d.isoformat(), price))

    # A) fresh: last close 1 day before as_of.
    portfolio("fresh_sleeve")
    position("fresh_sleeve", "FRSH")
    close_px("FRSH", AS_OF - timedelta(days=1), 60.0)

    # B) delisted: last close 30 days before as_of -- the finding's scenario.
    portfolio("delisted_sleeve")
    position("delisted_sleeve", "DEAD")
    close_px("DEAD", AS_OF - timedelta(days=30), 70.0)

    # C) never-priced: no price_cache row at all -> entry_price fallback.
    portfolio("noprice_sleeve")
    position("noprice_sleeve", "GHST")
    return tmp


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records: list[tuple[int, str]] = []

    def emit(self, record):
        self.records.append((record.levelno, record.getMessage()))

    def errors(self) -> str:
        return "\n".join(m for lv, m in self.records if lv >= logging.ERROR)


def main() -> int:
    from scripts.momentum import paper_mtm

    tmp = _fixture()
    failures: list[str] = []

    def check(cond, msg):
        print(f"  [{'OK  ' if cond else 'FAIL'}] {msg}")
        if not cond:
            failures.append(msg)

    def nav_for(sleeve):
        cap = _Capture()
        paper_mtm.log.addHandler(cap)
        try:
            # Called EXACTLY the way mtm_catchup calls it -- not through main().
            return paper_mtm.compute_nav(sleeve, AS_OF), cap
        finally:
            paper_mtm.log.removeHandler(cap)

    print("Running carry-forward staleness-bound tests...")
    print(f"  (MAX_CARRY_FORWARD_DAYS = {paper_mtm.MAX_CARRY_FORWARD_DAYS})")

    # 1. Fresh price -> no flag, NAV = cash + 100*60.
    nav, cap = nav_for("fresh_sleeve")
    check(nav["stale_tickers"] == [],
          f"fresh (1d old) is NOT flagged (got {nav['stale_tickers']})")
    check("STALE CARRY-FORWARD" not in cap.errors(),
          "fresh sleeve logs no STALE CARRY-FORWARD error")
    check(abs(nav["total_nav"] - (50_000 + 6_000)) < 1e-9,
          f"fresh NAV = $56,000.00 (got ${nav['total_nav']:,.2f})")

    # 2. 30d-old price -> flagged by ticker AND age, and STILL marked.
    nav, cap = nav_for("delisted_sleeve")
    check(nav["stale_tickers"] == [("DEAD", 30)],
          f"30d-old price IS flagged with ticker+age (got {nav['stale_tickers']})")
    errs = cap.errors()
    check("STALE CARRY-FORWARD" in errs and "DEAD 30d" in errs,
          "the error names the offending ticker and its age")
    check("recon CANNOT catch this" in errs,
          "the error says why verify_run cannot catch it")
    check(abs(nav["total_nav"] - (50_000 + 7_000)) < 1e-9,
          f"stale sleeve is STILL marked, at the fossil price "
          f"(got ${nav['total_nav']:,.2f}, expected $57,000.00) -- "
          f"report, never refuse")

    # 3. No close at all -> entry_price fallback, counted as missing.
    nav, _ = nav_for("noprice_sleeve")
    check(nav["missing_count"] == 1 and abs(nav["total_nav"] - (50_000 + 5_000)) < 1e-9,
          f"never-priced name falls back to entry_price "
          f"(missing={nav['missing_count']}, NAV=${nav['total_nav']:,.2f})")

    dbmod.close_thread_connection()
    try:
        shutil.rmtree(tmp)
    except OSError:
        pass  # temp dir; harmless if Windows holds a handle

    if failures:
        print(f"\nFAILED: {len(failures)} carry-forward regression(s)")
        return 1
    print("\nAll carry-forward staleness-bound tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
