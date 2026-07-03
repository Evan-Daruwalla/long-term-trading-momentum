"""Re-ingest filings that were dropped by WinError 10035 during the HTTP/2 era.

Reads accession numbers from var/ingest_backfill.out's `WinError 10035` warnings,
looks each up in the relevant cached quarterly index to recover its CIK and
file_date, then runs them back through the same fetch+parse+insert pipeline.
INSERT OR IGNORE on the signals table makes this safe to re-run.

Usage:
  python -m scripts.audit_dropped_filings
"""
from __future__ import annotations

import logging
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import httpx

from trading_bot import config
from trading_bot.sources.edgar import (
    _PARALLEL_WORKERS,
    _fetch_filing_xml,
    _insert_signals,
    _load_quarter_index,
    _parse_form4_xml,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("audit")

_LOG_PATH = config.VAR_DIR / "ingest_backfill.out"
_ACCESSION_RE = re.compile(
    r"Failed to process filing (\d{10}-\d{2}-\d{6}): \[WinError 10035\]"
)


def _dropped_accessions() -> list[str]:
    """Unique accession numbers logged as WinError 10035 drops, sorted."""
    text = _LOG_PATH.read_text(encoding="utf-8", errors="replace")
    return sorted(set(_ACCESSION_RE.findall(text)))


def _resolve_hits(
    client: httpx.Client, accessions: list[str]
) -> tuple[list[dict], list[str]]:
    """For each accession build a hit dict {adsh, ciks, file_date} by looking
    it up in the quarterly index. Returns (found_hits, unresolved_accessions).

    Accession's filer year is encoded as "-YY-", which narrows the lookup to
    one calendar year. We try each quarter in order (Q1..Q4) and cache the
    index by quarter to avoid repeat fetches.
    """
    by_year: dict[int, list[str]] = {}
    for adsh in accessions:
        yy = int(adsh.split("-")[1])
        year = 2000 + yy if yy < 70 else 1900 + yy
        by_year.setdefault(year, []).append(adsh)

    found: list[dict] = []
    unresolved: list[str] = []
    for year in sorted(by_year):
        want = set(by_year[year])
        # Build (adsh -> entry) index for the whole year, lazy-loaded by quarter.
        for qtr in (1, 2, 3, 4):
            if not want:
                break
            log.info("Loading %d-Q%d index to resolve %d accessions", year, qtr, len(want))
            entries = _load_quarter_index(client, year, qtr)
            for e in entries:
                if e["adsh"] in want:
                    found.append(e)
                    want.discard(e["adsh"])
        unresolved.extend(sorted(want))
    return found, unresolved


def _process_hit(client: httpx.Client, hit: dict) -> dict | None:
    """Mirror of edgar._poll_chunk's _process, but inline so we can run it
    standalone. Returns the counts dict or None if the filing was non-tradeable.
    """
    try:
        fetched = _fetch_filing_xml(client, hit)
        if fetched is None:
            return {"adsh": hit["adsh"], "status": "no_xml"}
        xml_url, xml_bytes = fetched
        rows = list(_parse_form4_xml(xml_bytes, hit, xml_url))
        buys = [r for r in rows if r["transaction_code"] in config.PURCHASE_TRANSACTION_CODES]
        sells = [r for r in rows if r["transaction_code"] in config.SELL_TRANSACTION_CODES]
        n_buys = _insert_signals(buys) if buys else 0
        n_sells = _insert_signals(sells) if sells else 0
        return {
            "adsh": hit["adsh"],
            "status": "parsed" if rows else "untradeable",
            "buys_inserted": n_buys,
            "sells_inserted": n_sells,
        }
    except Exception as e:
        log.warning("Re-ingest failed for %s: %s", hit["adsh"], e)
        return {"adsh": hit["adsh"], "status": "error", "error": str(e)}


def main() -> int:
    accessions = _dropped_accessions()
    log.info("Found %d unique WinError 10035 drops in log", len(accessions))
    if not accessions:
        log.info("Nothing to audit. Done.")
        return 0

    headers = {"User-Agent": config.SEC_USER_AGENT}
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=12)
    with httpx.Client(
        timeout=15.0, headers=headers, http2=False, limits=limits,
    ) as client:
        hits, unresolved = _resolve_hits(client, accessions)
        log.info("Resolved %d hits (%d unresolved)", len(hits), len(unresolved))
        if unresolved:
            log.warning("Unresolved sample: %s", unresolved[:5])

        with ThreadPoolExecutor(max_workers=_PARALLEL_WORKERS) as pool:
            results = list(pool.map(lambda h: _process_hit(client, h), hits))

    by_status: dict[str, int] = {}
    total_buys = total_sells = 0
    for r in results:
        if r is None:
            continue
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        total_buys += r.get("buys_inserted", 0) or 0
        total_sells += r.get("sells_inserted", 0) or 0

    log.info("=== Audit results ===")
    for k, v in sorted(by_status.items()):
        log.info("  %-12s : %d", k, v)
    log.info("  buys inserted : %d", total_buys)
    log.info("  sells inserted: %d", total_sells)
    log.info("  unresolved    : %d", len(unresolved))
    return 0


if __name__ == "__main__":
    sys.exit(main())
