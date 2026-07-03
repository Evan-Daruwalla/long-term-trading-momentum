"""Backdate the 4 systematic sleeves to 2026-05-01 on backfilled clean data.

After the re-inception (record AA) put the contaminated sleeves at a fresh
2026-06-12 start, this reconstructs their CLEAN track record from 2026-05-01 —
their true original inception — so they align with the untouched sleeves
(sector_top4, spy_benchmark) on the dashboard.

Method (one process, preload once, no per-call subprocess overhead):
  for each systematic sleeve:
    wipe paper state + re-init $100k
    replay the real monthly cadence on clean data:
      rebalance as-of 2026-05-01, then 2026-06-03  (the dates the originals ran)
      mark-to-market every trading day 2026-05-01 .. 2026-06-12
This populates paper_positions (final = 06-03 holdings) + paper_nav (30 rows).

NOT backdated: the LLM pair (mom_roa_top1 + llm_overlay_mom_roa_top1) — its
treatment decisions can't be honestly backdated without lookahead, and backdating
only the mechanical control would break the control-vs-treatment pairing. They
stay at their clean 2026-06-12 re-inception. sector_top4 / spy_benchmark /
llm_overlay_sector_top4 are untouched (already clean from their real inceptions).

Usage: python -m scripts.data_audit.backdate_sleeves --confirm
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date

from trading_bot.db import connect
from trading_bot.execution import market_data, paper_trader
from scripts.momentum import paper_rebalance, paper_mtm

# Quiet the verbose per-trade logging from the reused modules.
logging.basicConfig(level=logging.WARNING)
logging.getLogger("paper_rebalance").setLevel(logging.WARNING)
logging.getLogger("paper_mtm").setLevel(logging.ERROR)

STARTING_CASH = 100_000.0
REBALANCE_DATES = {"2026-05-01", "2026-06-03"}   # the dates the originals ran
# (strategy_name, top_n)
SLEEVES = [
    ("mom_v1_paper", 100),
    ("mom_v2_paper", 50),
    ("mom_roa_6535_paper", 50),
    ("residual_roa_6535_paper", 50),
]


def _trading_calendar(since: date, until: date) -> list[date]:
    """Real trading days in [since, until] from cached SPY closes."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT key_date FROM price_cache WHERE ticker='SPY' AND kind='close' "
            "AND price>0 AND key_date>=? AND key_date<=? ORDER BY key_date",
            (since.isoformat(), until.isoformat())).fetchall()
    return [date.fromisoformat(r[0]) for r in rows]


def _wipe_and_init(strategy_name: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM paper_positions WHERE strategy_name=?", (strategy_name,))
        conn.execute("DELETE FROM paper_nav WHERE strategy_name=?", (strategy_name,))
        conn.execute("DELETE FROM paper_portfolio WHERE strategy_name=?", (strategy_name,))
    paper_trader.init(strategy_name=strategy_name, starting_cash=STARTING_CASH)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    args = ap.parse_args()

    market_data.preload_caches()  # ONCE for the whole run
    calendar = _trading_calendar(date(2026, 5, 1), date(2026, 6, 12))
    print(f"Trading calendar: {len(calendar)} days {calendar[0]}..{calendar[-1]}")
    print(f"Rebalance on: {sorted(REBALANCE_DATES)}")
    if not args.confirm:
        print("DRY-RUN. Re-run with --confirm to wipe + backdate.")
        return 0

    for strategy_name, top_n in SLEEVES:
        print(f"\n=== {strategy_name} (top-{top_n}) ===", flush=True)
        _wipe_and_init(strategy_name)
        for d in calendar:
            if d.isoformat() in REBALANCE_DATES:
                paper_rebalance.rebalance(
                    as_of=d, strategy_name=strategy_name, starting_cash=STARTING_CASH,
                    top_n=top_n, half_spread_bps=5.0, dry_run=False)
            nav = paper_mtm.compute_nav(strategy_name, d)
            paper_mtm.write_nav(strategy_name, d, nav)
        pf = paper_trader.get(strategy_name)
        last = paper_mtm.compute_nav(strategy_name, calendar[-1])
        ret = (last["total_nav"] / STARTING_CASH - 1) * 100
        print(f"  done: {len(calendar)} nav rows, final NAV ${last['total_nav']:,.2f} "
              f"({ret:+.2f}%), {pf.n_open_positions} positions")
    print("\nBackdate complete. (LLM pair intentionally left at 2026-06-12.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
