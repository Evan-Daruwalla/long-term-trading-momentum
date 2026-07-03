# Daily trade-check research — 2026-06-10

Scheduled autonomous run. Reviews the live paper sleeves vs. real-world events of
the past week (≈06-03 → 06-09) and extracts strategy insight. No write actions
taken against the DB or sleeves — report only.

## TL;DR

The week's dominant real-world event was an **optical-networking sector
de-rating** triggered by **Ciena's (CIEN) 06-04 earnings**: a clean beat with
only a *modest* guidance raise → aggressive profit-taking that spread across the
whole crowded AI-optical cohort (CIEN, Fabrinet/FN, Lumentum, Coherent, Corning,
Marvell). Meanwhile the **memory/HBM complex (MU, +72% MTM) and semi-equipment
(AMAT/LRCX/KLAC)** kept ripping. The "AI trade" bifurcated: interconnect down,
compute/memory up.

Two live, well-identified takeaways:

1. **Residual momentum did its job.** At the *same* 06-03 rebalance where the
   raw-momentum sleeves bought CIEN and FN, `residual_roa_6535` declined both
   (and had sold Corning/GLW at +27%). That cohort then fell −19% to −29% in a
   week. Residual is now the top live sleeve (+6.11%) — concrete support for the
   2026-06-09 deployment decision. See `[[sleeves_verdict]]` attempt-24.
2. **The LLM-overlay invalidation stop fired correctly on FN** — first real
   exit-side data point for the overlay experiment `[[llm_overlay_experiment]]`.
   Net P&L tie vs control for now; the *quality* of the call was good. Details below.

## What happened to the names we hold

| Name | Sleeves holding (entry) | 1-wk move | Driver |
|------|------------------------|-----------|--------|
| CIEN | mom_v1, mom_v2, mom_roa_6535 (06-03) | **−29%** | 06-04 earnings: beat, raised FY26 rev to $6.3B (only modestly above $6.18B consensus) → profit-taking on a crowded, high-multiple name |
| FN   | mom_roa_6535, mom_v2, + both single-name sleeves (06-03) | **−19%** | No own news (last reported 05-04). Pure sector contagion from CIEN; broke below overlay's $600 invalidation 06-09 ($586 close) |
| MU   | all 4 systematic momentum sleeves (05-01) | **+72% MTM** | HBM sold out through 2026, ~60% of demand met; oligopoly pricing power; Goldman calls deepest memory shortage on record into 2028; near $1,040 |
| AMAT/LRCX/KLAC | residual_roa, mom_roa_6535 (05-01) | +27% to +28% | Semi-equipment riding the same memory/AI-capex supercycle |

Broad tape: S&P hit records 05-31, then a steep 06-05 Friday decline (same day
the optical cohort cracked), small 06-08 bounce. **CPI inflation print is this
week's main macro event** — event risk into mid-June.

## Insight 1 — Residual momentum avoided the crowded-beta blowup (validated)

At the 06-03 rebalance:
- `mom_roa_6535` and `mom_v2` **bought** CIEN + FN (high *raw* momentum = high
  common AI-optical beta).
- `residual_roa_6535` **declined** both and **sold** Corning/GLW at +27%.
- residual's open book entered only 05-01 (27) and 06-03 (23) — **none on 06-09**,
  so this is not hindsight from a post-crash rebalance.

The optical names ranked high on raw momentum but *not* on idiosyncratic/residual
momentum (their move was shared sector beta, not stock-specific). Neutralizing
market+sector exposure screened out exactly the cohort that then moved together
and crashed together on one earnings print. This is precisely the failure mode
residual momentum is designed to dodge, and it showed up live. Residual is now
+6.11% vs mom_roa_6535 +2.65% / mom_v2 −3.71%.

**No action needed** — this reinforces the existing deployment. Worth continuing
to watch whether residual's edge persists past this single episode (n=1 event).

## Insight 2 — The LLM overlay's invalidation stop fired on FN (experiment data)

- Both single-name sleeves bought FN @ $725 on 06-03.
- The overlay logged **BUY score 6, invalidation $600**, and its rationale
  *explicitly flagged the risk that played out*: "Rich (62x ttm / 44x fwd / 6x
  sales, above median PT) … ~46% rev from Nvidia+Cisco + CPO structural risk."
- FN broke $600 on 06-09 ($586) → overlay **sold at −19.3% (invalidation)**.
  Control still holds FN, will exit next rebalance.
- Current scoreboard: overlay −19.23% vs control −18.62% — a near tie. The
  overlay locked the loss; if FN rebounds the control wins this round, if FN
  keeps falling the overlay wins.

Honest read: the *entry* was not vetoed (the LLM saw the valuation/crowding risk
but still said BUY), so the overlay did **not** save the position — the stop just
capped the tail. The qualitative signal (LLM correctly enumerated the exact bear
case) is mildly encouraging, but this is one data point and the net-P&L edge is
zero so far. Keep logging toward the 30-pick / 12-mo kill switch.

## Candidate strategy ideas (testable, not yet built)

1. **Earnings-proximity haircut for momentum entries.** CIEN/FN were initiated
   06-03, one day before CIEN's 06-04 print, into a crowded high-multiple cohort.
   Test: at rebalance, down-weight or skip a name if it (or its sector bellwether)
   reports earnings within N trading days. Hypothesis: avoids "buy momentum right
   into the catalyst that ends it." Backtestable with an earnings-date calendar;
   need to source one. Risk: momentum's edge partly *comes from* post-earnings
   drift, so this could cut returns — measure both tails.

2. **Crowding / common-beta cap.** The optical cohort all crashed together because
   the momentum book was implicitly long one factor (AI-optical interconnect).
   residual_roa already addresses this structurally; an alternative for the
   *raw* sleeves is a per-sector or per-correlation-cluster position cap. Cheaper
   to test than a new sleeve: re-run mom_v2 history with a sector-exposure cap and
   compare DD.

3. **Bifurcation as a pair, not a basket.** Memory/HBM (long) vs optical
   interconnect (short/avoid) was a clean live spread this week. Long-only by
   constraint (under-18 sim, see `[[age_constraint]]`), so this stays research-only,
   but it argues for sub-sector tilts inside the AI complex rather than treating
   "AI semis" as one bucket.

## Loose ends for the operator

- `llm_overlay_sector_top4_paper` is still **unseeded** (100% cash, 0 decisions).
  This week's CPI print is exactly the macro-veto scenario it was built to test —
  it's missing the live event. Seeding is a write action and was not part of this
  task; flagging for manual decision. See `[[llm_overlay_experiment]]`.
- Data hygiene: FN/CIEN price path in `price_cache` looks clean (no Friday-spike
  artifacts), consistent with the post-audit filters holding.

## Sources

- [Ciena Q2 FY26 8-K](https://www.sec.gov/Archives/edgar/data/0000936395/000162828026040614/ex9912026q2earningspressre.htm)
- [Why is Ciena stock tumbling today — Investing.com](https://www.investing.com/news/stock-market-news/why-is-ciena-stock-tumbling-today-93CH-4726920)
- [Ciena falls 6% after earnings beat — CoinCentral](https://coincentral.com/ciena-cien-stock-falls-6-after-earnings-beat-heres-why/)
- [Fabrinet Q3 FY26 8-K](https://www.sec.gov/Archives/edgar/data/0001408710/000140871026000014/fn-2026504xex991q326.htm)
- [Micron HBM sold out — TechTimes](https://www.techtimes.com/articles/318017/20260608/micron-stock-climbs-hbm-sells-out-june-24-earnings-decides-ai-memory-trade.htm)
- [Micron MU +304% YTD — FXLeaders](https://www.fxleaders.com/news/2026/06/01/micron-mu-stock-soars-304-in-2026-ai-memory-chip-demand-fuels-rally/)
- [Stock market 06-08-2026 — CNBC](https://www.cnbc.com/2026/06/08/stock-market-today-live-updates.html)
