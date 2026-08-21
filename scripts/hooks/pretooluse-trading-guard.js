#!/usr/bin/env node
/*
 * trading-guard — PreToolUse hook (matcher: Bash|PowerShell).
 *
 * Denies the commands that move real state in this project: the rebalancers,
 * the LLM decide/rebalance ops paths, an Alpaca order submit, and `git push`.
 * CLAUDE.md and every scheduled-task spec forbid these in prose; this is the
 * mechanism that actually enforces it.
 *
 * WHY A HOOK AND NOT A settings.json DENY RULE (record DK, 2026-08-20):
 * Claude Code `Bash(...)` deny rules are PREFIX matchers — `Bash(prefix:*)`
 * matches "command starts with prefix", and the `:*` shorthand is only
 * recognised at the END of a pattern. The audit's first fix wrote
 * `Bash(:*paper_rebalance:*)`, where the leading `:` is a literal character, so
 * the rule required the command to begin with a colon and could never fire.
 * The real invocation is `.venv\Scripts\python.exe -m scripts.momentum.
 * paper_rebalance`, i.e. the token sits in the MIDDLE — which a prefix matcher
 * structurally cannot catch. A hook sees the whole command string.
 *
 * The `git push` / `git add -A` prefix rules in settings.json DO work and are
 * kept as a second layer; this hook re-covers `git push` because the prefix
 * rule misses `cd x && git push` and similar.
 *
 * Always exits 0 — the block is expressed via permissionDecision:"deny", never
 * via a crash. On an internal error it fails OPEN but NOISY, except that a
 * dangerous token found anywhere in the raw stdin still denies: a guard that
 * skips silently is a dead guard (record DI).
 */
"use strict";

// Each entry: [regex, human reason]. Matched against the whole command string,
// case-insensitively. Keep these anchored to the operation, not to a filename,
// so a renamed wrapper does not silently escape the guard.
const RULES = [
  [/paper_rebalance/i,
   "paper_rebalance moves real sleeve positions. It belongs to the scheduled tasks and to Evan, never to an agent."],
  [/_ops\s+rebalance/i,
   "an *_ops rebalance path moves real sleeve positions."],
  [/_ops\s+decide/i,
   "an *_ops decide path writes an LLM decision to the append-only decision log."],
  [/alpaca_sync\b[^\n]*--execute/i,
   "alpaca_sync --execute submits live orders to the Alpaca account."],
  [/\bgit\s+push\b/i,
   "publishing is Evan's call. A bare `git push` publishes the WHOLE branch, so unreviewed in-progress commits ride along (record DI.3, realised 2026-08-19 07:08 CDT)."],
];

function allow() { process.exit(0); }

function allowWithWarning(msg) {
  process.stdout.write(JSON.stringify({ systemMessage: msg }) + "\n");
  process.exit(0);
}

function deny(reason) {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: reason,
    },
  }) + "\n");
  process.exit(0);
}

function firstMatch(command) {
  for (const [re, why] of RULES) {
    if (re.test(command)) return why;
  }
  return null;
}

let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (c) => { raw += c; });
process.stdin.on("end", () => {
  let command;
  try {
    const payload = JSON.parse(raw);
    command = (payload.tool_input && payload.tool_input.command) || "";
  } catch (e) {
    // Could not parse the envelope. Do not wedge the session over it — but do
    // not wave a rebalance through either: scan the raw text as a fallback.
    const why = firstMatch(raw);
    if (why) {
      return deny("trading-guard (unparsed payload, matched raw text): " + why);
    }
    return allowWithWarning(
      "trading-guard: could not parse the PreToolUse payload; command NOT checked."
    );
  }

  if (!command) return allow();

  const why = firstMatch(command);
  if (why) {
    return deny(
      "trading-guard BLOCKED this command: " + why +
      "\nIf this is genuinely intended, Evan runs it himself."
    );
  }
  return allow();
});
