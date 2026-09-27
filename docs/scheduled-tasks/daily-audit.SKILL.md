---
name: daily-audit
description: daily audit
---

AUDIT SWEEP — read-only, one write exception (below).

Run `date` FIRST; compute the 7-day cutoff from its real output. Never invent timestamps.

Scope: top-level dirs under D:\ClaudeCode containing HANDOFF.md or a docs/ record.
Exclude *.ARCHIVED-* dirs.

STEP 0 — Trading-only fixed checks. Run these before classification; they are cheap and
they catch silent absences that no severity-ranked sweep will surface.

a. MISSING SESSION. For the previous weekday, `grep` D:\ClaudeCode\Trading\daily_report.md
   for BOTH `grep -cE '^## Report: <that date> \(<Weekday>\) .{1,3} Pre-Market Overnight Research'`
   AND the same with `Post-Market Close Analysis`. The separator is an em dash (U+2014)
   before 2026-09-25 and an ASCII hyphen from then on (ASCII rule of 2026-09-23), so a
   pattern that accepts only one of them reports every newer session as missing. Use
   exactly this form (tested 2026-09-26 against both header styles): the parens MUST be
   escaped under -E, and the separator is `.{1,3}` - NOT a bracket holding an em dash
   and a hyphen. This machine's Git Bash runs in the C locale, where a bracket cannot
   hold the 3-byte em dash and silently misses every em-dash header; `.{1,3}` matches
   the em dash as 1 character (UTF-8) or 3 bytes (C) and the hyphen as 1, and is ASCII
   (the ASCII-only .md hook refuses writing the em dash itself into this file).
   Report any weekday in the last 7 that is missing
   either one. A scheduled report that never fires produces no error and no artifact —
   the absence IS the failure, and nothing else detects it. (Observed: 2026-08-17 has a
   pre-market entry and no post-market one.)
b. DUPLICATE SESSION. Same grep, but flag any date whose header appears more than once —
   a re-fire double-counts in the week/period summaries.
c. SPEC DRIFT. `diff` each live scheduled-task SKILL.md under
   C:\Users\evan.EVANFREDY\.claude\scheduled-tasks\ against its committed snapshot in
   D:\ClaudeCode\Trading\docs\scheduled-tasks\<taskId>.SKILL.md. The live files are NOT
   under version control, so an edit to a spec that authorizes repo writes or trades is
   otherwise undetectable. Report any diff; report a missing snapshot as a finding.
d. CRON DRIFT. Read the live cron for every enabled task from the scheduled-tasks list
   (never from a doc) and compare against HANDOFF.md's task table. This machine has
   three documented drifts (records CQ.3, DG, and the monthly-rebalance day-gate).
e. TRADE/PUSH GUARD LIVE. Two layers, both must be present. `.claude/` is gitignored
   (.gitignore:13) so NEITHER settings file is version-controlled — nothing else would
   ever notice them being edited away. Assert presence; do not print the files.
   - Layer 1, settings deny (prefix rules, these work): BOTH
     D:\ClaudeCode\Trading\.claude\settings.json AND
     C:\Users\evan.EVANFREDY\.claude\settings.json must carry
     `Bash(git push:*)`, `Bash(git add -A:*)`, `Bash(git add .:*)`,
     `Bash(git reset --hard:*)`, `Bash(git rebase:*)`.
   - Layer 2, the PreToolUse hook (this is what actually blocks a rebalance): both
     files must register
     `scripts\hooks\pretooluse-trading-guard.js` on matcher `Bash|PowerShell`.
     Then RUN its self-check: `node scripts\hooks\test_trading_guard.js` — it must
     print 0 failed. Do NOT assert deny-rule strings for paper_rebalance / _ops
     rebalance / _ops decide / alpaca_sync --execute: those were tried as settings
     globs on 2026-08-20 and CANNOT work (Bash rules are prefix matchers; the token
     sits mid-command). Record DK. Asserting a string that cannot fire is a green
     light on a dead gate.

STEP 1 — Classify every project; print the table (project | verdict | evidence date)
before doing anything else. No silent drops. To classify, read ONLY: the dates/titles
of the last few entries in docs/Project Record — Full Chronological History.md (not
bodies), docs/audit_*.md filenames, and `git log --oneline --since=<cutoff>` if a repo.
- SKIP-AUDITED: an audit (record entry or audit_*.md) dated within the last 7 days
  AND fewer than 10 non-audit commits landed after that audit's own commit. Count with
  `git log --format=%s <audit-commit>..HEAD | grep -ivcE 'audit|landing.?check'`; if the
  project is not a repo, count non-audit record entries after the audit entry instead.
- ACTIVE: any non-audit record entry or commit within the last 7 days, OR a recent audit
  with >= 10 non-audit commits after it (churn override — elapsed time is not the only
  staleness signal; volume of unaudited change is). Print the count in the evidence column.
- INACTIVE: neither. Skip.

STEP 2 — Per ACTIVE project, in sequence:
a. Read that project's CLAUDE.md first (Trading/ServeLocal rules live there).
b. /audit — full cold audit.
c. /landing-check — scoped to the most recent record entry's claims vs disk
   (the audit changed nothing, so there is no new diff to sweep).

STEP 3 — Report, grouped by project. Within each project rank findings by severity.
Every finding: file:line, one-line issue, one-line surgical fix (shortest rung that
holds). No severity floor — small issues included, one line each. Cross-project
summary table at the end. Missing data is reported as missing, never guessed.

CONSTRAINTS — READ-ONLY: no code edits, no fixes applied, no commits, no HANDOFF
edits. ONE exception: after each project's audit, append one dated record entry
("Audit run — N findings, top: <item>") so future sweeps can detect it ran.

HOW TO APPEND THAT ENTRY — NEVER BY HAND. Write the body to a scratch .md file,
then run the script:

  node ~/.claude/skills/project-memory/append-record-entry.js \
    --record "<project>/docs/Project Record — Full Chronological History.md" \
    --title "Scheduled daily-audit: <summary>" \
    --body <scratch.md> \
    --date "<from a real `date` call — never guessed>"

An entry is a `# Appendix <X>` heading AND a matching front-matter TOC line, and
the two must be written TOGETHER. You will have READ the record in STEP 1, so
you will have seen the heading shape — do not imitate it with Edit/Write. Writing
the heading alone breaks the TOC/heading balance and BLOCKS EVERY LATER APPEND
by anyone until a human repairs it; picking the letter yourself races other
sessions and duplicates it. Both happened on 2026-09-01, from this task and from
an interactive session. The script takes a lock, derives the next free letter
from a live scan, and writes both lines atomically. A PreToolUse guard now denies
direct Edit/Write to a record file, so hand-splicing will fail anyway.

ASCII ONLY (rule added 2026-09-23). The appender refuses a title, date or body
containing any non-ASCII character: exit 2, a message starting "REFUSED:
non-ASCII character U+XXXX in the <title|date|body> (line N)", and nothing
written. The Write/Edit tools also deny adding non-ASCII to any .md file,
including your scratch body. So write the title and body ASCII from the start:
"-" for any dash, "->" for an arrow, straight quotes, "..." for an ellipsis,
"x" for a times sign, and plain letters for accented ones.

If the append is refused anyway, RETRY ONCE: replace every non-ASCII character
in the scratch body and the title, confirm with
  grep -nP '[^\x00-\x7F]' <scratch.md>
(it must print nothing), then re-run the same command. If the retry is also
refused, do NOT hand-write the entry. Finish the audit and make the FIRST line
of the cross-project summary "ENTRY NOT APPENDED: <project> - <the refusal
message>", so the miss is visible instead of silent.

For each audit, make a prompt that include the issue and fix with a high degree of precision. 1 per project that was audited