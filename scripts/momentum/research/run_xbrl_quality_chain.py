"""Chain mom-v2 + quality_xbrl sleeves: in-sample + held-out.

Now that we have point-in-time fundamentals, we can run the IN-SAMPLE
backtest without lookahead bias. This is the test that distinguishes
"quality factor is real" from "yfinance lookahead artifact".

Compares against the existing baselines:
  - momentum_v2 solo (top-50 monthly)
  - mom + low_vol (stdev-floor) sleeves
  - mom + quality (yfinance proxy) sleeves — held-out only, biased

Usage:
  python -m scripts.momentum.run_xbrl_quality_chain
"""
from __future__ import annotations

import subprocess, sys
from pathlib import Path

ROOT = Path(r"D:\ClaudeCode\Trading")
PY = sys.executable

runs = [
    ("2015-01-01", "2023-12-31", "sleeves_mom_qxbrl_in_sample"),
    ("2024-01-01", "2026-05-01", "sleeves_mom_qxbrl_holdout"),
]
for since, until, label in runs:
    print(f"\n{'='*70}\n=== {label}  {since} -> {until}\n{'='*70}", flush=True)
    rc = subprocess.call(
        [PY, "-m", "scripts.momentum.run_sleeves",
         "--since", since, "--until", until,
         "--sleeves", "momentum,quality_xbrl",
         "--label", label],
        cwd=str(ROOT),
    )
    print(f"--- exit {rc}", flush=True)
    if rc != 0:
        sys.exit(rc)
print("\nALL DONE", flush=True)
