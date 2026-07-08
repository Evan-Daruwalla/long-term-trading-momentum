# Project: Trading

Paper-trading systematic-equity platform. Evan is 17 — the deliverable is the
**track record and the engineering rigor**, not "make money now": every strategy
gets in-sample/held-out validation before it's trusted, decisions are logged and
never backdated, data bugs are audited and documented rather than hidden. At 18
the proven sleeves convert to live trading backed by a defensible history.

## Start of session (read in this order)

1. `HANDOFF.md` — current sleeve roster, NAVs, experiment status, automation.
2. Latest `docs/state_<date>.md` — current snapshot.
3. `PRD_ROADMAP.md` — the standing ops/infra plan (Fable 5, 2026-07-07); work
   its next open task unless Evan directs otherwise.

The append-only record (`docs/Project Record — Full Chronological History.md`)
is ground truth — when anything disagrees with it, the record wins. The sleeve
roster lives in HANDOFF.md; do NOT trust a copy of it anywhere else (including
old versions of this file — a stale roster here caused confusion before).

## Stack & commands

- Python venv. Invoke modules as `.venv\Scripts\python.exe -m scripts.momentum.<module>`
  from the repo root (matches all existing usage).
- **Frozen regression tests**: `.venv\Scripts\python.exe -m pytest
  trading_bot/strategies/test_strategies.py` — 4 pinned configs, must stay at
  **d=±0.0000pp after ANY Python change**, even "obviously unrelated" ones.
  Paste the real output; never say "should pass".
- DB: `var/trades.db` (~5 GB SQLite). Open **read-only** (`file:...?mode=ro`)
  unless the task explicitly writes. Frozen backup
  `var/trades.db.bak_pre_spike_cleanup` — DO NOT DELETE.
- Dashboard: Streamlit at http://localhost:8501 (`TradingDashboard` task);
  logs `var/dashboard.log`.
- Scheduled tasks: `TradingDailyMTM` (5:15pm daily → `daily.bat`, logs
  `var/last_daily_run.log`) and `monthy-llm-rebalance` (monthly ~6pm — **the
  typo is real; renaming it breaks the automation chain**).

## Hard rules

- **NEVER fabricate data, fills, prices, or results.** Missing data is reported
  as missing. Standing order, zero exceptions.
- **Never run anything that trades**: no `paper_rebalance`, no
  `*_ops rebalance/decide`, no `alpaca_sync --execute`. Those belong to the
  scheduled tasks and Evan. Dry-run/read modes only, and only when a task says so.
- **price_cache convention**: closes are split-adjusted, dividend-UNadjusted
  (yfinance `auto_adjust=False`). Every writer honors it; never add one that
  doesn't. (daily_price_refresh violated it until the 2026-06-09 audit.)
- **Never run concurrent `factor_backtest` against the same DB** — silent
  corruption. Always sequential.
- **NAV/decision history is sacred**: LLM decisions are never backdated, NAV
  history never rewritten. Data that looks wrong gets REPORTED in the record;
  deleting/fixing is Evan's call.
- **Timing**: stay out of the 5:00–6:30pm local window (daily MTM) and the 1st
  trading day of the month (rebalance) for anything DB-heavy. Prefer mornings.
- **Write-path changes are tested on a copy first**, never live-first (check
  free disk before copying the 5 GB DB).
- `alpaca_keys.env` holds live API keys: never print, log, commit, or move it.
- HTML twins (record, daily_report) are **script-generated only** — regenerate
  via `.venv\Scripts\python.exe -m scripts.render_record_html` /
  `render_daily_report_html.py`, never hand-edit. `daily_report.md` is
  newest-LAST (opposite of intuition).

## Definition of done

Work is not finished until ALL of these hold. Run them; don't assume.

1. The task's own done-check (from `PRD_ROADMAP.md` or Evan's instruction)
   passes, verified by actually running it.
2. Frozen tests print d=±0.0000pp — actual output stated in the report.
3. Record entry appended (absolute date + approx time, WHAT/WHY/HOW), HTML twin
   regenerated.
4. HANDOFF.md / state doc updated if reality shifted (new sleeve, automation
   change, audit finding).
5. Local commit when a task authorizes it. Never push without Evan's instruction.

## Documentation cadence (set 2026-05-28)

Update the record and `docs/state_*.md` **every 3 prompts** of real work
(a hook reminds you).

- **Record** (`docs/Project Record — Full Chronological History.md` — renamed
  2026-06-30 from `docs/record_2026-05-27.md`, same file): chronological log.
  Entries are timestamped (date + approximate time). Append as the next
  `# Appendix <XX> - Title (date)`, never edit prior appendices.
- **State** (`docs/state_<date>.md`): always-current snapshot. Create a NEW
  dated file when reality shifts significantly; mark the old one superseded at
  the top.

If the cadence slips, catch up at the next prompt and note in the record that
the cadence was missed by N prompts so future-me can audit.

## Project-specific quirks (durable — roster-level detail lives in HANDOFF.md)

- **Don't confuse `sector_top4_paper`** (LLM-experiment control) **with
  `sector_top4_full_paper`** (continuous systematic twin, unbroken since
  05-01). Identical picks going forward; they differ only in pre-07-01 P&L.
- **yfinance split misapplication tell**: a >1000% single-day move in the
  movers panel (KLAC 2026-06-12 applied a 10:1 split to history days early;
  needed manual position/NAV repair).
- **Data audit 2026-05-28** invalidated all prior in-sample numbers. Anything
  from before that date needs re-validation. `MAX_HIST_RATIO=100` is baseline
  universe-filter behavior; `NON_STOCK_TICKERS` (2026-06-09) keeps warmed
  ETFs/indices out of the stock universe.
- **cmd.exe batch-file gotcha** (2026-07-01, record Appendix AS):
  `rebalance.bat`/`daily.bat` silently corrupt their ENTIRE parse (garbled
  `'X' is not recognized` errors) if the file contains a single non-ASCII byte
  (e.g. an em-dash in a REM) or if a stray root file shadows a builtin name (a
  0-byte file named `ECHO` broke every bare `echo.` line). If a scheduled run
  aborts fast with garbled shell errors, check those two things before
  suspecting a data/logic bug. Keep .bat edits pure ASCII.
- Stray 0-byte format-spec-named files (`4`, `10.2f}`) recur in the repo root
  from an unidentified evening process (record Appendix AW) — harmless, never
  commit them, source still unfound.
