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
- [BF — M3.1 pre-inception NAV guard in paper_mtm + regression test](#appendix-bf---m31-pre-inception-nav-guard-in-paper_mtmpy--fixture-regression-test-2026-07-09-1350-local) (07-09)
- [BG — M3.2 post-run verifier (verify_run.py)](#appendix-bg---m32-post-run-verifier-verify_runpy-2026-07-09-1405-local) (07-09)
- [BH — First live coverage-gate catch: 07-09 MTM skipped, backfill deferred](#appendix-bh---first-live-coverage-gate-catch-07-09-mtm-skipped-backfill-deferred-2026-07-09-2235-local) (07-09)
- [BI — M3.3+M3.4 verifier wired into bats + ops stamp; M3 complete](#appendix-bi---m33m34-verifier-wired-into-dailymonthly-bats--ops-status-stamp-m3-complete-2026-07-09-2245-local) (07-09)
- [BJ — M4.1 experiment kill-switch tracker (experiment_report.py)](#appendix-bj---m41-experiment-kill-switch-tracker-experiment_reportpy-2026-07-09-2315-local) (07-09)
- [BK — M4.2 control-vs-treatment NAV divergence in experiment_report.py](#appendix-bk---m42-control-vs-treatment-nav-divergence-in-experiment_reportpy-2026-07-09-2325-local) (07-09)
- [BL — M4.3 kill-switch counters in dashboard LLM panel; M4 complete](#appendix-bl---m43-kill-switch-counters-in-the-dashboard-llm-panel-m4-complete-2026-07-09-2335-local) (07-09)
- [BM — M5 backup hygiene: rotating backups + weekly task + restore drill](#appendix-bm---m5-backup-hygiene-rotating-vacuum-into-backups--weekly-task--restore-drill-2026-07-09-2330-local) (07-09)
- [BN — M3.5 catch-up marking: self-healing daily MTM (option A)](#appendix-bn---m35-catch-up-marking-self-healing-daily-mtm-option-a-evan-authorized-2026-07-09-2355-local) (07-09)
- [BO — 07-09 NAV gap backfilled (settled + catch-up); provenance anomaly noted](#appendix-bo---07-09-nav-gap-backfilled-settled--catch-up-a-provenance-anomaly-noted-2026-07-10-1445-local) (07-10)
- [BP — 07-09 provenance RESOLVED: concurrent session backfilled it (gate-bypass risk)](#appendix-bp---07-09-provenance-resolved-a-concurrent-session-backfilled-it-gate-bypass-risk-noted-2026-07-10-1510-local) (07-10)
- [BQ — Coverage gate moved into paper_mtm.py; raw-MTM bypass closed](#appendix-bq---coverage-gate-moved-into-paper_mtmpy-itself-raw-mtm-bypass-closed-2026-07-10-1515-local) (07-10)
- [BR - Roadmap complete through M5 (M6 gated); 07-11 verification + HANDOFF fix](#appendix-br---prd-roadmap-complete-through-m5-m6-gated-07-11-verification-pass--handoff-freshness-fix-2026-07-11-2000-local) (07-11)
- [BS - Full audit + 4 fixes (monthly-rebalance path): verify wiring, gate/rebalance interaction, schedule drift](#appendix-bs---full-audit-monthly-rebalance-path--4-fixes-verify-wiring-coverage-gaterebalance-interaction-schedule-drift-2026-07-11-1500-local) (07-11)
- [BT - Monthly-rebalance cron shifted to 6:03pm (audit F4 applied)](#appendix-bt---monthly-rebalance-cron-shifted-533pm---603pm-audit-f4-applied-per-evan-2026-07-11-1520-local) (07-11)
- [BU - Prereg'd champ tweaks: overlays FAIL on clean data; residual 80/20 at-threshold](#appendix-bu---pre-registered-champ-tweak-experiments-on-clean-data-preemptive-overlays-fail-weight-sweep-finds-one-at-threshold-candidate-residual-8020-2026-07-14-0105-local) (07-14)
- [BV - EXPLORATORY residual hi-weight extension: w80 a plateau not a spike; no deploy](#appendix-bv---exploratory-post-hoc-residual-hi-weight-extension-w80-is-a-plateau-not-an-edge-spike-the-roa-leg-wants-10-20-percent-not-35-2026-07-14-0135-local) (07-14)
- [BW - Residual weight ladder DEPLOYED (10 sleeves, 05-01 replay); BV plateau -> live forward test](#appendix-bw---residual-weight-ladder-deployed-10-forward-test-sleeves-seeded-05-01-by-replay-bv-plateau---live-2026-07-14-1830-local) (07-14)
- [BX - Dashboard: residual ladder own panel; daily-report tasks self-commit + auto-push](#appendix-bx---residual-ladder-gets-its-own-dashboard-panel-daily-report-tasks-now-self-commit--auto-push-2026-07-14-1900-local) (07-14)
- [BY - Coverage-lag fix: morning refresh task (TradingMorningMTM); overlay stops found dormant](#appendix-by---coverage-lag-fixed-with-a-morning-refresh-task-tradingmorningmtm-separate-finding-overlay-invalidation-stops-are-dormant-2026-07-15-1440-local) (07-15)
- [BZ - Dormant overlay invalidation stops fixed: daily enforcement as-of the last settled close (Evan: option a)](#appendix-bz---dormant-overlay-invalidation-stops-fixed-daily-enforcement-as-of-the-last-settled-close-evan-option-a-2026-07-15-1730-local) (07-15)
- [CA - Stock-overlay stop check hardened: match the stop to the held ticker (cascade-log mispairing bug)](#appendix-ca---stock-overlay-stop-check-hardened-match-the-stop-to-the-held-ticker-cascade-log-mispairing-bug-2026-07-15-2020-local) (07-15)
- [CB - Doc-hygiene: stale --settled stop comments corrected + navigation docstrings](#appendix-cb---doc-hygiene-pass-stale-stop-comments-aligned-to---settled-enforcement-plus-modulepackage-navigation-docstrings-2026-07-15-2050-local) (07-15)
- [CC - Coverage gate validated LIVE: mid-market refresh rejected, partial bar self-healed, no NAV contamination](#appendix-cc---coverage-gate-validated-live-a-mid-market-morning_refresh-run-2026-07-16-1301-was-correctly-rejected-partial-bar-self-healed-with-no-nav-contamination-2026-07-17-1320-local) (07-17)
- [CD - Residual ladder -> 3-cadence experiment (9 monthly points + 19 weekly + 19 biweekly, 47 new sleeves; TradingLadderRebalance)](#appendix-cd---residual-weight-ladder-extended-to-a-3-cadence-experiment-9-monthly-points-added--full-19-point-weekly-and-biweekly-ladders-replay-seeded-05-01-live-forward-via-tradingladderrebalance-2026-07-17-1410-local) (07-17)
- [CE - QQQ (Nasdaq-100) second index control: 2 buy-hold sleeves, dotted line on every panel](#appendix-ce---nasdaq-100-qqq-added-as-a-second-index-control-two-buy-hold-benchmark-sleeves--dotted-line-on-every-overview-panel-2026-07-17-1430-local) (07-17)
- [CF - QQQ follow-ups: alpha-vs-QQQ column + QQQ row highlight; 07-01 cohort QQQ re-seeded to its real 07-06 start](#appendix-cf---qqq-follow-ups-alpha-vs-qqq-column--qqq-row-highlight-in-the-cohort-tables-and-the-07-01-cohort-qqq-control-re-seeded-to-its-real-07-06-start-2026-07-17-1445-local) (07-17)
- [CG - Full audit (4 Opus workers): 16 findings all fixed - collision hardening, dashboard loopback + 37x, monthly dispatcher](#appendix-cg---full-system-audit-4-parallel-opus-workers--automated-pass-16-findings-all-fixed-same-session---collision-hardening-dashboard-loopback--37x-speedup-monthly-single-process-dispatcher-2026-07-17-1555-local) (07-17)
- [CH - 2nd full audit (5 Opus workers): 2 CRITs - biweekly ladder never live-rebalanced; price_cache never back-adjusts splits ($83k phantom)](#appendix-ch---second-full-system-audit-5-parallel-opus-workers-2-criticals-found---the-biweekly-ladder-had-never-live-rebalanced-and-price_cache-never-back-adjusts-splits-83k-phantom-loss-across-48-sleeves-2026-07-28-1537-cdt) (07-28)
- [CI - 2 trading days of prices lost to a yfinance rate limit; CH's refresh fix had a hole (empty frame != exception), now closed](#appendix-ci---two-trading-days-of-prices-silently-lost-to-a-yfinance-rate-limit-the-ch-refresh-fix-had-a-hole-empty-frame--exception-now-closed-biweekly-ladder-catch-up-confirmed-fired-2026-08-02-1615-cdt) (08-02)
- [CJ - KLAC split back-adjustment APPLIED: cache root cause fixed, 15 open positions re-based, frozen d=0.0000pp; 31 closed rows deferred](#appendix-cj---klac-split-back-adjustment-applied-price_cache-root-cause-fixed-15-open-positions-re-based-frozen-tests-unmoved-at-d00000pp-the-31-closed-rows--5534370-deferred---compute_nav-has-no-historical-mode-2026-08-02-1653-cdt) (08-02)
- [CK - PRD M7.1 shipped (76/76 exact); M7.2 gate FAILED 94.48% - the ledger replays exactly but historical NAV is NOT reproducible (price_cache is mutable by design)](#appendix-ck---prd-m71-shipped-historical_statepy-7676-exact-m72-gate-failed-at-9448---the-cash-ledger-replays-exactly-but-historical-nav-is-not-reproducible-because-price_cache-is-deliberately-mutable-stop-per-the-prd-recommend-m73-only-2026-08-02-1723-cdt) (08-02)
- [CL - PRD M7.3 PASSED on a copy: 31 closed KLAC rows repair cleanly, cash reconciles $0.00 on 76/76, ladder spreads compress 1.4-2.8pp with no leader change; live apply BLOCKED-ON-EVAN](#appendix-cl---prd-m73-passed-on-a-copy-the-31-closed-klac-rows-repair-cleanly-cash-reconciles-at-000-on-7676-sleeves-ladder-spreads-compress-14-28pp-but-no-leader-changes-live-apply-blocked-on-evan-separately-verify_run-went-fail-5576-tonight-from-the-ci-backfill-2026-08-02-1750-cdt) (08-02)
- [CM - **M7 CLOSED**: KLAC repair applied LIVE, verify_run PASS 76/76, frozen d=0.0000pp; the 07-31 re-mark also cured the CI staleness; ladder spreads 7.58/12.93/4.93pp, no leader change](#appendix-cm---m7-closed-klac-repair-applied-live-by-evan-verify_run-pass-7676-frozen-d-00000pp-the-2026-07-31-nav-re-mark-also-cured-the-ci-rate-limit-staleness-ladder-spreads-compress-to-7581293493pp-with-no-leader-change-2026-08-02-2002-cdt) (08-02)
- [CN - The August rebalance would have been SKIPPED: live cron had drifted to day-1-of-month and 08-01 was a Saturday; restored to daily self-gating. `\llm rebal` jiggler decoded, `hellohello` confirmed real](#appendix-cn---the-august-monthly-rebalance-would-have-been-skipped-the-live-cron-had-drifted-to-day-1-of-month-and-2026-08-01-was-a-saturday-restored-to-daily-self-gating-the-undocumented-llm-rebal-jiggler-decoded-and-hellohello-confirmed-real-2026-08-02-2256-cdt) (08-02)
- [CO - verify_run gains check (e) rebalance cadence: a stale `rebalance_log.md` now FAILs loudly instead of passing silently; closes the blind spot CN found](#appendix-co---verify_run-gains-check-e-rebalance-cadence-a-stale-rebalance_logmd-now-fails-loudly-instead-of-passing-silently-closes-the-blind-spot-cn-found-2026-08-02-2337-cdt) (08-02)
- [CP - August monthly rebalance EXECUTED: 12 LLM overlay and cascade decisions logged, all sleeves rebalanced, verify_run PASS 76/76, Alpaca paper 132 orders 0 rejects; first live monthly fire since the CN cron-drift fix](#appendix-cp---august-monthly-rebalance-executed-12-llm-overlay-and-cascade-decisions-logged-all-sleeves-rebalanced-verify_run-pass-7676-alpaca-paper-132-orders-0-rejects-first-live-monthly-fire-since-the-cn-cron-drift-fix-2026-08-03-1825-cdt) (08-03)
- [CQ - Third full audit (cold subagent): the rebalance failure-visibility chain fixed (a failed rebalance stamped success and blocked its own retry, defeating CO's check (e)) + 8 more; 15 findings deferred](#appendix-cq---third-full-audit-cold-subagent-the-rebalance-failure-visibility-chain-fixed-plus-8-more-findings-15-findings-deferred-to-a-fresh-session-2026-08-05-1950-cdt) (08-05)
- [CR - The 15 deferred CQ.7 findings closed: cascade sleeves unstopped BY DESIGN (Evan's call; the audit's own example was the wrong position - XLU, not STX), buy/sell made genuinely atomic, M6 ungated, carry-forward staleness surfaced, backups validated before rotation, 6 doc-drift fixes](#appendix-cr---the-15-deferred-cq7-findings-closed-the-cascade-sleeves-are-unstopped-by-design-evans-call-and-the-audits-own-example-was-the-wrong-one-buysell-made-genuinely-atomic-m6-ungated-carry-forward-staleness-surfaced-backups-validated-before-rotation-plus-six-doc-drift-corrections-2026-08-05-2105-cdt) (08-05)
- [CS - PRD M6.1 SHIPPED: 231/231 mirrored orders reconcile filled; Alpaca's `submitted_at` is a queue-release time, and the August batch was HELD TO THE NEXT SESSION OPEN so M6.2 must not call it slippage](#appendix-cs---prd-m61-shipped-all-231-mirrored-orders-reconcile-231231-filled-and-the-august-batch-turns-out-to-have-been-held-to-the-next-session-open---so-m62-must-not-call-it-slippage-2026-08-05-2152-cdt) (08-05)
- [CT - PRD M6.2 pairing built and RUN, then STOPPED before writing slippage_log: the measured ~+100bps is intraday/overnight DRIFT, not slippage, and M6.3 run off it would have moved HALF_SPREAD_BPS 5 -> 100bps and corrupted every backtest](#appendix-ct---prd-m62-pairing-built-and-run-then-stopped-before-writing-slippage_log-the-measured-100bps-is-intradayovernight-drift-not-execution-slippage-and-m63-run-off-it-would-have-recalibrated-half_spread_bps-5bps---100bps-and-corrupted-every-backtest-2026-08-05-2225-cdt) (08-05)
- [CU - CT.5 step 1 done: sim fill basis PINNED exactly (close x 1+/-5bps, 34/34 and 33/35 on a 2-day-old batch); the July reference prices are GONE - price_cache was rewritten under them, so M6 has ZERO clean measurement windows](#appendix-cu---ct5-step-1-done-the-sims-fill-basis-is-pinned-exactly-close-x-1-5bps-proven-3434-and-3335-on-a-2-day-old-batch-and-the-july-reference-prices-are-gone---price_cache-was-rewritten-under-them-m6-currently-has-zero-clean-measurement-windows-2026-08-05-2312-cdt) (08-05)
- [CV - CU's forward fix SHIPPED and APPLIED LIVE: every fill now records the raw close it came from, so a rebalance stays measurable after price_cache moves under it (verify_run PASS 76/76, quick_check ok)](#appendix-cv---cus-forward-fix-shipped-and-applied-live-every-fill-now-records-the-raw-close-it-came-from-so-a-rebalance-stays-measurable-after-price_cache-moves-under-it-2026-08-05-2334-cdt) (08-05)
- [CW - Residual-ladder inversion DECOMPOSED: not cadence/turnover/cost/R1/one-name - the WHOLE gradient is in the 05-01 selection, is market-orthogonal, and is ONE MONTH (July: SPY +0.03% while momentum did -23.5%)](#appendix-cw---the-residual-ladder-inversion-decomposed-it-is-not-cadence-not-turnover-not-transaction-cost-not-r1-not-one-bad-name---the-entire-gradient-is-in-the-2026-05-01-stock-selection-it-is-market-orthogonal-and-it-is-one-month-july-when-spy-did-003-and-momentum-did--235-2026-08-07-0541-cdt) (08-07)
- [CX - Dependency CVE status DETERMINED with no new dependency (stdlib OSV, canary-verified): 8 packages / 74 advisories, none reachable; gitpython upgraded to close 18 RCE advisories; the dead-weight claim was a FALSE NEGATIVE and hellohello is INTENTIONAL - do not delete it](#appendix-cx---dependency-cve-status-determined-without-adding-a-dependency-stdlib-osv-canary-verified-gitpython-upgraded-to-close-18-rce-advisories-and-two-record-corrections---the-dead-weight-claim-was-a-false-negative-and-hellohello-is-intentional-2026-08-11-2248-cdt) (08-11)
- [CY - PRD M6 REDEFINED to implementation shortfall (Evan's call): drift is now MEASURED three ways (sd 192/499bps, 28% of fills BETTER than the sim, corr +0.7668 with each name's own overnight move) instead of asserted, so HALF_SPREAD_BPS stays 5.0; the true spread is UNMEASURED, not 100. Plus an unpaired-reason that was true 64/65](#appendix-cy---prd-m6-redefined-to-implementation-shortfall-evans-call-the-100bps-is-measured-to-be-drift-three-independent-ways-rather-than-asserted-so-half_spread_bps-stays-at-50---plus-a-canned-unpaired-reason-that-was-true-64-times-out-of-65-2026-08-11-2325-cdt) (08-11)
- [CZ - CQ.2 finding 2 CLOSED: the mandated frozen tests no longer write the live DB. Fixed at the NAME-RESOLUTION layer (TEMP tables shadow positions/portfolio_state) so price_cache still reads from main; proven by PRAGMA data_version unmoved, with a negative control showing the check can see a write. 137 residue rows REPORTED, not deleted](#appendix-cz---cq2-finding-2-closed-the-mandated-frozen-tests-no-longer-write-the-live-db-fixed-at-the-name-resolution-layer-temp-tables-shadow-positionsportfolio_state-not-by-redirecting-the-connection---which-would-have-taken-price_cache-with-it-2026-08-12-0720-cdt) (08-12)
- [DA - Cold audit, first full sweep since CQ: 15 findings + 8 edge cases; the two daily.bat handlers that never reached the exit gate are fixed, the crit is not (2026-08-12, ~17:25 CDT)](#appendix-da---cold-audit-first-full-sweep-since-cq-15-findings--8-edge-cases-the-two-dailybat-handlers-that-never-reached-the-exit-gate-are-fixed-the-crit-is-not-2026-08-12-1725-cdt) (08-12)
- [DB - verify_run crit CONFIRMED BY PREDICTION: FAIL 56/76 evening -> PASS 76/76 next morning with nothing repaired, 13 sleeves silently recovered; plus two CZ.5 factual corrections and one wrong call of my own](#appendix-db---the-verify_run-crit-confirmed-by-prediction-fail-5676-on-08-12-evening-pass-7676-on-08-13-morning-with-nothing-repaired-and-13-sleeves-silently-recovered-plus-two-cz5-factual-corrections-and-one-wrong-call-of-my-own-caught-before-it-reached-this-file-2026-08-13-1522-cdt) (08-13)
- [DC - The verify_run alarm is INVERTED: there are NO bad 08-10 rows; check (b) measures nightly price_cache revision, not the ledger; the 846 per-date cash divergences are the M7.3 KLAC repair to the cent (30/30). Task 1's canary premise falsified, Task 2 answered by the same mechanism](#appendix-dc---the-verify_run-alarm-is-inverted-there-are-no-bad-08-10-rows-check-b-measures-nightly-price_cache-revision-rather-than-the-ledger-and-the-846-per-date-cash-divergences-are-the-m73-klac-repair-to-the-cent-3030-task-1s-canary-premise-is-falsified-task-2-answered-by-the-same-mechanism-2026-08-13-2150-cdt) (08-13)
- [DD - **DA crit CLOSED**: check (b) split into (b1) per-date ledger cash (hard FAIL, via the existing replayer) and (b2) price drift (INFO); canaried by fault injection - a corrupted OLDER row FAILs while its newest row stays clean at drift($+0.00), which is exactly what navs[-1] could not see](#appendix-dd---the-da-crit-is-closed-verify_run-check-b-split-into-b1-per-date-ledger-cash-as-the-hard-fail-and-b2-price-drift-as-info-canaried-by-fault-injection-on-a-copy---a-corrupted-older-row-now-fails-while-the-newest-row-stays-clean-which-is-exactly-what-the-old-navs-1-check-could-not-see-2026-08-13-2159-cdt) (08-13)
- [DE - Scheduled daily-audit (2026-08-16): morning_refresh.bat gets DA's fix, `check_cache_gaps` wired into daily.bat, task table re-synced, DD's work committed](#appendix-de---scheduled-daily-audit-das-morning_refreshbatcache_gap-gaps-closed-handoffs-scheduled-task-table-re-synced-dds-own-work-committed-2026-08-16-1321-cdt) (08-16)
- [DF - Correction to DE.1: `e96c5fe` (record DA), not `e5366fd`, was the last non-daily-report commit](#appendix-df---correction-to-de1-the-wrong-commit-was-cited-as-last-non-daily-report-2026-08-16-1338-cdt) (08-16)
- [DG - Landing-check on DE: its day-1 cache-gap gate was a cmd.exe NO-OP (ran daily 08-16..08-18) and its "re-synced" task table missed `daily-trade-check-2` drifted back to `0 17` - both fixed. DA finding 4 CLOSED: the 3 lost LLM decisions were destroyed by INSERT OR REPLACE, not by hand; writers now plain INSERT + append-only triggers, canaried 15/15](#appendix-dg---landing-check-on-de-found-two-of-its-fixes-did-not-hold-the-day-1-cache-gap-gate-was-a-cmdexe-no-op-ran-daily-08-1608-18-and-the-re-synced-task-table-missed-a-cron-that-had-drifted-back-into-the-mtm-window-both-fixed-plus-da-finding-4-closed-the-three-lost-llm-decisions-were-destroyed-by-insert-or-replace-not-by-hand---writers-are-plain-insert-now-and-the-tables-are-append-only-at-the-db-layer-canaried-1515-2026-08-19-0005-cdt) (08-19)
- [DH - Landing-check on DG's own commit: SAFE, 3 corrections - DG.4 verified the DORMANT decision path; the LIVE `*_ops decide` path had no guard and would have traced out on 09-01, now refuses cleanly rc=2; one HANDOFF line; one diff count](#appendix-dh---landing-check-on-dg-its-own-commit-ebc059f-safe-three-corrections---dg4-verified-the-dormant-decision-path-the-live-one-had-no-guard-and-would-have-traced-out-of-the-unattended-603pm-task-on-09-01-now-refuses-cleanly-rc2-one-handoff-line-dg3-missed-one-wrong-diff-count-2026-08-19-0020-cdt) (08-19)
- [DI - Scheduled daily-audit (2026-08-19): `rebalance.bat`'s 15 `if errorlevel 1` gates were blind to negative crash codes -- a crashed `alpaca_sync --execute` stamped OK and exited 0; the daily-firing "monthly" rebalance gets a mechanical month gate; the daily-report auto-push (which had already published two unreviewed commits that morning) removed](#appendix-di---scheduled-daily-audit-the-15-exit-code-gates-on-the-one-script-that-trades-were-deaf-to-crash-codes-and-the-monthly-rebalance-was-gated-only-by-prose-an-llm-reads-2026-08-19-1645-cdt) (08-19)
- [DJ - Audit of `daily-trade-check-2`: its prohibitions (READ-ONLY, never `git add -A`, never push, never rebalance) had ZERO mechanical enforcement -- the deny list was 2 `Read(./.env*)` rules against a PUBLIC remote. Deny rules added to both settings files; the 4 live task specs (in no git repo) snapshotted to `docs/scheduled-tasks/` with a daily drift diff; `/landing-check` moved BEFORE the commit; 2026-08-17's missing post-close session found by the new check](#appendix-dj---audit-of-the-daily-trade-check-2-scheduled-task-spec-every-prohibition-in-the-file-that-authorizes-an-unattended-agent-to-write-this-repo-was-prose-with-zero-enforcement-and-the-one-time-it-was-tested-it-failed-deny-rules-added-specs-snapshotted-into-the-repo-landing-check-moved-before-the-commit-2026-08-20-2330-cdt) (08-20)

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


# Appendix BF - M3.1 pre-inception NAV guard in paper_mtm.py + fixture regression test (2026-07-09, ~13:50 local)

**PRD milestone M3, task 1 — first write-path change of the plan.** Make it impossible for the daily
MTM to write a NAV row dated before a sleeve's inception (the holiday-weekend $100k-pollution class,
Appendices AU/AV, that previously needed manual row deletion).

**WHAT.** Added `inception_date(strategy)` to `scripts/momentum/paper_mtm.py` and a guard in `main()`
(after the weekend skip, before `compute_nav`): if `as_of < inception_date(strategy)`, log
`SKIP pre-inception` and write nothing.

**WHY this inception formula** — `inception = min( date(paper_portfolio.initialized_at),
earliest paper_positions.entry_date )`. Verified empirically against all 17 sleeves that **neither
source alone is correct**:

- `initialized_at` is a wall-clock stamp that runs LATER than the true start for the **backdated**
  May sleeves (e.g. `mom_roa_6535_paper` re-inited 2026-06-13 but its NAV/entry history goes back to
  2026-05-01).
- earliest `entry_date` runs later than inception for the **07-06 cohort**, whose positions fill at
  the NEXT open 2026-07-07 while inception / first NAV is 2026-07-06.

Their `min` is right for every current sleeve and errs EARLY, so the guard can only skip genuinely
pre-inception dates — never a legitimate one. Defensive: on any parse failure `inception_date`
returns `date.min`, so a malformed row can never make tonight's live MTM wrongly skip a live sleeve.
For today's MTM (`as_of=2026-07-09`) every sleeve's inception is <= 2026-07-07, so the guard never
fires and behavior is byte-identical to before.

**HOW / verification.**

- New committed regression test `scripts/momentum/test_inception_guard.py` (fixture DB, no live DB /
  no price_cache needed — write cases use a cash-only sleeve). All 6 checks pass:

```
  [OK  ] backdated inception = 2026-05-01
  [OK  ] cohort inception = 2026-07-06, not first-fill 07-07
  [OK  ] cash-only inception = 2026-07-06
  [OK  ] MTM 2026-07-03 (pre-inception) writes NO nav row
  [OK  ] MTM 2026-07-06 (inception day) writes a nav row
  [OK  ] MTM 2026-07-09 (live date) writes a nav row
```

- **Copy test on real data** (PRD "test on a DB copy, never live-first"): `VACUUM INTO` snapshot of
  the live 5 GB DB (4.76 GB, consistent), ran the REAL `paper_mtm` against it. A fake
  `GUARD_TEST_FUTURE` sleeve (inception 2099-01-01) was SKIPPED for 2026-07-09 with no row; the live
  `mom_v1_paper` (173 positions, inception 2026-05-01) wrote its 2026-07-09 NAV row normally — guard
  does not interfere. Snapshot deleted after. The live DB was never written.

Frozen tests (paper_mtm.py changed):

```
  [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
  [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
  [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
  [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
  All regression tests passed.
```

d=±0.0000pp (4/4). The change runs live in tonight's `TradingDailyMTM` 5:15pm task; the guard never
fires for live sleeves at today's date, so that run is a no-op for behavior. M3.1 done; next open
task is M3.2 (post-run verifier, `verify_run.py`).


# Appendix BG - M3.2 post-run verifier (verify_run.py) (2026-07-09, ~14:05 local)

**PRD milestone M3, task 2.** A read-only self-check so an unattended daily/monthly run can't quietly
leave the books inconsistent.

**WHAT.** New `scripts/momentum/verify_run.py` (read-only, `file:...?mode=ro`). Per sleeve:
(a) **NAV continuity** — one `paper_nav` row for every trading day since inception, no gaps (dupes
are impossible, `paper_nav` PK is `(strategy, nav_date)`); intentional holiday flat rows are counted
and reported, not failed; (b) **cash reconciliation** — recompute `cash + Sum(qty x close@nav_date)`
the same way `paper_mtm` does (carry-forward last close, entry_price if none) and compare to the
stored `total_nav` within `$0.05`; (c) **position count vs target** — MONTHLY only, targets hardcoded
from HANDOFF's 2026-07-09 cohort spec, FAIL only if count EXCEEDS target (overlay/cascade sleeves are
variable veto->cash and reported, not asserted); (d) **no pre-inception rows**. `--mode daily` runs
a/b/d; `--mode monthly` adds c + an Alpaca submit/reject reminder line. Dated PASS/FAIL block appended
to a `verify_report.log` **co-located with the DB** (`--db` copy -> next to the copy, so test runs
never pollute the live ops log); nonzero exit on any FAIL. `--db` flag added up front (sanctioned by
M5.3).

**HOW / verification (done-check).**

- `--mode daily` against the LIVE DB (read-only): **RESULT: PASS (17/17 sleeves OK)**. Cash recon
  delta `$0.00` on every sleeve; continuity clean (46/46 trading days +2 holiday flat rows for the
  May family; 3/3 for the 07-06 cohort); position counts sane (`residual_roa_6535_0701` 48/50 = the
  2 untradable; `llm_overlay_mom_roa_top1` 0/var and `llm_overlay_sector_top4` 3/var = veto->cash).
- `--mode monthly` against live: also PASS 17/17 + the reminder line prints.
- **Broken-copy FAIL test**: `VACUUM INTO` snapshot, deleted one `mom_v1_paper` nav row (2026-06-01),
  ran `--db copy --mode daily` -> `[FAIL] mom_v1_paper ... continuity: 1 missing trading day
  (2026-06-01)`, `RESULT: FAIL (16/17)`, exit 1. Copy deleted; live DB untouched.

Frozen tests (new Python file; read-only, no strategy code touched):

```
  [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
  [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
  [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
  [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
  All regression tests passed.
```

d=±0.0000pp (4/4). M3.2 done. `verify_run` is not yet wired into the batch flow — that is M3.3
(daily.bat `--mode daily` after MTM; monthly_auto.bat `--mode monthly`).


# Appendix BH - First live coverage-gate catch: 07-09 MTM skipped, backfill deferred (2026-07-09, ~22:35 local)

**Operational event, not a code change** — the first production fire of the M2.2 coverage gate, on
the day it was deployed (2026-07-09, gate wired ~13:30). Recorded because it is the first time an
automated guardrail changed the run's outcome, and it leaves a real open item.

**What happened (all from `var/last_daily_run.log` + read-only DB queries; nothing fabricated).**

- The 17:15 `TradingDailyMTM` task ran `daily.bat`. The price refresh produced only **4,381** closes
  for 2026-07-09 (baseline median ~5,245). At 17:17 `check_coverage` FAILED (`4381 < 5000` floor),
  the gate did `exit /b 1`, and **all MTM + overlay ops were skipped**. The task exited nonzero.
  **No `paper_nav` row exists for 2026-07-09.** This is exactly the designed behavior — the gate
  refused to mark the books on incomplete data.
- **This is transient late-publication, not a data bug or systematic drop.** Proof: 2026-07-08 was
  itself incomplete at **4,379** closes when first checked ~13:20 today, and by this evening had
  **settled to 5,207**. `daily_price_refresh` fetches a ~30-day *range* (its docstring: "tolerant of
  missed days"), so late-arriving tickers self-heal on later runs; the same-day MTM is what catches
  the universe mid-publication.

**Backfill attempt (2026-07-09 ~22:30) — DEFERRED, correctly.** Evan authorized a coverage-gated
07-09 backfill. Re-ran `daily_price_refresh` (raised 07-09 from 4,381 to **4,724**), re-ran
`check_coverage --date 2026-07-09` → **still FAIL (4,724 < 5,000)**. Per the standing order and the
gate's own policy, **no MTM was written** — 07-09 has not finished publishing even at 22:31.
`paper_mtm` was NOT run. The 07-09 NAV gap therefore remains and `verify_run --mode daily` flags it
(17/17 sleeves, "1 missing trading day 2026-07-09"). The backfill will complete once 07-09 clears
the floor (07-08 shows full settling happens within a day).

**Guardrail chain worked end-to-end on its first live incident:** M2.2 caught the shortfall and
skipped the mark; M3.2 `verify_run` flags the resulting gap; M3.1's inception guard will protect the
eventual backfill MTM.

**Root cause + open items for Evan (REPORT ONLY — no schedule/strategy change made):**

1. **Root cause is timing.** The 17:15 MTM runs before yfinance finishes same-day universe
   publication. It will recur on any slow-publication day, leaving a one-day gap each time.
2. **Backfill 07-09** once `check_coverage --date 2026-07-09` passes (likely tomorrow): `paper_mtm
   --as-of 2026-07-09` per sleeve (idempotent REPLACE; inception guard protects it), then
   `verify_run --mode daily` should return PASS.
3. **Deeper fix, Evan's decision** (out of M3 guardrail scope): (A) move `TradingDailyMTM` later
   (~8-9pm ET) so same-day data is complete — simplest; or (B) add a self-healing catch-up step that
   re-MTMs the prior 1-2 trading days once their coverage passes. Not implemented pending Evan's call.

No commit of code for this entry; the refresh only updated `var/trades.db` price data (gitignored).


# Appendix BI - M3.3+M3.4 verifier wired into daily/monthly bats + ops-status stamp; M3 complete (2026-07-09, ~22:45 local)

**PRD milestone M3, tasks 3 + 4 — completes M3 (unattended-automation safety).** Done together
because both live in the `daily.bat` tail and M3.4's stamp consumes M3.3's verify result.

**M3.3 — wire the verifier.**
- `daily.bat`: after the graphify step (i.e. after MTM/anomaly), run `verify_run --mode daily`; on
  FAIL, write a FAIL ops stamp, echo a `VERIFY FAIL` line, and `exit /b 1` (loud + nonzero task exit
  per the PRD). On pass, fall through to a PASS stamp.
- `monthly_auto.bat`: after `call rebalance.bat`, run `verify_run --mode monthly`; FAIL -> echo +
  `exit /b 1`.
- Both files re-confirmed **pure ASCII**; the `^(daily^)` / `^(monthly^)` parens are escaped inside
  the echo/if context.

**M3.4 — surface failures for Evan. DEVIATION (sanctioned by the PRD): stamp goes to
`var/ops_status.log`, not `daily_report.md`.** Verified `daily_report.md` is Evan's hand-written
journal — only `render_daily_report_html.py` reads it, nothing writes it — so appending to it would
collide with his entries. The PRD's stated fallback is exactly this. New tiny helper
`scripts/momentum/ops_stamp.py` writes one newest-last dated line
(`[OPS <date>] coverage=<PASS/FAIL> verify=<PASS/FAIL/n/a> [- note]`); used a helper rather than
raw `echo` to avoid fragile cmd.exe date/variable/paren handling (a repeatedly-bitten hazard here,
Appendix AS). Stamps are written on the coverage-FAIL early-exit path (`coverage=FAIL, MTM skipped`)
and both daily verify branches.

**HOW / verification.**
- Both bats pure ASCII (byte scan).
- `ops_stamp.py`: PASS, FAIL, and coverage-FAIL invocations each append the correct dated line to
  `var/ops_status.log` (synthetic test lines then cleared so real runs seed it).
- Tail control flow tested with exit-code stubs: verify exit 0 -> PASS stamp + `Done` + batch exit 0;
  verify exit 1 -> FAIL stamp + `VERIFY FAIL` line + batch exit 1. Both branches correct.
- Did NOT run the full production `daily.bat` (trade-capable overlay ops; and 07-09 is mid-publication
  per Appendix BH). The isolated stub exercises the identical control flow.

**Known interaction (intended, flagged so it is not a surprise):** `verify_run --mode daily` will
FAIL — and therefore the daily task will exit nonzero — every run until the **2026-07-09 NAV gap
(Appendix BH) is backfilled**, because the gap is a real missing trading day the verifier is designed
to flag. This is the guardrail loudly surfacing an unresolved open item, not a false alarm; it clears
the moment 07-09 is backfilled.

Frozen tests (new Python file `ops_stamp.py`):

```
  [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
  [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
  [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
  [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
  All regression tests passed.
```

d=±0.0000pp (4/4). **M3 (unattended-automation safety) complete**: pre-inception guard (BF),
post-run verifier (BG), verifier wired into both bats (this entry), failures surfaced to
`var/ops_status.log` (this entry). Deadline milestones M2 + M3 are both in place before the
2026-08-01 unattended rebalance. Remaining PRD work: M4 (experiment-integrity reporting), M5 (backup
hygiene), M6 (slippage — gated on August fills). Open ops item carried forward: backfill the 07-09
NAV gap once coverage clears (Appendix BH).


# Appendix BJ - M4.1 experiment kill-switch tracker (experiment_report.py) (2026-07-09, ~23:15 local)

**PRD milestone M4, task 1** (experiment-integrity reporting). First M4 task; read-only.

**WHAT.** New `scripts/momentum/experiment_report.py` (read-only). Per LLM-overlay experiment
(stock -> `llm_overlay_log`; sector -> `sector_overlay_log`, each shared by control/cash-veto/cascade
sleeves): decisions to date with scores + verdicts, **pick count vs the >=30 kill threshold**,
**months elapsed vs the 12-month clock** (from the FIRST logged decision, not the 2026-07-01 cohort
P&L reset — the reset restarted NAVs but kept the decision history), and a **score-vs-forward-return
table** (decision-date close -> latest cached close, labelled UNREALIZED/INTERIM, no annualization or
stats — an honest eyeball only). Console + `--md` -> `docs/experiment_report_<date>.md`.

**HOW / verification (done-check).** Runs clean; the decision figures come straight from the same two
tables the dashboard's LLM panel reads (8 stock decisions / 5 dates; 15 sector / 3 dates), so they
are consistent with the dashboard by construction (a live cross-check belongs with the M4.3 dashboard
hook). `--md` wrote `docs/experiment_report_2026-07-09.md`. Honest interim picture on today's data:

- **stock**: 8 decisions, 1.3 months in. VETO names avg **-9.5%** (BE -9.8%, AAOI -27.7% — vetoes
  dodged real drops), BUY names avg **-9.4%** (WDC +8.6% good, but FN -33.4% dragged it). n=3/5 —
  noise, not proof.
- **sector**: 15 decisions, 0.9 months in. HOLD **-0.3%** vs VETO **-0.4%** — essentially no signal
  yet, matching the honest prior that a macro overlay is the weakest LLM edge.

Frozen tests (new Python file, read-only):

```
  [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
  [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
  [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
  [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
  All regression tests passed.
```

d=±0.0000pp (4/4). M4.1 done; next open task is M4.2 (extend with control-vs-treatment NAV
divergence for all three pairs).

**Context note (unchanged):** the 07-09 NAV backfill (Appendix BH) is still data-gated — 07-09 was
4,724 closes at 23:07, below the 5,000 floor; it will backfill once it settles. The M3.5 catch-up/
schedule fix remains a flagged decision for Evan; this M4 work is the ratified PRD continuation and
does not depend on it.


# Appendix BK - M4.2 control-vs-treatment NAV divergence in experiment_report.py (2026-07-09, ~23:25 local)

**PRD milestone M4, task 2.** Extended `experiment_report.py` with control-vs-treatment NAV
divergence for all three pairs (each experiment's control vs its cash-veto and cascade treatments),
from `paper_nav` READ-ONLY. All six sleeves share the 2026-07-06 cohort inception and a \$100k start,
so %-from-inception is directly comparable; the report shows each sleeve's %-from-inception and the
gap vs its control in \$ and pp.

**HOW / verification (done-check: output matches the dashboard's NAV numbers).** The report's NAVs
are read straight from `paper_nav.total_nav` (same source the dashboard uses); spot-checked against a
direct query and they match to the cent (e.g. control `mom_roa_top1_paper` \$96,346.83 -> report
\$96,347). Latest common mark is 2026-07-08 (2026-07-09 was gate-skipped, Appendix BH). Honest
interim divergence (tiny n, forward OOS only):

- **stock**: control `mom_roa_top1_paper` **-3.65%** (holds BE, which fell); cash-veto **+0.00%**
  (vetoed BE to cash, dodging the drop; **+3.65pp** vs control); cascade **+4.25%** (walked to WDC;
  **+7.90pp** vs control). Both stock treatments ahead so far — the veto/cascade avoided BE's decline.
- **sector**: control `sector_top4_paper` **+0.22%**; cash-veto **-0.50%** (**-0.73pp**); cascade
  **-0.88%** (**-1.10pp**). Both sector treatments slightly behind control — consistent with the
  standing prior that the macro overlay is the weakest LLM edge.

Frozen tests (Python changed):

```
  [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
  [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
  [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
  [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
  All regression tests passed.
```

d=±0.0000pp (4/4). M4.2 done; next open task is M4.3 (small dashboard hook — surface the n/30-picks
and months/12 kill-switch counters in the LLM panel if not already shown), which completes M4.


# Appendix BL - M4.3 kill-switch counters in the dashboard LLM panel; M4 complete (2026-07-09, ~23:35 local)

**PRD milestone M4, task 3 — completes M4.** Surface the kill-switch counters in the dashboard so the
n/30-picks and months/12 clocks are visible without running the CLI report.

**WHAT.** `trading_bot/dashboard/web.py`, LLM-experiments panel (the `##### LLM experiments` block,
~line 2087). Added one `st.caption` per experiment showing `kill-switch: <n>/30 picks · <months>/12
months (since <first-decision>)`, read from the same `llm_overlay_log` / `sector_overlay_log` tables
the panel already queries. Matches the existing panel convention exactly (same local sqlite
connection, same `st.caption`, the `·` middot already used two lines above). Surgical — nothing else
on the page changed.

**HOW / verification.**
- `web.py` compiles (`py_compile`).
- The exact panel snippets (COUNT + MIN(decision_date), then the month math) run against the live DB
  and produce the intended captions: **stock `8/30 picks · 1.3/12 months (since 2026-05-29)`**,
  **sector `15/30 picks · 0.9/12 months (since 2026-06-12)`** — matching the M4.1 report.
- **Live browser render NOT performed:** the Chrome extension is not connected in this session, so I
  could not load http://localhost:8501 to eyeball it (honest gap, not a code issue). The running
  dashboard (`TradingDashboard`, up since 12:09) will render the new captions on its next rerun; the
  change is inside an already-working `if`-block and only adds validated `st.caption` calls, so the
  render risk is minimal. Flagging so Evan can glance at the panel when convenient.

Frozen tests (dashboard Python changed; unrelated to strategies but run per the standing order):

```
  [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
  [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
  [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
  [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
  All regression tests passed.
```

d=±0.0000pp (4/4). **M4 (experiment-integrity reporting) complete**: kill-switch tracker (BJ),
control-vs-treatment divergence (BK), dashboard counters (this entry). Remaining PRD: M5 (backup
hygiene), M6 (slippage — gated on August fills). Open ops item still carried: backfill the 07-09 NAV
gap once coverage clears (Appendix BH); M3.5 catch-up/schedule fix remains Evan's decision.


# Appendix BM - M5 backup hygiene: rotating VACUUM-INTO backups + weekly task + restore drill (2026-07-09, ~23:30 local)

**PRD milestone M5 (backup hygiene) — all three tasks, done together (small + coupled).** Before
this the only backup was the frozen founding copy `var/trades.db.bak_pre_spike_cleanup`; now there
are rotating snapshots and a proven restore path.

**M5.1 — rotating backup script `scripts/backup_trades_db.py`.** SQLite `VACUUM INTO` (a bare copy of
a live WAL DB can catch a torn write) to `var/backups/trades_YYYY-MM-DD.db`; keeps the newest `--keep`
(default 3), deletes older; aborts if free disk < 2x DB size; never touches the frozen founding
backup (guarded + not in the glob). Verified: real run wrote a **4.76 GB** backup in ~59s; opened
read-only and **every row count matches live** (paper_nav 321, paper_positions 704, price_cache
37,463,451, paper_portfolio 17, both decision logs). Rotation deletion path dry-run with 4 seeded
backups + `--keep 3` correctly planned to delete only the oldest.

**M5.2 — weekly scheduled task `TradingWeeklyBackup`.** `cmd.exe /c ...python -m
scripts.backup_trades_db > var\backup.log 2>&1`, WorkingDirectory the repo root, trigger **Sundays
09:00** (far from the 17:15 MTM window). Registered via PowerShell `Register-ScheduledTask`. Verified:
`Get-ScheduledTask` shows it Ready; one manual `Start-ScheduledTask` completed with **LastTaskResult
0x0** and wrote the run to `var/backup.log`.

**M5.3 — restore drill.** Copied the newest backup to a scratch path (**4.76 GB in 3.2s**), opened it,
ran `verify_run --mode daily --db <scratch>` (**3.8s**). verify_run executed cleanly against the
restored DB and reproduced live's exact state — RESULT: FAIL (0/17) on the **known 2026-07-09 NAV gap**
(Appendix BH), which is the expected result and confirms the restore is FAITHFUL (it reproduces live
including the open gap). Scratch copy removed; live DB never touched.

Frozen tests (new Python file `backup_trades_db.py`):

```
  [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
  [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
  [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
  [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
  All regression tests passed.
```

d=±0.0000pp (4/4). **M5 complete.** Only `backup_trades_db.py` is committed; the backups
(`var/backups/`, gitignored) and the `TradingWeeklyBackup` task are local system state. Remaining PRD:
**M6 (slippage) is GATED on the 2026-08-01+ Alpaca fills** — cannot start until those exist, so this
is the end of the currently-actionable roadmap. Open items unchanged: backfill the 07-09 NAV gap once
coverage clears (BH); the M3.5 catch-up/schedule fix is a pending Evan decision.


# Appendix BN - M3.5 catch-up marking: self-healing daily MTM (option A, Evan-authorized) (2026-07-09, ~23:55 local)

**PRD amendment M3.5 (option A), authorized by Evan 2026-07-09.** Fixes the structural consequence of
the M2.2 coverage gate: same-day yfinance data is incomplete at the 17:15 run, so the gate skipped all
marking and left a NAV gap that would COMPOUND daily (07-09 unmarked, 07-10 next, ...) and fail the
daily task every evening. Catch-up marking closes the loop: mark each day from SETTLED data, when the
data is real, automatically.

**Four pieces (all tested; write-path developed against a DB copy first per the standing rule).**

1. **`check_coverage.py` refactor** — extracted `coverage_status(conn, date)` so the daily gate AND
   catch-up use IDENTICAL floor logic (`max(5000, 90%*10-day median)`); if they diverged a day could
   pass one and fail the other. Behavior-preserving: `--date 2026-07-07` PASS, default 07-09 FAIL,
   `--floor 999999` FAIL — unchanged.
2. **`mtm_catchup.py` (new, write-path)** — after refresh, marks every real trading day <= today that
   is (a) missing a paper_nav row, (b) settled to the coverage floor, (c) on/after the sleeve's
   inception, and (d) on/after the sleeve's last rebalance — guard (d) means a past day is never
   back-marked with positions that have since changed. Days below the floor are left PENDING (heal
   next run). Marks via `paper_mtm.compute_nav`/`write_nav`; **never overwrites an existing NAV** (the
   `d in navs` skip), so it only fills genuine gaps. Exit 0 = today settled+marked, 2 = today pending
   (normal), 1 = error. `--db` flag for copy-testing.
3. **`verify_run.py` tweak** — continuity now checks only up to the last SETTLED trading day; a
   below-floor "today" is PENDING, not a gap. This removes the daily false-FAIL while still catching
   real settled-history holes. Live: `settled<=2026-07-08 (pending>2026-07-08)` -> **PASS 17/17**.
4. **`daily.bat` rewrite (goto flow, pure ASCII)** — refresh -> [if today settled: enforce overlay
   stops] -> `mtm_catchup` -> anomaly -> graphify -> verify -> ops stamp. Stops run only on a settled
   today (so no stop fires off partial prices) and BEFORE catch-up (so today's NAV reflects any
   stop-sale). **Task now exits 0 on a normal pending day** (today heals next run); it fails nonzero
   only on a real verify gap or a catch-up error.

**Verification.**
- Copy test (VACUUM-INTO snapshot): deleted all 17 settled 2026-07-08 NAV rows, ran catch-up ->
  **re-marked 17/17**, left 07-09 PENDING, 0 blocked by the rebalance guard. Re-marked NAVs matched
  the originals except 6 sleeves differing by ~\$0.02-0.14 — expected and MORE correct: the originals
  were marked this morning on then-incomplete 07-08 data (carry-forward), the re-mark uses now-settled
  closes. (In production catch-up never overwrites, so this is a test artifact only.)
- Live dry-run: **no-op** (all settled days already marked; 07-09 pending) -> marked=0, exit 2 — the
  production path is safe right now.
- `daily.bat` goto flow stub-tested across today-settled / today-pending / catch-up-error /
  verify-fail — all branch correctly; the common pending case exits 0.
- Frozen tests d=±0.0000pp (4/4).

**Known minor edge (documented, not fixed):** if TODAY is settled at 17:15 (rare — data usually
lags) AND a stop fires AND a prior day is being healed the same run, that prior day is marked with
post-sale positions. The common case (today pending -> stops skipped -> no sale) is unaffected. A
`--prior-only`/`--today-only` split would make it exact; deferred as not worth the complexity now.

**Effect on the open items:** the **2026-07-09 NAV gap now self-heals automatically** at the next
daily run once 07-09 settles overnight (no manual backfill needed); the daily-task-fails-every-day
problem is resolved. Days marked-on-incomplete-data BEFORE this change (e.g. the slightly-stale 07-08)
are left as-is — catch-up only fills missing days, and rewriting existing NAV history is not something
it does.


# Appendix BO - 07-09 NAV gap backfilled (settled + catch-up); a provenance anomaly noted (2026-07-10, ~14:45 local)

**Operational event** — the 2026-07-09 NAV gap (Appendix BH) is now closed, and the M3.5 catch-up
path ran for real against live for the first time.

**What happened.** 2026-07-09 finally settled: a 2026-07-10 14:44 refresh brought it to **5,204
closes** (>= 5,000 floor) — it had been stuck at 4,381 (17:17) / 4,724 (22:30) / 4,726 (07-10 00:05)
before that. `check_coverage --date 2026-07-09` -> PASS. Ran the authorized `mtm_catchup` against live:
it **marked 2 sleeves** for 07-09 (`llm_overlay_mom_roa_top1_paper`, `llm_overlay_sector_top4_paper`),
left 2026-07-10 PENDING (4,352 < floor), exit 2. `verify_run --mode daily` -> **PASS 17/17**
(settled<=2026-07-09). All 17 sleeves now have a 2026-07-09 `paper_nav` row.

**Data-integrity check (the important part).** Recomputed each sleeve's 07-09 NAV from the now-settled
data and compared to the stored row: **0/17 stale — all match to the cent.** So every 07-09 mark is
correct.

**Provenance anomaly — REPORTED, unresolved (Evan's input needed).** Catch-up marked only 2 of the 17,
which means **15 sleeves already had a correct 07-09 row before this run** — everything except the two
cash-veto overlay treatments. That is unexpected: at 2026-07-09 18:04 `verify_run` showed all 17
missing 07-09; `TradingDailyMTM` ran 2026-07-09 17:15 and FAILED at the coverage gate (LastResult
0x1, no MTM); every live `mtm_catchup` I ran before the backfill was `--dry-run` (no writes); and the
only live python now is the Streamlit dashboard (read-only on `paper_nav`; its subprocess calls launch
backtests/sims, not live MTM). So some other process marked those 15 between 07-09 18:04 and 07-10
14:45. Most plausible: a manual `start_all.bat`/`paper_mtm` run by Evan, or the parallel session, once
07-09's held names were present (the ~500 late tickers are illiquid names the sleeves don't hold, so a
mark taken at 4,700-ish coverage would still price every held position correctly — consistent with the
exact match). **No corruption**: `paper_nav` is `INSERT OR REPLACE` on `(strategy, nav_date)` (SQLite
serializes writers; PK forbids dupes), verify's cash recon is exact, and the values are verified
correct. Flagging so Evan can confirm what ran; nothing needs fixing on the data itself.

The live `daily_price_refresh` also pulled 2026-07-10 to 4,352 closes (partial, market just closed) —
it stays PENDING and will be marked by catch-up on a later run once it settles, exactly as designed.


# Appendix BP - 07-09 provenance RESOLVED: a concurrent session backfilled it (gate-bypass risk noted) (2026-07-10, ~15:10 local)

Resolves the provenance question left open in Appendix BO (why 15 of the 17 07-09 `paper_nav` rows
existed before the authorized catch-up ran).

**Answer, from the session transcripts.** A **separate, concurrent Claude session** — `33e12a94`,
running in `D:\ClaudeCode` (parent dir) on an interactive task whose opening prompt was *"...You are
my senior engineering lead. Review and upgrade the CLAUDE.md..."* — ran a bash loop
`for s in <sleeves>: paper_mtm --as-of 2026-07-09 --strategy "$s"` at ~2026-07-10 14:41, ~4 minutes
before this session's catch-up backfill (14:45). It read `paper_mtm.py`'s `--as-of` backfill
docstring first, then looped it over ~15 sleeves. This session's `mtm_catchup` then marked only the 2
it had missed (`llm_overlay_mom_roa_top1_paper`, `llm_overlay_sector_top4_paper`). Ruled out along the
way: `TradingDailyMTM` (failed 07-09 17:15 at the coverage gate, 0 MTM in `last_daily_run.log`), the
Streamlit dashboard (read-only on `paper_nav`), and the `daily-trade-check` scheduled agents (raw-grep
of their transcripts shows no NAV-write; they read the NAV table per their SKILL).

**No harm — verified.** `paper_nav` is `INSERT OR REPLACE` on `(strategy, nav_date)` and SQLite
serializes writers, so the two concurrent backfills could not corrupt or duplicate; all 17 07-09 NAVs
were confirmed correct (fresh recompute matches to the cent, Appendix BO) and `verify_run` PASSes.

**Two real risks this exposed (REPORT for Evan — no change made):**
1. **Concurrent uncoordinated NAV writers.** Two sessions wrote 07-09 to the live 5 GB DB within
   minutes of each other. It was benign here, but the project's rule against concurrent DB writers
   (e.g. `factor_backtest`) applies in spirit — official NAV marking should have a single owner
   (the `daily.bat` catch-up).
2. **Raw `paper_mtm --as-of` bypasses the coverage gate.** The other session marked at ~14:41 when
   07-09 was still 4,726 closes (below the 5,000 floor). It happened to be correct (the ~500
   still-missing tickers were non-held names; EACO/FMBM were carried forward, matching the settled
   recompute), but a direct `paper_mtm` run has NO coverage gate — only `daily.bat`/`mtm_catchup` do.
   Options to close the bypass (Evan's call): fold the coverage check into `paper_mtm` itself
   (with a `--force` escape hatch), and/or make raw `paper_mtm` the discouraged path vs `mtm_catchup`.


# Appendix BQ - Coverage gate moved into paper_mtm.py itself; raw-MTM bypass closed (2026-07-10, ~15:15 local)

Closes the gate bypass exposed in Appendix BP: a raw `paper_mtm --as-of <date> --strategy X` call had
NO coverage check (only `daily.bat`/`mtm_catchup` did), so a concurrent session marked 2026-07-09 at
4,726 closes (< the 5,000 floor). Correct only by luck (held names present); the guardrail had a side
door.

**WHAT.** `scripts/momentum/paper_mtm.py` `main()` now runs the shared `coverage_status()` for `--as-of`
after the weekend + pre-inception guards and BEFORE `compute_nav`/`write_nav`: if the day is below the
floor and `--force` is not given, it logs `COVERAGE FAIL ... refusing to MTM` and returns exit 2
without writing. New `--force` flag bypasses it for the rare intentional case (held names known
present). `mtm_catchup` is **unaffected** — it calls `compute_nav`/`write_nav` directly (not `main()`)
and does its own per-day gating; verified it still runs (07-10 pending, marked=0, exit 2).

**HOW / verification.**
- `--as-of 2026-07-10` (pending, 4,352 < floor), no `--force` -> `COVERAGE FAIL`, **exit 2, 0 rows
  written** for the sleeve (refuses before writing).
- `--as-of 2026-07-09` (settled, 5,204), no `--force` -> proceeds, re-marks the same value
  ($104,310.00, idempotent) -> exit 0.
- `--force` path exercised by `test_inception_guard.py` (its fixture has no price data; the test uses
  `--force` and its 6 checks still pass).
- Frozen tests d=±0.0000pp (4/4).

**Design note.** The coverage floor logic lives once in `check_coverage.coverage_status()` and is now
consumed by four callers — the daily gate, `mtm_catchup`, `verify_run`'s pending-day boundary, and
(this entry) `paper_mtm` itself. Any NAV-writing path a human or another session is likely to reach
now refuses sub-floor data by default. The remaining coordination item (only one owner should mark
NAVs) is a process convention, not enforceable in code.


# Appendix BR - PRD roadmap complete through M5 (M6 gated); 07-11 verification pass + HANDOFF freshness fix (2026-07-11, ~20:00 local)

Not a new milestone - a verification checkpoint at the end of the Ops/Infra PRD. The executing
model was told to keep working the roadmap; the roadmap is done except for the gated tail, so this
entry records the honest stop rather than manufacturing work.

**State.** M1-M5 (+ amendment M3.5) are all complete and committed (record Appendices BB-BN, plus
the 07-09/07-10 hardening BO/BP/BQ). **M6 (slippage) is the only remaining PRD task and is GATED**
by its own terms: it cannot start until the 2026-08-01 unattended monthly rebalance produces Alpaca
PAPER fills. Today is 2026-07-11 - the fills do not exist. Per the PRD ("If the gate isn't met,
report and stop at M5"), the roadmap is at its stopping point.

**Verification run (all read-only).**
- `git status` clean; latest commit `bb3bae4` (BQ codebase-memory). Nothing uncommitted.
- `verify_run --mode daily` -> **RESULT: PASS (17/17 sleeves OK)**. Every sleeve: NAV continuity
  intact (the 4 continuous-May sleeves show 47/47 +2 holidays; the 07-06 cohort 4/4), cash recon
  delta $+/-0.00 (cent-perfect), 0 pre-inception rows, position counts at target. Calendar
  2026-05-01..2026-07-10, `settled<=2026-07-09`, `07-10 PENDING` (correct - 07-10 has not settled;
  it heals on the next scheduled run).
- Record TOC + appendix headings both terminate cleanly at BQ; anchors match (renderer contract).
- Friday 2026-07-10 17:15 `TradingDailyMTM` (first live run of the self-healing `daily.bat`, M3.5)
  exited 0x0: coverage PENDING (4,394 < 5,000 floor) -> stop-enforcement skipped -> `mtm_catchup`
  marked=0 (07-10 left pending) -> anomaly scan -> `verify_run` PASS 17/17 -> stamp
  `[OPS 2026-07-10] coverage=PENDING verify=PASS`. The pre-M3.5 flow failed the gate on this exact
  situation the night before (07-09, exit 1); M3.5 is proven in production.

**HANDOFF freshness fix (the only file change this entry).** HANDOFF's milestone note still listed
the raw-`paper_mtm` coverage-gate bypass as an OPEN risk (#2), but Appendix BQ closed it 2026-07-10.
Left as-is, a fresh session would think the bypass is live and might re-fix it. Corrected: risk #2
now reads CLOSED-by-BQ (paper_mtm.main() runs the shared gate, refuses sub-floor --as-of without
--force); risk #1 (one-owner NAV marking) noted as still a process convention; "Last updated" bumped
to 2026-07-11 with a one-line health-check summary. No code touched, so frozen tests were not re-run
(last green at BQ, 4/4 d=+/-0.0000pp); this entry changes documentation only.

**Bottom line.** The unattended system is healthy and its track record verifies clean. There is no
further roadmap work that can be started without either (a) the 2026-08-01 Alpaca fills (M6) or
(b) a new instruction from Evan outside the Ops/Infra scope guard.


# Appendix BS - Full audit (monthly-rebalance path) + 4 fixes: verify wiring, coverage-gate/rebalance interaction, schedule drift (2026-07-11, ~15:00 local)

Evan ran `/audit` after the roadmap hit its wall (Appendix BR). Read-only sweep weighted to the
unattended 2026-08-01 monthly rebalance - the first monthly run under the M3.5/BQ regime and the
live risk. Findings pass changed nothing; fixes below applied after Evan's "do all".

**Clean (verified, no action).** DB integrity (read-only): 0 duplicate / weekend / pre-inception
`paper_nav` rows, unbroken continuity, cash recon **$+0.0000** across all 17 sleeves, 0 bad/dup open
positions, 0 non-positive closes. The two sub-floor MARKED days (2026-06-19, 2026-07-03) are
legitimate NYSE holidays (Juneteenth; July-4-observed) correctly tolerated by `verify_run` as
"+2hol". Secrets: `alpaca_keys.env` git-ignored + untracked, no hardcoded keys in tracked Python.
`check_coverage`/`verify_run`/`mtm_catchup`/`paper_mtm` code reviewed - sound.

**How the live 08-01 path actually runs (the crux).** `monthy-llm-rebalance` is a Claude AGENT
task (not a Windows .bat task); its SKILL.md Step 4 runs `cmd /c rebalance.bat`. So `monthly_auto.bat`
- the "Option B" batch that M3.3 wired `verify_run --mode monthly` into - is NOT what fires; it is
unused (needs an Anthropic key, flagged UNTESTED). This reframed two findings.

**Finding 1 (HIGH) - the monthly verifier never ran on the real rebalance.** `verify_run --mode
monthly` lived only in the unused `monthly_auto.bat`; `rebalance.bat` called neither it nor
`check_coverage`. So the M3.2/M3.3 success criterion "the 2026-08-01 unattended rebalance gets
verified" was unmet - specifically the monthly-only position-count-vs-target check (c) would never
fire on the event it was built for. **Fix:** appended `verify_run --mode monthly` (FAIL -> nonzero
exit + log line) to the end of `rebalance.bat`.

**Finding 2 (HIGH, raised from the MED I first rated) - BQ's coverage gate would make the rebalance
day unmarked, and `verify_run` recon would then FAIL the night of every rebalance.** `rebalance.bat`
ends with 16 `paper_mtm --strategy X` calls; after Appendix BQ, `paper_mtm.main()` refuses a
sub-floor day (exit 2, no write) without `--force`, and same-day coverage at the ~17:33 rebalance is
always partial (~4,400 < 5,000). So the rebalance day goes unmarked while positions have JUST
changed. `verify_run` recon (verify_run.py:130-149) reconciles CURRENT positions against the LATEST
marked NAV - if that latest row is the PRE-rebalance day, post-rebalance positions do not reconcile
-> FAIL. This interaction had never been exercised (both `verify_run` and BQ postdate the last
rebalance, 07-07). **Deviation from the proposed fix:** I had proposed dropping the 16 calls
("catch-up owns marking"); tracing the recon logic showed dropping them makes the failure WORSE, so
the correct fix is **add `--force`** to all 16 (not remove). Justified: on a rebalance day the held
names are GUARANTEED present (`paper_rebalance` just filled them) and the MTM price basis == the fill
basis, so marking today on the partial cache is exactly correct - which is the precise case BQ's
`--force` escape hatch was written for.

**Finding 3 (LOW) - `rebalance.bat` has no coverage gate, and that is correct; documented so.** A
hard gate would abort every monthly run (same-day data is always partial at 17:33). It is safe
because 12-1 momentum ranks use the close ~21 trading days back (`SKIP_TRADING_DAYS`, momentum.py:27-
28), so partial same-day publication cannot misrank; fills carry-forward for any name missing a
same-day close. **Fix:** added a REM block to `rebalance.bat` explaining the deliberate omission +
the `--force` rationale, so a future maintainer does not "helpfully" add a gate and break the run.

**Finding 4 (LOW) - schedule/docs drift.** `list_scheduled_tasks` shows the live cron is
`30 17 * * *` (~5:33pm, jitter 183s), and the task's own SKILL.md says 5:30pm - but memory
`monthly_rebalance_trigger_timing_bug.md`, `MEMORY.md`, `HANDOFF.md`, and the architecture bin all
claimed `0 18 * * *` / 6:03pm (the 07-07 "restore to 0 18" never stuck). 5:33pm is only ~15 min
after the 5:15pm daily MTM, which on a cold/busy run can still be executing (07-10 finished ~17:37),
so on a REBALANCE day the daily MTM and the rebalance can overlap as two DB writers. **Fix:**
corrected all four docs to the verified `30 17`. The cron change itself (recommend 6:00pm for a clean
margin, restoring the originally-intended timing) is **flagged for Evan, NOT auto-applied** - retiming
a live real-Alpaca-adjacent unattended task is his call, and the record shows past timing changes were
made "with Evan's OK".

**Verification.**
- Frozen tests: **4/4 d=+/-0.0000pp** (v1 2023_Q4 -0.0000 / 2025_H1 -0.0000; v2 2023_Q4 -0.0000 /
  2025_H1 +0.0000). Only a .bat + docs changed, but run per contract.
- `verify_run --mode monthly` -> **PASS (17/17)** on the live DB - proves the newly-wired command runs
  and the book passes the monthly-only checks.
- `rebalance.bat`: pure ASCII (0 non-ASCII bytes), 16/16 `paper_mtm` calls carry `--force`, none
  without, `verify_run --mode monthly` present.
- **Boundary:** `rebalance.bat` was NOT executed end-to-end - it trades (`paper_rebalance`,
  `alpaca_sync --execute`), which is forbidden. Verified by component; the full run happens under the
  real 08-01 task.

**Files changed:** `scripts/momentum/rebalance.bat` (F1/F2/F3); `HANDOFF.md`, `MEMORY.md`,
`memory/monthly_rebalance_trigger_timing_bug.md`, `.claude/codebase-memory/architecture.md` (F4 +
BS cross-refs). `monthly_auto.bat` left untouched (unused Option B path; its now-redundant
`verify_run` is harmless).


# Appendix BT - Monthly-rebalance cron shifted 5:33pm -> 6:03pm (audit F4 applied per Evan) (2026-07-11, ~15:20 local)

Closes audit finding F4 (Appendix BS). Evan approved the recommended timing shift; applied it the
same session.

**WHAT.** `monthy-llm-rebalance` cron `30 17 * * *` -> `0 18 * * *` via
`mcp__scheduled-tasks__update_scheduled_task` (only the cron; the deliberately-typo'd task NAME was
left untouched). Now fires ~6:03pm local ("At 06:03 PM" + ~3-min dispatch jitter), a clean ~48-min
margin after the 5:15pm `TradingDailyMTM`, removing the rebalance-day two-writer overlap risk BS
flagged. `enabled=true`, nextRunAt 2026-07-12 18:03 (no-op - July already stamped in
`rebalance_log.md`); first REAL fire still 2026-08-01. Docs synced to the applied state:
`HANDOFF.md`, `.claude/codebase-memory/architecture.md`, `MEMORY.md`, and memory
`monthly_rebalance_trigger_timing_bug.md` (its CORRECTION block now reads APPLIED).

**Observed, not touched:** a stray scheduled task `hellohello` (cron `0 8 * * *`, description
"hello") exists on the machine and fires daily ~8:08am. Not part of the Trading system - looks like a
throwaway test task. Left as-is (not mine to delete; flagged to Evan). Harmless cruft.

**No code changed** in this entry (a scheduler-config change + doc sync); frozen tests unaffected
(last green 4/4 d=+/-0.0000pp at Appendix BS).


# Appendix BU - Pre-registered champ-tweak experiments on clean data: preemptive overlays FAIL, weight sweep finds ONE at-threshold candidate (residual 80/20) (2026-07-14, ~01:05 local)

Evan asked (2026-07-14, ~00:15) whether tweaking mom_roa_6535 / residual_roa_6535 would improve
results, then authorized the two research avenues from the options list: (2) preemptive risk
overlays and (3) a weight/top-N sweep, both against the post-backfill CLEAN cache. Design + decision
rules were LOCKED BEFORE any run in `docs/prereg_2026-07-14_champs_tweaks.md` - grids, windows
(in-sample 2015-01-01->2023-12-31; holdout 2024-01-01->2026-05-01), methodology (5 bps, monthly,
equal-weight, identical to the 06-13 revalidation), and thresholds (+5pp holdout = the measured
data-noise floor). New scripts `scripts/momentum/research/test_champs_preemptive_clean.py` and
`sweep_champs_weights_clean.py` (reusing `test_mom_v2_preemptive.py`'s overlay machinery for
apples-to-apples); 56 sequential backtests, 00:30-01:00 local (off-hours, Swing ingestion verified
isolated to swing.db); results in `var/momentum/champs_preemptive_clean.json` +
`champs_weight_sweep_clean.json`.

**Harness self-check.** The 65/35@50 sweep rows reproduce the 06-13 revalidation baselines to
+0.10..+0.63pp (mom_roa IS +5.00 vs +4.89, HO +36.23 vs +35.59; residual IS +9.59 vs +9.47, HO
+32.16 vs +32.07). The drift comes from a month of routine cache evolution (late XBRL filings,
split rebases) - itself a live demonstration that sub-1pp deltas are noise.

**Experiment A - preemptive overlays: verdict NONE. The overlay family is now closed.**
Trend-200DMA on the champs repeats its mom_v2 failure ON CLEAN DATA and is worse than doing
nothing: mom_roa in-sample CAGR +4.89 -> **-3.15%** with DD WORSE (-47.6 -> -58.5%: whipsaw sells
lows, re-enters late), holdout CAGR **-22.2pp**; residual holdout **-10.8pp** for only +2.9pp DD.
Vol-target 16/20% is a near-no-op on holdout (d_CAGR +-1pp, d_DD <=0.6pp) and mildly negative
in-sample (CAGR -0.7..-1.0pp; best in-sample DD gain +5.7pp on mom_roa voltgt16, but the rule
required HOLDOUT DD >= +5pp - no config came close, max +3.0pp). With reactive stops (Attempts
12-13), VIX gates (Appendix G), vol-target L/S (Appendix R), and now trend/vol-target on both
champs with clean data all failed, **the "DD control must be preemptive" hypothesis from Attempt 13
is answered: these SPY-based preemptive implementations do not work on this platform either.**

**Experiment B - weight/top-N sweep: ONE formal replacement candidate, AT threshold.**
- **Top-50 is confirmed frozen-correct for both champs**: every top-N deviation (25/75/100) loses
  holdout CAGR (-1.7..-8.1pp).
- **mom_roa 65/35: no change.** Holdout best is w7525 (+2.66pp, sub-threshold); in-sample now
  favors LOWER momentum weight (w5545 +2.63pp) while holdout favors higher - the windows disagree,
  the peak is broad, 65/35 stays the defensible middle. Matches the honest prior.
- **residual: holdout CAGR is MONOTONE in residual-momentum weight** - w80 +37.15% > w75 +35.71% >
  w70 +34.03% > w65 +32.16% > w60 +24.83% > w55 +21.94% > w50 +15.94% (21pp spread!), and
  in-sample mildly agrees (w80 +10.62% vs baseline +9.47%). **residual_roa_8020@50 beats the locked
  baseline on ALL EIGHT metric-window combos** (CAGR/Sharpe/DD both windows; holdout Sharpe 1.342
  vs 1.212, holdout DD -18.1 vs -20.1) and formally clears the pre-registered rule: holdout
  **+5.08pp** vs the required +5.00.

**Honest caveats on the w8020 finding (stated before any decision):** (1) it clears the threshold
by 0.08pp - and measured against the SAME-DAY 65/35 rerun (+32.16) instead of the locked 06-13
baseline (+32.07), the margin is +4.99pp, i.e. AT the noise floor, not above it; (2) w80 is the
EDGE of the pre-registered grid and the gradient is still rising - the "optimum" may lie outside,
classic tell of sample-fit toward the dominant signal; (3) 40 sweep runs against a ~29-month
holdout means one +5pp finding is not far from chance expectations; (4) at 80/20 the ROA leg is
nearly vestigial. Per the prereg, NOTHING deploys from this: the live sleeves and frozen params
are untouched. The defensible next step, if Evan wants one, is a NEW parallel research sleeve
(residual_roa_8020) to gather forward evidence - the exact pattern that vetted residual itself.
Extending the grid to w85/w90 after seeing w80 win would be data-snooping; if done, it is
exploratory only, never a deployment basis.

**Frozen tests after the new scripts (chained after the sweeps, same process pool):**
4/4 at d=+-0.0000pp (v1 2023_Q4 -0.0000 / 2025_H1 -0.0000; v2 2023_Q4 -0.0000 / 2025_H1 +0.0000).

**Files:** prereg doc + 2 research scripts (new, additive; no live module touched), 2 result JSONs
(var/, untracked by design like the 06-13 revalidation), this entry. Memory
`sleeves_verdict.md` updated: the preemptive-DD-control door Attempt 13 left open is now closed.


# Appendix BV - EXPLORATORY (post-hoc) residual hi-weight extension: w80 is a plateau, not an edge spike; the ROA leg wants ~10-20 percent, not 35 (2026-07-14, ~01:35 local)

Evan asked (option 3 of the BU options) to extend the residual weight grid past its edge to see
where the gradient tops out. **This is post-hoc / data-snooping BY CONSTRUCTION** (the grid w85/90/95
was chosen AFTER seeing w80 win the prereg'd sweep). Per the prereg it can ONLY inform a future
forward-test-sleeve decision (Evan's call); it can NEVER justify deployment.
`scripts/momentum/research/sweep_residual_hiw_ext.py`, residual only (mom_roa's sweep gradient was
non-monotone, nothing to extend), w80/85/90/95 x 2 windows, clean cache, 5 bps. Result JSON
`var/momentum/residual_hiw_ext.json` (gitignored). w80 rows reproduce the sweep (self-check).

**Result - the concerning "monotone rising at the edge" shape does NOT continue; it is a broad
plateau.** Residual holdout CAGR (65/35 baseline +32.07%):

| w (resid/ROA) | holdout CAGR | vs 65/35 | holdout Sharpe | holdout DD | in-sample CAGR |
|---|---|---|---|---|---|
| 80/20 | +37.15% | +5.08p | 1.342 | -18.1% | +10.62% |
| 85/15 | +36.13% | +4.06p | 1.358 | -18.5% | +11.24% |
| 90/10 | +36.89% | +4.82p | **1.414** | -18.4% | **+11.37%** |
| 95/05 | +34.66% | +2.59p | 1.362 | -18.1% | +10.46% |

**Interpretation (honest).**
1. **w80 is NOT a special optimum or an off-the-edge spike** - it sits near the top of a NOISY
   PLATEAU spanning w80-90 (holdout ~36-37%, ~1pp adjacent wobble = noise), which itself sits atop a
   CLEAN MONOTONE ramp from the sweep (w50 +15.9 -> w65 +32.1 -> w80 +37.2). A pure-noise result
   would not show that ramp-then-plateau structure, so there IS a real cross-sectional signal:
   **residual momentum wants only ~10-20% ROA, not the 35% it inherited from mom_roa_6535.**
2. **If anything w90 dominates w80** (higher holdout Sharpe 1.414 vs 1.342, higher in-sample CAGR,
   ~equal holdout CAGR/DD). So the sweep's "80/20" headline was just the grid edge; the plateau
   CENTER (~w85-90) is the honester point. Picking any single max is snooping.
3. **This still does NOT clear deployment** - it is post-hoc, one ~29-month holdout regime (2024-26),
   and the whole lift could be that regime favoring low-ROA residual. That is exactly what forward
   paper evidence tests. The live sleeves and frozen params remain UNTOUCHED (standing decision from
   BU option 1: log-only).
4. **Net upgrade vs BU:** the residual finding is stronger as a *characterization* (a robust plateau,
   not a lone at-threshold point) but UNCHANGED as a *decision* (no deploy). If Evan ever elects the
   forward-test sleeve (BU option 2), the honest construction is ~85/15 residual/ROA, seeded as a
   NEW parallel research sleeve, never a modification of residual_roa_6535.

**No live module touched; frozen tests unaffected (last 4/4 d=+-0.0000pp at BU). Nothing deployed.**


# Appendix BW - Residual weight ladder DEPLOYED: 10 forward-test sleeves seeded 05-01 by replay (BV plateau -> live) (2026-07-14, ~18:30 local)

Evan asked to turn the BU/BV residual-weight finding into a live forward test: "start all of these
residuals at the same time" (10 weights 50/50..95/05), and "we have the data from May first so why
not seed them all at 5/1 then run a simulation to get the data to where it is today." Done - 10 new
systematic paper sleeves, the roster's 4th family (HANDOFF now 27 sleeves).

**WHAT.** `residual_w<MM><RR>_paper` for (MM/RR) in 50/50, 55/45, 60/40, 65/35, 70/30, 75/25,
80/20, 85/15, 90/10, 95/05 - identical to `residual_roa_6535_paper` (top-50 monthly, 5 bps,
broker-realistic, `tradeable_universe`) EXCEPT the residual-mom/ROA Z-blend weight. This races the
BV finding (a broad w80-90 holdout PLATEAU in-backtest; residual momentum wants ~10-20% ROA, not
35%) forward, where it can't be overfit. Systematic, NO LLM decisions, NOT Alpaca-mirrored.

**HOW.** New `scripts/momentum/seed_residual_wsweep.py` - deterministic 05-01 REPLAY, the same
method that seeded `residual_roa_6535_paper` (06-09 backdate) and the 06-13 re-inception:
interleaved per sleeve `rebalance 05-01 -> MTM each settled day -> rebalance 06-03 -> MTM ->
rebalance 07-01 -> MTM through 07-13` (interleaving required: `compute_nav` prices CURRENT
positions, so each window's NAVs must be written before the next rebalance). Rebalance dates match
the May champions'. `last_rebalanced_at` stamped 07-01 so tonight/tomorrow's `mtm_catchup` extends
them past the pre-rebalance guard. Two surgical code edits: `paper_rebalance._strategy_config` +1
branch (parses the weights from the sleeve name -> `zcombo` residual+ROA rank_fn); `verify_run`
POSITION_TARGETS += the 10 names (target 50). Existing-sleeve guard in the seeder refuses to replay
over a live sleeve.

**TIMING / SAFETY.** Write-path tested on a full DB COPY first (`trades_seedtest.db`): replay ->
`verify_run --mode monthly` PASS 27/27, recon $0.00, continuity 48/48. Evan flagged the real clock
(6:08pm) - INSIDE the 5:00-6:30pm daily-MTM exclusion window - so the live write was HELD until
6:30pm (tonight's 5:15pm `TradingDailyMTM` confirmed finished 17:23 PASS 17/17; the 6:03pm
`monthy-llm-rebalance` fire no-ops on its gate). Live seed ran 18:30, 1.7 min, additive (existing
sacred history untouched).

**VERIFY (live).** `verify_run --mode monthly` -> **RESULT: PASS (27/27)**. All 10 ladder sleeves:
continuity 49/49 (05-01..07-13), recon delta $+/-0.00, 0 pre-inception, 45-47/50 open (broker-
realistic drops the same illiquid micro-caps as the champions). Frozen tests 4/4 d=+/-0.0000pp (run
before the seed). 27 sleeves total.

**HONESTY DEMARCATION (critical).** The 05-01->07-13 rows are DETERMINISTIC REPLAY on today's
cache - simulation, NOT live paper trading. **Live forward data begins 2026-07-14.** The backtest
that motivated the ladder (BU/BV) used data only through 2026-05-01, so the replayed 05-01->07-13
segment is genuinely post-selection (a mini-holdout) - but tiny (3 rebalances, ~10 weeks) and
therefore noise.

**Replay/cache-drift caveat (quantified).** The replayed 65/35 twin (`residual_w6535_paper`) does
NOT reproduce the live champion `residual_roa_6535_paper`, because the champion's 05-01->06-12
history was written on the 06-13 cache while this replay uses the 07-14 cache (a month of late XBRL
ROA restatements, split rebases, spike-nulls): identical at 05-01 ($99,950), diverges to -$2,294
(-2.03%) at the 06-30 peak, narrows to -$887 (-0.84%) at 07-13 (the 07-01 rebalance re-syncs
positions). So: the 10 ladder sleeves are internally consistent (same cache + method =
apples-to-apples AMONG THEMSELVES), but the replayed segment is a RECONSTRUCTION, not the champion's
exact stored NAVs. This also quantifies replay uncertainty at ~1-2% over 10 weeks - any ladder gap
smaller than that over the replayed part is cache-noise.

**Replay ranking (05-01->07-13, NOISE - do not read into it).** w6040 +5.80% / w5545 +5.63% /
w5050 +5.17% / w6535 +4.29% / w8515 +4.25% / w9505 +3.68% / w7525 +2.55% / w9010 +2.44% /
w7030 +2.37% / w8020 +2.23%. This INVERTS the backtest holdout (which favored HIGH residual
weight): over 10 weeks across near-identical baskets the ordering is dominated by noise, which is
exactly why the forward test exists and why no weight will be "chosen" for many months of live data.

**Automation.** No daily.bat change needed - `mtm_catchup` and `verify_run` iterate all
`paper_portfolio` sleeves, so the ladder is marked/verified automatically going forward.
`rebalance.bat` got a LADDER section (10 `paper_rebalance` + 10 `paper_mtm --force`, pure ASCII) so
the monthly rebalance carries them too. Dashboard picks them up from `paper_nav` with no change.

**Files:** `scripts/momentum/seed_residual_wsweep.py` (new), `scripts/momentum/paper_rebalance.py`
(+1 branch), `scripts/momentum/verify_run.py` (+10 targets), `scripts/momentum/rebalance.bat`
(ladder section), `HANDOFF.md` (4th family, 27 sleeves), this entry. Result on the live DB;
`trades_seedtest.db` copy can be deleted (scratch).


# Appendix BX - Residual ladder gets its own dashboard panel; daily-report tasks now self-commit + auto-push (2026-07-14, ~19:00 local)

Two small post-BW follow-ups (Evan-directed).

**Dashboard: residual ladder in its own panel.** The 10 `residual_w*` sleeves inception 05-01, so
they were landing in the Overview's "Original sleeves" cohort panel and crowding it (16 lines).
`trading_bot/dashboard/web.py`: added a `_is_ladder(s)` split (`name.startswith("residual_w")`) that
pulls them out of `original` into a third `_render_cohort_panel(ladder, key="residual_ladder")` under
its own heading ("Residual weight ladder ... record BW ... 05-01->07-13 is replay, live forward from
07-14"); added 10 `_SLEEVE_SHORT` labels ("resid 50/50" .. "resid 95/05") so the legend/table read
cleanly. Surgical (reuses the existing panel renderer); no other view touched. VERIFIED live at
http://localhost:8501 after `restart_dashboard.bat`: the new panel renders all 10 traces, the
Original panel is back to its 6 May sleeves, no errors. Frozen tests 4/4 d=+/-0.0000pp.

**Automation: the two daily-report research tasks now self-commit + auto-push.** `daily-trade-check`
(8:07am, Pre-Market) and `daily-trade-check-2` (5:30pm, Post-Market) previously wrote
`daily_report.md` + rendered the HTML twin but never committed, so the working tree showed dirty
`daily_report.*` every session (I had been committing them by hand, and once accidentally swept them
into an unrelated commit -> split back out). Their SKILL.md prompts (in
`~/.claude/scheduled-tasks/`, outside the repo) now end with: `git add daily_report.md
daily_report.html` (EXACTLY those two paths - never `-A`/`.`, so an unattended run can't stage
unrelated in-progress work) -> `git commit` -> `git push`; nothing-to-commit skips the push; a
rejected/failed push is NON-FATAL (leave it local, no force-push, no auto-merge/rebase). The
read/research-only, never-trade guardrail is restated in both. Effect: the remote stays current and
the tree stays clean without hand-holding. (These research tasks are not in HANDOFF's automation
roster - they are journal/research, not core trading automation.)

**Files:** `trading_bot/dashboard/web.py` (ladder panel + labels), this entry. SKILL.md prompts
edited live (outside the repo).


# Appendix BY - Coverage-lag fixed with a morning refresh task (TradingMorningMTM); SEPARATE FINDING: overlay invalidation stops are dormant (2026-07-15, ~14:40 local)

Evan (2026-07-15 AM): "the 07-14 coverage gate still hasn't cleared as of this morning - third time
this pattern has shown up in a week." Investigated read-only; it is a refresh-LATENCY issue, not a
data-quality failure, and the gate is behaving correctly.

**Diagnosis.**
- 07-14 cached at **4,376** closes (vs a ~5,200 baseline, floor 5,000) - a genuine 16% shortfall,
  below even the 90%-relative floor (4,702). 825 tickers missing vs 07-13; mostly the illiquid
  OTC/unit/fund tail, but **MRK (Merck) - a liquid large-cap - was also missing**, i.e. real
  incomplete publication, not "these never traded."
- **Read-only yfinance probe (no writes):** every missing sample name - MRK 120.78, EACO, KFII,
  UYSC, FMBM, ABCP - HAS a 2026-07-14 close at yfinance NOW. So the data is complete upstream; only
  OUR cache is stale.
- **Root cause:** the ONLY automatic refresh is the 5:15 PM `TradingDailyMTM`. Nothing re-fetches
  between the 07-14 5:15 PM run (when yfinance was still incomplete -> 4,376, pending) and the 07-15
  5:15 PM run. Earlier days (07-09/07-10) cleared faster only because manual refreshes ran mid-session
  during our work. So "hasn't cleared this morning" = nothing had run to re-pull it yet, not a stuck
  day. The coverage=PENDING stamps (07-10/07-13/07-14) are the NORMAL same-day-incomplete state at
  5:15 PM; each day then settles on the next run. The pain is purely the ~24 h heal latency.

**Fix (Evan approved option 1).** New Windows task **`TradingMorningMTM`** at **7:45 AM daily**,
`StartWhenAvailable`, mirrors `TradingDailyMTM`'s principal (evan / Interactive / Limited) ->
`scripts/momentum/morning_refresh.bat` (pure ASCII) = `daily_price_refresh` + `mtm_catchup` +
`verify_run --mode daily`, logs `var/last_morning_run.log`. The prior day (settled at yfinance
overnight) is re-pulled and catch-up-marked, so books are current by ~8 AM (and a Friday heals
Saturday AM, not Monday). Fires at 7:45 so it finishes before the 8:07 AM `daily-trade-check`
research task, which then sees the healed day.

**Why a SEPARATE task, not a 2nd trigger on `TradingDailyMTM` (as literally proposed).** A task runs
ONE action; a 2nd trigger would run the full `daily.bat`, whose overlay invalidation-stop enforcement
(`llm_overlay_ops` / `sector_overlay_ops check-invalidation` -> `paper_trader.sell(reason=
"invalidation")`) is coverage-gated: it SKIPS on PENDING evenings (latest cached date = today,
incomplete) but WOULD FIRE in a morning run (latest = yesterday, settled -> coverage PASS). That
would activate currently-dormant stops and alter the live LLM-overlay experiment as a side effect of
a data fix. So the morning task deliberately does refresh + catch-up + verify ONLY; stop-enforcement
stays on the evening cadence, unchanged.

**SEPARATE FINDING (flagged, NOT changed here) - the overlay invalidation stops are effectively
DORMANT.** Because `daily.bat` gates `check-invalidation` behind `check_coverage` PASS, and every
5:15 PM run finds "today" PENDING (same-day incomplete), the stops SKIP almost every evening
(ops_status shows PENDING on 07-10/07-13/07-14; PASS is rare). So the LLM-overlay experiment's
invalidation stops - a designed risk control (e.g. WDC stop 480) - have essentially never been
enforced. This is likely unintended. It is a live-experiment behavior change to fix, so it is
Evan's deliberate call, NOT bundled into this data-latency fix. Options when addressed: (a) enforce
stops against the last SETTLED close in the daily flow regardless of today's coverage, (b) add
stop-enforcement to the morning task once its interaction is reviewed, or (c) accept stops as
end-of-month-rebalance-only. Spawned as a separate task chip.

**Verification.** `TradingMorningMTM` registered: State Ready, action `cmd /c morning_refresh.bat >
var\last_morning_run.log 2>&1`, trigger Daily 07:45:00-05:00, StartWhenAvailable True, NextRun
2026-07-16 07:45. `morning_refresh.bat` pure ASCII (0 non-ASCII bytes); its three steps
(refresh / mtm_catchup / verify) are each proven this session. NOT run manually today (a mid-market
refresh would write a transient partial 07-15 bar) - 07-14 heals on tonight's 5:15 PM run, and the
morning task first fires 07-16 7:45 AM. No Python changed (new .bat only); frozen tests still 4/4
d=+/-0.0000pp (last run this session). Task config lives in Windows Task Scheduler, not the repo;
`morning_refresh.bat` + doc updates are committed.

# Appendix BZ - Dormant overlay invalidation stops fixed: daily enforcement as-of the last settled close (Evan: option a) (2026-07-15, ~17:30 local)

Follow-up to the SEPARATE FINDING flagged in Appendix BY. Investigated, confirmed, presented the
three options to Evan; **Evan chose option (a)** ("enforce stops against the last SETTLED close
regardless of today's coverage") and it is now implemented.

## BZ.1 Confirmation + quantification (all read-only, gathered before any edit)

- **Mechanism confirmed in code + live log.** `daily.bat` ran both `check-invalidation` calls only
  inside the coverage-PASS branch. The 2026-07-14 17:15 run's log shows the skip verbatim:
  `COVERAGE FAIL: only 4376 closes on 2026-07-14 (< floor 5000)` followed by
  `TODAY PENDING - incomplete same-day publication. Skipping stop-enforcement.`
- **Skip rate.** Every scheduled 5:15 PM ops stamp since stamping began is PENDING: 07-10, 07-13,
  07-14, and tonight's 07-15 (`coverage=PENDING verify=PASS`, run completed 17:18). The only PASS
  stamps (2x 07-12) came from manual/session runs, not the scheduled task.
- **Whole-history proof of dormancy.** Across ALL 563 closed positions in the entire DB (every
  sleeve, since inception), `exit_reason` is `rebalance` on every single row - **zero
  `invalidation` exits have ever occurred**.
- **Root cause, sharpened.** The gate requires UNIVERSE-WIDE coverage (>= 5,000 closes) - the right
  bar for MTM, which ranks the whole universe - but a stop-check only needs the HELD ticker's last
  settled close. On 07-14 the held sectors (XLB/XLI/XLK) all had settled closes cached at 17:15;
  the check was gated off anyway because the illiquid tail dragged universe coverage to 4,376.
- **No realized harm (honest bound).** The stock-overlay treatment
  (`llm_overlay_mom_roa_top1_paper`) has been ALL-CASH since the 07-01 reset (BE VETO), so its
  logged stops (e.g. WDC 480) had nothing to guard. The sector-overlay treatment has held
  XLB/XLI/XLK since 07-07 with stops 49.5/170/172; checked every close 07-07..07-14 - minimums
  50.16/180.37/179.18, **no breach occurred during the dormant window**. Latent control failure,
  not a loss event. Nothing to backdate; the fix is forward-only.

## BZ.2 The fix (option a) - 4 files

1. **`scripts/momentum/check_coverage.py`**: new `last_settled_date(conn, lookback=10)` - newest
   `key_date` whose close count passes the standard floor (same `coverage_status` logic as the
   gate, so "settled" means the same thing everywhere). Read-only.
2. **`scripts/momentum/llm_overlay_ops.py`** + **`scripts/momentum/sector_overlay_ops.py`**:
   `check-invalidation` gains a `--settled` flag - resolves `as_of` to the last settled trading
   day (read-only connection) instead of trusting `--as-of`/today. Without the flag, behavior is
   byte-identical to before.
3. **`scripts/momentum/daily.bat`**: stop-enforcement moved OUT of the PASS branch - it now runs
   unconditionally after the coverage check (which still sets the `%OPS_COV%` ops stamp), invoking
   both overlays with `--settled`. Header comments updated; file verified pure ASCII (0 non-ASCII
   bytes, per the Appendix AS gotcha).

Semantics: on a pending evening the stop prices AND dates at the last settled day (typically T-1) -
consistent with the sim's close-based `last_close_on_or_before` convention, and the sale lands
before that day is catch-up-marked (stops still run before `mtm_catchup` in the flow). When today
has settled by 17:15, behavior is what the PASS branch always intended: stop off today's close.
`TradingMorningMTM` (Appendix BY) remains trade-free - stops stay on the evening cadence, exactly
as decided there. This IS a deliberate live-experiment behavior change (the designed stops become
real), approved by Evan this session; treatment-vs-control comparability is forward-consistent
since the design always specified daily invalidation stops - they were just never firing.

## BZ.3 Verification

- Dry-runs (no trades; both also confirmed no breach at the settled close):
  `llm_overlay_ops check-invalidation --settled --dry-run` -> "pricing stop as-of 2026-07-14 (last
  settled trading day)" + "no open position - nothing to check" (treatment is in cash).
  `sector_overlay_ops check-invalidation --settled --dry-run` -> as-of 2026-07-14; XLB $50.64 >
  $49.50, XLI $180.45 > $170.00, XLK $183.62 > $172.00 - all "holding". These are the first
  enforcement-path stop evaluations the experiment has ever produced.
- Frozen regression tests after the Python changes - actual output:
  momentum_v1/2023_Q4 +14.5547% (d=-0.0000pp, 70 trades), momentum_v1/2025_H1 +1.8792%
  (d=-0.0000pp, 156), momentum_v2/2023_Q4 +14.4062% (d=-0.0000pp, 38), momentum_v2/2025_H1
  +10.2194% (d=+0.0000pp, 87). All 4 OK.
  NOTE: `python -m pytest` fails (pytest not installed in the venv); the working runner is
  `.venv\Scripts\python.exe -m trading_bot.strategies.test_strategies` - the pytest form in the
  project CLAUDE.md is stale.
- Timing discipline: tonight's 17:15 `TradingDailyMTM` run was verified COMPLETE (log "Done.",
  27/27 sleeves PASS, stamp written 17:18) before `daily.bat` was edited - never edit a .bat that
  cmd may still be executing. First live run of the new path: **2026-07-16 17:15**.

Not committed yet (no commit instruction at time of writing). HANDOFF.md updated (automation +
LLM-experiment sections).

# Appendix CA - Stock-overlay stop check hardened: match the stop to the held ticker (cascade-log mispairing bug) (2026-07-15, ~20:20 local)

Follow-up spun off from the Appendix BZ work (flagged as a task chip, then executed with Evan's
explicit go — live-experiment code, so it was presented before applying).

## CA.1 The bug

`scripts/momentum/llm_overlay_ops.py` `cmd_check_invalidation` looked up the active stop with
`llm_overlay.latest_decision(as_of)` = `SELECT * FROM llm_overlay_log WHERE decision_date <= ?
ORDER BY decision_date DESC, id DESC LIMIT 1` - the newest row for ANY ticker. But the
always-invested cascade sleeve (`llm_cascade_top1_paper`) logs decisions for OTHER names into the
SAME `llm_overlay_log` table (e.g. 2026-07-07 has both a BE VETO row and a WDC BUY row). So the
held position's price could be checked against a DIFFERENT name's invalidation level:
- Hold BE (stop ~220), newest row is WDC BUY (stop 480) -> BE ~220 <= 480 -> spurious invalidation
  sell at a stop that isn't BE's.
- Reverse pairing silently disables the real stop.

The rebalance path was already hardened against exactly this via `decision_for_ticker` (see its
docstring, added when the cascade sleeve launched); the daily stop path was missed. The SECTOR
overlay never had the bug - `sector_overlay_ops.cmd_check_invalidation` already calls
`sector_overlay.latest_decision_for(pos["ticker"], as_of)`. Latent at time of fix: the stock
treatment sleeve (`llm_overlay_mom_roa_top1_paper`) is all-cash (DB-verified, Appendix BZ), so no
position has ever been mispaired and NO history needs repair.

## CA.2 The fix (2 files, no design change)

1. `trading_bot/strategies/llm_overlay.py`: added `latest_decision_for(ticker, as_of)` - a mirror
   of the trusted `sector_overlay.latest_decision_for`, querying `llm_overlay_log WHERE ticker = ?
   AND decision_date <= ? ORDER BY decision_date DESC, id DESC LIMIT 1`.
2. `scripts/momentum/llm_overlay_ops.py` `cmd_check_invalidation`: moved `pos = open_positions[0]`
   above the lookup and switched to `llm_overlay.latest_decision_for(pos["ticker"], as_of)`; the
   "no active invalidation level" log line now names the ticker. The `--settled` pricing path, the
   sell, and all other logging are unchanged. `latest_decision` is retained (unused by the ops CLI
   now, but part of the module's public surface).

## CA.3 Verification

- `llm_overlay_ops check-invalidation --settled --dry-run` -> "pricing stop as-of 2026-07-14" +
  "no open position - nothing to check" (unchanged; treatment is in cash, so the ticker-matched
  path isn't exercised live yet - it will be the first time the treatment holds a name).
- Frozen regression tests - actual output: momentum_v1/2023_Q4 +14.5547% (d=-0.0000pp, 70),
  momentum_v1/2025_H1 +1.8792% (d=-0.0000pp, 156), momentum_v2/2023_Q4 +14.4062% (d=-0.0000pp,
  38), momentum_v2/2025_H1 +10.2194% (d=+0.0000pp, 87). All 4 OK. (The momentum sim doesn't import
  the overlay path, so no movement was expected - run anyway per the hard rule.)

Not committed (no commit instruction). HANDOFF.md stock-overlay note updated.


# Appendix CB - Doc-hygiene pass: stale stop comments aligned to --settled enforcement, plus module/package navigation docstrings (2026-07-15, ~20:50 local)

Pure documentation session (two commits, zero logic change): closes out the doc drift left by the
concurrent stop-fix (Appendices BZ/CA, done in a separate session) and adds navigation docstrings at
Evan's request.

## CB.1 Stale stop-comments corrected (commit 3966985)

A post-compaction consistency check (two sessions had edited the live docs concurrently) confirmed
the git history was linear and HANDOFF/record were coherent - appendices BY->BZ->CA sequential,
BY's dormant-stops FINDING correctly superseded by BZ's FIX. But two spots still described the OLD
coverage-gated/dormant stop behavior that BZ replaced with unconditional nightly `--settled`
enforcement:
- `scripts/momentum/morning_refresh.bat` REM (lines 14-21): said stops were "currently dormant" and
  "would fire in a morning run" (implying NOT in the evening) - backwards after BZ. Rewrote to state
  the evening run now OWNS stop-enforcement and the morning task skips it so the same settled close
  is not evaluated twice in one day. Re-verified pure ASCII (0 non-ASCII bytes) per the .bat rule.
- `.claude/codebase-memory/architecture.md` line 12: daily.bat flow read `[stops if today settled]`
  -> corrected to `stops (unconditional, as-of last settled close; record BZ)`.
Comment/bin only, no Python. Committed local, then pushed (51acb79..3966985).

## CB.2 Navigation docstring pass (commit 4ed8efa)

Evan asked to "add more verbose comments to the codebase to make finding things easier" and to
"update the /graphify-windows." Pushed back on both premises before acting:
- There is NO `graphify-windows` skill (only `graphify` v0.8.50, already Windows-aware), and the
  graphify knowledge graph already auto-refreshes nightly inside daily.bat (root graph.json stamped
  today 17:17) - nothing to update.
- A blanket "verbose comments everywhere" pass would be a ~91-file diff, largely redundant (an `ast`
  audit showed 22/23 scripts/momentum and 61/68 trading_bot files ALREADY carry a module docstring,
  atop the graph + codebase-memory bins + HANDOFF), and it fights the surgical-changes standard
  while multiplying the exact stale-comment rot just fixed in CB.1. Evan approved the targeted
  alternative.

Executed: the `ast` audit found 10 files with NO module docstring (all empty package `__init__.py`)
and 5 real modules with a thin one-liner. Filled the 10 `__init__.py` with a one/two-line package-
purpose landmark (scripts/momentum = the live ops CLIs; research = offline experiments; warm = cache
warmers; the six trading_bot subpackages), and upgraded the 5 thin modules to house-style navigation
headers (purpose + entry points + related files + invariants): `trading_bot/config.py` (canonical DB
paths + calibrated fill-cost constants; flagged the retired Form-4 filter flags), `trading_bot/db.py`
(the SCHEMA map + why the paper_* tables are wipe-isolated from positions/portfolio_state),
`trading_bot/execution/portfolio.py` (backtest-vs-paper distinction, book-value-not-MTM invariant),
`trading_bot/reporting/compare.py`, and `scripts/momentum/research/run_sleeves_chain.py`. Every
header was written from reading the actual file (no invented behavior); the 123 already-good
docstrings were left untouched.

## CB.3 Verification

- `py_compile` on all 15 edited files: OK.
- Frozen regression tests - actual output: momentum_v1/2023_Q4 +14.5547% (d=-0.0000pp, 70),
  momentum_v1/2025_H1 +1.8792% (d=-0.0000pp, 156), momentum_v2/2023_Q4 +14.4062% (d=-0.0000pp, 38),
  momentum_v2/2025_H1 +10.2194% (d=+0.0000pp, 87). All 4 OK.
- git diff: 15 files, +68/-5, docstring-only. Committed local, then pushed (3966985..4ed8efa).

No strategy/data/automation reality shifted this session, so HANDOFF carries no new snapshot and was
not modified; the architecture.md bin edit shipped inline in CB.1. Aside: today (07-15) NAV is
correctly PENDING (4,385 closes < 5,000 floor) and self-heals via TradingMorningMTM ~07:45 tomorrow -
by design, not a regression (asked + answered this session).


# Appendix CC - Coverage gate validated LIVE: a mid-market morning_refresh run (2026-07-16 13:01) was correctly rejected, partial bar self-healed with no NAV contamination (2026-07-17, ~13:20 local)

An accidental live stress-test of the price-coverage gate (record BN/BQ), plus a logged process slip.
Recording because it is the FIRST real-world proof - previously only reasoned about - that the gate
rejects mid-market intraday data and that a partial bar self-heals without contaminating NAV.

## CC.1 What happened (and the slip)

Evan: "run morning_refresh.bat". I asserted it was ~20:55 on 07-15 based on a STALE `date` reading
from earlier in the session and flagged only the one-way NAV-marking risk. The batch actually ran at
**2026-07-16 13:01, mid-market** (close is 15:00 CDT) - exactly the manual-mid-market-refresh case
record BY cautions against. The slip was the stale timestamp, not the command; the command is
non-trading by design and the gate made it harmless, but the process error is logged here honestly:
re-read the clock, do not assert time from memory.

## CC.2 The gate held (run output, 2026-07-16 13:01-13:04)

- `mtm_catchup`: **marked=27** as-of 2026-07-15 (all sleeves healed on overnight-settled closes -
  e.g. residual_w5050 $106,213.86, mom_roa_6535 $94,401.30, spy_benchmark $104,740.16).
- `mtm_catchup`: **PENDING 2026-07-16: coverage 4337 < floor 5000 - leaving unmarked**. The feared
  outcome (locking today's NAV to 1pm intraday prices, permanently, since NAV is never rewritten)
  did NOT occur - the gate refused the partial day.
- `verify_run`: **PASS (27/27)**, settled<=2026-07-15, continuity clean across all sleeves.

## CC.3 Self-heal verified (probe 2026-07-17 13:18, read-only)

Loop closed with VERIFIED facts, not a prediction:
- price_cache: 07-16 now **5,190 closes** (was the 4,337 intraday partial) - the 07-16 5:15pm daily
  run overwrote the partial bar with the official settled closes. 07-15 = 5,190, both settled.
- paper_nav: **07-16 marked for all 27 sleeves**; 07-15 marked. 07-17 (today) = 2 closes, correctly
  PENDING/unmarked.
- Net: NO NAV was ever computed on the intraday partial (07-16 was unmarked until it settled), so no
  sacred history was touched; the transient bar left zero trace after the evening overwrite.

## CC.4 Significance

This is the first LIVE demonstration under real conditions that (a) the coverage floor rejects
mid-market intraday data even when a human/agent runs a refresh at the wrong time, and (b) an
unmarked partial day self-corrects on the next settled refresh with no NAV contamination. The gate's
design intent (record BN self-healing MTM; BQ paper_mtm coverage-gating) is now empirically confirmed,
not just argued. No fix needed and none made; nulling the (already-overwritten) partial bar would be
pure churn. Read-only probes only; nothing committed by the run itself.


# Appendix CD - Residual weight ladder extended to a 3-cadence experiment: 9 monthly points added + full 19-point WEEKLY and BIWEEKLY ladders, replay-seeded 05-01, live forward via TradingLadderRebalance (2026-07-17, ~14:10 local)

Extends the residual weight ladder (record BW) from 10 monthly sleeves into a full
3-CADENCE experiment: the same resid-momentum/ROA blend ladder rebalanced monthly,
weekly, and biweekly, to forward-test whether rebalance FREQUENCY changes where on
the blend ladder the edge lives. Evan-directed; scope confirmed via three decisions
(full 19-point ladder per cadence; first-trading-day-of-week schedule; scheduled
tasks built now).

## CD.1 What was added

- **Monthly ladder filled to 19** — added the low-residual end residual_w<MM><RR>_paper
  for MM/RR in 05/95, 10/90, 15/85, 20/80, 25/75, 30/70, 35/65, 40/60, 45/55 (the
  existing 10 were 50/50..95/05). Same 05-01/06-03/07-01 monthly rebalances as BW.
- **WEEKLY ladder (new, 19)** — residual_w<MM><RR>_wk_paper, rebalanced on the first
  settled trading day of each ISO week: 05-01, 05-04, 05-11, 05-18, 05-26, 06-01,
  06-08, 06-15, 06-22, 06-29, 07-06, 07-13 (12 dates, holiday-aware).
- **BIWEEKLY ladder (new, 19)** — residual_w<MM><RR>_2wk_paper, every other week from
  05-01: 05-01, 05-11, 05-26, 06-08, 06-22, 07-06 (6 dates).
- **47 new sleeves -> 74 total.** Each cadence panel benchmarks against the existing
  spy_benchmark_paper (05-01 buy-hold); buy-hold is cadence-independent, so one SPY
  series serves all three (no duplicate SPY sleeves).

## CD.2 How (code, all surgical + tested-on-copy-first)

- **seed_residual_cadence_ladder.py** (new) — generalizes the BW seeder to param-driven
  cadences with per-name SKIP-existing (the BW seeder REFUSED if any residual_w% existed,
  so it could not add to the family). Same deterministic interleaved 05-01 replay
  (rebalance -> MTM each settled day -> next rebalance); last_rebalanced_at set to the
  last replay date so mtm_catchup/verify treat forward days as live.
- **paper_rebalance._strategy_config** — strips a `_wk`/`_2wk` cadence marker before
  reading the 4 weight digits; the rank function is cadence-independent (only the
  rebalance SCHEDULE differs), so weekly/biweekly reuse the identical zcombo blend.
- **verify_run** — generic `residual_w*` position target = 50 (no 47 hardcoded entries).
- **dashboard/web.py** — the single ladder panel split into three (monthly/weekly/biweekly
  via `_ladder_cadence`), each with the shared dotted SPY line; residual labels generated
  (`resid MM/RR` + ` w`/` 2w` tag) instead of 57 dict entries.
- **Forward automation.** Monthly: 9 lines added to rebalance.bat. Weekly+biweekly: new
  **ladder_forward_rebalance.py** dispatcher — runs every evening, SELF-DETERMINES from the
  trading calendar whether today is a weekly (first trading day of its ISO week) and/or
  biweekly (that week is an even number of weeks after the 05-01 anchor, W18) rebalance
  day, and rebalances only the due sleeves (holiday- and parity-aware). ONE process =>
  weekly+biweekly run sequentially, never a concurrent factor_backtest. Wired to a new
  **TradingLadderRebalance** task (daily 7:00pm, AFTER the 5:15pm MTM and ~6:03pm monthly
  rebalance so no two rebalance processes overlap). First real fire: Monday 2026-07-20
  (W30 -> both weekly and biweekly due); tonight (Fri) is a correct no-op.

## CD.3 Verification (all real output)

- **Copy-first** (VACUUM INTO snapshot, 4.76 GB): seeded 47 -> `verify_run` PASS **74/74**;
  additive-integrity probe confirmed every EXISTING sleeve byte-identical copy-vs-live
  (seed touched only the 47 new names); 57/57 residual sleeves continuity/sanity OK.
- **Frozen tests 4/4 at d=+/-0.0000pp** (v1 2023_Q4 +14.5547%/70, 2025_H1 +1.8792%/156;
  v2 2023_Q4 +14.4062%/38, 2025_H1 +10.2194%/87) after all Python changes.
- **Live seed**: 47 sleeves in 6.5 min -> `verify_run` LIVE PASS **74/74**.
- **Dispatcher due-ness** validated across dated scenarios (Mon W29 weekly-only, Tue W29
  none, Mon W28 weekly+biweekly, Fri none).
- **Dashboard**: all three panels render with SPY lines and correct labels (browser-checked).
- Test copy deleted; TradingLadderRebalance registered (State Ready, next run 2026-07-17 7pm).

## CD.4 NAV snapshot (deterministic 05-01 -> 07-16 REPLAY, cached closes)

HONESTY (same as BW): these rows are deterministic SIMULATION on cached closes, NOT live
fills. Live forward begins after each cadence's last replay rebalance (monthly 07-01,
weekly 07-13, biweekly 07-06); the 05-01->07-13 segment is post-BU/BV-selection data (a
tiny mini-holdout). **Across ALL three cadences the LOW-residual / high-ROA end leads and
the high-residual end lags** — which INVERTS the BV in-backtest w80-90 plateau. This is
10-11 weeks of REPLAY noise (BW carried the same caveat when its 05-01->07-13 ranking
inverted the holdout); live forward data decides, and the cadence comparison only becomes
meaningful once the weekly/biweekly sleeves accumulate live rebalances.

**MONTHLY** (19 sleeves, NAV @ 2026-07-16):

| blend | NAV | since 05-01 |
|---|---|---|
| 05/95 | $108,263 | +8.26% |
| 10/90 | $107,203 | +7.20% |
| 35/65 | $106,488 | +6.49% |
| 20/80 | $105,874 | +5.87% |
| 30/70 | $105,426 | +5.43% |
| 25/75 | $105,394 | +5.39% |
| 15/85 | $104,889 | +4.89% |
| 55/45 | $104,241 | +4.24% |
| 40/60 | $104,171 | +4.17% |
| 45/55 | $104,130 | +4.13% |
| 50/50 | $103,940 | +3.94% |
| 60/40 | $103,839 | +3.84% |
| 85/15 | $102,779 | +2.78% |
| 95/05 | $102,155 | +2.16% |
| 65/35 | $101,885 | +1.89% |
| 90/10 | $100,756 | +0.76% |
| 75/25 | $100,529 | +0.53% |
| 80/20 | $100,459 | +0.46% |
| 70/30 | $99,989 | -0.01% |

**WEEKLY** (19 sleeves, NAV @ 2026-07-16):

| blend | NAV | since 05-01 |
|---|---|---|
| 05/95 | $107,265 | +7.27% |
| 20/80 | $106,928 | +6.93% |
| 30/70 | $106,367 | +6.37% |
| 20/80 | $106,309 | +6.31% |
| 10/90 | $105,768 | +5.77% |
| 10/90 | $105,503 | +5.50% |
| 35/65 | $105,492 | +5.49% |
| 15/85 | $105,401 | +5.40% |
| 15/85 | $105,368 | +5.37% |
| 30/70 | $105,146 | +5.15% |
| 25/75 | $104,564 | +4.56% |
| 35/65 | $104,275 | +4.27% |
| 25/75 | $104,096 | +4.10% |
| 40/60 | $103,721 | +3.72% |
| 45/55 | $103,610 | +3.61% |
| 50/50 | $103,556 | +3.56% |
| 40/60 | $103,182 | +3.18% |
| 05/95 | $102,903 | +2.90% |
| 45/55 | $102,342 | +2.34% |
| 50/50 | $102,045 | +2.05% |
| 55/45 | $101,507 | +1.51% |
| 55/45 | $101,268 | +1.27% |
| 95/05 | $101,045 | +1.04% |
| 60/40 | $100,682 | +0.68% |
| 60/40 | $100,217 | +0.22% |
| 80/20 | $100,185 | +0.18% |
| 75/25 | $99,547 | -0.45% |
| 90/10 | $99,304 | -0.70% |
| 85/15 | $99,274 | -0.73% |
| 95/05 | $99,272 | -0.73% |
| 65/35 | $99,085 | -0.92% |
| 90/10 | $98,905 | -1.09% |
| 65/35 | $98,283 | -1.72% |
| 85/15 | $97,481 | -2.52% |
| 80/20 | $96,915 | -3.08% |
| 70/30 | $96,631 | -3.37% |
| 75/25 | $96,215 | -3.79% |
| 70/30 | $95,432 | -4.57% |

**BIWEEKLY** (19 sleeves, NAV @ 2026-07-16):

| blend | NAV | since 05-01 |
|---|---|---|
| 05/95 | $107,265 | +7.27% |
| 20/80 | $106,928 | +6.93% |
| 10/90 | $105,768 | +5.77% |
| 35/65 | $105,492 | +5.49% |
| 15/85 | $105,368 | +5.37% |
| 30/70 | $105,146 | +5.15% |
| 25/75 | $104,096 | +4.10% |
| 40/60 | $103,721 | +3.72% |
| 45/55 | $103,610 | +3.61% |
| 50/50 | $102,045 | +2.05% |
| 55/45 | $101,268 | +1.27% |
| 60/40 | $100,682 | +0.68% |
| 95/05 | $99,272 | -0.73% |
| 65/35 | $99,085 | -0.92% |
| 90/10 | $98,905 | -1.09% |
| 85/15 | $97,481 | -2.52% |
| 80/20 | $96,915 | -3.08% |
| 75/25 | $96,215 | -3.79% |
| 70/30 | $95,432 | -4.57% |


# Appendix CE - Nasdaq-100 (QQQ) added as a second index control: two buy-hold benchmark sleeves + dotted line on every Overview panel (2026-07-17, ~14:30 local)

Evan: "throw in QQQ on all the graphs as another control point" (same prompt also asked for
biweekly on its own graph with SPY - that was ALREADY live from Appendix CD's 3-panel split,
re-verified in the browser; no change needed there).

## CE.1 What

Two REAL buy-hold benchmark sleeves, mirroring the established spy_benchmark pattern exactly
(a real sleeve flows into every panel/table and is verified/MTM'd like everything else, no
special-case chart code):
- `qqq_benchmark_paper` - $100k of QQQ at the 2026-05-01 close (148.334935 sh @ 674.15).
  NAV @ 2026-07-16 $104,715.56 (+4.72%) vs SPY control +5.40% over the same window.
- `qqq_benchmark_0701_paper` - $100k at the 2026-07-01 close (137.898703 sh @ 725.17).
  NAV @ 2026-07-16 $97,348.21 (-2.65%). NOT Alpaca-mirrored (unlike spy_benchmark_0701).
76 sleeves total. QQQ history was already in price_cache (dividend-unadjusted, refreshed
daily, coverage identical to SPY - verified before seeding); daily MTM is automatic
(mtm_catchup marks every sleeve).

## CE.2 How

- `seed_spy_benchmark.py` generalized with a `--ticker` arg (default SPY - existing behavior
  unchanged); QQQ sleeves seeded with it. Tested on a fresh VACUUM INTO copy FIRST (both
  sleeves seeded, verify_run PASS 76/76 on the copy), then live (identical numbers -
  deterministic replay on the same cached closes; live verify PASS 76/76, recon $0.00).
- `verify_run.py` POSITION_TARGETS: qqq entries (1 each).
- `dashboard/web.py`: QQQ labels ("Nasdaq-100 (control)" / "(07-01)"); benchmark line styling
  split - SPY dotted gray #94a3b8, QQQ dotted amber #d4a017; the ladder panels' shared
  benchmark append now includes both 05-01 controls (buy-hold = cadence-independent, one
  series serves all three cadences); QQQ excluded from Top movers + Concentration alongside
  SPY (benchmarks, not stock picks).

## CE.3 Verification

- Browser-checked: Nasdaq-100 line renders on ALL 5 Overview panels (Original, 7/1 cohort,
  monthly/weekly/biweekly ladders); absent from Top movers/Concentration.
- verify_run LIVE: PASS 76/76.
- Frozen tests 4/4 at d=+/-0.0000pp (v1 +14.5547%/70 & +1.8792%/156, v2 +14.4062%/38 &
  +10.2194%/87).
- Test copy deleted after use.


# Appendix CF - QQQ follow-ups: alpha-vs-QQQ column + QQQ row highlight in the cohort tables, and the 07-01 cohort QQQ control re-seeded to its real 07-06 start (2026-07-17, ~14:45 local)

Three follow-ups to the QQQ control added in Appendix CE, all Evan-directed.

## CF.1 QQQ cohort control re-seeded 07-01 -> 07-06 (renamed)

The "7/1 cohort" actually deployed on the 2026-07-06 close: `spy_benchmark_0701_paper` and all the
`_0701` sleeves have inception/first-NAV 07-06 despite the `_0701` name. But CE seeded the QQQ
cohort control at 07-01, so its line started 5 days early and pulled the cohort panel's x-axis back
to Jul 1. Fixed by re-seeding at the cohort's real start and renaming to match:
- **Deleted** `qqq_benchmark_0701_paper` (created same session in CE) via a guarded, scoped script:
  it enumerates only `paper_%` tables that have a `strategy_name` column (paper_portfolio /
  paper_positions / paper_nav), asserts exactly 1 portfolio row, deletes only that sleeve, and
  re-counts to 0 + confirms the total dropped 76->75. Live delete (the sleeve was created today, so
  fully reversible by re-seeding; the seed path itself is already proven live).
- **Re-seeded** `qqq_benchmark_0706_paper` via `seed_spy_benchmark --ticker QQQ --inception
  2026-07-06`: bought 138.347028 QQQ @ 722.82 on 07-06, MTM'd 9 trading days (07-06..07-16), NAV
  $97,664.70 (-2.34%) - a 9/9 window matching `spy_benchmark_0701`.
NOTE: the SPY cohort control keeps its `_0701` name (its history is not mine to rewrite); only the
new QQQ sleeve is renamed to the accurate `_0706`. So the two cohort controls now share the same
07-06 start but differ in name suffix - a deliberate, minor cosmetic mismatch.

## CF.2 alpha vs QQQ column (Overview cohort tables)

Added an "alpha vs QQQ" column beside the existing "alpha vs SPY" in every Overview cohort table
(`_render_cohort_panel`). `_spy_cache_closes()` generalized to `_index_cache_closes(ticker)` (cache-
based, no network); the overview builds both a SPY and a QQQ close series and computes
`s["alpha_qqq"] = sleeve_pct - qqq_return_since_inception` alongside the SPY alpha. Column gets the
same red/green + `{:+.2f}%` formatting.

## CF.3 QQQ row highlight (like SPY)

The cohort-table row styler (`_style`) and the NAV-charts control styler (`_hl_control`) now tint
`Nasdaq-100` benchmark rows AMBER (rgba(212,160,23,0.20)) just as `S&P 500` rows are tinted GRAY -
matching the dotted line colors, so QQQ reads as a benchmark, not a tradeable sleeve.

SCOPE NOTE: the SINGLE-SLEEVE view's SPY control box (a fixed 5-column metric row) was left as-is -
adding a QQQ box there needs a layout change beyond "alpha in the tables"; the alpha-vs-QQQ lives in
the cohort tables where alpha-vs-SPY already lived. Flagged for a follow-up if wanted.

## CF.4 Verification

- verify_run LIVE: PASS **76/76** (`qqq_benchmark_0706_paper` continuity 9/9, recon $0.00).
- Frozen tests 4/4 at d=+/-0.0000pp.
- Browser: the 7/1 cohort panel now shows "Nasdaq-100 (07-06)" and its x-axis starts Jul 6 (was
  Jul 1); all 5 Overview panels render, so the tables (with the new alpha-vs-QQQ column) build
  cleanly. Label + verify_run POSITION_TARGETS updated 0701 -> 0706.


# Appendix CG - Full-system audit (4 parallel Opus workers + automated pass): 16 findings, all fixed same-session - collision hardening, dashboard loopback + 37x speedup, monthly single-process dispatcher (2026-07-17, ~15:55 local)

Evan: "/audit ... do a full audit of the system" then "do all". Hybrid audit per the audit skill:
an automated pass (frozen tests, compileall, verify_run, .bat ASCII sweep, secret-scan) plus a
manual sweep fanned out to FOUR parallel Opus 4.8 workers (correctness/automation-chain, data
integrity via read-only queries, security/secrets/infra, performance/docs-drift), findings
reviewed and the crit/high claims independently re-verified before reporting. Result: 2 HIGH,
3 MED, 11 LOW; zero data corruption (3,448 NAV rows, 18 tables, PK/orphan/jump/position scans all
clean); secrets history scan 0 findings (alpaca_keys.env never committed). Evan approved "do all".

## CG.1 The two HIGHs

**H1 - Rebalance-writer collision window (audit F#1).** The monthly rebalance.bat (6:03pm start on
the 1st trading day) measured ~35-45 min - dominated by ~34 per-process preloads of the 37.4M-row
price cache at ~44s each - while the new TradingLadderRebalance fired at 7:00pm. On a month whose
first trading day is a MONDAY (2026-08-03, 2026-11-02) the ladder rebalances 38 sleeves, and two
writer processes on one WAL SQLite with NO busy_timeout means the loser dies instantly with
"database is locked" - mid-rebalance, non-atomic, and INVISIBLE to verify_run (an under-count
passes; recon recomputes from actual positions). Fixed three ways, belt-and-suspenders:
- `PRAGMA busy_timeout=30000` in db.py `_new_connection` (a colliding writer now waits, not dies);
- TradingLadderRebalance moved 7:00pm -> 8:30pm (re-imported task XML; schtasks /change hung on a
  credential prompt in the non-interactive session - XML re-create is the reliable path);
- root cause removed: NEW `scripts/momentum/monthly_rebalance.py` (audit F#3, Opus worker) - a
  single-process dispatcher replacing the 29 paper_rebalance + 30 paper_mtm --force per-process
  lines in rebalance.bat. Preload paid ONCE (~52s) instead of ~59x (~25 min saved); same sleeves,
  same args, same order (dry-run plan matched the .bat inventory 29/29 + 30/30 exactly); per-sleeve
  try/except (a failed sleeve logs + skips, exit nonzero at end); refuses to silently CREATE a
  missing sleeve (paper_rebalance would mint one at $100k/today - every real sleeve is seeded by
  replay, so auto-creation is always a bug); ladder names generated from the seeder's WEIGHTS so
  the rosters cannot drift. The LLM-overlay ops sections, alpaca_sync, seed, stamp and verify
  stay in rebalance.bat unchanged.

**H2 - Dashboard exposed to the LAN (audit F#2).** Streamlit's default bind is 0.0.0.0: netstat
showed `0.0.0.0:8501 LISTENING` and dashboard.log printed LAN + External URLs - the whole
DB-backed dashboard (NAVs, positions, LLM decision logs) readable by any LAN device, no auth.
Fixed: `--server.address 127.0.0.1` in dashboard.bat. The old listener survived `schtasks /end`
(detached process, and interestingly owned by a NON-venv system Python) - killed PID explicitly,
relaunched via the task, verified `127.0.0.1:8501 LISTENING` and the dashboard renders.

## CG.2 The rest (by audit finding number)

- **#4 (MED)** Overview render was 382 queries / ~9.7s - a correlated last-close subquery over the
  37.5M-row price_cache repeated per sleeve x76. Opus worker replaced it with one bulk
  `GROUP BY ticker` query (`_bulk_last_closes()`, ttl=60): measured **36.9x** (10.213s -> 0.277s),
  functional match 225/225 held tickers, zero divergence.
- **#5 (MED)** Holiday NAV rows: 6 pre-M3.5 sleeves carry 2026-06-19/07-03 rows (marked against
  ~200 stray closes, +/-0.02%); 70 sleeves do not -> cross-sleeve comparisons must JOIN ON
  nav_date. DOCUMENTED in the data bin; the 12 legacy rows are KEPT - "do all" was NOT read as a
  sacred-history delete order; say "delete the holiday rows" to remove them. No new ones possible
  (M3.5 settled-day gate).
- **#6 (LOW)** start_all.bat em-dash (the Appendix-AS silent-corruption byte class) -> ASCII hyphen.
- **#7 (LOW)** ladder_rebalance.bat now ends with its own `verify_run --mode daily` + errorlevel
  warning (was: first check a full day later).
- **#8 (LOW)** Biweekly parity switched from ISO-week-number parity to ordinal-weeks-since-
  2026-04-27 (ANCHOR_MONDAY). ISO parity breaks in 53-week years - 2026 is one - producing a
  one-time 3-week gap (12-21 -> 01-11); ordinal parity gives strict 14-day spacing (12-21 -> 01-04)
  and is provably identical on all seeded + near-term dates (computed: all 6 seed dates even;
  07-20 +12w, 08-03 +14w due). Dry-runs re-validated: 07-13 weekly-only, 07-06 both.
- **#9 (LOW)** All 8 dashboard sqlite connects now read-only URIs via a `_ro_uri()` helper
  (write attempt confirmed blocked).
- **#10 (LOW)** `_load_paper_state` ttl 10s -> 60s.
- **#11 (LOW)** Cadence seeder now refuses `--end` earlier than a cadence's last rebalance date
  (would have produced a future-rebalanced, continuity-gapped sleeve).
- **#12 (LOW)** `_strategy_config`: `_0701` strip anchored to the exact `_0701_paper` suffix
  (blind `.replace` could mangle future names), and residual blends must sum to 100 (integer
  check, raises on malformed names instead of trading them).
- **#13 (LOW)** Docs drift: HANDOFF/architecture "verify_run wired into monthly_auto.bat" corrected
  to rebalance.bat/ladder_rebalance.bat; HANDOFF's "9 rows + SPY" Overview description rewritten
  for the 76-sleeve cohort-panel reality; web.py module docstring rewritten (was Form-4-era).
- **#14 (LOW)** monthly_auto.bat relabeled DORMANT-by-design (it is the documented Option-B
  unattended path, BLOCKED-ON-EVAN on an API credential - NOT dead code, so kept); 0-byte stray
  `docs/double-hyphen` git rm'd. The "gitignore the generated HTML twins" idea was REJECTED: the
  commit hook deliberately regenerates + stages the record twin.
- **#15 (LOW)** requirements.txt: floors -> exact pins (httpx 0.28.1, numpy 2.4.4, pandas 3.0.2,
  plotly 6.7.0, rich 15.0.0, streamlit 1.57.0, yfinance 1.3.0) + the missing runtime deps added.
  yfinance pinned deliberately: a silent upgrade could change adjustment semantics vs the
  split-adjusted/dividend-UNadjusted cache convention.
- **#16 (LOW)** daily.bat graphify path -> %USERPROFILE% (username no longer hardcoded into the
  public repo going forward; history retains it, not worth a rewrite).
- Data-bin correction found during #5: there is NO paper_transactions table (18 tables inventoried;
  older docs claimed one) - data.md fixed.

## CG.3 Audit info items (no action)

AFJK genuinely fell -51.7% on 2026-07-09 (sustained, ratio 2.07 - real decline, not a split
artifact; the 07-06 cohort's mom sleeves entered 07-07 @ $26.15). spy_benchmark cash = -1.5e-11
(FP epsilon). SEC_USER_AGENT email is deliberate per SEC policy. Firewall-rule enumeration did not
complete - internet (vs LAN) reachability of the old 0.0.0.0 bind was never confirmed either way;
moot post-fix. Known pre-existing asymmetry kept: the QQQ benchmark sleeves (like
spy_benchmark_0701) are not in the rebalance-evening MTM set - they heal next morning via catchup.

## CG.4 Verification (final sweep, real output)

Frozen tests 4/4 d=+/-0.0000pp (run before AND after every python-touching fix; v1 +14.5547%/70 &
+1.8792%/156, v2 +14.4062%/38 & +10.2194%/87). compileall scripts+trading_bot clean. verify_run
daily PASS 76/76. ALL .bat files pure ASCII. netstat: 127.0.0.1:8501. schtasks: TradingLadderRebalance
Next Run 20:30, Ready. monthly_rebalance --dry-run exit 0 (plan 29+30, one preload). Dashboard
browser-verified rendering all 5 panels post-change. Dispatcher's first live fire: 2026-08-03.


# Appendix CH - Second full-system audit (5 parallel Opus workers): 2 CRITICALs found - the biweekly ladder had NEVER live-rebalanced, and price_cache never back-adjusts splits ($83k phantom loss across 48 sleeves) (2026-07-28, ~15:37 CDT)

Evan: "/audit ... do a full audit of the system", explicitly choosing a FULL fresh sweep over a
delta-since-CG scan when offered the choice. Then "1" = fix everything EXCEPT rewriting the closed-
position NAV history. Method as in CG but wider: an automated pass plus FIVE parallel Opus 4.8
workers (correctness/automation, data integrity, security/deps/infra, performance/docs-drift, and a
dead-code/orphan sweep). Every crit/high was independently re-verified by the reviewing model with
its own queries before being reported - two worker claims were downgraded on that re-check (below).

PROCESS NOTE / correction: the reviewing model opened by telling Evan the last audit was
"yesterday". It was 2026-07-17 - ELEVEN days earlier. The claim came from stale session context
instead of reading the clock; `date` was run immediately after and the error corrected in the same
reply. This is the second dated instance of asserting a time from memory (cf. Appendix CC) and is
recorded so the pattern stays visible: run `date` BEFORE any temporal claim, not after.

## CH.1 CRITICAL 1 - the biweekly ladder has never live-rebalanced

`ladder_forward_rebalance` decided due-ness as "is TODAY the first trading day of its ISO week."
That is a DAY-based test with no catch-up: if the 8:30pm task does not run that one evening, the
cycle is lost permanently. On 2026-07-20 (a real trading day - 5,190 closes) the task did not run,
and the miss was invisible because (a) `verify_run` checks NAV continuity and cash recon but nothing
about rebalance CADENCE, and (b) `ladder_rebalance.bat` ended with `verify_run`, so the task's exit
code was verify's PASS regardless of what the dispatcher did.

Evidence (read-only queries, this session):
- weekly arm entry_dates: ... 07-06, 07-13, [07-20 ABSENT], 07-27
- biweekly arm entry_dates: 05-01, 05-11, 05-26, 06-08, 06-22, 07-06, then NOTHING
- all 19 `_2wk` sleeves still carry `last_rebalanced_at = 2026-07-06T00:00:00+00:00`, the midnight
  REPLAY stamp format written by the seeder - not a live wall-clock stamp (the `_wk` arm shows
  `2026-07-28T01:31:38.392397+00:00`).

So the biweekly leg of the 3-cadence experiment has been buy-and-hold since inception while
HANDOFF described it as a live 14-day-cadence forward test. 22 days.

FIXED - due-ness is now PERIOD-based and self-healing: "has this cadence traded yet inside its
current period?" (period = this calendar week's Monday for weekly; the current two-week block's
Monday for biweekly, anchored ordinal-even from 2026-04-27). A missed evening is picked up by the
next trading day in the same period. Also fixed in the same edit:
- per-sleeve try/except + failure list, and a nonzero return - previously EVERY path returned 0 and
  one raising sleeve aborted the whole ladder mid-run (`monthly_rebalance` already did this right);
- `ladder_rebalance.bat` now captures both exit codes and propagates them, so a ladder failure can
  no longer be masked by verify_run's PASS;
- a latent bug found while fixing, NOT in the audit findings: the old per-sleeve "already rebalanced
  today" guard compared `last_rebalanced_at[:10]` to the as-of date, but `paper_trader.py:179`
  stamps that column with write-time UTC. An 8:30pm CDT run stamps the NEXT UTC day, so the guard
  silently never matched and could not have prevented a double-rebalance. The new code derives the
  cadence's last activity from `paper_positions` entry/exit dates, which are true as-of dates and
  timezone-proof.

Verified by a 7-case assert self-check (scratchpad `check_cadence_logic.py`): seeded biweekly dates
map to 5 distinct blocks 14d apart; 50 block starts over ~2 years all exactly 14 days apart
(including the 2026 53-week boundary that CG fixed); the 07-20 miss now self-heals on 07-21; no
re-fire once a period is served; holiday-Monday still served on Tuesday.

CONSEQUENCE FLAGGED TO EVAN, DECISION PENDING AT TIME OF WRITING: under the new rule the biweekly
arm is DUE at the next 8:30pm run (it still owes the 07-20 block), i.e. 19 sleeves would rebalance
that evening. Options put to him: (1) let it fire and catch up, accepting one short 6-day interval
before 08-03 restores clean 14-day spacing, or (2) gate it to 08-03 for clean block alignment at the
cost of a 28-day gap. Recommendation given: (1).

## CH.2 CRITICAL 2 - price_cache never back-adjusts corporate actions

The KLAC 10:1 split (2026-05-13) was applied FORWARD ONLY. Cached history still reads $1,811.35 on
05-12 and $184.97 on 05-13. The 2026-06-12 repair (Appendix X) and the 2026-06-13 backfill fixed
SLEEVES, never the CACHE - so when the 3-cadence ladder was seeded on 2026-07-17 backdated to
05-01, it re-read the still-unadjusted history and reproduced the bug verbatim in 48 new sleeves.

Same ticker, same entry date, booked two opposite ways:
- 48 `residual_w*` sleeves: entry $1,727.12 (pre-split), 32 closed -> realized **-$53,215.70**
- `residual_roa_6535_paper` (repaired in June): entry $172.71 -> realized **+$1,079.84**
- ratio of the two entry prices: **10.0000** exactly

Aggregate phantom loss 48 sleeves: realized -$53,215.70 + unrealized -$29,965.11 = **-$83,180.81**.
Per sleeve that is about -1.8% to -1.9% of NAV, against a total ladder return spread of 11.43pp -
and it is NOT a common-mode offset that cancels in the comparison: it lands on different sleeves at
different exit dates (32 closed, 16 still open), so it differentially distorts the very rung-vs-rung
comparison the ladder exists to make. Also found: QDMI (ratio 0.372) cost one position -$1,769.62.

NOT FIXED THIS SESSION - deliberately. Repairing the 32 CLOSED positions means rewriting NAV history
that CLAUDE.md calls sacred, which Evan explicitly excluded from his "fix everything" approval. A
wrinkle surfaced while planning the mechanics and was put back to him: repairing the 16 OPEN rows
without also re-MTM-ing the contaminated days produces a NAV discontinuity (~+$1,800/sleeve with no
market move behind it), so open and closed are not cleanly separable. Three options were presented -
(a) repair + re-MTM (rewrites history), (b) repair + leave history (honest ledger forward, one
disclosed dated jump), (c) cache-only fix (nothing retroactive). Recommendation given: (b).
DECISION PENDING. The cache-level root cause (no back-adjustment pass at all) is what must actually
be broken to stop this recurring a third time.

## CH.3 The rest - fixed and verified this session

- **TradingWeeklyBackup dead 19 days (HIGH).** `Last Result -2147020576` (0x800710E0, "operator or
  administrator has refused the request"); `var/backups/` held exactly one file, `trades_2026-07-09.db`;
  `backup.log` was still untruncated from 07-09, proving cmd.exe never even launched on 07-12, 07-19
  or 07-26. Cause: `DisallowStartIfOnBatteries` + `StopIfGoingOnBatteries` both true. FIXED via
  Set-ScheduledTask (both false, plus `StartWhenAvailable` true so a missed Sunday now catches up).
  Ran it: 4.77 GB written in 26s, 2 generations retained. This was done FIRST, before any DB write,
  so a restore point existed - the 5 GB DB had had none for 19 days.
- **price_cache had no date-usable index (HIGH).** Only the PK autoindex (ticker, kind, key_date), so
  every date query full-scanned 37.5M rows. Measured on a full-size COPY (never live): GROUP BY
  8.258s -> 0.005s, count-for-one-date 4.415s -> 0.001s, range 9.170s -> 0.016s, results byte-
  identical, build 16.2s, +308 MB. Shipped as a documented reversible migration,
  `scripts/add_price_cache_date_index.py` (dry-run by default, `--execute` to apply). Live build
  14.7s; planner confirmed adopting it. End-to-end effect: the coverage gate went **7.1s -> 0.271s**.
- **daily_price_refresh could lose a 200-ticker batch and still exit 0** - now counts exhausted
  batches, logs the ticker count, and returns nonzero. Also routed through `trading_bot.db.connect()`,
  making it the last writer to pick up the `busy_timeout=30000` two-writer protection from CG.
- **check_coverage picked a stray-row day as its target** - one lone intraday ^VIX row for 07-28 made
  the gate report FAIL. `MIN_TRADING_DAY_COUNT` now guards target selection too; the gate now
  correctly evaluates 07-27 and reports PASS. (Consequence was benign - `daily.bat:28` routed exit 1
  to its today_pending branch - so this was downgraded from the worker's MED to LOW on re-check.)
- **seed_spy_benchmark rewrote the benchmark's ENTIRE NAV history every monthly run** (INSERT OR
  REPLACE over every cached close, called unconditionally by rebalance.bat) - now fills only dates
  with no existing nav row.
- **verify_run could not detect an under-filled sleeve** (it FAILed only on EXCEEDS, monthly-only) -
  now runs daily with a catastrophic-undershoot floor at 50% of target. Deliberately loose: mild
  undershoot is NORMAL here (live range 43-50 of 50) and is not a defect.
- **main.py re-introduced the LAN exposure CG had fixed** - `web-dashboard` built the Streamlit
  command with no `--server.address`, so it would have bound 0.0.0.0 again. Fixed. (Latent only; the
  live process was loopback, launched via dashboard.bat.) Also `init_db()` no longer fires on the two
  genuinely read-only subcommands.
- **13 modules opened the 5 GB DB read-write while only reading** - all converted to `?mode=ro`.
- Docs drift, all corrected: INDEX.md said "17 sleeves/3 families" (reality 76/4) - the first line a
  fresh session reads; `paper_transactions` referenced in 3 docs though no such table exists;
  CLAUDE.md's frozen-test command was `-m pytest ...` which CANNOT RUN (pytest is not installed) and
  is now the module invocation; CLAUDE.md listed 2 of 6 scheduled tasks; HANDOFF's "all 10
  rebalance.bat paper lines" predates the CG dispatcher; `memory/...` paths that do not resolve from
  the repo; dependencies.md claimed an alpaca SDK the code explicitly refuses. PRD_ROADMAP.md handled
  per Evan's convention - 12 dated strike-throughs, 7 criteria ticked, ZERO net deletions (verified
  by diff). Three criteria deliberately left unticked with in-file reasons rather than claimed done.
- Misc: `start_all.bat` printed "ALL UP" unconditionally (now branches on errorlevel);
  `watch_record_html.bat` claimed a `TradingRecordWatch` task that does not exist; two live strings
  pointed at module paths that would raise ModuleNotFoundError; `markdown`/`watchdog` added to
  requirements.txt.

## CH.4 Reported, deliberately NOT actioned

- **HIGH - phantom momentum in live selection.** Five non-reverting step-changes (ALIT 19.6x, MQ
  3.85x, DD 3.05x, QDMI 0.372) entered the 12-1 lookback and each name was bought on the first
  rebalance after. `MAX_HIST_RATIO` catches historical-much-greater-than-current; this is the
  reverse and no filter covers it. Entry prices are post-event and correct, so the corruption is in
  RANKING, not P&L. Causation was NOT proven - that needs a re-ranked backtest, which the audit was
  not permitted to run. Reported as mechanism-consistent, not as established fact.
- **alpaca_keys.env is readable by every local account** (`BUILTIN\Users: ReadAndExecute`,
  `Authenticated Users: Modify`, inherited). Contents never read. NOT changed by Claude - modifying
  OS security settings is outside what Claude does unilaterally; the `icacls` command was handed to
  Evan to run himself.
- **Undocumented scheduled task `\llm rebal`** - fires 5:59pm on 2026-08-01, one minute before the
  real rebalance, running a `user32.dll mouse_event` PowerShell one-liner. Reads as a deliberate
  keep-awake shim but appears in no repo doc. A second claimed task `\hellohello` could NOT be
  confirmed and is recorded as unverified rather than asserted.
- **12 legacy holiday NAV rows** - state re-confirmed unchanged from CG (exactly 12 rows, the same 6
  sleeves, the same 2 dates, none new). Still kept; still Evan's call.
- Dead code inventory produced (checkpoint: `scripts/check_june.py` has zero references anywhere;
  the whole `scripts/momentum/warm/` package is a dead cluster; `test_inception_guard.py` never runs
  automatically). NOTHING deleted - reported only, per the standing rule.

## CH.5 Verification (real output)

Frozen tests run THREE times - before the sweep, after all code edits, and again after the live index
build - 4/4 d=+/-0.0000pp every time (v1 +14.5547%/70 & +1.8792%/156, v2 +14.4062%/38 &
+10.2194%/87). compileall over scripts+trading_bot+main.py exit 0. `verify_run --mode daily` PASS
76/76 both before and after. Coverage gate 7.1s -> 0.271s. `PRAGMA quick_check` = ok,
`foreign_key_check` = no violations, 0 NAV gaps across all 76 sleeves, 0 pre-inception rows, cash
drift <= $1e-10, 0 orphans. Secret-scan over all 79 commits: 0 findings; alpaca_keys.env untracked
and ignored. All .bat files re-confirmed pure ASCII. 37 files changed, +393/-175.


# Appendix CI - Two trading days of prices silently lost to a yfinance rate limit: the CH refresh fix had a hole (empty frame != exception), now closed; biweekly ladder catch-up CONFIRMED fired (2026-08-02, ~16:15 CDT)

Evan, from the dashboard: "Prices through 2026-07-29 / 3246 stale holdings". Then "fix stale
holdings". Investigation, repair, and a follow-up fix to the gap that let it happen silently.

## CI.1 What was wrong

TWO independent causes stacked:
1. **The machine was powered off** from ~2026-07-30 to 2026-08-02 15:31 (TradingDashboard is an
   AtLogon task and its last run was 15:31 today, i.e. this boot). TradingDailyMTM last ran 07-29
   17:15, TradingMorningMTM 07-30 07:45. Nothing ran across 07-31 / 08-01 / 08-02.
2. **yfinance was rate-limiting**: `YFRateLimitError('Too Many Requests')` on nearly every batch.
   This is the part that mattered, because it did NOT surface as an error.

Result: `price_cache` ended at 2026-07-29 (5,176 closes), with 07-30 holding 3 stray rows and
07-31 entirely absent - both real trading days. 239 held tickers were pinned to the 07-29 close;
the dashboard's stale counter (which counts POSITION ROWS across 76 sleeves, not unique tickers)
read 3,246.

## CI.2 The hole in yesterday's fix - honest accounting

Appendix CH shipped a fix for exactly this class ("daily_price_refresh could lose a 200-ticker
batch and still exit 0"). It did not catch this case. The fix counted batches that exhausted all 3
retries **with an exception**; but yfinance swallows `YFRateLimitError` internally and returns an
**empty DataFrame** rather than raising, and the code classified an empty frame as a legitimate
"no bars in range". So the run printed `Done. 104170 rows upserted` and exited **0** while ~200
tickers per batch silently failed. A fix that addressed the symptom's shape but not its actual
failure mode.

CLOSED this session. `_process_batch` now also records wholly-EMPTY batches, and `main()`
disambiguates using whole-run context: empty batches only mean failure when OTHER batches in the
same run returned rows (on a weekend or holiday every batch is legitimately empty, and that must
stay exit 0 or the morning task would fail every Saturday).

The threshold is deliberate and was chosen against a real blast radius: `rebalance.bat:18`
HARD-ABORTS the monthly rebalance on errorlevel 1, and partial same-day publication (~4,400 of
~5,200 closes at 17:33) is NORMAL on a rebalance day. But normal partial publication shows up as
fewer rows PER TICKER, never as wholly-empty batches - so requiring
`EMPTY_BATCH_FAIL_FRACTION = 0.10` of batches to come back empty catches a real rate limit
(today: 6 of 30 = 20%) without letting an ordinary rebalance evening abort. Verified by a 4-case
self-check (scratchpad `check_ratelimit_fix.py`, no network/DB, VAR_DIR redirected):
all-empty/holiday -> 0; 6-of-30 empty with others succeeding -> 1 (was 0, the bug); 1-of-30 empty
-> 0 (rebalance not aborted); exception-lost batch -> 1 (unchanged contract).

## CI.3 The repair

Four spaced refresh passes were needed - the rate limit only clears with time, and hammering it
extends the block:

    07-31 closes:  0 -> 2,907 -> 4,461 -> 4,904 -> 5,049      (floor 5,000)

The coverage gate correctly held 07-30/07-31 as sub-floor PENDING through the first three passes -
the M3.5 guardrails behaved exactly as designed, refusing to MTM on partial data. After the fourth
pass `check_coverage` returned COVERAGE PASS (5,049 >= 5,000) and `mtm_catchup` marked **152 rows**
(76 sleeves x 07-30 + 07-31), `pending=none`. `verify_run --mode daily` -> **PASS (76/76)**.
237 of 239 held tickers now current to 07-31 (2 stragglers still at 07-29, below any gate).

## CI.4 The 9 verify failures from 07-29 - NOT the ladder fix

The 07-29 daily run had ended `verify=FAIL (67/76)`: 8 `_2wk` sleeves with a ~+$0.07 cash-recon
delta plus `llm_overlay_sector_top4_paper` at -$11.92. These first appeared 2026-07-29 07:47, the
morning AFTER the biweekly catch-up rebalance fired, so the CH ladder change was the prime suspect.
It was not: all 9 cleared to PASS 76/76 once complete prices landed and the NAVs were re-marked.
The cause was incomplete price data at mark time; the correlation with the rebalance was
circumstantial. Recorded because the suspicion was real and the exoneration should be too.

**Also CONFIRMED this session: the CH ladder fix worked.** 247 positions carry `entry_date =
2026-07-28` across the `_2wk` sleeves - the biweekly arm rebalanced on the 07-28 evening run, for
the first time since inception, exactly as the fix predicted it would.

## CI.5 PROCESS ERROR - a third instance, and this one changed a decision

Evan asked to run the monthly LLM-rebalance routine, whose Step 0 gate is "if
`rebalance_log.md`'s Last rebalance is in the CURRENT calendar month, STOP". The log reads
2026-07-01. The reviewing model asserted "today is 2026-07-28" **from stale session context
instead of running `date`**, concluded July == July, and stopped.

Today is 2026-08-02. July != August, so the gate actually PASSES and the model stopped for a
reason that was factually wrong. The outcome happened to be correct anyway - 08-02 is a Sunday
with no same-day close, which Step 2's data-integrity guardrail stops on - but by luck, not by
reasoning.

This is the THIRD dated instance of asserting a time from memory (Appendix CC, Appendix CH's own
process note, now this). The rule already exists in CLAUDE.md: run `date` BEFORE any temporal
claim. What is new here is the demonstration that the failure is not cosmetic - it can flip a
control-flow gate. NOTE: Appendix CH's own timestamp (2026-07-28 ~15:37 CDT) is CORRECT and was
briefly and wrongly said to need fixing; the audit really did run on 07-28 (its backup artifact is
`var/backups/trades_2026-07-28.db`, and the ladder fired that evening). Only the gate reasoning
used a stale date.

## CI.6 State + what is due next

Frozen tests 4/4 d=+/-0.0000pp after the refresh change. verify_run daily PASS 76/76. All 76
sleeves marked through 2026-07-31. Dashboard HTTP 200.

**2026-08-03 is a TRIPLE trigger day**: first trading day of August (monthly rebalance, needs the
LLM-decision routine), a Monday (weekly ladder), and an even ordinal block from ANCHOR_MONDAY
(biweekly ladder). Still OPEN and unresolved: the CH CRITICAL-2 KLAC repair (the
`backadjust_split` migration is written, copy-tested and idempotency-guarded, but its live
`--execute` was blocked by the permission classifier and is waiting on Evan), and the 32 closed
KLAC positions' phantom -$53,215.70, which remains in those sleeves' cash.


# Appendix CJ - KLAC split back-adjustment APPLIED: price_cache root cause fixed, 15 open positions re-based, frozen tests unmoved at d=0.0000pp; the 31 closed rows (-$55,343.70) deferred - compute_nav has no historical mode (2026-08-02, ~16:53 CDT)

Evan chose option (b) from the CH CRITICAL-2 menu (repair the cache + open positions, leave NAV
history), then authorised the 07-31 re-mark. He ran both live commands himself - the permission
classifier blocked Claude's `--execute` and the `paper_mtm --force` loop, and that block was
respected rather than routed around.

## CJ.1 What was applied

`scripts/backadjust_split.py --ticker KLAC --ratio 10 --effective 2026-05-13 --execute`:
- **4,327 price rows / 10** (close 4,115, next_open 106, next_open_range 106)
- **4,220 volume rows * 10** (volume 4,114, next_open_vol 106)
- untouched, correctly: atr_pct_20 (a percentage) and above_ma_50 (a boolean) - both scale-invariant
- **15 open positions re-based**: qty 1.230678 -> 12.306777, entry_price $1,727.1231 -> $172.7123,
  `entry_value` $2,125.53 PRESERVED (the Appendix X cost-basis invariant, which is what keeps the
  cash reconciliation at $0.00)
- guard fired correctly on the pre-run check: `cliff check: 9.793x across 2026-05-13 -- consistent
  with an un-adjusted 10:1 split`

**The cache cliff is gone.** Before: 05-12 $1,811.35 -> 05-13 $184.97. After: 05-11 $184.5190,
05-12 $181.1350, 05-13 $184.9710, 05-14 $189.2940 - a continuous series with an ordinary +2% day
where the 10x discontinuity used to be. The repaired entry price $172.7123 matches
`residual_roa_6535_paper`'s June-repaired basis to the digit, an independent consistency check.

**THE ROOT CAUSE IS NOW FIXED, not just its symptom.** Appendix X (06-12) and the 06-13 backfill
both repaired SLEEVES and left the cache unadjusted, which is precisely why seeding the ladder on
07-17 reproduced the bug in 48 new sleeves. A future split still needs this script run against it
(nothing detects splits automatically yet), but the tool now exists and is idempotency-guarded:
re-running refuses with "History looks ALREADY ADJUSTED", verified on the test copy.

## CJ.2 The frozen tests did not move - and that was the real risk

Back-adjusting rewrote 8,229 rows INSIDE both frozen-test windows (2023_Q4 and 2025_H1 are entirely
pre-split). The tests nonetheless returned **4/4 d=+/-0.0000pp**, exactly as predicted, for two
reasons that were reasoned out BEFORE the write rather than discovered after:
- momentum is ratio-based, and dividing every price in a window by the same 10 leaves every return
  identical;
- the script adjusts price AND volume together, so historical DOLLAR volume is invariant - verified
  on 5 sample dates spanning both windows, identical to the cent. Adjusting price alone would have
  cut dollar volume 10x and could have silently changed universe eligibility inside the frozen
  windows, which is the trap that would have forced a re-baseline.

## CJ.3 The disclosed discontinuity, and the 07-31 re-mark

Repairing the open positions made each affected sleeve's stored 07-31 NAV understate reality by
**+$2,024.93** (15 x $2,024.93 = $30,374, matching the audit's -$29,965 unrealized phantom figure).
`verify_run` immediately and correctly went to **FAIL (61/76)** - the recon check catching exactly
what it exists to catch.

Left alone that would have been a PERMANENT nightly failure, i.e. alarm fatigue on the one alarm
that matters - the same "nothing was watching" condition that let both CH criticals survive. So the
single latest settled day (2026-07-31) was re-marked for those 15 sleeves via `paper_mtm --force`.
The 05-01 -> 07-30 rows were NOT touched, so the corrective jump is visible and dated at
07-30 -> 07-31 rather than being smoothed away. Result: **verify_run PASS (76/76)**. The 15
sleeves' 07-31 NAV totals $1,575,678.39 (avg $105,045.23).

## CJ.4 What is NOT fixed, and the honest reason

The **31 closed positions carrying -$55,343.70** remain. (Scope correction found while surveying:
33 closed rows sit at the pre-split basis, but the 2 that exited 2026-05-11 bought AND sold before
the 05-13 split and are legitimately correct at +$276.56 - only the 31 that exited on/after 05-13
are corrupted. The count also grew 32 -> 33 between the 07-28 dry run and the 08-02 apply, as one
more position closed and took another -$1,851.44 into cash; that leak is now stopped, since the 15
surviving positions will close on a correct basis.)

Repairing them was offered as a simple third option. **It is not, and that framing was wrong.**
`paper_mtm.compute_nav` (:42-70) reads `pf.cash` - TODAY's cash - and `paper_trader.list_open()` -
CURRENTLY open positions. It has no historical mode at all. Re-marking the 1,881 affected
`paper_nav` rows with existing tooling would value today's positions at historical prices using
today's cash: garbage written over sacred history. Doing it correctly requires a historical-state
reconstructor - per-date position sets (derivable from entry/exit dates) and per-date CASH, which
can only be rebuilt by replaying every entry and exit, because there is NO `paper_transactions`
table (confirmed in the CG/CH audits). That is a build with its own copy-test and cash-recon proof,
not an extension of what exists.

Consequence to carry forward: **cross-rung ladder comparisons remain contaminated** by that
-$55,343.70, unevenly distributed across sleeves and exit dates. The unrealized half is fixed; the
realized half is not.

## CJ.5 Verification (real output)

Frozen tests 4/4 d=+/-0.0000pp AFTER the back-adjustment (v1 +14.5547%/70 & +1.8792%/156,
v2 +14.4062%/38 & +10.2194%/87). `verify_run --mode daily` FAIL 61/76 immediately post-repair
(expected, the discontinuity), then **PASS 76/76** after the 07-31 re-mark. Cache continuity
confirmed across 05-11..05-14. `alpaca_keys.env` ACL hardened by Evan
(`icacls /inheritance:r /grant:r`) - the audit's outstanding security item, now closed.

---

# Appendix CK - PRD M7.1 SHIPPED (historical_state.py, 76/76 exact); M7.2 gate FAILED at 94.48% - the cash ledger replays exactly but historical NAV is NOT reproducible because price_cache is deliberately mutable. STOP per the PRD; recommend M7.3-only (2026-08-02, ~17:23 CDT)

Evan: "run PRD task M7". M7 (added earlier the same day, record CJ) exists to repair the 31
CLOSED KLAC positions still holding -$55,343.70 of phantom realized loss inside their sleeves'
cash. Its first two tasks are read-only: build a historical-state reconstructor (M7.1), then
PROVE it against known-good history before letting it near contaminated history (M7.2).

M7.1 passed. **M7.2 failed its own gate, and the reason is more useful than the repair would
have been.** No DB write was made this session; nothing was repaired.

## CK.1 M7.1 - `scripts/momentum/historical_state.py` (read-only)

New module. `state_at(history, as_of)` returns `{cash, open_positions, n_open}` reconstructed
purely from `paper_positions` + `paper_portfolio`:

    cash(t) = starting_cash - SUM(entry_value where entry_date <= t)
                            + SUM(exit_value  where exit_date  <= t)
    open(t) = entry_date <= t AND (exit_date IS NULL OR exit_date > t)

Before writing it, the formula's premise was verified rather than assumed. `grep adjust_cash`
shows `paper_trader.adjust_cash` has NO caller outside `buy()`/`sell()`, nothing else writes
`paper_portfolio.cash`, and every `sell()` call site (7 of them across `paper_rebalance`,
`llm_overlay_ops`, `sector_overlay_ops`, `llm_cascade_ops`) passes the position's FULL `qty` -
so the cash credit is identically `exit_value`, never a partial. Schema sanity: 6,465 positions
(3,246 open / 3,219 closed), 0 closed rows with a null `exit_value` or `exit_date`, 0 open rows
carrying an `exit_date`, all 76 sleeves at `starting_cash` $100,000.

**Done-check (the PRD's own): PASS.**

    historical_state selfcheck  db=trades.db  as_of=2026-07-31  sleeves=76
    MAX |cash delta| across 76 sleeve(s): $0.000000
    RESULT: PASS (76/76 sleeves reconstruct exactly)

Open-position counts matched exactly on all 76. Zero sleeves had an entry or exit leg dated
after `as_of`, so the comparison is fully meaningful rather than accidentally clean.

## CK.2 M7.2 - the gate, and why it FAILED

Recomputed FULL NAV history for the **27 sleeves that never held KLAC** (their stored
`paper_nav` is known-good; any divergence is the reconstructor's fault, not the contamination's)
and diffed against the stored rows. `paper_nav` stores `cash` and `n_open_positions` per row
alongside `total_nav`, so the **ledger replay** and the **price resolution** were diffed
SEPARATELY - conflating them would have hidden which one was wrong.

    TOTAL: 1129/1195 rows within $0.01 (94.48%) across 27 sleeve(s)
    RESULT: FAIL (20/27 sleeves reproduce known history)

PRD bar was |delta| <= $0.01 on **>=95%** of rows. 94.48% misses it by 0.52pp. Per M7.2's own
wording - "If the reconstructor cannot reproduce known-good history, STOP and report" - this
session stops here.

**But the split diff says the reconstructor is not the problem:**

| axis | result |
|---|---|
| cash (ledger replay) | **1,194 / 1,195 rows exact = 99.92%** |
| n_open | 1,194 / 1,195 exact |
| total_nav (ledger + prices) | 1,129 / 1,195 = 94.48% |

## CK.3 Divergence class 1 - the single cash row (fully explained)

`llm_overlay_sector_top4_paper` @ 2026-07-28: stored cash $25,000.00 / 3 open, reconstructed
$48,818.14 / 2 open. Cause: the XLK **invalidation stop** (`exit_reason='invalidation'`,
`exit_date=2026-07-28`, `exit_value=$23,818.14`) - the ONLY non-rebalance exit in the entire DB.
`check-invalidation --settled` (record BZ) prices as-of the last SETTLED day and stamps
`exit_date` to it, but `daily.bat` writes the NAV row BEFORE running the stop check. So the
stored 07-28 row legitimately captures pre-exit state while the ledger books the exit on 07-28.

This is an **ordering artifact of the daily pipeline, not a data error and not a reconstructor
bug** - the reconstruction is arguably the more correct of the two. Per CLAUDE.md the stored row
stays as-is; it is reported, not fixed. It is also self-limiting: 1 row in 1,195, and it can only
ever affect a sleeve on the day a stop fires.

## CK.4 Divergence class 2 - historical NAV is NOT reproducible, by design

The other 65 divergent rows show cash exact, n_open exact, 0 carry-forwards, 0 missing prices.
With `nav = cash + SUM(qty x px)` and cash/qty/n_open all verified identical, the residual is
arithmetically FORCED to be `price_cache[ticker, date]` having changed since the row was written.
(`qty` is immutable here: the only script that mutates it is `backadjust_split.py`, scoped to a
single ticker, and these 27 sleeves never held KLAC.)

Confirmed from the code, not inferred: **`daily_price_refresh.py` re-downloads the last 30 days
for EVERY cached ticker with `INSERT OR REPLACE`** - deliberately, "tolerant of missed days
without needing complex gap detection". Every historical close inside a rolling 30-day window is
overwritten nightly with whatever yfinance currently serves.

The per-date deltas are blocky, not noisy - each block starts and ends at a rebalance boundary,
which is the signature of a held name being restated:

| block | sleeves | worst delta | matches |
|---|---|---|---|
| 05-15 -> 06-02 | mom_v1 | -$249.63 | 2026-06-13 history-gap backfill (2.25M rows) rewriting May |
| 06-15 -> 06-26 | all 3 | +$397.77 | same backfill + the 614 spike-nulls |
| 06-24 -> 06-25 | mom_roa_6535 | -$65.20 | same |
| 07-30 -> 07-31 | all 3 + ladder `_wk` | +$172.58 | **record CI, TODAY** - the yfinance rate limit dropped 07-30/07-31 for part of the universe; those names were marked on carry-forward and backfilled later |

Fingerprint confirming a shared-holding cause: mom_v1's 07-30 delta (+$86.29) is EXACTLY half
mom_v2's (+$172.58), and mom_v2's equals mom_roa_6535's to the cent - the top-100 vs top-50
slot-size ratio. 22 tickers held by all three carry a qty ratio of exactly 2.0000.

**The consequence, which the PRD did not anticipate:** a NAV row is a snapshot of a mutable
input. It cannot be reproduced once that input has been revised, and this system revises it
nightly by design. This is not fixable and not a bug - but it means **M7.4 as written would not
isolate the KLAC repair.** Re-marking ~1,881 rows with today's cache would silently restate them
for at least four unrelated reasons (the 06-13 backfill, the spike-nulls, nightly yfinance
revisions, and today's CI rate-limit backfill), and M7.5's "real before/after ladder numbers"
would be measuring all five effects at once while being reported as the KLAC fix.

Magnitude for scale: the largest unrelated restatement observed is +$397.77 on a $108k NAV
(0.37%), against the KLAC error's ~1.8% of NAV. Smaller, but the same order - not noise that
can be waved off.

## CK.5 Recommendation to Evan (his call, per the PRD)

**Do M7.3, skip M7.4.** Repair the 31 closed positions and the sleeves' CURRENT cash (the
$55,343.70), and leave the historical `paper_nav` rows alone. Rationale:

- It is exactly the precedent CJ already set for the 15 OPEN positions: fix present state, let
  the correction land as a visible dated jump, do not rewrite history.
- It makes cross-rung ladder comparison trustworthy **from the repair date forward**, which is
  the period that actually decides the experiment. HANDOFF already records the 05-01 -> 07-16
  replay as "10-11wk replay NOISE - live forward decides"; the historical spread was never the
  deciding evidence.
- It avoids rewriting 1,881 rows of sacred NAV history to achieve a restatement that would be
  provably impure.

Alternatives: (a) do nothing and permanently caveat the ladder - the PRD's stated cheap option,
now strictly worse than M7.3-only; (c) full M7.3+M7.4 as written - now known to conflate five
effects. Not recommended without Evan explicitly accepting that.

## CK.6 Verification (real output)

Frozen tests 4/4 **d=+/-0.0000pp** (run 2026-08-02 ~17:16 CDT, after `historical_state.py` was
created):

    [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
    [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
    [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
    [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)

    All regression tests passed.

No DB writes this session. Everything above ran against `file:...?mode=ro`. Work was done
between ~17:11 and ~17:23 CDT, which overlaps the 5:00-6:30pm MTM window the PRD says to avoid -
acceptable here ONLY because every query was read-only and short; a future M7.3 (which writes to
a copy) must respect the window.

---

# Appendix CL - PRD M7.3 PASSED ON A COPY: the 31 closed KLAC rows repair cleanly, cash reconciles at $0.00 on 76/76 sleeves, ladder spreads compress 1.4-2.8pp but no leader changes. Live apply BLOCKED-ON-EVAN. Separately: verify_run went FAIL 55/76 tonight from the CI backfill (2026-08-02, ~17:50 CDT)

Evan chose option 1 from the CK writeup: **do M7.3, skip M7.4** - repair the 31 closed positions
and the sleeves' CURRENT cash, leave the ~1,881 historical `paper_nav` rows alone. Executed
against a `VACUUM INTO` copy (5.08 GB, 87.8 s). **No live DB write was made.**

## CL.1 Three corrections to the numbers M7 was written with

The PRD and HANDOFF describe this repair with figures that do not survive contact with the DB.
All three were verified this session and the PRD/HANDOFF are corrected:

| stated | actual | why |
|---|---|---|
| "33 affected sleeves" | **31 sleeves** | 31 target rows, one per sleeve. The "33" appears to have counted the 2 legitimately-correct 05-11 exits' sleeves. |
| "repair the -$55,343.70" | cash moves **+$85,779.95** | -$55,343.71 is the phantom LOSS being removed. The true P&L on those 31 exits was a **+$30,436.24 GAIN**, so cash moves by the sum of both, not by the loss alone. |
| "15 open / 31 closed / 2 skipped = 48" | 16 open, 35 closed, **51 KLAC rows total** | 1 open + 2 closed were never contaminated (entered post-split at a correct basis) and are correctly untouched. |

A naive `entry_date < 2026-05-13 AND exit_date >= 2026-05-13` filter returns **33** rows, not 31.
The extra two entered before the split at a CORRECT price and must not be repaired. Only the
staleness self-guard (`entry_price > threshold`, threshold = first post-split close x sqrt(N) =
$584.93) selects the right 31. Anyone re-deriving this set without that guard will over-repair.

One of those two is `residual_roa_6535_paper` - the ORIGINAL sleeve, which booked its 05-01 KLAC
trade at the correct $172.71 while the 48 replay-seeded ladder sleeves booked $1,727.12 (exactly
the ratio-10 discrepancy record CJ identified). Its +$1,079.84 realized gain is real and was left
alone by the threshold guard, as designed.

## CL.2 The blocker M7.3 hit, and the fix

`backadjust_split.py` has an idempotency guard that refuses to run when the price cliff is gone
("History looks ALREADY ADJUSTED"). **Record CJ removed that cliff this morning.** So M7.3 as
written - "extend `backadjust_split.py` with `--include-closed`" - could never have run: the
script would abort before reaching the position repair.

Fix (surgical): the cliff guard now scopes to the **cache UPDATE** rather than the whole run. The
position repairs were always independently self-guarding (they touch nothing at or below
`threshold`), so skipping only the cache update is safe. The hard refusal is UNCHANGED on the
default path - it relaxes only under the new opt-in `--include-closed`. A second `--execute` is
therefore still incapable of dividing history by N twice.

## CL.3 What `--include-closed` does

For CLOSED rows entered before D at an un-adjusted price AND exited on/after D:
`qty * N`, `entry_price / N`, **`entry_value` PRESERVED** (the Appendix X cost-basis invariant),
`exit_value * N`, `realized_pnl = exit_value_new - entry_value`, and each sleeve's
`paper_portfolio.cash` corrected by `SUM(exit_value_new - exit_value_old)`.

`exit_price` is deliberately NOT touched: an exit on/after D was already priced post-split and is
correct. It was the SHARE COUNT that was wrong, so the exit PROCEEDS were understated N-fold.

**Beyond the PRD's list:** `realized_pnl_pct` is restated too. The PRD omitted it, but leaving it
at its pre-repair -89% beside a now-positive `realized_pnl` would be knowingly writing incoherent
data. It is recomputed as `(exit_value_new / entry_value - 1) * 100`.

`paper_nav` is NOT touched, under any flag - that is the whole point of choosing M7.3-only.

## CL.4 Done-checks (real output, on the copy)

Dry run correctly identified the state: cache SKIPPED (cliff 0.9793x, already adjusted),
0 open rows to repair (CJ did them), 31 closed rows across 31 sleeves, 2 skipped at +$276.56.

    realized_pnl total: $-55343.71 -> $+30436.24 | cash correction $+85779.95
    APPLIED: 0 price rows, 0 volume rows (cache SKIPPED (already adjusted)), 0 open +
             31 closed positions re-based (entry_value preserved), 31 sleeve cash
             correction(s) totalling $+85779.95.
    open positions still un-adjusted after repair: 0 (expect 0)
    closed positions still un-adjusted after repair: 0 (expect 0)
    closed rows failing realized_pnl == exit_value - entry_value or
      exit_value == qty * exit_price: 0 (expect 0)

**Done-check 1 - cash reconciles at $0.00 (the PRD's bar).** Using the M7.1 reconstructor, which
replays the position ledger independently of `paper_portfolio.cash`:

    historical_state selfcheck  db=m7_copy.db  as_of=2026-07-31  sleeves=76
    MAX |cash delta| across 76 sleeve(s): $0.000000
    RESULT: PASS (76/76 sleeves reconstruct exactly)

This is the strong check: the position edits and the cash correction are proven mutually
consistent, not merely each plausible. (Baseline before the repair: also PASS 76/76 - so the
repair preserved an invariant rather than accidentally restoring one.)

**Done-check 2 - realized_pnl plausibility.** All 31 repaired rows land at `entry_price`
$172.7123 (= 1727.123 / 10) with `exit_price` untouched in $175.56..$278.25, giving
`realized_pnl_pct` +1.65%..+61.11%, 0 rows internally incoherent. Cross-checked against KLAC's
actual adjusted price path - 05-01 $172.63, 05-18 $175.65, 06-03 $212.51, 06-22 $269.16,
07-28 $190.80 - every repaired P&L matches its own exit date's real price. Every one is a GAIN,
which is correct rather than suspicious: KLAC rose from $172 to a $269 June peak, so exits in
that window genuinely profited. That is precisely the gain the phantom loss was masking.

Frozen tests after the code change: **4/4 d=+/-0.0000pp** (v1 +14.5547%/70 & +1.8792%/156,
v2 +14.4062%/38 & +10.2194%/87).

## CL.5 Ladder impact - spreads compress, leaders do NOT change

NAV_after = latest stored NAV + that sleeve's cash correction. Exact, because closed positions
contribute nothing to `positions_value`; labelled a projection because it is arithmetic, not a
re-mark.

| cadence | n | affected | cross-rung spread BEFORE | AFTER | leader |
|---|---:|---:|---:|---:|---|
| WEEKLY | 19 | 10 | 10.56pp | **7.78pp** | w2080_wk -> unchanged |
| BIWEEKLY | 19 | 10 | 14.54pp | **12.93pp** | w0595_2wk -> unchanged |
| MONTHLY | 19 | 11 | 6.32pp | **4.93pp** | w0595 -> unchanged |

The distortion was real and material (1.4-2.8pp of spread, roughly a fifth to a quarter of it),
but **the qualitative read survives**: the low-residual/high-ROA end still leads all three
cadences, so the BV-plateau inversion noted in HANDOFF is not a KLAC artifact. Still a ~10-11
week replay window - live forward remains what decides it.

## CL.6 SEPARATE LIVE FINDING - tonight's daily run went FAIL 55/76

Unrelated to M7 and not caused by this session (no live writes were made). Found while checking
whether the DB was quiet enough to copy.

`var/last_daily_run.log`, 2026-08-02 17:18:52: `RESULT: FAIL (55/76 sleeves OK)`, banner
`VERIFY FAIL - daily run left a settled-history gap`. **That banner is misleading** - continuity
is 63/63 everywhere. The 21 failures are all **cash recon**, deltas +$195.18 .. +$234.40,
concentrated on the weekly ladder arm:

    [FAIL] residual_w9505_wk_paper  continuity(63/63) recon(delta $+233.46) preinc(0) pos(46/50)
             - cash recon: recomputed 101021.48 vs stored total_nav 100788.02 (delta +233.46)

Cause is exactly divergence class 2 from record CK, now surfacing live: the record CI rate-limit
backfill restored the 07-30/07-31 closes AFTER those NAV rows had been marked on carry-forward,
so the stored `total_nav` is stale against the now-complete cache. The magnitudes match the CK
measurements for the same sleeves (+$234.31 / +$231.49 / +$234.65 at 07-30) to within a day's drift.

**`mtm_catchup` will NOT heal this** - verified by reading it: it only marks days that are
MISSING for a sleeve, and these rows exist. Healing requires an explicit re-mark of 2026-07-31,
which is a rewrite of an existing NAV row and therefore Evan's call, not the model's.

## CL.7 M7.5 - live apply, BLOCKED-ON-EVAN

Unchanged from the PRD: Claude does not write to the live DB. Commands for Evan, in order:

    .venv\Scripts\python.exe -m scripts.backup_trades_db
    .venv\Scripts\python.exe -m scripts.backadjust_split --ticker KLAC --ratio 10 ^
        --effective 2026-05-13 --include-closed
    .venv\Scripts\python.exe -m scripts.backadjust_split --ticker KLAC --ratio 10 ^
        --effective 2026-05-13 --include-closed --execute
    .venv\Scripts\python.exe -m scripts.momentum.historical_state

Expect: dry run reports 31 closed / 31 sleeves / $+85,779.95; after `--execute`, the selfcheck
must print **PASS 76/76, max |cash delta| $0.000000**. If it does not, restore the backup.

Note that `verify_run --mode daily` will FAIL for the 31 repaired sleeves afterwards - their
latest NAV row predates the cash correction - on top of the 21 already failing from CL.6. Both
are cured by the same re-mark of 2026-07-31, which is a separate decision.

---

# Appendix CM - M7 CLOSED: KLAC repair applied LIVE by Evan, verify_run PASS 76/76, frozen d=+/-0.0000pp. The 2026-07-31 NAV re-mark also cured the CI rate-limit staleness. Ladder spreads compress to 7.58/12.93/4.93pp with NO leader change (2026-08-02, ~20:02 CDT)

The end of the KLAC saga that started with the 2026-06-12 split misapplication (Appendix X),
recurred through the 2026-07-17 ladder replay seeding (record CH), had its cache root cause fixed
this morning (record CJ), and is now fully repaired. **Evan ran every live command himself** -
Claude's live-DB writes are refused by the permission classifier (records CH/CJ), so this session
built and proved the tooling on a copy and handed over the commands.

## CM.1 What Evan ran, and what it did

    scripts.backup_trades_db                -> trades_2026-08-02.db (5.08 GB), 3 generations kept
    scripts.backadjust_split --ticker KLAC --ratio 10 --effective 2026-05-13 --include-closed
                                            -> dry run: 31 closed / 31 sleeves / $+85,779.95
    ... --execute                           -> APPLIED
    scripts.momentum.historical_state       -> PASS 76/76, MAX |cash delta| $0.000000
    scripts.data_audit.remark_nav_day --date 2026-07-31 --execute
                                            -> 41 changed, 35 already correct, 0 failures,
                                               net NAV delta $+88,298.92
    scripts.momentum.verify_run --mode daily -> **PASS (76/76 sleeves OK)**

The live dry run reproduced the copy-test numbers to the dollar ($-55,343.71 -> $+30,436.24,
cash $+85,779.95), which is the whole point of having tested on a `VACUUM INTO` copy first.

Frozen tests after all of it: **4/4 d=+/-0.0000pp** (v1 +14.5547%/70 & +1.8792%/156,
v2 +14.4062%/38 & +10.2194%/87).

## CM.2 The re-mark, and why it is NOT the M7.4 rewrite record CK rejected

New one-off: `scripts/data_audit/remark_nav_day.py` (dry-run by default), which re-marks ONE
already-existing `paper_nav` date for every sleeve, reusing `paper_mtm.compute_nav`/`write_nav`
and keeping the weekend, pre-inception and coverage guards. It exists because neither of the two
staleness sources self-heals: `mtm_catchup` only marks days that are MISSING (these rows existed),
and `paper_mtm --as-of` handles one sleeve per process launch.

The net $+88,298.92 decomposes exactly into the two known causes:

| cause | sleeves | amount |
|---|---:|---:|
| M7.3 KLAC cash correction (record CL) | 31 | $+85,779.95 |
| record CI rate-limit backfill restoring the 07-30/07-31 closes | ~10 | $+2,518.97 |
| already correct, left untouched | 35 | $0.00 |

**The distinction from M7.4 matters and is deliberate.** CK rejected re-marking ~1,881 rows
because `price_cache` is mutable by design (`daily_price_refresh` re-downloads 30 days nightly
with `INSERT OR REPLACE`), so a broad rewrite would silently restate history for UNNAMED price
revisions and then be reported as the KLAC fix. This re-mark touches **one** date, both of whose
staleness causes are named and dated, and the dry run enumerated every affected row with its
before/after value before anything was written. The 35 sleeves whose stored row already
reconciled were not rewritten at all.

That also closes the CL.6 finding (`TradingDailyMTM` FAIL 55/76 at 17:18) - it was the CI
backfill, and the same single re-mark cured it.

## CM.3 Ladder result - the honest before/after

Cross-rung spread of the residual weight ladder, measured from live `paper_nav` @ 2026-07-31,
BEFORE (pre-repair stored NAVs) and AFTER the full repair + re-mark:

| cadence | n | affected | spread BEFORE | spread AFTER | leader BEFORE | leader AFTER |
|---|---:|---:|---:|---:|---|---|
| WEEKLY | 19 | 10 | 10.56pp | **7.58pp** | w2080_wk | w2080_wk (+5.75%) |
| BIWEEKLY | 19 | 10 | 14.54pp | **12.93pp** | w0595_2wk | w0595_2wk (+7.60%) |
| MONTHLY | 19 | 11 | 6.32pp | **4.93pp** | w0595 | w0595 (+6.69%) |

The contamination was real and material - it inflated the apparent cross-rung spread by
1.4-3.0pp, roughly a fifth to a quarter of it. **But no cadence changes its leading rung**, so
the low-residual/high-ROA lead recorded in HANDOFF is NOT a KLAC artifact. (CL projected
7.78/12.93/4.93 from cash alone; the weekly arm came in 0.20pp lower because four `_wk` sleeves
also carried CI price staleness the projection did not model. Biweekly and monthly matched the
projection exactly.)

Standing caveat unchanged: this is still a ~10-11 week window that began as a REPLAY seed. Live
forward is what decides the ladder, not this spread.

## CM.4 M7 final status

- **M7.1** DONE - `historical_state.py`, exact on 76/76 sleeves.
- **M7.2** RAN, GATE FAILED at 94.48% - and the failure produced the milestone's most valuable
  finding: historical NAV is not reproducible in principle. Recorded in CK, not papered over.
- **M7.3** DONE - proved on a copy (CL), applied live (this entry).
- **M7.4** CORRECTLY NOT EXECUTED - blocked by the CK finding. The narrow single-day re-mark in
  CM.2 achieved the operational goal (`verify_run` PASS 76/76) without the 1,881-row rewrite.
- **M7.5** DONE - live `verify_run --mode daily` **PASS 76/76**, frozen d=+/-0.0000pp, this
  record entry, HANDOFF caveat removed, commit.

**M7 is closed.** Remaining open PRD work is M6 (slippage), still gated on Alpaca fills - the
2026-08-01 monthly rebalance was a Saturday, so the first live fire of `monthy-llm-rebalance`
under the current schedule is 2026-08-03.

## CM.5 Correction to CL.7

Appendix CL.7 printed the live-apply commands with `^` line continuations. That is cmd.exe
syntax; Evan's shell is PowerShell 5.1, where `^` is not a continuation and the commands would
have broken. The record is append-only so CL stands as written - the correct form is a single
line per command, as actually run and as shown in CM.1. Noted here so a future session copying
from CL does not inherit the bug.

# Appendix CN - The August monthly rebalance would have been SKIPPED: the live cron had drifted to day-1-of-month and 2026-08-01 was a Saturday. Restored to daily self-gating. The undocumented llm rebal jiggler decoded and hellohello confirmed real (2026-08-02, ~22:56 CDT)

A fresh session opened to do exactly what CM.4/CM.5 said to do next - watch the 2026-08-03
monthly rebalance and open M6 if it produced Alpaca fills. The orientation pass found that the
rebalance was never going to fire, and the doc that said it would (including CM itself, at
CM.4) was asserting a cron that had not been live for some time.

**Nothing was wrong with the data.** Independently re-verified at session start, before the
finding: live `verify_run --mode daily` **PASS (76/76 sleeves OK)** (2026-08-02 20:30, via
`TradingLadderRebalance`); frozen tests **4/4 d=+/-0.0000pp** (v1 +14.5547%/70 & +1.8792%/156,
v2 +14.4062%/38 & +10.2194%/87); `price_cache` complete through Fri 2026-07-31 at 5,165 closes
(07-30: 5,167), so the record CI rate-limit hole is fully backfilled and no trading day is
missing; `paper_nav` 76 sleeves x through 07-31; working tree clean at `134944e` == `origin/master`.

## CN.1 The finding

`mcp__scheduled-tasks__list_scheduled_tasks` reported, for `monthy-llm-rebalance`:

    cronExpression: "0 18 1 * *"        <- day 1 of the month ONLY
    schedule:       "At 06:00 PM, on day 1 of the month"
    nextRunAt:      2026-09-01T23:03:03Z
    enabled:        true

Three independent sources said it should be `0 18 * * *` (daily, self-gating):

| source | claim |
|---|---|
| `HANDOFF.md` (Monthly operations) | "cron `0 18 * * *`, ~6:03pm local ... self-gates on `rebalance_log.md`" |
| memory `monthly_rebalance_trigger_timing_bug.md` | "APPLIED 2026-07-11 with Evan's OK: shifted to `0 18 * * *`" (record BS) |
| the task's own `SKILL.md`:9 | "It fires **daily** at 5:30pm local ... every other day is a no-op via the gate below" |

The design *depends* on daily firing. The `rebalance_log.md` gate (SKILL.md Step 0) is what makes
it a monthly job: fire every evening, do real work only when the logged last-rebalance date is
from a prior month. A day-1-only cron removes the gate's whole reason to exist and replaces
"first TRADING day of the month" with "the 1st, trading day or not."

**2026-08-01 was a Saturday.** So:

- the 08-01 fire was a non-trading day (and the machine was off - see CN.3),
- `rebalance_log.md` still reads `Last rebalance: 2026-07-01`,
- the scheduler's own next fire was **2026-09-01**.

August's rebalance - 29 rebalance sleeves, every LLM overlay/cascade decision, and
`alpaca_sync --all --execute` - would simply not have happened. It would not have self-healed
either: 09-01 would have found a prior-month date in the gate and run, a full month late, with
August missing from the live record. And because `alpaca_sync --execute` is the only thing that
generates Alpaca fills, **PRD M6's gate would have stayed shut for another month** without
anyone knowing why.

`verify_run` cannot catch this. It checks NAV continuity, cash recon, position counts and
pre-inception rows. A sleeve that is never rebalanced has perfectly continuous NAV and perfectly
reconciled cash - it is just holding July's book. This is the same blind spot record CH found in
the biweekly ladder ("`verify_run` never caught it - it checks NAV continuity and cash, nothing
about cadence"), now recurring one layer up, at the scheduler.

## CN.2 Fix applied

`mcp__scheduled-tasks__update_scheduled_task(taskId="monthy-llm-rebalance",
cronExpression="0 18 * * *")` -> tool confirmed **"At 06:03 PM, every day."** (the ~3-min
deterministic dispatch jitter puts it at 6:03pm, matching what HANDOFF documents). Evan approved
the change explicitly before it was made; a scheduled-task edit is persistent configuration and
is not something the model does on its own initiative.

Verification honesty note: the confirming re-`list` call was refused by the permission
classifier. It was not worked around. The evidence that the change took is the update tool's own
returned confirmation string, and nothing stronger is claimed here. **A future session should
re-list and confirm `0 18 * * *` / `nextRunAt` on the next calendar day.**

Expected next behaviour: fires ~6:03pm daily; on 2026-08-03 the gate reads `2026-07-01` (prior
month) -> proceeds and does the real August rebalance; 08-04 onward reads `2026-08-03` (current
month) -> no-ops. 2026-08-03 is also the first live run of the `monthly_rebalance.py` dispatcher
and a Monday, which record CG flagged as a collision-risk month (1st trading day == Monday).

## CN.3 Why 08-01 was doubly lost: the machine was off

Independent of the cron, the machine was asleep or off from ~2026-07-29 evening until
**2026-08-02 ~15:39 CDT**. Evidence, all from `schtasks /query /v` last-run times plus the ops logs:

    TradingMorningMTM     Last Run 8/2 3:39:17 PM   (scheduled 7:45 AM)
    TradingWeeklyBackup   Last Run 8/2 3:39:17 PM   (scheduled Sun 9:00 AM)
    \llm rebal            Last Run 8/2 3:39:17 PM   (scheduled 1st, 5:59 PM)
    var/ops_status.log    ... 07-29, then jumps straight to 08-02

Every `StartWhenAvailable` task caught up in the same second, which is the signature of a wake,
not of five independent schedules. So even a correct `0 18 * * *` cron would have missed 08-01 -
but it would have caught 08-03. The cron is the load-bearing defect; the sleep is why there was
no second chance.

## CN.4 The undocumented `\llm rebal` task, decoded

Carried into this session as an open question ("reads as a deliberate keep-awake shim, but it's
in no repo doc"). It is a mouse jiggler:

    TaskName:   \llm rebal
    Task To Run: powershell.exe -command "(Add-Type '[DllImport(\"user32.dll\")]public static
                 extern void mouse_event(int a,int b,int c,int d,int e);' -Name u -PassThru)
                 ::mouse_event(1,0,0,0,0)"
    Next Run:   9/1/2026 5:59:00 PM
    Last Result: -2147020576

Two facts settle its purpose. Its schedule is **monthly on the 1st at 5:59 PM** - one minute
before an 18:00 fire, on the same day-of-month axis as the drifted `0 18 1 * *` cron. That is not
coincidence and it is not drift: **both were deliberately set to day-1**, by someone or some
earlier session, and the pair is internally consistent. The bug is the shared premise that
"day 1" and "first trading day" are the same thing.

And it does not work anyway. `-2147020576` is **0x800710E0** - the identical
`DisallowStartIfOnBatteries` / `StopIfGoingOnBatteries` error code that silently killed
`TradingWeeklyBackup` for 19 days (record CH). It returns before cmd/powershell ever launches.

**Deliberately NOT "fixed" this session, and this is a reversal of what this session first
offered.** Clearing its battery flags was proposed and Evan approved the plan that mentioned it;
on inspection the fix is close to worthless and was withdrawn rather than executed for the sake
of having done what was offered. Reasons: (a) with the cron restored to daily self-gating, a
day-1-only jiggler no longer guards anything - the rebalance day is now whatever the first
trading day is; (b) `mouse_event` prevents *idle sleep on an already-awake machine*, it cannot
wake a sleeping one, so it was never a defence against the CN.3 failure; (c) it is an
undocumented task nobody in the repo record created, and changing its behaviour on inference
about its purpose is worse than leaving it and documenting it, which is what this entry does.
The real exposure is "machine asleep at 6pm on the first trading day," and a jiggler is not the
control for that. Left enabled, unmodified, now on the record.

## CN.5 `\hellohello` confirmed real

Also carried in as unconfirmed ("I never confirmed the claimed `\hellohello` task exists"). It
exists - as a **Claude** scheduled task, not a Windows one, which is why a `schtasks` sweep would
never have found it:

    taskId: hellohello   description: "hello"   cron: 0 8 * * *   enabled: true

Harmless as far as its description goes, but it is live and firing daily at ~8:08am. Full Claude
task inventory found this session, for the record: `daily-trade-check` (`0 8 * * 1-5`),
`daily-trade-check-2` (`0 18 * * 1-5`), `monthy-llm-rebalance` (now `0 18 * * *`),
`cohort-0706-deploy` (disabled, one-time, last ran 07-07), `hellohello` (`0 8 * * *`).

**Flagged, not concluded:** `daily-trade-check-2` occupies `0 18 * * 1-5` - the same 6pm slot the
monthly rebalance now uses again. Whether the monthly was moved to day-1 to dodge that collision
is a hypothesis this session could not verify and is recorded as a hypothesis only. Both are
Claude agent tasks; if `daily-trade-check-2` only reads, there is no two-writer hazard, but that
was not audited here.

## CN.6 Two stale red flags that are NOT live failures

Both will mislead the next reader of the 08-03 run, so they are named here:

- `var/ops_status.log`'s last line reads `[OPS 2026-08-02] coverage=PASS verify=FAIL`. That is
  the 17:18 daily run from **before** the M7 repair (record CL.6). The 20:30 ladder run verified
  **PASS 76/76**, but `ladder_rebalance.bat` writes no ops stamp, so the tail of that file stays
  permanently misleading until the next `daily.bat`.
- `TradingDailyMTM`'s `Last Result` is `1` in Windows task history, same cause, same resolution.

Neither is a live failure. Per record CM's own warning: read the per-sleeve lines, not the banner.

## CN.7 Corrections to prior entries (append-only, so noted here)

- **CM.4** states "the first live fire of `monthy-llm-rebalance` under the current schedule is
  2026-08-03." False when written - the live cron at that moment was `0 18 1 * *` and the next
  fire was 2026-09-01. CM was reasoning from HANDOFF's documented cron, not from the scheduler.
- **memory `monthly_rebalance_trigger_timing_bug.md`** was titled RESOLVED and asserted a live
  cron of `0 18 * * *`. Updated this session. This is the **third** time this task's schedule has
  been found diverged from its documentation (`0 8 * * *` -> record AP; `30 17 * * *` -> record
  BS; `0 18 1 * *` -> here). The pattern is now strong enough to state as a standing rule:
  **read the cron from `list_scheduled_tasks`, never from a doc.** Any doc statement about this
  task's schedule is a claim about the past.

## CN.8 What this changes for 2026-08-03

Unchanged: do not run anything that trades. The rebalance is the scheduled task's job and Evan's.
The next session's job is still to read `var/last_daily_run.log`, `var/verify_report.log` and
`rebalance_log.md` after ~6:03pm and report what happened - but it should now expect the run to
occur, and should treat `rebalance_log.md` still reading `2026-07-01` on the morning of 08-04 as
a FAILURE signal, not as a no-op day.

M6 remains gated. If 08-03 produces Alpaca fills, the gate opens and M6.1
(`fetch_alpaca_fills.py`) starts. If it does not, the gate is still shut and the reason is now a
known one rather than a mystery.

# Appendix CO - verify_run gains check (e), rebalance cadence: a stale rebalance_log.md now FAILs loudly instead of passing silently. Closes the blind spot CN found (2026-08-02, ~23:37 CDT)

Direct follow-on to CN. The CN finding was not really "a cron drifted" - crons drift, that is
survivable. The finding was that **nothing in the system could tell you it had drifted.** A sleeve
that misses its rebalance keeps producing a perfect `verify_run` line forever: NAV continuity
unbroken, cash reconciled to the cent, position count on target, zero pre-inception rows. It is
just holding last month's book. Checks (a)-(d) are all state-consistency checks, and a stale
portfolio is perfectly self-consistent.

So the only reason CN was caught at all is that a human-directed session happened to read the
scheduler. That is not a control.

## CO.1 The check

`scripts/momentum/verify_run.py` gains **(e) rebalance cadence**, a run-level check (not
per-sleeve, so it sits after the sleeve loop):

> `rebalance_log.md`'s `Last rebalance:` date must be in the same calendar month as the last
> SETTLED trading day, **or later**.

Split into two functions so the logic is testable without I/O: `read_last_rebalance(path)` (the
file read, returns `None` rather than raising on a missing/unstamped file) and
`check_rebalance_cadence(logged, last_settled)` (pure).

The whole design rests on one observation that removes the need for a holiday calendar:
**`last_settled` falling in month M is itself proof that M's first trading day has passed.** So
there is no "is today the first trading day" computation anywhere - the settled-data frontier
already answers it. Two consequences that a naive "stamp month == current month" rule gets wrong,
both of which would have made the daily task red on ordinary evenings:

| situation | naive rule | (e) |
|---|---|---|
| 2026-08-02, settled 07-31, stamp 07-01 | FAIL (August has no stamp) | quiet - correct, August's first trading day has not happened |
| 08-03 6:03pm rebalance done, stamp 08-03, coverage not settled past 07-31 | FAIL (stamp is "ahead") | quiet - this is why the comparison is `>=`, not `==` |

## CO.2 Verification - four runs, all real output

**Unit** (`scripts/momentum/test_rebalance_cadence.py`, new, no DB/fixture/network):

    Running verify_run rebalance-cadence tests...
      [OK  ] read_last_rebalance: real format, unstamped file, missing file
      [OK  ] check_rebalance_cadence: 4 quiet cases, 3 fail cases
    All rebalance-cadence tests passed.

**FAIL path, end-to-end.** Rather than write a false FAIL into the live ops log to test this, the
run uses a schema-only fixture DB (4 tables, 0 rows) in the scratchpad. Zero rows means an empty
calendar, which means `last_settled` falls back to today (2026-08-02) - so the check runs against
the REAL, genuinely stale `rebalance_log.md` with no monkeypatching at all:

    === 2026-08-02 23:34 | verify_run mode=daily db=trades.db sleeves=0 calendar=none settled<=2026-08-02 ===
    [FAIL] (rebalance cadence)              last_rebalance(2026-07-01) settled_month(2026-08)
             - rebalance cadence: last rebalance 2026-07-01 predates the settled month 2026-08 -
               this month's monthly rebalance has NOT run (check the monthy-llm-rebalance cron, record CN)
    RESULT: FAIL (0/0 sleeves OK; rebalance cadence FAIL)
    exit=1

`verify_run` co-locates its report with the DB it describes, so that FAIL block landed in the
fixture directory. **`var/verify_report.log` was never touched by the failure test.**

**Live PASS** (read-only, live DB) - the check is correctly quiet today:

    [PASS] (rebalance cadence)              last_rebalance(2026-07-01) settled_month(2026-07)
    RESULT: PASS (76/76 sleeves OK)
    exit=0

**Frozen tests: 4/4 d=+/-0.0000pp** (v1 +14.5547%/70 & +1.8792%/156, v2 +14.4062%/38 &
+10.2194%/87).

## CO.3 Ordering, checked rather than assumed

The obvious way to get this wrong is a false FAIL fired by the project's own automation. Checked
in the batch files rather than reasoned about:

- `rebalance.bat` **stamps at line 123 and verifies at line 127** - stamp first. So the monthly
  run's own `--mode monthly` verify always sees a fresh stamp, including on a retry day. No change
  needed.
- `daily.bat` (5:15pm) and `morning_refresh.bat` (7:45am) can legitimately fire (e) before the
  6:03pm rebalance on the first trading day of a month - but only if that day's coverage has
  already SETTLED by then. Every weekday line in `var/ops_status.log` reads `coverage=PENDING`
  (the `PASS` lines are weekend runs, where the frontier is the previous Friday), so at 5:15pm on
  Monday 2026-08-03 `last_settled` will be Friday 07-31 -> month 2026-07 -> quiet.

**Residual window, stated rather than claimed impossible:** if a first-trading-day-of-month ever
settles before 5:15pm, that evening's daily task goes red for ~48 minutes until the 6:03pm
rebalance stamps. One evening, self-clearing, and it names its own cause in the log line. That is
an acceptable price for the check existing at all.

## CO.4 What it would have done

Given CN's actual timeline: 2026-08-04 07:45 (`TradingMorningMTM`), `last_settled` = 2026-08-03,
stamp = 2026-07-01 -> **FAIL**, with the cron named in the failure line. So the August miss would
have surfaced roughly 14 hours after it happened, in a log Evan already reads, instead of on
2026-09-01 or never. It does not prevent the miss - with the cron now restored to `0 18 * * *`
the following evening's fire is the actual repair - it makes the miss impossible to not notice.

Scope note: this is an ops guardrail on an existing verifier, consistent with the PRD's M3 theme
(unattended-automation safety). No strategy, factor, universe, sleeve or decision logic was
touched; no DB write of any kind.

---

# Appendix CP - August monthly rebalance EXECUTED: 12 LLM overlay and cascade decisions logged, all sleeves rebalanced, verify_run PASS 76/76, Alpaca paper 132 orders 0 rejects; first live monthly fire since the CN cron-drift fix (2026-08-03, ~18:25 CDT)

**WHAT.** The `monthy-llm-rebalance` scheduled task fired for August (first trading
day = Mon 2026-08-03; Aug 1 was a Saturday). Gate check: `rebalance_log.md` read
`Last rebalance: 2026-07-01` (prior month) → stale → proceeded. This is the first
live monthly rebalance since Appendix CN restored the cron from its day-1-only
drift, so it also confirms that fix works end-to-end.

Ran the runbook in order: `overlay_prep` (gather) → data-integrity guardrail →
12 LLM decisions (live web research) → `rebalance.bat` (execute) → verify. All
decisions and fills dated 2026-08-03.

**Data-integrity guardrail (passed).** Universe populated with real technicals as
of 2026-08-03; momentum sane (largest was ATEX 3m +92.9% / %>200DMA +113%, an
aggressive small-cap, nowhere near the >1000% split-artifact tell). Daily MTM had
already landed (17:17, verify PASS 76/76) so no two-writer overlap on `trades.db`
despite the run falling at ~18:15 (inside the 5-6:30pm MTM window — the 5:15pm
writer was long done).

**Macro backdrop (drove the sector risk-vetoes).** Live research: Fed held at
3.50-3.75%, market now pricing a ~63% chance of a SEPTEMBER HIKE (cuts fully
priced out); 10Y ~4.7%, near an 18-month high; Aug-2 tape showed rotation OUT of
tech/healthcare INTO cyclicals (XLY led +3.29%). Hawkish regime, rising long
yields.

**Decisions — STOCK overlay/cascade** (`llm_overlay_ops decide`, shared log; cash
overlay goes to cash on a veto, cascade walks the top-10 to the first BUY):
- MU  VETO (3, inval 800) - post-earnings unwind, -28%/30d from $1145 (Jun29) to ~$820, below 5/20/50 EMAs, RSI40, -10.6% last wk on memory-pricing buyer pushback. Cheap fwd P/E~12x but 1m-fwd setup broken.
- WDC VETO (4, inval 500) - Q4 earnings Aug5 = 2-day binary catalyst on a name below its 50DMA amid the memory/storage valuation correction. Veto on catalyst risk despite Citi/Wells PTs 800/730.
- VICR VETO (2, inval 195) - momentum rolling over hard: 1m -24.5%, 3m -20.4%, ~25% below 50DMA.
- BE  VETO (3, inval 200) - momentum blow-off unwinding: 1m -19.4%, 3m -24.9%, below 50DMA.
- STX BUY  (6, inval 730) - fresh Q4 beat-and-raise (EPS 5.71 vs 5.09, +12%) Jul28, +$100 post-earnings, Argus PT 900 / Barclays 1250, 25-analyst Strong Buy; HDD duopoly pricing power, catalyst behind it, 1m +1.3% recovering while peers fell. Below-50DMA the main caveat.

**Decisions — SECTOR overlay/cascade** (`sector_overlay_ops decide`; macro
RISK-veto; cascade needs 4 HOLD):
- XLK  VETO (4, inval 175) - below 50DMA, RSI43 fading; rotation out of tech, stretched valuations, hawkish-Fed pressure on long-duration growth. Fading + headwind.
- XLV  HOLD (7, inval 156) - above 50DMA, RSI60, -3% off highs; State Street upgraded healthcare to positive for Q3-2026, low-beta defensive fits the regime. Trending + macro-supported.
- XLE  HOLD (6, inval 56.50) - strongest 1m mover (+10.5%), above 50DMA, RSI61; cyclical-rotation beneficiary. Watch: Brent cut to ~$74 3Q26 (Iran/Hormuz de-escalation), soft into 2027. Momentum NOT fading.
- XLI  HOLD (6, inval 178) - above 50DMA, near highs; AI-datacenter + aerospace/defense demand, cyclical tailwind.
- XLB  VETO (3, inval 49) - below 5/20/50 EMAs, strongly bearish; hawkish-Fed/firm-USD headwind (cascade #5).
- XLRE VETO (3, inval 41) - most rate-sensitive sector into an 18-mo-high 10Y + Sept-hike risk; macro risk-veto despite a technical uptrend (cascade #6).
- XLU  HOLD (6, inval 44.50) - above 50DMA and 200DMA, RSI56; rate-proxy headwind offset by structural AI-datacenter power demand + defensive bid (cascade's 4th HOLD).

**Execution results (`rebalance.bat`, EXITCODE=0).**
- Dispatcher: 29 rebalance + 30 MTM sleeves, 0 failures, 43s.
- Stock control `mom_roa_top1_paper`: SELL BE, BUY MU (rotated to new #1).
- Stock overlay `llm_overlay_mom_roa_top1_paper`: VETO MU -> already CASH, no change.
- Stock cascade `llm_cascade_top1_paper`: pick=STX (first LLM-approved BUY) - SELL WDC, BUY STX.
- Sector overlay `llm_overlay_sector_top4_paper`: held XLE/XLI/XLV, XLK slot -> cash (1/4 cash).
- Sector cascade `llm_cascade_sector4_paper`: held XLV/XLE/XLI/XLU (all 4 HOLD-approved, 0 momentum-fill).
- Alpaca PAPER sync (`--all --execute`): residual_roa_6535_0701 submitted 62 / rejected 0; mom_roa_6535_0701 submitted 69 / rejected 0; spy_benchmark_0701 submitted 1 / rejected 0. Total 132 orders, 0 rejects.
- `rebalance_log.md` stamped 2026-08-03; verify_run --mode monthly RESULT: **PASS (76/76 sleeves OK)**, rebalance-cadence check now reads `last_rebalance(2026-08-03)`.

**WHY the vetoes clustered.** The entire memory/semis complex (MU/WDC/VICR/BE/INTC/
AAOI) is in a sharp valuation-driven unwind off June highs, so the stock overlay
correctly sat in cash and the cascade had to walk to #5 (STX) — the one name in
the top-10 with a fresh positive catalyst rather than a broken chart. On the
sector side the hawkish/rising-yield regime justified vetoing the two rate-proxy
laggards (XLB, XLRE) and tech (XLK, below its 50DMA), leaving a defensive+cyclical
HOLD set (XLV/XLE/XLI, plus XLU for the cascade). Honest prior stands: both
overlays are still expected to fail their kill switches; a veto-heavy month with
one lean-hold BUY is a legitimate data point, not a tuned result.

Scope note: this was the sanctioned monthly automation run (the task file is the
authorizing instruction; paper + Alpaca-PAPER only). Decisions are logged data,
not code — no strategy/factor/universe logic was touched, so the frozen
regression tests (a code-change guard) were not triggered; ops integrity was
verified instead by verify_run --mode monthly PASS 76/76. Full run log:
`var/monthly_rebalance_2026-08-03.log`.

# Appendix CQ - Third full audit (cold subagent): the rebalance failure-visibility chain fixed plus 8 more findings; 15 findings deferred to a fresh session (2026-08-05, ~19:50 CDT)

Evan ran `/audit` with no scope narrowing. This session had already shipped CN and
CO, so per the skill's step 0 the audit was run by a **cold general-purpose
subagent** given only the project path, the scope, the safety constraints, and the
docs as *claims under test* — no conversation history, no "this part is known
good." That mattered: the audit's top finding lands directly on the code CO
shipped three days earlier.

## CQ.1 The headline: check (e) could be defeated one layer down

CO added `verify_run` check (e) so a missed monthly rebalance FAILs loudly. The
audit found the artifact it reads is written unconditionally, so the check could
be satisfied by a run that did nothing. Three defects compounded:

| # | Defect | File |
|---|---|---|
| 3 | `paper_rebalance.rebalance()` returned **0** on both abort paths — the same value as "nothing needed to change" | `paper_rebalance.py:141,154` |
| 1 | `rebalance_log.md` stamped unconditionally at the end of the batch | `rebalance.bat:123`, `stamp_rebalance_log.py` |
| 4 | `rebalance.bat` discarded **14 of 16** python exit codes, including `alpaca_sync --all --execute` | `rebalance.bat:119` |

Chained: an empty universe aborts every sleeve, each abort returns 0, the batch
echoes a warning and continues, the stamp writes today's date, check (e) reads a
current-month date and PASSes, and the `monthy-llm-rebalance` Step 0 gate then
STOPs for the rest of the month — so the retry the CN cron fix restored never
fires. Every sleeve holds a stale book, and `verify_run` (a)-(d) still report
PASS 76/76, because a sleeve that never traded is perfectly self-consistent.

**Fixed.** Both `return 0` are now `raise RuntimeError` (both dispatchers already
wrap the call in try/except and count failures). `stamp_rebalance_log` takes
`--status OK|PARTIAL`, anchors to `PROJECT_ROOT` (finding 19), and exits 1 rather
than swallowing its own write failure. `rebalance.bat` accumulates `RC_FAIL` over
every step, which drives both the stamp status and the batch's own exit code —
the pattern `ladder_rebalance.bat` already used since record CH.
`check_rebalance_cadence` FAILs on `PARTIAL`.

**Verified by execution, not reading.** `rebalance.bat` cannot be run (it trades),
so every python invocation was replaced with `cmd /c exit N` in a scratch copy and
the real control flow was run three ways: all-OK -> **exit 0** "Rebalance
complete"; alpaca_sync fails -> **exit 1** + `STEP FAIL: alpaca_sync --execute` +
PARTIAL; dispatcher fails -> **exit 1** + `STEP FAIL: monthly_rebalance` + PARTIAL.

## CQ.2 Finding 2 - the mandated check is the forbidden operation

`CLAUDE.md` mandates the frozen regression tests after ANY python change, and
separately forbids concurrent `factor_backtest`. The frozen tests **are** a
factor_backtest: `test_strategies` -> `momentum_v1.run()` ->
`run_factor_backtest()` -> `_wipe_state()` ->
`DELETE FROM positions` / `DELETE FROM portfolio_state`
(`trading_bot/execution/factor_backtest.py:64-69`) through a read-WRITE
`connect()` that commits. Every mandated run is a second writer holding a lock on
the 5 GB live DB.

Confirmed from live data, not inferred: `positions` holds **137 rows** stamped
`entry_time` 2026-08-03T04:36:36Z (= 08-02 23:36 CDT, this session's own frozen
run) with `entry_date` 2025-01-02, i.e. the `2025_H1` frozen window;
`portfolio_state.cash = $39.26`. `paper_positions` is untouched at 3,222 open
rows — the paper track record was never at risk.

**The auditor's proposed fix does not hold and was not applied.** Pointing the
backtest at a scratch DB is not surgical: `positions`/`portfolio_state` are shared
by `broker.py`, `monitor.py`, `portfolio.py`, `multi_backtest.py`,
`reporting/dashboard.py`, `reporting/report.py` and `form4/optimize_r15_wf.py`,
all through one `db.connect()` — and redirecting them also redirects
`price_cache`, which the backtest reads. A real separation is a DB-layer change.

**What was done instead:** a busy-window guard in `test_strategies.main()` that
refuses to run inside 17:00-18:30, 19:45-21:00 and 07:30-08:15 unless `--force`.
That makes the "never two writers" rule mechanically enforceable for the first
time (the audit's M1 pass had classed it UNENFORCEABLE). **It does not stop the
tests writing the live DB, and the 137 residue rows are still there.** Sized
honestly rather than patched to look closed.

## CQ.3 The rest of what landed

- **7** — `alpaca_sync` swallowed order-CANCEL failures with a bare `pass` and no
  artifact of any kind. The order plan assumes open orders were cancelled; a
  survivor still fills on top of the new one. Now logged and counted into the
  return code.
- **9 / E3** — `fractionability.refresh()` cached ANY exception as
  `tradable=0, fractionable=0` for `STALE_DAYS = 30`, and `paper_rebalance`
  silently drops untradable names. One Alpaca 429 on a rebalance evening would
  have quietly thinned every sleeve for a month, and `UNDERFILL_FRACTION = 0.5`
  lets 25 of 50 names vanish while still reporting PASS. Only a genuine 404 is
  cached now; transport errors re-raise. The sibling silent `except: return None`
  on client construction now logs.
- **10 / E5** — `if errorlevel 2` is GREATER-OR-EQUAL, so any code >=2 took the
  SUCCESS branch, including cmd's 9009 for a missing interpreter.
- **11 / E7** — the rate-limit guard was gated on `total > 0`, so the partial
  outage of record CI was caught while a TOTAL outage returned 0.
- **20 / E10** — `base.startswith("sector_top4")` gave the 11-ETF universe to any
  future `sector_top4*` sleeve.
- **E4** — a forward-dated stamp (`2099-01-01`) satisfies every month comparison
  forever, silently voiding check (e) AND the task's Step 0 retry. Now bounded by
  `date.today()`.
- **E2** — `daily-trade-check-2` fired `0 18 * * 1-5`, reading `paper_nav` and
  `paper_positions` while the 18:03 rebalance was mid-write; commit `4caba7e`
  shows the 08-03 report committed and pushed at 18:16 from a mid-rebalance
  snapshot. Moved to **`0 19 * * 1-5`** with Evan's OK (08-03's rebalance finished
  18:24; the ladder starts 20:30).

## CQ.4 A near-miss worth recording

The first attempt at finding 20 replaced the prefix match with
`base in ("sector_top4", "sector_top4_full")` and **broke both real sector
sleeves** — `base` retains the `_paper` suffix. It was caught immediately because
the done-check was "resolve all 76 live sleeve names through `_strategy_config`"
rather than "read the diff": 65/76 resolved, and the two sector sleeves were in
the failures. Corrected to the `_paper` forms; that 76/76 resolution check is now
the permanent guard for this function. Recording it because the audit's own step 5
makes this exact point — a fix that was never fed its trigger is unverified.

## CQ.5 Verification

- Frozen tests **4/4 d=+/-0.0000pp** — v1 +14.5547%/70 & +1.8792%/156,
  v2 +14.4062%/38 & +10.2194%/87.
- `test_rebalance_cadence` extended to 6 quiet + 5 fail cases; passes.
- Busy-window guard unit-checked at 17:15, 18:03, 18:30 (exclusive upper bound),
  20:30, 07:45, 13:00, 23:00, plus `--force` override.
- `_strategy_config` resolves 76/76 live sleeve names to expected support.
- `daily.bat`, `rebalance.bat`, `ladder_rebalance.bat` re-verified pure ASCII with
  internally consistent line endings (`rebalance.bat` all-CRLF, the other two
  all-LF as they already were).

Commit `d7ff027`.

## CQ.6 A tooling warning that outranks any single finding

The cold auditor reports the **Grep tool returns 0 matches on DIRECTORY paths in
this repo** while GNU `grep -rn` returns many — `auto_adjust` 0 vs 29, `except`
under `scripts/momentum` 0 vs 36. It works on file paths. Cause undiagnosed. The
`/audit` skill already carried a note of the same behaviour observed 2026-08-03
(0 vs 21 on `auto_adjust`), so this is the second independent sighting.

**Consequence: any "no matches / clean" conclusion drawn from a directory-scoped
Grep call in this repo is unproven.** Two prior audits ran here. Every enumeration
behind this entry came from GNU `grep -rn` via Bash.

## CQ.7 STILL OPEN — 15 findings, deferred to a fresh session

Evan's call, made explicitly: finish the remainder in a fresh session rather than
push edits that could not be verified in the one that ran the audit. Fix order,
highest value first:

| # | Sev | What |
|---|---|---|
| **E1 / 6** | high | The two cascade sleeves have **no stop enforcement at all** — `llm_cascade_ops.py:151-159` has no `check-invalidation` subcommand and `daily.bat:41-42` covers only the two overlay modules, while the runbook claims daily enforcement. `llm_cascade_top1_paper` holds **STX with a logged invalidation of $730** right now. Flagged twice in `daily_report.md` and never promoted to a spec doc. **Decide first:** implementing this changes a live experiment arm's behaviour mid-flight (a PRD scope-guard question), so either implement AND date the changeover here, or document "cascade runs unstopped by design" in HANDOFF + the runbook |
| **5** | high | `paper_trader.buy()/sell()` are documented atomic but are two independent commits (`paper_trader.py:172-175`); a failure between legs closes a position without crediting cash, and `verify_run` recon recomputes from the same corrupted cash so it reports `delta $0.00` **forever**. Fix: one `with connect()`, thread `conn` through |
| **8** | high | HANDOFF still says M6 is GATED on Alpaca fills. 231 fills exist (99 on 07-07 + 132 on 08-03, record CP). `fetch_alpaca_fills.py` does not exist. Mark UNGATED; next task is M6.1 |
| **12** | med | `paper_mtm` computes `missing_count`/`aged_count`/`median_age_days` and the daily path discards them — `mtm_catchup` calls `compute_nav`/`write_nav` directly, never `main()`. Carry-forward has no age bound, so a delisted holding marks at its last-ever close indefinitely and recon still says `$0.00` |
| **E6** | P2 | `backup_trades_db.py:71-72,82` rotates over a **directory scan**, so a truncated `VACUUM INTO` counts as a generation and evicts a good backup. Fix: write `.part`, `PRAGMA integrity_check`, rename, rotate only over validated files |
| **15,16,13,14,17,22** | med/low | Doc drift: HANDOFF cites an **FN position that does not exist** (0 open FN rows anywhere); three enabled Claude tasks (`daily-trade-check`, `daily-trade-check-2`, `hellohello`) are in no inventory that claims to be complete — **two of them `git commit` and `git push` to this repo**; `MOMENTUM_DESIGN.md:35` specifies a $1M liquidity filter that has never existed (`universe.py:53` `MIN_DOLLAR_VOL = 0`) and its §3/§10 disagree on top-N; `docs/paper_trading_ops.md` is last in the PRD's mandated read-first chain and describes a 2-sleeve hand-run system; `sector_cache` (6,113 rows, live) vs `sectors_cache` (1,493 rows, research-only) both exist and HANDOFF lists only the latter; HANDOFF header still says "Last updated: 2026-07-17" |
| **E9 / 18** | low | `backadjust_split.py:71-74,127-129`'s UNKNOWN-kind detector cannot fire — it is `log.info` text in a dry-run survey, not a gate. `above_ma_200` already sits outside all three constant tuples. Harmless today (booleans are scale-invariant); a future price-like `kind` would be silently left un-adjusted, which is the KLAC class |
| **21** | low | `requirements.txt` pins 9 packages, 97 are installed; yfinance's transitive deps are unpinned so a clean rebuild can change adjustment behaviour. **CVE status could not be determined** — `pip-audit` absent, installing tools was not permitted |

Two things the audit could not verify and did not assert: the CVE status of the
dependency set, and the frozen-test deltas (the auditor was read-only and finding
2 proves the tests write).

# Appendix CR - The 15 deferred CQ.7 findings closed: the cascade sleeves are unstopped BY DESIGN (Evan's call, and the audit's own example was the wrong one), buy/sell made genuinely atomic, M6 ungated, carry-forward staleness surfaced, backups validated before rotation, plus six doc-drift corrections (2026-08-05, ~21:05 CDT)

Fresh session, per Evan's CQ.7 instruction to finish the remainder somewhere the
fixes could actually be verified. All 15 open findings are closed. Order below is
CQ.7's own priority order.

Three verification rules were applied throughout, and each one caught something:
feed a fix its trigger rather than reading the patch; use GNU `grep -rn` for any
enumeration (CQ.6); check the audit's factual claims before acting on them.

## CR.1 E1/6 - cascade stops: DECIDED, and the audit pointed at the wrong position

CQ.7 flagged that `llm_cascade_ops.py` has no `check-invalidation` subcommand and
`daily.bat:41-42` covers only the two CASH overlay modules, while the runbook
claimed daily enforcement - and cited `llm_cascade_top1_paper` holding **STX with
a logged invalidation of $730 right now** as the live exposure.

**Checked against the DB before acting. STX was never at risk**: closes 08-03
$831.06, 08-04 $845.35, 08-05 $837.66 against a $730 stop - 13% clear.

**The real exposure was XLU, which the audit did not name.**
`llm_cascade_sector4_paper` bought XLU on 2026-08-03 at **$44.38** against a
logged HOLD invalidation of **$44.50** - a stop set ABOVE its own entry price.
Its closes since: 44.36 / 44.11 / 43.66. It has been below its stop on **every
close it has ever had**. Had the cascade carried enforcement, XLU would have
exited on the 08-03 evening run.

Two further facts that shaped the decision:
- The 08-03 XLU rationale reads "Above 50DMA (44.96)" while that day's close was
  44.36. The invalidation level rests on an internally inconsistent decision.
- Enforcement demonstrably works on the arm that has it: the DB's ONLY
  `exit_reason='invalidation'` row is `llm_overlay_sector_top4_paper` exiting XLK
  on 2026-07-28.

**Presented to Evan as three options, not two.** CQ.7 framed it as implement-or-
document, but `trading_bot/strategies/llm_cascade.py` defines the arm as ALWAYS
INVESTED with never-idle fallbacks - that is its whole distinction from the cash
overlay. A stop exits to CASH, so bolting one on makes the arm a hybrid of the
two treatments and destroys the clean three-way comparison. The third option
(stop -> cascade to the next candidate) preserves always-invested AND adds
downside control, but is a new strategy rule mid-experiment, which the PRD scope
guard forbids outright, and needs a mid-month re-pick rule that does not exist.

**Evan chose: document unstopped by design.** No code change. Written into three
places so it can never again read as an oversight:
- `llm_cascade.py`'s docstring - the rationale, plus **the cost stated plainly:
  these sleeves have no downside control of any kind, a cascade pick rides to
  zero, and their drawdowns are NOT risk-comparable to the cash overlays'.**
- `HANDOFF.md` - a new "Cascade arm (always-invested)" subsection. The LLM
  Overlay Experiments section had documented only the two cash overlays.
- `docs/overlay_decision_runbook.md` - the invalidation convention now says "for
  the two CASH overlays only", plus a new bullet: the `invalidation_level` a
  decision logs is consumed by the cash-overlay sleeve only, so a level set for a
  name that only the cascade ends up holding **binds nothing**. `llm_cascade_ops.py`
  added to the Files table (it was absent).

XLU is **reported, not fixed** - recorded in HANDOFF as a decision-quality
datapoint for the kill-switch review, not a data bug. Nothing was traded.

## CR.2 Finding 5 - buy()/sell() were "atomic" in the docstring only

`paper_trader.buy()` and `sell()` each ran their position leg and their cash leg
through two separate `with connect()` blocks - two independent commits. A failure
in between committed one leg and dropped the other: a buy that inflates NAV
forever, or (worse) a sell that closes a position and never credits the proceeds.
The corruption is invisible to `verify_run`, whose cash recon recomputes from the
same `paper_portfolio.cash` it corrupted, so it reports delta $0.00 in perpetuity.

`db.connect()` hands back a REUSED thread-local connection that commits on exit,
so nesting `with connect()` would have committed the outer block's half-finished
work at the inner exit. Fixed as CQ.7 prescribed - one transaction, `conn`
threaded down through a small `_tx()` helper that joins the caller's transaction
when given one and owns its own otherwise. `open_position` / `close_position` /
`adjust_cash` take an optional `conn`; their default path is byte-identical to
before. Confirmed by GNU grep that those three primitives have **no callers
outside buy()/sell()**, and that no caller wraps buy/sell in its own
`with connect()` block.

New regression test `scripts/momentum/test_trade_atomicity.py`, 11 checks, all
passing. It opens by proving the trigger is real rather than asserting current
behaviour: the OLD split-leg shape, fed the same injected failure, **leaks a
position row with no cash debit** (open=1, cash untouched at $100,000). The new
buy() rolls back to zero rows, the new sell() leaves the position OPEN, and both
happy paths still move exactly the right cash.

## CR.3 Finding 8 - M6 is ungated

The gate condition has been met since 2026-08-03. **231 Alpaca PAPER orders, 0
rejects**: 99 on 07-07 (record AV) + 132 on 08-03 (record CP - residual_roa_6535_0701
62, mom_roa_6535_0701 69, spy_benchmark_0701 1). `scripts/momentum/fetch_alpaca_fills.py`
does not exist (verified). Marked UNGATED in `HANDOFF.md` (four separate stale
claims) and `PRD_ROADMAP.md` (five), striking in place with dated reasons per the
roadmap-history rule rather than rewriting the dated blockquotes that were true
when written.

**One honest caveat carried into the PRD**: the record logs orders SUBMITTED and
REJECTED, never orders FILLED. They were DAY orders expected to fill at the next
open, but confirming that is precisely M6.1's own done-check ("CSV rows match the
order counts the record logged"). 231 is the submitted count to reconcile
AGAINST, not a fill count to assume. **M6.1 is now the next open PRD task; it was
not started here** - this session's scope was the 15 findings.

## CR.4 Finding 12 - the daily path threw the staleness numbers away

`compute_nav` computes `missing_count` / `aged_count` / `median_age_days`, and
only `paper_mtm.main()` ever printed them. `daily.bat` has not gone through
`main()` since M3.5. Enumerating the callers turned the finding out to be wider
than reported: **six** write paths call `compute_nav`/`write_nav` directly and
every one discarded the metrics - `mtm_catchup`, `ladder_forward_rebalance`,
`monthly_rebalance`, `remark_nav_day` and two seeders.

So the fix went into the shared function rather than the reported call site
(CLAUDE.md's root-cause rule): reporting now happens **inside `compute_nav`**, so
all six paths get it and a seventh caller cannot forget it. `main()`'s now-
duplicate block was removed.

Added `MAX_CARRY_FORWARD_DAYS = 10` and a `stale_tickers` list, so the message
NAMES the offending ticker and its age instead of counting. Carry-forward itself
is deliberately left UNBOUNDED - refusing to mark would tear a hole in NAV
continuity, and re-valuing on a heuristic is exactly what record CK ruled out.
The bound is a **reporting** bound: report loudly, never refuse, never re-value.
The error text says why recon cannot catch it.

New regression test `scripts/momentum/test_carry_forward_bound.py`, 8 checks, all
passing: a 1-day-old price is not flagged, a 30-day-old one IS (named, with its
age), the sleeve is **still marked** at the fossil price, and a never-priced name
still falls back to `entry_price`. Checked for false positives against the live
DB: **0 of 192 distinct held tickers** would trigger it as of 2026-08-04. The flag
is silent today and speaks only when something is genuinely wrong.

## CR.5 E6 - a torn backup could evict a good one

`backup_trades_db.py` rotated over a directory glob, so a truncated `VACUUM INTO`
counted as a generation - and because its filename carries today's date it sorted
NEWEST, so the junk was RETAINED while good copies aged out. Three Sundays and all
three generations are junk, discovered during a restore. A second, independent
defect: the same-day rerun path `unlink()`ed the existing backup BEFORE starting
the new VACUUM, so a failure there destroyed a good generation and produced nothing.

Now write-validate-rename: VACUUM into `<name>.db.part` (which the `trades_*.db`
glob **cannot match**, so a failed write is invisible to rotation by construction
rather than by a filter), validate, then `os.replace`. Validation is
`PRAGMA integrity_check` **plus** a `paper_nav` row-count match against the
source - they fail differently: a torn write trips integrity_check, while a VACUUM
against the wrong source produces a perfectly valid database with the wrong rows.
On any failure: delete the `.part`, exit 1, and **do not rotate**.

New regression test `scripts/test_backup_validation.py`, 11 checks, all passing -
including the structural proof (the glob cannot see `.part`, and CAN see a junk
`trades_*.db`, which is the old bug) and the one that matters: a run whose
validation fails exits 1 and leaves **all three** pre-existing generations on
disk. `integrity_check` is O(db size); marked with its upgrade trigger
(switch to `quick_check` if this ever runs more often than daily).

## CR.6 E9/18 - the UNKNOWN-kind detector could not fire

It was `log.info` text inside a dry-run survey, not a gate. Confirmed the standing
false positive from live data: `price_cache` holds **`above_ma_200`**, which sits
outside all three classification tuples. Two fixes - `above_ma_200` classified
into `UNTOUCHED_KINDS` (a boolean IS scale-invariant, so this is a correct
classification, not a silencer), and the detector promoted to a real gate that
returns 1, with `--allow-unknown-kinds` as the deliberate escape hatch. Harmless
today; a future price-like `kind` would otherwise be left pre-split while `close`
was divided, which is the KLAC failure shape this script exists to repair.

Verified against fixture DBs (the subject is an operator-run one-off that is
dry-run by default, so this got a scratch check rather than a permanent test):
an unclassified kind halts with exit 1, `--allow-unknown-kinds` proceeds, and the
real live kind vocabulary including `above_ma_200` passes clean.

## CR.7 Finding 21 - environment pinned; CVE status honestly UNDETERMINED

`requirements.txt` pinned 9 packages against 97 installed, leaving yfinance's
entire transitive chain - `curl_cffi`, `requests`, `urllib3`, `lxml`,
`beautifulsoup4`, `peewee`, `frozendict`, `multitasking`, `platformdirs` - unpinned.
Those are exactly the libraries that fetch and parse the prices this project
treats as ground truth, so a clean rebuild could change adjustment behaviour
behind an unchanged `yfinance==1.3.0` pin.

Added **`requirements.lock.txt`** - 96 packages, full transitive snapshot of the
known-good venv, pure ASCII, with a documented header. `requirements.txt` keeps
its curated direct list and now points at the lock. All 9 direct pins cross-checked
against the lock: identical.

**CVE status: UNDETERMINED, and no claim is made in either direction.** Neither
`pip-audit` nor `safety` is installed; installing one would perturb the venv the
frozen tests are the contract for. The exact commands to settle it (preferably in
a throwaway venv) are written into the lock file's header.

## CR.8 Doc drift - findings 15, 16, 13, 14, 17, 22

Each verified against reality first, not taken from the audit.

- **15 - the FN position does not exist.** `HANDOFF.md` listed the single-name LLM
  sleeves as "deep underwater (FN position, both -19%)". **Zero open FN rows** in
  the DB; the 2 that exist are closed and pre-date the 07-01 reset. The claim
  survived two re-inceptions. Corrected to the real holdings: control
  `mom_roa_top1_paper` = **MU**, treatment = **cash** (BE vetoed), cascade =
  **STX**. The general point (single-name sleeves can be deep underwater, n is
  noise) was kept because it is still true.
- **16 - three enabled Claude tasks were in no inventory.** They run on Claude's
  scheduler, not `schtasks`, so they appear in NO `schtasks /query` output and
  nothing in this repo listed them. New "Claude agent scheduled tasks" table in
  `HANDOFF.md` covering all six (3 enabled, 3 disabled), read live from
  `list_scheduled_tasks`. **Two of them `git commit` and `git push` to this repo**
  (`daily-trade-check` 8:07am weekdays, `daily-trade-check-2` 7:00pm weekdays);
  both are narrowly scoped to `git add daily_report.md daily_report.html` with an
  explicit "NEVER `git add -A`", so an in-progress tree is not swept in.
  **`hellohello` is a stray enabled test task** firing daily at ~8:08am whose
  entire prompt is `hello (Just say "hi" back)` - **flagged for Evan, not
  deleted.**
  - **Bonus, and the reason this mattered: the record CN cron re-check is DONE.**
    HANDOFF asked a future session to re-list `monthy-llm-rebalance` because CN's
    confirming call was blocked by the permission classifier. It reads
    **`0 18 * * *`, "At 06:03 PM, every day", enabled**, `lastRunAt` 2026-08-05.
    **The CN fix HELD.** The CQ.3/E2 move of `daily-trade-check-2` to `0 19` held too.
- **13 - `MOMENTUM_DESIGN.md` specifies a filter that has never existed.** Its §1
  claims a "30-day median dollar volume >= $1M (liquidity floor)";
  `trading_bot/factors/universe.py:53` is `MIN_DOLLAR_VOL = 0`. Every backtest and
  every live sleeve has run with **no liquidity filter at all**. Separately, §3
  ("Top N = 50, 2% per name") contradicts §10 "Decisions - locked" ("top 100, 1%
  per name"); both shipped, as the separate `mom_v2_paper` / `mom_v1_paper`
  sleeves. Annotated in place with a HISTORICAL-DESIGN-DOC banner. **Turning the
  liquidity floor on is a strategy change and was NOT done.**
- **14 - `docs/paper_trading_ops.md` describes a 2-sleeve hand-run system** while
  76 sleeves run unattended. It is **last in `PRD_ROADMAP.md` §7's mandated
  read-first chain**, so an executing model is told to read it - which is why it
  got a banner rather than a quiet deletion. Body deliberately not rewritten.
- **17 - `sector_cache` vs `sectors_cache` are different tables and both are
  live.** `sector_cache` (6,113 rows) is what the running system reads and writes
  (`market_data`); `sectors_cache` (1,493 rows) is research-only
  (`warm/warm_sectors.py`). HANDOFF listed only the latter, so anyone trusting it
  would query the wrong table. HANDOFF also claimed "18 tables" and then named 10;
  **all 18 are now enumerated.**
- **22 - `HANDOFF.md` said "Last updated: 2026-07-17"** through the CE/CH/CJ-CN/CP/CQ
  work. Now 2026-08-05.

## CR.9 Verification

- Frozen tests **4/4 d=+/-0.0000pp**, run 2026-08-05 21:01 CDT, matching the CQ.5
  baselines exactly: v1 2023_Q4 +14.5547%/70 trades, v1 2025_H1 +1.8792%/156,
  v2 2023_Q4 +14.4062%/38, v2 2025_H1 +10.2194%/87.
- `test_trade_atomicity.py` - 11/11 pass (incl. the old-shape leak demonstration).
- `test_carry_forward_bound.py` - 8/8 pass; **0 false positives across all 192
  distinct held tickers** on the live DB.
- `test_backup_validation.py` - 11/11 pass.
- `backadjust_split` unknown-kind gate - 4/4 fixture checks pass.
- Live DB touched **read-only** throughout. Nothing traded, no NAV row written, no
  live-DB write attempted.
- Frozen tests were deliberately DEFERRED to 21:01 CDT: the CQ busy-window guard
  refuses 19:45-21:00, which is exactly the `TradingLadderRebalance` 20:30 slot.
  The guard did its job on its first real encounter.

## CR.10 Noticed and deliberately NOT acted on

Reported per the standing rule that data/design questions are Evan's call:

1. **`dividends_total` is classified scale-invariant in `backadjust_split`.** A
   per-share dividend is price-like and arguably needs dividing by N after a
   split. Pre-existing classification; changing it would alter the KLAC repair's
   semantics, and it is outside the finding (which was about the detector not
   firing). Flagged only.
2. **`price_cache` and `sector_cache` are not in `trading_bot/db.py`'s `SCHEMA`**
   despite its docstring calling SCHEMA "the authoritative definition of every
   table" - `market_data._ensure_cache_schema()` owns their DDL. Found while
   fixturing a test. Noted in HANDOFF; not one of the 15 findings.
3. **`hellohello`** - Evan's to delete.
4. **The XLU stop above its own entry price** (CR.1) - a decision-quality
   datapoint, logged for the kill-switch review.
5. **Finding 2 from CQ.2 remains open by design**: the frozen tests still write
   the live DB, and the 137 residue rows in `positions` are still there. The
   busy-window guard bounds WHEN, not WHETHER. A real fix is a DB-layer change.

Committed together with the code and doc changes it describes.

# Appendix CS - PRD M6.1 SHIPPED: all 231 mirrored orders reconcile 231/231 filled, and the August batch turns out to have been HELD TO THE NEXT SESSION OPEN - so M6.2 must not call it slippage (2026-08-05, ~21:52 CDT)

First task after M6 was ungated (record CR). New `scripts/momentum/fetch_alpaca_fills.py`
pulls FILLED orders from the three mirrored Alpaca PAPER accounts to CSV, read-only
(`GET /v2/orders` only), and reconciles them against what the record logged.

## CS.1 The client could not do the job as written

`alpaca_client.list_orders` took only `(status="open", limit=100)` — no date range,
no paging. Three separate ways that silently produces a wrong answer:

- **It cannot reach 2026-07-07 at all.** No `after`/`until` meant no way to ask
  for the deploy batch.
- **`limit=100` truncates, newest-first.** `residual_roa_6535_0701_paper` has 110
  orders in the M6 window and `mom_roa_6535_0701_paper` has 119 — both over 100.
  The OLDEST orders are the ones dropped, and nothing in the response says so.
- **A filled order is not `status="open"`.** Called as-is it returns `[]`, and the
  existing `or []` makes that indistinguishable from a successful empty fetch.

Extended with `after`/`until`/`direction`, default signature unchanged so
`alpaca_sync`'s cancel sweep (`list_orders(status="open")`) is untouched. Paging
lives in the fetch script (one consumer), walking `after` = the page's newest
`submitted_at` and deduping by order id.

## CS.2 Result: 231/231, clean

    ACCT1 residual_roa_6535_0701_paper  110 orders  ->  48 (07-07) + 62 (08-03), all filled
    ACCT2 mom_roa_6535_0701_paper       119 orders  ->  50 (07-07) + 69 (08-03), all filled
    ACCT3 spy_benchmark_0701_paper        2 orders  ->   1 (07-07) +  1 (08-03), all filled
    ALL: 231 filled vs 231 submitted per the record (AV=99, CP=132). Exit 0.

Every order in the window has `status='filled'`; there are no canceled, expired,
rejected or partially-filled orders. The done-check as the PRD wrote it — "CSV
rows match the order counts the record logged" — passes exactly, and it passes
because the fills genuinely are all there, not because the query was shaped to
agree. Output: `var/alpaca_fills_2026-07-01_2026-08-06.csv`.

## CS.3 The finding: Alpaca's `submitted_at` is a QUEUE-RELEASE time

The first run reported 0 filled for 2026-08-03 on all three accounts while the
totals reconciled perfectly — the signature of a wrong key, not missing data.
Chased rather than explained away, and it is a real property of the venue:

| source | when the 132 August orders were "submitted" |
|---|---|
| `var/alpaca_request_ids.log` (ours, authoritative for OUR side) | **132 POSTs in a 6-second burst, 2026-08-03T23:24:48-23:24:54Z = 18:24 CDT** |
| Alpaca's `submitted_at` field | **2026-08-04T08:00:16 - 13:23:01Z**, spread over 5.4 hours |

So `submitted_at` is when Alpaca's simulator released the order to its market,
8.5-14 hours after we sent it. Keying reconciliation off that field alone
mis-dates an entire batch by a day. `BATCHES` in the script now carries both
`rebalance` (local, what the record logs) and `alpaca_date`, with the discrepancy
documented at the constant rather than hidden. A window-total check was added too,
so a batch landing on an unexpected date is a finding rather than a silent miss.

## CS.4 The finding that matters more: the two batches are NOT comparable

Measured submit->fill lag, straight from the fetched data:

| batch | n | min | median | max | what it is |
|---|---:|---:|---:|---:|---|
| 2026-07-07 | 99 | 0.3s | **2.0s** | 5.6s | intraday, immediate |
| 2026-08-04 (the 08-03 rebalance) | 132 | 418.6s | **19,797s (5.5h)** | 20,086s | **held to the next session open** |

The July deploy ran mid-session (13:20 CDT) and filled in seconds. The August
rebalance POSTed at 18:24 CDT, after the close, so Alpaca held all 132 orders and
filled them at the next open — 13:30-13:36Z on 08-04, i.e. 09:30-09:36 ET.

**Consequence for M6.2, and it is not a detail:** the sim books its August fills at
the **2026-08-03 close**, while the mirror filled at the **2026-08-04 open**. The
price difference between them is dominated by the **overnight gap**, not by
execution quality. Calling that number "slippage" would be wrong, and it is exactly
the sort of plausible-looking figure that would then get cited. The July batch is a
genuine intraday execution comparison; the August batch is not. **They must not be
pooled into one slippage number.** The script prints this classification on every
run (`report_execution_timing`) so M6.2 cannot miss it.

This also raises a design question for Evan, deliberately NOT actioned here (it
would change live trading behaviour): the monthly rebalance fires at 18:03 CDT by
design — after the 17:15 daily MTM, per record BS — which guarantees every future
monthly mirror batch fills at the next open. Either that is accepted and M6.2
reports monthly mirroring as open-to-close-gap-inclusive, or the Alpaca sync moves
to an in-session slot. Not a bug; a tradeoff that was never stated.

## CS.5 Verification

- Live done-check: **231/231, exit 0** (output above).
- New `scripts/momentum/test_fetch_alpaca_fills.py`, offline (no network, no keys,
  no DB), 7 checks passing. It covers what a live run structurally cannot: each
  account took fewer than 500 orders, so **the paging loop never executes against
  real data**. Cases: 1,200 orders across 3 pages with no loss and no dupes; a
  short page terminating in one call; 600 orders sharing one timestamp
  terminating instead of spinning (the exclusive `after` cursor cannot advance —
  the code now logs INCOMPLETE if a full page yields nothing new, since that
  would silently truncate); a partial fill staying visible as qty 10 vs
  qty_filled 4; a shortfall producing a finding; a batch on an unexpected date
  producing a finding; and the clean 48+62 case staying silent.
- Frozen tests **4/4 d=+/-0.0000pp** — v1 +14.5547%/70 & +1.8792%/156,
  v2 +14.4062%/38 & +10.2194%/87.

## CS.6 Notes for M6.2

- The price column is named `filled_avg_price` because that is what Alpaca returns
  — an average across every print of that order, not a single fill price. Do not
  relabel it downstream.
- The CSV carries `order_id`, so re-fetching is idempotent and any future partial
  fill is traceable. It also carries `qty` and `qty_filled` separately, which is
  the only way a partial fill is visible at all.
- `price_cache` is dividend-UNadjusted and split-adjusted; Alpaca fills are raw
  traded prices. Same-day comparison is fine, which is what M6.2 does — but the
  July/August split above governs what the comparison MEANS.

# Appendix CT - PRD M6.2 pairing built and RUN, then STOPPED before writing slippage_log: the measured ~+100bps is intraday/overnight DRIFT, not execution slippage, and M6.3 run off it would have recalibrated HALF_SPREAD_BPS 5bps -> 100bps and corrupted every backtest (2026-08-05, ~22:25 CDT)

Immediately after M6.1 (record CS). The pairing machinery is finished, tested and
read-only; what is blocked is the **interpretation**. `slippage_log` was
deliberately left empty — writing rows whose basis is undefined is worse than
writing none, because a populated table reads as a settled measurement.

## CT.1 What was built

New `--alpaca-csv` path in `scripts/momentum/slippage_tracker.py`. The existing
`--csv` path is untouched: it is the deferred real-brokerage flow for 18, and
three things in it could not be reused.

| legacy behaviour | why it fails here |
|---|---|
| pairs by `ORDER BY ABS(julianday(entry_time) - ?) LIMIT 1` | always returns *something*, so it can never report an unpaired fill — and with a ticker held across two rebalances it silently picks the wrong leg |
| `direction = "buy" if qty > 0 else "sell"` | `paper_positions.qty` is always positive in a long-only sim, so every fill is labelled a buy |
| pairs every fill against `entry_price` | a SELL must pair against `exit_price`; comparing a sell to an entry compares two unrelated trades |

The new path joins on **(sleeve, ticker, rebalance date)** explicitly, takes
`side` from the Alpaca CSV, pairs buys to `entry_price` and sells to
`exit_price`, and maps Alpaca's queue-release date back to the sim rebalance date
per CS.3. Read-only by default (`mode=ro`), `--execute` to write — matching
`backadjust_split` and `remark_nav_day`.

## CT.2 Structural finding: the sim and the mirror are not 1:1

| sleeve | Alpaca buys / sells | sim entries / exits |
|---|---|---|
| mom_roa_6535_0701_paper | 69 / **50** | 69 / **19** |
| residual_roa_6535_0701_paper | 63 / **47** | 63 / **16** |
| spy_benchmark_0701_paper | 1 / **1** | 1 / **0** |

Buys match exactly. Sells do not, and it is not an error: `alpaca_sync`
reconciles each account to **target weights**, so it trims or tops up names the
sim merely holds at a different quantity. Those fills have no sim leg by
construction. **166 of 231 paired; the 65 unpaired are reported with that reason
rather than dropped**, so the count is never quietly explained away.

## CT.3 The numbers, and why they were not believed

Per (sleeve x batch x side), never pooled:

| rebalance | sleeve | side | n | mean bps | median bps |
|---|---|---|---:|---:|---:|
| 2026-07-07 | mom_roa_6535_0701_paper | buy | 50 | **+156.0** | +122.9 |
| 2026-07-07 | residual_roa_6535_0701_paper | buy | 48 | **+42.0** | +39.0 |
| 2026-08-03 | mom_roa_6535_0701_paper | buy | 19 | +396.2 | +463.1 |
| 2026-08-03 | mom_roa_6535_0701_paper | sell | 19 | −156.8 | −285.9 |
| 2026-08-03 | residual_roa_6535_0701_paper | buy | 15 | +183.4 | +162.0 |
| 2026-08-03 | residual_roa_6535_0701_paper | sell | 15 | −44.0 | +23.0 |

Whole-batch: 07-07 n=98 mean **+100.2**, median +83.6; 08-03 n=68 mean +97.6,
median +148.2.

A ~+100 bps median against the sim's **5 bps** half-spread assumption is a 20x
gap. That is the shape of a result that is wrong, not a result that is
interesting, so it was checked before being reported. It did not survive:

    ticker  sim_entry  close_2026-07-07   sim/close
    AAOI     115.9179          114.4100    1.013180
    AEHR      65.3577           66.9400    0.976362
    AGX      655.4126          663.1800    0.988288
    AMD      515.8578          516.1100    0.999511
    APLD      31.4057           30.7100    1.022654

`sim entry_price / price_cache close for the same date` ranges **0.976 to 1.023**
— not the **1.0005** a 5 bps half-spread implies. The sim prices via
`market_data.last_close_on_or_before(ticker, as_of) * (1 +/- spread)`
(`paper_rebalance.py:199,209,246`), so one of two things is true and this session
could not determine which: the 07-06 cohort deploy used an `as_of` that is not
recoverable from here, **or** `price_cache` has been revised underneath those
rows since. The second is not speculation — `daily_price_refresh` re-downloads
the last 30 days for every ticker with `INSERT OR REPLACE` **by design** (record
CK), and 2026-07-07 sat inside that rolling window until approximately now.

## CT.4 Why this is not slippage, and why that stops M6.3

Even setting the basis question aside, neither batch compares like with like:

- **July**: the mirror filled at **14:20 ET**, mid-session. The sim's reference is
  a **close**. The difference is ~1h40m of intraday drift.
- **August**: the mirror filled at the **next session's open** (record CS.4). The
  difference is an overnight gap.

The sim never books at a price the mirror ever transacted at. So ~+100 bps is
**intraday and overnight drift wearing a slippage label**, and the per-name
extremes (+1470.9 / −1364.9 bps) are single-name moves, exactly what drift
produces and what a spread cannot.

**M6.3 was therefore NOT started.** Its task text says to write a memo if measured
slippage differs materially from the 5 bps assumption. Run off these figures it
would recommend moving `HALF_SPREAD_BPS` from 5 to ~100 — a **20x** change to the
transaction-cost assumption underlying every backtest, every held-out validation,
and every sleeve comparison in this project. Nothing was written to
`slippage_log`; `HALF_SPREAD_BPS` is unchanged. This is the same failure mode the
M6.1 handoff was written to guard against, one milestone further down and with
far worse blast radius.

## CT.5 What unblocks it

1. **Pin the sim's fill-price basis for the 07-06 cohort.** Recover the `as_of`
   the deploy actually used (record AV / the `cohort-0706-deploy` task log) and
   compare against a price snapshot from that date, not today's mutated cache.
   If they still disagree, the cache has drifted under the positions and that is
   its own finding.
2. **Then decide what M6 can honestly measure.** If the mirror never fills at the
   sim's reference price, execution slippage is not measurable with the current
   design at all. Options, all Evan's call because they change live behaviour:
   have `alpaca_sync` submit market-on-close orders; or move the monthly slot
   in-session (CS.4 already raised that the 18:03 slot guarantees next-open
   fills); or redefine M6 as measuring **implementation shortfall** — sim
   reference price vs realised mirror price, drift included — which is a real and
   defensible metric, just not the one the PRD named.

Recommendation: (1) first, since it is cheap and read-only, then bring (2) to
Evan rather than picking for him.

## CT.6 Verification

- Pairing run live, read-only: 166/231 paired, 65 unpaired with reasons, exit 0.
- No `slippage_log` rows written. No `HALF_SPREAD_BPS` change. No live-DB write
  of any kind this session.
- Frozen tests **4/4 d=+/-0.0000pp** — v1 +14.5547%/70 & +1.8792%/156,
  v2 +14.4062%/38 & +10.2194%/87.
- Commit `33911f7`.

# Appendix CU - CT.5 step 1 done: the sim's fill basis is PINNED exactly (close x 1+/-5bps, proven 34/34 and 33/35 on a 2-day-old batch), and the July reference prices are GONE - price_cache was rewritten under them. M6 currently has ZERO clean measurement windows (2026-08-05, ~23:12 CDT)

CT.5 named two candidate causes for the M6.2 blocker and did not choose between
them: an `as_of` that could not be recovered, or `price_cache` revised underneath
the rows. Step 1 was to settle it. It is settled, and it is the second.

## CU.1 The sim's fill-price basis, pinned

    BUY  entry_price = last_close_on_or_before(ticker, rebalance_date) * (1 + 5bps)
    SELL exit_price  = last_close_on_or_before(ticker, rebalance_date) * (1 - 5bps)

`last_close_on_or_before` (`trading_bot/execution/market_data.py:292-311`) reads
`price_cache` **directly and raw** — no in-memory mirror, no adjustment layer —
which is what makes the comparison below valid rather than assumed.

Proven against the **2026-08-03** rebalance, two days old at time of test:

| leg | match | result |
|---|---|---|
| buys | `close x 1.0005` | **34 / 34 exact** (within 1e-6 relative) |
| sells | `close x 0.9995` | **33 / 35 exact** |
| sells | `close x 1.0005` | 0 / 35 — the sign is real, not assumed |

So the formula and the 5 bps half-spread are confirmed, not inferred. The two
non-matching sells are unexplained and are left as such rather than rounded away.

## CU.2 The July reference prices no longer exist

The same test against the **2026-07-07** deploy, 29 days old:

| entry_date | age | exact `close x 1.0005` | mean abs divergence | range | moved >0.5% |
|---|---:|---:|---:|---|---:|
| 2026-08-03 | 2 days | **34/34** | 0.000% | 0.000% | 0/34 |
| 2026-07-07 | 29 days | **0/98** | **1.384%** | −5.92% .. +5.20% | **79/98** |

And this is the part that rules out the alternative: backing out
`implied_close = entry_price / 1.0005` for all 50 `mom_roa_6535_0701_paper`
entries and searching **every** cached close from 2026-06-25 to 2026-07-10
returns **zero exact matches on any date**. A wrong `as_of` would have produced
50/50 exact matches on one date. Instead the nearest neighbours scatter across
ten different dates — the signature of a series that has drifted underneath the
positions, not of an off-by-one date.

**Conclusion: the `price_cache` closes the sim read on 2026-07-07 have been
overwritten, and the prices those fills were actually computed from are not
recoverable from this database.**

Cause NOT fully established, and deliberately not asserted. It is consistent with
record CK's mechanism — `daily_price_refresh` re-downloads the last 30 days for
every ticker with `INSERT OR REPLACE` **by design**, and 2026-07-07 sat inside
that rolling window until roughly now — but a plain re-download of the same close
does not obviously move a price 5.9%, and 79 of 98 names moved more than 0.5%.
The KLAC back-adjustment (CJ), the 614 spike-nulls and the CI rate-limit backfill
each touched specific rows, not eighty percent of a basket. **What is proven is
that the values changed; why they changed by this much is open.**

## CU.3 What this means for M6, and it is worse than CT thought

CT.4 established that neither batch compares like with like on TIMING. CU adds
that one of them cannot be compared at all, on DATA:

| batch | reference prices | fill timing | usable for slippage? |
|---|---|---|---|
| 2026-07-07 | **gone** — cache rewritten | intraday 14:20 ET vs a CLOSE reference | **no** |
| 2026-08-03 | intact, exact | next-session OPEN vs a CLOSE reference (CS.4) | **no** |

**M6 currently has zero clean measurement windows.** Not one of the 231 fills
supports a defensible execution-slippage number: the batch with good data has bad
timing, and the batch with better-behaved timing has no surviving reference data.

This also puts a shelf life on the whole exercise that nothing in the PRD
anticipated: **a rebalance's reference prices are only reliably recoverable for
about a month.** Any slippage measurement not taken within days of the rebalance
is measuring against a cache that has since moved.

## CU.4 The fix, which is forward-looking and small

Stop re-deriving the sim's reference price from a mutable cache after the fact.
**Capture it at rebalance time**, when it is still the number the fill actually
used — `paper_rebalance` already has the exact value in hand at
`paper_rebalance.py:199,209,246` and currently only persists the spread-adjusted
`entry_price`/`exit_price`, not the underlying close or the date it came from.

Persisting `(reference_close, reference_close_date)` alongside each fill makes
every FUTURE rebalance measurable and is additive — no existing column changes,
no history rewritten, and it does not touch strategy logic. It does not recover
July; nothing recovers July.

That still leaves the timing problem (CS.4), which is a live-behaviour decision
and Evan's: market-on-close mirror orders, an in-session monthly slot, or
redefining M6 as **implementation shortfall** — sim reference vs realised mirror
price, drift included — which is a real and defensible metric but is not the one
the PRD named. Renaming the goal to fit the available data is a choice worth
making deliberately rather than by drift.

## CU.5 Status and verification

- All queries read-only (`mode=ro`). No writes, no `slippage_log` rows, no
  `HALF_SPREAD_BPS` change. No code changed in this entry's work, so the frozen
  tests stand from `33911f7` at 4/4 d=+/-0.0000pp.
- M6.2 remains PARTIAL. Its first blocker (basis unknown) is now CLOSED; its
  second (nothing left to measure cleanly) is open and is a design decision.
- M6.3 remains NOT STARTED and still dangerous for the reason in CT.4 — the
  ~+100bps figure is drift, and CU makes it additionally untrustworthy for July
  because the reference leg of that comparison no longer exists.

# Appendix CV - CU's forward fix SHIPPED and APPLIED LIVE: every fill now records the raw close it came from, so a rebalance stays measurable after price_cache moves under it (2026-08-05, ~23:34 CDT)

CU proved a fill's reference price is unrecoverable after roughly a month. This
closes that going forward. It recovers nothing historical — July is still gone —
but from the next rebalance on, slippage stops having a shelf life.

## CV.1 What was added

Four nullable columns on `paper_positions`: `entry_ref_close`, `entry_ref_date`,
`exit_ref_close`, `exit_ref_date`.

The **date** is stored alongside the price on purpose.
`last_close_on_or_before` CARRIES FORWARD, so the close a fill used is not always
the rebalance date's — and that is exactly the distinction a later re-derivation
gets wrong while looking perfectly plausible. Storing only the price would leave
the same ambiguity in a new place.

Threaded through `paper_trader.open_position` / `close_position` / `buy` / `sell`
as **optional** keyword arguments, so every existing caller keeps working
unchanged and simply stores NULL. `paper_rebalance` now keeps the `(price, date)`
tuple it was already discarding with `[0]` at both call sites
(`paper_rebalance.py`, the sell loop and the buy loop).

**Purely additive.** No existing column touched, no row rewritten, no arithmetic
changed. These are provenance; if they altered any price, qty, cash or P&L they
would be a defect, and the tests below assert exactly that.

## CV.2 Migration, and the live apply

`scripts/add_fill_reference_columns.py` — dry-run by default, probes with
`mode=ro` first so a dry run never opens the live DB for writing, idempotent on
re-run. `ALTER TABLE ADD COLUMN` is metadata-only in SQLite, so the 5 GB file is
not rewritten.

**Evan ran the live apply himself** (Claude's live-DB writes are refused by the
permission classifier — the standing pattern since record CH):

    scripts.add_fill_reference_columns            -> dry run: 7,192 rows, 16 cols, 4 WILL ADD
    scripts.add_fill_reference_columns --execute  -> ADDED x4

Live state verified read-only immediately after:

| check | result |
|---|---|
| `paper_positions` columns | **20** (was 16), all four present |
| rows / open | **7,192 / 3,222** — unchanged |
| non-null provenance on existing rows | **0** — expected; nothing was backfilled |
| `PRAGMA quick_check` on the 5 GB file | **ok** |
| `verify_run --mode daily` | **PASS (76/76 sleeves OK)** |

One note on the cadence line, which reads
`last_rebalance(2026-08-03/nostatus)`: the 08-03 rebalance predates the
`--status` flag added in the 2026-08-04 audit, and a missing status is
deliberately treated as OK rather than as a failure. Working as designed, not a
gap.

## CV.3 A timing hazard that was real for about ten minutes

Between the code landing and the migration being applied, the new INSERT
referenced columns that did not yet exist — so any rebalance in that window would
have **errored**, and `TradingLadderRebalance` runs the same `paper_rebalance`
path nightly at 20:30. The window closed the same evening (the 20:30 run had
already passed, the next monthly is 2026-09-01), so nothing was hit. Recorded
because the general shape recurs: **a schema-dependent code change and its
migration are not independently safe, and the code half is the one that ships
first.** Apply the migration in the same sitting.

## CV.4 Verification

New `scripts/momentum/test_fill_reference.py`, fixture DBs only, live DB never
touched. It tests the two halves separately:

- **Migration**: dry run writes nothing; apply adds exactly 4 columns; a
  pre-existing row survives intact with NULL provenance; re-running is a clean
  no-op.
- **Capture**: a real `buy()` and `sell()` store provenance while
  `entry_price` / `entry_value` / cash / realized P&L stay bit-identical; the
  round-trip `ref_close * (1 + 5bps)` reproduces `entry_price` exactly and
  `* (1 - 5bps)` reproduces `exit_price` exactly; `entry_ref_date` is the
  CLOSE's date and `entry_date` the fill's, asserted as different values; and a
  legacy call omitting the new arguments still works and stores NULL.

All seven suites touching the fill path pass: `test_fill_reference`,
`test_inception_guard`, `test_trade_atomicity`, `test_carry_forward_bound`,
`test_rebalance_cadence`, `test_fetch_alpaca_fills`, `test_backup_validation`.
Frozen tests **4/4 d=+/-0.0000pp** — v1 +14.5547%/70 & +1.8792%/156,
v2 +14.4062%/38 & +10.2194%/87. Commit `f48d4b7`.

## CV.5 Where M6 stands now

- **M6.1** — done (record CS).
- **M6.2** — PARTIAL. Pairing machinery works. Both blockers are now understood:
  the basis question is CLOSED (CU), and the remaining one is that no existing
  batch is cleanly measurable. **The first rebalance whose fills carry provenance
  will be the first one that can produce a real number** — next monthly
  2026-09-01, or sooner via the nightly ladder, though the ladder is not
  Alpaca-mirrored so it yields provenance without a mirror to compare against.
- **M6.3** — NOT STARTED and still dangerous per CT.4. Nothing here changes that:
  provenance fixes the DATA half, not the TIMING half. The mirror still fills at
  the next open on a monthly rebalance (CS.4), so a September number would still
  be gap-contaminated unless Evan changes the mirror's order type or slot.

**Still Evan's decision, unchanged and now the only thing blocking M6:**
market-on-close mirror orders, an in-session monthly slot, or redefine M6 as
implementation shortfall — defensible, but a different metric than the PRD named,
and worth choosing deliberately rather than by drift.

# Appendix CW - The residual-ladder "inversion" DECOMPOSED: it is not cadence, not turnover, not transaction cost, not R1, not one bad name - the ENTIRE gradient is in the 2026-05-01 stock selection, it is market-orthogonal, and it is ONE MONTH (July, when SPY did +0.03% and momentum did -23.5%) (2026-08-07, ~05:41 CDT)

Ordered by Evan after the 08-06 post-close report flagged the ladder slope
steepening a third day running (monthly -0.0296, weekly -0.0735, biweekly
-0.1435, biweekly corr **-0.940** across 19 rungs). The task as given: *separate
the cadence effect from the weight effect.* That turned out to be the easy part,
and answering it properly exposed that the headline number means something
almost the opposite of how it reads.

**Read-only throughout.** `var/trades.db` opened `mode=ro` on every query. No
sleeve, NAV, price, or log row was written. All analysis scripts live in the
session scratchpad, not the repo.

## CW.0 The claim under test, and the one that was already wrong

The 08-06 post-close report (§6b) said:

> "the cadence and weight effects are confounded in the current design and
> **cannot be separated from this data**."

~~That is correct.~~ **That is WRONG and is retracted here.** The design is
fully crossed and the effects separate exactly. Correcting forward per the usual
convention; the 08-06 report is not edited.

## CW.1 The design is a clean 19x3 crossed factorial, and the three cadences started from IDENTICAL books

Verified against `paper_rebalance.py` `_strategy_config` (the `residual_w`
branch, lines ~80-105) and against the DB:

- **57 ladder sleeves = 19 weights x 3 cadences.** Weights `{5,10,...,95}`,
  identical set in all three cadences (checked, not assumed).
- **The rank function is cadence-independent by construction** - the source
  comment says so and the code strips the `_wk`/`_2wk` marker before parsing the
  four weight digits. Only the *schedule* differs.
- **`starting_cash` = $100,000.00 for all 57.** First `paper_nav` row is
  2026-05-01 for all 57, at $99,950.07-$99,950.13 (the ~$50 = 5bps one-way entry
  cost on ~100% deployment; this pins the sim's cost assumption empirically).
- **At 2026-05-01 the three cadences bought the SAME book at each weight.**
  Checked per weight: identical ticker sets AND identical `entry_value` to the
  cent. The buy-and-hold counterfactual computed below differs by
  **$0.0000** across cadences at every weight - as it must, and now proven
  rather than assumed.

Rebalance events actually executed (distinct `entry_date` per cadence):

| Cadence | events | dates |
|---|---:|---|
| monthly | 4 | 05-01, 06-03, 07-01, 08-03 |
| weekly | 14 | 05-01, 05-04, 05-11, 05-18, 05-26, 06-01, 06-08, 06-15, 06-22, 06-29, 07-06, 07-13, **07-27**, 08-03 |
| biweekly | 8 | 05-01, 05-11, 05-26, 06-08, 06-22, 07-06, **07-28**, 08-03 |

**Two schedule gaps are visible and are recorded, not fixed here:** the weekly
arm has **no 07-20 rebalance** (07-13 -> 07-27), and the biweekly arm's
07-06 -> 07-28 gap is **22 days, not 14**. Both fall in the record-CH /
record-CI window where the ladder dispatcher and the rate-limit backfill were
being repaired, which is the likely cause. Flagged for a later check; it does
not affect any conclusion below because both gaps are *inside* the July window
that turns out to carry the whole effect, and the effect is present in the
monthly arm too, which has no gap.

## CW.2 THE FINDING: the gradient is in the 05-01 selection. Trading did not create it.

Because all three cadences start from an identical book, the decomposition is
exact:

- **Buy-and-hold (BH)** = hold the 05-01 book untouched to 08-06. One curve per
  weight, cadence-independent. This is **pure selection**.
- **Actual - BH** = the entire cumulative contribution of every rebalance. This
  is **pure trading**.

Computed in dollars as `(100000 - invested) + sum(entry_value_i x px_0806_i /
px_0501_i)`, so it is split-invariant by construction (see CW.8).

| Series | slope (pp per weight point) | corr | mean |
|---|---:|---:|---:|
| **buy-and-hold (selection only)** | **-0.1153** | **-0.927** | +3.46% |
| actual, monthly | -0.0296 | -0.648 | +5.66% |
| actual, weekly | -0.0735 | -0.862 | +3.51% |
| actual, biweekly | -0.1434 | -0.940 | +2.75% |
| trading contribution, monthly | **+0.0857** | +0.841 | **+2.20pp** |
| trading contribution, weekly | +0.0418 | +0.658 | +0.05pp |
| trading contribution, biweekly | -0.0281 | -0.509 | -0.71pp |

**The buy-and-hold slope (-0.1153) is STEEPER than the monthly actual (-0.0296)
and about as steep as the biweekly actual (-0.1434).** Doing nothing at all
reproduces essentially the entire headline gradient.

Dollar-weighted, holding the 05-01 book untouched to 08-06: the **low end
(w05-w45) returned +6.67%** and the **high end (w55-w95) returned +0.23%** - a
**6.44pp spread from a single day's stock picking**, with zero trading involved.

The corollary is the answer to the question as asked: **monthly rebalancing has
been net POSITIVE (+2.20pp mean) and helped MORE at high residual weight
(+0.0857/pt); biweekly rebalancing has been net NEGATIVE (-0.71pp).** The
monthly arm's shallower slope is not a property of monthly rebalancing being
better - it is that its three post-inception swaps happened to partially repair
the bad high-weight picks.

## CW.3 The cadence difference is NOT transaction cost, and it is inside one standard error

Turnover (sum of `exit_value` / $100k base) scales almost perfectly with residual
weight - the tightest relationship in the whole dataset:

| Cadence | turnover slope (pp per weight pt) | corr | mean turnover | mean round-trips |
|---|---:|---:|---:|---:|
| monthly | +1.208 | **+0.975** | 101.7% | 45.2 |
| weekly | +2.767 | **+0.981** | 185.6% | 83.9 |
| biweekly | +1.826 | **+0.983** | 134.0% | 60.9 |

**But turnover cannot be the mechanism.** At the empirically-pinned 5bps
one-way (CW.1), a round trip costs ~10bps. The monthly-to-biweekly turnover
differential is ~32pp, i.e. **~0.06pp of cost**, against an observed
trading-contribution differential of **2.91pp**. **Cost explains about 2% of it.**
Note also that weekly has the *most* turnover and is *not* the worst arm - which
alone rules out a monotone cost story.

Per-event "swap alpha" (dollar-weighted forward return to 08-06 of what was
bought minus what was sold at that event; positive = the swap improved the book):

| Cadence | n events | sum | mean | sd | se(mean) |
|---|---:|---:|---:|---:|---:|
| monthly | 3 | +5.35pp | +1.78pp | 3.28pp | 1.90pp |
| weekly | 13 | +0.18pp | +0.01pp | 5.07pp | 1.41pp |
| biweekly | 7 | -2.10pp | -0.30pp | 5.67pp | 2.14pp |

**Every cadence's mean swap alpha is inside one standard error of zero.** The
monthly arm's whole +5.35pp comes from a single event - **06-03, +5.93pp** (the
other two are -2.10 and +1.52). The biweekly arm's two largest events nearly
cancel (**05-11 +10.04pp, 05-26 -10.68pp**). And **weekly and biweekly SHARE the
05-11 and 05-26 events**, so they are not independent samples of each other
either.

**Conclusion on the question as asked: the cadence effect on the ladder slope is
event-timing noise, not a cost or frequency property.** With 3 / 13 / 7 events
and a ~5pp per-event standard deviation, this design cannot currently
distinguish the three cadences at all.

## CW.4 The 19 rungs are not 19 observations

Jaccard overlap of the 05-01 holdings:

- **adjacent rungs (w -> w+5): 0.74 to 0.94.** Neighbours are near-copies.
- **endpoints w05 vs w95: 0.04 - FOUR shared names out of 47 and 49.**
- w05 vs w50: 0.24. w50 vs w95: 0.32.
- Union of all 19 rungs: **114 distinct names**; mean rung size 47.8.

**The ladder is a smooth interpolation between two nearly-disjoint portfolios,
sampled once.** A correlation of -0.940 across 19 such points is what a
*dose-response curve* looks like, not what 19 independent confirmations look
like. **The effective sample is closer to two portfolios in one window than to
19 observations,** and every r-value in this appendix (including the headline
-0.940) must be read that way.

That is not a criticism of the ladder - a dose-response curve is exactly what it
was built to produce. It is a criticism of reading its r-value as significance.

## CW.5 It is one month. And that month was a market-flat momentum unwind.

Weight-slope by sub-period, computed on **stored `paper_nav` rows only** (window
ends 08-05, the last marked day):

| Window | monthly | weekly | biweekly |
|---|---:|---:|---:|
| May (05-01 -> 05-29) | +0.0084 (r +0.20) | +0.0095 (r +0.19) | -0.0071 (r -0.16) |
| Jun (05-29 -> 06-30) | -0.0031 (r -0.07) | +0.0168 (r +0.41) | +0.0165 (r +0.44) |
| **Jul (06-30 -> 07-31)** | **-0.0243 (r -0.40)** | **-0.0934 (r -0.93)** | **-0.1437 (r -0.98)** |
| Aug MTD (07-31 -> 08-05) | -0.0057 (r -0.39) | +0.0098 (r +0.59) | +0.0148 (r +0.74) |
| FULL (05-01 -> 08-05) | -0.0273 (r -0.63) | -0.0666 (r -0.82) | -0.1351 (r -0.94) |

**Everything is July.** May, June and August-to-date are flat-to-positive in
essentially every cell.

**It is not the R1 anomaly.** Excluding the R1 window (07-24..07-30) entirely and
measuring 06-30 -> 07-23, July still slopes negative but far weaker:
**-0.0050 (r -0.11) / -0.0462 (r -0.74) / -0.0666 (r -0.88)**. So the R1 leg is
the single largest contributor but removing it does not remove the effect.

July decomposed into legs, with the high-vs-low spread (mean of w05-45 minus mean
of w55-95, all 57 sleeves):

| July leg | ladder mean | w05-45 | w55-95 | spread |
|---|---:|---:|---:|---:|
| 07-01 -> 07-08 | -4.36% | -2.69% | -5.91% | **+3.22pp** |
| 07-08 -> 07-15 | -0.01% | +0.44% | -0.47% | +0.91pp |
| 07-15 -> 07-23 | -0.55% | -1.62% | +0.53% | **-2.14pp** |
| 07-23 -> 07-29 (R1) | -5.40% | -3.20% | -7.45% | **+4.25pp** |
| 07-29 -> 07-31 (R1) | +4.77% | +3.55% | +5.82% | **-2.27pp** |

**The spread REVERSES SIGN in both rally legs.** The gradient is not a persistent
tilt; it opens in drawdown legs and closes in recovery legs.

And the regime itself, from the sleeves' own stored NAV:

| July 2026 (06-30 -> 07-31) | return |
|---|---:|
| `spy_benchmark_paper` | **+0.03%** |
| `qqq_benchmark_paper` | -6.57% |
| `mom_v1_paper` | **-23.52%** |
| `mom_v2_paper` | **-24.17%** |
| `mom_roa_6535_paper` | **-23.50%** |
| `residual_roa_6535_paper` | -8.88% |
| residual ladder, mean of 57 | -5.77% |

**July was a dead-flat index month in which pure momentum lost a quarter of its
value.** That is a factor unwind, not a market drawdown. The ladder's gradient is
the dose-response curve of that one event: the more residual-momentum weight a
rung carried, the more of the -23.5% it ate.

## CW.6 It survives beta adjustment - and the daily up/down asymmetry runs the FAVOURABLE way

Daily returns, 67 observations (05-01..08-05), regressed on `spy_benchmark_paper`:

| Cadence | beta slope/wt | r | **alpha slope/wt** | **r** | vol slope/wt | r |
|---|---:|---:|---:|---:|---:|---:|
| monthly | +0.00308 | +0.47 | **-0.0929** | **-0.89** | +0.00721 | +0.74 |
| weekly | +0.00600 | +0.79 | **-0.1435** | **-0.91** | +0.00949 | +0.90 |
| biweekly | +0.00684 | +0.80 | **-0.2110** | **-0.96** | +0.01095 | +0.91 |

**Beta does NOT explain it.** Beta is hump-shaped, not monotone - 0.84 at w05,
peaking ~1.53-1.62 around w50-w70, falling back to 1.19-1.47 at w95 - while the
return gradient is monotone. **The CAPM alpha slope is monotone and stronger than
the raw slope (biweekly r -0.96).** The loss is market-orthogonal, which is the
same statement as CW.5's "SPY +0.03%".

The up-day / down-day split (36 SPY up days, 29 down) is the result that most
constrains the interpretation:

| Weight | monthly up / down | weekly up / down | biweekly up / down |
|---|---|---|---|
| w05 | 0.61 / 0.88 | 0.75 / 0.86 | 0.69 / 0.93 |
| w50 | 1.63 / 0.76 | 1.85 / 0.87 | 1.98 / 0.96 |
| w95 | 1.28 / 0.41 | 1.77 / 0.59 | 1.85 / 0.64 |

down-beta minus up-beta, slope on weight: **-0.01335 (r -0.859) / -0.01605
(r -0.919) / -0.01823 (r -0.949)**; the statistic runs from about **+0.25 at w05
to about -1.2 at w95**.

**High-residual-weight rungs have HIGHER up-beta and LOWER down-beta.** On a
daily market-conditional basis that is a *desirable* profile, and they still lost
badly. **Therefore the losses do not arrive on down-market days - they arrive on
days the index is flat or up and momentum falls on its own.** That is a precise,
falsifiable description of what happened, and it matches July exactly.

## CW.7 What this does and does not establish

**Established:**

1. The ladder gradient is **selection at inception**, not trading, cadence,
   turnover, or transaction cost. Buy-and-hold reproduces it (-0.1153, r -0.927).
2. **Rebalancing has been net positive monthly (+2.20pp), neutral weekly,
   net negative biweekly (-0.71pp)** - and all three means are inside one
   standard error of zero over 3/13/7 events.
3. Transaction cost is **~2% of the observed cadence differential**; the sim's
   5bps one-way is empirically confirmed by the $99,950 inception NAV.
4. The effect is **market-orthogonal** (survives CAPM; alpha slope r up to
   -0.96) and **concentrated in July 2026**, a month in which SPY returned
   **+0.03%** while momentum sleeves lost **~23.5%**.
5. Not an artifact of **R1** (survives excluding 07-24..07-30, weakened), not of
   **FGMC** (slope -0.1154 -> -0.1011 ex-FGMC), not of the **KLAC 10:1 split**
   (BH computed in dollars from cache price ratios; KLAC is the only split among
   the 115 distinct 05-01 (ticker, entry_price) pairs and the ratio method is
   split-invariant).

**NOT established, and explicitly not claimed:**

- **This is NOT evidence that Appendix BV's w80-90 holdout plateau was wrong.**
  One factor-regime observation cannot refute a holdout result. The live sweep
  and the backtest disagree; that is a fact about two windows, not a verdict.
- **This is NOT evidence that low-residual/high-ROA is the better blend.** The
  spread reverses sign in both July rally legs and in August to date.
- **The three cadences are NOT distinguishable** in this data. Anyone citing a
  cadence ranking off these sleeves is reading 3-13 noisy events.
- **The 19 rungs are NOT 19 observations** (CW.4). No r-value here should be
  quoted as significance.

**What the ladder IS delivering, and it is genuinely useful:** a live,
correctly-wired dose-response measurement of the residual-momentum/ROA factor
spread. Over 05-01 -> 08-06 that spread ran **6.44pp in favour of ROA**, and the
ladder priced the sensitivity at roughly **0.10-0.14pp of return per weight point
per adverse month**. That is a real sizing number obtained the honest way. It is
the answer to "how much does this dial cost me when it goes against me," not to
"which setting is right."

## CW.8 Method notes and caveats

- **08-06 was UNMARKED** at analysis time (coverage 4,344 < 5,000 floor, sixth
  consecutive session; latest `paper_nav` = 2026-08-05). All 08-06 figures are
  **indicative re-marks** (open positions x official 08-06 `price_cache` closes +
  stored `paper_portfolio.cash`). All 192 held tickers had an 08-06 close, the
  condition under which the two prior re-marks validated at +$0.07 and +$18.65 on
  a $7.9M book. **Every sub-period and daily-regression result in CW.5/CW.6 uses
  stored rows only and ends 08-05**, so those are unaffected either way. DB state
  re-verified unchanged at 05:41 CDT on 08-07 (before the 07:45 heal).
- **Split-invariance.** The BH counterfactual uses dollars:
  `entry_value x (px_0806 / px_0501)`, both prices read from today's
  consistently split-adjusted `price_cache`, so the ratio is split-clean. Checked
  all 115 distinct 05-01 `(ticker, entry_price)` pairs against the cached 05-01
  close: exactly one falls outside [0.99, 1.02] - **KLAC at 10.005x**, the known
  2026-06-11 10:1 split. No other split or restatement in the set.
- **FGMC has no 08-06 close** (it is in the coverage tail; last close 08-05
  $4.44) and is marked there. It was held only at w75-w95 (~$2,039-2,081 each at
  05-01) and returned -56.4%. Removing it entirely moves the BH slope from
  -0.1154 to -0.1011 - materially the same.
- **Dividends.** `price_cache` is dividend-UNadjusted by project convention, and
  the sim does not credit dividends, so BH and actual are on the same basis. Both
  understate total return by the same dividend stream.
- All results reproduce from `var/trades.db` read-only; scripts are in the
  session scratchpad (`lad1.py` .. `lad12.py`), not committed.

## CW.9 Verification

**Frozen regression tests - run 2026-08-07 ~05:38 CDT, actual output:**

```
Running strategy regression tests...
  [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
  [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
  [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
  [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)

All regression tests passed.
```

d = +/-0.0000pp on all four pinned configs. **No repo Python was changed by this
appendix** - the tests are run because the standing rule requires the state to be
proven, not because anything was touched.

## CW.10 Open items this leaves

1. **The weekly arm is missing a 07-20 rebalance and the biweekly 07-06 -> 07-28
   gap is 22 days** (CW.1). Both sit in the record CH/CI repair window. Not
   investigated here; recorded so it is not re-discovered as a surprise.
2. The 08-06 post-close report's §6b "confounded / cannot be separated" claim is
   **retracted** (CW.0). It should be corrected forward in the next daily report,
   not edited in place.
3. The §6b hypothesis in that same report - that shorter cadence suffers more
   because it re-buys freshly-run-up names - is **not supported**: the trading
   contribution is *positive* at monthly and the cadence spread is inside one
   standard error. The mechanism is inception selection, not re-buying.

# Appendix CX - Dependency CVE status DETERMINED without adding a dependency (stdlib OSV, canary-verified), gitpython upgraded to close 18 RCE advisories, and two record corrections - the dead-weight claim was a false negative and hellohello is INTENTIONAL (2026-08-11, ~22:48 CDT)

The 2026-08-04 audit (record CQ) closed with dependency CVE status as **"could
not determine"** - `pip-audit` absent, installing tooling not permitted. That was
the correct thing to write at the time, and it stayed open. This determines it.

## CX.1 Why no new dependency was added

`pip-audit` is a convenience wrapper over public advisory data. The one part that
genuinely needs a library - deciding whether an installed version falls inside an
advisory's affected range under PEP 440 - is done **server-side** by OSV's
`/v1/querybatch`, which takes a concrete version and returns only the advisories
affecting it. Nothing left to reimplement. Installing a scanner would also have
pulled its own dependency tree into the venv, enlarging the surface being
measured, on a project whose complaint is that 97 packages sat behind 9
hand-pinned lines.

New `scripts/check_dependency_cves.py` - stdlib `urllib.request` + `json`, reads
`requirements.lock.txt`. Exit codes 0 / 1 / **2 = COULD NOT DETERMINE**; an
unreachable API is never reported as clean.

Two things make the answer trustworthy rather than merely produced:

- **CANARIES.** `urllib3==1.26.4` and `requests==2.19.1`, both with long-standing
  advisories, ride along in the same query. If a canary comes back clean the
  pipeline is broken - wrong ecosystem string, bad name normalization, changed
  API contract - and "no advisories" would be a FALSE NEGATIVE. Both returned
  hits on every run, so the negatives are verified.
- **PEP 503 normalization.** `pip freeze` emits `curl_cffi`; PyPI calls it
  `curl-cffi`. Querying the un-normalized name returns an empty result
  **indistinguishable from clean** - the exact silent-wrong-answer class.

## CX.2 The finding: 8 packages, 74 advisories, none reachable

OSV cannot know reachability, so it was triaged by hand:

| package | n | reachable? |
|---|---:|---|
| urllib3 2.6.3 | 4 | **LOW but real** - decompression bomb is a DoS on the nightly refresh. The cross-origin header leak needs credentials on the urllib3 path, and Alpaca rides **httpx**, not requests |
| soupsieve 2.8.3 | 4 | **No** - vector is an attacker-controlled CSS SELECTOR, not attacker-controlled HTML; ours are hardcoded |
| gitpython 3.1.49 | 18 | see CX.3 |
| pillow 12.2.0 | 26 | **No** - via streamlit/altair/plotly; the dashboard renders charts from the DB, never decodes untrusted images |
| starlette 1.0.0 / python-multipart 0.0.27 | 18 | **No** - Streamlit binds 127.0.0.1 only (verified in `var/dashboard.log`) |
| h2 4.3.0 | 2 | LOW - smuggling needs a hostile intermediary |
| idna 3.13 | 2 | **No** - needs attacker-controlled hostnames |

soupsieve is the textbook false positive: flagged because the package sits on the
untrusted-input path, but the vector points the wrong way.

**No upgrades were made off this.** A yfinance/pandas/urllib3 bump can change
price-adjustment behaviour and silently move every backtest number - worse than
any unreachable advisory.

## CX.3 A false negative, and the correction

Commit `4a1f69f` asserted gitpython was *"top-level, has no dependents, imported
nowhere in trading_bot/ or scripts/. Dead weight; removal is the cleanest fix."*
**That was wrong.** `streamlit` declares `gitpython!=3.1.19,<4,>=3.0.7` and
`streamlit/git_util.py:75` imports it at runtime, called from
`app_session.py:837`.

Cause: the reverse-dependency one-liner behind that claim split requirement
strings on `"="`, turning `GitPython!=3.1.19` into `GitPython!`, which matched
nothing. **The same commit shipped a scanner canaried specifically so a broken
query could not report a false clean - and the one-liner it reasoned from was not
canaried.** It surfaced only because Evan asked for the removal to be verified
before it was done.

Removal would also not have been durable: `pip install -r requirements.lock.txt`
reinstalls it via streamlit, and uninstalling breaks `pip check`. (It would NOT
have crashed the dashboard - the import sits in a `try:`/`except Exception:` that
logs at DEBUG and names "GitPython not installed" as an expected cause.)

**Upgraded instead**, Evan running the install: **3.1.49 -> 3.1.59** (OSV gives
`fixed: 3.1.51` for the whole cluster). gitpython touches no price path, so the
backtest-drift objection that blocks the other seven did not apply.

Verified after: `pip check` -> *No broken requirements found*;
`import streamlit.git_util` OK with `GitRepo` importable; CVE re-check **8 -> 7
packages** with canaries still hitting; frozen tests **4/4 d=+/-0.0000pp**.
Commits `4a1f69f`, `68eedea`. Findings: `var/dependency_cves_2026-08-11.json`.

## CX.4 Correction: `hellohello` is INTENTIONAL - do NOT delete it

Record CR listed it as *"an ENABLED Claude task firing daily ~8:08am, prompt is
literally `hello (Just say "hi" back)`. **Evan's to delete** - flagged, never
removed."*

**That characterisation is wrong and is corrected here.** Per Evan (2026-08-11):
it is a deliberate lightweight routine whose purpose is to **start the usage-limit
window** at a predictable time each morning. It is doing exactly what it was
built to do.

The record is append-only so CR stands as written. A future session reading CR
alone would delete a task that is load-bearing for Evan's daily workflow -
**this entry is the correction; do not remove `hellohello`.** Same lesson as the
`monthy-llm-rebalance` typo (record CN): an odd-looking name or a trivial-looking
prompt is not evidence of an accident.

## CX.5 Status

- Dependency CVE status: **DETERMINED**, and re-runnable in one command. The
  audit's open M9 item is closed.
- Still open and unchanged: M6.2/M6.3 (blocked on Evan's mirror-timing decision,
  records CT/CU/CV) and CQ.2 finding 2 (the frozen tests still write the live DB;
  the busy-window guard bounds WHEN, not WHETHER).

# Appendix CY - PRD M6 REDEFINED to implementation shortfall (Evan's call): the +100bps is MEASURED to be drift three independent ways rather than asserted, so HALF_SPREAD_BPS stays at 5.0 - plus a canned unpaired-reason that was true 64 times out of 65 (2026-08-11, ~23:25 CDT)

Records CT/CU/CV left M6 stalled on one question that was not the executing
model's to answer: if the mirror never fills at the sim's reference price,
execution slippage is not measurable, so is the goal wrong or is the plumbing
wrong? Evan decided on 2026-08-11: **the goal. M6 measures implementation
shortfall.** This entry executes that decision and closes M6.2/M6.3 on the code
side.

## CY.1 What the redefinition actually is

    shortfall = the sim's BOOKED reference price  vs  the realised mirror fill
                price, drift INCLUDED
                signed so positive = the mirror did worse than the sim
                reported per (rebalance x sleeve x side), NEVER pooled

The arithmetic did not change one character. The *claim being made about the
number* changed, and that is the whole content of the fix: CT.4 stopped M6.3 from
recalibrating `HALF_SPREAD_BPS` 5 -> 100 precisely because a number labelled
"slippage" invites exactly that use. A number labelled shortfall does not.

Why slippage is unmeasurable here, stated once for the future reader:

- The sim books at a **CLOSE** (`last_close_on_or_before x (1 +/- 5bps)`, pinned
  exactly in CU.1).
- 2026-07-07 filled **intraday, 14:20 ET**.
- 2026-08-03 filled at the **next session's open**, 09:30-09:36 ET on 08-04.
- Alpaca **rejects market-on-close orders 15:50-19:00 ET** and queues them to the
  FOLLOWING close after 19:00 ET (Evan). The 08-03 orders POSTed at
  `2026-08-03T23:24:48Z` = **19:24 ET** - past the cutoff, so MOC would have
  bought an extra day of delay, not removed it. There is no order-type flag that
  reaches the same day's auction from an 18:03-local slot; it takes changing when
  the sim prices relative to when the mirror submits.

**One thing worth being explicit about, because CU could easily be read the wrong
way: the CU data loss does NOT block shortfall.** Shortfall needs
`paper_positions.entry_price`/`exit_price`, which are persisted at fill time and
have never been rewritten. What CU proved unrecoverable is the `price_cache`
close those prices were DERIVED from - which is needed to DECOMPOSE shortfall
into spread plus drift, not to measure shortfall. So both batches are measurable
as shortfall and neither is measurable as slippage.

## CY.2 The numbers, per batch, never pooled

| rebalance | sleeve | side | n | mean | median | p95 | min | max |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 2026-07-07 | mom_roa_6535_0701_paper | buy | 50 | +156.0060 | +122.9452 | +381.8753 | -125.7624 | +1470.9289 |
| 2026-07-07 | residual_roa_6535_0701_paper | buy | 48 | +41.9696 | +39.0369 | +324.7726 | -228.0287 | +337.5104 |
| 2026-08-03 | mom_roa_6535_0701_paper | buy | 19 | +396.2302 | +463.1425 | +942.4410 | -830.9591 | +954.2990 |
| 2026-08-03 | mom_roa_6535_0701_paper | sell | 19 | -156.8307 | -285.8599 | +990.9768 | -1364.9059 | +1344.3888 |
| 2026-08-03 | residual_roa_6535_0701_paper | buy | 15 | +183.3875 | +162.0426 | +484.7587 | -74.0111 | +561.7445 |
| 2026-08-03 | residual_roa_6535_0701_paper | sell | 15 | -43.9853 | +23.0228 | +270.6131 | -945.9971 | +316.9342 |

Whole batch: **07-07 n=98 mean +100.1514 median +83.5756 sd 192.1**;
**08-03 n=68 mean +97.6415 median +148.1563 sd 498.7**. 166 of 231 fills paired
(unchanged from CT). All bps.

## CY.3 The part that matters most: drift is MEASURED, not argued

CT.4 asserted these numbers are drift. An assertion is what a future session
overrides. The M6.3 memo now measures it three independent ways, and the third
one is decisive:

| # | measurement | why a spread cannot produce it |
|---|---|---|
| a | cross-sectional **sd 192.1bps (Jul) / 498.7bps (Aug)** around means near +100 | a half-spread is near-constant per name; it would show sd of a few bps |
| b | **20/98 (Jul) and 26/68 (Aug)** fills came out BETTER than the sim | a spread cost is one-signed by construction - you always pay it |
| c | per-name August shortfall vs that same name's overnight close-to-close move (sign-matched to side): **corr = +0.7668, n=68** | a bid-ask spread does not know which direction the stock moved. A timing gap does, by definition |

Two limits stated in the memo rather than smoothed over: the fill was at the
**open** while (c) compares to the next **close**, so the +148.2bps residual is
the open-to-close move and is NOT a spread estimate; and (c) is impossible for
July, whose reference closes are gone (CU.2).

**Conclusion carried into the memo: the true spread is UNMEASURED - not 5, not
100.** That is the actual reason 5.0 should not be touched. "We measured 100" and
"we cannot measure it" lead to opposite actions, and only the second is true.

## CY.4 A canned reason that was true 64 times out of 65

Found while writing the memo, not by an audit. The unpaired bucket gave ONE
explanation to all 65 unpaired fills - "mirror weight adjustment on a name the sim
did not open/close at this rebalance." Checked instead of trusted: for each
unpaired fill, does a sim leg of that side exist on ANY date?

- **64** - no leg of that side at any date. Reason correct: `alpaca_sync`
  reconciles to target WEIGHTS, so it trims and tops up names the sim merely holds
  at a different quantity.
- **1** - `spy_benchmark_0701_paper` SPY buy. Its sim entry is dated
  **2026-07-06** (the cohort inception) while the mirror bought 07-07. That is a
  **date mismatch**, not a weight trim.

The tracker now tells the two apart and names the dates. It still does NOT pair
across the date boundary - loose date matching is the legacy path's defect
(CT.1), and relaxing it to gain one fill would reintroduce it. No number moved;
what changed is that the report no longer explains a finding wrongly. Small, but
it is the same class as CX.3: a plausible one-line explanation that nobody had
fed its own trigger.

## CY.5 What shipped

- `slippage_tracker.py`: `slippage_bps` -> `shortfall_bps` (no external caller,
  verified by `grep -rn`); report header, per-batch composition notes and a
  never-pool warning; the legacy `--report` view now warns when it is pooling
  shortfall rows; `write_slippage_log` labels every row
  `implementation-shortfall ...` in `note` and **skips duplicates** on
  (strategy, ticker, direction, broker_filled_at). The dedupe exists because this
  is a live write Evan runs by hand: a second run is a realistic accident, and
  duplicated rows would distort every later mean without failing anything.
- The step-4 comment block in the module docstring - the deferred real-brokerage
  path at 18 that literally says "bump HALF_SPREAD_BPS to recalibrate" - now
  carries the contemporaneity condition. Same trap, one venue over.
- New `scripts/momentum/test_shortfall_pairing.py`, fixture DB only: sign
  convention both sides, buy->`entry_price` / sell->`exit_price` with the two
  prices set far apart so a wrong-leg pairing cannot pass, the three unpaired
  causes told apart, and write idempotency.
- `docs/slippage_memo_2026-08-11.md` (M6.3). Recommends **no change**.
- `PRD_ROADMAP.md`: M6 section banner, milestone row, success criterion, M6.2 and
  M6.3 amended. M6.3's amendment carries the negative in a blockquote so it
  cannot be skimmed past.

## CY.6 Verification

- Report regenerated read-only; the six per-group rows reproduce CT.3 exactly, so
  the rename moved no number.
- Write proven on a `VACUUM INTO` copy (5,086,871,552 bytes, 1m42s):
  **166 rows written, re-run appends 0 and skips 166**, all 166 labelled. Copy vs
  live row counts identical for `paper_positions` 7,271 / `paper_nav` 4,740 /
  `paper_portfolio` 76 / `price_cache` 37,685,844.
- `test_shortfall_pairing` 6/6 checks pass.
- Frozen tests **4/4 d=+/-0.0000pp** - v1 +14.5547%/70 & +1.8792%/156,
  v2 +14.4062%/38 & +10.2194%/87. Run twice: after the first code batch and again
  after the unpaired-reason fix.
- **Live `slippage_log` is still 0 rows.** The `--execute` run against the live DB
  was attempted and **refused by the permission classifier** (standing behaviour
  since record CH). It is Evan's single command, from `D:\ClaudeCode\Trading`:

      .venv\Scripts\python.exe -m scripts.momentum.slippage_tracker --alpaca-csv var\alpaca_fills_2026-07-01_2026-08-06.csv --execute

  One line, no cmd.exe caret continuations (record CM's note). Re-running it is
  safe: the second run appends 0. Until he runs it, M6.2's done-check is met on a
  copy and NOT on live, and the PRD success criterion stays unticked.

# Appendix CZ - CQ.2 finding 2 CLOSED: the mandated frozen tests no longer write the live DB. Fixed at the NAME-RESOLUTION layer (TEMP tables shadow positions/portfolio_state), not by redirecting the connection - which would have taken price_cache with it (2026-08-12, ~07:20 CDT)

Work spans 2026-08-11 ~23:20 CDT to 2026-08-12 ~07:20 CDT (the session crossed
midnight; code comments are dated 08-12 to match this entry).

CQ.2 finding 2 has been open since the 2026-08-04 audit and was the last item on
CX.5's still-open list. `CLAUDE.md` mandates the frozen regression tests after
ANY python change and separately forbids concurrent `factor_backtest` against the
live DB. The frozen tests **are** a factor_backtest: `test_strategies` ->
`momentum_v1.run()` -> `run_factor_backtest()` -> `_wipe_state()` ->
`DELETE FROM positions` / `DELETE FROM portfolio_state` through a read-WRITE
`connect()` that commits. **The mandated check was the forbidden operation.**

CQ.2 shipped a busy-window guard and said so plainly: it bounds WHEN, not
WHETHER, and 137 residue rows were still sitting in the live DB. This closes the
WHETHER.

## CZ.1 Why the obvious fix does not work

The auditor proposed pointing the backtest at a scratch DB. CQ.2 already rejected
it and the reason is worth restating, because it is what makes this a DB-layer
problem rather than a one-line one:

- `positions`/`portfolio_state` are read and written by `broker.py`,
  `monitor.py`, `portfolio.py`, `multi_backtest.py`, `reporting/dashboard.py`,
  `reporting/report.py` and `scripts/form4/optimize_r15_wf.py`, all through one
  `db.connect()`.
- Redirecting that connection also redirects **`price_cache`** - 37,685,844 rows
  the backtest must read. A scratch DB does not have it.

So the seam cannot be the connection.

## CZ.2 The seam is name resolution

SQLite resolves an **unqualified** table name `temp -> main -> attached`. A TEMP
table named `positions` therefore shadows the real one for every
`... FROM positions ...` already written anywhere in this codebase - **no query
rewritten, no call site touched, no connection redirected** - while `price_cache`
has no shadow and still resolves to `main`.

New in `trading_bot/db.py`:

    shadow_backtest_state()     -> creates the TEMP shadows (idempotent)
    unshadow_backtest_state()   -> drops them, restoring the live view
    BACKTEST_STATE_TABLES        = ("positions", "portfolio_state")

Called from `factor_backtest._wipe_state()`, which already runs first in every
`run_factor_backtest()` - the natural chokepoint, so every momentum path and
every research script inherits the fix without opting in.

**The mechanism was canaried before anything was built on it** (a fixture DB,
main row 'LIVE' + temp row 'TEMP'): unqualified SELECT returned the temp row,
`main.positions` kept its own, `DELETE FROM positions` emptied temp and left main
at 1 row, and reopening the file showed the main row intact.

**One non-obvious detail.** The shadow DDL is copied from the live table's own
`sqlite_master.sql`, NOT from `db.SCHEMA`. `init_db()` adds `entry_date`,
`exit_date`, `peak_close_price`, `split_ratio_at_exit` and `dividends_received`
by defensive `ALTER TABLE`, and `SCHEMA` does not declare them - a shadow built
from `SCHEMA` would be silently missing five columns. The function asserts the
live and temp column lists are equal before returning, so that drift fails loudly
instead of at a random INSERT.

## CZ.3 Verification - including the negative control

Copy-first per `CLAUDE.md`. A `VACUUM INTO` copy (5,086,871,552 bytes) was made,
`trading_bot.db.DB_PATH` repointed at it, and the whole frozen suite run against
it.

| check | result |
|---|---|
| frozen suite on the COPY | 4/4 **d=+/-0.0000pp**, exit 0 |
| temp tables on the connection | `portfolio_state`, `positions`, `sqlite_sequence` |
| `temp.positions` after the run | **137 rows** - the backtest's own state |
| copy's `positions` before -> after | **137 -> 137**, id-sum `97,299,592` unchanged, entry_value-sum `259,234.8099` unchanged |
| copy's `portfolio_state.cash` | `39.26251401921501` unchanged |

A row COUNT alone would have proved nothing here - a wipe-and-rebuild lands on
137 rows again - so the check fingerprints `SUM(id)` too, which moves because
AUTOINCREMENT does not reuse ids.

**NEGATIVE CONTROL (the CQ.4 lesson: a fix never fed its trigger is unverified).**
`shadow_backtest_state` was monkeypatched to a no-op to simulate the pre-fix
code, and one backtest run against the same copy moved it
**(137, 97,299,592, 259,234.8099) -> (170, 120,762,815, 169,143.5573)**. The
check can see a live write. The PASS above is therefore a result, not a
tautology.

**Then live.** Frozen suite against `var/trades.db`:

- 4/4 **d=+/-0.0000pp** - v1 +14.5547%/70 & +1.8792%/156, v2 +14.4062%/38 &
  +10.2194%/87.
- `positions` **(137, 97,477,966, 259,234.8099)** before and after, identical;
  `portfolio_state.cash` `39.262514` both times.
- **`PRAGMA data_version` on an independent read-only connection: 2 before, 2
  after.** SQLite bumps that counter when any other connection commits to the
  file, so this is the strongest available statement: the run wrote **nothing**,
  not merely nothing to those two tables. That instrument was itself canaried on
  the copy - a known one-row UPDATE moved it 2 -> 3.

New `scripts/momentum/test_backtest_state_isolation.py` (fixture DB only) locks
it in: live rows survive a real `_wipe_state()`, a backtest INSERT lands in temp,
nothing persists to the file, **`price_cache` is not shadowed and still reads**,
the shadow is idempotent, its columns match the live table INCLUDING the
ALTER-added ones, and `unshadow` restores the live view. 7/7.

All eight sibling suites re-run green: `test_shortfall_pairing`,
`test_fill_reference`, `test_inception_guard`, `test_trade_atomicity`,
`test_carry_forward_bound`, `test_rebalance_cadence`, `test_fetch_alpaca_fills`.

## CZ.4 What deliberately did NOT change

- **`backtest.py` (the Form-4 walk-forward) is untouched.** `main.py backtest`
  uses it, and `main.py report` / `dashboard` / `positions` read what it leaves
  behind in a LATER process. Shadowing there would break that flow. Checked
  rather than assumed: `grep -rn` finds no reader of `positions` /
  `portfolio_state` under `scripts/momentum/`, and the one hit under `scripts/`
  (`form4/optimize_r15_wf.py:53`) reads it in the SAME process, immediately after
  a `backtest.py` run.
- **The busy-window guard stays**, with its docstring and refusal message
  corrected. It said "These tests WRITE the live DB", which is now false and
  would have been read as truth by the next session. Its justification is
  downgraded from correctness to I/O contention: a run still reads a 5 GB file
  hard with a 500 MB page cache and 256 MB mmap, and there is no reason to do
  that during a scheduled task. Removing it is now a judgement call for Evan, not
  a bug fix.

## CZ.5 The 137 residue rows - REPORTED, not deleted

`positions` holds **137 rows** stamped `entry_time` 2026-08-03T04:36:36Z with
`entry_date` 2025-01-02 (the `2025_H1` frozen window), and
`portfolio_state.cash = $39.262514`. They are the last pre-fix frozen run's
output.

Two consequences, stated rather than fixed:

1. **They are now permanent.** The only thing that used to clear them was the
   next frozen run's `_wipe_state()`, and that no longer reaches the file. Nothing
   else deletes them.
2. **`main.py report` / `dashboard` / `positions` will keep rendering them
   forever** as if they were a current portfolio. They were already stale; now
   they are frozen stale.

Nothing paper-trade lives in these tables (`paper_positions` is untouched at
7,271 rows / 3,222 open), so this is cosmetic, not a data-integrity issue.
**Deleting them is Evan's call and his command** - Claude's live-DB writes are
classifier-refused (standing since record CH). From `D:\ClaudeCode\Trading`, one
line, after a backup:

    .venv\Scripts\python.exe -c "import sqlite3; from trading_bot.config import DB_PATH; c=sqlite3.connect(DB_PATH); print('deleted', c.execute('DELETE FROM positions').rowcount, c.execute('DELETE FROM portfolio_state').rowcount); c.commit(); c.close()"

It is safe to skip entirely. It is also safe to run: a factor backtest no longer
depends on anything in those tables, and re-running it changes nothing.

## CZ.6 Status

- **CQ.2 finding 2: CLOSED.** The mandated check is no longer the forbidden
  operation, and it is proven by `data_version` rather than argued.
- Frozen tests **4/4 d=+/-0.0000pp**, live DB unmodified.
- Still open from CX.5: nothing. M6.2's LIVE `slippage_log` write (record CY.6)
  and these 137 rows are both Evan's commands, not open engineering.

# Appendix DA - Cold audit, first full sweep since CQ: 15 findings + 8 edge cases; the two daily.bat handlers that never reached the exit gate are fixed, the crit is not (2026-08-12, ~17:25 CDT)

**Trigger.** Evan ran `/audit` over every active project. Trading was held back
from the first sweep because another session was editing and running it at
07:14-07:16; it was audited once the tree went quiet (last write 08:24, clean at
`a5e9e49`). This entry records the sweep and the two fixes applied so far.

**The crit is a monitor that retracts a true alarm.** `verify_run.py:215`
reconciles cash against the **latest `paper_nav` row only**; the continuity walk
at `:195-202` asserts date PRESENCE, not value correctness. So a bad older row
becomes permanently invisible once a good newer row lands. It already happened:
`var/verify_report.log` shows FAIL 57/76 at 08-11 07:47, 17:17 and 20:30, then
PASS 76/76 at 08-12 07:46 **with nothing repaired between**. The 19 failing
sleeves are exactly the `residual_w*_wk_paper` set. The bad 08-10 rows are still
in the DB and are now unreachable by the only checker that looks. NOT FIXED —
honest recon needs a ledger replay per date and is sized **M**; a small patch
would only appear to close it.

**FIXED — two `daily.bat` handlers whose failure never reached the exit gate.**
- **Finding 3:** the two overlay `check-invalidation` calls had NO errorlevel
  check at all. A crash there left stops unfired — positions that should have
  exited to cash stay open and NAV is wrong — while the run continued to a PASS
  stamp and Task Scheduler showed green. Before letting this go live I verified
  both modules' `cmd_check_invalidation` return 0 on every normal path, so
  aborting on nonzero cannot fire benignly.
- **Finding 2:** `daily_price_refresh` correctly returns 1, but the `.bat`
  answered with a bare `echo WARNING` and discarded the code, so a stale-price day
  still stamped `verify=PASS`. The code is now captured and threaded into the ops
  stamp's `--note`.

Both use explicit `%errorlevel%` capture rather than `if errorlevel 1`, which is
GREATER-OR-EQUAL and therefore blind to a negative crash code — the same trap this
file already documents for `CATCHUP_RC`.

**VERIFICATION, without touching the 5 GB DB.** File is pure ASCII (one non-ASCII
byte corrupts the whole parse here), every `goto` resolves to a label, and all
four control-flow paths were exercised with stubbed subprocesses: success/exit 0
unchanged; stops-crash/exit 1 with the note; refresh-fail/note threaded; the
pre-existing `mtm_catchup` path unchanged.

**FROZEN TESTS NOT RUN.** The attempt at 17:12 was refused by the suite's own
guard — inside the 17:00-18:30 `TradingDailyMTM` window. It was **not** forced.
A `d=±0.0000pp` run is still owed for this change.

**Commit** `b87f247`. Not pushed.

**STILL OPEN from this sweep** (13 of 15 findings, 8 edge cases): the crit above;
finding 4, LLM decisions are never backdated is UNENFORCEABLE and three decisions
have ALREADY been overwritten (ids 4, 5, 9 missing; id=1 carries
`decision_date=2026-05-29` against `created_at=2026-05-31`); finding 5, `TOL_PCT
= 0.05` while CLAUDE.md and the PRD mandate `d=±0.0000pp`; finding 6, ticker
normalisation divergence between the two overlay twins; E3, the "monthly" LLM
rebalance task actually fires DAILY at 18:03 gated only by a natural-language
check, and `check_rebalance_cadence` structurally cannot detect a mid-month
firing. Real executed-line coverage is **1.7%** (254/15,272 statements, 8 of 195
modules), measured with `sys.settrace` rather than an import-graph proxy.

# Appendix DB - The verify_run crit CONFIRMED BY PREDICTION: FAIL 56/76 on 08-12 evening, PASS 76/76 on 08-13 morning with nothing repaired and 13 sleeves silently recovered; plus two CZ.5 factual corrections and one wrong call of my own, caught before it reached this file (2026-08-13, ~15:22 CDT)

Session instruction was two words of real scope: **"Push then /landing-check"**.
No code was changed. Everything below is either a verification result or a
correction to a prior appendix.

## DB.1 The push was already spent

`git push origin master` returned **`Everything up-to-date`**. Server-side
`refs/heads/master` (read with `ls-remote`, not the cached `origin/master` ref)
already carried the session's HEAD.

This is the "committed does NOT mean unpublished" hazard behaving exactly as
documented: `daily-trade-check` (~08:07 weekdays) and `daily-trade-check-2`
(~19:00) commit their reports and `git push` the whole branch, which publishes
anything left committed on master. Appendices CY/CZ/DA went public that way,
hours before anyone authorized a push. **The authorization was consumed by a
scheduled task before it was given.** Mid-session the branch advanced again to
`fcd4010` (08-13 pre-market daily report, `daily_report.{md,html}` only) and
that too was already pushed.

Nothing here is a defect to fix - it is the designed behavior of the trade-check
tasks. It is recorded because "I have not pushed" is not a safe assumption in
this repo, and a future session should not reason as if it were.

## DB.2 Landing-check verdict: SAFE

A cold agent re-derived every claim in `b2b4fb0..e5366fd` from artifacts and
disk, with no summary of the work handed to it.

- **All 7 changed files LANDED** on the copy that executes. `trading_bot` is not
  installed in site-packages, so no shadowing; each module resolved through the
  venv python reports `D:\ClaudeCode\Trading\...`. The two same-name hits found
  (`.venv/Lib/site-packages/git/db.py`, `.venv/.../pyarrow/tests/test_strategies.py`)
  are unrelated packages, not shadows.
- **Strongest landing evidence**: `daily.bat` was committed 17:14:20 and
  `TradingDailyMTM` fired at 17:15:01. `var/last_daily_run.log` proves the NEW
  file ran - the `:verify_fail` path stamped
  `[OPS 2026-08-12] coverage=PENDING verify=FAIL` and exited 1, matching the
  task's Last Result = 1.
- **15 of 18 extracted claims re-derived TRUE**, including DA's own assertion
  that the crit is *not* fixed: `verify_run.py:195-202` still tests date
  presence and `:213` still takes `navs[-1]`, untouched in the range. A stale
  "still broken" would have been as much a finding as a stale "fixed"; it is
  neither.

## DB.3 CZ.5 CORRECTED - two facts wrong, the mechanism right

CZ.5 states the `positions` residue is "**137 rows** stamped `entry_time`
2026-08-03T04:36:36Z with `entry_date` 2025-01-02".

Both details are wrong. Read from the live DB read-only:

- **No row in any snapshot carries `2026-08-03T04:36:36Z`.** Count of rows with
  `entry_time LIKE '2026-08-03%'` is **0**.
- **`entry_date` is not a single date.** It spans six monthly rebalance dates -
  2025-01-02 (50 rows), 2025-02-03 (19), 2025-03-03 (16), 2025-04-01 (19),
  2025-05-01 (14), 2025-06-02 (19). That is the whole `2025_H1` frozen window,
  which CZ names correctly elsewhere; only the first date of it reached CZ.5.

The row count (137) and `portfolio_state.cash = 39.262514` are correct.

**The mechanism claim in CZ.5 - "they are now permanent, nothing else deletes
them" - is TRUE, and is now positively proven rather than argued.** Four
snapshots, each holding exactly 137 rows with 137 distinct microsecond-resolution
timestamps inside a ~0.25 s burst:

| snapshot | entry_time burst (UTC) | local (CDT) | session that follows |
|---|---|---|---|
| `var/backups/trades_2026-07-28.db` | 19:59:19.68 -> .97 | 07-28 14:59 | CH, ~15:37 |
| `var/backups/trades_2026-08-02.db` | 22:49:56.95 -> 57.19 | 08-02 17:49 | CL, ~17:50 |
| `var/backups/trades_2026-08-09.db` | 08-07 10:40:17.79 -> .96 | 08-07 05:40 | CW, ~05:41 |
| live `var/trades.db` | 08-12 04:15:15.72 -> .94 | 08-11 23:15 | CY, ~23:25 |

Every burst is a wipe-and-rewrite of the whole table minutes before a session
that ran frozen tests - i.e. `_wipe_state()` on the **pre-fix** suite, exactly
the writer CZ identified. **All four predate the CZ fix (08-12 ~07:20 CDT).**

The negative control: a full frozen run executed this session at
**2026-08-13 ~15:20 CDT** left `entry_time` still at `2026-08-12T04:15:15Z`,
unchanged. The pre-fix suite would have rewritten it. The fix holds, confirmed
by a post-fix run rather than by the same `data_version` argument CZ used.

**Consequence for the queued command:** CZ.5's optional `DELETE FROM positions`
is valid and durable. Nothing rewrites those rows any more.

## DB.4 A wrong call of my own, caught before it reached this file

Working from the four-snapshot rewrite pattern in DB.3 and *before* checking
those timestamps against the fix date, I told Evan mid-session that the delete
command was **futile** - that something still rewrote the table and the rows
would come back - and hypothesized a `factor_backtest` TEMP-shadow leak into
`main.positions`.

That was wrong. All four bursts predate the fix; the shadow leak is not
happening; the delete is durable. The error was reasoning from a real pattern
without testing it against the one date that discriminated the two explanations.
Recorded because DB.3's table reads like evidence of an active writer until the
fix date is laid over it, and a future session re-deriving this should not have
to re-make the mistake.

## DB.5 CZ.4's "no reader" claim is now literally false, harmlessly

CZ.4 states `grep -rn` "finds no reader of `positions` / `portfolio_state` under
`scripts/momentum/`". That was true when written and is false now:
`scripts/momentum/test_backtest_state_isolation.py` - added by the same commit -
reads both. It operates on a throwaway fixture DB, so nothing follows from it.
Corrected for the record only.

## DB.6 THE CRIT, CONFIRMED BY PREDICTION

DA sized the `verify_run` recon crit M and left it open. The session handoff made
a falsifiable prediction from it: *the 07:45 morning run may report PASS 76/76
with nothing repaired, and a morning PASS is NOT resolution.*

Read from `var/verify_report.log`, the project's own accumulated report -
FAIL counts per run, every run in the file that had any:

| run | FAIL |
|---|---|
| 2026-07-09 18:04 | 17 |
| 2026-07-29 07:47 / 17:17 / 20:30 | 8 / 9 / 9 |
| 2026-08-02 16:21 / 17:18 / 19:56 | 15 / 21 / 41 |
| 2026-08-11 07:47 / 17:17 / 20:30 | 19 / 19 / 19 |
| **2026-08-12 07:46** | **0 - PASS 76/76** |
| 2026-08-12 17:18 / 20:30 | 20 / 20 |
| **2026-08-13 07:47** | **0 - PASS 76/76** |

**The prediction held.** `var/last_morning_run.log` at 2026-08-13 07:47:11 reads
`RESULT: PASS (76/76 sleeves OK)` with **zero `[FAIL]` lines**, after FAIL 56/76
at both 17:18 and 20:30 the evening before, with no repair performed by anyone
in between.

The sharper finding is what the set membership shows. Comparing the failing
sleeves at 08-11 07:47 (19) against 08-12 17:18 (20): **common = 6**. So

- **13 sleeves failed on 08-11 and passed on 08-12 with nothing repaired** -
  all of them `_wk`: `residual_w{3565,4060,4555,5050,5545,6040,6535,7030,7525,
  8020,8515,9010,9505}_wk_paper`.
- 14 sleeves were newly failing on 08-12.

A checker whose failing set turns over by two thirds in 24 h, with no
intervention, is not reporting the state of the ledger. It is reporting the
state of **one row** - `navs[-1]` at `verify_run.py:213` - and the continuity
walk at `:195-202` cannot catch the difference because it asserts date
*presence*, not value correctness. One good newer row makes every bad older row
permanently invisible.

This upgrades the crit from "observed once" (DA) to **predicted in advance and
reproduced**, which is the standard CQ.4 sets for trusting a checker at all.
The bad 08-10 rows are still in the DB. Fixing it is Task 1 of the next work
block and is unstarted.

## DB.7 Collateral still open

1. **`scripts/momentum/morning_refresh.bat:26` still carries DA finding 2
   verbatim** - `if errorlevel 1 echo WARNING: refresh failed; catch-up may use
   stale prices.` Bare echo, return code discarded. It is a live scheduled task
   (`TradingMorningMTM`, 7:45am). Not a copy-paste of the `daily.bat` fix: that
   script has no `ops_stamp` call to thread a note into, so it needs a decision,
   not a patch. `rebalance.bat:24` handles the same call correctly (hard abort).
2. **`HANDOFF.md` was never synced for Appendix DA** - still stamped
   `Last updated: 2026-08-12 ~07:25 CDT` (the CZ session), with no mention of the
   cold audit, the `daily.bat` change, or the crit. `HANDOFF.md:480` still
   describes `verify_run`'s cash recon with no caveat that it covers only the
   newest NAV row. Project CLAUDE.md definition-of-done item 4 covers exactly
   this.
3. `TradingLadderRebalance` returned exit **1** at 08-12 20:30 (its embedded
   `verify_run` FAILed). Same root cause as DB.6, noted separately because the
   task result is a second, independent surface for it.

## DB.8 Status

- Frozen tests **4/4 d=+/-0.0000pp**, run this session at ~15:20 CDT, exit 0:
  v1 +14.5547%/70 and +1.8792%/156, v2 +14.4062%/38 and +10.2194%/87.
- `positions` unchanged by that run - CZ fix confirmed holding post-fix.
- No code changed this session. Working tree clean; HEAD `fcd4010` = origin.
- **Open, unstarted**: the DB.6 crit (Task 1), the 08-12 residual-ladder FAIL
  diagnosis (Task 2), and 13 of DA's 15 findings plus its 8 edge cases.

# Appendix DC - The verify_run alarm is INVERTED: there are no bad 08-10 rows, check (b) measures nightly price_cache revision rather than the ledger, and the 846 per-date cash divergences are the M7.3 KLAC repair to the cent (30/30). Task 1's canary premise is falsified; Task 2 answered by the same mechanism (2026-08-13, ~21:50 CDT)

Task 1 was to replace `verify_run`'s latest-row-only cash recon with an honest
per-date ledger replay, and to prove the new checker FAILS on the known-bad
2026-08-10 rows (record DA crit, restated in the session handoff). The
investigation falsified the premise before any code was written. **No production
code changed this session; every query below ran against `mode=ro`.**

## DC.1 There are no bad 08-10 rows

Every per-date invariant that does NOT depend on mutable `price_cache` passes on
them. Across **all 4,892 `paper_nav` rows**, all 76 sleeves:

| invariant | violations |
|---|---|
| I1 `cash + positions_value == total_nav` (internal arithmetic) | **0** |
| I3 `n_open_positions` vs ledger replay | **1** |
| I4 `positions_value == 0` iff `n_open == 0` | **0** |
| cash vs ledger replay, on 2026-08-10 / -11 / -12 | **0 / 0 / 0** |

The single I3 violation is `llm_overlay_sector_top4_paper` @ 2026-07-28
(stored n=3, replay n=2) - the XLK invalidation-stop ordering artifact already
identified and explained in CK.3. It reproduces exactly, which is a useful
positive control on the replayer.

The 08-10 rows themselves are unremarkable, e.g. `residual_w0595_wk_paper`:

    2026-08-07 cash= 1.1752 pv= 104215.76 nav= 104216.94 n=49
    2026-08-10 cash= 0.0012 pv= 103768.61 nav= 103768.61 n=50
    2026-08-11 cash= 0.0012 pv= 103400.15 nav= 103400.15 n=50

Internally consistent, ledger-consistent, with the 08-10 rebalance (49 -> 50
positions, cash spent) correctly reflected.

**Task 1b as specified is unsatisfiable.** A cash checker cannot be made to fail
on rows whose cash is correct. Building one and declaring the crit closed would
have been precisely the "small patch that only appears to close it" DA warned
against.

## DC.2 What check (b) actually measures

`verify_run.py:215-236` is not a cash reconciliation. It takes **current**
`paper_portfolio.cash` plus **current** open positions, reprices them with
**today's** `price_cache` as of the latest stored nav date, and compares the
result to that row's stored `total_nav`:

    recomputed = paper_portfolio.cash + SUM(qty x last_close(ticker, latest))
    diff       = recomputed - paper_nav.total_nav[latest]

Per CK.4, `daily_price_refresh.py` re-downloads the last 30 days for every cached
ticker with `INSERT OR REPLACE`, deliberately. So every close inside a rolling
30-day window is overwritten nightly. Any such revision makes `recomputed`
disagree with the row that was written before it - **and the disagreement is the
revision, not an error.**

Proven by reproducing the reported deltas exactly, from a cold read:

| sleeve | run that reported it | stored `total_nav` | repriced now | delta | verify_run said |
|---|---|---|---|---|---|
| `residual_w0595_wk_paper` | 08-11 07:47 | 103,768.61 | 103,742.87 | **-25.73** | -25.73 |
| `residual_w1090_wk_paper` | 08-11 07:47 | 105,492.03 | 105,468.20 | **-23.82** | -23.82 |
| `mom_v1_paper` | 08-13 17:17 | 90,624.24 | 90,758.26 | **+134.02** | +134.02 |
| `mom_roa_6535_paper` | 08-13 17:17 | 94,001.03 | 94,176.19 | **+175.15** | +175.15 |

Four for four, to the cent, across two different nights and two unrelated sleeve
families.

**The mechanical loop, closed:** at 21:49 on 08-13 the newest `paper_nav` row is
still **2026-08-12** - the 08-13 row is PENDING until the 07:45 heal (the
settled-day logic at `:199-202`). So the 17:15 run reprices *today's revised*
cache against *yesterday's stored* row and fails. The 07:45 morning refresh then
writes rows with current prices, the newest row agrees with current prices, and
the run passes. That evening the cycle repeats.

## DC.3 The alarm is inverted

DA framed the crit as *"verify_run retracts true alarms"*, and the handoff as
*"it is actively lying to you right now"*. Half of that is right. The lying is
real; the direction is backwards.

**The crit is a genuine code defect.** `latest = navs[-1]` at `:218` means one
row is checked, and the continuity walk at `:199-207` asserts date *presence*,
not value correctness. A genuinely bad older row WOULD be invisible. That is
worth fixing on its own merits.

**But the observed FAIL/PASS flapping is not that defect.** It is check (b)
generating false alarms and then clearing them. Evidence, all read from
`var/verify_report.log` and tonight's task logs:

| run | result |
|---|---|
| 2026-08-11 07:47 / 17:17 / 20:30 | FAIL 57/76 (19 sleeves) |
| 2026-08-12 07:46 | PASS 76/76 |
| 2026-08-12 17:18 / 20:30 | FAIL 56/76 (20 sleeves) |
| 2026-08-13 07:47 | PASS 76/76 |
| 2026-08-13 17:17 / 20:30 | FAIL 55/76 (21 sleeves) |

Set membership is the tell:

- 08-11 (19) vs 08-12 (20): **common = 6**. Thirteen `_wk` sleeves failed then
  passed with nothing repaired.
- 08-12 (20) vs 08-13 (21): **common = 0**. Complete turnover in 24 h, and
  tonight's failures are `mom_*` sleeves - not the residual ladder at all.

A checker whose failing set has zero overlap night to night, with no
intervention, is not reporting the state of the ledger. It is sampling which
tickers yfinance revised that night.

**This also answers Task 2.** The 08-12 residual-ladder FAIL (deltas
+$0.14..+$0.35) needs no separate cause: same mechanism, different night's
revisions. It is not the CL.6 signature and needs no `remark_nav_day`. Nothing
is broken, so there is nothing to repair.

## DC.4 The 846 per-date cash divergences are the KLAC repair, exactly

A per-date replay of stored `paper_nav.cash` against
`historical_state.state_at()` flags **846 of 4,892 rows** across ~30 sleeves,
all in July. They are not a defect.

Cause: M7.3 (recommended CK.5, applied live CM on 2026-08-02) repaired the closed
KLAC positions and the sleeves' CURRENT cash, and **deliberately left historical
`paper_nav` rows alone**. The replay therefore books repaired `exit_value`s while
the stored July rows carry pre-repair cash.

Verified against the pre-repair backup `var/backups/trades_2026-07-28.db`:

- closed KLAC rows: 34 pre-repair -> 35 live; **30 had `exit_value` changed**,
  total delta **+$83,711.69**; 54 sleeves ever held KLAC.
- For each affected sleeve, the observed per-date cash divergence equals that
  sleeve's repair delta: **30 sleeves compared, 30 MATCH, 0 MISMATCH**, to the
  cent (e.g. `residual_w3070_paper` repair +2,885.48, observed +2,885.48).

The replayer itself is sound: for `residual_w3070_paper` the replay at the latest
nav date reproduces live `paper_portfolio.cash` at **19.863751 vs 19.863751,
delta -0.000000000**.

**Consequence for the design:** a naive per-date cash checker would emit 846
failures every day, forever, for a state Evan explicitly chose. Shipping it would
replace a checker that cries wolf nightly with one that cries wolf permanently.

## DC.5 Proposed fix - NOT yet built, Evan's call taken as "build it"

Split check (b) into two honest checks:

- **(b1) LEDGER - hard FAIL.** Per-date stored `paper_nav.cash` vs
  `historical_state.state_at()`, scoped to the post-repair epoch
  (`nav_date >= 2026-08-03`) or carrying the KLAC deltas as an explicit, cited
  allowlist. Immune to price mutability. A bad old row stays failed on every
  subsequent run instead of being masked by `navs[-1]` - which is the actual
  content of the DA crit.
- **(b2) PRICE DRIFT - demote to INFO.** Keep the existing repricing comparison
  but stop calling it a failure, since it measures by-design mutability (CK.4).
  Report the magnitude so a genuinely large drift is still visible.

**Canary (replacing the unsatisfiable 1b):** fault injection on a `VACUUM INTO`
copy - corrupt a known cash row, prove (b1) FAILS on it, prove it PASSES on the
unmodified copy. That proves the instrument can see a positive, which is the real
requirement behind 1b and behind CQ.4.

## DC.6 Status

- Frozen tests **4/4 d=+/-0.0000pp** (run this session ~15:20 CDT, exit 0);
  `positions` unchanged by that run, confirming the CZ fix holds post-fix.
- No production code changed. No DB writes. Working tree carries only this
  record entry and its HTML twin.
- **Open**: build (b1)/(b2) per DC.5; `morning_refresh.bat:26` (DA finding 2,
  DB.7); HANDOFF.md unsynced since CZ - now two appendices stale; 13 of DA's 15
  findings and its 8 edge cases.
- **Superseded**: DA's crit description and the handoff's Task 2 framing. The
  crit's code defect stands; its stated symptom and its canary do not.

# Appendix DD - The DA crit is CLOSED: verify_run check (b) split into (b1) per-date ledger cash as the hard FAIL and (b2) price drift as INFO, canaried by fault injection on a copy - a corrupted OLDER row now FAILs while the newest row stays clean, which is exactly what the old navs[-1] check could not see (2026-08-13, ~21:59 CDT)

Built the fix designed in DC.5, on Evan's instruction. This is the engineering
half of DC; read DC first for why the old check was wrong.

## DD.1 What changed - `scripts/momentum/verify_run.py`

One file, +53/-13 lines (`git diff --numstat`). Check (b) became two checks:

- **(b1) LEDGER CASH - hard FAIL.** For EVERY `paper_nav` row since
  `LEDGER_EPOCH`, stored `cash` must equal the entry/exit ledger replayed to that
  date. Uses the existing `historical_state.load_history` / `state_at` (record
  CK.1) - **no second replayer was written**, per the task's own constraint.
  Because it walks every row rather than `navs[-1]`, a bad row stays failed on
  every later run instead of being masked by one good newer row.
- **(b2) PRICE DRIFT - reported, never failed.** The old computation is kept
  verbatim for its diagnostic value but no longer appends to `fails`. It
  reprices CURRENT positions with TODAY's cache as of the latest nav row, so it
  measures how far `price_cache` has been revised since that row was written -
  by-design behavior (CK.4), not an error.

The per-sleeve info line changed shape accordingly:

    continuity(71/71) ledger(9/9) drift($+54.86) preinc(0) pos(44/50)

`recon(delta $x)` is gone; `ledger(ok/total)` and `drift($x)` replace it. Anything
parsing the old token will need updating - nothing in-repo does.

## DD.2 The epoch was MEASURED, not assumed

`LEDGER_EPOCH = "2026-07-31"`.

Rows before it legitimately disagree with the replay - M7.3 (CK.5, applied CM
2026-08-02) repaired closed KLAC positions and current cash while deliberately
leaving historical `paper_nav` alone (DC.4). Checking them would emit **846**
known, chosen failures on every run.

The boundary was derived by scanning all 4,892 rows rather than reasoned from the
repair date: **the last divergent `nav_date` is 2026-07-30, and every date from
2026-07-31 is clean on all 76 sleeves.** 2026-07-31 is the row CM re-marked. The
obvious guess - the 08-03 rebalance - would have been wrong by two trading days
and would have silently skipped two rows from the checked window.

**Known limitation, stated rather than hidden:** the epoch is a hardcoded date.
It is correct today and carries a comment citing CK.5/CM, but if the pre-epoch
history is ever repaired the constant becomes stale and will quietly under-check.
Deriving it at runtime was considered and skipped - it would mean re-deriving the
KLAC repair delta on every run, and a wrong auto-derivation fails silently in the
same direction. Flagged to Evan at build time.

## DD.3 Canary - fault injection, replacing the unsatisfiable 1b

Task 1b asked for proof the checker FAILs on the known-bad 08-10 rows. DC.1 showed
those rows are not bad, so that canary cannot exist. The requirement behind it -
CQ.4's "prove the instrument can see a positive before trusting its zero" - was
met by fault injection on a `VACUUM INTO` copy instead.

The injected fault is deliberately the one DA feared: **corrupt an OLDER row and
leave the newest row clean**, so a `navs[-1]` checker sees nothing.

| step | result |
|---|---|
| unmodified copy | **PASS 76/76**, `ledger(9/9)` on every sleeve, exit 0 |
| `residual_w0595_wk_paper` @ 2026-08-04, cash +$1000.00 | |
| `mom_v1_paper` @ 2026-08-06, cash -$250.25 | |
| injected copy | **FAIL 74/76**, exit 1 |

Exactly the two corrupted sleeves failed, each naming its date and delta:

    [FAIL] mom_v1_paper             continuity(71/71,+2hol) ledger(8/9) drift($+134.02) preinc(0) pos(100/100)
             - ledger cash: 1 row(s) since 2026-07-31 disagree with the entry/exit replay (e.g. 2026-08-06(+250.2500))
    [FAIL] residual_w0595_wk_paper  continuity(71/71) ledger(8/9) drift($+0.00) preinc(0) pos(50/50)
             - ledger cash: 1 row(s) since 2026-07-31 disagree with the entry/exit replay (e.g. 2026-08-04(-1000.0000))

**The load-bearing line is `residual_w0595_wk_paper`'s `drift($+0.00)`.** Its
newest row is untouched and its drift is zero - the old check read that row and
nothing else, so it would have reported PASS on a sleeve carrying a $1,000 ledger
error. The new check fails it. That is the DA crit, demonstrated closed rather
than argued closed.

Reproduction (the copy was deleted after the run; ~90 s to rebuild):

    VACUUM INTO 'var/canary/trades.db' from a mode=ro connection
    UPDATE paper_nav SET cash=cash+1000 WHERE strategy_name='residual_w0595_wk_paper' AND nav_date='2026-08-04'
    .venv\Scripts\python.exe -m scripts.momentum.verify_run --mode daily --db var\canary\trades.db

The copy must live in its OWN directory: `verify_run` writes its report to
`db_path.parent / "verify_report.log"`, so a copy placed directly in `var/` would
append to the live ops log. Confirmed isolated - `var/verify_report.log` stayed
at 829,258 bytes / 20:30 across all canary runs.

## DD.4 Effect on the live nightly result

The same live snapshot that produced **FAIL 55/76** at 17:17 and 20:30 today
produces **PASS 76/76** under the new checks, with the drift still visible and
some of it large (`residual_w9505_wk_paper` `drift($+316.83)`). Nothing was
repaired between those two results - the difference is entirely that a by-design
price revision is no longer being called a failure.

This is the intended outcome, and it is also the thing to watch: the nightly
signal goes quiet. If it stays quiet forever that is correct, but DD.3's canary
is the only evidence the gate can still fire, so it should be re-run after any
change to `historical_state.py` or the `paper_nav` writers.

## DD.5 Verification (real output)

Frozen tests **4/4 d=+/-0.0000pp**, exit 0, run 2026-08-13 ~21:57 CDT:

    [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
    [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
    [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
    [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)

    All regression tests passed.

- `CASH_RECON_TOL` removed - my change orphaned it (its only consumer was the
  deleted FAIL branch); 0 references remain repo-wide, module compiles and
  imports clean. Pre-existing dead code was left alone.
- End-to-end re-run on the final code after that removal: FAIL 74/76, exit 1,
  same two rows named.
- No live DB writes. The 4.8 GB `var/canary/` copy created for the canary was
  removed; 1.2 TB free.

## DD.6 Status

- **DA crit: CLOSED**, by demonstration (DD.3), not by widening a window.
- **Task 2: answered** in DC.3 - no repair needed, nothing was broken.
- Open: `morning_refresh.bat:26` (DA finding 2, DB.7); HANDOFF.md; 13 of DA's 15
  findings and its 8 edge cases; the `LEDGER_EPOCH` staleness risk in DD.2.
- Not pushed. Evan has not authorized a push of this work - but note DB.1: the
  weekday `daily-trade-check` tasks push the whole branch, so a commit left on
  master publishes itself.

# Appendix DE - Scheduled daily-audit: DA's morning_refresh.bat/cache_gap gaps closed, HANDOFF's scheduled-task table re-synced, DD's own work committed (2026-08-16, ~13:21 CDT)

## DE.1 What ran

The `daily-audit` scheduled task (undocumented until this entry - see DE.3)
ran a cross-project cold audit, then Evan replied "do all" to the findings.
This entry covers the Trading fixes only; Swing Trading, World Models
Research, Autonomous Car Project, ServeLocal, and the two portfolio landing
repos each got their own fixes this same pass, recorded in their own
projects.

## DE.2 Fixes applied

**T-1 - DD's own work committed.** Appendices DB/DC/DD plus the `verify_run.py`
rebuild and the pre-commit-hook delegation fix sat uncommitted for 3 days
(last non-daily-report commit was `e5366fd`, DA). Frozen tests re-verified
GREEN before committing (DE.4). Committed, not pushed - same standing
DB.1/DD.6 caveat.

**T-2 - `morning_refresh.bat` gets the DA-finding-2 fix daily.bat already had.**
Line 26 was a bare `echo` on refresh failure - nothing captured or propagated
the return code, and the file never called `ops_stamp.py` at all, so a failed
7:45am refresh left zero artifact anywhere. Now mirrors `daily.bat`'s
`REFRESH_RC`/`REFRESH_NOTE` pattern and calls `ops_stamp` on both the
verify-PASS and verify-FAIL paths, `goto`-based per the file's own
delayed-expansion note. Verified in isolation (not live - `mtm_catchup`
writes real MTM marks, and this control-flow change didn't need a live run to
prove correct): a stand-in copy with fake return codes confirmed all three
cases - refresh-fail/verify-pass, refresh-ok/verify-fail, both-ok - propagate
the right task exit code and note text.

**T-4 - `check_cache_gaps` is now actually scheduled.** Documented "re-run
monthly (M2.4)"; nothing scheduled it and `var/cache_gap_report.log` sat at
its one-off 2026-07-09 run for 38 days - UNENFORCEABLE. Wired into
`daily.bat`, gated on day-of-month via a Python one-liner (not cmd.exe's
locale-dependent `%DATE%` - see `ops_stamp.py`'s own docstring for why this
project avoids that parsing) rather than a separate scheduled task, so it
can't drift the way `monthy-llm-rebalance`'s cron already has three times.
Report-only, same non-blocking contract as the anomaly scan beside it.
Verified: the guard correctly returns 1 (skip) on today, 2026-08-16 (day 16);
a stand-in with a faked day=1 confirmed the run branch fires.

**T-5 - HANDOFF's scheduled-task table re-synced against the live list,
re-confirmed twice this session.** `daily-trade-check` is `0 7 * * 1-5`, not
`0 8`; the stray test task is `hellllo` (three L's) at `0 12 * * *`, not
`hellohello` at `0 8`; a SECOND, previously undocumented stray task
`hello-just-say-hi-back` fires `0 17 * * *` - 10 minutes before
`TradingDailyMTM`; `daily-audit` itself (the task that found this) was live
but absent from the table; `cohort-0706-deploy` is correctly documented as
disabled, not absent as an earlier read of this entry's own draft claimed.

**Not fixed, on inspection:**
- **T-3 (proposed: retain check_anomalies evidence) - SKIPPED, the premise
  was wrong.** The audit read `var/anomaly_report.log`'s CFNB entries as
  losing their evidence once `price_cache` gets overwritten by the next
  `daily_price_refresh`. Re-reading the log format: each header line already
  states `close=<date>`, and each `MOVE` line already carries ticker, percent
  move, and the before/after price - `MOVE  CFNB  +4112.1%  $33.9500->$1430.0000`.
  That is the full reproducible state (ticker, date, price) in text form
  already. The gap is that it isn't machine-queryable, a usability
  improvement, not the evidence-loss bug originally described. No fix
  applied; flagging the corrected understanding instead of a redundant patch.
- **T-6 (137 residue `positions` rows, `portfolio_state.cash=$39.262514`) -
  BLOCKED-ON-EVAN, unchanged.** Per CZ.5/DD, this needs a live `DELETE`
  against `trades.db` - Claude's live-DB writes are classifier-refused on
  this project by standing design, and CLAUDE.md reserves NAV/DB history
  edits for Evan regardless. Still a one-line command on his side.

## DE.3 Live scheduled tasks, re-confirmed via the tool (not this table)

Per the standing rule (`monthy-llm-rebalance` has drifted 3x), read live:
`daily-audit` - `0 7 * * *`, enabled, last ran 2026-08-16. Not previously
documented anywhere in this repo; it is the task that produced this entry.

## DE.4 Verification

- Frozen tests, re-run before committing DD's pending `verify_run.py` change:
  `.venv\Scripts\python.exe -m trading_bot.strategies.test_strategies` ->
  all 4 configs d=±0.0000pp, "All regression tests passed."
- `morning_refresh.bat` and the `daily.bat` T-4 addition: control-flow
  verified via stand-in `.bat` files with faked return codes (DE.2), not a
  live run - no live-DB write was needed to prove the branching correct, and
  running the real files would have triggered a live `mtm_catchup` mark
  outside this task's scope.
- No live DB writes this entry.

## DE.5 Status

- T-1, T-2, T-4, T-5: closed.
- T-3: withdrawn as a finding (premise was wrong).
- T-6: BLOCKED-ON-EVAN, unchanged, one line for him to run.
- Not pushed - Evan has not authorized a push; DB.1's push-on-commit caveat
  still applies to the two weekday Claude tasks.

# Appendix DF - Correction to DE.1: the wrong commit was cited as "last non-daily-report" (2026-08-16, ~13:38 CDT)

A post-fix `/landing-check` on DE's own commit caught a small citation error:
DE.1 named `e5366fd` as "the last non-daily-report commit" before this
entry's work landed. `e5366fd` is itself a Daily-report commit
(2026-08-12 19:16:32, "post-market close analysis entry"). The actual last
non-daily-report commit was `e96c5fe`, "Record Appendix DA" (2026-08-12
17:27:29) - two hours earlier, and the correct one. Confirmed by re-reading
`git log` for both hashes directly. Doesn't change anything DE fixed or
verified - only the one sentence identifying which commit preceded the
uncommitted work.

# Appendix DG - Landing-check on DE found two of its fixes did not hold: the day-1 cache-gap gate was a cmd.exe no-op (ran DAILY 08-16..08-18) and the "re-synced" task table missed a cron that had drifted back into the MTM window. Both fixed. Plus DA finding 4 CLOSED: the three lost LLM decisions were destroyed by INSERT OR REPLACE, not by hand - writers are plain INSERT now and the tables are append-only at the DB layer, canaried 15/15 (2026-08-19, ~00:05 CDT)

Evan: "find any outstanding work (no hallucinating) then use /landing-check with
/opus-workers", then "do all". The outstanding work was found by running a
landing-check on the previous session's commits (`7cd7b28`, `4757330`, record
DE/DF); a cold Opus worker did the sweep and every load-bearing finding below was
re-derived by hand before it was acted on. Session ran ~18:20 CDT 08-18 to ~00:05
CDT 08-19 (long gaps - clock read at each step).

## DG.1 DE's T-4 gate never gated: `check_cache_gaps` ran every day

DE T-4 wired `check_cache_gaps` into `daily.bat` "gated on day-of-month" and
recorded the gate as verified. It was not. The block form was:

    if not errorlevel 1 (
      echo.
      echo === Monthly cache-gap audit (non-blocking; day 1 of month) ===
      .venv\Scripts\python.exe -m scripts.momentum.check_cache_gaps
    )

cmd.exe closes a parenthesized block at the first unescaped `)` - which here is
the one inside the echo text. So the two `echo` lines were the block (skipped
on non-day-1) and the `check_cache_gaps` line fell OUTSIDE it and ran
unconditionally. Evidence, all from disk:

- `var/cache_gap_report.log` has dated blocks on **2026-08-16, 08-17, 08-18** -
  days 16, 17, 18.
- The banner `=== Monthly cache-gap audit` appears **0** times in
  `var/last_daily_run.log`; the sibling `=== Anomaly scan` banner appears 1 time
  (the canary that proves the grep can see banners).
- DE's own verification tested the Python one-liner's exit code (correct: 1 on
  a non-day-1) and a stand-in with a faked day=1 - it never exercised the
  non-day-1 `.bat` path, which is the only path that was broken.
- The 08-17 scheduled daily report already journaled the misfire as "the
  scheduled cache-gap audit also ran for the first time".

**Fix:** the block is replaced with the file's own `goto` idiom (its header
mandates `goto`, not blocks, precisely because of `%VAR%` parse-time expansion;
T-4 broke the file's own rule). Verified with three stand-ins built from the
exact patched lines and a fake gate:

    gate rc=1 (non-day-1)  -> no banner, no run          [new form]
    gate rc=0 (day 1)      -> banner + WOULD_RUN          [new form]
    gate rc=1 (non-day-1)  -> WOULD_RUN anyway            [OLD form - the bug, reproduced]

Pure ASCII, all `goto` targets resolve. Report-only contract unchanged. Note for
future `.bat` work: the file is **LF-only** on disk (`core.autocrlf=true`
normalizes at checkout); the worker's "121/121 CRLF" claim was false and cost two
failed byte-match patches before I read the bytes myself.

## DG.2 `daily-trade-check-2` had drifted back into the MTM window

DE T-5 claimed HANDOFF's task table was "re-synced against the live list,
re-confirmed twice". Reading the live list (the tool, not any doc):

| task | HANDOFF said | live was |
|---|---|---|
| `daily-trade-check-2` | `0 19 * * 1-5` (7:00pm) | **`0 17 * * 1-5` (5:00pm)** |
| `cohort-0706-deploy` | disabled | **absent** |

The `0 17` drift matters: that task reads `paper_nav`/`paper_positions` and was
moved OFF `0 18` on 2026-08-04 (record CQ.3/E2) for exactly the two-writer overlap
it now had again, 15 minutes before `TradingDailyMTM` at 17:15. **Restored to
`0 19 * * 1-5`** via the scheduled-task tool; the tool confirmed "At 07:00 PM,
Monday through Friday". This is the third documented cron drift on this machine
(`monthy-llm-rebalance` twice, record BS/CN, now this) - the standing rule "read
the live list, never a doc" is re-affirmed in the HANDOFF row.

`cohort-0706-deploy` is struck in HANDOFF's table with the note that DE T-5
overrode a correct earlier "absent" with "disabled".

## DG.3 HANDOFF/PRD lines that DE's own commit left stale

- `HANDOFF.md` "Still open from the DA audit" listed `morning_refresh.bat:26` -
  the very finding DE T-2 closed in the same commit. Corrected.
- `HANDOFF.md:509`, `PRD_ROADMAP.md:122`, `.claude/codebase-memory/architecture.md:8`
  all still called `check_cache_gaps` "standalone, re-run monthly". Corrected to
  the wired-and-gated state.
- `HANDOFF.md` Last-updated stamp said 08-13 despite the 08-16 edit. Now
  2026-08-18 ~23:55 CDT.

## DG.4 DA finding 4 CLOSED - the lost decisions were REPLACE'd, not deleted

DA: "LLM decisions are never backdated is UNENFORCEABLE and three decisions have
ALREADY been overwritten (ids 4, 5, 9 missing; id=1 carries
`decision_date=2026-05-29` against `created_at=2026-05-31`)". Read-only look at
what is actually there:

- `llm_overlay_log`: **13 rows, ids 1..16, missing 4/5/9, `sqlite_sequence=16`.**
  Reproduces DA exactly. `sector_overlay_log`: 22 rows, ids 1..22, none missing.
- The three rows are absent from **every surviving snapshot** (backups 08-02,
  08-09, 08-16; the 05-27 pre-spike backup predates the table). Their content is
  unrecoverable.
- The record has **no entry** mentioning their removal. Record AT (07-02 reset)
  says "decision logs untouched"; the 07-02 reset archive JSON contains no
  overlay rows.

**Mechanism, from the code, not inferred:** both writers used
`INSERT OR REPLACE` against `UNIQUE (decision_date, ticker)`
(`llm_overlay.py:122`, `sector_overlay.py:136`; docstrings said "Insert (or
replace)"). SQLite's REPLACE resolves a UNIQUE conflict by **deleting the old row
and inserting a new one with a fresh AUTOINCREMENT id.** So re-logging a decision
for the same (date, ticker) silently destroyed the original and burned an id.
Nobody had to break a rule; the SQL did it. The surviving timestamps fit: ids 6/7/8
(07-01 WDC/BE/SLGL) were created 06-30 17:36-17:40 - ids 4 and 5 sit immediately
before them, almost certainly first attempts re-logged minutes later; id 9 sits
between the 06-30 batch and 07-07's id 10 (WDC again). Stated as the consistent
explanation, not as proven - the rows are gone.

**On "backdated":** the `created_at != decision_date` rows split two ways. ids
6/7/8 and sector 5-10 were created **06-30 for a 07-01 decision** - pre-dated,
decided the evening before, which is the design. Only id=1 (created 05-31 for
05-29) and id=3 (06-13 for 06-12) were logged AFTER their date, 1-2 days, both in
the pre-automation era. Reported, not repaired - CLAUDE.md reserves that.

**Fix, two layers, one file each way:**

1. `record_decision` in both modules: `INSERT OR REPLACE` -> plain `INSERT`. A
   same-(date, ticker) re-log now raises `sqlite3.IntegrityError`. Checked all
   4 call sites: `overlay_auto_decide.py` already skips already-decided names
   (`if ticker in decided: continue` / `decision_for(as_of) is None`), so the
   automated monthly path is unaffected; the only path that could hit the
   conflict is a manual `*_ops decide` re-run, which is exactly the case that
   should refuse.
2. `trading_bot/db.py` SCHEMA: six triggers, `IF NOT EXISTS`, per table -
   BEFORE INSERT (refuse when the (date, ticker) already exists), BEFORE UPDATE,
   BEFORE DELETE, each `RAISE(ABORT, '... is append-only (record DG)')`. Applied
   to the live DB by `init_db()`, which `paper_mtm.write_nav()` calls on every
   NAV write - so the 5:15pm run on 08-19 installs them (0 triggers on live as of
   this entry; 0 duplicate keys, so nothing trips).

**Canary - `scripts/momentum/test_decision_log_append_only.py`, throwaway DB,
15/15 PASS.** It caught a real hole in my first attempt: I initially wrote only
UPDATE + DELETE triggers, and the test's raw `INSERT OR REPLACE` case FAILED -
**SQLite's REPLACE does not fire DELETE triggers unless `PRAGMA
recursive_triggers` is on**, so a delete trigger alone still let REPLACE
destroy rows through the DB layer. The BEFORE INSERT trigger closes that; the
re-run is 15/15. The test's first check is a positive control that runs the
exact old statement on a trigger-less twin table and shows id=1 destroyed and
seq burned - the instrument can see the bug it guards against (CQ.4).

## DG.5 Verification (real output)

Frozen tests **4/4 d=+/-0.0000pp**, exit 0, run 2026-08-18 ~23:59 CDT after all
Python edits:

    [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
    [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
    [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
    [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)

    All regression tests passed.

`test_decision_log_append_only`: 15/15 PASS, exit 0 (output above in DG.4).
`daily.bat`: 0 non-ASCII bytes; every `goto` target present exactly once.
`py_compile` clean on `db.py`, `llm_overlay.py`, `sector_overlay.py`.
No live DB writes. Diff: `daily.bat` +9/-5, `db.py` +27/-0, `llm_overlay.py`
+11/-2, `sector_overlay.py` +7/-2, `HANDOFF.md` +7/-7, `PRD_ROADMAP.md` +1/-1,
`architecture.md` +1/-1, plus the new test file.

## DG.6 Status

- DE T-4, T-5: **re-closed properly** (DG.1, DG.2). DE's "verified" on both was
  a verification of the wrong path / the wrong source.
- DA finding 4: **CLOSED** at writer + DB layer; live triggers land 08-19 17:15.
- Still open from DA: findings 5 (`TOL_PCT=0.05`), 6 (ticker normalisation
  between overlay twins), E3 (daily-firing "monthly" task + cadence check blind
  to mid-month fires), and the remaining edge cases.
- Evan's: `slippage_log` still 0 rows; `positions` residue still 137.
- Committed per Evan's "do all"; not pushed - but the DB.1 caveat stands, the
  weekday trade-check tasks push the whole branch (~07:07 tomorrow).

# Appendix DH - Landing-check on DG (its own commit `ebc059f`): SAFE, three corrections - DG.4 verified the DORMANT decision path, the LIVE one had no guard and would have traced out of the unattended 6:03pm task on 09-01, now refuses cleanly (rc=2); one HANDOFF line DG.3 missed; one wrong diff count (2026-08-19, ~00:20 CDT)

Per Evan's standing instruction the DG commit got its own cold landing-check (Opus
worker, artifacts only). Verdict SAFE; every claim in DG re-derived TRUE except
the three below, each re-derived by hand before acting.

## DH.1 DG.4 cited the wrong path - the live monthly path had no guard

DG.4 justified "the automated monthly path is unaffected" by
`overlay_auto_decide.py`'s `if ticker in decided: continue`. That module is only
reached via `monthly_auto.bat`, the **dormant** Option-B path (unscheduled). The
**live** path is `monthy-llm-rebalance` -> `overlay_prep.bat` -> the LLM issuing
`llm_overlay_ops decide` / `sector_overlay_ops decide` CLI calls, whose
`cmd_decide` called `record_decision` with no already-decided check and no
exception handling. `overlay_prep` does print "a decision is ALREADY logged ...
Nothing owed" - a natural-language guard, not code.

So DG's INSERT change moved the live failure mode from silent-overwrite to an
uncaught `sqlite3.IntegrityError` traceback inside an unattended task, first
exposure 2026-09-01. Right direction, wrong verification. **Fixed:** both
`cmd_decide` now catch `IntegrityError`, log one `REFUSED: ... already logged
and the log is append-only (record DG). Nothing was written.` line, and return 2.
No `.bat` consumes `decide`'s exit code (checked `rebalance.bat`,
`overlay_prep.bat`), so 2 is free. Proven in-process on a throwaway DB (live DB
untouched): rc sequence first/relog/first/relog/new-ticker = `0,2,0,2,0`, 2
REFUSED lines, 0 tracebacks, original rows intact.

## DH.2 `HANDOFF.md:97` still said "standalone `check_cache_gaps`"

DG.3 corrected three locations and missed the fourth - the M2 summary paragraph
in HANDOFF's own current-state block. Corrected. Repo-wide grep for the stale
phrasing over live docs now returns 0 (canary: `check_cache_gaps` itself 2 hits
in HANDOFF).

## DH.3 DG.5 diff count for `HANDOFF.md` was +7/-7; actual +15/-7

I computed the numstat, then added the finding-4 paragraph to HANDOFF, then did
not recompute. The other six per-file counts are correct.

## DH.4 What the check could not yet see - and how to close it tomorrow

Both DG predictions that depend on the next scheduled run were unobservable at
00:11 (no run of any kind since the 00:01 commit). Thirty-second re-check after
2026-08-19 17:15:

    grep -c "=== Monthly cache-gap audit" var/last_daily_run.log      # must stay 0 (day 19)
    wc -l var/cache_gap_report.log                                     # must stay 18, no 08-19 block
    sqlite: SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'    # must go 0 -> 6

Also confirmed by the worker, worth keeping: no `UPDATE` or `DELETE` against
either decision table exists anywhere in the repo, so the four UPDATE/DELETE
triggers cannot break an existing code path when they land.

## DH.5 Verification

Frozen tests **4/4 d=+/-0.0000pp**, exit 0, run 2026-08-19 ~00:14 CDT after the
`*_ops.py` edits:

    [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
    [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
    [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
    [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)

    All regression tests passed.

`py_compile` clean on both ops modules. Diff: `llm_overlay_ops.py` +17/-4,
`sector_overlay_ops.py` +17/-4, `HANDOFF.md` +2/-2, plus this entry and its twin.

# Appendix DI - Scheduled daily-audit: the 15 exit-code gates on the one script that trades were deaf to crash codes, and the "monthly" rebalance was gated only by prose an LLM reads (2026-08-19, ~16:45 CDT)

The scheduled `daily-audit` task fired 07:05 CDT. Its rule is to skip any project
whose last three record entries already contain an audit, so **Autonomous Car**
(AK, 08-16), **ServeLocal** (II.27, 08-16) and **World Models Research** (EZ's
cold G2-G4 sweep, 08-19) were skipped by rule, not by judgement. **Trading**,
**Skills** and **Swing Trading** were audited, each by a cold auditor plus a
separate landing-check that reads artifacts only.

Trading's cold audit returned **11 findings (1 high, 4 med, 6 low) and 7 edge
cases**. The landing-check on DF/DG/DH returned **SAFE** - every checkable claim
in all three re-derived TRUE from disk, including DH's own self-correction of
DG's `+7/-7` diff count, and DH.4's three morning re-checks all held. Evan
approved the safety-first subset only: **findings 1, E4 and E5**. The other 8
findings and 6 edge cases are OPEN and unfixed; see DI.6.

## DI.1 Finding 1 - `if errorlevel 1` is GREATER-OR-EQUAL, on the one script that trades

All 15 step gates in `rebalance.bat` were `if errorlevel 1`. That is `>= 1`, so
it is blind to a **negative** exit code - the `-1073741819` (0xC0000005, access
violation) a killed `python.exe` returns. A crashed `alpaca_sync --execute` or
`monthly_rebalance` therefore left `RC_FAIL=0`, stamped `stamp_rebalance_log
--status OK`, and exited 0. Real broker orders half-submitted, recorded as a
clean monthly rebalance - and `verify_run`'s cadence check then reads that OK
stamp and PASSes, so nothing downstream catches it either.

This is not a new lesson in this repo. `daily.bat:54-56` **documents this exact
trap** ("`if errorlevel 1`, which is GREATER-OR-EQUAL and therefore blind to a
negative crash code") and fixed itself for it after audit 2026-08-12 finding 3;
`ladder_rebalance.bat` and `morning_refresh.bat` already use the correct form.
`rebalance.bat` - the only one of the four that submits real orders - was the
one left on the old idiom. The audit found it by sibling-diffing the idiom
across all ten `.bat` files rather than reading any one of them.

Fix: each site becomes `set STEP_RC=%errorlevel%` on the following line plus
`if not "%STEP_RC%"=="0" (`. Block bodies unchanged. 15 sites, +47/-15.

## DI.2 Edge case E4 - the "monthly" rebalance fires DAILY, gated only by prose

`monthy-llm-rebalance` runs on cron `0 18 * * *` - **every day**, not monthly.
Its only month gate was Step 0 of the task's own prompt ("check
`rebalance_log.md` ... STOP"), i.e. natural language read by an LLM. The script
itself had no month check. `rebalance.bat`'s header comment says "Idempotent:
re-running same day is a no-op (target set unchanged)" - true the same day, and
false mid-month, because by then the ranks have moved. So a single mis-read of
that prose runs a full rebalance mid-month and it **trades**.

Fix: new `scripts/momentum/check_month_gate.py`, called before the price
refresh, refusing when `rebalance_log.md` already stamps the current calendar
month. `--allow-same-month` is the deliberate override.

One deliberate exception, so this does not re-introduce an older bug: a
**PARTIAL** stamp does NOT refuse. A PARTIAL is a failed run awaiting its retry,
and locking that retry out is exactly what audit 2026-08-04 finding 1 fixed when
it introduced `--status` in the first place. A legacy stamp with no status is
treated as OK (refuse), matching `check_rebalance_cadence`'s existing
convention.

## DI.3 E5 - the daily-report auto-push, which had already fired that morning

Both `daily-trade-check` prompts ended their report commit with a bare
`git push`. The `git add` is carefully scoped to exactly two paths, but
`git push` publishes the **whole branch**, so any unrelated local work commit
rides along. This was not hypothetical: at **07:08 CDT that morning** the
pre-market run pushed `ebc059f` and `c758d25` - the two landing-check work
commits from DG and DH - to the public remote along with its report. The audit
caught it as a CONSTRUCTED edge case; by the time the fix was applied it was
OBSERVED.

Fix: the push instruction is removed from both prompts; commits stay local and
publishing is Evan's call, which is what global CLAUDE.md required all along
("Commit only when asked; never push unless told"). **These two files live at
`~/.claude/scheduled-tasks/daily-trade-check*/SKILL.md`, outside this repo**, so
the fix is live on disk but is NOT in this or any commit - see DI.6.

## DI.4 Verification (real output)

Finding 1's claim and its fix, proven against real Windows exit codes rather
than argued:

    case A: exit -1073741819 (crashed python)
      OLD `if errorlevel 1`  : MISSED <-- the bug
      NEW explicit capture   : CAUGHT
    case B: exit 1     OLD: CAUGHT   NEW: CAUGHT    (no regression)
    case C: exit 0     OLD: passed   NEW: passed    (no false positive)
    case D: exit 9009  NEW: CAUGHT                  (missing interpreter)

End-to-end control flow over the whole patched 240-line file, every
`python.exe` call replaced by a stub so nothing traded:

    === gate REFUSES (mid-month firing)          exit=1 expect=1  [OK]
        | REFUSED: this calendar month is already rebalanced (see rebalance_log.md).
    === --allow-same-month, all steps clean      exit=0 expect=0  [OK]
        | [stub] STAMPED OK
    === alpaca_sync crashes -1073741819          exit=1 expect=1  [OK]
        | STEP FAIL: alpaca_sync --execute
        | [stub] STAMPED PARTIAL
    FLOW TEST PASS 3/3

That third case is the whole finding: **before the fix it stamped OK and exited
0.** (The first harness attempt reported a false 2/3 because a `.bat` invoking
another `.bat` without `call` transfers control permanently and never returns -
the test was terminating at the first stub, and two of its three "passes" were
coincidence. Recorded because a harness that passes for the wrong reason is the
same class of defect this audit is about.)

`check_month_gate --canary` covers every branch including month boundary and
year rollover:

    CANARY PASS 8/8

and against the live log:

    month gate: REFUSE -- last stamp 2026-08-03 (status legacy-OK) is already in 2026-08

Frozen regression tests, required by CLAUDE.md after any Python change:

    [OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
    [OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
    [OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
    [OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
    All regression tests passed.

`py_compile` clean. Commit `9d9fd72` holds exactly two files, +123/-15
(`rebalance.bat` +47/-15, `check_month_gate.py` +76). **This entry and its
HTML twin are NOT in that commit** - it landed before the entry was written,
so they follow separately; DG's and DH's entries shipped inside their own
commits and this one does not. The pre-commit secret gate ran and returned 0
findings. **Not pushed** - and with E5 applied, no scheduled task will push it
either.

## DI.5 A machine-wide check the audit added, and what it found

Independently of the per-project sweeps, every non-Microsoft scheduled task was
queried read-only. The five Trading/Swing daily jobs are all healthy (exit 0,
correct next-run times). One is not:

**`\llm rebal`** - enabled, Monthly, next run 2026-09-01 17:59, last run
2026-08-02 15:39 with `LastTaskResult -2147020576 = 0x800710E0` ("operator or
administrator refused the request") and `StopIfGoingOnBatteries=True`. Its
`Task To Run` is not a rebalance at all: it is a `mouse_event` wake-nudge, i.e.
a wake fired 4 minutes before the 18:03 `monthy-llm-rebalance`. It has sat
failed for 17 days, and the failure mode - refusal on battery - is the **same
one HANDOFF already documents at line 550 for `TradingWeeklyBackup`**, whose fix
(clearing the battery flags) was never applied here. Nothing surfaces it: no
log, no HANDOFF row, no check.

Also: HANDOFF's Windows task table lists **5** tasks; `schtasks` registers **8**
non-Microsoft ones. `\llm rebal`, `\Wake PC` and `\Wake PC 2` appear in no
project doc. DE T-5 and DG.2 both claim the task table was "re-synced against
the live list" - true, but only of the Claude-scheduler table, not the Windows
one.

This is finding 9 and is **OPEN**. It is Evan-gated: changing task settings and
deleting or documenting a task he created is his call, not the audit's.

## DI.6 What this entry does NOT cover - stated rather than implied

- **8 findings and 6 edge cases remain OPEN**, including three the audit ranked
  above most of what was fixed: `market_data.last_close_on_or_before` ignoring
  the NULL-quarantine convention its three siblings honour (finding 2, med, 42
  tickers currently in the enabling state, 0 rows live); `verify_run`'s
  continuity check deriving its calendar from the same table it is checking, so
  a wholly-lost trading day PASSes (finding 3 / E2, the realized 07-30+07-31
  shape); and `check_dependency_cves.py` being invoked by nothing (finding 5).
- **No HANDOFF sync yet.** This entry is the record; the live snapshot has not
  been updated for it.
- **E5's two files are not under version control here.** They live in
  `~/.claude/scheduled-tasks/`. The fix is live on disk with no commit behind
  it, and nothing in this repo's history will show it happened.
- **The Skills and Swing Trading audits are not recorded here** and their fixes
  are not committed. Swing's record entry was deliberately held: a **concurrent
  session was found writing that repo** during this one - it had applied the
  Swing audit's own finding 2, implemented V3 PBO scoping in
  `run_v1_harness_check.py`, staged an F14 execution (`var/swing.db.pre-F14.bak`
  exists; `swing.db` itself unchanged), and had already claimed appendix `FC`.
  Writing a Swing entry from here would have forked the append-only record.
  Flagged to Evan; he chose to hold both.

## DI.7 Status

`rebalance.bat` and `check_month_gate.py` committed (`9d9fd72`, local, unpushed).
The month gate first bites on **2026-09-01**, which is also the first firing of
`\llm rebal` since it started failing and the date DH's own `rc=2` guard first
matters - so 09-01 is the run to watch. E5 is live for the next scheduled
report run. Everything in DI.6 is open.


# Appendix DJ - Audit of the `daily-trade-check-2` scheduled-task spec: every prohibition in the file that authorizes an unattended agent to write this repo was prose with zero enforcement, and the one time it was tested it failed. Deny rules added, specs snapshotted into the repo, landing-check moved before the commit (2026-08-20, ~23:30 CDT)

**Trigger.** Evan ran `/audit` on `~/.claude/scheduled-tasks/daily-trade-check-2/SKILL.md`
immediately after that task's own 19:00 run produced the 08-20 post-close entry. Per the
audit skill's step 0 the executing session is a compromised auditor, so a **cold
general-purpose agent** was spawned with the file, the blast radius, and steps 1-6, and with
no conversation history. Its findings were then independently re-verified before action:
`.claude/settings.json`, `git remote -v`, `cd ~/.claude && git rev-parse`, `ls docs/research`,
and a header grep of `daily_report.md`. All confirmed.

**DJ.1 - The crit finding: the prohibitions were decorative.**

The spec asserts "This task is READ/RESEARCH ONLY", "NEVER `git add -A` or `git add .`",
"Do NOT push", "never push, force-push, pull, rebase, or auto-merge", "it must never
rebalance, MTM, or modify any sleeve, NAV, or price data". Every one of those was **prose an
LLM reads**, with nothing behind it:

```
.claude/settings.json   ->  permissions.deny = ["Read(./.env)", "Read(./.env.*)"]
~/.claude/settings.json ->  permissions had NO deny key at all
git remote -v           ->  https://github.com/Evan-Daruwalla/long-term-trading-momentum (PUBLIC)
```

This is the same class as DI's month gate ("gated only by prose an LLM reads") and it had
**already failed once for real**: record DI.3, 2026-08-19 07:08 CDT, when two landing-check
commits were pushed to the public remote by a task whose spec said not to.

**Fix:** nine `Bash(...)` deny rules added to **both** `.claude/settings.json` and
`~/.claude/settings.json` - the scheduled agent's cwd is not guaranteed, so a project-only
deny list is a deny list with a hole in it. Covered: `git push`, `git add -A`, `git add .`,
`git reset --hard`, `git rebase`, `*paper_rebalance*`, `*_ops rebalance*`, `*_ops decide*`,
`*alpaca_sync --execute*`. Both files re-parsed as valid JSON after the edit.

**DJ.2 - The spec that authorizes repo writes is in no git repo.**

`cd ~/.claude && git rev-parse --show-toplevel` -> *not a git repository*. There is no
history, no diff, no rollback, and no way to detect that a task spec was edited - on a machine
where this task's cron has drifted three times (CQ.3, DG, plus the monthly day-gate). Flagged
in DI.6; nothing had been done.

**Fix:** the four live Trading-relevant specs are now snapshotted to
`docs/scheduled-tasks/<taskId>.SKILL.md` (`daily-trade-check`, `daily-trade-check-2`,
`daily-audit`, `monthy-llm-rebalance`), and `daily-audit` STEP 0c diffs live-vs-snapshot every
morning. **Standing consequence: editing a task spec now requires re-copying it, or the next
audit reports drift.** That is the intended behaviour, not a bug.

**DJ.3 - `/landing-check` was running after the commit, gating nothing.**

The spec said "Then self-commit ... **Finally** use /landing-check". The skill's own contract
is a **pre-commit** sweep returning `SAFE TO COMMIT / FIX FIRST`. Running it after the commit
means its verdict cannot gate anything, and the record shows the cost: fabricated or wrong
detail reached **three of the five preceding entries** and each needed a second corrections
commit - `c118a3e` (wrong CFNB band low), `12f8bb6` (session counts carried past their
timestamp), `2d17058` (13 share counts written to 4 decimals from a 2-decimal console
display). The last of those happened in this very session, hours before the audit.

**Fix:** both daily-report specs now run `/landing-check` **before** `git add`, with the commit
gated on a clean verdict, plus an explicit clause authorizing a
`Daily report: <date> corrections - ...` commit if something is found after the fact.

**DJ.4 - A whole session was missing from the track record and nothing noticed.**

`grep -c "^## Report: 2026-08-17 (Monday) - Post-Market" daily_report.md` -> **0**. The
pre-market entry for 08-17 exists at line 30505; the post-close one was never written, and
there is no commit between `87466e3` (08-17 07:26) and `63affd0` (08-18 07:30). Nothing
errored. A scheduled report that never fires produces no error and no artifact - **the absence
is the failure**, and only a manual header-date diff would ever have caught it.

**Fix:** `daily-audit` gained a **STEP 0** running before classification: (a) missing session -
every weekday in the last 7 must have BOTH a Pre-Market and a Post-Market header; (b) duplicate
session; (c) spec drift per DJ.2; (d) cron drift read from the live tool, never from a doc.

**DJ.5 - PRE-FLIGHT blocks on both daily-report specs.**

Seven checks, each of which can abort the run, added to `daily-trade-check` and
`daily-trade-check-2`:

| check | why |
|---|---|
| 0a local `date` for the header | this task fires at 19:00 local = **00:00:22 UTC**, so a UTC-derived date files the session under tomorrow. `nextRunAt 2026-08-22T00:00:22.000Z`, jitter 22s. Seasonal - invisible all winter under CST. |
| 0b holiday abort | cron is `* * 1-5` with no holiday calendar; ~9 closed weekdays a year, on which "today's final NAV" is unsatisfiable and the compliant-looking output republishes yesterday under today's date |
| 0c duplicate-header abort | no idempotency clause existed; a re-fire double-counts in the week/period summaries |
| 0d echo the live cron into section 0 | turns a silent drift into a visible artifact |
| 0e `mode=ro` DB open | `grep -c 'mode=ro'` was **0** in both specs though CLAUDE.md makes it a hard rule; a default connect is read-write **and creates the file** on a wrong relative path, and `var/` is gitignored so a phantom DB would not show in `git status` |
| 0f month-boundary lock check | `monthy-llm-rebalance` fires ~18:03 and runs 15-35 min; on the 1st trading day it can still hold the DB when this task starts at 19:00 |
| 0g unmarked-NAV rule | **live right now** - `paper_nav` max is 2026-08-19 and 08-20 has 0/76 rows, the fourth consecutive session under the coverage floor. The spec said "query for today's final NAV" with no clause for the day being unmarked; the compliant-looking failure is publishing yesterday's NAV as today's close. |

Also added: the sections the format had converged on but the spec never required (**section 0
data-integrity/ops** and **the ladder-gradient/structural read**); an explicit **precision**
clause under DO-NOT-ASSUME (never print more significant digits than the source - the
`2d17058` failure mode); a stated working directory (the absolute repo path appeared **once**
in 3,647 characters, buried in the git clause); "`daily_report.md` is newest-LAST, read the
TAIL"; and a source-disagreement rule (publish the reconciled figure, flag the outlier, never
average silently).

**DJ.6 - `/research-brief` was forbidden by the spec's own whitelist.**

The spec opened with "use /research-brief" and later said "the ONLY writes it may make are
appending its own report to daily_report.md, rendering the HTML twin, and committing those two
report files". `/research-brief`'s defined deliverable is `docs/research/<date>_<slug>.md` plus
a record line - both outside that whitelist. `docs/research/` does not exist and no brief has
been produced by this task in ~37 runs; the methodology was being applied inline all along.
**Fix:** the spec now says to apply the *methodology* inline and explicitly not to save a
separate brief.

**DJ.7 - Non-atomic HTML render, and the no-op that reports nowhere.**

`scripts/render_record_html.py:107` did `open(out, "w")` then `f.write(html)` on a 5.7 MB
file, and the next spec step stages and commits that file - an interruption commits a truncated
twin, which CLAUDE.md forbids hand-editing. Both renderers share this one write site
(`render_daily_report_html.py` delegates to `render()`), so the chokepoint fix covers both. It
now writes `out + ".tmp"` then `os.replace()`. **Verified by feeding it the trigger**, not by
reading the patch: a simulated kill mid-write left the target byte-identical (34 bytes,
unchanged), a clean write replaced it and consumed the `.tmp`, and the pre-fix behaviour
truncated the same file to 50 bytes for contrast.

Separately, the spec's *only* handled failure - "If git reports nothing to commit, that is fine
- just note it in your summary and finish" - routes its notice to an unattended chat summary
nobody reads, when in fact nothing-to-commit means the report was never appended: a total
failure wearing the happy path's clothes. It now appends
`[OPS <date>] daily-trade-check-2 NO-OP: nothing to commit` to `var/ops_status.log`, and
`var/ops_status.log` was added to the write whitelist to keep that legal.

**DJ.8 - Two stray test tasks deleted.**

`hellllo` (`0 12 * * *`) and `hello-just-say-hi-back` (`0 17 * * *`) - both entire prompts were
`hello (Just say "hi" back)`, both still **enabled and firing daily**, the second one ~10
minutes before `TradingDailyMTM`. Flagged as "Evan's to delete" in HANDOFF since 2026-08-16
(DE T-5). Deleted on Evan's approval; 10 and 7 archived run sessions respectively. **Their
`SKILL.md` files were left on disk**, so the prompts are recoverable. The live task list is now
4 enabled (`daily-trade-check`, `daily-trade-check-2`, `monthy-llm-rebalance`, `daily-audit`)
plus one disabled one-time.

**DJ.9 - HANDOFF drift corrected.**

HANDOFF - the only live snapshot - still described both daily-report tasks as pushing, in four
places (`:616`, `:623`, `:624`, `:639`), and had been synced 41 minutes *after* the push clause
was removed. All four corrected, the two stray-task rows struck, and a note added recording the
enforcement layer and the re-copy obligation from DJ.2.

**DJ.10 - A caveat on DJ.1 found while committing: the enforcement layer is itself untracked.** `.gitignore:13` is `.claude/*` with a single exception (`!.claude/codebase-memory/`), so **neither** settings file is version-controlled. The deny rules that are now the only mechanical enforcement behind every scheduled task's "READ-ONLY / never push / never trade" prose live in files git cannot see - the same unversioned-config gap as DJ.2, one layer down. Copying them into the repo was rejected: the user-level file carries personal config and the remote is public. Instead `daily-audit` STEP 0e now **asserts the nine rules are present in both files by name** every morning and reports any that went missing, without printing either file. That detects removal; it does not prevent it. **Making these tracked is a real open question and it is Evan's call** - it needs a `!.claude/settings.json` negation and a decision about what belongs in a public repo.

**Verification.** Frozen regression tests after the Python change:

```
[OK  ] momentum_v1/2023_Q4: tpnl=+14.5547% (exp +14.5547%, d= -0.0000pp)  trades=70 (exp 70, d= +0)
[OK  ] momentum_v1/2025_H1: tpnl=+1.8792% (exp +1.8792%, d= -0.0000pp)  trades=156 (exp 156, d= +0)
[OK  ] momentum_v2/2023_Q4: tpnl=+14.4062% (exp +14.4062%, d= -0.0000pp)  trades=38 (exp 38, d= +0)
[OK  ] momentum_v2/2025_H1: tpnl=+10.2194% (exp +10.2194%, d= +0.0000pp)  trades=87 (exp 87, d= +0)
All regression tests passed.
```

Both renderers re-run clean (`daily_report.html` 5,718,872 bytes, 1,201 heading ids, 0 broken;
record twin 816,393 bytes, 147 links, 0 broken), no `.tmp` residue. Both settings files
re-parse as valid JSON. All four spec snapshots `diff`-clean against live.

**What was NOT done.** The audit's M6 was read-only - the spec itself was not executed, since
executing it writes and commits. No CVE database was consulted. The edge cases ranked P2/P3
that were fixed by clause (E5 duplicate-fire, E7 month-boundary lock) are **CONSTRUCTED, not
observed** - the clauses are untriggered guards, and the first real holiday and the first real
1st-trading-day collision are still the tests that matter. E1 (missing session) and E6
(unmarked NAV) were **OBSERVED** and are the two that were already costing something.
