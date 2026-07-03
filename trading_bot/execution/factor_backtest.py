"""Rebalance-based backtest for cross-sectional factor portfolios.

Parallel to execution/backtest.py but with a totally different shape:
no per-day signal-event loop, no per-position stops or take-profits. On
each rebalance date the strategy:
  1. Ranks the tradeable universe by a factor (momentum here).
  2. Builds an equal-weighted top-N basket.
  3. Sells anything currently held that's not in the new basket.
  4. Buys anything in the new basket not currently held.
  5. Holds untouched until next rebalance.

Between rebalances the loop only marks open positions to market so the
daily equity curve (used by sharpe_by_year) stays accurate.

Reuses:
  - market_data._MEM_PRICE / preload_caches
  - trading_bot.db / positions table (same schema as Form 4 backtest)
  - BacktestResult dataclass (incl. equity_curve + sharpe_by_year)
  - The Form 4 backtest's _mark_to_market helper

Trading mechanics:
  - Fill at close(rb_date) +- HALF_SPREAD_BPS (academic convention,
    standard for monthly-rebalance factor research). The next_open cache
    is keyed at signal dates only, so it's not available at arbitrary
    rebalance dates; using close + flat spread is the cleanest substitute.
  - No volume / liquidity check beyond the universe filter (v1).
  - No commissions (modern brokers are free).

Trading_bot.factors.universe.tradeable_universe is the gate. Anything it
returns is assumed fillable; failures (no close on rb_date) are skipped
and counted in `signals_no_price`-equivalent metrics.
"""
from __future__ import annotations

import json
import logging
import math
from datetime import date, datetime, timedelta, timezone

from trading_bot import config
from trading_bot.db import connect
from trading_bot.execution import backtest as bt_mod
from trading_bot.execution import market_data
from trading_bot.execution import portfolio as portfolio_mod
from trading_bot.factors import momentum
from trading_bot.factors.universe import tradeable_universe, _ticker_close_on


log = logging.getLogger(__name__)

HALF_SPREAD_BPS = 5.0    # 5 bps half-spread per fill, both sides


def _half_spread_frac() -> float:
    return HALF_SPREAD_BPS / 10_000.0


# Per-backtest watch of names that just stopped out, awaiting potential
# re-entry on rebound. Keyed by ticker; cleared at each rebalance and on
# _wipe_state. See _check_stops for semantics.
_stopped_watch: dict[str, dict] = {}


def _wipe_state() -> None:
    log.info("Factor backtest reset: clearing positions + portfolio_state")
    _stopped_watch.clear()
    with connect() as conn:
        conn.execute("DELETE FROM positions")
        conn.execute("DELETE FROM portfolio_state")


def _trading_calendar(since: date, until: date,
                      min_tickers_for_trading_day: int = 100) -> list[date]:
    """Master trading-day calendar. Prefers SPY's cached closes (always
    traded on US market days). Falls back to dates where at least
    `min_tickers_for_trading_day` cached tickers have closes — that
    threshold excludes US market holidays where stray foreign issuers or
    quote-feed artifacts left ghost closes on the calendar (e.g.
    2023-01-02 was the New Year holiday; about 30 tickers still showed
    closes there from data-feed quirks)."""
    if not market_data._MEM_LOADED:
        market_data.preload_caches()
    spy_dates = sorted({
        d for (t, k, d) in market_data._MEM_PRICE if t == "SPY" and k == "close"
    })
    if not spy_dates:
        log.warning("SPY closes not cached; filtering union calendar by >=%d tickers/day",
                    min_tickers_for_trading_day)
        from collections import Counter
        per_day = Counter(d for (_, k, d) in market_data._MEM_PRICE if k == "close")
        spy_dates = sorted(d for d, n in per_day.items()
                           if n >= min_tickers_for_trading_day)
    s, u = since.isoformat(), until.isoformat()
    return [date.fromisoformat(d) for d in spy_dates if s <= d <= u]


def _rebalance_dates(calendar: list[date], freq: str = "M") -> list[date]:
    """Pick rebalance days from a trading-day calendar.

    freq:
      - "M" (default): first trading day of each calendar month
      - "Q":           first trading day of each calendar quarter (Jan/Apr/Jul/Oct)
      - "W":           first trading day of each ISO week (Mondays unless holiday)
    """
    out: list[date] = []
    last_key = None
    for d in calendar:
        if freq == "M":
            key = (d.year, d.month)
        elif freq == "Q":
            key = (d.year, (d.month - 1) // 3)
        elif freq == "W":
            key = d.isocalendar()[:2]   # (iso_year, iso_week)
        else:
            raise ValueError(f"Unsupported freq {freq!r}; use M / Q / W")
        if key != last_key:
            out.append(d)
            last_key = key
    return out


def _current_open_positions() -> dict[str, dict]:
    """{ticker: position_dict} for all open positions."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, ticker, qty, entry_price FROM positions "
            "WHERE status='open'"
        ).fetchall()
    return {r["ticker"]: dict(r) for r in rows}


def _close_position(*, position_id: int, ticker: str, qty: float,
                    entry_price: float, fill_price: float, as_of: date) -> float:
    """Close one position at `fill_price`. Returns realized $ P&L."""
    realized = (fill_price - entry_price) * qty
    realized_pct = (fill_price / entry_price - 1.0) * 100.0
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute(
            """UPDATE positions SET
                 status='closed', exit_price=?, exit_value=?, exit_time=?,
                 exit_date=?, exit_reason=?, realized_pnl=?, realized_pnl_pct=?
               WHERE id=?""",
            (fill_price, fill_price * qty, now, as_of.isoformat(),
             "rebalance", realized, realized_pct, position_id),
        )
    portfolio_mod.adjust_cash(fill_price * qty)
    return realized


def _open_position(*, ticker: str, dollar_target: float,
                   fill_price: float, as_of: date) -> bool:
    """Buy `ticker` to ~dollar_target. Returns True on success.

    Fractional shares: positions.qty is REAL and the strategy is a
    paper / simulator anyway, so we don't floor to whole shares — that
    was the source of the v1 ~24-skip-per-rebalance bug where any name
    priced > dollar_target (e.g. NVDA >$1000 pre-split, AVGO, BRK-A)
    couldn't be bought at all. Brokers like Fidelity / Schwab now support
    fractional, so this is realistic too.
    """
    qty = dollar_target / fill_price
    if qty <= 0:
        return False
    actual = qty * fill_price
    now = datetime.now(timezone.utc).isoformat()
    sector = market_data.sector(ticker)
    with connect() as conn:
        conn.execute(
            """INSERT INTO positions
                 (ticker, status, qty, entry_price, entry_value, entry_time,
                  entry_date, sector, entry_components)
               VALUES (?, 'open', ?, ?, ?, ?, ?, ?, ?)""",
            (ticker, qty, fill_price, actual, now, as_of.isoformat(),
             sector, json.dumps({"factor": "momentum"})),
        )
    portfolio_mod.adjust_cash(-actual)
    return True


def _rebalance(*, as_of: date, top_n: int, rank_fn,
               position_scale_fn=None) -> tuple[int, int, int]:
    """Execute one rebalance. Returns (n_sells, n_buys, n_skipped).

    `rank_fn(universe, as_of) -> list[(ticker, score)]` returns the
    universe ranked best-first. The strategy keeps the top `top_n`.
    Using a rank_fn rather than a per-ticker factor function lets
    composite/multi-factor strategies do their cross-sectional combining
    in one place (see factors/composite.py).

    `position_scale_fn(as_of) -> float in [0,1]` (optional): scales the
    per-name $ allocation. 1.0 = full deployment (default). 0.5 = half
    invested, half cash. Used by vol-targeting overlay. Cash isn't put to
    work until next rebal."""
    universe = tradeable_universe(as_of)
    if len(universe) < top_n:
        log.warning("rebalance %s: universe has %d names < top_n=%d; using all",
                    as_of, len(universe), top_n)
    scored = rank_fn(universe, as_of)
    target_set = {t for t, _ in scored[:top_n]}

    current = _current_open_positions()
    sells = [c for c in current if c not in target_set]
    buys = [t for t in target_set if t not in current]

    n_sells = n_buys = n_skipped = 0
    spread = _half_spread_frac()

    # SELLS first to free cash
    for ticker in sells:
        _, px = _ticker_close_on(ticker, as_of)
        if px is None or px <= 0:
            n_skipped += 1
            continue
        fill = px * (1.0 - spread)
        pos = current[ticker]
        _close_position(position_id=pos["id"], ticker=ticker,
                        qty=pos["qty"], entry_price=pos["entry_price"],
                        fill_price=fill, as_of=as_of)
        n_sells += 1

    # Size buys from AVAILABLE CASH, not NAV. Earlier version used
    # NAV/top_n which overspent when kept positions appreciated more than
    # sold ones (NAV high, freed cash low) and drove cash negative — saw
    # $-9.8K on a 2023 smoke test. Sizing by free cash bounds spending
    # exactly to what's liquid. Kept positions' weights drift between
    # rebalances; acceptable for v1.
    if buys:
        avail = portfolio_mod.get_portfolio().cash
        # Keep a tiny buffer so spread-driven roundup doesn't push cash <0
        scale = 1.0 if position_scale_fn is None else max(0.0, min(1.0, position_scale_fn(as_of)))
        dollar_per = max(0.0, avail * 0.999) * scale / len(buys)
        for ticker in buys:
            _, px = _ticker_close_on(ticker, as_of)
            if px is None or px <= 0:
                n_skipped += 1
                continue
            fill = px * (1.0 + spread)
            if _open_position(ticker=ticker, dollar_target=dollar_per,
                              fill_price=fill, as_of=as_of):
                n_buys += 1
            else:
                n_skipped += 1

    return n_sells, n_buys, n_skipped


def _check_stops(*, as_of: date, stop_loss_pct: float,
                 reentry_buffer: float | None = None) -> tuple[int, int]:
    """Close any open position whose close has dropped at-or-below the
    stop threshold from entry. stop_loss_pct is negative (e.g. -0.15 for
    -15%). Returns (n_stopped, n_reentered).

    Re-entries (when reentry_buffer is not None): for each ticker on the
    watch (i.e. stopped earlier this rebal period), if today's close
    >= stop_fill * (1 + reentry_buffer), re-buy at close+spread for the
    original $ amount. Re-entries are processed BEFORE new stops so a
    same-day stop can't trigger same-day reentry. Watch is cleared at
    each rebalance (see _rebalance)."""
    spread = _half_spread_frac()
    n_stopped = n_reentered = 0

    # 1) Re-entries from watch
    if reentry_buffer is not None and _stopped_watch:
        to_drop: list[str] = []
        avail_cash = portfolio_mod.get_portfolio().cash
        for ticker, info in list(_stopped_watch.items()):
            _, px = _ticker_close_on(ticker, as_of)
            if px is None or px <= 0:
                continue
            if px < info["stop_fill"] * (1.0 + reentry_buffer):
                continue
            fill = px * (1.0 + spread)
            # Cap target at available cash so we never overspend
            d = min(info["original_value"], max(0.0, avail_cash * 0.999))
            if d <= 0:
                continue
            if _open_position(ticker=ticker, dollar_target=d,
                              fill_price=fill, as_of=as_of):
                avail_cash -= d
                n_reentered += 1
                to_drop.append(ticker)
        for t in to_drop:
            _stopped_watch.pop(t, None)

    # 2) New stops
    current = _current_open_positions()
    for ticker, pos in current.items():
        _, px = _ticker_close_on(ticker, as_of)
        if px is None or px <= 0:
            continue
        loss_pct = px / pos["entry_price"] - 1.0
        if loss_pct <= stop_loss_pct:
            fill = px * (1.0 - spread)
            _close_position(position_id=pos["id"], ticker=ticker,
                            qty=pos["qty"], entry_price=pos["entry_price"],
                            fill_price=fill, as_of=as_of)
            n_stopped += 1
            if reentry_buffer is not None:
                _stopped_watch[ticker] = {
                    "stop_fill": fill,
                    "original_value": pos["qty"] * pos["entry_price"],
                }
    return n_stopped, n_reentered


def run_factor_backtest(*, since: date, until: date,
                        top_n: int = 100,
                        starting_cash: float = 100_000.0,
                        rank_fn=None,
                        rebalance_freq: str = "M",
                        stop_loss_pct: float | None = None,
                        reentry_buffer: float | None = None,
                        position_scale_fn=None,
                        ) -> bt_mod.BacktestResult:
    """One factor-portfolio backtest from `since` to `until`. Returns a
    BacktestResult populated with daily MTM equity_curve, ready for
    sharpe_by_year().

    rebalance_freq: "M" monthly / "Q" quarterly / "W" weekly (see _rebalance_dates).

    stop_loss_pct (default None): when set (e.g. -0.15), positions whose
    close drops to/below entry*(1+stop_loss_pct) on any trading day between
    rebalances are closed at that day's close ± half-spread. Cash sits idle
    until next rebalance (unless reentry_buffer is also set). None preserves
    the frozen no-stop behavior used by mom_v2 and all backtest archive runs.

    reentry_buffer (default None): when set together with stop_loss_pct,
    enables same-name re-entry after a stop. A stopped ticker is added to
    a per-rebal watch; on any subsequent day in the same period, if its
    close >= stop_fill * (1 + reentry_buffer), it's re-bought at close+spread
    for its original $ size. Watch resets each rebalance. Requires
    stop_loss_pct to be set; ignored otherwise.
    """
    if rank_fn is None:
        rank_fn = momentum.rank_universe
    _wipe_state()
    portfolio_mod.init_portfolio(starting_cash=starting_cash)
    market_data.preload_caches()

    calendar = _trading_calendar(since, until)
    if not calendar:
        raise RuntimeError(f"No trading days cached in [{since}, {until}]")
    rebal = set(d.isoformat() for d in _rebalance_dates(calendar, freq=rebalance_freq))
    log.info("Factor backtest: %s -> %s, %d trading days, %d rebalances%s",
             since, until, len(calendar), len(rebal),
             f", stop={stop_loss_pct:+.2%}" if stop_loss_pct is not None else "")

    daily: list[bt_mod.DailyRecord] = []
    equity_curve: list[tuple[str, float]] = []
    daily_rate = config.CASH_INTEREST_APY / 365.0
    total_rebalances = 0
    total_sells = total_buys = total_skipped = 0
    total_stopped = total_reentered = 0
    last_pct_logged = -1

    # Iterate every calendar day so cash interest accrues weekends too,
    # matching backtest.py's convention.
    cur = since
    while cur <= until:
        is_trading = cur.isoformat() in {d.isoformat() for d in calendar}
        if is_trading:
            if cur.isoformat() in rebal:
                # New rebal period: watch from prior period is stale (any
                # name in the new target gets normal rebuy; others should
                # be abandoned).
                _stopped_watch.clear()
                s, b, sk = _rebalance(as_of=cur, top_n=top_n, rank_fn=rank_fn,
                                      position_scale_fn=position_scale_fn)
                total_rebalances += 1
                total_sells += s; total_buys += b; total_skipped += sk
            elif stop_loss_pct is not None:
                ns, nr = _check_stops(as_of=cur, stop_loss_pct=stop_loss_pct,
                                      reentry_buffer=reentry_buffer)
                total_stopped += ns
                total_reentered += nr
            equity_curve.append((cur.isoformat(), bt_mod._mark_to_market(cur)))
        if daily_rate:
            cash = portfolio_mod.get_portfolio().cash
            portfolio_mod.adjust_cash(cash * daily_rate)
        cur += timedelta(days=1)
        # Progress log mirrors Form 4 backtest so the dashboard parses it.
        total_days = max(1, (until - since).days + 1)
        days_done = (cur - since).days
        pct = int(days_done * 100 / total_days)
        if pct >= last_pct_logged + 5:
            log.info("backtest progress: %d/%d days (%d%%)  cur=%s",
                     days_done, total_days, pct, cur.isoformat())
            last_pct_logged = pct

    pf = portfolio_mod.get_portfolio()
    with connect() as conn:
        closed_count = conn.execute(
            "SELECT COUNT(*) FROM positions WHERE status='closed'"
        ).fetchone()[0]
        realized = conn.execute(
            "SELECT COALESCE(SUM(realized_pnl), 0) FROM positions WHERE status='closed'"
        ).fetchone()[0]

    log.info("Factor backtest done: %d rebalances, %d sells, %d buys, %d skipped%s",
             total_rebalances, total_sells, total_buys, total_skipped,
             (f", {total_stopped} stops, {total_reentered} reentries"
              if stop_loss_pct is not None else ""))

    return bt_mod.BacktestResult(
        since=since, until=until,
        starting_cash=starting_cash,
        ending_cash=pf.cash,
        open_positions_value=pf.open_positions_value,
        closed_count=closed_count,
        open_count=pf.open_position_count,
        realized_pnl=realized,
        signals_tradeable=0,         # not applicable to factor strategy
        signals_total=0,
        signals_placed=total_buys,
        daily=daily,
        equity_curve=equity_curve,
    )
