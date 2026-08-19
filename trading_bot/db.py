"""SQLite schema (the `SCHEMA` DDL) plus thread-local connection helpers.

`connect()` yields a per-thread WAL connection tuned for the backtest workload
(~500K roundtrips/profile): synchronous=NORMAL, ~500MB page cache, 256MB mmap.
`init_db()` applies `SCHEMA` idempotently and back-fills columns older DBs lack.

`SCHEMA` is the authoritative definition of every table - the Form-4 `signals`,
the backtest `positions`/`portfolio_state`, and the live paper-trade
`paper_portfolio`/`paper_positions`/`paper_nav` plus `llm_overlay_log`/
`sector_overlay_log`. The `paper_*` tables are deliberately SEPARATE from
`positions`/`portfolio_state` because `factor_backtest._wipe_state()` truncates
the latter on every run - paper state must survive that - and are keyed by
`strategy_name` so many sleeves share one DB.

Since 2026-08-12 (record CZ) that truncation no longer reaches the file at all:
`shadow_backtest_state()` puts `positions`/`portfolio_state` in per-connection
TEMP tables for the duration of a backtest. See the block above those functions
for why name resolution, and not a scratch DB, is the right seam.
"""
import re
import sqlite3
import threading
from contextlib import contextmanager
from typing import Iterator

from trading_bot.config import DB_PATH, VAR_DIR


# Thread-local connection cache. Backtest runs make ~500K SQL roundtrips per
# profile; a fresh connect() per call costs measurably even on local SQLite.
# Each thread reuses one connection, paying setup once.
_tls = threading.local()


def _new_connection() -> sqlite3.Connection:
    """Open a connection with the performance pragmas this workload needs.

    journal_mode=WAL: persistent DB property, set once. Allows readers + writer
        to coexist without rollback-journal fsyncs on every commit.
    synchronous=NORMAL: trades a tiny crash-safety window (last commit) for
        ~5-10x write throughput. Acceptable for a paper-trade backtest.
    cache_size=-500000: 500MB page cache (negative = KB). Our DB is ~500MB
        of price_cache, so we can hold the whole hot set resident.
    mmap_size=256MB: lets SQLite serve reads via mmap, skipping the page-cache
        copy for hot pages. Stacks with cache_size.
    busy_timeout=30s: WAL allows only ONE writer; without a timeout a second
        writer process gets an immediate "database is locked" error, which can
        abort a rebalance mid-sleeve (audit 2026-07-17, record CG — the 6:03pm
        monthly / 8:30pm ladder tasks are separate writer processes). With it,
        a colliding writer WAITS up to 30s per statement instead of dying.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-500000")
    conn.execute("PRAGMA mmap_size=268435456")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def close_thread_connection() -> None:
    """Tear down the thread-local connection. Call from test fixtures or at
    process exit if you need a clean shutdown — normal usage doesn't require
    it (the OS closes file descriptors when the process ends)."""
    conn = getattr(_tls, "conn", None)
    if conn is not None:
        try:
            conn.commit()
        finally:
            conn.close()
        _tls.conn = None


SCHEMA = """
CREATE TABLE IF NOT EXISTS signals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  accession TEXT,
  filed_at TEXT,
  transaction_date TEXT,
  ticker TEXT NOT NULL,
  issuer_name TEXT,
  issuer_cik TEXT,
  filer_name TEXT NOT NULL,
  filer_cik TEXT,
  filer_title TEXT,
  is_director INTEGER,
  is_officer INTEGER,
  is_ten_percent_owner INTEGER,
  transaction_code TEXT,
  shares REAL,
  price_per_share REAL,
  total_value REAL,
  acquired_disposed TEXT,
  raw_xml_url TEXT,
  ingested_at TEXT NOT NULL,
  UNIQUE (source, accession, filer_cik, transaction_date, ticker, transaction_code, shares)
);

CREATE INDEX IF NOT EXISTS idx_signals_ticker ON signals(ticker);
CREATE INDEX IF NOT EXISTS idx_signals_filed_at ON signals(filed_at);
CREATE INDEX IF NOT EXISTS idx_signals_source ON signals(source);

CREATE TABLE IF NOT EXISTS ingest_state (
  source TEXT PRIMARY KEY,
  last_poll_at TEXT NOT NULL,
  last_filed_at TEXT
);

CREATE TABLE IF NOT EXISTS positions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ticker TEXT NOT NULL,
  status TEXT NOT NULL,                -- 'open' | 'closed'
  qty REAL NOT NULL,
  entry_price REAL NOT NULL,
  entry_value REAL NOT NULL,
  entry_time TEXT NOT NULL,            -- wall-clock when the row was inserted
  entry_date TEXT,                     -- simulated as-of date (the trading day)
  entry_score INTEGER,
  entry_components TEXT,               -- JSON snapshot of scoring breakdown
  sector TEXT,                         -- yfinance sector at entry, for cap enforcement
  exit_price REAL,
  exit_value REAL,
  exit_time TEXT,                      -- wall-clock when closed
  exit_date TEXT,                      -- simulated as-of date for the close
  exit_reason TEXT,                    -- stop_loss | take_profit | time_60d | signal_reversal | manual
  realized_pnl REAL,
  realized_pnl_pct REAL,
  notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);
CREATE INDEX IF NOT EXISTS idx_positions_ticker ON positions(ticker);
CREATE INDEX IF NOT EXISTS idx_positions_sector ON positions(sector);

-- Single-row table for cash + bookkeeping. CHECK constraint enforces singleton.
CREATE TABLE IF NOT EXISTS portfolio_state (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  starting_cash REAL NOT NULL,
  cash REAL NOT NULL,
  initialized_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- Paper-trade tables. KEPT SEPARATE from positions / portfolio_state because
-- factor_backtest._wipe_state() truncates those on every backtest run, which
-- would destroy live paper-trade state. Keyed by `strategy_name` so multiple
-- strategies can paper-trade in parallel against the same DB.
CREATE TABLE IF NOT EXISTS paper_portfolio (
  strategy_name TEXT PRIMARY KEY,
  starting_cash REAL NOT NULL,
  cash REAL NOT NULL,
  initialized_at TEXT NOT NULL,
  last_rebalanced_at TEXT
);

CREATE TABLE IF NOT EXISTS paper_positions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  strategy_name TEXT NOT NULL,
  ticker TEXT NOT NULL,
  status TEXT NOT NULL,                -- 'open' | 'closed'
  qty REAL NOT NULL,
  entry_price REAL NOT NULL,
  entry_value REAL NOT NULL,
  entry_date TEXT NOT NULL,            -- ISO date when entered
  entry_score REAL,                    -- factor score at entry (for diagnostics)
  sector TEXT,
  exit_price REAL,
  exit_value REAL,
  exit_date TEXT,
  exit_reason TEXT,                    -- 'rebalance' for now
  realized_pnl REAL,
  realized_pnl_pct REAL,
  -- Fill provenance (record CU, 2026-08-05). The RAW close each fill was derived
  -- from, before the half-spread, plus the date that close came from -- which is
  -- NOT always the rebalance date, because last_close_on_or_before carries
  -- forward. Captured at fill time on purpose: price_cache is deliberately
  -- mutable (daily_price_refresh re-downloads 30 days with INSERT OR REPLACE,
  -- record CK), so re-deriving a fill's reference price later silently fails.
  -- Measured: 29-day-old fills match NO stored close on any date; 2-day-old
  -- fills match 34/34. Without these columns a rebalance is unmeasurable for
  -- slippage after about a month. NULL on every row written before this change.
  entry_ref_close REAL,
  entry_ref_date TEXT,
  exit_ref_close REAL,
  exit_ref_date TEXT
);
CREATE INDEX IF NOT EXISTS idx_paper_positions_strategy ON paper_positions(strategy_name);
CREATE INDEX IF NOT EXISTS idx_paper_positions_status ON paper_positions(strategy_name, status);
CREATE INDEX IF NOT EXISTS idx_paper_positions_ticker ON paper_positions(ticker);

-- Daily MTM log, one row per (strategy, date). Built by paper_mtm.py.
CREATE TABLE IF NOT EXISTS paper_nav (
  strategy_name TEXT NOT NULL,
  nav_date TEXT NOT NULL,
  cash REAL NOT NULL,
  positions_value REAL NOT NULL,
  total_nav REAL NOT NULL,
  n_open_positions INTEGER NOT NULL,
  PRIMARY KEY (strategy_name, nav_date)
);

-- LLM-overlay decision log. One pre-committed decision per rebalance date for
-- the llm_overlay_mom_roa_top1_paper experiment (see strategies/llm_overlay.py). The
-- candidate is always the top mom_roa_6535-ranked name; the LLM either BUYs
-- or VETOs it, and records the price level at which the long thesis breaks.
-- Logging the decision BEFORE acting is the whole point: it makes the
-- discretionary overlay falsifiable after the fact (do scores predict
-- forward returns? does VETO add value vs the no-veto control?).
CREATE TABLE IF NOT EXISTS llm_overlay_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  decision_date TEXT NOT NULL,         -- ISO date the decision applies to (rebalance day)
  ticker TEXT NOT NULL,                -- candidate = top mom_roa name at decision time
  score REAL,                          -- 1-10 from the equity-analyst deep dive
  verdict TEXT NOT NULL,               -- 'BUY' | 'VETO'
  invalidation_level REAL,             -- close at/below which thesis breaks -> exit to cash
  rationale TEXT,                      -- one-line summary of the call
  created_at TEXT NOT NULL,
  -- (date, ticker): one decision per candidate per rebalance date. The cash
  -- overlay only logs #1; the cascade sleeve (llm_cascade) logs several names
  -- deeper in the ranking on the same date, so the key must include ticker.
  UNIQUE (decision_date, ticker)
);

-- Sector-overlay decision log. Parallel experiment to llm_overlay_log but for
-- the sector_top4 sleeve: a MACRO/top-down LLM overlay (rate regime, sector
-- valuation/crowding, earnings breadth) that may VETO any of the 4 momentum-
-- picked SPDR sector ETFs to cash. Multi-name, so the key is
-- (decision_date, ticker) — up to TOP_N rows per rebalance date. Kept separate
-- from llm_overlay_log so the live single-name experiment is untouched.
-- Honest prior: weaker test than the stock overlay (macro = lowest LLM edge);
-- see strategies/sector_overlay.py.
CREATE TABLE IF NOT EXISTS sector_overlay_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  decision_date TEXT NOT NULL,         -- ISO date the decision applies to (rebalance day)
  ticker TEXT NOT NULL,                -- sector ETF (XLK, XLE, ...) among the top-4
  score REAL,                          -- 1-10 conviction the sector beats cash next month
  verdict TEXT NOT NULL,               -- 'HOLD' | 'VETO'
  invalidation_level REAL,             -- ETF close at/below which thesis breaks -> exit to cash
  rationale TEXT,                      -- one-line summary of the call
  created_at TEXT NOT NULL,
  UNIQUE (decision_date, ticker)
);

-- Decision logs are APPEND-ONLY (CLAUDE.md: "LLM decisions are never backdated").
-- The Python writers use plain INSERT since 2026-08-18 (record DG); these
-- triggers make the same rule hold for ANY writer, including raw SQL, so a
-- future INSERT OR REPLACE / UPDATE / DELETE cannot quietly destroy a row the
-- way three were destroyed before (llm_overlay_log ids 4, 5, 9 - record DA
-- finding 4). Idempotent via IF NOT EXISTS; applied to the live DB by init_db().
-- BEFORE INSERT, not just DELETE: SQLite's REPLACE conflict-resolution does NOT
-- fire delete triggers unless PRAGMA recursive_triggers is on, so a delete
-- trigger alone still lets `INSERT OR REPLACE` destroy the old row. Refusing the
-- insert while a (date, ticker) row exists closes that path for every writer.
CREATE TRIGGER IF NOT EXISTS llm_overlay_log_no_relog BEFORE INSERT ON llm_overlay_log
WHEN EXISTS (SELECT 1 FROM llm_overlay_log
             WHERE decision_date = NEW.decision_date AND ticker = NEW.ticker)
BEGIN SELECT RAISE(ABORT, 'llm_overlay_log is append-only (record DG): decision already logged for this date+ticker'); END;
CREATE TRIGGER IF NOT EXISTS llm_overlay_log_no_update BEFORE UPDATE ON llm_overlay_log
BEGIN SELECT RAISE(ABORT, 'llm_overlay_log is append-only (record DG)'); END;
CREATE TRIGGER IF NOT EXISTS llm_overlay_log_no_delete BEFORE DELETE ON llm_overlay_log
BEGIN SELECT RAISE(ABORT, 'llm_overlay_log is append-only (record DG)'); END;
CREATE TRIGGER IF NOT EXISTS sector_overlay_log_no_relog BEFORE INSERT ON sector_overlay_log
WHEN EXISTS (SELECT 1 FROM sector_overlay_log
             WHERE decision_date = NEW.decision_date AND ticker = NEW.ticker)
BEGIN SELECT RAISE(ABORT, 'sector_overlay_log is append-only (record DG): decision already logged for this date+ticker'); END;
CREATE TRIGGER IF NOT EXISTS sector_overlay_log_no_update BEFORE UPDATE ON sector_overlay_log
BEGIN SELECT RAISE(ABORT, 'sector_overlay_log is append-only (record DG)'); END;
CREATE TRIGGER IF NOT EXISTS sector_overlay_log_no_delete BEFORE DELETE ON sector_overlay_log
BEGIN SELECT RAISE(ABORT, 'sector_overlay_log is append-only (record DG)'); END;
"""


# ---------------------------------------------------------------------------
# Backtest scratch state (record CZ; audit finding CQ.2 #2).
#
# `positions` and `portfolio_state` are BACKTEST tables -- nothing paper-trade
# lives in them. `factor_backtest._wipe_state()` DELETEs both on every run, and
# `CLAUDE.md` mandates running the frozen tests (which ARE a factor_backtest)
# after any Python change while separately forbidding concurrent factor_backtest
# against the live DB. So the mandated check was the forbidden operation: a
# second writer holding a lock on the live 5 GB file, leaving residue rows behind.
#
# The fix is name resolution, not plumbing. SQLite resolves an UNQUALIFIED table
# name temp -> main -> attached, so a TEMP table named `positions` shadows the
# real one for every `... FROM positions ...` already written anywhere in this
# codebase -- broker.py, monitor.py, portfolio.py, multi_backtest.py,
# reporting/*, form4/optimize_r15_wf.py -- with no query rewritten and no
# connection redirected. `price_cache` has no shadow, so the backtest still
# reads the real 37.7M-row cache from `main`. TEMP tables live in the
# connection's own temp store and are gone when it closes; the live file is
# never written.
# ---------------------------------------------------------------------------

BACKTEST_STATE_TABLES = ("positions", "portfolio_state")

_CREATE_TABLE_RE = re.compile(r"^\s*CREATE\s+TABLE\s+", re.IGNORECASE)


def _columns(conn: sqlite3.Connection, schema: str, table: str) -> list[str]:
    return [r[1] for r in conn.execute(f"PRAGMA {schema}.table_info({table})")]


def shadow_backtest_state(conn: sqlite3.Connection | None = None) -> tuple[str, ...]:
    """Shadow the backtest state tables with per-connection TEMP copies.

    Idempotent: a table already shadowed on this connection is left alone.
    Returns the tables newly shadowed.

    The DDL is copied from the LIVE table's own `sqlite_master.sql` rather than
    from `SCHEMA` above, so the shadow inherits the defensive ALTER-added columns
    (`peak_close_price`, `split_ratio_at_exit`, `dividends_received`, ...) that
    `SCHEMA` does not declare. Copying `SCHEMA` instead would build a shadow
    missing those columns and the backtest would fail on a column that exists in
    the real table -- so the column sets are asserted equal before returning.

    NOTE: once shadowed, this connection can no longer see the real
    `positions` / `portfolio_state` unqualified. Use `main.positions` for that,
    or `unshadow_backtest_state()`.
    """
    own = conn is None
    if own:
        ctx = connect()
        conn = ctx.__enter__()
    try:
        shadowed = []
        temp_tables = {r[0] for r in conn.execute(
            "SELECT name FROM temp.sqlite_master WHERE type='table'")}
        for table in BACKTEST_STATE_TABLES:
            if table in temp_tables:
                continue
            row = conn.execute(
                "SELECT sql FROM main.sqlite_master WHERE type='table' AND name=?",
                (table,)).fetchone()
            if row is None or not row[0]:
                raise RuntimeError(
                    f"cannot shadow {table!r}: no such table in the live DB. "
                    "Run init_db() first.")
            ddl, n = _CREATE_TABLE_RE.subn("CREATE TEMP TABLE ", row[0], count=1)
            if n != 1:
                raise RuntimeError(f"unexpected DDL for {table!r}: {row[0][:80]!r}")
            conn.execute(ddl)
            live, temp = _columns(conn, "main", table), _columns(conn, "temp", table)
            if live != temp:
                raise RuntimeError(
                    f"shadow of {table!r} does not match the live table: "
                    f"live={live} temp={temp}")
            shadowed.append(table)
        return tuple(shadowed)
    finally:
        if own:
            ctx.__exit__(None, None, None)


def unshadow_backtest_state(conn: sqlite3.Connection | None = None) -> tuple[str, ...]:
    """Drop the TEMP shadows so unqualified names resolve to the live tables again."""
    own = conn is None
    if own:
        ctx = connect()
        conn = ctx.__enter__()
    try:
        dropped = []
        for table in BACKTEST_STATE_TABLES:
            if conn.execute("SELECT 1 FROM temp.sqlite_master WHERE type='table' "
                            "AND name=?", (table,)).fetchone():
                conn.execute(f"DROP TABLE temp.{table}")
                dropped.append(table)
        return tuple(dropped)
    finally:
        if own:
            ctx.__exit__(None, None, None)


def init_db() -> None:
    VAR_DIR.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript(SCHEMA)
        # Defensive column adds for tables created by older versions.
        for table, col, decl in [
            ("positions", "entry_date", "TEXT"),
            ("positions", "exit_date", "TEXT"),
            ("positions", "peak_close_price", "REAL"),
            ("positions", "split_ratio_at_exit", "REAL"),
            ("positions", "dividends_received", "REAL"),
        ]:
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")
            except sqlite3.OperationalError:
                pass  # column already exists


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    """Yield the per-thread sqlite connection.

    Commits on normal exit so the existing `with connect() as conn: ...`
    pattern keeps its write semantics. Does NOT close — the connection
    persists for the thread's lifetime and is reused by subsequent calls.
    """
    conn = getattr(_tls, "conn", None)
    if conn is None:
        conn = _new_connection()
        _tls.conn = conn
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
