# project-memory index — Trading

Read first: important.md - critical facts, injected by the important-inject hook (added 2026-09-30)

New standard bins (2026-09-30; first line STATUS: = stub, see that line): decisions, people, timeline, glossary, compliance, budget, operations, services, experiments, writing, hardware, important

- security.md — secrets, alpaca_keys.env, PAPER-only live guards, no-trade rules, the PreToolUse trading guard + its 2 OPEN holes (updated 2026-09-06)
- performance.md — 5 GB DB read-only rule, no concurrent factor_backtest, timing window (updated 2026-07-08)
- architecture.md — 76 sleeves/4 families, paper_* tables, key scripts, Alpaca mirror, automation, M2 guardrails + M3 automation-safety + M3.5 self-healing MTM + M4 experiment reporting + M5 backups + paper_mtm coverage gate (updated 2026-07-28)
- features.md — LLM-overlay experiment, broker-realistic sizing, frozen-test contract (updated 2026-07-08)
- conventions.md — price_cache flag, module invocation, docs/append-only rules (updated 2026-07-08)
- gotchas.md — shadow-file leak, cmd.exe batch traps (`if errorlevel` is >=; a block ends at the first `)` in echo text), Bash deny rules are PREFIX matchers, the guard's .bat wrapper escape, yfinance quirks, graphify (updated 2026-09-06)

Standards bins (updated 2026-07-15; the committed choices, one home each):
- dependencies.md — Python venv, yfinance (auto_adjust=False), pandas/numpy, streamlit/plotly, httpx, markdown, watchdog, rich, SQLite; pins in requirements. **No pytest, no alpaca package** (Alpaca is a hand-rolled httpx wrapper) — corrected 2026-07-28.
- ui.md — **N/A, no UI/UX** (only the internal Streamlit dashboard; no end-user flow).
- testing.md — the frozen-test contract (d=±0.0000pp, paste real output) + verifiers + test-on-a-copy rule.
- data.md — price_cache invariant, trades.db read-only, no concurrent factor_backtest, paper_* schema, sacred history.
- tooling.md — module invocation, the 6 scheduled tasks (daily/morning/ladder/weekly-backup/dashboard + monthy-rebalance), timing window, HTML render, .bat gotchas. **Read the LIVE cron via `list_scheduled_tasks`, never this file or HANDOFF — 4 documented drifts (records AP, BS, CN, DO.3).**
- disclosure.md — what may leave this project (stub 2026-09-06; Evan is 17, PAPER only, numbers must trace to the record). ALWAYS load before any case study / portfolio / public README.

Cross-bin invariants (always load these):
- `price_cache` closes are split-adjusted, dividend-UNADJUSTED (`auto_adjust=False`). Every writer honors it.
- After ANY Python change: `.venv\Scripts\python.exe -m trading_bot.strategies.test_strategies` must print d=±0.0000pp (pytest not installed; the module is the invocation). Paste real output.
- DB `var/trades.db` opens read-only unless the task writes; NEVER run concurrent `factor_backtest`.
- NEVER fabricate data/fills/results; NEVER run anything that trades (`--execute`, `paper_rebalance`, `*_ops rebalance`). alpaca_keys.env is secret.
- Record is append-only; `HANDOFF.md` is the only live snapshot; roster lives in HANDOFF (not CLAUDE.md).
- Append record entries with `node ~/.claude/skills/project-memory/append-record-entry.js`, NEVER by hand — hand-splicing overwrote three sessions' entries once (record BT).
- Enforcement of "never trade" lives in the agent-only PreToolUse hook, NOT in the Python entry points: Evan's own terminal must stay able to run these by hand (record DP.2).
