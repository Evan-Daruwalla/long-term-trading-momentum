# security — secrets, keys, live-trade guards

- `alpaca_keys.env` holds LIVE Alpaca API keys — never print, log, commit, echo, or move it. Gitignored (`.gitignore`: `*.env`, `alpaca_keys.env`). (CLAUDE.md; verified 2026-07-08)
- No secrets or the DB are tracked in git: `.gitignore` excludes `.env`, `*.env`, `alpaca_keys.env`, `var/`, `*.db`, `*.db-journal`. `git ls-files` confirmed none present. Safe to push. (verified 2026-07-08 before the first GitHub push)
- Alpaca integration is PAPER-only and live is HARD-GUARDED in code (`trading_bot/execution/alpaca_client.py` — paper base URL default, `is_live()` guard). Claude never creates accounts, enters keys, or fires LIVE orders — automated PAPER routing only. (memory `age_constraint`, `alpaca-paper-integration`)
- `alpaca_sync.py` `--execute` submits real (paper) orders; dry-run is the default. Only the scheduled `monthy-llm-rebalance` task and Evan run `--execute`; never invoke it ad-hoc. (CLAUDE.md hard rules)
- Never run anything that trades: no `paper_rebalance`, no `*_ops rebalance/decide`, no `alpaca_sync --execute`. Dry-run/read modes only. (CLAUDE.md)
- `.claude/settings.json` denies `Read(./.env)` / `Read(./.env.*)`. (settings.json permissions)

## Agent-vs-trade enforcement (added 2026-09-06)

- **`scripts/hooks/pretooluse-trading-guard.js`** (PreToolUse, matcher `Bash|PowerShell`) is the mechanism that enforces what CLAUDE.md and every task spec only state in prose. 5 rules: `paper_rebalance`, `_ops rebalance`, `_ops decide`, `alpaca_sync --execute`, `git push`. Always exits 0; blocks via `permissionDecision:"deny"`. Self-check `node scripts/hooks/test_trading_guard.js` — 20/20 as of 2026-09-06. (record DK)
- **It fires ONLY on Claude's Bash/PowerShell tool calls.** Evan's own terminal does not pass through it — which is deliberate and load-bearing: it is how he rescued the September rebalance by hand on 2026-09-01. Do NOT move enforcement into the Python entry points; that would block his legitimate manual runs. Keep enforcement in the agent-only layer. (record DP.2)
- **Two OPEN holes, both Evan's call, neither fixed as of 2026-09-06:**
  1. **Wrapper escape** — see `gotchas.md`; a `.bat` walks past all 5 rules. Fix proposed 2026-09-06 (static scan of `.bat` contents, recursive, comment-stripped), NOT approved and NOT written.
  2. **Guard-vs-automation collision** — rule 3 (`/_ops\s+decide/i`) denies exactly the step `monthy-llm-rebalance` Step 3 needs, with no bypass flag and no way for the hook to tell which session is calling. The task therefore CANNOT complete itself; every month is manual until this is decided. 2026-10-01 hits the identical denial. (records DN.2, DO.1 finding 1, DP.6)
- **A guard denial in a transcript is NOT evidence an agent tried to trade** — it false-positives on documentation text naming the token.
