"""Chain mom-v2 + quality_xbrl_v2 sleeves: in-sample + held-out.

Tests the 8-component quality factor (with FCF/Piotroski) against the
3-component v1 to see if richer signal changes the combination story.

Usage:
  python -m scripts.momentum.run_xbrl_v2_chain
"""
from __future__ import annotations

import subprocess, sys
from pathlib import Path

ROOT = Path(r"D:\ClaudeCode\Trading")
PY = sys.executable

runs = [
    ("2015-01-01", "2023-12-31", "sleeves_mom_qxbrlv2_in_sample"),
    ("2024-01-01", "2026-05-01", "sleeves_mom_qxbrlv2_holdout"),
]
for since, until, label in runs:
    print(f"\n{'='*70}\n=== {label}  {since} -> {until}\n{'='*70}", flush=True)
    rc = subprocess.call(
        [PY, "-m", "scripts.momentum.run_sleeves",
         "--since", since, "--until", until,
         "--sleeves", "momentum,quality_xbrl_v2",
         "--label", label],
        cwd=str(ROOT),
    )
    print(f"--- exit {rc}", flush=True)
    if rc != 0:
        sys.exit(rc)
print("\nALL DONE", flush=True)
