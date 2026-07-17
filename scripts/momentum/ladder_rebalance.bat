@echo off
REM Forward (live) rebalance for the WEEKLY + BIWEEKLY residual ladders (record CD).
REM
REM Runs every evening at 8:30pm via the TradingLadderRebalance scheduled task,
REM AFTER the 5:15pm daily MTM and well clear of the ~6:03pm monthly rebalance
REM (audit 2026-07-17, record CG: the monthly run measured ~35-45 min, so the
REM old 7:00pm slot left only a thin margin against a two-writer collision --
REM the project's hard "no concurrent rebalance processes" rule). The dispatcher
REM self-decides from the trading calendar whether today is a weekly and/or
REM biweekly rebalance day, and rebalances only the due sleeves (holiday- and
REM every-other-week-aware). A non-rebalance evening is a fast no-op.
cd /d D:\ClaudeCode\Trading
.venv\Scripts\python.exe -m scripts.momentum.ladder_forward_rebalance
if errorlevel 1 echo WARNING: ladder rebalance reported an error; check the log above.

echo.
echo === Post-run verification (daily) ===
REM Audit fix (record CG): verify immediately after a ladder rebalance instead
REM of waiting for the next evening's daily.bat. Last command = task exit code.
.venv\Scripts\python.exe -m scripts.momentum.verify_run --mode daily
