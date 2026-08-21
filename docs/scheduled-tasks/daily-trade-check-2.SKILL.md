---
name: daily-trade-check-2
description: Review the previous day/week/months trade data and research what happened the previous day when pertaining to the stocks bought. The goal is to gain insight into how the real world affects the stocks and come up with strategies to either improve the current sleeves or gain insight into new sleeves biased on new data that could have an edge in the market
---

Working directory: `D:\ClaudeCode\Trading`. `cd` there first — every path below is relative to it.

PRE-FLIGHT — do all of these BEFORE any research. Each one can abort the run.

0a. Run `date`. Use its LOCAL date and weekday for the report header and for every timestamp in the entry — never a UTC-derived date. This task fires at 19:00 local, which is already the NEXT UTC day while CDT is in force, so a UTC date files the session under tomorrow and the next morning's run reads it as the prior session. Label the zone by the reported UTC offset (UTC-5 -> CDT, UTC-6 -> CST); never hardcode either.

0b. If the US equity market was CLOSED today (holiday, or a halt with no settle), append a two-line entry under the normal header saying so and STOP — skip sections 1-7. The cron is Mon-Fri with no holiday calendar, so this check is the only thing between a market holiday and a report that republishes yesterday's numbers under today's date.

0c. Grep `daily_report.md` for `## Report: <today> (<Weekday>) — Post-Market Close Analysis`. If it is already present, STOP and report that this run is a duplicate re-fire. Never append a second entry for the same date — the week/period summaries double-count it.

0d. Read this task's live cron and `nextRunAt` from the scheduled-tasks list and echo them, plus the `date` output, into section 0 of the report. This task's cron has drifted three times on this machine (records CQ.3, DG); printing it into the artifact is what turns a silent drift into a visible one. At `0 17` it would read `paper_nav` 15 minutes BEFORE the 5:15pm MTM writes it, and every NAV in the report would be the prior session's with no symptom.

0e. Open the DB READ-ONLY, always: `sqlite3.connect('file:var/trades.db?mode=ro', uri=True)`. A default connect is read-write AND creates the file if the relative path is wrong; `var/` is gitignored, so a phantom empty DB would not appear in `git status`.

0f. If today is the 1st trading day of the month, `monthy-llm-rebalance` (fires ~18:03, observed runs 15-35 min) may still hold the DB for write. Confirm this month's rebalance has finished before querying. If you hit `database is locked`, STOP and report it — never append a partial entry.

0g. Check `max(nav_date)` in `paper_nav`. If it is EARLIER than today, today is UNMARKED (the 5:15pm MTM refuses to mark when price coverage is below its floor). Say so explicitly in section 0, label every NAV and day-move INDICATIVE, and state the method used to derive it. NEVER present a carried-forward NAV as today's marked close. This is not hypothetical — four consecutive sessions were unmarked as of 2026-08-20.

---

Read `daily_report.md` — it is newest-LAST, so read the TAIL, not the head; a plain read with no offset returns months-old entries. Summaries only for the last week, full sections if clarification is needed. Then query `var/trades.db` (read-only, per 0e) for today's final NAV, all position changes, and key movers; research what happened today for every stock held across all sleeves — earnings, news, analyst actions, sector moves, macro data — and review the past day/week/month of trade data to understand how real-world events are shaping portfolio performance.

Apply the /research-brief METHODOLOGY inline — sourcing discipline, citations re-fetched rather than recalled, negatives cross-checked — but do NOT save a separate brief to `docs/`. This task's only prose output is the `daily_report.md` entry; a `docs/research/` file would be a write this task is not permitted to make.

Produce a highly in-depth post-close report (this is the second report of the day, after markets close) covering: (0) data integrity and operational status — MTM/coverage state per 0g, the cron echo per 0d, any held ticker missing a close for today, and any price anomaly; (1) market summary with index closes and sector performance; (2) full NAV table for all sleeves from paper_nav DB; (3) key position analysis including movers, anything approaching a stop or target, and new developments; (4) LLM overlay treatment vs. control update; (5) week/period summary if applicable; (6) ladder gradient and the structural read — the residual-weight rungs and the clean-start cohort against its benchmarks; (7) strategic insights on whether current sleeves have structural edge or whether new long-term-viable sleeve concepts are supported by today's data — no recommendation is fine.

Include dates and source URLs throughout. Append the report to `daily_report.md` under the header `## Report: YYYY-MM-DD (Weekday) — Post-Market Close Analysis` with a > **DAILY SUMMARY** block immediately after the header covering NAV since inception for all sleeves ranked best-to-worst, day moves, key movers with reason, macro event, LLM overlay standings, and critical outstanding items.

DO NOT ASSUME OR MAKE UP ANY DETAILS, EVEN THE SMALLEST ONES. This includes PRECISION: never print a figure to more significant digits than the source it came from — re-query at the precision you intend to publish rather than re-typing a rounded console value with digits added.

Research methodology: run web searches in this order — (1) "[ticker] news [date]" for each held position, (2) "S&P 500 Nasdaq [date] market recap" for overall market context, (3) any macro events relevant to the portfolio: Fed speakers, CPI/PCE/jobs prints, oil/geopolitics if energy names are held, semiconductor supply chain news if semi names are held; (4) sector-level searches for sectors with >20% portfolio weight; prioritize: earnings beats/misses, guidance changes, analyst upgrades/downgrades, CEO/CFO commentary, M&A, regulatory actions, insider buying/selling, short interest changes, and any macro regime shifts (rate expectations, geopolitical escalation, commodity moves) — these are the events that historically move the portfolio names most; skip generic market color with no ticker-specific relevance; cite source URL and date for every claim. Where sources disagree on a figure, publish the reconciled one and flag the outlier; never average them silently.

After finishing, run `.venv\Scripts\python.exe -m scripts.render_daily_report_html` to refresh the HTML daily report file.

Then run /landing-check with a sonnet 5 agent — BEFORE staging anything. Its contract is a PRE-commit sweep and its verdict gates the commit: fix whatever it finds, then commit once. (This step ran AFTER the commit until 2026-08-20, which let fabricated detail into three of the five preceding entries — `c118a3e`, `12f8bb6`, `2d17058` — each needing a second corrections commit.)

Only once landing-check is clean, self-commit ONLY the two report files so the working tree stays clean: from `D:\ClaudeCode\Trading` run `git add daily_report.md daily_report.html` (EXACTLY those two paths — NEVER `git add -A` or `git add .`, so unrelated in-progress work is never swept in) then `git commit -m "Daily report: <YYYY-MM-DD> post-market close analysis entry"`. Do NOT push — publishing is Evan's call. A bare `git push` publishes the WHOLE branch, not just these two report files, so unreviewed in-progress work commits ride along (audit 2026-08-19 E5; realized 2026-08-19 07:08 CDT, when two landing-check commits were published this way). Leave every commit local; never push, force-push, pull, rebase, or auto-merge.

If something is found only after a commit has already landed, fix it and make a second commit `Daily report: <YYYY-MM-DD> corrections - <what and why>` — same two paths, still no push.

If git reports nothing to commit, that means the report was never appended: a total failure wearing the happy path's clothes. Append one line to `var/ops_status.log` — `[OPS <YYYY-MM-DD>] daily-trade-check-2 NO-OP: nothing to commit` — so the next run and the daily audit can see it, then report it and finish.

CONSTRAINTS — READ/RESEARCH ONLY. Never rebalance, MTM, or modify any sleeve, NAV, or price row. Never run `paper_rebalance`, `*_ops rebalance`/`decide`, or `alpaca_sync --execute`. The ONLY writes permitted are: (a) appending this report to `daily_report.md`, (b) rendering `daily_report.html`, (c) committing exactly those two paths, (d) a corrections commit of the same two paths, (e) one line appended to `var/ops_status.log` on a no-op.
