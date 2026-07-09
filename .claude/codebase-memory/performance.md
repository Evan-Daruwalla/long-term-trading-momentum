# performance — DB scale, hot paths, timing constraints

- `var/trades.db` is a ~5 GB SQLite DB (positions, NAVs, `price_cache`, XBRL, decision logs). Open READ-ONLY (`file:...?mode=ro`) unless the task explicitly writes. (CLAUDE.md)
- **NEVER run concurrent `factor_backtest` against the same DB — silent corruption.** Always sequential. The frozen tests route through `factor_backtest`, so don't run them alongside anything else touching the DB. (CLAUDE.md)
- Timing exclusion: stay out of 5:00–6:30pm local (the 5:15pm `TradingDailyMTM` writes the DB) and the 1st trading day of the month (rebalance). Prefer mornings for DB-heavy work. (CLAUDE.md, PRD_ROADMAP §4)
- Write-path changes are tested on a COPY of `trades.db` first (check free disk before copying 5 GB), never live-first. (CLAUDE.md)
- `daily_price_refresh` persists Volume alongside Close from one yfinance download, so the whole universe's volume is fresh daily at zero extra cost — the old per-rebalance `warm_held_volumes` pass was removed as redundant (record Appendix AI). (HANDOFF)
- Frozen regression tests run ~30s (2 short windows × 2 strategies) via `python -m trading_bot.strategies.test_strategies`. (test_strategies.py docstring)
