# scripts/momentum/research/

Experiment scripts. NONE are production. Kept for forensic record and
re-running if the audit baselines change.

Output goes to `var/data_audit/*.json` and `*.out`.

## What's in here

### Stop-loss + reentry (Attempts 12, 13 — failed on clean data)
- `test_mom_v2_stops.py` — 4 stop levels × 2 windows
- `test_mom_v2_stops_reentry.py` — 3 reentry buffers × 2 windows

### Preemptive overlays (Attempts 14, 15 — failed)
- `test_mom_v2_preemptive.py` — trend filter + vol-target combinations
- `test_vol_target_clean.py` — vol-target 7-target sweep
- `test_vol_target_finetune.py` — portfolio-vol vs SPY-vol × lookbacks
- `test_vix_regime.py` — VIX term-structure regime (Attempt 18)

### Multi-factor (Attempts 5-11, 16, 17, 19, 20 — mostly failed)
- `test_quality_screen.py` — yfinance quality filter
- `test_quality_standalone.py` — XBRL quality solo
- `test_accruals_standalone.py` — Sloan accruals solo
- `test_regime_gated.py` — SPY-vs-RSP regime switcher
- `test_restricted_universes.py` — top500/top1000 by market cap
- `test_reversal_and_mta.py` — short-term reversal + mom-then-accruals
- `test_mom_roa.py` — initial coarse sweep (Attempt 17 — WINNER)
- `test_mom_roa_refine.py` — finer weight sweep around the winner
- `test_mom_roa_tc.py` — TC sensitivity on mom_roa_6535
- `test_mom_roa_acc.py` — 3-factor with accruals (Attempt 19, failed)
- `test_pead.py` — PEAD overlay (Attempt 20, failed)

### Long-short (research-only, can't deploy without margin)
- `test_long_short_momentum.py` — plain LS (busts in-sample)
- `test_long_short_voltgt.py` — LS + vol-target-spread (partial fix)

### Older infrastructure
- `mono_factor_sweep.py` — 24-config mono-factor sweep (Phase 2a)
- `robustness_test.py` — top-N × rebal-freq sweep (validated v2)
- `run_sleeves.py` / `run_sleeves_chain.py` — Phase 2b sleeves
- `run_xbrl_quality_chain.py` / `run_xbrl_v2_chain.py` — XBRL chains
- `tc_sensitivity.py` — TC sweep (general)
- `diagnose_alpha.py` — alpha decomposition helper

## Deployed strategy lives in...
`trading_bot/strategies/mom_roa_6535.py` (frozen spec) +
`scripts/momentum/paper_rebalance.py` (live execution).
