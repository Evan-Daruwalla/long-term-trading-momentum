# data — Trading

Last updated 2026-07-15. Canonical home for the data/schema standards. The
price_cache convention, trades.db read-only rule, and no-concurrent-backtest
rule are also always-load cross-bin invariants (INDEX).

## The #1 data invariant
- **price_cache**: closes are SPLIT-ADJUSTED, DIVIDEND-UNADJUSTED (yfinance
  `auto_adjust=False`). EVERY cache writer honors it; never add one that doesn't.
  (`daily_price_refresh` violated it until the 2026-06-09 audit.)

## The DB
- `var/trades.db` (~5 GB SQLite). Open **read-only** (`file:...?mode=ro`) unless
  the task explicitly writes. Frozen backup `var/trades.db.bak_pre_spike_cleanup`
  — DO NOT DELETE. Backups via `scripts/backup_trades_db.py` (SQLite `VACUUM
  INTO`, never a bare copy of the live WAL DB) → `var/backups/`.
- **NEVER run concurrent `factor_backtest` against the same DB** — silent
  corruption. Always sequential.

## Schema (paper-sim tables — structural detail in architecture.md)
- `paper_portfolio`, `paper_positions` (open/closed), `paper_nav`
  (nav_date, total_nav), `paper_transactions`; plus `price_cache`,
  `llm_overlay_log`, `sector_overlay_log`.
- Universe filters: `MAX_HIST_RATIO=100` (baseline), `NON_STOCK_TICKERS`
  (2026-06-09, keeps warmed ETFs/indices out of the stock universe),
  `MIN_TRADING_DAY_COUNT=1000` (excludes market-closed noise days in guardrail checks).

## Sacred-history rule
- NAV/decision history is SACRED: LLM decisions never backdated, NAV never
  rewritten. Data that looks wrong is REPORTED in the record; deleting/fixing is
  Evan's call.
- Coverage floor `check_coverage.coverage_status()` = max(5000, 90%×10-day-median);
  only the daily.bat catch-up should mark NAVs (one-writer process convention,
  not code-enforced).
