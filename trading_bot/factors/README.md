# trading_bot/factors/

## PRODUCTION (deployed in paper trade)

| Module | Used by | Purpose |
|---|---|---|
| `momentum.py` | mom_v1_paper, mom_v2_paper | 12-1 month momentum signal |
| `roa.py` | mom_roa_6535_paper | Return on Assets (Novy-Marx 2013) |
| `mom_roa_zscore.py` | mom_roa_6535_paper | Cross-sectional Z combiner |
| `universe.py` | ALL strategies | Tradeable universe filter (incl. MAX_HIST_RATIO data-quality filter) |

## RESEARCH ONLY (kept for reproducibility, NOT deployed)

| Module | Status | See |
|---|---|---|
| `accruals.py` | Failed standalone (Attempt 7) | memory/sleeves_verdict.md |
| `mom_roa_acc_zscore.py` | Failed 3-factor (Attempt 19) | memory/sleeves_verdict.md |
| `mom_roa_pead_zscore.py` | Failed 3-factor (Attempt 20) | memory/sleeves_verdict.md |
| `pead.py` | Failed standalone + overlay (Attempt 20) | memory/sleeves_verdict.md |
| `low_vol.py` | Failed sleeve (Attempts 1-3) | memory/sleeves_verdict.md |
| `quality.py` | Lookahead-biased (Attempt 4) | memory/sleeves_verdict.md |
| `quality_xbrl.py` | Failed sleeve (Attempt 5) | memory/sleeves_verdict.md |
| `quality_xbrl_v2.py` | Failed sleeve (Attempt 6) | memory/sleeves_verdict.md |
| `mom_quality_screen.py` | Failed filter (Attempt 7) | memory/sleeves_verdict.md |
| `mom_then_accruals.py` | Failed non-sleeve combo (Attempt 9) | memory/sleeves_verdict.md |
| `reversal.py` | Failed (Attempt 10) | memory/sleeves_verdict.md |
| `regime.py` / `regime_gated.py` | Failed regime gate (Attempt 11) | memory/sleeves_verdict.md |
| `composite.py` | Naive percentile composite, failed | momentum_baseline.md |

## Adding a new factor

1. Implement `score(ticker, as_of) -> float | None`
2. Implement `rank_universe(tickers, as_of) -> list[(ticker, score)]` (best-first)
3. Test standalone via `factor_backtest.run_factor_backtest(rank_fn=mymod.rank_universe)`
4. For combinations, use the Z-score pattern from `mom_roa_zscore.py` —
   avoid percentile-rank composites (lose magnitude info, killed Attempt 1)
5. If wins on BOTH windows: deploy as paper sleeve via the
   `_strategy_rank_fn()` dispatch in `scripts/momentum/paper_rebalance.py`
