"""Stamp rebalance_log.md with the date of this rebalance run.

Called as the last step of rebalance.bat so the repo-root rebalance_log.md
always shows when the last rebalance happened. Rebalances run on the first
trading day of each calendar month, so date.today() at run time IS the
rebalance date. Best-effort: never raises (can't abort the monthly batch).

Standalone: python -m scripts.momentum.stamp_rebalance_log
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

OUT = Path("rebalance_log.md")


def main() -> int:
    today = date.today().isoformat()
    OUT.write_text(
        "# Rebalance Log\n\n"
        f"**Last rebalance:** {today}\n\n"
        "_Auto-stamped by `scripts/momentum/rebalance.bat` (last step) on each "
        "run.\nMonthly rebalances run on the first trading day of each calendar "
        "month._\n",
        encoding="utf-8",
    )
    print(f"stamp_rebalance_log: last rebalance -> {today}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # best-effort: never abort the rebalance batch
        print(f"stamp_rebalance_log: WARN {e}", flush=True)
        raise SystemExit(0)
