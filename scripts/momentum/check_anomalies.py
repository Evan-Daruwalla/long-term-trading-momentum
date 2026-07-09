"""Single-day price-anomaly detector for the daily flow (read-only, non-blocking).

Surfaces the "split misapplication" failure class (record Appendix X / KLAC
2026-06-12): yfinance applies a split to history days early, producing a bogus
>1000% single-day move that corrupts ranks and NAVs. The tell is the giant
one-day move. This scans for it every day and REPORTS — it never halts the flow
(a huge move can be legitimate news), and it never touches data. Acting on a
finding is Evan's call.

Reads price_cache + paper_positions READ-ONLY (file:...?mode=ro). Never writes
the DB; appends a dated section to var/anomaly_report.log.

Checks, for the target close date vs the prior trading day:
  1. Held names (open in any sleeve) whose |1-day move| exceeds --held-threshold
     (default 300%).
  2. Any cached ticker whose |1-day move| exceeds --cache-threshold (default
     1000%) — the KLAC tell.
  3. Held names with no close on the target date (stale/missing mark).

Usage:
  python -m scripts.momentum.check_anomalies
  python -m scripts.momentum.check_anomalies --date 2026-07-07
  python -m scripts.momentum.check_anomalies --held-threshold 200 --cache-threshold 800
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from datetime import datetime

from trading_bot.config import DB_PATH, VAR_DIR

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("check_anomalies")

# A market-closed day leaves only a couple hundred stray closes; require a real
# trading day when auto-picking the target/prior dates (matches check_coverage).
MIN_TRADING_DAY_COUNT = 1000
REPORT_PATH = VAR_DIR / "anomaly_report.log"


def _ro_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _recent_trading_dates(conn: sqlite3.Connection, before: str | None, n: int) -> list[str]:
    """Most recent `n` real trading dates (count >= MIN_TRADING_DAY_COUNT),
    optionally strictly before `before`, newest first."""
    where = "kind='close' AND price IS NOT NULL"
    params: list = []
    if before:
        where += " AND key_date < ?"
        params.append(before)
    rows = conn.execute(
        f"SELECT key_date, COUNT(*) AS c FROM price_cache WHERE {where} "
        f"GROUP BY key_date ORDER BY key_date DESC LIMIT ?",
        (*params, n * 3),
    ).fetchall()
    return [r["key_date"] for r in rows if r["c"] >= MIN_TRADING_DAY_COUNT][:n]


def _closes_on(conn: sqlite3.Connection, d: str) -> dict[str, float]:
    rows = conn.execute(
        "SELECT ticker, price FROM price_cache "
        "WHERE kind='close' AND key_date=? AND price IS NOT NULL",
        (d,),
    ).fetchall()
    return {r["ticker"]: r["price"] for r in rows}


def _held_tickers(conn: sqlite3.Connection) -> dict[str, list[str]]:
    """{ticker: [sleeves holding it]} for all open paper positions."""
    rows = conn.execute(
        "SELECT DISTINCT ticker, strategy_name FROM paper_positions WHERE status='open'"
    ).fetchall()
    held: dict[str, list[str]] = {}
    for r in rows:
        held.setdefault(r["ticker"], []).append(r["strategy_name"])
    return held


def scan(conn: sqlite3.Connection, target: str, prior: str,
         held_thresh: float, cache_thresh: float, min_price: float) -> tuple[list[str], dict]:
    """Return (anomaly_lines, stats). Move % = (p_new/p_old - 1) * 100."""
    new = _closes_on(conn, target)
    old = _closes_on(conn, prior)
    held = _held_tickers(conn)
    anomalies: list[str] = []

    # 1 + 2: single-day moves. Held names get the tighter threshold and no price
    # floor (we want to know about anything we own). Every other ticker gets the
    # cache-wide KLAC threshold, but only above --min-price: sub-penny nanocaps
    # routinely swing >1000% in ratio terms ($0.0007->$0.01) and are noise, not
    # the split-misapplication tell (KLAC was ~$800 when it fired).
    for tk, p_new in new.items():
        p_old = old.get(tk)
        if p_old is None or p_old == 0:
            continue
        move = (p_new / p_old - 1.0) * 100.0
        if tk in held:
            if abs(move) > held_thresh:
                anomalies.append(
                    f"MOVE  {tk:8s} {move:+9.1f}%  ${p_old:.4f}->${p_new:.4f}  "
                    f"[HELD {','.join(held[tk])}]")
        elif abs(move) > cache_thresh and p_old >= min_price:
            anomalies.append(
                f"MOVE  {tk:8s} {move:+9.1f}%  ${p_old:.4f}->${p_new:.4f}  [cache]")

    # 3: held names with no close on the target date.
    for tk, sleeves in sorted(held.items()):
        if tk not in new:
            anomalies.append(
                f"NOCLOSE {tk:8s} no close on {target}  [HELD {','.join(sleeves)}]")

    stats = {"n_new": len(new), "n_old": len(old), "n_held": len(held)}
    return anomalies, stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None,
                    help="Target close date (ISO). Default: latest trading day.")
    ap.add_argument("--held-threshold", type=float, default=300.0,
                    help="Flag held-name |1-day move %%| above this (default 300).")
    ap.add_argument("--cache-threshold", type=float, default=1000.0,
                    help="Flag any |1-day move %%| above this (default 1000, the KLAC tell).")
    ap.add_argument("--min-price", type=float, default=1.0,
                    help="Cache-wide moves only flagged when the prior close >= this "
                         "(default $1) to skip sub-penny nanocap noise. Held names are exempt.")
    args = ap.parse_args()

    conn = _ro_connect()
    if args.date:
        target = args.date
        prior_list = _recent_trading_dates(conn, args.date, 1)
    else:
        latest = _recent_trading_dates(conn, None, 1)
        if not latest:
            log.error("No trading days in price_cache.")
            return 1
        target = latest[0]
        prior_list = _recent_trading_dates(conn, target, 1)
    if not prior_list:
        log.error("No prior trading day before %s — cannot compute 1-day moves.", target)
        return 1
    prior = prior_list[0]

    anomalies, stats = scan(conn, target, prior,
                            args.held_threshold, args.cache_threshold, args.min_price)

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = (f"=== {stamp} | anomaly scan  close={target}  prior={prior}  "
              f"held={stats['n_held']} cache_new={stats['n_new']} "
              f"thresholds held>{args.held_threshold:.0f}% "
              f"cache>{args.cache_threshold:.0f}%@>=${args.min_price:.2f} ===")
    log.info(header)
    if anomalies:
        for a in anomalies:
            log.warning("  " + a)
        log.warning("ANOMALIES: %d flagged for %s.", len(anomalies), target)
    else:
        log.info("0 anomalies for %s.", target)

    # Append a dated section to the report log (this file is ours, no redirect
    # collision — unlike last_daily_run.log).
    VAR_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write(header + "\n")
        if anomalies:
            for a in anomalies:
                f.write("  " + a + "\n")
            f.write(f"ANOMALIES: {len(anomalies)} flagged.\n\n")
        else:
            f.write("0 anomalies.\n\n")

    # Non-blocking by design: always exit 0 so daily.bat never halts on a move.
    return 0


if __name__ == "__main__":
    sys.exit(main())
