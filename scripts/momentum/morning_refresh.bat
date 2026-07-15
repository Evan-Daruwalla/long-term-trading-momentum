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
REM DELIBERATELY NOT daily.bat: daily.bat's overlay invalidation-stop enforcement
REM (llm_overlay_ops / sector_overlay_ops check-invalidation -> paper_trader.sell)
REM is coverage-gated. It SKIPS on PENDING evenings (latest cached date = today,
REM incomplete) but WOULD FIRE in a morning run (latest = yesterday, settled),
REM which would activate stops that are currently dormant and change the live
REM LLM-overlay experiment. So this task does refresh + catch-up + verify ONLY;
REM stop-enforcement stays on the evening cadence. (Separate "stops rarely fire"
REM note is in record BY for a deliberate decision later.)

cd /d D:\ClaudeCode\Trading

echo === Morning price refresh (heal prior-day coverage lag) ===
.venv\Scripts\python.exe -m scripts.momentum.daily_price_refresh
if errorlevel 1 echo WARNING: refresh failed; catch-up may use stale prices.

echo.
echo === Catch-up MTM: mark every now-settled missing trading day, all sleeves ===
.venv\Scripts\python.exe -m scripts.momentum.mtm_catchup

echo.
echo === Post-run verification (daily) ===
REM verify_run is the LAST command so its exit code is this task's result
REM (PASS -> 0, FAIL -> nonzero shows in the task history). mtm_catchup's exit 2
REM (today still PENDING in the morning) is normal and does not fail the task.
.venv\Scripts\python.exe -m scripts.momentum.verify_run --mode daily
