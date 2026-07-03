@echo off
REM Watches "docs\Project Record - Full Chronological History.md" and
REM re-renders the matching .html the instant it changes (watchdog,
REM event-driven, not polling). Used by the TradingRecordWatch scheduled
REM task (AtLogon trigger) so it survives Claude restarts and reboots.
REM
REM Logs go to var\record_watch.log (overwritten each launch).
REM
REM Manual usage:
REM   scripts\watch_record_html.bat                 (foreground, with console output)
REM   schtasks /run /tn TradingRecordWatch           (detached, via task scheduler)

cd /d D:\ClaudeCode\Trading

.venv\Scripts\python.exe -m scripts.watch_record_html > var\record_watch.log 2>&1
