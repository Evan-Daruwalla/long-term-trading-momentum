"""Wipe + re-init the phantom-contaminated sleeves for a clean re-inception.

Run AFTER archive_contaminated_sleeves.py. Deletes the open positions, NAV
history, and portfolio row for each contaminated sleeve, then re-creates it
fresh at $100k (today's inception). The caller then rebalances each on the
now-backfilled clean data. Leaves the 3 clean sleeves (sector_top4,
llm_overlay_sector_top4, spy_benchmark) and the decision logs untouched.

Usage: python -m scripts.data_audit.reinception_wipe --confirm
"""
from __future__ import annotations

import argparse
import sys

from trading_bot.db import connect
from trading_bot.execution import paper_trader

CONTAMINATED = [
    "mom_v1_paper", "mom_v2_paper", "mom_roa_6535_paper",
    "residual_roa_6535_paper", "mom_roa_top1_paper",
    "llm_overlay_mom_roa_top1_paper",
]
STARTING_CASH = 100_000.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true",
                    help="actually wipe (otherwise dry-run)")
    args = ap.parse_args()

    with connect() as conn:
        for s in CONTAMINATED:
            p = conn.execute("SELECT COUNT(*) FROM paper_positions WHERE strategy_name=? AND status='open'", (s,)).fetchone()[0]
            n = conn.execute("SELECT COUNT(*) FROM paper_nav WHERE strategy_name=?", (s,)).fetchone()[0]
            print(f"  {s:34} would wipe: {p} open pos, {n} nav rows")
            if args.confirm:
                conn.execute("DELETE FROM paper_positions WHERE strategy_name=?", (s,))
                conn.execute("DELETE FROM paper_nav WHERE strategy_name=?", (s,))
                conn.execute("DELETE FROM paper_portfolio WHERE strategy_name=?", (s,))

    if not args.confirm:
        print("\nDRY-RUN. Re-run with --confirm to wipe + re-init.")
        return 0

    for s in CONTAMINATED:
        paper_trader.init(strategy_name=s, starting_cash=STARTING_CASH)
        pf = paper_trader.get(s)
        print(f"  re-init {s:34} cash=${pf.cash:,.2f} inception={pf.initialized_at[:10]}")
    print("\nWiped + re-inited 6 sleeves at $100k. Now rebalance each on clean data.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
