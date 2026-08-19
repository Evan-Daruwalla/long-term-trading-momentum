"""Mechanical month gate for rebalance.bat (audit 2026-08-19, edge case E4).

The `monthy-llm-rebalance` scheduled task fires DAILY (cron `0 18 * * *`); its
only month gate was prose in the task's own Step 0, read by an LLM. A mis-read
there runs rebalance.bat mid-month -- and the script's "idempotent, safe to
re-run same day" note holds only while the target set is unchanged, so mid-month
the ranks have moved and it TRADES.

Exit codes:
    0  no stamp for this calendar month -- safe to rebalance
    1  this month already stamped -- REFUSE

A PARTIAL stamp deliberately does NOT refuse: that is a failed run awaiting its
retry, and locking the retry out is exactly the bug audit 2026-08-04 finding 1
fixed by introducing --status in the first place.
"""

from __future__ import annotations

import sys
from datetime import date

from scripts.momentum.verify_run import read_last_rebalance


def month_gate(logged: str | None, status: str | None,
               today: str) -> tuple[int, str]:
    """Pure logic, so it is testable without touching the log. -> (rc, reason)."""
    if not logged:
        return 0, "no rebalance stamp on record"
    if logged[:7] != today[:7]:
        return 0, f"last stamp {logged} is not in {today[:7]}"
    if status == "PARTIAL":
        return 0, f"last stamp {logged} is PARTIAL -- retry allowed"
    # status None == a log written before --status existed; check_rebalance_cadence
    # treats that legacy shape as OK, so this does too.
    return 1, (f"last stamp {logged} (status {status or 'legacy-OK'}) is already "
               f"in {today[:7]}")


def _canary() -> int:
    """Self-check: every branch of month_gate, incl. the retry path."""
    cases = [
        # (logged, status, today, expect_rc, label)
        (None, None, "2026-08-19", 0, "no stamp at all -> allow"),
        ("2026-07-01", "OK", "2026-08-19", 0, "prior month OK -> allow"),
        ("2026-08-03", "OK", "2026-08-19", 1, "this month OK -> REFUSE"),
        ("2026-08-03", "PARTIAL", "2026-08-19", 0, "this month PARTIAL -> allow retry"),
        ("2026-08-03", None, "2026-08-19", 1, "this month legacy-OK -> REFUSE"),
        ("2026-07-31", "OK", "2026-08-01", 0, "month boundary, prior -> allow"),
        ("2026-12-01", "OK", "2026-12-31", 1, "year-end same month -> REFUSE"),
        ("2026-12-31", "OK", "2027-01-04", 0, "year rollover -> allow"),
    ]
    failed = 0
    for logged, status, today, expect, label in cases:
        rc, reason = month_gate(logged, status, today)
        ok = rc == expect
        failed += not ok
        print(f"  [{'OK ' if ok else 'FAIL'}] {label}: rc={rc} ({reason})")
    total = len(cases)
    print(f"CANARY {'PASS' if not failed else 'FAIL'} {total - failed}/{total}")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if "--canary" in argv:
        return _canary()
    logged, status = read_last_rebalance()
    today = date.today().isoformat()
    rc, reason = month_gate(logged, status, today)
    print(f"month gate: {'REFUSE' if rc else 'ALLOW'} -- {reason}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
