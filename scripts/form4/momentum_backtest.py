"""Cross-sectional momentum benchmark.

Long top 20 by 6-month total return (skipping the most recent 21 trading
days, per Jegadeesh/Titman 1993), equal-weight, monthly rebalance.

Universe: tickers in `signals` table that also have full close history
in price_cache. Same universe as the Form-4 strategy for fair head-to-head.

Why this benchmark: cross-sectional momentum is the most replicated factor
in finance (positive Sharpe ~0.5-0.8 over decades). If our event-driven
Form-4 strategy can't beat a generic momentum portfolio on the same
universe, we don't have an edge worth deploying.

Output: var/sim_archive/runs/momentum-{run_id}/momentum.json with NAV
series, monthly returns, and summary metrics. Designed for side-by-side
comparison with R14/R15 Form-4 results.

Usage:
  python -m scripts.momentum_backtest --since 2021-05-01 --until 2026-04-24
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import sqlite3
import statistics
from collections import defaultdict
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

from trading_bot.config import DB_PATH, VAR_DIR

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

ARCHIVE_ROOT = VAR_DIR / "form4" / "archive" / "runs"

MOMENTUM_LOOKBACK_DAYS = 180   # ~6 months
MOMENTUM_SKIP_DAYS     = 21    # ~1 month — drops short-term reversal noise
TOP_N                  = 20    # equal-weight long the top decile-ish
MIN_HISTORY_DAYS       = 200   # require ≥200 cached bars to be eligible


def _load_prices(since: date, until: date) -> dict[str, list[tuple[date, float]]]:
    """Load close history. Returns {ticker: [(date, price), ...]} sorted asc."""
    extended_since = since - timedelta(days=400)  # need pre-window for first lookback
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT ticker, key_date, price FROM price_cache "
        "WHERE kind='close' AND key_date >= ? AND key_date <= ? AND price > 0",
        (extended_since.isoformat(), until.isoformat()),
    ).fetchall()
    conn.close()

    by_ticker: dict[str, list[tuple[date, float]]] = defaultdict(list)
    for ticker, key_date, price in rows:
        try:
            d = date.fromisoformat(key_date)
        except ValueError:
            continue
        by_ticker[ticker].append((d, float(price)))
    for t in by_ticker:
        by_ticker[t].sort()
    # Drop tickers with too little history to score
    return {t: ps for t, ps in by_ticker.items() if len(ps) >= MIN_HISTORY_DAYS}


def _filter_universe(prices: dict, conn: sqlite3.Connection) -> dict:
    """Restrict price universe to tickers that appear in signals table."""
    universe = {r[0] for r in conn.execute(
        "SELECT DISTINCT ticker FROM signals WHERE transaction_code='P'"
    )}
    return {t: ps for t, ps in prices.items() if t in universe}


def _price_at(history: list[tuple[date, float]], target: date,
              max_lookback_days: int = 5) -> float | None:
    """Return the most recent close on or before `target`, within max_lookback."""
    # Binary search: linear is fine for ~1500 entries per ticker
    candidate = None
    for d, p in reversed(history):
        if d <= target:
            if (target - d).days <= max_lookback_days:
                candidate = p
            break
    return candidate


def _trading_days(prices: dict) -> list[date]:
    """Union of all trading dates seen across the universe, sorted ascending."""
    seen: set[date] = set()
    for h in prices.values():
        seen.update(d for d, _ in h)
    return sorted(seen)


def _rebalance_dates(trading_days: list[date], since: date, until: date) -> list[date]:
    """First trading day of each month in [since, until]."""
    out = []
    seen_months: set[tuple[int, int]] = set()
    for d in trading_days:
        if d < since or d > until:
            continue
        ym = (d.year, d.month)
        if ym not in seen_months:
            out.append(d)
            seen_months.add(ym)
    return out


def _rank_momentum(prices: dict, as_of: date) -> list[tuple[str, float]]:
    """Score each ticker by (price_skip / price_lookback) - 1, sorted desc."""
    skip = as_of - timedelta(days=MOMENTUM_SKIP_DAYS)
    lookback = as_of - timedelta(days=MOMENTUM_SKIP_DAYS + MOMENTUM_LOOKBACK_DAYS)
    out = []
    for ticker, hist in prices.items():
        p_skip = _price_at(hist, skip)
        p_lb = _price_at(hist, lookback)
        if p_skip and p_lb and p_lb > 0:
            ret = p_skip / p_lb - 1.0
            # Sanity cap — protects against split-related blowups in cache
            if -0.95 < ret < 10.0:
                out.append((ticker, ret))
    out.sort(key=lambda x: x[1], reverse=True)
    return out


def _portfolio_return(prices: dict, holdings: list[str],
                      start: date, end: date) -> float:
    """Equal-weight return from start to end. Skips tickers missing a fill."""
    rets = []
    for ticker in holdings:
        hist = prices.get(ticker)
        if not hist:
            continue
        p_s = _price_at(hist, start)
        p_e = _price_at(hist, end)
        if p_s and p_e and p_s > 0:
            rets.append(p_e / p_s - 1.0)
    if not rets:
        return 0.0
    return sum(rets) / len(rets)


def _sharpe_annualized(monthly_returns: list[float]) -> float:
    """Annualized Sharpe assuming 12 monthly returns/year. Risk-free = 0."""
    if len(monthly_returns) < 2:
        return 0.0
    mean = statistics.mean(monthly_returns)
    sd = statistics.stdev(monthly_returns)
    if sd == 0:
        return 0.0
    return (mean / sd) * math.sqrt(12)


def _max_drawdown(nav_series: list[tuple[date, float]]) -> float:
    """Worst peak-to-trough decline expressed as fraction (e.g. -0.32)."""
    peak = -float("inf")
    worst = 0.0
    for _, v in nav_series:
        if v > peak:
            peak = v
        dd = (v / peak - 1.0) if peak > 0 else 0.0
        if dd < worst:
            worst = dd
    return worst


def run_momentum(*, since: date, until: date, starting_cash: float = 100_000.0) -> dict:
    log.info("Loading close cache...")
    all_prices = _load_prices(since, until)
    conn = sqlite3.connect(DB_PATH)
    prices = _filter_universe(all_prices, conn)
    conn.close()
    log.info("Universe: %d tickers (filtered from %d cache, %d signals)",
             len(prices), len(all_prices), len(prices))

    tdays = _trading_days(prices)
    rebal_dates = _rebalance_dates(tdays, since, until)
    log.info("Rebalance dates: %d (first=%s, last=%s)",
             len(rebal_dates), rebal_dates[0], rebal_dates[-1])

    nav = starting_cash
    nav_series: list[tuple[date, float]] = [(rebal_dates[0], nav)]
    monthly_returns: list[float] = []
    rebalance_log: list[dict] = []
    holdings: list[str] = []

    for i, rebal_date in enumerate(rebal_dates):
        # Realize last month's return on PRIOR holdings, then rebalance.
        if holdings and i > 0:
            prev_date = rebal_dates[i - 1]
            ret = _portfolio_return(prices, holdings, prev_date, rebal_date)
            nav *= (1 + ret)
            nav_series.append((rebal_date, nav))
            monthly_returns.append(ret)

        ranked = _rank_momentum(prices, rebal_date)
        new_holdings = [t for t, _ in ranked[:TOP_N]]
        rebalance_log.append({
            "date": rebal_date.isoformat(),
            "nav": round(nav, 2),
            "holdings": new_holdings,
            "n_eligible": len(ranked),
        })
        holdings = new_holdings

    # Carry final holdings to `until`
    if holdings:
        ret = _portfolio_return(prices, holdings, rebal_dates[-1], until)
        nav *= (1 + ret)
        nav_series.append((until, nav))
        monthly_returns.append(ret)

    total_pnl = nav - starting_cash
    total_pnl_pct = 100.0 * (nav / starting_cash - 1.0)
    sharpe = _sharpe_annualized(monthly_returns)
    mdd = _max_drawdown(nav_series)

    return {
        "strategy": "cross_sectional_momentum",
        "since": since.isoformat(),
        "until": until.isoformat(),
        "starting_cash": starting_cash,
        "ending_nav": round(nav, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 4),
        "annualized_sharpe": round(sharpe, 4),
        "max_drawdown_pct": round(100.0 * mdd, 4),
        "n_rebalances": len(rebal_dates),
        "n_universe": len(prices),
        "params": {
            "lookback_days": MOMENTUM_LOOKBACK_DAYS,
            "skip_days": MOMENTUM_SKIP_DAYS,
            "top_n": TOP_N,
            "min_history_days": MIN_HISTORY_DAYS,
        },
        "nav_series": [[d.isoformat(), round(v, 2)] for d, v in nav_series],
        "monthly_returns": [round(r, 6) for r in monthly_returns],
        "rebalance_log": rebalance_log,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2021-05-01")
    ap.add_argument("--until", default="2026-04-24")
    ap.add_argument("--starting-cash", type=float, default=100_000.0)
    ap.add_argument("--label", default=None)
    args = ap.parse_args()

    since = date.fromisoformat(args.since)
    until = date.fromisoformat(args.until)
    started_at = datetime.now(timezone.utc)

    result = run_momentum(since=since, until=until, starting_cash=args.starting_cash)

    run_id = "momentum-" + started_at.strftime("%Y%m%d-%H%M%S")
    run_dir = ARCHIVE_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    result["run_id"] = run_id
    result["label"] = args.label or run_id
    result["started_at"] = started_at.isoformat()
    result["elapsed_seconds"] = (datetime.now(timezone.utc) - started_at).total_seconds()

    with (run_dir / "momentum.json").open("w") as f:
        json.dump(result, f, indent=2, default=str)
    # Also write a meta.json so list_runs() can pick it up alongside Form-4 runs
    meta = {
        "run_id": run_id,
        "label": result["label"],
        "started_at": result["started_at"],
        "elapsed_seconds": result["elapsed_seconds"],
        "since": result["since"],
        "until": result["until"],
        "starting_cash": result["starting_cash"],
        "strategy": "momentum",
        "summary": {
            "momentum": {
                "total_pnl_pct": result["total_pnl_pct"],
                "annualized_sharpe": result["annualized_sharpe"],
                "max_drawdown_pct": result["max_drawdown_pct"],
                "n_rebalances": result["n_rebalances"],
                "n_universe": result["n_universe"],
            }
        },
    }
    with (run_dir / "meta.json").open("w") as f:
        json.dump(meta, f, indent=2, default=str)

    print("\n" + "=" * 72)
    print(f"  MOMENTUM BACKTEST  {result['since']} -> {result['until']}")
    print("=" * 72)
    print(f"  Universe       : {result['n_universe']:,} tickers")
    print(f"  Rebalances     : {result['n_rebalances']}")
    print(f"  Starting NAV   : ${result['starting_cash']:>12,.0f}")
    print(f"  Ending NAV     : ${result['ending_nav']:>12,.0f}")
    print(f"  Total return   : {result['total_pnl_pct']:+.2f}%")
    print(f"  Annualized Sharpe: {result['annualized_sharpe']:+.3f}")
    print(f"  Max drawdown   : {result['max_drawdown_pct']:+.2f}%")
    print(f"  Archived to    : {run_dir}")


if __name__ == "__main__":
    main()
