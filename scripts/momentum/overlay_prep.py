"""One-command GATHER for the monthly LLM-overlay decisions (both sleeves).

Prints, in a single run, everything needed to make the live-web veto/approve
calls for BOTH overlays — the stock overlay (mom_roa_top1) and the macro sector
overlay (sector_top4) — so the monthly "Option A" flow is:

    1. python -m scripts.momentum.overlay_prep        <- this (read-only gather)
    2. Claude runs the live-web research per docs/overlay_decision_runbook.md
    3. log each owed decision via the *_overlay_ops `decide` subcommand
    4. rebalance.bat   (overlay rebalances refuse until decisions are logged)

This script does NOT trade and does NOT log anything. It only reports:
  - the current mechanical candidate(s),
  - whether a NEW decision is actually owed (the stock sleeve only needs one
    when the #1 mom_roa name CHANGES; an unchanged name carries its decision),
  - observable technicals from price_cache (the sim-consistent signals that sit
    alongside the live-web macro read).

Usage:  python -m scripts.momentum.overlay_prep [YYYY-MM-DD]   (default: today)
"""
from __future__ import annotations

import statistics
import sys
from datetime import date

from trading_bot.db import connect
from trading_bot.execution import market_data, paper_trader
from trading_bot.factors import sector_momentum
from trading_bot.strategies import llm_cascade, llm_overlay, sector_overlay


def _closes(conn, ticker: str, n: int = 260) -> list[tuple[str, float]]:
    rows = conn.execute(
        "SELECT key_date, price FROM price_cache WHERE ticker=? AND kind='close' "
        "AND price>0 ORDER BY key_date DESC LIMIT ?", (ticker, n)).fetchall()
    return [(r["key_date"], r["price"]) for r in reversed(rows)]


def _rsi(px: list[float], n: int = 14) -> float | None:
    if len(px) < n + 1:
        return None
    gains = losses = 0.0
    for i in range(-n, 0):
        ch = px[i] - px[i - 1]
        gains += max(ch, 0.0)
        losses += max(-ch, 0.0)
    if losses == 0:
        return 100.0
    rs = (gains / n) / (losses / n)
    return 100 - 100 / (1 + rs)


def _technicals(conn, ticker: str) -> str:
    series = _closes(conn, ticker)
    if len(series) < 60:
        return f"    {ticker}: insufficient cached history"
    px = [p for _, p in series]
    last = px[-1]
    dma50 = statistics.mean(px[-50:])
    dma200 = statistics.mean(px[-200:]) if len(px) >= 200 else statistics.mean(px)
    hi = max(px[-252:]) if len(px) >= 252 else max(px)

    def rb(nd: int) -> float:
        return (last / px[-1 - nd] - 1) * 100 if len(px) > nd else float("nan")

    return (f"    {ticker}: ${last:.2f}  50DMA{'>' if last > dma50 else '<'}"
            f"({dma50:.2f})  %>200DMA {(last / dma200 - 1) * 100:+.1f}%  "
            f"1m {rb(21):+.1f}%  3m {rb(63):+.1f}%  from52wHi "
            f"{(last / hi - 1) * 100:+.1f}%  RSI14 {_rsi(px):.0f}")


def _stock_section(conn, as_of: date) -> None:
    print("\n" + "#" * 72)
    print("# STOCK OVERLAY  (llm_overlay_mom_roa_top1 vs mom_roa_top1 control)")
    print("#" * 72)
    cand = llm_overlay.candidate(as_of)
    if cand is None:
        print("  No candidate at this date (empty universe?).")
        return
    ticker, z = cand
    held = paper_trader.list_open(llm_overlay.CONTROL_STRATEGY)
    held_t = held[0]["ticker"] if held else None
    print(f"  Top mom_roa name : {ticker}  (z={z:+.3f})")
    print(f"  Control holds    : {held_t or 'CASH'}")
    print(_technicals(conn, ticker))

    if ticker == held_t:
        latest = llm_overlay.latest_decision(as_of)
        print("\n  >>> NAME UNCHANGED - no new decision required. The existing "
              "decision carries; its stop is enforced daily by daily.bat.")
        if latest:
            print(f"      last decision: {latest['verdict']} {latest['ticker']} "
                  f"score={latest['score']} inval={latest['invalidation_level']}")
        return
    if llm_overlay.decision_for(as_of) is not None:
        d = llm_overlay.decision_for(as_of)
        print(f"\n  >>> NEW name, but a decision is ALREADY logged for {as_of}: "
              f"{d['verdict']} {d['ticker']}. Nothing owed.")
        return
    print(f"\n  >>> NEW name {ticker} - 1 DECISION OWED. Run the 3 prompts "
          "(see runbook, Stock section):")
    print(f"      1) Equity-analyst deep dive on {ticker} -> score 1-10")
    print(f"      2) {ticker} vs 3-4 closest peers (growth/margins/valuation)")
    print(f"      3) Devil's-advocate long {ticker}; give an exact invalidation price")
    print(f"      Then: python -m scripts.momentum.llm_overlay_ops decide "
          f"--ticker {ticker} --score N --verdict BUY|VETO --invalidation P "
          f"--rationale \"...\"")


def _sector_section(conn, as_of: date) -> None:
    print("\n" + "#" * 72)
    print("# SECTOR OVERLAY  (llm_overlay_sector_top4 vs sector_top4 control)")
    print("#" * 72)
    cands = sector_overlay.candidates(as_of)
    if not cands:
        print("  No sector candidates at this date.")
        return
    decided = sector_overlay.decisions_for(as_of)
    print(f"  Top-{sector_overlay.TOP_N} SPDR sectors by 12-1 momentum:")
    for ticker, score in cands:
        name = sector_momentum.SECTOR_NAMES.get(ticker, ticker)
        dec = decided.get(ticker)
        tag = f"[decided: {dec['verdict']}]" if dec else "[OWED]"
        print(f"\n  {ticker} ({name})  mom={score:+.3f}  {tag}")
        print(_technicals(conn, ticker))
    owed = [t for t, _ in cands if t not in decided]
    print(f"\n  >>> {len(owed)} sector decision(s) owed: {owed or 'none'}")
    if owed:
        print("      Run the 4 macro prompts per owed sector (rates / valuation+"
              "crowding / fundamental trend / bear+invalidation) — see runbook "
              "§Sector. Then per sector:")
        print("      python -m scripts.momentum.sector_overlay_ops decide "
              "--ticker XXX --score N --verdict HOLD|VETO --invalidation P "
              "--rationale \"...\"")


def _cascade_section(conn, as_of: date) -> None:
    """Deeper-ranking view for the always-invested CASCADE sleeves: walk down
    until the stock has 1 BUY and the sector has 4 HOLDs. Decisions are the SAME
    log as the cash overlays (no double-log) — this just shows what's still owed
    deeper than #1 / the top-4 for the cascade to differ from the control."""
    print("\n" + "#" * 72)
    print("# LLM-CASCADE (always-invested 3rd pair) — needs decisions DEEPER")
    print("#   share the cash overlays' decision log; log via the same `decide` CLIs")
    print("#" * 72)

    # ---- stock cascade: walk top-10 until a BUY ----
    print("\n  STOCK cascade (llm_cascade_top1) — walk down until 1 BUY:")
    ranked = llm_cascade.stock_ranking(as_of)
    chosen = None
    for i, (ticker, z) in enumerate(ranked, 1):
        dec = llm_overlay.decision_for_ticker(as_of, ticker)
        verdict = dec["verdict"] if dec else "OWED"
        mark = "  <== first BUY (cascade holds this)" if (verdict == "BUY" and chosen is None) else ""
        if verdict == "BUY" and chosen is None:
            chosen = ticker
        print(f"    #{i:<2} {ticker:6} z={z:+.3f}  [{verdict}]{mark}")
        print(_technicals(conn, ticker))
        if chosen is not None:
            break
    if chosen is None:
        print(f"\n  >>> No BUY logged in the top-{len(ranked)} — cascade FALLS BACK to "
              f"raw #1 ({ranked[0][0] if ranked else '?'}) = same as control. Log "
              "BUY/VETO down the list (llm_overlay_ops decide) until one BUY.")
    else:
        print(f"\n  >>> Cascade stock pick = {chosen}.")

    # ---- sector cascade: walk all sectors until 4 HOLDs ----
    print("\n  SECTOR cascade (llm_cascade_sector4) — walk down until 4 HOLD:")
    sranked = llm_cascade.sector_ranking(as_of)
    decided = sector_overlay.decisions_for(as_of)
    holds: list[str] = []
    for i, (ticker, score) in enumerate(sranked, 1):
        dec = decided.get(ticker)
        verdict = dec["verdict"] if dec else "OWED"
        if verdict == "HOLD" and len(holds) < llm_cascade.SECTOR_SLOTS:
            holds.append(ticker)
        name = sector_momentum.SECTOR_NAMES.get(ticker, ticker)
        print(f"    #{i:<2} {ticker:5} ({name})  mom={score:+.3f}  [{verdict}]")
        if len(holds) == llm_cascade.SECTOR_SLOTS:
            break
    n_owed = llm_cascade.SECTOR_SLOTS - len(holds)
    if n_owed > 0:
        print(f"\n  >>> Only {len(holds)} HOLD so far: {holds}. Need "
              f"{llm_cascade.SECTOR_SLOTS}; evaluate the next sector(s) above until "
              f"{n_owed} more HOLD (else cascade momentum-fills = leaks vetoed names).")
    else:
        print(f"\n  >>> Cascade sector picks = {holds}.")


def main() -> int:
    as_of = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    market_data.preload_caches()
    print("=" * 72)
    print(f"OVERLAY DECISION PREP  (as_of {as_of})")
    print("Rubric: docs/overlay_decision_runbook.md   |   read-only, no trades")
    print("=" * 72)
    with connect() as conn:
        _stock_section(conn, as_of)
        _sector_section(conn, as_of)
        _cascade_section(conn, as_of)
    print("\n" + "=" * 72)
    print("After logging all OWED decisions, run rebalance.bat (or the per-sleeve")
    print("rebalance commands). Both overlay rebalances refuse until decided.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
