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
from scripts.momentum.check_coverage import coverage_status

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


def inception_date(strategy_name: str) -> date:
    """Earliest date a NAV row is legitimate for this sleeve.

    = min( date(paper_portfolio.initialized_at), earliest paper_positions.entry_date ).
    Neither source alone is correct: initialized_at is a wall-clock stamp that runs
    LATER than the true start for BACKDATED sleeves (mom_roa_6535_paper was re-inited
    2026-06-13 but its history goes back to 2026-05-01), while earliest entry_date runs
    later than inception for the 07-06 cohort (positions fill at the NEXT open 2026-07-07,
    but inception / first NAV is 2026-07-06). Their min is correct for every current
    sleeve and errs EARLY, so the guard can only skip genuinely pre-inception dates,
    never a legitimate one. Defensive: on any parse issue returns date.min, so a bad
    row can never make the daily MTM wrongly skip a live sleeve.
    """
    with connect() as conn:
        prow = conn.execute(
            "SELECT initialized_at FROM paper_portfolio WHERE strategy_name=?",
            (strategy_name,)).fetchone()
        erow = conn.execute(
            "SELECT MIN(entry_date) AS d FROM paper_positions WHERE strategy_name=?",
            (strategy_name,)).fetchone()
    candidates: list[date] = []
    for raw in (prow["initialized_at"] if prow else None,
                erow["d"] if erow else None):
        if raw:
            try:
                candidates.append(date.fromisoformat(str(raw)[:10]))
            except ValueError:
                pass
    return min(candidates) if candidates else date.min


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
    ap.add_argument("--force", action="store_true",
                    help="MTM even if the day's coverage is below the floor "
                         "(bypass the coverage gate). Use only when you know the "
                         "held names are all present.")
    args = ap.parse_args()

    as_of = date.fromisoformat(args.as_of)
    # Skip weekends: the TradingDailyMTM scheduled task (StartWhenAvailable)
    # also fires on Sat/Sun, which wrote carry-forward NAV rows on non-trading
    # days (audit 2026-06-09 found 12 weekend rows; deleted). Holidays still
    # write a flat row — rare and harmless vs. risking a skipped real day.
    if as_of.weekday() >= 5:
        log.info("MTM %s is a weekend — skipping (no trading day).", as_of)
        return 0
    # Pre-inception guard: never write a NAV row dated before the sleeve's
    # inception. This is the holiday-weekend $100k-pollution class (record
    # Appendices AU/AV) that previously needed manual row deletion.
    inc = inception_date(args.strategy)
    if as_of < inc:
        log.warning("SKIP pre-inception: %s as_of=%s is before inception=%s — "
                    "no NAV row written.", args.strategy, as_of, inc)
        return 0
    # Coverage gate: refuse to mark a day whose universe publication is below the
    # floor, unless --force. This closes the raw-`paper_mtm` bypass of the daily
    # flow's gate (record Appendix BP: a concurrent session backfilled 07-09 at
    # 4,726 < floor via raw paper_mtm). mtm_catchup does its own per-day gating
    # and calls compute_nav/write_nav directly, so it is unaffected by this.
    if not args.force:
        with connect() as conn:
            cov = coverage_status(conn, as_of.isoformat())
        if not cov["ok"]:
            log.error("COVERAGE FAIL: %s has %d closes < floor %d — refusing to MTM "
                      "%s (pass --force to override; see record Appendix BP).",
                      as_of, cov["count"], cov["floor"], args.strategy)
            return 2
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
