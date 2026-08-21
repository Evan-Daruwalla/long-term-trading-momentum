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
   for BOTH `## Report: <that date> (<Weekday>) — Pre-Market Overnight Research` AND
   `... — Post-Market Close Analysis`. Report any weekday in the last 7 that is missing
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

Make audit fix prompts that include the issue and fix with a high degree of precision. 1 per project that was audited