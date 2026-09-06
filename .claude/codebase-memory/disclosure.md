# disclosure — what may leave this project

**Status: stub, no outward-facing artifact published yet (2026-09-06).** Created
per the project-memory standards set so the constraint has one obvious home
before it is needed, not after.

Standing constraints that already apply if anything is published:

- **Evan is 17.** No brokerage account in his name; the Alpaca account is PAPER
  only. Any case study, portfolio entry, or public README must not imply live
  trading or real capital at risk.
- **`alpaca_keys.env` is secret** — never printed, logged, committed, screenshotted,
  or included in a demo. A dashboard screenshot must not show account identifiers.
- **Numbers must trace to the record.** Every metric in an outward-facing artifact
  cites a dated record entry or a commit; anything that cannot be traced is cut,
  not rounded or estimated. (memory `no-reprecision-from-rounded-output`: a figure
  with more significant figures than the tool output it came from is fabricated.)
- **The public remote is real.** `git push` publishes the WHOLE branch — see
  `security.md`; unreviewed in-progress commits ride along.
- The honest framing is the process, not returns: the deliverable is the track
  record and the engineering rigor. Sleeve P&L over a few months is noise and
  must not be presented as evidence of edge.
