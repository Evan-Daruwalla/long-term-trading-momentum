# Handoff

## Goal

Build a paper-trading systematic-equity strategy on US stocks. Owner is 17,
can't open a real brokerage until 18 — so the immediate goal is **build
rigor + a track record**, not "make money now." Every strategy gets a proper
in-sample / held-out evaluation before it's trusted; the workflow itself is
the asset.

## Current state — Phase 2d, 27 sleeves live (07-06 cohort + residual weight ladder)

**Last updated: 2026-07-15** — this file is the only live snapshot (state-doc
tier retired 2026-07-08; historical snapshots archived in record Appendix AZ).

> **2026-07-09 — PRD milestones M2 + M3 + M4 + M5 complete, plus amendment M3.5**
> (record Appendices BB–BN); the two before-2026-08-01 deadline milestones (M2/M3)
> plus M4 + M5 are in place, and the daily pipeline is now self-healing (M3.5). **M6 (slippage) is the only remaining task and is GATED on the
> 2026-08-01+ Alpaca PAPER fills — it cannot start until those exist.** M5 (backup
> hygiene): `scripts/backup_trades_db.py` (rotating `VACUUM INTO` backups, keep 3,
> disk-guard), weekly `TradingWeeklyBackup` task (Sun 9am → `var/backup.log`),
> restore drill passed. M2 (data-quality guardrails): read-only `check_coverage` +
> `check_anomalies` wired into `daily.bat`, standalone `check_cache_gaps`. M3
> (unattended-automation safety): pre-inception NAV guard in `paper_mtm.py`
> (+regression test), read-only `verify_run` wired into
> `daily.bat`/`monthly_auto.bat`, ops-status stamp to `var/ops_status.log` (NOT
> `daily_report.md` — that's Evan's journal). M4 (experiment-integrity reporting):
> `experiment_report.py` (kill-switch tracker + control-vs-treatment NAV
> divergence, `--md`), plus n/30-picks & months/12 counters in the dashboard LLM
> panel. Interim experiment read: stock treatments AHEAD of control (cash +3.65pp
> dodging BE, cascade +7.90pp via WDC); sector treatments slightly behind
> (−0.73/−1.10pp). Tiny n — forward OOS only, not proof.
>
> **M3.5 catch-up marking DEPLOYED (record Appendix BN) — the daily pipeline now
> self-heals.** The coverage gate first fired in production 2026-07-09 17:17
> (4,381 < 5,000 floor), correctly skipping the 07-09 mark. `daily.bat` now runs
> `scripts/momentum/mtm_catchup.py` after refresh: it marks every SETTLED missing
> trading day (today included) for all sleeves and leaves still-pending days for
> the next run. `verify_run` treats a below-floor "today" as PENDING (not a gap),
> and the daily task exits 0 on a normal pending day (fails only on a real
> settled-history gap).
>
> **2026-07-09 gap RESOLVED (record Appendices BO/BP).** 07-09 settled to 5,204
> closes on 2026-07-10 14:44; catch-up backfilled it and `verify_run` -> PASS
> 17/17, all 07-09 NAVs verified correct (recompute matches to the cent).
> **Provenance RESOLVED:** 15 of the 17 rows were pre-marked by a *concurrent*
> Claude session (`33e12a94`, a "review the CLAUDE.md" task in `D:\ClaudeCode`)
> that looped `paper_mtm --as-of 2026-07-09 --strategy $s` at 14:41 — ~4 min
> before this session's catch-up marked the other 2. No corruption (idempotent
> REPLACE + serialized writers). **Two risks flagged (Appendix BP):** (1)
> concurrent uncoordinated NAV writers — official marking should have one owner
> (the `daily.bat` catch-up), still a process convention not code-enforced; (2)
> raw `paper_mtm --as-of` bypassed the coverage gate (it marked at 4,726 < floor;
> correct only by luck of held-names-present) — **CLOSED 2026-07-10 (record
> Appendix BQ): `paper_mtm.main()` now runs the shared `coverage_status()` gate
> and refuses a sub-floor `--as-of` day (exit 2, no write) unless `--force`.**
> Next PRD work: only M6 (slippage), gated on the 2026-08-01+ Alpaca fills.
>
> **2026-07-11 health check (record Appendix BR):** roadmap is complete through
> M5; M6 stays gated (no Alpaca fills until 2026-08-01+). Read-only `verify_run
> --mode daily` -> PASS 17/17 (continuity, cent-perfect cash recon, 0
> pre-inception, 07-10 correctly PENDING); working tree clean, all work committed
> through BQ. Friday 2026-07-10 17:15 `TradingDailyMTM` was the first live run of
> the self-healing `daily.bat` and exited 0 (coverage PENDING skip -> catch-up
> marked=0 -> verify PASS), where the pre-M3.5 flow would have failed the gate.

> **2026-07-07 — the 07-01/07-06 clean-start cohort is DEPLOYED (record
> Appendix AV).** 11 new sleeves went live on the 2026-07-06 close via the
> unattended `cohort-0706-deploy` scheduled task; 3 of them are mirrored to
> Evan's real Alpaca PAPER accounts (99 orders submitted, 0 rejections); and the
> monthly `monthy-llm-rebalance` scheduled task was re-enabled (first live fire
> 2026-08-01). This sits alongside — not replacing — the continuous May family.

> **2026-07-08**: Alpaca mirror sizing now carries a 1% cash buffer
> (`trading_bot/execution/alpaca_sync.py`, commit `3807f23`; record Appendix AY).
> Frozen tests re-run 2026-07-08 ~20:35, d=±0.0000pp on all 4 configs (Appendix BA).

The DB now holds **27 sleeves in four families** (this file is the roster
source — `CLAUDE.md` holds the durable invariants, not the roster, since
2026-07-08):

**1. Continuous May systematic + benchmark** (inception 2026-05-01; the 6
contaminated sleeves were re-inceptioned on clean data 2026-06-13):

| Sleeve | NAV (2026-07-07) |
|---|---:|
| residual_roa_6535_paper | $104,964 |
| spy_benchmark_paper | $103,755 |
| sector_top4_full_paper (continuous systematic twin) | $102,271 |
| mom_roa_6535_paper | $96,982 |
| mom_v2_paper | $95,200 |
| mom_v1_paper | $95,124 |

**2. 07-06 cohort — 5 systematic `_0701` + benchmark** (inception 2026-07-06;
★ = mirrored to Alpaca PAPER): `mom_roa_6535_0701_paper`★ $100,355 ·
`mom_v2_0701_paper` $100,212 · `residual_roa_6535_0701_paper`★ $100,207 (48/50,
2 untradable) · `mom_v1_0701_paper` $100,141 · `spy_benchmark_0701_paper`★
$99,525.

**3. 07-06 cohort — 6 LLM-experiment** (inception 2026-07-06): stock arm
`mom_roa_top1_paper` (control, holds **BE**) / `llm_overlay_mom_roa_top1_paper`
(veto→**cash**, BE vetoed) / `llm_cascade_top1_paper` (cascade→**WDC**); sector
arm `sector_top4_paper` (control XLK/XLE/XLI/XLB) /
`llm_overlay_sector_top4_paper` (XLK/XLI/XLB, XLE→cash) /
`llm_cascade_sector4_paper` (XLK/XLI/XLB/**XLV**).

> ⚠️ **Do not confuse** `sector_top4_paper` (07-06 LLM-experiment control) with
> `sector_top4_full_paper` (continuous systematic twin, unbroken since 05-01).
> They hold identical picks going forward; they differ only in pre-07-01 P&L.

**4. Residual weight ladder** (inception 2026-05-01, replay-seeded 2026-07-14;
record BW): 10 systematic sleeves `residual_w<MM><RR>_paper` differing ONLY in the
residual-mom/ROA blend (MM/RR %), top-50 monthly, same config as
`residual_roa_6535_paper` otherwise. Forward-test of the BU/BV in-backtest
weight-plateau finding. **NOT Alpaca-mirrored, no LLM decisions.** NAV @ 2026-07-13
(deterministic 05-01→07-13 REPLAY — live forward data begins 2026-07-14; see BW
honesty demarcation + the ~1–2% replay/cache-drift caveat): w6040 $105,800 ·
w5545 $105,625 · w5050 $105,167 · w6535 $104,294 · w8515 $104,252 · w9505 $103,678
· w7525 $102,550 · w9010 $102,441 · w7030 $102,373 · w8020 $102,234. (This 05-01→
07-13 ranking is 10-week NOISE — inverts the backtest holdout; forward data decides.)

### Systematic sleeve specs

| Sleeve | Factor | Spec file |
|---|---|---|
| mom_v1_paper | 12-1 momentum, top-100 | `trading_bot/strategies/momentum_v1.py` |
| mom_v2_paper | 12-1 momentum, top-50 | `trading_bot/strategies/momentum_v2.py` |
| mom_roa_6535_paper | 65% mom Z + 35% ROA Z, top-50 | `trading_bot/strategies/mom_roa_6535.py` |
| residual_roa_6535_paper | 65% residual-mom Z + 35% ROA Z, top-50 | `trading_bot/strategies/residual_roa_6535.py` |
| residual_w<MM><RR>_paper (×10) | MM% residual-mom Z + RR% ROA Z, top-50 (weight ladder) | `scripts/momentum/paper_rebalance.py` `_strategy_config` (parsed from name) |
| sector_top4_paper | 12-1 momentum on 11 SPDR ETFs, top-4 | `trading_bot/strategies/sector_top4.py` |

Regression tests: `trading_bot/strategies/test_strategies.py` — 4 pinned
configs, must stay at d=±0.0000pp after every change.

### Backtest performance — RE-VALIDATED 2026-06-13 on backfilled clean data

Re-measured after the history-gap backfill (full report:
`docs/revalidation_2026-06-13.md`; raw: `var/data_audit/revalidate_2026-06-13.json`).
Same methodology as before (5 bps, monthly, equal-weight). Held-out = 2024-01 →
2026-05; in-sample = 2015-01 → 2023-12.

| Strategy | In-sample CAGR (Δ vs old) | Held-out CAGR (Δ) | Held-out Sharpe | Held-out maxDD | Held-out Calmar |
|---|---:|---:|---:|---:|---:|
| residual_roa_6535 | +9.47% (+0.6) | +32.07% (+1.2) | **1.21** | **−20.1%** | **1.60** |
| mom_roa_6535 | +4.89% (**−4.97**) | +35.59% (−0.9) | 1.13 | −30.4% | 1.17 |
| sector_top4 | +8.14% (+0.3) | +17.59% (−0.0) | 0.91 | −16.2% | 1.09 |
| mom_v1 | +5.91% (+1.2) | +24.23% (+2.2) | 0.90 | −33.9% | 0.71 |
| mom_v2 | +3.54% (+0.8) | +26.47% (−1.5) | 0.89 | −34.8% | 0.76 |

**Verdict:** the picture clarified, didn't collapse. **residual_roa_6535's
leadership is confirmed real** (least-contaminated at 6%, now in-sample champion +
best risk-adjusted held-out). **mom_roa_6535's in-sample edge was phantom-inflated
(halved)** — re-frame it as a held-out/recent-regime specialist, not all-weather.
sector_top4 (ETF) held-out −0.0pp = methodology sanity check passes. No sleeve
invalidated; live lineup unchanged.

> ⚠️ Read absolute CAGRs as **survivor-biased upper bounds** — yfinance fills only
> currently-listed names, so the backfilled 2019-2026 universe excludes
> 2019-2025 delistings. The live paper-trade (clean from 2026-06-12) is the only
> true forward OOS test. See report §Caveats.

### MAJOR DATA AUDIT (2026-05-28) — trust nothing before this date

yfinance had Friday-spike + unadjusted-reverse-split corruption.
Contaminated the in-sample window (tickers like ITC, TNB, FOOD showed
5,000-10,000× bogus closes). Cleaned 2,017 rows; added `MAX_HIST_RATIO=100`
filter; re-baselined frozen tests. DB backup: `var/trades.db.bak_pre_spike_cleanup`.

Convention: `price_cache` closes are **split-adjusted, dividend-UNadjusted**
(`auto_adjust=False`). Every cache writer must use that flag.

---

## LLM Overlay Experiments

### Stock-level overlay (mom_roa_top1)
- **Control**: `mom_roa_top1_paper` — always holds #1 ranked mom_roa name
- **Treatment**: `llm_overlay_mom_roa_top1_paper` — holds only on logged BUY;
  exits on invalidation price stop
- **Rule**: run 3 prompts (growth/quality/risk) on every new underlying name
  before the treatment buys. Decision logged via `llm_overlay_ops`.
- **Stops FIXED 2026-07-15 (record BZ)**: invalidation stops were DORMANT since
  deployment — `daily.bat` gated `check-invalidation` behind a universe-wide
  coverage PASS that the 5:15pm run almost never sees (today = pending), so
  they simply never ran (zero `invalidation` exits in current DB history).
  Now enforced EVERY evening via `--settled` (priced as-of the last settled
  trading day). First live run of the new path: 2026-07-16 5:15pm. Evan chose
  this (option a) over morning-task enforcement / rebalance-only.
- **Current state (2026-07-15, DB-verified)**: treatment has never held a
  position since the 07-01 reset (all cash — the #1 candidate BE was VETO'd
  07-01 and again 07-07); control holds the #1 name. (The pre-reset FN
  history lives in the record.)
- **Kill switch**: 12 months / 30 picks, drop if scores don't predict returns
  OR treatment doesn't beat control over 30 picks.

### Macro sector overlay
- **Control**: `sector_top4_paper`
- **Treatment**: `llm_overlay_sector_top4_paper` — sector_top4 picks with
  a 4-prompt macro veto (rates/valuation/breadth/bear-case); veto → cash for
  that 25% slot
- **Current state (2026-07-15, DB-verified)**: holds XLB/XLI/XLK since 07-07
  (XLE slot VETO'd → cash); live stops 49.5/170/172 — none breached through
  07-14. Same stop fix as the stock overlay applies (record BZ): enforced
  nightly as-of the last settled close from 2026-07-16.
- **Code**: `trading_bot/strategies/sector_overlay.py`, `scripts/momentum/sector_overlay_ops.py`

---

## Infrastructure

### Database
- `var/trades.db` (~5 GB) — all paper positions, NAVs, price cache, XBRL
- Backup: `var/trades.db.bak_pre_spike_cleanup` — DO NOT DELETE
- Tables: `price_cache`, `paper_portfolio`, `paper_positions`, `paper_nav`,
  `paper_transactions`, `xbrl_facts`, `sectors_cache`, `fundamentals_cache`,
  `signals`, `llm_overlay_log`, `sector_overlay_log`
- **CRITICAL**: never run concurrent `factor_backtest` against same DB — silent corruption

### Key scripts
| Script | Purpose |
|---|---|
| `scripts/momentum/daily_price_refresh.py` | Bulk yfinance refresh (~4,300 tickers) |
| `scripts/momentum/paper_rebalance.py --strategy NAME --top-n N` | Monthly rebalance |
| `scripts/momentum/paper_mtm.py --strategy NAME [--as-of DATE]` | Daily mark-to-market |
| `scripts/momentum/llm_overlay_ops.py candidate\|decide\|rebalance\|check-invalidation` | LLM stock overlay; `check-invalidation --settled` runs nightly in `daily.bat` (record BZ) |
| `scripts/momentum/sector_overlay_ops.py candidate\|decide\|rebalance\|check-invalidation` | LLM sector overlay; `check-invalidation --settled` runs nightly in `daily.bat` (record BZ) |
| `scripts/momentum/seed_spy_benchmark.py` | One-off SPY sleeve seeder (idempotent) |
| `scripts/momentum/check_coverage.py` | Coverage gate (read-only): fails if the day's close count < floor. Wired into `daily.bat` before MTM (M2.1/M2.2) |
| `scripts/momentum/check_anomalies.py` | Anomaly detector (read-only): flags KLAC-class 1-day moves + missing held marks → `var/anomaly_report.log`. Wired into `daily.bat` after MTM, non-blocking (M2.3) |
| `scripts/momentum/check_cache_gaps.py` | Cache-gap auditor (read-only): flags rankable tickers with history holes >5 trading days → `var/cache_gap_report.log`. Standalone, re-run monthly (M2.4) |
| `scripts/momentum/verify_run.py --mode daily\|monthly` | Post-run verifier (read-only): per-sleeve NAV continuity (to last SETTLED day), cash recon, position-count (monthly), no-pre-inception → `var/verify_report.log`. Wired into `daily.bat`/`monthly_auto.bat` (M3.2/M3.3) |
| `scripts/momentum/mtm_catchup.py [--dry-run]` | Self-healing MTM: marks every settled missing trading day (incl today) for all sleeves; skips pending days + never overwrites/back-marks across a rebalance. Runs in `daily.bat` after refresh (M3.5) |
| `scripts/momentum/ops_stamp.py` | Appends a dated one-line run-status stamp to `var/ops_status.log` (M3.4) |
| `scripts/momentum/experiment_report.py [--md]` | LLM-experiment kill-switch tracker + control-vs-treatment NAV divergence (read-only) → console / `docs/experiment_report_<date>.md` (M4.1/M4.2) |
| `scripts/backup_trades_db.py [--keep N] [--dry-run]` | Rotating `VACUUM INTO` backup of `trades.db` → `var/backups/`, keep newest 3, disk-guard (M5.1) |

### Batch files
| File | When to run |
|---|---|
| `scripts/momentum/daily.bat` | Daily after market close (auto via `TradingDailyMTM` at 5:15pm) |
| `scripts/momentum/rebalance.bat` | 1st trading day of each month (manual, idempotent) |
| `scripts/start_all.bat` | Manual full restart (kills dashboard, refreshes prices, MTMs all) |
| `scripts/dashboard.bat` | Manual dashboard launch |

### Scheduled Windows tasks
- **`TradingDashboard`** — launches Streamlit at logon, auto-recovers
  Dashboard: http://localhost:8501/   Logs: `var/dashboard.log`
- **`TradingDailyMTM`** — fires `daily.bat` at 5:15 PM, `StartWhenAvailable`
  Logs: `var/last_daily_run.log`
- **`TradingMorningMTM`** — fires `morning_refresh.bat` at 7:45 AM daily,
  `StartWhenAvailable` (added 2026-07-15, record BY). Refresh + `mtm_catchup` +
  verify ONLY (NO stop-enforcement) — heals the once-daily coverage LAG so a day
  pending at the 5:15 PM run is marked by ~8 AM instead of ~24 h later. Logs:
  `var/last_morning_run.log`
- **`TradingWeeklyBackup`** — Sundays 9:00 AM → `backup_trades_db.py` (rotating
  `VACUUM INTO` backup). Logs: `var/backup.log` (added 2026-07-09, M5.2)

Manual control:
```
schtasks /run /tn TradingDashboard    # restart dash
schtasks /end /tn TradingDashboard    # kill dash
schtasks /run /tn TradingDailyMTM     # run daily MTM now
```

### Dashboard
`trading_bot/dashboard/web.py` — Streamlit, port 8501.
Tabs: **Live experiment** (paper-trade) + **Backtest archive**.

Views on the paper-trade tab:
- **📊 Overview** (default): status strip, all-sleeve table (9 rows + SPY
  control), compact NAV %-chart, top movers across held names, LLM experiment
  panel, concentration warnings.
- **🔬 Single sleeve**: positions, NAV history, vs-SPY benchmark.
- **📈 NAV charts**: overlay %-from-inception + absolute-$ for all sleeves.

Chart conventions (as of 2026-06-10):
- %-hover shows 3 decimal places (`+.3f`)
- Traces added in descending latest-value order (unified hover reads highest→lowest)
- S&P 500 control is `spy_benchmark_paper` read from DB (no network)

---

## What's been ruled out (25+ experiments)

Full list in `memory/sleeves_verdict.md`. Summary of failure patterns:

| Pattern | Examples |
|---|---|
| Factor combos / sleeves (dilution/correlation) | quality, low-vol, XBRL, PEAD, accruals |
| Universe restrictions (survivorship / alpha-tail removal) | top-500/1000 by market cap |
| Reactive risk controls (fails on monthly momentum) | stops −10/−15/−20/−25%, stop+reentry |
| Timing/regime gating | SPY 200-DMA filter, VIX short-vol |
| Leveraged LETF rotation | Gayed LETF (doesn't beat benchmark risk-adj) |
| Single-asset timing | Turn-of-month (can't beat buy-hold in bull market) |
| Long-short momentum | Unbounded short-squeeze risk in 2021; busts in-sample at any leverage |

New experiments closed 2026-06-09 (see `docs/research_2026-06-09_algo_candidates.md`):
- **DEPLOYED**: residual_roa_6535 (Attempt 24) — beats mom_v2 both windows
- **REJECTED**: VIX short-vol (neg held-out Sharpe), Gayed LETF (loses vs QQQ),
  turn-of-month (loses vs buy-hold), vol-target L/S (meme-squeeze risk)

---

## Known limitations

- **yfinance data quality**: split-adjusted closes can be mis-applied early
  (e.g. KLAC 10:1 split 2026-06-12 — yfinance applied it to history 3-4 days
  early; required manual `paper_positions` qty/price correction + NAV rewind).
  Watch for >1000% single-day moves in the movers panel — that's the tell.
- **Survivorship bias** in `price_cache`: ~4,200 tickers cached vs the full
  universe of names ever traded. Cannot fix without a paid PIT data source.
- **In-sample validation is marginal** (+2.72%/yr mom_v2, clean data).
  Strategy rests on 2.4yr held-out + forward paper trade only.
- **Single-name LLM sleeves are deep underwater** (FN position, both
  −19%). The experiment is designed for 12mo/30 picks — current n=1 is noise.
- **No slippage realism check yet** — deferred until ~20 real fills (post-Aug 2026).
- **No short support** in `paper_trader` — blocks deploying L/S vol-target
  even as paper trade. Not building until the strategy passes in-sample.

---

## Monthly operations (first trading day of each month)

**Now automated** via the `monthy-llm-rebalance` Claude scheduled task (cron
`0 18 * * *`, ~6:03pm local — shifted back from a drifted `30 17`/~5:33pm on
2026-07-11 per Evan, to clear a rebalance-day two-writer overlap with the 5:15pm
daily MTM; record BS; self-gates on `rebalance_log.md` so only the first
trading day of the month does real work). It runs `rebalance.bat` (all 10 paper
lines carry `--broker-realistic`), does the LLM overlay decisions per
`docs/overlay_decision_runbook.md`, MTMs everything (per-sleeve `paper_mtm
--force` so the rebalance day is marked despite partial same-day coverage,
record BS), runs `verify_run --mode monthly`, and fires
`alpaca_sync --all --execute`. First live fire under this schedule: 2026-08-01.
If monthly rebalances stop running, confirm the task is enabled (memory
`monthly_rebalance_trigger_timing_bug.md`).

Manual fallback (same steps) if you ever need to run it by hand:
1. `rebalance.bat` after market close (refresh → rebalance → MTM → Alpaca mirror).
2. LLM stock overlay: if the control changes its underlying name, run the eval,
   log a BUY/VETO via `llm_overlay_ops.py decide`, then re-run.
3. Sector overlay: `sector_overlay_ops.py candidate` → 4 macro decisions via
   `decide` → rebalance.
4. Review dashboard Overview — NAV continuity, cash recon, stale-data warnings.

## Documentation
- `docs/record_2026-05-27.md` — **renamed 2026-06-30 to
  `docs/Project Record — Full Chronological History.md`** (same file, content
  unchanged) — full chronological record (Appendix A–AN), with a TOC +
  thematic digest + experiment index in the front-matter
- `docs/record_2026-05-27.html` — **renamed alongside it to
  `docs/Project Record — Full Chronological History.html`** — rendered,
  double-clickable view of the record (generated; regenerate with
  `.venv\Scripts\python.exe -m scripts.render_record_html`, or run
  `scripts\watch_record_html.bat` to auto-render on every save)
- State-doc tier RETIRED 2026-07-08 (Evan's decision): point-in-time snapshots
  live inside the record (all prior `state_*.md` archived verbatim in Appendix
  AZ; the source files were deleted 2026-07-08). Never create new
  `docs/state_*.md` files.
- `docs/paper_trading_ops.md` — ops guide (daily/monthly procedures)
- `docs/research_2026-06-09_algo_candidates.md` — June algo-research report
- `memory/` — per-verdict memory files (sleeves_verdict, data_audit, etc.)
- `daily_report.md` — owner's daily trading journal
