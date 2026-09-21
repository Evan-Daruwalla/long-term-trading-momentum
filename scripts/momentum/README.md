# scripts/momentum/

Production paper-trade scripts at the top level. Research artifacts in
`research/`, cache warmers in `warm/`.

## Production (run these regularly)

| Script | Purpose | Run when |
|---|---|---|
| `daily.bat` | refresh prices + MTM all 76 paper sleeves | every trading day after close |
| `rebalance.bat` | refresh prices + rebalance all due sleeves + MTM | 1st trading day of each month |
| `monthly_rebalance.py` | the dispatcher `rebalance.bat` calls; iterates `REBALANCE_SLEEVES` | called by rebalance.bat |
| `ladder_forward_rebalance.py` | weekly + biweekly residual ladders, self-deciding | 8:30pm daily via `ladder_rebalance.bat` |
| `daily_price_refresh.py` | bulk yfinance pull (last 30 days × universe) | called by .bat above |
| `paper_rebalance.py` | one-strategy rebalance (top-N momentum or mom+ROA) | called by rebalance.bat |
| `paper_mtm.py` | mark-to-market one strategy → paper_nav table | called by daily.bat / rebalance.bat |
| `archive_v1_v2.py` | regenerate dashboard backtest archive JSONs | after audit or strategy change |
| `run_momentum.py` | run a momentum backtest end-to-end | ad-hoc |

## Subdirs

- **`research/`** — 39 experiment scripts (test_*.py, mono_factor_sweep, etc.).
  All failed-or-irrelevant. Kept for record. Run via
  `python -m scripts.momentum.research.test_xxx`.
  **Caution (audit finding 27, 2026-09-20):** 16 of these hardcode a mom_v2
  baseline of in-sample `2.72` / holdout `28.81`. Both are stale. Ground truth
  from `var/data_audit/revalidate_2026-06-13.json` is **3.5407 / 26.465**.
- **`warm/`** — 8 cache-warming utilities (warm_xbrl.py, warm_volumes.py, etc.).
  Run once per data-source addition. Most data already warmed.

## Strategy mapping

`paper_rebalance.py` dispatches to factor modules based on `--strategy`:
- `mom_v1_paper`, `mom_v2_paper` → `momentum.rank_universe` (top-100/50)
- `mom_roa_6535_paper` → `mom_roa_zscore.make_rank_fn(0.65, 0.35)`

To add a new sleeve: add a branch in `_strategy_rank_fn()`, init the
portfolio, and add the sleeve to `REBALANCE_SLEEVES` in
`monthly_rebalance.py` (ladder sleeves go in `ladder_forward_rebalance.py`
instead).

> **Corrected 2026-09-20 (audit finding 15).** This file described a
> 3-sleeve system; there are **76**. It also said to "add MTM/rebal lines to
> the two .bat files" — that stopped being true on 2026-07-28, when the
> per-sleeve lines were consolidated into the `monthly_rebalance.py`
> dispatcher. Following the old instruction would have edited files that no
> longer drive the roster.
