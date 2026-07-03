# Project: Trading

## Documentation cadence (set 2026-05-28)

Update `docs/record_*.md` and `docs/state_*.md` **every 3 prompts** to reflect
current project state.

- **Record** (`docs/record_2026-05-27.md` + later appendices — **renamed
  2026-06-30 to `docs/Project Record — Full Chronological History.md`**, same
  file, content unchanged): chronological log. Entries are timestamped (date +
  approximate time). Append as Appendix C/D/etc, never edit prior appendices.
- **State** (`docs/state_2026-05-28.md` is current; older snapshots kept):
  always-current snapshot. Create a NEW dated file when reality shifts
  significantly (audit, baseline change, deployment change). Mark old state
  files as superseded at the top.

If the cadence slips, do a catch-up update at the next prompt. Note in the
record that the cadence was missed by N prompts so future-me can audit.

## Karpathy guidelines reminder
- Simplicity first - smallest code that solves the problem
- Surgical changes - touch only what is needed
- Surface tradeoffs - state assumptions, do not hide confusion
- Define success criteria - loop until verified

## Project-specific quirks
- Paper-trading SEVENTEEN strategy sleeves in parallel across 3 groups
  (updated 2026-07-01 — verified against `paper_nav` DISTINCT strategy_name):
  - **6 systematic + benchmark** (inception 2026-05-01): `mom_v1_paper`
    (top-100 momentum), `mom_v2_paper` (top-50 momentum), `mom_roa_6535_paper`
    (top-50 mom+ROA Z-score), `residual_roa_6535_paper` (top-50 residual-mom+
    ROA), `sector_top4_full_paper` (top-4 of 11 SPDR sectors, continuous
    twin — see split below), `spy_benchmark_paper` (S&P 500 control, real
    $100k buy-and-hold SPY, MTM'd daily but NEVER rebalanced — no
    paper_rebalance config branch, MTM-only in the bats; seed/re-MTM via
    `scripts/momentum/seed_spy_benchmark.py`; dashboard SPY line reads this
    sleeve's `paper_nav`, NOT yfinance).
  - **6 LLM-experiment sleeves, 2 arms x 3 variants** (ALL reset to a fresh
    $100k / 2026-07-01 inception on 2026-06-30 via
    `scripts/data_audit/align_llm_07_01.py --confirm` for a clean head-to-head;
    archived reversibly to `var/align_llm_07_01_archive.json`; record
    AK.5/AK.6): stock arm = `mom_roa_top1_paper` (control, always buys #1
    mom_roa name) / `llm_overlay_mom_roa_top1_paper` (cash-veto treatment) /
    `llm_cascade_top1_paper` (always-invested cascade treatment — walks the
    top-10 mom_roa names until a BUY instead of going to cash); sector arm =
    `sector_top4_paper` (control — see split below) /
    `llm_overlay_sector_top4_paper` (cash-veto treatment, 4-prompt macro
    rubric) / `llm_cascade_sector4_paper` (cascade treatment — walks all 11
    sectors until 4 HOLDs). Cascade sleeves are a 3rd, higher-bar test of the
    LLM as active selector (must out-pick raw momentum, not just beat cash),
    run alongside — not replacing — the cash-veto arm. Shared kill switch:
    12mo / ≥30 picks, dropped if scores don't predict forward returns or
    treatment doesn't beat control.
  - **5-sleeve 7/1 clean-start cohort** (inception 2026-07-01; the 3 marked *
    mirror to real Alpaca PAPER accounts via `alpaca_sync --execute`):
    `mom_v1_0701_paper`, `mom_v2_0701_paper`, `mom_roa_6535_0701_paper`*,
    `residual_roa_6535_0701_paper`* (dup configs of the May systematic
    sleeves — `paper_rebalance._strategy_config` strips the `_0701` infix to
    reuse base configs), `spy_benchmark_0701_paper`*.
  - **`sector_top4_paper` vs `sector_top4_full_paper`**: the 06-30
    LLM-experiment reset desynced `sector_top4` from the 5-way systematic
    comparison (it had run since 05-01), so it was split in two — the plain
    sleeve is now the LLM-experiment control (07-01 inception), `_full` is
    the continuous systematic twin restored from the same archive (05-01,
    unbroken, 41 pre-reset nav rows preserved). Both hold identical picks
    going forward; they differ only in pre-07-01 P&L. Don't confuse them in
    analysis or dashboard reads.
- **cmd.exe batch-file gotcha** (found 2026-07-01, record Appendix AS):
  `rebalance.bat`/`daily.bat` will silently corrupt their ENTIRE parse (fails
  fast with garbled `'X' is not recognized` errors, not a real error message)
  if the file contains a non-ASCII byte (e.g. an em-dash in a REM comment) or
  if a stray file in the project root shadows a builtin name (a 0-byte file
  literally named `ECHO` broke every bare `echo.` line). If a scheduled
  rebalance run aborts fast with garbled shell errors instead of real python
  output, check for non-ASCII bytes in the `.bat` and stray shadow files
  before suspecting a data/logic bug.
- DB at `var/trades.db` (~5 GB). Backup at
  `var/trades.db.bak_pre_spike_cleanup` from 2026-05-27.
- price_cache CONVENTION: closes are split-adjusted but dividend-UNadjusted
  (yfinance `auto_adjust=False`). Every writer must use that flag —
  daily_price_refresh violated it until the 2026-06-09 audit caught + repaired
  the mixed-basis seam.
- Data audit 2026-05-28 invalidated all prior in-sample numbers.
  Anything from before that date needs re-validation.
- Universe filter `MAX_HIST_RATIO=100` is now baseline behavior. Frozen spec
  regression tests use this filter. `NON_STOCK_TICKERS` (2026-06-09) keeps
  warmed ETFs/indices out of the stock universe.
- Concurrent `factor_backtest` runs against same DB corrupt state.
  Always run sequentially.

---

## Ruflo / Claude-Flow integration (activated 2026-06-27)

ruflo v3 is wired into this project: MCP server in `.mcp.json`, runtime config in
`.claude-flow/config.yaml`, and hooks + 30 skills / 17 agents / 16 commands under
`.claude/`. The custom docs-cadence hook above is preserved alongside ruflo's
hooks in `.claude/settings.json`.

- **Coordination is via MCP tools** (run inside the Claude Code session — these
  work today): discover with `ToolSearch("memory")`, `ToolSearch("swarm")`.
  Key tools: `memory_store`, `memory_search`, `swarm_init`, `agent_spawn`,
  `hooks_route`.
- **When to swarm**: 3+ files, new features, cross-module refactors, security or
  performance work. NOT for single-file edits, 1–2 line fixes, or questions.
- **Before a big task**: `memory_search` for prior patterns; **after success**:
  `memory_store` what worked (namespace `patterns`).
- **CAVEAT — autonomous daemon/background workers are NOT active**: they need the
  `claude` CLI on PATH or `ANTHROPIC_API_KEY`, neither of which is set (this
  machine runs the Claude Code desktop app, not a PATH CLI). The MCP tools above
  work regardless; only the standalone background-worker daemon is unavailable.
  To enable it later: install the Claude Code CLI on PATH or set
  `ANTHROPIC_API_KEY`, then `npx ruflo@latest daemon start`.
