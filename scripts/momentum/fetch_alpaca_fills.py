"""PRD M6.1 - pull FILLED orders from the mirrored Alpaca PAPER accounts to CSV.

Read-only: GET /v2/orders only. Never submits, cancels, or modifies anything.
Never prints a key (credentials come from alpaca_accounts.configured_accounts(),
the same loader alpaca_sync uses).

Feeds M6.2, which pairs each fill against the sim's `paper_positions.entry_price`
to measure slippage in bps. This script only FETCHES and RECONCILES.

Reconciliation, and why it is stated the way it is
--------------------------------------------------
The project record logs orders **SUBMITTED** and **REJECTED** (99 on 2026-07-07,
record AV; 132 on 2026-08-03, record CP; 0 rejects both times). It has never
logged a FILL count. So 231 is the number to reconcile AGAINST, not a fill count
to assume. Every submitted order lands in exactly one terminal state, so the
identity that must hold per account is:

    submitted = filled + partially_filled + canceled + expired + rejected + <still open>

If filled < submitted, that is a FINDING to report, not a gap to explain away -
a DAY market order that never filled means the sim booked a position the mirror
does not hold, which is exactly the divergence M6 exists to measure.

Paging: /v2/orders has no page cursor. We walk forward with `after` = the last
page's newest `submitted_at` (an EXCLUSIVE bound) and dedupe by order id, which
also covers orders sharing a timestamp. Without paging + an explicit date range
this endpoint cannot reach 2026-07-07 at all, and its 100-row default silently
drops the OLDEST orders (it returns newest-first).

Price column: `filled_avg_price` is Alpaca's AVERAGE across every print of that
order, not a single fill price. A market order can fill in several prints. The
column is named for what it is; do not relabel it "fill_price" downstream.

Usage (read-only):
    python -m scripts.momentum.fetch_alpaca_fills
    python -m scripts.momentum.fetch_alpaca_fills --since 2026-07-01 --out var/fills.csv
"""
from __future__ import annotations

import argparse
import csv
import logging
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from trading_bot.config import VAR_DIR
from trading_bot.execution.alpaca_accounts import configured_accounts
from trading_bot.execution.alpaca_client import AlpacaError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("fetch_alpaca_fills")

PAGE_LIMIT = 500  # Alpaca's documented maximum for /v2/orders
MAX_PAGES = 40    # backstop: 40 x 500 = 20,000 orders, far above any real window

# Orders the mirror is known to have SUBMITTED, from the record. Used only to
# print an explicit reconciliation line - never to filter or fabricate rows.
#
# `alpaca_date` is NOT a typo and NOT the rebalance date. Alpaca's `submitted_at`
# is the simulator's QUEUE-RELEASE time, not when we POSTed. Measured 2026-08-05:
# all 132 August POSTs left this machine in a 6-second burst at 23:24:48-23:24:54Z
# (18:24 CDT, 2026-08-03) per var/alpaca_request_ids.log, yet Alpaca stamps them
# submitted_at 2026-08-04T08:00-13:23Z. Keying reconciliation off submitted_at
# alone therefore mis-dates a whole batch by a day. The July batch went out
# mid-session and has no such shift, which is why only one entry below is offset.
BATCHES = [
    {"rebalance": "2026-07-07", "alpaca_date": "2026-07-07",
     "counts": {"residual_roa_6535_0701_paper": 48,
                "mom_roa_6535_0701_paper": 50,
                "spy_benchmark_0701_paper": 1}},      # 99 total, record AV
    {"rebalance": "2026-08-03", "alpaca_date": "2026-08-04",
     "counts": {"residual_roa_6535_0701_paper": 62,
                "mom_roa_6535_0701_paper": 69,
                "spy_benchmark_0701_paper": 1}},      # 132 total, record CP
]
SUBMITTED_TOTAL_ALL_ACCOUNTS = {"2026-07-07": 99, "2026-08-03": 132}

CSV_COLUMNS = [
    # The six the PRD names...
    "ticker", "side", "qty", "filled_avg_price", "filled_at", "account",
    # ...plus what M6.2 and any re-run actually need. order_id makes the fetch
    # idempotent and lets a partial fill be traced back; filled_qty vs qty is
    # how a partial fill is visible at all; status is how a NON-fill is visible.
    "order_id", "sleeve", "status", "qty_filled", "submitted_at",
]


def _iso(d: date) -> str:
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc).isoformat()


def fetch_orders(client, *, since: date, until: date) -> list[dict]:
    """Every order in [since, until), paged and deduped by id.

    status="all" on purpose: a filled-only query cannot prove the reconciliation
    identity above, because the canceled/expired orders are exactly what explains
    a filled count below the submitted count.
    """
    seen: dict[str, dict] = {}
    cursor = _iso(since)
    for page_n in range(MAX_PAGES):
        page = client.list_orders(status="all", limit=PAGE_LIMIT,
                                  after=cursor, until=_iso(until),
                                  direction="asc")
        if not page:
            break
        fresh = {o["id"]: o for o in page if o["id"] not in seen}
        seen.update(fresh)
        log.info("    page %d: %d order(s), %d new (total %d)",
                 page_n + 1, len(page), len(fresh), len(seen))
        if not fresh:
            if len(page) >= PAGE_LIMIT:
                # A FULL page with nothing new means >PAGE_LIMIT orders share one
                # `submitted_at`, so the exclusive `after` cursor cannot advance
                # past them and the remainder is unreachable. Vanishingly unlikely
                # at Alpaca's timestamp precision, but it would silently truncate,
                # so it must not pass quietly.
                log.error("INCOMPLETE: a full %d-order page advanced the cursor "
                          "by nothing - more than %d orders share submitted_at=%s "
                          "and cannot be paged past. Results are TRUNCATED.",
                          PAGE_LIMIT, PAGE_LIMIT, cursor)
            break  # same timestamp repeating; nothing further to gain
        cursor = max(o["submitted_at"] for o in page)
        if len(page) < PAGE_LIMIT:
            break
    else:
        log.error("PAGING STOPPED at the %d-page backstop - results may be "
                  "INCOMPLETE. Narrow --since/--until and re-run.", MAX_PAGES)
    return list(seen.values())


def to_rows(orders: list[dict], account) -> list[dict]:
    """Only orders that actually put shares on the book become CSV rows."""
    rows = []
    for o in orders:
        qty_filled = float(o.get("filled_qty") or 0)
        if qty_filled <= 0:
            continue
        rows.append({
            "ticker": o.get("symbol"),
            "side": o.get("side"),
            "qty": o.get("qty"),
            "filled_avg_price": o.get("filled_avg_price"),
            "filled_at": o.get("filled_at"),
            "account": f"ACCT{account.n}",
            "order_id": o.get("id"),
            "sleeve": account.sleeve,
            "status": o.get("status"),
            "qty_filled": o.get("filled_qty"),
            "submitted_at": o.get("submitted_at"),
        })
    return rows


def reconcile(orders: list[dict], rows: list[dict], account) -> list[str]:
    """Per-account reconciliation. Returns findings (empty list = reconciled)."""
    findings: list[str] = []
    by_status: dict[str, int] = {}
    for o in orders:
        by_status[o.get("status", "?")] = by_status.get(o.get("status", "?"), 0) + 1
    log.info("  ACCT%d %s: %d order(s) in window -> %s",
             account.n, account.sleeve, len(orders),
             ", ".join(f"{k}={v}" for k, v in sorted(by_status.items())) or "none")
    log.info("  ACCT%d %s: %d with a nonzero fill", account.n, account.sleeve, len(rows))

    for b in BATCHES:
        n_sub = b["counts"].get(account.sleeve)
        if n_sub is None:
            continue
        day = b["alpaca_date"]
        n_seen = sum(1 for o in orders if str(o.get("submitted_at", ""))[:10] == day)
        n_fil = sum(1 for r in rows if str(r["submitted_at"])[:10] == day)
        verdict = "OK" if n_fil == n_sub else "FINDING"
        log.info("  ACCT%d %s rebalance %s (alpaca %s): record says %d submitted | "
                 "API shows %d order(s), %d filled -> %s", account.n, account.sleeve,
                 b["rebalance"], day, n_sub, n_seen, n_fil, verdict)
        if n_seen != n_sub:
            findings.append(f"{account.sleeve} rebalance {b['rebalance']}: record "
                            f"logged {n_sub} orders SUBMITTED, API returned {n_seen}")
        if n_fil != n_sub:
            findings.append(f"{account.sleeve} rebalance {b['rebalance']}: {n_sub} "
                            f"submitted but {n_fil} FILLED - the mirror does not "
                            f"hold what the sim booked for that rebalance")

    # Window total, independent of any date key -- catches a batch that landed on
    # an unexpected date instead of silently reporting it missing.
    want_total = sum(b["counts"].get(account.sleeve, 0) for b in BATCHES)
    if want_total and len(rows) != want_total:
        findings.append(f"{account.sleeve}: {len(rows)} filled row(s) in the whole "
                        f"window vs {want_total} expected across all batches")
    return findings


def report_execution_timing(rows: list[dict]) -> None:
    """Submit->fill lag per batch. This is M6.2's headline caveat, not a nicety.

    The July batch went out mid-session and filled in seconds. The August batch
    was POSTed after the close, so Alpaca held it to the next session and filled
    it at that OPEN - about 14 hours after the sim booked its own fills at the
    2026-08-03 close. The sim-vs-mirror price difference for August is therefore
    dominated by the OVERNIGHT GAP, not by execution quality. The two batches are
    not comparable and must not be pooled into one slippage number.
    """
    from collections import defaultdict
    by_batch = defaultdict(list)
    for r in rows:
        by_batch[str(r["submitted_at"])[:10]].append(r)
    log.info("EXECUTION TIMING (drives M6.2's interpretation):")
    for day in sorted(by_batch):
        b = by_batch[day]
        lags = []
        for r in b:
            if not r["filled_at"]:
                continue
            t0 = datetime.fromisoformat(str(r["submitted_at"]).replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(str(r["filled_at"]).replace("Z", "+00:00"))
            lags.append((t1 - t0).total_seconds())
        if not lags:
            continue
        lags.sort()
        med = lags[len(lags) // 2]
        kind = ("intraday, immediate" if med < 60 else
                "HELD TO THE NEXT SESSION OPEN - overnight gap, not slippage")
        log.info("  alpaca %s: n=%d  lag min=%.1fs median=%.1fs max=%.1fs  -> %s",
                 day, len(b), lags[0], med, lags[-1], kind)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-07-01",
                    help="Inclusive start date (default covers the 07-07 deploy).")
    ap.add_argument("--until", default=None, help="Exclusive end date (default: tomorrow).")
    ap.add_argument("--out", default=None,
                    help="CSV path (default var/alpaca_fills_<since>_<until>.csv).")
    args = ap.parse_args()

    since = date.fromisoformat(args.since)
    until = (date.fromisoformat(args.until) if args.until
             else date.fromordinal(date.today().toordinal() + 1))
    out = Path(args.out) if args.out else VAR_DIR / f"alpaca_fills_{since}_{until}.csv"

    accounts = configured_accounts()
    if not accounts:
        log.error("No Alpaca accounts configured (alpaca_keys.env). Nothing to fetch.")
        return 2
    log.info("Fetching orders %s -> %s for %d account(s) [READ-ONLY]",
             since, until, len(accounts))

    all_rows: list[dict] = []
    findings: list[str] = []
    for a in accounts:
        try:
            with a.client() as c:
                orders = fetch_orders(c, since=since, until=until)
        except AlpacaError as e:
            # Report, never fabricate: an account we could not read is NOT an
            # account with zero fills.
            log.error("  ACCT%d %s: FETCH FAILED (%s)", a.n, a.sleeve, e)
            findings.append(f"{a.sleeve}: fetch FAILED ({e}) - counts below EXCLUDE "
                            f"this account; do not read the total as complete")
            continue
        rows = to_rows(orders, a)
        findings.extend(reconcile(orders, rows, a))
        all_rows.extend(rows)

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        w.writeheader()
        w.writerows(all_rows)
    log.info("Wrote %d fill row(s) -> %s", len(all_rows), out)
    if all_rows:
        report_execution_timing(all_rows)

    total_expected = sum(SUBMITTED_TOTAL_ALL_ACCOUNTS.values())
    log.info("ALL ACCOUNTS: %d filled row(s) vs %d order(s) submitted per the "
             "record (%s)", len(all_rows), total_expected,
             ", ".join(f"{d}={n}" for d, n in sorted(SUBMITTED_TOTAL_ALL_ACCOUNTS.items())))

    if findings:
        log.error("RECONCILIATION FINDINGS (%d) - report these, do not explain "
                  "them away:", len(findings))
        for f in findings:
            log.error("  - %s", f)
        return 1
    log.info("RECONCILED: every logged order is accounted for.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
