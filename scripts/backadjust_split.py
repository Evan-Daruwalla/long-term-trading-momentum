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

WHAT IT DELIBERATELY DOES NOT DO:
  * It does not touch CLOSED positions or their realized P&L.
  * It does not touch paper_nav.
  Both are sacred history under CLAUDE.md; rewriting them is Evan's explicit call,
  not a side effect of a data repair. Consequence: sleeves that already CLOSED an
  un-adjusted position keep that phantom realized P&L in their cash balance.

Ratios are supplied by the operator, not inferred: yfinance's splits_json was empty
for KLAC, and inferring N from the price cliff is unreliable because the stock also
moves on the split date (KLAC's raw cliff is 9.79x for a true 10:1 split).

Usage:
  python -m scripts.backadjust_split --ticker KLAC --ratio 10 --effective 2026-05-13
  python -m scripts.backadjust_split --ticker KLAC --ratio 10 --effective 2026-05-13 --execute
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
    if not (n / 2.0 <= cliff <= n * 2.0):
        log.error("%s: expected an un-adjusted cliff near %.4gx across %s, found %.4gx "
                  "(%s $%.4f -> $%.4f). History looks ALREADY ADJUSTED (or the ratio/date "
                  "is wrong). Refusing to touch it.", t, n, eff, cliff,
                  last_pre["key_date"], last_pre["price"], cutoff["price"])
        conn.close()
        return 1
    log.info("cliff check: %.4gx across %s -- consistent with an un-adjusted %.4g:1 split",
             cliff, eff, n)

    if not args.execute:
        log.info("DRY RUN -- %d price rows, %d volume rows, %d positions would change. "
                 "Re-run with --execute.", n_price, n_vol, len(stale))
        conn.close()
        return 0

    # --- apply -------------------------------------------------------------
    with conn:
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
    log.info("APPLIED: %d price rows /%.4f, %d volume rows *%.4f, %d open positions "
             "re-based (entry_value preserved).", n_price, n, n_vol, n, len(stale))

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
    conn.close()
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
