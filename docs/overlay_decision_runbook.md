# LLM-Overlay Decision Runbook (Option A: Claude-in-the-loop)

**Purpose.** Make the monthly veto/approve calls for the two LLM-overlay
experiments **repeatable, consistent, and auditable** — so the decision quality
doesn't drift with whoever (or whichever session) runs it, and so the same
rubric can later drive a fully-unattended job (Option B) without rewriting it.

**What "Option A" is.** The mechanical parts of the monthly cycle are already
automated (daily MTM + both overlays' stop-enforcement via `daily.bat`; the
systematic + overlay rebalance execution via `rebalance.bat`). The ONE step that
needs a human-or-LLM with live web access is the macro/equity **decision**. Under
Option A, *you trigger it and Claude does it* — you make no judgment calls and
click through nothing. The flow is one gather command, Claude's live-web
research against this rubric, the logged decisions, then the rebalance.

> Option B (fully unattended, no human) needs a headless `claude` CLI or an
> `ANTHROPIC_API_KEY` on this machine (neither is installed as of 2026-06-12).
> When one exists, this runbook is the spec the headless agent follows; nothing
> here changes.

---

## The monthly flow (first trading day, after close)

```
1.  cmd /c D:\ClaudeCode\Trading\scripts\momentum\overlay_prep.bat
        # read-only; prints both overlays' candidates, what's OWED, + technicals

2.  Claude runs the live-web research per the rubrics below and LOGS each owed
    decision with the matching `decide` command (dated to the rebalance day):
      python -m scripts.momentum.llm_overlay_ops    decide  --ticker T --score N --verdict BUY|VETO  --invalidation P --rationale "..."
      python -m scripts.momentum.sector_overlay_ops decide  --ticker X --score N --verdict HOLD|VETO --invalidation P --rationale "..."

3.  cmd /c D:\ClaudeCode\Trading\scripts\momentum\rebalance.bat
        # rebalances all systematic sleeves + both overlays (now un-blocked) + MTMs
```

**`--as-of`.** All `decide` calls and the rebalance must use the SAME date (the
rebalance day). `decide`/`rebalance` default to today; pass `--as-of YYYY-MM-DD`
if you run them on a different calendar day than the rebalance date.

**When nothing is owed.** The stock overlay only owes a decision when the #1
mom_roa name *changes* from the currently-held name (an unchanged name carries
its prior decision; its stop is enforced daily). The sector overlay owes a
decision for each of the 4 candidate sectors every rebalance. `overlay_prep`
tells you exactly what is owed, so a "0 owed" run means go straight to step 3.

---

## Shared scoring + invalidation convention

- **Score = 1-10 conviction the name/sector beats CASH over the next ~1 month.**
  This is the falsifiable quantity the kill switch tests against forward returns,
  so score the *forward* setup, not the trailing run. Rough anchors: 8-10 strong
  conviction; 6-7 lean-hold; 4-5 marginal/coin-flip; 1-3 step aside (a veto).
- **Verdict** follows score but is a judgment, not a threshold: BUY/HOLD to stay
  in, VETO to move that slot to cash. A genuine all-HOLD month is a valid data
  point — do **not** manufacture a veto for the sake of having one.
- **Invalidation** = an exact close level at which the thesis is broken -> exit
  to cash. `daily.bat` enforces it automatically every day. Convention: just
  below the 50-DMA or the nearest real support; give a name already sitting on
  its 50-DMA a little room so it isn't stopped on day one. For a VETO there is no
  position to stop, so invalidation is optional/documentary.

## Decision discipline (applies to both overlays)

- **No lookahead.** Decide only on information available as of the rebalance
  date. Never let knowledge of subsequent moves shape a call.
- **Log the rationale in one line.** It is the audit trail; cite the datapoints
  (yields, RSI, 50-DMA, the specific catalyst), not vibes.
- **Honest prior, stated.** Both overlays are EXPECTED to fail their kill
  switches. Run them to test, not because we believe them. Do not tune the
  rubric to flatter the experiment.

---

## Stock overlay — rubric (`llm_overlay_mom_roa_top1` vs `mom_roa_top1`)

Candidate = the #1 name in the mom_roa_6535 ranking. Decision owed only when that
name changes. Run the 3 prompts `overlay_prep` prints (deep dive -> score 1-10;
peer comparison; devil's-advocate long + exact invalidation), grounded in **live
web** (latest filings/guidance, analyst revisions, valuation vs history/peers)
**plus** the printed technicals (trend vs 50/200-DMA, RSI, 1m/3m momentum,
distance from 52w high).

BUY when the forward setup is sound: durable growth/quality, valuation not
extreme for the growth, no imminent thesis-breaker, and price action not in a
confirmed breakdown. VETO when it's a momentum blow-off now rolling over,
valuation is priced-for-perfection into decelerating fundamentals, or there's a
concrete near-term catalyst risk. **Data-integrity check:** if the candidate's
trailing momentum looks impossible (e.g. 3m return in the hundreds/thousands of
%), suspect a split/spike artifact in `price_cache` before trusting the rank —
sanity-check the recent close ladder (the BKGM/KLAC failure mode).

Kill switch: 12 months / >=30 picks. Drop if scores show no positive
rank-correlation with forward returns OR the treatment doesn't beat the control.

## Sector overlay — rubric (`llm_overlay_sector_top4` vs `sector_top4`)

Candidates = the top-4 SPDR sectors by 12-1 momentum (same picks the control
makes). Decision owed for all 4 each rebalance. This is a **macro RISK-veto**,
not alpha-seeking: the defensible use is stepping aside from a sector that is
narrow, expensive, and fighting the macro/rate regime. Run the 4 macro prompts
per sector, grounded in **live web** for the backdrop + the printed technicals
per sector:

1. **Macro & rate regime** — 10Y/2Y level + direction, Fed cut/hold/hike odds,
   USD trend, oil (for energy). Tailwind / neutral / headwind for this sector's
   rate-sensitivity (long-duration vs rate-beneficiary vs cyclical)?
2. **Valuation & crowding** — forward P/E vs own history, fund flows, breadth of
   the move (broad vs 2-3 mega-caps), overbought (RSI, % > 200-DMA).
3. **Fundamental trend** — earnings-revision direction, the one catalyst/risk
   that matters this month; are fundamentals confirming or diverging from price?
4. **Bear case + invalidation** — hardest near-term bear case; an exact ETF
   close level that breaks the thesis -> cash.

VETO a sector when the price momentum is fading (below 50-DMA, weak RSI, flat/neg
recent return) AND the macro read is a headwind (e.g. a commodity sector into a
strengthening USD, or a fragile single-catalyst rally). HOLD the broad, trending,
macro-supported sectors. Veto -> that 25% slot is cash (NOT redeployed), so the
only difference from the control is the veto itself.

Kill switch: 12 months / >=30 sector-decisions. Drop if scores show no positive
rank-correlation with forward 1-month sector returns OR the treatment doesn't
beat `sector_top4_paper` net of costs.

### Worked example — the seeding decision (2026-06-12)

Macro: Fed on hold (~97% for 6/16-17), 2Y 3.94% / 10Y 4.41% (higher-for-longer),
USD strengthening (commodity headwind), oil a Strait-of-Hormuz supply-shock trade
with EIA seeing 2026 demand -1.1mb/d + later oversupply.

| Sector | Verdict | Score | Why (macro + technicals) | Inval |
|---|---|---:|---|---:|
| XLE | VETO | 3 | Fragile geopolitical-supply rally; below 50-DMA, RSI 41, flat 3m; USD headwind | - |
| XLK | HOLD | 7 | Strongest momentum, NOT overbought (RSI 54); AI capex intact; valuations rich but trend healthy | 165 |
| XLI | HOLD | 8 | Data-center/electrification + reshoring capex; broad, near highs | 170 |
| XLB | HOLD | 5 | Marginal: weakest momentum, on 50-DMA, USD headwind, but copper/AI demand intact | 49.5 |

(Full reasoning: record Appendix Z.3.)

---

## Option B activation (fully-unattended cron)

Option A keeps Claude in the loop. Option B removes the human entirely — a
scheduled job makes the LLM calls via the Anthropic API. The scaffold is built
but **UNTESTED** (no credential was available on this machine when written,
2026-06-13). To activate:

1. **Install the SDK** into the venv: `.venv\Scripts\pip.exe install anthropic`
2. **Set the key**: `setx ANTHROPIC_API_KEY "sk-ant-..."` (per-run cost, ~once a
   month). Uses model `claude-opus-4-8` with the `web_search` server tool.
3. **Smoke-test first** (does NOT trade or log): on a rebalance-eligible date,
   `python -m scripts.momentum.overlay_auto_decide --as-of YYYY-MM-DD --dry-run`
   — eyeball the printed verdicts before trusting it.
4. **Wire the schedule** (1st trading day, after close), e.g. a Windows task that
   runs `scripts\momentum\monthly_auto.bat` (= `overlay_auto_decide` →
   `rebalance.bat`).

**Safe-fail by design:** if the key is missing, the SDK import fails, or any
decision can't be produced, `overlay_auto_decide` logs NOTHING and exits 1; the
overlay rebalance then REFUSES (it requires decisions). A broken auto-decide can
only leave the overlays un-rebalanced for a human — it can never cause a bad
trade. The systematic sleeves rebalance regardless.

**Honest caveat:** an unattended LLM making real (paper) trading decisions
monthly with no review is exactly what was asked, but it trades model-variance
and a live-web dependency for hands-off operation. Review the decision log
periodically. The in-session Option A remains the lower-risk default.

## Files

| Path | Role |
|---|---|
| `scripts/momentum/overlay_prep.py` / `.bat` | one-command read-only gather (both overlays) |
| `scripts/momentum/llm_overlay_ops.py` | stock overlay: candidate / decide / rebalance / check-invalidation |
| `scripts/momentum/sector_overlay_ops.py` | sector overlay: same subcommands |
| `trading_bot/strategies/llm_overlay.py` | stock overlay design + kill switch |
| `trading_bot/strategies/sector_overlay.py` | sector overlay design + kill switch |
| `scripts/momentum/rebalance.bat` | monthly execution (refuses overlays until decided) |
| `scripts/momentum/daily.bat` | daily MTM + both overlays' stop enforcement (auto 5:15pm) |
