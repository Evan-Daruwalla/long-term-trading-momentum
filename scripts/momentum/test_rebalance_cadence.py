"""Regression test for verify_run's (e) rebalance-cadence check (record CO).

The check exists because (a)-(d) structurally cannot see a missed monthly
rebalance — an un-rebalanced sleeve has continuous NAV and cent-perfect cash
recon, it just holds a stale book (record CN).

Asserts the two halves separately, since the file read and the date logic are
separate functions:
  1. read_last_rebalance parses the real rebalance_log.md format (and returns
     None, not a crash, on a missing or unstamped file).
  2. check_rebalance_cadence fires on a stale stamp and stays quiet on the four
     situations that are legitimately normal — including the two that a naive
     "stamp month == current month" rule would get wrong: the pre-rebalance days
     of a new month, and the evening of the rebalance itself.

No DB, no fixtures, no network.

Run:
    python -m scripts.momentum.test_rebalance_cadence
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from scripts.momentum.verify_run import check_rebalance_cadence, read_last_rebalance


def test_read() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="verify_cadence_"))

    real = tmp / "rebalance_log.md"
    real.write_text(
        "# Rebalance Log\n\n**Last rebalance:** 2026-07-01\n\n"
        "_Auto-stamped by `scripts/momentum/rebalance.bat` (last step) on each run._\n",
        encoding="utf-8")
    assert read_last_rebalance(real) == "2026-07-01", read_last_rebalance(real)

    unstamped = tmp / "empty.md"
    unstamped.write_text("# Rebalance Log\n\nnothing here yet\n", encoding="utf-8")
    assert read_last_rebalance(unstamped) is None

    assert read_last_rebalance(tmp / "does_not_exist.md") is None
    print("  [OK  ] read_last_rebalance: real format, unstamped file, missing file")


def test_cadence() -> None:
    # The live 2026-08 situation this check was written for. On 08-02 the
    # settled frontier is still Friday 07-31, so a July stamp is CORRECT and the
    # check must stay quiet — firing here would have made every pre-rebalance
    # evening of a new month a red task-history entry.
    assert check_rebalance_cadence("2026-07-01", "2026-07-31") == []

    # 08-03 fires at 6:03pm but coverage does not settle until overnight, so the
    # 8:30pm ladder run still sees settled=07-31 with an 08-03 stamp. '>=' keeps
    # this quiet; a '==' rule would false-FAIL it.
    assert check_rebalance_cadence("2026-08-03", "2026-07-31") == []

    # The real signal: 08-03 has settled and the stamp is still July.
    fails = check_rebalance_cadence("2026-07-01", "2026-08-03")
    assert len(fails) == 1, fails
    assert "has\n" not in fails[0] and "NOT run" in fails[0], fails[0]

    # Same month, rebalance done — the ordinary rest-of-month state.
    assert check_rebalance_cadence("2026-08-03", "2026-08-14") == []

    # A whole month skipped is still exactly one FAIL, not silence.
    assert len(check_rebalance_cadence("2026-07-01", "2026-09-02")) == 1

    # Unreadable log is reported, never assumed fine.
    assert len(check_rebalance_cadence(None, "2026-08-03")) == 1

    print("  [OK  ] check_rebalance_cadence: 4 quiet cases, 3 fail cases")


def main() -> int:
    print("Running verify_run rebalance-cadence tests...")
    test_read()
    test_cadence()
    print("\nAll rebalance-cadence tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
