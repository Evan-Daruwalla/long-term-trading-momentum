@echo off
REM STATUS (audit 2026-07-17, record CG): DORMANT by design -- referenced by NO
REM scheduled task or script. This is the "Option B" fully-unattended path,
REM BLOCKED-ON-EVAN until an Anthropic API credential is provisioned. The LIVE
REM monthly path is the monthy-llm-rebalance agent task -> rebalance.bat.
REM Kept as the documented activation route; do not delete.
REM
REM FULLY-UNATTENDED monthly rebalance (Option B). UNTESTED until a credential is
REM provisioned -- see docs/overlay_decision_runbook.md "Option B activation".
REM   1. overlay_auto_decide.py : Anthropic API makes the LLM veto/approve calls.
REM   2. rebalance.bat          : rebalances all sleeves (overlays included).
REM Safe-fail: if auto-decide errors (no key, API down), it logs no decisions and
REM rebalance.bat REFUSES the overlay rebalance -- systematic sleeves still
REM rebalance; the overlays are simply left for a human. No bad trade possible.
REM Schedule on the 1st trading day of the month, after close (e.g. schtasks).

cd /d D:\ClaudeCode\Trading

echo === Auto-decide LLM overlays (Anthropic API) ===
.venv\Scripts\python.exe -m scripts.momentum.overlay_auto_decide
if errorlevel 1 (
    echo WARNING: overlay auto-decide failed. Overlays will be SKIPPED by rebalance
    echo          ^(they refuse without decisions^). Systematic sleeves still rebalance.
)

echo.
echo === Monthly rebalance ===
call scripts\momentum\rebalance.bat

echo.
echo === Post-run verification ^(monthly^) ===
.venv\Scripts\python.exe -m scripts.momentum.verify_run --mode monthly
if errorlevel 1 (
    echo VERIFY FAIL - monthly run left an inconsistency. See var\verify_report.log.
    exit /b 1
)
