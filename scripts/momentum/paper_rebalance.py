"""Paper-trade rebalance for mom_v2: one-shot, today-only.

Usage:
  # First run (creates portfolio with $100K starting cash):
  python -m scripts.momentum.paper_rebalance

  # Subsequent runs (loads existing state, rebalances to current top-50):
  python -m scripts.momentum.paper_rebalance

  # Dry run — print trade list, don't write:
  python -m scripts.momentum.paper_rebalance --dry-run

  # Custom strategy name or starting cash (first run only):
  python -m scripts.momentum.paper_rebalance --strategy mom_v2_paper --starting-cash 100000

Algorithm:
  1. Load eligible universe at as_of (default: today)
  2. Rank by 12-1 momentum, take top-50
  3. Compare to current open paper positions
  4. SELL positions not in target (use today's close fill ± 5bps half-spread)
  5. Spread freed cash equally across NEW buys
  6. Log a per-rebalance summary

Matches mom_v2 frozen spec: top_n=50, monthly, $100K start, 5 bps half-spread,
equal-weight from available cash.
"""
from __future__ import annotations

import argparse
import logging
import math
import sys
from datetime import date

from trading_bot.execution import fractionability, market_data, paper_trader
from trading_bot.factors import (
    momentum, mom_roa_zscore, sector_momentum, residual_momentum, roa, zcombo,
)
from trading_bot.factors.universe import tradeable_universe
from trading_bot.strategies import momentum_v2, mom_roa_6535, residual_roa_6535


def _strategy_config(strategy_name: str):
    """Map paper strategy name -> (rank_fn, universe_fn) tuple.
    rank_fn(tickers, as_of) -> [(ticker, score), ...]
    universe_fn(as_of) -> list[ticker]

    Centralized so adding new sleeves only requires adding a branch here.

    The `_0701` infix marks a 7/1-cohort duplicate of an existing sleeve (same
    rank/universe config, fresh $100k inception 07-01). Strip it so the duplicate
    reuses its base sleeve's config — no per-duplicate branch needed.
    """
    # Anchored strip (audit 2026-07-17, record CG): only the exact `_0701_paper`
    # suffix marks a cohort duplicate. A blind replace("_0701", "") could mangle
    # a future name containing those digits elsewhere (e.g. inside a weight token).
    if strategy_name.endswith("_0701_paper"):
        base = strategy_name[:-len("_0701_paper")] + "_paper"
    else:
        base = strategy_name
    if base in ("mom_v1_paper", "mom_v2_paper"):
        return momentum.rank_universe, tradeable_universe
    if base == "mom_roa_6535_paper":
        return (mom_roa_zscore.make_rank_fn(mom_roa_6535.W_MOM, mom_roa_6535.W_ROA),
                tradeable_universe)
    if base == "residual_roa_6535_paper":
        return (zcombo.make_rank_fn([
                    (residual_momentum.residual_momentum_score, residual_roa_6535.W_RESID),
                    (roa.roa_score, residual_roa_6535.W_ROA)]),
                tradeable_universe)
    if base.startswith("sector_top4"):
        # sector strategy uses 11 SPDR ETFs, ignores tradeable_universe filter.
        # Prefix match covers both sector_top4_paper (07-01 LLM-experiment control)
        # and sector_top4_full_paper (full 05-01 systematic control) — identical config.
        return (sector_momentum.rank_universe,
                lambda as_of: list(sector_momentum.SECTOR_UNIVERSE))
    if base.startswith("residual_w") and base.endswith("_paper"):
        # Residual-weight-sweep experiment family (records BW, CD): residual_w<MM><RR>
        # where MM = residual-momentum weight %, RR = ROA weight % (e.g. w8020 = 80/20).
        # Identical top-50 config to residual_roa_6535_paper; ONLY the resid/ROA blend
        # weight varies (Appendix BV found a broad w80-90 holdout plateau in-backtest;
        # this races it live). An optional cadence marker follows the digits — monthly
        # (none, BW), _wk (weekly) or _2wk (biweekly) (CD): the RANK FUNCTION is
        # cadence-independent, so strip the marker and read the same 4 weight digits;
        # only the rebalance SCHEDULE differs (which task rebalances the sleeve).
        digits = base[len("residual_w"):-len("_paper")]
        for _marker in ("_2wk", "_wk"):
            if digits.endswith(_marker):
                digits = digits[:-len(_marker)]
                break
        if len(digits) == 4 and digits.isdigit():
            mm, rr = int(digits[:2]), int(digits[2:])
            # Guard (record CG): the ladder is defined as complementary blends;
            # a name whose weights don't sum to 100 is a typo, not a strategy.
            if mm + rr != 100:
                raise ValueError(f"{strategy_name}: weights {mm}/{rr} do not sum "
                                 f"to 100 — refusing to trade a malformed blend.")
            w_resid, w_roa = mm / 100.0, rr / 100.0
            return (zcombo.make_rank_fn([
                        (residual_momentum.residual_momentum_score, w_resid),
                        (roa.roa_score, w_roa)]),
                    tradeable_universe)
    raise ValueError(f"Unknown strategy: {strategy_name}. "
                     f"Add a branch in _strategy_config().")

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("paper_rebalance")


def _alpaca_client_or_none():
    """First configured Alpaca account's client, or None if no keys. Lazy import
    so the core sim / backtests never hard-depend on the Alpaca integration."""
    try:
        from trading_bot.execution.alpaca_accounts import configured_accounts
        accts = configured_accounts()
        return accts[0].client() if accts else None
    except Exception:
        return None


def rebalance(*, as_of: date, strategy_name: str, starting_cash: float,
              top_n: int, half_spread_bps: float, dry_run: bool,
              broker_realistic: bool = False) -> int:
    """Returns the number of position changes (sells + buys).

    broker_realistic (default False, so backtests/frozen specs are unchanged):
    buy WHOLE shares of non-fractionable names and drop untradable/inactive ones,
    matching what the Alpaca mirror can actually execute (see fractionability.py)."""
    paper_trader.init(strategy_name=strategy_name, starting_cash=starting_cash)
    market_data.preload_caches()
    pf = paper_trader.get(strategy_name)

    log.info("Paper portfolio: strategy=%s starting=$%.0f cash=$%.2f open=%d",
             pf.strategy_name, pf.starting_cash, pf.cash, pf.n_open_positions)

    # 1. Build universe + rank (universe selection is strategy-specific)
    rank_fn, universe_fn = _strategy_config(strategy_name)
    universe = universe_fn(as_of)
    if not universe:
        log.error("Empty universe at %s for %s. Aborting.", as_of, strategy_name)
        return 0
    # Stale-data guard (added 2026-05-30 per audit C2): if universe is
    # suspiciously small (e.g., only ETFs survive freshness filter), the
    # script would otherwise liquidate all stock holdings into whatever's
    # left. Sector strategy's universe is naturally 11, so use its exact
    # size; everything else needs at least 2x top_n with a floor of 200.
    min_universe = 11 if strategy_name.startswith("sector_top4") else max(2 * top_n, 200)
    if len(universe) < min_universe:
        log.error("Universe size %d < required %d for %s at %s. "
                  "Likely stale price_cache. ABORTING (would otherwise "
                  "liquidate holdings catastrophically).",
                  len(universe), min_universe, strategy_name, as_of)
        return 0
    log.info("Universe at %s for %s: %d eligible tickers",
             as_of, strategy_name, len(universe))

    scored = rank_fn(universe, as_of)
    target_list = scored[:top_n]
    target_set = {t for t, _ in target_list}
    target_score = {t: s for t, s in target_list}
    log.info("Ranked top-%d momentum (score range: %.3f to %.3f)",
             len(target_list), target_list[0][1] if target_list else 0,
             target_list[-1][1] if target_list else 0)

    # 2. Diff vs current open positions
    current = paper_trader.list_open(strategy_name)
    current_by_ticker = {p["ticker"]: p for p in current}
    sells = [p for p in current if p["ticker"] not in target_set]
    buys  = [t for t in target_set if t not in current_by_ticker]
    keeps = [p for p in current if p["ticker"] in target_set]

    log.info("Rebalance plan: sells=%d  buys=%d  keeps=%d  (target=%d)",
             len(sells), len(buys), len(keeps), len(target_set))

    if dry_run:
        print("\n=== DRY RUN — no DB writes ===")
        print(f"\nSELLS ({len(sells)}):")
        for p in sells:
            px = market_data.last_close_on_or_before(p["ticker"], as_of)[0]
            mtm = px * p["qty"] if px else 0
            pnl = mtm - p["entry_value"]
            print(f"  {p['ticker']:6s}  qty={p['qty']:.2f}  entry=${p['entry_price']:.2f}  "
                  f"now=${px or 0:.2f}  pnl=${pnl:+.2f}")
        print(f"\nBUYS ({len(buys)}):")
        for t in buys[:20]:
            px = market_data.last_close_on_or_before(t, as_of)[0]
            print(f"  {t:6s}  px=${px or 0:.2f}  mom_score={target_score.get(t, 0):+.4f}")
        if len(buys) > 20:
            print(f"  ... and {len(buys) - 20} more")
        return 0

    # 3. Execute sells (frees cash)
    spread = half_spread_bps / 10_000.0
    n_sells_done = 0
    for p in sells:
        px = market_data.last_close_on_or_before(p["ticker"], as_of)[0]
        if px is None or px <= 0:
            log.warning("  Skip sell %s: no price at %s", p["ticker"], as_of)
            continue
        fill = px * (1.0 - spread)
        realized = paper_trader.sell(
            position_id=p["id"], qty=p["qty"], fill_price=fill, as_of=as_of,
            strategy_name=strategy_name)
        n_sells_done += 1
        log.info("  SELL  %s  qty=%.2f  fill=$%.2f  pnl=$%+.2f",
                 p["ticker"], p["qty"], fill, realized)

    # 4. Execute buys — equal dollar share of available cash
    n_buys_done = 0
    # Broker realism: whole-share non-fractionable names, drop untradable ones.
    nonfrac: set[str] = set()
    skipped: dict[str, str] = {}
    if buys and broker_realistic:
        client = _alpaca_client_or_none()
        if client is not None:
            try:
                fractionability.refresh(set(buys), client)
            finally:
                client.close()
        nonfrac, untradable = fractionability.classify(set(buys))
        for t in list(buys):
            if t in untradable:
                skipped[t] = "untradable/inactive on Alpaca"
                buys.remove(t)
    if buys:
        pf_after_sells = paper_trader.get(strategy_name)
        # 0.999 buffer so rounding from spread doesn't push cash <0
        avail = max(0.0, pf_after_sells.cash * 0.999)
        dollar_per = avail / len(buys) if buys else 0
        log.info("Buying %d new positions, ~$%.2f each (from avail $%.2f)",
                 len(buys), dollar_per, pf_after_sells.cash)
        for t in buys:
            px = market_data.last_close_on_or_before(t, as_of)[0]
            if px is None or px <= 0:
                log.warning("  Skip buy %s: no price at %s", t, as_of)
                continue
            fill = px * (1.0 + spread)
            qty = dollar_per / fill
            if t in nonfrac:  # whole shares only on Alpaca
                qty = float(math.floor(qty))
                if qty < 1:
                    skipped[t] = "non-fractionable, <1 whole share at budget"
                    continue
            if qty <= 0:
                log.warning("  Skip buy %s: qty=0 (dollar_per=%.2f / fill=%.2f)",
                            t, dollar_per, fill)
                continue
            sector = (sector_momentum.SECTOR_NAMES.get(t)
                      if strategy_name.startswith("sector_top4")
                      else market_data.sector(t))
            paper_trader.buy(
                strategy_name=strategy_name, ticker=t,
                qty=qty, fill_price=fill, as_of=as_of,
                entry_score=target_score.get(t), sector=sector)
            n_buys_done += 1
            log.info("  BUY   %s  qty=%.2f  fill=$%.2f  sector=%s",
                     t, qty, fill, sector or "?")
    if skipped:
        log.info("  Broker-realistic: %d name(s) NOT bought: %s", len(skipped),
                 ", ".join(f"{t} ({r})" for t, r in skipped.items()))

    paper_trader.mark_rebalanced(strategy_name)

    # 5. Final summary
    pf_final = paper_trader.get(strategy_name)
    log.info("=" * 60)
    log.info("REBALANCE COMPLETE  %s", as_of)
    log.info("  Sells done:    %d", n_sells_done)
    log.info("  Buys done:     %d", n_buys_done)
    log.info("  Cash:          $%.2f", pf_final.cash)
    log.info("  Open value:    $%.2f", pf_final.open_positions_value)
    log.info("  Total entry$:  $%.2f", pf_final.total_entry_value)
    log.info("  Open count:    %d  (target %d)",
             pf_final.n_open_positions, top_n)
    log.info("=" * 60)
    return n_sells_done + n_buys_done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=date.today().isoformat(),
                    help="Rebalance date (default: today)")
    ap.add_argument("--strategy", default=paper_trader.DEFAULT_STRATEGY)
    ap.add_argument("--starting-cash", type=float,
                    default=momentum_v2.STARTING_CASH,
                    help="Only used on first run (idempotent init)")
    ap.add_argument("--top-n", type=int, default=momentum_v2.TOP_N)
    ap.add_argument("--half-spread-bps", type=float,
                    default=momentum_v2.HALF_SPREAD_BPS)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--broker-realistic", action="store_true",
                    help="Whole-share non-fractionable names + drop untradable "
                         "ones, matching what the Alpaca paper mirror can execute.")
    args = ap.parse_args()

    rebalance(
        as_of=date.fromisoformat(args.as_of),
        strategy_name=args.strategy,
        starting_cash=args.starting_cash,
        top_n=args.top_n,
        half_spread_bps=args.half_spread_bps,
        dry_run=args.dry_run,
        broker_realistic=args.broker_realistic,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
