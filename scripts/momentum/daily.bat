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
set REFRESH_RC=%errorlevel%
set REFRESH_NOTE=
REM Audit 2026-08-12, finding 2: the script correctly returns 1 on failure, but a
REM bare `echo WARNING` is an artifact nothing downstream reads -- so a stale-price
REM day still exited 0 and stamped verify=PASS. Carry it to the ops stamp instead.
REM goto, not a parenthesized block: this file expands %VARS% at parse time (see
REM the header note), so a block would read the pre-block value.
if "%REFRESH_RC%"=="0" goto refresh_ok
echo WARNING: Price refresh failed. Marks may use stale prices.
set REFRESH_NOTE=--note "price refresh failed rc=%REFRESH_RC% - marks may use stale prices"
:refresh_ok

echo.
echo === Coverage check for TODAY (ops stamp only; does NOT gate stops) ===
.venv\Scripts\python.exe -m scripts.momentum.check_coverage
set COV_RC=%errorlevel%
if not "%COV_RC%"=="0" goto today_pending

set OPS_COV=PASS
goto enforce_stops

:today_pending
set OPS_COV=PENDING
echo TODAY PENDING - incomplete same-day publication.
echo Today will be marked by catch-up on the next run once it settles.

:enforce_stops
echo.
echo === Enforce overlay invalidation stops (as-of last settled trading day) ===
REM Audit 2026-08-12, finding 3: these two had NO errorlevel check at all, so a
REM crash here left stops unfired -- positions that should have exited to cash stay
REM open and NAV is wrong -- while the run exited 0 and the task reported green.
REM Explicit capture rather than `if errorlevel 1`, which is GREATER-OR-EQUAL and
REM therefore blind to a negative crash code (see the CATCHUP_RC note below).
.venv\Scripts\python.exe -m scripts.momentum.llm_overlay_ops check-invalidation --settled
set STOPS_RC=%errorlevel%
if not "%STOPS_RC%"=="0" goto stops_error
.venv\Scripts\python.exe -m scripts.momentum.sector_overlay_ops check-invalidation --settled
set STOPS_RC=%errorlevel%
if not "%STOPS_RC%"=="0" goto stops_error

echo.
echo === Catch-up MTM: mark every settled missing trading day (incl today), all sleeves ===
.venv\Scripts\python.exe -m scripts.momentum.mtm_catchup
set CATCHUP_RC=%errorlevel%
REM Audit 2026-08-04, finding 10 / E5: `if errorlevel 2` is GREATER-OR-EQUAL, so
REM ANY code >=2 took the SUCCESS branch -- argparse's 2, and cmd's 9009 for a
REM missing interpreter. Only 2 means "today is still pending".
if "%CATCHUP_RC%"=="2" goto catchup_ok
if not "%CATCHUP_RC%"=="0" goto catchup_error

:catchup_ok
echo.
echo === Anomaly scan: KLAC-class single-day moves + missing held marks (non-blocking) ===
.venv\Scripts\python.exe -m scripts.momentum.check_anomalies
REM Report-only by design: a giant move can be legitimate news, so never halt.

REM Audit 2026-08-16, finding T-4: check_cache_gaps was documented "re-run
REM monthly (M2.4)" but nothing scheduled it -- var/cache_gap_report.log sat at
REM its 2026-07-09 one-off run for 38 days, an UNENFORCEABLE contract. Gated on
REM day-of-month via Python (not cmd.exe's locale-dependent %DATE% parsing --
REM see ops_stamp.py's docstring for why this project avoids that) rather than
REM a separate scheduled task, so it can't drift the way monthy-llm-rebalance's
REM cron did. Report-only, same non-blocking contract as the anomaly scan above.
.venv\Scripts\python.exe -c "import sys,datetime; sys.exit(0 if datetime.date.today().day==1 else 1)"
REM goto, not a parenthesized block (file header rule): the 2026-08-16 block form
REM had "(...)" inside the echo text, which closed the block early and made the
REM check run EVERY day (record DG). Escaping the parens works too, but is
REM fragile; goto is what the rest of this file uses.
set GATE_RC=%errorlevel%
if not "%GATE_RC%"=="0" goto cache_gap_skip
echo.
echo === Monthly cache-gap audit - non-blocking, day 1 of month ===
.venv\Scripts\python.exe -m scripts.momentum.check_cache_gaps
:cache_gap_skip

echo.
echo === Refresh Graphify code knowledge-graph (structural, non-fatal) ===
REM Scope is controlled by .graphifyignore (trading_bot/ + scripts/, minus docs/tests/research).
"%USERPROFILE%\.local\bin\graphify.exe" update
set GRAPHIFY_RC=%errorlevel%
if not "%GRAPHIFY_RC%"=="0" echo WARNING: Graphify update failed. Code graph may be stale.

echo.
echo === Post-run verification (daily) ===
.venv\Scripts\python.exe -m scripts.momentum.verify_run --mode daily
set VERIFY_RC=%errorlevel%
if not "%VERIFY_RC%"=="0" goto verify_fail
.venv\Scripts\python.exe -m scripts.momentum.ops_stamp --coverage %OPS_COV% --verify PASS %REFRESH_NOTE%
echo.
echo Done.
exit /b 0

:stops_error
echo ERROR: overlay stop enforcement failed (rc=%STOPS_RC%). Stops may NOT have fired.
.venv\Scripts\python.exe -m scripts.momentum.ops_stamp --coverage %OPS_COV% --verify n/a --note "stop enforcement error rc=%STOPS_RC%"
exit /b 1

:catchup_error
echo ERROR: mtm_catchup failed. See output above.
.venv\Scripts\python.exe -m scripts.momentum.ops_stamp --coverage %OPS_COV% --verify n/a --note "mtm_catchup error"
exit /b 1

:verify_fail
.venv\Scripts\python.exe -m scripts.momentum.ops_stamp --coverage %OPS_COV% --verify FAIL %REFRESH_NOTE%
echo VERIFY FAIL - daily run left a settled-history gap. See var\verify_report.log.
exit /b 1
