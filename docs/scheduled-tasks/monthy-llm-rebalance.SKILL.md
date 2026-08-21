---
name: monthy-llm-rebalance
description: Run the monthy LLM rebalance
---

IF rebalance_log.md SHOWS THAT THE MONTHY REBALANCE HAS RUN ALREADY THIS MONTH STOP READING AND END THE RESPONSE.

This is the Trading project's monthly paper-trading rebalance (D:\ClaudeCode\Trading). It fires
daily at 5:30pm local (after the 5:15pm `TradingDailyMTM` close pipeline lands real closes) but
should only do real work on the FIRST trading day of each calendar month — every other day is a
no-op via the gate below. There are 4 systematic factor sleeves, 3 LLM-experiment pairs (a stock
overlay, a sector overlay, and a cascade variant of each sharing the same decision logs), a 7/1
clean-start cohort, an SPY benchmark, and 3 of the sleeves mirror into real Alpaca PAPER accounts.
This routine's job is specifically the LLM-experiment decisions + triggering the full rebalance.

**Full rubric detail lives in `docs/overlay_decision_runbook.md` — read it if anything below is
ambiguous.** This prompt summarizes it so the routine is self-contained, but the runbook is the
source of truth if they ever diverge.

## Step 0 — Gate (only proceed if stale)

Check `rebalance_log.md` for "Last rebalance: YYYY-MM-DD". If that date is already in the CURRENT
calendar month, STOP — nothing to do, this is a no-op day. Only continue if it's from a prior
month (i.e. this is the first trigger of a new month).

## Step 1 — Gather (read-only, no trades)

Run: `cmd /c D:\ClaudeCode\Trading\scripts\momentum\overlay_prep.bat`

This prints three sections: STOCK OVERLAY, SECTOR OVERLAY, and LLM-CASCADE (a deeper-ranking view
for the always-invested 3rd pair — it shares the SAME decision log as the two cash overlays above
it, so cascade decisions use the identical `decide` CLIs, just on names/sectors further down the
ranking). Each section tells you exactly what is OWED vs. already decided vs. unchanged (no new
decision needed).

## Step 2 — Data-integrity guardrail (STOP conditions, checked BEFORE researching anything)

- **Empty universe / "No candidate at this date"**: this means `price_cache` doesn't have a
  same-day close yet (e.g. this task fired before the close pipeline ran, or `daily_price_refresh`
  failed). Do NOT force it. Do NOT log a decision or run `rebalance.bat` off stale/partial data
  mislabeled as today. STOP, report the situation to Evan (what you found, why, what's needed to
  retry — e.g. a resend on this task or a manual re-trigger this evening), and leave
  `rebalance_log.md` untouched. This exact failure happened 2026-07-01 (see record Appendix AP /
  memory `monthly_rebalance_trigger_timing_bug.md`) — "report, don't act" was the correct call.
- **Implausible momentum**: if a candidate's trailing 3-month return looks impossible (hundreds/
  thousands of percent), suspect a split/spike artifact in `price_cache` before trusting the rank
  — sanity-check the recent close ladder (the BKGM/KLAC failure mode; see memory
  `corporate_action_splits.md`). If confirmed corrupted, stop and report rather than trading on it.

If gather looks clean (real technicals, sane momentum, or explicitly "0 owed" with names carried
from last month), proceed.

## Step 3 — Decisions (live web research, one rubric per instrument type)

For every OWED item printed in Step 1 (across all three sections — stock, sector, AND cascade),
do live-web research and log a decision. Shared convention:

- **Score = 1-10 conviction the name/sector beats CASH over the next ~1 month** (forward setup,
  not trailing run). 8-10 strong conviction; 6-7 lean-hold; 4-5 marginal; 1-3 veto.
- **Invalidation** = exact close level where the thesis breaks → auto-exit to cash (enforced daily
  by `daily.bat`). Convention: just below the 50-DMA or nearest real support.
- **No lookahead** — decide only on information available as of the rebalance date.
- **Log the rationale in one line** — cite datapoints (yields, RSI, 50-DMA, the specific catalyst),
  not vibes. This is the audit trail.
- **Honest prior**: both overlays are EXPECTED to fail their kill switches (12mo / ≥30 picks,
  dropped if scores don't predict forward returns or treatment doesn't beat control). Don't tune
  the rubric to flatter the experiment — a genuine all-HOLD month is a valid data point.

**Stock overlay/cascade** (`llm_overlay_mom_roa_top1` / `llm_cascade_top1` vs `mom_roa_top1`
control): 3 prompts grounded in live web + the printed technicals — (1) equity-analyst deep dive
→ score, (2) vs 3-4 closest peers, (3) devil's-advocate long + exact invalidation. BUY when the
forward setup is sound (durable growth/quality, valuation not extreme, no imminent thesis-breaker).
VETO on a momentum blow-off rolling over, priced-for-perfection valuation, or concrete near-term
catalyst risk. Log via:
`.venv\Scripts\python.exe -m scripts.momentum.llm_overlay_ops decide --ticker T --score N --verdict BUY|VETO --invalidation P --rationale "..."`

**Sector overlay/cascade** (`llm_overlay_sector_top4` / `llm_cascade_sector4` vs `sector_top4`
control): this is a macro RISK-veto, not alpha-seeking. 4 prompts per candidate sector grounded in
live web + technicals — (1) macro/rate regime (10Y/2Y, Fed odds, USD, oil), (2) valuation/crowding
(fwd P/E vs history, breadth, RSI), (3) fundamental trend (earnings revisions, the one catalyst
that matters), (4) bear case + invalidation level. VETO when momentum is fading (below 50-DMA, weak
RSI) AND the macro read is a headwind. HOLD the broad, trending, macro-supported sectors. A veto
sends that slot to cash (not redeployed). Log via:
`.venv\Scripts\python.exe -m scripts.momentum.sector_overlay_ops decide --ticker X --score N --verdict HOLD|VETO --invalidation P --rationale "..."`

**Cascade specifics**: the stock cascade walks the top-10 mom_roa names until it finds a BUY (else
falls back to raw #1 = same as control); the sector cascade walks all 11 sectors until it has 4
HOLDs (else momentum-fills the remainder). `overlay_prep`'s cascade section shows exactly how many
more OWED evaluations are needed at which rank — keep evaluating down the list with the SAME
`decide` commands above until satisfied.

All `decide` calls and the rebalance must use the SAME date (today, the rebalance day).

## Step 4 — Execute

Run: `cmd /c D:\ClaudeCode\Trading\scripts\momentum\rebalance.bat`

This refreshes prices, rebalances all 4 systematic sleeves + the 7/1 cohort duplicates, MTMs
everything, rebalances both LLM-overlay treatments + the cascade pair (refuses if any required
decision is missing — re-run Step 3 if so), mirrors 3 sleeves (residual_roa_6535_0701,
mom_roa_6535_0701, spy_benchmark_0701) into their real Alpaca PAPER accounts via
`alpaca_sync --execute` (skips cleanly if keys are missing), and stamps `rebalance_log.md` with
today's date as the last step (idempotent — safe to re-run same-day).

## Step 5 — Report to Evan

Summarize: what was owed vs. carried, each new decision + one-line rationale, confirmation the
rebalance completed cleanly (or what failed and why), and Alpaca sync status. Start the response
with "Evan,".