"""Operations CLI for the LLM-overlay experiment (two single-name sleeves).

Subcommands
-----------
  candidate            Print today's mechanical candidate + the 3 analyst prompts.
  decide               Log a pre-committed LLM decision (BUY/VETO + invalidation).
  rebalance --mode M   Rebalance a sleeve. M = control | overlay.
  check-invalidation   Exit the overlay to cash if its stop level is breached.
  init                 Idempotently create both paper portfolios.

Typical monthly flow
--------------------
  python -m scripts.momentum.llm_overlay_ops candidate
  # (run the 3 prompts against current data, then:)
  python -m scripts.momentum.llm_overlay_ops decide --ticker NVDA --score 7 \
      --verdict BUY --invalidation 165.00 --rationale "AI capex still accelerating"
  python -m scripts.momentum.llm_overlay_ops rebalance --mode control
  python -m scripts.momentum.llm_overlay_ops rebalance --mode overlay

Daily (folded into daily.bat)
-----------------------------
  python -m scripts.momentum.llm_overlay_ops check-invalidation

See trading_bot/strategies/llm_overlay.py for the full experiment design and
the pre-committed kill switch.
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date

from trading_bot.execution import market_data, paper_trader
from trading_bot.strategies import llm_overlay

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("llm_overlay_ops")


def _init_both() -> None:
    paper_trader.init(strategy_name=llm_overlay.CONTROL_STRATEGY,
                      starting_cash=llm_overlay.STARTING_CASH)
    paper_trader.init(strategy_name=llm_overlay.OVERLAY_STRATEGY,
                      starting_cash=llm_overlay.STARTING_CASH)


def _set_single_position(*, strategy_name: str, target: str | None,
                         entry_score: float | None, as_of: date,
                         dry_run: bool, reason_open: str = "rebalance") -> int:
    """Move a single-name sleeve to hold exactly `target` (or cash if None).
    Returns number of trades executed. Reuses paper_trader for all bookkeeping."""
    market_data.preload_caches()
    open_positions = paper_trader.list_open(strategy_name)
    cur = open_positions[0] if open_positions else None
    cur_ticker = cur["ticker"] if cur else None

    if cur_ticker == target:
        log.info("[%s] already holds %s — no change.", strategy_name,
                 target or "CASH")
        if not dry_run:
            paper_trader.mark_rebalanced(strategy_name)
        return 0

    spread = llm_overlay.HALF_SPREAD_BPS / 10_000.0
    trades = 0

    # 1. Sell current holding (if any)
    if cur is not None:
        px = market_data.last_close_on_or_before(cur["ticker"], as_of)[0]
        if px is None or px <= 0:
            log.warning("[%s] no price for %s at %s — cannot sell; aborting.",
                        strategy_name, cur["ticker"], as_of)
            return 0
        fill = px * (1.0 - spread)
        if dry_run:
            log.info("[%s] DRY: SELL %s qty=%.4f @ ~$%.2f",
                     strategy_name, cur["ticker"], cur["qty"], fill)
        else:
            realized = paper_trader.sell(
                position_id=cur["id"], qty=cur["qty"], fill_price=fill,
                as_of=as_of, strategy_name=strategy_name)
            log.info("[%s] SELL %s qty=%.4f @ $%.2f pnl=$%+.2f",
                     strategy_name, cur["ticker"], cur["qty"], fill, realized)
        trades += 1

    # 2. Buy target (if any). VETO/cash target => stay in cash.
    if target is not None:
        px = market_data.last_close_on_or_before(target, as_of)[0]
        if px is None or px <= 0:
            log.warning("[%s] no price for target %s at %s — staying in cash.",
                        strategy_name, target, as_of)
        else:
            fill = px * (1.0 + spread)
            pf = paper_trader.get(strategy_name)
            avail = max(0.0, pf.cash * 0.999)   # buffer vs spread rounding
            qty = avail / fill
            if dry_run:
                log.info("[%s] DRY: BUY %s qty=%.4f @ ~$%.2f (avail $%.2f)",
                         strategy_name, target, qty, fill, avail)
            elif qty > 0:
                sector = market_data.sector(target)
                paper_trader.buy(
                    strategy_name=strategy_name, ticker=target, qty=qty,
                    fill_price=fill, as_of=as_of, entry_score=entry_score,
                    sector=sector)
                log.info("[%s] BUY %s qty=%.4f @ $%.2f sector=%s",
                         strategy_name, target, qty, fill, sector or "?")
            trades += 1

    if not dry_run:
        paper_trader.mark_rebalanced(strategy_name)
    return trades


# ---------------- subcommands ----------------

def cmd_candidate(args) -> int:
    as_of = date.fromisoformat(args.as_of)
    market_data.preload_caches()
    cand = llm_overlay.candidate(as_of)
    if cand is None:
        log.error("No candidate at %s (empty universe?).", as_of)
        return 1
    ticker, z = cand
    px = market_data.last_close_on_or_before(ticker, as_of)[0]
    print("=" * 70)
    print(f"LLM-OVERLAY CANDIDATE  (as_of {as_of})")
    print("=" * 70)
    print(f"  Ticker:   {ticker}")
    print(f"  Z-score:  {z:+.3f}  (top of mom_roa_6535 ranking)")
    print(f"  Close:    ${px:.2f}" if px else "  Close:    (no price)")
    print("\nRun these 3 prompts against CURRENT data, then `decide`:\n")
    print(f"  1) Equity-analyst deep dive on {ticker}: business model, financials")
    print(f"     (growth, margins, debt, cash flow), forward outlook, valuation vs")
    print(f"     its own history, catalysts + risks (6-18mo). End: score 1-10.")
    print(f"  2) Compare {ticker} to its 3-4 closest competitors on growth, margins,")
    print(f"     valuation multiples. Cheap / fair / expensive? Value or trap? What")
    print(f"     has to be true for today's price to make sense?")
    print(f"  3) Devil's advocate on a LONG in {ticker}: hardest bear case, what's")
    print(f"     priced in, what I'm ignoring. Give an exact invalidation price.")
    print("\nThen:")
    print(f"  python -m scripts.momentum.llm_overlay_ops decide --ticker {ticker} \\")
    print(f"      --score N --verdict BUY|VETO --invalidation PRICE --rationale \"...\"")
    print("=" * 70)
    return 0


def cmd_decide(args) -> int:
    decision_date = date.fromisoformat(args.as_of)
    llm_overlay.record_decision(
        decision_date=decision_date, ticker=args.ticker.upper(),
        score=args.score, verdict=args.verdict,
        invalidation_level=args.invalidation, rationale=args.rationale)
    log.info("Logged decision for %s: %s %s score=%s invalidation=%s",
             decision_date, args.verdict.upper(), args.ticker.upper(),
             args.score, args.invalidation)
    return 0


def cmd_rebalance(args) -> int:
    as_of = date.fromisoformat(args.as_of)
    _init_both()

    if args.mode == "control":
        cand = llm_overlay.candidate(as_of)
        if cand is None:
            log.error("No candidate at %s — control rebalance aborted.", as_of)
            return 1
        ticker, z = cand
        log.info("[control] candidate=%s z=%+.3f", ticker, z)
        # Detect a NEW underlying buy (name change). Per experiment rule, every
        # name the underlying buys must get the 3-prompt LLM evaluation before
        # the treatment acts — flag it loudly so the overlay never silently
        # stalls in cash on an un-evaluated name.
        held = paper_trader.list_open(llm_overlay.CONTROL_STRATEGY)
        held_ticker = held[0]["ticker"] if held else None
        if ticker != held_ticker and llm_overlay.decision_for(as_of) is None:
            log.warning("=" * 60)
            log.warning("NEW UNDERLYING BUY: %s (was %s). LLM EVALUATION OWED.",
                        ticker, held_ticker or "CASH")
            log.warning("Run: candidate -> 3 prompts -> decide --ticker %s "
                        "before `rebalance --mode overlay`.", ticker)
            log.warning("=" * 60)
        _set_single_position(
            strategy_name=llm_overlay.CONTROL_STRATEGY, target=ticker,
            entry_score=z, as_of=as_of, dry_run=args.dry_run)
        return 0

    # overlay mode: act on the LLM decision for THIS rebalance's #1 candidate.
    # Look it up by (date, candidate ticker) — not a LIMIT-1 row — so the
    # cascade sleeve logging several names on the same date can't make us grab
    # the wrong decision.
    cand = llm_overlay.candidate(as_of)
    if cand is None:
        log.error("[overlay] no candidate at %s — refusing to trade.", as_of)
        return 1
    cand_t = cand[0]
    decision = llm_overlay.decision_for_ticker(as_of, cand_t)
    if decision is None:
        log.error("[overlay] no decision logged for %s (#1) on %s — run the 3 "
                  "prompts (`candidate`) then `decide --ticker %s ...` first. "
                  "Refusing to trade (won't silently become the control).",
                  cand_t, as_of, cand_t)
        return 1
    if decision["verdict"] == "BUY":
        target = decision["ticker"]
        log.info("[overlay] decision=BUY %s score=%s invalidation=%s",
                 target, decision["score"], decision["invalidation_level"])
    else:
        target = None
        log.info("[overlay] decision=VETO %s — moving to cash.",
                 decision["ticker"])
    _set_single_position(
        strategy_name=llm_overlay.OVERLAY_STRATEGY, target=target,
        entry_score=decision["score"], as_of=as_of, dry_run=args.dry_run)
    return 0


def cmd_check_invalidation(args) -> int:
    as_of = date.fromisoformat(args.as_of)
    open_positions = paper_trader.list_open(llm_overlay.OVERLAY_STRATEGY)
    if not open_positions:
        log.info("[overlay] no open position — nothing to check.")
        return 0
    decision = llm_overlay.latest_decision(as_of)
    if decision is None or decision["invalidation_level"] is None:
        log.info("[overlay] no active invalidation level — nothing to check.")
        return 0
    inval = decision["invalidation_level"]
    pos = open_positions[0]
    px = market_data.last_close_on_or_before(pos["ticker"], as_of)[0]
    if px is None:
        log.warning("[overlay] no price for %s at %s — cannot check stop.",
                    pos["ticker"], as_of)
        return 0
    if px <= inval:
        log.warning("[overlay] INVALIDATION HIT: %s close $%.2f <= stop $%.2f. "
                    "Exiting to cash.", pos["ticker"], px, inval)
        if not args.dry_run:
            spread = llm_overlay.HALF_SPREAD_BPS / 10_000.0
            fill = px * (1.0 - spread)
            realized = paper_trader.sell(
                position_id=pos["id"], qty=pos["qty"], fill_price=fill,
                as_of=as_of, strategy_name=llm_overlay.OVERLAY_STRATEGY,
                reason="invalidation")
            log.warning("[overlay] SOLD %s qty=%.4f @ $%.2f pnl=$%+.2f (stop)",
                        pos["ticker"], pos["qty"], fill, realized)
    else:
        log.info("[overlay] %s close $%.2f > stop $%.2f — holding.",
                 pos["ticker"], px, inval)
    return 0


def cmd_init(args) -> int:
    _init_both()
    log.info("Initialized %s and %s (idempotent).",
             llm_overlay.CONTROL_STRATEGY, llm_overlay.OVERLAY_STRATEGY)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_cand = sub.add_parser("candidate", help="print candidate + 3 prompts")
    p_cand.add_argument("--as-of", default=date.today().isoformat())
    p_cand.set_defaults(func=cmd_candidate)

    p_dec = sub.add_parser("decide", help="log a pre-committed LLM decision")
    p_dec.add_argument("--as-of", default=date.today().isoformat())
    p_dec.add_argument("--ticker", required=True)
    p_dec.add_argument("--score", type=float, default=None)
    p_dec.add_argument("--verdict", required=True, choices=["BUY", "VETO", "buy", "veto"])
    p_dec.add_argument("--invalidation", type=float, default=None,
                       help="close at/below which the long thesis breaks")
    p_dec.add_argument("--rationale", default=None)
    p_dec.set_defaults(func=cmd_decide)

    p_reb = sub.add_parser("rebalance", help="rebalance a sleeve")
    p_reb.add_argument("--mode", required=True, choices=["control", "overlay"])
    p_reb.add_argument("--as-of", default=date.today().isoformat())
    p_reb.add_argument("--dry-run", action="store_true")
    p_reb.set_defaults(func=cmd_rebalance)

    p_chk = sub.add_parser("check-invalidation", help="enforce overlay stop")
    p_chk.add_argument("--as-of", default=date.today().isoformat())
    p_chk.add_argument("--dry-run", action="store_true")
    p_chk.set_defaults(func=cmd_check_invalidation)

    p_ini = sub.add_parser("init", help="create both paper portfolios")
    p_ini.set_defaults(func=cmd_init)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
