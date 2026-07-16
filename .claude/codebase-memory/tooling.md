# tooling — Trading

Last updated 2026-07-15. Canonical home for run/automation + commands.

## Module invocation
- ALWAYS `.venv\Scripts\python.exe -m scripts.momentum.<module>` (or
  `-m trading_bot...`) from the repo root — matches all existing usage.

## Scheduled tasks (the automation chain)
- `TradingDailyMTM` — 5:15pm daily → `daily.bat` (goto flow: refresh → coverage
  gate → mtm_catchup → anomaly → graphify → verify → stamp; exits 0 on a normal
  pending day). Log `var/last_daily_run.log`.
- `TradingMorningMTM` — 7:45am → `morning_refresh.bat` (heals a day left pending
  at 5:15pm; record BY, 2026-07-15).
- `monthy-llm-rebalance` — monthly Claude-agent task → SKILL.md Step 4 runs
  `rebalance.bat`; cron `0 18 * * *` (~6:00pm; shifted from ~5:33pm on 2026-07-11
  to clear a two-writer overlap with the 5:15pm MTM). **The typo "monthy" is REAL
  — renaming it breaks the chain.**
- `TradingWeeklyBackup` — Sun 9am. `TradingDashboard` — Streamlit :8501.

## Timing window (avoid for DB-heavy work)
- Stay out of 5:00–6:30pm local (daily MTM) and the 1st trading day of the month
  (rebalance). Prefer mornings.

## Docs render (HTML twins — SCRIPT-GENERATED only)
- `.venv\Scripts\python.exe -m scripts.render_record_html` (record) /
  `render_daily_report_html.py` (daily report); shared `render(src,out,title,
  topbar)`, `gh_slugify` anchors, asserts `broken: 0`. Never hand-edit the
  `.html`. `daily_report.md` is newest-LAST (opposite of intuition) and is Evan's
  hand-written journal — automation writes `var/ops_status.log`, not it.

## .bat gotchas (detail in gotchas.md)
- Keep ALL .bat edits pure ASCII — one non-ASCII byte (em-dash in a REM) or a
  stray builtin-shadowing root file silently corrupts the whole cmd.exe parse.

## Commit discipline
- Commit only when a task/Evan authorizes; NEVER push without Evan. End messages
  with the `Co-Authored-By: Claude …` trailer.
