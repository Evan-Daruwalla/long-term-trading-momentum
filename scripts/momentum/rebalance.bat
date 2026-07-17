@echo off
REM Monthly rebalance - run on the FIRST trading day of each calendar month
REM after market close. Order: refresh, rebalance v1+v2+roa, MTM all.
REM
REM Runs FOUR parallel sleeves (decided 2026-05-28 / 2026-05-29):
REM   mom_v1_paper       (top-100, momentum-only, diversified)
REM   mom_v2_paper       (top-50,  momentum-only, concentrated)
REM   mom_roa_6535_paper (top-50,  momentum 65% + ROA 35% Z-score combo)
REM   sector_top4_paper  (top-4 of 11 SPDR sector ETFs, defensive)
REM See HANDOFF.md + memory/sleeves_verdict.md (Attempts 17, 21) for context.
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
REM The per-sleeve paper_mtm calls below use --force to bypass paper_mtm's own
REM coverage gate (record Appendix BQ): on a rebalance day the held names are
REM GUARANTEED present (we just filled them) and the MTM price basis == the fill
REM basis, so marking today on the partial cache is correct. Without --force those
REM calls refuse (exit 2, no write), leaving the rebalance day unmarked while
REM positions have changed -> verify_run recon would then FAIL that night.

echo.
echo === Monthly rebalance: mom_v1_paper (top-100) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy mom_v1_paper --top-n 100 --broker-realistic

echo.
echo === Monthly rebalance: mom_v2_paper (top-50) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy mom_v2_paper --top-n 50 --broker-realistic

echo.
echo === Monthly rebalance: mom_roa_6535_paper (top-50 mom+ROA Z-score) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy mom_roa_6535_paper --top-n 50 --broker-realistic

echo.
echo === Monthly rebalance: residual_roa_6535_paper (top-50 residual-mom+ROA Z) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_roa_6535_paper --top-n 50 --broker-realistic

echo.
echo === Monthly rebalance: sector_top4_paper (top-4 of 11 SPDR sectors) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy sector_top4_paper --top-n 4 --broker-realistic

echo.
echo === Monthly rebalance: sector_top4_full_paper (same picks, full 05-01 history; systematic control) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy sector_top4_full_paper --top-n 4 --broker-realistic

echo.
echo === 7/1 COHORT: fresh-on-07-01 duplicates of the May systematic sleeves ===
echo (same configs, $100k inception 07-01; clean-start cohort that mirrors to Alpaca paper)
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy mom_v1_0701_paper --top-n 100 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy mom_v2_0701_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy mom_roa_6535_0701_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_roa_6535_0701_paper --top-n 50 --broker-realistic

echo.
echo === Mark-to-market: spy_benchmark_paper (S^&P 500 control, buy-and-hold SPY, NOT rebalanced) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy spy_benchmark_paper --force

echo.
echo === Seed/MTM: spy_benchmark_0701_paper (S^&P 500 control aligned with the 7/1 cohort; reset to 07-06) ===
echo Idempotent buy-and-hold SPY at the 07-06 close; no-op stub until that close lands.
.venv\Scripts\python.exe -m scripts.momentum.seed_spy_benchmark --sleeve spy_benchmark_0701_paper --inception 2026-07-06

echo.
echo === Mark-to-market: mom_v1_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_v1_paper --force

echo.
echo === Mark-to-market: mom_v2_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_v2_paper --force

echo.
echo === Mark-to-market: mom_roa_6535_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_roa_6535_paper --force

echo.
echo === Mark-to-market: residual_roa_6535_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_roa_6535_paper --force

echo.
echo === Mark-to-market: sector_top4_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy sector_top4_paper --force

echo.
echo === Mark-to-market: sector_top4_full_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy sector_top4_full_paper --force

echo.
echo === Mark-to-market: 7/1 cohort duplicates ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_v1_0701_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_v2_0701_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_roa_6535_0701_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_roa_6535_0701_paper --force

echo.
echo === RESIDUAL WEIGHT LADDER (MONTHLY cadence): 19 same-start sleeves, only the resid/ROA blend varies ===
echo (records BW/CD: forward-test of the BU/BV weight-plateau finding; seeded by
echo  05-01 replay. Systematic, no LLM decisions, not Alpaca-mirrored. The WEEKLY
echo  and BIWEEKLY cadences rebalance via ladder_forward_rebalance.py, NOT here.)
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w0595_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w1090_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w1585_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w2080_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w2575_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w3070_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w3565_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w4060_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w4555_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w5050_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w5545_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w6040_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w6535_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w7030_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w7525_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w8020_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w8515_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w9010_paper --top-n 50 --broker-realistic
.venv\Scripts\python.exe -m scripts.momentum.paper_rebalance --strategy residual_w9505_paper --top-n 50 --broker-realistic

echo.
echo === Mark-to-market: residual weight ladder (MONTHLY cadence) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w0595_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w1090_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w1585_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w2080_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w2575_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w3070_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w3565_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w4060_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w4555_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w5050_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w5545_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w6040_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w6535_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w7030_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w7525_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w8020_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w8515_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w9010_paper --force
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_w9505_paper --force

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
echo Rebalance complete (4 systematic + 3 LLM-experiment sleeves; 3 mirrored to Alpaca paper).
