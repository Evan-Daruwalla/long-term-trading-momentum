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
  weekly   -> rebalance if today is the FIRST trading day of its ISO week.
  biweekly -> also require today's ISO week to be an even number of weeks after
              the 05-01 anchor week (W18) — i.e. weeks W18, W20, W22, ...

  'first trading day of the week' = the most recent settled trading day BEFORE
  today falls in an earlier ISO week. 'today is a trading day' = today has
  >= TRADING_DAY_MIN cached closes (market was open; a holiday leaves only a
  couple hundred stray rows). Ranks use trailing (t-21) data, so evening partial
  coverage does not misrank — same reason rebalance.bat has no coverage gate.

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
from datetime import date

from scripts.momentum.seed_residual_cadence_ladder import WEIGHTS, CADENCES, MONTHLY_DATES

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("ladder_forward_rebalance")

TRADING_DAY_MIN = 1000          # market-open threshold (matches check_coverage)
ANCHOR_WEEK = MONTHLY_DATES[0].isocalendar()[1]   # 05-01 ISO week = W18
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


def _last_trading_day_before(db_path, d: date) -> date | None:
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    rows = conn.execute(
        "SELECT key_date, COUNT(*) n FROM price_cache WHERE kind='close' AND price IS NOT NULL "
        "AND key_date < ? GROUP BY key_date ORDER BY key_date DESC LIMIT 30",
        (d.isoformat(),)).fetchall()
    conn.close()
    for kd, n in rows:
        if n >= TRADING_DAY_MIN:
            return date.fromisoformat(kd)
    return None


def _rebalance_sleeves(names, as_of, paper_rebalance, paper_mtm):
    from trading_bot.db import connect
    done = []
    for name in names:
        with connect() as conn:
            row = conn.execute("SELECT last_rebalanced_at FROM paper_portfolio "
                               "WHERE strategy_name=?", (name,)).fetchone()
        if row is None:
            log.warning("%s: sleeve does not exist; skipping", name)
            continue
        if row["last_rebalanced_at"] and str(row["last_rebalanced_at"])[:10] == as_of.isoformat():
            log.info("%s: already rebalanced %s; skipping", name, as_of)
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
    return done


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

    prev = _last_trading_day_before(db_path, today)
    weekly_due = prev is None or prev.isocalendar()[:2] != today.isocalendar()[:2]
    biweekly_due = weekly_due and (today.isocalendar()[1] - ANCHOR_WEEK) % 2 == 0

    log.info("today=%s week=W%d prev_trading_day=%s | weekly_due=%s biweekly_due=%s",
             today, today.isocalendar()[1], prev, weekly_due, biweekly_due)

    if not weekly_due:
        log.info("Not the first trading day of the week; no ladder rebalance due today.")
        return 0

    plan = [("weekly", WEEKLY_SLEEVES)]
    if biweekly_due:
        plan.append(("biweekly", BIWEEKLY_SLEEVES))

    if args.dry_run:
        for cad, names in plan:
            log.info("[DRY] would rebalance %d %s sleeves as-of %s", len(names), cad, today)
        return 0

    from scripts.momentum import paper_rebalance, paper_mtm
    for cad, names in plan:
        log.info("=== %s ladder: rebalancing %d sleeves as-of %s ===", cad, len(names), today)
        done = _rebalance_sleeves(names, today, paper_rebalance, paper_mtm)
        log.info("=== %s: rebalanced %d/%d sleeves ===", cad, len(done), len(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
