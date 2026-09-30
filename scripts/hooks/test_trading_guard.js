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

// ---- record EE hardening (2026-09-29): the eight escapes + cwd scoping ------
// Dangerous tokens are built by concatenation so this file never carries a
// literal the guard would itself match when the file is grepped or cat-ed.
const RB = "re" + "balance";
const RBC = "Re" + "balance";
const DEC = "de" + "cide";
const PSH = "pu" + "sh";
const EXE = "--ex" + "ecute";
const TRADING_CWD = "D:\\ClaudeCode\\Trading";
const CITOYA_CWD = "D:\\ClaudeCode\\Citoya";

function bashIn(command, cwd) {
  return { tool_name: "Bash", cwd, tool_input: { command } };
}

// Each entry is denied when the payload carries the Trading cwd.
const DENY_TRADING = [
  // the two module dispatchers the old rule list missed
  `.venv\\Scripts\\python.exe -m scripts.momentum.monthly_${RB}`,
  `.venv\\Scripts\\python.exe -m scripts.momentum.ladder_forward_${RB}`,
  // the .bat wrappers and the unattended monthly chain
  `scripts\\momentum\\${RB}.bat`,
  `cmd /c scripts\\momentum\\ladder_${RB}.bat`,
  `cmd /c scripts\\momentum\\monthly_auto.bat`,
  // the auto-decide path and the ops decide / rebalance subcommands
  `.venv\\Scripts\\python.exe -m scripts.momentum.overlay_auto_${DEC}`,
  `.venv\\Scripts\\python.exe scripts\\momentum\\llm_overlay_ops.py ${DEC} --ticker X`,
  `.venv\\Scripts\\python.exe -m scripts.momentum.llm_cascade_ops ${RB}-stock`,
  `.venv\\Scripts\\python.exe -m scripts.momentum.sector_overlay_ops ${RB}-sector`,
  // the ledger stamp and the scheduled-task launchers
  `.venv\\Scripts\\python.exe -m scripts.momentum.stamp_${RB}_log --status OK`,
  `schtasks /run /tn TradingLadder${RBC}`,
  `Start-ScheduledTask -TaskName TradingLadder${RBC}`,
  // alpaca_sync: argparse allowed --exec / --ex / --e as abbreviations of the flag
  `.venv\\Scripts\\python.exe -m trading_bot.execution.alpaca_sync --all ${EXE}`,
  `.venv\\Scripts\\python.exe -m trading_bot.execution.alpaca_sync --all --exec`,
  `.venv\\Scripts\\python.exe -m trading_bot.execution.alpaca_sync --all --ex`,
  `.venv\\Scripts\\python.exe -m trading_bot.execution.alpaca_sync --all --e`,
  `.venv\\Scripts\\python.exe -c "from trading_bot.execution import alpaca_sync as a; a.sync_account(x, execute = True)"`,
  // push with a flag between git and push, and an indirected push
  `git -C D:/ClaudeCode/Trading ${PSH} origin master`,
  `set X=${PSH} & git %X%`,
  // shell-quoting splits inside a token (^ ' " \ are stripped before matching)
  `.venv\\Scripts\\python.exe -m scripts.momentum.paper_reb^alance`,
  `.venv\\Scripts\\python.exe -m scripts.momentum.paper_reb''alance`,
  `.venv\\Scripts\\python.exe -m scripts.momentum.paper_reb""alance`,
  `.venv\\Scripts\\python.exe -m scripts.momentum.paper_reb\\alance`,
  `git pu\\sh`,
];

const ALLOW_TRADING = [
  // reading ABOUT the ledger or the monthly spec is not running it
  `cat rebalance_log.md`,
  `grep "Last ${RB}" rebalance_log.md`,
  // the daily-audit STEP 0c spec diff (the filenames carry the word)
  `diff "C:\\Users\\evan.EVANFREDY\\Documents\\Claude\\Scheduled\\monthy-llm-${RB}\\SKILL.md" "docs\\scheduled-tasks\\monthy-llm-${RB}.SKILL.md"`,
  // read-only checks that share the vocabulary
  `.venv\\Scripts\\python.exe -m scripts.momentum.check_month_gate`,
  `.venv\\Scripts\\python.exe -m scripts.momentum.test_${RB}_cadence`,
  // SQL that names the exit reason
  `sqlite3 var/trades.db "select count(*) from paper_positions where exit_reason='${RB}'"`,
  `git commit -F msg.txt`,
  `.venv\\Scripts\\python.exe -m scripts.data_audit.remark_nav_day --date 2026-09-28`,
  `.venv\\Scripts\\python.exe -m trading_bot.execution.alpaca_sync --all`,
  `.venv\\Scripts\\python.exe -m trading_bot.execution.alpaca_sync --all --dry-run`,
];

for (const c of DENY_TRADING) {
  const r = run(bashIn(c, TRADING_CWD));
  if (r.decision === "deny") { pass++; }
  else { fail++; console.log("FAIL (Trading cwd, should DENY):", c); }
}
for (const c of ALLOW_TRADING) {
  const r = run(bashIn(c, TRADING_CWD));
  if (r.decision === "allow") { pass++; }
  else { fail++; console.log("FAIL (Trading cwd, should ALLOW):", c, r.raw); }
}

// Missing cwd fails CLOSED: a Trading-only rule still applies.
{
  const c = `cmd /c scripts\\momentum\\monthly_auto.bat`;
  const r = run({ tool_name: "Bash", tool_input: { command: c } });
  if (r.decision === "deny") { pass++; }
  else { fail++; console.log("FAIL (no cwd field, should DENY - fail closed):", c); }
}

// cwd scoping: outside Trading the Trading-only rules do not apply, but the
// user-wide git-publish rule still does (the hook is registered for every project).
{
  const outside = `.venv\\Scripts\\python.exe -m scripts.momentum.paper_${RB}`;
  let r = run(bashIn(outside, CITOYA_CWD));
  if (r.decision === "allow") { pass++; }
  else { fail++; console.log("FAIL (Citoya cwd, Trading-only rule should be scoped out):", outside, r.raw); }

  r = run(bashIn(`git ${PSH}`, CITOYA_CWD));
  if (r.decision === "deny") { pass++; }
  else { fail++; console.log("FAIL (Citoya cwd, git publish should still DENY):", `git ${PSH}`); }

  // a command that names the Trading path pulls the Trading rules back in
  const named = `cd D:/ClaudeCode/Trading && .venv/Scripts/python.exe -m scripts.momentum.paper_${RB}`;
  r = run(bashIn(named, CITOYA_CWD));
  if (r.decision === "deny") { pass++; }
  else { fail++; console.log("FAIL (Citoya cwd but command names the Trading path, should DENY):", named); }
}

// Unparseable payload: the same three-way matching applies to the raw text.
assert.strictEqual(run("not json but mentions cmd /c monthly_auto.bat").decision, "deny",
  "unparsed payload: a Trading-only token must deny (cwd unknown -> fail closed)");
pass++;
assert.strictEqual(run(`not json but mentions paper_reb^alance and git ${PSH}`).decision, "deny",
  "unparsed payload: a quoting-split token must deny");
pass++;

console.log(`\ntrading-guard self-check: ${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);
