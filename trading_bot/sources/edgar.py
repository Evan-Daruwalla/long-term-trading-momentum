"""SEC EDGAR Form 4 ingestion (Phase 1).

Two-step pipeline per filing:
  1. Discover Form 4s in a date range from EDGAR's quarterly form.idx
     (cached per-quarter to disk). Each hit is metadata only: accession
     number, CIK, file date.
  2. For each hit, fetch the submission .txt and parse the ownership XML.

Only open-market purchases (transaction code 'P') are kept as conviction
signals; sells and routine compensation events (A, M, F, G, ...) are
parsed but discarded so we don't pollute the scoring stream.
"""
from __future__ import annotations

import json
import logging
import re
import threading
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from typing import Iterable, Iterator

import httpx

from trading_bot import config
from trading_bot.db import connect


log = logging.getLogger(__name__)

_MAX_RETRY_ATTEMPTS = 8
_RETRY_BASE_DELAY_SECONDS = 2.0

# SEC fair-access policy caps clients at 10 req/sec. We push to 9.5 with the
# token bucket guaranteeing minimum spacing; remaining headroom absorbs the
# occasional retry burst without tripping a 429.
_RATE_LIMIT_PER_SEC = 9.5
# Workers per chunk's parallel filing fetch. Each worker keeps its own HTTP/1.1
# connection in the httpx pool; the rate limiter still caps aggregate req/sec.
_PARALLEL_WORKERS = 8

# SGML wrapper extraction: EDGAR submission .txt files contain all docs
# inline as SGML. For Form 4 the XML lives inside a single <XML>...</XML>
# block (modern filings, ~99% of post-2008). _XML_BLOCK_RE matches that.
_XML_BLOCK_RE = re.compile(rb"<XML>\s*(.*?)\s*</XML>", re.DOTALL)

# On-disk cache of EDGAR's quarterly form index. One .idx file per quarter,
# fetched once and reused for every weekly chunk that overlaps the quarter.
# Past quarters are immutable; the current quarter's idx is refreshed if
# stale (see _load_quarter_index).
_INDEX_CACHE_DIR = config.VAR_DIR / "edgar_index_cache"
_QUARTER_INDEX_FRESH_SECONDS = 4 * 3600  # 4h staleness for current quarter


class _TokenBucket:
    """Thread-safe minimum-interval throttle. Every `acquire()` call sleeps
    until at least `interval` seconds have passed since the previous acquire.
    """

    def __init__(self, rate_per_sec: float):
        self.interval = 1.0 / rate_per_sec
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait = self.interval - (now - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()


_rate_limiter = _TokenBucket(_RATE_LIMIT_PER_SEC)


def _get_with_retry(
    client: httpx.Client, url: str, *, params: dict | None = None
) -> httpx.Response:
    """GET with rate limiting and exponential-backoff retry on transient errors.

    Retries on 429, 5xx, and httpx.TimeoutException (connect/read/write).
    Everything else (success or 4xx permanent) returns immediately.
    """
    last_response: httpx.Response | None = None
    for attempt in range(1, _MAX_RETRY_ATTEMPTS + 1):
        _rate_limiter.acquire()
        try:
            r = client.get(url, params=params)
        except httpx.TimeoutException as e:
            if attempt >= _MAX_RETRY_ATTEMPTS:
                raise
            wait = _RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1))
            log.warning(
                "Timeout on %s (attempt %d/%d): %s, retrying in %.1fs",
                url, attempt, _MAX_RETRY_ATTEMPTS, e, wait,
            )
            time.sleep(wait)
            continue

        if r.status_code != 429 and r.status_code < 500:
            r.raise_for_status()
            return r
        last_response = r
        if attempt < _MAX_RETRY_ATTEMPTS:
            # 429 honors Retry-After if present, else exponential.
            retry_after = r.headers.get("Retry-After") if r.status_code == 429 else None
            try:
                wait = float(retry_after) if retry_after else _RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1))
            except ValueError:
                wait = _RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1))
            log.warning(
                "SEC %s on %s (attempt %d/%d), retrying in %.1fs",
                r.status_code, url, attempt, _MAX_RETRY_ATTEMPTS, wait,
            )
            time.sleep(wait)
    assert last_response is not None  # all retries exhausted via status path
    last_response.raise_for_status()
    return last_response  # unreachable

_OFFICER_TITLE_PATTERNS = (
    "chief executive officer", "ceo",
    "chief financial officer", "cfo",
)


def poll(*, since: date, until: date, chunk_days: int = 7) -> dict:
    """Poll EDGAR for Form 4 filings in [since, until]. Idempotent.

    The range is auto-chunked into 7-day sub-windows. Smaller chunks give
    progress logs more granularity and bound the rerun cost on a chunk-level
    failure; the quarterly index lookup (see _search_form4) is shared across
    all chunks in the same quarter via on-disk cache.
    """
    stats = {"scanned": 0, "parsed": 0, "purchases_stored": 0, "sells_stored": 0, "errors": 0}
    headers = {"User-Agent": config.SEC_USER_AGENT}
    total_days = (until - since).days + 1
    log.info("Backfill range: %s -> %s (%d days)", since, until, total_days)

    # 15s timeout: SEC normally responds in <1s. Caps the bleed when a TCP
    # connection goes dead.
    # HTTP/1.1 with a connection pool, NOT HTTP/2. HTTP/2 multiplexes all
    # parallel worker requests over a single TCP connection on Windows,
    # which causes (a) WSAEWOULDBLOCK (WinError 10035) when h2's flow-
    # control window fills and (b) silent stalls when the server-side
    # stream dies but the OS-level TCP session stays open. HTTP/1.1 gives
    # each worker its own keepalive connection from the pool; sized for
    # 8 workers + headroom.
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=12)
    with httpx.Client(
        timeout=15.0, headers=headers, http2=False, limits=limits,
    ) as client:
        cur = since
        while cur <= until:
            chunk_end = min(cur + timedelta(days=chunk_days - 1), until)
            # Total% reflects days completed BEFORE this chunk starts. After
            # the chunk finishes, the next iteration's line shows the bumped
            # value, which gives a natural "before/after" reading in the log.
            days_done = (cur - since).days
            total_pct = 100.0 * days_done / total_days
            log.info(
                "Polling EDGAR chunk %s -> %s  (overall %.1f%%)",
                cur, chunk_end, total_pct,
            )
            try:
                _poll_chunk(client, stats, cur, chunk_end)
            except Exception as e:
                # A chunk-level failure (search-index 5xx after exhausted retries,
                # network blip, etc.) shouldn't kill a multi-hour backfill.
                # Log, increment, and move on; INSERT OR IGNORE means we can
                # safely re-run the same range later to fill the gap.
                stats["errors"] += 1
                log.error("Chunk %s -> %s failed entirely: %s", cur, chunk_end, e)
            cur = chunk_end + timedelta(days=1)

    log.info("Backfill complete: %s -> %s  (overall 100.0%%)", since, until)
    _record_poll(until)
    return stats


def _poll_chunk(
    client: httpx.Client, stats: dict, since: date, until: date
) -> None:
    """Search the chunk's hits serially, then process them in parallel."""
    hits = list(_search_form4(client, since, until))
    if not hits:
        log.info("  chunk %s -> %s: 0 filings", since, until)
        return
    total_hits = len(hits)
    log.info("  chunk %s -> %s: %d filings", since, until, total_hits)

    def _process(hit: dict):
        try:
            fetched = _fetch_filing_xml(client, hit)
            if fetched is None:
                return None
            xml_url, xml_bytes = fetched
            rows = list(_parse_form4_xml(xml_bytes, hit, xml_url))
            buys = [r for r in rows if r["transaction_code"] in config.PURCHASE_TRANSACTION_CODES]
            sells = [r for r in rows if r["transaction_code"] in config.SELL_TRANSACTION_CODES]
            return {"parsed": bool(rows), "buys": buys, "sells": sells, "adsh": hit.get("adsh")}
        except Exception as e:
            log.warning("Failed to process filing %s: %s", hit.get("adsh"), e)
            return "ERROR"

    # Log progress at fixed milestones so each chunk gets ~5 update lines no
    # matter its size. Cleaner than mod-N logging which produces irregular %s.
    milestones = [0.20, 0.40, 0.60, 0.80, 1.00]
    next_idx = 0
    processed = 0

    with ThreadPoolExecutor(max_workers=_PARALLEL_WORKERS) as pool:
        for result in pool.map(_process, hits):
            stats["scanned"] += 1
            processed += 1
            if next_idx < len(milestones) and processed / total_hits >= milestones[next_idx]:
                log.info(
                    "    chunk progress: %d/%d (%.0f%%)",
                    processed, total_hits, milestones[next_idx] * 100,
                )
                next_idx += 1
            if result == "ERROR":
                stats["errors"] += 1
                continue
            if result is None:
                continue
            if result["parsed"]:
                stats["parsed"] += 1
            if result["buys"]:
                stats["purchases_stored"] += _insert_signals(result["buys"])
            if result["sells"]:
                stats["sells_stored"] += _insert_signals(result["sells"])


def _search_form4(
    client: httpx.Client, since: date, until: date
) -> Iterator[dict]:
    """Yield Form 4 filings in [since, until] from cached quarterly indexes.

    The legacy efts.sec.gov/LATEST/search-index endpoint is unreliable
    (~10% 500-error rate during US market hours, also the source of the
    silent-stall hangs we hit). EDGAR's nightly-published quarterly form
    index covers the same data, lives on www.sec.gov/Archives (much more
    stable), and is one fetch per quarter — naturally cacheable since past
    quarters are immutable.
    """
    cur_year, cur_qtr = since.year, _quarter_of(since.month)
    end_year, end_qtr = until.year, _quarter_of(until.month)
    while (cur_year, cur_qtr) <= (end_year, end_qtr):
        for entry in _load_quarter_index(client, cur_year, cur_qtr):
            d = date.fromisoformat(entry["file_date"])
            if since <= d <= until:
                yield entry
        cur_qtr += 1
        if cur_qtr > 4:
            cur_qtr, cur_year = 1, cur_year + 1


def _quarter_of(month: int) -> int:
    return (month - 1) // 3 + 1


def _quarter_end(year: int, qtr: int) -> date:
    last_month = qtr * 3
    return date(year, last_month, 31 if last_month in (3, 12) else 30)


def _load_quarter_index(
    client: httpx.Client, year: int, qtr: int
) -> list[dict]:
    """Return the parsed list of Form 4 entries for a quarter. Disk-cached.

    Past quarters are cached indefinitely (the index never changes once the
    quarter ends). The current quarter's cache is refreshed if older than
    _QUARTER_INDEX_FRESH_SECONDS.
    """
    cache_file = _INDEX_CACHE_DIR / f"form4_{year}_QTR{qtr}.json"
    is_past_quarter = _quarter_end(year, qtr) < date.today()
    if cache_file.exists():
        if is_past_quarter or (
            time.time() - cache_file.stat().st_mtime < _QUARTER_INDEX_FRESH_SECONDS
        ):
            return json.loads(cache_file.read_text())

    url = f"https://www.sec.gov/Archives/edgar/full-index/{year}/QTR{qtr}/form.idx"
    log.info("Fetching EDGAR index %d-Q%d", year, qtr)
    r = _get_with_retry(client, url)
    entries = _parse_form_idx(r.text)
    log.info("  cached %d Form 4 entries from %d-Q%d", len(entries), year, qtr)
    _INDEX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(entries))
    return entries


def _parse_form_idx(text: str) -> list[dict]:
    """Parse SEC quarterly form.idx, returning only originals of Form 4.

    Format (fixed-width columns, header above a dashed separator):
        Form Type   Company Name                CIK         Date Filed  Filename
        4           ACME CORP                   0000123456  2020-01-02  edgar/data/123456/0000123456-20-000001-index.htm
    Form type is in column [0:12]; the rest can have variable internal
    whitespace, so rsplit picks off the trailing CIK / date / filename.
    """
    out: list[dict] = []
    in_body = False
    for line in text.splitlines():
        if not in_body:
            if line.startswith("---"):
                in_body = True
            continue
        if line[:12].strip() != "4":  # excludes 4/A amendments
            continue
        rest = line[12:].rsplit(None, 3)
        if len(rest) != 4:
            continue
        _company, cik_s, date_s, filename = rest
        m = re.search(r"(\d{10}-\d{2}-\d{6})", filename)
        if not m:
            continue
        out.append({
            "adsh": m.group(1),
            "ciks": [cik_s.strip()],
            "file_date": date_s.strip(),
        })
    return out


def _extract_xml_from_sgml(sgml: bytes) -> bytes | None:
    """Pull the Form 4 XML out of a complete SGML submission.

    Submissions wrap every contained doc in <DOCUMENT>...<XML>...</XML>...
    For Form 4 there's one such block. The captured payload usually starts
    with the `<?xml ...?>` declaration, but some filings have leading
    whitespace/comments — strip back to `<?xml` if present.
    """
    m = _XML_BLOCK_RE.search(sgml)
    if not m:
        return None
    payload = m.group(1).strip()
    if not payload.startswith(b"<?xml"):
        idx = payload.find(b"<?xml")
        if idx >= 0:
            payload = payload[idx:]
    return payload


def _fetch_filing_xml(
    client: httpx.Client, hit: dict
) -> tuple[str, bytes] | None:
    """Fetch the ownership XML for a filing. Returns (url, bytes) or None.

    Fast path (1 HTTP call): pull `{accession}.txt`, the full SGML submission
    with all docs inline. For Form 4 this is typically <15KB and contains the
    XML in a single <XML> block. Confirmed working back to 2012-era filings.

    Slow path (2 HTTP calls): if the .txt fetch fails or the XML can't be
    extracted, fall back to the legacy index.json + xml approach. This covers
    edge-case filings (very old SGML-only Form 4s, malformed submissions).

    A previous "primary_doc.xml fast path" was reverted on 2026-04-28 because
    the filename isn't predictable. The .txt path uses only the accession
    number, which IS predictable and stable across EDGAR's history.
    """
    if not hit["ciks"]:
        return None
    cik = int(hit["ciks"][0])  # int() drops leading zeros for the URL
    accession_nodashes = hit["adsh"].replace("-", "")
    folder = f"{config.EDGAR_ARCHIVES_BASE}/{cik}/{accession_nodashes}"
    txt_url = f"{folder}/{hit['adsh']}.txt"

    # Fast path: full SGML submission in one request.
    try:
        r = _get_with_retry(client, txt_url)
        xml = _extract_xml_from_sgml(r.content)
        if xml:
            return txt_url, xml
        log.debug("No <XML> block in %s, falling back to slow path", hit["adsh"])
    except httpx.HTTPStatusError as e:
        log.debug(
            ".txt fast path %s for %s, falling back",
            e.response.status_code, hit["adsh"],
        )

    # Slow path: index.json + xml.
    try:
        r = _get_with_retry(client, f"{folder}/index.json")
    except httpx.HTTPStatusError as e:
        log.warning(
            "index.json unavailable for %s (%s)",
            hit["adsh"], e.response.status_code,
        )
        return None
    files = (r.json().get("directory") or {}).get("item") or []

    for preferred in ("primary_doc.xml",):
        if any(f["name"] == preferred for f in files):
            xml_url = f"{folder}/{preferred}"
            return xml_url, _get_with_retry(client, xml_url).content

    for f in files:
        n = f["name"]
        if n.lower().endswith(".xml") and n.lower() != "filingsummary.xml":
            xml_url = f"{folder}/{n}"
            try:
                return xml_url, _get_with_retry(client, xml_url).content
            except httpx.HTTPStatusError as e:
                log.warning(
                    "XML fetch failed for %s (%s)",
                    hit["adsh"], e.response.status_code,
                )
                return None
    return None


def _parse_form4_xml(
    xml_bytes: bytes, hit: dict, xml_url: str
) -> Iterator[dict]:
    """Yield one row per (reporting owner, non-derivative transaction)."""
    root = ET.fromstring(xml_bytes)
    # Strip any default namespace so XPath stays simple.
    for el in root.iter():
        if isinstance(el.tag, str) and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]

    if root.tag != "ownershipDocument":
        return

    issuer = root.find("issuer")
    issuer_name = _text(issuer, "issuerName")
    ticker = _text(issuer, "issuerTradingSymbol")
    issuer_cik = _text(issuer, "issuerCik")
    if not _is_tradeable_ticker(ticker):
        return  # private/untradeable issuer — skip

    owners = root.findall("reportingOwner")
    txns = root.findall("nonDerivativeTable/nonDerivativeTransaction")
    if not owners or not txns:
        return

    for owner in owners:
        owner_id = owner.find("reportingOwnerId")
        rel = owner.find("reportingOwnerRelationship")
        filer_cik = _text(owner_id, "rptOwnerCik")
        filer_name = _text(owner_id, "rptOwnerName")
        filer_title = _text(rel, "officerTitle")
        is_director = _bool(_text(rel, "isDirector"))
        is_officer = _bool(_text(rel, "isOfficer"))
        is_ten = _bool(_text(rel, "isTenPercentOwner"))

        if not filer_name:
            continue

        for txn in txns:
            code = _text(txn, "transactionCoding/transactionCode")
            shares = _float(_text(txn, "transactionAmounts/transactionShares/value"))
            price = _float(
                _text(txn, "transactionAmounts/transactionPricePerShare/value")
            )
            txn_date = _text(txn, "transactionDate/value")
            a_d = _text(
                txn, "transactionAmounts/transactionAcquiredDisposedCode/value"
            )

            yield {
                "source": "form4",
                "accession": hit["adsh"],
                "filed_at": hit.get("file_date"),
                "transaction_date": txn_date,
                "ticker": ticker.upper(),
                "issuer_name": issuer_name,
                "issuer_cik": issuer_cik,
                "filer_name": filer_name,
                "filer_cik": filer_cik,
                "filer_title": filer_title,
                "is_director": _opt_int(is_director),
                "is_officer": _opt_int(is_officer),
                "is_ten_percent_owner": _opt_int(is_ten),
                "transaction_code": code,
                "shares": shares,
                "price_per_share": price,
                "total_value": (shares * price)
                    if (shares is not None and price is not None) else None,
                "acquired_disposed": a_d,
                "raw_xml_url": xml_url,
            }


def _insert_signals(rows: Iterable[dict]) -> int:
    rows = list(rows)
    if not rows:
        return 0
    now = datetime.now(timezone.utc).isoformat()
    sql = """
      INSERT OR IGNORE INTO signals (
        source, accession, filed_at, transaction_date, ticker,
        issuer_name, issuer_cik, filer_name, filer_cik, filer_title,
        is_director, is_officer, is_ten_percent_owner,
        transaction_code, shares, price_per_share, total_value,
        acquired_disposed, raw_xml_url, ingested_at
      ) VALUES (
        :source, :accession, :filed_at, :transaction_date, :ticker,
        :issuer_name, :issuer_cik, :filer_name, :filer_cik, :filer_title,
        :is_director, :is_officer, :is_ten_percent_owner,
        :transaction_code, :shares, :price_per_share, :total_value,
        :acquired_disposed, :raw_xml_url, :ingested_at
      )
    """
    inserted = 0
    with connect() as conn:
        for r in rows:
            cur = conn.execute(sql, {**r, "ingested_at": now})
            inserted += max(cur.rowcount, 0)
    return inserted


def _record_poll(until: date) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute(
            "INSERT INTO ingest_state(source, last_poll_at, last_filed_at) "
            "VALUES (?, ?, ?) "
            "ON CONFLICT(source) DO UPDATE SET "
            "  last_poll_at=excluded.last_poll_at, "
            "  last_filed_at=excluded.last_filed_at",
            ("form4", now, until.isoformat()),
        )


def is_ceo_or_cfo(title: str | None) -> bool:
    """Heuristic for the +1 CEO/CFO scoring bonus (used in Phase 2)."""
    if not title:
        return False
    t = title.lower()
    return any(p in t for p in _OFFICER_TITLE_PATTERNS)


_NON_TICKER_VALUES = {"NONE", "N/A", "NA", "PRIVATE", "-"}


def _is_tradeable_ticker(t: str | None) -> bool:
    if not t:
        return False
    t = t.strip().upper()
    if t in _NON_TICKER_VALUES:
        return False
    # Real US tickers are 1-5 alphanumeric chars, sometimes with a dot suffix.
    return 1 <= len(t) <= 8 and all(c.isalnum() or c in ".-" for c in t)


# --- small helpers -----------------------------------------------------------

def _text(parent, path: str) -> str | None:
    if parent is None:
        return None
    el = parent.find(path)
    if el is None or el.text is None:
        return None
    return el.text.strip() or None


def _float(s: str | None) -> float | None:
    if s is None:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _bool(s: str | None) -> bool | None:
    if s is None:
        return None
    return s.strip() in ("1", "true", "True")


def _opt_int(b: bool | None) -> int | None:
    return int(b) if b is not None else None
