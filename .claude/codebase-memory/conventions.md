# conventions — how to write code & docs here

- **price_cache convention**: closes are SPLIT-ADJUSTED, DIVIDEND-UNADJUSTED (yfinance `auto_adjust=False`). Every cache writer MUST honor it; never add one that doesn't. (CLAUDE.md — this is the #1 data invariant)
- Invoke modules as `.venv\Scripts\python.exe -m scripts.momentum.<module>` (or `-m trading_bot...`) from the repo root — matches all existing usage. (CLAUDE.md)
- After ANY Python change, run the frozen tests and paste the REAL output; must be d=±0.0000pp. Never say "should pass". (CLAUDE.md definition of done)
- **NEVER fabricate data/fills/prices/results.** Missing data is reported as missing. Standing order, zero exceptions. (CLAUDE.md)
- **Docs**: append-only record (`docs/Project Record — Full Chronological History.md`), new `# Appendix <XX>` per entry + matching front-matter TOC line, prior entries never edited. Absolute dates always. (CLAUDE.md, project-memory skill)
- **State-doc tier RETIRED 2026-07-08** — never create `docs/state_<date>.md`; `HANDOFF.md` is the only live snapshot; the 5 old state docs are archived verbatim in record Appendix AZ. (record AZ, HANDOFF)
- HTML twins are SCRIPT-GENERATED only — regen via `python -m scripts.render_record_html` / `render_daily_report_html`; never hand-edit the `.html`. `daily_report.md` is newest-LAST (opposite of intuition). (CLAUDE.md)
- Commit only when a task/Evan authorizes; never push without Evan's instruction. End commit messages with the `Co-Authored-By: Claude ...` trailer. (CLAUDE.md, PRD)
- `.claude/` is gitignored here, so this codebase-memory dir is LOCAL (not committed). (`.gitignore:13`)
