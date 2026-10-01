# important - Trading

> Critical facts: getting one wrong is irreversible or expensive, invalidates
> results, or breaks a live external constraint. Numbered, dated, newest last.
> CLAUDE.md wins on conflict. Never remove an entry without telling Evan.
> Keep entries short; detail lives in the topic bin. ASCII only.
> Created 2026-09-30 from CLAUDE.md, HANDOFF.md and the bins (Skills record EA follow-up).

## 1. Never run anything that trades (2026-09-30)
**What:** no `paper_rebalance`, no `*_ops rebalance/decide`, no `alpaca_sync --execute`. Those belong to the scheduled tasks and Evan; dry-run/read modes only, and only when a task says so.
**Constrains:** the trade guard (`scripts/hooks/pretooluse-trading-guard.js`) also denies any Bash command that NAMES a dispatcher module or `rebalance.bat`, even `cat`/`grep` - use the Read/Grep tools. Never route around it.
**Why:** a model-placed order changes the paper book and the track record, which is the deliverable.
**Source:** CLAUDE.md:48-50; HANDOFF.md 2026-09-29 EF block; detail in security.md.

## 2. Frozen regression tests after ANY Python change (2026-09-30)
**What:** `.venv\Scripts\python.exe -m trading_bot.strategies.test_strategies` - 4 pinned configs must print d=+/-0.0000pp. pytest is NOT installed.
**Constrains:** paste the real output, even for "obviously unrelated" changes; never "should pass".
**Why:** the frozen tests are what keeps every historical result comparable.
**Source:** CLAUDE.md:24-29; detail in testing.md.

## 3. History is sacred: never fabricate, backdate or rewrite (2026-09-30)
**What:** never invent data, fills, prices or results; never backdate an LLM decision; never rewrite NAV history. `paper_nav` is SEALED (live since 2026-09-23): repair only with `remark_nav_day --date D --execute --reason "..."`.
**Constrains:** data that looks wrong is REPORTED in the record; deleting or fixing it is Evan's call.
**Why:** the defensible track record is the point of the project.
**Source:** CLAUDE.md:46-47, 68-70; gotchas.md:18.

## 4. alpaca_keys.env - never open, print, log, commit or move (2026-09-30)
**What:** it holds the Alpaca API keys (a PAPER account).
**Constrains:** no read, no cat, no copy. BLOCKED-ON-EVAN: the Read-deny for it in both settings files is not added yet.
**Why:** a leaked key is a credential incident on a public repo.
**Source:** CLAUDE.md:75; HANDOFF.md 2026-09-29 EF block; detail in security.md.

## 5. The database: read-only by default, copy first, keep the frozen backup (2026-09-30)
**What:** `var/trades.db` (~5 GB SQLite) opens read-only (`file:...?mode=ro`) unless the task writes. Write-path changes are tested on a copy first (check free disk). `var/trades.db.bak_pre_spike_cleanup` - DO NOT DELETE.
**Constrains:** never run concurrent `factor_backtest`; stay out of 5:00-6:30pm local and the 1st trading day for anything DB-heavy.
**Why:** `price_cache` is not shadowed, so a write collision corrupts shared state; the backup is the only pre-cleanup copy.
**Source:** CLAUDE.md:30-32, 54-67, 71-74; detail in data.md.

## 6. price_cache convention (2026-09-30)
**What:** closes are split-adjusted, dividend-UNadjusted (yfinance `auto_adjust=False`). Every writer honors it.
**Constrains:** never add a writer that does not.
**Why:** a mixed basis silently corrupts NAV (the MLI split restatement, record EJ, 2026-09-30).
**Source:** CLAUDE.md:51-53; HANDOFF.md 2026-09-29 EF block.

## 7. Scheduled task name typo is load-bearing (2026-09-30)
**What:** the Claude agent task is `monthy-llm-rebalance` - the typo is real.
**Constrains:** never rename it.
**Why:** renaming breaks the monthly automation chain.
**Source:** CLAUDE.md:40-42; detail in tooling.md.

## 8. Paper only until Evan decides otherwise - his age is RECORDED INCONSISTENTLY (2026-09-30)
**What:** CLAUDE.md:3 and disclosure.md say Evan is 17 (proven sleeves convert to live trading at 18), but Citoya's security.md (Billing heading) says he has been 18 since 2026-09-08. Unresolved - ask Evan; do not resolve it from the docs.
**Constrains:** until Evan says otherwise, nothing may imply live trading or real capital, and no live-conversion work starts.
**Why:** going live is irreversible and moves real money; the repo is public.
**Source:** CLAUDE.md:3-7; disclosure.md:9-22; Citoya citoya-v2 security.md (Billing).

## 9. LIVE 2026-10-01: the monthly rebalance is MANUAL (2026-09-30)
**What:** Steps 3 and 4 of the scheduled task are denied by the guard; Evan runs it. Afterwards look for STALE-SKIP lines and run the printed `RETRY ... --as-of <D>` line. LQDA fell 57% on the 09-30 bar (70.69 -> 30.26), held by 6 sleeves - check it is real news before the monthly ranks on it.
**Constrains:** do not attempt the rebalance; do not "fix" LQDA data without evidence.
**Why:** a wrong bar feeds the monthly ranking for a whole month.
**Source:** HANDOFF.md 2026-09-29 EF block. Remove this entry (telling Evan) once 2026-10-01 is done.

## 10. Never push; commit only when authorized; no Co-Authored-By (2026-09-30)
**What:** the GitHub remote is public and real (published 2026-09-26 and 2026-09-29).
**Constrains:** commits only when a task authorizes them; Evan pushes.
**Why:** public history is permanent.
**Source:** CLAUDE.md:93, 134; HANDOFF.md 2026-09-29 EF block.
