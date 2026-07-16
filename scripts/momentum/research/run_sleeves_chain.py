"""Chain the in-sample + held-out `run_sleeves` backtests in one shot.

Runs `scripts.momentum.run_sleeves` twice as subprocesses - in-sample
(2015-01-01..2023-12-31) then held-out (2024-01-01..2026-05-01), labelled
`sleeves_stdevfloor_*` - aborting on the first non-zero exit. A research
convenience wrapper, not part of live automation.
"""
from __future__ import annotations

import subprocess, sys
from pathlib import Path

ROOT = Path(r"D:\ClaudeCode\Trading")
PY = sys.executable

runs = [
    ("2015-01-01", "2023-12-31", "sleeves_stdevfloor_in_sample"),
    ("2024-01-01", "2026-05-01", "sleeves_stdevfloor_holdout"),
]
for since, until, label in runs:
    print(f"\n{'='*70}\n=== {label}  {since} -> {until}\n{'='*70}", flush=True)
    rc = subprocess.call(
        [PY, "-m", "scripts.momentum.run_sleeves",
         "--since", since, "--until", until, "--label", label],
        cwd=str(ROOT),
    )
    print(f"--- exit {rc}", flush=True)
    if rc != 0:
        sys.exit(rc)
print("\nALL DONE", flush=True)
