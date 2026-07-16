"""Backtest portfolio: cash + open-position bookkeeping over `portfolio_state`/`positions`.

The BACKTEST counterpart to `paper_trader.py` (which owns the persistent
`paper_*` tables). This singleton `portfolio_state` row is truncated by
`factor_backtest._wipe_state()` on every run. `init_portfolio()` is idempotent
(never resets cash); `open_positions_value` is book value (sum of `entry_value`),
NOT mark-to-market. `open_position_value_by_sector()` backs the sector cap.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from trading_bot.db import connect


@dataclass
class PortfolioState:
    starting_cash: float
    cash: float
    open_positions_value: float       # sum of entry_value (book value, not MTM)
    open_position_count: int
    initialized_at: str
    updated_at: str

    @property
    def total_value(self) -> float:
        return self.cash + self.open_positions_value


def init_portfolio(starting_cash: float = 100_000.0) -> PortfolioState:
    """Create the singleton portfolio_state row. Idempotent — calling again
    is a no-op (does NOT reset cash)."""
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO portfolio_state(id, starting_cash, cash, initialized_at, updated_at) "
            "VALUES (1, ?, ?, ?, ?)",
            (starting_cash, starting_cash, now, now),
        )
    return get_portfolio()


def get_portfolio() -> PortfolioState:
    with connect() as conn:
        row = conn.execute("SELECT * FROM portfolio_state WHERE id=1").fetchone()
        if row is None:
            raise RuntimeError(
                "Portfolio not initialized. Run: python main.py init-portfolio"
            )
        agg = conn.execute(
            "SELECT COALESCE(SUM(entry_value), 0) v, COUNT(*) c "
            "FROM positions WHERE status='open'"
        ).fetchone()
    return PortfolioState(
        starting_cash=row["starting_cash"],
        cash=row["cash"],
        open_positions_value=agg["v"],
        open_position_count=agg["c"],
        initialized_at=row["initialized_at"],
        updated_at=row["updated_at"],
    )


def adjust_cash(delta: float) -> None:
    """Apply a cash delta. Negative for buys, positive for sells."""
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute(
            "UPDATE portfolio_state SET cash = cash + ?, updated_at = ? WHERE id=1",
            (delta, now),
        )


def open_position_value_by_sector() -> dict[str, float]:
    """Sum of entry_value per sector for open positions. Used for sector cap."""
    out: dict[str, float] = {}
    with connect() as conn:
        for row in conn.execute(
            "SELECT COALESCE(sector, 'UNKNOWN') s, SUM(entry_value) v "
            "FROM positions WHERE status='open' GROUP BY s"
        ):
            out[row["s"]] = row["v"] or 0.0
    return out


def has_open_position(ticker: str) -> bool:
    with connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM positions WHERE ticker=? AND status='open' LIMIT 1",
            (ticker,),
        ).fetchone()
    return row is not None
