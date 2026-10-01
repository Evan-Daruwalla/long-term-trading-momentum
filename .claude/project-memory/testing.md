# testing — Trading

Last updated 2026-07-15. Canonical home for the testing standard. The
frozen-test contract is also an always-load cross-bin invariant (INDEX).

## The frozen-test contract (THE testing rule)
- `.venv\Scripts\python.exe -m trading_bot.strategies.test_strategies`
  — 4 pinned strategy configs. Must stay at **d=±0.0000pp after ANY Python
  change**, even "obviously unrelated" ones. **Paste the REAL output; never say
  "should pass".** Part of the definition of done for every task.
  **pytest is NOT installed in the venv** — the `-m pytest ...` form documented
  here until 2026-07-28 could never run; the module `__main__` block
  (`test_strategies.py:160`) is the real invocation.

## Other tests + verification
- `test_inception_guard.py` — regression test for the pre-inception NAV guard (M3).
- Read-only "did it actually work" verifiers (not pytest): `verify_run.py --mode
  daily|monthly` (NAV continuity / cash recon / position counts / no-pre-inception),
  `check_coverage.py`, `check_anomalies.py`, `check_cache_gaps.py` (see data.md /
  tooling.md).
- Write-path changes are tested on a COPY of the DB first, never live-first
  (check free disk before copying the ~5 GB DB).

## Hard rule
- NEVER fabricate data/fills/prices/results — missing data is reported as missing.
  A green test claimed without real pasted output is a violation.
