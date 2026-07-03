# Trading

A systematic-equity paper-trading research project. Multiple momentum/factor
strategy sleeves run in parallel against a shared SQLite store, with an
LLM-overlay arm testing whether an LLM veto/selection layer improves on pure
quantitative signals. Everything here is paper trading — no live brokerage
execution.

The goal isn't "make money now," it's building evaluation rigor: every
strategy gets an in-sample / held-out backtest before being trusted, and the
workflow itself (audits, walk-forward validation, clean re-inception after
data bugs) is treated as the real asset.

## Structure

- `trading_bot/` — core package: execution engine, factor library, scoring,
  strategies, data sources (EDGAR Form 4), reporting/dashboard, DB layer.
- `scripts/` — operational tooling:
  - `momentum/` — daily price refresh, mark-to-market, rebalancing, LLM
    overlay ops (the day-to-day paper-trading pipeline).
  - `form4/` — insider Form-4 filing ingestion and backtesting.
  - `data_audit/` — one-off audits, backfills, and data-integrity checks.
- `docs/` — dated audit reports, research notes, and point-in-time state
  snapshots.
- `HANDOFF.md` — running summary of current strategy sleeves and status.
- `MOMENTUM_DESIGN.md` — design rationale for the momentum factor sleeves.

## Running it

```
scripts\start_all.bat        # bring up the dashboard + refresh all sleeves
scripts\momentum\daily.bat   # daily price refresh + mark-to-market (auto-runs at market close)
```

Or drive individual subcommands via `main.py` (Form-4 scoring/backtesting)
and the `scripts.momentum.*` / `scripts.form4.*` / `scripts.data_audit.*`
modules directly. Requires Python 3.10+ and the packages in
`requirements.txt` (httpx, yfinance, rich).

## Current state

See [`HANDOFF.md`](HANDOFF.md) for the live sleeve roster and status, and
`docs/` for dated audits and research notes. `CLAUDE.md` documents
project-specific conventions and known quirks (data conventions, known gotchas).

## Code navigation

This repo has a [Graphify](https://graphify.net/) knowledge graph checked out
locally (`graphify-out/`, gitignored) covering `trading_bot/` + `scripts/`,
refreshed automatically by `daily.bat`.
