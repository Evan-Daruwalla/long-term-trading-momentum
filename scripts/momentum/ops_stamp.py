"""Append a one-line dated ops-status stamp to var/ops_status.log (M3.4).

Evan reads `daily_report.md`, but that file is his hand-written journal (only
`render_daily_report_html.py` reads it; nothing writes it), so the automated
daily-run status goes to `var/ops_status.log` instead — one newest-last line per
run — rather than colliding with the journal. Kept as a tiny helper so daily.bat
doesn't have to build a dated string in fragile cmd.exe syntax.

Usage (from daily.bat):
  python -m scripts.momentum.ops_stamp --coverage PASS --verify PASS
  python -m scripts.momentum.ops_stamp --coverage FAIL --note "MTM skipped, closes below floor"
"""
from __future__ import annotations

import argparse
import datetime

from trading_bot.config import VAR_DIR


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage", required=True, help="PASS or FAIL")
    ap.add_argument("--verify", default="n/a", help="PASS, FAIL, or n/a")
    ap.add_argument("--note", default="", help="optional trailing note")
    args = ap.parse_args()

    stamp = (f"[OPS {datetime.date.today().isoformat()}] "
             f"coverage={args.coverage} verify={args.verify}")
    if args.note:
        stamp += f" - {args.note}"

    VAR_DIR.mkdir(parents=True, exist_ok=True)
    with open(VAR_DIR / "ops_status.log", "a", encoding="utf-8") as f:
        f.write(stamp + "\n")
    print(stamp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
