"""One-time (idempotent) maintenance: flag joint-filer groups in `signals`.

Background
----------
SEC Form 4 sometimes has the same economic transaction reported by multiple
related legal entities (fund GP + LP + advisor + sub-funds, etc.). They share:
  * accession (one filing)
  * ticker, transaction_date, transaction_code, shares
…but each entity has a distinct `filer_cik`. Per SEC rules each must file,
so the rows are NOT database duplicates and the existing UNIQUE constraint
correctly keeps them. But for analytics they represent ONE economic event.

This script tags each such group with a `co_filing_group_id` column so we
can:
  * audit how widespread joint filings are
  * collapse to one effective trade in dashboard / analytics
  * leave scoring untouched (clusters.py already handles this case via the
    suspect_co_filing collapse, so no behavior change there)

Idempotent: running again only re-tags rows whose grouping changed (e.g.
after a new backfill chunk added members to an existing group).
"""
from __future__ import annotations

import logging

from trading_bot.db import connect


log = logging.getLogger(__name__)


def ensure_column() -> None:
    """Add `co_filing_group_id` column if not present. SQLite-safe."""
    with connect() as c:
        cols = {row[1] for row in c.execute("PRAGMA table_info(signals)")}
        if "co_filing_group_id" not in cols:
            c.execute("ALTER TABLE signals ADD COLUMN co_filing_group_id TEXT")
            c.execute(
                "CREATE INDEX IF NOT EXISTS idx_signals_co_filing "
                "ON signals(co_filing_group_id)"
            )
            log.info("Added co_filing_group_id column + index.")


def flag_groups() -> dict:
    """Tag all joint-filer groups. Group ID = smallest signal.id in the group.

    Returns counts: {groups, rows_tagged, single_rows_cleared}.
    """
    ensure_column()

    with connect() as c:
        # Find groups: same (accession, ticker, transaction_date,
        # transaction_code, shares) across 2+ rows.
        groups = c.execute(
            """
            SELECT MIN(id) AS group_id, COUNT(*) AS n,
                   accession, ticker, transaction_date, transaction_code, shares
            FROM signals
            WHERE accession IS NOT NULL
              AND transaction_date IS NOT NULL
            GROUP BY accession, ticker, transaction_date, transaction_code, shares
            HAVING COUNT(*) > 1
            """
        ).fetchall()

        rows_tagged = 0
        for g in groups:
            gid = f"cof-{g['group_id']}"
            n = c.execute(
                """
                UPDATE signals
                SET co_filing_group_id = ?
                WHERE accession = ?
                  AND ticker = ?
                  AND transaction_date = ?
                  AND transaction_code = ?
                  AND shares = ?
                  AND (co_filing_group_id IS NULL OR co_filing_group_id != ?)
                """,
                (gid, g["accession"], g["ticker"], g["transaction_date"],
                 g["transaction_code"], g["shares"], gid),
            ).rowcount
            rows_tagged += n

        # Clean up: any row tagged that is no longer in a group (e.g., the
        # other rows were deleted) — clear its tag for honesty.
        cleared = c.execute(
            """
            UPDATE signals SET co_filing_group_id = NULL
            WHERE co_filing_group_id IS NOT NULL
              AND id NOT IN (
                SELECT s.id FROM signals s
                JOIN signals other
                  ON  other.accession = s.accession
                  AND other.ticker = s.ticker
                  AND other.transaction_date = s.transaction_date
                  AND other.transaction_code = s.transaction_code
                  AND other.shares = s.shares
                  AND other.id != s.id
              )
            """
        ).rowcount

    return {
        "groups": len(groups),
        "rows_tagged": rows_tagged,
        "single_rows_cleared": cleared,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    stats = flag_groups()
    print(f"Co-filing groups: {stats['groups']:,}")
    print(f"Rows newly tagged or retagged: {stats['rows_tagged']:,}")
    print(f"Single-row tags cleared: {stats['single_rows_cleared']:,}")
