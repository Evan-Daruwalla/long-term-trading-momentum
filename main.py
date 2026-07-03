"""Trading bot CLI entry point.

Phase 1 ships a single subcommand:
  poll-edgar  — fetch recent Form 4 filings into the SQLite store.
"""
from __future__ import annotations

import argparse
import logging
from datetime import date, timedelta

from trading_bot.db import connect, init_db
from trading_bot.execution import backtest as backtest_mod
from trading_bot.execution import monitor as monitor_mod
from trading_bot.execution import multi_backtest as multi_bt_mod
from trading_bot.execution import portfolio as portfolio_mod
from trading_bot.execution import runner as exec_runner
from trading_bot.reporting import compare as compare_mod
from trading_bot.reporting import dashboard as dashboard_mod
from trading_bot.reporting import report as report_mod
from trading_bot.scoring import clusters, scorer
from trading_bot.sources import edgar


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    # httpx logs every request at INFO; that's noise here.
    logging.getLogger("httpx").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description="Trading bot CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    poll = sub.add_parser(
        "poll-edgar", help="Fetch recent Form 4 filings into SQLite"
    )
    poll.add_argument(
        "--since",
        type=date.fromisoformat,
        default=date.today() - timedelta(days=1),
        help="Earliest filing date (YYYY-MM-DD). Default: yesterday.",
    )
    poll.add_argument(
        "--until",
        type=date.fromisoformat,
        default=date.today(),
        help="Latest filing date (YYYY-MM-DD). Default: today.",
    )
    poll.add_argument(
        "--audit", action="store_true",
        help="After polling completes, run scripts.audit_backfill over the "
             "same date range. Surfaces missing/dropped filings and recovers "
             "a sample so silent ingest losses can't accumulate. The dashboard "
             "launcher sets this by default; ad-hoc CLI runs default off.",
    )
    poll.add_argument(
        "--audit-sample", type=int, default=500,
        help="Sample size passed to the post-audit recovery (default 500). "
             "0 = recover every missing accession (slow).",
    )

    fc = sub.add_parser(
        "find-clusters",
        help="Find tickers with 2+ distinct insiders buying within N days",
    )
    fc.add_argument("--window", type=int, default=30, help="Window in days (default 30)")
    fc.add_argument("--min-filers", type=int, default=2, help="Minimum distinct filers (default 2)")

    sc = sub.add_parser("score", help="Score all tickers in the window")
    sc.add_argument("--window", type=int, default=30, help="Window in days (default 30)")
    sc.add_argument("--all", action="store_true",
                    help="Show all scored tickers (default: only tradeable, score>=5)")

    ip = sub.add_parser("init-portfolio", help="Initialize the simulated portfolio (idempotent)")
    ip.add_argument("--cash", type=float, default=100_000.0, help="Starting cash (default $100,000)")

    ex = sub.add_parser("execute", help="Place buys for tradeable scores via the simulator")
    ex.add_argument("--window", type=int, default=30, help="Scoring window in days (default 30)")

    pos = sub.add_parser("positions", help="Show portfolio + positions")
    pos.add_argument("--closed", action="store_true", help="Show closed positions instead of open")

    mon = sub.add_parser("monitor", help="Evaluate exit triggers on all open positions")

    bt = sub.add_parser("backtest", help="Walk-forward simulation over a date range (WIPES state)")
    bt.add_argument("--since", type=date.fromisoformat, required=True, help="Start date (YYYY-MM-DD)")
    bt.add_argument("--until", type=date.fromisoformat, required=True, help="End date (YYYY-MM-DD)")
    bt.add_argument("--cash", type=float, default=100_000.0, help="Starting cash (default $100,000)")

    rep = sub.add_parser("report", help="Rich-formatted simulation report")
    rep.add_argument("--live", action="store_true",
                     help="Fetch current prices for open positions (slow)")

    dash = sub.add_parser("dashboard", help="Live full-screen dashboard (Ctrl+C to exit)")
    dash.add_argument("--refresh", type=float, default=5.0, help="Refresh seconds (default 5)")
    dash.add_argument("--live", action="store_true",
                      help="Fetch live prices (slow per refresh)")

    mb = sub.add_parser("multi-backtest",
                        help="Run conservative + normal + aggressive sims sequentially")
    mb.add_argument("--since", type=date.fromisoformat, required=True, help="Start date (YYYY-MM-DD)")
    mb.add_argument("--until", type=date.fromisoformat, required=True, help="End date (YYYY-MM-DD)")
    mb.add_argument("--cash", type=float, default=100_000.0, help="Starting cash per profile (default $100K)")
    mb.add_argument("--label", type=str, default=None,
                    help="Human-readable run name shown in the web dashboard (e.g. 'R9-50DMA-tuned')")
    mb.add_argument("--resume", type=str, default=None,
                    help="Resume a specific run_id, skipping profiles whose JSON already exists")

    sub.add_parser("compare", help="Side-by-side view of the last multi-backtest run")

    web = sub.add_parser("web-dashboard",
                         help="Launch the rich web dashboard (Streamlit) in the browser")
    web.add_argument("--port", type=int, default=8501, help="Port to bind Streamlit on (default 8501)")
    web.add_argument("--no-browser", action="store_true", help="Don't auto-open the browser")

    args = parser.parse_args()
    init_db()

    if args.cmd == "poll-edgar":
        stats = edgar.poll(since=args.since, until=args.until)
        print(
            f"EDGAR poll [{args.since} -> {args.until}]: "
            f"scanned={stats['scanned']} parsed={stats['parsed']} "
            f"purchases_stored={stats['purchases_stored']} "
            f"sells_stored={stats['sells_stored']} errors={stats['errors']}"
        )
        if args.audit:
            # Auto-chained post-backfill audit. Append-only to the same log
            # the dashboard tails, so the run's "completion + audit" story is
            # in one place.
            from scripts.form4.audit_backfill import run_audit
            try:
                run_audit(
                    since=args.since, until=args.until, sample=args.audit_sample,
                )
            except Exception as e:
                logging.error("Post-poll audit failed: %s", e, exc_info=True)
    elif args.cmd == "score":
        results = scorer.score_all(window_days=args.window)
        if not args.all:
            # Hide pure-veto rows (no buys to begin with — never tradeable anyway).
            results = [r for r in results if not r.vetoed and r.score >= scorer.TRADE_THRESHOLD]
        if not results:
            print(f"No tradeable signals in last {args.window} days.")
            return
        print(f"Scoring window: last {args.window} days  ({results[0].window_start} -> {results[0].window_end})\n")
        print(f"  {'TICKER':<8} {'SCORE':>5} {'POS%':>5} {'BUYERS':>6} {'EFF':>4} {'BUY_$':>14} {'CEO?':>5}  COMPONENTS")
        for r in results:
            if r.vetoed:
                print(f"  {r.ticker:<8} {'VETO':>5} {'0':>5} {'-':>6} {'-':>4} {'-':>14} {'-':>5}  {r.veto_reason}")
                continue
            comp = " ".join(f"{k}={v}" for k, v in r.components.items())
            ceo = "yes" if r.has_ceo_cfo else "no"
            tag = "[HIGH]" if r.position_size_pct >= scorer.HIGH_CONVICTION_POSITION_PCT else ""
            print(
                f"  {r.ticker:<8} {r.score:>5} {r.position_size_pct:>5.1f} "
                f"{r.distinct_buy_filers:>6} {r.effective_cluster_filers:>4} "
                f"{r.total_buy_value:>14,.0f} {ceo:>5}  {comp} {tag}"
            )
    elif args.cmd == "init-portfolio":
        pf = portfolio_mod.init_portfolio(starting_cash=args.cash)
        print(f"Portfolio: cash=${pf.cash:,.2f} starting=${pf.starting_cash:,.2f} (initialized {pf.initialized_at})")

    elif args.cmd == "execute":
        stats = exec_runner.execute_pending(window_days=args.window)
        print(
            f"Execution: considered={stats.considered} placed={stats.placed} "
            f"already_open={stats.skipped_already_open} no_cash={stats.skipped_no_cash} "
            f"sector_cap={stats.skipped_sector_cap} no_price={stats.skipped_no_price} "
            f"errors={stats.errors}"
        )
        pf = portfolio_mod.get_portfolio()
        print(
            f"Portfolio: cash=${pf.cash:,.2f} open_value=${pf.open_positions_value:,.2f} "
            f"total=${pf.total_value:,.2f} positions={pf.open_position_count}"
        )

    elif args.cmd == "report":
        report_mod.render(live_prices=args.live)

    elif args.cmd == "dashboard":
        dashboard_mod.run(refresh_seconds=args.refresh, live_prices=args.live)

    elif args.cmd == "multi-backtest":
        results = multi_bt_mod.run_all(since=args.since, until=args.until, starting_cash=args.cash,
                                       label=args.label, resume_run_id=args.resume)
        print(f"\n=== Multi-backtest complete: {len(results)} profile(s) ===")
        for r in results:
            sign = "+" if r.total_pnl >= 0 else ""
            print(f"  {r.profile_name:<14} P&L {sign}${r.total_pnl:>10,.0f}  ({sign}{r.total_pnl_pct:.2f}%)  "
                  f"closed={r.closed_count}  open={r.open_count}")
        print("\nRun `python main.py compare` for the side-by-side view.")

    elif args.cmd == "compare":
        compare_mod.render()

    elif args.cmd == "web-dashboard":
        # Streamlit's CLI is the supported launch path — re-exec via subprocess
        # rather than calling the Streamlit Python API (which is unstable
        # across versions).
        import subprocess
        import sys
        from pathlib import Path
        app_path = Path(__file__).resolve().parent / "trading_bot" / "dashboard" / "web.py"
        cmd = [
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", str(args.port),
            "--server.headless", "true" if args.no_browser else "false",
            "--browser.gatherUsageStats", "false",
            "--theme.base", "dark",
        ]
        print(f"Launching dashboard at http://localhost:{args.port} ...")
        subprocess.run(cmd, check=False)

    elif args.cmd == "backtest":
        result = backtest_mod.run_backtest(
            since=args.since, until=args.until, starting_cash=args.cash
        )
        print(f"\n=== Backtest {result.since} -> {result.until} ===")
        print(f"Starting cash: ${result.starting_cash:>12,.2f}")
        print(f"Ending cash:   ${result.ending_cash:>12,.2f}")
        print(f"Open value:    ${result.open_positions_value:>12,.2f}")
        print(f"Total value:   ${result.ending_value:>12,.2f}")
        print(f"Realized P&L:  ${result.realized_pnl:>12,.2f}")
        print(f"Total P&L:     ${result.total_pnl:>12,.2f}  ({result.total_pnl_pct:+.2f}%)")
        print(f"Closed: {result.closed_count}   Open: {result.open_count}\n")

        # Daily activity (only days where something happened)
        active = [d for d in result.daily if d.execution.placed > 0
                  or d.monitor.closed_stop_loss + d.monitor.closed_take_profit
                     + d.monitor.closed_signal_reversal + d.monitor.closed_time_60d > 0]
        if active:
            print("Active days:")
            print(f"  {'DATE':<12} {'PLACED':>6} {'CLOSED':>6}  detail")
            for d in active:
                m = d.monitor
                closed = m.closed_stop_loss + m.closed_take_profit + m.closed_signal_reversal + m.closed_time_60d
                detail_parts = []
                if d.execution.placed: detail_parts.append(f"buys={d.execution.placed}")
                if m.closed_stop_loss: detail_parts.append(f"stop={m.closed_stop_loss}")
                if m.closed_take_profit: detail_parts.append(f"tp={m.closed_take_profit}")
                if m.closed_signal_reversal: detail_parts.append(f"reversal={m.closed_signal_reversal}")
                if m.closed_time_60d: detail_parts.append(f"60d={m.closed_time_60d}")
                print(f"  {d.day:<12} {d.execution.placed:>6} {closed:>6}  {' '.join(detail_parts)}")

        # Closed-positions detail
        with connect() as conn:
            closed = conn.execute(
                "SELECT ticker, qty, entry_price, exit_price, realized_pnl, "
                "realized_pnl_pct, exit_reason, entry_time, exit_time "
                "FROM positions WHERE status='closed' ORDER BY realized_pnl DESC"
            ).fetchall()
        if closed:
            print(f"\nClosed positions ({len(closed)}):")
            print(f"  {'TICKER':<8} {'QTY':>6} {'ENTRY':>7} {'EXIT':>7} {'P&L_$':>10} {'P&L_%':>7}  REASON")
            for r in closed:
                print(
                    f"  {r['ticker']:<8} {r['qty']:>6.0f} {r['entry_price']:>7.2f} "
                    f"{r['exit_price']:>7.2f} {r['realized_pnl']:>10,.0f} "
                    f"{r['realized_pnl_pct']:>+7.1f}  {r['exit_reason']}"
                )

            wins = sum(1 for r in closed if (r['realized_pnl'] or 0) > 0)
            print(f"\n  Win rate: {wins}/{len(closed)} ({100*wins/len(closed):.1f}%)")

        # Open positions detail
        with connect() as conn:
            opens = conn.execute(
                "SELECT ticker, qty, entry_price, entry_value, entry_score, sector "
                "FROM positions WHERE status='open' ORDER BY entry_value DESC"
            ).fetchall()
        if opens:
            print(f"\nStill-open positions ({len(opens)}):")
            print(f"  {'TICKER':<8} {'QTY':>6} {'ENTRY':>7} {'VALUE':>10} {'SCORE':>5}  SECTOR")
            for r in opens:
                print(
                    f"  {r['ticker']:<8} {r['qty']:>6.0f} {r['entry_price']:>7.2f} "
                    f"{r['entry_value']:>10,.0f} {r['entry_score']:>5}  {r['sector'] or '-'}"
                )

    elif args.cmd == "monitor":
        stats = monitor_mod.monitor_positions()
        print(
            f"Monitor: checked={stats.checked} held={stats.held} no_price={stats.no_price}\n"
            f"  closed: stop_loss={stats.closed_stop_loss} take_profit={stats.closed_take_profit} "
            f"signal_reversal={stats.closed_signal_reversal} time_60d={stats.closed_time_60d}"
        )

    elif args.cmd == "positions":
        pf = portfolio_mod.get_portfolio()
        print(
            f"Portfolio: cash=${pf.cash:,.2f} open_value=${pf.open_positions_value:,.2f} "
            f"total=${pf.total_value:,.2f} (started ${pf.starting_cash:,.2f})\n"
        )
        status = "closed" if args.closed else "open"
        with connect() as conn:
            rows = conn.execute(
                "SELECT * FROM positions WHERE status=? ORDER BY entry_time DESC", (status,)
            ).fetchall()
        if not rows:
            print(f"No {status} positions.")
            return
        if status == "open":
            print(f"  {'TICKER':<8} {'QTY':>8} {'ENTRY_$':>9} {'VALUE':>12} {'SCORE':>5} {'SECTOR':<22}  ENTERED")
            for r in rows:
                print(
                    f"  {r['ticker']:<8} {r['qty']:>8.0f} {r['entry_price']:>9.2f} "
                    f"{r['entry_value']:>12,.0f} {r['entry_score'] or 0:>5} "
                    f"{(r['sector'] or '-'):<22}  {r['entry_time'][:19]}"
                )
        else:
            print(f"  {'TICKER':<8} {'QTY':>8} {'ENTRY':>8} {'EXIT':>8} {'P&L_$':>10} {'P&L_%':>7} REASON")
            for r in rows:
                print(
                    f"  {r['ticker']:<8} {r['qty']:>8.0f} {r['entry_price']:>8.2f} "
                    f"{(r['exit_price'] or 0):>8.2f} {(r['realized_pnl'] or 0):>10,.0f} "
                    f"{(r['realized_pnl_pct'] or 0):>+7.1f} {r['exit_reason'] or '-'}"
                )

    elif args.cmd == "find-clusters":
        results = clusters.find_clusters(
            window_days=args.window, min_filers=args.min_filers
        )
        if not results:
            print(f"No clusters found in last {args.window} days.")
            return
        print(f"{len(results)} cluster(s) in last {args.window} days:\n")
        print(f"  {'TICKER':<8} {'FILERS':>7} {'EFF':>4} {'TRADES':>7} {'TOTAL_$':>15}  SUSPECT  NAMES")
        for c in results:
            flag = "co-filing" if c.suspect_co_filing else ""
            names = ", ".join(c.filer_names[:3]) + ("..." if len(c.filer_names) > 3 else "")
            print(
                f"  {c.ticker:<8} {c.filer_count:>7} {c.effective_filer_count:>4} "
                f"{c.independent_trade_count:>7} {c.total_value:>15,.0f}  "
                f"{flag:<9} {names}"
            )


if __name__ == "__main__":
    main()
