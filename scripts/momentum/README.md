# scripts/momentum/

Production paper-trade scripts at the top level. Research artifacts in
`research/`, cache warmers in `warm/`.

## Production (run these regularly)

| Script | Purpose | Run when |
|---|---|---|
| `daily.bat` | refresh prices + MTM all 3 paper sleeves | every trading day after close |
| `rebalance.bat` | refresh prices + rebalance all 3 sleeves + MTM | 1st trading day of each month |
| `daily_price_refresh.py` | bulk yfinance pull (last 30 days × universe) | called by .bat above |
| `paper_rebalance.py` | one-strategy rebalance (top-N momentum or mom+ROA) | called by rebalance.bat |
| `paper_mtm.py` | mark-to-market one strategy → paper_nav table | called by daily.bat / rebalance.bat |
| `archive_v1_v2.py` | regenerate dashboard backtest archive JSONs | after audit or strategy change |
| `run_momentum.py` | run a momentum backtest end-to-end | ad-hoc |

## Subdirs

- **`research/`** — 29 experiment scripts (test_*.py, mono_factor_sweep, etc.).
  All failed-or-irrelevant. Kept for record. Run via
  `python -m scripts.momentum.research.test_xxx`.
- **`warm/`** — 5 cache-warming utilities (warm_xbrl.py, warm_volumes.py, etc.).
  Run once per data-source addition. Most data already warmed.

## Strategy mapping

`paper_rebalance.py` dispatches to factor modules based on `--strategy`:
- `mom_v1_paper`, `mom_v2_paper` → `momentum.rank_universe` (top-100/50)
- `mom_roa_6535_paper` → `mom_roa_zscore.make_rank_fn(0.65, 0.35)`

To add a new sleeve: add a branch in `_strategy_rank_fn()`, init the
portfolio with `paper_rebalance --strategy NAME --as-of 2026-05-01`,
add MTM/rebal lines to the two .bat files.
