# Daily Trade Research — 2026-06-08 (covering Fri 2026-06-05)

Automated `daily-trade-check` run. Today is Mon 2026-06-08; the prior trading
day was **Fri 2026-06-05**, which turned out to be a major market event.

## TL;DR

Friday 6/05 was a **sector-wide semiconductor crash** (Philadelphia
Semiconductor Index −10.3%, its worst single day since 2020; Nasdaq −4.2%).
Our momentum sleeves are structurally concentrated in AI-semis (the prior
6–12-month momentum winners), so they were maximally exposed. **Drawdown on
the day mapped monotonically to concentration**, exactly as risk theory
predicts:

| Sleeve | Fri 6/05 1-day | Concentration |
|---|---|---|
| `sector_top4_paper` | **−3.05%** | 4 sector ETFs (most diversified) |
| `mom_v1_paper` (top-100) | −5.46% | 41% Tech |
| `mom_roa_6535_paper` (top-50) | −5.53% | 52% Tech |
| `mom_v2_paper` (top-50) | −5.77% | 47% Tech |
| `mom_roa_top1` / `llm_overlay` (FN) | **−13.07%** | single name |

Nobody was *broken* — a tech-heavy momentum book losing ~5–6% on a −10% SOX day
is roughly beta-consistent. The lesson is about **structure**, not failure.

## What actually happened (real-world research)

Confirmed via web search of 6/04–6/07 coverage:

1. **Broadcom (AVGO) AI guidance miss (primary catalyst).** Q3 AI-chip
   guidance came in at ~$16B vs the ~$17.2B consensus, and management did **not
   raise** the FY2026 AI-semi forecast → classic "sell-the-news." AVGO −14% on
   6/04, which rippled through the entire chip supply chain on 6/05.
2. **Rates.** A hot May jobs report (+172k) pushed the 10-yr above 4.5%,
   cooling Fed-cut hopes and pressuring high-multiple growth/semis.
3. **Narrative shift.** Emerging "memory-chip glut + soft smartphone demand"
   story added fuel; AI-optics sentiment cooled.

This is a **macro + single-sector** shock, not a stock-specific story for most
names — every one of our 12 biggest 1-day losers was a semi / semi-cap-
equipment / optical name (QUIK −15.8, AEHR −15.6, RMBS −14.2, MXL −14.1,
MU −13.3, FN −13.1, AAOI −12.8, CLS −12.6, UCTT −12.4, LASR −12.0, TER −12.0,
AMKR −12.0). Every gainer was defensive (MCK +2.5, NYT +2.2, CRAI +2.2, pharma).

### Fabrinet (FN) — the single-name cautionary tale
The `mom_roa_top1` sleeve (and its LLM-overlay twin) bought FN at **$725 on
6/03** — the exact top of a 2-day **+16% spike** (FN was $622 on 6/01). By 6/05
it had fully round-tripped to $621.25 (−14% from entry). Company-specific
overhang per news: cautious Q4 guidance, a drop in operating cash flow, higher
capex, and AI-optics profit-taking after record highs. **Momentum bought a
parabolic top right before the repricing.**

> Flag: the `llm_overlay_mom_roa_top1` sleeve set a **$600 invalidation stop**
> on FN. FN closed 6/05 at $621.25 — only **3.4% above the stop**. It likely
> triggers Monday if the slide continues. (No action taken — paper sleeve,
> rebalance/MTM tasks run on their own schedule.)

### The 6/03 rebalance chased the crowded trade
Every name the last rebalance (6/03) *added* is now a top loser: FN −14%,
CIEN −21%, RMBS −15%, WDC −14%, INTC −12%. All semis, all bought within days of
the sector cracking. Meanwhile the **inception (5/01) semis are still the big
winners**: MU +59%, DOCN +65%, STX +17%, LRCX +18%. Same sector — the
difference is entry timing. Momentum rotated *into* an already-extended theme.

## Strategy ideas (ranked by edge / effort)

**1. Sector cap on the momentum sleeves (preemptive DD control).**
Confirmed `paper_rebalance.py` has **no sector cap** today — momentum naturally
ran Tech to ~50%. Cap any single GICS sector at ~30–35% of book (redistribute to
next-ranked names). On Friday this would have roughly halved the momentum
sleeves' loss (toward the −3% the diversified sector sleeve took). This is
*preemptive*, not reactive — which is exactly what [[sleeves_verdict]] concluded
DD control must be (reactive stops/buffers all failed). **Highest-conviction
idea; backtest it.** Caveat: a sector cap will also trim the MU/DOCN-style
winners, so test net CAGR/Sharpe on both windows, not just drawdown.

**2. Overbought / extension entry filter.**
Confirmed no extension filter exists. FN/RMBS/WDC/CIEN were all bought
mid-parabola. Add a rule rejecting names trading >X% above their 20-day MA
(or top-decile short-term RSI) at rebalance — i.e. "don't pay up for momentum
that already went vertical." Note `research/test_reversal_and_mta.py` exists;
check whether this was already explored before re-running.

**3. Seed the macro LLM overlay (`llm_overlay_sector_top4_paper`).**
Built 2026-06-05, still unseeded (cash $100k, 0 decisions — confirmed). Its
4-prompt macro veto (rates / valuation / breadth / bear-case → cash) is aimed at
*precisely* this kind of rate-spike + breadth-deterioration event. 6/05 is an
ideal first forward-test for it. Recommend seeding so the next macro wobble is
captured. (Honest prior from [[llm_overlay_experiment]] still holds: macro is
the weakest LLM edge — but it's now built, so let it run.)

**4. Re-confirm: single-name top-1 is a variance machine, not a strategy.**
Both top-1 sleeves took −13% in a day from one name's idiosyncratic + sector
move. This is the experiment working as designed (it's a control for the LLM
overlay, [[llm_overlay_experiment]]), but it underscores that N=1 sizing is
dominated by luck; don't read signal into its absolute level — only into
control-vs-treatment *spread*.

## What I did NOT do
- No trades, no rebalances, no seeding, no stop executions — all sleeves run via
  their own scheduled tasks; this run is research/reporting only.
- Did not implement the sector cap or extension filter — flagged for a future
  backtest session (needs both-window validation per the post-audit discipline).

## Verification notes
- Prices from `var/trades.db` `price_cache` (yfinance, real market data).
- 1-day NAV moves computed 6/04→6/05 from `paper_nav` (6/06–6/07 are weekend,
  prices flat — earlier weekend rows are not the trading-day move).
- Real-world causes corroborated by CNBC / TheStreet / Yahoo / TipRanks
  6/04–6/07 coverage.

## UPDATE — Monday 6/08 follow-through (added later 6/08, after market data landed)

The first run of this report (earlier 6/08) only had data through Fri 6/05 and
left one question open: *would the slide continue Monday, and would FN's $600
stop trigger?* Monday's prices are now in the DB. **The crash did NOT continue —
6/08 was a sharp V-bounce.** The flush was sentiment/positioning, not a
fundamental regime break.

Crash names, 6/05 → 6/08 close:
`MU +9.9%, INTC +11.2%, AAOI +11.1%, LRCX +7.0%, AMKR +5.1%, TER +4.7%,
RMBS +4.6%, CLS +4.0%, QUIK +3.9%, STX +3.5%, WDC +3.0%, AVGO +2.8%`.
A few kept falling (`CIEN −4.4%, AEHR −2.9%, MXL −2.0%, DOCN −0.3%`).

Sleeve NAV recovery 6/05 → 6/08: roa6535 **+1.47%**, v2 +1.08%, v1 +0.82%,
sector_top4 +0.46%, both top-1 sleeves +0.40%. Cumulative since 5/01 inception:
roa6535 **+3.69%** (leader), sector_top4 +2.59%, v1 −1.58%, v2 −2.74%,
top-1 −13.4%, llm-overlay-top1 −14.0%.

**FN: stop did NOT trigger.** FN closed 6/05 $621.25 → 6/08 **$623.71**, staying
above the $600 invalidation level. Still −14% from the $725 entry, but no exit
fired in any sleeve (confirmed: all five FN positions still `open`, zero recent
exits in `paper_positions`).

### The strategic lesson the bounce hands us (this is the real find)
A **reactive** stop-loss would have sold FN/CIEN/RMBS into Friday's −13% bottom
and **missed Monday's +5–11% bounce** in the very names it sold. This is a clean,
live re-confirmation of [[sleeves_verdict]]: reactive risk control (stops,
re-entry buffers) whipsaws on exactly this kind of 1-day flush — DD control has
to be **preemptive**. It re-ranks this morning's two backtest ideas:

- **Sector cap (preemptive) — promote to top priority.** Confirmed mom_v2 is
  currently **47.8% Technology** (+ 23.8% Healthcare) open-weight, so a 30–35%
  GICS cap would bind today. It dampens the *entry into* the crowded theme
  without forcing a *sell at* the bottom. This is the right shape of control.
- **Single-name stop (reactive) — the FN near-miss argues against it.** Had the
  stop sat at, say, $640 instead of $600 it would have fired Friday and locked
  the loss one trading day before the bounce. N=1 + reactive stop = whipsaw
  machine; keep top-1 sleeves as the LLM-overlay *control* only, not a template.

`llm_overlay_sector_top4_paper` is still unseeded (cash $100k, 0 decisions) — the
6/05→6/08 round-trip would have been an ideal first forward-test for its macro
veto; re-flagged for seeding (no write action taken here).

Net: nothing broke, the books bounced with the tape, and the episode produced
one genuinely useful, falsifiable conclusion — **prefer a preemptive sector cap
over reactive stops** — to validate in a both-window backtest.

Sources:
- [TheStreet — Stock Market Today June 5 2026](https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-june-05-2026)
- [CNBC — Nasdaq falls 4%, traders flee chip stocks](https://www.cnbc.com/2026/06/04/stock-market-today-live-updates.html)
- [CNBC — Broadcom, Micron, ARM sink](https://www.cnbc.com/2026/06/04/chipmaker-equities-micron-marvell-broadcom-intel.html)
- [TipRanks — Why Fabrinet's Hot Stock Is Suddenly Sinking](https://www.tipranks.com/news/catalyst/why-fabrinets-hot-stock-is-suddenly-sinking)
- [Intellectia — Semiconductor Selloff June 2026](https://intellectia.ai/blog/semiconductor-stocks-selloff-june-2026)
