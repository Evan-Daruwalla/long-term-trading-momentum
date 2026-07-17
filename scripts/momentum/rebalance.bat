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

echo === Daily price refresh ===
.venv\Scripts\python.exe -m scripts.momentum.daily_price_refresh
if errorlevel 1 (
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
if errorlevel 1 (
    echo WARNING: monthly_rebalance reported a sleeve failure. See output above; verify_run will re-check.
)

echo.
echo === Seed/MTM: spy_benchmark_0701_paper (S^&P 500 control aligned with the 7/1 cohort; reset to 07-06) ===
echo Idempotent buy-and-hold SPY at the 07-06 close; no-op stub until that close lands.
.venv\Scripts\python.exe -m scripts.momentum.seed_spy_benchmark --sleeve spy_benchmark_0701_paper --inception 2026-07-06

echo.
echo === LLM-experiment CONTROL rebalance: mom_roa_top1_paper ===
.venv\Scripts\python.exe -m scripts.momentum.llm_overlay_ops rebalance --mode control

echo.
echo === LLM-experiment TREATMENT rebalance: llm_overlay_mom_roa_top1_paper ===
echo RULE: every name the underlying control sleeve BUYS must get the 3-prompt LLM
echo eval first. The control step above prints "NEW UNDERLYING BUY" + ticker
echo when the name changed. requires a decision logged for today FIRST. If it
echo errors with "no decision logged", run candidate + decide by hand, re-run:
echo   .venv\Scripts\python.exe -m scripts.momentum.llm_overlay_ops candidate
echo   .venv\Scripts\python.exe -m scripts.momentum.llm_overlay_ops decide --ticker X --score N --verdict BUY^|VETO --invalidation P --rationale "..."
.venv\Scripts\python.exe -m scripts.momentum.llm_overlay_ops rebalance --mode overlay

echo.
echo === Mark-to-market: mom_roa_top1_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_roa_top1_paper --force

echo.
echo === Mark-to-market: llm_overlay_mom_roa_top1_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy llm_overlay_mom_roa_top1_paper --force

echo.
echo === SECTOR-overlay TREATMENT rebalance: llm_overlay_sector_top4_paper ===
echo RULE: macro LLM veto on the top-4 sectors (control = sector_top4_paper above).
echo Requires a HOLD/VETO decision for ALL 4 candidate sectors FIRST, else refuses:
echo   .venv\Scripts\python.exe -m scripts.momentum.sector_overlay_ops candidate
echo   .venv\Scripts\python.exe -m scripts.momentum.sector_overlay_ops decide --ticker XLK --score N --verdict HOLD^|VETO --invalidation P --rationale "..."
.venv\Scripts\python.exe -m scripts.momentum.sector_overlay_ops rebalance

echo.
echo === Mark-to-market: llm_overlay_sector_top4_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy llm_overlay_sector_top4_paper --force

echo.
echo === LLM-CASCADE (always-invested 3rd pair) rebalance: stock + sector ===
echo Reuses the SAME logged decisions as the cash overlays above (no double-log),
echo just cascades past VETOes to the next-best instead of going to cash:
echo   stock  = first BUY in the top-10 mom_roa names (else raw #1)
echo   sector = first 4 HOLD sectors (else momentum-fill to 4)
echo Log decisions DEEPER in the ranking (llm_overlay_ops / sector_overlay_ops
echo decide) for the cascade to differ from the control. See overlay_prep.
.venv\Scripts\python.exe -m scripts.momentum.llm_cascade_ops rebalance-stock
.venv\Scripts\python.exe -m scripts.momentum.llm_cascade_ops rebalance-sector

echo.
echo === Mark-to-market: LLM-cascade sleeves ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy llm_cascade_top1_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy llm_cascade_sector4_paper --force

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

echo.
echo === Stamp rebalance_log.md (records when this rebalance happened) ===
.venv\Scripts\python.exe -m scripts.momentum.stamp_rebalance_log

echo.
echo === Post-run verification (monthly) ===
.venv\Scripts\python.exe -m scripts.momentum.verify_run --mode monthly
if errorlevel 1 (
    echo VERIFY FAIL - monthly rebalance left an inconsistency. See var\verify_report.log.
    exit /b 1
)

echo.
echo Rebalance complete (systematic + ladder via dispatcher; 3 LLM-experiment pairs; 3 mirrored to Alpaca paper).
