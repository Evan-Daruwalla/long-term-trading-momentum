"""Cluster detection: 2+ distinct insiders buying the same stock within N days.

A cluster is the strongest Form 4 conviction signal in the scoring rubric
(+3 base, +2 more for 3+ filers). Co-filings — multiple related entities
(funds, family offices, GPs) reporting one underlying transaction — would
otherwise inflate naive cluster counts, so we flag them.

Heuristic: if `filer_count > independent_trade_count` (where an independent
trade is a distinct (date, shares, price) triple), some filers are reporting
the same trade. Scoring should treat that as one filer, not many.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from trading_bot.db import connect
from trading_bot.scoring.quality import QUALITY_FILTER_SQL


@dataclass
class Cluster:
    ticker: str
    filer_count: int               # distinct filer_cik values
    effective_filer_count: int     # filer_count discounted for co-filings
    independent_trade_count: int   # distinct (date, shares, price) triples
    total_value: float
    window_start: str
    window_end: str
    filer_names: list[str]
    suspect_co_filing: bool

    def as_row(self) -> dict:
        return {
            "ticker": self.ticker,
            "filer_count": self.filer_count,
            "effective_filer_count": self.effective_filer_count,
            "independent_trade_count": self.independent_trade_count,
            "total_value": self.total_value,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "filer_names": "; ".join(self.filer_names),
            "suspect_co_filing": self.suspect_co_filing,
        }


def find_clusters(
    *,
    window_days: int = 30,
    min_filers: int = 2,
    as_of: date | None = None,
) -> list[Cluster]:
    """Return clusters of insider purchases within the rolling window."""
    as_of = as_of or date.today()
    window_start = (as_of - timedelta(days=window_days)).isoformat()
    window_end = as_of.isoformat()

    sql = f"""
      SELECT ticker, filer_cik, filer_name, transaction_date,
             shares, price_per_share, total_value
      FROM signals
      WHERE source = 'form4'
        AND transaction_code = 'P'
        AND transaction_date IS NOT NULL
        AND transaction_date BETWEEN ? AND ?
        AND filed_at IS NOT NULL AND filed_at <= ?
        {QUALITY_FILTER_SQL}
    """

    by_ticker: dict[str, list[dict]] = {}
    with connect() as conn:
        for r in conn.execute(sql, (window_start, window_end, window_end)):
            by_ticker.setdefault(r["ticker"], []).append(dict(r))

    clusters: list[Cluster] = []
    for ticker, rows in by_ticker.items():
        filer_ciks = {r["filer_cik"] for r in rows if r["filer_cik"]}
        if len(filer_ciks) < min_filers:
            continue

        independent_trades = {
            (r["transaction_date"], r["shares"], r["price_per_share"])
            for r in rows
        }
        suspect = len(filer_ciks) > len(independent_trades)
        # When filers reported overlapping (date,shares,price) triples, they
        # are almost certainly related entities reporting one institutional
        # decision (e.g. fund GP + LP + advisor all filing the same trade).
        # Collapse the whole group to one effective actor.
        if suspect:
            effective = 1
        else:
            effective = len(filer_ciks)
        if effective < min_filers:
            continue

        clusters.append(Cluster(
            ticker=ticker,
            filer_count=len(filer_ciks),
            effective_filer_count=effective,
            independent_trade_count=len(independent_trades),
            total_value=sum(r["total_value"] or 0 for r in rows),
            window_start=window_start,
            window_end=window_end,
            filer_names=sorted({r["filer_name"] for r in rows if r["filer_name"]}),
            suspect_co_filing=suspect,
        ))

    clusters.sort(key=lambda c: (c.effective_filer_count, c.total_value), reverse=True)
    return clusters
