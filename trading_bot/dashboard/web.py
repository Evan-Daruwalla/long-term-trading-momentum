"""Streamlit web dashboard for the multi-profile backtest results.

Reads the versioned `var/sim_archive/runs/{run_id}/` folders and renders:

  * Overview tab — at-a-glance compare of all 3 profiles for the selected run
  * Per-profile tabs — KPI cards, exit-reason / sector / score breakdowns,
    cumulative P&L, position table, and per-position price chart with
    entry / exit markers (yfinance-backed)
  * Compare Runs tab — pick two runs and see their metrics side-by-side
  * Backfill tab — live progress bars + tail of `var/ingest_backfill.out`
    so the user can watch the EDGAR backfill from the same UI

Auto-refresh is implemented as a periodic `st.rerun()` driven by a sleep
in the sidebar — keeps the dashboard up-to-date as new runs land in the
archive without forcing a page reload.

Launch via `python main.py web-dashboard` (or directly via Streamlit:
`streamlit run trading_bot/dashboard/web.py`).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf

from trading_bot.config import DB_PATH, VAR_DIR


# Paths grouped by strategy (post-reorg 2026-05-26): Form 4 (archived) and
# Momentum (current). Logs (*.out / *.pid) stay at var/ root since they're
# runtime scratch, not strategy outputs.
ARCHIVE_DIR = VAR_DIR / "form4" / "archive"        # Form 4 backtest runs
RUNS_DIR = ARCHIVE_DIR / "runs"
OPTIMIZER_RUNS_DIR = VAR_DIR / "form4" / "optimizer"  # R15 Form 4 optimizer
MOMENTUM_RUNS_DIR = VAR_DIR / "momentum" / "runs"     # momentum single-factor
SLEEVES_RUNS_DIR  = VAR_DIR / "momentum" / "sleeves"  # momentum + low_vol sleeves

BACKFILL_LOG = VAR_DIR / "ingest_backfill.out"
BACKFILL_PID_FILE = VAR_DIR / "backfill.pid"
SIM_PID_FILE = VAR_DIR / "simulation.pid"
OPTIMIZER_PID_FILE = VAR_DIR / "optimizer.pid"
# Optimizer logs follow the convention var/optimizer_<label>.out; we pick
# the most recently modified one for the live view.
OPTIMIZER_LOG_GLOB = "optimizer_*.out"
SLEEVES_LOG_GLOB = "sleeves_*.out"


def _latest_sim_log() -> Path:
    """Pick the newest var/sim_*.out — tracks whichever sim is most recent
    (R9, R10, R11…) without a code edit per iteration."""
    candidates = sorted(VAR_DIR.glob("sim_*.out"), key=lambda p: p.stat().st_mtime,
                        reverse=True)
    return candidates[0] if candidates else VAR_DIR / "sim.out"

PROFILE_ORDER = ["conservative", "normal", "aggressive"]
PROFILE_COLORS = {
    "conservative": "#3b82f6",
    "normal": "#10b981",
    "aggressive": "#f97316",
}

EXIT_COLORS = {
    "take_profit": "#22c55e",
    "trailing_stop": "#84cc16",
    "signal_reversal": "#06b6d4",
    "time_60d": "#a855f7",
    "breakeven_stop": "#f59e0b",
    "stop_loss": "#ef4444",
}


# -----------------------------------------------------------------------------
# Data loading

@st.cache_data(ttl=10, show_spinner=False)
def list_runs() -> list[dict]:
    """All archived runs, newest first. TTL=10s so new runs surface fast.

    Includes in-progress runs (no meta.json yet) by synthesizing a placeholder
    from whichever profile JSONs have already been written. multi_backtest.py
    writes meta.json only after all 3 profiles finish; this lets the dashboard
    surface partial results while a simulation is still running.
    """
    if not RUNS_DIR.exists():
        return []
    out = []
    for d in sorted(RUNS_DIR.iterdir(), reverse=True):
        if not d.is_dir():
            continue
        meta_path = d / "meta.json"
        if meta_path.exists():
            with meta_path.open() as f:
                meta = json.load(f)
        else:
            # No meta.json yet: either an actively-running sim, or an old
            # aborted run. Distinguish via mtime — directories modified in
            # the last 12 h are treated as live; older = abandoned.
            import time as _time
            fresh = (_time.time() - d.stat().st_mtime) < 12 * 3600
            partial = None
            for prof in ["conservative", "normal", "aggressive"]:
                p = d / f"{prof}.json"
                if p.exists():
                    with p.open() as f:
                        partial = json.load(f)
                    break
            # An empty fresh dir = sim just started, no JSONs yet — still surface it.
            # An empty stale dir = abandoned skeleton — skip.
            if partial is None and not fresh:
                continue
            tag = "[RUNNING]" if fresh else "[INCOMPLETE]"
            meta = {
                "run_id": d.name,
                "label": f"{tag} {d.name}",
                "since": (partial or {}).get("since"),
                "until": (partial or {}).get("until"),
                "starting_cash": (partial or {}).get("starting_cash"),
                "in_progress": fresh,
            }
        meta["_dir"] = str(d)
        out.append(meta)
    return out


@st.cache_data(ttl=30, show_spinner=False)
def load_profile(run_id: str, profile: str) -> dict | None:
    """Load one profile's archive from one run. Memoized per (run, profile)."""
    p = RUNS_DIR / run_id / f"{profile}.json"
    if not p.exists():
        return None
    with p.open() as f:
        return json.load(f)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_price_history(ticker: str, start: str, end: str) -> pd.DataFrame:
    """yfinance daily OHLCV for the chart drill-down. 5-min cache so popular
    tickers don't get re-fetched on every interaction."""
    try:
        end_d = (date.fromisoformat(end) + timedelta(days=2)).isoformat()
        start_d = (date.fromisoformat(start) - timedelta(days=5)).isoformat()
        df = yf.Ticker(ticker).history(start=start_d, end=end_d, auto_adjust=False)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_spy_series(start: str, end: str) -> pd.DataFrame:
    """S&P 500 benchmark daily series, sourced from the real
    `spy_benchmark_paper` sleeve's NAV (a $100k buy-and-hold SPY position,
    inception 2026-05-01) — read straight from the DB, no network. Falls back
    to price_cache SPY closes if that sleeve isn't seeded. Returns columns
    nav_date (tz-naive Timestamp) and close; callers use only the ratio
    close / close[0], so the absolute scale (NAV $ vs raw price) is irrelevant.

    Replaces the old yfinance fetch, which rate-limited and intermittently left
    the S&P line blank — the "broken control" reported 2026-06-10. `start`/`end`
    are retained for the cache key + call-site compatibility; callers filter by
    `nav_date >= inception` themselves."""
    import sqlite3 as _sq
    from trading_bot.config import DB_PATH as _DB
    conn = _sq.connect(_DB)
    try:
        rows = conn.execute(
            "SELECT nav_date, total_nav FROM paper_nav "
            "WHERE strategy_name='spy_benchmark_paper' ORDER BY nav_date"
        ).fetchall()
        if not rows:    # sleeve not seeded — fall back to raw cached SPY closes
            rows = conn.execute(
                "SELECT key_date, price FROM price_cache WHERE ticker='SPY' "
                "AND kind='close' ORDER BY key_date").fetchall()
    finally:
        conn.close()
    rows = [(d, v) for d, v in rows if v is not None and v > 0]
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame({"nav_date": pd.to_datetime([d for d, _ in rows]),
                         "close": [v for _, v in rows]})


def spy_return_pct(inception) -> float | None:
    """S&P 500 (SPY) % return from `inception` (a tz-naive Timestamp) to today.
    Used for the 'control' headline. None if SPY data is unavailable."""
    if inception is None:
        return None
    spy = fetch_spy_series(inception.date().isoformat(), date.today().isoformat())
    spy = spy[spy["nav_date"] >= inception]
    if spy.empty:
        return None
    return (spy["close"].iloc[-1] / spy["close"].iloc[0] - 1.0) * 100.0


def closed_to_df(profile: dict) -> pd.DataFrame:
    rows = profile.get("closed_positions") or []
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    for col in ("entry_date", "exit_date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def open_to_df(profile: dict) -> pd.DataFrame:
    rows = profile.get("open_positions") or []
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if "entry_date" in df.columns:
        df["entry_date"] = pd.to_datetime(df["entry_date"], errors="coerce")
    return df


# -----------------------------------------------------------------------------
# Formatting helpers

def fmt_pct(v: float) -> str:
    return f"{v:+.2f}%" if v is not None else "—"


def fmt_dollars(v: float) -> str:
    if v is None:
        return "—"
    sign = "-" if v < 0 else ""
    return f"{sign}${abs(v):,.0f}"


def color_pct(v: float) -> str:
    return "#22c55e" if v > 0 else "#ef4444" if v < 0 else "#94a3b8"


# -----------------------------------------------------------------------------
# Charts

def exit_reason_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty or "exit_reason" not in df.columns:
        return go.Figure()
    g = df.groupby("exit_reason").agg(
        count=("realized_pnl_pct", "size"),
        avg_pnl_pct=("realized_pnl_pct", "mean"),
        total_pnl=("realized_pnl", "sum"),
    ).reset_index()
    g["color"] = g["exit_reason"].map(EXIT_COLORS).fillna("#64748b")
    g = g.sort_values("count", ascending=True)
    fig = go.Figure(go.Bar(
        x=g["count"], y=g["exit_reason"], orientation="h",
        marker_color=g["color"],
        text=[f"{c} trades · avg {p:+.1f}%" for c, p in zip(g["count"], g["avg_pnl_pct"])],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Trades: %{x}<br>Avg P&L: %{customdata[0]:+.1f}%<br>Total $: %{customdata[1]:,.0f}<extra></extra>",
        customdata=list(zip(g["avg_pnl_pct"], g["total_pnl"])),
    ))
    fig.update_layout(
        title="Exit reason breakdown",
        height=300, margin=dict(l=10, r=80, t=40, b=10),
        xaxis_title="Closed trades",
        yaxis_title=None,
    )
    return fig


def sector_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty or "sector" not in df.columns:
        return go.Figure()
    g = df.groupby(df["sector"].fillna("Unknown")).agg(
        count=("realized_pnl_pct", "size"),
        total_pnl=("realized_pnl", "sum"),
    ).reset_index().rename(columns={"sector": "Sector"})
    g = g.sort_values("count", ascending=False).head(12)
    fig = px.bar(
        g, x="Sector", y="count", color="total_pnl",
        color_continuous_scale=[(0, "#ef4444"), (0.5, "#94a3b8"), (1, "#22c55e")],
        color_continuous_midpoint=0,
        text="count",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        title="Sector exposure (closed trades)",
        height=300, margin=dict(l=10, r=10, t=40, b=10),
        coloraxis_colorbar=dict(title="Total $ P&L"),
    )
    return fig


def score_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty or "entry_score" not in df.columns:
        return go.Figure()
    g = df.groupby("entry_score").agg(
        count=("realized_pnl_pct", "size"),
        avg_pnl_pct=("realized_pnl_pct", "mean"),
    ).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=g["entry_score"], y=g["count"],
        marker=dict(color=g["avg_pnl_pct"], colorscale=[(0, "#ef4444"), (0.5, "#94a3b8"), (1, "#22c55e")], cmid=0,
                    colorbar=dict(title="Avg P&L %")),
        text=[f"{p:+.1f}%" for p in g["avg_pnl_pct"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Entry-score distribution (color = avg P&L %)",
        xaxis_title="Score at entry", yaxis_title="Closed trades",
        height=300, margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def cumulative_pnl_chart(df: pd.DataFrame, starting_cash: float) -> go.Figure:
    if df.empty or "exit_date" not in df.columns:
        return go.Figure()
    s = df.dropna(subset=["exit_date"]).sort_values("exit_date").copy()
    s["cum_pnl"] = s["realized_pnl"].cumsum()
    s["equity"] = starting_cash + s["cum_pnl"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=s["exit_date"], y=s["equity"],
        mode="lines", line=dict(width=2, color="#3b82f6"),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.12)",
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Equity: $%{y:,.0f}<extra></extra>",
    ))
    fig.add_hline(y=starting_cash, line_dash="dash", line_color="#64748b",
                  annotation_text=f"Start ${starting_cash:,.0f}", annotation_position="top right")
    fig.update_layout(
        title="Equity curve from realized P&L",
        height=320, margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title=None, yaxis_title="Account equity ($)",
    )
    return fig


def pnl_distribution_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty or "realized_pnl_pct" not in df.columns:
        return go.Figure()
    fig = go.Figure(go.Histogram(
        x=df["realized_pnl_pct"],
        nbinsx=40,
        marker=dict(color="#3b82f6", line=dict(color="#1e3a8a", width=0.5)),
    ))
    fig.add_vline(x=0, line_dash="dash", line_color="#64748b")
    median_pnl = df["realized_pnl_pct"].median()
    fig.add_vline(x=median_pnl, line_dash="dot", line_color="#f59e0b",
                  annotation_text=f"median {median_pnl:+.1f}%", annotation_position="top")
    fig.update_layout(
        title="Closed-trade P&L distribution (%)",
        height=300, margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title="Realized P&L %", yaxis_title="Trades",
    )
    return fig


def position_price_chart(position: dict) -> go.Figure | None:
    """Stock chart for a single closed/open position with entry & exit markers."""
    ticker = position.get("ticker")
    entry_date = position.get("entry_date")
    if not ticker or not entry_date:
        return None
    end_date = position.get("exit_date") or date.today().isoformat()
    df = fetch_price_history(ticker, str(entry_date), str(end_date))
    if df.empty:
        return None

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        increasing_line_color="#22c55e", decreasing_line_color="#ef4444",
        name=ticker, showlegend=False,
    ))

    # Entry marker
    entry_price = position.get("entry_price")
    if entry_price:
        fig.add_trace(go.Scatter(
            x=[pd.to_datetime(entry_date)], y=[entry_price],
            mode="markers+text", text=["BUY"], textposition="top center",
            marker=dict(symbol="triangle-up", size=18, color="#3b82f6",
                        line=dict(color="white", width=2)),
            name="Entry", hovertemplate="<b>BUY %{x|%Y-%m-%d}</b><br>$%{y:.2f}<extra></extra>",
        ))

    # Exit marker (only for closed positions)
    exit_date = position.get("exit_date")
    exit_price = position.get("exit_price")
    if exit_date and exit_price is not None:
        reason = position.get("exit_reason") or "exit"
        color = EXIT_COLORS.get(reason, "#64748b")
        fig.add_trace(go.Scatter(
            x=[pd.to_datetime(exit_date)], y=[exit_price],
            mode="markers+text",
            text=[f"SELL ({reason})"], textposition="bottom center",
            marker=dict(symbol="triangle-down", size=18, color=color,
                        line=dict(color="white", width=2)),
            name="Exit", hovertemplate="<b>SELL %{x|%Y-%m-%d}</b><br>$%{y:.2f}<extra></extra>",
        ))

    pnl = position.get("realized_pnl_pct")
    title_suffix = f" · {pnl:+.1f}%" if pnl is not None else " (open)"
    fig.update_layout(
        title=f"{ticker}{title_suffix}",
        height=420, margin=dict(l=10, r=10, t=40, b=10),
        xaxis_rangeslider_visible=False,
        xaxis_title=None, yaxis_title="Price ($)",
    )
    return fig


# -----------------------------------------------------------------------------
# Per-profile view

def render_profile(profile_name: str, profile_data: dict, run_meta: dict) -> None:
    pnl_pct = profile_data.get("total_pnl_pct", 0.0)
    pnl_dollars = profile_data.get("total_pnl", 0.0)
    closed_count = profile_data.get("closed_count", 0)
    open_count = profile_data.get("open_count", 0)
    starting_cash = profile_data.get("starting_cash", 100_000.0)
    ending_cash = profile_data.get("ending_cash", 0.0)
    open_value = profile_data.get("open_positions_value", 0.0)

    closed_df = closed_to_df(profile_data)
    open_df = open_to_df(profile_data)

    win_rate = (closed_df["realized_pnl_pct"] > 0).mean() * 100 if not closed_df.empty else 0.0
    avg_pnl = closed_df["realized_pnl_pct"].mean() if not closed_df.empty else 0.0

    # KPI cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total return", fmt_pct(pnl_pct), help="Realized + unrealized P&L vs starting cash")
    c2.metric("P&L ($)", fmt_dollars(pnl_dollars))
    c3.metric("Closed trades", f"{closed_count:,}")
    c4.metric("Open positions", f"{open_count:,}")
    c5.metric("Win rate", f"{win_rate:.1f}%")
    c6.metric("Avg trade", fmt_pct(avg_pnl))

    # Profile config snapshot for this run
    cfg = (run_meta.get("profiles") or {}).get(profile_name, {})
    if cfg:
        with st.expander("Profile config used in this run", expanded=False):
            cfg_cols = st.columns(4)
            cfg_cols[0].markdown(
                f"**Score gates**\n\nthreshold = `{cfg.get('trade_threshold')}`\n\n"
                f"high-conviction = `{cfg.get('high_conviction_threshold')}`"
            )
            cfg_cols[1].markdown(
                f"**Sizing**\n\nstandard = `{cfg.get('standard_position_pct')}%`\n\n"
                f"high-conv = `{cfg.get('high_conviction_position_pct')}%`"
            )
            cfg_cols[2].markdown(
                f"**Hard exits**\n\nstop-loss = `{cfg.get('stop_loss_pct')}%`\n\n"
                f"take-profit = `{cfg.get('take_profit_pct')}%`\n\n"
                f"time exit = `{cfg.get('time_exit_days')}d`"
            )
            cfg_cols[3].markdown(
                f"**Loss prevention**\n\nbreakeven = `{cfg.get('breakeven_trigger_pct')}%`\n\n"
                f"trail trigger = `{cfg.get('trailing_trigger_pct')}%`\n\n"
                f"trail dist = `{cfg.get('trailing_distance_pct')}%`"
            )

    # Cash decomposition
    st.caption(
        f"**Cash:** {fmt_dollars(ending_cash)} · "
        f"**Open value:** {fmt_dollars(open_value)} · "
        f"**Starting:** {fmt_dollars(starting_cash)} · "
        f"**Range:** {profile_data.get('since')} → {profile_data.get('until')}"
    )

    st.divider()

    # Equity curve
    if not closed_df.empty:
        st.plotly_chart(cumulative_pnl_chart(closed_df, starting_cash), use_container_width=True)

    # Charts row
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(exit_reason_chart(closed_df), use_container_width=True)
        st.plotly_chart(score_chart(closed_df), use_container_width=True)
    with col_b:
        st.plotly_chart(pnl_distribution_chart(closed_df), use_container_width=True)
        st.plotly_chart(sector_chart(closed_df), use_container_width=True)

    st.divider()

    # Position table + drill-down
    st.subheader("Positions")
    pos_tab1, pos_tab2 = st.tabs([f"Closed ({closed_count})", f"Open ({open_count})"])

    with pos_tab1:
        if closed_df.empty:
            st.info("No closed positions in this run.")
        else:
            display_cols = [
                "ticker", "entry_date", "exit_date", "entry_score", "sector",
                "qty", "entry_price", "exit_price", "exit_reason",
                "realized_pnl", "realized_pnl_pct",
            ]
            display_cols = [c for c in display_cols if c in closed_df.columns]
            df_display = closed_df[display_cols].sort_values("realized_pnl", ascending=False)
            st.dataframe(
                df_display, use_container_width=True, hide_index=True,
                column_config={
                    "realized_pnl": st.column_config.NumberColumn("P&L ($)", format="$%.2f"),
                    "realized_pnl_pct": st.column_config.NumberColumn("P&L %", format="%+.2f%%"),
                    "entry_price": st.column_config.NumberColumn("Entry", format="$%.4f"),
                    "exit_price": st.column_config.NumberColumn("Exit", format="$%.4f"),
                    "qty": st.column_config.NumberColumn("Qty", format="%.0f"),
                },
                height=320,
            )
            ticker_options = closed_df["ticker"].tolist()
            picked = st.selectbox(
                "Drill-down: pick a closed trade to chart",
                options=ticker_options,
                index=0 if ticker_options else None,
                key=f"closed_picker_{profile_name}",
            )
            if picked:
                pos_row = closed_df[closed_df["ticker"] == picked].iloc[0].to_dict()
                # Convert any pandas Timestamps to ISO strings for the chart helper.
                for k in ("entry_date", "exit_date"):
                    v = pos_row.get(k)
                    if isinstance(v, pd.Timestamp):
                        pos_row[k] = v.date().isoformat()
                fig = position_price_chart(pos_row)
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No price data available for {picked}.")

    with pos_tab2:
        if open_df.empty:
            st.info("No open positions in this run.")
        else:
            display_cols = [
                "ticker", "entry_date", "entry_score", "sector",
                "qty", "entry_price", "entry_value", "peak_close_price",
            ]
            display_cols = [c for c in display_cols if c in open_df.columns]
            st.dataframe(
                open_df[display_cols], use_container_width=True, hide_index=True,
                column_config={
                    "entry_price": st.column_config.NumberColumn("Entry", format="$%.4f"),
                    "entry_value": st.column_config.NumberColumn("Cost basis", format="$%.2f"),
                    "peak_close_price": st.column_config.NumberColumn("Peak close", format="$%.4f"),
                    "qty": st.column_config.NumberColumn("Qty", format="%.0f"),
                },
                height=320,
            )
            picked = st.selectbox(
                "Drill-down: pick an open position to chart",
                options=open_df["ticker"].tolist(),
                key=f"open_picker_{profile_name}",
            )
            if picked:
                pos_row = open_df[open_df["ticker"] == picked].iloc[0].to_dict()
                for k in ("entry_date",):
                    v = pos_row.get(k)
                    if isinstance(v, pd.Timestamp):
                        pos_row[k] = v.date().isoformat()
                fig = position_price_chart(pos_row)
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No price data available for {picked}.")


# -----------------------------------------------------------------------------
# Overview

def render_overview(run_meta: dict, run_results: dict) -> None:
    st.markdown(
        f"### Run `{run_meta.get('run_id')}`  ·  "
        f"{run_meta.get('since')} → {run_meta.get('until')}  ·  "
        f"start ${run_meta.get('starting_cash', 0):,.0f}"
    )

    cols = st.columns(3)
    for col, name in zip(cols, PROFILE_ORDER):
        data = run_results.get(name)
        with col:
            if not data:
                st.warning(f"{name.title()} — no data")
                continue
            pnl_pct = data["total_pnl_pct"]
            pnl_dol = data["total_pnl"]
            color = color_pct(pnl_pct)
            st.markdown(
                f"""
                <div style="border-left: 4px solid {PROFILE_COLORS[name]}; padding-left: 12px;">
                  <div style="color: #64748b; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">{name}</div>
                  <div style="font-size: 2.4rem; font-weight: 700; color: {color}; line-height: 1.1;">{pnl_pct:+.2f}%</div>
                  <div style="color: #94a3b8;">{fmt_dollars(pnl_dol)} · {data['closed_count']} closed · {data['open_count']} open</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Summary chart: bar of P&L per profile
    summary_df = pd.DataFrame([
        {
            "profile": name,
            "P&L %": data["total_pnl_pct"],
            "P&L $": data["total_pnl"],
            "closed": data["closed_count"],
        }
        for name in PROFILE_ORDER
        if (data := run_results.get(name))
    ])
    if not summary_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                summary_df, x="profile", y="P&L %",
                color="profile", color_discrete_map=PROFILE_COLORS,
                text=summary_df["P&L %"].map(lambda v: f"{v:+.2f}%"),
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(height=320, showlegend=False, title="Total return by profile",
                              margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            # Stack: closed_count side-by-side
            fig2 = px.bar(
                summary_df, x="profile", y="closed",
                color="profile", color_discrete_map=PROFILE_COLORS,
                text="closed",
            )
            fig2.update_traces(textposition="outside")
            fig2.update_layout(height=320, showlegend=False, title="Closed-trade count by profile",
                               margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig2, use_container_width=True)


# -----------------------------------------------------------------------------
# Compare runs

def render_compare(runs: list[dict]) -> None:
    st.markdown("Pick two runs to diff metrics across all three profiles.")
    if len(runs) < 2:
        st.info("Need at least two archived runs to compare. Run the multi-backtest twice.")
        return

    def _cmp_label(r: dict) -> str:
        return (r.get("label") or r["run_id"]) + f"  ({r.get('since')}→{r.get('until')})"

    cmp_labels = [_cmp_label(r) for r in runs]
    cmp_ids = [r["run_id"] for r in runs]
    cmp_map = dict(zip(cmp_labels, cmp_ids))

    col_a, col_b = st.columns(2)
    la = col_a.selectbox("Run A (baseline)", options=cmp_labels, index=min(1, len(cmp_labels) - 1), key="cmp_a")
    lb = col_b.selectbox("Run B (comparison)", options=cmp_labels, index=0, key="cmp_b")
    a, b = cmp_map[la], cmp_map[lb]

    rows = []
    for profile_name in PROFILE_ORDER:
        pa = load_profile(a, profile_name) or {}
        pb = load_profile(b, profile_name) or {}
        rows.append({
            "Profile": profile_name,
            "A: P&L %": pa.get("total_pnl_pct"),
            "B: P&L %": pb.get("total_pnl_pct"),
            "Δ P&L pp": (pb.get("total_pnl_pct") or 0) - (pa.get("total_pnl_pct") or 0),
            "A closed": pa.get("closed_count"),
            "B closed": pb.get("closed_count"),
            "A open": pa.get("open_count"),
            "B open": pb.get("open_count"),
        })
    df = pd.DataFrame(rows)
    st.dataframe(
        df, hide_index=True, use_container_width=True,
        column_config={
            "A: P&L %": st.column_config.NumberColumn(format="%+.2f%%"),
            "B: P&L %": st.column_config.NumberColumn(format="%+.2f%%"),
            "Δ P&L pp": st.column_config.NumberColumn(format="%+.2f"),
        },
    )

    # Side-by-side bar
    plot_df = pd.DataFrame([
        {"profile": r["Profile"], "run": "A", "P&L %": r["A: P&L %"]} for r in rows
    ] + [
        {"profile": r["Profile"], "run": "B", "P&L %": r["B: P&L %"]} for r in rows
    ])
    fig = px.bar(plot_df, x="profile", y="P&L %", color="run", barmode="group",
                 color_discrete_map={"A": "#94a3b8", "B": "#3b82f6"})
    fig.update_layout(height=360, title=f"P&L %: {a}  vs  {b}", margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------------------------------
# Backfill log tail

def _is_pid_alive(pid: int) -> bool:
    """Cross-platform PID liveness probe.

    Windows: `os.kill(pid, 0)` raises OSError WinError 87 ("parameter is
    incorrect") on EVERY pid regardless of state, so we can't use it. Shell
    out to `tasklist` instead — slower (~50ms) but works for any user-owned
    process. The CSV output starts with the image name in double quotes
    when a match exists; empty stdout means no match.

    Unix: kill(pid, 0) is reliable. ProcessLookupError = dead, success or
    PermissionError = alive (PermissionError means the process exists but
    we can't signal it, e.g. owned by another user).
    """
    if sys.platform == "win32":
        try:
            r = subprocess.run(
                ["tasklist", "/NH", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                capture_output=True, text=True, timeout=5,
            )
        except (subprocess.SubprocessError, OSError):
            return False
        # tasklist with no match prints "INFO: No tasks..." to stdout/stderr.
        # With a match, stdout has a CSV line starting with the image name.
        return r.returncode == 0 and "INFO:" not in r.stdout and bool(r.stdout.strip())
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists but unsignalable — still alive
    except OSError:
        return False


def _read_tracked_pid(pid_file: Path) -> int | None:
    """Read a PID file, verify the process is alive. Cleans stale files."""
    if not pid_file.exists():
        return None
    try:
        pid = int(pid_file.read_text().strip())
    except (ValueError, OSError):
        return None
    if _is_pid_alive(pid):
        return pid
    try:
        pid_file.unlink()
    except OSError:
        pass
    return None


def _backfill_pid() -> int | None:
    """Return PID of running backfill if alive, else None (and clean stale file)."""
    return _read_tracked_pid(BACKFILL_PID_FILE)


def _start_backfill(since: date, until: date) -> tuple[bool, str]:
    """Spawn `main.py poll-edgar` detached, write PID file, append to log."""
    if _backfill_pid() is not None:
        return False, "Backfill already running."

    project_root = VAR_DIR.parent
    cmd = [
        sys.executable,
        str(project_root / "main.py"),
        "poll-edgar",
        "--since", since.isoformat(),
        "--until", until.isoformat(),
        # Auto-audit on completion: counts missing accessions, classifies a
        # random sample (untradeable / other_codes_only / true miss), and
        # appends the report to the backfill log. See scripts/audit_backfill.py.
        "--audit",
    ]
    log_fh = open(BACKFILL_LOG, "ab")  # append-binary so the existing tail survives
    kwargs: dict = {"stdout": log_fh, "stderr": subprocess.STDOUT, "stdin": subprocess.DEVNULL}
    if sys.platform == "win32":
        # Detach so the child survives streamlit reloads and doesn't share a console.
        kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000008  # DETACHED_PROCESS
        )
    else:
        kwargs["start_new_session"] = True
    try:
        proc = subprocess.Popen(cmd, cwd=str(project_root), **kwargs)
    except Exception as e:
        log_fh.close()
        return False, f"Failed to start: {e}"
    BACKFILL_PID_FILE.write_text(str(proc.pid))
    return True, f"Started backfill PID {proc.pid} ({since} → {until})."


def _stop_backfill() -> tuple[bool, str]:
    pid = _backfill_pid()
    if pid is None:
        return False, "No backfill running."
    if sys.platform == "win32":
        # taskkill /T also kills child processes spawned by the runner.
        result = subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True, text=True,
        )
        ok = result.returncode == 0
        msg = result.stdout.strip() or result.stderr.strip() or f"taskkill rc={result.returncode}"
    else:
        try:
            os.kill(pid, 9)
            ok, msg = True, f"Killed PID {pid}."
        except OSError as e:
            ok, msg = False, str(e)
    if ok:
        try:
            BACKFILL_PID_FILE.unlink()
        except OSError:
            pass
    return ok, msg


# Two log line shapes give us "current chunk":
# 1. Chunk start (no count yet, fired before SEC search returns):
#    "Polling EDGAR chunk 2015-01-01 -> 2015-01-07  (overall 0.0%)"
# 2. Chunk header with filing count (fired after search returns):
#    "  chunk 2015-01-01 -> 2015-01-07: 8133 filings"
_CHUNK_START_RE = re.compile(
    r"Polling EDGAR chunk (\d{4}-\d{2}-\d{2}) -> (\d{4}-\d{2}-\d{2})"
)
_CHUNK_HEADER_RE = re.compile(
    r"chunk (\d{4}-\d{2}-\d{2}) -> (\d{4}-\d{2}-\d{2}): (\d+) filings"
)
# Per-chunk milestone (~5 per chunk):
#   "    chunk progress: 1029/8133 (12%)"
_CHUNK_PROGRESS_RE = re.compile(r"chunk progress: (\d+)/(\d+) \(\d+%\)")
# Whole-job line at every chunk start:
#   "Polling EDGAR chunk 2015-01-01 -> 2015-01-07  (overall 12.3%)"
_OVERALL_PCT_RE = re.compile(r"\(overall ([\d.]+)%\)")
_LOG_TS_RE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", re.MULTILINE)
# Pairs a leading timestamp with an "(overall X%)" on the same line, so we
# can derive recent throughput rather than extrapolating from job start
# (which bakes in any early-run 429 backoff or warmup).
_TS_OVERALL_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?\(overall ([\d.]+)%\)",
    re.MULTILINE,
)
_BACKFILL_RANGE_RE = re.compile(
    r"Backfill range: (\d{4}-\d{2}-\d{2}) -> (\d{4}-\d{2}-\d{2})"
)
# Chunk 100%-complete signal: every chunk that finishes emits one of these
# with the total filings processed in that chunk.
_CHUNK_DONE_RE = re.compile(r"chunk progress: \d+/(\d+) \(100%\)")

_INDEX_CACHE_DIR = VAR_DIR / "edgar_index_cache"


@st.cache_data(ttl=86400)
def _quarter_filings(year: int, qtr: int) -> list[dict]:
    """Load (or fetch + cache) a quarterly Form 4 index.

    Reuses edgar._load_quarter_index so the on-disk JSON cache stays
    consistent with what the worker produces. First fetch for a missing
    quarter blocks ~1-3s; subsequent calls hit Streamlit's in-memory cache.
    """
    cache_file = _INDEX_CACHE_DIR / f"form4_{year}_QTR{qtr}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    # Fetch via the shared edgar helper. The 30s timeout is generous because
    # this only runs on the dashboard render path for uncached quarters.
    import httpx
    from trading_bot import config
    from trading_bot.sources import edgar
    with httpx.Client(
        headers={"User-Agent": config.SEC_USER_AGENT},
        timeout=30.0, http2=False,
    ) as client:
        return edgar._load_quarter_index(client, year, qtr)


@st.cache_data(ttl=86400)
def _count_filings_in_range(since: date, until: date) -> int:
    """Total Form 4 filings filed in [since, until]. Uses cached quarterly
    indexes, fetching any missing quarters on first call.
    """
    cur_year, cur_qtr = since.year, (since.month - 1) // 3 + 1
    end_year, end_qtr = until.year, (until.month - 1) // 3 + 1
    total = 0
    while (cur_year, cur_qtr) <= (end_year, end_qtr):
        for e in _quarter_filings(cur_year, cur_qtr):
            d = date.fromisoformat(e["file_date"])
            if since <= d <= until:
                total += 1
        cur_qtr += 1
        if cur_qtr > 4:
            cur_qtr, cur_year = 1, cur_year + 1
    return total


def _parse_backfill_progress(log_text: str) -> dict:
    """Extract progress signals from the backfill log.

    All progress numbers are derived from filing counts (signals done /
    total signals), NOT from the calendar-day percent the worker prints
    in the log. Filings/day isn't uniform across the run (2020 has ~30%
    more Form 4s/day than 2015), so the calendar measure is misleading.

    Returns a dict with:
      overall_pct       : 100 * filings_processed / total_filings_in_run.
                          None until we have enough data.
      filings_total     : total Form 4 filings in the current run's date
                          range (counted from quarterly indexes).
      filings_processed : filings done so far in the current run.
      filings_remaining : filings_total - filings_processed.
      filings_per_sec   : measured throughput over the current run.
      current_chunk     : (since, until) of the chunk in flight.
      chunk_total       : filings in the in-flight chunk.
      chunk_done        : filings completed within the in-flight chunk.
      chunk_pct         : chunk_done / chunk_total * 100.
      eta_seconds       : filings_remaining / filings_per_sec.
      started_at        : datetime of the first log line (job start).
      latest_ts         : datetime of the most recent log line.
      done              : True iff "Backfill complete" line is present.
    """
    out: dict = {
        "overall_pct": None, "current_chunk": None,
        "chunk_total": None, "chunk_done": None, "chunk_pct": 0.0,
        "eta_seconds": None, "started_at": None, "latest_ts": None,
        "filings_per_sec": None, "filings_processed": None,
        "filings_total": None, "filings_remaining": None,
        "done": False,
    }
    if not log_text:
        return out

    # Determine the in-flight chunk. The "Polling EDGAR chunk" line fires
    # first (before the search returns); the count-bearing header fires
    # after. Pick whichever appears LATER in the log so we always reflect
    # the freshest chunk, even when only the start line has been written.
    chunk_starts = list(_CHUNK_START_RE.finditer(log_text))
    chunk_headers = list(_CHUNK_HEADER_RE.finditer(log_text))
    last_start = chunk_starts[-1] if chunk_starts else None
    last_header = chunk_headers[-1] if chunk_headers else None
    chunk_anchor = max(
        (m for m in (last_start, last_header) if m is not None),
        key=lambda m: m.start(), default=None,
    )

    if chunk_anchor is not None:
        out["current_chunk"] = (chunk_anchor.group(1), chunk_anchor.group(2))
        # Filing count comes from the header form; the start form has none.
        if last_header is not None and (
            last_start is None or last_header.start() >= last_start.start()
        ):
            try:
                out["chunk_total"] = int(last_header.group(3))
            except (ValueError, IndexError):
                pass

        # Chunk-progress milestones — only count those AFTER the latest
        # chunk anchor; earlier chunks' progress lines are stale.
        tail = log_text[chunk_anchor.end():]
        progress_matches = _CHUNK_PROGRESS_RE.findall(tail)
        if progress_matches:
            try:
                done, total = int(progress_matches[-1][0]), int(progress_matches[-1][1])
                out["chunk_done"] = done
                out["chunk_total"] = total  # most accurate live number
                if total > 0:
                    out["chunk_pct"] = 100.0 * done / total
            except ValueError:
                pass

    # Timestamps: first and last
    ts_matches = _LOG_TS_RE.findall(log_text)
    if ts_matches:
        try:
            out["started_at"] = datetime.strptime(ts_matches[0], "%Y-%m-%d %H:%M:%S")
            out["latest_ts"] = datetime.strptime(ts_matches[-1], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass

    # Find the current run's date range from the most recent "Backfill range"
    # line. Each restart emits one. Everything before it is from a prior run
    # and shouldn't count toward this run's progress.
    range_matches = list(_BACKFILL_RANGE_RE.finditer(log_text))
    if not range_matches:
        out["done"] = "Backfill complete" in log_text
        return out
    last_range = range_matches[-1]
    current_run_text = log_text[last_range.start():]
    try:
        run_since = date.fromisoformat(last_range.group(1))
        run_until = date.fromisoformat(last_range.group(2))
    except ValueError:
        out["done"] = "Backfill complete" in log_text
        return out

    # Cumulative filings processed in current run: sum of fully-completed
    # chunk totals + the in-flight chunk's progress.
    completed_filings = sum(
        int(m) for m in _CHUNK_DONE_RE.findall(current_run_text)
    )
    in_flight = out["chunk_done"] or 0
    out["filings_processed"] = completed_filings + in_flight

    # Total filings in run's date range — exact count from quarterly indexes.
    # Best-effort: if a quarter fetch fails (e.g. SEC down at dash render time),
    # filings_total stays None and the bar/ETA show "starting…".
    try:
        out["filings_total"] = _count_filings_in_range(run_since, run_until)
    except Exception:
        pass

    if out["filings_total"]:
        out["filings_remaining"] = max(0, out["filings_total"] - out["filings_processed"])
        out["overall_pct"] = 100.0 * out["filings_processed"] / out["filings_total"]

    # Throughput: filings_processed / elapsed_wall_clock.
    run_ts = _LOG_TS_RE.findall(current_run_text)
    if run_ts and out["latest_ts"] is not None and out["filings_processed"]:
        try:
            run_started = datetime.strptime(run_ts[0], "%Y-%m-%d %H:%M:%S")
            elapsed = (out["latest_ts"] - run_started).total_seconds()
            if elapsed > 0:
                out["filings_per_sec"] = out["filings_processed"] / elapsed
        except ValueError:
            pass

    if out["filings_per_sec"] and out["filings_remaining"]:
        out["eta_seconds"] = out["filings_remaining"] / out["filings_per_sec"]

    out["done"] = "Backfill complete" in log_text
    return out


def _format_eta(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {sec}s"
    hours, minutes = divmod(minutes, 60)
    if hours < 48:
        return f"{hours}h {minutes}m"
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h"


@st.cache_data(ttl=15)
def _backfill_coverage() -> dict:
    """Return coverage stats: monthly counts, full range, and missing months.

    Cheap query (~1ms on 500K rows). Cached for 15s so repeat renders during
    auto-refresh don't hammer the DB.
    """
    from trading_bot.db import connect

    with connect() as c:
        rng = c.execute(
            "SELECT MIN(filed_at), MAX(filed_at), COUNT(*) FROM signals"
        ).fetchone()
        rows = c.execute(
            "SELECT substr(filed_at,1,7) AS ym, COUNT(*) "
            "FROM signals GROUP BY ym ORDER BY ym"
        ).fetchall()

    monthly = {r[0]: r[1] for r in rows}
    return {
        "min_date": rng[0],
        "max_date": rng[1],
        "total": rng[2] or 0,
        "monthly": monthly,
    }


def _render_backfill_coverage() -> None:
    cov = _backfill_coverage()
    if cov["total"] == 0:
        st.warning("No signals in DB yet — run a backfill to populate.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Earliest filing", cov["min_date"])
    c2.metric("Latest filing", cov["max_date"])
    c3.metric("Total signals", f"{cov['total']:,}")

    # Build a continuous month series from min→max so gaps surface visibly.
    monthly = cov["monthly"]
    start = datetime.strptime(cov["min_date"][:7], "%Y-%m").date().replace(day=1)
    end = datetime.strptime(cov["max_date"][:7], "%Y-%m").date().replace(day=1)
    months: list[str] = []
    cur = start
    while cur <= end:
        months.append(cur.strftime("%Y-%m"))
        # Advance one month
        if cur.month == 12:
            cur = cur.replace(year=cur.year + 1, month=1)
        else:
            cur = cur.replace(month=cur.month + 1)

    df = pd.DataFrame(
        {"month": months, "signals": [monthly.get(m, 0) for m in months]}
    )
    # Color empty months red so gaps pop.
    df["status"] = df["signals"].apply(
        lambda n: "missing" if n == 0 else ("sparse" if n < 1000 else "ok")
    )
    fig = px.bar(
        df, x="month", y="signals", color="status",
        color_discrete_map={"ok": "#10b981", "sparse": "#f59e0b", "missing": "#ef4444"},
        title="Signals per month (red = missing, amber = <1k = likely partial)",
    )
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10),
                      xaxis_tickangle=-45, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    # List missing/sparse months explicitly.
    missing = df[df["status"] == "missing"]["month"].tolist()
    sparse = df[df["status"] == "sparse"]["month"].tolist()
    if missing:
        st.error(f"**Missing months ({len(missing)}):** {', '.join(missing)}")
    if sparse:
        st.warning(f"**Sparse months ({len(sparse)}):** {', '.join(sparse)}")
    if not missing and not sparse:
        st.success(f"✅ Continuous coverage from {cov['min_date']} to {cov['max_date']}.")


def _sim_pid() -> int | None:
    return _read_tracked_pid(SIM_PID_FILE)


def _start_simulation(since: date, until: date, cash: float, label: str | None = None) -> tuple[bool, str]:
    if _sim_pid() is not None:
        return False, "Simulation already running."
    project_root = VAR_DIR.parent
    cmd = [
        sys.executable,
        str(project_root / "main.py"),
        "multi-backtest",
        "--since", since.isoformat(),
        "--until", until.isoformat(),
        "--cash", str(cash),
    ]
    if label and label.strip():
        cmd += ["--label", label.strip()]
    log_fh = open(_latest_sim_log(), "ab")
    kwargs: dict = {"stdout": log_fh, "stderr": subprocess.STDOUT, "stdin": subprocess.DEVNULL}
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000008
        )
    else:
        kwargs["start_new_session"] = True
    try:
        proc = subprocess.Popen(cmd, cwd=str(project_root), **kwargs)
    except Exception as e:
        log_fh.close()
        return False, f"Failed to start: {e}"
    SIM_PID_FILE.write_text(str(proc.pid))
    return True, f"Started simulation PID {proc.pid} ({since} → {until}, cash=${cash:,.0f})."


def _stop_simulation() -> tuple[bool, str]:
    pid = _sim_pid()
    if pid is None:
        return False, "No simulation running."
    if sys.platform == "win32":
        result = subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True, text=True,
        )
        ok = result.returncode == 0
        msg = result.stdout.strip() or result.stderr.strip() or f"taskkill rc={result.returncode}"
    else:
        try:
            os.kill(pid, 9)
            ok, msg = True, f"Killed PID {pid}."
        except OSError as e:
            ok, msg = False, str(e)
    if ok:
        try:
            SIM_PID_FILE.unlink()
        except OSError:
            pass
    return ok, msg


def _parse_log_ts(line: str) -> datetime | None:
    try:
        return datetime.strptime(line[:23], "%Y-%m-%d %H:%M:%S,%f")
    except (ValueError, IndexError):
        return None


def _estimate_eta(progress_lines: list[str], profile_lines: list[str]) -> str | None:
    """Project remaining wall-clock from progress-line cadence.

    Each profile resets to day 0; '=== Profile X/Y' tells us where we are in
    the multi-profile sweep. ETA = time-to-finish-current-profile + (profiles
    left × avg-profile-duration). The avg uses the current profile's observed
    rate so far — pessimistic early, sharper as the run accumulates samples.
    """
    if not progress_lines:
        return None
    last = progress_lines[-1]
    last_ts = _parse_log_ts(last)
    if last_ts is None:
        return None
    try:
        n_done, total = (int(x) for x in last.split("progress:")[1].split("days")[0].split("/"))
    except (IndexError, ValueError):
        return None

    # Current profile = X/Y from latest "=== Profile X/Y: name ..." line.
    cur_idx, n_profiles = 1, 1
    if profile_lines:
        try:
            spec = profile_lines[-1].split("Profile")[1].split(":")[0].strip()
            cur_idx, n_profiles = (int(x) for x in spec.split("/"))
        except (IndexError, ValueError):
            pass

    # Find first progress line *within the current profile* — anything after
    # the latest "=== Profile" log entry. Falls back to the run start if we
    # can't locate that boundary.
    cur_profile_ts = _parse_log_ts(profile_lines[-1]) if profile_lines else None
    in_profile = [ln for ln in progress_lines
                  if cur_profile_ts is None or
                  ((_parse_log_ts(ln) or last_ts) >= cur_profile_ts)]
    first = in_profile[0] if in_profile else progress_lines[0]
    first_ts = _parse_log_ts(first) or last_ts
    try:
        n_first = int(first.split("progress:")[1].split("/")[0].strip())
    except (IndexError, ValueError):
        n_first = 0

    elapsed = (last_ts - first_ts).total_seconds()
    days_progressed = n_done - n_first
    if elapsed <= 0 or days_progressed <= 0:
        return None
    rate = days_progressed / elapsed  # backtest-days per real-second
    secs_per_profile = total / rate
    secs_remaining_cur = (total - n_done) / rate
    profiles_left = max(0, n_profiles - cur_idx)
    eta_secs = secs_remaining_cur + profiles_left * secs_per_profile
    eta_dt = datetime.now() + timedelta(seconds=eta_secs)

    def _fmt(s: float) -> str:
        h, rem = divmod(int(s), 3600)
        m, _ = divmod(rem, 60)
        return f"{h}h{m:02d}m" if h else f"{m}m"

    return (
        f"⏱ ETA: ~{_fmt(eta_secs)} remaining · finishes ~{eta_dt.strftime('%H:%M')} "
        f"(profile {cur_idx}/{n_profiles}, ~{_fmt(secs_per_profile)}/profile)"
    )


def render_simulation() -> None:
    st.markdown("### Multi-profile simulation")

    running_pid = _sim_pid()
    status_col, _ = st.columns([3, 2])
    with status_col:
        if running_pid is not None:
            st.success(f"🟢 Running (PID {running_pid})")
        else:
            st.info("⚪ Not running")

    with st.expander("Start a new simulation", expanded=running_pid is None):
        c1, c2, c3 = st.columns(3)
        since_in = c1.date_input("Since", value=date(2021, 5, 1), key="sim_since")
        until_in = c2.date_input("Until", value=date.today(), key="sim_until")
        cash_in = c3.number_input("Cash $", value=100_000, step=10_000, key="sim_cash")
        label_in = st.text_input(
            "Run label (optional)",
            placeholder="e.g. R9-50DMA-tuned  — shown in the dashboard run selector",
            key="sim_label",
        )
        if st.button("▶ Start sim", disabled=running_pid is not None,
                     use_container_width=True, type="primary"):
            ok, msg = _start_simulation(since_in, until_in, float(cash_in), label=label_in or None)
            (st.success if ok else st.error)(msg)
            time.sleep(0.5)
            st.rerun()

    if st.button("⏸ Pause sim", disabled=running_pid is None, type="secondary"):
        ok, msg = _stop_simulation()
        (st.success if ok else st.error)(msg)
        time.sleep(0.5)
        st.rerun()

    st.divider()
    st.markdown("#### Progress")
    sim_log = _latest_sim_log()
    if not sim_log.exists():
        st.info(f"No simulation log yet at {sim_log}.")
        return
    st.caption(f"Tailing `{sim_log.name}`")
    try:
        text = sim_log.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        st.error(f"Could not read log: {e}")
        return

    lines = text.splitlines()

    # Latest profile being run.
    profile_lines = [ln for ln in lines if "=== Profile" in ln]
    if profile_lines:
        st.info(f"`{profile_lines[-1].strip().split(' INFO ')[-1]}`")

    # Latest backtest progress line for the current profile.
    progress_lines = [ln for ln in lines if "backtest progress:" in ln]
    if progress_lines:
        last = progress_lines[-1]
        # Parse out the percentage: "backtest progress: N/M days (P%)  cur=YYYY-MM-DD"
        try:
            pct = int(last.split("(")[1].split("%")[0])
        except (IndexError, ValueError):
            pct = 0
        st.progress(pct / 100, text=f"{pct}% — {last.strip().split(' INFO ')[-1]}")

        eta_text = _estimate_eta(progress_lines, profile_lines)
        if eta_text:
            st.caption(eta_text)
    else:
        st.caption("Waiting for first progress line…")

    last_n = st.slider("Lines to show", 20, 500, 80, key="sim_tail_lines")
    st.code("\n".join(lines[-last_n:]) or "(log empty)", language="log")


def render_backfill() -> None:
    st.markdown("### EDGAR backfill")

    # ---- Controls row ----
    running_pid = _backfill_pid()
    status_col, btn_col = st.columns([3, 2])
    with status_col:
        if running_pid is not None:
            st.success(f"🟢 Running (PID {running_pid})")
        else:
            st.info("⚪ Not running")

    with st.expander("Start a new backfill", expanded=running_pid is None):
        c1, c2, c3 = st.columns(3)
        default_since = date(2024, 1, 1)
        default_until = date.today()
        since_in = c1.date_input("Since", value=default_since, key="bf_since")
        until_in = c2.date_input("Until", value=default_until, key="bf_until")
        if c3.button("▶ Start", disabled=running_pid is not None,
                     use_container_width=True, type="primary"):
            ok, msg = _start_backfill(since_in, until_in)
            (st.success if ok else st.error)(msg)
            time.sleep(0.5)
            st.rerun()

    if st.button("⏸ Pause", disabled=running_pid is None, type="secondary"):
        ok, msg = _stop_backfill()
        (st.success if ok else st.error)(msg)
        time.sleep(0.5)
        st.rerun()

    st.divider()
    st.markdown("#### Coverage")
    _render_backfill_coverage()

    st.divider()
    if not BACKFILL_LOG.exists():
        st.info(f"No backfill log yet at {BACKFILL_LOG}.")
        return
    try:
        text = BACKFILL_LOG.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        st.error(f"Could not read log: {e}")
        return

    # ---- Progress bars ----
    st.markdown("#### Progress")
    prog = _parse_backfill_progress(text)

    overall = prog["overall_pct"]
    if overall is not None:
        rate = prog["filings_per_sec"]
        rate_str = f"{rate * 60:.0f}/min" if rate else "—"
        done = prog["filings_processed"] or 0
        total = prog["filings_total"] or 0
        st.progress(min(int(overall), 100),
                    text=f"Overall: {done:,}/{total:,} filings "
                         f"({overall:.2f}%)  ·  {rate_str}  ·  "
                         f"ETA {_format_eta(prog['eta_seconds'])}")
    else:
        st.progress(0, text="Overall: starting…")

    if prog["current_chunk"] is not None:
        c_since, c_until = prog["current_chunk"]
        c_done = prog["chunk_done"] or 0
        c_total = prog["chunk_total"] or 0
        chunk_label = (
            f"Current chunk {c_since} → {c_until}  ·  "
            f"{c_done:,}/{c_total:,} filings ({prog['chunk_pct']:.0f}%)"
        )
        st.progress(min(int(prog["chunk_pct"]), 100), text=chunk_label)

    if prog["done"]:
        st.success("✅ Backfill complete")
    elif running_pid is None and prog["overall_pct"] is not None:
        st.warning("⚠ Process not running but log isn't marked complete — "
                   "the backfill may have died. Check the tail below.")

    # ---- Live tail ----
    st.markdown("#### Live tail")
    lines = text.splitlines()
    last_n = st.slider("Lines to show", 20, 500, 80)
    st.code("\n".join(lines[-last_n:]) or "(log empty)", language="log")


# -----------------------------------------------------------------------------
# Optimizer (parameter-search) tab
#
# Renders the live status of scripts/optimize_r15.py. Two progress scales:
#  - Trial N/total — from "[ N/T] running trial-NN:" header lines.
#  - Within-trial day progress — from the underlying backtest's
#    "backtest progress: D/T days (P%)" lines.

_OPT_TRIAL_RE = re.compile(r"^\[\s*(\d+)/(\d+)\]\s+running\s+(trial-\d+):\s+(.+)$",
                           re.MULTILINE)
_OPT_RESULT_RE = re.compile(
    r"->\s+tpnl=(-?[\d.]+)%\s+worst=(-?[\d.]+)%\s+cov=(-?[\d.]+)%\s+closed=(\d+)\s+\(([\d.]+)s\)"
)
_OPT_BTPROG_RE = re.compile(
    r"backtest progress:\s+(\d+)/(\d+)\s+days\s+\((\d+)%\)\s+cur=(\d{4}-\d{2}-\d{2})"
)


def _optimizer_pid() -> int | None:
    return _read_tracked_pid(OPTIMIZER_PID_FILE)


def _latest_optimizer_log() -> Path | None:
    candidates = sorted(VAR_DIR.glob(OPTIMIZER_LOG_GLOB),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _parse_optimizer_progress(text: str) -> dict:
    """Extract current trial #, current backtest %, and per-trial results.
    Returns a dict the renderer can consume directly."""
    trials = list(_OPT_TRIAL_RE.finditer(text))
    if not trials:
        return {"started": False, "current_trial": 0, "total_trials": 0,
                "trial_label": "", "trial_params": "", "results": [],
                "bt_done": 0, "bt_total": 0, "bt_pct": 0, "bt_cur": ""}
    last_trial = trials[-1]
    current_trial = int(last_trial.group(1))
    total_trials  = int(last_trial.group(2))
    trial_label   = last_trial.group(3)
    trial_params  = last_trial.group(4)

    # Per-completed-trial results
    results = []
    # Pair each trial header with the FIRST "-> tpnl=" that follows it.
    headers = [(m.start(), int(m.group(1)), m.group(3), m.group(4)) for m in trials]
    res_matches = list(_OPT_RESULT_RE.finditer(text))
    for hstart, idx, label, params in headers:
        nxt = next((rm for rm in res_matches if rm.start() > hstart), None)
        if nxt is None:
            continue
        results.append({
            "trial": idx, "label": label, "params": params,
            "tpnl": float(nxt.group(1)), "worst": float(nxt.group(2)),
            "cov": float(nxt.group(3)), "closed": int(nxt.group(4)),
            "elapsed_s": float(nxt.group(5)),
        })

    # Within-trial backtest progress: most recent line in the file
    bt_matches = list(_OPT_BTPROG_RE.finditer(text))
    if bt_matches:
        last = bt_matches[-1]
        bt_done, bt_total, bt_pct, bt_cur = (
            int(last.group(1)), int(last.group(2)),
            int(last.group(3)), last.group(4),
        )
    else:
        bt_done = bt_total = bt_pct = 0
        bt_cur = ""

    return {"started": True, "current_trial": current_trial,
            "total_trials": total_trials, "trial_label": trial_label,
            "trial_params": trial_params, "results": results,
            "bt_done": bt_done, "bt_total": bt_total, "bt_pct": bt_pct,
            "bt_cur": bt_cur}


def render_optimizer() -> None:
    st.markdown("### Parameter-search optimizer")

    running_pid = _optimizer_pid()
    status_col, _ = st.columns([3, 2])
    with status_col:
        if running_pid is not None:
            st.success(f"🟢 Running (PID {running_pid})")
        else:
            st.info("⚪ Not running")

    log_path = _latest_optimizer_log()
    if log_path is None:
        st.info("No optimizer log yet — launch via `python -m scripts.optimize_r15`.")
        return
    st.caption(f"Tailing `{log_path.name}`")

    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        st.error(f"Could not read log: {e}")
        return

    prog = _parse_optimizer_progress(text)

    # ---- Trial-level progress ----
    st.markdown("#### Progress")
    if not prog["started"]:
        st.progress(0, text="Waiting for first trial…")
    else:
        completed = len(prog["results"])
        cur = prog["current_trial"]
        total = prog["total_trials"]
        # Overall % = (completed full trials + within-trial fraction) / total
        within = (prog["bt_pct"] / 100.0) if cur > completed else 0.0
        overall_pct = (completed + within) / max(total, 1) * 100.0
        st.progress(min(int(overall_pct), 100),
                    text=f"Overall: trial {cur}/{total} "
                         f"({completed} complete)  ·  {overall_pct:.1f}%")
        if prog["bt_total"]:
            st.progress(min(prog["bt_pct"], 100),
                        text=f"Current trial ({prog['trial_label']}): "
                             f"{prog['bt_done']:,}/{prog['bt_total']:,} days "
                             f"({prog['bt_pct']}%)  ·  through {prog['bt_cur']}")

        # Live params for the currently-running trial
        st.caption(f"**{prog['trial_label']}** params: `{prog['trial_params']}`")

    # ---- Leaderboard so far ----
    if prog["results"]:
        st.markdown("#### Leaderboard (completed trials)")
        rows = sorted(prog["results"], key=lambda r: r["tpnl"], reverse=True)
        import pandas as pd
        df = pd.DataFrame([{
            "Trial": r["label"],
            "TPnl %":   r["tpnl"],
            "Worst %":  r["worst"],
            "Cov %":    r["cov"],
            "Closed":   r["closed"],
            "Time (s)": r["elapsed_s"],
            "Params":   r["params"],
        } for r in rows])
        st.dataframe(
            df.style.format({"TPnl %": "{:+.2f}", "Worst %": "{:+.2f}",
                             "Cov %": "{:.1f}", "Time (s)": "{:.0f}"}),
            use_container_width=True,
        )
        best = rows[0]
        st.success(f"Best so far: **{best['label']}** "
                   f"tpnl={best['tpnl']:+.2f}% (worst={best['worst']:+.2f}%, "
                   f"cov={best['cov']:.1f}%, closed={best['closed']})")
    else:
        st.caption("No completed trials yet.")

    # Done detection
    if "Full results written to" in text:
        st.success("✅ Optimizer complete")
    elif running_pid is None and prog["started"]:
        st.warning("⚠ Process not running but log isn't marked complete — "
                   "the optimizer may have died. Check the tail below.")

    # ---- Live tail ----
    st.markdown("#### Live tail")
    lines = text.splitlines()
    last_n = st.slider("Lines to show", 20, 500, 80, key="opt_tail_lines")
    st.code("\n".join(lines[-last_n:]) or "(log empty)", language="log")


def _load_sleeves_runs() -> list[dict]:
    """Read all var/sleeves_runs/*.json into a list sorted newest-first.

    Each entry already carries run_id / since / until / per_sleeve / combined_*
    so we just attach a label parsed from the filename suffix.
    """
    if not SLEEVES_RUNS_DIR.exists():
        return []
    runs: list[dict] = []
    for p in sorted(SLEEVES_RUNS_DIR.glob("*.json"),
                    key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        # label = filename after the timestamp prefix, sans .json
        stem = p.stem  # e.g. "20260526-041502_sleeves_in_sample"
        d["label"] = stem.split("_", 1)[1] if "_" in stem else stem
        d["_path"] = str(p)
        runs.append(d)
    return runs


def _latest_sleeves_log() -> Path | None:
    cands = sorted(VAR_DIR.glob(SLEEVES_LOG_GLOB),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0] if cands else None


def render_factors() -> None:
    """Factor-portfolio (momentum / low_vol sleeve) runs.

    These are the Phase 2a outputs after Form 4 was retired. Each JSON in
    var/sleeves_runs/ is a paired in-sample / held-out sleeves run that
    combined two independent factor sleeves into a single equity curve.
    """
    st.markdown("### Factor portfolios — sleeves")
    st.caption(
        "Two-sleeve multi-factor: each factor (momentum 12-1, low-vol 60d) "
        "runs as its own equal-weight top-100 portfolio with $50K starting "
        "capital, monthly rebalance. Curves combined post-hoc."
    )

    runs = _load_sleeves_runs()
    if not runs:
        st.info(
            "No sleeve runs yet. Launch via:\n"
            "`python -m scripts.run_sleeves_chain`  (90 min in-sample + held-out)"
        )
        # Still show live log if a run is mid-flight
        log = _latest_sleeves_log()
        if log and log.exists():
            st.markdown("#### Live tail")
            try:
                st.code(log.read_text(encoding="utf-8", errors="replace")[-4000:],
                        language="log")
            except OSError as e:
                st.error(f"Could not read log: {e}")
        return

    labels = [f"{r['label']}  ({r.get('since')} → {r.get('until')})" for r in runs]
    pick = st.selectbox("Sleeves run", options=labels, index=0, key="sleeves_pick")
    sel = runs[labels.index(pick)]

    # ---- Headline ----
    per = sel.get("per_sleeve", {})
    combined_tpnl = sel.get("combined_total_pnl_pct")
    elapsed = sel.get("elapsed_seconds", 0.0)
    # Up to 2 per-sleeve cards; if only 1 sleeve exists (mom_v1/v2 standalone),
    # only show the one. Pad with wall-time for the remainder.
    sleeve_names = list(per.keys())[:2]
    cols = st.columns(2 + len(sleeve_names) + 1)
    cols[0].metric("Combined total return",
              f"{combined_tpnl:+.2f}%" if combined_tpnl is not None else "—")
    cols[1].metric("Top-N per sleeve",
              str(sel.get("top_n_per_sleeve", "—")))
    for i, name in enumerate(sleeve_names):
        cols[2 + i].metric(f"{name} sleeve",
              f"{per.get(name,{}).get('total_pnl_pct', 0):+.2f}%")
    cols[-1].metric("Wall time", f"{elapsed/60:.1f} min")

    # ---- Equity curve ----
    curve = sel.get("combined_equity_curve") or []
    if curve:
        df = pd.DataFrame(curve, columns=["date", "equity"])
        df["date"] = pd.to_datetime(df["date"])
        fig = px.line(df, x="date", y="equity",
                      title=f"Combined equity ({sel.get('since')} → {sel.get('until')})")
        fig.update_layout(height=380, margin=dict(l=40, r=20, t=40, b=30),
                          yaxis_tickformat="$,.0f")
        st.plotly_chart(fig, use_container_width=True)

    # ---- Per-year Sharpe table (combined + per-sleeve) ----
    yrs = sorted({y for d in [sel.get("combined_yearly_sharpe", {})] + [
        per.get(name, {}).get("yearly_sharpe", {}) for name in per]
                 for y in d})
    if yrs:
        rows = []
        for y in yrs:
            row = {"year": y}
            row["combined"] = sel.get("combined_yearly_sharpe", {}).get(y)
            for name in per:
                row[name] = per[name].get("yearly_sharpe", {}).get(y)
            rows.append(row)
        sdf = pd.DataFrame(rows).set_index("year")
        st.markdown("#### Annualized Sharpe by year")
        st.dataframe(sdf.style.format("{:+.2f}", na_rep="—"),
                     use_container_width=True)

    # ---- Per-sleeve detail ----
    st.markdown("#### Per-sleeve detail")
    for name, d in per.items():
        with st.expander(f"{name}", expanded=False):
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("Total return", f"{d.get('total_pnl_pct',0):+.2f}%")
            cc2.metric("Closed trades", f"{d.get('closed_count', 0):,}")
            cc3.metric("Open trades", f"{d.get('open_count', 0):,}")

    # ---- Compare table across all runs ----
    st.markdown("#### All runs — compare")
    # Build dynamic columns from whatever sleeves appear across runs.
    all_sleeves = sorted({s for r in runs for s in r.get("per_sleeve", {})})
    rows = []
    for r in runs:
        rp = r.get("per_sleeve", {})
        row = {
            "Label": r["label"],
            "Since": r.get("since"),
            "Until": r.get("until"),
            "Top-N": r.get("top_n_per_sleeve"),
            "Combined %": r.get("combined_total_pnl_pct"),
        }
        for s in all_sleeves:
            row[f"{s} %"] = rp.get(s, {}).get("total_pnl_pct")
        row["Cash/sleeve"] = f"${r.get('cash_per_sleeve', 0):,.0f}"
        rows.append(row)
    rdf = pd.DataFrame(rows)
    fmt = {"Combined %": "{:+.2f}"} | {f"{s} %": "{:+.2f}" for s in all_sleeves}
    st.dataframe(rdf.style.format(fmt, na_rep="—"),
                 use_container_width=True)

    # ---- Live tail if a run is mid-flight ----
    log = _latest_sleeves_log()
    if log and log.exists():
        st.markdown("#### Latest log tail")
        try:
            text = log.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            st.error(f"Could not read log: {e}")
            return
        lines = text.splitlines()
        st.caption(f"`{log.name}`  ({len(lines):,} lines)")
        last_n = st.slider("Lines to show", 20, 500, 60, key="sleeves_tail_lines")
        st.code("\n".join(lines[-last_n:]) or "(log empty)", language="log")


# -----------------------------------------------------------------------------
# Paper-trading live view

@st.cache_data(ttl=10, show_spinner=False)
def _load_paper_state(strategy_name: str = "mom_v2_paper") -> dict | None:
    """Read paper_portfolio + paper_positions + paper_nav for one strategy.
    Returns None if no portfolio row exists (experiment not yet started)."""
    import sqlite3
    from trading_bot.config import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        pf_row = conn.execute(
            "SELECT * FROM paper_portfolio WHERE strategy_name=?",
            (strategy_name,)).fetchone()
    except sqlite3.OperationalError:
        # Table doesn't exist yet — schema migration hasn't run
        conn.close()
        return None
    if pf_row is None:
        conn.close()
        return None
    open_rows = conn.execute(
        "SELECT * FROM paper_positions WHERE strategy_name=? AND status='open' "
        "ORDER BY entry_date DESC, ticker",
        (strategy_name,)).fetchall()
    closed_rows = conn.execute(
        "SELECT * FROM paper_positions WHERE strategy_name=? AND status='closed' "
        "ORDER BY exit_date DESC, id DESC LIMIT 50",
        (strategy_name,)).fetchall()
    nav_rows = conn.execute(
        "SELECT nav_date, cash, positions_value, total_nav, n_open_positions "
        "FROM paper_nav WHERE strategy_name=? ORDER BY nav_date",
        (strategy_name,)).fetchall()
    # Latest cached close + date per ticker (for MTM + staleness flag).
    # Uses a correlated subquery so price + date come from the same row
    # (audit M1: avoids non-standard SQLite GROUP BY semantics).
    open_tickers = tuple({r["ticker"] for r in open_rows})
    last_closes: dict[str, float] = {}
    last_close_dates: dict[str, str] = {}
    if open_tickers:
        placeholders = ",".join("?" * len(open_tickers))
        for t, d, p in conn.execute(
            f"SELECT pc.ticker, pc.key_date, pc.price FROM price_cache pc "
            f"WHERE pc.kind='close' AND pc.ticker IN ({placeholders}) "
            f"AND pc.key_date = (SELECT MAX(key_date) FROM price_cache "
            f"  WHERE ticker=pc.ticker AND kind='close')",
            open_tickers,
        ).fetchall():
            last_closes[t] = p
            last_close_dates[t] = d
    conn.close()
    return {
        "portfolio": dict(pf_row),
        "open_positions": [dict(r) for r in open_rows],
        "closed_positions": [dict(r) for r in closed_rows],
        "nav_history": [dict(r) for r in nav_rows],
        "last_closes": last_closes,
        "last_close_dates": last_close_dates,
    }


# ---- Overview view helpers -------------------------------------------------

_SLEEVE_SHORT = {
    "mom_v1_paper": "mom_v1", "mom_v2_paper": "mom_v2",
    "mom_roa_6535_paper": "mom_roa", "residual_roa_6535_paper": "residual",
    "mom_v1_0701_paper": "mom_v1 (07-01)", "mom_v2_0701_paper": "mom_v2 (07-01)",
    "mom_roa_6535_0701_paper": "mom_roa (07-01)",
    "residual_roa_6535_0701_paper": "residual (07-01)",
    "sector_top4_paper": "sector4 (07-01)",
    "sector_top4_full_paper": "sector4 (full)",
    "mom_roa_top1_paper": "top1 (ctl)",
    "llm_overlay_mom_roa_top1_paper": "llm_top1",
    "llm_overlay_sector_top4_paper": "llm_sector",
    "llm_cascade_top1_paper": "casc_top1",
    "llm_cascade_sector4_paper": "casc_sec4",
    "spy_benchmark_paper": "S&P 500 (control)",
    "spy_benchmark_0701_paper": "S&P 500 (07-01)",
}


def _short(name: str) -> str:
    return _SLEEVE_SHORT.get(name, name[:-6] if name.endswith("_paper") else name)


def _rg(v):
    """Red/green text style for a signed-pct cell. Module-level so both the
    cohort panels and the movers table share it."""
    if v is None or (isinstance(v, float) and v != v):
        return ""
    return f"color: {'#22c55e' if v > 0 else '#ef4444' if v < 0 else '#94a3b8'}"


def _sleeve_inception(s: dict):
    """Earliest entry_date across positions, else initialized_at (tz-naive)."""
    eds = [p["entry_date"] for p in (s["open_positions"] + s["closed_positions"])
           if p.get("entry_date")]
    inc = pd.to_datetime(min(eds)) if eds else pd.to_datetime(s["initialized_at"])
    if inc is not None and inc.tzinfo is not None:
        inc = inc.tz_localize(None)
    return inc


@st.cache_data(ttl=300, show_spinner=False)
def _spy_cache_closes() -> list[tuple[str, float]]:
    """SPY daily closes from price_cache (sorted by date). Cache-based — same
    pricing basis as the sleeves themselves, no network."""
    import sqlite3 as _sq
    from trading_bot.config import DB_PATH as _DB
    conn = _sq.connect(_DB)
    rows = conn.execute(
        "SELECT key_date, price FROM price_cache WHERE ticker='SPY' "
        "AND kind='close' ORDER BY key_date").fetchall()
    conn.close()
    return [(d, p) for d, p in rows if p is not None and p > 0]


def _spy_ret_between(start_iso: str, spy: list[tuple[str, float]]) -> float | None:
    """SPY % return from first close at-or-after start_iso through last close."""
    import bisect
    dates = [d for d, _ in spy]
    i = bisect.bisect_left(dates, start_iso)
    if i >= len(spy) or spy[i][1] <= 0:
        return None
    return (spy[-1][1] / spy[i][1] - 1.0) * 100.0


def _render_cohort_panel(panel_sleeves: list[dict], key: str) -> None:
    """Dense table + compact %-from-inception NAV chart for one cohort of
    sleeves. Factored out of _render_overview so the Original (05-01) and 7/1
    cohorts each get their own table + chart (also keeps each hover box small)."""
    if not panel_sleeves:
        st.info("No sleeves in this cohort yet.")
        return

    rows = [{
        "Sleeve": _short(s["name"]),
        "NAV": s["cur_nav"],
        "Day %": s["day_pct"],
        "Total %": s["pct"],
        "α vs SPY": s["alpha"],
        "Max DD %": s["max_dd"],
        "Cash": s["cash"],
        "Pos": s["n_open"],
        "Rebal'd": s["last_rebal"],
    } for s in panel_sleeves]
    df = pd.DataFrame(rows).sort_values("Total %", ascending=False)

    def _style(row):
        if str(row["Sleeve"]).startswith("S&P 500"):
            return ["background-color: rgba(148,163,184,0.25)"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df.style.apply(_style, axis=1)
          .map(_rg, subset=["Day %", "Total %", "α vs SPY"])
          .format({"NAV": "${:,.0f}", "Day %": "{:+.2f}%", "Total %": "{:+.2f}%",
                   "α vs SPY": "{:+.2f}%", "Max DD %": "{:+.1f}%",
                   "Cash": "${:,.0f}"}, na_rep="—"),
        use_container_width=True, hide_index=True,
        height=38 * (len(df) + 1),
    )

    # Compact NAV chart (% from inception). Build traces first, add in descending
    # latest-value order so the x-unified hover box reads highest -> lowest.
    fig = go.Figure()
    _traces = []  # (latest_ret, trace)
    for s in panel_sleeves:
        if not s["nav_hist"]:
            continue
        ndf = pd.DataFrame(s["nav_hist"])
        ndf["nav_date"] = pd.to_datetime(ndf["nav_date"])
        if s["inception"] is not None and s["inception"] < ndf["nav_date"].min():
            ndf = pd.concat([pd.DataFrame([{"nav_date": s["inception"],
                                            "total_nav": s["starting"]}]),
                             ndf], ignore_index=True)
        ndf["ret_pct"] = ((ndf["total_nav"] / s["starting"] - 1.0) * 100).round(3)
        is_spy = s["name"].startswith("spy_benchmark")
        label = _short(s["name"])
        _traces.append((ndf["ret_pct"].iloc[-1], go.Scatter(
            x=ndf["nav_date"], y=ndf["ret_pct"], name=label, mode="lines+markers",
            line=(dict(color="#94a3b8", width=2, dash="dot") if is_spy else None),
            hovertemplate=(label + "<br>%{x|%Y-%m-%d}: %{y:+.3f}%<extra></extra>"))))
    if not _traces:
        st.caption("No NAV history yet — this cohort deploys on its 07-01 rebalance.")
        return
    for _, tr in sorted(_traces, key=lambda t: t[0], reverse=True):
        fig.add_trace(tr)
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(height=430, margin=dict(l=40, r=20, t=10, b=25),
                      xaxis_title=None, yaxis_title="% from inception",
                      yaxis_ticksuffix="%", yaxis_hoverformat="+.3f",
                      hovermode="x unified",
                      hoverlabel=dict(font_size=11, namelength=-1),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                  xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True, key=f"navchart_{key}")


def _render_overview(all_names: list[str]) -> None:
    """Default landing view: every sleeve's vitals on one dense screen."""
    from datetime import date as _date
    today_iso = _date.today().isoformat()
    spy = _spy_cache_closes()

    # ---- Load all sleeves (incl. the hidden LLM control — it's a real $100k) ----
    sleeves = []
    for name in all_names:
        state = _load_paper_state(name)
        if not state:
            continue
        pf = state["portfolio"]
        lc = state["last_closes"]
        cur_pos_val = sum(p["qty"] * (lc.get(p["ticker"]) or p["entry_price"])
                          for p in state["open_positions"])
        cur_nav = pf["cash"] + cur_pos_val
        nav_hist = state["nav_history"]
        # Day % = live NAV vs the last NAV row strictly before today.
        base_row = None
        if nav_hist:
            base_row = (nav_hist[-2] if (nav_hist[-1]["nav_date"] == today_iso
                                         and len(nav_hist) >= 2) else nav_hist[-1])
        day_pct = ((cur_nav / base_row["total_nav"] - 1.0) * 100.0
                   if base_row and base_row["total_nav"] > 0 else 0.0)
        # Live max drawdown over recorded history + current point.
        peak, mdd = pf["starting_cash"], 0.0
        for v in [r["total_nav"] for r in nav_hist] + [cur_nav]:
            peak = max(peak, v)
            if peak > 0:
                mdd = min(mdd, (v / peak - 1.0) * 100.0)
        s = {
            "name": pf["strategy_name"], "starting": pf["starting_cash"],
            "cash": pf["cash"], "cur_nav": cur_nav,
            "pct": (cur_nav / pf["starting_cash"] - 1.0) * 100,
            "day_pct": day_pct, "max_dd": mdd,
            "n_open": len(state["open_positions"]),
            "nav_hist": nav_hist,
            "open_positions": state["open_positions"],
            "closed_positions": state["closed_positions"],
            "initialized_at": pf.get("initialized_at"),
            "last_rebal": (pf.get("last_rebalanced_at") or "—")[:10],
            "last_close_dates": state["last_close_dates"],
        }
        s["inception"] = _sleeve_inception(s)
        s["alpha"] = None
        if s["inception"] is not None:
            spy_ret = _spy_ret_between(s["inception"].date().isoformat(), spy)
            if spy_ret is not None:
                s["alpha"] = s["pct"] - spy_ret
        sleeves.append(s)
    if not sleeves:
        st.warning("No sleeve data.")
        return

    # ---- Status strip ----
    spy_day = ((spy[-1][1] / spy[-2][1] - 1.0) * 100.0
               if len(spy) >= 2 and spy[-2][1] > 0 else None)
    earliest = min((s["inception"] for s in sleeves if s["inception"] is not None),
                   default=None)
    spy_since = (_spy_ret_between(earliest.date().isoformat(), spy)
                 if earliest is not None else None)
    n_stale = sum(1 for s in sleeves for d in s["last_close_dates"].values()
                  if (_date.today() - _date.fromisoformat(d)).days > 3)
    # Next monthly rebalance = 1st weekday of next month (manual via rebalance.bat).
    nm = (_date.today().replace(day=1) + timedelta(days=32)).replace(day=1)
    while nm.weekday() >= 5:
        nm += timedelta(days=1)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Prices through", spy[-1][0] if spy else "—",
              delta=(f"{n_stale} stale holdings" if n_stale else "all fresh"),
              delta_color=("inverse" if n_stale else "normal"))
    c2.metric("S&P 500 today", f"{spy_day:+.2f}%" if spy_day is not None else "—")
    c3.metric("S&P 500 since inception",
              f"{spy_since:+.2f}%" if spy_since is not None else "—")
    c4.metric("Next rebalance (manual)", nm.strftime("%b %d"))

    # ---- Two cohort panels: Original (since 05-01) vs the 7/1 cohort ----
    # Split by inception: the 07-01 reset/duplicate sleeves all carry inception
    # 2026-07-01; everything older is an original sleeve. The S&P control sits in
    # whichever cohort matches its inception (spy_benchmark=05-01, _0701=07-01).
    CUTOVER = _date(2026, 7, 1)

    def _is_0701(s) -> bool:
        inc = s["inception"]
        return inc is not None and inc.date() >= CUTOVER

    original = [s for s in sleeves if not _is_0701(s)]
    cohort_0701 = [s for s in sleeves if _is_0701(s)]

    st.markdown("#### Original sleeves · since 2026-05-01")
    _render_cohort_panel(original, key="original")
    st.markdown("#### 7/1 cohort · fresh $100k, inception 2026-07-01")
    _render_cohort_panel(cohort_0701, key="cohort0701")
    st.caption("Legend click = hide/show · double-click = isolate. Full-size "
               "charts + absolute $ in the **NAV charts** view.")

    # ---- Bottom row: movers | experiments | concentration ----
    col_mv, col_ex = st.columns([3, 2])

    with col_mv:
        st.markdown("##### Top movers today (held names)")
        held: dict[str, list[str]] = {}
        for s in sleeves:
            if s["name"].startswith("spy_benchmark"):
                continue    # SPY is the benchmark, not a stock pick
            for p in s["open_positions"]:
                held.setdefault(p["ticker"], []).append(_short(s["name"]))
        movers = []
        if held:
            import sqlite3 as _sq
            from trading_bot.config import DB_PATH as _DB
            conn = _sq.connect(_DB)
            ph = ",".join("?" * len(held))
            by_t: dict[str, list[tuple[str, float]]] = {}
            for t, d, p in conn.execute(
                f"SELECT ticker, key_date, price FROM price_cache "
                f"WHERE kind='close' AND ticker IN ({ph}) "
                f"AND key_date >= date('now','-9 day') ORDER BY key_date",
                    tuple(held)).fetchall():
                if p and p > 0:
                    by_t.setdefault(t, []).append((d, p))
            conn.close()
            for t, rows_t in by_t.items():
                if len(rows_t) >= 2 and rows_t[-2][1] > 0:
                    movers.append((t, (rows_t[-1][1] / rows_t[-2][1] - 1.0) * 100,
                                   rows_t[-1][1]))
        if movers:
            movers.sort(key=lambda r: r[1])
            sel = movers[-5:][::-1] + movers[:5]
            mdf = pd.DataFrame([{
                "Ticker": t, "Day %": pct, "Last $": px,
                "Held by": ", ".join(sorted(set(held[t]))),
            } for t, pct, px in sel])
            st.dataframe(
                mdf.style.map(_rg, subset=["Day %"])
                   .format({"Day %": "{:+.2f}%", "Last $": "${:,.2f}"}),
                use_container_width=True, hide_index=True,
                height=38 * (len(mdf) + 1))
        else:
            st.caption("No price data for held names.")

    with col_ex:
        st.markdown("##### LLM experiments")
        import sqlite3 as _sq
        from trading_bot.config import DB_PATH as _DB
        conn = _sq.connect(_DB)
        ld = conn.execute(
            "SELECT decision_date, ticker, verdict, score, invalidation_level "
            "FROM llm_overlay_log ORDER BY decision_date DESC LIMIT 1").fetchone()
        if ld:
            d, t, v, sc, inv = ld
            px_row = conn.execute(
                "SELECT price FROM price_cache WHERE ticker=? AND kind='close' "
                "ORDER BY key_date DESC LIMIT 1", (t,)).fetchone()
            px = px_row[0] if px_row else None
            stop_txt = (f"stop ${inv:,.0f} ({(px / inv - 1) * 100:+.1f}% away)"
                        if (px and inv) else f"stop ${inv:,.0f}" if inv else "")
            st.markdown(f"**Stock veto** — {d}: **{v} {t}** (score {sc}/10), "
                        f"last ${px:,.2f} · {stop_txt}" if px else
                        f"**Stock veto** — {d}: **{v} {t}** (score {sc}/10)")
            by = {s["name"]: s for s in sleeves}
            ctl = by.get("mom_roa_top1_paper")
            trt = by.get("llm_overlay_mom_roa_top1_paper")
            if ctl and trt:
                gap = trt["pct"] - ctl["pct"]
                st.caption(f"treatment {trt['pct']:+.2f}% vs control "
                           f"{ctl['pct']:+.2f}% → LLM effect **{gap:+.2f}pp**")
        n_sec = conn.execute("SELECT COUNT(*) FROM sector_overlay_log").fetchone()[0]
        sec_trt = next((s for s in sleeves
                        if s["name"] == "llm_overlay_sector_top4_paper"), None)
        if sec_trt is not None:
            status = ("UNSEEDED — 100% cash, awaiting first 4-sector decision "
                      "round" if (sec_trt["n_open"] == 0 and n_sec == 0)
                      else f"{n_sec} decisions logged, {sec_trt['n_open']} held")
            st.markdown(f"**Sector veto** — {status}")
        conn.close()

        st.markdown("##### Concentration (top sector)")
        for s in sleeves:
            if (s["name"].startswith(("sector_top4", "spy_benchmark"))
                    or s["name"] in ("llm_overlay_sector_top4_paper",
                                     "mom_roa_top1_paper",
                                     "llm_overlay_mom_roa_top1_paper")):
                continue
            tot, by_sec = 0.0, {}
            for p in s["open_positions"]:
                mv = p["qty"] * p["entry_price"]
                tot += mv
                by_sec[p.get("sector") or "?"] = by_sec.get(p.get("sector") or "?", 0) + mv
            if tot <= 0:
                continue
            sec, w = max(by_sec.items(), key=lambda kv: kv[1])
            w_pct = w / tot * 100
            warn = " ⚠️" if w_pct > 35 else ""
            st.caption(f"{_short(s['name'])}: {sec} {w_pct:.0f}%{warn}")


def _render_overlay_all(available: list[str]) -> None:
    """Overlay NAV curves for all paper-trade sleeves on one chart with
    sortable headline metrics. Reads stored paper_nav (so it inherits
    whatever cadence MTM has been run at)."""
    # Load each sleeve's portfolio + NAV history
    sleeves: list[dict] = []
    for s in available:
        state = _load_paper_state(s)
        if not state:
            continue
        pf = state["portfolio"]
        last_closes = state["last_closes"]
        # Recompute live MTM (don't trust last paper_nav row alone)
        cur_pos_val = sum(
            p["qty"] * (last_closes.get(p["ticker"]) or p["entry_price"])
            for p in state["open_positions"]
        )
        cur_nav = pf["cash"] + cur_pos_val
        sleeves.append({
            "name": pf["strategy_name"],
            "starting": pf["starting_cash"],
            "cash": pf["cash"],
            "cur_nav": cur_nav,
            "pct": (cur_nav / pf["starting_cash"] - 1.0) * 100,
            "n_open": len(state["open_positions"]),
            "nav_hist": state["nav_history"],
            "initialized_at": pf.get("initialized_at"),
            "open_positions": state["open_positions"],
            "closed_positions": state["closed_positions"],
        })

    if not sleeves:
        st.warning("No sleeve data to overlay.")
        return

    # ---- Headlines: one row per sleeve ----
    st.markdown("#### Sleeve headlines (current MTM)")
    rows = [{
        "Sleeve": s["name"],
        "Start $": s["starting"],
        "Current NAV": s["cur_nav"],
        "Return %": s["pct"],
        "Cash": s["cash"],
        "Open": s["n_open"],
    } for s in sleeves]
    # S&P 500 control row, over the earliest sleeve inception → today.
    _incs = []
    for s in sleeves:
        eds = [p["entry_date"] for p in (s["open_positions"] + s["closed_positions"])
               if p.get("entry_date")]
        inc = pd.to_datetime(min(eds)) if eds else pd.to_datetime(s["initialized_at"])
        if inc is not None and inc.tzinfo is not None:
            inc = inc.tz_localize(None)
        if inc is not None:
            _incs.append(inc)
    spy_ctrl_pct = spy_return_pct(min(_incs)) if _incs else None
    if spy_ctrl_pct is not None:
        base_start = sleeves[0]["starting"]
        rows.append({
            "Sleeve": "S&P 500 (control)",
            "Start $": base_start,
            "Current NAV": base_start * (1.0 + spy_ctrl_pct / 100.0),
            "Return %": spy_ctrl_pct,
            "Cash": 0.0,
            "Open": 0,
        })
    head_df = pd.DataFrame(rows).sort_values("Return %", ascending=False)

    def _hl_control(row):
        if str(row["Sleeve"]).startswith("S&P 500"):
            return ["background-color: rgba(148,163,184,0.25)"] * len(row)
        return [""] * len(row)

    st.dataframe(
        head_df.style.apply(_hl_control, axis=1).format({
            "Start $": "${:,.0f}", "Current NAV": "${:,.2f}",
            "Return %": "{:+.2f}%", "Cash": "${:,.2f}",
        }),
        use_container_width=True, hide_index=True,
    )
    st.caption("The shaded **S&P 500 (control)** row is the benchmark, "
               "not a tradeable sleeve — it shows where the market sits "
               "in the ranking over the same period.")

    # ---- Overlay NAV chart (% return from inception) ----
    st.markdown("#### NAV overlay (% return from inception)")
    st.caption("Tip: click a name in the legend to hide/show it; "
               "double-click to isolate one line.")
    # Collect traces, then add them in descending latest-value order so the
    # x-unified hover box reads highest -> lowest (Plotly orders unified-hover
    # entries by trace index). The S&P 500 control ranks in-line with the rest.
    fig = go.Figure()
    _traces = []  # (latest_ret, trace)
    for s in sleeves:
        if not s["nav_hist"]:
            continue
        nav_df = pd.DataFrame(s["nav_hist"])
        nav_df["nav_date"] = pd.to_datetime(nav_df["nav_date"])
        # Prepend inception point at 0%
        entry_dates = [p["entry_date"] for p in (s["open_positions"] + s["closed_positions"])
                       if p.get("entry_date")]
        if entry_dates:
            inception = pd.to_datetime(min(entry_dates))
        else:
            inception = pd.to_datetime(s["initialized_at"])
        # paper_nav dates are tz-naive but initialized_at is tz-aware ISO;
        # strip tz so the comparison/concat don't raise (sleeves in cash have
        # no entry_date to fall back on).
        if inception is not None and inception.tzinfo is not None:
            inception = inception.tz_localize(None)
        if inception is not None and inception < nav_df["nav_date"].min():
            seed = pd.DataFrame([{"nav_date": inception, "total_nav": s["starting"]}])
            nav_df = pd.concat([seed, nav_df], ignore_index=True)
        nav_df["ret_pct"] = ((nav_df["total_nav"] / s["starting"] - 1.0) * 100).round(3)
        _traces.append((nav_df["ret_pct"].iloc[-1], go.Scatter(
            x=nav_df["nav_date"], y=nav_df["ret_pct"],
            name=s["name"], mode="lines+markers",
            hovertemplate=(s["name"] + "<br>%{x|%Y-%m-%d}: %{y:+.3f}%<extra></extra>"),
        )))
    # S&P 500 (SPY) benchmark, normalized to % return from the earliest sleeve inception.
    _inceptions = []
    for s in sleeves:
        eds = [p["entry_date"] for p in (s["open_positions"] + s["closed_positions"])
               if p.get("entry_date")]
        inc = pd.to_datetime(min(eds)) if eds else pd.to_datetime(s["initialized_at"])
        if inc is not None and inc.tzinfo is not None:
            inc = inc.tz_localize(None)
        if inc is not None:
            _inceptions.append(inc)
    if _inceptions:
        g_start = min(_inceptions)
        spy = fetch_spy_series(g_start.date().isoformat(), date.today().isoformat())
        spy = spy[spy["nav_date"] >= g_start]
        if not spy.empty:
            base = spy["close"].iloc[0]
            spy["ret_pct"] = ((spy["close"] / base - 1.0) * 100).round(3)
            _traces.append((spy["ret_pct"].iloc[-1], go.Scatter(
                x=spy["nav_date"], y=spy["ret_pct"],
                name="S&P 500 (SPY)", mode="lines",
                line=dict(color="#94a3b8", width=2, dash="dot"),
                hovertemplate="S&P 500<br>%{x|%Y-%m-%d}: %{y:+.3f}%<extra></extra>",
            )))
    for _, tr in sorted(_traces, key=lambda t: t[0], reverse=True):
        fig.add_trace(tr)
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        height=460, margin=dict(l=40, r=20, t=20, b=30),
        xaxis_title=None, yaxis_title="Return from inception (%)",
        yaxis_ticksuffix="%", yaxis_hoverformat="+.3f",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---- Overlay NAV chart (absolute $) ----
    st.markdown("#### NAV overlay (absolute $)")
    fig2 = go.Figure()
    _traces2 = []  # (latest_nav, trace)
    for s in sleeves:
        if not s["nav_hist"]:
            continue
        nav_df = pd.DataFrame(s["nav_hist"])
        nav_df["nav_date"] = pd.to_datetime(nav_df["nav_date"])
        entry_dates = [p["entry_date"] for p in (s["open_positions"] + s["closed_positions"])
                       if p.get("entry_date")]
        if entry_dates:
            inception = pd.to_datetime(min(entry_dates))
        else:
            inception = pd.to_datetime(s["initialized_at"])
        # paper_nav dates are tz-naive but initialized_at is tz-aware ISO;
        # strip tz so the comparison/concat don't raise (sleeves in cash have
        # no entry_date to fall back on).
        if inception is not None and inception.tzinfo is not None:
            inception = inception.tz_localize(None)
        if inception is not None and inception < nav_df["nav_date"].min():
            seed = pd.DataFrame([{"nav_date": inception, "total_nav": s["starting"]}])
            nav_df = pd.concat([seed, nav_df], ignore_index=True)
        _traces2.append((nav_df["total_nav"].iloc[-1], go.Scatter(
            x=nav_df["nav_date"], y=nav_df["total_nav"],
            name=s["name"], mode="lines+markers",
            hovertemplate=(s["name"] + "<br>%{x|%Y-%m-%d}: $%{y:,.0f}<extra></extra>"),
        )))
    # S&P 500 (SPY) benchmark scaled to the first sleeve's starting cash.
    if sleeves and _inceptions:
        g_start = min(_inceptions)
        spy = fetch_spy_series(g_start.date().isoformat(), date.today().isoformat())
        spy = spy[spy["nav_date"] >= g_start]
        if not spy.empty:
            base = spy["close"].iloc[0]
            spy["nav_equiv"] = sleeves[0]["starting"] * spy["close"] / base
            _traces2.append((spy["nav_equiv"].iloc[-1], go.Scatter(
                x=spy["nav_date"], y=spy["nav_equiv"],
                name="S&P 500 (SPY)", mode="lines",
                line=dict(color="#94a3b8", width=2, dash="dot"),
                hovertemplate="S&P 500<br>%{x|%Y-%m-%d}: $%{y:,.0f}<extra></extra>",
            )))
    for _, tr in sorted(_traces2, key=lambda t: t[0], reverse=True):
        fig2.add_trace(tr)
    if sleeves:
        fig2.add_hline(y=sleeves[0]["starting"], line_dash="dash",
                       line_color="gray",
                       annotation_text=f"Start ${sleeves[0]['starting']:,.0f}")
    fig2.update_layout(
        height=380, margin=dict(l=40, r=20, t=20, b=30),
        xaxis_title=None, yaxis_title="Total NAV ($)",
        yaxis_tickformat="$,.0f",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
        hovermode="x unified",
    )
    st.plotly_chart(fig2, use_container_width=True)


def _render_llm_overlay_panel(strategy_name: str) -> None:
    """Decision log + control-vs-treatment comparison for the LLM experiment."""
    from trading_bot.strategies import llm_overlay
    st.info(
        "**LLM-overlay experiment.** `mom_roa_top1_paper` (control) always "
        "buys the #1 mom_roa name. `llm_overlay_mom_roa_top1_paper` (treatment) buys the "
        "same name only on a logged **BUY**, else holds cash, and exits if the "
        "**invalidation** price is breached. Kill switch: 12 mo / ≥30 picks — "
        "drop it if scores don't predict forward returns OR it doesn't beat "
        "the control net of costs."
    )

    decisions = llm_overlay.all_decisions()
    if decisions:
        st.markdown("##### Pre-committed decision log")
        ddf = pd.DataFrame(decisions)[
            ["decision_date", "ticker", "verdict", "score",
             "invalidation_level", "rationale"]
        ].rename(columns={
            "decision_date": "Date", "ticker": "Ticker", "verdict": "Verdict",
            "score": "Score", "invalidation_level": "Invalidation", "rationale": "Rationale",
        })
        st.dataframe(
            ddf.style.format({"Score": "{:.0f}", "Invalidation": "${:.2f}"},
                             na_rep="—"),
            use_container_width=True, hide_index=True,
        )
    else:
        st.caption(
            "No decisions logged yet. Run "
            "`python -m scripts.momentum.llm_overlay_ops candidate` then "
            "`... decide ...`."
        )

    # Quick control-vs-treatment NAV comparison
    import sqlite3 as _sq
    conn = _sq.connect(DB_PATH)
    conn.row_factory = _sq.Row
    rows = conn.execute(
        "SELECT strategy_name, starting_cash, cash FROM paper_portfolio "
        "WHERE strategy_name IN ('mom_roa_top1_paper', 'llm_overlay_mom_roa_top1_paper')"
    ).fetchall()
    pf_by = {r["strategy_name"]: r for r in rows}
    conn.close()
    if len(pf_by) == 2:
        _PAIR = {
            "mom_roa_top1_paper": "Control — mom_roa_top1 (no veto)",
            "llm_overlay_mom_roa_top1_paper":  "Treatment — llm_overlay (BUY/VETO + stop)",
        }
        cols = st.columns(2)
        for i, name in enumerate(("mom_roa_top1_paper", "llm_overlay_mom_roa_top1_paper")):
            state = _load_paper_state(name)
            if not state:
                continue
            pf = state["portfolio"]
            lc = state["last_closes"]
            nav = pf["cash"] + sum(
                p["qty"] * (lc.get(p["ticker"]) or p["entry_price"])
                for p in state["open_positions"])
            pct = (nav / pf["starting_cash"] - 1.0) * 100
            short = "Control (no veto)" if name == "mom_roa_top1_paper" else "Treatment (LLM)"
            cols[i].metric(short, fmt_dollars(nav), delta=f"{pct:+.2f}%")

        # Paired NAV overlay: control vs treatment on one chart (% from start).
        st.markdown("##### Control vs treatment — NAV (% from inception)")
        fig = go.Figure()
        _pair_traces = []  # (latest_ret, trace) — added high->low for hover order
        for name in ("mom_roa_top1_paper", "llm_overlay_mom_roa_top1_paper"):
            state = _load_paper_state(name)
            if not state or not state["nav_history"]:
                continue
            pf = state["portfolio"]
            start = pf["starting_cash"]
            ndf = pd.DataFrame(state["nav_history"])
            ndf["nav_date"] = pd.to_datetime(ndf["nav_date"])
            # Seed an inception point at 0% so a single MTM row still draws.
            entry_dates = [p["entry_date"] for p in
                           (state["open_positions"] + state["closed_positions"])
                           if p.get("entry_date")]
            inception = (pd.to_datetime(min(entry_dates)) if entry_dates
                         else pd.to_datetime(pf.get("initialized_at")))
            if inception is not None and inception.tzinfo is not None:
                inception = inception.tz_localize(None)
            if inception is not None and inception < ndf["nav_date"].min():
                ndf = pd.concat(
                    [pd.DataFrame([{"nav_date": inception, "total_nav": start}]),
                     ndf], ignore_index=True)
            ndf["ret_pct"] = ((ndf["total_nav"] / start - 1.0) * 100).round(3)
            _pair_traces.append((ndf["ret_pct"].iloc[-1], go.Scatter(
                x=ndf["nav_date"], y=ndf["ret_pct"], name=_PAIR[name],
                mode="lines+markers",
                line=dict(dash="dot") if name == "mom_roa_top1_paper" else None,
                hovertemplate=(_PAIR[name] +
                               "<br>%{x|%Y-%m-%d}: %{y:+.3f}%<extra></extra>"),
            )))
        for _, tr in sorted(_pair_traces, key=lambda t: t[0], reverse=True):
            fig.add_trace(tr)
        any_curve = bool(_pair_traces)
        if any_curve:
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.update_layout(
                height=360, margin=dict(l=40, r=20, t=20, b=30),
                xaxis_title=None, yaxis_title="Return from inception (%)",
                yaxis_ticksuffix="%", yaxis_hoverformat="+.3f",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Gap between the two lines = the LLM overlay's net effect "
                       "(same candidate, costs, dates; only the veto/stop differ).")
        else:
            st.caption("No NAV history yet for the experiment sleeves.")

    # Control's positions — the control sleeve is hidden from the main
    # selector, so this is the only place to see what it actually holds
    # (the treatment's positions render in the main view below this panel).
    ctrl = _load_paper_state("mom_roa_top1_paper")
    if ctrl:
        st.markdown("##### Control (mom_roa_top1) — positions")
        lc = ctrl["last_closes"]
        op = ctrl["open_positions"]
        if op:
            orows = [{
                "Ticker": p["ticker"],
                "Sector": p["sector"] or "?",
                "Qty": p["qty"],
                "Entry $": p["entry_price"],
                "Last $": lc.get(p["ticker"]) or p["entry_price"],
                "P&L %": ((lc.get(p["ticker"]) or p["entry_price"])
                          / p["entry_price"] - 1.0) * 100.0,
                "Entry date": p["entry_date"],
            } for p in op]
            st.caption(f"Open ({len(op)})")
            st.dataframe(
                pd.DataFrame(orows).style.format({
                    "Qty": "{:.2f}", "Entry $": "${:.2f}", "Last $": "${:.2f}",
                    "P&L %": "{:+.2f}%"}, na_rep="—"),
                use_container_width=True, hide_index=True)
        else:
            st.caption("Open: none (control is in cash).")
        cp = ctrl["closed_positions"]
        if cp:
            crows = [{
                "Ticker": p["ticker"],
                "Entry $": p["entry_price"],
                "Exit $": p["exit_price"],
                "Entry date": p["entry_date"],
                "Exit date": p["exit_date"],
                "Exit reason": p["exit_reason"],
                "Realized %": p["realized_pnl_pct"],
            } for p in cp]
            st.caption(f"Closed ({len(cp)})")
            st.dataframe(
                pd.DataFrame(crows).style.format({
                    "Entry $": "${:.2f}", "Exit $": "${:.2f}",
                    "Realized %": "{:+.2f}%"}, na_rep="—"),
                use_container_width=True, hide_index=True)


def _render_sector_overlay_panel() -> None:
    """Decision log + control-vs-treatment comparison for the SECTOR overlay."""
    from trading_bot.strategies import sector_overlay
    st.info(
        "**Sector-overlay experiment (macro).** `sector_top4_paper` (control) "
        "holds the top-4 SPDR sectors by momentum, no veto. "
        "`llm_overlay_sector_top4_paper` (treatment) holds the same 4 at ~25% "
        "each, except sectors a MACRO LLM read (rates / valuation / breadth) "
        "**VETOs** to cash, with a per-sector invalidation stop. Honest prior: "
        "a weaker test than the stock overlay — macro is where the LLM has the "
        "least edge. Kill switch: 12 mo / ≥30 sector-decisions."
    )

    decisions = sector_overlay.all_decisions()
    if decisions:
        st.markdown("##### Pre-committed sector decision log")
        ddf = pd.DataFrame(decisions)[
            ["decision_date", "ticker", "verdict", "score",
             "invalidation_level", "rationale"]
        ].rename(columns={
            "decision_date": "Date", "ticker": "Sector", "verdict": "Verdict",
            "score": "Score", "invalidation_level": "Invalidation",
            "rationale": "Rationale"})
        st.dataframe(
            ddf.style.format({"Score": "{:.0f}", "Invalidation": "${:.2f}"},
                             na_rep="—"),
            use_container_width=True, hide_index=True)
    else:
        st.caption(
            "No sector decisions logged yet. Run "
            "`python -m scripts.momentum.sector_overlay_ops candidate` then "
            "`... decide ...` for each of the 4 sectors.")

    _PAIR = {
        "sector_top4_paper": "Control — sector_top4 (no veto)",
        "llm_overlay_sector_top4_paper": "Treatment — sector_overlay (macro veto)",
    }
    cols = st.columns(2)
    for i, name in enumerate(("sector_top4_paper", "llm_overlay_sector_top4_paper")):
        state = _load_paper_state(name)
        if not state:
            continue
        pf = state["portfolio"]
        lc = state["last_closes"]
        nav = pf["cash"] + sum(
            p["qty"] * (lc.get(p["ticker"]) or p["entry_price"])
            for p in state["open_positions"])
        pct = (nav / pf["starting_cash"] - 1.0) * 100
        short = "Control (no veto)" if name == "sector_top4_paper" else "Treatment (macro)"
        cols[i].metric(short, fmt_dollars(nav), delta=f"{pct:+.2f}%")

    st.markdown("##### Control vs treatment — NAV (% from inception)")
    fig = go.Figure()
    _pair_traces = []  # (latest_ret, trace) — added high->low for hover order
    for name in ("sector_top4_paper", "llm_overlay_sector_top4_paper"):
        state = _load_paper_state(name)
        if not state or not state["nav_history"]:
            continue
        pf = state["portfolio"]
        start = pf["starting_cash"]
        ndf = pd.DataFrame(state["nav_history"])
        ndf["nav_date"] = pd.to_datetime(ndf["nav_date"])
        entry_dates = [p["entry_date"] for p in
                       (state["open_positions"] + state["closed_positions"])
                       if p.get("entry_date")]
        inception = (pd.to_datetime(min(entry_dates)) if entry_dates
                     else pd.to_datetime(pf.get("initialized_at")))
        if inception is not None and inception.tzinfo is not None:
            inception = inception.tz_localize(None)
        if inception is not None and inception < ndf["nav_date"].min():
            ndf = pd.concat(
                [pd.DataFrame([{"nav_date": inception, "total_nav": start}]),
                 ndf], ignore_index=True)
        ndf["ret_pct"] = ((ndf["total_nav"] / start - 1.0) * 100).round(3)
        _pair_traces.append((ndf["ret_pct"].iloc[-1], go.Scatter(
            x=ndf["nav_date"], y=ndf["ret_pct"], name=_PAIR[name],
            mode="lines+markers",
            line=dict(dash="dot") if name == "sector_top4_paper" else None,
            hovertemplate=(_PAIR[name] +
                           "<br>%{x|%Y-%m-%d}: %{y:+.3f}%<extra></extra>"))))
    for _, tr in sorted(_pair_traces, key=lambda t: t[0], reverse=True):
        fig.add_trace(tr)
    any_curve = bool(_pair_traces)
    if any_curve:
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(
            height=360, margin=dict(l=40, r=20, t=20, b=30),
            xaxis_title=None, yaxis_title="Return from inception (%)",
            yaxis_ticksuffix="%", yaxis_hoverformat="+.3f",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Gap = the macro overlay's net effect (same 4 candidates, "
                   "sizing, costs, dates; only the veto/stop differ).")
    else:
        st.caption("No NAV history yet for the sector-experiment sleeves.")


def render_paper_trading() -> None:
    """Live view of the ongoing paper-trade experiment.
    Reads the paper_* tables populated by paper_rebalance + paper_mtm.
    Supports multiple parallel strategies (mom_v1_paper, mom_v2_paper)."""
    st.markdown("### Live paper-trade experiment")
    st.caption(
        "Reads `paper_portfolio` / `paper_positions` / `paper_nav` from "
        "`var/trades.db`. Updated by `scripts/momentum/paper_rebalance.py` "
        "(monthly) and `paper_mtm.py` (daily)."
    )

    # Discover available strategies (any rows in paper_portfolio)
    import sqlite3 as _sq
    from trading_bot.config import DB_PATH as _DB
    conn = _sq.connect(_DB)
    conn.row_factory = _sq.Row
    available = [r["strategy_name"] for r in conn.execute(
        "SELECT strategy_name FROM paper_portfolio ORDER BY strategy_name").fetchall()]
    conn.close()

    # mom_roa_top1_paper is the LLM experiment's CONTROL. It keeps running in
    # the DB and is shown inside the llm_overlay panel's comparison chart, but
    # it's hidden as a standalone selectable sleeve (and from the all-sleeves
    # overlay) so it doesn't clutter the view — you read it against the
    # treatment, not on its own. The Overview table DOES include it (it's a
    # real $100k sleeve and the table is built for density).
    # spy_benchmark_paper is the S&P 500 control — a real $100k buy-and-hold SPY
    # sleeve (inception 2026-05-01). It's shown AS the benchmark (shaded control
    # row + dotted line), drawn separately in each view, so it's kept out of the
    # selectable-strategy / overlay lists to avoid double-counting. The Overview
    # DOES list it (available_all) as a real, shaded control row.
    SPY_SLEEVE = "spy_benchmark_paper"
    available_all = list(available)
    _HIDDEN_SLEEVES = {"mom_roa_top1_paper"}
    available = [s for s in available
                 if s not in _HIDDEN_SLEEVES and s != SPY_SLEEVE]

    if not available:
        st.info(
            "No paper-trade experiment running yet. Initialize via:\n\n"
            "```cmd\n"
            "D:\\ClaudeCode\\Trading\\scripts\\momentum\\rebalance.bat\n"
            "```\n\n"
            "Or see `docs/paper_trading_ops.md` for full procedure."
        )
        return

    # View toggle: single sleeve vs. all sleeves overlay. Persisted in
    # st.query_params so the choice survives both st.rerun() AND browser
    # refresh (otherwise the radio UI drifts out of sync with rendered
    # content). Explicit `key=` ensures stable widget identity across reruns.
    if len(available) > 1:
        _VIEW_OPTS = {"overview": "📊 Overview",
                      "single": "🔬 Single sleeve",
                      "overlay": "📈 NAV charts"}
        qp = st.query_params
        default_view = qp.get("paper_view", "overview")
        if default_view not in _VIEW_OPTS:
            default_view = "overview"
        view_key = st.radio(
            "View", list(_VIEW_OPTS.keys()),
            format_func=lambda k: _VIEW_OPTS[k],
            index=list(_VIEW_OPTS.keys()).index(default_view),
            horizontal=True, label_visibility="collapsed",
            key="paper_view_radio",
        )
        if qp.get("paper_view") != view_key:
            qp["paper_view"] = view_key
        if view_key == "overview":
            _render_overview(available_all)
            return
        if view_key == "overlay":
            _render_overlay_all(available)
            return
        # Per-sleeve selection also persists via query param so refresh
        # keeps you on the same strategy + chart.
        sleeve_qp = qp.get("sleeve", "mom_v2_paper")
        if sleeve_qp not in available:
            sleeve_qp = "mom_v2_paper" if "mom_v2_paper" in available else available[0]
        strategy_name = st.selectbox(
            "Strategy", available,
            index=available.index(sleeve_qp),
            help="Switch between parallel paper-trade sleeves",
            key="paper_sleeve_select",
        )
        if qp.get("sleeve") != strategy_name:
            qp["sleeve"] = strategy_name
    else:
        strategy_name = available[0]

    state = _load_paper_state(strategy_name)
    if state is None:
        st.warning(f"Strategy {strategy_name} has portfolio row but no data loaded.")
        return

    pf = state["portfolio"]
    open_pos = state["open_positions"]
    closed_pos = state["closed_positions"]
    nav_hist = state["nav_history"]
    last_closes = state["last_closes"]
    last_close_dates = state["last_close_dates"]
    # Audit fix (2026-05-30): warn loudly when prices are aged.
    from datetime import date as _date
    today = _date.today()
    ages = [(today - _date.fromisoformat(d)).days
            for d in last_close_dates.values()]
    if ages:
        n_old = sum(1 for a in ages if a > 3)
        if n_old > 0:
            median_age = sorted(ages)[len(ages) // 2]
            st.warning(
                f"Price staleness: {n_old} / {len(ages)} holdings have prices "
                f">3 days old (median age {median_age}d). "
                f"NAV may be inaccurate. Run "
                f"`python -m scripts.momentum.daily_price_refresh` to refresh."
            )

    # ---- Compute current MTM from latest cached closes (don't trust the
    # last paper_nav row alone; it may be stale if MTM hasn't run today) ----
    cur_positions_value = sum(
        p["qty"] * (last_closes.get(p["ticker"]) or p["entry_price"])
        for p in open_pos
    )
    cur_nav = pf["cash"] + cur_positions_value
    starting_cash = pf["starting_cash"]
    pct_vs_start = (cur_nav / starting_cash - 1.0) * 100.0

    # Inception (earliest entry, else initialized_at) — used by the S&P 500
    # control headline AND the NAV equity curve below.
    _entry_dates = [p["entry_date"] for p in (open_pos + closed_pos)
                    if p.get("entry_date")]
    inception = (pd.to_datetime(min(_entry_dates)) if _entry_dates
                 else pd.to_datetime(pf.get("initialized_at")))
    if inception is not None and inception.tzinfo is not None:
        inception = inception.tz_localize(None)
    spy_pct = spy_return_pct(inception)

    # ---- Headlines ----
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Current NAV", fmt_dollars(cur_nav),
              delta=f"{pct_vs_start:+.2f}% vs start")
    c2.metric("Open positions", f"{len(open_pos)}")
    c3.metric("Cash", fmt_dollars(pf["cash"]))
    last_rebal = pf.get("last_rebalanced_at") or "—"
    if isinstance(last_rebal, str) and "T" in last_rebal:
        last_rebal = last_rebal.split("T")[0]
    c4.metric("Last rebalance", last_rebal)
    # S&P 500 control: tinted background marks it as the benchmark, not a sleeve.
    if spy_pct is not None:
        spy_color = color_pct(spy_pct)
        alpha = pct_vs_start - spy_pct
        c5.markdown(
            f"""
            <div style="background: rgba(148,163,184,0.15); border-left: 4px solid #94a3b8; border-radius: 6px; padding: 6px 10px;">
              <div style="color:#94a3b8; font-size:0.78rem; text-transform:uppercase; letter-spacing:0.04em;">S&amp;P 500 · control</div>
              <div style="font-size:1.6rem; font-weight:700; color:{spy_color}; line-height:1.25;">{spy_pct:+.2f}%</div>
              <div style="color:#94a3b8; font-size:0.78rem;">same period · α {alpha:+.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        c5.metric("S&P 500 · control", "—")

    # ---- NAV equity curve ----
    if nav_hist:
        nav_df = pd.DataFrame(nav_hist)
        nav_df["nav_date"] = pd.to_datetime(nav_df["nav_date"])
        # Prepend an inception point at starting_cash so newly-deployed sleeves
        # with only 1 MTM row still render a line (px.line on 1 point shows
        # nothing). `inception` was computed above for the headlines.
        if inception is not None and inception < nav_df["nav_date"].min():
            seed = pd.DataFrame([{"nav_date": inception, "cash": starting_cash,
                                  "positions_value": 0.0,
                                  "total_nav": starting_cash,
                                  "n_open_positions": 0}])
            nav_df = pd.concat([seed, nav_df], ignore_index=True)
        fig = go.Figure()
        # Add traces in descending latest-$ order so the x-unified hover box
        # reads highest -> lowest (sleeve vs S&P 500 control).
        _traces = [(nav_df["total_nav"].iloc[-1], go.Scatter(
            x=nav_df["nav_date"], y=nav_df["total_nav"],
            name=pf["strategy_name"], mode="lines+markers",
            hovertemplate=(pf["strategy_name"] + "<br>%{x|%Y-%m-%d}: $%{y:,.0f}<extra></extra>"),
        ))]
        # S&P 500 (SPY) benchmark scaled to this sleeve's starting cash.
        if inception is not None:
            spy = fetch_spy_series(inception.date().isoformat(), date.today().isoformat())
            spy = spy[spy["nav_date"] >= inception]
            if not spy.empty:
                base = spy["close"].iloc[0]
                spy["nav_equiv"] = starting_cash * spy["close"] / base
                _traces.append((spy["nav_equiv"].iloc[-1], go.Scatter(
                    x=spy["nav_date"], y=spy["nav_equiv"],
                    name="S&P 500 (SPY)", mode="lines",
                    line=dict(color="#94a3b8", width=2, dash="dot"),
                    hovertemplate="S&P 500<br>%{x|%Y-%m-%d}: $%{y:,.0f}<extra></extra>",
                )))
        for _, tr in sorted(_traces, key=lambda t: t[0], reverse=True):
            fig.add_trace(tr)
        fig.add_hline(y=starting_cash, line_dash="dash", line_color="gray",
                      annotation_text=f"Start ${starting_cash:,.0f}")
        fig.update_layout(height=380, margin=dict(l=40, r=20, t=40, b=30),
                          title=f"Paper NAV — {pf['strategy_name']}",
                          yaxis_tickformat="$,.0f", xaxis_title=None,
                          yaxis_title="Total NAV", hovermode="x unified",
                          legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                      xanchor="right", x=1))
        st.caption("Tip: click a name in the legend to hide/show it; "
                   "double-click to isolate one line.")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No NAV history yet — run `paper_mtm.py` to log today's MTM.")

    # ---- LLM-overlay decision log (only for the experiment sleeves) ----
    if strategy_name in ("llm_overlay_mom_roa_top1_paper", "mom_roa_top1_paper"):
        _render_llm_overlay_panel(strategy_name)
    if strategy_name == "llm_overlay_sector_top4_paper":
        _render_sector_overlay_panel()

    # ---- Open positions with live MTM ----
    st.markdown("#### Open positions")
    if not open_pos:
        st.warning("No open positions.")
    else:
        rows = []
        for p in open_pos:
            last_px = last_closes.get(p["ticker"]) or p["entry_price"]
            last_d = last_close_dates.get(p["ticker"])
            mtm = p["qty"] * last_px
            pnl = mtm - p["entry_value"]
            pnl_pct = (last_px / p["entry_price"] - 1.0) * 100.0
            if last_d is None:
                age_d = None
                stale_marker = "NO PRICE"
            else:
                age_d = (today - _date.fromisoformat(last_d)).days
                stale_marker = f"{age_d}d old" if age_d > 3 else ""
            rows.append({
                "Ticker": p["ticker"],
                "Sector": p["sector"] or "?",
                "Qty": p["qty"],
                "Entry $": p["entry_price"],
                "Last $": last_px,
                "Last date": last_d or "—",
                "Entry val": p["entry_value"],
                "MTM $": mtm,
                "P&L $": pnl,
                "P&L %": pnl_pct,
                "Entry date": p["entry_date"],
                "Mom score": p.get("entry_score"),
                "Stale": stale_marker,
            })
        odf = pd.DataFrame(rows).sort_values("P&L %", ascending=False)
        st.dataframe(
            odf.style.format({
                "Qty": "{:.2f}", "Entry $": "${:.2f}", "Last $": "${:.2f}",
                "Entry val": "${:,.0f}", "MTM $": "${:,.0f}",
                "P&L $": "${:+,.0f}", "P&L %": "{:+.2f}%",
                "Mom score": "{:+.3f}",
            }, na_rep="—"),
            use_container_width=True, height=400,
        )
        # Sector breakdown bar
        sector_summary = (odf.groupby("Sector")["MTM $"].sum()
                          .sort_values(ascending=False))
        fig_sec = go.Figure(go.Bar(
            x=sector_summary.index, y=sector_summary.values,
            text=[f"${v:,.0f}" for v in sector_summary.values],
            textposition="auto",
        ))
        fig_sec.update_layout(
            title="Sector exposure (by current MTM $)", height=280,
            margin=dict(l=40, r=20, t=40, b=30),
            yaxis_tickformat="$,.0f",
        )
        st.plotly_chart(fig_sec, use_container_width=True)

    # ---- Closed positions (last 50) ----
    st.markdown(f"#### Closed positions (last {len(closed_pos)})")
    if not closed_pos:
        st.caption("No positions closed yet (first month or no rebalances).")
    else:
        crows = []
        for p in closed_pos:
            crows.append({
                "Ticker": p["ticker"],
                "Sector": p["sector"] or "?",
                "Qty": p["qty"],
                "Entry $": p["entry_price"],
                "Exit $": p["exit_price"],
                "Entry date": p["entry_date"],
                "Exit date": p["exit_date"],
                "Exit reason": p["exit_reason"],
                "Realized $": p["realized_pnl"],
                "Realized %": p["realized_pnl_pct"],
            })
        cdf = pd.DataFrame(crows)
        st.dataframe(
            cdf.style.format({
                "Qty": "{:.2f}", "Entry $": "${:.2f}", "Exit $": "${:.2f}",
                "Realized $": "${:+,.0f}", "Realized %": "{:+.2f}%",
            }, na_rep="—"),
            use_container_width=True, height=320,
        )

    # ---- Strategy spec / footer (derived per-sleeve so it's correct
    # regardless of selection) ----
    _SPEC_BY_SLEEVE = {
        "mom_v1_paper":       ("mom_v1 (locked 2026-05-28)",
                               "12-1 momentum", 100, "monthly", "5 bps"),
        "mom_v2_paper":       ("mom_v2 (locked 2026-05-26)",
                               "12-1 momentum", 50, "monthly", "5 bps"),
        "mom_roa_6535_paper": ("mom_roa_6535 (locked 2026-05-28)",
                               "Z(mom)*0.65 + Z(ROA)*0.35", 50, "monthly", "5 bps"),
        "residual_roa_6535_paper": ("residual_roa_6535 (locked 2026-06-09)",
                               "Z(residual-mom)*0.65 + Z(ROA)*0.35", 50, "monthly", "5 bps"),
        "sector_top4_paper":  ("sector_top4 (locked 2026-05-29)",
                               "12-1 sector momentum (11 SPDR ETFs)", 4, "monthly", "5 bps"),
        "mom_roa_top1_paper": ("mom_roa_top1 CONTROL (locked 2026-05-31)",
                               "top-1 by mom_roa Z-score, no veto", 1, "monthly", "5 bps"),
        "llm_overlay_mom_roa_top1_paper":  ("llm_overlay TREATMENT (locked 2026-05-31)",
                               "top-1 mom_roa + LLM BUY/VETO + invalidation stop", 1,
                               "monthly", "5 bps"),
        "llm_overlay_sector_top4_paper":  ("sector_overlay TREATMENT (locked 2026-06-05)",
                               "top-4 sectors + macro LLM HOLD/VETO + invalidation stop", 4,
                               "monthly", "5 bps"),
    }
    spec = _SPEC_BY_SLEEVE.get(strategy_name,
                               (strategy_name, "?", "?", "?", "?"))
    st.markdown(f"#### Strategy spec ({spec[0]})")
    spec_cols = st.columns(4)
    spec_cols[0].caption(f"Factor: {spec[1]}")
    spec_cols[1].caption(f"top_n: {spec[2]}")
    spec_cols[2].caption(f"Rebalance: {spec[3]}")
    spec_cols[3].caption(f"Half-spread: {spec[4]}")


# -----------------------------------------------------------------------------
# Main app

def main() -> None:
    st.set_page_config(page_title="Trading Bot Dashboard", page_icon="📈",
                       layout="wide", initial_sidebar_state="expanded")

    # ---- Sidebar ----
    st.sidebar.title("📈 Trading Bot")
    st.sidebar.caption("Paper-trade sleeves + research views")

    strategy = st.sidebar.radio(
        "Strategy",
        options=["🎲 Momentum (current)", "📋 Form 4 (archived)", "🔧 Shared infra"],
        index=0,
        help=("Momentum = Phase 2a factor portfolios (working baseline, "
              "+19.5%/yr in-sample). Form 4 = insider-buy strategy, closed "
              "2026-05-22. Shared = EDGAR cache / simulation runner used "
              "by both."),
    )
    st.sidebar.divider()

    runs = list_runs()

    # Bail-out only if Form 4 view selected and no runs exist; momentum
    # has its own data loader and doesn't need the Form 4 archive.
    if strategy.startswith("📋") and not runs:
        st.sidebar.warning("No Form 4 archived runs.")
        st.title("Trading Bot Dashboard")
        st.info(
            "No Form 4 runs to show. Run `python main.py multi-backtest "
            "--since YYYY-MM-DD --until YYYY-MM-DD` to generate one."
        )
        return

    # Per-strategy controls + headline preview live in the sidebar so the
    # main pane stays focused on whichever strategy was picked above.
    auto_refresh = st.sidebar.toggle(
        "Auto-refresh", value=False,
        help="Re-poll the archive directory and the backfill log on a timer.")
    # Interval spans by-the-second (fine) up to once a day (coarse). Still a
    # slider; labels map to seconds for the sleep at the end of render.
    _INTERVALS = [
        ("5s", 5), ("10s", 10), ("15s", 15), ("30s", 30), ("45s", 45),
        ("1m", 60), ("2m", 120), ("5m", 300), ("15m", 900), ("30m", 1800),
        ("1h", 3600), ("6h", 21600), ("12h", 43200), ("1d", 86400),
    ]
    refresh_label = st.sidebar.select_slider(
        "Interval", options=[lbl for lbl, _ in _INTERVALS], value="15s",
        disabled=not auto_refresh,
        help="Auto-refresh cadence: every few seconds up to once a day.")
    refresh_seconds = dict(_INTERVALS)[refresh_label]

    # How long ago prices were last refreshed: marker written by
    # daily_price_refresh; fall back to the scheduled daily.bat run-log mtime.
    _refresh_dt = None
    try:
        _mk = VAR_DIR / "last_price_refresh.txt"
        if _mk.exists():
            _refresh_dt = datetime.fromisoformat(_mk.read_text().strip())
        else:
            _ld = VAR_DIR / "last_daily_run.log"
            if _ld.exists():
                _refresh_dt = datetime.fromtimestamp(_ld.stat().st_mtime, tz=timezone.utc)
    except Exception:
        _refresh_dt = None
    if _refresh_dt is not None:
        if _refresh_dt.tzinfo is None:
            _refresh_dt = _refresh_dt.replace(tzinfo=timezone.utc)
        _secs = max(0, int((datetime.now(timezone.utc) - _refresh_dt).total_seconds()))
        _ago = (f"{_secs // 60}m ago" if _secs < 3600
                else f"{_secs // 3600}h {(_secs % 3600) // 60}m ago" if _secs < 86400
                else f"{_secs // 86400}d ago")
        st.sidebar.caption(
            f"🕒 Data refreshed {_ago} "
            f"({_refresh_dt.astimezone().strftime('%b %d %H:%M')})")
    else:
        st.sidebar.caption("🕒 Data refreshed: —")

    # Page-refresh timer: how long this view has been up since the last full
    # load / "Refresh now" click. Anchored in session_state (reset by the button).
    # Rendered as a client-side JS ticker so it updates live on mousemove
    # (throttled to 500ms) without a server rerun; 1m interval as an idle backstop.
    _page_anchor = st.session_state.setdefault("page_refreshed_at", datetime.now())
    _anchor_ms = int(_page_anchor.timestamp() * 1000)
    _page_timer_html = """
<div id="pt" style="font:0.8rem/1.4 'Source Sans Pro',sans-serif;color:#808495;margin:0;">🔁 Page refreshed just now</div>
<script>
var A=__ANCHOR__;
function fmt(s){s=Math.max(0,Math.floor(s));
 if(s<5)return 'just now';if(s<60)return s+'s ago';
 if(s<3600)return Math.floor(s/60)+'m ago';
 return Math.floor(s/3600)+'h '+Math.floor((s%3600)/60)+'m ago';}
function upd(){var e=document.getElementById('pt');if(e)e.textContent='🔁 Page refreshed '+fmt((Date.now()-A)/1000);}
upd();
var doc=document;try{if(window.parent&&window.parent.document)doc=window.parent.document;}catch(e){}
var last=0;
doc.addEventListener('mousemove',function(){var t=Date.now();if(t-last<500)return;last=t;upd();});
setInterval(upd,60000);
</script>
""".replace("__ANCHOR__", str(_anchor_ms))
    with st.sidebar:
        components.html(_page_timer_html, height=24)

    if st.sidebar.button("🔄 Refresh now"):
        st.session_state["page_refreshed_at"] = datetime.now()  # reset page timer
        st.cache_data.clear()   # (a) clear ALL data caches -> fresh DB re-read
        st.rerun()
    st.sidebar.divider()

    # ---- Form 4 sidebar (only when that strategy is selected) ----
    selected_run = None
    selected_run_id = None
    run_results: dict = {}
    if strategy.startswith("📋") and runs:
        run_ids = [r["run_id"] for r in runs]
        def _run_display(r: dict) -> str:
            lbl = r.get("label") or r["run_id"]
            date_part = f"  ({r.get('since')}→{r.get('until')})"
            return lbl + date_part
        labels = [_run_display(r) for r in runs]
        label_to_id = dict(zip(labels, run_ids))
        selected_label = st.sidebar.selectbox("Form 4 run", options=labels, index=0)
        selected_run_id = label_to_id[selected_label]
        selected_run = next(r for r in runs if r["run_id"] == selected_run_id)
        st.sidebar.caption(f"Total runs archived: **{len(runs)}**")

        st.sidebar.divider()
        st.sidebar.markdown("**Latest run headlines**")
        latest = runs[0]
        summary = latest.get("summary", {})
        for name in PROFILE_ORDER:
            s = summary.get(name) or {}
            v = s.get("total_pnl_pct")
            if v is None:
                continue
            st.sidebar.markdown(
                f"<span style='color:{PROFILE_COLORS[name]}'>●</span> "
                f"<b>{name}</b> · <span style='color:{color_pct(v)}'>{v:+.2f}%</span>",
                unsafe_allow_html=True,
            )
        run_results = {p: load_profile(selected_run_id, p) for p in PROFILE_ORDER}

    # ---- Main ----
    st.title("Trading Bot Dashboard")

    if strategy.startswith("🎲"):
        # MOMENTUM (current) — factor portfolios + live paper-trade experiment
        st.caption(
            "mom_v2 frozen 2026-05-26: top-50 monthly, +21.0%/yr in-sample, "
            "+26.5%/yr held-out. Now in paper-trade mode."
        )
        mom_tabs = st.tabs([
            "📈 Live experiment",
            "🔬 Backtest archive",
        ])
        with mom_tabs[0]:
            render_paper_trading()
        with mom_tabs[1]:
            render_factors()

    elif strategy.startswith("📋"):
        # FORM 4 (archived) — insider-buy strategy, closed 2026-05-22
        _run_lbl = selected_run.get("label") or selected_run_id
        st.caption(
            f"**Form 4 archive** — strategy CLOSED 2026-05-22 (no edge found). "
            f"Showing **{_run_lbl}** (`{selected_run_id}`) · "
            f"{selected_run.get('since')} → {selected_run.get('until')} · "
            f"{len(runs)} run(s) archived"
        )
        sub = st.tabs([
            "📊 Overview",
            "🛡️ Conservative", "⚖️ Normal", "🔥 Aggressive",
            "🆚 Compare runs",
            "🧪 Simulation",
            "🎯 R15 Optimizer",
        ])
        with sub[0]:
            render_overview(selected_run, run_results)
        for i, name in enumerate(PROFILE_ORDER, start=1):
            with sub[i]:
                data = run_results.get(name)
                if data is None:
                    st.warning(f"No archive for {name} in this run.")
                else:
                    render_profile(name, data, selected_run)
        with sub[4]:
            render_compare(runs)
        with sub[5]:
            render_simulation()
        with sub[6]:
            render_optimizer()

    else:
        # SHARED — EDGAR cache & infra (used by both strategies for price
        # data; Form 4 also used it for filings ingest).
        st.caption("Shared data infrastructure — EDGAR cache, price warm.")
        render_backfill()

    # Auto-refresh via a non-blocking fragment timer. The previous
    # time.sleep()+st.rerun() blocked the script thread for the whole interval,
    # which (on this tall page) left "ghost" copies of the prior render stacked
    # at the bottom each cycle. A fragment with run_every fires from the frontend
    # without blocking; a timestamp gate skips the fragment's initial call so it
    # can't tight-loop, then triggers a clean full-app rerun on each tick.
    st.session_state.setdefault("_last_full_refresh", time.time())

    @st.fragment(run_every=(refresh_seconds if auto_refresh else None))
    def _auto_refresh_tick():
        if not auto_refresh:
            return
        now = time.time()
        if now - st.session_state["_last_full_refresh"] >= refresh_seconds:
            st.session_state["_last_full_refresh"] = now
            list_runs.clear()
            load_profile.clear()
            st.rerun(scope="app")

    _auto_refresh_tick()


if __name__ == "__main__":
    main()
