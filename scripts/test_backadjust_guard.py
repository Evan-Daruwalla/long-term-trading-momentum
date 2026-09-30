"""Regression test for the backadjust_split idempotency guard (record EE, item 9).

The guard exists to stop a SECOND repair run from dividing an already-adjusted
cache by N again. It used to accept any cliff in [N/2, 2N]. For N=2 that band is
[1.0, 4.0], so an already-adjusted series whose last pre-split -> first post-split
move is a flat 1.0x PASSED the guard and would have been halved a second time.
The band is now +/-25% around N (abs(cliff / N - 1) <= 0.25).

Builds a tiny fixture DB in a temp dir and drives the script as a subprocess via
`--db`. DRY RUN ONLY: no run here ever applies a repair, the live DB is never
opened, and each case also proves the fixture's price_cache is byte-identical
afterwards.

Cases:
  1. N=2, cliff 1.0x   (already adjusted)     -> refused, rc 1   [FAILS on the old band]
  2. N=2, cliff 2.0x   (genuinely un-adjusted) -> guard passes, dry run rc 0
  3. N=10, cliff 9.79x (the real KLAC tell)    -> guard passes, dry run rc 0

Run:
    python -m scripts.test_backadjust_guard
"""
from __future__ import annotations

import hashlib
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EFF = "2026-06-10"


def _make_db(path: Path, pre_px: float, post_px: float) -> None:
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE price_cache (ticker TEXT, kind TEXT, key_date TEXT, "
                 "price REAL, PRIMARY KEY (ticker, kind, key_date))")
    conn.execute("CREATE TABLE paper_positions (id INTEGER PRIMARY KEY, "
                 "strategy_name TEXT, ticker TEXT, status TEXT, qty REAL, "
                 "entry_price REAL, entry_value REAL, entry_date TEXT, "
                 "exit_price REAL, exit_value REAL, exit_date TEXT, "
                 "realized_pnl REAL, realized_pnl_pct REAL)")
    conn.execute("CREATE TABLE paper_portfolio (strategy_name TEXT, cash REAL)")
    rows = [("FIX", "close", f"2026-06-0{d}", pre_px) for d in range(1, 10)]
    rows.append(("FIX", "close", EFF, post_px))
    conn.executemany("INSERT INTO price_cache VALUES (?,?,?,?)", rows)
    conn.commit()
    conn.close()


def _digest(path: Path) -> str:
    conn = sqlite3.connect(path)
    rows = conn.execute("SELECT * FROM price_cache ORDER BY ticker, kind, key_date").fetchall()
    conn.close()
    return hashlib.sha256(repr(rows).encode()).hexdigest()


def _run_dry(db: Path, ratio: float) -> int:
    argv = [sys.executable, "-m", "scripts.backadjust_split", "--ticker", "FIX",
            "--ratio", str(ratio), "--effective", EFF, "--db", str(db)]
    # Belt and braces: this test must never ask the script to apply anything.
    assert not any(a.startswith("--ex") for a in argv), "test must stay dry-run"
    assert str(db).startswith(tempfile.gettempdir()), "test must use the temp fixture DB"
    return subprocess.run(argv, cwd=REPO, capture_output=True, text=True).returncode


def _case(name: str, ratio: float, pre_px: float, post_px: float, want_rc: int) -> bool:
    tmp = Path(tempfile.mkdtemp(prefix="bas_guard_"))
    db = tmp / "fixture.db"
    _make_db(db, pre_px, post_px)
    before = _digest(db)
    rc = _run_dry(db, ratio)
    unchanged = _digest(db) == before
    shutil.rmtree(tmp, ignore_errors=True)
    ok = rc == want_rc and unchanged
    print(f"{'PASS' if ok else 'FAIL'}  {name}: rc={rc} (want {want_rc}), "
          f"price_cache unchanged={unchanged}")
    return ok


def main() -> int:
    results = [
        _case("N=2 cliff 1.0x (already adjusted) is refused", 2.0, 50.0, 50.0, 1),
        _case("N=2 cliff 2.0x (un-adjusted) passes the guard", 2.0, 100.0, 50.0, 0),
        _case("N=10 cliff 9.79x (KLAC tell) passes the guard", 10.0, 979.0, 100.0, 0),
    ]
    failed = results.count(False)
    print(f"\nbackadjust guard test: {results.count(True)} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
