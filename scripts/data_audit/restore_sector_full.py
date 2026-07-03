"""Re-create the full-history sector_top4 control as a SECOND sleeve.

The 07-01 alignment reset (align_llm_07_01.py) wiped sector_top4_paper's 05-01
history so the LLM-experiment control is head-to-head with the overlays at 07-01.
But sector_top4 is ALSO the core *systematic* control, which wants the full
05-01 curve. Rather than choose, we keep both:

  sector_top4_paper       -> 07-01 reset  (LLM-experiment control, unchanged)
  sector_top4_full_paper  -> full 05-01 history, restored from the archive here
                             (systematic-comparison control; keeps rebalancing)

Source: var/align_llm_07_01_archive.json['sector_top4_paper'] (written by the
alignment reset, so this is exactly the pre-reset state). Idempotent: wipes any
existing sector_top4_full_paper rows first.

Usage:  python -m scripts.data_audit.restore_sector_full [--confirm]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from trading_bot.db import connect

ARCHIVE = Path("var/align_llm_07_01_archive.json")
SRC = "sector_top4_paper"
DST = "sector_top4_full_paper"


def _insert(conn, table: str, rows: list[dict]) -> int:
    n = 0
    for r in rows:
        r = {k: v for k, v in r.items() if k != "id"}  # let AUTOINCREMENT assign
        r["strategy_name"] = DST
        cols = ", ".join(r.keys())
        ph = ", ".join("?" for _ in r)
        conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({ph})", tuple(r.values()))
        n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    args = ap.parse_args()

    src = json.loads(ARCHIVE.read_text())[SRC]
    print(f"Archive {SRC}: {len(src['portfolio'])} pf, "
          f"{len(src['positions'])} pos, {len(src['nav'])} nav rows")
    if not args.confirm:
        print("\nDRY-RUN. Re-run with --confirm to (re)create", DST)
        return 0

    with connect() as conn:
        for t in ("paper_positions", "paper_nav", "paper_portfolio"):
            conn.execute(f"DELETE FROM {t} WHERE strategy_name=?", (DST,))
        npf = _insert(conn, "paper_portfolio", src["portfolio"])
        npos = _insert(conn, "paper_positions", src["positions"])
        nnav = _insert(conn, "paper_nav", src["nav"])
    print(f"Created {DST}: {npf} pf, {npos} pos, {nnav} nav rows "
          f"(full 05-01 history). It rebalances with the other sleeves going forward.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
