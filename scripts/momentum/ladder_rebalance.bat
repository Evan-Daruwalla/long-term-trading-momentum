@echo off
REM Forward (live) rebalance for the WEEKLY + BIWEEKLY residual ladders (record CD).
REM
REM Runs every evening via the TradingLadderRebalance scheduled task, AFTER the
REM 5:15pm daily MTM and the ~6:03pm monthly rebalance, so no two rebalance
REM processes overlap -- the project's hard "never concurrent factor_backtest"
REM rule. The dispatcher self-decides from the trading calendar whether today is
REM a weekly and/or biweekly rebalance day, and rebalances only the due sleeves
REM (holiday- and every-other-week-aware). A non-rebalance evening is a fast no-op.
cd /d D:\ClaudeCode\Trading
.venv\Scripts\python.exe -m scripts.momentum.ladder_forward_rebalance
