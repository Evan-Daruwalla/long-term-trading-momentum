"""Chain Phase 2 backtests: momentum-with-fractional held-out,
multi-factor in-sample, multi-factor held-out. Sequential because each
WIPES the positions table."""
from __future__ import annotations

import subprocess, sys
from pathlib import Path

ROOT = Path(r"D:\ClaudeCode\Trading")
PY = sys.executable

runs = [
    ("momentum", "2024-01-01", "2026-05-01", "mom_frac_holdout"),
    ("multi",    "2015-01-01", "2023-12-31", "multi_in_sample"),
    ("multi",    "2024-01-01", "2026-05-01", "multi_holdout"),
]

for factor, since, until, label in runs:
    print(f"\n{'='*70}\n=== RUN: factor={factor}  {since} -> {until}  label={label}\n{'='*70}", flush=True)
    rc = subprocess.call(
        [PY, "-m", "scripts.run_momentum",
         "--factor", factor, "--since", since, "--until", until,
         "--label", label],
        cwd=str(ROOT),
    )
    print(f"--- exit {rc}", flush=True)
    if rc != 0:
        print(f"!!! aborting chain at {label}", flush=True)
        sys.exit(rc)

print("\nALL DONE", flush=True)
