@echo off
REM Daily paper-trade maintenance - run after market close each trading day.
REM Order: refresh prices first, then mark-to-market all 3 sleeves.
REM
REM If price refresh fails, MTM will use stale prices (and warn in logs).
REM
REM Sleeves marked daily:
REM   mom_v1_paper        (top-100, momentum-only)
REM   mom_v2_paper        (top-50,  momentum-only)
REM   mom_roa_6535_paper  (top-50,  mom 65% + ROA 35%)
REM   sector_top4_paper   (top-4 of 11 SPDR sector ETFs)
REM   mom_roa_top1_paper  (top-1 mom_roa, LLM-experiment CONTROL)
REM   llm_overlay_mom_roa_top1_paper   (top-1 mom_roa + LLM veto/stop, TREATMENT)
REM   llm_overlay_sector_top4_paper    (sector_top4 + macro LLM veto, TREATMENT)

cd /d D:\ClaudeCode\Trading

echo === Daily price refresh ===
.venv\Scripts\python.exe -m scripts.momentum.daily_price_refresh
if errorlevel 1 (
    echo WARNING: Price refresh failed. MTM may use stale prices.
)

echo.
echo === Coverage gate: require full price publication before MTM ===
.venv\Scripts\python.exe -m scripts.momentum.check_coverage
if errorlevel 1 (
    echo COVERAGE FAIL - incomplete price publication. Skipping all MTM and overlay ops today.
    echo Investigate before trusting today's NAVs. See check_coverage output above.
    exit /b 1
)

echo.
echo === Daily MTM: spy_benchmark_paper (S^&P 500 control, buy-and-hold SPY) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy spy_benchmark_paper

echo.
echo === Daily MTM: spy_benchmark_0701_paper (S^&P 500 control, 07-01 cohort) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy spy_benchmark_0701_paper

echo.
echo === Daily MTM: mom_v1_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_v1_paper

echo.
echo === Daily MTM: mom_v2_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_v2_paper

echo.
echo === Daily MTM: mom_roa_6535_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_roa_6535_paper

echo.
echo === Daily MTM: residual_roa_6535_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_roa_6535_paper

echo.
echo === Daily MTM: 7/1 cohort duplicates (mom_v1/v2/roa/residual, fresh 07-01) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_v1_0701_paper
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_v2_0701_paper
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_roa_6535_0701_paper
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy residual_roa_6535_0701_paper

echo.
echo === Daily MTM: sector_top4_paper ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy sector_top4_paper

echo.
echo === Daily MTM: sector_top4_full_paper (full 05-01 history; systematic control) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy sector_top4_full_paper

echo.
echo === LLM-overlay: enforce invalidation stop ===
.venv\Scripts\python.exe -m scripts.momentum.llm_overlay_ops check-invalidation

echo.
echo === Daily MTM: mom_roa_top1_paper (LLM control) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy mom_roa_top1_paper

echo.
echo === Daily MTM: llm_overlay_mom_roa_top1_paper (LLM treatment) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy llm_overlay_mom_roa_top1_paper

echo.
echo === Sector-overlay: enforce per-sector invalidation stops ===
.venv\Scripts\python.exe -m scripts.momentum.sector_overlay_ops check-invalidation

echo.
echo === Daily MTM: llm_overlay_sector_top4_paper (sector treatment) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy llm_overlay_sector_top4_paper

echo.
echo === Daily MTM: LLM-cascade sleeves (always-invested 3rd pair, no stops) ===
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy llm_cascade_top1_paper
.venv\Scripts\python.exe -m scripts.momentum.paper_mtm --strategy llm_cascade_sector4_paper

echo.
echo === Refresh Graphify code knowledge-graph (structural, non-fatal) ===
REM Scope is controlled by .graphifyignore (trading_bot/ + scripts/, minus docs/tests/research).
"C:\Users\evan.EVANFREDY\.local\bin\graphify.exe" update
if errorlevel 1 (
    echo WARNING: Graphify update failed. Code graph may be stale.
)

echo.
echo Done.
