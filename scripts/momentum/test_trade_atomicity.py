"""Regression test for buy()/sell() transactional atomicity (audit finding 5).

`paper_trader.buy()` and `sell()` are documented as doing both legs -- the
position row AND the cash move -- atomically. Until 2026-08-05 they were two
independent commits, so a failure in between committed one leg and dropped the
other. That corruption is also INVISIBLE: `verify_run`'s cash recon recomputes
from the same `paper_portfolio.cash` it corrupted, so it reports delta $0.00
forever (record CQ.7 finding 5).

Builds a tiny fixture DB (temp file), points the DB layer at it, and asserts:
  0. the OLD split-leg shape really does lose the invariant -- the demonstration
     that this test has a real trigger and isn't just asserting current behavior.
  1. buy() with a failing cash leg leaves NO position row and cash untouched.
  2. sell() with a failing cash leg leaves the position OPEN and cash untouched.
  3. both happy paths still move exactly one position and exactly the right cash.

No live DB, no price_cache needed.

Run:
    python -m scripts.momentum.test_trade_atomicity
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

from trading_bot import db as dbmod

SLEEVE = "atomicity_fixture_paper"
START_CASH = 100_000.0
AS_OF = date(2026, 8, 5)


class _CashLegFailed(RuntimeError):
    """Stands in for any mid-call failure: a lock timeout, a killed process,
    a disk error -- anything between the two legs."""


def _fixture() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="pt_atomicity_"))
    dbmod.close_thread_connection()
    dbmod.DB_PATH = tmp / "trades.db"
    dbmod.VAR_DIR = tmp
    dbmod.init_db()
    return tmp


def _state(paper_trader) -> tuple[int, int, float]:
    """(open rows, total rows, cash) for the fixture sleeve."""
    with dbmod.connect() as c:
        n_open = c.execute(
            "SELECT COUNT(*) FROM paper_positions "
            "WHERE strategy_name=? AND status='open'", (SLEEVE,)).fetchone()[0]
        n_all = c.execute(
            "SELECT COUNT(*) FROM paper_positions WHERE strategy_name=?",
            (SLEEVE,)).fetchone()[0]
    return n_open, n_all, paper_trader.get(SLEEVE).cash


def main() -> int:
    # Import AFTER the DB layer can be patched; paper_trader reads dbmod
    # globals at call time, so patching before the first call is enough.
    from trading_bot.execution import paper_trader

    tmp = _fixture()
    failures: list[str] = []

    def check(cond, msg):
        print(f"  [{'OK  ' if cond else 'FAIL'}] {msg}")
        if not cond:
            failures.append(msg)

    def with_failing_cash_leg(fn):
        """Run fn() with adjust_cash raising, and report whether it raised."""
        real = paper_trader.adjust_cash

        def boom(*a, **kw):
            raise _CashLegFailed("simulated failure between the two legs")

        paper_trader.adjust_cash = boom
        try:
            fn()
            return False
        except _CashLegFailed:
            return True
        finally:
            paper_trader.adjust_cash = real

    print("Running buy()/sell() atomicity tests...")
    paper_trader.init(strategy_name=SLEEVE, starting_cash=START_CASH)

    # 0. The trigger is real: the OLD shape (two independent commits) commits
    #    the position leg and loses the cash leg. This is what buy() used to do.
    raised = with_failing_cash_leg(lambda: (
        paper_trader.open_position(strategy_name=SLEEVE, ticker="OLD", qty=10,
                                   fill_price=100.0, as_of=AS_OF),
        paper_trader.adjust_cash(-1000.0, strategy_name=SLEEVE),
    ))
    n_open, _, cash = _state(paper_trader)
    check(raised and n_open == 1 and cash == START_CASH,
          f"OLD split-leg shape LEAKS a position with no cash debit "
          f"(open={n_open}, cash=${cash:,.2f}) -- the bug this test guards")
    # Clean the leak up so the real cases start from a known state.
    with dbmod.connect() as c:
        c.execute("DELETE FROM paper_positions WHERE ticker='OLD'")
    check(_state(paper_trader) == (0, 0, START_CASH), "fixture reset to 0 rows / full cash")

    # 1. buy(): cash leg fails -> BOTH legs rolled back.
    raised = with_failing_cash_leg(lambda: paper_trader.buy(
        strategy_name=SLEEVE, ticker="AAA", qty=10, fill_price=100.0, as_of=AS_OF))
    n_open, n_all, cash = _state(paper_trader)
    check(raised, "buy() propagates the cash-leg failure (does not swallow it)")
    check(n_all == 0,
          f"buy() rollback leaves NO position row at all (got {n_all})")
    check(cash == START_CASH,
          f"buy() rollback leaves cash at ${START_CASH:,.2f} (got ${cash:,.2f})")

    # 2. Happy-path buy still works.
    pos_id = paper_trader.buy(strategy_name=SLEEVE, ticker="BBB", qty=10,
                              fill_price=100.0, as_of=AS_OF)
    n_open, _, cash = _state(paper_trader)
    check(n_open == 1 and abs(cash - (START_CASH - 1000.0)) < 1e-9,
          f"buy() commits both legs (open={n_open}, cash=${cash:,.2f}, "
          f"expected ${START_CASH - 1000.0:,.2f})")

    # 3. sell(): cash leg fails -> position stays OPEN, cash untouched.
    cash_before = cash
    raised = with_failing_cash_leg(lambda: paper_trader.sell(
        position_id=pos_id, qty=10, fill_price=110.0, as_of=AS_OF,
        strategy_name=SLEEVE))
    n_open, _, cash = _state(paper_trader)
    check(raised, "sell() propagates the cash-leg failure")
    check(n_open == 1,
          f"sell() rollback leaves the position OPEN (got open={n_open}) -- "
          f"the worse direction: a closed position whose proceeds vanished")
    check(cash == cash_before,
          f"sell() rollback leaves cash at ${cash_before:,.2f} (got ${cash:,.2f})")

    # 4. Happy-path sell still works.
    realized = paper_trader.sell(position_id=pos_id, qty=10, fill_price=110.0,
                                 as_of=AS_OF, strategy_name=SLEEVE)
    n_open, _, cash = _state(paper_trader)
    expected_cash = cash_before + 1100.0
    check(n_open == 0 and abs(cash - expected_cash) < 1e-9,
          f"sell() commits both legs (open={n_open}, cash=${cash:,.2f}, "
          f"expected ${expected_cash:,.2f})")
    check(abs(realized - 100.0) < 1e-9,
          f"sell() returns realized P&L $100.00 (got ${realized:,.2f})")

    dbmod.close_thread_connection()
    try:
        shutil.rmtree(tmp)
    except OSError:
        pass  # temp dir; harmless if Windows holds a handle

    if failures:
        print(f"\nFAILED: {len(failures)} atomicity regression(s)")
        return 1
    print("\nAll buy()/sell() atomicity tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
