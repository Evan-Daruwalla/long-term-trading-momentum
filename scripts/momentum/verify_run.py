"""Post-run verifier for the daily/monthly automation (read-only).

After an unattended MTM or rebalance, confirms each sleeve's state is internally
consistent so a silent failure can't quietly contaminate the record. Checks per
sleeve:
  (a) NAV continuity  — one paper_nav row for every trading day since inception,
      no gaps. (Dupes are impossible: paper_nav PK is (strategy, nav_date).)
      Rows on non-trading days (intentional holiday flat rows) are reported, not
      failed.
  (b1) ledger cash — for EVERY paper_nav row since LEDGER_EPOCH, the stored cash
      must equal the entry/exit ledger replayed to that date
      (historical_state.state_at). FAIL. This is the real invariant: it depends
      only on the ledger, so a bad row stays failed on every later run.
  (b2) price drift — reprices current positions with today's cache as of the
      latest nav row and compares to its stored total_nav. REPORTED, NEVER
      FAILED: historical NAV is not reproducible in principle because
      daily_price_refresh rewrites a rolling 30-day window with INSERT OR
      REPLACE by design (CK.4), so this measures cache revision, not error.
      It was the FAIL gate until 2026-08-13; as a gate it fired nightly on a
      failing set that turned over completely in 24h with nothing repaired
      (record DC).
  (c) position count vs target. Hardcoded targets from HANDOFF's 2026-07-09
      cohort spec; overlay/cascade sleeves are variable (veto->cash) so they are
      reported, not asserted. FAIL if count EXCEEDS target (MONTHLY only — an
      overshoot is only meaningful right after a rebalance) or if it falls below
      UNDERFILL_FRACTION of target (both modes — a wipeout is always a failure).
  (d) no pre-inception rows — no paper_nav row dated before inception.

Plus one run-level (not per-sleeve) check:
  (e) rebalance cadence — rebalance_log.md's "Last rebalance:" date must be in
      the same calendar month as the last SETTLED trading day or later, must not
      be in the future, and its "Status:" must not be PARTIAL. Checks
      (a)-(d) structurally CANNOT catch a missed monthly rebalance: a sleeve
      that never rebalanced has perfectly continuous NAV and cent-perfect cash
      recon, it just holds a stale book. That is how the 2026-08 rebalance
      nearly vanished (record CN — the cron had drifted to day-1-of-month and
      2026-08-01 was a Saturday). Reads the repo's rebalance_log.md, so it
      describes live ops state even under --db.

--mode daily runs (a),(b1),(b2),(c: underfill only),(d),(e); --mode monthly adds the
EXCEEDS half of (c) and a reminder line to eyeball the Alpaca submit/reject
counts in the run log. Read-only (file:...?mode=ro);
appends a dated PASS/FAIL block to var/verify_report.log; nonzero exit on any FAIL.

Usage:
  python -m scripts.momentum.verify_run --mode daily
  python -m scripts.momentum.verify_run --mode monthly
  python -m scripts.momentum.verify_run --mode daily --db path/to/copy.db
"""
from __future__ import annotations

import argparse
import logging
import re
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

from trading_bot.config import DB_PATH, PROJECT_ROOT
from scripts.momentum.check_coverage import coverage_status
from scripts.momentum import historical_state as hs

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("verify_run")

MIN_TRADING_DAY_COUNT = 1000
# (b1) ledger-replay epoch. Rows BEFORE this date legitimately disagree with the
# entry/exit replay: M7.3 (recommended CK.5, applied live CM 2026-08-02) repaired
# the 31 closed KLAC positions and the sleeves' CURRENT cash but deliberately left
# historical paper_nav rows alone, so the replay books repaired exit_values against
# pre-repair stored cash. Measured, not assumed: the last divergent nav_date is
# 2026-07-30 and every date from 2026-07-31 (the row CM re-marked) is clean, on all
# 76 sleeves. Checking them would emit 846 known, chosen failures every run.
LEDGER_EPOCH = "2026-07-31"
# Catastrophic-underfill floor: FAIL below this share of the position target.
# Deliberately far under the normal 43-50 of 50 range so a thin rebalance never
# trips it — this catches wipeouts (e.g. a mass liquidation), not selectivity.
UNDERFILL_FRACTION = 0.5

# Open-position targets from HANDOFF (2026-07-09 cohort spec). Overlay/cascade
# sleeves are intentionally variable (a macro/stock veto sends a slot to cash),
# so they are NOT listed here and get a report-only line.
POSITION_TARGETS = {
    "mom_v1_paper": 100, "mom_v1_0701_paper": 100,
    "mom_v2_paper": 50, "mom_v2_0701_paper": 50,
    "mom_roa_6535_paper": 50, "mom_roa_6535_0701_paper": 50,
    "residual_roa_6535_paper": 50, "residual_roa_6535_0701_paper": 50,
    "sector_top4_paper": 4, "sector_top4_full_paper": 4,
    "spy_benchmark_paper": 1, "spy_benchmark_0701_paper": 1,
    "qqq_benchmark_paper": 1, "qqq_benchmark_0706_paper": 1,
    "mom_roa_top1_paper": 1,
    # Residual weight ladder (record BW, seeded 2026-07-14): top-50 like the
    # champions; broker-realistic drops a few untradable names, so counts run
    # 44-50 — FAIL only on EXCEEDS, same as every other target.
    "residual_w5050_paper": 50, "residual_w5545_paper": 50,
    "residual_w6040_paper": 50, "residual_w6535_paper": 50,
    "residual_w7030_paper": 50, "residual_w7525_paper": 50,
    "residual_w8020_paper": 50, "residual_w8515_paper": 50,
    "residual_w9010_paper": 50, "residual_w9505_paper": 50,
}


REBALANCE_LOG = PROJECT_ROOT / "rebalance_log.md"
_LAST_REBALANCE_RE = re.compile(r"Last rebalance:\**\s*(\d{4}-\d{2}-\d{2})")
_STATUS_RE = re.compile(r"Status:\**\s*(OK|PARTIAL)")


def read_last_rebalance(path: Path = REBALANCE_LOG) -> tuple[str | None, str | None]:
    """(date, status) from rebalance_log.md; either element None if absent.

    status is None for a log written before --status existed (audit 2026-08-04,
    finding 1); that legacy shape is treated as OK by check_rebalance_cadence,
    since the next real run re-stamps it either way.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None, None
    d = _LAST_REBALANCE_RE.search(text)
    s = _STATUS_RE.search(text)
    return (d.group(1) if d else None), (s.group(1) if s else None)


def check_rebalance_cadence(logged: str | None, last_settled: str,
                            status: str | None = None,
                            today: str | None = None) -> list[str]:
    """(e) Has this month's rebalance run, and did it succeed? Pure logic.

    Anchoring on last_settled's MONTH is what makes this correct without a
    holiday calendar: last_settled falling in month M is itself proof that M's
    first trading day has passed, so a stamp still pointing at an earlier month
    means the rebalance was missed. Before that (e.g. 08-02, settled 07-31) a
    July stamp is right and this stays quiet. '>=' not '==' so the evening of
    the rebalance itself passes, when the stamp is already 08-03 but coverage
    has not settled past 07-31 yet.

    The future-date guard exists because the month comparison alone accepts any
    forward-dated stamp: a log reading 2099-01-01 would satisfy every month
    check forever, silently disabling this gate AND the rebalance task's own
    Step 0 retry gate (audit 2026-08-04, E4). The stamp is written with
    date.today(), so it can never legitimately exceed today.
    """
    today = today or date.today().isoformat()
    if logged is None:
        return [f"rebalance cadence: no parseable 'Last rebalance:' date in "
                f"{REBALANCE_LOG.name}"]
    if logged > today:
        return [f"rebalance cadence: stamp {logged} is in the FUTURE (today "
                f"{today}) - the stamp is written with date.today(), so this is "
                f"corrupt or was written under a wrong clock; the gate is void"]
    if logged[:7] < last_settled[:7]:
        return [f"rebalance cadence: last rebalance {logged} predates the settled "
                f"month {last_settled[:7]} - this month's monthly rebalance has "
                f"NOT run (check the monthy-llm-rebalance cron, record CN)"]
    if status == "PARTIAL":
        return [f"rebalance cadence: last rebalance {logged} stamped PARTIAL - at "
                f"least one step of that run returned non-zero; the run is NOT "
                f"trustworthy and no retry will fire (see the run log)"]
    return []


def _ro_connect(db_path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def trading_calendar(conn: sqlite3.Connection, start: str) -> list[str]:
    rows = conn.execute(
        "SELECT key_date, COUNT(*) AS c FROM price_cache "
        "WHERE kind='close' AND price IS NOT NULL AND key_date >= ? "
        "GROUP BY key_date ORDER BY key_date ASC",
        (start,),
    ).fetchall()
    return [r["key_date"] for r in rows if r["c"] >= MIN_TRADING_DAY_COUNT]


def inception(conn: sqlite3.Connection, strategy: str) -> date:
    """min(date(initialized_at), earliest entry_date) — matches paper_mtm."""
    prow = conn.execute("SELECT initialized_at FROM paper_portfolio WHERE strategy_name=?",
                        (strategy,)).fetchone()
    erow = conn.execute("SELECT MIN(entry_date) AS d FROM paper_positions WHERE strategy_name=?",
                        (strategy,)).fetchone()
    cands: list[date] = []
    for raw in (prow["initialized_at"] if prow else None, erow["d"] if erow else None):
        if raw:
            try:
                cands.append(date.fromisoformat(str(raw)[:10]))
            except ValueError:
                pass
    return min(cands) if cands else date.min


def _last_close(conn: sqlite3.Connection, ticker: str, d: str):
    r = conn.execute(
        "SELECT price FROM price_cache WHERE ticker=? AND kind='close' "
        "AND key_date<=? AND price IS NOT NULL ORDER BY key_date DESC LIMIT 1",
        (ticker, d)).fetchone()
    return r["price"] if r else None


def verify_sleeve(conn: sqlite3.Connection, strategy: str, calendar: list[str],
                  monthly: bool, last_settled: str) -> tuple[list[str], str]:
    """Return (fail_reasons, info_line)."""
    fails: list[str] = []
    inc = inception(conn, strategy)
    cal_set = set(calendar)

    navs = [r["nav_date"] for r in conn.execute(
        "SELECT nav_date FROM paper_nav WHERE strategy_name=? ORDER BY nav_date",
        (strategy,)).fetchall()]
    nav_set = set(navs)

    # (a) continuity — only up to the last SETTLED trading day. Days after it are
    # PENDING (data still publishing at the 17:15 run) and heal via mtm_catchup
    # (M3.5); flagging them as gaps would fail the daily task every evening.
    window = [d for d in calendar if inc.isoformat() <= d <= last_settled]
    missing = [d for d in window if d not in nav_set]
    holiday_rows = sum(1 for d in navs if d not in cal_set and d >= inc.isoformat())
    if missing:
        fails.append(f"continuity: {len(missing)} missing trading day(s) "
                     f"(e.g. {','.join(missing[:5])})")

    # (d) no pre-inception rows
    preinc = [d for d in navs if d < inc.isoformat()]
    if preinc:
        fails.append(f"pre-inception: {len(preinc)} nav row(s) before {inc} "
                     f"(e.g. {','.join(preinc[:5])})")

    # (b1) LEDGER — per-date cash vs the entry/exit replay. Hard FAIL.
    # Replaces the old latest-row-only recon, which read navs[-1] alone: one good
    # newer row made every bad older row permanently invisible, so the checker
    # retracted its own findings overnight (record DA crit; reproduced DB.6).
    # Walking every row in the epoch means a bad row stays failed on every later run.
    # CASH, not NAV, deliberately: historical NAV is not reproducible even in
    # principle — daily_price_refresh rewrites a rolling 30-day window with
    # INSERT OR REPLACE by design (CK.4). Cash depends only on the ledger.
    ledger_bad: list[str] = []
    history = hs.load_history(conn, strategy)
    ledger_rows = conn.execute(
        "SELECT nav_date, cash FROM paper_nav WHERE strategy_name=? "
        "AND nav_date >= ? ORDER BY nav_date", (strategy, LEDGER_EPOCH)).fetchall()
    for r in ledger_rows:
        delta = hs.state_at(history, r["nav_date"])["cash"] - r["cash"]
        if abs(delta) > hs.CASH_TOL:
            ledger_bad.append(f"{r['nav_date']}({delta:+.4f})")
    if ledger_bad:
        fails.append(f"ledger cash: {len(ledger_bad)} row(s) since {LEDGER_EPOCH} "
                     f"disagree with the entry/exit replay "
                     f"(e.g. {', '.join(ledger_bad[:5])})")

    # (b2) PRICE DRIFT — reported, never failed. This reprices CURRENT positions
    # with TODAY's cache as of the latest stored nav date and compares to that
    # row's total_nav, so it measures how far price_cache has been revised since
    # the row was written. That revision is by design (CK.4), which is why it is
    # no longer a FAIL: as a gate it produced a nightly false alarm whose failing
    # set turned over completely in 24h with nothing repaired (record DC).
    recon = "n/a"
    if navs:
        latest = navs[-1]
        stored = conn.execute(
            "SELECT total_nav FROM paper_nav WHERE strategy_name=? AND nav_date=?",
            (strategy, latest)).fetchone()["total_nav"]
        cash = conn.execute("SELECT cash FROM paper_portfolio WHERE strategy_name=?",
                            (strategy,)).fetchone()["cash"]
        pos = conn.execute(
            "SELECT ticker, qty, entry_price FROM paper_positions "
            "WHERE strategy_name=? AND status='open'", (strategy,)).fetchall()
        pv = 0.0
        for p in pos:
            px = _last_close(conn, p["ticker"], latest)
            pv += (px if px is not None else p["entry_price"]) * p["qty"]
        recon = f"{cash + pv - stored:+.2f}"

    # (c) position count vs target
    n_open = conn.execute(
        "SELECT COUNT(*) AS c FROM paper_positions WHERE strategy_name=? AND status='open'",
        (strategy,)).fetchone()["c"]
    tgt = POSITION_TARGETS.get(strategy)
    if tgt is None and strategy.startswith("residual_w") and strategy.endswith("_paper"):
        tgt = 50  # entire residual ladder (monthly / _wk / _2wk cadences) targets top-50
    if monthly and tgt is not None and n_open > tgt:
        fails.append(f"position count {n_open} EXCEEDS target {tgt}")
    # Lower bound, DAILY too: an EXCEEDS-only check let a catastrophically
    # liquidated sleeve (3 of 50 names) pass forever. Mild undershoot is NORMAL
    # (rebalance drops ineligible/untradable names; observed 43-50 of 50), so
    # this fires only at half the target — a wipeout, not a thin month.
    if tgt is not None and n_open < UNDERFILL_FRACTION * tgt:
        fails.append(f"position count {n_open} is UNDER {int(UNDERFILL_FRACTION*100)}% "
                     f"of target {tgt} - sleeve looks catastrophically under-filled")
    tgt_str = (f"{n_open}/{tgt}" if tgt is not None else f"{n_open}/var")

    info = (f"continuity({len(window)-len(missing)}/{len(window)}"
            f"{'' if not holiday_rows else f',+{holiday_rows}hol'}) "
            f"ledger({len(ledger_rows)-len(ledger_bad)}/{len(ledger_rows)}) "
            f"drift(${recon}) preinc({len(preinc)}) pos({tgt_str})")
    return fails, info


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["daily", "monthly"], default="daily")
    ap.add_argument("--db", default=None, help="DB path (default: live var/trades.db).")
    args = ap.parse_args()

    db_path = DB_PATH if args.db is None else Path(args.db)
    conn = _ro_connect(db_path)
    monthly = args.mode == "monthly"

    sleeves = [r["strategy_name"] for r in conn.execute(
        "SELECT strategy_name FROM paper_portfolio ORDER BY strategy_name")]
    # Earliest inception across sleeves bounds the calendar.
    earliest = min((inception(conn, s) for s in sleeves), default=date.today())
    calendar = trading_calendar(conn, earliest.isoformat())

    # Last trading day whose coverage has settled to the floor; anything after it
    # is PENDING publication (not a gap). Scan newest-first, stop at first settled.
    last_settled = calendar[-1] if calendar else date.today().isoformat()
    for d in reversed(calendar):
        if coverage_status(conn, d)["ok"]:
            last_settled = d
            break

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    cal_span = f"{calendar[0]}..{calendar[-1]}" if calendar else "none"
    pending_note = "" if (not calendar or last_settled == calendar[-1]) else \
        f"  (pending>{last_settled})"
    header = (f"=== {stamp} | verify_run mode={args.mode}  db={db_path.name}  "
              f"sleeves={len(sleeves)}  calendar={cal_span}  settled<={last_settled}"
              f"{pending_note} ===")
    out = [header]
    n_fail = 0
    for s in sleeves:
        fails, info = verify_sleeve(conn, s, calendar, monthly, last_settled)
        if fails:
            n_fail += 1
            out.append(f"[FAIL] {s:32s} {info}")
            for f in fails:
                out.append(f"         - {f}")
        else:
            out.append(f"[PASS] {s:32s} {info}")
    # (e) run-level cadence check — not per-sleeve, so it sits after the loop.
    logged, rb_status = read_last_rebalance()
    cadence_fails = check_rebalance_cadence(logged, last_settled, rb_status)
    cadence_info = (f"last_rebalance({logged or 'unreadable'}/{rb_status or 'nostatus'}) "
                    f"settled_month({last_settled[:7]})")
    out.append(f"[{'FAIL' if cadence_fails else 'PASS'}] {'(rebalance cadence)':32s} "
               f"{cadence_info}")
    for f in cadence_fails:
        out.append(f"         - {f}")

    if monthly:
        out.append("REMINDER (monthly): eyeball Alpaca submit/reject counts in the "
                   "rebalance log for the 3 mirrored sleeves; verify_run does not call the API.")
    result = (f"RESULT: {'FAIL' if n_fail or cadence_fails else 'PASS'} "
              f"({len(sleeves) - n_fail}/{len(sleeves)} sleeves OK"
              f"{'; rebalance cadence FAIL' if cadence_fails else ''})")
    out.append(result)

    for ln in out:
        (log.error if ln.startswith("[FAIL]") or ln.startswith("RESULT: FAIL") else log.info)(ln)

    # Co-locate the report with the DB it describes: live DB -> var/verify_report.log
    # (unchanged), a --db copy -> next to the copy, so test runs never pollute the
    # live ops log.
    report_path = db_path.parent / "verify_report.log"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "a", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n\n")

    return 1 if (n_fail or cadence_fails) else 0


if __name__ == "__main__":
    sys.exit(main())
