@echo off
REM ===================================================================
REM  START EVERYTHING - one command to bring the trading rig fully live
REM  after a reboot (or anytime you want it current).
REM
REM  What it does:
REM    1. Cleanly (re)launches the Streamlit dashboard (kills any stale
REM       process, frees port 8501, relaunches detached via scheduled task).
REM    2. Refreshes prices + marks-to-market ALL sleeves (daily.bat), so the
REM       dashboard shows current NAVs instead of last session's.
REM
REM  Note: both pieces ALSO auto-run on their own (TradingDashboard at logon,
REM  TradingDailyMTM at 5:15pm). This is the manual "do it now" button.
REM
REM  Usage:  scripts\start_all.bat
REM ===================================================================

cd /d D:\ClaudeCode\Trading

echo ############## 1/2  Dashboard ##############
call scripts\restart_dashboard.bat

echo.
echo ############## 2/2  Refresh prices + MTM all sleeves ##############
call scripts\momentum\daily.bat
if errorlevel 1 goto :daily_failed

echo.
echo ============================================================
echo  ALL UP. Dashboard: http://localhost:8501/
echo  (all paper sleeves refreshed + marked to market; see HANDOFF.md
echo   for the current roster)
echo ============================================================
goto :eof

:daily_failed
echo.
echo ============================================================
echo  FAILED: scripts\momentum\daily.bat exited non-zero.
echo  Prices/NAVs may be STALE. Check var\last_daily_run.log.
echo  Dashboard (if it came up): http://localhost:8501/
echo ============================================================
exit /b 1
