# Project Record — Full Chronological History

Written 2026-05-27. Every entry is grounded in one of:
- Memory files (`~/.claude/projects/D--ClaudeCode-Trading/memory/*.md`)
- Source file modification timestamps (from `stat`)
- Output file modification timestamps (from `stat`)
- JSON result artifact content (from `var/momentum/*.json`)
- Existing doc content (`HANDOFF.md`, `docs/state_2026-05-27.md`)

Sections where a timestamp can't be precisely verified are explicitly
marked. No fabricated metrics, dates, or file names.

> **REMINDER (added 2026-06-30): after editing this file, refresh the HTML.**
> The rendered view (`Project Record — Full Chronological History.html`, same
> folder) does NOT auto-update — it's a static snapshot. Run one of:
> - One-shot: `.venv\Scripts\python.exe -m scripts.render_record_html`
> - Live while editing: `scripts\watch_record_html.bat` (watches this file,
>   re-renders instantly on every save, event-driven via `watchdog` — leave
>   it running in a terminal for the session, Ctrl+C to stop)

---

# How this document is organized

This record has two parts plus this navigation front-matter (added 2026-06-12;
purely additive — no prior content was altered):

- **Part I — Phases 0–3** (`##` headings): the original 2026-05-27
  consolidation, written in one pass from memory files + file timestamps.
  Covers project origin through the first paper-trade deployment.
- **Part II — Appendices A–X** (`#` headings): chronological addenda appended
  one session at a time per the `CLAUDE.md` cadence rule. **Append-only** —
  prior appendices are never edited. Appendix A is the detailed Form-4 era
  history; B onward is the post-record running log.

The two heading levels encode that distinction (Phases are sections of the
original record; Appendices are top-level addenda). Sub-sections use the
`Letter.Number` convention (e.g. `B.7`, `Q.2`).

The three sections below — **Table of Contents**, **Thematic digest**, and
**Experiment index** — are reading aids. The authoritative detail always
lives in the dated entry, not the digest.

---

# Table of Contents

**Part I — Original record (2026-05-27)**
- [Phase 0 — Project origin](#phase-0--project-origin-2026-04-25) (~04-25)
- [Phase 1 — Form 4 insider-copy strategy](#phase-1--form-4-insider-copy-strategy-closed-2026-05-22) (closed 05-22)
- [Phase 2a — Momentum baseline](#phase-2a--momentum-baseline-2026-05-25) (05-25)
- [Phase 2b — Sleeve multi-factor experiments](#phase-2b--sleeve-multi-factor-experiments-2026-05-26) (05-26)
- [Phase 2c — Version freeze + regression tests + robustness](#phase-2c--strategy-version-freeze--regression-tests--robustness-2026-05-26) (05-26)
- [Phase 2d — XBRL pipeline + quality factors](#phase-2d--xbrl-pipeline--quality-factors-2026-05-26--2026-05-27) (05-26→27)
- [Phase 2e — Closing experiments](#phase-2e--closing-experiments-2026-05-27) (05-27)
- [Phase 3 — Consolidation](#phase-3--consolidation-2026-05-27-afternoon) (05-27)
- [Summary timeline](#summary-timeline-verified-anchor-points) · [What's not in this record](#whats-not-in-this-record-honest-gaps)

**Part II — Appendices (chronological)**
- [A — Detailed Phase 1 history (Form 4 era)](#appendix-a--detailed-phase-1-history-form-4-era-2026-04-25-to-2026-05-22) (04-25→05-22)
- [B — Paper trade + Data audit + Overlay re-tests](#appendix-b---paper-trade--data-audit--overlay-re-tests-2026-05-27-to-2026-05-28) (05-27→28)
- [C — Vol-target fine-tune + docs cadence hook](#appendix-c---vol-target-fine-tune--docs-cadence-hook-2026-05-28-late-session) (05-28)
- [D — Long-short momentum research arc](#appendix-d---long-short-momentum-research-arc-2026-05-28-evening) (05-28)
- [E — Plan B: ROA + momentum combo](#appendix-e---plan-b-roa--momentum-cross-sectional-combo-2026-05-28-evening-contd) (05-28)
- [F — mom_roa_6535 deployment + new-data exploration](#appendix-f---mom_roa_6535-deployment--new-data-exploration-begins-2026-05-28-late) (05-28)
- [G — VIX regime + 3-factor + PEAD launch](#appendix-g---vix-regime-test--3-factor-extension--pead-launch-2026-05-28-night) (05-28)
- [H — 3-factor extensions: accruals + PEAD](#appendix-h---3-factor-extensions-accruals--pead-2026-05-29-early-morning) (05-29)
- [I — Structurally novel strategies + file reorg + ops](#appendix-i---structurally-novel-strategies--file-reorg--ops-2026-05-29) (05-29)
- [J — Audit fixes + LLM-overlay experiment](#appendix-j---audit-fixes--llm-overlay-experiment-2026-05-30--05-31) (05-30→31)
- [K — LLM-overlay first treatment trade + cadence rule](#appendix-k---llm-overlay-first-treatment-trade--cadence-rule-2026-06-03) (06-03)
- [L — June rebalance, sleeve rename, sim refactor + audit](#appendix-l---june-rebalance-sleeve-rename-sim-refactor--audit-2026-06-0304) (06-03→04)
- [M — Market selloff analysis + sector-overlay experiment](#appendix-m---market-selloff-analysis--sector-overlay-experiment-2026-06-05) (06-05)
- [N — Dashboard S&P 500 control benchmark](#appendix-n---dashboard-sp-500-control-benchmark-2026-06-06) (06-06)
- [O — Daily-trade-check: 6/05 chip crash follow-up](#appendix-o---daily-trade-check-follow-up-on-the-605-chip-crash-2026-06-08-automated) (06-08)
- [P — Algo-landscape research: top-5 candidates](#appendix-p---algo-landscape-research-top-5-candidates-2026-06-09) (06-09)
- [Q — Built + backtested top-5; deployed 1 winner](#appendix-q---built--backtested-the-top-5-candidates-deployed-1-winner-2026-06-09) (06-09)
- [R — Long-short vol-target: re-run + crash-fix, FAIL](#appendix-r---long-short-vol-target-re-run--crash-fix-sweep-verified-fail-2026-06-09) (06-09)
- [S — Backdated residual_roa_6535_paper to 05-01](#appendix-s---backdated-residual_roa_6535_paper-to-2026-05-01-2026-06-09) (06-09)
- [T — Full audit, 4th sweep](#appendix-t---full-audit-4th-sweep-2026-06-09-late) (06-09)
- [U — Dashboard rework: dense Overview view](#appendix-u---dashboard-rework-dense-overview-default-view-2026-06-10) (06-10)
- [V — Scheduled daily-trade-check: optical sell-off](#appendix-v---scheduled-daily-trade-check-optical-sell-off--residual-validation-2026-06-10) (06-10)
- [W — S&P 500 control as a real sleeve + chart polish](#appendix-w---sp-500-control-as-a-real-sleeve--chart-polish-2026-06-10) (06-10)
- [X — KLAC 10:1 split fix + Overview markers](#appendix-x---klac-101-split-data-integrity-fix--overview-markers-2026-06-11) (06-11)
- [Y — Docs overhaul: HANDOFF rewrite, record reorg, HTML render](#appendix-y---docs-overhaul-handoff-rewrite-record-reorganization-html-render-2026-06-12) (06-12)
- [Z — KLAC split self-heal, held-position seam verifier, sector-overlay seeded](#appendix-z---klac-split-self-heal-held-position-seam-verifier-sector-overlay-seeded-2026-06-12) (06-12)
- [AA — Systemic history-gap bug: backfill, frozen re-baseline, sleeve re-inception](#appendix-aa---systemic-history-gap-data-bug-backfill-frozen-re-baseline-sleeve-re-inception-2026-06-13) (06-13)
- [AB — Strategy re-validation on backfilled clean data](#appendix-ab---strategy-re-validation-on-backfilled-clean-data-2026-06-13) (06-13)
- [AC — Sleeve backdate to 05-01, slippage realism, unattended-cron scaffold](#appendix-ac---sleeve-backdate-to-05-01-slippage-realism-unattended-cron-scaffold-2026-06-13) (06-13)
- [AD — ADV liquidity gap closed; daily volume-staleness finding](#appendix-ad---adv-liquidity-gap-closed-daily-volume-staleness-finding-2026-06-13) (06-13)
- [AE — Volume-staleness fix: monthly held-name warm wired into rebalance (option b)](#appendix-ae---volume-staleness-fix-monthly-held-name-warm-wired-into-rebalance-option-b-2026-06-14) (06-14)
- [AF — Daily trade check: Iran peace deal, SEZL +14.4%, MU hits $1T](#appendix-af---daily-trade-check-iran-peace-deal-sezl-144-mu-hits-1t-2026-06-15) (06-15)
- [AG — Daily trade check: Juneteenth long weekend gap, MU earnings week](#appendix-ag---daily-trade-check-juneteenth-long-weekend-gap-mu-earnings-week-2026-06-22) (06-22)
- [AH — rebalance_log.md + SNSE→FTH ticker-rename corporate action](#appendix-ah---rebalance_logmd--snsefth-ticker-rename-corporate-action-2026-06-27) (06-27)
- [AI — Graph-driven workflow optimization: daily refresh persists volume (supersedes AE)](#appendix-ai---graph-driven-workflow-optimization-daily-refresh-persists-volume-supersedes-ae-2026-06-27) (06-27)
- [AJ — June-30 lock prep: KLAC split, SATS→ECHO, AAOI verify, overlay evals](#appendix-aj---june-30-lock-prep-klac-split-sats-echo-aaoi-verify-overlay-evals-2026-06-29) (06-29)
- [AK — LLM-cascade sleeves (always-invested 3rd overlay pair) + dashboard fixes](#appendix-ak---llm-cascade-sleeves-always-invested-3rd-overlay-pair--dashboard-fixes-2026-06-30) (06-30)
- [AL — Alpaca paper integration begins + 7/1 clean-start cohort](#appendix-al---alpaca-paper-integration-begins--71-clean-start-cohort-2026-06-30) (06-30)
- [AM — Graphify root expansion + AlpacaError bridge trace + appendix-date audit](#appendix-am---graphify-root-expansion--alpacaerror-bridge-trace--appendix-date-audit-2026-06-30) (06-30)
- [AN — Record file renamed; HTML render tied to it](#appendix-an---record-file-renamed-html-render-tied-to-it-2026-06-30) (06-30)
- [AO — Rename notes added at every record_2026-05-27 mention](#appendix-ao---rename-notes-added-at-every-record_2026-05-27-mention-2026-06-30) (06-30)
- [AP — Fixed the monthly-rebalance trigger timing bug](#appendix-ap---fixed-the-monthly-rebalance-trigger-timing-bug-2026-07-01) (07-01)
- [AQ — daily_report.md gets the same standalone-HTML render](#appendix-aq---daily_reportmd-gets-the-same-standalone-html-render-2026-07-01) (07-01)
- [AR — Rewrote monthy-llm-rebalance's prompt: full context + instructions](#appendix-ar---rewrote-monthy-llm-rebalances-prompt-full-context--instructions-2026-07-01) (07-01)
- [AS — cmd.exe batch-parsing bug found + fixed; July rebalance completes](#appendix-as---cmdexe-batch-parsing-bug-in-rebalancebatdailybat-found--fixed-july-rebalance-completes-2026-07-01) (07-01)
- [AT — Alpaca non-fractionable gap fixed; all 11 07-01 sleeves reset to 07-06](#appendix-at---alpaca-non-fractionable-gap-fixed-whole-share-fallback--db-reflect-all-11-07-01-sleeves-reset-to-07-06-2026-07-02) (07-02)
- [AU — Attempted a 07-02 early deploy; HELD to 07-06 for incomplete close data](#appendix-au---attempted-a-07-02-early-deploy-held-to-07-06-for-incomplete-close-data-2026-07-02) (07-02)
- [AV — 07-06 cohort deploy executed; 11 sleeves live, Alpaca mirrored, monthly task re-enabled](#appendix-av---07-06-cohort-deploy-executed-all-11-sleeves-live-alpaca-mirrored-monthly-task-re-enabled-2026-07-07-1320-local) (07-07)
- [AW — Session ops: RuFlo statusline disabled, shadow-file recurrence, deploy scheduled from chat](#appendix-aw---session-ops-ruflo-statusline-disabled-stray-file-source-shadow-file-recurrence-deploy-scheduled-from-chat-2026-07-0507-07) (07-05→07)
- [AX — CLAUDE.md rewritten; ruflo fully removed; PRD-handoff system built](#appendix-ax---claudemd-rewritten-ruflo-fully-removed-prd-handoff-system-built-2026-07-08-afternoon) (07-08)
- [AY — Handoff sync: TOC backlog repaired, cash-buffer cadence miss logged, doc pointers fixed](#appendix-ay---handoff-sync-toc-backlog-repaired-am-ax-cash-buffer-cadence-miss-logged-doc-pointers-fixed-2026-07-08-1715-local) (07-08)
- [AZ — State-doc tier retired: every state_&lt;date&gt;.md archived verbatim](#appendix-az---state-doc-tier-retired-every-state_md-archived-verbatim-below-2026-07-08-1730-local) (07-08)
- [BA — Owed frozen-test run cleared (cash-buffer commit 3807f23)](#appendix-ba---owed-frozen-test-run-cleared-cash-buffer-commit-3807f23-2026-07-08-2035-local) (07-08)
- [BB — M2.1 coverage gate script; caught live 07-08 shortfall](#appendix-bb---m21-coverage-gate-check_coveragepy-caught-live-07-08-incomplete-publication-shortfall-2026-07-09-1320-local) (07-09)
- [BC — M2.2 coverage gate wired into daily.bat, ahead of MTM](#appendix-bc---m22-coverage-gate-wired-into-dailybat-ahead-of-mtm-2026-07-09-1330-local) (07-09)
- [BD — M2.3 anomaly detector wired into daily.bat](#appendix-bd---m23-anomaly-detector-check_anomaliespy-wired-into-dailybat-2026-07-09-1335-local) (07-09)
- [BE — M2.4 cache-gap auditor; M2 complete](#appendix-be---m24-cache-gap-auditor-check_cache_gapspy-full-run-15207-flagged-m2-complete-2026-07-09-1340-local) (07-09)

---

# Thematic digest

> A topic-organized summary of the chronological log. Every figure here is
> drawn from the dated entry it summarizes; follow the link for the evidence.

## The arc in one paragraph

Started as a **Form 4 insider-copy bot** (Phase 1) → walk-forward + held-out
both showed no edge → **closed 2026-05-22**. Pivoted to **systematic factor
portfolios** built on a momentum core (Phase 2a→2e). A **major data audit on
2026-05-28** (Appendix B) found yfinance Friday-spike + unadjusted-reverse-split
corruption that had inflated the in-sample numbers — collapsing the 9-year
in-sample validation to "2.4-year held-out only." Since then the project has
**paper-traded multiple sleeves forward** while continuing controlled research,
with periodic full audits (Appendices L, T) catching and fixing data/sim seams.

## Deployed sleeves (the winners that cleared the bar)

| Sleeve | What | First deployed | Detail |
|---|---|---|---|
| mom_v1_paper | 12-1 momentum, top-100 | paper since 05-01 | [B.16–B.17](#b16---2026-05-28-0500---v1-vs-v2-head-to-head-on-clean-data) |
| mom_v2_paper | 12-1 momentum, top-50 (frozen baseline) | paper since 05-01 | [Phase 2c](#phase-2c--strategy-version-freeze--regression-tests--robustness-2026-05-26) |
| mom_roa_6535_paper | 65% mom Z + 35% ROA Z, top-50 | [F.3](#f3---2026-05-28-2230---deployed-mom_roa_6535_paper-as-3rd-sleeve) (Attempt 17) | first to beat mom_v2 both windows |
| sector_top4_paper | 12-1 momentum on 11 SPDR ETFs, top-4 | [I.3/I.6](#i3---2026-05-29---structurally-novel-idea-1-sector-momentum) | defensive diversifier (~½ the DD) |
| residual_roa_6535_paper | 65% residual-mom Z + 35% ROA Z, top-50 | [Q.4](#q4---deployment-of-residual_roa_6535_paper) (Attempt 24) | lower-DD sibling; backdated to 05-01 in [S](#appendix-s---backdated-residual_roa_6535_paper-to-2026-05-01-2026-06-09) |
| spy_benchmark_paper | $100k buy-and-hold SPY control | [W](#appendix-w---sp-500-control-as-a-real-sleeve--chart-polish-2026-06-10) | benchmark, never rebalanced |

LLM-experiment sleeves (falsifiable, kill-switch-gated, NOT trusted strategies):
the **stock overlay** pair `mom_roa_top1_paper` (control) vs
`llm_overlay_mom_roa_top1_paper` (treatment) — [J](#appendix-j---audit-fixes--llm-overlay-experiment-2026-05-30--05-31),
[K](#appendix-k---llm-overlay-first-treatment-trade--cadence-rule-2026-06-03) — and the
**macro sector overlay** `llm_overlay_sector_top4_paper` — [M.2](#m2---built-a-sector-overlay-macro-llm-veto--user-said-a-build-path).

## The data-integrity thread (why pre-2026-05-28 numbers are suspect)

- **[Appendix B](#appendix-b---paper-trade--data-audit--overlay-re-tests-2026-05-27-to-2026-05-28)** — the founding audit: Friday spikes + unadjusted
  reverse splits; mom_v2 in-sample +455% → +27.3% total once cleaned. Fixes:
  spike-null (2,017 rows), `universe.MAX_HIST_RATIO=100`, re-baselined frozen tests.
- **[Appendix J](#appendix-j---audit-fixes--llm-overlay-experiment-2026-05-30--05-31)** — staleness audit: `daily_price_refresh` hadn't run in
  11 days; NAVs were stale-wrong. Added scheduled tasks + staleness guards.
- **[Audit 2026-06-01]** (BKGM price ghost), **[Appendix L.3](#l3---sim-refactor-behavior-preserving--full-audit-report-docsaudit_2026-06-04md)** (sim refactor +
  audit), **[Appendix T](#appendix-t---full-audit-4th-sweep-2026-06-09-late)** (dividend-adjustment seam in daily_price_refresh —
  the cache convention is split-adjusted, dividend-UNadjusted), **[Appendix X](#appendix-x---klac-101-split-data-integrity-fix--overview-markers-2026-06-11)**
  (KLAC 10:1 split applied early by yfinance).
- **Standing convention**: `price_cache` closes are **split-adjusted,
  dividend-UNadjusted** (`auto_adjust=False`). Every cache writer must honor it.

## Standing lessons (recur across the log)

1. **Validate held-out wins on in-sample before promoting** — weekly/quarterly
   rebal looked great held-out, were 2024-26 overfits ([Phase 2c](#phase-2c--strategy-version-freeze--regression-tests--robustness-2026-05-26)).
2. **Risk control on momentum must be preemptive, not reactive** — stops,
   stops+reentry, trend filter, VIX gate all failed ([B](#appendix-b---paper-trade--data-audit--overlay-re-tests-2026-05-27-to-2026-05-28), [G](#appendix-g---vix-regime-test--3-factor-extension--pead-launch-2026-05-28-night)); reinforced live by
   the 6/05→6/08 V-bounce ([O.1](#o1---monday-608-follow-through-automated-same-day-after-market-data-landed)).
3. **~1 deployable winner per ~20 attempts** — matches the academic factor-decay
   base rate; "obvious next ideas" rarely beat the current best.
4. **Long-short momentum carries unbounded short-squeeze risk** — busts
   in-sample at any leverage ([R](#appendix-r---long-short-vol-target-re-run--crash-fix-sweep-verified-fail-2026-06-09)); held-out edge is regime luck. Research-only.

---

# Experiment index

> Every backtested experiment and its verdict, with a link to the detail.
> "Attempt N" numbers are cited only where the log assigns them.

| Experiment | Where | Verdict |
|---|---|---|
| Form 4 insider-copy (Phase 1) | [Phase 1](#phase-1--form-4-insider-copy-strategy-closed-2026-05-22) / [App. A](#appendix-a--detailed-phase-1-history-form-4-era-2026-04-25-to-2026-05-22) | ❌ No edge (walk-forward + held-out) |
| Naive composite mom+lowvol (Attempt 1) | [Phase 2a](#phase-2a--momentum-baseline-2026-05-25) | ❌ Killed in-sample 19.6→4.0%/yr |
| Separate sleeves $50k top-100 (Attempt 2) | [Phase 2b](#phase-2b--sleeve-multi-factor-experiments-2026-05-26) | ❌ $1M ADV filter killed mom premium |
| Stdev-floor sleeves (Attempt 3) | [Phase 2b](#phase-2b--sleeve-multi-factor-experiments-2026-05-26) | ❌ No diversification benefit |
| **momentum_v2 (top-50)** freeze | [Phase 2c](#phase-2c--strategy-version-freeze--regression-tests--robustness-2026-05-26) | ✅ **Frozen baseline** |
| Weekly / quarterly rebalance | [Phase 2c](#phase-2c--strategy-version-freeze--regression-tests--robustness-2026-05-26) | ❌ 2024-26 overfit |
| yfinance-proxy quality (Attempt 4) | [Phase 2d](#phase-2d--xbrl-pipeline--quality-factors-2026-05-26--2026-05-27) | ❌ Lookahead-biased |
| XBRL quality v1 (Attempt 5) | [Phase 2d](#phase-2d--xbrl-pipeline--quality-factors-2026-05-26--2026-05-27) | ❌ Real but doesn't combine |
| Mono-factor sweep (24 configs) | [Phase 2d](#phase-2d--xbrl-pipeline--quality-factors-2026-05-26--2026-05-27) | ❌ None beat v2 both windows |
| XBRL quality v2 8-comp (Attempt 6) | [Phase 2d](#phase-2d--xbrl-pipeline--quality-factors-2026-05-26--2026-05-27) | ❌ Failed combination |
| quality_xbrl_v2 standalone | [Phase 2e](#phase-2e--closing-experiments-2026-05-27) | ❌ Underperforms benchmarks in-sample |
| Restricted top500/1000 universe | [Phase 2e](#phase-2e--closing-experiments-2026-05-27) | ❌ Survivorship-biased |
| mom_quality_screen (Attempt 7) | [Phase 2e](#phase-2e--closing-experiments-2026-05-27) | ❌ -13.8pp/yr in-sample |
| Stop-loss sweep (Attempt 12) | [B.2](#b2---2026-05-27-2355---stop-loss-sweep-attempt-12-failed) | ❌ Reactive control fails |
| Stops + reentry (Attempt 13) | [B.4](#b4---2026-05-28-0010---stops--reentry-sweep-attempt-13-failed) | ❌ Strictly worse than plain stops |
| SPY 200-DMA trend filter | [B.6](#b6---2026-05-28-0020---preemptive-overlay-sweep-trend--voltgt) / [B.20](#b20---2026-05-28-1200---re-ran-all-overlay-tests-on-clean-data) | ❌ -6pp in / -20pp held-out |
| Vol-target (all variants) | [B.14](#b14---2026-05-28-0400---vol-target-deep-sweep-on-clean-data), [C.2](#c2---2026-05-28-1700---vol-target-fine-tune-for-completeness) | ❌ Marginal; closed |
| Long-short momentum (Attempt 15) | [D.3](#d3---2026-05-28-1900---long-short-momentum-built-attempt-15) | ⚠️ Research-only (busts in-sample) |
| LS + vol-target-spread (Attempt 16) | [D.5](#d5---2026-05-28-2000---ls--vol-target-spread-attempt-16) | ⚠️ Best held-out Sharpe; research-only |
| **mom_roa_6535 (Attempt 17)** | [E.3](#e3---2026-05-28-2130---coarse-sweep-first-winner) / [F.3](#f3---2026-05-28-2230---deployed-mom_roa_6535_paper-as-3rd-sleeve) | ✅ **DEPLOYED** — beats v2 both windows |
| VIX term-structure regime | [G.1](#g1---2026-05-28-2300---vix-term-structure-regime-filter-test) | ❌ Triggers on noise, misses crashes |
| 3-factor mom+ROA+accruals | [H.1](#h1---2026-05-29-0000---3-factor-mom--roa--accruals-sweep-results) | ❌ Tradeoff, not improvement |
| PEAD (yfinance earnings) | [H.2](#h2---2026-05-29-0030---pead-new-data-experiment) | ❌ Dilutes; data only back to 2020 |
| **Sector momentum → sector_top4** | [I.3](#i3---2026-05-29---structurally-novel-idea-1-sector-momentum) | ✅ **DEPLOYED** — defensive 4th sleeve |
| Insider-cluster overlay (mrc_55_30_15) | [I.4](#i4---2026-05-29---structurally-novel-idea-2-insider-cluster-overlay) | ➖ Ties mom_roa; too correlated |
| Cross-strategy ensemble | [I.5](#i5---2026-05-29---structurally-novel-idea-3-cross-strategy-ensemble) | ➖ No clean both-window win |
| **residual_roa_6535 (Attempt 24)** | [Q.2](#q2---backtests-both-frozen-windows-references-re-run-live-on-clean-data) / [Q.4](#q4---deployment-of-residual_roa_6535_paper) | ✅ **DEPLOYED** — lower-DD sibling |
| Turn-of-month + T-bill carry | [Q.2](#q2---backtests-both-frozen-windows-references-re-run-live-on-clean-data) | ❌ Loses to SPY buy-hold |
| VIX-gated short-vol (SVXY) | [Q.2](#q2---backtests-both-frozen-windows-references-re-run-live-on-clean-data) | ❌ Negative held-out Sharpe |
| Gayed leveraged-ETF rotation | [Q.2](#q2---backtests-both-frozen-windows-references-re-run-live-on-clean-data) | ❌ Loses vs QQQ benchmark |
| LS vol-target crash-fix sweep | [R.2–R.3](#r2---crash-fix-sweep-5d-lookback--8-target--hard-gross-cap-15x-fails-worse) | ❌ Busts worse; unbounded short risk |
| LLM stock overlay (BE veto, FN buy) | [J](#appendix-j---audit-fixes--llm-overlay-experiment-2026-05-30--05-31), [K](#appendix-k---llm-overlay-first-treatment-trade--cadence-rule-2026-06-03) | 🔬 Running (kill switch 12mo/30 picks) |
| LLM macro sector overlay | [M.2](#m2---built-a-sector-overlay-macro-llm-veto--user-said-a-build-path) | 🔬 Built; unseeded |

---

## Phase 0 — Project origin (~2026-04-25)

**Source:** `memory/project_overview.md`, `memory/congress_data_decision.md`,
`memory/age_constraint.md` (all originSessionId `767c5c7c-...`).

### Initial brief
Build a Python bot that copies smart-money insider buys:
- Ingest SEC Form 4 filings
- Score tickers by conviction (single-insider buys, CEO/CFO bonus, dollar-amount
  bonus, multi-insider clusters in 30-day window)
- Trade via Alpaca paper account when score ≥ 5
- **Hard rule**: paper-trade for 3+ months before any live deployment

### Constraints surfaced on 2026-04-25
1. **Age constraint** (`memory/age_constraint.md`): user is 17. No real brokerage
   (Alpaca, Schwab, IBKR, Robinhood) available until 18 + SSN/KYC. Phase 3
   pivoted to local `BrokerSimulator` class instead of Alpaca paper account.
   `.env` Alpaca key slots kept for the eventual migration.
2. **Congressional data deferred** (`memory/congress_data_decision.md`): Quiver
   Quantitative wants $30/mo (Tier 1) or $75/mo (Tier 2). Free alternatives
   were dead (Stock Watcher S3 buckets returned 403, Capitol Trades BFF
   returned 503 to non-browser clients). Decision: skip the congressional
   signal source entirely until Form-4-only paper trading proves out.
   Scoring rubric line items "Congressional purchase: +2" and "Same ticker
   in both Form 4 AND congressional: +2" remain inert in v1.

### Output artifact dates (price-cache backfill era)
First out-file modification timestamps observed in `var/`:
- `var/poll.out`              2026-04-25 17:09
- `var/poll2.out`             2026-04-25 17:49
- `var/backfill.out`          2026-04-25 22:55
- `var/backfill_6mo.out`      2026-04-26 12:59
- `var/backfill_2yr.out`      2026-04-27 20:37
- `var/backfill_5y.out`       2026-05-02 17:07
- `var/warm_cache.out`        2026-05-05 14:23
- `var/warm_atr.out`          2026-05-06 21:48

Interpretation: Form 4 ingest + ~5-year price cache backfill ran 2026-04-25
through ~2026-05-06.

---

## Phase 1 — Form 4 insider-copy strategy (closed 2026-05-22)

**Source:** `memory/form4_verdict.md`, file timestamps in `scripts/form4/`,
existing `HANDOFF.md` (pre-update version).

### Work performed (verified by file existence)
Scripts present in `scripts/form4/`:
- `warm_atr.py`, `ingest_form25.py`, `detect_delistings_offline.py`,
  `warm_splits.py`, `audit_dropped_filings.py`, `audit_backfill.py`,
  `run_holdout.py`, `run_phase2_chain.py`, `momentum_backtest.py`,
  `diagnose_r9.py`, `investigate_score9.py`, `optimize_r15.py`,
  `optimize_r15_wf.py`, `tail_dependence.py`, `walk_forward.py`

Output files in `var/`:
- `var/sim_r8.out` through `var/sim_r17_full.out` (rebuild iterations)
- `var/optimizer_2010_2018.out`, `var/optimizer_2010_2018_v2.out`,
  `var/optimizer_wf.out`
- `var/audit_2010_2020.out`
- `var/multi_2y_*.out` (multi-trial parameter sweeps, run 2026-04-28
  through 2026-05-01 per timestamps)

### Verdicts logged (from `memory/form4_verdict.md`)
1. **Single-window raw-return optimizer**: overfit badly. Winner +128%
   in-sample, **−7.5%** on a held-out year when SPY did +29%.
2. **Walk-forward Sharpe optimizer** (Phase 1 fix): confirmed the signal
   has no edge. 4 diverse trading configs (threshold 5-9, stop-loss -8
   to -20, take-profit 25-35, time-exit 60-240, position size 3-7) ALL
   landed at mean yearly Sharpe ≈ 0 across 2015-2024. Best config:
   positive in only 6/10 years; worst-year Sharpe -1.47.
3. **Held-out confirmation**: trial-09 (winner of single-window optimizer
   on 2010-2018) returned -7.54% in May 2025 → May 2026 while SPY did +29%.

**Verdict (2026-05-22):** "Form 4 is dead. Don't restart Form 4 work unless
a fundamentally new approach changes the data (e.g., paid CRSP, different
signal class)."

Infrastructure preserved for reuse: EDGAR ingest pipeline, ~10 yr
price-cache for 8,800+ tickers, walk-forward harness, held-out discipline.

---

## Phase 2a — Momentum baseline (2026-05-25)

**Source:** `memory/momentum_baseline.md`, original `HANDOFF.md` (now archived
into this record by replacement), file timestamps in `trading_bot/factors/`
and `scripts/momentum/`.

### Files created (verified timestamps)
- `trading_bot/factors/__init__.py`          2026-05-25 20:03
- `trading_bot/factors/composite.py`         2026-05-25 21:48
- `var/momentum/runs/20260526-011017_smoke.json`  2026-05-25 20:12 (first smoke)
- `var/momentum/runs/20260526-011417_smoke2.json` 2026-05-25 20:14
- `var/momentum/runs/20260526-011648_smoke3.json` 2026-05-25 20:17
- `var/momentum/runs/20260526-011759_in_sample.json` 2026-05-25 20:40
- `var/momentum/runs/20260526-014206_holdout.json`   2026-05-25 20:44
- `var/momentum/runs/20260526-025026_mom_frac_holdout.json` 2026-05-25 21:55
- `var/momentum/runs/20260526-025549_multi_in_sample.json`  2026-05-25 22:42
- `var/momentum/runs/20260526-034301_multi_holdout.json`    2026-05-25 22:46

### Strategy v1 (from `memory/momentum_baseline.md`)
- 12-1 month momentum (Jegadeesh-Titman academic standard, no parameter tuning)
- Top 100 stocks, equal-weight, monthly rebalance, long-only, fractional shares
- Universe: cached US stocks, ≥252 days history, close ≥$5 both today AND
  252 days ago (kills reverse-split pump artifacts)
- Fill at close(rebal_date) ± 5bps half-spread

### Results recorded
| Window | Total | CAGR | Mean yearly Sharpe | vs SPY |
|---|---:|---:|---:|---|
| In-sample 2015-2023 | +398% | 19.6%/yr | +0.27 | +10%/yr |
| Held-out 2024-2026 (2.4 yr) | +53.1% | 19.5%/yr | +0.72 | ~0%/yr (matches) |

All held-out yearly Sharpes positive (2024 +0.41, 2025 +0.46, 2026 +1.28).

### Fractional-shares fix
Original v1 used `math.floor(dollar_target/price)`. With $100K NAV / 100
names = $1K/name, any stock priced >$1000 (NVDA pre-split, AVGO, BRK-A)
was skipped entirely (~24 skips per rebalance). Fix: use fractional qty
(`positions.qty` is REAL already). Net effect: +5pp on held-out, all yearly
Sharpes up ~0.05.

### Multi-factor experiment #1 (FAILED — naive composite)
File: `trading_bot/factors/composite.py` (timestamp 2026-05-25 21:48).
Combined momentum + low-vol via percentile-rank averaging. Killed in-sample
CAGR from 19.6%/yr → 4.0%/yr (loss of 15.6 pp/yr).
**Mechanism:** low-vol filter excludes the high-vol names where momentum's
real premium lives (biotech rips, AI rallies, energy spikes).

---

## Phase 2b — Sleeve multi-factor experiments (2026-05-26)

**Source:** `memory/sleeves_verdict.md`, file timestamps, sleeve JSON outputs.

### Files created
- `trading_bot/factors/universe.py`           2026-05-26 02:11
- `scripts/momentum/warm_volumes.py`          2026-05-26 01:06
- `scripts/momentum/tc_sensitivity.py`        2026-05-26 02:21
- `scripts/momentum/diagnose_alpha.py`        2026-05-26 02:25
- `scripts/momentum/run_momentum.py`          2026-05-26 02:26
- `trading_bot/factors/low_vol.py`            2026-05-26 17:08
- `scripts/momentum/run_sleeves_chain.py`     2026-05-26 17:08

### Sleeve output files (verified timestamps in `var/momentum/sleeves/`)
| Timestamp | File |
|---|---|
| 2026-05-26 00:10 | `20260526-041502_sleeves_in_sample.json` |
| 2026-05-26 00:14 | `20260526-051040_sleeves_holdout.json` |
| 2026-05-26 01:57 | `20260526-062946_sleeves_gated_in_sample.json` |
| 2026-05-26 02:01 | `20260526-065713_sleeves_gated_holdout.json` |
| 2026-05-26 17:40 | `20260526-220849_sleeves_stdevfloor_in_sample.json` |
| 2026-05-26 17:45 | `20260526-224107_sleeves_stdevfloor_holdout.json` |

Companion `.out` files: `var/sleeves_chain.out`, `var/sleeves_gated.out`,
`var/sleeves_stdevfloor.out`.

### Attempt 2 — Separate sleeves, each $50K, top-100 (FAILED)
(from `memory/sleeves_verdict.md`)
- Without volume filter: momentum sleeve +345%/9yr, low-vol sleeve +7%/9yr
  (illiquid trust units / preferreds)
- Added $1M median dollar-vol universe filter (`scripts/momentum/warm_volumes.py`):

| Run | Combined | Momentum | Low-vol |
|---|---:|---:|---:|
| In-sample ungated | +176% | +345% | +7% |
| In-sample gated | +10% | +29% | −9% |
| Held-out ungated | +33% | +53% | +12% |
| Held-out gated | +24% | +45% | +3% |

Why it failed: $1M ADV removes high-vol small-caps where momentum lives
AND leaves the lowest-vol names dominated by closed-end bond funds
(NXJ, NAD, FRA, BGB) that have ~0.3-0.5%/day stdev but ~0% real return.

### Attempt 3 — Stdev floor (1.0%/day) inside `low_vol.rank_universe` (FAILED)
- Picks problem fixed: bond CEFs gone, low-vol now picks real stable
  large-caps (ATO/IEX/WMB/KMI/KR/NOC/WFC/AFL/PFE)
- Returns improved: in-sample low-vol +6.8% → +13.8%; held-out +11.8% → +17.4%
- Combined: in-sample +176% → +181%, held-out +32.6% → +36.0%
- **But no diversification benefit:**
  - Held-out mean yearly Sharpe identical to mom-solo (+0.72 both)
  - In-sample combined Sharpe (+0.23) actually *worse* than mom-solo (+0.27)
  - Adding low-vol reduces total return by 18pp held-out (capital tied up
    in slower sleeve), with no Sharpe gain to compensate

---

## Phase 2c — Strategy version freeze + regression tests + robustness (2026-05-26)

**Source:** `memory/momentum_v2_verdict.md`, file timestamps, robustness JSON.

### Files created (verified)
- `trading_bot/strategies/__init__.py`        2026-05-26 18:53
- `trading_bot/strategies/momentum_v1.py`     2026-05-26 18:54
- `trading_bot/strategies/momentum_v2.py`     2026-05-26 21:31
- `trading_bot/strategies/test_strategies.py` 2026-05-26 23:27
- `scripts/momentum/robustness_test.py`       2026-05-26 20:12
- `var/momentum/robustness_holdout.json`      2026-05-26 19:25
- `var/momentum/robustness_in_sample.json`    2026-05-26 21:29
- `var/robustness_test.out`                   2026-05-26 19:25
- `var/robustness_in_sample.out`              2026-05-26 21:29

### Test reference values (from `test_strategies.py:39-48`)
Reference captured 2026-05-26. Format: `{strategy: {window: (total_pnl_pct, closed_count)}}`:
- `momentum_v1`:
  - `2023_Q4`: `(12.6237, 67)`
  - `2025_H1`: `(2.1865, 154)`
- `momentum_v2`:
  - `2023_Q4`: `(12.2794, 37)`
  - `2025_H1`: `(12.1738, 90)`
- Tolerances: 5 bps on total_pnl_pct, exact match on trade count.

### Robustness sweep (from `memory/momentum_v2_verdict.md`)
- `top_n`: 100 → 50 (the only change from v1)
- Validated on BOTH in-sample 2015-2023 AND held-out 2024-2026

| Window | Metric | v1 (top-100) | v2 (top-50) | Δ |
|---|---|---:|---:|---:|
| In-sample 2015-23 | Total | +398% | +456% | +58 pp |
| In-sample 2015-23 | CAGR | 19.6%/yr | 21.0%/yr | +1.4 pp/yr |
| Held-out 2024-26 | Total | +53% | +73% | +20 pp |
| Held-out 2024-26 | CAGR | 21.4%/yr | 26.5%/yr | +5.1 pp/yr |
| Held-out Sharpe (mean) | | +0.81 | +0.87 | +0.06 |

### Critical overfit caught
Held-out alone suggested two even better configs that VANISHED on in-sample:
- `top-100 weekly`: held-out +28.4%/yr, **in-sample +1.6%/yr** (2024-26 overfit)
- `top-100 quarterly`: held-out +28.5%/yr, **in-sample +1.8%/yr** (2024-26 overfit)

**Lesson recorded:** always validate held-out wins on in-sample before promoting.

---

## Phase 2d — XBRL pipeline + quality factors (2026-05-26 → 2026-05-27)

**Source:** `memory/sleeves_verdict.md` attempts 4-6, file timestamps,
sleeve JSON outputs.

### Files created
- `trading_bot/factors/quality.py`                 2026-05-26 18:58 (yfinance proxy)
- `scripts/momentum/warm_fundamentals.py`          2026-05-26 17:53
- `var/sleeves_mom_quality.out`                    2026-05-26 18:45
- `var/sleeves_mom_quality_filtered.out`           2026-05-26 19:05
- `trading_bot/factors/quality_xbrl.py`            2026-05-26 23:33
- `scripts/momentum/run_xbrl_quality_chain.py`     2026-05-26 23:33
- `var/warm_xbrl.out`                              2026-05-27 00:04
- `var/sleeves_xbrl_chain.out`                     2026-05-27 01:35
- `trading_bot/factors/momentum.py`                2026-05-27 01:54 (parameterized — added `make_rank_fn(lookback, skip)` closure factory)
- `scripts/momentum/mono_factor_sweep.py`          2026-05-27 01:56
- `scripts/momentum/warm_xbrl.py`                  2026-05-27 01:57
- `trading_bot/factors/quality_xbrl_v2.py`         2026-05-27 01:58
- `var/momentum/mono_factor_sweep.json`            2026-05-27 02:02
- `var/mono_factor_sweep.out`                      2026-05-27 02:02
- `var/warm_xbrl_v2.out`                           2026-05-27 02:30
- `scripts/momentum/run_xbrl_v2_chain.py`          2026-05-27 02:31
- `var/sleeves_xbrl_v2_chain.out`                  2026-05-27 02:35

### Attempt 4 — yfinance-proxy quality (LOOKAHEAD-BIASED)
File: `trading_bot/factors/quality.py`. Scored z(ROE) + z(GM) + z(OM) - z(D/E)
with sanity filters (returnOnAssets ≥ 0.08, operating margin in (-1.0, 1.0)).

Results (held-out 2024-2026, $100K total, from `memory/sleeves_verdict.md`):
- mom + quality (raw, no filter): +50.0% combined / +0.78 Sharpe
- mom + quality (ROA+OM filtered): +92.5% combined / +0.92 Sharpe
- momentum solo (v1): +54.5% combined / +0.72 Sharpe

**Caveat noted:** +128.9% quality-sleeve return (over 2.4 yrs = +43%/yr) is
6-9x the academic quality alpha (~5-7%/yr). Almost certainly lookahead leak.
Magnitude confirmed unreliable.

### Attempt 5 — SEC XBRL point-in-time quality v1 (DEFINITIVE: real but doesn't combine)
Files: `scripts/momentum/warm_xbrl.py`, `trading_bot/factors/quality_xbrl.py`.
SEC EDGAR XBRL company-facts API ingest at ~7.7 req/sec. User-Agent:
"trading-bot-research evan.research@gmail.com". Built `xbrl_facts` table
(ticker, cik, concept, period_end, filed, fy, fp, form, accn, val).
Point-in-time lookups use `filed <= as_of - 60d` lag.

Results (from `memory/sleeves_verdict.md`):

| Strategy | In-sample 2015-23 | Held-out 2024-26 |
|---|---:|---:|
| mom_v2 solo (top-50) | +456% / Sharpe +0.23 | +73% / Sharpe +0.87 |
| mom + quality_xbrl | +203% / Sharpe +0.21 | +42% / Sharpe +0.83 |
| (yfinance quality, biased) | N/A | +93% / Sharpe +0.92 |

Quality_xbrl solo: in-sample +66.3% over 9 yrs = +5.8%/yr; held-out +28.3%
over 2.4 yrs = +10.8%/yr. **The 32pp/yr drop when lookahead removed confirms
yfinance result was almost entirely artifact.**

### Mono-factor sweep (validated v2 at optimum)
Tested 4 lookbacks × 3 top-N values × 2 windows = 24 configs
(`scripts/momentum/mono_factor_sweep.py`). From `var/momentum/mono_factor_sweep.json`:

In-sample CAGR (excerpts verified from JSON):
- `12-1_top30`: +21.34%, closed 1206
- `12-1_top50`: +21.00%, closed 1925 (= v2)
- `12-1_top75`: +18.29%, closed 2736

Per `memory/momentum_v2_verdict.md`:

| Lookback | top-30 IS | top-50 IS | top-75 IS | top-30 HO | top-50 HO | top-75 HO |
|---|---:|---:|---:|---:|---:|---:|
| 12-1 | +21.3% | +21.0% | +18.3% | +18.5% | +27.5% | +26.1% |
| 9-1 | -9.9% | -6.3% | -3.2% | +2.6% | +3.2% | +12.0% |
| 6-1 | +18.5% | +16.6% | +16.4% | -23.2% | -11.6% | -1.3% |
| 3-1 | +26.7% | +22.5% | +102.1% | -25.6% | -18.7% | -12.7% |

Zero configurations beat v2 (12-1, top-50, monthly) on BOTH windows.
3-1 top-75 in-sample +102.1% was a 2017-pump artifact; held-out -12.7%
confirms it.

### Attempt 6 — XBRL quality v2 (8-component) sleeve (FAILED combination)
File: `trading_bot/factors/quality_xbrl_v2.py`. Composite:
z(ROE) + z(OM) + z(FCF/Assets) + z(CurrentRatio) + z(Persistence) - z(D/E)
- z(AssetGrowth) - z(Dilution). Uses `cutoff_now` and `cutoff_1y` for
year-ago comparisons.

From `memory/sleeves_verdict.md`: standalone +7.4%/yr in-sample,
+13.0%/yr held-out (modestly stronger than v1). Combined with momentum:
still underperforms mom_v2 solo on both windows. Same pattern.

---

## Phase 2e — Closing experiments (2026-05-27)

**Source:** file timestamps, JSON result content, `memory/sleeves_verdict.md`
(quality standalone section), `memory/restricted_universes_verdict.md`.

### Test A — quality_xbrl_v2 STANDALONE (2026-05-27 12:53–12:59)
Files:
- `scripts/momentum/test_quality_standalone.py`  2026-05-27 12:53
- `var/momentum/quality_standalone_test.json`    2026-05-27 12:59
- `var/quality_standalone.out`                   2026-05-27 12:59

Results (verified from `quality_standalone_test.json`, all 8 configs run):

In-sample (top-N × CAGR / Sharpe / max DD):
- top-25:  +4.62%/yr / +0.245 / -36.2%
- top-50:  +5.75%/yr / +0.277 / -30.2%
- top-75:  +7.24%/yr / +0.352 / -30.4%
- top-100: +7.47%/yr / +0.358 / -28.5%

Held-out (top-N × CAGR / Sharpe / max DD):
- top-25:  +14.27%/yr / +0.610 / -20.8%
- top-50:  +13.59%/yr / +0.603 / -19.7%
- top-75:  +14.02%/yr / +0.812 / -20.1%
- top-100: +13.59%/yr / +0.857 / -20.4%

Benchmarks (in-sample / held-out total %): SPY 171.9/56.2, RSP 130.0/33.7,
IWM 90.5/42.8.

**Verdict logged in `memory/sleeves_verdict.md`:** NOT DEPLOYABLE as parallel
strategy. In-sample all configs underperform all benchmarks. Held-out
top-100 +13.6%/yr beats RSP +13.3% by 0.3pp (noise) but loses to SPY +21%,
IWM +16.5%, mom_v2 +26.5%. Concentration finding: top-100 wins on BOTH return
and Sharpe for quality (opposite of momentum, which wants top-50).

### Test B — Restricted universes (2026-05-27 13:27–13:40)
Files:
- `scripts/momentum/warm_sectors.py`              2026-05-27 13:27
- `scripts/momentum/test_restricted_universes.py` 2026-05-27 13:27
- `var/warm_sectors.out`                          2026-05-27 13:37 (1,491 sectors / 1,500 attempted)
- `var/momentum/restricted_universes_test.json`   2026-05-27 13:40
- `var/restricted_universes.out`                  2026-05-27 13:40

Results (verified from `restricted_universes_test.json`):

In-sample 2015-2023 (9 yr):
- top500   (univ size 500):  total +238.6%, CAGR +14.52%/yr, Sharpe +0.572, closed 1439
- top1000  (univ size 1000): total +318.0%, CAGR +17.23%/yr, Sharpe +0.627, closed 1552
- ex_tech  (univ size 5617): total +376.8%, CAGR +18.96%/yr, Sharpe +0.186, closed 1917
- mom_v2 default reference: +21.0%/yr (still wins in-sample)

Held-out 2024-2026 (2.3 yr):
- top500:   total +258.6%, CAGR +73.00%/yr, Sharpe +1.362, closed 338
- top1000:  total +240.5%, CAGR +69.19%/yr, Sharpe +1.313, closed 364
- ex_tech:  total +36.4%,  CAGR +14.26%/yr, Sharpe +0.581, closed 531
- mom_v2 default reference: +26.5%/yr

**Verdict logged in `memory/restricted_universes_verdict.md`:** Held-out
+73%/yr is survivorship-biased. The `_top_n_by_marketcap()` query in
`test_restricted_universes.py:40-49` reads a SINGLE marketCap snapshot
(2026 value) applied across all rebalances 2015→2026. Two biases:
forward-looking inclusion (NVDA grew into top500 — letting 2015 backtest
pick it because we know it becomes $3T) and survivorship (actual 2015
top500 contained Lehman-era survivors, GE pre-split, Sears, oil names
that collapsed — none in 2026 snapshot).

In-sample LOSS (-2 to -6 pp/yr vs mom_v2) is the trustworthy signal:
restriction removes momentum's small-cap tail where premium lives.
Held-out WIN is the bias paying out maximally during today's winners'
actual winning period.

Discarded; mom_v2 default universe remains baseline.

### Test C — mom_quality_screen filter (2026-05-27 13:38–14:12)
Files:
- `trading_bot/factors/mom_quality_screen.py`  2026-05-27 13:38
- `scripts/momentum/run_sleeves.py` (modified) 2026-05-27 13:38 (added
  quality, quality_xbrl, quality_xbrl_v2, mom_quality_screen to SLEEVE_REGISTRY)
- `scripts/momentum/test_quality_screen.py`    2026-05-27 13:41
- `var/momentum/quality_screen_test.json`      2026-05-27 14:12
- `var/quality_screen.out`                     2026-05-27 14:12

Algorithm (from `trading_bot/factors/mom_quality_screen.py`):
1. Rank universe by momentum, take top-200
2. Compute quality_xbrl_v2 score for all tickers
3. Keep only mom-top-200 picks that have quality score ≥ median
4. Return them ordered by momentum score

Results (verified from `quality_screen_test.json`):

| window | total | CAGR | Sharpe | closed |
|---|---:|---:|---:|---:|
| in_sample | +86.42% | +7.17%/yr | +0.251 | 877 |
| holdout | +75.67% | +27.36%/yr | +1.037 | 323 |

vs mom_v2:
| window | delta CAGR |
|---|---:|
| in_sample | **−13.83 pp/yr** |
| holdout | +0.89 pp/yr (noise) |

**Verdict logged in `memory/sleeves_verdict.md` attempt 7:** screen cuts
~83% of mom-top-200 picks (only ~34 names pass median quality per smoke
test). Cuts include the small-cap moonshots where mom's premium lives.
Held-out "win" is regime accident (2024-26 mega-caps led anyway). 7th
multi-factor failure in a row, same mechanism as the prior 6.

### Note on test failures during launch (2026-05-27 ~14:05)
First two background launches of `test_quality_screen.py` failed with
exit code 1:
- Attempt 1 (id `b9vaa5tva`): bash error `cd: too many arguments` (used
  `cd /d` which is cmd.exe syntax, not bash)
- Attempt 2 (id `bqbpj6yf9`): `ModuleNotFoundError: No module named 'yfinance'`
  — bash was using system Python 3.14 (`C:\Users\.../AppData/Local/Python/
  pythoncore-3.14-64/python.exe`) instead of project venv

Resolution: invoke `.venv/Scripts/python.exe` directly. Attempt 3 (id
`bk3he9nqf`) completed successfully.

---

## Phase 3 — Consolidation (2026-05-27 afternoon)

### Files created
- `docs/state_2026-05-27.md` — 200-line consolidation snapshot (working
  strategy, ruled-out experiments, infrastructure inventory, paper-trade
  plumbing gaps, open research questions, candidate next factors)
- `docs/record_2026-05-27.md` — this file (**renamed 2026-06-30 to
  `docs/Project Record — Full Chronological History.md`**, same file, content
  unchanged — see Appendix AN)
- `HANDOFF.md` — updated from 2026-05-25 baseline version to current state

### Database verified state (at write time)
Tables in `var/trading.db`:
- `price_cache`: 35,667,657 rows
- `xbrl_facts`: 4,819,633 rows
- `fundamentals_cache`: 46,824 rows
- `sectors_cache`: 1,493 rows
- `signals`: 2,326,932 rows (legacy Form 4)
- `positions`: 359 rows
- `portfolio_state`: 1 row

### XBRL concepts in `xbrl_facts` (verified by query)
16 concepts, with ticker coverage:
- Assets (4182), NetCashProvidedByUsedInOperatingActivities (4174),
  NetIncomeLoss (4157), StockholdersEquity (4094),
  CashAndCashEquivalentsAtCarryingValue (4019),
  PropertyPlantAndEquipmentNet (3717), OperatingIncomeLoss (3517),
  AssetsCurrent (3416), LiabilitiesCurrent (3409),
  PaymentsToAcquirePropertyPlantAndEquipment (3403), LongTermDebt (2794),
  Revenues (2663), RevenueFromContractWithCustomerExcludingAssessedTax (2582),
  LongTermDebtNoncurrent (2136), GrossProfit (2070), LongTermDebtCurrent (2008)

### Memory files updated
- `memory/MEMORY.md` — added line for `restricted_universes_verdict.md`;
  updated line for `sleeves_verdict.md` to reflect 7 failures
- `memory/restricted_universes_verdict.md` — created
- `memory/sleeves_verdict.md` — appended attempt 7 (mom_quality_screen)

### Decision pending
User selected "option 4 (consolidate) + option 3 (try new factor family)"
from the 4 options presented. Option 4 complete (this record + state doc +
HANDOFF). Option 3 candidate: accruals factor (Sloan 1996), all required
XBRL concepts already in `xbrl_facts`. Build cost ~1 hr. Awaiting go/no-go.

---

## Summary timeline (verified anchor points)

| Date | Event | Evidence |
|---|---|---|
| 2026-04-25 | Project briefed, congress data deferred, age constraint logged | memory files originSession `767c5c7c-...` |
| 2026-04-25 → 05-06 | Form 4 ingest + 5-yr price-cache backfill | var/backfill_*.out, var/warm_*.out timestamps |
| 2026-05-22 | Form 4 verdict: no edge | memory/form4_verdict.md |
| 2026-05-25 | Momentum v1 baseline (top-100) | memory/momentum_baseline.md + smoke JSON timestamps |
| 2026-05-25 | Naive composite (mom+lowvol) attempt 1: FAILED | memory/momentum_baseline.md |
| 2026-05-26 | Sleeve attempts 2-3: FAILED | sleeves JSON 2026-05-26 |
| 2026-05-26 | Momentum v2 frozen (top-50) + regression tests | momentum_v2.py:1, test_strategies.py:36 |
| 2026-05-26 | yfinance-quality attempt 4: lookahead-biased | memory/sleeves_verdict.md, var/sleeves_mom_quality.out |
| 2026-05-26 → 27 | XBRL pipeline warmed (v1 + v2 expand) | warm_xbrl.out 05-27 00:04, warm_xbrl_v2.out 05-27 02:30 |
| 2026-05-27 02:02 | Mono-factor sweep: no config beats v2 | var/momentum/mono_factor_sweep.json |
| 2026-05-27 02:35 | XBRL quality v2 sleeve attempt 6: FAILED | var/sleeves_xbrl_v2_chain.out |
| 2026-05-27 12:59 | Quality v2 standalone: not deployable | var/momentum/quality_standalone_test.json |
| 2026-05-27 13:40 | Restricted universes: survivorship-biased | var/momentum/restricted_universes_test.json |
| 2026-05-27 14:12 | mom_quality_screen attempt 7: FAILED | var/momentum/quality_screen_test.json |
| 2026-05-27 (after) | Consolidation: state doc + record + HANDOFF | this file |

## What's not in this record (honest gaps)

- **Pre-2026-04-25 history**: the initial scoping conversation/brief.
  Memory files don't capture it directly; only the decisions that came out.
- **Some Form 4 era detail**: there are ~30 `var/sim_r*.out` and `var/multi_*.out`
  files between 2026-04-28 and 2026-05-05 representing intermediate optimizer
  runs. They're recoverable but not individually narrated here — `memory/
  form4_verdict.md` summarized the conclusion (4 diverse configs at Sharpe ≈ 0)
  which is what mattered.
- **Exact backfill ticker counts at each milestone**: the `var/backfill_*.out`
  files would show this but aren't read line-by-line in this record.
- **Conversations / decision discussions**: this record covers WHAT was built
  and WHAT was learned. The reasoning conversations live in the session
  transcripts at `~/.claude/projects/D--ClaudeCode-Trading/*.jsonl`.

---

# Appendix A — Detailed Phase 1 history (Form 4 era) (2026-04-25 to 2026-05-22)

> **Source attribution**: This appendix was reconstructed from a separate
> evidence base than the main record above — (a) tuning-history comments
> embedded in `trading_bot/profiles.py` (current file retains R7 and R9
> comments verbatim; R1-R6 numbers cited below were captured from earlier
> revisions of the same file in prior sessions), (b) the project's
> `MEMORY.md` notes, (c) `multi_backtest.py` / `backtest.py` / `web.py`
> contents. Verified at write time: `profiles.py` (2026-05-06 21:43),
> `multi_backtest.py` (2026-05-07 21:06), `dashboard/web.py` (2026-05-26
> 02:27), `maintenance/flag_co_filings.py` (2026-05-02 17:14),
> `config.py` (2026-05-12 13:38) all exist. The R7 and R9 narrative is
> verifiable today; the R1-R6 numbers depend on prior-session memory.

## A.1 — Initial Form 4 design

- SEC EDGAR Form 4 polling → SQLite `signals` table
- Cluster detection (`clusters.py`): tickers with N+ distinct insiders buying
  within a window
- Scoring (`scorer.py`): 0-9 composite score with components for cluster size,
  CEO/CFO presence, dollar value, etc. Joint-filer collapse via
  `suspect_co_filing` to avoid amplification from related legal entities.
- Execution (`runner.py` → `broker.py` → `portfolio.py`): paper-trade only;
  position sizing as % of portfolio; sector cap = 20%.
- Monitor (`monitor.py`): stop-loss, take-profit, signal-reversal, time-exit
  triggers. Later added breakeven trigger and trailing-stop.
- Walk-forward backtest (`backtest.py`) wipes positions + portfolio_state
  before each run.
- Three risk profiles (`profiles.py`): conservative / normal / aggressive.
  Switched in/out via `use_profile()` context manager.
- Multi-profile sequential runs (`multi_backtest.py`): runs all 3 profiles
  on the same date range, archives results.
- User constraint: user is 17 → paper-trade only, no live broker until 18.
- Strategy plan: paper-trade 3+ months before considering live.

## A.2 — Tuning iterations on NORMAL profile (2026-04-28, pre-cost-fix)

From `profiles.py` comments (earlier revision):
- **v1**: BE=6, trail=15/7 → **+9.59%** (legacy was +12.29%; trail clipped winners)
- **v2**: BE=6, trail=22/10 → **+3.08%** (BE fired 16/50, scratched recoverers)
- **v3**: BE=10, trail=22/10 → **+1.78%** (mid-range exits steal TP wins)
- **v4**: BE=0, trail=35/10 → **+12.29%** (matches legacy; LP machinery inert)
- **v5**: threshold 5→4, TP 30→40, sizes 5/10→6/12 → **+1.63%**, 13 closes (cash starvation)
- **v6**: kept ONLY threshold=4 from v5 → **+8.14%** (vs +12.29%); score=4 entries
  net-negative AND displace later score=5+ arrivals. Reverted to v4.

## A.3 — Tuning iterations on AGGRESSIVE profile (2026-04-28, pre-cost-fix)

From `profiles.py` comments (earlier revision):
- **v1**: BE=8, trail=25/12 → **+17.01%** (vs legacy +20.76%; median win +42.4→+7.2%)
- **v2**: BE=8, trail=50/20 → **+11.99%** (BE fired 9/22; median win +5.6%)
- **v3**: BE=0, trail=35/15 → **+18.24%** (trail never fired)
- **v4**: identical to v3 → **+18.24%** (locked in for that window)
- **v5**: HC 7→6, TP 40→55, trail off → **−1.18%** (TP=55 starved cash)
- **v6**: kept ONLY HC=6 → **+9.81%** (vs +18.24%); score=6 doesn't deserve
  15% sizing tier. Reverted to v4.

## A.4 — R3: post realistic-cost fix (2026-04-30)

- Cost model fixed (slippage/commission). v4 baseline showed normal **−15.49%**
  (only 8 closes) and aggressive **−18.18%** (9 closes).
- Root cause: 10% sizing fills the portfolio fast → `time_60d` gap-down exits dominate.
- Fix: add BE/trail to normal and aggressive (matching conservative) to recycle cash.

## A.5 — R6 → R7 (2026-04-30)

R6 changes that REGRESSED vs R5 (verified from current `profiles.py:66-70, 99-102, 132-138`):
- **Conservative**: threshold 8→9, time_exit 90→120 → **−5.93%** (vs R5 +1.26%)
  Reason: score=9 requires cluster≥3 AND CEO/CFO AND $500K — too rare.
- **Normal**: HC=9 → **−5.58%** (vs R5 +4.83%); smaller sizing hurt score=8 trades.
- **Aggressive**: TP=70/SL=−20 → **−23.14%**; only 11% of closes reached TP=70.

R7 = revert to R5 settings. Aggressive identity reframed:
same exit discipline as normal, but bigger position sizes (7/15 vs 5/10).
The aggressive lever is now *capital allocation*, not *rule looseness*.

R7 baseline (locked-in): cons **+1.26%**, norm **+4.83%**, agg **−8.14%**.

## A.6 — R8: 50-day MA trend filter

Plan: `~/.claude/plans/rosy-petting-lake.md`.

**Hypothesis:** dominant failure mode was wide stop-loss tail — insider buys
are often "value traps" where insider thinks stock is cheap but market knows
something. Stocks in extended downtrends keep falling.

**Single-lever change:** reject any insider-buy entry where next-open close is
below its 50-day moving average. No new score components. No new tunables.

**"Lazy" implementation:** don't pre-warm; let `price_cache` populate on first hit.

Files changed:
- `config.py`: `TREND_FILTER_ENABLED=True`, `TREND_FILTER_WINDOW=50`
- `market_data.py`: `is_above_ma(ticker, as_of, window=50) -> bool | None`,
  cached under `kind = "above_ma_50"` in `price_cache`
- `runner.py`: trend check between sector-cap and `broker.place_buy()`.
  `None` (no data) → pass (don't penalize for yfinance flakiness).

Order matters: trend check AFTER cheap DB/cash/sector checks (don't pay API
call for already-rejected trades), BEFORE `place_buy()` (don't waste fill lookup).

No profile changes in R8 — isolate the filter's effect against R7.

## A.7 — Infrastructure added in the R8/R9 session

### Backfill 429 retry fix (`sources/edgar.py`)
- Bug: `_get_with_retry` only retried 5xx; 429s threw immediately.
- Fix: also retry on 429 with `Retry-After` header support.

### Joint-filer dedup (`maintenance/flag_co_filings.py`) — NEW FILE
- Form 4 sometimes has same economic transaction reported by multiple related
  legal entities (fund GP + LP + advisor + sub-funds) — same accession,
  ticker, date, code, shares but different filer_cik.
- Added `co_filing_group_id TEXT` column to `signals` + index.
- Idempotent script tags 2+ row groups with `cof-{min_id}`.
- Tagged **221,850 rows** across **50,886 joint-filer groups**.
- No scoring change needed — `clusters.py` already handled this via
  `suspect_co_filing` collapse.

### 5-year EDGAR backfill
- Completed: 2021-04-30 → 2026-04-24, **689,912 signals**.

### Web dashboard additions (`dashboard/web.py`)
- Streamlit at http://localhost:8501
- Tabs: Overview, Conservative, Normal, Aggressive, Compare runs, Backfill, Simulation
- Backfill tab: Start/Stop buttons, monthly-coverage bar chart
  (green/amber/red by signal density), PID file management
- Simulation tab: Start/Stop buttons, live progress bar parsing 5%-interval
  log lines, live tail
- 5%-interval progress logging added to `backtest.py`:
  `"backtest progress: N/M days (P%)  cur=YYYY-MM-DD"`
  Same format as backfill so dashboard uses one grep
- Per-profile progress logging added to `multi_backtest.py`:
  `"=== Profile N/3: {name} (run_id=...) ==="`

### Versioned run archive
- `var/sim_archive/runs/{run_id}/` per multi-backtest run
- Each contains `meta.json` + `{conservative,normal,aggressive}.json`
- `meta.json` captures: run_id, started_at, elapsed_seconds, since, until,
  starting_cash, per-profile dataclass dump, summary {pnl_pct, closed, open}
- Top-level `{profile}.json` still written for back-compat with terminal dash

### `--label` CLI argument
- `multi-backtest --label "R9-50DMA-tuned"` stores label in `meta.json["label"]`
- Dashboard run selector + Compare tab now show label instead of timestamp
- Falls back to raw run_id if no label provided
- Simulation tab has a free-text "Run label" field

## A.8 — R9 profile tuning (2026-05-05)

**Hypothesis:** with R8's MA filter screening downtrenders, entries are higher
quality → can tighten SL (less drawdown room needed) and loosen score cutoff
on conservative (let the filter do quality work).

(All values verified against current `profiles.py:75-117, 145-154`.)

**CONSERVATIVE:**
- `trade_threshold` 8 → 7 (filter handles quality cutoff)
- `take_profit_pct` 30 → 40 (trend-followers run further)
- `breakeven_trigger` 8 → 10 (avoid premature scratch on small bounces)
- `trailing_trigger` 20 → 22 (consistency with BE)

**NORMAL:**
- `stop_loss_pct` −15 → −12 (filtered entries shouldn't fall far)
- `high_conv_threshold` 8 → 9 (focus 10% sizing on cleanest signals)

**AGGRESSIVE:**
- `stop_loss_pct` −15 → −12 (matches normal's R9 reasoning)
- `standard_position_pct` 7 → 8 (more capital on trend-confirmed entries)

R9 sim launched: PID 1217, label "R9-50DMA-tuned",
range 2021-05-01 → 2026-04-24, log `var/sim_r9_full.out`
(verified file exists, mtime 2026-05-05 16:29).

## A.9 — R10/R11 — vol-stop and regime-conditional time exits

Not narrated in the source content above, but the current `profiles.py:52-61,
85-94, 118-128, 155-166` documents R11 (Tier 1.3) additions to all three
profiles:
- `vol_stop_atr_mult` (Conservative 2.0, Normal 2.5, Aggressive 3.0) with
  per-profile `vol_stop_min_pct` and `vol_stop_max_pct` bands
- `time_exit_uptrend_mult` and `time_exit_downtrend_mult` for
  regime-conditional holding period scaling

R11 comment on Normal: "Goal: stop 0% of n=22 stops cohort from R10 firing
on benign noise; the actual losers will still trigger because their TR
blew past 2.5σ entering the trade." This implies R10 was a prior round
involving stop-firing analysis. Detail beyond this is not in the current
file.

## A.10 — Gaps in the Phase 1 detail

(From the source content's explicit "what I don't have evidence for" section)
- R1–R5 exact tuning results (only R5 baseline numbers and the R6 regression
  notes are in the in-code history accessible today).
- Initial scoring weights / `scorer.py` iteration history.
- The exact transition from Form 4 to factor portfolios (no R8/R9-era session
  activity on momentum/sleeves code).
- The R9 sim's final results (it was still running at end of the R8/R9 session;
  `var/sim_r9_full.out` exists but its final outcome is not summarized here).
- Anything between R9 (2026-05-05) and the Form 4 closure (2026-05-22) — the
  17-day gap during which the strategy was decisively refuted.

The Form 4 era's final verdict (`memory/form4_verdict.md`, 2026-05-22) records
that 4 diverse trading configs all landed at mean yearly Sharpe ≈ 0 across
2015-2024 walk-forward, and held-out trial-09 returned −7.54% in May 2025→2026
when SPY did +29%. The R10/R11 vol-stop additions visible in `profiles.py` were
presumably part of the final tuning push during this 17-day gap, but no
session-grounded narrative for them exists in the materials available at this
write time.


# Appendix B - Paper trade + Data audit + Overlay re-tests (2026-05-27 to 2026-05-28)

Picks up where the main timeline ends (paper-trade deployment) and runs
through the data audit that invalidated most prior in-sample results.

## B.1 - 2026-05-27 ~23:50 - User observation triggers overlay research
User noted: "momentum v2 seems to be good at buying low but relatively bad
at selling before the dip (~30k drop from feb 15 to mar 11 and oct 30 to
nov 11 (both 2025) during the v2 holdout)". Asked to try stop-loss.

## B.2 - 2026-05-27 ~23:55 - Stop-loss sweep (Attempt 12, FAILED)
Built `_check_stops` in `factor_backtest.py`, added optional
`stop_loss_pct` param. Frozen regression tests still passed at d=0.0000pp
(default None preserves spec). Sweep: stop in {-10, -15, -20, -25%} x 2
windows = 8 runs.

Result on (then) baseline (assumed +21% CAGR / -36% DD in-sample):
- All 4 stop levels showed in-sample max DD blowing up to ~-87% (51pp regression)
- Held-out looked attractive (stop15: +2.3pp CAGR, +3.2pp DD)
- Verdict at the time: REJECTED - in-sample -51pp DD regression is a hard kill.
  Documented in `memory/sleeves_verdict.md` as Attempt 12.

## B.3 - 2026-05-28 ~00:00 - User asks to explore Option C (stops + reentry)
After discussion of why Option B (refill slot from ranker) would not work,
user agreed Option C (re-enter SAME ticker after rebound) was the cleanest
test. Built `_stopped_watch` state + `reentry_buffer` param.

## B.4 - 2026-05-28 ~00:10 - Stops + reentry sweep (Attempt 13, FAILED)
Sweep: stop=-15% x reentry_buffer in {0, 2, 5%} x 2 windows = 6 runs.
Result: DD identical to plain stops (~-87%), CAGR MONOTONICALLY DEGRADES
with buffer size (-6.2/-7.4/-7.9pp at buf 0/2/5%).
Predicted Option C would help; was wrong. Re-entries fire during rebounds
buying recovered prices, next chop catches them at -15% from higher entry,
losses compound. Documented as Attempt 13.

## B.5 - 2026-05-28 ~00:15 - Discussion of preemptive alternatives
With reactive stops failed twice, user asked about preemptive risk control.
Discussed trend filter (SPY > 200-DMA) and vol-target (Moreira & Muir 2017).

## B.6 - 2026-05-28 ~00:20 - Preemptive overlay sweep (trend + voltgt)
Built `make_trend_filtered_ranker` (wraps rank_fn, returns [] when SPY < SMA)
and `make_vol_target_scaler` (returns position_scale_fn from target_vol).
Added `position_scale_fn` param to `run_factor_backtest`. Frozen spec passed.

Sweep: 4 configs (trend200, voltgt16, voltgt20, combined) x 2 windows = 8 runs.
Apparent result: voltgt looked like a WIN - 14x Sharpe improvement
(+0.016 -> +0.205) with minimal CAGR cost. Trend filter showed -6pp in-sample,
-20pp held-out.

## B.7 - 2026-05-28 ~00:30 - Cross-test pattern recognition -> audit triggered
Noticed ALL 4 overlays (stops, stops+reentry, voltgt, trend) showed
in-sample max DD around -87%. Too consistent to be coincidence. Computed
baseline mom_v2's actual in-sample max DD from archived equity curve:
**-87.35% with "peak" $1,295,572 in Aug 2017 reverting in 6 days.**

Identified: the peak was a data artifact - equity curve had spikes to
$627K on isolated days while real value was ~$80K.

## B.8 - 2026-05-28 ~00:45 - Root cause: yfinance data corruption
Investigated price_cache for spike-day tickers. Found:
- JAGX at $8.4 billion per share (real: ~$3)
- WHLR at $7.4 billion (real: ~$1.14)
- ITC at $14,200 every Friday (real: ~$30)
- TNB at $13,000 every Friday (real: ~$1.75)
- FOOD at $13,935 (real: ~$0.32)

Pattern: ~477 spike-rows on Fridays specifically. yfinance had a
years-long Friday data anomaly affecting acquired/delisted tickers.

Also identified Category 2 corruption: unadjusted reverse splits causing
continuously inflated historical closes (WKHS: $1,950-$9,210 in 2018-2023,
real split-adjusted price ~$3 today). yfinance `auto_adjust=True` does not
fix these - their split DB is broken at the source.

## B.9 - 2026-05-28 ~01:00 - Spike cleanup applied
Built `scripts/data_audit/find_price_spikes.py`. Uses rolling-median check
(price > 10x median of 5 neighbors each side = spike). Found 2,017 spike
rows across 149 tickers. DB backed up (`var/trades.db.bak_pre_spike_cleanup`,
4.6 GB). Nulled spike rows so MTM falls back to entry_price.

## B.10 - 2026-05-28 ~01:30 - First re-run revealed in-sample collapse
Re-ran mom_v2 in-sample baseline. Result: total return **dropped from +455%
to -22.88%**. The strategy was earning phantom MTM gains from data
corruption. Held-out unchanged (+27%) - that period had clean data.

## B.11 - 2026-05-28 ~02:00 - Universe-level consistency filter
Spike cleanup was not enough - continuous unadjusted data still passed the
$5 min_price filter. Built `universe.MAX_HIST_RATIO=100`: rejects tickers
whose historical close is > 100x their current stable price (median of
last 60 closes). Catches ARSC ($8000 historical -> $0.10 current) and
similar reverse-split-corruption cases.

Re-ran mom_v2 with filter: in-sample +27.3% CAGR / -55% DD (real numbers).
Held-out +80.4% CAGR / -34% DD (still strong, slight improvement).

## B.12 - 2026-05-28 ~02:30 - Frozen spec re-baselined
Old expected values in `test_strategies.py` were captured on contaminated
data. Updated:
- momentum_v1/2023_Q4: 12.6237% -> **14.4673%** (67 -> 64 trades)
- momentum_v2/2023_Q4: 12.2794% -> **14.6655%** (37 -> 36 trades)
- 2025_H1 values unchanged (held-out window already clean)
Both strategies now pass at d=0.0000pp.

## B.13 - 2026-05-28 ~03:00 - TC sensitivity sweep
Question: how robust is the strategy to transaction costs? Default 5bps
half-spread is optimistic for small/mid-cap universe. Swept 5/10/15/20/30 bps.

Result: held-out CAGR is **robust** (+28.81% -> +26.42% across 5-30 bps).
In-sample is fragile (+2.72% -> +0.73%) but already marginal at any TC level.
At realistic 15-20 bps: held-out still +27-28%/yr.

## B.14 - 2026-05-28 ~04:00 - Vol-target deep sweep on CLEAN data
Re-ran the original vol-target test now that baseline is not contaminated.
Sweep: 7 targets (12-25%) x 2 windows = 14 runs.

Result: **the prior "14x Sharpe improvement" was a data artifact.** On clean
data, baseline Sharpe is already +0.167 / +0.903. Vol-target across all
targets produces same-or-slightly-worse Sharpe. Tradeoff is minimal:
voltgt16 gives +3.3pp DD reduction for -0.4pp CAGR cost. Not worth complexity.

## B.15 - 2026-05-28 ~04:30 - Archive regeneration
Re-ran `scripts/momentum/archive_v1_v2.py` to regenerate the dashboard's
backtest archive JSONs with clean data:
- mom_v1 in-sample: +339% -> **+51.4%** total
- mom_v2 in-sample: +455% -> **+27.3%** total
- Held-out values essentially unchanged (clean already)

Moved old contaminated archives to `var/momentum/sleeves/archive_pre_audit/`.

## B.16 - 2026-05-28 ~05:00 - v1 vs v2 head-to-head on clean data
Computed full risk/return profile both windows. CLEAN REGIME SPLIT:
- **In-sample (9 yr): mom_v1 wins on every metric** (CAGR +4.72 vs +2.72,
  Sharpe +0.210 vs +0.167, DD -48.9 vs -55.3, Calmar +0.096 vs +0.049)
- **Held-out (2.4 yr): mom_v2 wins on every metric** (CAGR +28.81 vs +22.08,
  Sharpe +0.903 vs +0.813, DD -33.86 vs -34.29, Calmar +0.851 vs +0.644)

In-sample contains 2021-23 momentum crash -> diversification (v1's 100 names) wins.
Held-out had no comparable crash -> concentration (v2's 50 names) captures upside.

## B.17 - 2026-05-28 ~05:25 - User decision: run both in parallel
User chose "Run both in parallel" from the strategy options. Initialized
mom_v1_paper with backdated as_of=2026-05-01 to match mom_v2's inception.
After 27 days both running:
- mom_v1_paper: $98,454.88 (-1.55%)
- mom_v2_paper: $96,977.34 (-3.02%)
- v1 leading by 1.5pp in first 27 days (diversification benefit appearing).

## B.18 - 2026-05-28 ~05:30 - Infrastructure: dual-sleeve scripts + dashboard
- `rebalance.bat`: now calls both v1 and v2 rebalance + MTM sequentially
- `daily.bat`: now MTMs both sleeves
- `dashboard/web.py`: paper-trade tab gets a strategy selector when >1 sleeve
- `paper_trading_ops.md`: updated for dual-sleeve operation
- `HANDOFF.md`: updated deployment status

## B.19 - 2026-05-28 ~11:57 - Dashboard bug fix
Streamlit reported `NameError: name 'DB_PATH' is not defined` in
render_paper_trading. My added code referenced DB_PATH at module scope
but the existing pattern imports it locally inside _load_paper_state.
Fixed by adding local import.

## B.20 - 2026-05-28 ~12:00 - Re-ran all overlay tests on clean data
User asked to verify prior verdicts hold on clean data. Updated baseline
references in test_mom_v2_stops.py, test_mom_v2_stops_reentry.py, and
test_mom_v2_preemptive.py. Ran all 22 backtests sequentially.

Result: **all prior conclusions stand directionally**:
- Stops: -4 to -6pp in-sample CAGR, marginal DD changes. Stop15 actually
  marginally helps held-out (+0.9pp CAGR, +3.2pp DD). Mixed/regime-dependent.
- Stops + reentry: monotonically degrades with buffer, strictly worse.
- Trend filter: -6.4pp in-sample, -21pp held-out - still a disaster.
- Vol-target 16-20%: -0.3 to -0.4pp CAGR, +0.7 to +3.3pp DD - marginal.

Most interesting change: stops are not the catastrophe they appeared to be
(the -87% DD was data artifact, real effect is ~-5pp CAGR). Still net reject.

## B.21 - 2026-05-28 ~12:15 - User asked about fine-tuning vol-target
Discussed: 7 targets already swept, looser targets do nothing in held-out
because SPY's 21-day vol rarely exceeded 20% in 2024-2026. Untested knobs:
portfolio-vol signal (instead of SPY), daily-check (instead of rebal-only),
shorter lookback (5-10d). Honest prediction: small improvements at best.
User did not opt to run the test.

## B.22 - 2026-05-28 ~12:25 - User requested record/state cadence
"For the docs/record and docs/state I want you to update them every
3 prompts to reflect the current state of the project. include date and
time stamps in the record." This Appendix B is the catch-up update; will
attempt to maintain cadence going forward within this session.


# Appendix C - Vol-target fine-tune + docs cadence hook (2026-05-28 late session)

Picks up from end of Appendix B. Covers the cadence-hook installation
and the final vol-target fine-tune sweep.

## C.1 - 2026-05-28 ~12:30 - Docs cadence hook installed
User requested every-3-prompts cadence for docs/record + docs/state with
date/time stamps. Built:
- `.claude/settings.json` - hooks config
- `.claude/hooks/check_docs_cadence.py` - increments counter on each
  UserPromptSubmit, emits `[DOCS_CADENCE]` reminder every 3rd prompt
- `.claude/cadence.json` - per-machine counter state (gitignored)
- `CLAUDE.md` - project rules including cadence + Karpathy guidelines

Verified hook works in isolation (`python check_docs_cadence.py` 3 times,
3rd run emits reminder). Counter reset to 0 after testing.

**Caveat**: hook requires Claude Code to reload settings.json. Until
restart, cadence is tracked manually.

## C.2 - 2026-05-28 ~17:00 - Vol-target fine-tune (for completeness)
User: "fine tune the vol-target for completeness".

Built `scripts/momentum/test_vol_target_finetune.py`:
- Pre-pass: run baseline mom_v2 over 2014-06 to 2026-05 to capture daily
  returns -> portfolio-vol lookup
- Sweep 6 configs: SPY-vol vs Portfolio-vol x lookback 10/21/60 days
- SPY at target 16%, Portfolio at target 25% (matches mom's ~1.5x SPY vol)
- 12 backtests total (~10 min)

### Results vs baseline (+2.72% in / +28.81% hold CAGR)

In-sample deltas (all negative or marginal):
- spy_10d_t16: -0.30pp CAGR, +2.39pp DD
- spy_21d_t16: -0.45pp CAGR, +3.29pp DD (the existing default)
- spy_60d_t16: -1.63pp CAGR, +1.50pp DD (worst SPY)
- port_10d_t25: -0.54pp CAGR, -0.49pp DD (portfolio-vol underperforms)
- port_21d_t25: -0.83pp CAGR, +2.03pp DD
- port_60d_t25: -1.45pp CAGR, +2.13pp DD

Held-out deltas (one tiny positive, others negative):
- spy_10d_t16: -1.18pp CAGR
- spy_21d_t16: -0.42pp CAGR
- **spy_60d_t16: +0.73pp CAGR, +0.04pp DD, +0.024 Sharpe** (only positive)
- port_10d_t25: -2.63pp CAGR, +3.44pp DD
- port_21d_t25: -1.50pp CAGR, +4.46pp DD
- port_60d_t25: -1.19pp CAGR, +3.33pp DD

### Verdict
**No variant beats baseline on BOTH windows simultaneously.** Most
interesting finding: portfolio-vol gives larger DD reduction (3-4pp on
held-out) but at HIGHER CAGR cost - net Sharpe goes DOWN. The "more
accurate signal" hypothesis was wrong; vol-target's structural trade-off
(scale down = miss returns) dominates signal quality.

Vol-target line of research **definitively closed**. Memory updated
(`memory/data_audit_2026-05-28.md`). Same conclusion as the simpler
sweep: mom_v2 baseline (no overlay) remains the right configuration.

## C.3 - 2026-05-28 ~17:30 - User asks about other strategies
"lets look at some other strategies" - explored options for new alpha
research. Discussion items: long-short market-neutral, sector momentum,
value via XBRL, low-vol / idiosyncratic vol. Recommendations pending
user direction.


# Appendix D - Long-short momentum research arc (2026-05-28 evening)

Builds on Appendix C. Covers vol-target fine-tune closure + the long-short
momentum exploration (Attempts 15 + 16 in sleeves_verdict).

## D.1 - 2026-05-28 ~18:00 - Vol-target fine-tune closed
Six-config sweep (SPY-vol vs Portfolio-vol x 10/21/60d lookbacks).
Best variant `spy_60d_t16` only barely positive on held-out (+0.73pp CAGR)
and worst on in-sample (-1.63pp). No variant beats baseline on both windows.
Portfolio-vol gives larger DD reduction (3-4pp) but at higher CAGR cost.
Vol-target research line definitively closed. See memory/data_audit_2026-05-28.md.

## D.2 - 2026-05-28 ~18:30 - User: "lets look at some other strategies"
Surveyed: long-short, sector momentum, value+momentum (XBRL), low-vol,
PEAD. Recommended long-short market-neutral momentum as best
learning-per-hour. User selected.

## D.3 - 2026-05-28 ~19:00 - Long-short momentum built (Attempt 15)
Built `scripts/momentum/test_long_short_momentum.py`. Standalone (no
DB pollution): in-memory positions dict, dollar-neutral, 2x gross on
$100K. Top-50 long + bottom-50 short by same 12-1 momentum signal.
Borrow fee applied daily on short notional.

### Results: textbook regime split
- **In-sample (2015-2023): BUST.** All borrow levels (1/2/5%) ended
  with NEGATIVE NAV. 2022 momentum crash + short squeeze on loser
  cohort wiped out all capital.
- **Held-out (2024-2026): BEST CAGR seen.** ls_borrow1: +46.99% CAGR,
  +1.063 Sharpe vs long-only +28.81/+0.903. Even at 5% borrow: +41.42%.
  Worse max DD (-51% vs -34%) due to leverage.

Classic Daniel & Moskowitz (2016) "Momentum Crashes" pattern reproduced.

### First-attempt bug
First run crashed JSON serialization because CAGR was complex
(negative_nav**(1/years)). Fixed: added bust detection, NaN handling,
custom JSON serializer for None CAGRs.

## D.4 - 2026-05-28 ~19:30 - User: "do a and then plan b"
Built A: vol-target-spread on long-short (Barroso & Santa-Clara 2015 fix).
Wrote out detailed plan for B (value+momentum via XBRL) without building.

## D.5 - 2026-05-28 ~20:00 - LS + vol-target-spread (Attempt 16)
Built `scripts/momentum/test_long_short_voltgt.py`. Tracks live daily
L-S spread returns in memory, computes 21-day realized vol, scales gross
exposure by `min(1, target / realized)`. Sweep target in {10, 12, 16%}.

### Results: HUGE held-out improvement, in-sample bust partially mitigated
- **In-sample**: still busts (NAV went negative ~-$30K then recovered
  to +$21-26K). 21-day lookback too slow for 2022 crash. Avg scale
  was 0.60-0.72 (reducing exposure but not enough fast enough).
- **Held-out**: best Sharpe + lowest DD of any strategy in the project:
  - ls_voltgt10: +35.20% CAGR, **+1.345 Sharpe**, -20.67% DD
  - ls_voltgt12: +37.75% CAGR, +1.337 Sharpe, -22.57% DD
  - ls_voltgt16: +41.12% CAGR, +1.305 Sharpe, -25.86% DD
  - vs long-only mom_v2 (+0.903 Sharpe, -33.86% DD): +0.40-0.44 Sharpe
    improvement, +8-13pp DD reduction, +6-12pp CAGR.

### Verdict
Held-out: VALIDATED. Largest Sharpe improvement seen in project.
In-sample: partial fix (didn't fully eliminate bust). To complete the
academic claim would need shorter lookback + lower target + hard cap.

**Deployment status**: research-only. User is 17, no margin account.
Long-short shorting microcaps not realistic to paper-trade. Bookmarked
for age 18+. End of long-short research arc.

## D.6 - 2026-05-28 ~20:30 - Cadence prompt #3 reached, docs updated
This Appendix D is the catch-up. State doc 2026-05-28 is still current
(no structural change: no deployment change, mom_v1_paper + mom_v2_paper
still running). Memory files updated for both Attempts 15 + 16.

Next decision point: build B (value+momentum) or pause research and let
paper trade accumulate data.


# Appendix E - Plan B: ROA + momentum cross-sectional combo (2026-05-28 evening cont'd)

Continues from Appendix D. User asked to "run phase 3" of plan B (value+momentum).

## E.1 - 2026-05-28 ~21:00 - Substitution decision
Plan B was canonical value+momentum (P/B + 12-1 momentum). Discovered
shares-outstanding data not cached (dei: namespace not warmed). Without
shares, can't compute P/B, P/E, EV/EBITDA. Options:
  (i) Warm dei: via EDGAR (~1hr setup)
  (ii) Substitute with a related fundamental factor using cached data

Chose (ii): substituted with ROA (Novy-Marx 2013 profitability). Same
spirit (fundamental factor uncorrelated with momentum). Uses
NetIncomeLoss (TTM) + Assets (PIT-lagged). Both already in xbrl_facts.

## E.2 - 2026-05-28 ~21:15 - Built ROA factor + Z-score combiner
- `trading_bot/factors/roa.py`: roa_score = NI_TTM / avg(Assets_now, Assets_1y).
  Filters: ni!=None, assets>0, |ratio|<=1 (sanity bound on data errors).
- `trading_bot/factors/mom_roa_zscore.py`: cross-sectional Z-score combo.
  Per rebal: compute mom + ROA scores, drop tickers missing either,
  Z-score each factor, combined = w_mom*Z_mom + w_roa*Z_roa. Z-scores
  (not percentile ranks) preserve magnitude information.

## E.3 - 2026-05-28 ~21:30 - Coarse sweep: FIRST WINNER
`scripts/momentum/test_mom_roa.py`: 4 weight configs (roa_solo, 5050,
7030, 3070) x 2 windows = 8 backtests, ~6 min.

### Results vs baseline mom_v2 (+2.72/+28.81 CAGR)

| Config | In CAGR | In Sharpe | Hold CAGR | Hold Sharpe | Verdict |
|---|---:|---:|---:|---:|---|
| roa_solo | +7.35% | +0.409 | +8.16% | +0.359 | only in-sample beat |
| mom_roa_5050 | +6.54% | +0.304 | +29.21% | +0.968 | beats baseline both |
| **mom_roa_7030** | +3.93% | +0.201 | **+36.08%** | **+1.098** | **BIG WIN both** |
| mom_roa_3070 | +5.64% | +0.244 | +13.14% | +0.594 | held-out fails |

mom_roa_7030 is the **first strategy in 16+ attempts** to beat mom_v2 on
BOTH windows on EVERY metric simultaneously:
- In-sample: +1.21pp CAGR, +0.034 Sharpe, +8.63pp DD
- Held-out: +7.27pp CAGR, +0.195 Sharpe, +2.95pp DD

The ROA standalone is a real but weak factor (+7.35%/+8.16% CAGR with low
Sharpe - profitability works but isn't a CAGR-driver). Combined with mom
at 70/30 weight is where the magic happens: keeps most of mom's directional
edge while ROA filters out the most-junk momentum picks.

## E.4 - 2026-05-28 ~21:45 - Refinement sweep launched
User: "yes" to proceed with refinement + TC sensitivity.

`scripts/momentum/test_mom_roa_refine.py`: 4 more weights (8020, 7525,
6535, 6040) x 2 windows = 8 backtests, ~5-6 min. Currently running
(PID bcxm0vtxd at 21:48).

Followup: TC sensitivity on the winning weight (5/15/25 bps half-spread)
to confirm it survives realistic costs. If still positive, deploy as
mom_roa_paper third paper-trade sleeve alongside mom_v1_paper and
mom_v2_paper.

## E.5 - Note on cadence
This is the docs update for prompt 3 of the second 3-prompt cycle. Hook
still not loaded by Claude Code; manually tracking. Counter reset
after this update.


# Appendix F - mom_roa_6535 deployment + new-data exploration begins (2026-05-28 late)

Continues from Appendix E. Plan B (substituted with ROA) produced the
first deployable winner; user now opens up to new data sources.

## F.1 - 2026-05-28 ~22:00 - Refinement sweep confirmed broad peak
`scripts/momentum/test_mom_roa_refine.py`: 4 more weights (8020, 7525,
6535, 6040). Held-out CAGR by weight: 8020:+33.4 / 7525:+36.2 /
7030:+36.1 / 6535:+36.5 / 6040:+37.0 / 5050:+29.2. Peak is BROAD around
60-70% mom weight - not overfit to a single tuning point.

## F.2 - 2026-05-28 ~22:15 - TC sensitivity on mom_roa_6535
`scripts/momentum/test_mom_roa_tc.py`: 5 TC levels x 2 windows = 10 runs.
RESULT: edge is CONSTANT across TC levels (+7.64pp held-out CAGR vs mom_v2
at every TC 5-25 bps). Means same turnover profile as mom_v2 - ROA changes
slowly, no excess churn. Robust to realistic small-cap trading costs.

## F.3 - 2026-05-28 ~22:30 - Deployed mom_roa_6535_paper as 3rd sleeve
Built:
- `trading_bot/strategies/mom_roa_6535.py` - frozen spec, locked 2026-05-28
  (params W_MOM=0.65, W_ROA=0.35, top_n=50, monthly, 5bps half)
- Modified `scripts/momentum/paper_rebalance.py` - new `_strategy_rank_fn()`
  dispatch dict maps strategy_name -> rank_fn
- Updated `rebalance.bat` + `daily.bat` to call all 3 sleeves
- Initialized portfolio with backdated as_of=2026-05-01 inception

27-day live comparison:
  - mom_v1_paper        $98,454.88 (-1.55%)
  - mom_v2_paper        $96,977.34 (-3.02%)
  - mom_roa_6535_paper  $99,848.12 (-0.15%)  <-- best so far

Picks differ meaningfully: mom_v2 picked speculative biotechs (IMNM, PRPO,
AMLX, SNSE); mom_roa_6535 picks profitable names (STX, MU, GLW, MKSI).
The ROA Z-score is filtering out negative-NI speculation rallies.

## F.4 - Memory + HANDOFF updated
- `memory/sleeves_verdict.md`: Attempt 17 documented (mom_roa_6535 WIN)
- `HANDOFF.md`: 3-sleeve deployment table, why-three rationale, both v1-v2
  regime split and mom_roa_6535 win

## F.5 - 2026-05-28 ~23:00 - User: "keep looking dont be afraid to need to use other data we dont have"
Opening up to new data sources. Considering options ranked by EV/effort:
- WARM dei:CommonStockSharesOutstanding -> canonical value+momentum
- VIX term structure regime detector (^VIX + ^VXV from yfinance)
- FINRA short-interest data for crowded-shorts avoidance
- Yahoo earnings calendar/surprise for PEAD-lite
- Form 4 insider cluster buys overlay (revisit closed Phase 1 with combo lens)
- FRED macro factors (yield curve inversion)
- Google Trends search interest

Picking next experiment. This Appendix F is docs catch-up for prompt 3
of 3-cycle.


# Appendix G - VIX regime test + 3-factor extension + PEAD launch (2026-05-28 night)

Continues from Appendix F. User opened up to new data sources.

## G.1 - 2026-05-28 ~23:00 - VIX term-structure regime filter test
NEW DATA: ^VIX and ^VIX3M from yfinance (3016 days, 2014-2026).

`scripts/momentum/test_vix_regime.py`: applies VIX/VIX3M ratio as a
position scaler on mom_v2 + mom_roa_6535. Three variants:
  - hard cutoff at 1.0 (canonical backwardation = stress = go to cash)
  - hard cutoff at 0.95 (more sensitive)
  - graded linear scale around 1.0

12 backtests run. Signal stats: VIX/VIX3M inverted only 7.7% of days
(median ratio 0.877). Signal triggers rarely.

### First-attempt bug
^VXV ticker was delisted (renamed to ^VIX3M by Cboe in 2017). First
fetch returned 0 rows. Updated to ^VIX3M, cleared empty cache, refetched.

### Results: virtually no effect on either strategy
- mom_v2 best variant (vix_grad_1.0 in-sample): +0.22pp CAGR -- noise
- mom_v2 held-out vix_hard_1.0: -0.10pp CAGR (signal rarely fires in 2024-26)
- mom_roa_6535 held-out vix_hard_1.0: +0.64pp CAGR (tiny win, within noise)
- vix_hard_0.95 (more sensitive): -5pp CAGR for +8pp DD reduction - bad trade

**Verdict**: VIX regime doesn't reliably catch the SPECIFIC drawdowns
that hurt momentum. Same lesson as trend filter: external regime signals
trigger on noise, miss slow crashes. Documented and closed.

## G.2 - 2026-05-28 ~23:30 - User: "do 1 and 2"
Two parallel experiments launched:

### Part 1: 3-factor combo (mom + ROA + accruals)
- New `trading_bot/factors/mom_roa_acc_zscore.py` (cross-sectional Z combo)
- New `scripts/momentum/test_mom_roa_acc.py`: 6 weight configs x 2 windows
- Tests if accruals as 3rd factor improves mom_roa_6535 winner
- Currently running (PID bgqucr168, ~6-8 min)

### Part 2: PEAD via yfinance earnings dates (uses new data)
- New `scripts/data_audit/fetch_earnings_dates.py`: bulk fetch via
  yf.Ticker.earnings_dates for ~3128 tickers
- Will cache to var/data_audit/earnings_dates_cache.json
- Currently running (PID b1sqd3u6i, ~30-50 min)
- Followup: write test_pead.py to use this data

## G.3 - Pending
- Read Part 1 results, evaluate vs mom_roa_6535 winner
- After Part 2 fetch completes, build PEAD signal + test
- This Appendix G is the docs cadence update for prompt 3.


# Appendix H - 3-factor extensions: accruals + PEAD (2026-05-29 early morning)

Continues from Appendix G. Tested both follow-ups to mom_roa_6535 winner.

## H.1 - 2026-05-29 ~00:00 - 3-factor (mom + ROA + accruals) sweep results
Built `trading_bot/factors/mom_roa_acc_zscore.py`. 6 weight configs tested.

### Results
| Config | In CAGR | Hold CAGR | vs mom_roa_6535 |
|---|---:|---:|---|
| mra_60_30_10 | +5.93% | +31.49% | beats in-sample, LOSES held-out (-4.96pp) |
| mra_50_30_20 | +5.83% | +29.65% | best DD (-26.36% in!), loses held-out |
| (all others) | +5.7-5.9% | +29.6-32.0% | similar tradeoff |

**Verdict**: tradeoff, not improvement. Accruals filter trades held-out
alpha (~-5pp CAGR) for in-sample DD reduction (~+5pp). NO variant beats
mom_roa_6535 on held-out CAGR or Sharpe. Not deployable.

## H.2 - 2026-05-29 ~00:30 - PEAD: new-data experiment
Fetched yfinance earnings_dates for 3,128 tickers (~94 min runtime).
2,504 successful (80% coverage), 52,744 earnings events captured with
EPS surprise %.

### First-attempt bug
Initial fetch returned 0 successes because `lxml` package wasn't installed
(yfinance uses it to parse earnings HTML). Killed bad fetch via TaskStop,
installed lxml via pip, restarted with proper API.

### Built infrastructure
- `trading_bot/factors/pead.py` - pead_score returns surprise_pct of
  most recent earnings within 60-day lookback
- `trading_bot/factors/mom_roa_pead_zscore.py` - 3-factor Z-combiner with
  PEAD-missing fallback to neutral 0 (preserves strategy pre-2020 when
  PEAD data doesn't exist)
- `scripts/momentum/test_pead.py` - 7-config sweep

### Results
| Config | In CAGR | Hold CAGR | vs mom_roa_6535 |
|---|---:|---:|---|
| pead_solo | +7.53% / Sh 0.096 | +16.17% | huge DD (-72%) — too noisy |
| mom_pead_70_30 | +2.67% | +22.10% | HURTS held-out vs baseline |
| mom_pead_50_50 | +2.88% | +26.05% | hurts held-out |
| mrp_60_30_10 | +3.63% | +34.03% | loses held-out -2.42pp |
| mrp_50_30_20 | +4.79% | +34.38% | ties in-sample, loses held-out -2.07pp |

**Verdict**: PEAD doesn't help. yfinance data only goes back to 2020 (half
the in-sample period has no signal). PEAD solo has terrible Sharpe + DD.
Combined with mom+ROA, PEAD just dilutes the working signal. No variant
beats mom_roa_6535. Spent ~94 min fetching new data for negative result.

## H.3 - Research arc closure
After this session's exhaustive exploration, mom_roa_6535 stands as the
only deployable winner found. Failed extensions:
- accruals as 3rd factor
- PEAD as overlay (2-factor with mom)
- PEAD as 3rd factor with mom+ROA
- VIX term structure regime
- Trend filter (SPY > 200-DMA)
- Stop-loss (plain + reentry)
- Vol-target (all variants)
- Long-short (research-only, can't deploy without margin)

**Deployed paper sleeves (final, 3):**
- mom_v1_paper (top-100 momentum, diversified)
- mom_v2_paper (top-50 momentum, concentrated)
- mom_roa_6535_paper (top-50, 65% mom Z + 35% ROA Z, current best)

**Next source of forward OOS evidence: live paper-trade returns over
3-12 months.** Real validation comes from forward data, not more backtest
parameter sweeps. The current research bag (1 winner, 17+ failures) is
consistent with the academic literature: 90% of factor-research candidates
fail to deliver in OOS, and "obvious next ideas" rarely beat the
current best.

This Appendix H is the docs cadence update for prompt 3.


# Appendix I - Structurally novel strategies + file reorg + ops (2026-05-29)

User asked to "try the structurally novel ideas" then "do 3 and organize
the files within claudecode/trading".

## I.1 - 2026-05-29 - File organization
Moved 29 research scripts from `scripts/momentum/` to
`scripts/momentum/research/`. Moved 5 warm scripts to
`scripts/momentum/warm/`. Cleaned stale __pycache__ dirs. Added READMEs at
key locations:
- `scripts/momentum/README.md`
- `scripts/momentum/research/README.md`
- `scripts/momentum/warm/README.md`
- `trading_bot/factors/README.md` (PROD vs RESEARCH tagging)
- `var/data_audit/README.md` (artifact catalog)

Verified frozen mom_v2/v1 regression tests still pass at d=0.0000pp.

## I.2 - 2026-05-29 - Operations: Task Scheduler + slippage tracker
Built `scripts/momentum/task_scheduler/`:
- `MomentumPaperDaily.xml` (weekdays 16:30)
- `MomentumPaperRebalance.xml` (1st of month 16:30)
- README with import instructions

Built `scripts/momentum/slippage_tracker.py`:
- Creates `slippage_log` table schema
- CSV ingest pairs real broker fills to paper positions, computes bps
- `--report` for summary
- Dormant until user goes live (~age 18)

## I.3 - 2026-05-29 - Structurally novel idea 1: Sector momentum
Built `scripts/momentum/research/test_sector_momentum.py`. Fetched 11 SPDR
sector ETFs (XLE, XLF, XLI, XLB, XLK, XLP, XLU, XLV, XLY, XLC, XLRE) from
yfinance (~5sec, 3016 days cached). Top-N sector rotation, monthly.

### Results
| Config | In CAGR | Hold CAGR | DD profile |
|---|---:|---:|---|
| mom_v2 (stocks) | +2.72% | +28.81% | -55.26% / -33.86% |
| mom_roa_6535 (stocks) | +4.73% | +36.45% | -44.28% / -30.43% |
| **sector_top2** | **+8.85%** | +18.98% | -35.08% / -19.52% |
| sector_top4 | +7.87% | +17.59% | -31.97% / -16.22% (Sharpe 0.906) |

**Surprising**: sector rotation BEATS stock-level momentum in-sample.
Likely because sector ETFs sidestep penny-stock/data-quality issues.
Held-out CAGR much lower BUT max DD ~half of stock strategies.

**Verdict**: defensive diversifier candidate. Different return profile.
Not a replacement for mom_roa_6535 but candidate for 4th paper sleeve.

## I.4 - 2026-05-29 - Structurally novel idea 2: Insider cluster overlay
Built `trading_bot/factors/insider_cluster.py`. Uses existing 2.3M Form 4
rows with NEW framing: count distinct insiders buying in 30-day window
(transaction_code='P', acquired_disposed='A', total_value >= $10K).

### Results
| Config | In CAGR | In Sharpe | Hold CAGR | Hold Sharpe |
|---|---:|---:|---:|---:|
| cluster_solo | +2.58% | +0.119 | +9.56% | +0.524 — weak |
| mom_cluster_50_50 | +1.15% | +0.034 | +19.22% | +0.882 — bad |
| **mrc_55_30_15** | **+5.83%** | **+0.266** | +34.44% | **+1.116** |
| mrc_50_30_20 | +5.84% | +0.256 | +31.91% | +1.061 |
| mrc_60_25_15 | +4.26% | +0.203 | +31.22% | +1.020 |

`mrc_55_30_15` BEATS mom_roa_6535 in-sample on EVERY metric (+1.10pp CAGR,
+0.025 Sharpe, +1.59pp DD). Held-out Sharpe TIES (+1.116 vs +1.111) with
slightly lower CAGR (-2.01pp). Closest "tie" with mom_roa_6535 yet.

**Verdict**: similar Sharpe profile to mom_roa_6535. Different alpha
source but similar risk-adjusted result. Not a clear improvement; doesn't
add much diversification value (correlated with mom_roa_6535).

## I.5 - 2026-05-29 - Structurally novel idea 3: Cross-strategy ensemble
Built `trading_bot/factors/ensemble.py`. Meta-level voting between
mom_v1 / mom_v2 / mom_roa_6535. 4 modes: intersection, majority, union,
weighted.

### Results
| Mode | In CAGR | Hold CAGR | Hold Sharpe |
|---|---:|---:|---:|
| intersection | +1.89% | **+37.79%** | +1.059 |
| majority/weighted/union | +4.88% | +30.42% | +0.968 |
| (mom_roa_6535 ref) | +4.73% | +36.45% | +1.111 |

`ens_intersection` (only tickers in ALL 3 strategy top-Ns) beats
mom_roa_6535 on held-out CAGR by +1.34pp BUT loses Sharpe (-0.052) and
in-sample (-0.83pp CAGR). Mixed verdict.

Majority/weighted/union collapse to identical results — vote-count
ranking at top_n=50 produces the same picks.

**Verdict**: no clear improvement. Intersection is interesting but doesn't
beat on both windows.

## I.6 - Synthesis
Three structurally novel ideas tested. NONE cleanly beats mom_roa_6535 on
both windows. Two candidates for 4th-sleeve diversification:
1. sector_top4 (genuinely different alpha source, defensive)
2. mrc_55_30_15 (closest tie, similar return profile)

Recommendation: deploy sector_top4 if user wants 4-strategy diversification.
Skip mrc_55_30_15 (too similar to mom_roa_6535).

After 22+ multi-factor attempts, mom_roa_6535 remains the deployed
champion. The "1 winner out of N" ratio matches academic factor research
norms (~5%).

This Appendix I is the docs cadence update for prompt 3.

# Appendix J - Audit fixes + LLM-overlay experiment (2026-05-30 → 05-31)

## Sim/data/dash audit (2026-05-30)
Full audit on user request. Report: `docs/audit_2026-05-30.md`. Headline:
`daily_price_refresh.py` had not run since 2026-05-19 → 197/204 open holdings
priced 11-23 days stale. The dashboard had been showing all 3 stock sleeves
DOWN (-0.15 to -3.02%) when, on fresh prices, they were UP +3.6 to +6.5%.
The stored "mom_v2 -3.02% on 2026-05-28" was MTM'd on May-7/19 prices stamped
May-28 — a pure staleness artifact, not a real drop.

Fixes shipped:
- Ran price refresh (111K rows), backfilled daily paper_nav from inception
  (2026-05-01) so the dash shows smooth day-by-day curves.
- C2 guard: paper_rebalance aborts if universe < max(2*top_n,200) (11 for
  sector) — prevents catastrophic liquidation-into-ETFs on stale-data days.
- Age-aware staleness: dashboard flags per-position price age + top-level
  warning; paper_mtm logs WARN (>3d) / ERROR (>7d).
- Per-sleeve dashboard spec card (was hardcoded mom_v2); portable last_closes
  SQL; "All sleeves overlay" tab; view+sleeve persisted in query params.
- TWO Windows scheduled tasks now run independent of Claude/IDE:
  `TradingDashboard` (AtLogon) + `TradingDailyMTM` (5:15pm daily). Dashboard
  + MTM survive Claude open/close.

True current NAVs (4 systematic sleeves): mom_roa_6535 +6.50% (leader),
mom_v2 +3.75%, mom_v1 +3.67%, sector_top4 +3.29%.

## LLM-overlay experiment (2026-05-31)
User proposed LLM-driven discretionary stock picking (find a promising stock,
run 3 analyst prompts). Analyzed from 5 angles, NO yes-man:
- Optimist: useful as a forced-rigor risk VETO on systematic picks (6/10).
- Methodologist: un-walk-forwardable, n=1 per pick, re-derives owned factors (2/10).
- Behavioral: narrative seduction; erodes the systematic discipline that works (3/10).
- Market-efficiency: no info edge on public data + stale model; illiquid niche
  is where our DATA is worst (2/10).
- Pragmatic engineer: defensible ONLY if operationalized as a logged,
  pre-committed, falsifiable overlay (5/10).

Verdict: NOT a standalone strategy. Built it as a falsifiable experiment with
a pre-committed kill switch instead of arguing about it.

Implementation (see memory/llm_overlay_experiment.md):
- `llm_overlay_log` table; `trading_bot/strategies/llm_overlay.py`;
  `scripts/momentum/llm_overlay_ops.py` (candidate/decide/rebalance/check-invalidation).
- Two single-name $100k sleeves, top-1 by mom_roa_6535 Z-score:
  `mom_roa_top1_paper` (CONTROL, no veto) vs `llm_overlay_paper` (TREATMENT,
  buy only on logged BUY + daily invalidation stop).
- Kill switch (= Form 4 bar): 12mo / ≥30 picks; drop if scores don't predict
  forward 3mo returns OR treatment doesn't beat control net of costs.

First decision (2026-05-29): candidate BE (Bloom Energy), Z=+11.53 — verified
a REAL 17x run ($16→$285, no data artifact). VETO, score 5/10, invalidation
$220. Real growth (Q1 rev +130%, FY guide $3.4-3.8B) but 27x sales / 149x
non-GAAP EPS / above mean analyst PT ($260) / 50% revenue from one customer /
16x-extended. Control holds BE; treatment holds cash. First clean comparison.

Honest prior recorded: expect the experiment to FAIL its kill switch.

This Appendix J is the docs cadence catch-up (audit + experiment work spanned
several prompts under model claude-opus-4-7/4-8).


# Appendix K - LLM-overlay first treatment trade + cadence rule (2026-06-03)

## K.1 - 2026-06-03 ~17:50 - User: "the llm overlay hasn't initiated a trade yet"
Diagnosed: working as designed, not a bug. The only logged decision was the
5/29 BE VETO → treatment correctly sat in cash. It had stalled because the
June monthly rebalance was overdue (rebalance.bat is MANUAL; only daily MTM +
dashboard are scheduled — nobody ran it on the 1st June trading day) AND no
new decision had been logged.

## K.2 - User directive (cadence): "run the 3 prompts on every trade the
underlying algorithm passes through as a buy"
Rule set: every name the underlying (control) BUYS gets the 3-prompt LLM eval
before the treatment acts. Implemented (surgical):
- `llm_overlay_ops.py` control rebalance now prints "NEW UNDERLYING BUY
  <ticker>" + "LLM EVALUATION OWED" when the #1 name changed.
- overlay rebalance's no-decision error now names the current candidate.
- rebalance.bat note updated with the rule.

## K.3 - June rebalance executed (both LLM sleeves, synced 6/03)
Candidate rotated BE→FN (Fabrinet), Z=+15.17, $725. Ran the 3 prompts on
CURRENT web data:
- Q3 FY26 rev $1.214B (+39% YoY), record EPS, beat+raise, debt-free ($945M
  cash, $4.4M debt). LTM rev $4.24B, EPS $11.64.
- BUT thin-margin assembler (gross 12% / net 10%) priced at 62x ttm / 44x fwd
  / 6x sales; $725 ABOVE median sell-side PT (~$544); ~46% rev from
  Nvidia+Cisco; CPO structural risk; LTM FCF only $46M (low conversion).
Verdict: BUY, score 6, invalidation $600. Consistency check vs BE veto: FN is
cheaper on sales, profitable, less concentrated → clears the bar BE failed.
- Control: SOLD BE +$712.56 realized (BE ~flat +0.7% over 5/29-6/03 — veto
  neither dodged a top nor missed much), BOUGHT FN 138.71 sh @ $725.36.
- Treatment: FIRST TRADE — BOUGHT FN 137.72 sh @ $725.36. NAV -0.05% (entry
  spread only). Control NAV +0.66% (carries the realized BE gain).
- n=2 picks now (1 VETO, 1 BUY). Kill switch unchanged (12mo / ≥30 picks).

NOTE: the 4 systematic sleeves' June monthly rebalance is ALSO overdue (only
the 2 LLM sleeves were rebalanced this prompt, matching the user's scope).


# Appendix L - June rebalance, sleeve rename, sim refactor + audit (2026-06-03→04)

## L.1 - Full June monthly rebalance (all 6 sleeves)
Ran rebalance.bat end-to-end. FIRST run failed (exit 255): latent cmd-parsing
bug — an `echo` inside the `if errorlevel 1 (...)` block contained unescaped
parens `(would use stale ranks)`, whose `)` closed the block early → `. was
unexpected`. (This is why the bat had never run end-to-end before; LLM sleeves
were always rebalanced via direct `python -m`.) Fixed (removed the parens),
re-ran clean. Results: mom_roa_6535 +7.99% (leader), sector_top4 +5.48%,
mom_v1 +3.01%, mom_v2 +2.14%; LLM control/treatment both hold FN. Universe
3078 eligible (first systematic rebalance under the new MAX_PRICE_USD ghost
filter). All MTMs + invalidation check (FN $725 > $600 stop) ran.

## L.2 - Renamed treatment sleeve
`llm_overlay_paper` → `llm_overlay_mom_roa_top1_paper` (the `_mom_roa_top1`
suffix distinguishes it as the overlay on the top-1 mom_roa pick). Updated 5
code files (OVERLAY_STRATEGY const, web.py, daily.bat, rebalance.bat, db.py)
+ DB migration (1 portfolio / 1 position / 5 NAV rows) with a collision
pre-check. Control sleeve `mom_roa_top1_paper` unchanged. Verified: MTM works,
dashboard HTTP 200, zero stale references.
REJECTED a proposed top-50 overlay (`llm_overlay_mom_roa_6535`): ~30 evals/mo
infeasible + a 1-of-50 veto moves ~2% NAV = methodologically weak test. User
agreed to skip; keep the experiment single-name.

## L.3 - Sim refactor (behavior-preserving) + full audit  [report: docs/audit_2026-06-04.md]
User: "refactor all the code in the sim and make sure it remains working, then
do a full audit." Did NOT blind-rewrite (would violate surgical discipline on
live money-adjacent code). Two real targets:
1. De-duped a 3-way-copied "last close at-or-before" SQL helper →
   `market_data.last_close_on_or_before()`; removed orphaned imports.
2. Removed the "caller must remember adjust_cash" foot-gun → atomic
   `paper_trader.buy()/sell()`; migrated 5 call sites. (+ dropped a dead
   `import json`.)
Verified green: frozen tests 0.0000pp, all-6 NAVs byte-identical, throwaway
buy/sell recon $0 drift, rebalance + llm dry-runs clean, dashboard 200.
Audit: cash-ledger recon all 6 = $0.0000 drift; NAV recon all 6 = $0.0000;
PRAGMA quick_check ok; 0 FK violations. Zero behavior change, two smells gone.


# Appendix M - Market selloff analysis + sector-overlay experiment (2026-06-05)

## M.1 - "massive drop today, analyze it"
Real, broad selloff (not a data ghost: 71% of 4,350 tickers down, median
-1.26%, corroborated by news). Catalyst = two-punch: (1) Broadcom earnings
disappointed → AI/semiconductor-boom doubt → SOX biggest 1-day drop since Mar
2020, ~$1T erased (Marvell/Micron/AMD/Intel all down hard); (2) hot May jobs
(172k vs ~85k exp) → 10Y >4.5%, 30Y >5%, rate-cut hopes dead. Nasdaq ~-4.2%,
S&P ~-2.6%. Cache: SPY -2.58%, XLK -6.66%. (1-day yfinance date offset: worst
day labeled 06-05 in cache vs news 06-04/05.) Sleeve impact 06-04→06-05:
LLM sleeves (FN) -13.1%; mom_v2 -5.9%, mom_roa_6535 -5.6%, mom_v1 -5.5%;
sector_top4 -3.0% (most defensive). FN $714.78→$621.25, stop $600 — did NOT
trigger but only 3.4% away (armed; auto-exits on a <=600 close via daily.bat).

## M.2 - Built a SECTOR overlay (macro LLM veto) — user said "a" (build path)
After a feasibility analysis (operationally easy: 4 ETFs/mo; veto moves 25% so
not diluted like the rejected top-50; BUT the 3 stock prompts don't fit ETFs →
needs MACRO prompts where the LLM has least edge), designed a 4-prompt macro set
and built it ISOLATED from the live stock overlay:
- `trading_bot/strategies/sector_overlay.py` (candidates, macro prompts, log fns)
- `scripts/momentum/sector_overlay_ops.py` (candidate/decide/rebalance/check-
  invalidation/init; refuses unless all 4 sectors decided; veto→cash 25% slot)
- `sector_overlay_log` table UNIQUE(decision_date,ticker)
- treatment sleeve `llm_overlay_sector_top4_paper` ($100k); control = existing
  `sector_top4_paper`. Wired daily.bat + rebalance.bat; dashboard panel +
  spec entry.
Verified: candidate prints per-sector prompts (top-4 today XLK/XLE/XLI/XLB);
rebalance refuses w/o decisions; frozen tests 0.0000pp; quick_check ok;
dashboard HTTP 200. NOT yet seeded (cash, 0 decisions) — pending the first
4-sector macro decision round. Honest prior: weaker test than the stock overlay.


# Appendix N - Dashboard S&P 500 control benchmark (2026-06-06)

Dashboard-only changes (no strategy/data/sim logic touched; frozen tests
unaffected). Added an S&P 500 (SPY) "control" benchmark everywhere returns are
shown, so every sleeve is judged against just-buying-the-market.

## N.1 - SPY benchmark line on all NAV charts
- New cached helper `fetch_spy_series(start, end)` in web.py — SPY daily closes
  via the existing yfinance path, tz-naive nav_date + close. Price-only (no
  dividends reinvested) to match the sleeves apples-to-apples; SPY (the ETF),
  not ^GSPC, since it's what you'd actually buy.
- Overlay tab: SPY drawn on BOTH the % chart (normalized to 0% at the earliest
  sleeve inception) and the absolute-$ chart (scaled to first sleeve's start),
  gray dotted line.
- Single-sleeve NAV curve: rebuilt from px.line → go.Figure with named traces;
  SPY scaled to that sleeve's own starting cash, anchored to that sleeve's own
  inception. (Verified SPY fetch: +3.13% since ~5/1 inception.)

## N.2 - Show/hide lines
Plotly legend toggle is native (single-click hide, double-click isolate). The
single-sleeve chart previously had NO legend (one unnamed px.line trace) — now
has named traces + horizontal legend so it's toggleable. Added caption hints on
single-sleeve + overlay charts. Did NOT build custom st.multiselect (legend
toggle is the standard zero-maintenance tool); flagged that to user.

## N.3 - S&P 500 as a "control" in the headlines (distinct background)
- New scalar helper `spy_return_pct(inception)` (SPY % from inception→today).
- Single-sleeve headlines: added a 5th column (st.columns 4→5) with an HTML
  card — tinted bg `rgba(148,163,184,0.15)` + gray left-border marks it as the
  benchmark, shows SPY % over the same period + alpha (sleeve − SPY).
  Refactored inception to compute ONCE before headlines, reused by the NAV
  block (removed the duplicate calc there).
- Overlay "Sleeve headlines" table: appended an "S&P 500 (control)" row that
  sorts INTO the ranking (shows where the market sits) with a shaded background
  via Styler.apply; caption clarifies it's a benchmark, not a tradeable sleeve.

Verified: py_compile OK; styler logic test (control row sorts in + highlighted);
SPY fetch live; dashboard HTTP 200 throughout. Theme-safe: rgba gray tint reads
on both light/dark Streamlit themes (no config.toml theme set).


# Appendix O - Daily-trade-check follow-up on the 6/05 chip crash (2026-06-08, automated)

Automated `daily-trade-check` run over the weekend. Re-examined Fri 6/05 (the
SOX crash already logged same-day in Appendix M) with new framing + actionable
ideas. Report: `docs/research_2026-06-08_chip_crash.md`.

NEW vs M.1:
- Friday drawdown maps MONOTONICALLY to concentration: sector_top4 -3.0% <
  momentum books -5.5% < single-name FN -13.1%. Diversification did exactly
  what it should — quantified, not just observed.
- Timing insight: the 6/03 rebalance BOUGHT the crowded semi top — every name
  it added (FN, CIEN -21%, RMBS -15%, WDC -14%, INTC -12%) is now a top loser,
  while the same-sector 5/01-inception semis (MU +59%, DOCN +65%, STX, LRCX)
  are the big winners. Momentum rotated into an already-extended theme.
- Confirmed via grep: `paper_rebalance.py` has NO sector cap and NO overbought/
  extension entry filter. Two net-new backtest ideas proposed:
  (1) cap any GICS sector at ~30-35% of book (preemptive DD control, aligns
  with sleeves_verdict's "DD control must be preemptive"); (2) reject names
  >X% above 20-day MA at entry (don't buy parabolas like FN @ $725).
- Reiterated: seed the built-but-unseeded `llm_overlay_sector_top4_paper` —
  6/05 is the ideal first forward-test for its macro rate/breadth veto.
No code/data/trade changes — research + report only.

## O.1 - Monday 6/08 follow-through (automated, same day, after market data landed)

Second daily-trade-check fire of 6/08, now with Monday's prices in the DB
(`price_cache` close max key_date = 2026-06-08, 5866 tickers). Resolves the open
question Appendix O left: the slide did NOT continue — **6/08 was a sharp
V-bounce**, so the crash read as a positioning flush, not a regime break.

- Crash names rebounded hard 6/05→6/08: MU +9.9%, INTC +11.2%, AAOI +11.1%,
  LRCX +7.0%, RMBS +4.6%, TER +4.7%, AVGO +2.8%. A few kept sliding
  (CIEN −4.4%, AEHR −2.9%, MXL −2.0%).
- Sleeve NAV recovery 6/05→6/08: roa6535 +1.47%, v2 +1.08%, v1 +0.82%,
  sector_top4 +0.46%, both top-1 +0.40%. Cum since 5/01: roa6535 +3.69% (lead),
  sector +2.59%, v1 −1.58%, v2 −2.74%, top-1 −13.4%, llm-top1 −14.0%.
- **FN stop did NOT trigger.** $621.25 (6/05) → $623.71 (6/08), held above the
  $600 invalidation; all five FN positions still open, zero recent exits.
- KEY FIND: the V-bounce is fresh live evidence for [[sleeves_verdict]]'s
  preemptive-not-reactive thesis. A reactive stop would have sold the 6/05
  bottom and missed the 6/08 bounce. → **Promote the sector cap (preemptive) to
  the top backtest idea over single-name stops (reactive).** Confirmed mom_v2 is
  47.8% Tech / 23.8% Healthcare today, so a 30–35% GICS cap would bind now.
Report updated: `docs/research_2026-06-08_chip_crash.md` (Monday follow-through
section). No code/data/trade changes — research + report only.


# Appendix P - Algo-landscape research: top-5 candidates (2026-06-09)

User asked for full research into all trading-algorithm types + a ranked top-5
"most profit" proposal (>30 min analysis). Done as a pure research deliverable
— NO code/data/trade changes. Full report: `docs/research_2026-06-09_algo_candidates.md`.

Method: inventoried all 23 prior attempts (so no duplicates proposed), locked
constraints (long-only til 18, EOD yfinance, 5-30bps TC, frozen-window
validation), then ~14 web searches/fetches across every strategy family. All
expectations haircut by McLean-Pontiff decay (-26% OOS / -58% post-pub) AND
the project's own 1-winner-in-23 base rate.

**Top 5 (ranked by expected CAGR x survival probability x deployability):**
1. Vol-targeted L/S momentum ACTIVATION PROGRAM — own Attempt 16 held-out
   +35-41%/Sharpe 1.3 is the project's biggest measured edge; fix in-sample
   2022 bust (5d vol lookback, 8% target, gross cap) + build short paper-sim
   now, deploy at 18.
2. VIX-term-structure-gated short-vol sleeve (SVXY when VIX/VIX3M contango +
   SPY>275DMA, else cash) — biggest documented premium accessible long-only
   at EOD; ^VIX/^VIX3M already cached; expect 10-20% CAGR w/ rare -30-50%
   tail months; size small.
3. Residual momentum + 52wk-high construction sweep on flagship — academic 2x
   risk-adj vs std momentum, crash-resistant; ZERO new data; 1 session;
   highest info-per-hour.
4. Gayed leveraged-ETF trend rotation (SSO/TQQQ over 200DMA else BIL) — LETFs
   need no margin; 12-20% post-haircut; whipsaw is the failure mode; NOT
   redundant w/ failed trend200 (that gated stock alpha on an index signal).
5. Turn-of-month + T-bill carry (SPY 4d/month, BIL rest) — 7.2%/yr Sharpe
   1.04 at 20% exposure + carry = ~10%; highest survival probability, lowest
   CAGR; the "control" candidate.

Rejected with receipts: overnight effect (TC-fatal), pairs/stat-arb (shorts +
decade decay), index-add arb (vanished per Greenwood-Sammon), GEM dual
momentum (17.4%->5.9%/yr post-pub), ML ranking (GKX's own dominant signals =
mom/liquidity/vol — already owned; overfit risk), BTC trend (18+ KYC,
honorable mention), options/HFT (infrastructure class).

Recommended sequence: #3 first (1 session, zero data), #5, #2, #4, with #1
running as background program. Each must pass both frozen windows + paper
sleeve before anything goes live at 18.


# Appendix Q - Built + backtested the top-5 candidates; deployed 1 winner (2026-06-09)

User: "add all 5 [research candidates] to the trading dash and fix price
staleness". Chose the disciplined path (AskUserQuestion): build + backtest each,
deploy ONLY those that beat the bar. NOT a quick dash edit — the dash only shows
sleeves that exist in paper_portfolio, which requires a built+validated strategy.

## Q.1 - Price staleness FIXED
Ran daily_price_refresh (109,830 close rows, 1.9 min). After refresh: 0 stale
holdings across all 6 sleeves. The warning was just the pre-5:15pm gap (scheduled
TradingDailyMTM hadn't run) + 1 ticker yfinance lagged a day. Warning logic left
intact (it caught a real bug on 2026-05-30); it's working as designed.

## Q.2 - Backtests (both frozen windows, references re-run LIVE on clean data)
Built factors: residual_momentum.py (Blitz idiosyncratic momentum = alpha/resid
_sd from a SPY market-model regression; NOT mean(resid) which is ~0 by OLS
construction — bug caught in smoke test), high_52w.py (George-Hwang), zcombo.py
(generic Z-combiner). Plus 3 single-asset timing sims (turn_of_month, gayed_letf,
vix_shortvol) reading price_cache directly. Fetched VIX+LETF data
(warm_vol_letf_etfs.py: ^VIX/^VIX3M/SVXY/VIXY/SSO/UPRO/QLD/TQQQ/QQQ).

VERDICTS:
- #3 residual_roa_6535: **PASS / DEPLOYED**. In-sample +8.86%/Sh0.419/-37.62%;
  held-out +30.84%/Sh1.065/-20.28%. Beats mom_v2 on BOTH windows on return AND
  Sharpe AND DD (2nd strategy ever to clear the bar). Vs champion mom_roa_6535:
  wins in-sample on all 3, loses held-out CAGR -5.6pp, ~ties Sharpe, much better
  DD (+10pp). A lower-drawdown sibling, not a champion replacement. Rejected the
  52wk variants: high52w_solo (negative in-sample Sharpe), high52w_roa_6535
  (textbook overfit — in-sample +9.89% best of all, held-out CAGR collapses to
  +11.65%).
- #5 turn_of_month: REJECT. In-sample Sharpe 0.249 (<0.7 bar); loses to SPY
  buy-hold on Sharpe AND CAGR both windows; held-out +4.17% < 4.5% cash. Effect
  is real+positive (tiny -8% DD) but can't beat a bull-market buy-and-hold.
- #2 vix_shortvol: REJECT. Held-out Sharpe NEGATIVE (-0.42); even gated it ate a
  -26.5% single day in-sample (pre-committed kill: EOD gate can't dodge intraday
  spikes); -0.5x relevering killed the edge post-2018.
- #4 gayed_letf: REJECT for deploy. QLD_rot/TQQQ_rot beat mom_v2 but that's a
  benchmark mismatch — vs their natural benchmark (QQQ) they LOSE Sharpe (0.52
  vs 0.86 in / 0.96 vs 1.11 hold) AND DD on both windows. The 200-DMA filter
  only cuts the LETF tail (-82%->-55%); doesn't earn risk-adjusted edge. Gayed
  thesis didn't replicate. (Offered as optional aggressive sleeve; not auto-deployed.)
- #1 vol-targeted L/S: research-only (no shorts in paper_trader; no margin til 18).

Net: 1 deployable winner of 4 tested — matches the project's ~1-in-20 base rate.

## Q.3 - CONTAMINATION BUG caught + fixed
warm_vol_letf_etfs added TQQQ/SVXY/QLD (huge 2023 momentum, ranks #115/#132/#191)
to price_cache → they entered the STOCK tradeable_universe → momentum_v1/2023_Q4
frozen test broke (-0.1986pp; v2 unaffected since they never reached top-50).
FIX: added universe.NON_STOCK_TICKERS exclusion set (+ "^"-prefix indices) to
tradeable_universe. sector_top4 (own SECTOR_UNIVERSE) + residual_momentum (reads
SPY directly) unaffected. All 4 frozen tests back to 0.0000pp. This also confirms
the pre-existing sector/SPY/RSP ETFs never affected frozen windows (rank >300).
Without this fix the live momentum sleeves would have bought TQQQ on next rebal.

## Q.4 - Deployment of residual_roa_6535_paper
Frozen spec strategies/residual_roa_6535.py; dispatch in paper_rebalance
_strategy_config; daily.bat MTM + rebalance.bat rebalance+MTM wired; dashboard
_SPEC_BY_SLEEVE entry (auto-discovered from paper_portfolio otherwise). Seeded
$100k, inception 2026-06-09 (NOT backdated — forward OOS starts now), 50
positions, NAV $99,950.07 (-0.05% = entry spread). Cash recon drift $0.0000.
Dashboard HTTP 200. Now 5 systematic sleeves (mom_v1/v2/roa6535/residual6535/
sector4) + 3 LLM-experiment.


# Appendix R - Long-short vol-target: re-run + crash-fix sweep, VERIFIED FAIL (2026-06-09)

User asked why #1 (vol-target L/S momentum) "can't be tested now" — correct
pushback: it CAN be backtested now (was, Attempt 16); what's blocked is paper
DEPLOYMENT (no short support in paper_trader) and LIVE (age 18/margin). Then:
"do both" = (1) re-run existing LS vol-target on clean data, (2) run the
crash-fix sweep.

## R.1 - Re-run test_long_short_voltgt on current data: CONFIRMS Attempt 16
Held-out STILL excellent: ls_voltgt10 +36.23%/Sharpe 1.300/DD -20.8%
(targets 10-16% all Sharpe 1.24-1.30). In-sample STILL busts (all targets,
DD -241% to -265%, NAV goes deeply negative mid-2022 then recovers to small
positive). Clean data + NON_STOCK_TICKERS exclusion didn't change the verdict.

## R.2 - Crash-fix sweep (5d lookback / 8% target / hard gross cap 1.5x): FAILS WORSE
test_long_short_voltgt_crashfix.py. ALL 4 configs still BUST in-sample, with
DEEPER drawdowns (-332% to -776%) than the original. fix_21d_t8_cap15 is
STRICTLY more conservative than original ls_voltgt10 yet busts worse — a red
flag I chased down:

VERIFIED NO BUG: ran my crash-fix engine with the original's exact params
(21d/t10/cap2.0) -> reproduced original EXACTLY (ending +25,801, DD -241.2%,
avgScale 0.601). So the worse numbers are REAL, not an engine bug. Cause:
(a) vol-targeting on the book's OWN returns is a feedback loop (lower leverage
-> lower measured vol -> re-levers vs the cap); (b) 5d lookback is noisy and
reads false-calm right before squeezes -> deploys at the cap into the crash.

## R.3 - Tested de-levering to 1x gross (scale_cap 0.5): STILL BUSTS
1x_voltgt_t10_21d: in-sample BUST (minNAV -$194,649, DD -261%); held-out
+22.53%/Sharpe 0.900. A 1x book losing ~$294k from $100k is impossible from
price moves UNLESS the short leg blows up. ROOT CAUSE identified: long-short
momentum SHORTS the worst-momentum names = exactly the short-squeeze
candidates (2021 meme stocks 10-50x). Monthly rebalancing can't react to a
mid-month squeeze; NAV goes deeply negative before month-end. This is
unbounded short risk, NOT a leverage problem -> de-levering can't fix it.

## R.4 - VERDICT for #1
Held-out edge is real and the best risk-adjusted in the project (Sharpe ~1.3),
but it's REGIME LUCK: 2024-26 had no meme-squeeze. The 2015-23 in-sample busts
at 2x AND 1x AND under every reactive vol-control variant. Consistent with the
project's standing lesson (Attempts 12-14): reactive risk control on momentum
fails; control must be PREEMPTIVE. The proposed crash fix does NOT work.
What MIGHT (future research, not done): hard per-name buy-to-cover stops on
shorts (bounds squeeze), or filtering the SHORT universe (drop low-float/high-SI
squeeze candidates; only short liquid large-caps). Until then #1 stays
research-only — and now for a STRONGER reason than "age/margin": it's not
risk-survivable in-sample regardless. NOT deploying short support in
paper_trader (would be premature for an un-deployable strategy).


# Appendix S - Backdated residual_roa_6535_paper to 2026-05-01 (2026-06-09)

User: backdate the live paper sleeve to 2026-05-01 so it has the same start +
elapsed time as mom_roa_6535 (the other sleeves are all 5/01). Reversed my
earlier "inception today" call — backdating is fair here: deterministic on
cached prices, same method the original sleeves were seeded by, and it makes
the dashboard head-to-head apples-to-apples.

Method (one-off orchestration, since no seed script exists): wiped the
today-seeded sleeve -> rebalance as-of 2026-05-01 -> daily MTM 5/01..6/02 (22
trading days) -> rebalance as-of 2026-06-03 (mirrors mom_roa's exact June
rebalance date; 23 sells/23 buys/27 keeps) -> daily MTM 6/03..6/09 (5 days).
27 NAV rows, 5/01..6/09.

Verify: cash recon $0.0000 (note: correct ledger = starting - SUM(entry over
ALL positions) + SUM(exit over CLOSED); my first check wrongly omitted closed
entries and falsely flagged drift on BOTH sleeves incl. known-clean mom_roa —
corrected, both $0.0000). Dashboard HTTP 200.

Head-to-head over the now-identical 5/01->6/09 window: residual_roa_6535
**+6.11%** vs mom_roa_6535 **+2.65%** (+3.46pp). 5 weeks = noise, but residual
is ahead early, consistent with its stronger/lower-DD backtest. Updated spec
docstring inception note. Sleeve spec/dispatch/bat-wiring unchanged from
Appendix Q.


# Appendix T - Full audit, 4th sweep (2026-06-09 late)

User: "audit every file in the folder. Look for any inconsistencies, flaws, or
sim issues." Full report: docs/audit_2026-06-09.md. Headlines:

- **C1 CRITICAL (found+fixed): dividend-adjustment seam.** daily_price_refresh
  was the ONLY cache writer using auto_adjust=True (cache convention =
  dividend-UNadjusted everywhere else). Every run since 05-30 stamped adjusted
  closes over the trailing 30d of ~4,300 tickers — measured -0.57% to -0.91%
  on XOM/JNJ/CVX/IBM rows near their ex-divs. Fixed the flag, repaired with a
  60-day re-refresh (217,438 rows), verified against recorded bad values,
  frozen tests 0.0000pp, re-MTM'd all 8 sleeves. Convention now documented in
  code + CLAUDE.md quirks.
- **H1 (fixed): weekend NAV rows.** Scheduled MTM fires Sat/Sun → 24
  carry-forward rows across 7 sleeves. Deleted; paper_mtm now skips weekends.
- **M1 (fixed): 104 junk root files** (zero-byte shell shrapnel incl. a 0-byte
  paper_rebalance.py decoy, a `null` error log, varquality_screen.out). Root
  now has only the 8 real files.
- **M2 (fixed): stale docs** — dash caption var/trading.db→var/trades.db;
  CLAUDE.md quirks updated (8 sleeves not "TWO", ~5GB DB, cache convention,
  NON_STOCK_TICKERS). HANDOFF.md flagged stale (not rewritten).
- **Clean**: cash recon $0.0000 all 8 sleeves; position math exact; NAV
  continuity gap-free; universe 3,095 w/ zero ETF leakage + no ETFs in stock
  sleeves; scheduled tasks healthy; backup intact; bats cover all sleeves;
  the auto_adjust=True research scripts never wrote to cache.
- **Documented nuances**: residual-momentum early-2015 truncated regression
  windows (SPY data starts 2014-06); single-asset sims fill at prior close
  (standard, both strategies rejected anyway); ToM window variant; crashfix
  engine conservative init (verified by exact replication); holiday NAV rows
  possible.
NAVs post-repair: v1 -2.07% / v2 -3.71% / roa +2.65% / residual +6.11% /
sector +2.34% / top1 control -18.62% / top1 treatment -19.23% / sector
overlay unseeded.


# Appendix U - Dashboard rework: dense Overview default view (2026-06-10)

User: "rework the dash to be more user friendly and info dense." Added a new
DEFAULT '📊 Overview' view to the paper-trade tab (existing Single-sleeve and
NAV-charts views unchanged; radio now 3 options, query-param persisted).

One dense screen:
- Status strip: prices-through date + stale-holdings count, S&P 500 today,
  S&P 500 since inception, next manual rebalance date.
- All-sleeve table (INCLUDING the normally-hidden mom_roa_top1 control — 8
  sleeves + shaded S&P control row): NAV / Day % / Total % / alpha-vs-SPY /
  live Max DD / Cash / Pos / last rebalance, red-green colored, sorted by
  return. Short display names (mom_v1, residual, llm_top1, ...).
- Compact NAV-%-from-inception chart (all sleeves + SPY dotted), legend
  click-to-hide.
- Top movers today across all HELD names (top 5 up + 5 down, with which
  sleeves hold them).
- LLM experiments panel: latest stock-veto decision + live stop distance
  (reads llm_overlay_log + price_cache), treatment-vs-control gap in pp,
  sector-overlay status (unseeded/decision count).
- Concentration captions: top sector weight per stock sleeve, warning >35%.

Implementation: _render_overview + helpers (_short, _sleeve_inception,
_spy_cache_closes, _spy_ret_between) in web.py. SPY data for Overview comes
from price_cache (same pricing basis as sleeves, no network); the other views
keep their yfinance benchmark. Day% = live NAV vs last pre-today paper_nav
row. Verified: py_compile, headless render test (monkeypatched st: table 9x9,
chart 9 traces, movers 10x4, no exceptions), pandas-3 Styler.map confirmed,
dashboard HTTP 200.

# Appendix V - Scheduled daily trade-check: optical sell-off + residual validation (2026-06-10)

Autonomous scheduled run (daily-trade-check). Report:
docs/research_2026-06-10_overnight_optical_selloff.md. No write actions to
DB/sleeves.

Real-world event of the week: CIEN 06-04 earnings (beat, only modest raise) ->
profit-taking that de-rated the whole crowded AI-optical cohort (CIEN/FN/Lumentum/
Coherent/Corning/Marvell). Memory/HBM (MU +72% MTM) + semi-equipment (AMAT/LRCX/
KLAC) kept ripping. The AI trade bifurcated: interconnect down, compute/memory up.

Two validated findings:
- RESIDUAL MOMENTUM DODGED IT (live, well-identified): at the SAME 06-03 rebalance
  where mom_v2 + mom_roa_6535 bought CIEN+FN, residual_roa_6535 declined both and
  had sold Corning/GLW at +27%. residual's open book entered only 05-01 (27) +
  06-03 (23), NONE on 06-09 -> not hindsight. Cohort then fell -19% (FN) to -29%
  (CIEN) in a week. residual now top live sleeve +6.11% vs mom_roa_6535 +2.65% /
  mom_v2 -3.71%. Reinforces the 06-09 deployment; n=1 event, keep watching.
- LLM-OVERLAY INVALIDATION STOP FIRED on FN: both single-name sleeves bought FN @
  725 on 06-03; overlay logged BUY score6 inval 600 with a rationale that named
  the exact bear case (62x ttm, ~46% rev Nvidia+Cisco, CPO risk). FN broke 600 on
  06-09 (586) -> overlay sold -19.3%; control still holds. Net ~tie (overlay
  -19.23% vs control -18.62%). Entry was NOT vetoed (LLM said BUY) so overlay only
  capped the tail; one exit-side data point toward the 30-pick kill switch.

Strategy ideas logged (not built): (1) earnings-proximity haircut for momentum
entries; (2) crowding/common-beta or per-sector position cap on the raw sleeves;
(3) sub-sector tilts inside the AI complex (memory vs interconnect) instead of one
"AI semis" bucket. Loose end: llm_overlay_sector_top4 still unseeded -> missing the
CPI-week macro-veto test it was built for (seeding is a manual write decision).

Cadence note: this is a standalone scheduled run; record + research doc updated
same prompt, cadence not slipped.

# Appendix W - S&P 500 control as a real sleeve + chart polish (2026-06-10)

User: "the S&P 500 control is broken. I want it to function like another sleeve
(Invested 100k into s&P 500 on may 1 2026 but use the actual day to day returns
of the S&P 500 to update the %s). round the %s on the charts to the nearest
0.001% and when you hover over the graph on a particular day they should show up
in order from highest % or $ to lowest % or $."

Root cause of "broken": the dashboard's overlay + single-sleeve SPY line came
from `fetch_spy_series`, a yfinance fetch that rate-limited and intermittently
returned empty -> the S&P line vanished. (The Overview's SPY was already
cache-based and fine.)

Three changes:

1. **SPY is now a REAL sleeve** — `spy_benchmark_paper`. New one-off
   `scripts/momentum/seed_spy_benchmark.py`: $100k buys SPY fully-invested at
   the 2026-05-01 close (qty 138.763611 @ 720.65), never rebalanced, MTM'd
   daily 05-01 -> today from the same cached SPY closes every sleeve uses. It's
   a genuine buy-and-hold position whose NAV moves with the actual daily S&P.
   Verified: cash recon drift $0.0000000000; 27 NAV rows, no weekend/missing
   trading days; 05-01 $100,000.00 -> 06-09 $102,275.72 (+2.276%). Wired
   MTM-only into daily.bat + rebalance.bat (NOT rebalance — paper_rebalance
   has no config branch for it; it's buy-and-hold).

2. **Dashboard sources SPY from the real sleeve, no network.** Rewrote
   `fetch_spy_series` to read `spy_benchmark_paper`'s paper_nav (fallback:
   price_cache SPY closes) — same (nav_date, close) shape so every call site
   (overlay %/$, single-sleeve) is unchanged and now never blanks.
   `spy_return_pct` inherits the fix. In the Overview the S&P control is now a
   first-class shaded sleeve ROW (real NAV / Day% / MaxDD / alpha≈0), replacing
   the old synthetic row; excluded from the selectable-strategy + overlay lists
   (`SPY_SLEEVE`) so it isn't double-counted; skipped in top-movers +
   concentration (it's the benchmark, not a stock pick).

3. **Chart polish.** All %-chart hovers now show 3 decimals (`%{y:+.3f}%`,
   = nearest 0.001%); $ charts keep $ formatting. Hover ordering: confirmed
   from the bundled plotly.js (Streamlit 1.57 / plotly 6.7) that `x unified`
   sorts its in-hover legend by **trace index**, with no value-sort option
   (`Se.entries.sort((a,b)=>a.trace.index-b.trace.index)`). So per the user's
   pick (asked via AskUserQuestion — "keep unified box, order by latest
   standings" vs "switch to true per-day compare hover"), every NAV chart now
   builds its traces then adds them in **descending latest-value order**, so the
   unified box reads highest->lowest (exact at the current edge / most days;
   on a historical day where ranks differ it reflects today's standings —
   Plotly can't re-sort the unified box per hovered day without custom JS).
   Single-sleeve chart also switched to `x unified` so sleeve-vs-SPP show
   together, ranked.

Verified: web.py py_compile OK; Streamlit AppTest headless render of all three
views (overview/overlay/single) = 0 exceptions; frozen tests momentum_v1/v2 ×
2023_Q4/2025_H1 all d=±0.0000pp (the new sleeve doesn't touch them); dashboard
restarted (TradingDashboard task) -> HTTP 200. DB now has 9 paper sleeves (8
strategy + spy_benchmark control).

Cadence note: docs updated this prompt (record + state + CLAUDE.md), cadence
not slipped.

Follow-up (same session): user reported the hover %s still showed full
precision. Root cause was not the per-trace `hovertemplate` (`%{y:+.3f}%` —
which `qle`/`hovertemplateString` in the bundled plotly.js does honor) but a
belt-and-suspenders gap: added `yaxis_hoverformat="+.3f"` to all four %-charts
so the hover rounds to 0.001% even on plotly.js builds that don't apply the
template's inline number spec in `x unified` mode. (The other likely factor: a
stale browser tab cached the pre-restart figure — a hard refresh / Ctrl+Shift+R
picks up the new chart.) Dashboard restarted, HTTP 200; overview AppTest 0
exceptions.


# Appendix X - KLAC 10:1 split data-integrity fix + Overview markers (2026-06-11)

Two same-session items. The split fix is the substantive one — same CLASS of
failure as the 2026-05-28 [[data_audit]] contamination (yfinance mishandling a
corporate action), now caught live by a user eyeballing the dashboard.

## X.1 - Overview NAV chart: points back on the line
User: "bring back the points on the graph on the overview tab ... make it like
the nav overlay on the NAV charts tab." The Overview %-from-inception chart used
`mode="lines"`; the NAV-charts overlay uses `mode="lines+markers"`. One-line
change to match (markers restored). Dashboard restarted -> HTTP 200.

## X.2 - KLAC 10:1 split: symptom = Overview "Top movers" showed KLAC +1,029%
User: "KLAC only went up [~13%] today, why does the overview tab say it went up
>1000%."

ROOT CAUSE: KLA Corp 10-for-1 split effective 2026-06-12. yfinance applied the
split adjustment to HISTORY 3-4 days early but not to the latest bar, leaving
`price_cache` in a MIXED frame:
- Jun 8 $210.81, Jun 9 $213.94, Jun 10 $213.56  (already ÷10 = split-adjusted)
- Jun 11 $2,411.64  (un-adjusted, pre-split frame)
The Overview movers panel computes last/prev close = 2411.64 / 213.56 = **+1,029%**.

TWO-PART FIX (both verified):
1. **price_cache** — corrected Jun 11 to **$241.164** (= 2411.64 / 10), pulling
   it into the same split-adjusted frame as Jun 8-10. (Jun 12 not yet on
   yfinance at fix time.) Movers now reads $213.56 -> $241.16 = **+12.9%**, in
   line with the semi rally (LRCX +12.7%, AMAT +11%).
2. **paper_positions** — KLAC is held ONLY by `residual_roa_6535_paper` (id 425).
   Applied the split to the open row: qty **1.15831 -> 11.58314**, entry_price
   **$1,724.92 -> $172.49**, **entry_value UNCHANGED at $1,998.00**. Cost basis
   preserved by construction (qty x price invariant) so the cash ledger is
   untouched.

Then re-MTM'd Jun 8-11 so the historical NAV curve is internally consistent
(corrected qty 11.583 x the already-split-adjusted $210-213 -> KLAC ~$2,442 on
Jun 8-10, not the broken 1.158 x $213 = ~$245 that had carved a ~$2,200 V-dip
into the curve).

VERIFIED:
- Cash recon drift = **$0.0000000000** (formula: starting - SUM(entry_value ALL)
  + SUM(exit_value CLOSED); residual: 100000 - 149387.83 + 49437.37 = 49.54 = cash).
- KLAC marks 11.583 x $241.16 = **$2,793** (vs $1,998 cost = +39.8%), not the
  broken 1.158 x $241 = $279.
- Corrected residual NAV series: Jun 8 $105,685.88 / Jun 9 $106,108.26 /
  Jun 10 $105,764.64 / Jun 11 **$109,011.93 (+9.012%)**.
- The +3.07% Jun-11 day is now LEGITIMATE (KLAC +12.9% on the semi bounce + 49
  other names), NOT the "~$2,530 KLAC artifact" the same-day daily_report.md
  feared. With both qty and price in one frame, the artifact is gone.

PREVENTED: the daily report flagged that an un-split position would mark
1.158 x $241 = $279 on Jun 12 (a fake ~$2,514 loss). The qty fix forecloses that.

GOING FORWARD: `daily_price_refresh` uses `auto_adjust=False`, which still
applies SPLIT adjustments (only dividends are left un-adjusted, per the cache
convention) -> the next refresh keeps Jun 8-11 split-adjusted and consistent
with the corrected qty. No further manual intervention expected. If yfinance
ever re-writes Jun 11 back to a pre-split value, the +1,029% would reappear —
worth a glance after the 6/12 refresh.

Cadence note: docs cadence had slipped ~2-3 prompts across the small dashboard
tweaks (file creation, hover, markers); this Appendix X is the catch-up and
covers the substantive KLAC fix the same prompt it landed. State doc
(state_2026-05-28.md) unchanged — no infra/baseline shift, just a data repair.


# Appendix Y - Docs overhaul: HANDOFF rewrite, record reorganization, HTML render (2026-06-12)

Pure documentation/tooling session. NO strategy/data/sim/trade changes; no
frozen-test-affecting code touched. All work is on docs + the dashboard's
read-only presentation.

## Y.1 - HANDOFF.md fully rewritten
The handoff was badly stale (showed 4 sleeves + pre-June state). Rewrote to
current reality: 9 DB sleeves (5 systematic + 3 LLM-experiment + spy_benchmark),
per-sleeve spec table, backtest performance table, both LLM overlays with current
state (FN position, sector overlay unseeded), corrected infra (var/trades.db not
trading.db, start_all.bat, seed_spy_benchmark.py, scheduled tasks), dashboard
views + chart conventions, the 25+ ruled-out experiments by failure pattern, and
known limitations (incl. the KLAC-style split-artifact risk). Dated 2026-06-12.

## Y.2 - record_2026-05-27.md reorganized (additive only)
> *[EDITORIAL NOTE 2026-06-30 — added after the fact, original text below unchanged:
> this file was renamed to `docs/Project Record — Full Chronological History.md` on
> 2026-06-30, same file, content unchanged. See Appendix AN.]*
User: "without losing any info or hallucinating reformat the record file to be
more organized" → answered "do 2 and 3 and make 3 more of a summary". Chose the
append-only-safe interpretation (honors CLAUDE.md "never edit prior appendices"
+ the no-info-loss constraint): added front-matter, normalized one heading, did
NOT rewrite any body prose. Verified body intact (24 appendices A-X, 8 phases,
2046 -> 2279 lines, +233 lines all front-matter).

Added before Phase 0:
- "How this document is organized" — documents the 2-part scheme (Phases =
  original record, Appendices = append-only chronological addenda).
- Table of Contents — clickable links to every Phase + all 24 Appendices.
  Anchors generated programmatically (GitHub slug algorithm: lowercase, drop
  non-word/space/hyphen, spaces->hyphens, em-dash removal leaves a double hyphen)
  so they resolve, not hand-guessed.
- Thematic digest — the chronological log reorganized by topic (the arc, deployed
  winners table, data-integrity thread, standing lessons). Every figure links to
  the dated entry it summarizes; no new numbers introduced.
- Experiment index — every backtested experiment + verdict (deployed/rejected/
  research-only/running), attempt numbers cited only where the log assigns them.

Normalized: `# APPENDIX A` -> `# Appendix A` (the lone casing outlier; all 24
appendix headers now uniform). Did NOT re-level all ~150 headings (Phases H2 vs
Appendices H1) — that's ~150 edits with real corruption risk for marginal gain
and conflicts with append-only; documented the existing scheme instead.

## Y.3 - Standalone HTML render: docs/record_2026-05-27.html
> *[EDITORIAL NOTE 2026-06-30 — added after the fact, original text below unchanged:
> both `docs/record_2026-05-27.md` and this `.html` were renamed on 2026-06-30 to
> `docs/Project Record — Full Chronological History.md`/`.html` (same files, content
> unchanged). See Appendix AN.]*

User wanted a double-clickable rendered view. Installed the pure-Python
`markdown` package INTO THE PROJECT VENV (`.venv`, markdown 3.10.2) — a new
dependency whose ONLY purpose is this HTML render (not used by any trading code).
Converted with extensions tables/fenced_code/toc/sane_lists/nl2br and a CUSTOM
slugify matching the GitHub anchors above, so the in-doc TOC links resolve in the
HTML. Single self-contained file (embedded CSS, auto light/dark, sticky TOC bar),
~165 KB. Verified all 58 internal links resolve to real heading ids, 0 broken.

Caught + fixed one anchor bug doing this: the L.3 heading has two *literal*
consecutive spaces ("audit  [report"), which markdown collapses to one before
slugifying (single hyphen) while my raw-line TOC slug kept two. Fixed the digest
link to single-hyphen — correct for BOTH the HTML and GitHub (both collapse
consecutive spaces). The em-dash double-hyphens are unaffected (the em-dash char
sits between the spaces, so they're not "consecutive" until it's removed).

The .html is a GENERATED ARTIFACT. Regenerate after any record edit with:
`.venv\Scripts\python.exe -m scripts.render_record_html` (built in Y.6). The
script bakes in the GitHub-matching slugify + embedded CSS + the scroll tweak,
and self-verifies that 0 internal anchors are broken (exits non-zero if any are).

## Y.4 - Anchor scroll position
User: jumped-to sections should land ~1/4 down, not jammed at the top. Set
`scroll-margin-top: 25vh` on h1-h4 (was 16px; briefly 33vh). Now baked into the
render script (Y.6) as SCROLL_MARGIN_TOP, so it survives regeneration.

## Y.5 - daily_report.md
Created an empty `daily_report.md` at repo root as the owner's daily trading
journal (user fills it; it already has several dated entries incl. the 6/11 KLAC
flag the owner wrote). Not generated by code.

## Y.6 - scripts/render_record_html.py (durable render)
> *[EDITORIAL NOTE 2026-06-30 — added after the fact, original text below unchanged:
> the script's hardcoded `record_2026-05-27` paths were updated to match the
> 2026-06-30 rename (`Project Record — Full Chronological History`); see Appendix AN.]*

Built the render script (replacing the throwaway temp converters used in Y.3).
Reads docs/record_2026-05-27.md -> writes docs/record_2026-05-27.html with the
GitHub-matching `gh_slugify`, embedded CSS, and `SCROLL_MARGIN_TOP=25vh` baked
in. Self-verifies anchors (asserts 0 broken internal links; exits non-zero if
any href has no matching id) so a future record edit that desyncs the TOC fails
loudly instead of shipping dead links. Re-rendered after adding this Appendix Y:
59 links, 192 ids, 0 broken. It is the ONLY consumer of the venv `markdown`
package (markdown 3.10.2, installed this session purely for the render).

Cadence note: this Appendix Y is the catch-up for the docs-overhaul prompts since
X (handoff, reformat, view-options, html, scroll x2). State doc unchanged — no
infra/baseline/strategy shift, only documentation + presentation.

---

# Appendix Z - KLAC split self-heal, held-position seam verifier, sector-overlay seeded (2026-06-12)

New session (handoff-driven). Brought data current, closed two loose ends from
the handoff (the KLAC split watch + seeding the macro sector overlay), and built
a reusable data-integrity check. The 6/12 session landed mid-work (~5:30pm), so
all numbers below are 2026-06-12 close.

## Z.1 - KLAC 10:1 split SELF-HEALED on the 6/12 refresh (loose end #1 closed)
Appendix X hand-fixed KLAC on 6/11 (position onto the post-split basis; the cache
still had an interior seam: 06-05 $1929 -> 06-08 $211). The watch item was: after
the first post-6/12 refresh, check whether yfinance re-wrote the recent bars and
re-broke the mark. It did NOT re-break — it self-healed the RIGHT way: the 6/12
refresh divided the OLD bars down onto the post-split basis (06-05 $1929->$192.92,
06-04 $2131->$213.11, 06-03 $2125->$212.51), so the whole series is now continuous
at ~$190-254. KLAC 6/12 close $254.54; position qty 11.5831 @ entry $172.49 ->
MTM $2,948; latest/entry = 1.48x (sane). residual_roa_6535 6/12 NAV $110,283.81
(+1.17% on the day, KLAC +5.5%) — continuous, NO 10x error. The leader's NAV is
trustworthy; the feared re-÷10-of-recent-bars did not occur.

## Z.2 - scripts/data_audit/check_held_split_seams.py (new, reusable)
A post-refresh integrity check for split/spike seams in HELD positions, built so
the KLAC-style watch is a command, not an eyeball of the dashboard movers panel.
Two checks per open position (last 8 closes):
  1. SEAM — any consecutive-day move beyond [0.5x, 2x]. FAIL (exit 1) if the seam
     touches the LATEST bar (live mark on a broken basis NOW); WARN (exit 0) for
     an interior seam (cosmetic for the current mark, real in history).
  2. BASIS — latest_close / entry_price outside [0.2x, 5x]. FAIL. This was added
     AFTER I caught my own blind spot: a UNIFORM rescale of the whole series (what
     yfinance just did to KLAC) leaves NO day-over-day seam for check 1 to see,
     yet would mark a live position ~Nx wrong. The position's entry_price is the
     split-consistent anchor (the hand-fix keeps it so), so it's the right
     yardstick. Band is safe for monthly sleeves (a held name moving >5x or <0.2x
     from entry in weeks is implausible from real price action); documented that
     long holds could legitimately exceed it. Read-only. Current run: OK (no seam,
     every held name within band). If a future refresh re-breaks a split, this
     exits 1 with the offending name + ladder.

## Z.3 - Sector macro-overlay SEEDED (loose end #2 closed)
llm_overlay_sector_top4_paper had been built 06-05 but never seeded (cash, 0
decisions) — so it was accruing no forward data on the macro-veto test it exists
for. Seeded as-of 2026-06-12. Decided per-user to source the macro view from LIVE
WEB (vs internal-only): the WebSearch tool confirmed "current month is June 2026",
so web macro is coherent with the sim's dates. Honest caveat logged: web calls are
not as reproducible later as a technicals-only call would be (matters for the
"did scores predict returns" audit), and I cannot vet June-2026 macro against my
Jan-2026 training — accepted the tradeoff at user direction.

Candidates(2026-06-12) = XLK, XLE, XLI, XLB — identical to the control's current
holdings, so the treatment differs from sector_top4_paper ONLY by the veto.
Live-web macro read (≈6/12): Fed on hold ~97% for 6/16-17, funds 3.50-3.75%, cuts
pushed to Q3/Q4; 2Y 3.94% / 10Y 4.41% (higher-for-longer); USD strengthening (DXY
~100, golden cross) = commodity headwind; oil a Strait-of-Hormuz supply-shock
trade with EIA seeing 2026 demand -1.1mb/d + later oversupply. Decisions logged to
sector_overlay_log (one per sector):
  - XLE VETO  score 3 — rally is a fragile geopolitical-supply trade, price
    already diverging (below 50DMA, RSI 41, flat 3m), USD headwind. Slot -> cash.
  - XLK HOLD  score 7 inval 165 — strongest momentum, NOT overbought (RSI 54,
    -7.6% off highs); AI capex intact, valuations rich but trend healthy.
  - XLI HOLD  score 8 inval 170 — best macro story (data-center/electrification +
    reshoring capex), broad, near highs. Cleanest hold.
  - XLB HOLD  score 5 inval 49.5 — marginal: weakest momentum, on its 50DMA, USD
    headwind, but copper/AI-buildout demand intact, not yet broken. Tight stop.
Rebalance (as-of 6/12): BUY XLK 135.21 @ $184.89, XLI 141.83 @ $176.27, XLB 478.87
@ $52.21 ($25k each); XLE 25% slot held as cash. Post-trade NAV $99,962.52
(-0.037% = exactly 5bps half-spread on $75k traded; cash $25,000 + positions
$74,962.52 recon clean). The daily check-invalidation for this sleeve is already
wired in daily.bat (line 62), so the three stops enforce automatically from now.
First falsifiable macro-veto data point: does stepping aside from XLE help vs the
control over the next month? Honest prior (unchanged): expect the overlay to fail
its kill switch; macro is the lowest-edge use of an LLM.

## Z.4 - Automation of the monthly overlay decision — analysis (build pending user choice)
User asked that the LLM veto/approve "happen automatically without the need for
user input" when rebalances hit. Mapped the existing wiring: daily.bat already
automates ALL daily mechanics (MTM + both overlays' check-invalidation);
rebalance.bat already executes both overlay rebalances — but it REFUSES the
overlay rebalance until HOLD/VETO decisions are logged. So the ONLY manual,
human-in-the-loop step is the monthly decision itself, which inherently needs an
LLM-with-web at decision time. Three ways to automate it: (A) headless `claude`
CLI on a schedule, (B) a Python script calling the Anthropic API with web search,
(C) an in-session autonomous routine I run when a rebalance happens (live-web
research -> decide -> rebalance, no calls asked of the user). Probed this machine:
the `claude` CLI is NOT on PATH and ANTHROPIC_API_KEY is NOT set, so (A) and (B)
need the user to provision a credential first. (C) is buildable now with zero new
infra and matches the experiment's "Claude-in-the-loop" design. Left as an open
question to the user: build (C) now, and/or set up (A)/(B) once a credential
exists. No code written for this yet.

## Z.5 - Cadence + frozen tests
This Appendix Z is the 3-prompt cadence update for this session. No strategy or
factor code was touched (the verifier is a new standalone audit script; the
sector-overlay seeding is data writes via existing, unchanged strategy code), so
the frozen regression tests are not implicated — ran them anyway as insurance:
still d=±0.0000pp. State snapshot refreshed for the now-seeded 9th sleeve + 6/12
standings.

---

# Appendix AA - Systemic history-gap data bug: backfill, frozen re-baseline, sleeve re-inception (2026-06-13)

The single biggest data-integrity finding since the founding 2026-05-28 audit.
What started (Appendix Z, via overlay_prep) as a one-off "CIEN phantom" turned
out to be a systemic cache-completeness bug contaminating ~half of every
momentum sleeve's live book. Full chain: discover -> scope -> backfill ->
re-clean -> re-baseline frozen -> re-inception the contaminated sleeves.

## AA.1 - Discovery: CIEN was a phantom, then it wasn't just CIEN
overlay_prep flagged the stock overlay's #1 mom_roa name as CIEN with a
"3m +1267%" — the split/spike tell the runbook warns about. CIEN's cache had
2,263 rows ending 2018-12-28, a 7.3-yr hole, then 45 rows from 2026-04 (the user
asked "what is the CIEN data gap"; confirmed the exact boundaries). The 12-1
momentum lookback (252 ROWS back, not contiguous CALENDAR days) resolved "12mo
ago" to a 2018 $33 bar vs $446 now = +1250% phantom -> z=+12.9 -> ranked #1.

## AA.2 - Scope: it's ~815 tickers incl. AAPL/GOOGL, contaminating live sleeves
Built a recent-contiguity filter (252-rows-back bar must be <420 cal days old)
to size it: it removed 472 names from the universe at 2026-06-12 — but the
lookback bars clustered at 2018-03-05 / 2024-03-05 and the list included AAPL,
GOOGL, AMGN, PG, CSCO, NOC, FN. Year-coverage check confirmed: AAPL/GOOGL/FN/CIEN
each had ~250 rows/yr 2010-2018, ZERO for 2019-2025, then a 45-row 2026 burst —
a partial cache warm (old bulk pull stopped at 2018; daily_refresh only appends
recent), never backfilled. 815 tickers had this signature. Live blast radius
(checked vs open positions): mom_roa_6535 28/50 phantom (56%), mom_v2 24/50
(48%), mom_v1 39/100 (39%), residual_roa 3/50 (6% — idiosyncratic momentum
dodged it, partly why it led), mom_roa_top1 = FN (the entire LLM stock
experiment sat on a phantom). sector_top4 / sector overlay / spy = 0 (ETF-based).

The naive filter BROKE the frozen 2025_H1 test (v1 +0.34pp, v2 -1 trade) because
the frozen baseline was ITSELF mildly phantom-contaminated. Reverted the filter
(repo green) and surfaced the real fork to the user: backfill (root cause) vs
filter (shrink universe, delete real names). Probed yfinance — it HAS the missing
data (AAPL 2021-Q1 returned 61 real rows). User chose **backfill + re-baseline +
re-inception**.

## AA.3 - Backfill (scripts/data_audit/backfill_history_gaps.py)
Target = every ticker with a 2026 close but <200 rows in 2024 OR 2025 (1,556
names). Re-fetched 2019-01-01 -> today via daily_price_refresh._process_batch
(auto_adjust=False, the price_cache convention), INSERT OR REPLACE — fills the
hole + refreshes recent bars, never touches the audit-cleaned pre-2019 data.
**2,249,015 close rows upserted in 1.1 min.** Verified: AAPL/GOOGL/FN/CIEN now
4,015-4,135 rows continuous 2019-2026 (252/yr, matching NVDA). Residual TRUE
phantoms (pre-2019 hist + 2026 burst + missing middle + price>=$5) = **0** — so
backfill ALONE fixed it, no filter needed (the reverted filter stays out; AAPL/
GOOGL remain tradeable with REAL momentum). CIEN's +700% is now REAL (smooth
month-by-month $87 Jan25 -> $580 May26, no jumps) — a legit momentum monster, not
an artifact, so it correctly ranks high now.

## AA.4 - Re-clean + frozen re-baseline
The backfill added some junk-name artifacts (penny-stock zeros/spikes). Ran the
canonical spike detector (find_price_spikes --apply): nulled 614 rows across 133
sub-$5 tickers (all already $5-filter-excluded; hygiene only). Then re-baselined
the frozen tests — the backfill legitimately changes the 2023/2025 universes:
  mom_v1 2023_Q4 +14.4673->+14.5547 (64->70 trades), 2025_H1 +2.3022->+1.8792 (153->156)
  mom_v2 2023_Q4 +14.6655->+14.4062 (36->38 trades), 2025_H1 +12.4171->+10.2194 (93->87)
The 2025_H1 DROPS confirm the old numbers were inflated by phantom holdings.
Updated EXPECTED in test_strategies.py with a dated re-baseline comment; tests
green at d=±0.0000pp.

## AA.5 - Re-inception of the 6 contaminated sleeves (clean from 2026-06-12)
Archived all 6 sleeves' full pre-reset state to var/reinception_archive_2026-06-13.json
(archive_contaminated_sleeves.py), then wiped positions/NAV/portfolio and re-init
$100k (reinception_wipe.py --confirm). Rebalanced on clean data as-of 2026-06-12
(today=6/13 is a Saturday, empty universe -> used the last session):
  mom_v1 (100), mom_v2 (50), mom_roa_6535 (50), residual_roa_6535 (50) — all
  filled to target, NAV $99,950.07 (-0.05% = 5bps entry spread). New holdings
  phantom-free: the 6/2/1/1 "gappy"-flagged names (BMNR/INBX/PACS/RHLD/MBX/RAPP/
  FGMC) are LEGIT recent IPOs (first dates 2024-25, lookback bar 2025-06-11 = a
  real ~1yr-old bar), not stale-bar phantoms.
LLM stock pair restarted on the new clean #1 = **AAOI** (Applied Optoelectronics,
z=+9.08, $169.05): control mom_roa_top1 BUY AAOI 590.65 @ $169.13 ($99,950);
treatment llm_overlay = **VETO** (score 4, inval $150) — live-web read: real
AI-optics fundamentals (record Q1'26 rev, raised 2026 guide >$1.1B, 800G/1.6T
orders > capacity) BUT ~110-215x fwd earnings WITH net losses after a +936% 12m
run, momentum rolling over (-24% 1m), analyst PTs at/below spot -> poor 1-month
risk/reward. Treatment holds $100k cash. The 3 ETF-based clean sleeves
(sector_top4, llm_overlay_sector_top4, spy_benchmark) were NOT touched — they
keep their 2026-05-01/06-05 history.

## AA.6 - State after this appendix + LOOSE ENDS
9 sleeves: 6 re-inceptioned fresh at $100k (2026-06-12, clean data); 3 clean
sleeves retain prior history. New files: backfill_history_gaps.py,
archive_contaminated_sleeves.py, reinception_wipe.py (data_audit). Deleted the
orphaned find_history_gaps.py (scaffolding for the rejected filter; backfill
--dry-run is the gap reporter now).
LOOSE ENDS this created:
  1. The HELD-OUT / IN-SAMPLE strategy numbers (residual +30.84%, mom_roa
     +36.47%, etc. in HANDOFF) were measured on CONTAMINATED data and are now
     STALE — they need full re-validation on the backfilled cache. Not done this
     session (a large multi-backtest re-run). Do NOT trust them until re-measured.
  2. 388 tickers remain "gappy" (yfinance couldn't fill — delisted/SPAC-units/
     recent IPOs); 0 are true phantoms (none have pre-2019+missing-middle+price>=5).
  3. The contaminated 2026-05-01 -> 06-12 forward track record of the 6 sleeves
     is preserved in the archive JSON but is invalid (phantom-selected); the
     trustworthy forward record restarts 2026-06-12.
Cadence: this is a catch-up entry (the session ran long on one continuous thread:
verifier -> overlay automation -> sector seed -> CIEN -> this). State doc:
new docs/state_2026-06-13.md supersedes 2026-06-12.

---

# Appendix AB - Strategy re-validation on backfilled clean data (2026-06-13)

Closed Appendix AA's biggest loose end: re-ran the full in-sample / held-out
validation for all 5 systematic strategies on the backfilled cache, same
methodology as v1_vs_v2_clean.py (scripts/data_audit/revalidate_strategies.py,
sequential — never concurrent factor_backtest; 5 min, 15 backtests). Full report:
docs/revalidation_2026-06-13.md; raw: var/data_audit/revalidate_2026-06-13.json.

**New clean CAGR vs stale (in-sample / held-out):** residual_roa_6535 9.47/32.07
(+0.6/+1.2), mom_roa_6535 4.89/35.59 (**-4.97**/-0.9), sector_top4 8.14/17.59
(+0.3/**-0.00**), mom_v1 5.91/24.23 (+1.2/+2.2), mom_v2 3.54/26.47 (+0.8/-1.5).

**Verdict:** picture clarified, didn't collapse. **residual_roa_6535's lead is
CONFIRMED REAL** (6% contaminated, barely moved; now in-sample champion + best
risk-adjusted held-out: Sharpe 1.21, Calmar 1.60, -20% DD vs peers' -30%+). The
big correction is **mom_roa_6535: in-sample HALVED (9.86->4.89)** — its in-sample
edge was phantom-inflated (most-contaminated sleeve, 56%); held-out still #1 raw
CAGR, so re-frame it as a held-out/recent-regime specialist, not all-weather.
**sector_top4 held-out -0.00pp** = methodology sanity check (ETF-only, untouched by
a stock backfill). mom_v1 improved (phantoms were a drag); mom_v2 mixed. No sleeve
invalidated; live lineup unchanged.

**Honest caveats (the analysis was done inline — a 10-agent verification workflow
was attempted but hit a transient server rate-limit; the adversarial angles were
folded in by hand):** (1) SURVIVORSHIP BIAS is now the dominant limit — the
backfill filled only currently-listed survivors, so the 2019-2026 universe
excludes 2019-25 delistings -> all CAGRs are inflated upper bounds. (2) Held-out
may be concentration-driven (a few backfilled survivor-IPO moonshots like
BMNR/INBX/PACS). (3) ROA fundamentals were NOT backfilled (price-only), so the
mom_roa/residual in-sample ROA component may be thin. The live paper-trade (clean
from 06-12) remains the only true forward OOS test.

---

# Appendix AC - Sleeve backdate to 05-01, slippage realism, unattended-cron scaffold (2026-06-13)

User: "backdate all the sleeves on the live trader to may 1st then tackle
everything but the survivorship limit."

## AC.1 - Backdated the 4 systematic sleeves to 2026-05-01 (clean data)
The re-inception (Appendix AA) had restarted the contaminated sleeves at 06-12.
Reconstructed their CLEAN track record from their true 05-01 inception so they
align with the untouched sleeves. scripts/data_audit/backdate_sleeves.py (one
process, preload once, replay): wipe + re-init $100k, rebalance on the real
historical cadence (05-01 and 06-03 — confirmed from the archived entry_dates),
MTM every trading day 05-01..06-12 (30 rows). Results (continuous, 0 NAV jumps):
mom_v1 +2.36%, mom_v2 +1.39%, mom_roa_6535 +6.58%, residual_roa_6535 +6.13%.
Notable: residual's clean live return is +6.13% vs the contaminated +10.28% over
the same window — its apparent live lead was partly phantom-SELECTION inflation
(it had picked different, better-performing names on dirty data). On clean data
mom_roa (+6.58%) edges residual (+6.13%), consistent with the re-validation.

**LLM pair NOT backdated (deliberate, flagged to user).** The stock experiment's
treatment acts only on logged, hindsight-free decisions; fabricating 05-01/06-03
BUY/VETO calls now (knowing the outcomes) would inject lookahead and destroy the
falsifiability that is the experiment's whole point — and backdating only the
mechanical control would break the control-vs-treatment pairing. So mom_roa_top1
+ llm_overlay_mom_roa_top1 stay at their clean 06-12 re-inception. Final state:
7 sleeves aligned at 05-01 (5 systematic + spy + sector overlay at 06-05), LLM
stock pair at 06-12.

## AC.2 - Slippage realism (scripts/data_audit/slippage_realism.py)
The real slippage_tracker needs ~20 real broker fills (post-Aug 2026); the
until-then proxy = a TC-sensitivity sweep on clean data for the two best sleeves.
**Edge is ROBUST to realistic-to-pessimistic costs (held-out):** residual_roa
+32.07%(5bps) -> +28.33%(40bps); mom_roa_6535 +35.59% -> +32.24%. Only ~3.5pp
CAGR cost at 40bps half-spread (80bps round-trip, 8x the 5bps assumption); at a
realistic 15bps the edge is essentially intact. Not TC-fragile. GAP: per-name
dollar-volume isn't warmed in the cache (volume cached for 0/134 held names), so
the ADV/liquidity-bucket analysis couldn't run — warming volumes (scripts/
momentum/warm/warm_volumes.py) is a prerequisite, deferred (the TC robustness
makes it less critical).

## AC.3 - Fully-unattended cron scaffold (Option B) - UNTESTED pending credential
Built scripts/momentum/overlay_auto_decide.py + monthly_auto.bat: a headless
path that makes the monthly LLM veto/approve via the Anthropic API
(claude-opus-4-8 + web_search server tool, two-step research->structured-verdict),
logs decisions via the existing record_decision functions, then rebalance.bat
runs. Consulted the claude-api skill for correct API usage. NOT executed
end-to-end — neither `anthropic` (pip) nor ANTHROPIC_API_KEY is present on this
box. Verified the SAFE-FAIL path only: missing module/key -> logs nothing ->
exits 1 -> rebalance refuses the overlays (no bad trade possible). Activation
(pip install anthropic + set key + smoke-test --dry-run + schedule) documented in
docs/overlay_decision_runbook.md "Option B activation". The in-session Option A
remains the lower-risk default.

## AC.4 - Cadence
Loose ends now: survivorship (un-fixable without PIT data, user said skip);
volume-warming for the ADV liquidity check (new, minor); slippage tracker
(post-Aug real fills); Option B cron (needs a credential); July rebalance
(future). State + HANDOFF updated for the backdated 05-01 standings.

# Appendix AD - ADV liquidity gap closed; daily volume-staleness finding (2026-06-13)

Closed AC.2's "volume cached for 0/134" loose end and, in doing so, corrected the
diagnosis behind it.

## AD.1 - The "0/134" was a stale-volume artifact, not a missing cache
The cache actually has volume for ~5,818 of 5,875 tickers; every held STOCK had
volume rows. The snapshot read 0/134 because `universe.median_dollar_volume`
needs a COMPLETE 60-trading-day window ending `as_of` (any missing day -> None),
and volume was frozen at ~2026-05-01: **`daily_price_refresh` writes closes every
day but never persists volume**, so the close cache marches to 06-12 while volume
stops at the last `warm_volumes` run. The 60-day ADV window ending 06-12 was
therefore incomplete for ~every name -> all None -> 0/134. Held STOCK sample:
73 cached closes vs 43 cached volumes in 2026-03-01..06-12.

## AD.2 - Scope check: live universe NOT affected
`universe.MIN_DOLLAR_VOL = 0` -> the dollar-volume filter is OFF, so a None ADV
never excludes a name from the tradeable universe in any deployed path. That is
why the 06-03 backdated rebalance built a normal portfolio despite stale volume.
The gap is **diagnostic-only**; it would only bite a backtest that explicitly
sets `min_dollar_vol > 0` (none of the five deployed strategies do).

## AD.3 - Fix + the real liquidity read
Targeted recent-window volume warm for the 139 held names (2026-02-15..06-13,
11,398 rows, reusing warm_volumes' tested download path), then re-ran just
`liquidity_snapshot()`. Held names across the 4 systematic sleeves are LIQUID in
the median: **median 60-day ADV = $100.6M**; buckets >$50M:80, $10-50M:23,
$1-10M:16, **<$1M:5** (124/134 now have a full window, 10 still sparse). Thin
tail: PTN $183k/day, FGMC $417k, NRT $479k, CMTV $745k, SNSE $829k. At the
current $100k/sleeve scale (~$2k/position) even the thinnest name is ~1% of a
day's volume -> the 5bps assumption is well-supported now; the thin tail is a
flag only IF a sleeve is ever scaled to 7-8 figures. var/data_audit/
slippage_realism.json liquidity block updated (tc_sweep untouched).

## AD.4 - Open recommendation (NOT silently implemented)
The root cause — `daily_price_refresh` not persisting volume — means the volume
cache will always drift stale. Since `MIN_DOLLAR_VOL = 0` this has no live
impact, so the cheap options are a tradeoff for the user, not an auto-fix: (a)
leave it and re-warm volume on demand before an ADV check (what was done here);
(b) add a monthly `warm_volumes` step to the rebalance flow to keep the cache
fresh; or (c) make `daily_price_refresh` persist volume alongside closes (most
correct, but touches the daily pipeline + roughly doubles its write volume).
Recommend (b) if the ADV check becomes routine, else (a). Frozen tests green
(volume rows don't touch the close-based momentum path; verified ±0.0000pp).

# Appendix AE - Volume-staleness fix: monthly held-name warm wired into rebalance (option b) (2026-06-14)

User picked option (b) from AD.4. Implemented as a NEW permanent script
`scripts/momentum/warm/warm_held_volumes.py`, wired into `rebalance.bat` as the
last step (after all rebalances + MTM, so it tops up volume for the NEW
holdings).

Scope decision (held-names-only, NOT universe-wide): MIN_DOLLAR_VOL=0, so the
live `tradeable_universe` build never reads volume — the only consumer is the ADV
diagnostic over held names. Warming the full ~5,800-name universe monthly would
be ~21 min + rate-limit-prone for data nothing reads; the held-name warm is ~140
names / ~1 min / 3 batches, reusing warm_volumes' tested download path. The
script is best-effort (never raises -> can't abort the monthly batch) and runs
last anyway. It warms a 130-calendar-day window (covers the 60-trading-day ADV
lookback with slack) and prints how many held names now have a full window. If
MIN_DOLLAR_VOL is ever turned on, switch to the universe-wide warm_volumes.py.

Smoke-tested standalone: 12,510 rows, 129/139 held names with a full 60d window
(the ~10 short are recent IPOs/SPACs with <60 trading days — handled as None).
Frozen tests unaffected (no strategy/universe code touched; volume rows don't
enter the close-based momentum path).

# Appendix AF - Daily trade check: Iran peace deal, SEZL +14.4%, MU hits $1T (2026-06-15)

Automated scheduled task ran. daily_report.md updated with June 15 entry (no sleeve
NAV for the day — awaiting daily.bat 5:15pm MTM run).

Key events since June 12 close:
- US-Iran peace deal announced June 14-15 (signing Geneva June 19). WTI crude −5.5%
  to ~$80. Energy stocks (APA −3.5%+) face direct headwind; residual_roa energy cluster
  (~15% weight) is net drag of ~−0.45% on June 15.
- S&P +1.49%, Nasdaq +2.38% on June 15. Semi equipment surge: LRCX +7.7%, INTC +3.2%,
  MU up to ~$1,057 (+7.7% from June 12). MU market cap hit $1T in 48 days (fastest ever).
- SEZL +14.4% on June 14 after product-launch expansion (rewards hub, Pay-in-5, 48mo
  lending, Canada Adyen, Sezzle Mobile). Large positive for residual_roa.
- STX at $985.97 (+5.9%), Mizuho PT $1,090, BofA $1,000, JPMorgan $920. No split
  announced yet; approaching the natural zone.
- AAOI (new control top-1 after re-inception): closed $169.05 June 12, $170.42 June 15
  (+0.81%). LLM treatment in cash (AAOI vetoed). Treatment mildly ahead.
- SPCX (SpaceX): $177.99 June 15 (+10.6% from $160.95 June 12 IPO close). Driver is
  MSCI early-inclusion mechanical buying from $15-20T AUM against 4% free float.
- BE (Bloom Energy): Nebius master agreement up to $2.6B revenue. MS $310 maintained.
  Systematic sleeves that held through Crusoe panic may be vindicated.
- LLM sector overlay XLE veto VINDICATED: energy fell 3.5%+ on June 15; the XLE→cash
  slot saved ~$875 vs the control sleeve. First live data point for macro overlay.

No code changes in this session. No structural structures to any sleeve. Research and
daily_report.md update only.

# Appendix AG - Daily trade check: Juneteenth long weekend gap, MU earnings week (2026-06-22)

Automated scheduled task (daily-trade-check) ran ~8am ET Monday June 22.
daily_report.md updated with June 22 pre-market entry. No code/data/trade changes.

**Calendar note:** June 19, 2026 was Juneteenth (federal holiday — NYSE/NASDAQ closed).
June 18 confirmed as last real trading day. "June 19" NAV rows in paper_nav are Juneteenth
carryovers at June 18 prices; only 204 OTC micro-cap tickers have any June 19 close in
price_cache.

**NAV standings at June 18 close (confirmed baseline):**
- mom_roa_6535: $111,098.78 (+11.10%, +7.48pp vs SPY) — best single session June 18 +2.95%
- residual_roa_6535: $107,920.26 (+7.92%)
- mom_v1: $105,796.70 (+5.80%), mom_v2: $105,690.21 (+5.69%)
- sector_top4: $103,726.38 (+3.73%), spy_benchmark: $103,620.34 (+3.62%)
- llm_overlay_sector_top4: $101,354.01 (+1.35%)
- llm_overlay_mom_roa_top1 (cash): $100,000.00 (0.00%)
- mom_roa_top1_paper (AAOI): $95,697.37 (−4.30%)

All 5 systematic sleeves beat SPY on June 18 (+0.78%).

**Key events since June 18:**
- SATS: EchoStar made the deferred $183M interest payment June 18 — Event of Default averted.
  July 1 principal maturity (~$2B 7¾% Notes) remains. July 1 model exit unchanged.
- US-Iran Geneva peace talks POSTPONED June 19 — oil bounced from lows. Energy exits (APA,
  DINO, PARR, NRT, PBR) still targeted July 1; structural IEA supply glut thesis intact.
- MU: +3.04% pre-market June 22 (~$1,168). Earnings Wednesday June 24 AH; consensus EPS
  ~$20.25, Revenue ~$34.5B (+272% YoY). All 46 covering analysts = BUY. Week's defining event.
- INTC: steady ~$134, 4 days without official Apple/Intel press release.
- PRAX: confirmed −13% from entry; POWER1 primary miss June 1; July 1 exit very high probability.
- LLM overlay: AAOI control $95,697 vs treatment (cash) $100,000 = +$4,303 treatment lead.
- July 1 rebalance 9 days out; definite exits: SATS, QDMI, APA, DINO, PARR, NRT, PBR, PRAX,
  CIEN, CBOE, FN; strong holds: MU, WDC, STX, DOCN, INTC, BE, ARWR, AGX, FIX, VRT, ICHR.

Cadence note: standalone scheduled run; record updated same prompt, cadence not slipped.

# Appendix AH - rebalance_log.md + SNSE→FTH ticker-rename corporate action (2026-06-27)

Cadence catch-up: missed the 3-prompt docs cadence by ~1 cycle (the rebalance_log
add below went unrecorded at the time). Two items. (NB: appended as AH — the
06-15/06-22 daily-trade-check runs took AF/AG after my AE.)

## AH.1 - rebalance_log.md (records when the last rebalance happened)
Added repo-root `rebalance_log.md` showing **Last rebalance: <date>** + a tiny
stamper `scripts/momentum/stamp_rebalance_log.py`, wired as the final step of
rebalance.bat so it auto-updates each run (best-effort, never aborts the batch).
Seeded to 2026-06-03 (the last real monthly rebalance trading date — NOT the
06-13 backdate-op timestamp).

## AH.2 - SNSE → FTH ticker rename (the "2 stale holdings")
Dashboard showed "2 stale holdings" (web.py: a holding is stale when its latest
close is >3 days old). Root cause: ONE name, SNSE, held in mom_v1 + mom_v2 (the
dashboard counts per sleeve -> "2"). SNSE's price froze at 2026-06-22.

Why: Sensei Biotherapeutics completed its Faeth reverse-merger, **renamed to
Faeth Therapeutics and changed ticker SNSE -> FTH (effective 2026-06-16)**;
yfinance served the old symbol a few more days then dropped it. Verified the
transition is a clean **1:1 rename, NO reverse split**: FTH and SNSE price/volume
histories are identical through 06-22 (06-22 FTH $23.19 ~ SNSE $23.30), FTH
carries the full series since 2021-02-04, and continues live past the freeze
(06-23 $24.00 -> 06-26 $22.87). Series B PREFERRED conversion (06-15) hit
preferred holders, not existing common — common is continuous 1:1.

Migration (pure symbol rename; mirrors corporate_action_splits playbook but
simpler — no qty/price adjustment): (1) relabel ALL SNSE price_cache rows (3,408
across every kind) -> FTH (FTH had 0 rows, no PK collision; avoids a duplicate
identical series that would double-list in historical backtests); (2) warm FTH's
4 missing post-freeze days 06-23..06-26 (auto_adjust=False); (3) relabel the 2
paper_positions rows SNSE->FTH (qty/entry_price/entry_value/entry_date untouched
-> cost basis invariant, no cash moved: cash stayed $39.63/$36.60); (4) re-MTM
mom_v1 + mom_v2 for 06-23..06-26 (INSERT OR REPLACE) so paper_nav reflects FTH's
real closes instead of the stale $23.30. SNSE now has 0 cache rows; FTH spans
2021-02-04..2026-06-26 (1,354 closes). Verified: dashboard n_stale 2 -> 0, FTH
fresh, positions still counted (100/50), and **frozen tests green at ±0.0000pp**
(the relabel is invisible — same prices, no tie-break shift, and SNSE wasn't a
selection in the 2023_Q4 / 2025_H1 windows).

# Appendix AI - Graph-driven workflow optimization: daily refresh persists volume (supersedes AE) (2026-06-27)

User: "using the graph try to optimize the workflow." Rebuilt code graph (now
covers scripts/, 1,272 nodes) surfaced two signals: god nodes = the hot paths
(db.connect 76, factor_backtest, config, market_data, momentum, paper_rebalance),
and heavy duplication. Most duplication (_sharpe_by_year 34x, _max_drawdown 29x,
run_one 28x) is in scripts/momentum/research/ (the frozen failed-sleeve archive)
— deliberately NOT refactored (high churn, zero live-workflow value, surgical).

The duplication that touched the LIVE workflow was the data-pipeline cluster
(_download / _bulk_insert / _process_batch across daily_price_refresh + the
warm_* scripts), which pointed at a concrete RUNTIME waste: rebalance.bat
downloaded overlapping yfinance data TWICE — daily_price_refresh (closes) then
warm_held_volumes (volume) — even though `_process_batch` already had the whole
OHLCV frame in hand and threw Volume away.

**Fix:** `daily_price_refresh._process_batch` now persists Volume alongside Close
from the same download (raw shares, split-unadjusted, INSERT OR REPLACE). Removed
the warm_held_volumes step from rebalance.bat (script kept as a manual backstop).
Net effect: volume is now fresh DAILY for the whole universe at ZERO extra
download cost (it was already fetched), the monthly workflow drops a yfinance
pass, and the volume-staleness root cause behind AD/AE is gone — so this
**supersedes Appendix AE** (the monthly held-name warm, option b). The earlier
(b) choice was the right call under its framing (minor diagnostic gap, don't
touch the daily pipeline); the explicit "optimize the workflow" ask changed the
calculus, and (c) — persist in the daily refresh — strictly dominates it.

Verified: _process_batch on AAPL/MSFT/NVDA now writes close AND volume to the
same latest date (06-26); frozen tests green ±0.0000pp (volume is inert to the
close-based momentum path). Reversible: re-add the bat line to restore AE.

# Appendix AJ - June-30 lock prep: KLAC split, SATS->ECHO, AAOI verify, overlay evals (2026-06-29)

Four critical items flagged for the June 30 score lock. Today = 06-29; lock MTM
is 06-30; next rebalance 07-01.

## AJ.1 - KLAC 10:1 split: residual_roa position was unadjusted (FIXED)
residual_roa_6535_paper held KLAC qty 1.157 @ entry $1727.12 (the pre-split 05-01
price), marked at the post-split close $278.39 = ~$322 — understated. The 06-13
backdate re-created the position at the pre-split entry without split adjustment
(the 06-12 self-heal in Appendix Z only fixed then-existing rows). Confirmed 10:1
two ways: $1727.12/10 = $172.71, and the cited ~$2,898 = (qty x10 - qty) x $278.39.
Applied the corporate_action_splits playbook: qty x10 -> 11.5684, entry /10 ->
$172.71, entry_value UNCHANGED $1998 (cost-basis invariant, cash untouched).
residual_roa re-MTM'd: NAV $108,873 -> **$111,771 (+11.77%)** — now the live
leader, ahead of mom_roa_6535 ($110,357).

OPEN (pre-07-01, NOT lock-critical): KLAC price_cache still has a pre/post-split
SEAM — May-1 close $1726 (pre-split, outside daily_price_refresh's 30d window)
vs June $210-278 (post-split, refreshed). MTM uses the latest close so the lock
is fine, but the 07-01 momentum rank will see KLAC's 12-1 return across the seam
(~-84% garbage). Fix before 07-01 rebalance: divide KLAC closes before the seam
(~2026-05-30) by 10. Flagged, not done tonight (broad cache mutation, not lock-
critical, wanted seam-date precision over a rushed edit).

## AJ.2 - SATS -> ECHO ticker rename (FIXED)
EchoStar renamed ticker SATS -> ECHO eff 2026-06-24 (CUSIP unchanged -> pure 1:1,
web-confirmed; SATS & ECHO yfinance prices identical $109.17->$100.84). Held in
mom_v1/mom_v2/mom_roa_6535. Migration: first DELETED 218 STALE rows for the OLD
ECHO (Echo Global Logistics, delisted 2021 — derived kinds only, no closes; must
not conflate), then relabeled SATS cache (8,612 rows) + 3 positions -> ECHO,
warmed ECHO recent days. ECHO now spans 2010-01-04..2026-06-29 (4,146 closes);
SATS gone. Three sleeves re-MTM'd. (Same playbook as the FTH/SNSE rename, Appendix
AH — variant now in memory/corporate_action_splits.)

## AJ.3 - AAOI price ($150.10 vs web ~$136.88): NOT a cache bug (UNRESOLVED)
The cache 06-29 close $150.10 was flagged as suspect. Verified: **yfinance itself
returns $150.10** (vol 10.3M) — the cache matches its own canonical source, so it
is NOT corrupt. The web search showed an intraday range $127.01-$140.83 / ~$136.88
that conflicts with (is below) yfinance's value. Could not authoritatively
reconcile yfinance vs web; AAOI is hyper-volatile (this sleeve swung +13pct then
-17pct in single days, Appendix). Did NOT overwrite the canonical pipeline value
with a web snapshot. mom_roa_top1 holds 590 AAOI -> ~$7,800 NAV swing at stake.
RECOMMENDATION: eyeball AAOI's 06-30 close at lock; the lock MTM uses 06-30, not
06-29, so the 06-29 discrepancy is superseded at lock time anyway.

## AJ.4 - LLM overlay evals (DONE, logged for 07-01)
Ran overlay_prep. Stock #1 changed AAOI -> **BE** (Bloom Energy, z=+9.26); sector
top-4 = XLK/XLE/XLI/XLB (all owed). Macro read (live web): Fed held 3.50-3.75pct
but new Chair Warsh HAWKISH (9 members project >=1 hike 2026, core PCE 3.0->3.3pct,
10Y 4.49pct); oil ~$70 SOFT (US-Iran de-escalation removed war premium, demand
-1.1mb/d). Option-A decisions logged dated 07-01 (pre-committed, no lookahead):
- **BE -> VETO (4)**: real accelerating fundamentals (FY26 rev guide $3.4-3.8B
  ~80pct YoY; Nebius $2.6B/328MW + Oracle/AEP AI-datacenter deals) BUT ~128x fwd
  EPS, trading at/above mean analyst PT (~$267 vs ~$275), momentum cooling (1m
  -5.2pct, -20.5pct off 52wHi) into hawkish Fed. Priced-for-perfection + cooling.
- **XLK -> HOLD (7)** inval 174: strongest mom (3m +42.7pct), not overbought
  (RSI 51), AI-capex intact.
- **XLE -> VETO (3)**: momentum fading (below 50DMA, RSI 26, 3m -14.4pct) AND
  soft-oil/de-escalation macro headwind. Textbook macro-risk veto; prior vindicated.
- **XLI -> HOLD (7)** inval 172: broad strength near 52wHi, +5.2pct 1m, reshoring/
  AI-infra capex.
- **XLB -> HOLD (5)** inval 48: marginal (below 50DMA, USD headwind) but 3m +3.6pct
  positive; coin-flip, no manufactured veto.

Frozen tests green ±0.0000pp after all DB changes (the SATS->ECHO relabel is
invisible to the 2023_Q4/2025_H1 windows — same prices). KLAC cache-seam rebase
is the one open follow-up before the 07-01 rebalance.

# Appendix AK - LLM-cascade sleeves (always-invested 3rd overlay pair) + dashboard fixes (2026-06-30)

## AK.1 - Dashboard tightening (this session)
Several dashboard refinements: refresh-interval slider widened to a select_slider
(5s..1d); a "Data refreshed N ago" caption (marker stamped by daily_price_refresh,
falls back to last_daily_run.log mtime); a live "Page refreshed N ago" timer
(client-side components.html iframe, updates on mousemove throttled 500ms, 1m idle
backstop); "Refresh now" now does st.cache_data.clear() (fresh DB re-read) + resets
the page timer. **Ghost fix:** the "ghost of past screens stacking at the bottom"
was the auto-refresh — the old time.sleep()+st.rerun() blocked the thread and left
stale DOM each cycle (Evan confirmed auto-refresh was ON). Replaced with a
non-blocking st.fragment(run_every=) timer (gated by a timestamp so it can't
tight-loop) that triggers a clean st.rerun(scope="app").

## AK.2 - LLM-cascade: the 'always invested' 3rd overlay pair
User wanted the overlays to cascade to the next-best on a veto instead of going to
cash. Because that changes WHAT the experiment measures (risk-veto -> active
selection), built it as a THIRD pair run ALONGSIDE the cash overlays (not a
replacement) so the clean veto-vs-cash signal is preserved. Two new $100k sleeves
(inception 2026-07-01), controls shared with the cash overlays:
- `llm_cascade_top1_paper`  (vs control mom_roa_top1_paper)
- `llm_cascade_sector4_paper` (vs control sector_top4_paper)

Design (trading_bot/strategies/llm_cascade.py + scripts/momentum/llm_cascade_ops.py):
- **Always invested via cascade.** Stock: hold the first BUY walking down the top-10
  mom_roa names; if none approved, fall back to the raw #1. Sector: hold the first 4
  HOLD sectors walking down all 11; if <4 approved, momentum-fill the rest.
- **Decisions SHARED with the cash overlays' logs** (llm_overlay_log /
  sector_overlay_log) — a BUY/VETO judgment on a name is identical regardless of
  which sleeve consumes it, so no double-logging; the cascade just reads deeper.
- **Safety fix:** the stock cash sleeve used llm_overlay.decision_for(date) (LIMIT 1),
  which becomes ambiguous once the cascade logs several names per date. Added
  decision_for_ticker(date, ticker) and switched the cash overlay rebalance to look
  up ITS candidate (#1) specifically. (Sector already used a per-ticker dict, safe.)
- **No intra-month stops** on the cascade (a stop->cash would contradict
  always-invested); it holds its picks until the next monthly rebalance.
- Wired into rebalance.bat (rebalance + MTM) and daily.bat (MTM only). Dashboard
  auto-discovers them (+ short labels casc_top1 / casc_sec4). 11 sleeves now.

Honest prior (stated in the module): the bar is HIGHER than the cash version —
control already holds momentum #1/top-4, so the cascade can only differ by replacing
a high-momentum name with a LOWER one the LLM prefers, i.e. it must out-PICK raw
momentum. Same 12mo / >=30-pick kill switch.

Verified: dry-run both rebalances as-of 06-29 (no decisions that date -> stock
falls back to BE #1, sector momentum-fills XLK/XLE/XLI/XLB = equals control, the
correct degenerate). Frozen tests green +-0.0000pp. **OPEN before they DIVERGE on
07-01:** decisions must be logged DEEPER in the ranking (stock #2+ since BE #1 is
VETOed; sector #5 since only 3 of the top-4 are HOLD) — overlay_prep still only
prints #1 / top-4, so a deeper-candidates view + those extra evals are the
remaining step.

## AK.3 - overlay_prep deeper view + cascade primed for 07-01
Extended overlay_prep with a CASCADE section: walks the stock top-10 (until a BUY)
and all 11 sectors (until 4 HOLDs), showing each candidate's logged decision. Stock
ranking: BE, SLGL, WDC, MU, VICR, PL, AEHR, STX, CIEN, PRAX; sector #5 XLY, #6 XLV.
Did the deeper Option-A evals (live web), logged for 07-01:
- **SLGL #2 -> VETO (3)**: pre-revenue single-asset biotech, binary Phase-3 Q4 2026.
- **WDC #3 -> BUY (7) inval 560** = stock cascade PICK: AI-HDD supercycle, +45pct YoY
  rev, capacity committed to 2028-29, EPS revisions +70pct; rich but accelerating.
- **XLY #5 -> VETO (4)**: weakening consumer + rate headwind.
- **XLV #6 -> HOLD (6) inval 150** = sector cascade 4th: defensive rotation, hawkish
  regime. Cascade resolves: stock = WDC; sector = XLK/XLI/XLB/XLV (verified).

## AK.4 - SCHEMA BUG found + fixed (llm_overlay_log single-key)
Logging several stock names for 07-01 silently collapsed to one row: llm_overlay_log
had `UNIQUE (decision_date)` (built for the single-name overlay), so each INSERT OR
REPLACE overwrote the prior — and it had ALSO wiped the lock-prep BE VETO. This would
have broken the cash overlay too (after AK.2's decision_for_ticker switch, no BE
decision -> refuse). Fixed: migrated llm_overlay_log to `UNIQUE (decision_date,
ticker)` (matches sector_overlay_log; recreate+copy, existing rows had distinct dates
so no conflict), updated the DDL in db.py, re-logged BE + SLGL. Verified 07-01 holds
BE VETO / SLGL VETO / WDC BUY; cash overlay BE lookup = VETO.

## AK.5 - One-time alignment reset of all 6 LLM-experiment sleeves to 07-01
User chose to align ALL six LLM-experiment sleeves to a fresh $100k / 07-01 inception
(head-to-head from one date, then cumulative). scripts/data_audit/align_llm_07_01.py
archived current state (var/align_llm_07_01_archive.json — reversible) then wiped +
re-inited at $100k / inception 07-01: mom_roa_top1, llm_overlay_mom_roa_top1,
llm_cascade_top1, sector_top4, llm_overlay_sector_top4, llm_cascade_sector4. Decision
logs NOT touched. **CAVEAT carried to the user:** sector_top4 is ALSO a core
systematic sleeve — resetting it desyncs it from the other 4 systematic sleeves
(still 05-01) in the systematic comparison; reversible from the archive if unintended.
07-01 deployment: control mom_roa_top1->BE; cash stock overlay->cash (BE vetoed);
stock cascade->WDC; control sector_top4->XLK/XLE/XLI/XLB; cash sector overlay->
XLK/XLI/XLB (XLE->cash); sector cascade->XLK/XLI/XLB/XLV. Frozen tests green.

## AK.6 - Resolved the sector_top4 desync: TWO sector controls now
The AK.5 caveat (resetting sector_top4 to 07-01 desynced it from the systematic
comparison) is now resolved by keeping BOTH instead of choosing (user: "make 2
sector top 4s, 1 full from the archive and one reset on 7/1"):
- **sector_top4_paper** = the 07-01 reset (unchanged) — the LLM-experiment control,
  head-to-head with the sector overlays/cascade which are all at 07-01. The sector
  overlay CONTROL_STRATEGY still points here, so nothing in the experiment moved.
- **sector_top4_full_paper** = NEW sleeve, restored from var/align_llm_07_01_archive
  .json (the exact pre-reset 05-01 state: 4 open XLI/XLE/XLB/XLK, 41 nav rows
  05-01..06-29, NAV $102,423.84 / +2.42%). The full-history systematic control.
Both rebalance identically going forward (same top-4 momentum sectors); they differ
only in pre-07-01 P&L. Build: scripts/data_audit/restore_sector_full.py (idempotent,
--confirm). paper_rebalance.py's three `== "sector_top4_paper"` checks generalized to
`.startswith("sector_top4")` (config branch, min_universe=11, sector-name tag) so the
new sleeve gets identical handling. rebalance.bat + daily.bat each got a rebalance/MTM
line for the full sleeve; dashboard labels: "sector4 (07-01)" vs "sector4 (full)" (the
full one auto-appears as a selectable systematic sleeve). Frozen tests green
(v1 14.5547/1.8792, v2 14.4062/10.2194, 0.0000pp). Dashboard restarted (HTTP 200).

## AK.7 - Overview hover-box clipping fix + S&P 500 07-01 baseline
Two small follow-ups after the 9th sleeve landed:
- **Hover clip:** the Overview all-sleeves overlay uses Plotly hovermode="x unified",
  so every sleeve stacks into one tooltip; the 9th sleeve pushed the box past the
  350px plot and it clipped at top. Fix (web.py ~2000): height 350->430 + hoverlabel
  font_size=11, namelength=-1. (Offered "closest" hovermode as an alternative.)
- **S&P 500 07-01 baseline:** the 07-01 LLM cohort needed an S&P control that also
  starts 07-01 (the existing spy_benchmark_paper is 05-01). Parameterized
  seed_spy_benchmark.py with --sleeve/--inception (defaults unchanged) and created
  **spy_benchmark_0701_paper** ($100k buy-and-hold SPY, inception 07-01). Today is
  06-30 so there's no 07-01 close yet -> the seed creates a $100k cash stub now and
  the BUY happens on the 07-01 rebalance (idempotent seed wired into rebalance.bat;
  MTM into daily.bat + rebalance.bat). Dashboard: short label "S&P 500 (07-01)";
  is_spy styling generalized to startswith("spy_benchmark") so it renders as a dotted
  gray benchmark line + auto-shaded table row; movers/concentration panels generalized
  to exclude both SPY sleeves (and both sector_top4 sleeves). Frozen tests green.

# Appendix AL - Alpaca paper integration begins + 7/1 clean-start cohort (2026-06-30)
**Project pivot (2026-06-30):** Evan opened an Alpaca PAPER account (ACTIVE, $100k)
and wants the sleeves to trade automatically there, mirroring the DB sim. Age note
re-surfaced (the "local sim until 18" plan): Alpaca paper is still a real brokerage
signup; Evan has the account. Hard lines held: Claude does NOT create accounts, enter
keys, or fire LIVE trades — Evan owns those; automated PAPER routing (no real money)
is in scope.
- **alpaca_client.py (NEW, trading_bot/execution/):** thin httpx REST client (NOT the
  alpaca-py SDK — httpx already a dep). Reads APCA_API_KEY_ID/APCA_API_SECRET_KEY/
  APCA_API_BASE_URL from env; DEFAULTS to the paper host and hard-guards live behind an
  explicit base-url change. get_account/list_positions/list_orders/submit_order(qty|
  notional)/cancel_order. Persists every X-Request-ID to var/alpaca_request_ids.log
  (Alpaca asks you to keep them; not queryable later). `python -m
  trading_bot.execution.alpaca_client` = connectivity smoke test. Evan ran it -> 200,
  account PA... ACTIVE, cash $100k, buying_power $371k (4x paper margin).
- **Alpaca multi-account reality (researched):** one login caps at ~3 paper accounts
  (official docs state no number, but every third-party report = 3). Evan's "10
  accounts, 1 per sleeve" likely won't fit; one account can't isolate per-sleeve P&L
  (positions commingle). DECISION: Evan tests his real cap first, THEN we map sleeves
  to whatever he can create. Alpaca wiring HELD pending that number.
- **7/1 clean-start cohort (DB side, built now):** duplicated the 4 May systematic
  sleeves as fresh $100k/inception-07-01 sleeves — mom_v1_0701_paper (top-100),
  mom_v2_0701_paper, mom_roa_6535_0701_paper, residual_roa_6535_0701_paper (all top-50).
  _strategy_config() now strips the `_0701` infix so a duplicate reuses its base
  sleeve's config (no per-dup branch). Wired into rebalance.bat (rebalance+MTM) +
  daily.bat (MTM); dashboard short labels "... (07-01)". They deploy on the 07-01
  rebalance. (sector_top4 + spy already have 07-01 versions, so the full 7/1 cohort =
  these 4 + sector_top4_paper + spy_benchmark_0701 + the 6 LLM-experiment sleeves.)
  PENDING: a dedicated dashboard "7/1 cohort" panel grouping them — deferred until the
  Alpaca cap is known + cohort membership confirmed, to avoid rework. Frozen green.

## AL.1 - Alpaca routing BUILT: 3 paper accounts, weight-mirror
Cap confirmed = 3 paper accounts/login. Evan created 3, generated keys, all verify
(ACTIVE, $100k each). Mapping (Evan's choice — "mom roa, residual roa, S&P 500"):
ACCT1 residual_roa_6535_0701_paper, ACCT2 mom_roa_6535_0701_paper, ACCT3
spy_benchmark_0701_paper (all 07-01 cohort, aligned with the fresh Alpaca accounts).
- **alpaca_keys.env** (NEW, gitignored via `.env`/`*.env`/explicit): paste-target with
  ALPACA_ACCT{1,2,3}_KEY_ID/_SECRET/_SLEEVE. Keys live ONLY here (never chat/committed).
- **alpaca_accounts.py** (NEW): no-dependency .env loader (doesn't override real env
  vars) + `configured_accounts()` + `account_for_sleeve()`; `python -m ...alpaca_accounts`
  pings all 3 → [OK]/[FAIL].
- **alpaca_sync.py** (NEW): mirrors a DB sleeve into its paper account by TARGET WEIGHTS
  (each DB position's mkt value / total) scaled to the account's own equity, FRACTIONAL
  qty (4dp) → deploys ~100% (validated: $99,999.91 of $100k, $0.09 drag, vs $8.3k drag
  whole-share). Diff vs current Alpaca qty → SELLs (full exit for dropped names) then
  BUYs as market DAY orders; cancels open orders first; per-order try/except so a
  non-fractionable/unknown symbol logs + continues. **DRY-RUN by default; --execute to
  submit. Paper-only (client hard-guards live).** Dry-run against all 3 (empty 0701
  sleeves) → "nothing to do" (plumbing verified live).
- **Wiring:** rebalance.bat now ends with `alpaca_sync --all --execute` (after the DB
  rebalances), so the mirror fires whenever Evan runs the monthly rebalance — same
  trigger as the DB rebalance (rebalance.bat is MANUAL; only daily.bat=MTM is scheduled).
  First real mirror = the 07-01 rebalance. Claude never creates accounts/enters keys/
  fires LIVE; Evan runs the bat.
- **Trigger confirmed:** Evan's `monthy-llm-rebalance` scheduled task (daily 8:03am,
  next 07-01) gates on rebalance_log.md (last=06-03 → fires for July), runs overlay_prep
  then rebalance.bat — which now carries the Alpaca sync. So the mirror fires inside the
  EXISTING routine, no change needed; 8am pre-open => market orders queue to the 9:30 open.

## AL.2 - Overview split into two cohort panels
Overview now renders TWO panels (user: "2 overview panels, one for the original sleeves
and one for the 7/1 sleeves") instead of one combined table+chart. Extracted
`_render_cohort_panel(sleeves, key)` (dense table + %-from-inception NAV chart) and call
it twice: "Original · since 2026-05-01" (6 sleeves) and "7/1 cohort · inception 07-01"
(11 sleeves). Split rule = inception >= 2026-07-01. Shared status strip stays on top,
movers/experiments/concentration stay below (all sleeves). Bonus: each cohort's hover box
is now small again (~6 vs ~13 lines). Empty 0701 chart shows "deploys on its 07-01
rebalance" until 7/1. Dashboard restarted (HTTP 200).

## AL.3 - Fix: NameError _rg from the AL.2 extraction
The AL.2 panel extraction moved the `_rg` red/green cell-color helper into
`_render_cohort_panel`, but the movers table further down in `_render_overview` still
referenced it -> `NameError: name '_rg' is not defined` at render time (py_compile
didn't catch it; it's a runtime name-resolution error, not a syntax error). Fix:
promoted `_rg` to a module-level function so both the cohort panels and the movers table
share it; removed the now-duplicate local copy. Verified by importing the module (`_rg`
callable) + grepping all `_rg`/`_style` references resolve in scope; dashboard restarted
(HTTP 200). Lesson logged: exercise the actual render path, not just py_compile, when
refactoring shared closures out of a function.

## AL.4 - Docs-cadence hook was dormant; fixed registration
Audit (user asked "is the updates still firing every 3 prompts"): NO — `.claude/cadence
.json` was frozen at count=0 / last_reminder 2026-05-29, and no `[DOCS_CADENCE]` reminder
had appeared all session. The script (`.claude/hooks/check_docs_cadence.py`, CADENCE=3)
works when invoked (manual run incremented 0->1), so the fault was INVOCATION: settings.json
had two UserPromptSubmit entries and the cadence one carried a stray `"matcher": ""`
(UserPromptSubmit takes no matcher), which the harness skipped — only the ruflo `route`
hook (no matcher) ran. Fix: merged the cadence command into the working matcher-less
UserPromptSubmit group + removed the stray entry (added timeout 5000); JSON re-validated;
counter reset to 0. NB the docs themselves stayed current the whole time because Claude
was updating record/state manually each substantive prompt (AK.6–AL.3). CAVEAT: settings
.json hook changes may only load on a new session — if cadence.json count stays 0 across
the next few prompts, a session restart will pick up the new registration.

# Appendix AM - Graphify root expansion + AlpacaError bridge trace + appendix-date audit (2026-06-30)

## AM.1 - /graphify expanded to full project root
Prior graphs only scanned `trading_bot/`. Expanded scan root to the full project
(`D:\ClaudeCode\Trading`), adding `scripts/` (95 files) + `main.py`, excluding tooling
noise (`.claude`, `.claude-flow`, `.swarm`). AST-only (code), $0 token cost. Graph grew
1329->1349 nodes, 2429 edges, 120 communities (re-clustered). `.graphify_root` updated to
the project root so future `--update` runs cover everything.

## AM.2 - Traced why AlpacaError bridges the Alpaca-integration community to the paper core
User asked why graphify flagged `AlpacaError` as a high-betweenness cross-community bridge.
Queried the graph directly: `AlpacaError` has exactly one edge leaving its own community —
`inherits->RuntimeError`, and `runtimeerror` sits in the `paper_trader` community because
several unrelated modules (factor_backtest.py, market_data.py's CacheMiss, portfolio.py)
also raise/inherit it. **Verdict: that specific edge is a weak/generic bridge** — a shared
Python builtin, not real coupling. The *real* bridge is architectural and was under-weighted
by the clusterer: `trading_bot/execution/alpaca_sync.py` (filed inside the Alpaca community)
directly imports `paper_trader` and calls `paper_trader.list_open(sleeve)` to read the paper
sleeve's live DB state before translating it into Alpaca orders, catching `AlpacaError` around
the submission calls. Reported both the topological finding and this honest caveat to the user
per graphify's EXTRACTED/INFERRED/AMBIGUOUS convention.

## AM.3 - Appendix-date audit (this entry)
User: "make sure all the appendix items have dates." Audited all 38 top-level `# Appendix`
headers (A-AL). Found two gaps:
- **Appendix A** had no date in its header (unlike B onward). Grounded from A.10's own text
  (Form-4 era spans project origin through the 2026-05-22 closure) -> added
  `(2026-04-25 to 2026-05-22)`; updated its anchor + the two links that pointed to it (TOC,
  Thematic-digest verdict table).
- **Appendix AL** (added last session) was mistakenly written as `## AL` (H2, no date) instead
  of `# Appendix AL - ... (date)` (H1) per this doc's own stated convention ("the two heading
  levels encode Phases vs Appendices" — see "How this document is organized"). It was also
  missing from the Part II Table of Contents entirely. Fixed: promoted to
  `# Appendix AL - Alpaca paper integration begins + 7/1 clean-start cohort (2026-06-30)`,
  added its TOC entry. AL.1-AL.4 subsections left as-is (H2, no per-item date) — matches the
  established convention since Appendix L era, where only the top-level Appendix header carries
  a date and subsections don't. Verified new anchors match GitHub's slug algorithm before editing
  cross-references. No content beyond headers/TOC/links touched.

Cadence: this is the prompt-3 catch-up since AL.4 (graphify expansion + AlpacaError trace +
this audit all fell in the same 3-prompt window).

# Appendix AN - Record file renamed; HTML render tied to it (2026-06-30)

Evan renamed `docs/record_2026-05-27.md` -> `docs/Project Record — Full Chronological History
.md` (matching the doc's own H1 title) and asked whether the rendered `.html` could auto-update
from the `.md`.

- **Fixed the break the rename caused:** `scripts/render_record_html.py` had the old filename
  hardcoded (`SRC`/`OUT`) — after the rename it would have failed with `FileNotFoundError` on
  next run. Replaced with a single `DOC_NAME` constant derived from the doc's own title so
  source/output stay in sync. Re-ran; 0 broken internal anchors (72 links / 246 heading ids).
- **Auto-update mechanism (`scripts/watch_record_html.py` + `.bat`, NEW):** a `watchdog`-based
  file watcher (already in the venv, no new dependency) on `docs/`, event-driven via Windows'
  `ReadDirectoryChangesW` (not a polling loop) — re-renders the instant the target `.md` is
  saved, ~1s debounce for editors that emit multiple write events per save. **Live-tested**:
  appended a line to the `.md`, watcher fired and the `.html` mtime matched within the 3s check
  window; reverted the test line, re-render followed automatically. Cleaned up all stray test
  processes afterward (`taskkill` on PIDs from the manual test runs).
- **Decision — reminder over daemon:** offered Evan a persistent AtLogon scheduled task (same
  pattern as `TradingDashboard`/`TradingDailyMTM`) for always-on live sync; he chose a lighter
  option instead — a reminder note baked into the top of the record `.md` itself, pointing at
  the one-shot render command and the `watch_record_html.bat` live-watch command, so whoever
  (Claude or Evan) next edits the doc sees it and runs the refresh consciously rather than a
  silent background process persisting across reboots. No scheduled task was created.
- **Known stale reference (not fixed, out of scope):** `CLAUDE.md`, `HANDOFF.md`, and
  `state_2026-06-12.md` still prose-reference the old `record_2026-05-27.md` name; functional
  code (the render script) was the only thing that actually broke, so those were left alone
  per the surgical-changes rule — flagging here in case a future prompt wants to sweep them.

# Appendix AO - Rename notes added at every record_2026-05-27 mention (2026-06-30)

Follow-up to AN: user asked to "make a note that the file has been renamed at each point
record_2026-05-27.md is mentioned" (closing the loose end AN itself flagged) and to re-render
the HTML. Swept the whole project (grep, excluding `graphify-out/`) for every mention:

- **CLAUDE.md, HANDOFF.md, docs/state_2026-06-12.md** — live/current-state docs; added an
  inline rename note next to each mention (content otherwise untouched).
- **This record's Part I** (`Phase 3 — Consolidation`, "Files created" list, the original
  2026-05-27 "this file" line) — added an inline note.
- **Appendix Y (Y.2, Y.3, Y.6)** — these narrate what was built ON 2026-06-12 and are
  append-only per this doc's own rule ("prior appendices are never edited"). Rewriting them
  to reflect a rename that happened 18 days later would be revisionist. Instead added a
  clearly-marked `> *[EDITORIAL NOTE 2026-06-30 — added after the fact, original text below
  unchanged: ...]*` blockquote directly above each mention — annotates without altering the
  original historical prose, same spirit as Y.2's own "additive only" reorg.
- **The `.html`** was left alone (generated artifact, not hand-edited) — regenerated instead
  via the render script so it picks up all of the above automatically.

Re-ran `.venv\Scripts\python.exe -m scripts.render_record_html` after these edits: 0 broken
internal anchors.

# Appendix AP - Fixed the monthly-rebalance trigger timing bug (2026-07-01)

The `monthy-llm-rebalance` Claude scheduled task fired 2026-07-01 08:03am (cron `0 8 * * *`)
and correctly bailed: at 8am `price_cache` only has through the prior close, `tradeable_universe`
is strict same-day, so the mom_roa candidate/cascade ranking came back empty ("No candidate at
this date"). The routine did the right thing — logged nothing, ran no rebalance, left
`rebalance_log.md` at 2026-06-03. Root cause is structural: the 8am cron fires before the market
close, but the runbook needs "first trading day, after close." Real closes only land at 5:15pm
via `TradingDailyMTM` (daily.bat runs `daily_price_refresh` first, then MTMs — daily.bat:18-19),
so the 8am trigger could never complete; it would hit the empty-universe wall every month.

Fix (Evan approved): rescheduled `monthy-llm-rebalance` `0 8 * * *` -> `0 18 * * *` (6:03pm local)
via `mcp__scheduled-tasks__update_scheduled_task`. 6pm is after the 5:15pm close pipeline, so the
real same-day closes are cached before the routine fires. The routine still self-gates on
`rebalance_log.md` (SKILL.md line 6), so only the first 6pm run of a month does work. Because the
log was still 2026-06-03 (stale for July), the 2026-07-01 18:03 run was set to auto-complete the
July rebalance with correct prices — sector overlay owes 0 new decisions (top-4 unchanged:
XLK/XLI/XLB HOLD, XLE VETO), only the stock overlay needs a live decision on the real 7/1
mom_roa #1. Memory `monthly_rebalance_trigger_timing_bug.md` + its MEMORY.md pointer flipped from
"open bug" to RESOLVED. No code changed — schedule-only fix.

# Appendix AQ - daily_report.md gets the same standalone-HTML render (2026-07-01)

User: "do the same HTML conversion to daily_report.md." `daily_report.md` (repo root, the owner's
running trade journal — now ~15k lines / ~1MB, auto-appended by the daily-trade-check routines) is
a flat chronological log with `##`/`###` headings and NO in-doc TOC/anchors (grep `](#` = 0).
- **Refactored `scripts/render_record_html.py` (behavior-preserving):** extracted the render body
  into a reusable `render(src, out, title, topbar)` and added `{title}`/`{topbar}` placeholders to
  the HTML TEMPLATE (were hardcoded "Project Record"). `main()` now calls `render(...)` with the
  record's title + its TOC-jump topbar link. Verified the record still renders byte-identically
  (252,663 bytes, 72 links, 0 broken) — pure refactor, no output change.
- **New `scripts/render_daily_report_html.py`:** thin second entry point importing that shared
  `render()`, so template/CSS/light-dark/slugify stay identical. Title "Daily Reports — Trading",
  plain "Daily Reports" topbar (no TOC link, since the journal has no TOC). Writes
  `daily_report.html` at repo root. First render: 1,337,806 bytes, 658 heading ids, 0 broken.
- **Not done (offered, not imposed):** `daily_report.md` is auto-appended by the scheduled
  routines, so unlike the record it has no interactive "editor" to see a reminder note; a
  reminder-in-file wouldn't fire. Left auto-refresh out of scope for now — the `.html` is a
  generated artifact, regenerate with `.venv\Scripts\python.exe -m scripts.render_daily_report_html`.
  Natural next step if wanted: extend `watch_record_html.py` to also watch root/`daily_report.md`,
  or append the render call to the end of the daily-trade-check routine.

# Appendix AR - Rewrote monthy-llm-rebalance's prompt: full context + instructions (2026-07-01)

The scheduled task's SKILL.md was 4 terse lines ("run overlay_prep, do the research per the
runbook, run rebalance.bat") — it worked when the operator already held full context in an active
session, but wasn't self-contained. User asked for a prompt with "full context and instructions."

Rewrote it (108 lines) to be self-sufficient without requiring the runbook to be re-read every
time (though it still points to `docs/overlay_decision_runbook.md` as the source of truth if
anything diverges):
- **Step 0 gate** — explicit rebalance_log.md month-check before doing anything.
- **Step 1 gather** — `overlay_prep.bat`, and explicitly names its THIRD section (LLM-CASCADE,
  added AK.2/AK.3) which the old runbook never documented — the cascade shares the cash overlays'
  decision log and needs deeper-than-#1/top-4 evaluations, which the terse prompt would have
  silently missed.
- **Step 2 data-integrity guardrail** — baked in TODAY's exact incident (empty-universe / stale
  price -> STOP, report don't act, cite Appendix AP + the timing-bug memory) and the standing
  BKGM/KLAC split-artifact sanity check, as explicit STOP conditions checked BEFORE any research.
- **Step 3 decisions** — compact but complete rubric (score/invalidation/no-lookahead/rationale/
  honest-prior) plus both overlays' specific prompts and the exact `decide` CLI syntax, inline
  (not just "see runbook") so a cold run doesn't need a second file read.
- **Step 4 execute** — names exactly what `rebalance.bat` does now (4 systematic + 7/1 cohort +
  both overlay treatments + cascade pair + the Alpaca sync for 3 mirrored sleeves + the log stamp)
  so the operator recognizes the output instead of being surprised by the Alpaca step.
- **Step 5 report** — explicit summarize-to-Evan instruction, "Evan," opener per standing
  preference.

Verified via `mcp__scheduled-tasks__list_scheduled_tasks`: prompt saved (SKILL.md now 108 lines).
Noted in passing (not investigated further, out of scope for this prompt-only task): the listed
cron/next-run display showed a jittered time (~5:33pm) slightly different from the 6:03pm base set
in Appendix AP, and `lastRunAt` showed the task had already fired once this evening — worth Evan
checking the outcome of that run separately.

# Appendix AS - cmd.exe batch-parsing bug in rebalance.bat/daily.bat found + fixed; July rebalance completes (2026-07-01)

Answers AR's open question: the ~5:33pm run's "outcome unverified" was this bug. The 6:03pm
`monthy-llm-rebalance` firing (this session) hit it too — `rebalance.bat` aborted almost
instantly with garbled `'M' is not recognized as an internal or external command` / `'d' is not
recognized` / `'cho' is not recognized` errors, printing a false-looking
`ERROR: Price refresh failed. ABORTING rebalance` even though no real price-refresh attempt had
happened. `rebalance_log.md` correctly stayed untouched (idempotent failure, no partial state).

**Root-caused to two things, both fixed:**
1. A stray 0-byte file literally named `ECHO` in the project root (`D:\ClaudeCode\Trading\ECHO`,
   mtime 2026-06-29 23:53) shadowed the `echo.` builtin used throughout both `.bat` files for
   blank-line spacing — cmd.exe resolves bare `echo.` to a file named `ECHO` if one exists in cwd,
   then fails to "execute" it since it has no recognized extension. Deleted the file.
2. An em-dash (U+2014) inside a `REM` comment on `rebalance.bat` line 146 ("...closes — so the
   old...") corrupts cmd.exe's batch-file parse state for the *entire* file, not just that line —
   confirmed via bisection (isolated to that exact line; a neutralized copy with only that line
   changed reproduced the same top-of-file-looking garbage, and removing it alone fixed it).
   Replaced with a plain hyphen. Also fixed two unescaped `&` in "S&P 500" text (`rebalance.bat`
   lines 56/60, `daily.bat` lines 25/29) — cmd treats bare `&` as a command separator — escaped to
   `S^&P`.

Verified the fix with a neutralized dry-run (all `.venv\Scripts\python.exe` calls replaced with
`echo SKIP`) before re-running for real: clean end-to-end, no parse errors. **Blast-radius check**:
no git repo here (no commit history), but file mtimes put both edits at "today, during the AK/AL/
AM/AR editing burst" and grep of this record (otherwise exhaustive back to April) found zero prior
mention of this failure signature — read as introduced and fixed same-day, not a weeks-long silent
outage. Cross-checked against DB history: `mom_v1_paper`, `mom_v2_paper`, `mom_roa_6535_paper`,
`residual_roa_6535_paper`, `spy_benchmark_paper`, and `sector_top4_full_paper` all show complete,
gap-free `paper_nav` history through today — no evidence any OTHER sleeve was silently skipped in
this window.

**False lead, corrected**: initially hypothesized this same bug explained why `sector_top4_paper`
showed 0 open positions / 100% cash going into today's rebalance. Wrong — `sector_top4_paper` had
complete history through 06-29 (41 nav rows, NAV $102,423.84) and was intentionally wiped and
re-inceptioned to 07-01 by `align_llm_07_01.py --confirm` per Appendix AK.5/AK.6 (deliberate,
user-directed, archived reversibly to `var/align_llm_07_01_archive.json`). No new bug there — see
AK.5/AK.6 for the real story. Filed as a follow-up task rather than left unresolved; closed here.

**July monthly rebalance completed cleanly (18:19-18:34) after the fix, exit code 0:**
- Decisions: 0 new — all carried from 06-30 (BE VETO stock overlay/cascade #1; XLK/XLI/XLB HOLD +
  XLE VETO sector overlay; SLGL VETO + WDC BUY stock cascade #2/#3; XLV HOLD sector cascade #4).
- 4 systematic sleeves rebalanced (mom_v1/v2/roa/residual), `sector_top4_full_paper` unchanged,
  `sector_top4_paper` bought its 07-01 picks, all 4 members of the 7/1 clean-start cohort got their
  first-ever inception buys, both SPY benchmarks MTM'd/seeded, both overlay treatments + both
  cascade sleeves rebalanced per the carried decisions.
- Alpaca PAPER sync: `residual_roa_6535_0701_paper` 44/50 submitted (6 rejected: not-fractionable/
  inactive assets, normal Alpaca constraints, not a bug), `mom_roa_6535_0701_paper` 48/50 submitted
  (2 rejected, same reason), `spy_benchmark_0701_paper` 1/1 submitted clean.
- `rebalance_log.md` stamped 2026-07-01.

**Separately noted, not addressed here**: ~97 stray root-level junk files (zero-byte shell
shrapnel, same class as the `ECHO` file) have re-accumulated since the Appendix T/M1 cleanup on
2026-06-09 — worth a cleanup pass, out of scope for this entry.

# Appendix AT - Alpaca non-fractionable gap fixed (whole-share fallback + DB reflect); all 11 07-01 sleeves reset to 07-06 (2026-07-02)

Evan noticed some 07-01 Alpaca mirror orders "didn't buy." Root-caused: `alpaca_sync` submits
FRACTIONAL qty, but Alpaca rejects a fractional order on a non-fractionable asset (422) and can't
trade a delisted one at all — the per-order `except AlpacaError` then silently skipped them. On the
07-01 mirror that was residual_0701 43/50, mom_roa_0701 48/50. Confirmed via Alpaca's asset API:
non-fractionable (whole-share only) = DMAA/EDRY/FNRN/KFII/AFJK/SLGL; inactive/delisted = EACO/FMBM;
XOM was fractionable but its lone order canceled (after-hours). So ~14%/4% of those two accounts sat
in cash.

**Fix — Option 1 (whole-share fallback) + reflect it in the DB sim (Evan's choice):**
- **`trading_bot/execution/fractionability.py` (NEW):** tiny `alpaca_asset_meta` cache table +
  `refresh(tickers, client)` (fills tradable/fractionable from Alpaca on demand, monthly-stale) +
  `classify(tickers)` (CACHE-ONLY read; unknown tickers default to tradable+fractionable → **zero
  behavior change** anywhere the cache isn't populated, so backtests/frozen specs are untouched).
  Added `AlpacaClient.get_asset()`.
- **`alpaca_sync`:** non-fractionable target names → WHOLE-share (floor); untradable → dropped;
  both reported per account ("NOT buyable on Alpaca: …"). Dry-run verified: residual_0701 now
  targets 48 (DMAA/EDRY/FNRN/KFII kept as whole-share, only EACO/FMBM dropped), mom_roa_0701 keeps
  AFJK/SLGL as whole-share.
- **`paper_rebalance`:** new `--broker-realistic` flag (default OFF → backtests unchanged) applies
  the SAME floor/drop so the DB sleeves match what Alpaca can execute. Added to all 10
  `paper_rebalance` lines in `rebalance.bat`. **Frozen tests still 0.0000pp** (they route through
  `factor_backtest`, not `paper_rebalance`; verified).

**Reset all 11 07-01-inception sleeves to fresh $100k / inception 2026-07-06** (Evan: "reset all
7/1 sleeves to start tomorrow" — but **7/3 is the Independence-Day market holiday**, NYSE closed, so
07-06 Monday is the next real trading day). `scripts/data_audit/reset_0701_to_0706.py` (archived to
`var/reset_0701_to_0706_archive.json`, reversible; decision logs untouched) wiped + re-inited:
mom_v1/v2/roa/residual_0701, spy_0701, mom_roa_top1, both overlays, both cascades, sector_top4.
All now $100k / 0 open / incep 07-06. The continuous May sleeves (mom_v1/v2/roa/residual_paper,
sector_top4_full, spy_benchmark) were NOT touched — they keep their 07-01 monthly rebalance. Fixed
`rebalance.bat`'s spy_0701 seed `--inception 2026-07-01 → 2026-07-06`.

**Scheduled task `monthy-llm-rebalance` DISABLED** (was firing daily 6:03pm) to stop it auto-
deploying the reset cohort prematurely on 07-02..07-05 (and it would empty-universe-bail on the
07-03 holiday anyway). Re-enable as part of the 07-06 deploy.

**PENDING — the 07-06 deploy (coordinated, after the 5:15pm close pipeline):** (1) Evan
dashboard-resets the 3 Alpaca PAPER accounts to $100k (can't be done via API — dashboard-only;
Claude never touches account settings). (2) Targeted deploy of ONLY the 11 cohort sleeves (NOT full
`rebalance.bat`, to avoid double-rebalancing the base May sleeves): `overlay_prep` as-of 07-06 →
log the 07-06 LLM decisions → rebalance the 5 systematic 0701 (`--broker-realistic`) + seed spy_0701
07-06 + the 6 LLM sleeves + MTM all 11 → `alpaca_sync --all --execute`. (3) Re-enable the task for
August's monthly run. No rebalance was run on 07-02 (per Evan's 07-06 start choice; 07-06 closes
don't exist until Monday).

# Appendix AU - Attempted a 07-02 early deploy; HELD to 07-06 for incomplete close data (2026-07-02)

Evan: "I just created 3 accounts and updated the keys. Why not just the rebalance buy now." So we
tried to bring the deploy forward from 07-06 to tonight (07-02, a normal trading day). Two checks
first:
- **Accounts OK:** the 3 NEW Alpaca paper accounts verify ACTIVE / $100k / flat (new account #s —
  PA3MD0BVF2WN / PA37FAQU4MOY / PA3RXQ3LDX94). So the "$100k reset" is satisfied by fresh accounts;
  **no dashboard reset needed** (supersedes AT's pending item 1).
- **Data NOT OK → held.** At 16:43 local (market closed ~1h40m) `price_cache` still topped out at
  07-01; ran `daily_price_refresh`, got only 4,414 07-02 closes vs the ~5,200 baseline (6/30 5,213,
  7/1 5,204). Waited 40 min, re-pulled: still 4,416 — and the prices were byte-identical across both
  pulls, i.e. NOT settling; yfinance simply hasn't published 07-02 for ~790 tickers (234 real >$5
  names). Measured the actual impact: mom_roa_6535 top-50 was **44/50 identical** 7/1-vs-7/2, only
  **1** name (WBHC) excluded purely for missing data (the other 5 = normal rank drift); universe
  3,273→3,071 (-6%). So this was INCOMPLETE-coverage, not the corrupted-value class (spikes/phantoms)
  — values present were final. Presented the tradeoff; **Evan chose HOLD to 07-06** (clean full
  universe over ~1 off-pick per stock sleeve).
- **Cleanup:** the 5:15pm `TradingDailyMTM` had written a stray pre-inception `2026-07-02` $100k nav
  row to each of the 11 flat reset sleeves — deleted all 11 (`paper_nav` where `nav_date < 07-06`).
  **NB the daily MTM will re-add flat rows over the 07-03..07-05 holiday weekend, so the 07-06 deploy
  must first delete pre-07-06 nav rows for these 11 sleeves.** The partial 07-02 closes now in
  `price_cache` are correct values (harmless; future refresh fills the gap). State otherwise
  unchanged from AT: 11 sleeves $100k/flat/incep-07-06, task still disabled, code fixes in place.

# Appendix AV - 07-06 cohort deploy executed; all 11 sleeves live, Alpaca mirrored, monthly task re-enabled (2026-07-07, ~13:20 local)

Ran as the scheduled `cohort-0706-deploy` one-time task, unattended, ~4am-plus gate satisfied.

**Precondition (Step 1):** `daily_price_refresh` ran clean (only routine delisted-ticker noise).
`price_cache` count for `2026-07-06` = **5,206 closes** (vs recent-day baseline ~5,200-5,255) →
PASS, well clear of the 5,000 abort floor. Proceeded.

**Cleanup (Step 2):** deleted 11 stray pre-inception `paper_nav` rows (dated `2026-07-03`, written by
the holiday-weekend 5:15pm MTM per Appendix AU's warning) — one per cohort sleeve. Confirmed 0
remain before `2026-07-06`.

**Systematic 0701 deploy (Step 3), all `--broker-realistic`:**
- `mom_v1_0701_paper` — top-100, 100/100 bought, cash $145.00
- `mom_v2_0701_paper` — top-50, 50/50 bought, cash $112.31
- `mom_roa_6535_0701_paper` — top-50, 50/50 bought, cash $110.37
- `residual_roa_6535_0701_paper` — top-50, **48/50** bought (FMBM, EMYB skipped — untradable/
  inactive on Alpaca, normal broker-realistic behavior, not a bug), cash $120.97
- `spy_benchmark_0701_paper` — seeded 133.106 SPY @ $751.28 on 2026-07-06, MTM'd to $99,506.17
  (-0.49%, tracks SPY's actual 07-06→07-07 move)

**LLM-experiment decisions (Step 4), live-web research dated 2026-07-07 (all rationale + source URLs
logged in the decision tables):**
- **Stock control candidate BE (Bloom Energy), score 4, VETO.** 128x forward P/E / ~19x NTM revenue
  vs peer median ~6x; price $263.81 already above the $181.79 consensus analyst target; -23.7% off
  52w high, below 50-DMA; Q2 earnings 7/28 sets a high bar into an already-stretched valuation —
  textbook "momentum blow-off now rolling over."
- **Stock cascade walked to #2 WDC (Western Digital), score 6, BUY** (BE VETO'd, cascade needs the
  first BUY). Distinguished from BE by durability: HDD capacity sold out through 2026 with firm
  multi-year customer contracts into 2027-2028 (real revenue visibility, not pure momentum), 30x fwd
  P/E vs 16x tech-sector average (elevated but not extreme). Cascade sleeve holds WDC; stock control
  still holds BE (unaffected by the veto by design); stock overlay treatment sits in CASH.
- **Sector candidates (top-4 by 12-1 momentum): XLK HOLD(6), XLE VETO(3), XLI HOLD(8), XLB HOLD(5).**
  XLE repeats the 2026-06-12 fragile-geopolitical-rally VETO pattern (below 50-DMA, RSI 38, negative
  1m/3m, EIA sees 2026 demand -1.1mb/d against rising non-OPEC+ supply). XLI cleanest setup (above
  50-DMA, RSI 55, +10.1% 3m, reshoring/infra/data-center capex tailwind, broad holdings). XLB the
  recurring marginal-hold (barely above 50-DMA, weak RSI 41, but copper/AI-infra demand intact).
  Sector overlay treatment: 3 of 4 slots filled (XLK/XLI/XLB), XLE slot in cash.
- **Sector cascade needed a 4th HOLD** (only 3 of the top-4 HOLD'd) — walked to rank #5 **XLV
  (Health Care), score 7, HOLD**: strong rotation-into-healthcare trend (9.6% above 50-DMA, at its
  52w high, GLP-1/oncology earnings strength offsetting an overbought RSI 72.2, which is the noted
  near-term risk). Cascade sector sleeve holds XLK/XLI/XLB/XLV, all 4 slots filled — no
  momentum-fill leakage needed.
- Rebalanced in order: `llm_overlay_ops rebalance --mode control` (BE), `--mode overlay` (VETO→cash),
  `llm_cascade_ops rebalance-stock` (WDC), `paper_rebalance --strategy sector_top4_paper --top-n 4`
  (control, all 4 incl. vetoed XLE), `sector_overlay_ops rebalance` (treatment, 3 of 4),
  `llm_cascade_ops rebalance-sector` (4 of 4).

**MTM (Step 5):** all 11 sleeves MTM'd clean — cash reconciles to entry-vs-invested, position counts
match target (100/50/50/48/1/1/0/1/4/3/4), no drift.

**Alpaca PAPER mirror (Step 6):** `alpaca_sync --all --execute` against the 3 fresh accounts —
`residual_roa_6535_0701_paper` 48/48 submitted (0 rejected), `mom_roa_6535_0701_paper` 50/50
submitted (0 rejected), `spy_benchmark_0701_paper` 1/1 submitted (0 rejected). 99 DAY orders total,
queued to the next market open, 0 rejections.

**Monthly task (Step 7):** `monthy-llm-rebalance` re-enabled, cron changed `30 17 * * *` →
`0 18 * * *` (6:03pm local w/ dispatch jitter) per the deploy task's instruction. Its July log gate
still no-ops the rest of the month; first live fire will be 2026-08-01.

State: all 11 07-06-cohort sleeves are now live and invested (or intentionally in cash per a logged
VETO), 3 mirrored to real Alpaca PAPER accounts, recurring monthly automation restored for August.

# Appendix AW - Session ops: RuFlo statusline disabled (stray-file source), shadow-file recurrence, deploy scheduled from chat (2026-07-05..07-07)

Housekeeping done across an interactive session that spanned the deploy (the deploy itself is AV;
this is the surrounding manual work).

**Stray root-level files diagnosed.** Empty untracked files named `12` (07-03 08:13) and `20%`
(07-05 20:01) kept appearing in the repo root — the same *class* as the CLAUDE.md cmd.exe
shadow-file gotcha, but a new source. Ruled OUT the `.bat`/scheduled-task path (no reboot/logon near
the timestamps; no bare numeric redirect in any `.bat`; no `shell=True`/`os.system` in the Python).
Traced `20%` to the **RuFlo V3 statusline** (`.claude/helpers/statusline.cjs`), which prints raw
`"20% ctx"` (unescaped `%`) on nearly every turn via a `cmd /c` invocation — leaking `%`-fragments as
redirect targets. **FIX: removed the `statusLine` block from `.claude/settings.json`** (decorative
RuFlo progress metrics unrelated to trading; every re-render was a chance to drop junk). The
docs-cadence hook and ruflo MCP hooks were left untouched.

**HONEST OPEN ITEM (not fixed):** format-spec-named files (`4`, `10.2f}`, `12.2f}`) **recurred
2026-07-07 ~18:29**, i.e. AFTER the statusline disable — so the statusline was the `20%` source but
NOT the source of these. They look like Python format specs (`{:>10.2f}` etc.) leaking as shell
redirect targets from an evening scheduled run (a `scratch_positions.csv`, 49 KB, dropped at the same
18:29 timestamp). Source not yet found; the files are empty and harmless but clutter `git status`.
Flagged for a future session. Also noted: an untracked `PRD_ROADMAP.md` (25 KB) appeared at 23:11 —
author/intent unconfirmed, left untouched.

**Other session work:** fixed a "run un" typo in both `daily-trade-check` / `daily-trade-check-2`
scheduled-task SKILL.md files; committed the day's `daily_report.md`/`.html` (commit 673a72b); and
**scheduled the `cohort-0706-deploy` one-time task** (fireAt 2026-07-07 04:05 local) from chat, with a
fully self-contained prompt + a Step-1 abort-gate requiring >=5,000 closes for 2026-07-06 before
deploying — which is what then ran as AV. NB: the session's injected context date was stale by ~2 days
(showed 07-05 while the real clock was 07-07), caught via the system clock during this doc sync;
absolute-timestamp scheduling made the deploy fire correctly regardless.

# Appendix AX - CLAUDE.md rewritten; ruflo fully removed; PRD-handoff system built (2026-07-08, ~afternoon)

**WHAT:** Cross-project handoff-hardening session (run from D:\ClaudeCode root). In this repo:
(1) `CLAUDE.md` rewritten — added purpose/stack/commands, hard rules (read-only DB default, never
run trading ops, 5:00-6:30pm window, alpaca_keys.env, HTML twins, newest-last daily_report), and a
definition of done; REMOVED the stale sleeve roster (it had drifted from the 07-06 re-inception —
HANDOFF.md is now the single roster source) and the dead ruflo section. Old file kept at
`CLAUDE.md.bak_2026-07-08`. (2) Ruflo/claude-flow fully removed: hooks stripped from
`.claude/settings.json` (docs-cadence hook preserved; backup at
`.claude/settings.json.bak_pre_ruflo_cleanup_2026-07-08`), `.claude-flow/` (30K) and `.swarm/`
(1.8M) deleted, duplicate `.claude/skills/skill-builder` deleted. Globally: ruflo hooks stripped
from `~/.claude/settings.json`, `~/.claude/agents` and `~/.claude/helpers` renamed to
`*.bak_claude_flow_2026-07-08` (reversible). This completes what Appendix AW started (statusline
disable) — the MCP server itself was already gone (`.mcp.json.bak_pre_ruflo_removal`).

**WHY:** Evan is preparing to hand day-to-day execution to cheaper models (Opus/Sonnet); CLAUDE.md
must be self-sufficient, and the dead ruflo section actively instructed models to use MCP tools
that no longer exist. The ~100-agent claude-flow roster in `~/.claude/agents` was loading into
every session on every project — pure token drag.

**HOW:** Audit first (verified .mcp.json absent, agents/commands dirs empty, hook-handler.cjs
falling back to the user-level copy), Evan approved scope via four decisions (full ruflo cleanup;
dups-only skill deletion), then backups before every destructive step. New user-level skills
`/prd-next` and `/record-entry` operationalize the PRD_ROADMAP execution loop; a model-handoff
protocol section was added to the global `~/.claude/CLAUDE.md`. No trading code, data, or
scheduled tasks were touched; frozen tests not run (no Python changed).

# Appendix AY - Handoff sync: TOC backlog repaired (AM-AX), cash-buffer cadence miss logged, doc pointers fixed (2026-07-08, ~17:15 local)

First run of the merged `/project-memory` skill's handoff workflow (the skill that replaced
`/handoff`, `/memory-bootstrap`, `/prd-next`, `/record-entry`, and `/codebase-memory` — this
corrects Appendix AX, which named `/prd-next`/`/record-entry` as the new skills; they were merged
into `/project-memory` later the same day, originals parked in
`~/.claude/skills.bak_merged_into_project-memory_2026-07-08/`).

**WHAT this sync found and fixed:**

1. **Record TOC was stale by 12 entries.** The front-matter Table of Contents had no lines for
   Appendices AM through AX — the per-appendix TOC line had been silently skipped since
   2026-06-30. All 12 lines added (additive front-matter maintenance; no entry content touched).
   The new skill makes the TOC line an explicit step of every record entry, so this class of
   drift should be extinct going forward.
2. **Cadence miss: commit `3807f23` (2026-07-08 12:47, "Add 1% cash buffer to Alpaca mirror
   sizing", `trading_bot/execution/alpaca_sync.py`, +6/−1, authored by an Opus 4.8 session) landed
   with NO record entry.** Logged here instead of by its own session. Per the CLAUDE.md rule,
   ANY Python change owes a frozen-test run; the record shows no evidence one was run at that
   commit.
3. **HONEST OPEN ITEM (deferred, not skipped):** this handoff executed at ~17:12 local — inside
   the 5:00–6:30pm daily-MTM window — so the frozen tests were NOT run now (DB-heavy work is
   barred in the window). Next session outside the window: run
   `.venv\Scripts\python.exe -m pytest trading_bot/strategies/test_strategies.py`, confirm
   d=±0.0000pp, and log the actual output here. Until then the cash-buffer commit's frozen-test
   status is UNVERIFIED.
4. **Stale doc pointers fixed** (in-place edits to living snapshots, sanctioned): `HANDOFF.md`
   and `docs/state_2026-07-07.md` both said "full roster + rationale in `CLAUDE.md`" — stale
   since Appendix AX moved the roster out of CLAUDE.md to end the duplication drift. Both now
   point at HANDOFF as the roster source; CLAUDE.md holds the durable invariants.

**Uncommitted at time of writing** (committing is Evan's call): the AX CLAUDE.md rewrite,
today's `daily_report.md`/`.html` changes, and untracked `CLAUDE.md.bak_2026-07-08` /
`.mcp.json.bak_pre_ruflo_removal` / `scratch_positions.csv` (the last still author-unconfirmed,
see AW).

# Appendix AZ - State-doc tier retired: every state_<date>.md archived verbatim below (2026-07-08, ~17:30 local)

Evan's decision, 2026-07-08: the dated state-snapshot tier is retired project-system-wide. Snapshots now live inside this record; `HANDOFF.md` remains the always-current view. Reason: the three-way HANDOFF/state/record sync burden caused real drift (see AY item 4 — the same stale pointer lived in two files). The five state files are archived below **verbatim except that every heading is demoted two levels** (fence-aware) so this record's appendix structure stays intact. The source files are banner-marked MIGRATED and await Evan's deletion approval.

## AZ.1 — state_2026-05-27.md (verbatim archive; headings demoted two levels)

### Project State — 2026-05-27  [SUPERSEDED 2026-05-28]

**⚠️ STALE.** Replaced by `docs/state_2026-05-28.md` after the data audit
revealed in-sample numbers below were contaminated. See that file for the
current state. This doc is kept for historical reference only.

Consolidation snapshot after closing the momentum + multi-factor research arc.
Purpose: capture what's validated, what's been ruled out, and what's needed
for paper-trading deployment, so future work doesn't re-tread the same paths.

#### Working strategy

**momentum_v2** — frozen 2026-05-26, regression-tested
(`trading_bot/strategies/momentum_v2.py`, `test_strategies.py`).

| Param | Value |
|---|---|
| Factor | 12-1 momentum (Jegadeesh-Titman) |
| Universe | All US stocks ≥ $5, ≥ 252 days history |
| top_n | 50 |
| Rebalance | Monthly |
| Weighting | Equal-weight (2% each) |
| Half-spread | 5 bps |
| Starting capital | $100K |

Validated returns:
- In-sample 2015-01 → 2023-12 (9 yr): +455.6% total, +21.0%/yr, Sharpe +0.23
- Held-out 2024-01 → 2026-05 (2.4 yr): +72.8% total, +26.5%/yr, Sharpe +0.87

Both windows beat SPY meaningfully (+9 pp/yr in-sample, +5 pp/yr held-out).

#### What's been ruled out (don't retest without new data)

| Experiment | Result | Why |
|---|---|---|
| Form 4 insider-copy | Closed 2026-05-22 | Walk-forward + held-out both null |
| Naive composite (mom+lowvol) | Failed | Killed mom premium |
| Volume-gated sleeves ($1M ADV) | Failed | Removed mom's small-cap tail |
| Stdev-floor sleeves | Failed | No diversification benefit |
| yfinance-quality sleeve | Lookahead-biased | +32 pp/yr drop when fixed |
| XBRL quality v1 (3-comp) sleeve | Failed combination | Drags combined return |
| XBRL quality v2 (8-comp) sleeve | Failed combination | Same pattern |
| XBRL quality v2 STANDALONE | Not deployable | Underperforms SPY in-sample |
| Mono-factor sweep (24 configs) | None beat mom_v2 | Top-50 monthly is optimum |
| mom_quality_screen filter | Failed in-sample | -13.8 pp/yr |
| Restricted top500/top1000 | Survivorship-biased | Held-out win is artifact |
| Weekly / quarterly rebalance | 2024-26 overfit | Caught by robustness test |

Pattern across all multi-factor failures: any sleeve added to momentum is
either too correlated (loses synchronously in 2018/2022) or has lower Sharpe
than momentum (drags the combined ratio). Diversification math doesn't work
out without an uncorrelated factor that's also high-Sharpe.

Pattern across all universe-restriction failures: momentum's premium lives
in the small-cap / high-vol tail. Removing it removes the alpha.

#### Infrastructure inventory

**Data tables** (sqlite at `var/trading.db`):
- `price_cache`: 35.7M rows, ~4,200 tickers, daily OHLC+adj
- `xbrl_facts`: 4.8M rows, 4,182 tickers, 16 us-gaap concepts, PIT (filed_date)
- `sectors_cache`: 1,493 tickers (top-1500 by cap)
- `fundamentals_cache`: 46,824 rows (yfinance snapshot — has lookahead, use for sizing only)
- `signals`: 2.3M Form 4 rows (legacy, mom_v2 doesn't use)

**Factors** (`trading_bot/factors/`):
- `momentum.py` — production
- `quality_xbrl_v2.py` — works standalone but underperforms, kept for research
- `low_vol.py`, `quality.py`, `quality_xbrl.py`, `composite.py`,
  `mom_quality_screen.py` — preserved for reference, all confirmed dead
- `universe.py` — eligible-ticker builder (price ≥ $5, history ≥ 252d)

**Backtest engine** (`trading_bot/execution/`):
- `factor_backtest.py` — generic factor backtest with monthly rebalance
- `backtest.py`, `portfolio.py`, `monitor.py`, `broker.py` — Form 4 era,
  reusable for paper-trade execution
- `runner.py` — Form 4 signal executor. **Will need momentum adapter.**

**Strategies** (`trading_bot/strategies/`):
- `momentum_v1.py`, `momentum_v2.py` — frozen with version strings
- `test_strategies.py` — regression tests pinning v1/v2 exact output
  (5 bps return tolerance, exact trade count)

**Scripts** (`scripts/momentum/`):
- Warm scripts: `warm_xbrl.py`, `warm_sectors.py`, `warm_fundamentals.py`,
  `warm_volumes.py`
- Tests: `robustness_test.py`, `mono_factor_sweep.py`,
  `test_quality_standalone.py`, `test_restricted_universes.py`,
  `test_quality_screen.py`
- Chains: `run_sleeves.py`, `run_momentum.py`

#### Paper-trading deployment — what's missing

User turns 18 in [future date]. Cannot use Alpaca/IBKR until then. Until then,
deployment = local simulator that:
1. Reads today's date
2. Pulls fresh prices for the universe (yfinance with caching)
3. Computes mom_v2 ranks as of today
4. Compares top-50 to current paper portfolio
5. Generates buy/sell trade list
6. Logs to a paper-portfolio table; tracks P&L mark-to-market daily

**What exists**: backtest engine, portfolio tracking (positions table),
broker simulator, sector exposure tracking, monitor for exits.

**What needs building**:
1. **Momentum-adapter for runner.py** — currently runner reads `scorer.tradeable`
   (Form 4 signals). Need a momentum-specific entry point that calls
   `momentum.rank_universe(today's_universe, today)` and returns top-50 tickers.
2. **Daily price refresh job** — cron/scheduled task to warm prices for the
   eligible universe before market open each day. (Today this is manual.)
3. **Rebalance scheduler** — on first trading day of each month, trigger
   the momentum runner. (Today no scheduler exists.)
4. **Paper-portfolio table** — `positions` table already exists but is mixed
   with Form 4 era data. Either filter by strategy_id or fresh table.
5. **Daily mark-to-market** — extend existing portfolio tracking to record
   daily NAV for the paper portfolio (needed for actual Sharpe measurement).
6. **Slippage realism check** — backtest uses 5 bps half-spread. Track real
   fill prices vs expected for monthly rebalances; widen if necessary.

Estimated work for all 6 items: 4-8 hours focused. The hard problems are
solved (factor, ranking, universe, validation); what's left is operational
plumbing.

#### Open research questions

1. **Can momentum + an uncorrelated factor work?** The 7 failures all used
   factors correlated with momentum (price-based) or with low Sharpe
   (XBRL quality). Genuinely uncorrelated candidates: short-term reversal
   (anti-correlated by construction at 1-week horizon), idiosyncratic vol,
   accruals.

2. **Is mom_v2 robust to the next regime?** All validation is 2015-2026,
   a single super-cycle. Could fail badly in 1970s-style stagflation or
   2000-style dot-com bust. Hard to test without earlier data
   (price_cache starts 2010ish).

3. **Does survivorship bias inflate the price_cache itself?** We have
   ~4,200 tickers in price_cache. The actual 2015 universe contained
   thousands of names that are now delisted. Some delisted tickers might
   be in our cache (Form 4 ingest had a delisting tracker), but coverage
   is incomplete. mom_v2's in-sample +21%/yr might be 2-4 pp inflated.

4. **What's the actual paper-trade slippage on monthly rebalances?**
   Backtest assumes 5 bps. Real fills depend on order timing, market depth,
   correlated rebalancers. Will know after 2-3 months of paper trading.

#### Next factor — option 3 candidates

User wants a "completely different factor family" — anti-correlated with
momentum or fundamentally distinct in driver. Top candidates given our data:

##### A. Accruals (Sloan 1996) — RECOMMENDED
- **Signal**: `accruals = (NetIncome - CashFlowFromOps) / Assets`
- **Direction**: SHORT high accruals, LONG low accruals (or just LONG low)
- **Theory**: High accruals = earnings inflated by non-cash items, mean-revert
- **Data needed**: NetIncomeLoss, NetCashProvidedByUsedInOperatingActivities,
  Assets — **all 3 already in xbrl_facts** (4,157 / 4,174 / 4,182 tickers)
- **Build cost**: ~1 hour. Add `trading_bot/factors/accruals.py`, ranking,
  backtest.
- **Why it might combine with mom**: Accruals is FUNDAMENTAL (no price input),
  measured annually, low turnover (~20%/yr). Different driver entirely.
  Academic evidence shows it's largely uncorrelated with momentum.

##### B. Short-term reversal (1-week)
- **Signal**: -1 × return over past 5 days
- **Direction**: LONG worst recent losers, SHORT best recent winners
- **Theory**: Microstructure/liquidity overreaction; mean-revert within 1-4 weeks
- **Data**: price_cache only — already have it
- **Build cost**: ~30 min
- **Why it might combine with mom**: Anti-correlated by construction
  (mom buys winners, reversal buys losers). Big caveat: this is a strategy
  for low-frequency traders with high turnover; with 5 bps TC and weekly
  rebal it may not survive costs.

##### C. Idiosyncratic volatility
- **Signal**: residual stdev after regressing daily returns on SPY
- **Direction**: LONG low ivol, SHORT high ivol (ivol anomaly)
- **Theory**: high-ivol stocks attract lottery-seeking retail, get overpriced
- **Data**: price_cache + SPY — have it
- **Build cost**: ~1 hour (regression per ticker per period)
- **Why it might combine**: theoretical anti-correlation with mom (mom-winners
  often have high ivol)

##### D. PEAD (post-earnings drift)
- **Signal**: stock return in 3-day window around earnings announcement,
  then drift over next 60 days
- **Data needed**: earnings announcement dates, surprise direction
- **Data we have**: XBRL filing dates approximate this. Real PEAD data
  (analyst estimates) we don't have.
- **Build cost**: ~3-4 hours, with significant risk that filing-date proxy
  doesn't capture the actual earnings event
- **Not recommended** unless we get real earnings calendar data

##### Recommendation: build A (accruals) first

- All data already in xbrl_facts
- Build cost ~1 hour
- Different driver from momentum (fundamental, low-turnover)
- Closest match to "find a high-Sharpe uncorrelated factor" — the missing
  piece in every multi-factor failure so far
- If accruals also doesn't combine, the lesson is "no fundamentally-defined
  factor combines with mom on this universe at this scale," and we stop
  looking down that road.

#### Recommended sequence

1. **Now**: review this doc; confirm or push back on direction
2. **Soon (~1 hr)**: build `factors/accruals.py`, smoke-test standalone
3. **Soon (~30 min)**: test accruals + mom sleeves (last try at combination)
4. **Then**: depending on result, either deploy mom_v2 paper-trade OR continue
   factor research
5. **Background**: when paper-trading priority rises, build the 6 plumbing
   items above

## AZ.2 — state_2026-05-28.md (verbatim archive; headings demoted two levels)

### Project State - 2026-05-28

> **SUPERSEDED 2026-06-12** by `docs/state_2026-06-12.md` (9 sleeves, sector
> overlay seeded). This file's "Quick read" (TWO sleeves) is stale; kept for
> history. The audit/data-quality sections below remain valid reference.

Snapshot of current reality after today's data audit. Replaces
state_2026-05-27.md (which was written before the audit and is now stale on
in-sample numbers, sleeve verdicts, and deployment status).

#### Quick read

**Strategies running in paper trade**: TWO sleeves in parallel
- `mom_v1_paper` (top-100 momentum, more diversified) - NAV $98,454.88 (-1.55%)
- `mom_v2_paper` (top-50 momentum, more concentrated) - NAV $96,977.34 (-3.02%)

Both inceptioned 2026-05-01. After 27 days, v1 leading by 1.5pp - consistent
with the in-sample story that diversification helps in choppy regimes.

**Active development**: NONE. Data audit complete. Vol-target / stops /
trend filter all tested on clean data and rejected.

#### What changed in the past 24 hours (audit)

##### Data quality discoveries
1. **Friday spike artifacts** (2010-2018): every Friday, ~150 tickers showed
   bogus closes 5,000-10,000x real values. Affected ITC ($30 -> $14,200),
   TNB ($1.75 -> $13,000), FOOD ($0.32 -> $13,935), and others.
2. **Unadjusted reverse splits**: 673 tickers (WKHS, ARSC, SRNE...) with
   continuously inflated historical closes. yfinance split DB broken
   regardless of `auto_adjust=True/False`.
3. **Impact**: mom_v2's "+21% CAGR in-sample" validation was largely
   fictitious. Real number is +2.72%/yr.

##### Fixes applied
1. **Spike cleanup**: 2,017 rows nulled in `price_cache`.
   Script: `scripts/data_audit/find_price_spikes.py`. DB backup at
   `var/trades.db.bak_pre_spike_cleanup` (4.6 GB).
2. **Universe consistency filter**: new `MAX_HIST_RATIO=100` in
   `factors/universe.py`. Rejects tickers whose historical close is
   > 100x current stable price.
3. **Frozen spec re-baselined**: `test_strategies.py` updated with
   clean-data expected values. Old in-sample values were artifacts.
4. **Dashboard updated**: paper-trade tab now has strategy selector,
   shows both v1 and v2.

#### Current performance (CLEAN DATA, 2026-05-28)

##### mom_v2 (top-50, frozen baseline)
| Window | Total | CAGR | Max DD | Mean Sharpe | Calmar |
|---|---:|---:|---:|---:|---:|
| in_sample 2015-2023 | +27.3% | +2.72% | -55.26% | +0.167 | 0.049 |
| holdout 2024-2026.5 | +80.4% | +28.81% | -33.86% | +0.903 | 0.851 |

##### mom_v1 (top-100, original baseline, NOW THE IN-SAMPLE CHAMP)
| Window | Total | CAGR | Max DD | Mean Sharpe | Calmar |
|---|---:|---:|---:|---:|---:|
| in_sample 2015-2023 | +51.4% | +4.72% | -48.90% | +0.210 | 0.096 |
| holdout 2024-2026.5 | +59.2% | +22.08% | -34.29% | +0.813 | 0.644 |

##### Regime split (why we run both)
- **In-sample** (includes 2021-23 momentum crash): v1 wins all metrics.
  Diversification helps when there is a crash to survive.
- **Held-out** (calm 2024-2026): v2 wins all metrics. Concentration
  captures upside when there is no crash to worry about.
- **Going forward**: paper trade decides. Run both, let live data resolve.

#### Universe and filters

`tradeable_universe(as_of)` rejects tickers unless:
- has cached close on `as_of`
- has >= 252 prior trading days of cached closes (12 months for momentum)
- close >= $5 on `as_of` AND on the 252-day-back reference date
- close / current_stable_price <= 100 (DATA QUALITY, new 2026-05-28)

Universe size: ~2700-3000 tickers depending on date.

#### Transaction cost reality check

Default `HALF_SPREAD_BPS = 5.0` (10bp round-trip). For the small-mid-cap
universe this is optimistic. TC sensitivity sweep (2026-05-28):

| half_bps | round-trip | In-sample CAGR | Held-out CAGR |
|---:|---:|---:|---:|
| 5 (current default) | 10bp | +2.72% | +28.81% |
| 10 | 20bp | +2.32% | +28.33% |
| 15 (realistic) | 30bp | +1.92% | +27.85% |
| 20 | 40bp | +1.52% | +27.37% |
| 30 (worst case) | 60bp | +0.73% | +26.42% |

Held-out result is **robust** - survives any plausible TC. In-sample is
fragile but already marginal at any TC level.

#### Failed experiments (14 total, all closed)

All rejected on CLEAN data unless noted. Detailed in
`memory/sleeves_verdict.md`:

| # | Experiment | Verdict |
|---|---|---|
| 1 | Naive percentile composite | Killed in-sample |
| 2 | Volume-gated sleeves | $1M ADV filter killed mom's premium |
| 3 | Stdev-floor sleeves | No diversification benefit |
| 4 | yfinance-quality sleeve | Lookahead bias |
| 5 | XBRL quality v1 sleeve | Drags combined return |
| 6 | XBRL quality v2 sleeve | Same pattern |
| 7 | mom_quality_screen filter | Killed in-sample |
| 8 | Accruals (Sloan) standalone | Underperforms baseline |
| 9 | mom-then-accruals (combo) | Did not beat mom_v2 |
| 10 | Short-term reversal | Negative expected return |
| 11 | Restricted top500/1000 universe | Survivorship-biased |
| 12 | Intra-rebal stop-loss | -4 to -6pp in-sample CAGR |
| 13 | Stop-loss + same-name reentry | Strictly worse than plain stops |
| 14 | SPY 200-DMA trend filter | -6/-21pp CAGR in/out |
| -- | Vol-target 12-25% | Marginal; not worth complexity |
| -- | Weekly/quarterly rebal | 2024-26 overfit (per momentum_v2_verdict) |

Pattern: no overlay or factor combination meaningfully improves mom_v2
on clean data. The strategy IS the volatility.

#### Infrastructure

##### Code structure (unchanged)
- `trading_bot/factors/momentum.py` - 12-1 momentum (production)
- `trading_bot/factors/universe.py` - filtered universe (now with MAX_HIST_RATIO)
- `trading_bot/execution/factor_backtest.py` - generic factor backtest engine
  (with optional stop_loss_pct, reentry_buffer, position_scale_fn)
- `trading_bot/strategies/momentum_v1.py`, `momentum_v2.py` - frozen specs
- `trading_bot/strategies/test_strategies.py` - regression tests (re-baselined)

##### Paper-trade infrastructure
- `scripts/momentum/paper_rebalance.py --strategy NAME --top-n N`
- `scripts/momentum/paper_mtm.py --strategy NAME`
- `scripts/momentum/daily_price_refresh.py` - bulk yfinance refresh
- `scripts/momentum/daily.bat` - MTMs all sleeves
- `scripts/momentum/rebalance.bat` - rebalances + MTMs all sleeves
- SLEEVES (2026-06-09): 5 systematic — mom_v1, mom_v2, mom_roa_6535,
  **residual_roa_6535** (new winner, inception 2026-06-09, residual-momentum×ROA,
  lower-DD sibling of mom_roa_6535), sector_top4 — + 3 LLM-experiment sleeves.
- BENCHMARK SLEEVE (2026-06-10): `spy_benchmark_paper` — a real $100k
  buy-and-hold SPY position (inception 2026-05-01, qty 138.763611 @ 720.65,
  never rebalanced), MTM'd daily like any sleeve via daily.bat/rebalance.bat.
  This is the S&P 500 "control": 9 paper sleeves total in the DB now (8 strategy
  + 1 benchmark). Seed: scripts/momentum/seed_spy_benchmark.py. 06-09 NAV
  $102,275.72 (+2.276%).
- universe.NON_STOCK_TICKERS (added 2026-06-09): excludes ETFs/indices (sector
  SPDRs, SPY/RSP/QQQ, leveraged SSO/UPRO/QLD/TQQQ, vol SVXY/VIXY, "^" indices)
  from the STOCK tradeable_universe so warmed non-stock tickers can't leak into
  momentum/ROA picks. Frozen tests pass at 0.0000pp.

##### Dashboard
- `trading_bot/dashboard/web.py` - Streamlit dashboard
- Tabs: Live experiment (paper trade), Backtest archive
- Paper-trade tab views (2026-06-10): **📊 Overview (default)** — one dense
  screen: status strip (freshness/SPY today/SPY since inception/next rebal),
  sleeve table (Day%/Total%/α/MaxDD/cash/pos, incl. hidden LLM control + the
  shaded S&P control as a real row), compact NAV chart, top movers among held
  names, LLM-experiment status (latest veto + stop distance + treatment-control
  gap), sector-concentration warnings — plus 🔬 Single sleeve and 📈 NAV charts.
- S&P 500 (SPY) control benchmark: as of 2026-06-10 it is a REAL sleeve
  (`spy_benchmark_paper`, see Paper-trade infrastructure above), not a yfinance
  fetch. Its NAV curve is drawn on every chart (overlay %/$, single-sleeve) and
  shown shaded ("control") in the headlines. `fetch_spy_series` /
  `spy_return_pct` now read that sleeve's paper_nav (fallback: price_cache SPY
  closes) — NO network, which fixes the old "broken"/blank S&P line. Price-only
  SPY to match the dividend-unadjusted sleeves. Plotly legend toggles lines.
- Chart conventions (2026-06-10): %-chart hovers show 3 decimals (nearest
  0.001%); NAV charts add traces in descending latest-value order so the
  `x unified` hover box reads highest→lowest (Plotly orders unified-hover
  entries by trace index — no per-day value-sort exists without custom JS, so
  the order tracks current standings).

##### Audit artifacts
- `scripts/data_audit/find_price_spikes.py` - spike detector + applier
- `scripts/data_audit/find_stale_history.py` - stale-history detector (not applied)
- `scripts/data_audit/verify_cleanup.py` - re-runs baseline post-cleanup
- `scripts/data_audit/tc_sensitivity.py` - TC sweep
- `scripts/data_audit/v1_vs_v2_clean.py` - head-to-head
- `var/data_audit/*.json` - all sweep results

#### Pending / deferred

1. **Slippage realism check** - deferred until ~20 real fills (post-Aug 2026)
2. **Refetch all data with auto_adjust=True** - multi-hour, may not help
   (yfinance split DB broken at source for affected tickers)
3. **Paid PIT data source** - the only way to get truly survivorship-bias-free
   universe. Probably $$$$.
4. **3-6 months of paper-trade data** - the next meaningful OOS evidence

#### Recommended sequence (no urgency)

1. **Run daily.bat after each trading day's close** - keeps both sleeves marked
2. **Run rebalance.bat on 1st trading day of each month** - rebalances both
3. **Check the dashboard occasionally** - compare v1 vs v2 NAV curves
4. **In ~3 months**: review forward NAV; either v1 or v2 will pull ahead, or
   they will tie (keep both)
5. **In ~6-12 months**: enough OOS data to make a real strategy choice

#### Trust budget

- Anything backtested **post-2026-05-28** on the current DB: trustworthy
- Anything **pre-2026-05-28**: contaminated unless re-tested
- The 2024-2026.5 held-out: clean from the start (no spike-tickers held)
- The 2015-2023 in-sample: was largely fake, now corrected but marginal

The strategy validation now rests on:
- 2.4 years of clean held-out data
- Forward paper-trade data starting 2026-05-01 (currently 27 days)

That is the entire trust budget. Plan accordingly.

## AZ.3 — state_2026-06-12.md (verbatim archive; headings demoted two levels)

### Project State - 2026-06-12

> **SUPERSEDED 2026-06-13** by `docs/state_2026-06-13.md`. The standings below
> are the PRE-BACKFILL, phantom-contaminated numbers (the momentum sleeves were
> ~half-built on stale-data phantoms — found + fixed 2026-06-13, record Appendix
> AA). Kept for history; do not treat its sleeve returns as valid.

Current always-current snapshot. Supersedes `state_2026-05-28.md` (whose "Quick
read" was stale at TWO sleeves). For the full onboarding picture see `HANDOFF.md`
(rewritten 2026-06-12); for the chronological log see `docs/record_2026-05-27.md`
(Appendix Z is this session) — **renamed 2026-06-30 to
`docs/Project Record — Full Chronological History.md`**, same file, content
unchanged.

#### Quick read

**9 paper sleeves in `var/trades.db`**, all MTM'd daily (auto via `TradingDailyMTM`
5:15pm) and shown on the dashboard (http://localhost:8501/). Standings at the
2026-06-12 close:

| Sleeve | Type | NAV | Return |
|---|---|---:|---:|
| residual_roa_6535_paper | systematic top-50 | $110,284 | **+10.28%** |
| mom_roa_6535_paper | systematic top-50 | $107,013 | +7.01% |
| sector_top4_paper | systematic top-4 SPDR | $103,803 | +3.80% |
| spy_benchmark_paper | benchmark (buy-hold SPY) | $102,928 | +2.93% |
| mom_v1_paper | systematic top-100 | $102,199 | +2.20% |
| mom_v2_paper | systematic top-50 | $100,343 | +0.34% |
| llm_overlay_sector_top4_paper | LLM macro-veto (treatment) | $99,963 | −0.04% |
| mom_roa_top1_paper | LLM control (holds FN) | $84,851 | −15.15% |
| llm_overlay_mom_roa_top1_paper | LLM treatment (in cash) | $80,766 | −19.23% |

Inception 2026-05-01 for all except the LLM stock pair (05-29) and the LLM sector
overlay (seeded 2026-06-12). 4 of 5 systematic sleeves beat the SPY control;
residual_roa leads comfortably (validates its lower-DD backtest thesis vs
mom_roa). LLM stock pair still deep underwater on the single FN trade (n=1 noise).

**Active development**: none open. This session seeded the sector overlay and
added a held-position split-seam verifier (below).

#### What changed since 2026-05-28

- **+4 sleeves** beyond the original v1/v2: mom_roa_6535, residual_roa_6535
  (deployed/backdated 06-09), sector_top4, spy_benchmark (06-10), plus the 3
  LLM-experiment sleeves (stock pair 05-31, sector overlay built 06-05 /
  **seeded 06-12**).
- **Sector macro-overlay is now live** (`llm_overlay_sector_top4_paper`). First
  decision (2026-06-12, live-web macro): VETO XLE (fragile Hormuz supply-shock
  trade, diverging technicals, USD headwind) → its 25% slot is cash; HOLD
  XLK/XLI/XLB. Control = `sector_top4_paper`. Kill switch: 12mo / ≥30 decisions.
- **KLAC 10:1 split self-healed** on the 06-12 refresh (whole series now on the
  post-split basis; leader's mark consistent — see record Z.1). Loose end closed.
- **New audit tool**: `scripts/data_audit/check_held_split_seams.py` — post-refresh
  check that every held position's latest mark is on a sane basis (day-over-day
  seam + latest/entry band). Run after a price refresh; exits 1 on a suspect mark.

#### Infrastructure (unchanged from HANDOFF.md)

- DB `var/trades.db` (~5 GB); audit backup `var/trades.db.bak_pre_spike_cleanup`
  (never delete). price_cache: split-adjusted, dividend-UNadjusted (auto_adjust=False).
- `daily.bat` (auto 5:15pm): refresh + MTM all 9 + both overlays' check-invalidation.
- `rebalance.bat` (manual, 1st trading day): refresh + rebalance 5 systematic +
  both overlays + MTM all. **Overlay rebalance refuses until LLM decisions logged**
  — that monthly decision is the only human-in-the-loop step (automation of it is
  an open question; the `claude` CLI and ANTHROPIC_API_KEY are both absent on this
  box, so a fully-unattended job needs a credential provisioned first — record Z.4).
- Scheduled tasks: `TradingDashboard` (logon), `TradingDailyMTM` (5:15pm).
- Frozen regression tests `trading_bot/strategies/test_strategies.py` — d=±0.0000pp.

#### Trust budget (unchanged)

In-sample (pre-2026-05-28) is contamination-affected and marginal. Real validation
rests on the 2.4-year clean held-out + forward paper-trade since 2026-05-01 (now
~6 weeks). Forward data is the only new evidence that counts.

#### Open loose ends

1. Slippage realism check — deferred until ~20 real fills (post-Aug 2026).
2. Monthly rebalance decision automation — pending user choice on depth (record Z.4).
3. Next rebalance: 1st trading day of July 2026 (`rebalance.bat`, manual).

## AZ.4 — state_2026-06-13.md (verbatim archive; headings demoted two levels)

### Project State - 2026-06-13

> **SUPERSEDED 2026-07-07 — see `state_2026-07-07.md`** (07-06 cohort deployed,
> Alpaca mirror live, monthly task re-enabled). Kept for history.

Current snapshot. Supersedes `state_2026-06-12.md` (which captured the
pre-backfill, phantom-contaminated standings). Major change since: a systemic
history-gap data bug was found and fixed (backfill + frozen re-baseline), and the
6 contaminated sleeves were re-inceptioned on clean data. Full detail: record
Appendix AA. Onboarding: `HANDOFF.md`.

#### Headline: the momentum sleeves were ~half-built on phantom data (now fixed)

~815 tickers (incl. AAPL, GOOGL, FN, CIEN) had only 2010-2018 + a 2026 burst
cached — a multi-year hole — so their 12-1 momentum was measured against a stale
pre-gap (2018) bar and phantom-ranked into the sleeves (mom_roa_6535 was 56%
phantom, mom_v2 48%, mom_v1 39%; residual_roa only 6%). FIXED 2026-06-13:
backfilled the missing 2019-present daily closes from yfinance (2.25M rows,
auto_adjust=False), re-cleaned spikes (614 rows), re-baselined the frozen tests,
and re-inceptioned the 6 contaminated sleeves fresh at $100k on clean data.

#### Sleeves (9 total)

**Systematic sleeves — BACKDATED to 2026-05-01 on clean data (06-13), aligned with
the ETF sleeves. Clean live returns 05-01→06-12:**

| Sleeve | Type | NAV | Return |
|---|---|---:|---:|
| mom_roa_6535_paper | systematic top-50 | $106,579 | **+6.58%** |
| residual_roa_6535_paper | systematic top-50 | $106,134 | +6.13% |
| sector_top4_paper | systematic top-4 SPDR | $103,803 | +3.80% |
| spy_benchmark_paper | benchmark | $102,928 | +2.93% |
| mom_v1_paper | systematic top-100 | $102,358 | +2.36% |
| mom_v2_paper | systematic top-50 | $101,394 | +1.39% |

On clean live data mom_roa leads, residual 2nd; both beat SPY; mom_v1/v2 trail it.
(residual's contaminated +10.28% over this window was partly phantom-selection
inflation — clean is +6.13%; record AC.1.)

**LLM stock pair — kept at 2026-06-12 re-inception (NOT backdated: backdating the
treatment's decisions would inject hindsight and break the experiment):**

| Sleeve | Inception | Holds | NAV |
|---|---|---|---:|
| mom_roa_top1_paper | 2026-06-12 | AAOI (new clean #1) | $99,950 |
| llm_overlay_mom_roa_top1_paper | 2026-06-12 | cash (AAOI vetoed) | $100,000 |
| llm_overlay_sector_top4_paper | 2026-06-05 (seeded 06-12) | XLK/XLI/XLB, XLE→cash | $99,962 |

#### TRUST BUDGET — important

- **Forward paper-trade**: trustworthy from 2026-06-12 for the 6 re-inceptioned
  sleeves (clean data); from 2026-05-01 for the 3 ETF sleeves. The contaminated
  2026-05-01 → 06-12 record of the 6 is archived (var/reinception_archive_2026-06-13.json)
  but INVALID.
- **Backtest numbers**: RE-VALIDATED 2026-06-13 on the backfilled cache
  (docs/revalidation_2026-06-13.md). residual_roa_6535 confirmed best risk-adjusted
  (held-out Sharpe 1.21 / Calmar 1.60 / −20% DD, in-sample champion +9.47%);
  mom_roa_6535 in-sample halved (9.86→4.89, was phantom-inflated) but still #1
  held-out raw CAGR (35.59%). Caveat: absolute CAGRs are survivor-biased upper
  bounds (only currently-listed names in the cache). No sleeve invalidated.
- **Frozen tests**: re-baselined 2026-06-13 to the post-backfill values
  (v1 14.5547/70 & 1.8792/156; v2 14.4062/38 & 10.2194/87), green at ±0.0000pp.

#### Infrastructure (unchanged unless noted)

- DB `var/trades.db` (~5 GB, now ~37M price rows after backfill). price_cache:
  split-adjusted, dividend-UNadjusted (auto_adjust=False).
- daily.bat (auto 5:15pm): refresh + MTM all 9 + both overlays' check-invalidation.
- rebalance.bat (manual, 1st trading day): systematic + overlay rebalances + MTM.
  Overlay decisions: docs/overlay_decision_runbook.md + scripts/momentum/overlay_prep.bat.
- New data_audit tools: backfill_history_gaps.py, archive_contaminated_sleeves.py,
  reinception_wipe.py, check_held_split_seams.py.

#### Open loose ends

1. ~~Re-validate backtests~~ **DONE** (docs/revalidation_2026-06-13.md).
2. ~~Backdate sleeves to 05-01~~ **DONE** (record AC.1; systematic only — LLM pair
   can't be honestly backdated).
3. ~~Slippage realism~~ **DONE** (record AC.2): edge robust to 40bps half-spread.
   ~~SUB-GAP: ADV not warmed~~ **DONE** (record AD): the "0/134" was stale volume
   (daily_price_refresh writes closes but not volumes), not a missing cache;
   MIN_DOLLAR_VOL=0 so the live universe was never affected. Warmed held-name
   volume → held names are liquid (median 60d ADV $100.6M; thin tail of 5 names
   <$1M/day, harmless at $100k/sleeve scale). FIXED — final form (record AI,
   supersedes AE): daily_price_refresh now persists Volume alongside Close from
   the same yfinance download, so the whole universe's volume is fresh DAILY at
   zero extra cost. The redundant monthly warm_held_volumes step was removed from
   rebalance.bat (script kept as a manual backstop). Volume-staleness root cause
   eliminated.
4. **Survivorship bias** — dominant un-fixable data limitation (backfill filled
   only currently-listed names). Needs paid PIT/delisted data. User said skip.
   Trust the live forward record over backtest levels.
5. Overlay automation — Option A built (runbook + overlay_prep). Option B
   (unattended cron, overlay_auto_decide.py + monthly_auto.bat) SCAFFOLDED but
   UNTESTED — needs `pip install anthropic` + ANTHROPIC_API_KEY (runbook "Option B
   activation"). Safe-fail verified.
6. Real slippage tracker — activates at ~20 real broker fills (post-Aug 2026).
7. Next rebalance: 1st trading day of July 2026 (07-01). overlay_prep already run
   + all 5 overlay decisions logged for 07-01 (record AJ.4): stock #1 = BE (VETO);
   sectors XLK HOLD, XLE VETO, XLI HOLD, XLB HOLD.
8. **June-30 lock prep DONE (record AJ):** KLAC 10:1 position fix (residual_roa
   -> +11.77%, now leader), SATS->ECHO 1:1 rename, AAOI verified (cache matches
   yfinance $150.10; web/yfinance conflict UNRESOLVED — eyeball 06-30 close),
   overlay evals logged. **OPEN before 07-01 rebalance (NOT lock-critical):** KLAC
   price_cache pre/post-split SEAM (May $1726 vs June $278) — divide pre-~05-30
   KLAC closes by 10 or the 07-01 momentum rank sees ~-84% garbage for KLAC.
9. **Zero-volume untradeable names in the sleeves (MIN_DOLLAR_VOL=0 root cause):**
   06-30 the dash showed 7 "stale" holdings = 6 thin micro-caps lagging a day
   (warmed, self-healing via daily.bat). Verifying the worst, **QDMI** (residual)
   is an unidentifiable zero-volume instrument with flat round-number stepping
   quotes ($69.92->$26->$8, no volume) marked -89% ($1998->$228). Left at $8 for
   the lock (user choice a; unverifiable, self-clears at 07-01 when momentum drops
   it). QDMI/BKFG/CNTA/WBHC are all zero-volume — they enter because the dollar-
   volume filter is OFF. RECOMMENDATION (post-lock, re-baselines frozen tests):
   set a small MIN_DOLLAR_VOL floor so untradeable names can't be selected.
10. **LLM-cascade 3rd overlay pair (record AK, built 06-30):** two new $100k
    sleeves `llm_cascade_top1_paper` + `llm_cascade_sector4_paper` (inception
    07-01) that, on a VETO, cascade to the next-best instead of going to cash —
    always invested. Run ALONGSIDE the cash overlays (clean veto-vs-cash signal
    preserved). Share the cash overlays' decision logs; wired into rebalance.bat
    + daily.bat; dashboard auto-shows them. **OPEN before they diverge on 07-01:**
    overlay_prep only prints #1 / top-4 — needs a deeper-candidates view + the
    extra evals (stock #2+ since BE is vetoed; sector #5 since only 3 HOLDs), else
    the cascade falls back to = the control on 07-01. **RESOLVED 06-30 (record
    AK.3-AK.6):** overlay_prep got the deeper view; deeper evals logged (cascade
    stock=WDC, sector=XLK/XLI/XLB/XLV); the llm_overlay_log UNIQUE(date) schema bug
    that was silently overwriting multi-name decisions was fixed to
    UNIQUE(date,ticker); and all 6 LLM-experiment sleeves were aligned to fresh
    $100k/07-01 (archived, reversible).
11. **TWO sector_top4 controls now (record AK.6, 06-30):** the 07-01 alignment reset
    desynced sector_top4 from the systematic comparison, so it's kept as BOTH:
    `sector_top4_paper` = the 07-01 reset (LLM-experiment control, head-to-head with
    the sector overlays/cascade); `sector_top4_full_paper` = NEW, restored from
    var/align_llm_07_01_archive.json with the full 05-01 history (NAV $102,423.84 /
    +2.42%, holds XLI/XLE/XLB/XLK) — the systematic-comparison control. Both rebalance
    identically going forward (differ only in pre-07-01 P&L). The sector overlay
    CONTROL_STRATEGY still points at sector_top4_paper, so the experiment is unchanged.
12. **S&P 500 07-01 baseline (record AK.7, 06-30):** `spy_benchmark_0701_paper` —
    a $100k buy-and-hold SPY control aligned with the 07-01 LLM cohort (parallel to
    the 05-01 `spy_benchmark_paper`). Created as a $100k cash stub now; auto-buys SPY
    on the 07-01 rebalance (idempotent seed_spy_benchmark.py --sleeve/--inception,
    wired into rebalance.bat; MTM in daily.bat). Renders as a dotted "S&P 500 (07-01)"
    benchmark line. NB sleeve count is now ~10 — the Overview unified-hover box was
    enlarged (height 430, font 11) to fit.
13. **Alpaca paper integration STARTED (record AL, 06-30):** Evan opened an Alpaca
    PAPER account (ACTIVE $100k) and wants automated mirroring of the sleeves.
    `trading_bot/execution/alpaca_client.py` = thin httpx client (paper-default,
    live-guarded, env keys APCA_API_*, X-Request-IDs -> var/alpaca_request_ids.log);
    smoke test returns 200. **HELD:** Alpaca caps ~3 paper accounts/login (Evan wanted
    10, 1/sleeve) — Evan is testing his real cap, then we map sleeves->accounts and
    wire automated paper order routing. Claude never creates accounts / enters keys /
    fires LIVE orders.
14. **7/1 clean-start cohort (record AL):** the 4 May systematic sleeves now have
    07-01 duplicates (mom_v1_0701 / mom_v2_0701 / mom_roa_6535_0701 /
    residual_roa_6535_0701, fresh $100k, deploy on the 07-01 rebalance). With
    sector_top4_paper (07-01), spy_benchmark_0701, and the 6 LLM sleeves, the whole
    07-01 cohort starts clean on one date — the set that will map to Alpaca paper.
    paper_rebalance._strategy_config strips `_0701` to reuse base configs. PENDING: a
    dedicated dashboard "7/1 cohort" panel (deferred until Alpaca cohort is finalized).
15. **Alpaca routing BUILT (record AL.1):** cap=3, 3 accounts created + verified. Mapping
    ACCT1 residual_roa_6535_0701 / ACCT2 mom_roa_6535_0701 / ACCT3 spy_benchmark_0701.
    Keys in `alpaca_keys.env` (gitignored). `alpaca_accounts.py` (loader+verify) +
    `alpaca_sync.py` (weight-mirror, fractional, dry-run default / --execute, paper-
    guarded). rebalance.bat ends with `alpaca_sync --all --execute`, so the mirror fires
    on each MANUAL monthly rebalance — first real mirror = 07-01. Preview anytime:
    `python -m trading_bot.execution.alpaca_sync --all`. NB rebalance.bat is not
    scheduled (only daily.bat/MTM is) — Evan runs it on the 1st.

## AZ.5 — state_2026-07-07.md (verbatim archive; headings demoted two levels)

### Project State - 2026-07-07

Current snapshot. Supersedes `state_2026-06-13.md`. Major change since: the
07-01/07-06 clean-start cohort was reset and **deployed** — 11 new sleeves went
live on 2026-07-06 close, 3 mirrored to real Alpaca PAPER accounts, and the
monthly rebalance is now a re-enabled scheduled task. Full detail: record
Appendices AL–AV. Onboarding: `HANDOFF.md`.

#### Headline: the 07-06 cohort is live (17 sleeves total in the DB)

The project now runs three parallel families (full roster + rationale in
`HANDOFF.md`; `CLAUDE.md` holds durable invariants only, since 2026-07-08):

1. **6 continuous May systematic + benchmark** (inception 2026-05-01, the
   6 contaminated sleeves re-inceptioned 2026-06-13 on clean data):
   `mom_v1_paper`, `mom_v2_paper`, `mom_roa_6535_paper`,
   `residual_roa_6535_paper`, `sector_top4_full_paper` (continuous systematic
   twin), `spy_benchmark_paper`.
2. **11-sleeve 07-06 clean-start cohort** (inception 2026-07-06, DEPLOYED
   2026-07-07 via the `cohort-0706-deploy` scheduled task — record AV): the
   5 systematic `_0701` duplicates + `spy_benchmark_0701_paper`, plus the 6
   LLM-experiment sleeves (stock control/overlay/cascade + sector
   control/overlay/cascade). The 3 marked below mirror to Alpaca PAPER.

#### Sleeves (17 total, all NAV'd 2026-07-07)

**Continuous May family:**

| Sleeve | NAV | Inception |
|---|---:|---|
| residual_roa_6535_paper | $104,964 | 2026-05-01 (re-incep 06-13) |
| spy_benchmark_paper | $103,755 | 2026-05-01 |
| sector_top4_full_paper | $102,271 | 2026-05-29 |
| mom_roa_6535_paper | $96,982 | 2026-05-01 (re-incep 06-13) |
| mom_v2_paper | $95,200 | 2026-05-01 (re-incep 06-13) |
| mom_v1_paper | $95,124 | 2026-05-01 (re-incep 06-13) |

**07-06 cohort (deployed 2026-07-07; ★ = mirrored to Alpaca PAPER):**

| Sleeve | Holds | NAV |
|---|---|---:|
| mom_roa_top1_paper (stock control) | BE (Bloom Energy) | $102,130 |
| llm_cascade_top1_paper (stock cascade) | WDC (BE vetoed → #2) | $100,805 |
| mom_roa_6535_0701_paper ★ | top-50 | $100,355 |
| sector_top4_paper (sector control) | XLK/XLE/XLI/XLB | $100,396 |
| mom_v2_0701_paper | top-50 | $100,212 |
| residual_roa_6535_0701_paper ★ | top-48 (2 untradable) | $100,207 |
| mom_v1_0701_paper | top-100 | $100,141 |
| llm_overlay_sector_top4_paper (sector veto) | XLK/XLI/XLB, XLE→cash | $100,112 |
| llm_cascade_sector4_paper (sector cascade) | XLK/XLI/XLB/XLV | $100,060 |
| llm_overlay_mom_roa_top1_paper (stock veto) | **cash** (BE vetoed) | $100,000 |
| spy_benchmark_0701_paper ★ | 133.106 SPY | $99,525 |

#### 07-06 deploy — LLM decisions logged 2026-07-07 (record AV)

- **Stock control BE (Bloom Energy), score 4, VETO** (128x fwd P/E, price above
  consensus target, rolling over). Overlay treatment → cash.
- **Stock cascade → WDC (Western Digital), score 6, BUY** (HDD sold out through
  2026 = real revenue visibility, not pure momentum).
- **Sectors: XLK HOLD(6), XLE VETO(3, fragile geopolitical oil rally), XLI
  HOLD(8, cleanest), XLB HOLD(5, marginal).** Sector cascade needed a 4th HOLD →
  **XLV (Health Care), score 7, HOLD**.

#### Alpaca PAPER mirror (record AV)

`alpaca_sync --all --execute` submitted **99 DAY orders, 0 rejections** across
Evan's 3 fresh accounts (residual_roa_6535_0701 48/48, mom_roa_6535_0701 50/50,
spy_benchmark_0701 1/1), queued to the next open. Whole-share/broker-realistic
logic (record AT) means untradable/non-fractionable names are floored to whole
shares or dropped in BOTH the DB sim and the Alpaca mirror — so the two agree.
Claude never creates accounts / enters keys / fires LIVE orders.

#### Monthly automation (record AV, memory [[monthly-rebalance-trigger-timing-bug]])

`monthy-llm-rebalance` scheduled task is **RE-ENABLED**, cron `0 18 * * *`
(6:03pm local). Its `rebalance_log.md` gate no-ops the rest of July; first live
fire is 2026-08-01. The `cohort-0706-deploy` one-time task auto-disabled after
its successful 2026-07-07 run.

#### Trust budget (unchanged from 06-13 unless noted)

- **Forward paper-trade** is the only true OOS test. Continuous May family:
  trustworthy from 2026-06-13 (6 re-inceptioned) / 2026-05-01 (benchmarks). New
  cohort: trustworthy from 2026-07-06.
- **Backtests**: last re-validated 2026-06-13 (`docs/revalidation_2026-06-13.md`).
  residual_roa_6535 = best risk-adjusted; absolute CAGRs are survivor-biased
  upper bounds.
- **Frozen tests**: at ±0.0000pp (post-backfill baseline). The broker-realistic
  `fractionability` path defaults unknown tickers → tradable+fractionable, so
  backtests/frozen specs are UNAFFECTED (verified).

#### Infrastructure (unchanged unless noted)

- DB `var/trades.db` (~5 GB). price_cache split-adjusted, dividend-UNadjusted
  (auto_adjust=False). 2026-07-06 close coverage = 5,206 tickers (full).
- `daily.bat` (auto 5:15pm `TradingDailyMTM`): refresh + MTM all sleeves.
- `rebalance.bat` (all 10 paper lines now carry `--broker-realistic`) — but the
  monthly run is now driven by the `monthy-llm-rebalance` scheduled task, not a
  manual invocation.
- New code (record AT): `trading_bot/execution/fractionability.py`
  (`alpaca_asset_meta` cache), `alpaca_client.get_asset`, broker-realistic
  paths in `alpaca_sync` + `paper_rebalance`.
- RuFlo V3 statusline DISABLED in `.claude/settings.json` (was spawning stray
  `%`-named files in the repo root — record AW).

#### Open loose ends

1. **Stray shadow-named files in repo root RECUR** (record AW): `20%` traced to
   the RuFlo statusline (disabled). But format-spec-named files (`4`, `10.2f}`,
   `12.2f}`) reappeared 2026-07-07 ~18:29 from a DIFFERENT source — a scheduled
   run leaking an unescaped shell/format-spec redirect target. Source NOT yet
   found; harmless empty files but they clutter `git status`. Also `scratch_positions.csv`
   (49 KB) dropped at 18:29 by an evening scheduled task.
2. **`PRD_ROADMAP.md`** (25 KB, untracked, created 2026-07-07 23:11) — appeared
   in the repo root; author/intent unconfirmed. Do not touch without asking Evan.
3. First Alpaca fills settle at next market open (07-08) — verify the 99 orders
   filled and reconcile against the 3 sleeves' DB positions.
4. Real slippage tracker activates at ~20 real broker fills (post-Aug 2026).
5. Survivorship bias — dominant un-fixable data limitation; trust live forward
   record over backtest levels.
6. Dedicated dashboard "cohort" panel still deferred.

# Appendix BA - Owed frozen-test run cleared (cash-buffer commit 3807f23) (2026-07-08, ~20:35 local)

Resolves the open item flagged in Appendix AY item 3. The 2026-07-08 12:47 commit `3807f23`
("Add 1% cash buffer to Alpaca mirror sizing", `trading_bot/execution/alpaca_sync.py`, an Opus
session) had landed with no evidence of a frozen-test run, and AY deferred it because the handoff
executed inside the 5:00-6:30pm MTM window. Run now at ~20:35 local (outside the window), via the
invocation the test file documents (`python -m trading_bot.strategies.test_strategies` — pytest is
not installed in this venv, only the optional-alternate note in the file's docstring mentions it):

```
  [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
  [OK  ] momentum_v1/2025_H1: tpnl=+1.8792%  (exp +1.8792%,  d= -0.0000pp)  trades=156 (exp 156, d= +0)
  [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
  [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
  All regression tests passed.
```

All four pinned configs at d=±0.0000pp — as expected, since the cash-buffer change is confined to
the Alpaca mirror-sizing path (`alpaca_sync.py`) and never touches the strategy/factor/sim code the
frozen tests exercise. AY item 3 is closed.


# Appendix BB - M2.1 coverage gate (check_coverage.py); caught live 07-08 incomplete-publication shortfall (2026-07-09, ~13:20 local)

**PRD milestone M2, task 1** (Data-quality guardrails / coverage gate). First execution task under
`PRD_ROADMAP.md` after the M1 documentation catch-up. Ops/infra only, read-only against the DB.

**WHAT.** New `scripts/momentum/check_coverage.py` (read-only, `file:...?mode=ro`): reports the
non-NULL `close` count for the latest cached trading date (or `--date`), compares it to a floor,
and exits 0 (PASS) / 1 (FAIL). Floor = `max(5000, 90% * baseline)` where baseline is the **median**
close count over the prior 10 *trading* days. Market-closed days leave only a couple hundred stray
closes (e.g. Juneteenth 2026-06-19 = 204, the observed-July-4th holiday 2026-07-03 = 213), so dates
below `MIN_TRADING_DAY_COUNT=1000` are excluded from the baseline — median alone would already be
robust to one or two, this makes it explicit. `--floor N` overrides the computed floor.

**WHY.** Mirrors, in code, the manual "coverage >= 5,000 closes" gate the 07-06 deploy enforced by
hand (Appendix AV). The failure class is incomplete yfinance publication (Appendix AU): a day's
closes arrive for only ~4,400 of ~5,200 tickers and never settle, and MTM on that partial data
silently mismarks NAVs/ranks. M2.2 will wire this in front of MTM in `daily.bat`.

**HOW / verification (done-check from the PRD).**

- `--date 2026-07-07` (last complete day): `5206` closes >= floor `5000` -> **PASS, exit 0**.
- `--floor 999999`: **FAIL, exit 1**.
- Default (latest cached date) -> **FAIL, exit 1**, and this is a *real* catch, not a contrived one:
  the latest cached day **2026-07-08 has only 4,379 closes vs a 5,247 baseline** (~16% short) —
  a live incomplete-publication event of exactly the Appendix AU class. Reported, not touched: per
  the standing rule, data that looks wrong is surfaced, and backfilling/refreshing is Evan's call.
  (Consequence to be aware of: any MTM already written for 2026-07-08 used partial data.)

Frozen tests after the change (`python -m trading_bot.strategies.test_strategies`):

```
  [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
  [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
  [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
  [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
  All regression tests passed.
```

d=±0.0000pp on all four pinned configs — expected, the script is read-only and touches no
strategy/factor/sim code. M2.1 done; next open task is M2.2 (wire the gate into `daily.bat`).


# Appendix BC - M2.2 coverage gate wired into daily.bat, ahead of MTM (2026-07-09, ~13:30 local)

**PRD milestone M2, task 2.** Wire the M2.1 coverage gate into the daily flow so an
incomplete-publication day fails loudly instead of MTM-ing on partial data.

**WHAT.** Inserted a gate block in `scripts/momentum/daily.bat` immediately after the price-refresh
step and before the first MTM:

```
echo === Coverage gate: require full price publication before MTM ===
.venv\Scripts\python.exe -m scripts.momentum.check_coverage
if errorlevel 1 (
    echo COVERAGE FAIL - incomplete price publication. Skipping all MTM and overlay ops today.
    echo Investigate before trusting today's NAVs. See check_coverage output above.
    exit /b 1
)
```

On failure it echoes a `COVERAGE FAIL` line, skips **everything** downstream (all MTM *and* the
overlay `check-invalidation` ops), and `exit /b 1`.

**WHY the placement.** The scheduled task runs `cmd /c ...\daily.bat > var\last_daily_run.log 2>&1`
(verified via `Get-ScheduledTask TradingDailyMTM`), so daily.bat's whole stdout is already
redirected to `last_daily_run.log`. The `COVERAGE FAIL` echo therefore lands in that log with no
explicit `>>` append — and an explicit append was deliberately *avoided*, because the parent `cmd`
holds that file open for the run and a child `>>` to the same path can collide. `exit /b 1`
propagates as the batch's exit code, so the `cmd /c` returns 1 and the task history shows failure.
Putting the gate before the overlay ops is also a safety win: on a bad-data day it prevents
`llm_overlay_ops`/`sector_overlay_ops check-invalidation` from firing a stop-loss **sell** off a
missing/partial price.

**HOW / verification.**

- `.bat` confirmed **pure ASCII** (byte scan, no >127 bytes) — the cmd.exe parse-corruption trap
  (Appendix AS) avoided. Echo text carries no parens, so no `^(`/`^)` escaping needed inside the
  `if` block.
- Gate control flow tested in **isolation** (a standalone harness replicating the exact block,
  calling the real `check_coverage`), both branches:
  - `--date 2026-07-07` -> `COVERAGE PASS` (5206 >= 5000), harness `exit 0`, "would proceed to MTM".
  - `--floor 999999` -> `COVERAGE FAIL` line printed, MTM skipped, `exit /b 1`.
- **Did NOT run the full production `daily.bat`.** It executes the trade-capable
  `*_ops check-invalidation` steps (they call `paper_trader.sell` on a stop breach with no
  `--dry-run`), which the PRD forbids me from running; and 2026-07-09 is an in-progress trading day
  with no settled closes (the latest cached day, 2026-07-08, is itself the incomplete one from
  Appendix BB). Full end-to-end validation will happen when `TradingDailyMTM` fires at 5:15pm, or
  when Evan runs it. The isolated harness exercises the identical cmd.exe control flow.

Frozen tests (no Python changed this task; run anyway per the standing order):

```
  [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
  [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
  [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
  [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
  All regression tests passed.
```

d=±0.0000pp (4/4). M2.2 done; next open task is M2.3 (anomaly detector, `check_anomalies.py`).


# Appendix BD - M2.3 anomaly detector (check_anomalies.py) wired into daily.bat (2026-07-09, ~13:35 local)

**PRD milestone M2, task 3.** Detect the split-misapplication failure class (record Appendix X /
KLAC 2026-06-12) the same day it happens, and surface missing marks on held names.

**WHAT.** New read-only `scripts/momentum/check_anomalies.py`. For the latest trading day vs the
prior one it flags: (1) held names (open in any sleeve) with `|1-day move|` > `--held-threshold`
(default 300%); (2) any ticker with `|1-day move|` > `--cache-threshold` (default 1000%, the KLAC
tell) **and** prior close >= `--min-price` (default \$1); (3) held names with no close on the
target date. Console + a dated section appended to `var/anomaly_report.log`. **Non-blocking**:
always exits 0, because a huge move can be legitimate news — halting MTM on it would be wrong.
Wired into `daily.bat` after the last MTM, before the graphify step, with no errorlevel check.

**WHY the `--min-price` floor.** First live run without it flagged `WBBA \$0.0007->\$0.01 (+1244%)`
— a sub-penny nanocap whose tiny absolute move is a huge ratio. That is noise, not the tell (KLAC
was ~\$800 when it misfired). The floor applies only to the cache-wide rule; held names are exempt
(we want to know about anything we own regardless of price, and the universe filters keep sub-penny
names out of holdings anyway).

**HOW / verification.**

- `--date 2026-07-07` (both days complete): **"0 anomalies for 2026-07-07"** — the clean dated
  entry the done-check asks for, written to `var/anomaly_report.log`.
- Default (latest = the incomplete 2026-07-08 from Appendix BB): correctly flags **4 held names with
  no close** — `AFJK` (mom_v1/mom_roa_6535 x2 cohorts), `EACO`, `FMBM`, `KFII`
  (residual_roa_6535) — among the ~800 tickers missing on that partial-publication day. Exit 0
  (non-blocking). This is independent confirmation that 2026-07-08's incompleteness reached actual
  holdings, not just the cache tail.
- `daily.bat` re-confirmed **pure ASCII**; the anomaly echo's parens are escaped `^(`/`^)` inside
  the block.

Frozen tests (new Python file):

```
  [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
  [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
  [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
  [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
  All regression tests passed.
```

d=±0.0000pp (4/4). M2.3 done; next open task is M2.4 (cache-gap audit, `check_cache_gaps.py`) — the
last M2 task.

**Standing finding for Evan (unchanged, restated):** 2026-07-08 was marked-to-market on incomplete
data (4,379 closes; 158 held names, >=4 with no mark). Per the standing order this is REPORTED, not
fixed — whether to re-refresh 07-08 and re-MTM is Evan's call.


# Appendix BE - M2.4 cache-gap auditor (check_cache_gaps.py); full run 1/5207 flagged, M2 complete (2026-07-09, ~13:40 local)

**PRD milestone M2, task 4 — completes M2 (Data-quality guardrails).** The re-runnable detector for
the Appendix AA failure class (2026-06-13: ~815 tickers with a multi-year history hole that
phantom-ranked stale names into half of every momentum sleeve).

**WHAT.** New read-only `scripts/momentum/check_cache_gaps.py`. Builds the real trading-day calendar
for a lookback window (`--months`, default 13 — the 12-1 momentum need), takes every ticker with a
close on the last 3 calendar days as "rankable", and for each finds the longest run of consecutive
calendar trading days with no close **inside its own first..last range**. Flags runs > `--max-gap`
(default 5). Bulk-loads the window's closes once (~1.3M rows) and indexes against the calendar, so a
full ~5,200-ticker run is ~10s. Appends a dated report to `var/cache_gap_report.log`; writes nothing
to the DB.

**HOW / verification — full run (done-check: "full run completes; findings documented").**

```
window=2025-05-28..2026-07-08  trading_days=279  rankable=5207  max_gap>5
flagged: 1 of 5207 rankable tickers have an internal hole > 5 consecutive trading days.
  BDPT     worst_gap=  8d  2026-03-27..2026-04-08  window_coverage=78%
```

**1 of 5,207** rankable tickers flagged — the 2026-06-13 backfill is holding; no 815-class
recurrence. The single flagged name, **BDPT** (8 trading-day hole late Mar-early Apr 2026), is
**not held by any sleeve** (verified against open `paper_positions`), so it has zero live impact —
a likely halt/data outage in one nanocap, reported not fixed per the standing order. Re-run monthly
in one command per the M2 success criteria.

Frozen tests (new Python file):

```
  [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
  [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
  [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
  [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
  All regression tests passed.
```

d=±0.0000pp (4/4).

**M2 milestone snapshot.** All four data-quality guardrails now exist, all read-only:
`check_coverage.py` (BB, wired into daily.bat BC), `check_anomalies.py` (BD, wired BD),
`check_cache_gaps.py` (this entry, standalone monthly). The three deadline failure classes
(coverage / spikes / gaps) are detectable same-day before the 2026-08-01 unattended rebalance.
Next: M3 (unattended-automation safety) — pre-inception NAV guard, post-run verifier, verifier
wiring, and Evan-facing failure surfacing.
