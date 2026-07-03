"""One-time reset: wipe all 11 07-01-inception sleeves to a fresh $100k and move
their inception to 2026-07-06 (the next trading day — 7/3 is the Independence-Day
market holiday). Requested 2026-07-02 after the botched/partial 7/1 rebalance +
the Alpaca non-fractionable mirror gap; they redeploy cleanly on the 7/6 rebalance
with the new broker-realistic logic.

Archives current state first (reversible). Decision logs (llm_overlay_log /
sector_overlay_log) are NOT touched — they're date-keyed, so stale 07-01 rows
don't affect a 7/6 rebalance.

Usage:  python -m scripts.data_audit.reset_0701_to_0706 [--confirm]
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from trading_bot.db import connect
from trading_bot.execution import paper_trader

SLEEVES = [
    "mom_v1_0701_paper",
    "mom_v2_0701_paper",
    "mom_roa_6535_0701_paper",
    "residual_roa_6535_0701_paper",
    "spy_benchmark_0701_paper",
    "mom_roa_top1_paper",
    "llm_overlay_mom_roa_top1_paper",
    "llm_cascade_top1_paper",
    "sector_top4_paper",
    "llm_overlay_sector_top4_paper",
    "llm_cascade_sector4_paper",
]
STARTING_CASH = 100_000.0
INCEPTION = "2026-07-06T00:00:00+00:00"
ARCHIVE = Path("var/reset_0701_to_0706_archive.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    args = ap.parse_args()

    with connect() as conn:
        conn.row_factory = sqlite3.Row
        archive = {}
        for s in SLEEVES:
            pf = conn.execute("SELECT * FROM paper_portfolio WHERE strategy_name=?", (s,)).fetchall()
            pos = conn.execute("SELECT * FROM paper_positions WHERE strategy_name=?", (s,)).fetchall()
            nav = conn.execute("SELECT * FROM paper_nav WHERE strategy_name=?", (s,)).fetchall()
            archive[s] = {"portfolio": [dict(r) for r in pf],
                          "positions": [dict(r) for r in pos],
                          "nav": [dict(r) for r in nav]}
            n_open = sum(1 for r in pos if r["status"] == "open")
            print(f"  {s:34} {n_open:>3} open pos, {len(nav):>3} nav rows")

        if not args.confirm:
            print(f"\nDRY-RUN. {len(SLEEVES)} sleeves would archive -> {ARCHIVE}, "
                  f"wipe, and re-init at $100k inception {INCEPTION[:10]}.")
            print("Re-run with --confirm to apply.")
            return 0

        ARCHIVE.write_text(json.dumps(archive, indent=2, default=str))
        print(f"\nArchived current state -> {ARCHIVE}")
        for s in SLEEVES:
            conn.execute("DELETE FROM paper_positions WHERE strategy_name=?", (s,))
            conn.execute("DELETE FROM paper_nav WHERE strategy_name=?", (s,))
            conn.execute("DELETE FROM paper_portfolio WHERE strategy_name=?", (s,))

    for s in SLEEVES:
        paper_trader.init(strategy_name=s, starting_cash=STARTING_CASH)
    with connect() as conn:
        for s in SLEEVES:
            conn.execute("UPDATE paper_portfolio SET initialized_at=? WHERE strategy_name=?",
                         (INCEPTION, s))
    print(f"\nReset {len(SLEEVES)} sleeves to $100k, inception {INCEPTION[:10]}.")
    print("Flat ($100k cash, 0 positions) until the 7/6 rebalance. Archive is reversible.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
