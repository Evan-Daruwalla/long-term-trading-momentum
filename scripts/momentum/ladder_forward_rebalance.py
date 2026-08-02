"""Forward (live) rebalancer for the WEEKLY + BIWEEKLY residual ladders (record CD).

The monthly ladder rebalances forward via rebalance.bat (the monthly task). The
weekly/biweekly ladders need their own cadence — this runs EVERY evening (the
TradingLadderRebalance task, after the 5:15pm daily MTM) and self-determines
whether today is a rebalance day for each cadence, rebalancing only the due
sleeves. Self-determination from the trading calendar (not a fixed weekday
trigger) means holidays and the every-other-week biweekly cadence are handled
correctly.

CONCURRENCY: one process rebalances all due sleeves SEQUENTIALLY, so it never
runs a factor_backtest concurrently with itself. It is scheduled AFTER the
monthly rebalance window (6:03pm) and the daily MTM (5:15pm) so no two rebalance
processes overlap — the project's hard "never concurrent factor_backtest" rule.

RULES (mirror how the ladder was seeded, record CD):
  weekly   -> rebalance if this cadence has not yet traded inside the CURRENT
              calendar week (period start = this week's Monday).
  biweekly -> same test against the current TWO-week block, whose start is an
              EVEN number of ordinal weeks since ANCHOR_MONDAY (2026-04-27, the
              Monday of the 05-01 seed week). Ordinal parity, not ISO-week-number
              parity: ISO parity breaks in 53-week years (2026) with a one-time
              3-week gap at the year boundary (record CG).

  Due-ness is PERIOD-based, not day-based, and therefore SELF-HEALING: the old
  rule ("today IS the first trading day of the week") permanently lost a cycle
  whenever the evening task failed to run, which is exactly what happened on
  2026-07-20 — both cadences were skipped and the biweekly arm sat buy-and-hold
  from 07-06 while verify_run kept reporting PASS (audit 2026-07-28). Under the
  period rule a missed evening is picked up by the next trading day in the same
  period. 'today is a trading day' = today has >= TRADING_DAY_MIN cached closes
  (market was open; a holiday leaves only a couple hundred stray rows). Ranks use
  trailing (t-21) data, so evening partial coverage does not misrank — the same
  reason rebalance.bat has no coverage gate.

Like rebalance.bat, the rebalance day is force-marked (compute_nav + write_nav)
so verify_run reconciles the new positions against a same-day NAV.

Usage:
  python -m scripts.momentum.ladder_forward_rebalance --dry-run   # decide + print, no writes
  python -m scripts.momentum.ladder_forward_rebalance             # LIVE (the scheduled task)
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from datetime import date, timedelta

from scripts.momentum.seed_residual_cadence_ladder import WEIGHTS, CADENCES, MONTHLY_DATES

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("ladder_forward_rebalance")

TRADING_DAY_MIN = 1000          # market-open threshold (matches check_coverage)
# Biweekly anchor = the MONDAY of the 05-01 seed week (2026-04-27). Parity uses
# ordinal weeks since this date, NOT raw ISO week numbers: ISO parity breaks in
# a 53-week year (2026 is one) and would insert a one-time 3-week gap across
# 2026-12-21 -> 2027-01-11 (audit 2026-07-17, record CG). Ordinal parity gives
# strict 14-day spacing forever and is identical to the seeded schedule
# (05-01, 05-11, 05-26, 06-08, 06-22, 07-06, then 07-20, 08-03, ...).
ANCHOR_MONDAY = MONTHLY_DATES[0] - timedelta(days=MONTHLY_DATES[0].weekday())  # 2026-04-27
TOP_N = 50
HALF_SPREAD_BPS = 5.0           # same fill model the ladder was seeded with

WEEKLY_SLEEVES = [CADENCES["weekly"][1](mm, rr) for mm, rr in WEIGHTS]
BIWEEKLY_SLEEVES = [CADENCES["biweekly"][1](mm, rr) for mm, rr in WEIGHTS]


def _today_close_count(db_path, d: date) -> int:
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    n = conn.execute("SELECT COUNT(*) FROM price_cache WHERE kind='close' "
                     "AND price IS NOT NULL AND key_date=?", (d.isoformat(),)).fetchone()[0]
    conn.close()
    return n


def _last_activity_date(db_path, names) -> date | None:
    """Latest as-of date on which this cadence actually traded (entry or exit).

    Used instead of paper_portfolio.last_rebalanced_at because that column is
    stamped with write-time UTC (paper_trader.mark_rebalanced), so an evening
    CDT run lands on the NEXT UTC day and cannot be compared to an as-of date.
    Position dates are true as-of dates, so they are timezone-proof."""
    if not names:
        return None
    qs = ",".join("?" * len(names))
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    row = conn.execute(
        f"SELECT MAX(d) FROM (SELECT MAX(entry_date) d FROM paper_positions "
        f"WHERE strategy_name IN ({qs}) "
        f"UNION ALL SELECT MAX(exit_date) FROM paper_positions "
        f"WHERE strategy_name IN ({qs}))", tuple(names) * 2).fetchone()
    conn.close()
    return date.fromisoformat(row[0]) if row and row[0] else None


def _rebalance_sleeves(names, as_of, paper_rebalance, paper_mtm):
    """Rebalance each sleeve, isolating failures so one bad sleeve cannot abort
    the rest of the ladder. Returns (done, failed) — mirrors monthly_rebalance."""
    from trading_bot.db import connect
    done, failed = [], []
    for name in names:
        try:
            with connect() as conn:
                row = conn.execute("SELECT strategy_name FROM paper_portfolio "
                                   "WHERE strategy_name=?", (name,)).fetchone()
            if row is None:
                log.warning("%s: sleeve does not exist; skipping", name)
                failed.append(name)
                continue
            n = paper_rebalance.rebalance(
                as_of=as_of, strategy_name=name, starting_cash=100_000.0,
                top_n=TOP_N, half_spread_bps=HALF_SPREAD_BPS,
                dry_run=False, broker_realistic=True,
            )
            nav = paper_mtm.compute_nav(name, as_of)
            paper_mtm.write_nav(name, as_of, nav)
            log.info("%s: %d changes; NAV@%s $%.2f", name, n, as_of, nav["total_nav"])
            done.append(name)
        except Exception:
            log.exception("%s: rebalance FAILED; continuing with remaining sleeves", name)
            failed.append(name)
    return done, failed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Decide + print, write nothing.")
    ap.add_argument("--as-of", default=None, help="Override today (ISO date), for testing.")
    args = ap.parse_args()

    import trading_bot.db as _db
    db_path = _db.DB_PATH
    today = date.fromisoformat(args.as_of) if args.as_of else date.today()

    n_today = _today_close_count(db_path, today)
    if n_today < TRADING_DAY_MIN:
        log.info("%s is not a trading day (%d closes < %d); nothing to rebalance.",
                 today, n_today, TRADING_DAY_MIN)
        return 0

    # Due-ness is PERIOD-based, not day-based: "has this cadence rebalanced yet
    # inside its current period?" rather than "is today the first trading day of
    # the week?". The day-based form silently lost a whole cycle whenever the
    # evening task did not run — 2026-07-20 was missed for both cadences and
    # could never be recovered, leaving the biweekly arm buy-and-hold from 07-06
    # (audit 2026-07-28). Period boundaries are calendar Mondays, so a holiday
    # Monday simply shifts the catch-up to the first trading day that follows.
    ordinal_week = (today - ANCHOR_MONDAY).days // 7
    week_start = today - timedelta(days=today.weekday())
    block_start = ANCHOR_MONDAY + timedelta(weeks=ordinal_week - (ordinal_week % 2))

    weekly_last = _last_activity_date(db_path, WEEKLY_SLEEVES)
    biweekly_last = _last_activity_date(db_path, BIWEEKLY_SLEEVES)
    weekly_due = weekly_last is None or weekly_last < week_start
    biweekly_due = biweekly_last is None or biweekly_last < block_start

    log.info("today=%s (+%dw from anchor) | weekly: last=%s period>=%s due=%s | "
             "biweekly: last=%s period>=%s due=%s",
             today, ordinal_week, weekly_last, week_start, weekly_due,
             biweekly_last, block_start, biweekly_due)

    plan = []
    if weekly_due:
        plan.append(("weekly", WEEKLY_SLEEVES))
    if biweekly_due:
        plan.append(("biweekly", BIWEEKLY_SLEEVES))

    if not plan:
        log.info("Both cadences already rebalanced inside their current period; "
                 "nothing due today.")
        return 0

    if args.dry_run:
        for cad, names in plan:
            log.info("[DRY] would rebalance %d %s sleeves as-of %s", len(names), cad, today)
        return 0

    from scripts.momentum import paper_rebalance, paper_mtm
    all_failed = []
    for cad, names in plan:
        log.info("=== %s ladder: rebalancing %d sleeves as-of %s ===", cad, len(names), today)
        done, failed = _rebalance_sleeves(names, today, paper_rebalance, paper_mtm)
        log.info("=== %s: rebalanced %d/%d sleeves (%d failed) ===",
                 cad, len(done), len(names), len(failed))
        all_failed.extend(failed)

    if all_failed:
        log.error("%d sleeve(s) FAILED: %s", len(all_failed), ", ".join(all_failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
