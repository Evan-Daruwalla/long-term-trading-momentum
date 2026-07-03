"""SEC EDGAR XBRL company-facts ingest.

For every ticker with cached prices, fetches the company's XBRL facts
JSON from data.sec.gov and persists the concepts needed for quality
factor calculation, with filing dates so we can compute POINT-IN-TIME
values later (no lookahead bias).

Why this exists: the yfinance .info-based quality factor is a current
snapshot and gives lookahead-biased backtest results. To know whether
quality actually adds alpha, we need to know what each company's ROE/D/E
/etc. was on, say, 2018-06-01 — i.e., the most recent filing as of that
date. That requires the filed_date, not just the latest reported value.

SEC compliance:
  - Max 10 requests/sec per IP (we use 8 to be safe)
  - Identifying User-Agent required by SEC fair-use policy
  - Caches per ticker so re-runs only fetch what's missing

Schema:
  xbrl_facts (
    ticker      TEXT,
    cik         INTEGER,
    concept     TEXT,       -- e.g. 'NetIncomeLoss', 'Revenues'
    period_end  TEXT,       -- ISO date, end of the reporting period
    filed       TEXT,       -- ISO date, when SEC received the filing
    fy          INTEGER,    -- fiscal year
    fp          TEXT,       -- fiscal period: FY, Q1, Q2, Q3
    form        TEXT,       -- 10-K, 10-Q, etc.
    accn        TEXT,       -- accession number (filing id)
    val         REAL,
    PRIMARY KEY (ticker, concept, period_end, filed, accn)
  )

Concepts pulled (us-gaap namespace):
  - Revenues / RevenueFromContractWithCustomerExcludingAssessedTax
  - NetIncomeLoss
  - StockholdersEquity
  - Assets
  - LongTermDebt + LongTermDebtCurrent (sum = total debt approx)
  - OperatingIncomeLoss
  - GrossProfit

Usage:
  python -m scripts.momentum.warm_xbrl --limit 20      # smoke
  python -m scripts.momentum.warm_xbrl                  # full
  python -m scripts.momentum.warm_xbrl --refresh AAPL   # force re-fetch one
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime, timezone
from typing import Iterator

import urllib.request
import urllib.error

from trading_bot.config import DB_PATH

# SEC API config
SEC_USER_AGENT = "trading-bot-research evan.research@gmail.com"
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
RATE_LIMIT_DELAY = 0.13     # ~7.7 req/sec, under SEC's 10/sec cap

# Concepts to extract from us-gaap namespace
CONCEPTS = [
    # Existing (v1 quality_xbrl)
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "NetIncomeLoss",
    "StockholdersEquity",
    "Assets",
    "LongTermDebt",
    "LongTermDebtNoncurrent",
    "LongTermDebtCurrent",
    "OperatingIncomeLoss",
    "GrossProfit",
    "AssetsCurrent",
    "LiabilitiesCurrent",
    # Added for quality_xbrl_v2 (FCF / Piotroski components)
    "NetCashProvidedByUsedInOperatingActivities",   # CFO
    "PaymentsToAcquirePropertyPlantAndEquipment",   # CapEx
    "CashAndCashEquivalentsAtCarryingValue",
    "PropertyPlantAndEquipmentNet",
    "CommonStockSharesOutstanding",                  # for dilution detection
    "CommonStockSharesIssued",
]


def _http_get(url: str) -> bytes | None:
    """One GET with SEC user-agent. Returns body or None on 404."""
    req = urllib.request.Request(
        url, headers={"User-Agent": SEC_USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        if e.code in (403, 429):
            print(f"  HTTP {e.code} on {url} — sleeping 60s", flush=True)
            time.sleep(60)
            return _http_get(url)
        print(f"  HTTP {e.code} on {url}: {e.reason}", flush=True)
        return None
    except Exception as e:
        print(f"  Error fetching {url}: {e}", flush=True)
        return None


def _fetch_ticker_cik_map() -> dict[str, int]:
    """Returns {ticker: cik}. Pulls the SEC's official mapping file."""
    print(f"Fetching ticker->CIK map from {TICKERS_URL}", flush=True)
    body = _http_get(TICKERS_URL)
    if not body:
        raise SystemExit("Could not fetch SEC ticker mapping")
    data = json.loads(body)
    out: dict[str, int] = {}
    for row in data.values():
        out[row["ticker"].upper()] = int(row["cik_str"])
    print(f"  Loaded {len(out):,} ticker->CIK entries", flush=True)
    return out


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS xbrl_facts (
            ticker      TEXT NOT NULL,
            cik         INTEGER NOT NULL,
            concept     TEXT NOT NULL,
            period_end  TEXT NOT NULL,
            filed       TEXT NOT NULL,
            fy          INTEGER,
            fp          TEXT,
            form        TEXT,
            accn        TEXT NOT NULL,
            val         REAL,
            PRIMARY KEY (ticker, concept, period_end, filed, accn)
        )"""
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_xbrl_ticker_filed "
        "ON xbrl_facts (ticker, filed)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_xbrl_concept_filed "
        "ON xbrl_facts (concept, filed)"
    )


def _all_cached_tickers(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT DISTINCT ticker FROM price_cache WHERE kind='close' ORDER BY ticker"
    ).fetchall()
    return [r[0] for r in rows]


def _tickers_with_xbrl(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT DISTINCT ticker FROM xbrl_facts").fetchall()
    return {r[0] for r in rows}


def _parse_facts(ticker: str, cik: int, facts_json: dict
                 ) -> Iterator[tuple]:
    """Yield (ticker, cik, concept, period_end, filed, fy, fp, form, accn, val)
    rows from a single companyfacts JSON. Only the concepts we care about,
    only USD-denominated (skips per-share-only items)."""
    facts = facts_json.get("facts", {})
    gaap = facts.get("us-gaap", {})
    for concept in CONCEPTS:
        item = gaap.get(concept)
        if not item:
            continue
        units = item.get("units", {})
        # Prefer USD; fall back to first numeric unit available
        usd_data = units.get("USD") or next(
            (v for k, v in units.items() if k != "shares"), None)
        if not usd_data:
            continue
        for entry in usd_data:
            yield (
                ticker, cik, concept,
                entry.get("end"),
                entry.get("filed"),
                entry.get("fy"),
                entry.get("fp"),
                entry.get("form"),
                entry.get("accn"),
                float(entry["val"]) if entry.get("val") is not None else None,
            )


def fetch_one(ticker: str, cik: int) -> list[tuple] | None:
    """Returns list of (ticker, cik, concept, ...) rows, or None on fetch fail.
    Empty list means SEC has the company but we extracted nothing useful."""
    url = FACTS_URL.format(cik=cik)
    body = _http_get(url)
    if body is None:
        return None
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return None
    return list(_parse_facts(ticker, cik, data))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None,
                    help="Limit tickers (smoke testing)")
    ap.add_argument("--refresh", default=None,
                    help="Force re-fetch a single ticker even if cached")
    ap.add_argument("--refresh-all", action="store_true",
                    help="Re-fetch every ticker (use when CONCEPTS list grows)")
    args = ap.parse_args()

    conn = sqlite3.connect(DB_PATH)
    _ensure_table(conn)

    cik_map = _fetch_ticker_cik_map()
    time.sleep(RATE_LIMIT_DELAY)

    if args.refresh:
        # Single ticker refresh path
        t = args.refresh.upper()
        if t not in cik_map:
            print(f"No CIK for {t} in SEC mapping")
            return 1
        print(f"Refreshing {t} (CIK {cik_map[t]})")
        conn.execute("DELETE FROM xbrl_facts WHERE ticker=?", (t,))
        rows = fetch_one(t, cik_map[t])
        if rows is not None:
            conn.executemany(
                "INSERT OR IGNORE INTO xbrl_facts "
                "(ticker,cik,concept,period_end,filed,fy,fp,form,accn,val) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
            conn.commit()
            print(f"  Inserted {len(rows)} rows")
        conn.close()
        return 0

    cached_tickers = _all_cached_tickers(conn)
    # Only fetch tickers that (a) have prices, (b) appear in SEC mapping.
    # With --refresh-all, ignore the already-done check (use when CONCEPTS
    # list expanded and we need to backfill new concepts).
    if args.refresh_all:
        done = set()
        print("--refresh-all: re-fetching every cached ticker", flush=True)
    else:
        done = _tickers_with_xbrl(conn)
    todo = [t for t in cached_tickers
            if t in cik_map and t not in done]
    if args.limit:
        todo = todo[:args.limit]

    print(f"Cached tickers: {len(cached_tickers):,}", flush=True)
    print(f"In SEC mapping: {sum(1 for t in cached_tickers if t in cik_map):,}", flush=True)
    print(f"Already in xbrl_facts: {len(done):,}", flush=True)
    print(f"To fetch this run: {len(todo):,}", flush=True)
    if not todo:
        print("Nothing to do.")
        return 0

    started = time.time()
    n_ok = n_empty = n_fail = 0
    for i, t in enumerate(todo, 1):
        cik = cik_map[t]
        rows = fetch_one(t, cik)
        if rows is None:
            n_fail += 1
        else:
            if rows:
                conn.executemany(
                    "INSERT OR IGNORE INTO xbrl_facts "
                    "(ticker,cik,concept,period_end,filed,fy,fp,form,accn,val) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
                conn.commit()
                n_ok += 1
            else:
                n_empty += 1
        if i % 25 == 0 or i == len(todo):
            elapsed = time.time() - started
            rate = i / elapsed
            eta = (len(todo) - i) / rate
            print(f"  [{i:5d}/{len(todo)}]  ok={n_ok:5d} empty={n_empty:4d} "
                  f"fail={n_fail:4d}  {rate:.1f}/s  ETA {eta/60:.1f} min",
                  flush=True)
        time.sleep(RATE_LIMIT_DELAY)

    conn.close()
    elapsed = (time.time() - started) / 60
    print(f"\nDone in {elapsed:.1f} min. ok={n_ok}, empty={n_empty}, fail={n_fail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
