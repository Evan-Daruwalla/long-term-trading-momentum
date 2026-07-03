"""Live, auto-refreshing terminal dashboard.

Full-screen rich.Live view that refreshes every N seconds. Ctrl+C to exit.
Reads the same DB the bot writes to, so when a backtest or live run is
adding positions you'll see them appear in real time.

Layout:
  +-------------------------------------------------------------+
  | Portfolio summary (top)                                     |
  +---------------+---------------------------------------------+
  | Sector        | Closed positions                            |
  | exposure +    +---------------------------------------------+
  | Exit reasons  | Open positions                              |
  +---------------+---------------------------------------------+
  | Recent activity feed                                        |
  +-------------------------------------------------------------+
"""
from __future__ import annotations

import time
from datetime import datetime

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from trading_bot.db import connect
from trading_bot.execution import market_data, portfolio as portfolio_mod


def run(*, refresh_seconds: float = 5.0, live_prices: bool = False) -> None:
    """Render the live dashboard until Ctrl+C."""
    console = Console()
    layout = _build_layout()

    try:
        with Live(layout, console=console, screen=True, refresh_per_second=4):
            while True:
                _refresh(layout, live_prices=live_prices)
                time.sleep(refresh_seconds)
    except KeyboardInterrupt:
        console.print("[dim]Dashboard closed.[/]")


def _build_layout() -> Layout:
    layout = Layout()
    layout.split(
        Layout(name="header", size=7),
        Layout(name="body"),
        Layout(name="footer", size=10),
    )
    layout["body"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=2),
    )
    layout["left"].split(
        Layout(name="sectors", ratio=1),
        Layout(name="exits", ratio=1),
    )
    layout["right"].split(
        Layout(name="closed", ratio=1),
        Layout(name="open", ratio=1),
    )
    return layout


def _refresh(layout: Layout, *, live_prices: bool) -> None:
    layout["header"].update(_header_panel())
    layout["sectors"].update(_sector_panel())
    layout["exits"].update(_exit_reason_panel())
    layout["closed"].update(_closed_panel())
    layout["open"].update(_open_panel(live_prices=live_prices))
    layout["footer"].update(_activity_panel())


# ---- panels ----------------------------------------------------------------

def _header_panel() -> Panel:
    try:
        pf = portfolio_mod.get_portfolio()
    except RuntimeError:
        return Panel(
            Align.center(Text("No portfolio. Run init-portfolio or backtest.", style="yellow")),
            title="Trading Bot",
        )
    pnl = pf.total_value - pf.starting_cash
    pnl_pct = (pnl / pf.starting_cash) * 100.0 if pf.starting_cash else 0.0
    color = "green" if pnl >= 0 else "red"
    sign = "+" if pnl >= 0 else ""

    grid = Table.grid(expand=True)
    grid.add_column(justify="left")
    grid.add_column(justify="center")
    grid.add_column(justify="right")
    grid.add_row(
        Text.from_markup(
            f"[bold]Cash[/] ${pf.cash:,.0f}    "
            f"[bold]Open[/] ${pf.open_positions_value:,.0f} ({pf.open_position_count})    "
            f"[bold]Total[/] ${pf.total_value:,.0f}"
        ),
        Text.from_markup(f"[{color} bold]{sign}${pnl:,.0f}  ({sign}{pnl_pct:.2f}%)[/]"),
        Text.from_markup(f"[dim]as of {datetime.now().strftime('%H:%M:%S')}[/]"),
    )
    return Panel(grid, title="[bold]Trading Bot — Live Dashboard[/]", border_style=color)


def _sector_panel() -> Panel:
    with connect() as conn:
        rows = conn.execute(
            "SELECT COALESCE(sector, 'Unknown') s, COUNT(*) n, SUM(entry_value) v "
            "FROM positions WHERE status='open' GROUP BY s ORDER BY v DESC"
        ).fetchall()
    if not rows:
        return Panel("[dim]No open positions[/]", title="Sector exposure", border_style="blue")

    total = sum(r["v"] for r in rows)
    table = Table(box=box.SIMPLE, expand=True, show_edge=False)
    table.add_column("Sector", style="cyan")
    table.add_column("#", justify="right")
    table.add_column("Value", justify="right")
    table.add_column("%", justify="right")
    for r in rows:
        pct = 100 * r["v"] / total if total else 0
        # Highlight near-cap exposures
        pct_text = f"{pct:.1f}%"
        if pct >= 18:
            pct_text = f"[yellow]{pct_text}[/]"
        if pct >= 20:
            pct_text = f"[red]{pct_text}[/]"
        table.add_row(r["s"][:18], str(r["n"]), f"${r['v']:,.0f}", pct_text)
    return Panel(table, title="Sector exposure (cap = 20%)", border_style="blue")


def _exit_reason_panel() -> Panel:
    with connect() as conn:
        rows = conn.execute(
            "SELECT exit_reason, COUNT(*) n, AVG(realized_pnl_pct) avg_pct, "
            "SUM(realized_pnl) total_pnl "
            "FROM positions WHERE status='closed' "
            "GROUP BY exit_reason ORDER BY n DESC"
        ).fetchall()
    if not rows:
        return Panel("[dim]No closed positions yet[/]", title="Exit reasons", border_style="blue")

    table = Table(box=box.SIMPLE, expand=True, show_edge=False)
    table.add_column("Reason")
    table.add_column("#", justify="right")
    table.add_column("Avg %", justify="right")
    table.add_column("Total $", justify="right")
    color_map = {"take_profit": "green", "stop_loss": "red",
                 "signal_reversal": "yellow", "time_60d": "white"}
    for r in rows:
        c = color_map.get(r["exit_reason"], "white")
        avg = r["avg_pct"] or 0.0
        tot = r["total_pnl"] or 0.0
        table.add_row(
            f"[{c}]{r['exit_reason']}[/]",
            str(r["n"]),
            f"{avg:+.1f}%",
            f"[{'green' if tot >= 0 else 'red'}]{tot:+,.0f}[/]",
        )
    return Panel(table, title="Exit reasons", border_style="blue")


def _closed_panel() -> Panel:
    with connect() as conn:
        rows = conn.execute(
            "SELECT ticker, qty, entry_price, exit_price, realized_pnl, "
            "realized_pnl_pct, exit_reason "
            "FROM positions WHERE status='closed' "
            "ORDER BY COALESCE(exit_date, exit_time) DESC LIMIT 12"
        ).fetchall()
    if not rows:
        return Panel("[dim]No closed positions yet[/]",
                     title="Closed positions (most recent)", border_style="green")

    table = Table(box=box.SIMPLE, expand=True, show_edge=False)
    table.add_column("Ticker", style="cyan")
    table.add_column("Qty", justify="right")
    table.add_column("Entry", justify="right")
    table.add_column("Exit", justify="right")
    table.add_column("P&L", justify="right")
    table.add_column("%", justify="right")
    table.add_column("Reason")
    color_map = {"take_profit": "green", "stop_loss": "red",
                 "signal_reversal": "yellow", "time_60d": "white"}
    for r in rows:
        pnl = r["realized_pnl"] or 0
        pct = r["realized_pnl_pct"] or 0
        c = "green" if pnl >= 0 else "red"
        rc = color_map.get(r["exit_reason"], "white")
        table.add_row(
            r["ticker"], f"{r['qty']:.0f}",
            f"{r['entry_price']:.2f}", f"{r['exit_price']:.2f}",
            f"[{c}]{pnl:+,.0f}[/]", f"[{c}]{pct:+.1f}%[/]",
            f"[{rc}]{r['exit_reason']}[/]",
        )
    return Panel(table, title=f"Closed positions (last {len(rows)})", border_style="green")


def _open_panel(*, live_prices: bool) -> Panel:
    with connect() as conn:
        rows = conn.execute(
            "SELECT ticker, qty, entry_price, entry_value, entry_score, sector, "
            "COALESCE(entry_date, substr(entry_time,1,10)) day "
            "FROM positions WHERE status='open' "
            "ORDER BY entry_value DESC LIMIT 20"
        ).fetchall()
    if not rows:
        return Panel("[dim]No open positions[/]",
                     title="Open positions", border_style="cyan")

    table = Table(box=box.SIMPLE, expand=True, show_edge=False)
    table.add_column("Ticker", style="cyan")
    table.add_column("Qty", justify="right")
    table.add_column("Entry", justify="right")
    if live_prices:
        table.add_column("Now", justify="right")
        table.add_column("P&L", justify="right")
    table.add_column("Value", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Sector")
    for r in rows:
        cells = [r["ticker"], f"{r['qty']:.0f}", f"{r['entry_price']:.2f}"]
        if live_prices:
            current = market_data.latest_price(r["ticker"])
            if current is None:
                cells += ["[dim]?[/]", "[dim]?[/]"]
            else:
                u = (current - r["entry_price"]) * r["qty"]
                up = (current - r["entry_price"]) / r["entry_price"] * 100.0
                c = "green" if u >= 0 else "red"
                cells += [f"{current:.2f}", f"[{c}]{up:+.1f}%[/]"]
        score = r["entry_score"] or 0
        score_cell = f"[bold yellow]{score}[/]" if score >= 8 else str(score)
        cells += [f"${r['entry_value']:,.0f}", score_cell, (r["sector"] or "-")[:18]]
        table.add_row(*cells)
    return Panel(table, title=f"Open positions ({len(rows)})", border_style="cyan")


def _activity_panel() -> Panel:
    with connect() as conn:
        rows = conn.execute("""
            SELECT day, SUM(buys) buys, SUM(sells) sells FROM (
              SELECT COALESCE(entry_date, substr(entry_time,1,10)) day, 1 buys, 0 sells
              FROM positions
              UNION ALL
              SELECT COALESCE(exit_date, substr(exit_time,1,10)) day, 0 buys, 1 sells
              FROM positions WHERE exit_time IS NOT NULL
            ) GROUP BY day ORDER BY day DESC LIMIT 8
        """).fetchall()
    if not rows:
        return Panel("[dim]No activity[/]", title="Recent activity", border_style="white")

    table = Table(box=box.SIMPLE, expand=True, show_edge=False)
    table.add_column("Date")
    table.add_column("Buys", justify="right")
    table.add_column("Sells", justify="right")
    for r in reversed(rows):  # ascending for readability
        b = r["buys"] or 0
        s = r["sells"] or 0
        table.add_row(
            r["day"],
            f"[green]{b}[/]" if b else "[dim]0[/]",
            f"[red]{s}[/]" if s else "[dim]0[/]",
        )
    hint = Text.from_markup(
        "  [dim]Refreshing every few seconds. Press Ctrl+C to exit.[/]"
    )
    return Panel(Group(table, hint), title="Recent activity", border_style="white")
