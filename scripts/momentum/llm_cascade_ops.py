"""Operations CLI for the LLM-CASCADE sleeves (the 'always invested' 3rd pair).

Unlike the cash overlays, a VETO here means 'skip to the next-best candidate',
not 'go to cash'. Decisions are SHARED with the cash overlays' logs, so you log
them with the EXISTING `llm_overlay_ops decide` (stock) and `sector_overlay_ops
decide` (sector) — just deeper into the ranking. These sleeves then read those
decisions and cascade.

Subcommands
-----------
  init               Idempotently create both cascade paper portfolios ($100k).
  rebalance-stock    Hold the first BUY in the top-10 mom_roa names (else #1).
  rebalance-sector   Hold the first 4 HOLD sectors (else momentum-fill to 4).

Monthly flow (after logging decisions via the existing overlay `decide` CLIs):
  python -m scripts.momentum.llm_cascade_ops rebalance-stock
  python -m scripts.momentum.llm_cascade_ops rebalance-sector

See trading_bot/strategies/llm_cascade.py for the design + fallbacks.
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date

from trading_bot.execution import market_data, paper_trader
from trading_bot.factors import sector_momentum
from trading_bot.strategies import llm_cascade
from scripts.momentum.llm_overlay_ops import _set_single_position

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("llm_cascade_ops")


def _nav(strategy_name: str, as_of: date) -> float:
    pf = paper_trader.get(strategy_name)
    val = 0.0
    for p in paper_trader.list_open(strategy_name):
        px = market_data.last_close_on_or_before(p["ticker"], as_of)[0] or p["entry_price"]
        val += p["qty"] * px
    return pf.cash + val


def cmd_init(args) -> int:
    paper_trader.init(strategy_name=llm_cascade.STOCK_CASCADE_STRATEGY,
                      starting_cash=llm_cascade.STARTING_CASH)
    paper_trader.init(strategy_name=llm_cascade.SECTOR_CASCADE_STRATEGY,
                      starting_cash=llm_cascade.STARTING_CASH)
    log.info("Initialized %s and %s (idempotent).",
             llm_cascade.STOCK_CASCADE_STRATEGY, llm_cascade.SECTOR_CASCADE_STRATEGY)
    return 0


def cmd_rebalance_stock(args) -> int:
    as_of = date.fromisoformat(args.as_of)
    paper_trader.init(strategy_name=llm_cascade.STOCK_CASCADE_STRATEGY,
                      starting_cash=llm_cascade.STARTING_CASH)
    market_data.preload_caches()
    pick = llm_cascade.stock_pick(as_of)
    if pick is None:
        log.error("[stock-cascade] empty universe at %s — aborted.", as_of)
        return 1
    ticker, z, fallback = pick
    log.info("[stock-cascade] pick=%s z=%+.3f %s", ticker, z,
             "(FALLBACK to #1 — no BUY in top-%d)" % llm_cascade.CASCADE_DEPTH
             if fallback else "(LLM-approved BUY)")
    _set_single_position(
        strategy_name=llm_cascade.STOCK_CASCADE_STRATEGY, target=ticker,
        entry_score=z, as_of=as_of, dry_run=args.dry_run)
    return 0


def cmd_rebalance_sector(args) -> int:
    as_of = date.fromisoformat(args.as_of)
    strat = llm_cascade.SECTOR_CASCADE_STRATEGY
    paper_trader.init(strategy_name=strat, starting_cash=llm_cascade.STARTING_CASH)
    market_data.preload_caches()

    picks, approved = llm_cascade.sector_picks(as_of)
    if not picks:
        log.error("[sector-cascade] no sector candidates at %s — aborted.", as_of)
        return 1
    filled = [t for t in picks if t not in approved]
    log.info("[sector-cascade] hold=%s  (HOLD-approved=%s  momentum-fill=%s)",
             picks, approved, filled)

    spread = llm_cascade.HALF_SPREAD_BPS / 10_000.0
    nav = _nav(strat, as_of)
    slot = nav / llm_cascade.SECTOR_SLOTS
    log.info("[sector-cascade] NAV=$%.2f  slot=$%.2f (1/%d)",
             nav, slot, llm_cascade.SECTOR_SLOTS)

    current = {p["ticker"]: p for p in paper_trader.list_open(strat)}
    target = set(picks)
    sells = [p for t, p in current.items() if t not in target]
    buys = [t for t in picks if t not in current]

    trades = 0
    for p in sells:
        px = market_data.last_close_on_or_before(p["ticker"], as_of)[0]
        if px is None or px <= 0:
            log.warning("  skip sell %s: no price at %s", p["ticker"], as_of)
            continue
        fill = px * (1.0 - spread)
        if args.dry_run:
            log.info("  DRY SELL %s qty=%.4f @ ~$%.2f", p["ticker"], p["qty"], fill)
        else:
            realized = paper_trader.sell(position_id=p["id"], qty=p["qty"],
                                         fill_price=fill, as_of=as_of,
                                         strategy_name=strat)
            log.info("  SELL %s qty=%.4f @ $%.2f pnl=$%+.2f",
                     p["ticker"], p["qty"], fill, realized)
        trades += 1

    for t in buys:
        px = market_data.last_close_on_or_before(t, as_of)[0]
        if px is None or px <= 0:
            log.warning("  skip buy %s: no price at %s", t, as_of)
            continue
        avail = paper_trader.get(strat).cash * 0.999
        dollars = min(slot, avail)
        fill = px * (1.0 + spread)
        qty = dollars / fill
        if qty <= 0:
            log.warning("  skip buy %s: no cash (avail $%.2f)", t, avail)
            continue
        if args.dry_run:
            log.info("  DRY BUY %s qty=%.4f @ ~$%.2f ($%.2f)", t, qty, fill, dollars)
        else:
            paper_trader.buy(strategy_name=strat, ticker=t, qty=qty, fill_price=fill,
                             as_of=as_of, entry_score=None,
                             sector=sector_momentum.SECTOR_NAMES.get(t))
            log.info("  BUY %s qty=%.4f @ $%.2f ($%.2f)", t, qty, fill, dollars)
        trades += 1

    if not args.dry_run:
        paper_trader.mark_rebalanced(strat)
    log.info("[sector-cascade] rebalance %s: %d trades; held=%s",
             "DRY" if args.dry_run else "done", trades, picks)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_i = sub.add_parser("init", help="create both cascade portfolios")
    p_i.set_defaults(func=cmd_init)

    p_s = sub.add_parser("rebalance-stock", help="cascade-rebalance the stock sleeve")
    p_s.add_argument("--as-of", default=date.today().isoformat())
    p_s.add_argument("--dry-run", action="store_true")
    p_s.set_defaults(func=cmd_rebalance_stock)

    p_x = sub.add_parser("rebalance-sector", help="cascade-rebalance the sector sleeve")
    p_x.add_argument("--as-of", default=date.today().isoformat())
    p_x.add_argument("--dry-run", action="store_true")
    p_x.set_defaults(func=cmd_rebalance_sector)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
