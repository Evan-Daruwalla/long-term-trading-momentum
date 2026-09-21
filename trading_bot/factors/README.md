# trading_bot/factors/

## PRODUCTION (deployed in paper trade)

| Module | Used by | Purpose |
|---|---|---|
| `momentum.py` | mom_v1_paper, mom_v2_paper | 12-1 month momentum signal |
| `roa.py` | mom_roa_6535_paper | Return on Assets (Novy-Marx 2013) |
| `mom_roa_zscore.py` | mom_roa_6535_paper | Cross-sectional Z combiner |
| `universe.py` | ALL strategies | Tradeable universe filter (incl. MAX_HIST_RATIO data-quality filter) |
| `residual_momentum.py` | residual_roa_6535_paper (+ its `_0701` twin and the 54 w-sweep/ladder sleeves) | Residual / idiosyncratic momentum |
| `zcombo.py` | residual_roa_6535_paper | Generic Z-score combiner |
| `sector_momentum.py` | sector_top4_paper, sector_top4_full_paper, sector_overlay, llm_cascade | Sector-ETF momentum over the 11 SPDRs |

> **Added 2026-09-20 (audit finding 18).** These three were missing from this
> table while being imported by live strategies — verified by grepping
> `trading_bot/strategies/` and `scripts/momentum/`. The table listed 4 of the
> 25 modules in this directory as production; the real count is 7.

## RESEARCH ONLY (kept for reproducibility, NOT deployed)

> **Path correction, 2026-09-20 (audit finding 19).** The bare `memory/...`
> paths in the `See` column below **do not resolve** — `find` returns nothing
> for `sleeves_verdict.md` or `momentum_baseline.md` anywhere in this repo.
> Those files live outside git, under
> `C:\Users\evan.EVANFREDY\.claude\projects\D--ClaudeCode-Trading\memory\`.
> `HANDOFF.md` fixed this identical bug in itself on 2026-07-28; this copy was
> missed.
>
> **Also undocumented and genuinely orphaned** (zero importers in
> `trading_bot/strategies/` or `scripts/momentum/`, checked 2026-09-20):
> `ensemble.py`, `high_52w.py`, `insider_cluster.py`.

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
