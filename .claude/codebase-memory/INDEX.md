# codebase-memory index — Trading

- security.md — secrets, alpaca_keys.env, PAPER-only live guards, no-trade rules (updated 2026-07-08)
- performance.md — 5 GB DB read-only rule, no concurrent factor_backtest, timing window (updated 2026-07-08)
- architecture.md — 17 sleeves/3 families, paper_* tables, key scripts, Alpaca mirror, automation, M2 guardrails + M3 automation-safety + M3.5 self-healing MTM + M4 experiment reporting + M5 backups + paper_mtm coverage gate (updated 2026-07-10)
- features.md — LLM-overlay experiment, broker-realistic sizing, frozen-test contract (updated 2026-07-08)
- conventions.md — price_cache flag, module invocation, docs/append-only rules (updated 2026-07-08)
- gotchas.md — shadow-file leak, cmd.exe batch traps, yfinance quirks (incl. live 07-08 incomplete pub), graphify (updated 2026-07-09)

Standards bins (updated 2026-07-15; the committed choices, one home each):
- dependencies.md — Python venv, yfinance (auto_adjust=False), pandas, pytest, streamlit, alpaca SDK, SQLite; pins in requirements.
- ui.md — **N/A, no product frontend** (only the internal Streamlit dashboard).
- testing.md — the frozen-test contract (d=±0.0000pp, paste real output) + verifiers + test-on-a-copy rule.
- data.md — price_cache invariant, trades.db read-only, no concurrent factor_backtest, paper_* schema, sacred history.
- tooling.md — module invocation, scheduled tasks (daily/morning/monthy-rebalance), timing window, HTML render, .bat gotchas.

Cross-bin invariants (always load these):
- `price_cache` closes are split-adjusted, dividend-UNADJUSTED (`auto_adjust=False`). Every writer honors it.
- After ANY Python change: `.venv\Scripts\python.exe -m trading_bot.strategies.test_strategies` must print d=±0.0000pp (pytest not installed; the module is the invocation). Paste real output.
- DB `var/trades.db` opens read-only unless the task writes; NEVER run concurrent `factor_backtest`.
- NEVER fabricate data/fills/results; NEVER run anything that trades (`--execute`, `paper_rebalance`, `*_ops rebalance`). alpaca_keys.env is secret.
- Record is append-only; `HANDOFF.md` is the only live snapshot; roster lives in HANDOFF (not CLAUDE.md).
