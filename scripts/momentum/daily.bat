@echo off
REM Daily paper-trade maintenance (M3.5 catch-up flow, 2026-07-09).
REM
REM Flow: refresh -> [if TODAY settled: enforce overlay stops] -> catch-up MTM
REM (marks every settled missing trading day, today included, for ALL sleeves) ->
REM anomaly scan -> graphify -> verify -> ops stamp.
REM
REM TODAY-PENDING is NORMAL: same-day yfinance data is usually incomplete at the
REM 17:15 run, so today is left unmarked and gets marked by the NEXT run's catch-up
REM once it settles (record Appendix BH/BI + the M3.5 amendment). The task fails
REM (nonzero exit) ONLY on a real settled-history gap (verify) or a catch-up error.
REM Stop-enforcement is skipped on a pending day so no stop fires off partial prices.
REM Branching uses goto (not parenthesized blocks) so %OPS_COV% expands correctly.

cd /d D:\ClaudeCode\Trading

echo === Daily price refresh ===
.venv\Scripts\python.exe -m scripts.momentum.daily_price_refresh
if errorlevel 1 echo WARNING: Price refresh failed. Marks may use stale prices.

echo.
echo === Coverage check for TODAY (gates same-day stop-enforcement) ===
.venv\Scripts\python.exe -m scripts.momentum.check_coverage
if errorlevel 1 goto today_pending

set OPS_COV=PASS
echo.
echo === Enforce overlay invalidation stops (today settled) ===
.venv\Scripts\python.exe -m scripts.momentum.llm_overlay_ops check-invalidation
.venv\Scripts\python.exe -m scripts.momentum.sector_overlay_ops check-invalidation
goto do_catchup

:today_pending
set OPS_COV=PENDING
echo TODAY PENDING - incomplete same-day publication. Skipping stop-enforcement.
echo Today will be marked by catch-up on the next run once it settles.

:do_catchup
echo.
echo === Catch-up MTM: mark every settled missing trading day (incl today), all sleeves ===
.venv\Scripts\python.exe -m scripts.momentum.mtm_catchup
if errorlevel 2 goto catchup_ok
if errorlevel 1 goto catchup_error

:catchup_ok
echo.
echo === Anomaly scan: KLAC-class single-day moves + missing held marks (non-blocking) ===
.venv\Scripts\python.exe -m scripts.momentum.check_anomalies
REM Report-only by design: a giant move can be legitimate news, so never halt.

echo.
echo === Refresh Graphify code knowledge-graph (structural, non-fatal) ===
REM Scope is controlled by .graphifyignore (trading_bot/ + scripts/, minus docs/tests/research).
"C:\Users\evan.EVANFREDY\.local\bin\graphify.exe" update
if errorlevel 1 echo WARNING: Graphify update failed. Code graph may be stale.

echo.
echo === Post-run verification (daily) ===
.venv\Scripts\python.exe -m scripts.momentum.verify_run --mode daily
if errorlevel 1 goto verify_fail
.venv\Scripts\python.exe -m scripts.momentum.ops_stamp --coverage %OPS_COV% --verify PASS
echo.
echo Done.
exit /b 0

:catchup_error
echo ERROR: mtm_catchup failed. See output above.
.venv\Scripts\python.exe -m scripts.momentum.ops_stamp --coverage %OPS_COV% --verify n/a --note "mtm_catchup error"
exit /b 1

:verify_fail
.venv\Scripts\python.exe -m scripts.momentum.ops_stamp --coverage %OPS_COV% --verify FAIL
echo VERIFY FAIL - daily run left a settled-history gap. See var\verify_report.log.
exit /b 1
