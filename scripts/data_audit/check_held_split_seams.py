"""Post-refresh integrity check for split/spike seams in HELD positions.

Why this exists: a corporate action (e.g. KLAC 10:1, eff. 2026-06-12) makes
yfinance rewrite a ticker's history onto a new split basis. If the cached
closes end up on a DIFFERENT basis than the stored paper_position (qty /
entry_price), the daily MTM marks the position at ~10x the wrong level and the
sleeve's NAV silently jumps. The 2026-06-11 hand-fix put KLAC's position on the
post-split basis; the risk is the next refresh re-rewriting the recent bars and
breaking that alignment again (record Appendix X, memory corporate_action_splits).

What it does: for every OPEN position across all sleeves it runs two checks on
the cached closes from the ticker's EARLIEST open entry_date to the latest bar
(record EE, 2026-09-29: the old last-8-bars window missed MLI's 2:1 cliffs, which
sat weeks behind the latest bar while positions opened before them were held):

  Check 1 (seam)  — any consecutive-day move beyond [1/MULT, MULT]x, or within
                    SPLIT_TOL of a split ratio even inside that band. Severities:
    FAIL (exit 1) — the ratio is within SPLIT_TOL of a common split ratio
                    (k or 1/k for k in SPLIT_KS), ANYWHERE in the scan window: a
                    corporate-action cliff inside a held position's life means
                    entry_price and the cached history are on different bases. OR
                    the seam touches the LATEST bar (latest vs prior close is a
                    >MULT jump): the live mark is on a different basis than
                    yesterday's -> marked wrong RIGHT NOW. Re-apply the fix.
    WARN (exit 0) — an interior >MULT move that is NOT near a split ratio (KOD
                    2.78x on 2026-09-28 is 7.3% from 3:1): cosmetic for the
                    current mark (MTM uses only the latest close) but shown so a
                    human confirms it is real news, not a new data break.
  Check 2 (basis) — latest_close / entry_price outside [1/BAND_HI, BAND_HI].
    FAIL (exit 1) — catches a UNIFORM rescale of the whole series (yfinance
                    re-applying a split to ALL bars), which leaves NO seam for
                    check 1 to see but marks the live position ~Nx wrong. The
                    position's entry_price is the split-consistent anchor.

Read-only on the DB (file:...?mode=ro). Appends its findings, each line prefixed
"[split-seams]", to var/anomaly_report.log. Run after a price refresh:
    .venv\\Scripts\\python.exe -m scripts.data_audit.check_held_split_seams
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import datetime

from trading_bot.config import DB_PATH, VAR_DIR

REPORT_PATH = VAR_DIR / "anomaly_report.log"
WINDOW = 8     # recent closes SHOWN per flagged name (the scan covers every bar since entry)
MULT = 2.0     # a single-day move beyond this (or below 1/this) = seam tell
BAND_HI = 5.0  # latest_close/entry_price outside [1/BAND_HI, BAND_HI] = basis-suspect
               # (safe for monthly sleeves; long holds could legitimately exceed it)
SPLIT_KS = (2, 3, 4, 5, 10)  # common split ratios (and their reverses)
SPLIT_TOL = 0.05             # relative distance from k or 1/k that still counts as a split


def near_split_ratio(r: float, tol: float = SPLIT_TOL) -> bool:
    """True if a 1-day close ratio r sits within `tol` (relative) of k or 1/k, k in SPLIT_KS."""
    # shortcut: duplicated in scripts/momentum/check_anomalies.py (the daily-flow
    # scan must not import from data_audit). Merge into one module if a 3rd copy is needed.
    return any(abs(r / k - 1.0) <= tol or abs(r * k - 1.0) <= tol for k in SPLIT_KS)


def _ro_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _closes_since(conn, ticker: str, since: str) -> list[tuple[str, float]]:
    rows = conn.execute(
        "SELECT key_date, price FROM price_cache "
        "WHERE ticker=? AND kind='close' AND price > 0 AND key_date >= ? "
        "ORDER BY key_date",
        (ticker, since)).fetchall()
    return [(r["key_date"], r["price"]) for r in rows]  # oldest->newest


def _scan(emit) -> int:
    # Distinct held tickers across every sleeve, with the sleeves that hold them.
    holders: dict[str, list[dict]] = {}
    conn = _ro_connect()
    for r in conn.execute(
            "SELECT ticker, strategy_name, qty, entry_price, entry_date "
            "FROM paper_positions WHERE status='open'"):
        holders.setdefault(r["ticker"], []).append(
            {"sleeve": r["strategy_name"], "qty": r["qty"],
             "entry_price": r["entry_price"], "entry_date": r["entry_date"]})

    fails, warns, basis = [], [], []
    for ticker in sorted(holders):
        series = _closes_since(conn, ticker, min(h["entry_date"] for h in holders[ticker]))
        if len(series) < 2:
            continue

        # Check 1 — day-over-day seam (catches a partial rewrite that leaves
        # a discontinuity, e.g. only the recent or only the old bars rescaled).
        seams = []  # (i, prev_date, prev_px, date, px, ratio)
        for i in range(1, len(series)):
            d0, p0 = series[i - 1]
            d1, p1 = series[i]
            ratio = p1 / p0
            # near_split_ratio also catches a real 2:1 that lands just INSIDE the
            # MULT band (MLI 2026-06-05: 0.5008x, a hair above 1/MULT).
            if ratio >= MULT or ratio <= 1.0 / MULT or near_split_ratio(ratio):
                seams.append((i, d0, p0, d1, p1, ratio))
        if seams:
            latest_idx = len(series) - 1
            hard = any(s[0] == latest_idx or near_split_ratio(s[5]) for s in seams)
            (fails if hard else warns).append((ticker, series, seams))

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
    conn.close()

    if not fails and not warns and not basis:
        emit("OK: no >{:.0f}x day move since entry on any held name and every held "
             "name's latest mark is within [{:.2g}x, {:.0f}x] of its "
             "entry_price.".format(MULT, 1.0 / BAND_HI, BAND_HI))
        return 0

    for sev, group in (("FAIL", fails), ("WARN", warns)):
        for ticker, series, seams in group:
            latest_idx = len(series) - 1
            emit(f"\n[{sev} seam] {ticker}  held by "
                 f"{', '.join(h['sleeve'] for h in holders[ticker])}")
            emit("  recent closes: " +
                 "  ".join(f"{d}={px:.2f}" for d, px in series[-WINDOW:]))
            for i, d0, p0, d1, p1, ratio in seams:
                tag = ("  <- split-like" if near_split_ratio(ratio) else
                       "  <- LATEST bar" if i == latest_idx else "")
                emit(f"    seam {d0} ${p0:.2f} -> {d1} ${p1:.2f}  "
                     f"({ratio:.4f}x){tag}")
            latest_d, latest_px = series[-1]
            for h in holders[ticker]:
                emit(f"    {h['sleeve']}: qty={h['qty']:.4f} "
                     f"entry=${h['entry_price']:.2f} -> MTM @ {latest_d} "
                     f"${latest_px:.2f} = ${h['qty'] * latest_px:,.2f}")

    for ticker, h, latest_px, r, series in basis:
        emit(f"\n[FAIL basis] {ticker}  ({h['sleeve']}): latest close "
             f"${latest_px:.2f} is {r:.3f}x its entry_price "
             f"${h['entry_price']:.2f} — outside [{1.0/BAND_HI:.2g}x, "
             f"{BAND_HI:.0f}x]. Likely a uniform split-rescale of the cache "
             f"(no day-over-day seam to catch). Verify the mark basis.")
        emit("  recent closes: " +
             "  ".join(f"{d}={px:.2f}" for d, px in series[-WINDOW:]))

    if fails or basis:
        n = len(fails) + len(basis)
        emit(f"\n>>> {n} held name(s) marked on a SUSPECT basis. "
             "Verify / re-apply the split fix (see Appendix X).")
        return 1
    emit(f"\n>>> {len(warns)} name(s) with a large NON-split-ratio move (latest "
         "mark OK). Confirm each is real news, not a data break.")
    return 0


def main() -> int:
    report: list[str] = []

    def emit(msg: str) -> None:
        print(msg)
        report.extend("[split-seams] " + ln.rstrip() for ln in msg.splitlines() if ln.strip())

    rc = _scan(emit)
    # Same log check_anomalies appends to; the prefix tells the two apart.
    VAR_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write(f"[split-seams] === {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
                f"held split-seam scan (rc={rc}) ===\n")
        for ln in report:
            f.write(ln + "\n")
        f.write("\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
