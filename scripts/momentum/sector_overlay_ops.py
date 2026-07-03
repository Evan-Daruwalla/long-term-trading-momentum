"""Operations CLI for the SECTOR-overlay experiment (macro LLM veto).

Parallel to llm_overlay_ops.py but for the sector_top4 sleeve and MULTI-NAME:
the treatment holds the 4 momentum-picked SPDR sectors at ~25% each, except
sectors the LLM VETOs (their 25% slot stays cash). Control = sector_top4_paper
(already run by rebalance.bat); this CLI only drives the treatment sleeve.

Subcommands
-----------
  candidate           Print the 4 candidate sectors + macro prompts (per sector).
  decide              Log one pre-committed decision (HOLD/VETO) for a sector.
  rebalance           Rebalance the treatment (refuses unless all 4 decided).
  check-invalidation  Exit any held sector to cash if its stop is breached.
  init                Idempotently create the treatment paper portfolio.

Monthly flow
------------
  python -m scripts.momentum.sector_overlay_ops candidate
  # run the 4 macro prompts per sector, then ONE decide per sector:
  python -m scripts.momentum.sector_overlay_ops decide --ticker XLK --score 4 \
      --verdict VETO --invalidation 175 --rationale "narrow semi leadership, rates headwind"
  ... (repeat for the other 3 sectors) ...
  python -m scripts.momentum.sector_overlay_ops rebalance

Daily (fold into daily.bat)
---------------------------
  python -m scripts.momentum.sector_overlay_ops check-invalidation

See trading_bot/strategies/sector_overlay.py for the design + kill switch.
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date

from trading_bot.execution import market_data, paper_trader
from trading_bot.factors import sector_momentum
from trading_bot.strategies import sector_overlay

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("sector_overlay_ops")


def _init() -> None:
    paper_trader.init(strategy_name=sector_overlay.TREATMENT_STRATEGY,
                      starting_cash=sector_overlay.STARTING_CASH)


def _nav(strategy_name: str, as_of: date) -> float:
    """Current mark-to-market NAV = cash + Σ qty·last_close (carry-forward)."""
    pf = paper_trader.get(strategy_name)
    val = 0.0
    for p in paper_trader.list_open(strategy_name):
        px = market_data.last_close_on_or_before(p["ticker"], as_of)[0] or p["entry_price"]
        val += p["qty"] * px
    return pf.cash + val


# ---------------- subcommands ----------------

def cmd_candidate(args) -> int:
    as_of = date.fromisoformat(args.as_of)
    market_data.preload_caches()
    cands = sector_overlay.candidates(as_of)
    if not cands:
        log.error("No sector candidates at %s (cache empty?).", as_of)
        return 1
    print("=" * 70)
    print(f"SECTOR-OVERLAY CANDIDATES  (as_of {as_of})  top-{sector_overlay.TOP_N}")
    print("=" * 70)
    for ticker, score in cands:
        px = market_data.last_close_on_or_before(ticker, as_of)[0]
        name = sector_momentum.SECTOR_NAMES.get(ticker, ticker)
        print(f"\n### {ticker} ({name})  mom={score:+.3f}  "
              f"close={'$%.2f' % px if px else 'n/a'}")
        for line in sector_overlay.prompts(ticker):
            print("  " + line.replace("\n", "\n  "))
    print("\n" + "=" * 70)
    print("Then, ONCE PER SECTOR:")
    print("  python -m scripts.momentum.sector_overlay_ops decide --ticker XXX \\")
    print("      --score N --verdict HOLD|VETO --invalidation PRICE --rationale \"...\"")
    print("Then: python -m scripts.momentum.sector_overlay_ops rebalance")
    print("=" * 70)
    return 0


def cmd_decide(args) -> int:
    decision_date = date.fromisoformat(args.as_of)
    sector_overlay.record_decision(
        decision_date=decision_date, ticker=args.ticker.upper(),
        score=args.score, verdict=args.verdict,
        invalidation_level=args.invalidation, rationale=args.rationale)
    log.info("Logged %s decision for %s: %s score=%s invalidation=%s",
             args.ticker.upper(), decision_date, args.verdict.upper(),
             args.score, args.invalidation)
    return 0


def cmd_rebalance(args) -> int:
    as_of = date.fromisoformat(args.as_of)
    _init()
    market_data.preload_caches()
    strat = sector_overlay.TREATMENT_STRATEGY

    cands = sector_overlay.candidates(as_of)
    if not cands:
        log.error("No sector candidates at %s — rebalance aborted.", as_of)
        return 1
    cand_tickers = [t for t, _ in cands]

    # Require a decision for EVERY candidate (won't silently become the control)
    decisions = sector_overlay.decisions_for(as_of)
    missing = [t for t in cand_tickers if t not in decisions]
    if missing:
        log.error("[treatment] missing decisions for %s on %s. Run `candidate` "
                  "+ `decide` for all %d sectors first. Refusing to trade.",
                  missing, as_of, len(cand_tickers))
        return 1

    holds = [t for t in cand_tickers if decisions[t]["verdict"] == "HOLD"]
    vetoes = [t for t in cand_tickers if decisions[t]["verdict"] == "VETO"]
    log.info("[treatment] candidates=%s  HOLD=%s  VETO=%s",
             cand_tickers, holds, vetoes)

    spread = sector_overlay.HALF_SPREAD_BPS / 10_000.0
    nav = _nav(strat, as_of)
    slot = nav / sector_overlay.TOP_N      # fixed 1/TOP_N sizing; veto slot -> cash
    log.info("[treatment] NAV=$%.2f  slot=$%.2f (1/%d)", nav, slot, sector_overlay.TOP_N)

    current = {p["ticker"]: p for p in paper_trader.list_open(strat)}
    target = set(holds)
    sells = [p for t, p in current.items() if t not in target]   # rotated-out OR vetoed
    buys = [t for t in holds if t not in current]                # keeps are left untouched

    trades = 0
    # 1. Sells (rotated-out or newly-vetoed) -> cash
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

    # 2. Buys (new HOLD sectors) at the fixed slot, clamped to available cash
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
            paper_trader.buy(strategy_name=strat, ticker=t, qty=qty,
                             fill_price=fill, as_of=as_of,
                             entry_score=decisions[t]["score"],
                             sector=sector_momentum.SECTOR_NAMES.get(t))
            log.info("  BUY %s qty=%.4f @ $%.2f ($%.2f)", t, qty, fill, dollars)
        trades += 1

    if not args.dry_run:
        paper_trader.mark_rebalanced(strat)
    held_after = sorted(set(current) - {p["ticker"] for p in sells} | set(buys))
    log.info("[treatment] rebalance %s: %d trades; held sectors=%s (vetoed->cash=%s)",
             "DRY" if args.dry_run else "done", trades, held_after, vetoes)
    return 0


def cmd_check_invalidation(args) -> int:
    as_of = date.fromisoformat(args.as_of)
    strat = sector_overlay.TREATMENT_STRATEGY
    open_positions = paper_trader.list_open(strat)
    if not open_positions:
        log.info("[sector-overlay] no open positions — nothing to check.")
        return 0
    spread = sector_overlay.HALF_SPREAD_BPS / 10_000.0
    for pos in open_positions:
        dec = sector_overlay.latest_decision_for(pos["ticker"], as_of)
        if dec is None or dec["invalidation_level"] is None:
            continue
        inval = dec["invalidation_level"]
        px = market_data.last_close_on_or_before(pos["ticker"], as_of)[0]
        if px is None:
            log.warning("[sector-overlay] no price for %s at %s — skip stop.",
                        pos["ticker"], as_of)
            continue
        if px <= inval:
            log.warning("[sector-overlay] INVALIDATION HIT: %s close $%.2f <= "
                        "stop $%.2f. Exiting to cash.", pos["ticker"], px, inval)
            if not args.dry_run:
                fill = px * (1.0 - spread)
                realized = paper_trader.sell(position_id=pos["id"], qty=pos["qty"],
                                             fill_price=fill, as_of=as_of,
                                             strategy_name=strat,
                                             reason="invalidation")
                log.warning("[sector-overlay] SOLD %s qty=%.4f @ $%.2f pnl=$%+.2f",
                            pos["ticker"], pos["qty"], fill, realized)
        else:
            log.info("[sector-overlay] %s close $%.2f > stop $%.2f — holding.",
                     pos["ticker"], px, inval)
    return 0


def cmd_init(args) -> int:
    _init()
    log.info("Initialized %s (idempotent).", sector_overlay.TREATMENT_STRATEGY)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_c = sub.add_parser("candidate", help="print candidates + macro prompts")
    p_c.add_argument("--as-of", default=date.today().isoformat())
    p_c.set_defaults(func=cmd_candidate)

    p_d = sub.add_parser("decide", help="log a pre-committed sector decision")
    p_d.add_argument("--as-of", default=date.today().isoformat())
    p_d.add_argument("--ticker", required=True)
    p_d.add_argument("--score", type=float, default=None)
    p_d.add_argument("--verdict", required=True,
                     choices=["HOLD", "VETO", "hold", "veto"])
    p_d.add_argument("--invalidation", type=float, default=None)
    p_d.add_argument("--rationale", default=None)
    p_d.set_defaults(func=cmd_decide)

    p_r = sub.add_parser("rebalance", help="rebalance the treatment sleeve")
    p_r.add_argument("--as-of", default=date.today().isoformat())
    p_r.add_argument("--dry-run", action="store_true")
    p_r.set_defaults(func=cmd_rebalance)

    p_k = sub.add_parser("check-invalidation", help="enforce per-sector stops")
    p_k.add_argument("--as-of", default=date.today().isoformat())
    p_k.add_argument("--dry-run", action="store_true")
    p_k.set_defaults(func=cmd_check_invalidation)

    p_i = sub.add_parser("init", help="create the treatment paper portfolio")
    p_i.set_defaults(func=cmd_init)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
