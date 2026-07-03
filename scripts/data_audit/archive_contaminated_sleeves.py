"""Archive the pre-re-inception state of the phantom-contaminated sleeves.

Before wiping the 6 sleeves that were trading on gappy/phantom-momentum picks
(record Appendix AA), dump their current positions + NAV history to JSON so the
contaminated track record is preserved for the audit trail (the live numbers
are invalid, but we don't destroy data silently).

Writes var/reinception_archive_2026-06-13.json. Read-only on the DB.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from trading_bot.config import DB_PATH

CONTAMINATED = [
    "mom_v1_paper", "mom_v2_paper", "mom_roa_6535_paper",
    "residual_roa_6535_paper", "mom_roa_top1_paper",
    "llm_overlay_mom_roa_top1_paper",
]
OUT = Path("var/reinception_archive_2026-06-13.json")


def main() -> int:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    archive = {}
    for s in CONTAMINATED:
        pf = conn.execute("SELECT * FROM paper_portfolio WHERE strategy_name=?", (s,)).fetchone()
        pos = conn.execute(
            "SELECT ticker, qty, entry_price, entry_value, entry_date, status "
            "FROM paper_positions WHERE strategy_name=? AND status='open' ORDER BY ticker",
            (s,)).fetchall()
        navs = conn.execute(
            "SELECT nav_date, total_nav, cash, positions_value, n_open_positions "
            "FROM paper_nav WHERE strategy_name=? ORDER BY nav_date", (s,)).fetchall()
        archive[s] = {
            "portfolio": dict(pf) if pf else None,
            "n_open": len(pos),
            "open_positions": [dict(p) for p in pos],
            "nav_first": dict(navs[0]) if navs else None,
            "nav_last": dict(navs[-1]) if navs else None,
            "nav_rows": len(navs),
            "full_nav_history": [dict(n) for n in navs],
        }
        last = archive[s]["nav_last"]
        print(f"  {s:34} pos={len(pos):3} navs={len(navs):3} "
              f"lastNAV={last['total_nav']:.2f}" if last else f"  {s}: no NAV")
    conn.close()
    OUT.write_text(json.dumps(archive, indent=2))
    print(f"\nArchived {len(CONTAMINATED)} sleeves -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
