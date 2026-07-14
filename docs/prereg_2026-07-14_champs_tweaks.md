# Pre-registration — champion-sleeve tweak experiments (2026-07-14, ~00:25 CST)

**Written BEFORE any result was computed.** Evan authorized ("run 2 and 3", 2026-07-14):
re-test the two research avenues from the 07-12 options list against the two deployed
champions on the post-backfill CLEAN cache. This doc locks the grids and decision rules
in advance so the results can't be curve-fit after the fact.

**Strategies under test:** `mom_roa_6535` (65/35 mom×ROA Z, top-50 M) and
`residual_roa_6535` (65/35 residual-mom×ROA Z, top-50 M).

**Clean baselines** (2026-06-13 revalidation, `var/data_audit/revalidate_2026-06-13.json`,
record Appendix AB — the only valid comparison numbers):

| strategy | window | CAGR | maxDD | Sharpe |
|---|---|---|---|---|
| mom_roa_6535 | in_sample | +4.89% | (json) | (json) |
| mom_roa_6535 | holdout | +35.59% | (json) | (json) |
| residual_roa_6535 | in_sample | +9.47% | (json) | (json) |
| residual_roa_6535 | holdout | +32.07% | (json) | (json) |

(The scripts load exact maxDD/Sharpe baselines from the JSON; CAGRs above quoted from the
06-13 log for the record.)

**Methodology (identical to the 06-13 revalidation):** `factor_backtest.run_factor_backtest`,
5 bps half-spread, monthly rebalance, equal weight, $100k start. Windows: in_sample
2015-01-01→2023-12-31; holdout 2024-01-01→2026-05-01. Sequential runs only (one process).
Data: live `price_cache` (post-backfill; read path).

## Experiment A — preemptive risk overlays (option 2)

Configs (SAME four as the 2026-05/06 mom_v2 test, `test_mom_v2_preemptive.py`, for
apples-to-apples): `trend200` (SPY<200DMA at rebalance → all cash), `voltgt16`,
`voltgt20` (scale = min(1, target/realized SPY 21d vol)), `trend200_vt16` (both).
2 strategies × 4 configs × 2 windows = 16 runs.

**Honest prior: NEGATIVE.** Trend filter and VIX gate failed on mom_v2 (record
Appendices B/G: "triggers on noise, misses crashes"); vol-target failed in-sample at any
leverage (Appendix R). Those verdicts were pre-backfill and against mom_v2 — that is the
only reason a clean re-test on the champs is justified.

**Deployment-candidate rule (ALL must hold, per strategy/config):**
1. holdout maxDD improves by ≥ +5pp (less negative) vs that strategy's clean baseline;
2. holdout CAGR within −3pp of clean baseline;
3. in_sample CAGR within −2pp of clean baseline;
4. mean Sharpe not worse than baseline on BOTH windows.

## Experiment B — weight / top-N sweep (option 3)

Grid per strategy: signal weight ∈ {80/20, 75/25, 70/30, **65/35**, 60/40, 55/45, 50/50}
at top-50, plus top-N ∈ {25, 75, 100} at 65/35. 10 configs × 2 strategies × 2 windows
= 40 runs. (The original mom_roa weight sweep was pre-backfill — the question is whether
the 60–70% broad peak MOVED after the data repair, not to find a new point estimate.)

**Replacement rule:** the frozen 65/35 top-50 stands unless a variant beats that
strategy's clean baseline on BOTH windows with holdout CAGR margin ≥ +5pp (the measured
data-noise floor: cleaning alone moved holdout CAGRs ±0.9–2.2pp and in-sample up to
−5pp) AND in_sample CAGR ≥ baseline. Sub-threshold winners are reported as
noise-indistinguishable, not adopted.

**Honest prior:** broad peak persists; 65/35 within noise of best; no change.

## Multiple-testing note

56 backtests against a ~29-month holdout. The ≥5pp margins exist precisely because at
this many comparisons, smaller "wins" are expected by chance. Whatever the outcome,
nothing deploys from this doc alone — any deployment is a separate Evan decision as a
NEW parallel sleeve; the live sleeves and their frozen params are untouched.

**Outputs:** `var/momentum/champs_preemptive_clean.json`,
`var/momentum/champs_weight_sweep_clean.json`; results + verdicts go in the record with
this prereg cited.
