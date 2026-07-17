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
"""
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
  realized_pnl_pct REAL
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
"""


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
