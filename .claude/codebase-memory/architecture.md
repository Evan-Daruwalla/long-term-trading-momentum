# architecture — system shape

Roster is authoritative in `HANDOFF.md`, NOT here and NOT in CLAUDE.md (moved out 2026-07-08 to end duplication drift). This bin is structural only.

- **17 sleeves in 3 families** (`var/trades.db`): (1) continuous May systematic + benchmark (inception 2026-05-01), (2) the 07-06 clean-start cohort — 5 systematic `_0701` dups + `spy_benchmark_0701`, (3) 6 LLM-experiment sleeves (stock + sector × control/overlay/cascade). Deployed 2026-07-07 (record AV). (HANDOFF)
- Paper-sim tables: `paper_portfolio` (strategy_name, cash, initialized_at), `paper_positions` (status open/closed, qty, entry_*), `paper_nav` (nav_date, total_nav), `paper_transactions`; plus `price_cache`, `llm_overlay_log`, `sector_overlay_log`. (HANDOFF)
- Key scripts (all `scripts/momentum/` unless noted): `paper_rebalance.py`, `paper_mtm.py`, `daily_price_refresh.py`, `llm_overlay_ops.py`, `sector_overlay_ops.py`, `llm_cascade_ops.py`, `seed_spy_benchmark.py`; `trading_bot/execution/{alpaca_client,alpaca_accounts,alpaca_sync,fractionability}.py`. (HANDOFF, verified this session)
- Alpaca mirror (`alpaca_sync.py`): mirrors 3 sleeves (residual_roa_6535_0701, mom_roa_6535_0701, spy_benchmark_0701) into 3 paper accounts by target-weight × account equity, market DAY orders, `--execute`-gated. `fractionability.py` (`alpaca_asset_meta` cache) → whole-share fallback for non-fractionable names in BOTH sim and mirror (record AT). (alpaca_sync.py, verified 2026-07-08)
- Automation: `TradingDailyMTM` (5:15pm → `daily.bat`), `monthy-llm-rebalance` (Claude scheduled task, cron `0 18 * * *`, self-gates on `rebalance_log.md`; first live fire 2026-08-01), `TradingDashboard` (Streamlit :8501). (HANDOFF, memory)
- Docs render: `scripts/render_record_html.py` exposes shared `render(src,out,title,topbar)`; `render_daily_report_html.py` reuses it. `gh_slugify` makes GitHub-compatible anchors; renderer asserts `broken: 0`. (verified this session)
