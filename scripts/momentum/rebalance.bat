@echo off
REM Monthly rebalance - run on the FIRST trading day of each calendar month
REM after market close. Order: refresh -> monthly_rebalance dispatcher (ALL
REM systematic + ladder rebalance+MTM in ONE process) -> spy_0701 seed -> LLM
REM overlays -> alpaca sync -> stamp -> verify.
REM
REM Systematic roster (decided 2026-05-28 onward): the 6 May sleeves
REM (mom_v1/v2, mom_roa_6535, residual_roa_6535, sector_top4, sector_top4_full),
REM the 4 _0701-cohort duplicates, and the 19-point residual weight ladder
REM (MONTHLY cadence). See HANDOFF.md + memory/sleeves_verdict.md for context.
REM
REM Idempotent: re-running same day is a no-op (target set unchanged).

cd /d D:\ClaudeCode\Trading

REM Audit 2026-08-04, finding 4: this batch used to discard 14 of its 16
REM python exit codes -- including alpaca_sync --execute, which submits real
REM broker orders. RC_FAIL accumulates any non-zero step; it decides the
REM stamp's --status and this batch's own exit code.
set RC_FAIL=0

REM Audit 2026-08-19, edge case E4: `monthy-llm-rebalance` fires DAILY (cron
REM `0 18 * * *`); its ONLY month gate was prose in that task's Step 0, read by
REM an LLM. A mis-read there runs this script mid-month, when the ranks have
REM moved -- so the "idempotent, re-running same day is a no-op" note above no
REM longer holds and this TRADES. This is the mechanical gate.
REM --allow-same-month is the deliberate override (it also covers the
REM documented same-day re-run).
if /i "%~1"=="--allow-same-month" goto month_gate_ok
.venv\Scripts\python.exe -m scripts.momentum.check_month_gate
set GATE_RC=%errorlevel%
if not "%GATE_RC%"=="0" (
    echo REFUSED: this calendar month is already rebalanced ^(see rebalance_log.md^).
    echo Re-run with --allow-same-month if this is a deliberate re-run.
    exit /b %GATE_RC%
)
:month_gate_ok

echo === Daily price refresh ===
.venv\Scripts\python.exe -m scripts.momentum.daily_price_refresh
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo ERROR: Price refresh failed. ABORTING rebalance - would use stale ranks.
    exit /b 1
)

REM NO coverage gate here (unlike daily.bat) BY DESIGN. The monthly rebalance MUST
REM run on the 1st trading day even though same-day publication is incomplete at
REM this hour (~4,400 of ~5,200 closes at 17:33; it settles overnight). A hard
REM coverage gate would abort every monthly run. It is safe because 12-1 momentum
REM ranks use the close ~21 trading days back (SKIP_TRADING_DAYS, momentum.py), so
REM incomplete SAME-day data does not affect ranks; fills carry-forward for any
REM name missing a same-day close (paper_rebalance last_close_on_or_before).
REM The monthly_rebalance dispatcher's MTM phase replicates paper_mtm --force to
REM bypass paper_mtm's own coverage gate (record Appendix BQ): on a rebalance day
REM the held names are GUARANTEED present (we just filled them) and the MTM price
REM basis == the fill basis, so marking today on the partial cache is correct.
REM Without --force the coverage gate would refuse (no write), leaving the
REM rebalance day unmarked while positions changed -> verify_run recon would then
REM FAIL that night.

echo.
echo === Systematic + ladder rebalance + MTM (single-process dispatcher) ===
REM audit 2026-07-17 fix #3 (record Appendix CG): the ~29 paper_rebalance + ~30
REM paper_mtm --force lines that used to live here were one OS process each, and
REM every process re-preloaded the ~37.5M-row price_cache (~44s) -> ~25 min wasted.
REM monthly_rebalance runs the SAME sleeves, same args, same order in ONE process
REM (cache preloaded once). It covers the 6 May systematic sleeves, the 4 _0701
REM duplicates, the 19-point residual weight ladder (MONTHLY cadence) and the
REM spy_benchmark_paper mark. The LLM-overlay sleeves + the spy_benchmark_0701
REM seed stay below (they depend on their own ops/seed steps). Sleeve roster lives
REM in the module + HANDOFF.md. A failed sleeve is logged and skipped, not fatal.
.venv\Scripts\python.exe -m scripts.momentum.monthly_rebalance
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: monthly_rebalance reported a sleeve failure. See output above.
    set RC_FAIL=1
)

echo.
echo === Seed/MTM: spy_benchmark_0701_paper (S^&P 500 control aligned with the 7/1 cohort; reset to 07-06) ===
echo Idempotent buy-and-hold SPY at the 07-06 close; no-op stub until that close lands.
.venv\Scripts\python.exe -m scripts.momentum.seed_spy_benchmark --sleeve spy_benchmark_0701_paper --inception 2026-07-06
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: seed_spy_benchmark
    set RC_FAIL=1
)

echo.
echo === LLM-experiment CONTROL rebalance: mom_roa_top1_paper ===
.venv\Scripts\python.exe -m scripts.momentum.llm_overlay_ops rebalance --mode control
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: llm_overlay control
    set RC_FAIL=1
)

echo.
echo === LLM-experiment TREATMENT rebalance: llm_overlay_mom_roa_top1_paper ===
echo RULE: every name the underlying control sleeve BUYS must get the 3-prompt LLM
echo eval first. The control step above prints "NEW UNDERLYING BUY" + ticker
echo when the name changed. requires a decision logged for today FIRST. If it
echo errors with "no decision logged", run candidate + decide by hand, re-run:
echo   .venv\Scripts\python.exe -m scripts.momentum.llm_overlay_ops candidate
echo   .venv\Scripts\python.exe -m scripts.momentum.llm_overlay_ops decide --ticker X --score N --verdict BUY^|VETO --invalidation P --rationale "..."
.venv\Scripts\python.exe -m scripts.momentum.llm_overlay_ops rebalance --mode overlay
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: llm_overlay treatment
    set RC_FAIL=1
)

echo.
echo === Mark-to-market: mom_roa_top1_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_roa_top1_paper --force
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: mtm mom_roa_top1
    set RC_FAIL=1
)

echo.
echo === Mark-to-market: llm_overlay_mom_roa_top1_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy llm_overlay_mom_roa_top1_paper --force
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: mtm llm_overlay_top1
    set RC_FAIL=1
)

echo.
echo === SECTOR-overlay TREATMENT rebalance: llm_overlay_sector_top4_paper ===
echo RULE: macro LLM veto on the top-4 sectors (control = sector_top4_paper above).
echo Requires a HOLD/VETO decision for ALL 4 candidate sectors FIRST, else refuses:
echo   .venv\Scripts\python.exe -m scripts.momentum.sector_overlay_ops candidate
echo   .venv\Scripts\python.exe -m scripts.momentum.sector_overlay_ops decide --ticker XLK --score N --verdict HOLD^|VETO --invalidation P --rationale "..."
.venv\Scripts\python.exe -m scripts.momentum.sector_overlay_ops rebalance
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: sector_overlay treatment
    set RC_FAIL=1
)

echo.
echo === Mark-to-market: llm_overlay_sector_top4_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy llm_overlay_sector_top4_paper --force
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: mtm llm_overlay_sector4
    set RC_FAIL=1
)

echo.
echo === LLM-CASCADE (always-invested 3rd pair) rebalance: stock + sector ===
echo Reuses the SAME logged decisions as the cash overlays above (no double-log),
echo just cascades past VETOes to the next-best instead of going to cash:
echo   stock  = first BUY in the top-10 mom_roa names (else raw #1)
echo   sector = first 4 HOLD sectors (else momentum-fill to 4)
echo Log decisions DEEPER in the ranking (llm_overlay_ops / sector_overlay_ops
echo decide) for the cascade to differ from the control. See overlay_prep.
.venv\Scripts\python.exe -m scripts.momentum.llm_cascade_ops rebalance-stock
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: cascade stock
    set RC_FAIL=1
)
.venv\Scripts\python.exe -m scripts.momentum.llm_cascade_ops rebalance-sector
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: cascade sector
    set RC_FAIL=1
)

echo.
echo === Mark-to-market: LLM-cascade sleeves ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy llm_cascade_top1_paper --force
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: mtm cascade_top1
    set RC_FAIL=1
)
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy llm_cascade_sector4_paper --force
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: mtm cascade_sector4
    set RC_FAIL=1
)

REM NOTE: the volume cache is kept fresh by daily_price_refresh (top of this
REM script) which now persists volume alongside closes - so the old per-rebalance
REM warm_held_volumes pass was removed (redundant double-download). The manual
REM scripts.momentum.warm.warm_held_volumes still exists as a backstop.

echo.
echo === Alpaca PAPER sync: mirror residual_roa / mom_roa / SPY into their paper accounts ===
echo Submits market orders to reconcile each Alpaca paper account to its sleeve's target
echo weights (scaled to that account's equity). PAPER only; needs alpaca_keys.env filled.
echo Skips cleanly if keys are missing or a sleeve hasn't deployed yet.
.venv\Scripts\python.exe -m trading_bot.execution.alpaca_sync --all --execute
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: alpaca_sync --execute
    set RC_FAIL=1
)

echo.
echo === Stamp rebalance_log.md (records when this rebalance happened) ===
REM The stamp is the ONLY proof this run happened: verify_run's cadence check
REM reads it and the monthly task's Step 0 gate STOPs on it. Stamping OK after
REM a failed run hid the failure AND locked out the retry (audit finding 1).
if "%RC_FAIL%"=="1" (
    .venv\Scripts\python.exe -m scripts.momentum.stamp_rebalance_log --status PARTIAL
) else (
    .venv\Scripts\python.exe -m scripts.momentum.stamp_rebalance_log --status OK
)
set STEP_RC=%errorlevel%
if not "%STEP_RC%"=="0" (
    echo STEP FAIL: stamp_rebalance_log
    set RC_FAIL=1
)

echo.
echo === Post-run verification (monthly) ===
.venv\Scripts\python.exe -m scripts.momentum.verify_run --mode monthly
set VERIFY_RC=%errorlevel%
if not "%VERIFY_RC%"=="0" echo VERIFY FAIL - monthly rebalance left an inconsistency. See var\verify_report.log.

echo.
REM Exit code must reflect BOTH the step failures and verify, same pattern as
REM ladder_rebalance.bat (record CH). Before this, verify_run was effectively the
REM only gate, so a failed rebalance step that left the DB self-consistent -- a
REM sleeve that never traded is perfectly consistent -- exited 0.
if "%RC_FAIL%"=="1" (
    echo Rebalance INCOMPLETE - at least one step failed; rebalance_log.md stamped PARTIAL.
    exit /b 1
)
if not "%VERIFY_RC%"=="0" exit /b %VERIFY_RC%

echo Rebalance complete (systematic + ladder via dispatcher; 3 LLM-experiment pairs; 3 mirrored to Alpaca paper).
