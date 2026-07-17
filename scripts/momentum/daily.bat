@echo off
REM Daily paper-trade maintenance (M3.5 catch-up flow, 2026-07-09;
REM stop-enforcement decoupled from the coverage gate 2026-07-15, Appendix BZ).
REM
REM Flow: refresh -> coverage check (sets the ops stamp only) -> enforce overlay
REM stops as-of the LAST SETTLED trading day (ALWAYS runs; --settled resolves
REM the newest coverage-passing date, so stops price off settled closes even
REM when today is pending - previously a pending today skipped them entirely
REM and they never fired) -> catch-up MTM (marks every settled missing trading
REM day, today included, for ALL sleeves) -> anomaly scan -> graphify ->
REM verify -> ops stamp.
REM
REM TODAY-PENDING is NORMAL: same-day yfinance data is usually incomplete at the
REM 17:15 run, so today is left unmarked and gets marked by the NEXT run's catch-up
REM once it settles (record Appendix BH/BI + the M3.5 amendment). The task fails
REM (nonzero exit) ONLY on a real settled-history gap (verify) or a catch-up error.
REM Branching uses goto (not parenthesized blocks) so %OPS_COV% expands correctly.

cd /d D:\ClaudeCode\Trading

echo === Daily price refresh ===
.venv\Scripts\python.exe -m scripts.momentum.daily_price_refresh
if errorlevel 1 echo WARNING: Price refresh failed. Marks may use stale prices.

echo.
echo === Coverage check for TODAY (ops stamp only; does NOT gate stops) ===
.venv\Scripts\python.exe -m scripts.momentum.check_coverage
if errorlevel 1 goto today_pending

set OPS_COV=PASS
goto enforce_stops

:today_pending
set OPS_COV=PENDING
echo TODAY PENDING - incomplete same-day publication.
echo Today will be marked by catch-up on the next run once it settles.

:enforce_stops
echo.
echo === Enforce overlay invalidation stops (as-of last settled trading day) ===
.venv\Scripts\python.exe -m scripts.momentum.llm_overlay_ops check-invalidation --settled
.venv\Scripts\python.exe -m scripts.momentum.sector_overlay_ops check-invalidation --settled

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
"%USERPROFILE%\.local\bin\graphify.exe" update
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
