@echo off
REM ===================================================================
REM  START EVERYTHING — one command to bring the trading rig fully live
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

echo.
echo ============================================================
echo  ALL UP. Dashboard: http://localhost:8501/
echo  (4 systematic sleeves + llm_overlay; mom_roa_top1 control runs hidden)
echo ============================================================
