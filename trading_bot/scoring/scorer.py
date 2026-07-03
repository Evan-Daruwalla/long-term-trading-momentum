"""Per-ticker scoring engine.

Reading C of the rubric (selected 2026-04-25):
  +2  any insider buy in the window (flat — not per filer)
  +3  cluster of 2+ effective filers (co-filing-corrected)
  +2  cluster of 3+ effective filers (additional, on top of the +3)
  +1  any buying filer is CEO or CFO (once per ticker)
  +1  total buy value > $500K (once per ticker)
 VETO sells exist for ticker AND no buys in the window — never trade

Position sizing:
  score 5-7 -> 5%  of portfolio   (standard)
  score 8+  -> 10% of portfolio   (high conviction)
  score <5  -> no trade
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from trading_bot import config
from trading_bot.db import connect
from trading_bot.scoring.clusters import find_clusters
from trading_bot.scoring.quality import QUALITY_FILTER_SQL
from trading_bot.sources.edgar import is_ceo_or_cfo


DOLLAR_BONUS_THRESHOLD = 500_000
TRADE_THRESHOLD = 5
HIGH_CONVICTION_THRESHOLD = 8
STANDARD_POSITION_PCT = 5.0
HIGH_CONVICTION_POSITION_PCT = 10.0


@dataclass
class TickerScore:
    ticker: str
    score: int
    vetoed: bool
    veto_reason: str | None
    position_size_pct: float
    distinct_buy_filers: int
    effective_cluster_filers: int
    total_buy_value: float
    has_ceo_cfo: bool
    sells_in_window: int
    components: dict = field(default_factory=dict)
    window_start: str = ""
    window_end: str = ""


def score_all(*, window_days: int = 30, as_of: date | None = None) -> list[TickerScore]:
    as_of = as_of or date.today()
    window_start = (as_of - timedelta(days=window_days)).isoformat()
    window_end = as_of.isoformat()

    clusters_by_ticker = {
        c.ticker: c for c in find_clusters(window_days=window_days, as_of=as_of)
    }

    # filed_at <= window_end ensures backtests don't see signals that hadn't
    # been filed yet. For live use (as_of=today) the filter is a no-op.
    # `filed_at IS NOT NULL` is defensive — Form 4 ingest always sets it,
    # but a NULL row would otherwise sneak past the look-ahead guard.
    # NB: QUALITY_FILTER_SQL only applies to 'P' rows (size/role gate). Sells
    # ('S') still need to pass through unfiltered so the sell-veto rule fires
    # correctly when an unfiltered insider dumps shares on a stock our buys
    # were considering.
    sql = f"""
      SELECT ticker, transaction_code, filer_cik, filer_name, filer_title,
             total_value
      FROM signals
      WHERE source = 'form4'
        AND transaction_date IS NOT NULL
        AND transaction_date BETWEEN ? AND ?
        AND filed_at IS NOT NULL AND filed_at <= ?
        AND (
          (transaction_code = 'P' {QUALITY_FILTER_SQL})
          OR transaction_code = 'S'
        )
    """
    by_ticker: dict[str, list[dict]] = {}
    with connect() as conn:
        for r in conn.execute(sql, (window_start, window_end, window_end)):
            by_ticker.setdefault(r["ticker"], []).append(dict(r))

    out: list[TickerScore] = []
    for ticker, rows in by_ticker.items():
        buys = [r for r in rows if r["transaction_code"] == "P"]
        sells = [r for r in rows if r["transaction_code"] == "S"]

        # Sell veto fires only when there are NO buys in the window.
        if sells and not buys:
            out.append(TickerScore(
                ticker=ticker, score=0, vetoed=True,
                veto_reason=f"{len(sells)} sell signal(s), no buys in window",
                position_size_pct=0.0,
                distinct_buy_filers=0,
                effective_cluster_filers=0,
                total_buy_value=0.0,
                has_ceo_cfo=False,
                sells_in_window=len(sells),
                window_start=window_start, window_end=window_end,
            ))
            continue

        if not buys:
            continue  # nothing to score

        components: dict[str, int] = {}
        score = 0

        # +2 flat for any buy signal
        score += 2
        components["any_buy"] = 2

        cluster = clusters_by_ticker.get(ticker)
        eff = cluster.effective_filer_count if cluster else 0
        if eff >= 2:
            score += 3
            components["cluster_2plus"] = 3
        if eff >= 3:
            score += 2
            components["cluster_3plus"] = 2

        has_ceo_cfo = any(is_ceo_or_cfo(r["filer_title"]) for r in buys)
        if has_ceo_cfo:
            score += 1
            components["ceo_cfo"] = 1

        total_buy_value = sum((r["total_value"] or 0) for r in buys)
        if total_buy_value > DOLLAR_BONUS_THRESHOLD:
            score += 1
            components["over_500k"] = 1

        if score >= HIGH_CONVICTION_THRESHOLD:
            pos = HIGH_CONVICTION_POSITION_PCT
        elif score >= TRADE_THRESHOLD:
            pos = STANDARD_POSITION_PCT
        else:
            pos = 0.0

        distinct_buy_filers = len({r["filer_cik"] for r in buys if r["filer_cik"]})

        out.append(TickerScore(
            ticker=ticker, score=score, vetoed=False, veto_reason=None,
            position_size_pct=pos,
            distinct_buy_filers=distinct_buy_filers,
            effective_cluster_filers=eff,
            total_buy_value=total_buy_value,
            has_ceo_cfo=has_ceo_cfo,
            sells_in_window=len(sells),
            components=components,
            window_start=window_start, window_end=window_end,
        ))

    out.sort(key=lambda s: (s.score, s.total_buy_value), reverse=True)
    return out


def tradeable(scores: list[TickerScore]) -> list[TickerScore]:
    """Filter to tickers that should actually be traded."""
    return [s for s in scores if not s.vetoed and s.score >= TRADE_THRESHOLD]
