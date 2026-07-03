# Handoff

## Goal

Build a paper-trading systematic-equity strategy on US stocks. Owner is 17,
can't open a real brokerage until 18 — so the immediate goal is **build
rigor + a track record**, not "make money now." Every strategy gets a proper
in-sample / held-out evaluation before it's trusted; the workflow itself is
the asset.

## Current state — Phase 2d, 5 systematic + 3 LLM-experiment + 1 benchmark

**Last updated: 2026-06-13**

> **2026-06-13 — major data fix + sleeve re-inception (record Appendix AA).**
> A systemic cache-gap bug (~815 tickers incl. AAPL/GOOGL missing 2019-2025
> data) had phantom-ranked stale-momentum names into the sleeves (~half of every
> momentum book). Backfilled the missing data (2.25M rows), re-baselined the
> frozen tests, and **re-inceptioned the 6 contaminated sleeves fresh at $100k on
> clean data as-of 2026-06-12**. Their old 2026-05-01 → 06-12 record was phantom-
> contaminated (archived, invalid). Backtest numbers below are STALE pending
> re-validation on the backfilled cache.

### Running sleeves (9 total in DB)

| Sleeve | Type | Top-N | Inception | NAV | Return | Notes |
|---|---|---:|---|---:|---:|---|
| mom_roa_6535_paper | systematic | 50 | 2026-05-01 | $106,579 | +6.58% | backdated, clean data |
| residual_roa_6535_paper | systematic | 50 | 2026-05-01 | $106,134 | +6.13% | backdated |
| sector_top4_paper | systematic | 4 | 2026-05-01 | $103,803 | +3.80% | ETFs, untouched |
| spy_benchmark_paper | benchmark | — | 2026-05-01 | $102,928 | +2.93% | untouched |
| mom_v1_paper | systematic | 100 | 2026-05-01 | $102,358 | +2.36% | backdated |
| mom_v2_paper | systematic | 50 | 2026-05-01 | $101,394 | +1.39% | backdated |
| mom_roa_top1_paper | LLM control | 1 | 2026-06-12 | $99,950 | — | AAOI (new clean #1) |
| llm_overlay_mom_roa_top1_paper | LLM treatment | 1 | 2026-06-12 | $100,000 | — | cash (AAOI VETOed) |
| llm_overlay_sector_top4_paper | LLM treatment | 4 | 2026-06-05 | $99,962 | — | seeded 06-12, VETO XLE |

The 4 systematic sleeves were **backdated to 2026-05-01 on clean data** (06-13),
aligned with the ETF sleeves. The **LLM stock pair stays at 2026-06-12** — its
treatment decisions can't be honestly backdated (would inject hindsight). Clean
live returns above are 05-01→06-12; mom_roa leads, residual 2nd, both beat SPY.

### Systematic sleeve specs

| Sleeve | Factor | Spec file |
|---|---|---|
| mom_v1_paper | 12-1 momentum, top-100 | `trading_bot/strategies/momentum_v1.py` |
| mom_v2_paper | 12-1 momentum, top-50 | `trading_bot/strategies/momentum_v2.py` |
| mom_roa_6535_paper | 65% mom Z + 35% ROA Z, top-50 | `trading_bot/strategies/mom_roa_6535.py` |
| residual_roa_6535_paper | 65% residual-mom Z + 35% ROA Z, top-50 | `trading_bot/strategies/residual_roa_6535.py` |
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
- **Current state**: both hold FN (Fabrinet). Treatment exited FN at $600 stop
  (Jun-09); control still holds. Divergence starting to accumulate.
- **Kill switch**: 12 months / 30 picks, drop if scores don't predict returns
  OR treatment doesn't beat control over 30 picks.

### Macro sector overlay
- **Control**: `sector_top4_paper`
- **Treatment**: `llm_overlay_sector_top4_paper` — sector_top4 picks with
  a 4-prompt macro veto (rates/valuation/breadth/bear-case); veto → cash for
  that 25% slot
- **Current state**: UNSEEDED (cash, $100k, no decisions yet)
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
| `scripts/momentum/llm_overlay_ops.py candidate\|decide\|rebalance` | LLM stock overlay |
| `scripts/momentum/sector_overlay_ops.py candidate\|decide\|rebalance` | LLM sector overlay |
| `scripts/momentum/seed_spy_benchmark.py` | One-off SPY sleeve seeder (idempotent) |

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

1. Run `rebalance.bat` (after market close; it refreshes prices, rebalances
   all 5 systematic sleeves, MTMs everything incl. SPY benchmark).
2. For LLM stock overlay: if control sleeve changes its underlying name,
   run the 3-prompt eval first, log a BUY/VETO decision via
   `llm_overlay_ops.py decide`, then re-run `rebalance.bat`.
3. For sector overlay (when seeded): run `sector_overlay_ops.py candidate`,
   then 4 macro-prompt decisions via `decide`, then `rebalance.bat`.
4. Review dashboard Overview after rebalance — check NAV continuity, cash
   recon, stale-data warnings.

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
- `docs/state_2026-05-28.md` — current project state snapshot
- `docs/paper_trading_ops.md` — ops guide (daily/monthly procedures)
- `docs/research_2026-06-09_algo_candidates.md` — June algo-research report
- `memory/` — per-verdict memory files (sleeves_verdict, data_audit, etc.)
- `daily_report.md` — owner's daily trading journal
