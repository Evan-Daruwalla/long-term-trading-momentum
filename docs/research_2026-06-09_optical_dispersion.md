# Daily Trade Research — 2026-06-09 (covering Tue 2026-06-09)

Automated `daily-trade-check` run. Today is Tue 2026-06-09. The prior trading
day (Mon 6/08) was the V-bounce already documented in
[research_2026-06-08_chip_crash.md](research_2026-06-08_chip_crash.md). This
report covers **today's session (6/09)**, for which intraday/close prices are
already in `price_cache` (4,456 tickers as of this run).

## TL;DR

The chip selloff resumed today, but the real story is a **clean split inside
the AI-optics theme**: a single megatrend produced a **+9% winner and a −14%
loser on the same day**.

- **Optical *fiber / materials* (winner):** Corning (GLW) **+9.3%** premarket on
  a multibillion-dollar Amazon data-center fiber deal — its 3rd hyperscaler
  contract this year (after Meta ~$6B and Nvidia).
- **Optical *transceivers / co-packaged optics* (losers):** a SemiAnalysis
  institutional note (sourced from Computex Taipei) flagged a likely **CPO
  rollout delay** → AAOI **−17%** (worst name in all three momentum books),
  COHR −11%, MXL −8%, CIEN −6%, FN −6%, LITE −8%. *Contested:* Nvidia's
  networking SVP publicly said there are **no** anticipated CPO delays.

**Our momentum sleeves hold every loser (AAOI, COHR, FN, MXL, CIEN) and none of
the winner (GLW).** Same thesis, wrong half. Broad tape was down too (S&P −1%,
Nasdaq −2%) on continued mega-cap-tech rotation and a hardening of Fed
**rate-*hike*** bets (escalation from the "fewer cuts" framing of 6/05).

| Sleeve | est. 1d book move (6/08→6/09) | Note |
|---|---|---|
| `mom_v1_paper` (top-100) | **−0.50%** | most diversified momentum book |
| `mom_v2_paper` (top-50) | **−1.01%** | |
| `mom_roa_6535_paper` (top-50) | **−1.03%** | still cumulative leader |
| `sector_top4_paper` | ~flat | XLI +1.1, XLB +1.6 offset XLK −1.9, XLE −1.6 |
| `mom_roa_top1` / `llm_overlay` (FN) | **−6.05%** | FN $623.71 → $586.00 |

Nothing broke. A −0.5 to −1.0% day on a −2% Nasdaq is sub-beta — the sleeves are
actually *holding up better* than the index because the non-optical, non-mega-cap
holdings (semi-cap equipment, homebuilders, med-tech) diverged **up** today:
UCTT +9.5%, ICHR +7.3%, CALX +3.8%, MHO +3.9%, VCEL +3.5%.

## The real find: dispersion *within* a theme

The 6/08 report's headline lesson was "momentum concentrated us into one crowded
theme (AI-optics)." Today sharpens it: **the theme is not monolithic.** On 6/09
the AI-data-center-optical buildout simultaneously:

- **rewarded** the large-cap incumbent supplier with a signed hyperscaler
  contract (GLW, +9%), and
- **punished** the small/mid-cap transceiver pure-plays on a *rumor* about
  product-roadmap timing (AAOI/COHR/MXL/CIEN/FN, −6 to −17%).

Momentum systematically selected the second group, because the small-cap
transceiver names had the steeper 6–12-month price runs (higher beta, more
"momentum"). The lower-beta large-cap expression of the identical thesis was
invisible to a pure price-momentum ranker. **This is the structural reason the
book caught the losing half.**

### Why this matters for sleeve design
- A **GICS-sector cap** (the 6/08 top-priority idea, cap Tech at ~30–35%) is
  directionally right but **too coarse to have helped today**: the optical
  transceiver cluster is only **5.4% / 8.6% / 6.4%** of the v1 / v2 / roa books
  respectively — far under any sector cap, yet it produced essentially all of
  today's pain. The acute risk is a **tight correlation cluster of co-moving
  small-caps**, not the broad sector weight.
- The better-targeted control is therefore a **correlation-cluster / sub-industry
  cap** (limit aggregate weight in any group of names whose pairwise return
  correlation exceeds a threshold), *or* a **size/quality tilt** that would have
  nudged the book toward GLW-like incumbents over AAOI-like pure-plays. The
  `mom_roa` sleeve's quality (ROA) filter is a partial version of this already —
  worth checking whether a market-cap floor would have surfaced GLW.

Caveat (unchanged from prior audits): any such filter must be validated on
**both** windows for net CAGR/Sharpe, not just drawdown — clusters like this are
also where the biggest *winners* live (MU +59%, DOCN +65% since inception are the
same kind of high-beta theme names).

## Catalyst type → mean-reversion odds (3rd confirmation of the reactive-stop trap)

Pattern across three sessions:
- **6/05 crash** = macro (Broadcom AI guide-down + rates) → **V-bounced 6/08**.
- **6/09 optical leg** = a *contested research note* (SemiAnalysis CPO-delay vs
  Nvidia's denial), not earnings or a fundamental break.

A reactive stop-loss selling AAOI/FN/COHR into today's −6 to −17% close would,
on this catalyst type, very plausibly sell right before a "denial bounce" — the
same whipsaw the 6/08 bounce demonstrated and that [[sleeves_verdict]] already
concluded must be avoided. This is now the **third independent live
re-confirmation** that DD control here must be **preemptive (cluster cap / size
tilt), not reactive (stops).**

## FN: the LLM stock-overlay experiment hits its first real divergence

FN closed **$586.00** today — **below the $600 invalidation stop** the
`llm_overlay_mom_roa_top1_paper` treatment sleeve set on its 6/03 entry. Verified
in code: `daily.bat` (scheduled 5:15pm via the `TradingDailyMTM` task) runs
`llm_overlay_ops check-invalidation`, which sells to cash when `close <= stop`.
**Tonight's automated run will therefore exit FN from the treatment sleeve**
(locking ≈ −19% from the $725 entry), while the **control** (`mom_roa_top1_paper`,
no stop) keeps holding FN. As of this run both still show FN `open` because
tonight's MTM/invalidation cycle hasn't run yet. *No manual action taken — the
scheduled task does this on its own.*

Two things make this a genuinely informative first divergence (per
[[llm_overlay_experiment]]):
1. The overlay's own 6/03 BUY rationale **explicitly named "CPO structural risk"**
   as the bear case — and CPO is *exactly* the risk that fired today. The LLM
   identified the right risk and bought anyway, but its invalidation level is now
   doing the job the thesis-level judgment didn't.
2. The control-vs-treatment spread from here is the actual experiment: if FN keeps
   falling, the stop scores a point **for** the overlay; if FN bounces on Nvidia's
   CPO denial, it scores **against** (reactive whipsaw). Watch the spread, not
   either sleeve's absolute level.

## Strategy ideas (ranked by edge / effort)

1. **Correlation-cluster cap (refines the 6/08 sector-cap idea — promote).**
   Cap aggregate book weight in any cluster of names with pairwise correlation
   above a threshold (e.g. >0.7 over trailing 60d), redistributing to the next
   uncorrelated ranked name. This targets today's actual failure mode (a 5–9%
   cluster doing all the damage) where a 30–35% GICS cap would not have bound.
   Backtest both windows; compare head-to-head against the simpler GICS cap so we
   know whether the extra complexity buys anything.
2. **Size/quality tilt check (cheap diagnostic, near-zero new data).**
   Re-rank a recent rebalance with a market-cap floor and see whether GLW-class
   incumbents would have displaced the AAOI-class pure-plays. If a modest cap
   floor systematically swaps the losing half of a theme for the winning half
   without killing CAGR, that's a high-value, low-effort upgrade. `mom_roa`
   already half-does this via ROA; quantify the marginal effect of size.
3. **Seed the macro LLM overlay (`llm_overlay_sector_top4_paper`) — 3rd re-flag.**
   Still unseeded (cash $100k, 0 decisions, confirmed). A 5/05→6/09 stretch of
   rate-*hike* bets + tech derating + breadth deterioration is precisely its
   target regime; every unseeded day is a missed forward-test. (Honest prior from
   [[llm_overlay_experiment]] unchanged: macro is the weakest LLM edge — but it's
   built, so let it run.)
4. **Don't over-fit to optical.** The cluster is only 5–9% of book and the names
   are also the source of the biggest inception winners. The lesson is about a
   *general* cluster-risk control, not a one-off "avoid optics" rule.

## What I did NOT do
- No trades, rebalances, seeding, or stop executions. All sleeves run via their
  own scheduled tasks; the FN invalidation exit will fire automatically tonight.
- Did not implement the cluster cap or size-tilt diagnostic — flagged for a
  future both-window backtest session per post-audit discipline.
- Did not edit `record_*`/`state_*` (doc-cadence files). Following the 6/08
  daily-run precedent of research-doc-only; flag for the next interactive session
  that the 3-prompt cadence may be due.

## Verification notes
- Prices from `var/trades.db` `price_cache` (kind=`close`, yfinance). 6/09 has
  4,456 tickers cached at run time (partial vs ~5,260 on a settled day — a few
  thin names may revise after tonight's full refresh).
- 1-day moves computed 6/08→6/09 close; book moves are entry-qty-weighted over
  priced holdings (1 name missing a 6/09 price in each momentum book).
- Real-world causes corroborated by CNBC / TheStreet / Benzinga / GuruFocus /
  Yahoo Finance 6/08–6/09 coverage.

## Sources
- [TheStreet — Stock Market Today June 8, 2026 (Monday comeback)](https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-june-08-2026)
- [Benzinga — Applied Optoelectronics shares sliding Tuesday (CPO-delay note)](https://www.benzinga.com/trading-ideas/movers/26/06/53095747/applied-optoelectronics-shares-are-sliding-tuesday-whats-driving-the-action)
- [GuruFocus — AAOI drops 14% amid bearish report](https://www.gurufocus.com/news/8908427/applied-optoelectronics-aaoi-shares-drop-14-amid-bearish-report)
- [MSN/Reuters — AAOI leads networking stocks down on CPO rollout-delay report](https://www.msn.com/en-us/money/other/applied-optoelectronics-leads-networking-stocks-down-following-report-on-cpo-rollout-delay/ar-AA25cVuo)
- [GuruFocus — Corning surges following Amazon deal](https://www.gurufocus.com/news/8905262/corning-glw-sees-stock-surge-following-amazon-deal)
- [Yahoo Finance — Why Corning is up after Amazon's multiyear US data-center fiber deal](https://finance.yahoo.com/markets/stocks/articles/why-corning-glw-6-1-061410127.html)
- [Yahoo Finance — Nasdaq sinks as AI trade halts on Fed-hike bets](https://finance.yahoo.com/markets/live/stock-market-today-dow-sp-500-nasdaq-sink-as-jobs-report-fuels-fed-hike-bets-chip-stocks-sell-off-230134285.html)
