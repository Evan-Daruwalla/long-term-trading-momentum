"""Daily mark-to-market logger for paper-trade portfolio.

Writes one row to paper_nav per (strategy_name, nav_date). Idempotent —
re-running for the same date REPLACES the row (REPLACE INTO), so it's safe
to run multiple times per day during testing.

Usage:
  # Today:
  python -m scripts.momentum.paper_mtm

  # Specific date (useful for backfilling NAVs from inception):
  python -m scripts.momentum.paper_mtm --as-of 2026-05-01

  # Strategy:
  python -m scripts.momentum.paper_mtm --strategy mom_v2_paper

NAV components:
  - cash (from paper_portfolio.cash)
  - positions_value = sum(qty × close_at(as_of)) for all open positions
  - total_nav = cash + positions_value

When a ticker has no cached close on as_of (delisted, halted, weekend),
it's marked-to-market using the most recent prior close (carry-forward).
This matches how factor_backtest's _mark_to_market handles it.
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date

from trading_bot.db import connect, init_db
from trading_bot.execution import market_data, paper_trader

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("paper_mtm")


def compute_nav(strategy_name: str, as_of: date) -> dict:
    """Returns {cash, positions_value, total_nav, n_open, missing_count,
    aged_count, median_age_days}."""
    pf = paper_trader.get(strategy_name)
    open_positions = paper_trader.list_open(strategy_name)
    positions_value = 0.0
    missing = 0
    ages: list[int] = []
    for p in open_positions:
        px, px_date = market_data.last_close_on_or_before(p["ticker"], as_of)
        if px is None:
            log.warning("  No close for %s at-or-before %s - using entry_price",
                        p["ticker"], as_of)
            px = p["entry_price"]
            missing += 1
        else:
            ages.append((as_of - px_date).days)
        positions_value += px * p["qty"]
    aged = sum(1 for a in ages if a > 3)
    median_age = sorted(ages)[len(ages) // 2] if ages else 0
    return {
        "cash": pf.cash,
        "positions_value": positions_value,
        "total_nav": pf.cash + positions_value,
        "n_open": len(open_positions),
        "missing_count": missing,
        "aged_count": aged,
        "median_age_days": median_age,
    }


def write_nav(strategy_name: str, as_of: date, nav: dict) -> None:
    init_db()
    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO paper_nav "
            "(strategy_name, nav_date, cash, positions_value, total_nav, n_open_positions) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (strategy_name, as_of.isoformat(),
             nav["cash"], nav["positions_value"], nav["total_nav"], nav["n_open"]),
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=date.today().isoformat())
    ap.add_argument("--strategy", default=paper_trader.DEFAULT_STRATEGY)
    args = ap.parse_args()

    as_of = date.fromisoformat(args.as_of)
    # Skip weekends: the TradingDailyMTM scheduled task (StartWhenAvailable)
    # also fires on Sat/Sun, which wrote carry-forward NAV rows on non-trading
    # days (audit 2026-06-09 found 12 weekend rows; deleted). Holidays still
    # write a flat row — rare and harmless vs. risking a skipped real day.
    if as_of.weekday() >= 5:
        log.info("MTM %s is a weekend — skipping (no trading day).", as_of)
        return 0
    nav = compute_nav(args.strategy, as_of)
    write_nav(args.strategy, as_of, nav)

    # Compute return vs starting cash for log readability
    pf = paper_trader.get(args.strategy)
    pct = (nav["total_nav"] / pf.starting_cash - 1.0) * 100.0
    log.info("MTM %s  strategy=%s", as_of, args.strategy)
    log.info("  Cash:            $%12.2f", nav["cash"])
    log.info("  Positions value: $%12.2f", nav["positions_value"])
    log.info("  TOTAL NAV:       $%12.2f  (%+.3f%% vs start)", nav["total_nav"], pct)
    log.info("  Open positions:  %d", nav["n_open"])
    if nav["missing_count"]:
        log.warning("  Missing prices (used entry_price): %d / %d positions",
                    nav["missing_count"], nav["n_open"])
    if nav["aged_count"]:
        level = log.error if nav["median_age_days"] > 7 else log.warning
        level("  PRICE STALENESS: %d / %d positions have prices >3d old "
              "(median age %dd). Run daily_price_refresh.py.",
              nav["aged_count"], nav["n_open"], nav["median_age_days"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
