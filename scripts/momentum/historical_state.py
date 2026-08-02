"""Reconstruct a sleeve's cash + open positions AS OF any past date (read-only).

WHY THIS EXISTS (PRD M7.1, record CJ). `paper_mtm.compute_nav` has no historical
mode: it reads `paper_portfolio.cash` (TODAY's cash) and `paper_trader.list_open()`
(CURRENTLY open positions), so it can only mark the present. Repairing the 31 closed
KLAC positions (-$55,343.70 of phantom realized loss, record CJ) requires re-marking
~1,881 historical `paper_nav` rows, and that needs per-date cash — which cannot be
looked up because there is no `paper_transactions` table (confirmed by the CG and CH
audits). It has to be REPLAYED from `paper_positions`.

The replay is exact, not an approximation, because every paper cash movement goes
through `paper_trader.buy()` / `paper_trader.sell()`:
    buy  -> adjust_cash(-qty * fill_price) == -entry_value
    sell -> adjust_cash(+qty * fill_price) == +exit_value   (every call site passes
                                                             the position's full qty)
`paper_trader.adjust_cash` has no other caller in the repo, and nothing else writes
`paper_portfolio.cash`. Therefore:

    cash(t) = starting_cash - SUM(entry_value where entry_date <= t)
                            + SUM(exit_value  where exit_date  <= t)
    open(t) = rows with entry_date <= t AND (exit_date IS NULL OR exit_date > t)

Same-day round trips (entry_date == exit_date == t) net out correctly: the position
is closed at t, and both legs of its cash are counted at t.

READ-ONLY. This module never writes; it opens the DB `file:...?mode=ro`.

Usage:
  # M7.1 self-check: reconstruct every sleeve at the last settled trading day and
  # compare against the live paper_portfolio.cash / open-position count.
  python -m scripts.momentum.historical_state
  python -m scripts.momentum.historical_state --as-of 2026-06-30 --strategy mom_v2_paper
  python -m scripts.momentum.historical_state --db path/to/copy.db

  # M7.2 validation: recompute FULL NAV history for the KLAC-free sleeves and diff
  # against the stored paper_nav rows (known-good history the repair never touched).
  python -m scripts.momentum.historical_state --mode validate
"""
from __future__ import annotations

import argparse
import bisect
import logging
import sqlite3
import sys
from pathlib import Path

from trading_bot.config import DB_PATH
from scripts.momentum.check_coverage import last_settled_date

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("historical_state")

# Cash must reconstruct to the cent. The residual is pure float-summation error
# over a few thousand entry/exit legs, which lands ~1e-9 -- anything above a
# tenth of a cent means a cash movement this module does not know about.
CASH_TOL = 0.005


def _ro_connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def load_history(conn: sqlite3.Connection, strategy_name: str) -> dict:
    """All of a sleeve's ledger, read once, for repeated state_at() calls.

    Re-querying per date would be thousands of round trips against a 5 GB DB;
    a sleeve's whole position history is a few hundred rows.
    """
    prow = conn.execute(
        "SELECT starting_cash FROM paper_portfolio WHERE strategy_name=?",
        (strategy_name,)).fetchone()
    if prow is None:
        raise RuntimeError(f"No paper_portfolio row for {strategy_name!r}")
    rows = conn.execute(
        "SELECT id, ticker, qty, entry_price, entry_value, entry_date, "
        "       exit_price, exit_value, exit_date, status "
        "FROM paper_positions WHERE strategy_name=? ORDER BY entry_date, ticker",
        (strategy_name,)).fetchall()
    return {
        "strategy_name": strategy_name,
        "starting_cash": prow["starting_cash"],
        "positions": [dict(r) for r in rows],
    }


def state_at(history: dict, as_of: str) -> dict:
    """{cash, open_positions, n_open} for `history` as of ISO date `as_of`."""
    cash = history["starting_cash"]
    open_positions = []
    for p in history["positions"]:
        if p["entry_date"] > as_of:
            continue                       # not entered yet
        cash -= p["entry_value"]
        if p["exit_date"] is not None and p["exit_date"] <= as_of:
            cash += p["exit_value"]
        else:
            open_positions.append(p)
    return {"cash": cash, "open_positions": open_positions,
            "n_open": len(open_positions)}


def state_at_db(conn: sqlite3.Connection, strategy_name: str, as_of: str) -> dict:
    """One-shot convenience wrapper (PRD M7.1's named signature)."""
    return state_at(load_history(conn, strategy_name), as_of)


def load_closes(conn: sqlite3.Connection, tickers: list[str]) -> dict:
    """{ticker: ([key_date...], [price...])} ascending, for bisect lookups.

    `market_data.last_close_on_or_before` is one indexed query PER (ticker, date);
    re-marking a sleeve's full history needs tens of thousands of them. Reading each
    ticker's series once and bisecting is the same answer, orders of magnitude fewer
    round trips.
    """
    out: dict[str, tuple[list[str], list[float]]] = {}
    for t in tickers:
        rows = conn.execute(
            "SELECT key_date, price FROM price_cache WHERE ticker=? AND kind='close' "
            "AND price IS NOT NULL ORDER BY key_date ASC", (t,)).fetchall()
        out[t] = ([r["key_date"] for r in rows], [r["price"] for r in rows])
    return out


def last_close_at(closes: dict, ticker: str, as_of: str) -> float | None:
    """Carry-forward close on-or-before `as_of` — the bisect twin of
    `market_data.last_close_on_or_before` (same rule: nearest prior close, else None)."""
    dates, prices = closes.get(ticker, ([], []))
    i = bisect.bisect_right(dates, as_of)
    return prices[i - 1] if i else None


def nav_at(closes: dict, history: dict, as_of: str) -> dict:
    """Historical NAV for `history` at `as_of`, computed exactly the way
    `paper_mtm.compute_nav` computes today's: carry-forward close per open position,
    falling back to entry_price when no close exists at-or-before the date.
    """
    st = state_at(history, as_of)
    positions_value = 0.0
    missing = 0
    for p in st["open_positions"]:
        px = last_close_at(closes, p["ticker"], as_of)
        if px is None:
            px = p["entry_price"]
            missing += 1
        positions_value += px * p["qty"]
    return {"cash": st["cash"], "positions_value": positions_value,
            "total_nav": st["cash"] + positions_value,
            "n_open": st["n_open"], "missing_count": missing}


def validate(conn: sqlite3.Connection, strategies: list[str],
             tol: float) -> tuple[int, list[str]]:
    """Diff recomputed history against the STORED paper_nav rows, per sleeve.

    paper_nav stores cash and n_open_positions alongside total_nav, so the ledger
    replay and the price resolution are diffed SEPARATELY -- a cash mismatch means
    the reconstructor is wrong, a nav-only mismatch means the price_cache moved
    under the stored row. Conflating them would hide which.
    """
    out: list[str] = []
    n_fail = 0
    tot_rows = tot_ok = 0
    for s in strategies:
        hist = load_history(conn, s)
        closes = load_closes(conn, sorted({p["ticker"] for p in hist["positions"]}))
        rows = conn.execute(
            "SELECT nav_date, cash, total_nav, n_open_positions FROM paper_nav "
            "WHERE strategy_name=? ORDER BY nav_date", (s,)).fetchall()
        if not rows:
            out.append(f"[SKIP] {s:32s} no paper_nav rows")
            continue
        n_ok = n_cash_bad = n_open_bad = 0
        worst = 0.0
        worst_row = ""
        worst_cash = 0.0
        for r in rows:
            d = r["nav_date"]
            got = nav_at(closes, hist, d)
            dn = got["total_nav"] - r["total_nav"]
            dc = got["cash"] - r["cash"]
            if abs(dc) > tol:
                n_cash_bad += 1
            if got["n_open"] != r["n_open_positions"]:
                n_open_bad += 1
            if abs(dn) <= tol:
                n_ok += 1
            if abs(dn) > abs(worst):
                worst, worst_row = dn, d
            worst_cash = max(worst_cash, abs(dc))
        pct = 100.0 * n_ok / len(rows)
        tot_rows += len(rows)
        tot_ok += n_ok
        flags = []
        if n_cash_bad:
            flags.append(f"cash!={n_cash_bad}(max ${worst_cash:.4f})")
        if n_open_bad:
            flags.append(f"n_open!={n_open_bad}")
        ok = pct >= 95.0 and not n_cash_bad and not n_open_bad
        if not ok:
            n_fail += 1
        out.append(f"[{'PASS' if ok else 'FAIL'}] {s:32s} "
                   f"{n_ok}/{len(rows)} rows within ${tol} ({pct:5.1f}%)  "
                   f"worst nav delta {worst:+.4f} @ {worst_row or 'n/a'}"
                   + ("  " + " ".join(flags) if flags else ""))
    pct_all = 100.0 * tot_ok / tot_rows if tot_rows else 0.0
    out.append(f"TOTAL: {tot_ok}/{tot_rows} rows within ${tol} ({pct_all:.2f}%) "
               f"across {len(strategies)} sleeve(s)")
    out.append(f"RESULT: {'FAIL' if n_fail else 'PASS'} "
               f"({len(strategies) - n_fail}/{len(strategies)} sleeves reproduce known history)")
    return n_fail, out


def selfcheck(conn: sqlite3.Connection, as_of: str,
              strategies: list[str]) -> tuple[int, list[str]]:
    """Reconstruct each sleeve at `as_of` vs the LIVE portfolio row.

    Only honest when no position was entered or exited after `as_of` -- otherwise
    a mismatch is expected, not a bug -- so those sleeves are reported explicitly
    rather than silently passed or failed.
    """
    out: list[str] = []
    n_fail = 0
    worst = 0.0
    for s in strategies:
        hist = load_history(conn, s)
        st = state_at(hist, as_of)
        live = conn.execute(
            "SELECT cash FROM paper_portfolio WHERE strategy_name=?", (s,)).fetchone()["cash"]
        live_open = conn.execute(
            "SELECT COUNT(*) AS c FROM paper_positions "
            "WHERE strategy_name=? AND status='open'", (s,)).fetchone()["c"]
        after = sum(1 for p in hist["positions"]
                    if p["entry_date"] > as_of
                    or (p["exit_date"] is not None and p["exit_date"] > as_of))
        d_cash = st["cash"] - live
        worst = max(worst, abs(d_cash))
        fails = []
        if abs(d_cash) > CASH_TOL:
            fails.append(f"cash {st['cash']:.4f} vs live {live:.4f} (delta {d_cash:+.4f})")
        if st["n_open"] != live_open:
            fails.append(f"open count {st['n_open']} vs live {live_open}")
        tag = "" if not after else f"  [{after} leg(s) after {as_of}]"
        if fails:
            n_fail += 1
            out.append(f"[FAIL] {s:32s} " + "; ".join(fails) + tag)
        else:
            out.append(f"[PASS] {s:32s} cash ${st['cash']:>12,.2f} "
                       f"(delta {d_cash:+.4f})  open {st['n_open']}{tag}")
    out.append(f"MAX |cash delta| across {len(strategies)} sleeve(s): ${worst:.6f}")
    out.append(f"RESULT: {'FAIL' if n_fail else 'PASS'} "
               f"({len(strategies) - n_fail}/{len(strategies)} sleeves reconstruct exactly)")
    return n_fail, out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["selfcheck", "validate"], default="selfcheck",
                    help="selfcheck (M7.1): reconstruct vs live portfolio. "
                         "validate (M7.2): recompute full NAV history vs stored paper_nav.")
    ap.add_argument("--as-of", default=None,
                    help="selfcheck only. ISO date; default the last SETTLED trading day.")
    ap.add_argument("--strategy", default=None,
                    help="One sleeve. Default: all sleeves (selfcheck) / all "
                         "KLAC-free sleeves (validate).")
    ap.add_argument("--tol", type=float, default=0.01,
                    help="validate only: per-row |delta| tolerance in dollars.")
    ap.add_argument("--db", default=None, help="DB path (default: live var/trades.db).")
    args = ap.parse_args()

    db_path = DB_PATH if args.db is None else Path(args.db)
    conn = _ro_connect(db_path)

    if args.mode == "validate":
        # Only sleeves that NEVER held KLAC: their stored NAV history is known-good,
        # so any divergence is the reconstructor's fault, not the contamination's.
        strategies = [args.strategy] if args.strategy else [
            r["strategy_name"] for r in conn.execute(
                "SELECT strategy_name FROM paper_portfolio WHERE strategy_name NOT IN "
                "(SELECT DISTINCT strategy_name FROM paper_positions WHERE ticker='KLAC') "
                "ORDER BY strategy_name")]
        log.info("historical_state validate  db=%s  KLAC-free sleeves=%d  tol=$%s",
                 db_path.name, len(strategies), args.tol)
        n_fail, out = validate(conn, strategies, args.tol)
        for ln in out:
            (log.error if ln.startswith("[FAIL]") or ln.startswith("RESULT: FAIL")
             else log.info)(ln)
        conn.close()
        return 1 if n_fail else 0

    as_of = args.as_of or last_settled_date(conn)
    if as_of is None:
        log.error("No settled trading day found in price_cache; pass --as-of.")
        return 1

    strategies = [args.strategy] if args.strategy else [
        r["strategy_name"] for r in conn.execute(
            "SELECT strategy_name FROM paper_portfolio ORDER BY strategy_name")]

    log.info("historical_state selfcheck  db=%s  as_of=%s  sleeves=%d",
             db_path.name, as_of, len(strategies))
    n_fail, out = selfcheck(conn, as_of, strategies)
    for ln in out:
        (log.error if ln.startswith("[FAIL]") or ln.startswith("RESULT: FAIL") else log.info)(ln)
    conn.close()
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
