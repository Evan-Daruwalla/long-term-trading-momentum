@echo off
REM Cleanly restart the Streamlit dashboard.
REM
REM Why this exists: `schtasks /end /tn TradingDashboard` (or Stop-ScheduledTask)
REM stops the task but does NOT reliably kill the python child that `cmd`
REM spawned, so a stale process keeps serving OLD code on port 8501. This
REM script kills by command-line match, confirms the port is free, then
REM relaunches via the scheduled task (detached from this console).
REM
REM Usage:  scripts\restart_dashboard.bat

cd /d D:\ClaudeCode\Trading

echo === Stopping scheduled task (if running) ===
schtasks /end /tn TradingDashboard >nul 2>&1

echo === Killing any python serving streamlit / web.py ===
powershell -NoProfile -Command ^
  "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -like '*streamlit*' -or $_.CommandLine -like '*web.py*' } | ForEach-Object { Write-Host ('  killing PID ' + $_.ProcessId); Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }; Start-Sleep -Seconds 2"

echo === Freeing port 8501 if still bound ===
powershell -NoProfile -Command ^
  "$c = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue; if ($c) { Write-Host ('  port held by PID ' + $c.OwningProcess + ' - killing'); Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue; Start-Sleep -Seconds 1 } else { Write-Host '  port 8501 free' }"

echo === Relaunching dashboard (detached via scheduled task) ===
schtasks /run /tn TradingDashboard

echo.
echo Dashboard restarting. Give it ~5s, then open http://localhost:8501/
echo Logs: var\dashboard.log
