"""Stamp rebalance_log.md with the date AND outcome of this rebalance run.

Called as the last step of rebalance.bat so the repo-root rebalance_log.md
always shows when the last rebalance happened. Rebalances run on the first
trading day of each calendar month, so date.today() at run time IS the
rebalance date.

**--status is load-bearing** (audit 2026-08-04, finding 1). This file is the
ONLY artifact proving a monthly rebalance happened: `verify_run`'s cadence
check reads it, and the `monthy-llm-rebalance` task's Step 0 gate STOPs for the
rest of the month once the date is in the current month. Stamping
unconditionally therefore made a totally failed rebalance look identical to a
healthy one AND locked out its own retry. rebalance.bat now passes
`--status PARTIAL` when any step returned non-zero, and check_rebalance_cadence
FAILs on anything but OK.

Standalone: python -m scripts.momentum.stamp_rebalance_log [--status OK|PARTIAL]
"""
from __future__ import annotations

import argparse
from datetime import date

from trading_bot.config import PROJECT_ROOT

# PROJECT_ROOT, not Path("rebalance_log.md") (audit finding 19): the reader
# (verify_run) already anchors to PROJECT_ROOT, and a cwd-relative writer only
# agreed with it because rebalance.bat happens to `cd /d` first.
OUT = PROJECT_ROOT / "rebalance_log.md"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", choices=["OK", "PARTIAL"], default="OK",
                    help="PARTIAL if any step of the rebalance failed.")
    args = ap.parse_args()

    today = date.today().isoformat()
    OUT.write_text(
        "# Rebalance Log\n\n"
        f"**Last rebalance:** {today}\n\n"
        f"**Status:** {args.status}\n\n"
        "_Auto-stamped by `scripts/momentum/rebalance.bat` (last step) on each "
        "run.\nMonthly rebalances run on the first trading day of each calendar "
        "month.\nStatus PARTIAL means at least one step returned non-zero - "
        "verify_run's\ncadence check FAILs until a clean run re-stamps it OK._\n",
        encoding="utf-8",
    )
    print(f"stamp_rebalance_log: last rebalance -> {today} ({args.status})", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        # Exit 1, not 0 (audit finding 1): this is the run's proof-of-execution.
        # If it cannot be written, the run must not report success - and the
        # stale stamp will independently FAIL the next cadence check.
        print(f"stamp_rebalance_log: ERROR {e}", flush=True)
        raise SystemExit(1)
