"""Rich console tables comparing multi-profile backtest results side by side.

`render()` loads the profile archives via `execution/multi_backtest.load_archives()`
and prints a summary table, an exit-reason breakdown, and per-profile top
winners/losers. Read-only console output; writes nothing.
"""
from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from trading_bot.execution import multi_backtest


PROFILE_COLORS = {
    "conservative": "blue",
    "normal": "white",
    "aggressive": "magenta",
}


def render() -> None:
    console = Console()
    results = multi_backtest.load_archives()
    if not results:
        console.print("[red]No multi-backtest archives found.[/] "
                      "Run `python main.py multi-backtest --since YYYY-MM-DD --until YYYY-MM-DD` first.")
        return

    _render_summary(console, results)
    _render_exit_breakdown(console, results)
    _render_top_winners_losers(console, results)


def _render_summary(console: Console, results: list[multi_backtest.ProfileSimResult]) -> None:
    table = Table(title=f"Profile comparison  ({results[0].since} -> {results[0].until})",
                  box=box.SIMPLE_HEAVY, title_style="bold", header_style="bold")
    table.add_column("Metric")
    for r in results:
        c = PROFILE_COLORS.get(r.profile_name, "white")
        table.add_column(f"[{c}]{r.profile_name}[/]", justify="right")

    rows = [
        ("Starting cash", lambda r: f"${r.starting_cash:,.0f}"),
        ("Ending cash", lambda r: f"${r.ending_cash:,.0f}"),
        ("Open value", lambda r: f"${r.open_positions_value:,.0f}"),
        ("Total value", lambda r: f"${r.starting_cash + r.total_pnl:,.0f}"),
        ("Realized P&L", lambda r: _colored_money(r.realized_pnl)),
        ("Total P&L $", lambda r: _colored_money(r.total_pnl)),
        ("Total P&L %", lambda r: _colored_pct(r.total_pnl_pct)),
        ("Closed positions", lambda r: str(r.closed_count)),
        ("Open positions", lambda r: str(r.open_count)),
        ("Win rate", _win_rate),
        ("Avg win %", lambda r: _avg_win_pct(r)),
        ("Avg loss %", lambda r: _avg_loss_pct(r)),
    ]
    for label, fn in rows:
        table.add_row(label, *(fn(r) for r in results))

    console.print(table)


def _render_exit_breakdown(console: Console, results: list[multi_backtest.ProfileSimResult]) -> None:
    table = Table(title="\nExit reasons (count / total $)", box=box.SIMPLE_HEAVY, title_style="bold")
    table.add_column("Reason")
    for r in results:
        c = PROFILE_COLORS.get(r.profile_name, "white")
        table.add_column(f"[{c}]{r.profile_name}[/]", justify="right")

    reasons = ["take_profit", "stop_loss", "signal_reversal", "time_60d"]
    for reason in reasons:
        cells = []
        for r in results:
            matching = [p for p in r.closed_positions if p.get("exit_reason") == reason]
            if not matching:
                cells.append("[dim]-[/]")
                continue
            total_pnl = sum((p.get("realized_pnl") or 0) for p in matching)
            color = "green" if total_pnl >= 0 else "red"
            cells.append(f"{len(matching)} / [{color}]{total_pnl:+,.0f}[/]")
        table.add_row(reason, *cells)

    console.print(table)


def _render_top_winners_losers(console: Console, results: list[multi_backtest.ProfileSimResult]) -> None:
    for r in results:
        c = PROFILE_COLORS.get(r.profile_name, "white")
        body = []
        closed = sorted(r.closed_positions,
                        key=lambda p: (p.get("realized_pnl_pct") or 0), reverse=True)
        if not closed:
            body.append("[dim]No closed positions[/]")
        else:
            for label, picks in [("Top 3 winners", closed[:3]),
                                 ("Top 3 losers",  closed[-3:][::-1])]:
                body.append(f"[bold]{label}:[/]")
                for p in picks:
                    pnl_pct = p.get("realized_pnl_pct") or 0
                    color = "green" if pnl_pct >= 0 else "red"
                    body.append(
                        f"  {p.get('ticker'):<6} "
                        f"[{color}]{pnl_pct:+.1f}%[/]  "
                        f"({p.get('exit_reason')})"
                    )
        console.print(Panel("\n".join(body),
                            title=f"[{c}]{r.profile_name}[/]   "
                                  f"closed={r.closed_count}  "
                                  f"P&L=[{('green' if r.total_pnl>=0 else 'red')}]"
                                  f"{r.total_pnl_pct:+.2f}%[/]",
                            border_style=c))


# --- helpers -----------------------------------------------------------------

def _colored_money(v: float) -> str:
    color = "green" if v >= 0 else "red"
    sign = "+" if v >= 0 else ""
    return f"[{color}]{sign}${v:,.0f}[/]"


def _colored_pct(v: float) -> str:
    color = "green" if v >= 0 else "red"
    sign = "+" if v >= 0 else ""
    return f"[{color}]{sign}{v:.2f}%[/]"


def _win_rate(r: multi_backtest.ProfileSimResult) -> str:
    closed = r.closed_positions
    if not closed:
        return "[dim]-[/]"
    wins = sum(1 for p in closed if (p.get("realized_pnl") or 0) > 0)
    return f"{wins}/{len(closed)} ({100*wins/len(closed):.0f}%)"


def _avg_win_pct(r: multi_backtest.ProfileSimResult) -> str:
    wins = [p.get("realized_pnl_pct") or 0 for p in r.closed_positions
            if (p.get("realized_pnl") or 0) > 0]
    if not wins:
        return "[dim]-[/]"
    return f"[green]+{sum(wins)/len(wins):.1f}%[/]"


def _avg_loss_pct(r: multi_backtest.ProfileSimResult) -> str:
    losses = [p.get("realized_pnl_pct") or 0 for p in r.closed_positions
              if (p.get("realized_pnl") or 0) <= 0]
    if not losses:
        return "[dim]-[/]"
    return f"[red]{sum(losses)/len(losses):.1f}%[/]"
