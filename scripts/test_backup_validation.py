"""Regression test for backup write-validate-rename (audit finding E6).

Rotation in `backup_trades_db` counts backups by FILENAME. Until 2026-08-05 a
half-written `VACUUM INTO` therefore counted as a good generation and evicted a
real one -- and since its name carries today's date it sorted NEWEST, so the
junk was retained while the good copies aged out. The same-day rerun path also
unlinked the existing backup BEFORE starting the new VACUUM, so a failure there
destroyed a generation and produced nothing.

Builds a tiny fixture DB (temp file), points the script's module globals at it,
and asserts:
  1. the rotation glob CANNOT see a `.part` file -- the structural reason a
     failed write is now invisible to rotation (and that it COULD see a
     `trades_*.db` one, which is the bug being guarded).
  2. validate_backup() rejects a truncated file and a right-shaped-but-wrong-
     content file, and accepts a real one.
  3. a run whose validation fails exits 1, deletes its `.part`, and leaves
     EVERY pre-existing generation on disk -- no rotation.
  4. a normal run writes a validated backup and rotates to --keep.

No live DB (the 5 GB VACUUM is not what is under test -- the rotation and
validation logic is), no network.

Run:
    python -m scripts.test_backup_validation
"""
from __future__ import annotations

import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

from scripts import backup_trades_db as bk


def _make_db(path: Path, n_nav_rows: int) -> None:
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE paper_nav (strategy_name TEXT, nav_date TEXT, "
                 "cash REAL, positions_value REAL, total_nav REAL, "
                 "n_open_positions INTEGER)")
    conn.executemany(
        "INSERT INTO paper_nav VALUES ('s', ?, 1, 2, 3, 0)",
        [(f"2026-01-{i + 1:02d}",) for i in range(n_nav_rows)])
    conn.commit()
    conn.close()


def _fixture() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="bk_validate_"))
    _make_db(tmp / "trades.db", n_nav_rows=25)
    bk.DB_PATH = tmp / "trades.db"
    bk.VAR_DIR = tmp
    bk.BACKUP_DIR = tmp / "backups"
    bk.BACKUP_DIR.mkdir()
    return tmp


def _run(argv: list[str]) -> int:
    saved = sys.argv
    sys.argv = ["backup_trades_db", *argv]
    try:
        return bk.main()
    finally:
        sys.argv = saved


def _names() -> list[str]:
    return sorted(p.name for p in bk.BACKUP_DIR.iterdir())


def main() -> int:
    tmp = _fixture()
    failures: list[str] = []

    def check(cond, msg):
        print(f"  [{'OK  ' if cond else 'FAIL'}] {msg}")
        if not cond:
            failures.append(msg)

    print("Running backup write-validate-rename tests...")

    # 1. The structural guarantee: `.part` is outside the rotation glob, a
    #    junk `trades_*.db` is INSIDE it (that is the bug this replaces).
    (bk.BACKUP_DIR / "trades_2026-01-01.db.part").write_bytes(b"junk")
    (bk.BACKUP_DIR / "trades_2026-01-01.db").write_bytes(b"junk")
    globbed = {p.name for p in bk.BACKUP_DIR.glob("trades_*.db")}
    check("trades_2026-01-01.db.part" not in globbed,
          "rotation glob CANNOT see a .part file")
    check("trades_2026-01-01.db" in globbed,
          "rotation glob CAN see a truncated trades_*.db -- the old bug")
    for p in bk.BACKUP_DIR.iterdir():
        p.unlink()

    # 2. validate_backup: truncated / wrong-content / good.
    truncated = bk.BACKUP_DIR / "truncated.db"
    truncated.write_bytes((bk.DB_PATH.read_bytes())[:2048])
    check(bk.validate_backup(truncated, 25) is not None,
          f"validate_backup REJECTS a truncated file "
          f"({bk.validate_backup(truncated, 25)})")

    wrong = bk.BACKUP_DIR / "wrong.db"
    _make_db(wrong, n_nav_rows=3)
    reason = bk.validate_backup(wrong, 25)
    check(reason is not None and "row count" in reason,
          f"validate_backup REJECTS a valid-but-wrong-content DB ({reason})")

    good = bk.BACKUP_DIR / "good.db"
    shutil.copyfile(bk.DB_PATH, good)
    check(bk.validate_backup(good, 25) is None,
          "validate_backup ACCEPTS a real copy")
    for p in bk.BACKUP_DIR.iterdir():
        p.unlink()

    # 3. A failing validation must not cost an existing generation.
    for d in ("2026-08-01", "2026-08-02", "2026-08-03"):
        shutil.copyfile(bk.DB_PATH, bk.BACKUP_DIR / f"trades_{d}.db")
    before = _names()
    real_validate = bk.validate_backup
    bk.validate_backup = lambda path, expect: "simulated torn write"
    try:
        rc = _run(["--keep", "2"])
    finally:
        bk.validate_backup = real_validate
    after = _names()
    check(rc == 1, f"failed validation exits 1 (got {rc})")
    check(after == before,
          f"NO generation lost and NO rotation on a failed write "
          f"(before={before}, after={after})")
    check(not any(n.endswith(".part") for n in after),
          f"the .part file is cleaned up (got {after})")

    # 4. Happy path: validated write + rotation down to --keep.
    rc = _run(["--keep", "2"])
    after = _names()
    check(rc == 0, f"normal run exits 0 (got {rc})")
    check(len(after) == 2 and not any(n.endswith(".part") for n in after),
          f"rotation keeps exactly 2 validated backups (got {after})")
    newest = bk.BACKUP_DIR / after[-1]
    check(bk.validate_backup(newest, 25) is None,
          f"the retained newest backup {newest.name} validates")

    try:
        shutil.rmtree(tmp)
    except OSError:
        pass  # temp dir; harmless if Windows holds a handle

    if failures:
        print(f"\nFAILED: {len(failures)} backup-validation regression(s)")
        return 1
    print("\nAll backup write-validate-rename tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
