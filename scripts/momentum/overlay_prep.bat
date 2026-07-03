@echo off
REM One-command GATHER for the monthly LLM-overlay decisions (both sleeves).
REM Read-only: prints candidates, what's OWED, and technicals. Trades nothing.
REM Step 1 of the Option-A monthly flow -- see docs/overlay_decision_runbook.md.
REM   1. overlay_prep.bat        (this)
REM   2. Claude logs the owed decisions via *_overlay_ops decide ...
REM   3. rebalance.bat

cd /d D:\ClaudeCode\Trading
.venv\Scripts\python.exe -m scripts.momentum.overlay_prep %1
