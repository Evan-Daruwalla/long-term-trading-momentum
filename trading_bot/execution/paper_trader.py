"""Paper-trade portfolio state for live (today-only) rebalancing.

Distinct from `portfolio.py` which is the BACKTEST portfolio that gets wiped
by `factor_backtest._wipe_state()`. Paper-trade state lives in `paper_*`
tables and must persist across days.

API parallels portfolio.py: init / get / adjust_cash / open / close / list.

Single strategy MVP — `strategy_name` is the key, defaulting to "mom_v2_paper".
Multi-strategy support is trivial extension if/when needed.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone

from trading_bot.db import connect, init_db

DEFAULT_STRATEGY = "mom_v2_paper"


@dataclass(frozen=True)
class PaperPortfolio:
    strategy_name: str
    starting_cash: float
    cash: float
    open_positions_value: float    # sum of entry_value for open positions
    n_open_positions: int
    initialized_at: str
    last_rebalanced_at: str | None

    @property
    def total_entry_value(self) -> float:
        return self.cash + self.open_positions_value


def init(strategy_name: str = DEFAULT_STRATEGY,
         starting_cash: float = 100_000.0) -> PaperPortfolio:
    """Create the paper-portfolio row if it doesn't exist. Idempotent —
    calling again does NOT reset cash or positions."""
    init_db()    # ensure schema exists (esp. on first run)
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO paper_portfolio "
            "(strategy_name, starting_cash, cash, initialized_at) "
            "VALUES (?, ?, ?, ?)",
            (strategy_name, starting_cash, starting_cash, now),
        )
    return get(strategy_name)


def get(strategy_name: str = DEFAULT_STRATEGY) -> PaperPortfolio:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM paper_portfolio WHERE strategy_name=?",
            (strategy_name,),
        ).fetchone()
        if row is None:
            raise RuntimeError(
                f"Paper portfolio for {strategy_name!r} not initialized. "
                f"Call paper_trader.init({strategy_name!r}, starting_cash=...)."
            )
        agg = conn.execute(
            "SELECT COALESCE(SUM(entry_value), 0) v, COUNT(*) c "
            "FROM paper_positions WHERE strategy_name=? AND status='open'",
            (strategy_name,),
        ).fetchone()
    return PaperPortfolio(
        strategy_name=row["strategy_name"],
        starting_cash=row["starting_cash"],
        cash=row["cash"],
        open_positions_value=agg["v"],
        n_open_positions=agg["c"],
        initialized_at=row["initialized_at"],
        last_rebalanced_at=row["last_rebalanced_at"],
    )


def adjust_cash(delta: float,
                strategy_name: str = DEFAULT_STRATEGY) -> None:
    """Apply cash delta. Negative for buys, positive for sells."""
    with connect() as conn:
        conn.execute(
            "UPDATE paper_portfolio SET cash = cash + ? "
            "WHERE strategy_name=?",
            (delta, strategy_name),
        )


def list_open(strategy_name: str = DEFAULT_STRATEGY) -> list[dict]:
    """All open positions for the strategy, as dicts."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM paper_positions "
            "WHERE strategy_name=? AND status='open' "
            "ORDER BY ticker",
            (strategy_name,),
        ).fetchall()
    return [dict(r) for r in rows]


def open_position(*, strategy_name: str = DEFAULT_STRATEGY,
                  ticker: str, qty: float, fill_price: float,
                  as_of: date, entry_score: float | None = None,
                  sector: str | None = None) -> int:
    """Insert a new open position. Returns the position id.
    Caller is responsible for calling adjust_cash(-qty*fill_price) separately."""
    entry_value = qty * fill_price
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO paper_positions "
            "(strategy_name, ticker, status, qty, entry_price, entry_value, "
            " entry_date, entry_score, sector) "
            "VALUES (?, ?, 'open', ?, ?, ?, ?, ?, ?)",
            (strategy_name, ticker, qty, fill_price, entry_value,
             as_of.isoformat(), entry_score, sector),
        )
        return cur.lastrowid


def close_position(*, position_id: int, fill_price: float, as_of: date,
                   reason: str = "rebalance") -> float:
    """Close one open position at fill_price. Returns realized $ P&L.
    Caller is responsible for calling adjust_cash(+qty*fill_price) separately."""
    with connect() as conn:
        row = conn.execute(
            "SELECT qty, entry_price FROM paper_positions WHERE id=?",
            (position_id,),
        ).fetchone()
        if row is None:
            raise RuntimeError(f"Position id={position_id} not found")
        qty, entry_px = row["qty"], row["entry_price"]
        realized = (fill_price - entry_px) * qty
        realized_pct = (fill_price / entry_px - 1.0) * 100.0
        conn.execute(
            "UPDATE paper_positions SET "
            "  status='closed', exit_price=?, exit_value=?, "
            "  exit_date=?, exit_reason=?, "
            "  realized_pnl=?, realized_pnl_pct=? "
            "WHERE id=?",
            (fill_price, fill_price * qty, as_of.isoformat(), reason,
             realized, realized_pct, position_id),
        )
    return realized


def buy(*, strategy_name: str = DEFAULT_STRATEGY, ticker: str, qty: float,
        fill_price: float, as_of: date, entry_score: float | None = None,
        sector: str | None = None) -> int:
    """Open a position AND debit cash atomically. Returns the position id.

    Wraps open_position + adjust_cash so callers can't forget the cash leg
    (the prior split API was a foot-gun: a buy with no matching cash debit
    silently inflates NAV).
    """
    pos_id = open_position(strategy_name=strategy_name, ticker=ticker, qty=qty,
                           fill_price=fill_price, as_of=as_of,
                           entry_score=entry_score, sector=sector)
    adjust_cash(-qty * fill_price, strategy_name=strategy_name)
    return pos_id


def sell(*, position_id: int, qty: float, fill_price: float, as_of: date,
         strategy_name: str = DEFAULT_STRATEGY,
         reason: str = "rebalance") -> float:
    """Close a position AND credit cash atomically. Returns realized $ P&L.

    Counterpart to buy(); `qty` is the position's share count (credited as
    qty*fill_price). Wrapping the two legs prevents a sell that frees no cash.
    """
    realized = close_position(position_id=position_id, fill_price=fill_price,
                              as_of=as_of, reason=reason)
    adjust_cash(qty * fill_price, strategy_name=strategy_name)
    return realized


def mark_rebalanced(strategy_name: str = DEFAULT_STRATEGY) -> None:
    """Stamp last_rebalanced_at with now (UTC)."""
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute(
            "UPDATE paper_portfolio SET last_rebalanced_at=? "
            "WHERE strategy_name=?",
            (now, strategy_name),
        )
