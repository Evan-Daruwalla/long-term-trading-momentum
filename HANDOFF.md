# Handoff

## Goal

Build a paper-trading systematic-equity strategy on US stocks. Owner is 17,
can't open a real brokerage until 18 — so the immediate goal is **build
rigor + a track record**, not "make money now." Every strategy gets a proper
in-sample / held-out evaluation before it's trusted; the workflow itself is
the asset.

## Current state — Phase 2d, 76 sleeves live (07-06 cohort + residual 3-cadence ladder)

**Last updated: 2026-09-29 ~21:50 CDT (record EF)** — this file is the only live snapshot
(state-doc tier retired 2026-07-08; historical snapshots archived in record
Appendix AZ).

> **Kept short on purpose.** On 2026-09-22 this file was 923 lines / 70 KB —
> ~18k tokens to reach a dozen actionable lines, in the document whose entire
> job is to be read first. 239 lines of dated narrative that the record already
> carried were replaced by the pointer table below (every appendix letter
> verified to exist before deletion). **History goes in the record. If you find
> yourself pasting a narrative block here, write an appendix and link it.**

> **2026-09-29 ~21:50 CDT (record EF) - EE audit items 1-10 worked, UNCOMMITTED.**
> - **The trade guard closes all 8 escapes** (self-check 60/0). Trading rules are
>   scoped to this repo; git+publish is global. It now denies any Bash command
>   naming a dispatcher module or `rebalance.bat`, even a `cat`/`grep` - use the
>   Read/Grep tools.
> - **2026-10-01 monthly is MANUAL (Evan):** Step 3 and Step 4 of the scheduled
>   task are both denied. On a market-closed day the dispatcher exits 3 and
>   `rebalance.bat` stops before any leg, with no stamp. An LLM leg with a stale
>   bar exits 4 (STALE-SKIP, holding kept, stamp stays OK): run the printed
>   `RETRY ... --as-of <D>` line after the day settles.
> - The ladder writes NAV only when coverage is OK. `mtm_catchup` reads the
>   last-rebalance stamp as a LOCAL date. 2026-09-28's 10 stale ladder rows were
>   re-marked (+$1.39, logged).
> - **BLOCKED-ON-EVAN:** (1) `alpaca_keys.env` Read-deny in both settings files
>   (exact lines in EF); (2) MLI 2026-06-05 cliff (0.5008, 14 sleeves) needs an
>   external corporate-action check. The seam checker now FAILs on it nightly
>   (report-only, `var/anomaly_report.log`).
> - Publishing already happened (2026-09-26 22:12 and 2026-09-29 14:28); 134 of
>   215 public commits carry the trailer. The bins no longer tell models to add it.

> **2026-09-22 ~14:30 CDT (record DV) — COLD AUDIT EXECUTED, AND A DATA DEFECT
> IT CAUSED.** A full `/audit` produced 39 findings; 5 commits shipped
> (`5b44107` `94c1215` `62c4680` `0f01fa8` `cc93239`). Frozen tests 4/4 at
> d=±0.0000pp. Details in record **DV**; do not re-summarize them here.
>
> **RESOLVED 2026-09-22 (records DW, DX) — the DV cash-backdating fault.**
> `compute_nav` now replays the ledger for a past date the sleeve traded after
> (`82644c2`). The 17 falsified 2026-09-17 rows (wrong cash AND wrong position
> set; $289.20 summed |NAV| vs replay; DV's $6,135.89 unreconciled) were
> **restored live 16:02 CDT** on Evan's call. `verify_run` **PASS 76/76**.
>
> **⚠️ `paper_nav` is now SEALED (record DX, committed `0b3bb67`; triggers live since 2026-09-23).** A row
> with a newer row for the same sleeve refuses REPLACE/UPDATE/DELETE unless
> `paper_nav_restatement` logged that (sleeve, date) in the last 10 min.
> `remark_nav_day --execute` now REQUIRES `--reason` and logs it. Gap-fill and
> same-day re-mark are unaffected. The triggers install on the live DB at the
> first `init_db()` — i.e. tonight's 17:15 run — committed or not.
>
> (2026-09-21 was re-marked 76/76 on 2026-09-23, record DZ.)
>
> **2026-09-23 ~22:50 CDT (records DY, DZ) - rate limit fixed, 09-21 marked.**
> yfinance rate-limits every refresh from ~batch 15 of 30, one ticker at a
> time, so no guard fired (09-22: A-J 94%, K-Z 46%). `daily_price_refresh` now
> retries the dropped tickers after 60/120/240 s cooldowns, and exits 1 if 5%
> or more are still missing (the monthly rebalance aborts on that). Live run:
> 1,995 dropped, 13 left (0.3%), runtime 9.3 min. **2026-09-21 marked 76/76,
> $7,718,922.42; verify PASS 76/76.** The stage 5 triggers are LIVE (5
> triggers, 19 restatement rows). The fix was committed 2026-09-26
> (docs-sync).
>
> **CORRECTED 2026-09-26 (record EC):** DZ's "09-22 is a Yahoo data hole" was
> WRONG - a throttled NaN misread as a missing bar. 09-22..09-25 are all marked
> 76/76 (09-22: 5,111 closes, $7,742,284.34). Weekly ladder Mon 09-28, monthly
> Thu 10-01.
>
> **2026-09-26 (record EC) - scheduled-task specs.** Five EB defects closed.
> Both report specs now end with a DONE-CHECK (grep own header, must be 1). It
> can NOT catch a run that dies at start; daily-audit STEP 0a does. Every header
> grep now uses `\(<Weekday>\) .{1,3} <Session>`, because the bracket form fails
> in this machine's C locale. **2026-09-24 Post-Market is a permanent hole** -
> never backfill it. 5 snapshots now, `hellow` included. (The 2026-09-26 "all 5 match live" was
> false by 2026-09-29: daily-audit had a ServeLocal->Citoya edit at 14:17;
> re-snapshotted 2026-09-29 ~21:45, all 5 identical again.)
>
> **The audit's own headline:** record appendices DS/DT/DU are three runs of
> this project's `daily-audit` that had already found several of these, and
> nothing acted — that task is spec'd READ-ONLY (no commits, no HANDOFF edits),
> so its findings sat uncommitted and this file never mentioned them.

### Recent history — read the appendix, not a copy

This section used to carry 240 lines of dated narrative duplicating the record.
Trimmed 2026-09-22; every letter below was verified to exist before deletion.

| Date | What | Record |
|---|---|---|
| 2026-09-22 | Cold audit executed, 5 commits; `remark_nav_day` cash-backdating found | **DV** |
| 2026-09-08 / 09-10 / 09-17 | `daily-audit` runs: trade-guard escapes, monthly path missing the stale-bar guard — unactioned | DS / DT / DU |
| 2026-09-06 | September account committed to HEAD; doc sync + drift-check | DR / DQ |
| 2026-08-19 | 15 exit-code gates deaf to crash codes; mechanical month gate added | DI |
| 2026-08-13 | Nightly `verify_run` FAIL was a false alarm; checker rebuilt (b1 ledger / b2 drift) | DA–DD |
| 2026-08-12 | Frozen tests stopped writing the live DB (TEMP-table shadowing) | CZ |
| 2026-08-11 | PRD M6 redefined to implementation shortfall; M6.1–M6.3 closed | CY |
| 2026-07-11 | Roadmap health check | BR |
| 2026-07-09 | M2–M5 + M3.5 complete; the 07-09 coverage gap resolved | BO / BP |
| 2026-07-07 | 07-01/07-06 clean-start cohort deployed | AV |
| 2026-07-08 | Alpaca mirror 1% cash buffer (`3807f23`) | AY / BA |


The DB now holds **76 sleeves in four families** (this file is the roster
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

Plus `qqq_benchmark_paper` (added 2026-07-17, record CE): $100k buy-hold QQQ from
the 05-01 close — a second index control next to SPY. NAV @ 2026-07-16 $104,716
(+4.72%). NOT Alpaca-mirrored.

**2. 07-06 cohort — 5 systematic `_0701` + benchmark** (inception 2026-07-06;
★ = mirrored to Alpaca PAPER): `mom_roa_6535_0701_paper`★ $100,355 ·
`mom_v2_0701_paper` $100,212 · `residual_roa_6535_0701_paper`★ $100,207 (48/50,
2 untradable) · `mom_v1_0701_paper` $100,141 · `spy_benchmark_0701_paper`★
$99,525. Plus `qqq_benchmark_0706_paper` (added 2026-07-17, records CE/CF; NOT
mirrored): $100k buy-hold QQQ from the **07-06** close (started 07-06 to match this
cohort's real start, like `spy_benchmark_0701` — record CF re-seeded it from the
original 07-01), NAV @ 2026-07-16 $97,665 (-2.34%).

**3. 07-06 cohort — 6 LLM-experiment** (inception 2026-07-06): stock arm
`mom_roa_top1_paper` (control, holds **BE**) / `llm_overlay_mom_roa_top1_paper`
(veto→**cash**, BE vetoed) / `llm_cascade_top1_paper` (cascade→**WDC**); sector
arm `sector_top4_paper` (control XLK/XLE/XLI/XLB) /
`llm_overlay_sector_top4_paper` (XLK/XLI/XLB, XLE→cash) /
`llm_cascade_sector4_paper` (XLK/XLI/XLB/**XLV**).

> ⚠️ **Do not confuse** `sector_top4_paper` (07-06 LLM-experiment control) with
> `sector_top4_full_paper` (continuous systematic twin, unbroken since 05-01).
> They hold identical picks going forward; they differ only in pre-07-01 P&L.

**4. Residual weight ladder — 3-cadence experiment** (inception 2026-05-01,
replay-seeded; records BW/CD): the SAME 19-point residual-mom/ROA blend ladder
`residual_w<MM><RR>[_wk|_2wk]_paper` (MM/RR %, top-50, same config as
`residual_roa_6535_paper` otherwise) rebalanced at THREE cadences — **monthly**
(19, no suffix; 05-01/06-03/07-01), **weekly** (19, `_wk`; first trading day each
week), **biweekly** (19, `_2wk`; every other week). 57 ladder sleeves. Forward-test
of whether rebalance FREQUENCY changes where on the blend ladder the edge lives
(extends the BU/BV weight-plateau question). **NOT Alpaca-mirrored, no LLM
decisions.** Full NAV snapshot in record CD. As of the 05-01->07-16 REPLAY
(deterministic, NOT live fills; live forward begins after each cadence's last replay
rebalance — monthly 07-01, weekly 07-13, biweekly 07-06), the LOW-residual/high-ROA
end LEADS all three cadences, INVERTING the BV backtest w80-90 plateau — 10-11wk
replay NOISE (BW carried the same caveat), live forward decides. Weekly/biweekly
rebalance forward via `ladder_forward_rebalance.py` (TradingLadderRebalance, daily
8:30pm, self-decides due-ness); monthly via `rebalance.bat`.

> **WHAT THE LADDER GRADIENT ACTUALLY MEASURES (2026-08-07, record CW) — read
> this BEFORE quoting any slope or r-value from these 57 sleeves.**
> The three cadences bought **identical 05-01 books** (proven, not assumed), so
> weight and cadence separate exactly — the earlier "confounded" reading is
> retracted. Decomposed:
> - **The whole gradient is 05-01 stock selection, not trading.** Buy-and-hold
>   the 05-01 book untouched reproduces slope **-0.1153 (r -0.927)**, steeper
>   than the monthly actual (-0.0296). Dollar-weighted BH: w05-45 **+6.67%** vs
>   w55-95 **+0.23%**.
> - **Rebalancing is net POSITIVE monthly (+2.20pp), neutral weekly, net
>   negative biweekly (-0.71pp)** — all three inside one standard error of zero
>   over 3/13/7 events (per-event sd ~3-6pp). **The cadences are NOT
>   distinguishable in this data.** Transaction cost explains ~2% of the
>   difference (5bps one-way, empirically pinned by the $99,950 inception NAV).
> - **The 19 rungs are NOT 19 observations.** Adjacent-rung Jaccard 0.74-0.94;
>   **w05 vs w95 = 0.04 (4 shared names of 47/49)**. It is a dose-response curve
>   between two near-disjoint portfolios sampled once. Never quote r as significance.
> - **It is ONE MONTH.** May/June/Aug-MTD slopes are flat-to-positive; all of it
>   is **July**, when `spy_benchmark_paper` returned **+0.03%** while `mom_v1/v2/
>   mom_roa_6535` lost **~23.5%**. Survives excluding R1 (weaker) and excluding
>   FGMC; KLAC's 10:1 is the only split in the 05-01 set and the method is
>   split-invariant.
> - Market-orthogonal: survives CAPM (alpha slope r to **-0.96**); high-weight
>   rungs actually have HIGHER up-beta and LOWER down-beta, so the losses arrive
>   on flat/up index days.
> **Therefore: this does NOT refute BV's w80-90 holdout plateau and does NOT
> establish low-residual/high-ROA as better.** What it gives is a live sizing
> number — roughly **0.10-0.14pp of return per weight point per adverse month**.
> Two schedule gaps recorded but not fixed: weekly has **no 07-20 rebalance**,
> biweekly's 07-06→07-28 gap is **22 days**.

> **TWO AUDIT FINDINGS AGAINST THIS LADDER (2026-07-28, record CH) — read before
> citing any ladder number.**
> 1. **The BIWEEKLY arm had never live-rebalanced.** Due-ness was day-based ("is
>    today the first trading day of the week"), so the 2026-07-20 evening miss was
>    unrecoverable; all 19 `_2wk` sleeves sat buy-and-hold from 07-06 while this
>    doc described them as a live 14-day cadence. The weekly arm lost 07-20 too
>    (07-13 -> 07-27). `verify_run` never caught it — it checks NAV continuity and
>    cash, nothing about cadence. FIXED 2026-07-28: due-ness is now PERIOD-based
>    and self-healing, the dispatcher fails loudly (per-sleeve try/except + nonzero
>    exit), and `ladder_rebalance.bat` propagates its exit code instead of letting
>    verify_run's PASS mask it.
> 2. **The ladder carried ~$83k of phantom KLAC loss — ~~HALF-REPAIRED~~ FULLY
>    REPAIRED 2026-08-02 ~20:00 CDT (records CJ → CK → CL → CM; PRD M7 CLOSED).
>    Live `verify_run --mode daily` PASS 76/76, frozen d=±0.0000pp. Cross-rung
>    ladder comparison is TRUSTWORTHY again — see the 2026-08-02 CLOSED note at the
>    end of this block for the real before/after spreads.** The history below is
>    kept for the audit trail; read it in order.
>    `price_cache` never back-adjusted corporate actions, so
>    seeding on 2026-07-17 backdated to 05-01 re-read unadjusted pre-split KLAC
>    history: 48 sleeves booked the same 05-01 trade at $1,727.12 that
>    `residual_roa_6535_paper` booked at $172.71 — ratio exactly 10.0000.
>    - **FIXED**: the cache root cause (`scripts/backadjust_split.py`, 4,327 price
>      rows ÷10 + 4,220 volume ×10; the split cliff is gone) and the 15 surviving
>      OPEN positions (qty×10, price÷10, `entry_value` preserved). Frozen tests
>      unmoved at d=±0.0000pp; 2026-07-31 re-marked for those 15 sleeves so
>      verify_run returns PASS 76/76. The corrective jump is visible and dated at
>      07-30→07-31; earlier NAV rows were deliberately NOT rewritten.
>    - ~~**STILL BROKEN**~~ **[RESOLVED 2026-08-02, record CM]**: the 31 CLOSED
>      positions that exited on/after the 05-13
>      split still hold **−$55,343.70** of phantom realized loss inside those
>      sleeves' CASH. (The 2 that exited 05-11 are legitimately correct, +$276.56.)
>      ~~**Cross-rung ladder comparisons remain NOT trustworthy.**~~ ~~Fixing it needs a
>      historical-state reconstructor that does not exist~~: `paper_mtm.compute_nav`
>      has no historical mode (reads today's cash + today's open positions), and
>      per-date cash can only be rebuilt by replaying entries/exits because there
>      is no `paper_transactions` table. ~1,881 NAV rows would be rewritten.
>    - **2026-08-02 UPDATE (record CK, PRD M7.1/M7.2).** The reconstructor now
>      EXISTS — `scripts/momentum/historical_state.py`, read-only, verified exact
>      on all 76 sleeves ($0.000000 cash delta). But its validation gate FAILED at
>      94.48% (bar: 95%), and the failure is informative: the **cash ledger replays
>      exactly** (1,194/1,195 stored NAV rows), while **historical NAV is NOT
>      reproducible in principle** — `daily_price_refresh.py` re-downloads the last
>      30 days for every ticker with `INSERT OR REPLACE` by design, so a stored NAV
>      row is a snapshot of an input the system revises nightly. **Consequence: the
>      planned M7.4 NAV rewrite would restate those 1,881 rows for four unrelated
>      reasons on top of the KLAC fix and is now BLOCKED.** Recommended path is
>      M7.3 only — repair the 31 closed positions + current cash, leave history
>      alone (same precedent as the 15 open positions above). ~~**Awaiting Evan.**~~
>    - **2026-08-02, M7.3 PASSED ON A COPY (record CL) — Evan chose M7.3-only.**
>      `backadjust_split.py --include-closed` repairs the 31 closed rows
>      (qty×10, entry_price÷10, entry_value preserved, exit_value×10,
>      realized_pnl restated) and corrects each sleeve's cash. On the copy:
>      `historical_state` selfcheck **PASS 76/76, max |cash delta| $0.000000**;
>      frozen tests 4/4 d=±0.0000pp. ~~**LIVE APPLY IS STILL PENDING — Evan runs it
>      (Claude does not write the live DB); commands in record CL.7.**~~ **[APPLIED
>      LIVE 2026-08-02 ~19:54 by Evan — record CM. NOTE: CL.7's commands used cmd.exe
>      `^` continuations, which break in PowerShell 5.1; use one line per command.]**
>      Corrected figures: **31 sleeves, not 33** (a naive date filter returns 33;
>      2 entered pre-split at a CORRECT basis — one is `residual_roa_6535_paper` —
>      and only the `entry_price > $584.93` staleness guard selects the right set).
>      Cash moves **+$85,779.95**, not $55,343.70: the −$55,343.71 phantom loss is
>      removed AND a real **+$30,436.24 gain** is booked (KLAC rose $172→$269 over
>      the exit window). Projected ladder effect: cross-rung spread weekly
>      10.56→7.78pp, biweekly 14.54→12.93pp, monthly 6.32→4.93pp — **no cadence
>      changes its leading rung**, so the low-residual/high-ROA lead is NOT a KLAC
>      artifact.
>    - ✅ **2026-08-02 ~20:00 CDT — CLOSED (record CM, PRD M7 complete).** Evan ran
>      the live apply himself. Live `verify_run --mode daily` → **PASS 76/76**;
>      `historical_state` → PASS 76/76 at **$0.000000**; frozen tests 4/4
>      d=±0.0000pp. The repair also needed a **2026-07-31 NAV re-mark** — the 31
>      repaired sleeves' newest row carried pre-repair cash, and ~10 more were
>      already stale from the record CI rate-limit backfill; neither self-heals
>      (`mtm_catchup` only fills MISSING days). New one-off
>      `scripts/data_audit/remark_nav_day.py` re-marks exactly ONE date for all
>      sleeves (dry-run default, `paper_mtm`'s guards): **41 changed, 35 already
>      correct, 0 failures, net $+88,298.92** = $85,779.95 KLAC cash + $2,518.97
>      restored 07-30/31 prices. That single re-mark also cured the
>      `TradingDailyMTM` FAIL 55/76 seen at 17:18 (record CL.6). It is deliberately
>      NOT the M7.4 span rewrite that record CK ruled out — one date, both causes
>      named, every affected row enumerated before writing.
>      **REAL ladder spreads (live `paper_nav` @ 2026-07-31): weekly 10.56→7.58pp,
>      biweekly 14.54→12.93pp, monthly 6.32→4.93pp; leaders w2080_wk (+5.75%),
>      w0595_2wk (+7.60%), w0595 (+6.69%) — ALL UNCHANGED.** The contamination
>      inflated apparent spread by 1.4-3.0pp but never changed the ranking, so the
>      low-residual/high-ROA lead is confirmed NOT a KLAC artifact. Standing caveat
>      unchanged: ~10-11 week replay-seeded window; live forward decides.

### Systematic sleeve specs

| Sleeve | Factor | Spec file |
|---|---|---|
| mom_v1_paper | 12-1 momentum, top-100 | `trading_bot/strategies/momentum_v1.py` |
| mom_v2_paper | 12-1 momentum, top-50 | `trading_bot/strategies/momentum_v2.py` |
| mom_roa_6535_paper | 65% mom Z + 35% ROA Z, top-50 | `trading_bot/strategies/mom_roa_6535.py` |
| residual_roa_6535_paper | 65% residual-mom Z + 35% ROA Z, top-50 | `trading_bot/strategies/residual_roa_6535.py` |
| residual_w<MM><RR>[_wk\|_2wk]_paper (×57) | MM% residual-mom Z + RR% ROA Z, top-50 (weight ladder, 3 cadences) | `scripts/momentum/paper_rebalance.py` `_strategy_config` (parsed from name) |
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
- **Stop check hardened 2026-07-15 (record CA)**: the stop lookup now matches
  the HELD ticker (`latest_decision_for`) instead of a cascade-contaminated
  `LIMIT 1` row — prevents pairing a position with another name's stop. Latent
  (all-cash), no history repair.
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

### Cascade arm (always-invested) — **UNSTOPPED BY DESIGN**
- **Sleeves**: `llm_cascade_top1_paper` (stock) / `llm_cascade_sector4_paper`
  (sector). A VETO cascades to the next-best candidate instead of going to cash,
  so the sleeve is never idle. Controls are shared with the cash overlays.
- **These two sleeves have NO stop enforcement, and that is deliberate**
  (Evan's decision 2026-08-05, record CR; audit finding E1/6). `llm_cascade_ops.py`
  has no `check-invalidation` subcommand and `daily.bat` runs one only for the two
  CASH overlay modules. A stop exits to CASH, and always-invested is this arm's
  entire distinction from the cash overlays — a stop-to-cash would make it a
  hybrid of the two treatments and destroy the three-way comparison.
  **Cost, stated plainly: these sleeves have no downside control of any kind, so
  their drawdowns are NOT risk-comparable to the cash overlays'.** Rationale in
  `trading_bot/strategies/llm_cascade.py`'s docstring.
- The `invalidation_level` on a logged decision is consumed by the **cash overlay
  sleeve only**. The cascade reads the same rows for their verdicts and ignores
  that column.
- ⚠️ **Reported, not fixed (record CR):** the 2026-08-03 XLU decision logged a HOLD
  with an invalidation of **$44.50 while that day's close was $44.36** — a stop set
  *above* its own entry price, on a rationale whose own text says "Above 50DMA
  (44.96)". XLU has closed below $44.50 every day since (44.36 / 44.11 / 43.66).
  Only the cascade holds XLU, so the level binds nothing today. It is a
  decision-quality datapoint for the kill-switch review, not a data bug.

---

## Infrastructure

### Database
- `var/trades.db` (~5 GB) — all paper positions, NAVs, price cache, XBRL
- Backup: `var/trades.db.bak_pre_spike_cleanup` — DO NOT DELETE
- Tables — **all 18, enumerated 2026-08-05** (the previous list said "18 total"
  and then named only 10, audit finding 17): `alpaca_asset_meta`, `delistings`,
  `fundamentals_cache`, `ingest_state`, `llm_overlay_log`, `paper_nav`,
  `paper_portfolio`, `paper_positions`, `portfolio_state`, `positions`,
  `price_cache`, `sector_cache`, `sector_overlay_log`, `sectors_cache`,
  `signals`, `slippage_log`, `sqlite_sequence`, `xbrl_facts`
  - ⚠️ **`sector_cache` and `sectors_cache` are DIFFERENT tables and both are
    live.** `sector_cache` (6,113 rows) is the one the running system reads and
    writes — `market_data._ensure_cache_schema` creates it, ticker→sector.
    `sectors_cache` (1,493 rows) is the research-only one. Only the latter was
    listed here before, so anyone trusting this file would have queried the
    wrong table.
  - `positions` / `portfolio_state` are the **BACKTEST** tables. ~~that
    `factor_backtest._wipe_state()` truncates on every frozen-test run.~~ Nothing
    paper-trade lives there (record CQ.2). **[2026-08-12, record CZ: the frozen
    tests NO LONGER WRITE THESE — or anything else in the live DB. `_wipe_state()`
    now shadows both tables into per-connection TEMP tables first, so a full
    frozen run leaves `PRAGMA data_version` unmoved. `price_cache` is
    deliberately NOT shadowed, which is why a scratch-DB redirect was the wrong
    fix.
    CONSEQUENCE: the **137 residue rows** in `positions` (+ `portfolio_state.cash
    = $39.262514`) from the last pre-fix run are now **PERMANENT** — the next
    frozen run used to clear them and no longer does, and nothing else deletes
    them. `main.py report` / `dashboard` / `positions` will render them forever as
    a stale portfolio. Cosmetic, not integrity: `paper_positions` is untouched at
    7,271 rows / 3,222 open. Deleting them is Evan's one-line command — record
    CZ.5.]**
  - **There is no `paper_transactions` table** (listed here in error until
    2026-07-28; fills live in `paper_positions`).
  - `price_cache` and `sector_cache` are NOT in `trading_bot/db.py`'s `SCHEMA`
    despite its docstring calling SCHEMA "the authoritative definition of every
    table" — `market_data._ensure_cache_schema()` owns their DDL. Noticed
    2026-08-05 while fixturing a test; left as-is, it is not one of the audit's
    findings.
- **CRITICAL**: never run concurrent `factor_backtest` against same DB — silent corruption

### Key scripts
| Script | Purpose |
|---|---|
| `scripts/momentum/daily_price_refresh.py` | Bulk yfinance refresh (~4,300 tickers) |
| `scripts/momentum/paper_rebalance.py --strategy NAME --top-n N` | Monthly rebalance |
| `scripts/momentum/paper_mtm.py --strategy NAME [--as-of DATE]` | Daily mark-to-market |
| `scripts/momentum/llm_overlay_ops.py candidate\|decide\|rebalance\|check-invalidation` | LLM stock overlay; `check-invalidation --settled` runs nightly in `daily.bat` (record BZ) |
| `scripts/momentum/sector_overlay_ops.py candidate\|decide\|rebalance\|check-invalidation` | LLM sector overlay; `check-invalidation --settled` runs nightly in `daily.bat` (record BZ) |
| `scripts/momentum/seed_spy_benchmark.py` | One-off index-benchmark sleeve seeder (idempotent; `--ticker` — seeded SPY + QQQ controls) |
| `scripts/momentum/check_coverage.py` | Coverage gate (read-only): fails if the day's close count < floor. Wired into `daily.bat` before MTM (M2.1/M2.2) |
| `scripts/momentum/check_anomalies.py` | Anomaly detector (read-only): flags KLAC-class 1-day moves + missing held marks → `var/anomaly_report.log`. Wired into `daily.bat` after MTM, non-blocking (M2.3) |
| `scripts/momentum/check_cache_gaps.py` | Cache-gap auditor (read-only): flags rankable tickers with history holes >5 trading days → `var/cache_gap_report.log`. Wired into `daily.bat`, gated to day 1 of month (record DE T-4; the gate was a no-op until DG fixed the block→goto — it ran DAILY 08-16..08-18) |
| `scripts/momentum/check_month_gate.py [--canary]` | Month gate for `rebalance.bat` (read-only): exits 1 when `rebalance_log.md` already stamps the current calendar month, so the daily-firing `monthy-llm-rebalance` cannot run a second rebalance mid-month on a mis-read of its own prose gate (record DI.2). A **PARTIAL** stamp does NOT refuse — that is a failed run awaiting its retry, and locking it out is the bug audit 2026-08-04 finding 1 fixed. Override: `rebalance.bat --allow-same-month`. Self-check: `--canary` 8/8 |
| `scripts/momentum/verify_run.py --mode daily\|monthly` | Post-run verifier (read-only): per-sleeve NAV continuity (to last SETTLED day), **(b1) per-date ledger cash — every row since `LEDGER_EPOCH=2026-07-31` must match `historical_state.state_at()`, hard FAIL (record DD; replaced the `navs[-1]`-only recon that hid bad older rows)**, **(b2) price drift — reported, NEVER failed (measures `price_cache` revision, which is by design per CK.4)**, position-count (monthly), no-pre-inception, **plus run-level (e) rebalance cadence** — `rebalance_log.md`'s date must be in the settled month or later, else FAIL (record CO; closes the CN blind spot — an un-rebalanced sleeve passes (a)-(d) perfectly, it just holds a stale book) → `var/verify_report.log`. Wired into `daily.bat` (M3.2), `rebalance.bat` (record BS), `ladder_rebalance.bat` (record CG) |
| `scripts/momentum/mtm_catchup.py [--dry-run]` | Self-healing MTM: marks every settled missing trading day (incl today) for all sleeves; skips pending days + never overwrites/back-marks across a rebalance. Runs in `daily.bat` after refresh (M3.5) |
| `scripts/momentum/ops_stamp.py` | Appends a dated one-line run-status stamp to `var/ops_status.log` (M3.4) |
| `scripts/momentum/experiment_report.py [--md]` | LLM-experiment kill-switch tracker + control-vs-treatment NAV divergence (read-only) → console / `docs/experiment_report_<date>.md` (M4.1/M4.2) |
| `scripts/backup_trades_db.py [--keep N] [--dry-run]` | Rotating `VACUUM INTO` backup of `trades.db` → `var/backups/`, keep newest 3, disk-guard (M5.1) |
| `scripts/data_audit/remark_nav_day.py --date D [--execute]` | Re-marks ONE already-existing `paper_nav` date for every sleeve (record CM). Dry-run by default, enumerating each row's before/after; only rewrites rows that actually move. Keeps `paper_mtm`'s weekend/pre-inception/coverage guards. Use when a stale-but-PRESENT NAV row needs correcting — `mtm_catchup` only fills MISSING days. **One date at a time by design**: a broad span rewrite is what record CK ruled out |
| `scripts/backadjust_split.py --ticker T --ratio N --effective D [--include-closed] [--execute]` | Back-adjusts `price_cache` for a split and repairs un-adjusted paper positions. Dry-run by default. `--include-closed` (M7.3, record CL) also repairs CLOSED rows that exited on/after D and corrects sleeve cash — opt-in, and the only mode that relaxes the cliff guard (to the CACHE update only, so a re-run can still never double-divide history). Never touches `paper_nav` |
| `scripts/momentum/historical_state.py [--mode selfcheck\|validate]` | Reconstructs a sleeve's cash + open positions AS OF any past date by replaying `paper_positions` (read-only; there is no `paper_transactions` table). `selfcheck` = M7.1 done-check vs the live portfolio; `validate` = M7.2 full-history diff vs stored `paper_nav`. Ledger replay is exact; NAV recompute is NOT reproducible for past dates — see record CK before using it to rewrite anything |

### Batch files
| File | When to run |
|---|---|
| `scripts/momentum/daily.bat` | Daily after market close (auto via `TradingDailyMTM` at 5:15pm) |
| `scripts/momentum/rebalance.bat` | 1st trading day of each month (auto via the `monthy-llm-rebalance` Claude task). **Refuses if this calendar month is already stamped** (`check_month_gate.py`, record DI.2) — pass `--allow-same-month` for a deliberate re-run. All 15 step gates use explicit `%errorlevel%` capture, not `if errorlevel 1` (record DI.1) |
| `scripts/momentum/ladder_rebalance.bat` | Nightly weekly/biweekly ladder rebalance (auto via `TradingLadderRebalance` 8:30pm; no-op on evenings where both cadences have already been served this period). Propagates the dispatcher's exit code (record CH) |
| `scripts/add_price_cache_date_index.py` | One-time migration, APPLIED 2026-07-28 (record CH): partial index on `price_cache(key_date) WHERE kind='close' AND price IS NOT NULL`. Every date query used to full-scan 37.5M rows; the coverage gate went 7.1s -> 0.271s. Dry-run by default, `--execute` to apply, reversible via `DROP INDEX idx_pc_close_date` |
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
  `VACUUM INTO` backup). Logs: `var/backup.log` (added 2026-07-09, M5.2).
  **Was silently DEAD 2026-07-09 → 2026-07-28** (record CH): `DisallowStartIfOnBatteries`
  + `StopIfGoingOnBatteries` made every run return `-2147020576` (0x800710E0) without
  ever launching cmd.exe, so `backup.log` kept showing the 07-09 run and the 5 GB DB
  sat on a single 19-day-old copy. Both flags cleared and `StartWhenAvailable` set
  2026-07-28; verified by a real run (4.77 GB in 26s, 2 generations retained).
  If backups stop appearing again, check those power flags FIRST.
- **`TradingLadderRebalance`** — fires `ladder_rebalance.bat` daily at 8:30 PM,
  `StartWhenAvailable` (added 2026-07-17 at 7 PM, record CD; moved to 8:30 PM same
  day, audit record CG — the measured ~35-45 min monthly run from 6:03 PM left the
  7 PM slot a too-thin margin against a two-writer collision). Forward rebalance for
  the WEEKLY + BIWEEKLY residual ladders: `ladder_forward_rebalance.py` self-decides
  whether today is a weekly/biweekly rebalance day (holiday-aware; biweekly parity is
  ordinal-weeks-since-2026-04-27, immune to 53-ISO-week years). Ends with its own
  `verify_run --mode daily`. Logs: `var/last_ladder_run.log`
  **Since 2026-08-26 (record DM) it passes `strict_fill_date=True`: any leg whose
  reference bar is not `as_of`'s own close is SKIPPED, not filled carry-forward.**
  Prompted by 08-24, when 41 exits across 19 sleeves filled off the 08-21 bar
  (TPL 383.64 vs the true 373.45) for **$457.00** of proceeds the real bar did not
  support. A skipped leg is self-healing — due-ness is period-based, so the next
  rebalance inside the period retries it. **First live exercise: 2026-08-31**
  (both cadences due). Note an aggregate coverage gate would NOT have caught this:
  08-24 settled at 5,144 closes over a 5,000 floor while five held names were
  missing, and 08-26 is BLOCKED at 4,267 while 211/216 held names have a close —
  the guard has to be per-ticker. **`monthly_rebalance.py` is deliberately NOT
  wired** (identical exposure, runs 6:03pm so MORE exposed; one-line change,
  Evan's call — open item).
- **`\llm rebal`** — Monthly, day 1, 5:59 PM. **Despite the name it is NOT a
  rebalance**: its action is a `mouse_event` wake-nudge, i.e. a wake fired 4
  minutes before the 6:03 PM `monthy-llm-rebalance` Claude task below.
  ~~**CURRENTLY FAILING and has been since 2026-08-02** — `LastTaskResult`
  `-2147020576` (0x800710E0, "operator or administrator refused the request")
  with `StopIfGoingOnBatteries=True`.~~ **CORRECTED 2026-09-20 (audit finding 9):
  this is FALSE as of today.** Live `schtasks /query /v` reads `Last Run Time:
  9/1/2026 5:59:00 PM`, `Last Result: 0` — it succeeded. The claim was true when
  written and was never re-checked. `StopIfGoingOnBatteries=True` is still set,
  so the failure mode remains available; it just has not fired since 08-02.
  **This is the identical failure mode documented
  for `TradingWeeklyBackup` above**, whose fix (clear the power flags, set
  `StartWhenAvailable`) was applied 2026-07-28 and never applied here. Next
  opportunity 2026-09-01 — the same run DH's new `rc=2` decide guard first
  matters on. Nothing surfaces this: no log, no check. **OPEN, Evan's to change**
  (record DI.5).
- **`\Wake PC`** (daily 5:29 PM) / **`\Wake PC 2`** (daily 7:59 AM) — the same
  `mouse_event` wake-nudge, paired to the evening and morning MTM slots. They
  fire AFTER their slots, which is correct: both MTM tasks carry
  `StartWhenAvailable`, so a wake after the slot triggers the missed run.
  Undocumented here until 2026-08-19 (record DI.5).

> **Task-table completeness (record DI.5).** DE T-5 and DG.2 both state the task
> table was "re-synced against the live list" — true of the *Claude-scheduler*
> table below, not this one. This section listed 5 tasks while `schtasks`
> registered 8 non-Microsoft ones. The three above were the gap.

### Claude agent scheduled tasks (SEPARATE from the Windows tasks above)

> **2026-08-20 (audit of `daily-trade-check-2`) — the scheduled tasks now have MECHANICAL enforcement and a drift detector.** The audit's crit finding was that every prohibition in the daily-report specs ("READ/RESEARCH ONLY", "NEVER `git add -A`", "never push", "never rebalance") was prose with **zero enforcement** — the deny list held two `Read(./.env*)` rules and nothing else, against a **public** remote, and it had already failed once for real (record DI.3). Three things changed:
> 1. **CORRECTED 2026-08-20 by record DK - read this, not the original line.** Deny rules were added to BOTH `.claude/settings.json` and `~/.claude/settings.json` (the scheduled agent's cwd is not guaranteed), but **four of the nine were dead syntax**: a LEADING `:*` is literal, Claude Code `Bash(...)` rules are PREFIX matchers, and the dangerous token sits mid-command (`...python.exe -m scripts.momentum.<rebalancer>`), so a glob could never have worked. Those four were **removed, not repaired**. What is live now: **(a)** five working prefix rules in both files - `Bash(git push:*)`, `Bash(git add -A:*)`, `Bash(git add .:*)`, `Bash(git reset --hard:*)`, `Bash(git rebase:*)`; **(b)** a PreToolUse hook, `scripts/hooks/pretooluse-trading-guard.js`, registered on `Bash|PowerShell` in both files, which is what actually blocks the rebalancer, the decide path, Alpaca order-submit and `git push`. Self-check: `node scripts\hooks\test_trading_guard.js` -> 20/20. **It has one accepted false positive: it also blocks merely MENTIONING those tokens in a shell command (e.g. a `grep` for one), which is deliberate - a false positive costs a rephrase, a false negative costs a real trade.**
> 2. **The live task specs are now snapshotted into the repo** at `docs/scheduled-tasks/<taskId>.SKILL.md` (4 of them; 5 since 2026-09-26, record EC, `hellow` added). The live files under `~/.claude/scheduled-tasks/` are in NO git repo, so an edit to a spec that authorizes repo writes or trades was previously undetectable. `daily-audit` STEP 0c now diffs live-vs-snapshot every morning — **when you edit a task spec, re-copy it or the audit will report drift.**
> 3. **`daily-audit` gained a STEP 0** (missing session / duplicate session / spec drift / cron drift / trade-guard live - STEP 0e RUNS the hook's self-check rather than asserting rule strings, because asserting a string that cannot fire is a green light on a dead gate). The missing-session check exists because **2026-08-17 has a pre-market entry and no post-market one** and nothing detected it — a scheduled report that never fires produces no error and no artifact.
>
> Both daily-report specs were also rewritten with a PRE-FLIGHT block: local-`date` header (the 19:00 task fires 22s past the UTC date line under CDT), holiday abort, duplicate-header abort, `mode=ro` DB open, month-boundary lock check, and an unmarked-NAV rule (**never present a carried-forward NAV as a marked close**). `/landing-check` now runs **BEFORE** the commit, not after — it had been gating nothing, and fabricated detail reached three of five consecutive entries.

**Added 2026-08-05 (audit finding 16).** These run through Claude's own
scheduler, not `schtasks`, so they appear in NO `schtasks /query` output and were
in no inventory in this repo — three of them enabled and firing daily, two of
them **committing to this repo** (local only — the push clause was removed 2026-08-19 after audit DI.3/E5; re-verified and re-stated 2026-08-20). Read the live list with
`mcp__scheduled-tasks__list_scheduled_tasks`; prompts live in
`C:\Users\evan.EVANFREDY\.claude\scheduled-tasks\<id>\SKILL.md`.

| Task | Cron | State | What it does |
|---|---|---|---|
| `monthy-llm-rebalance` | **`0 18 1-5 * *`** (~6:03pm, days 1-5 ONLY) — **4th drift, live-read 2026-09-06; was `0 18 * * *`. NOT restored, Evan's call.** Next run 2026-10-01. | **enabled** | The monthly rebalance. Self-gates on `rebalance_log.md`. **The typo is load-bearing — never rename.** |
| `daily-trade-check` | `0 7 * * 1-5` (~7:07am weekdays) | **enabled** | Pre-market research report → appends to `daily_report.md`, renders the HTML twin, then /landing-check, then `git add` (those 2 files only) + `commit`. **Local only — never pushes** (audit DI.3/E5) |
| `daily-trade-check-2` | `0 19 * * 1-5` (7:00pm weekdays) | **enabled** | Post-close analysis report, same append + landing-check + commit. **Local only — never pushes** (audit DI.3/E5). Moved from `0 18` to `0 19` on 2026-08-04 (record CQ.3/E2) because it was reading `paper_nav`/`paper_positions` mid-rebalance. **Found drifted back to `0 17` (5:00pm, 15 min before `TradingDailyMTM`) on 2026-08-18 and restored to `0 19` (record DG) - third documented cron drift on this machine; read the live list, never this table** |
| `hellow` | `0 12,17,22 * * *` (12:00 / 17:00 / 22:00 daily) | **enabled** | Evan's own routine (prompt: `Hello (just say hi back)`). Created 2026-08-20 23:25. **Intentional - Evan confirmed it stays** (record DK.2). Documented here because an undocumented enabled task is the exact condition that made the two deleted strays hard to reason about. Note the 17:00 fire is ~15 min before `TradingDailyMTM`. |
| ~~`hellllo`~~ | ~~`0 12 * * *`~~ | **DELETED 2026-08-20** | Stray test task (`hello (Just say "hi" back)`), fired daily for months. Removed in the 2026-08-20 audit (finding 13); 10 run sessions archived. `SKILL.md` left on disk at `~/.claude/scheduled-tasks/hellllo/` so the prompt is recoverable. |
| ~~`hello-just-say-hi-back`~~ | ~~`0 17 * * *`~~ | **DELETED 2026-08-20** | Second stray test task, same prompt; fired ~10 min before `TradingDailyMTM`. Removed in the 2026-08-20 audit (finding 13); 7 run sessions archived. `SKILL.md` left on disk. |
| `daily-audit` | `0 7 * * *` (~7:05am daily) | **enabled** | Runs `/audit` + `/landing-check` on active projects (this project's audits land here, in HANDOFF, and in the record). Found live 2026-08-16 (audit finding T-5) — was undocumented here entirely. |
| ~~`cohort-0706-deploy`~~ | ~~manual~~ | **absent** | One-time 07-06 cohort deploy, fired 2026-07-07. NOT in the live task list as of 2026-08-18 (record DG); DE T-5 wrote "disabled" over an earlier correct read of "absent" |
| `check-0803-rebalance` | one-time | disabled | Post-mortem of the 08-03 rebalance, fired 2026-08-04 |
| `audit-all-projects-2026-08-21` | one-time | disabled | Cold `/audit` sweep of all 11 projects under `D:\ClaudeCode`, 2 Opus workers each, findings only. Fired 2026-08-22. Added to this table 2026-09-06 — it was live and in no doc. |

> ✅ **Cron re-confirmed 2026-08-05 20:13 CDT** — the record CN note asked a future
> session to re-list `monthy-llm-rebalance` because the confirming call was
> blocked by the permission classifier. Done: it reads **`0 18 * * *`, "At 06:03
> PM, every day", enabled**, `lastRunAt` 2026-08-05. The CN fix HELD. Per the
> standing rule this cron has drifted 3× — keep reading it from the tool, never
> from this table.
>
> **Two writers to `daily_report.md`**: `daily-trade-check` and
> `daily-trade-check-2` both append and commit locally; neither pushes. Their windows are 11 hours apart,
> and both are explicitly scoped to `git add daily_report.md daily_report.html`
> (never `-A`), so an in-progress working tree is not swept in.

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
- **📊 Overview** (default): status strip, then per-cohort panels (Original ·
  7/1 cohort · residual ladder × 3 cadences), each a table (α vs SPY + α vs QQQ,
  SPY/QQQ rows tinted) + compact NAV %-chart with dotted SPY/QQQ benchmark
  lines; top movers across held names, LLM experiment panel, concentration
  warnings. 76 sleeves total.
- **🔬 Single sleeve**: positions, NAV history, vs-SPY benchmark.
- **📈 NAV charts**: overlay %-from-inception + absolute-$ for all sleeves.

Chart conventions (as of 2026-06-10):
- %-hover shows 3 decimal places (`+.3f`)
- Traces added in descending latest-value order (unified hover reads highest→lowest)
- S&P 500 control is `spy_benchmark_paper` read from DB (no network)

---

## What's been ruled out (25+ experiments)

Full list in the `sleeves_verdict` memory file. (Path corrected 2026-07-28: the
`memory/` directory is NOT in this repo — those files live in Claude's
per-project memory at
`C:\Users\evan.EVANFREDY\.claude\projects\D--ClaudeCode-Trading\memory\`,
outside git.) Summary of failure patterns:

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
- ~~**Single-name LLM sleeves are deep underwater** (FN position, both
  −19%).~~ **[WRONG — corrected 2026-08-05, audit finding 15. There are ZERO
  open FN rows in the DB (2 closed ones, both pre-dating the 07-01 reset). The
  stock arm currently holds: control `mom_roa_top1_paper` = **MU**, treatment
  `llm_overlay_mom_roa_top1_paper` = **cash** (BE vetoed), cascade
  `llm_cascade_top1_paper` = **STX**. The FN claim survived two re-inceptions.]**
  The standing point does hold: the experiment is designed for 12mo/30 picks —
  current n is noise, and a single-name sleeve can be deep underwater at any time.
- **No slippage realism check yet** — ~~deferred until ~20 real fills (post-Aug
  2026)~~. ~~**[2026-08-05: the fills now exist (231 orders, 0 rejects — 07-07 and
  08-03), so this is no longer blocked on data; it is blocked on M6.1
  `fetch_alpaca_fills.py` being built. Still a real limitation until then.]**~~
  **[2026-08-11, record CY — this limitation is now PERMANENT under the current
  design, and it is not a to-do. Execution slippage is NOT MEASURABLE here: the
  sim books at a CLOSE, the mirror filled intraday (July) and at the next
  session's OPEN (August), and Alpaca rejects market-on-close orders 15:50–19:00
  ET and queues them to the following close after 19:00 ET, so the 18:03-local
  monthly slot cannot reach the same day's auction at all. **Evan therefore
  REDEFINED M6 to measure IMPLEMENTATION SHORTFALL** (sim booked reference price
  vs realised mirror fill, drift INCLUDED, per batch, never pooled): 07-07 n=98
  mean **+100.15bps**, 08-03 n=68 mean **+97.64bps**.
  **The true half-spread is UNMEASURED — not 5bps confirmed, not 100bps.
  `HALF_SPREAD_BPS` stays at 5.0 and must NOT be recalibrated off shortfall
  (`docs/slippage_memo_2026-08-11.md`).** Getting a real spread number needs a
  batch where the sim's reference and the mirror's fill are contemporaneous,
  which is a live-behaviour change and Evan's call.]**
- **No short support** in `paper_trader` — blocks deploying L/S vol-target
  even as paper trade. Not building until the strategy passes in-sample.

---

## Monthly operations (first trading day of each month)

> ✅ **September 2026 IS rebalanced — but BY HAND, and the automation is still
> broken.** Records **DN** (18:15, the block) → **DO** (20:14, independent audit
> confirming it) → **DP** (22:20, the resolution). Read in that order.
>
> **2026-09-01, done:** Evan ran the six decisions + `rebalance.bat` himself at
> 21:55 CDT. Exit 0 in 14m40s, stamped **`2026-09-01 / OK`**, `verify_run
> --mode monthly` **PASS 76/76**, frozen tests **d=±0.0000pp** on all 4 configs,
> Alpaca **128 orders, all HTTP 200** (accepted at submit — *not* proof of fills;
> `verify_run` never calls the API). Sleeve book verified against
> `paper_positions` directly, because an un-rebalanced sleeve passes verify too.
>
> 🛑 **STILL BLOCKED for 2026-10-01 and every month after. BLOCKED-ON-EVAN.**
> The `monthy-llm-rebalance` task fired on time on 09-01, the month gate opened,
> the data gate passed — then every decision-logging call was **denied by
> `scripts/hooks/pretooluse-trading-guard.js`** (rule 3, installed 2026-08-20,
> record DK). No bypass flag exists, so the task cannot complete its own Step 3.
> 09-01 was the first monthly rebalance since that hook shipped; DK verified the
> rules fire, not what else they fire on. **September was rescued by hand inside
> four hours — that is Evan being awake, not a mechanism.** Decide one of:
> give the hook a narrow override the scheduled task's own launch env can present
> (record DO.1's shape — *not* a loosened regex), or accept that monthly
> rebalances are manual and change the task file to say so.
>
> ⚠️ **Open (DN.3 / DO.1 finding 2): the guard is bypassed wholesale by `cmd /c
> rebalance.bat`** — PROVEN empirically on 09-01, which ran through it. The hook
> only sees the command string handed to the Bash tool, never the subprocesses it
> spawns, so the wrapper runs four guarded operations (live Alpaca orders
> included) untouched. Evan invoking it is the intended path; the point is that an
> *agent* is one `cmd /c` from the same thing. Unfixed.
>
> ⚠️ **Open (DN.4 / DO.1 findings 3-4): `overlay_prep` under-reports what is
> owed.** Its stock section carries a decision forward when the #1 name is
> unchanged, but the consumer does an **exact-date** lookup and refuses without a
> same-day row — the gather says "nothing owed", then the rebalance refuses. It
> also prints a ticker-blind `latest_decision` under the wrong name. Unfixed.

**Now automated** via the `monthy-llm-rebalance` Claude scheduled task (cron
`0 18 1-5 * *`, ~6:03pm local on days 1-5 ONLY — **corrected here 2026-09-20,
audit finding 33: this line said `0 18 * * *` and contradicted the task table
above, which has the live value. Read the live cron, never a doc.** Shifted back
from a drifted `30 17`/~5:33pm on
2026-07-11 per Evan, to clear a rebalance-day two-writer overlap with the 5:15pm
daily MTM; record BS; self-gates on `rebalance_log.md` so only the first
trading day of the month does real work).

> ⚠️ **THIS TASK'S SCHEDULE HAS DRIFTED FROM ITS DOCUMENTATION THREE TIMES**
> (`0 8 * * *` → record AP; `30 17 * * *` → record BS; `0 18 1 * *` → record CN).
> **Read the cron from `mcp__scheduled-tasks__list_scheduled_tasks`, never from
> this file** — any statement here is a claim about the past.
> **2026-08-02 ~22:56 CDT (record CN):** found live at **`0 18 1 * *`** — day 1
> of the month ONLY, `nextRunAt` 2026-09-01. Since 2026-08-01 was a **Saturday**,
> the entire August rebalance (29 sleeves + all LLM decisions + `alpaca_sync
> --execute`, i.e. M6's gate) would have been silently skipped, and would NOT
> have self-healed. Restored to `0 18 * * *` with Evan's OK; the tool confirmed
> "At 06:03 PM, every day." The confirming re-`list` was blocked by the
> permission classifier — **a future session should re-list and confirm.**
> `verify_run` structurally cannot catch this: an un-rebalanced sleeve has
> perfectly continuous NAV and perfectly reconciled cash, it just holds a stale
> book (same blind spot as the record CH biweekly-ladder finding, one layer up). It runs `rebalance.bat`, which since 2026-08-19 **refuses outright if this calendar month is already stamped** (`check_month_gate.py`, record DI.2 — the prose self-gate above is no longer the only thing standing between a daily-firing task and a mid-month rebalance). A deliberate re-run needs `--allow-same-month`. It
dispatches through `scripts/momentum/monthly_rebalance.py` (29 rebalance + 30
MTM sleeves, all `--broker-realistic`) instead of the old per-sleeve .bat lines
— the "all 10 paper lines" phrasing here was obsolete as of 2026-07-28. It also
does the LLM overlay decisions per
`docs/overlay_decision_runbook.md`, MTMs everything (per-sleeve `paper_mtm
--force` so the rebalance day is marked despite partial same-day coverage,
record BS), runs `verify_run --mode monthly`, and fires
`alpaca_sync --all --execute`. ~~First live fire under this schedule:
2026-08-01.~~ **2026-08-01 was a Saturday and the cron was day-1-only, so
nothing fired; the first live fire is 2026-08-03** (record CN). That is also the
first run of the `monthly_rebalance.py` dispatcher and a Monday — record CG's
flagged collision-risk shape (1st trading day == Monday).
If monthly rebalances stop running, check the CRON FIRST (it has drifted 3×),
then that the task is enabled (memory `monthly_rebalance_trigger_timing_bug.md`).

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
- Per-verdict memory files (sleeves_verdict, data_audit, etc.) — **not in this
  repo**; they live in Claude's per-project memory at
  `C:\Users\evan.EVANFREDY\.claude\projects\D--ClaudeCode-Trading\memory\`
  (outside git). The bare `memory/` path used here until 2026-07-28 never resolved.
- `daily_report.md` — owner's daily trading journal

---

## Next-session prompt (paste-ready)

```
Trading project (D:\ClaudeCode\Trading). Read in this order: HANDOFF.md (top
blocks are 2026-09-22..09-29, records DV-EF) -> the record's front-matter TOC ->
PRD_ROADMAP.md. The append-only record is ground truth; HANDOFF is the only live
snapshot.

STATE (verified 2026-09-29 ~21:50 CDT):
- Record EF work is UNCOMMITTED (guard, trading-day/coverage gates, strict LLM
  fills, backtest shadow, split detectors). Ask Evan before committing; no
  Co-Authored-By trailer.
- 76 sleeves; 2026-09-22..09-28 all marked 76/76; verify_run PASS. Frozen
  tests 4/4 d=+/-0.0000pp. paper_nav is SEALED (stage 5 triggers live since
  2026-09-23): restate history only via remark_nav_day --execute --reason.
- daily_price_refresh retries the per-ticker yfinance rate limit (60/120/240 s)
  and exits 1 when >=5% of live tickers are still missing -- that aborts the
  monthly rebalance by design. Refresh runtime is now ~9 min.
- PUBLISHED: 65620db was pushed 2026-09-26 22:12:07 CDT (7 minutes after record
  ED said it was held), and 3c5f511 on 2026-09-29 14:28:50 CDT. 134 of 215
  public commits carry the Co-Authored-By trailer. Its source was the
  codebase-memory bins (conventions.md / tooling.md), not the task specs; both
  bins were corrected 2026-09-29.

THEN:
- Monthly Thu 2026-10-01: MANUAL (Evan). The guard now denies both the decide
  step and the .bat step of the scheduled task. Do not route around it. After
  the run, check for STALE-SKIP lines and their printed retry commands.
- BLOCKED-ON-EVAN: alpaca_keys.env Read-deny (both settings files, see EF);
  MLI 2026-06-05 cliff needs an external corporate-action source (EF item 9).
- Stage 5 leftovers: stamp_rebalance_log atomicity (os.replace), alpaca_sync
  per-account isolation, 2 cache-poisoning bugs (warm_fundamentals,
  fetch_earnings_dates).
- Stage 6: TOL_PCT 0.05 -> 0.001; wire the orphaned scripts/momentum/test_*.py
  (now incl. test_compute_nav_asof, test_paper_nav_seal,
  test_refresh_rate_limit) into daily.bat; auto_adjust=False in 5 research
  benchmarks; 16 files with stale mom_v2 baselines (truth: in-sample 3.5407,
  holdout 26.465).
- Stage 8: the trading guard, six bypasses. EVAN APPROVES THE DIFF BEFORE ANY
  CODE (his rule, 2026-09-06).
- A3: staleness detector (record appendices newer than HANDOFF's stamp).
- BLOCKED-ON-EVAN, small: audit finding 35 (Alpaca keys file into the Read deny
  list in .claude/settings.json).

HARD RULES: never run anything that trades; no .bat execution. DB read-only
(file:...?mode=ro) unless the task writes; write paths are tested on a DB copy
first (SQLite backup API, ~12 s). Frozen tests after ANY Python change, real
output pasted. Stay out of 17:00-18:30 and 19:45-21:00 local for DB-heavy work.
Records: append ONLY with append-record-entry.js, ASCII only. Commit only when
asked, with NO Co-Authored-By trailer; never publish to the remote.

KNOWN FRICTION: the PreToolUse guard denies any Bash command whose STRING merely
contains a guarded token (it fired on writing this very prompt through a
heredoc). Author content with the Write tool and keep the Bash string clean.

LESSONS 2026-09-22..09-26: a None/NaN from Yahoo is not a missing bar until it
survives the retry cooldowns (DZ misread one; corrected in EC). Test any grep
pattern in the C locale -- a bracket cannot hold the 3-byte em dash (EC). Cite
line numbers only from a direct grep -n.
```
