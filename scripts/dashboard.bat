@echo off
REM Launches the Streamlit dashboard, detached from any parent process.
REM Used by the TradingDashboard scheduled task (AtLogon trigger) so the
REM dashboard survives Claude restarts and reboots.
REM
REM Logs go to var/dashboard.log (overwritten each launch).
REM
REM Manual usage:
REM   scripts\dashboard.bat            (foreground, with console output)
REM   schtasks /run /tn TradingDashboard   (detached, via task scheduler)

cd /d D:\ClaudeCode\Trading

REM Headless: no browser auto-open. runOnSave off: don't restart on file
REM edits (we want a stable long-lived process).
.venv\Scripts\python.exe -m streamlit run trading_bot\dashboard\web.py ^
    --server.headless true ^
    --server.runOnSave false ^
    --server.port 8501 ^
    > var\dashboard.log 2>&1
