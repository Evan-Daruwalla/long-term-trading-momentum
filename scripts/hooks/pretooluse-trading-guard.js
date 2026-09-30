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
 * The `git add -A` prefix rule in settings.json DOES work and is kept as a
 * second layer; this hook covers `git push` because a prefix rule misses
 * `cd x && git push` and `git -C x push`.
 *
 * DESIGN (rewritten after record EE, 2026-09-29, which found 8 escapes):
 *  - Rules are INVOCATION-SHAPED, not bare words. A bare-word `rebalance` rule
 *    would deny reading rebalance_log.md, the daily-audit spec diff of
 *    monthy-llm-rebalance, and SQL like exit_reason='rebalance'. Each TRADING
 *    rule names a module, a .bat wrapper, an *_ops subcommand, or a flag.
 *  - SCOPING. This hook is registered user-wide, so the Trading-only rules must
 *    not fire in other projects. RULES split into GLOBAL (publishing, wrong in
 *    every repo) and TRADING. TRADING applies when payload.cwd or the command
 *    matches ClaudeCode[\\/]Trading, and ALSO when payload.cwd is missing
 *    (fail closed: an unknown location is treated as Trading).
 *  - THREE STRINGS per command are tested, and any hit denies: the raw command;
 *    `norm` (^ ' " removed, whitespace runs collapsed) which defeats
 *    paper_reb^alance / paper_reb''alance and multi-space splits; and `norm`
 *    with \ and ` also removed, which defeats paper_reb\alance and `git pu\sh`.
 *    Backslashes are kept in the first two so path-anchored rules still see
 *    `scripts\momentum\rebalance.bat`.
 *  - The --exec escape was an argparse abbreviation (alpaca_sync accepted
 *    --e/--ex/--exec for --execute); the source now sets allow_abbrev=False, and
 *    the regex still covers every prefix as the second layer.
 *
 * KNOWN LIMITS (not closed, by design): an env-var or variable-indirected module
 * name (`X=paper_; python -m ...${X}rebalance`) cannot be seen by a string
 * matcher; a clone of this repo outside a path matching ClaudeCode/Trading
 * scopes to the GLOBAL rules only unless its cwd is missing; the git rule
 * over-matches any command carrying both `git` and `push` (a commit message that
 * mentions push denies; rephrase); and hooks cover only Bash/PowerShell, not
 * the Read/Edit tools.
 *
 * Always exits 0 — the block is expressed via permissionDecision:"deny", never
 * via a crash. On an internal error it fails OPEN but NOISY, except that a
 * dangerous token found anywhere in the raw stdin still denies: a guard that
 * skips silently is a dead guard (record DI).
 */
"use strict";

// Each entry: [regex, human reason]. Matched case-insensitively against three
// forms of the command (see DESIGN above).
const GLOBAL_RULES = [
  [/\bgit\b[\s\S]*\bpush\b|\bpush\b[\s\S]*\bgit\b/i,
   "publishing is Evan's call. A bare `git push` publishes the WHOLE branch, so unreviewed in-progress commits ride along (record DI.3, realised 2026-08-19 07:08 CDT)."],
];

const TRADING_RULES = [
  [/\b(?:monthly_|ladder_forward_|paper_)rebalance\b/i,
   "paper_rebalance moves real sleeve positions. It belongs to the scheduled tasks and to Evan, never to an agent."],
  [/(?:^|[\s\\\/])(?:ladder_)?rebalance\.bat\b/i,
   "the rebalance .bat wrappers dispatch the live rebalance and the Alpaca sync."],
  [/\bmonthly_auto(?:\.bat)?\b/i,
   "monthly_auto is the unattended monthly rebalance chain."],
  [/_ops\b[\s\S]*?\brebalance(?:-stock|-sector)?\b/i,
   "an *_ops rebalance path moves real sleeve positions."],
  [/_ops\b[\s\S]*?\bdecide\b/i,
   "an *_ops decide path writes an LLM decision to the append-only decision log."],
  [/\boverlay_auto_decide\b/i,
   "overlay_auto_decide writes LLM decisions to the append-only decision log."],
  [/\bstamp_rebalance_log\b/i,
   "stamp_rebalance_log writes the monthly-run ledger, which gates the whole month."],
  [/\b(?:schtasks\b[\s\S]*\/run|Start-ScheduledTask)\b[\s\S]*TradingLadderRebalance/i,
   "starting the TradingLadderRebalance task runs the live ladder rebalance."],
  [/alpaca_sync\b[\s\S]*?\s--e(?:x(?:e(?:c(?:u(?:t(?:e)?)?)?)?)?)?(?=[\s=]|$)/i,
   "alpaca_sync --execute submits live orders to the Alpaca account (--e/--ex/--exec are argparse abbreviations of it)."],
  [/alpaca_sync\b[\s\S]*\bexecute\s*=\s*True/i,
   "alpaca_sync with execute=True submits live orders to the Alpaca account."],
];

// Trading-only rules apply inside this project, or whenever the location is unknown.
const TRADING_PATH = /ClaudeCode[\\/]Trading/i;

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

// raw, norm (^ ' " stripped, whitespace collapsed), norm with \ and ` stripped.
function forms(command) {
  const norm = command.replace(/[\^'"]/g, "").replace(/\s+/g, " ");
  return [command, norm, norm.replace(/[\\`]/g, "")];
}

function firstMatch(command, applyTrading) {
  const rules = applyTrading ? GLOBAL_RULES.concat(TRADING_RULES) : GLOBAL_RULES;
  const strings = forms(command);
  for (const [re, why] of rules) {
    for (const s of strings) {
      if (re.test(s)) return why;
    }
  }
  return null;
}

let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (c) => { raw += c; });
process.stdin.on("end", () => {
  let command;
  let applyTrading;
  try {
    const payload = JSON.parse(raw);
    command = (payload.tool_input && payload.tool_input.command) || "";
    const cwd = typeof payload.cwd === "string" ? payload.cwd : "";
    // Missing cwd -> fail closed (treated as Trading).
    applyTrading = cwd === "" || TRADING_PATH.test(cwd) || TRADING_PATH.test(command);
  } catch (e) {
    // Could not parse the envelope. Do not wedge the session over it — but do
    // not wave a rebalance through either: scan the raw text as a fallback,
    // with every rule (the cwd is unknown).
    const why = firstMatch(raw, true);
    if (why) {
      return deny("trading-guard (unparsed payload, matched raw text): " + why);
    }
    return allowWithWarning(
      "trading-guard: could not parse the PreToolUse payload; command NOT checked."
    );
  }

  if (!command) return allow();

  const why = firstMatch(command, applyTrading);
  if (why) {
    return deny(
      "trading-guard BLOCKED this command: " + why +
      "\nIf this is genuinely intended, Evan runs it himself."
    );
  }
  return allow();
});
