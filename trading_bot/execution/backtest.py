"""Walk-forward backtest over a date range.

For each trading day D in [since, until]:
  1. monitor_positions(as_of=D) — evaluate exits on existing positions
                                  using D's close price.
  2. execute_pending(as_of=D)   — score signals visible by D, place buys
                                  that fill at D+1's open.

The signals + market data we already have are reused. Backtest WIPES the
positions and portfolio_state tables before running — it's destructive
by design (a backtest from a non-empty state is not reproducible).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta

from trading_bot import config
from trading_bot.db import connect
from trading_bot.execution import market_data
from trading_bot.execution import monitor as monitor_mod
from trading_bot.execution import portfolio as portfolio_mod
from trading_bot.execution import runner as exec_runner


log = logging.getLogger(__name__)


@dataclass
class DailyRecord:
    day: str
    monitor: monitor_mod.MonitorStats
    execution: exec_runner.ExecutionStats


@dataclass
class BacktestResult:
    since: date
    until: date
    starting_cash: float
    ending_cash: float
    open_positions_value: float
    closed_count: int
    open_count: int
    realized_pnl: float
    # Survivorship-bias quantification, computed once per run by
    # _data_coverage(). signals_tradeable = distinct P-signals in the window
    # that have a real fill price cached; signals_total = all distinct
    # P-signals. The gap is the delisted set yfinance can't serve — a
    # genuine, unfixable upward bias on results.
    #
    # NB: this is per-signal. An earlier version counted broker.place_buy
    # failures, but the runner retries a failed buy every day a signal is in
    # its 30-day window, inflating the failure count ~30x and making
    # coverage read ~3% when the true figure is ~48%.
    signals_tradeable: int = 0
    signals_total: int = 0
    signals_placed: int = 0
    daily: list[DailyRecord] = field(default_factory=list)
    # (iso_date, total_portfolio_value) marked-to-market per trading day.
    # Used to compute real portfolio Sharpe (overall and per-year).
    equity_curve: list[tuple[str, float]] = field(default_factory=list)

    @property
    def ending_value(self) -> float:
        return self.ending_cash + self.open_positions_value

    def sharpe_by_year(self, risk_free_apy: float = 0.045) -> dict[str, float]:
        """Annualized Sharpe of daily portfolio returns, bucketed by calendar
        year. The walk-forward optimizer ranks configs on the consistency of
        these — a config that's only positive in one regime is overfit."""
        import statistics
        by_year: dict[str, list[float]] = {}
        prev_val = None
        prev_year = None
        daily_rf = risk_free_apy / 252.0
        for iso, val in self.equity_curve:
            year = iso[:4]
            if prev_val is not None and prev_val > 0 and year == prev_year:
                by_year.setdefault(year, []).append(val / prev_val - 1.0)
            prev_val, prev_year = val, year
        out: dict[str, float] = {}
        for year, rets in by_year.items():
            if len(rets) < 20:                 # too few days to be meaningful
                continue
            sd = statistics.pstdev(rets)
            if sd == 0:
                out[year] = 0.0
                continue
            excess = statistics.fmean(rets) - daily_rf
            out[year] = (excess / sd) * (252 ** 0.5)
        return out

    @property
    def total_pnl(self) -> float:
        return self.ending_value - self.starting_cash

    @property
    def total_pnl_pct(self) -> float:
        return (self.total_pnl / self.starting_cash) * 100.0 if self.starting_cash else 0.0

    @property
    def mtm_total_pnl_pct(self) -> float:
        """MTM-based total return. Prefer this over total_pnl_pct for
        factor / buy-and-hold strategies where positions stay open
        across the test; total_pnl_pct uses open_positions_value (book),
        which understates by ~all the unrealized gains."""
        if not self.equity_curve or not self.starting_cash:
            return self.total_pnl_pct
        final_mtm = self.equity_curve[-1][1]
        return (final_mtm / self.starting_cash - 1.0) * 100.0

    @property
    def coverage_pct(self) -> float:
        """Fraction of in-window P-signals with a real fill price. Below ~70%
        means yfinance survivorship is materially inflating results."""
        return (self.signals_tradeable / self.signals_total * 100.0
                if self.signals_total else 100.0)

    @property
    def worst_case_pnl_pct(self) -> float:
        """Pessimistic survivorship bound: assume every untradeable (delisted)
        signal would have been a -100% loss at average entry size. True impact
        is between this and total_pnl_pct.

        Capped at -100% — you cannot lose more than the whole portfolio. When
        this pegs at exactly -100.0 the missing-data fraction is simply too
        large to bound usefully; read coverage_pct instead."""
        untradeable = self.signals_total - self.signals_tradeable
        if self.signals_placed <= 0 or self.starting_cash <= 0 or untradeable <= 0:
            return self.total_pnl_pct
        with connect() as conn:
            r = conn.execute(
                "SELECT AVG(entry_value) FROM positions WHERE entry_value IS NOT NULL"
            ).fetchone()
        avg_entry = (r[0] or 0.0)
        hypo_loss_pct = (untradeable * avg_entry / self.starting_cash) * 100.0
        return max(self.total_pnl_pct - hypo_loss_pct, -100.0)


def run_backtest(
    *, since: date, until: date, starting_cash: float = 100_000.0
) -> BacktestResult:
    _wipe_state()
    portfolio_mod.init_portfolio(starting_cash=starting_cash)
    # Bulk-load price + sector caches into RAM. Backtest's day loop hits
    # these tables hundreds of thousands of times; one preload pays for
    # itself many times over. Idempotent across multi-profile runs.
    market_data.preload_caches()

    daily: list[DailyRecord] = []
    equity_curve: list[tuple[str, float]] = []
    daily_rate = config.CASH_INTEREST_APY / 365.0
    cur = since
    total_days = max(1, (until - since).days + 1)
    last_pct_logged = -1
    while cur <= until:
        if cur.weekday() < 5:  # Mon-Fri only; yfinance returns None on holidays
            mon_stats = monitor_mod.monitor_positions(as_of=cur)
            exec_stats = exec_runner.execute_pending(as_of=cur)
            daily.append(DailyRecord(day=cur.isoformat(), monitor=mon_stats, execution=exec_stats))
            equity_curve.append((cur.isoformat(), _mark_to_market(cur)))
        # Accrue interest on idle cash every calendar day (weekends count —
        # T-bill / sweep programs pay every day, not just trading days).
        if daily_rate:
            cash = portfolio_mod.get_portfolio().cash
            portfolio_mod.adjust_cash(cash * daily_rate)
        cur += timedelta(days=1)

        # Progress log every 5% so the dashboard / log can show completion.
        # The format mirrors the backfill's "(overall N%)" line so the
        # dashboard can use the same grep to find the latest progress line.
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

    signals_placed = sum(d.execution.placed for d in daily)
    tradeable, total = _data_coverage(since, until)

    return BacktestResult(
        since=since,
        until=until,
        starting_cash=starting_cash,
        ending_cash=pf.cash,
        open_positions_value=pf.open_positions_value,
        closed_count=closed_count,
        open_count=pf.open_position_count,
        realized_pnl=realized,
        signals_tradeable=tradeable,
        signals_total=total,
        signals_placed=signals_placed,
        daily=daily,
        equity_curve=equity_curve,
    )


def _mark_to_market(as_of: date, cache_only: bool = True) -> float:
    """Total portfolio value on `as_of`: cash + sum(qty x close) over open
    positions. portfolio.open_positions_value is book value (sum of
    entry_value), which makes a flat step-function curve useless for Sharpe;
    this prices each open position at its as_of close.

    cache_only=True (default for backtests): only consult the preloaded
    in-memory price cache, never go live. Falls back to entry_price when
    a close is missing. This avoids per-day yfinance calls that get
    rate-limited on multi-year sweeps (factor backtests call this on
    EVERY trading day, ~250/yr × N years × ~100 open positions).
    cache_only=False preserves the legacy live-fallback behavior used by
    Form 4 production paths.
    """
    pf = portfolio_mod.get_portfolio()
    mtm = pf.cash
    with connect() as conn:
        opens = conn.execute(
            "SELECT ticker, qty, entry_price FROM positions WHERE status='open'"
        ).fetchall()
    iso = as_of.isoformat()
    for p in opens:
        if cache_only:
            # Direct in-memory lookup; no yfinance fallback.
            px = market_data._MEM_PRICE.get((p["ticker"], "close", iso))
        else:
            px = market_data.price_on_date(p["ticker"], as_of)
        mtm += p["qty"] * (px if px and px > 0 else p["entry_price"])
    return mtm


def _buy_day(filed_at_iso: str) -> str:
    """First weekday >= filed_at — the day the backtest first attempts the
    buy, and therefore the key next_open is looked up / cached under."""
    d = date.fromisoformat(filed_at_iso[:10])
    while d.weekday() >= 5:  # Sat/Sun -> next Monday
        d += timedelta(days=1)
    return d.isoformat()


def _data_coverage(since: date, until: date) -> tuple[int, int]:
    """(tradeable, total) distinct P-signals filed in [since, until].

    tradeable = those with a real (non-NULL) next_open cached at their
    buy-day key. The rest are delisted tickers yfinance can't serve — the
    survivorship gap. Per-signal, so it's immune to the runner's daily
    retry loop that inflated the old place_buy-failure counter."""
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT ticker, filed_at FROM signals
             WHERE source='form4' AND transaction_code='P'
               AND filed_at BETWEEN ? AND ?
            """,
            (since.isoformat(), until.isoformat()),
        ).fetchall()
        tradeable = 0
        for r in rows:
            hit = conn.execute(
                "SELECT price FROM price_cache WHERE ticker=? AND kind='next_open' "
                "AND key_date=?",
                (r["ticker"], _buy_day(r["filed_at"])),
            ).fetchone()
            if hit is not None and hit["price"] is not None:
                tradeable += 1
    return tradeable, len(rows)


def _wipe_state() -> None:
    log.info("Backtest reset: clearing positions + portfolio_state")
    with connect() as conn:
        conn.execute("DELETE FROM positions")
        conn.execute("DELETE FROM portfolio_state")
