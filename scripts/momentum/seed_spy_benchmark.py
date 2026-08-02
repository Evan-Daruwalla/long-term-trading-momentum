"""One-off seed for the S&P 500 control as a *real* paper sleeve.

Creates `spy_benchmark_paper`: $100k invested in SPY at the 2026-05-01 close,
held (never rebalanced), and marked-to-market daily from inception -> today
using the same cached SPY closes every other sleeve uses. This is the "function
like another sleeve" benchmark requested 2026-06-10 — it replaces the old
yfinance-sourced dashboard line (which rate-limited and left the S&P curve
blank / "broken").

Idempotent: re-running won't double-buy the position, and it only marks NAV
dates that have no row yet (never rewrites settled NAV history).
Before the first close at/after inception exists, it creates a $100k cash stub
(inception set) and buys on the first run where a close is available — so it can
be wired into rebalance.bat to auto-seed the 07-01 baseline when 07-01 arrives.

Also seeds other buy-hold index benchmarks via --ticker (record CE: the QQQ
control sleeves qqq_benchmark_paper / qqq_benchmark_0701_paper use the same
mechanics — only the ticker and sleeve name differ).

Run (default 05-01 SPY baseline):
  .venv\\Scripts\\python.exe -m scripts.momentum.seed_spy_benchmark
Run (07-01 baseline, aligned with the 07-01 LLM-experiment cohort):
  .venv\\Scripts\\python.exe -m scripts.momentum.seed_spy_benchmark --sleeve spy_benchmark_0701_paper --inception 2026-07-01
Run (QQQ controls):
  .venv\\Scripts\\python.exe -m scripts.momentum.seed_spy_benchmark --sleeve qqq_benchmark_paper --ticker QQQ
  .venv\\Scripts\\python.exe -m scripts.momentum.seed_spy_benchmark --sleeve qqq_benchmark_0701_paper --ticker QQQ --inception 2026-07-01
"""
from __future__ import annotations

import argparse
from datetime import date

from trading_bot.db import connect
from trading_bot.execution import paper_trader
from scripts.momentum import paper_mtm

SLEEVE = "spy_benchmark_paper"
INCEPTION = date(2026, 5, 1)
START_CASH = 100_000.0


def _closes_since(ticker: str, d0: date) -> list[tuple[str, float]]:
    # trading_bot.db.connect, not raw sqlite3.connect: it sets busy_timeout=30s
    # so a collision with the concurrent writer waits instead of dying on
    # "database is locked" (audit 2026-07-17, record CG).
    with connect() as conn:
        rows = conn.execute(
            "SELECT key_date, price FROM price_cache "
            "WHERE ticker=? AND kind='close' AND key_date>=? ORDER BY key_date",
            (ticker, d0.isoformat()),
        ).fetchall()
    return [(d, p) for d, p in rows if p and p > 0]


def _existing_nav_dates(sleeve: str) -> set[str]:
    with connect() as conn:
        return {r[0] for r in conn.execute(
            "SELECT nav_date FROM paper_nav WHERE strategy_name=?", (sleeve,))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sleeve", default=SLEEVE)
    ap.add_argument("--ticker", default="SPY",
                    help="Index ETF to buy-hold (default SPY; e.g. QQQ)")
    ap.add_argument("--inception", default=INCEPTION.isoformat(),
                    help="ISO date YYYY-MM-DD")
    args = ap.parse_args()
    sleeve = args.sleeve
    ticker = args.ticker
    inception = date.fromisoformat(args.inception)

    paper_trader.init(sleeve, START_CASH)
    # Backdate inception so the dashboard's inception logic lines up.
    with connect() as conn:
        conn.execute(
            "UPDATE paper_portfolio SET initialized_at=? WHERE strategy_name=?",
            (inception.isoformat() + "T00:00:00+00:00", sleeve),
        )

    closes = _closes_since(ticker, inception)
    if not closes:
        # No close at/after inception yet (e.g. 07-01 baseline seeded on 06-30):
        # the $100k cash stub now exists; re-run once the close lands to buy + MTM.
        print(f"No {ticker} closes in cache since {inception} — created $100k stub "
              f"for {sleeve}; re-run on/after the inception close to buy + MTM.")
        return 0
    first_date, first_px = closes[0]

    # Buy the index ETF fully-invested at the inception close (idempotent).
    if not paper_trader.list_open(sleeve):
        qty = START_CASH / first_px
        paper_trader.buy(strategy_name=sleeve, ticker=ticker, qty=qty,
                         fill_price=first_px, as_of=inception, sector="Index")
        print(f"Bought {qty:.6f} {ticker} @ {first_px} on {first_date}")
    else:
        print(f"{ticker} position already open - skipping buy")

    # Daily MTM from inception -> today, GAP-FILL ONLY. write_nav is INSERT OR
    # REPLACE and rebalance.bat runs this every month, so looping every cached
    # close used to restamp the sleeve's ENTIRE settled NAV history on each run
    # — NAV history is never rewritten (project rule). Dates that already have a
    # row are skipped; a brand-new sleeve has none, so seeding is unchanged.
    already = _existing_nav_dates(sleeve)
    n = 0
    for d_iso, _ in closes:
        if d_iso in already:
            continue
        as_of = date.fromisoformat(d_iso)
        nav = paper_mtm.compute_nav(sleeve, as_of)
        paper_mtm.write_nav(sleeve, as_of, nav)
        n += 1

    pf = paper_trader.get(sleeve)
    last_nav = paper_mtm.compute_nav(sleeve, date.fromisoformat(closes[-1][0]))
    print(f"MTM'd {n} new trading day(s) "
          f"(scanned {closes[0][0]} -> {closes[-1][0]}). "
          f"cash=${pf.cash:.6f}  "
          f"NAV=${last_nav['total_nav']:,.4f}  "
          f"({(last_nav['total_nav'] / START_CASH - 1) * 100:+.4f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
