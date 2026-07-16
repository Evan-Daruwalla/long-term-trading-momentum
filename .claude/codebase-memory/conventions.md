# conventions — how to write code & docs here

- **price_cache** (split-adjusted, dividend-UNADJUSTED, `auto_adjust=False`) → canonical in **data.md**; also an always-load INDEX invariant.
- Module invocation (`.venv\Scripts\python.exe -m …` from the repo root) → **tooling.md**.
- Frozen-test contract (d=±0.0000pp after ANY Python change, paste REAL output) → **testing.md**; also an INDEX invariant.
- **NEVER fabricate data/fills/prices/results.** Missing data is reported as missing. Standing order, zero exceptions. (CLAUDE.md)
- **Docs**: append-only record (`docs/Project Record — Full Chronological History.md`), new `# Appendix <XX>` per entry + matching front-matter TOC line, prior entries never edited. Absolute dates always. (CLAUDE.md, project-memory skill)
- **State-doc tier RETIRED 2026-07-08** — never create `docs/state_<date>.md`; `HANDOFF.md` is the only live snapshot; the 5 old state docs are archived verbatim in record Appendix AZ. (record AZ, HANDOFF)
- HTML twins (script-generated only; regen commands; `daily_report.md` newest-LAST) → **tooling.md**.
- Commit only when a task/Evan authorizes; never push without Evan's instruction. End commit messages with the `Co-Authored-By: Claude ...` trailer. (CLAUDE.md, PRD)
- `.gitignore` ignores `.claude/*` (line 13) but RE-INCLUDES `.claude/codebase-memory/` (line 15) — so this bin dir IS tracked/committed. (Corrected 2026-07-15; supersedes the earlier "local, not committed" note, which was wrong — verified via `git ls-files`.)
