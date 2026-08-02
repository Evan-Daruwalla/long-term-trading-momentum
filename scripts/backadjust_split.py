"""Back-adjust cached history for a stock split, and repair un-adjusted OPEN positions.

WHY THIS EXISTS (audit 2026-07-28, record CH). price_cache is built forward-only:
daily_price_refresh appends today's close and never revisits history. yfinance
serves post-split prices from the split date onward, so a split silently leaves a
10x cliff inside the cached series -- violating the project's own stated
convention that closes are SPLIT-ADJUSTED (dividend-unadjusted).

That cliff has now caused the same bug twice:
  * 2026-06-12 (Appendix X) -- KLAC 10:1 -- repaired the affected SLEEVES.
  * 2026-07-17 -- the 3-cadence ladder was replay-seeded backdated to 05-01, re-read
    the still-unadjusted cache, and reproduced it verbatim in 48 new sleeves
    (-$83,180.81 phantom loss).
Both earlier fixes repaired POSITIONS. Neither repaired the CACHE, which is why it
came back. This script fixes the cache.

WHAT IT DOES, for ticker T with ratio N effective on date D (first post-split close):
  1. price_cache rows with key_date < D:
       price-like kinds (close, next_open, next_open_range)   -> price / N
       volume-like kinds (volume, next_open_vol)              -> price * N
       scale-invariant kinds (atr_pct_20 percent, above_ma_50 boolean) -> untouched
     Adjusting price AND volume together keeps historical DOLLAR volume invariant,
     which matters: adjusting price alone would cut dollar volume N-fold and could
     silently change universe eligibility inside the frozen-test windows.
  2. OPEN paper_positions entered before D at an un-adjusted price:
       qty * N, entry_price / N, entry_value PRESERVED.
     Preserving entry_value is the cost-basis invariant from Appendix X -- it is what
     keeps the cash reconciliation at $0.0000.
  3. ONLY with --include-closed (PRD M7.3, record CK/CL): CLOSED positions entered
     before D at an un-adjusted price AND exited on/after D:
       qty * N, entry_price / N, entry_value PRESERVED (same as open), plus
       exit_value * N, realized_pnl = exit_value_new - entry_value, and the sleeve's
       paper_portfolio.cash corrected by SUM(exit_value_new - exit_value_old).
     exit_price is NOT touched -- an exit on/after D was already priced post-split and
     is correct; it is the SHARE COUNT that was wrong, so the exit PROCEEDS were N-fold
     understated. Positions that exited BEFORE D are skipped: they entered and exited on
     the same un-adjusted scale, so their P&L is already right (KLAC: 2 rows, +$276.56).

WHAT IT DELIBERATELY DOES NOT DO:
  * It does not touch paper_nav -- EVER, including under --include-closed. Historical
    NAV rows are sacred under CLAUDE.md, and record CK proved they are not even
    reproducible (daily_price_refresh rewrites the last 30 days of price_cache nightly
    with INSERT OR REPLACE, so a stored NAV row is a snapshot of a mutated input).
    After a repair the affected sleeves' LATEST NAV row is stale by the cash correction;
    re-marking that one day is a separate, explicit step for the operator.
  * Without --include-closed it does not touch CLOSED positions at all (the pre-M7.3
    behaviour, unchanged). Consequence, if you leave the flag off: sleeves that already
    CLOSED an un-adjusted position keep that phantom realized P&L in their cash.

Ratios are supplied by the operator, not inferred: yfinance's splits_json was empty
for KLAC, and inferring N from the price cliff is unreliable because the stock also
moves on the split date (KLAC's raw cliff is 9.79x for a true 10:1 split).

Usage:
  python -m scripts.backadjust_split --ticker KLAC --ratio 10 --effective 2026-05-13
  python -m scripts.backadjust_split --ticker KLAC --ratio 10 --effective 2026-05-13 --execute
  ... --include-closed   # ALSO repair closed rows + sleeve cash (M7.3)
  ... --db <path>   # run against a COPY first (project rule: never test write paths live)
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("backadjust_split")

PRICE_KINDS = ("close", "next_open", "next_open_range")
VOLUME_KINDS = ("volume", "next_open_vol")
# atr_pct_20 is a percentage and above_ma_50 a boolean: both are scale-invariant.
UNTOUCHED_KINDS = ("atr_pct_20", "above_ma_50", "splits_json", "dividends_json",
                   "split_ratio", "dividends_total")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--ratio", required=True, type=float,
                    help="Split ratio N (10 for a 10:1 split).")
    ap.add_argument("--effective", required=True,
                    help="ISO date of the FIRST post-split close.")
    ap.add_argument("--db", default=None, help="DB path (default: the live DB).")
    ap.add_argument("--execute", action="store_true", help="Apply (default: dry run).")
    ap.add_argument("--include-closed", action="store_true",
                    help="ALSO repair CLOSED positions that exited on/after --effective "
                         "(exit_value * N, realized_pnl restated) and correct each "
                         "sleeve's paper_portfolio.cash. Opt-in: PRD M7.3.")
    args = ap.parse_args()

    if args.ratio <= 0:
        raise SystemExit("--ratio must be positive")

    if args.db:
        db_path = Path(args.db)
    else:
        import trading_bot.db as _db
        db_path = _db.DB_PATH

    t, n, eff = args.ticker, args.ratio, args.effective
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=30000")

    # --- survey ------------------------------------------------------------
    log.info("DB: %s", db_path)
    log.info("%s: ratio %.4f effective %s (adjusting key_date < %s)", t, n, eff, eff)

    rows = conn.execute(
        "SELECT kind, COUNT(*) c FROM price_cache WHERE ticker=? AND key_date < ? "
        "GROUP BY kind ORDER BY kind", (t, eff)).fetchall()
    if not rows:
        log.warning("%s: no cached rows before %s; nothing to do.", t, eff)
        return 0

    n_price = n_vol = 0
    for r in rows:
        k, c = r["kind"], r["c"]
        if k in PRICE_KINDS:
            log.info("  %-18s %6d rows -> price / %.4f", k, c, n)
            n_price += c
        elif k in VOLUME_KINDS:
            log.info("  %-18s %6d rows -> price * %.4f", k, c, n)
            n_vol += c
        else:
            tag = "scale-invariant" if k in UNTOUCHED_KINDS else "UNKNOWN KIND"
            log.info("  %-18s %6d rows -> untouched (%s)", k, c, tag)

    pos = conn.execute(
        "SELECT id, strategy_name, qty, entry_price, entry_value FROM paper_positions "
        "WHERE ticker=? AND status='open' AND entry_date < ?", (t, eff)).fetchall()
    # Only rows still carrying a pre-split basis need repair. A position already
    # adjusted (or entered post-split) sits near the post-split price.
    cutoff = conn.execute(
        "SELECT price FROM price_cache WHERE ticker=? AND kind='close' AND key_date>=? "
        "ORDER BY key_date LIMIT 1", (t, eff)).fetchone()
    if cutoff is None:
        log.error("%s: no post-split close found at/after %s; refusing to guess.", t, eff)
        return 1
    threshold = cutoff["price"] * (n ** 0.5)      # geometric midpoint, order-of-magnitude test
    stale = [p for p in pos if p["entry_price"] > threshold]
    log.info("open positions before %s: %d total, %d still un-adjusted "
             "(entry_price > %.2f)", eff, len(pos), len(stale), threshold)
    for p in stale[:3]:
        log.info("    %-28s qty %.6f -> %.6f | px %.4f -> %.4f | value %.2f (held)",
                 p["strategy_name"], p["qty"], p["qty"] * n,
                 p["entry_price"], p["entry_price"] / n, p["entry_value"])
    if len(stale) > 3:
        log.info("    ... and %d more", len(stale) - 3)

    # --- closed positions (M7.3, opt-in) ------------------------------------
    # Same staleness self-guard as the open path (entry_price > threshold), plus
    # exit_date >= eff. A position that exited BEFORE eff entered and exited on the
    # same un-adjusted scale, so its realized P&L is already correct -- repairing it
    # would CREATE an error.
    closed: list = []
    cash_delta: dict[str, float] = {}
    if args.include_closed:
        closed = conn.execute(
            "SELECT id, strategy_name, qty, entry_price, entry_value, exit_price, "
            "       exit_value, exit_date, realized_pnl "
            "FROM paper_positions WHERE ticker=? AND status='closed' AND entry_date < ? "
            "AND exit_date >= ? AND entry_price > ? ORDER BY exit_date, strategy_name",
            (t, eff, eff, threshold)).fetchall()
        skipped = conn.execute(
            "SELECT COUNT(*) c, COALESCE(SUM(realized_pnl),0) p FROM paper_positions "
            "WHERE ticker=? AND status='closed' AND entry_date < ? AND exit_date < ? "
            "AND entry_price > ?", (t, eff, eff, threshold)).fetchone()
        for p in closed:
            cash_delta[p["strategy_name"]] = (cash_delta.get(p["strategy_name"], 0.0)
                                              + p["exit_value"] * n - p["exit_value"])
        old_pnl = sum(p["realized_pnl"] for p in closed)
        new_pnl = sum(p["exit_value"] * n - p["entry_value"] for p in closed)
        log.info("closed positions entered before %s and exited on/after it: %d "
                 "across %d sleeve(s)", eff, len(closed), len(cash_delta))
        log.info("  SKIPPED (exited before %s, already correct): %d row(s), "
                 "realized_pnl $%+.2f", eff, skipped["c"], skipped["p"])
        for p in closed[:3]:
            log.info("    %-28s exit %s | xv %.2f -> %.2f | pnl %+.2f -> %+.2f",
                     p["strategy_name"], p["exit_date"], p["exit_value"],
                     p["exit_value"] * n, p["realized_pnl"],
                     p["exit_value"] * n - p["entry_value"])
        if len(closed) > 3:
            log.info("    ... and %d more", len(closed) - 3)
        log.info("  realized_pnl total: $%+.2f -> $%+.2f | cash correction $%+.2f",
                 old_pnl, new_pnl, sum(cash_delta.values()))

    # --- idempotency guard -------------------------------------------------
    # The position repair is self-guarding (it only touches rows still above the
    # price threshold), but the cache UPDATE is not: a second --execute would
    # divide history by N again and silently corrupt it. Refuse unless the split
    # cliff is actually still present. A correctly-adjusted series shows a normal
    # daily move here (KLAC: 0.979), an un-adjusted one shows ~N (KLAC: 9.79).
    last_pre = conn.execute(
        "SELECT key_date, price FROM price_cache WHERE ticker=? AND kind='close' "
        "AND key_date < ? AND price IS NOT NULL ORDER BY key_date DESC LIMIT 1",
        (t, eff)).fetchone()
    if last_pre is None:
        log.error("%s: no pre-split close before %s; nothing to adjust.", t, eff)
        conn.close()
        return 1
    cliff = last_pre["price"] / cutoff["price"]
    adjust_cache = (n / 2.0 <= cliff <= n * 2.0)
    if not adjust_cache:
        # The guard exists to stop a SECOND --execute from dividing history by N again.
        # It protects the cache UPDATE only -- the position repairs are independently
        # self-guarding (they touch nothing at/below `threshold`). Before M7.3 the whole
        # run aborted here, which would have made the closed-row repair impossible on a
        # cache CJ had already fixed. Default path keeps the hard refusal.
        if not args.include_closed:
            log.error("%s: expected an un-adjusted cliff near %.4gx across %s, found %.4gx "
                      "(%s $%.4f -> $%.4f). History looks ALREADY ADJUSTED (or the ratio/date "
                      "is wrong). Refusing to touch it.", t, n, eff, cliff,
                      last_pre["key_date"], last_pre["price"], cutoff["price"])
            conn.close()
            return 1
        log.warning("cliff check: %.4gx across %s -- price_cache is ALREADY back-adjusted. "
                    "SKIPPING the cache UPDATE; repairing POSITIONS only (--include-closed).",
                    cliff, eff)
    else:
        log.info("cliff check: %.4gx across %s -- consistent with an un-adjusted %.4g:1 split",
                 cliff, eff, n)

    if not args.execute:
        log.info("DRY RUN -- %d price rows, %d volume rows (cache %s), %d open + %d closed "
                 "position(s), %d sleeve cash correction(s) would change. Re-run with --execute.",
                 n_price if adjust_cache else 0, n_vol if adjust_cache else 0,
                 "WILL be adjusted" if adjust_cache else "already adjusted, SKIPPED",
                 len(stale), len(closed), len(cash_delta))
        conn.close()
        return 0

    # --- apply -------------------------------------------------------------
    with conn:
        if adjust_cache:
            conn.execute(
                f"UPDATE price_cache SET price = price / ? WHERE ticker=? AND key_date < ? "
                f"AND price IS NOT NULL AND kind IN ({','.join('?' * len(PRICE_KINDS))})",
                (n, t, eff, *PRICE_KINDS))
            conn.execute(
                f"UPDATE price_cache SET price = price * ? WHERE ticker=? AND key_date < ? "
                f"AND price IS NOT NULL AND kind IN ({','.join('?' * len(VOLUME_KINDS))})",
                (n, t, eff, *VOLUME_KINDS))
        for p in stale:
            conn.execute(
                "UPDATE paper_positions SET qty=?, entry_price=? WHERE id=?",
                (p["qty"] * n, p["entry_price"] / n, p["id"]))
        for p in closed:
            xv_new = p["exit_value"] * n
            # exit_price is already post-split and stays put; entry_value is the
            # preserved cost basis. realized_pnl_pct is restated too -- leaving it at
            # the pre-repair -89% beside a positive realized_pnl would be incoherent.
            conn.execute(
                "UPDATE paper_positions SET qty=?, entry_price=?, exit_value=?, "
                "realized_pnl=?, realized_pnl_pct=? WHERE id=?",
                (p["qty"] * n, p["entry_price"] / n, xv_new,
                 xv_new - p["entry_value"],
                 (xv_new / p["entry_value"] - 1.0) * 100.0, p["id"]))
        for sleeve, delta in cash_delta.items():
            conn.execute("UPDATE paper_portfolio SET cash = cash + ? WHERE strategy_name=?",
                         (delta, sleeve))
    log.info("APPLIED: %d price rows /%.4f, %d volume rows *%.4f (cache %s), %d open + "
             "%d closed positions re-based (entry_value preserved), %d sleeve cash "
             "correction(s) totalling $%+.2f.",
             n_price if adjust_cache else 0, n, n_vol if adjust_cache else 0, n,
             "adjusted" if adjust_cache else "SKIPPED (already adjusted)",
             len(stale), len(closed), len(cash_delta), sum(cash_delta.values()))

    # --- verify ------------------------------------------------------------
    span = conn.execute(
        "SELECT key_date, price FROM price_cache WHERE ticker=? AND kind='close' "
        "AND key_date < ? ORDER BY key_date DESC LIMIT 1", (t, eff)).fetchone()
    log.info("continuity: last pre-split close %s $%.4f vs first post-split $%.4f "
             "(ratio %.3f)", span["key_date"], span["price"], cutoff["price"],
             span["price"] / cutoff["price"])
    bad = conn.execute(
        "SELECT COUNT(*) c FROM paper_positions WHERE ticker=? AND status='open' "
        "AND entry_date < ? AND entry_price > ?", (t, eff, threshold)).fetchone()["c"]
    log.info("open positions still un-adjusted after repair: %d (expect 0)", bad)
    if args.include_closed:
        bad_c = conn.execute(
            "SELECT COUNT(*) c FROM paper_positions WHERE ticker=? AND status='closed' "
            "AND entry_date < ? AND exit_date >= ? AND entry_price > ?",
            (t, eff, eff, threshold)).fetchone()["c"]
        # Internal consistency of every repaired row: realized_pnl must equal
        # exit_value - entry_value, and exit_value must equal qty * exit_price.
        incoh = conn.execute(
            "SELECT COUNT(*) c FROM paper_positions WHERE ticker=? AND status='closed' "
            "AND entry_date < ? AND exit_date >= ? AND ("
            "  ABS(realized_pnl - (exit_value - entry_value)) > 0.01 OR "
            "  ABS(exit_value - qty * exit_price) > 0.01)",
            (t, eff, eff)).fetchone()["c"]
        log.info("closed positions still un-adjusted after repair: %d (expect 0)", bad_c)
        log.info("closed rows failing realized_pnl == exit_value - entry_value "
                 "or exit_value == qty * exit_price: %d (expect 0)", incoh)
        bad += bad_c + incoh
    conn.close()
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
