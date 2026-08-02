@echo off
REM Watches "docs\Project Record - Full Chronological History.md" and
REM re-renders the matching .html the instant it changes (watchdog,
REM event-driven, not polling). MANUAL helper only - it is NOT wired to any
REM scheduled task (there is no TradingRecordWatch task; it must be started
REM by hand and dies with its console).
REM
REM Logs go to var\record_watch.log (overwritten each launch).
REM
REM Manual usage:
REM   scripts\watch_record_html.bat                 (foreground, with console output)

cd /d D:\ClaudeCode\Trading

.venv\Scripts\python.exe -m scripts.watch_record_html > var\record_watch.log 2>&1
