@echo off
REM Morning heal for the price-coverage LATENCY (record BY, 2026-07-15).
REM
REM Problem: the 5:15pm TradingDailyMTM leaves "today" PENDING (same-day yfinance
REM publication is incomplete at 17:15) and NOTHING re-fetches until the next
REM 5:15pm run, so a trading day stays unmarked for ~24h (and a Friday for the
REM whole weekend). Diagnosed 2026-07-15: the data is complete at yfinance
REM overnight; only our cache is stale between the once-daily runs.
REM
REM This runs in the morning: re-pull prices (the prior day has settled at yfinance
REM by now) and mark it via catch-up, so the books are current by ~8am instead of
REM ~24h later.
REM
REM DELIBERATELY NOT daily.bat: daily.bat now enforces the overlay invalidation
REM stops EVERY evening as-of the last settled close (llm_overlay_ops /
REM sector_overlay_ops check-invalidation --settled -> paper_trader.sell; record
REM BZ, 2026-07-15). Stop-enforcement is owned by that evening run; the morning
REM task must NOT run it too, or the SAME settled close would be evaluated twice
REM in one day. So this task does refresh + catch-up + verify ONLY; stops stay on
REM the evening cadence.

cd /d D:\ClaudeCode\Trading

echo === Morning price refresh (heal prior-day coverage lag) ===
.venv\Scripts\python.exe -m scripts.momentum.daily_price_refresh
set REFRESH_RC=%errorlevel%
set REFRESH_NOTE=
REM Audit 2026-08-16, finding T-2: mirrors daily.bat's 2026-08-12 fix (finding 2)
REM -- a bare echo on failure is an artifact nothing downstream reads, and this
REM file never called ops_stamp at all, so a failed morning refresh left NO
REM record anywhere for a stale-price day. goto, not a parenthesized block: this
REM file expands %VARS% at parse time (see daily.bat's header note), so a block
REM would read the pre-block value.
if "%REFRESH_RC%"=="0" goto refresh_ok
echo WARNING: refresh failed; catch-up may use stale prices.
set REFRESH_NOTE=--note "morning refresh failed rc=%REFRESH_RC% - catch-up may use stale prices"
:refresh_ok

echo.
echo === Catch-up MTM: mark every now-settled missing trading day, all sleeves ===
.venv\Scripts\python.exe -m scripts.momentum.mtm_catchup

echo.
echo === Post-run verification (daily) ===
REM verify_run is the LAST python command so its exit code is this task's
REM result (PASS -> 0, FAIL -> nonzero shows in the task history). mtm_catchup's
REM exit 2 (today still PENDING in the morning) is normal and does not fail the
REM task. ops_stamp runs after it on BOTH paths so this run leaves a record
REM either way -- previously only the evening daily.bat run ever stamped.
.venv\Scripts\python.exe -m scripts.momentum.verify_run --mode daily
set VERIFY_RC=%errorlevel%
if "%VERIFY_RC%"=="0" goto verify_ok
.venv\Scripts\python.exe -m scripts.momentum.ops_stamp --coverage n/a --verify FAIL %REFRESH_NOTE%
exit /b %VERIFY_RC%

:verify_ok
.venv\Scripts\python.exe -m scripts.momentum.ops_stamp --coverage n/a --verify PASS %REFRESH_NOTE%
exit /b 0
