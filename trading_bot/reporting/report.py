"""Rich-formatted simulation report.

Reads whatever is currently in `positions` + `portfolio_state` and renders
a colored summary. Independent of any backtest run — call it whenever you
want a snapshot of the current sim state.

  python main.py report                # book-value report (fast)
  python main.py report --live         # also fetch current prices (slow, ~1s/ticker)
"""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from trading_bot.db import connect
from trading_bot.execution import market_data, portfolio as portfolio_mod


def render(*, live_prices: bool = False) -> None:
    console = Console()

    try:
        pf = portfolio_mod.get_portfolio()
    except RuntimeError:
        console.print("[red]No portfolio yet.[/] Run `python main.py init-portfolio` "
                      "or `python main.py backtest` first.")
        return

    _render_summary(console, pf)
    _render_closed(console)
    _render_open(console, live_prices=live_prices)
    _render_daily_activity(console)


def _render_summary(console: Console, pf) -> None:
    pnl = pf.total_value - pf.starting_cash
    pnl_pct = (pnl / pf.starting_cash) * 100.0 if pf.starting_cash else 0.0
    color = "green" if pnl >= 0 else "red"
    sign = "+" if pnl >= 0 else ""

    body = (
        f"Cash:           [bold]${pf.cash:>14,.2f}[/]\n"
        f"Open value:     [bold]${pf.open_positions_value:>14,.2f}[/]   "
        f"({pf.open_position_count} positions)\n"
        f"Total value:    [bold]${pf.total_value:>14,.2f}[/]\n"
        f"Starting cash:  [dim]${pf.starting_cash:>14,.2f}[/]\n"
        f"P&L:            [{color} bold]{sign}${pnl:>13,.2f}   ({sign}{pnl_pct:.2f}%)[/]"
    )
    console.print(Panel(body, title="[bold]Portfolio[/]", border_style=color, box=box.ROUNDED))


def _render_closed(console: Console) -> None:
    with connect() as conn:
        rows = conn.execute(
            "SELECT ticker, qty, entry_price, exit_price, realized_pnl, "
            "       realized_pnl_pct, exit_reason, entry_time, exit_time "
            "FROM positions WHERE status='closed' "
            "ORDER BY realized_pnl DESC"
        ).fetchall()
    if not rows:
        console.print("\n[dim]No closed positions yet.[/]\n")
        return

    table = Table(title=f"\nClosed positions ({len(rows)})", box=box.SIMPLE_HEAVY,
                  title_style="bold", header_style="bold")
    table.add_column("Ticker", style="cyan")
    table.add_column("Qty", justify="right")
    table.add_column("Entry $", justify="right")
    table.add_column("Exit $", justify="right")
    table.add_column("P&L $", justify="right")
    table.add_column("P&L %", justify="right")
    table.add_column("Reason")

    wins = 0
    losses = 0
    win_pct_sum = 0.0
    loss_pct_sum = 0.0
    for r in rows:
        pnl = r["realized_pnl"] or 0.0
        pct = r["realized_pnl_pct"] or 0.0
        is_win = pnl > 0
        if is_win:
            wins += 1
            win_pct_sum += pct
        else:
            losses += 1
            loss_pct_sum += pct
        color = "green" if is_win else "red"
        reason_color = {
            "take_profit": "green",
            "stop_loss": "red",
            "signal_reversal": "yellow",
            "time_60d": "white",
        }.get(r["exit_reason"], "white")
        table.add_row(
            r["ticker"],
            f"{r['qty']:.0f}",
            f"{r['entry_price']:.2f}",
            f"{r['exit_price']:.2f}",
            f"[{color}]{pnl:+,.2f}[/]",
            f"[{color}]{pct:+.1f}%[/]",
            f"[{reason_color}]{r['exit_reason']}[/]",
        )

    console.print(table)

    n = len(rows)
    win_rate = 100 * wins / n if n else 0.0
    avg_win = win_pct_sum / wins if wins else 0.0
    avg_loss = loss_pct_sum / losses if losses else 0.0
    expectancy_pct = (win_rate / 100 * avg_win) + ((1 - win_rate / 100) * avg_loss)
    console.print(
        f"  [bold]Win rate:[/] {wins}/{n} ([green]{win_rate:.1f}%[/])   "
        f"[bold]Avg win:[/] [green]+{avg_win:.1f}%[/]   "
        f"[bold]Avg loss:[/] [red]{avg_loss:.1f}%[/]   "
        f"[bold]Expectancy:[/] {expectancy_pct:+.2f}% per trade"
    )


def _render_open(console: Console, *, live_prices: bool) -> None:
    with connect() as conn:
        rows = conn.execute(
            "SELECT ticker, qty, entry_price, entry_value, entry_score, sector, entry_time "
            "FROM positions WHERE status='open' "
            "ORDER BY entry_value DESC"
        ).fetchall()
    if not rows:
        console.print("\n[dim]No open positions.[/]\n")
        return

    title = f"\nOpen positions ({len(rows)})"
    if live_prices:
        title += "  [dim](fetching live prices...)[/]"
    table = Table(title=title, box=box.SIMPLE_HEAVY, title_style="bold", header_style="bold")
    table.add_column("Ticker", style="cyan")
    table.add_column("Qty", justify="right")
    table.add_column("Entry $", justify="right")
    if live_prices:
        table.add_column("Now $", justify="right")
        table.add_column("Unreal $", justify="right")
        table.add_column("Unreal %", justify="right")
    table.add_column("Book value", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Sector")

    total_unreal = 0.0
    total_book = 0.0
    for r in rows:
        total_book += r["entry_value"]
        cells = [r["ticker"], f"{r['qty']:.0f}", f"{r['entry_price']:.2f}"]
        if live_prices:
            current = market_data.latest_price(r["ticker"])
            if current is None:
                cells += ["[dim]?[/]", "[dim]?[/]", "[dim]?[/]"]
            else:
                unreal = (current - r["entry_price"]) * r["qty"]
                unreal_pct = (current - r["entry_price"]) / r["entry_price"] * 100.0
                total_unreal += unreal
                color = "green" if unreal >= 0 else "red"
                cells += [
                    f"{current:.2f}",
                    f"[{color}]{unreal:+,.0f}[/]",
                    f"[{color}]{unreal_pct:+.1f}%[/]",
                ]
        cells += [
            f"{r['entry_value']:,.0f}",
            f"[bold]{r['entry_score']}[/]" if r['entry_score'] and r['entry_score'] >= 8 else f"{r['entry_score']}",
            r["sector"] or "[dim]-[/]",
        ]
        table.add_row(*cells)

    console.print(table)
    console.print(f"  [bold]Total book value:[/] ${total_book:,.0f}", end="")
    if live_prices:
        color = "green" if total_unreal >= 0 else "red"
        console.print(f"   [bold]Total unrealized:[/] [{color}]{total_unreal:+,.0f}[/]")
    else:
        console.print("\n  [dim]Run with --live to fetch current prices.[/]")


def _render_daily_activity(console: Console) -> None:
    """Buys + closes by day (entry_time + exit_time)."""
    with connect() as conn:
        rows = conn.execute("""
            SELECT day, SUM(buys) buys, SUM(sells) sells
            FROM (
              SELECT COALESCE(entry_date, substr(entry_time, 1, 10)) day, 1 buys, 0 sells
              FROM positions
              UNION ALL
              SELECT COALESCE(exit_date, substr(exit_time, 1, 10)) day, 0 buys, 1 sells
              FROM positions WHERE exit_time IS NOT NULL
            )
            GROUP BY day ORDER BY day
        """).fetchall()
    if not rows:
        return

    table = Table(title="\nDaily activity", box=box.SIMPLE, title_style="bold", header_style="bold")
    table.add_column("Date")
    table.add_column("Buys", justify="right")
    table.add_column("Sells", justify="right")

    for r in rows:
        b = r["buys"] or 0
        s = r["sells"] or 0
        table.add_row(
            r["day"],
            f"[green]{b}[/]" if b else "[dim]0[/]",
            f"[red]{s}[/]" if s else "[dim]0[/]",
        )
    console.print(table)
