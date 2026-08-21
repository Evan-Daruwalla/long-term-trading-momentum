#!/usr/bin/env node
/*
 * Self-check for pretooluse-trading-guard.js. Assert-based, no framework.
 * Run: node scripts/hooks/test_trading_guard.js
 *
 * The DENY cases are the exact command shapes the settings.json glob rules
 * `Bash(:*paper_rebalance:*)` etc. failed to match (record DK).
 */
"use strict";
const { execFileSync } = require("child_process");
const path = require("path");
const assert = require("assert");

const HOOK = path.join(__dirname, "pretooluse-trading-guard.js");

function run(payload) {
  const out = execFileSync(process.execPath, [HOOK], {
    input: typeof payload === "string" ? payload : JSON.stringify(payload),
    encoding: "utf8",
  });
  if (!out.trim()) return { decision: "allow", raw: "" };
  const j = JSON.parse(out);
  const d = j.hookSpecificOutput && j.hookSpecificOutput.permissionDecision;
  return { decision: d || "allow", raw: out };
}

function bash(command) { return { tool_name: "Bash", tool_input: { command } }; }

const DENY = [
  // the real invocation shape: the token sits in the MIDDLE, which is exactly
  // what a prefix-matching glob cannot catch
  ".venv\\Scripts\\python.exe -m scripts.momentum.paper_rebalance",
  "cd /d/ClaudeCode/Trading && .venv/Scripts/python.exe -m scripts.momentum.paper_rebalance --all",
  ".venv\\Scripts\\python.exe -m scripts.momentum.sector_overlay_ops rebalance",
  ".venv\\Scripts\\python.exe -m scripts.momentum.llm_overlay_ops decide",
  ".venv\\Scripts\\python.exe -m scripts.momentum.alpaca_sync --execute",
  "git push",
  "git push origin master",
  "cd /d/ClaudeCode/Trading && git push",   // prefix rule misses this; hook must not
  "GIT_DIR=. git   push --force",
];

const ALLOW = [
  "git status",
  "git add daily_report.md daily_report.html",
  'git commit -m "Daily report: 2026-08-20 post-market close analysis entry"',
  "git log --oneline -5",
  ".venv\\Scripts\\python.exe -m scripts.render_daily_report_html",
  ".venv\\Scripts\\python.exe -m trading_bot.strategies.test_strategies",
  ".venv\\Scripts\\python.exe -m scripts.momentum.alpaca_sync --dry-run",
  "grep -n paper_rebalance CLAUDE.md",   // NOTE: reading ABOUT it is also denied; see below
];

let pass = 0, fail = 0;
for (const c of DENY) {
  const r = run(bash(c));
  if (r.decision === "deny") { pass++; }
  else { fail++; console.log("FAIL (should DENY):", c); }
}
for (const c of ALLOW) {
  const r = run(bash(c));
  // the grep case is a known, accepted false positive - asserted explicitly below
  if (c.startsWith("grep")) continue;
  if (r.decision === "allow") { pass++; }
  else { fail++; console.log("FAIL (should ALLOW):", c, r.raw); }
}

// Known and accepted: substring matching also blocks merely MENTIONING the
// token (grep/cat). That is the deliberate trade - a false positive costs one
// rephrase, a false negative costs a real trade. Asserted so it stays a
// decision on the record rather than a surprise.
assert.strictEqual(run(bash("grep -n paper_rebalance CLAUDE.md")).decision, "deny",
  "expected the known false-positive-on-mention behaviour");
pass++;

// Empty / missing command must not deny.
assert.strictEqual(run({ tool_name: "Bash", tool_input: {} }).decision, "allow");
pass++;

// Unparseable payload: allows normally, but still denies on a dangerous token.
assert.strictEqual(run("this is not json").decision, "allow");
pass++;
assert.strictEqual(run("not json but mentions alpaca_sync --execute").decision, "deny",
  "unparsed payload carrying a dangerous token must still deny (fail-closed on the token)");
pass++;

console.log(`\ntrading-guard self-check: ${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);
