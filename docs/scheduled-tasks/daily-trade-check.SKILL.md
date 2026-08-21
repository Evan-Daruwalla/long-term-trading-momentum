---
name: daily-trade-check
description: Review the previous day/week/months trade data and research 2 what happened the previous day when pertaining to the stocks bought.
---

Working directory: `D:\ClaudeCode\Trading`. `cd` there first — every path below is relative to it.

PRE-FLIGHT — do all of these BEFORE any research. Each one can abort the run.

0a. Run `date`. Use its LOCAL date and weekday for the report header and for every timestamp in the entry — never a UTC-derived date. Label the zone by the reported UTC offset (UTC-5 -> CDT, UTC-6 -> CST); never hardcode either.

0b. If the US equity market is CLOSED today (holiday), append a two-line entry under the normal header saying so and STOP — skip sections 1-6. The cron is Mon-Fri with no holiday calendar, so this check is the only thing between a market holiday and a report that republishes stale numbers under today's date.

0c. Grep `daily_report.md` for `## Report: <today> (<Weekday>) — Pre-Market Overnight Research`. If it is already present, STOP and report that this run is a duplicate re-fire. Never append a second entry for the same date.

0d. Read this task's live cron and `nextRunAt` from the scheduled-tasks list and echo them, plus the `date` output, into section 0 of the report. Cron drift is a documented recurring failure on this machine (records CQ.3, DG); printing it into the artifact is what turns a silent drift into a visible one.

0e. Open the DB READ-ONLY, always: `sqlite3.connect('file:var/trades.db?mode=ro', uri=True)`. A default connect is read-write AND creates the file if the relative path is wrong; `var/` is gitignored, so a phantom empty DB would not appear in `git status`.

0f. This task fires at 07:07, BEFORE the 07:45 `TradingMorningMTM` heal. If the previous session is still unmarked, say so and state that the morning heal has not yet run at compile time — report the schedule, never predict the outcome.

0g. Check `max(nav_date)` in `paper_nav` and state which date it is. If the most recent trading session is UNMARKED (the 5:15pm MTM refuses to mark when price coverage is below its floor), say so explicitly in section 0, label every derived NAV and move INDICATIVE, and state the method used. NEVER present a carried-forward NAV as a marked close.

---

Read `daily_report.md` — it is newest-LAST, so read the TAIL, not the head; a plain read with no offset returns months-old entries. Summaries only for the last week, full sections if clarification is needed. Then query `var/trades.db` (read-only, per 0e) for current positions and latest NAV; research overnight news, pre-market moves, earnings, macro data, and any analyst actions for stocks currently held or likely to enter at rebalance; review the past day/week/month of trade data to identify how real-world events are affecting the portfolio.

Apply the /research-brief METHODOLOGY inline — sourcing discipline, citations re-fetched rather than recalled, negatives cross-checked — but do NOT save a separate brief to `docs/`. This task's only prose output is the `daily_report.md` entry; a `docs/research/` file would be a write this task is not permitted to make.

Produce a highly in-depth pre-market report (market has not opened — no intraday performance data exists) covering: (0) data integrity and operational status — MTM/coverage state per 0f/0g, the cron echo per 0d, any held ticker missing a recent close, and any price anomaly; (1) portfolio standings from last close; (2) overnight/pre-market moves with % changes; (3) catalyst and macro review; (4) LLM overlay status; (5) risk flags and upcoming events; (6) strategic insights on whether current sleeves have structural edge or whether new long-term-viable sleeve concepts are supported by today's data — no recommendation is fine.

Include dates and source URLs throughout. Append the report to `daily_report.md` under the header `## Report: YYYY-MM-DD (Weekday) — Pre-Market Overnight Research` with a > **DAILY SUMMARY** block immediately after the header covering NAV standings, key pre-market moves, macro catalyst, LLM overlay status, and critical outstanding items.

DO NOT ASSUME OR MAKE UP ANY DETAILS, EVEN THE SMALLEST ONES. This includes PRECISION: never print a figure to more significant digits than the source it came from — re-query at the precision you intend to publish rather than re-typing a rounded console value with digits added.

Research methodology: run web searches in this order — (1) "[ticker] news [date]" for each held position, (2) "S&P 500 Nasdaq [date] market recap" for overall market context, (3) any macro events relevant to the portfolio: Fed speakers, CPI/PCE/jobs prints, oil/geopolitics if energy names are held, semiconductor supply chain news if semi names are held; (4) sector-level searches for sectors with >20% portfolio weight; prioritize: earnings beats/misses, guidance changes, analyst upgrades/downgrades, CEO/CFO commentary, M&A, regulatory actions, insider buying/selling, short interest changes, and any macro regime shifts (rate expectations, geopolitical escalation, commodity moves) — these are the events that historically move the portfolio names most; skip generic market color with no ticker-specific relevance; cite source URL and date for every claim. Where sources disagree on a figure, publish the reconciled one and flag the outlier; never average them silently.

After finishing, run `.venv\Scripts\python.exe -m scripts.render_daily_report_html` to refresh the HTML daily report file.

Then run /landing-check with a sonnet 5 agent — BEFORE staging anything. Its contract is a PRE-commit sweep and its verdict gates the commit: fix whatever it finds, then commit once. (This step ran AFTER the commit until 2026-08-20, which let fabricated detail into three of the five preceding entries — `c118a3e`, `12f8bb6`, `2d17058` — each needing a second corrections commit.)

Only once landing-check is clean, self-commit ONLY the two report files so the working tree stays clean: from `D:\ClaudeCode\Trading` run `git add daily_report.md daily_report.html` (EXACTLY those two paths — NEVER `git add -A` or `git add .`, so unrelated in-progress work is never swept in) then `git commit -m "Daily report: <YYYY-MM-DD> pre-market overnight research entry"`. Do NOT push — publishing is Evan's call. A bare `git push` publishes the WHOLE branch, not just these two report files, so unreviewed in-progress work commits ride along (audit 2026-08-19 E5; realized 2026-08-19 07:08 CDT, when two landing-check commits were published this way). Leave every commit local; never push, force-push, pull, rebase, or auto-merge.

If something is found only after a commit has already landed, fix it and make a second commit `Daily report: <YYYY-MM-DD> corrections - <what and why>` — same two paths, still no push.

If git reports nothing to commit, that means the report was never appended: a total failure wearing the happy path's clothes. Append one line to `var/ops_status.log` — `[OPS <YYYY-MM-DD>] daily-trade-check NO-OP: nothing to commit` — so the next run and the daily audit can see it, then report it and finish.

CONSTRAINTS — READ/RESEARCH ONLY. Never rebalance, MTM, or modify any sleeve, NAV, or price row. Never run `paper_rebalance`, `*_ops rebalance`/`decide`, or `alpaca_sync --execute`. The ONLY writes permitted are: (a) appending this report to `daily_report.md`, (b) rendering `daily_report.html`, (c) committing exactly those two paths, (d) a corrections commit of the same two paths, (e) one line appended to `var/ops_status.log` on a no-op.
