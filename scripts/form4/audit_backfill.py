"""Post-backfill audit: report missing and duplicate signals.

For the date range, this:
  1. Builds the full set of Form 4 accessions from the cached quarterly indexes
     (the source-of-truth list of what EDGAR published).
  2. Queries the signals table for accessions we actually have.
  3. Classifies the gap. Most missing accessions are INTENTIONAL skips —
     untradeable issuers, derivative-only grants, no nonDerivative
     transactions — not data loss. To tell them apart we re-fetch a
     random sample (default 500) and classify each as:
       * "untradeable"        → ticker not tradeable per _is_tradeable_ticker
       * "other_codes_only"   → has rows, none are P or S (A/M/F/G/J/K)
       * "no_xml"             → ownership XML couldn't be located
       * "recovered"          → P/S rows INSERTED — this is a real miss
       * "fetch_failed"       → network error during re-fetch
     The sample's category mix extrapolates to the full missing population.
  4. Reports duplicates. The signals UNIQUE constraint forbids exact dupes,
     so this is a sanity histogram: median / p99 / max rows-per-accession.
     A single huge filing (~120 rows) is normal — institutional co-filings
     can disclose 100+ transactions in one accession. We only warn if the
     max is >> p99 by a wide margin, which would suggest a parser bug.

Usage:
  python -m scripts.audit_backfill                       # default 2015-01-01..2020-12-31
  python -m scripts.audit_backfill --since 2017-01-01 --until 2020-12-31
  python -m scripts.audit_backfill --no-recover          # report-only, no SEC traffic
  python -m scripts.audit_backfill --sample 0            # recover ALL missing (slow!)
"""
from __future__ import annotations

import argparse
import logging
import random
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import httpx

from trading_bot import config
from trading_bot.db import connect
from trading_bot.sources.edgar import (
    _PARALLEL_WORKERS,
    _fetch_filing_xml,
    _insert_signals,
    _load_quarter_index,
    _parse_form4_xml,
)

logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("audit")
log.setLevel(logging.INFO)


def _expected_accessions(client: httpx.Client, since: date, until: date) -> dict[str, dict]:
    """Return {adsh: hit} for every Form 4 entry filed in [since, until].
    `hit` has the same shape edgar._fetch_filing_xml expects (adsh, ciks, file_date).
    """
    out: dict[str, dict] = {}
    cur_year, cur_qtr = since.year, (since.month - 1) // 3 + 1
    end_year, end_qtr = until.year, (until.month - 1) // 3 + 1
    while (cur_year, cur_qtr) <= (end_year, end_qtr):
        log.info("Loading %d-Q%d index", cur_year, cur_qtr)
        for e in _load_quarter_index(client, cur_year, cur_qtr):
            d = date.fromisoformat(e["file_date"])
            if since <= d <= until:
                out[e["adsh"]] = e
        cur_qtr += 1
        if cur_qtr > 4:
            cur_qtr, cur_year = 1, cur_year + 1
    return out


def _have_accessions(since: date, until: date) -> set[str]:
    """Distinct Form 4 accessions in the DB with filed_at in [since, until]."""
    sql = """
      SELECT DISTINCT accession FROM signals
       WHERE source = 'form4'
         AND accession IS NOT NULL
         AND filed_at BETWEEN ? AND ?
    """
    with connect() as conn:
        return {r["accession"] for r in conn.execute(sql, (since.isoformat(), until.isoformat()))}


def _recover_missing(
    client: httpx.Client, missing: list[dict]
) -> dict[str, dict]:
    """Re-fetch + re-parse + INSERT OR IGNORE each missing hit. Returns
    per-accession results: {adsh: {status, inserted}}.
    """
    def _one(hit: dict) -> tuple[str, dict]:
        try:
            fetched = _fetch_filing_xml(client, hit)
            if fetched is None:
                return hit["adsh"], {"status": "no_xml", "inserted": 0}
            xml_url, xml_bytes = fetched
            rows = list(_parse_form4_xml(xml_bytes, hit, xml_url))
            if not rows:
                return hit["adsh"], {"status": "untradeable", "inserted": 0}
            buys = [r for r in rows if r["transaction_code"] in config.PURCHASE_TRANSACTION_CODES]
            sells = [r for r in rows if r["transaction_code"] in config.SELL_TRANSACTION_CODES]
            inserted = (_insert_signals(buys) if buys else 0) + (_insert_signals(sells) if sells else 0)
            if inserted > 0:
                return hit["adsh"], {"status": "recovered", "inserted": inserted}
            # Parsed rows but none were P or S — expected (other codes filtered).
            return hit["adsh"], {"status": "other_codes_only", "inserted": 0}
        except Exception as e:
            return hit["adsh"], {"status": "fetch_failed", "inserted": 0, "error": str(e)}

    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=_PARALLEL_WORKERS) as pool:
        for adsh, r in pool.map(_one, missing):
            results[adsh] = r
    return results


def _duplicate_report(since: date, until: date, top_n: int = 10) -> None:
    """Report duplicate-related sanity stats.

    The UNIQUE constraint prevents exact dupes at the row level. What we can
    still surface is accessions with anomalously high row counts (e.g., a
    parser bug emitting the same transaction multiple times under different
    filer keys would inflate this).
    """
    sql = """
      SELECT accession, COUNT(*) AS n FROM signals
       WHERE source = 'form4'
         AND filed_at BETWEEN ? AND ?
       GROUP BY accession
       ORDER BY n DESC
    """
    with connect() as conn:
        counts = [(r["accession"], r["n"]) for r in conn.execute(sql, (since.isoformat(), until.isoformat()))]

    if not counts:
        log.info("No signals in range — duplicate report skipped.")
        return

    rows_per_filing = sorted([n for _, n in counts], reverse=True)
    median = rows_per_filing[len(rows_per_filing) // 2]
    p99 = rows_per_filing[len(rows_per_filing) // 100]
    max_n = rows_per_filing[0]
    log.info("Per-filing rows: median=%d, p99=%d, max=%d", median, p99, max_n)
    # Real outliers — institutional co-filings legitimately have ~100-200 rows
    # in a single accession. Only flag if max is wildly above p99 (e.g. 10x),
    # which would indicate a parser-emit-duplicate bug.
    if max_n > 500 and max_n > p99 * 10:
        log.warning("Outlier filings (top %d by row count):", top_n)
        for adsh, n in counts[:top_n]:
            log.warning("  %s : %d rows", adsh, n)
    else:
        log.info("Row counts look normal (max within %dx of p99).", max_n // max(p99, 1))


def run_audit(
    *, since: date, until: date, sample: int = 500, no_recover: bool = False
) -> dict:
    """Run the audit and return a summary dict. Prints a human report to stdout.

    Args mirror the CLI flags. Returns:
      {"expected": int, "have": int, "missing": int,
       "status_counts": {status: n}, "inserted": int, "sampled": bool}
    """
    headers = {"User-Agent": config.SEC_USER_AGENT}
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=12)
    with httpx.Client(timeout=15.0, headers=headers, http2=False, limits=limits) as client:
        expected = _expected_accessions(client, since, until)
        log.info("Expected Form 4 accessions in range: %d", len(expected))
        have = _have_accessions(since, until)
        log.info("In DB so far                      : %d", len(have))

        missing_adshs = sorted(set(expected) - have)
        log.info("Missing from DB                   : %d", len(missing_adshs))

        results: dict[str, dict] = {}
        sampled = False
        if missing_adshs and not no_recover:
            if sample > 0 and len(missing_adshs) > sample:
                random.seed(42)
                pick = random.sample(missing_adshs, sample)
                log.info("Sampling %d of %d missing for recovery classification",
                         len(pick), len(missing_adshs))
                sampled = True
            else:
                pick = missing_adshs
                log.info("Re-fetching all %d missing accessions...", len(pick))
            results = _recover_missing(client, [expected[a] for a in pick])

    status_counts: Counter[str] = Counter()
    total_inserted = 0
    for r in results.values():
        status_counts[r["status"]] += 1
        total_inserted += r.get("inserted", 0)

    print("\n" + "=" * 72)
    print(f"  AUDIT  {since} -> {until}")
    print("=" * 72)
    print(f"  Expected (in EDGAR index)  : {len(expected):>10,}")
    print(f"  Present in DB              : {len(have):>10,}")
    print(f"  Missing from DB            : {len(missing_adshs):>10,}")
    if results:
        sample_size = len(results)
        header = ("Recovery classification (sampled, extrapolated)"
                  if sampled else "Recovery classification (full)")
        print(f"  {header}:")
        for status, n in sorted(status_counts.items(), key=lambda x: -x[1]):
            pct = 100.0 * n / sample_size
            est_total = int(round(pct / 100.0 * len(missing_adshs))) if sampled else n
            extrap = f"  -> ~{est_total:>7,} in full pop." if sampled else ""
            print(f"    {status:<22} : {n:>5,}  ({pct:>5.1f}%){extrap}")
        print(f"  Signal rows inserted       : {total_inserted:>10,}")
    print()
    _duplicate_report(since, until)
    print("=" * 72, flush=True)

    return {
        "expected": len(expected),
        "have": len(have),
        "missing": len(missing_adshs),
        "status_counts": dict(status_counts),
        "inserted": total_inserted,
        "sampled": sampled,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2015-01-01")
    ap.add_argument("--until", default="2020-12-31")
    ap.add_argument("--no-recover", action="store_true",
                    help="Skip re-fetching missing accessions (report-only mode).")
    ap.add_argument("--sample", type=int, default=500,
                    help="Random sample size for recovery classification. "
                         "Use 0 to recover all missing (slow on large gaps).")
    args = ap.parse_args()
    run_audit(
        since=date.fromisoformat(args.since),
        until=date.fromisoformat(args.until),
        sample=args.sample,
        no_recover=args.no_recover,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
