"""Post-refresh integrity check for split/spike seams in HELD positions.

Why this exists: a corporate action (e.g. KLAC 10:1, eff. 2026-06-12) makes
yfinance rewrite a ticker's history onto a new split basis. If the cached
closes end up on a DIFFERENT basis than the stored paper_position (qty /
entry_price), the daily MTM marks the position at ~10x the wrong level and the
sleeve's NAV silently jumps. The 2026-06-11 hand-fix put KLAC's position on the
post-split basis; the risk is the next refresh re-rewriting the recent bars and
breaking that alignment again (record Appendix X, memory corporate_action_splits).

What it does: for every OPEN position across all sleeves it runs two checks on
the last WINDOW cached closes:

  Check 1 (seam)  — any consecutive-day move beyond [1/MULT, MULT]x. Severities:
    FAIL (exit 1) — the seam touches the LATEST bar (latest vs prior close is a
                    >MULT jump): the live mark is on a different basis than
                    yesterday's -> marked wrong RIGHT NOW. Re-apply the fix.
    WARN (exit 0) — an INTERIOR seam (not the latest edge), e.g. an old KLAC
                    06-05->06-08 boundary: cosmetic for the current mark (MTM
                    uses only the latest close) but real in history; shown so a
                    human confirms it's the expected artifact, not a new break.
  Check 2 (basis) — latest_close / entry_price outside [1/BAND_HI, BAND_HI].
    FAIL (exit 1) — catches a UNIFORM rescale of the whole series (yfinance
                    re-applying a split to ALL bars), which leaves NO seam for
                    check 1 to see but marks the live position ~Nx wrong. The
                    position's entry_price is the split-consistent anchor.

Read-only. Run after a price refresh:
    .venv\\Scripts\\python.exe -m scripts.data_audit.check_held_split_seams
"""
from __future__ import annotations

import sys
from datetime import date

from trading_bot.db import connect
from trading_bot.execution import paper_trader

WINDOW = 8     # recent closes to inspect per held name
MULT = 2.0     # a single-day move beyond this (or below 1/this) = seam tell
BAND_HI = 5.0  # latest_close/entry_price outside [1/BAND_HI, BAND_HI] = basis-suspect
               # (safe for monthly sleeves; long holds could legitimately exceed it)


def _recent_closes(conn, ticker: str, n: int) -> list[tuple[str, float]]:
    rows = conn.execute(
        "SELECT key_date, price FROM price_cache "
        "WHERE ticker=? AND kind='close' AND price > 0 "
        "ORDER BY key_date DESC LIMIT ?",
        (ticker, n)).fetchall()
    return [(r["key_date"], r["price"]) for r in reversed(rows)]  # oldest->newest


def main() -> int:
    # Distinct held tickers across every sleeve, with the sleeves that hold them.
    holders: dict[str, list[dict]] = {}
    with connect() as conn:
        for sn, in conn.execute(
                "SELECT DISTINCT strategy_name FROM paper_positions WHERE status='open'"):
            for p in paper_trader.list_open(sn):
                holders.setdefault(p["ticker"], []).append(
                    {"sleeve": sn, "qty": p["qty"], "entry_price": p["entry_price"]})

        fails, warns, basis = [], [], []
        for ticker in sorted(holders):
            series = _recent_closes(conn, ticker, WINDOW)
            if len(series) < 2:
                continue

            # Check 1 — day-over-day seam (catches a partial rewrite that leaves
            # a discontinuity, e.g. only the recent or only the old bars rescaled).
            seams = []  # (i, prev_date, prev_px, date, px, ratio)
            for i in range(1, len(series)):
                d0, p0 = series[i - 1]
                d1, p1 = series[i]
                ratio = p1 / p0 if p0 else float("inf")
                if ratio >= MULT or ratio <= 1.0 / MULT:
                    seams.append((i, d0, p0, d1, p1, ratio))
            if seams:
                latest_idx = len(series) - 1
                touches_latest = any(s[0] == latest_idx for s in seams)
                (fails if touches_latest else warns).append((ticker, series, seams))

            # Check 2 — basis vs the position's own entry_price (the split-
            # consistent anchor). A UNIFORM rescale of the whole series leaves
            # NO day-over-day seam (check 1 misses it) but every bar ends up
            # ~Nx off, so latest_close / entry_price blows past a sane band.
            # These sleeves rebalance monthly, so a held name moving >BAND_HIx or
            # <1/BAND_HIx from entry in weeks is implausible from real price
            # action -> almost certainly a data-basis error on a LIVE mark.
            latest_px = series[-1][1]
            for h in holders[ticker]:
                r = latest_px / h["entry_price"] if h["entry_price"] else float("inf")
                if r >= BAND_HI or r <= 1.0 / BAND_HI:
                    basis.append((ticker, h, latest_px, r, series))

        if not fails and not warns and not basis:
            print("OK: no split/spike seams (>{:.0f}x day move) and every held "
                  "name's latest mark is within [{:.2g}x, {:.0f}x] of its "
                  "entry_price.".format(MULT, 1.0 / BAND_HI, BAND_HI))
            return 0

        for sev, group in (("FAIL", fails), ("WARN", warns)):
            for ticker, series, seams in group:
                print(f"\n[{sev} seam] {ticker}  held by "
                      f"{', '.join(h['sleeve'] for h in holders[ticker])}")
                print("  recent closes: " +
                      "  ".join(f"{d}={px:.2f}" for d, px in series))
                for _, d0, p0, d1, p1, ratio in seams:
                    print(f"    seam {d0} ${p0:.2f} -> {d1} ${p1:.2f}  "
                          f"({ratio:.2f}x)")
                latest_d, latest_px = series[-1]
                for h in holders[ticker]:
                    print(f"    {h['sleeve']}: qty={h['qty']:.4f} "
                          f"entry=${h['entry_price']:.2f} -> MTM @ {latest_d} "
                          f"${latest_px:.2f} = ${h['qty'] * latest_px:,.2f}")

        for ticker, h, latest_px, r, series in basis:
            print(f"\n[FAIL basis] {ticker}  ({h['sleeve']}): latest close "
                  f"${latest_px:.2f} is {r:.3f}x its entry_price "
                  f"${h['entry_price']:.2f} — outside [{1.0/BAND_HI:.2g}x, "
                  f"{BAND_HI:.0f}x]. Likely a uniform split-rescale of the cache "
                  f"(no day-over-day seam to catch). Verify the mark basis.")
            print("  recent closes: " +
                  "  ".join(f"{d}={px:.2f}" for d, px in series))

        if fails or basis:
            n = len(fails) + len(basis)
            print(f"\n>>> {n} held name(s) marked on a SUSPECT basis. "
                  "Verify / re-apply the split fix (see Appendix X).")
            return 1
        print(f"\n>>> {len(warns)} interior seam(s) only (latest mark OK). "
              "Confirm each is the expected known artifact.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
