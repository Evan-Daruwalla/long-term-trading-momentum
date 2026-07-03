"""One-time alignment reset: re-baseline the six LLM-experiment sleeves to fresh
$100k as of 2026-07-01 so they're head-to-head from one date (user choice
2026-06-30). Archives current state first (reversible). Then runs cumulatively.

NB sector_top4_paper is ALSO a core systematic sleeve — resetting it desyncs it
from the other 4 systematic sleeves (still 05-01) in the systematic comparison.
Archived, so it can be reverted alone if that wasn't intended.

Usage:  python -m scripts.data_audit.align_llm_07_01 [--confirm]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from trading_bot.db import connect
from trading_bot.execution import paper_trader

SLEEVES = [
    "mom_roa_top1_paper",                 # stock control
    "llm_overlay_mom_roa_top1_paper",     # stock cash treatment
    "llm_cascade_top1_paper",             # stock cascade treatment
    "sector_top4_paper",                  # sector control (ALSO systematic)
    "llm_overlay_sector_top4_paper",      # sector cash treatment
    "llm_cascade_sector4_paper",          # sector cascade treatment
]
STARTING_CASH = 100_000.0
INCEPTION = "2026-07-01T00:00:00+00:00"
ARCHIVE = Path("var/align_llm_07_01_archive.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    args = ap.parse_args()

    with connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        archive = {}
        for s in SLEEVES:
            pf = conn.execute("SELECT * FROM paper_portfolio WHERE strategy_name=?", (s,)).fetchall()
            pos = conn.execute("SELECT * FROM paper_positions WHERE strategy_name=?", (s,)).fetchall()
            nav = conn.execute("SELECT * FROM paper_nav WHERE strategy_name=?", (s,)).fetchall()
            archive[s] = {"portfolio": [dict(r) for r in pf],
                          "positions": [dict(r) for r in pos],
                          "nav": [dict(r) for r in nav]}
            n_open = sum(1 for r in pos if r["status"] == "open")
            print(f"  {s:34} {n_open} open pos, {len(nav)} nav rows")

        if not args.confirm:
            print("\nDRY-RUN. Re-run with --confirm to archive + wipe + re-init at 07-01.")
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
    print(f"\nReset {len(SLEEVES)} LLM-experiment sleeves to $100k, inception {INCEPTION[:10]}.")
    print("They deploy on the 07-01 rebalance (rebalance.bat). Archive is reversible.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
