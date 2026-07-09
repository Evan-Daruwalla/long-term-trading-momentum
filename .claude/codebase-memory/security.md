# security — secrets, keys, live-trade guards

- `alpaca_keys.env` holds LIVE Alpaca API keys — never print, log, commit, echo, or move it. Gitignored (`.gitignore`: `*.env`, `alpaca_keys.env`). (CLAUDE.md; verified 2026-07-08)
- No secrets or the DB are tracked in git: `.gitignore` excludes `.env`, `*.env`, `alpaca_keys.env`, `var/`, `*.db`, `*.db-journal`. `git ls-files` confirmed none present. Safe to push. (verified 2026-07-08 before the first GitHub push)
- Alpaca integration is PAPER-only and live is HARD-GUARDED in code (`trading_bot/execution/alpaca_client.py` — paper base URL default, `is_live()` guard). Claude never creates accounts, enters keys, or fires LIVE orders — automated PAPER routing only. (memory `age_constraint`, `alpaca-paper-integration`)
- `alpaca_sync.py` `--execute` submits real (paper) orders; dry-run is the default. Only the scheduled `monthy-llm-rebalance` task and Evan run `--execute`; never invoke it ad-hoc. (CLAUDE.md hard rules)
- Never run anything that trades: no `paper_rebalance`, no `*_ops rebalance/decide`, no `alpaca_sync --execute`. Dry-run/read modes only. (CLAUDE.md)
- `.claude/settings.json` denies `Read(./.env)` / `Read(./.env.*)`. (settings.json permissions)
