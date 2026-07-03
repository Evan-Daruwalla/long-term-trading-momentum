"""Drip-warm every gap in the persistent cache so STRICT_CACHE=1 holds.

Different from warm_cache / warm_close / warm_atr / warm_splits in two ways:

  1. **Coverage-driven.** Compares the strategy's actual cache needs
     (signals × backtest window) against price_cache.kind contents and
     enumerates exactly the (ticker, kind, key_date) tuples missing.
  2. **Patient.** Runs at one batch every BATCH_DELAY seconds, with a
     LONG_PAUSE on rate-limit signal. Yfinance lets you retry once you
     wait long enough; this script just waits.

Run periodically (or once overnight) until "0 missing tuples". After
that, set STRICT_CACHE=1 and never call yfinance again during backtests.

Idempotent. Safe to interrupt and resume.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import time
from datetime import date, datetime, timedelta

import pandas as pd
import yfinance as yf

from trading_bot.config import DB_PATH

BATCH_SIZE   = 50           # smaller batches → fewer rate-limit triggers
BATCH_DELAY  = 5.0          # seconds between batches (gentle)
LONG_PAUSE   = 120.0        # seconds after a rate-limit signal
# Defaults preserve the original 2021-2026 R-iteration behavior.
# Override via --dl-start/--dl-end/--sig-start/--sig-end for historical warms.
DL_START     = "2020-06-01"
DL_END       = "2026-05-08"
SIG_START    = "2021-05-01"
SIG_END      = "2099-12-31"
TICKER_RE    = re.compile(r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$")
ATR_WINDOW   = 20
MA_WINDOW    = 50

# Kinds we warm in this script. above_ma_200 is SPY-only and already done;
# splits_json is per-ticker not per-date. Both handled in dedicated scripts.
KINDS_PER_SIG_DATE = ("next_open", "next_open_vol", "next_open_range",
                      f"above_ma_{MA_WINDOW}", f"atr_pct_{ATR_WINDOW}")


def _valid(t: str) -> bool:
    return bool(TICKER_RE.match(t))


def _is_rate_limit(exc: BaseException) -> bool:
    s = str(exc).lower()
    return "too many requests" in s or "rate limit" in s


def _expected_close_rows(dl_start: str, dl_end: str) -> int:
    """~63% of calendar days are trading days. Use 50% as the threshold
    so partial coverage (holidays, delistings near edges) doesn't trigger
    pointless re-warms, but missing-by-year gaps do trigger."""
    d0 = date.fromisoformat(dl_start); d1 = date.fromisoformat(dl_end)
    calendar_days = max(1, (d1 - d0).days + 1)
    return int(calendar_days * 0.50 * (252/365))


def _missing_tickers_for_close(conn: sqlite3.Connection) -> list[str]:
    """Tickers in our universe with <expected close rows IN [DL_START,DL_END]
    = need re-warm. Date-range-filtered so 'AAPL has 1500 post-2020 rows'
    doesn't mask 'AAPL has 0 rows in 2010-2018'."""
    threshold = _expected_close_rows(DL_START, DL_END)
    rows = conn.execute(
        """
        SELECT s.ticker, COUNT(p.key_date) AS n
        FROM (SELECT DISTINCT ticker FROM signals WHERE transaction_code='P'
              AND filed_at BETWEEN ? AND ?) s
        LEFT JOIN price_cache p
          ON p.ticker = s.ticker AND p.kind = 'close'
          AND p.key_date BETWEEN ? AND ?
        GROUP BY s.ticker
        HAVING n < ?
        """,
        (SIG_START, SIG_END, DL_START, DL_END, threshold),
    ).fetchall()
    return sorted({t for (t, _n) in rows if _valid(t)})


def _buy_day_keys(filed_at_iso: str, n_weekdays: int = 6) -> list[str]:
    """Candidate backtest buy-days for a P signal.

    The simulator looks up next_open / above_ma keyed by the *day it attempts
    the buy* — execute_pending(as_of=D). A signal first becomes visible the
    first weekday D >= filed_at, and the backtest only runs entries on
    weekdays (`cur.weekday() < 5`). The buy can slip a few days past that
    (filing on a holiday, ticker already held, portfolio full), so we warm
    the first `n_weekdays` weekday candidates starting at filed_at. Keying by
    transaction_date (the old behavior) is wrong — it's 2-4 days too early.
    """
    d = date.fromisoformat(filed_at_iso[:10])
    keys: list[str] = []
    while len(keys) < n_weekdays:
        if d.weekday() < 5:          # Mon-Fri
            keys.append(d.isoformat())
        d += timedelta(days=1)
    return keys


def _missing_per_signal_pairs(conn: sqlite3.Connection) -> dict[str, list[str]]:
    """{ticker: [buy_day]} — the per-signal-date cache keys to warm.

    Keys are the candidate backtest buy-days (see _buy_day_keys), NOT the
    signal transaction_date. INSERT OR IGNORE downstream makes re-emitting
    already-cached keys harmless, so there's no canary-skip here.
    """
    rows = conn.execute(
        """
        SELECT DISTINCT s.ticker, substr(s.filed_at, 1, 10) AS fa
        FROM signals s
        WHERE s.transaction_code='P' AND s.filed_at BETWEEN ? AND ?
        """,
        (SIG_START, SIG_END),
    ).fetchall()
    out: dict[str, set[str]] = {}
    for ticker, fa in rows:
        if _valid(ticker) and fa:
            out.setdefault(ticker, set()).update(_buy_day_keys(fa))
    return {t: sorted(keys) for t, keys in out.items()}


def _bulk_insert(rows: list[tuple]) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.executemany(
        "INSERT OR IGNORE INTO price_cache (ticker, kind, key_date, price) "
        "VALUES (?,?,?,?)",
        rows,
    )
    conn.commit()
    conn.close()


def _download(tickers: list[str]) -> pd.DataFrame | None:
    """yf.download with rate-limit-aware retries."""
    for attempt in range(5):
        try:
            df = yf.download(
                tickers, start=DL_START, end=DL_END,
                auto_adjust=False, progress=False, group_by="ticker",
                actions=False,
            )
            return df
        except Exception as e:
            if _is_rate_limit(e):
                pause = LONG_PAUSE * (attempt + 1)
                print(f"  rate-limited; sleeping {pause:.0f}s "
                      f"(attempt {attempt+1}/5)", flush=True)
                time.sleep(pause)
                continue
            print(f"  download error: {e}", flush=True)
            return None
    return None


def _emit_close_rows(ticker: str, df: pd.DataFrame) -> list[tuple]:
    """All daily close rows for a ticker."""
    if df is None or df.empty:
        return []
    closes = df["Close"].dropna()
    return [(ticker, "close", (ts.date() if hasattr(ts, "date") else ts).isoformat(),
             float(c)) for ts, c in closes.items()]


def _emit_per_signal_rows(ticker: str, df: pd.DataFrame, signal_dates: list[str]) -> list[tuple]:
    """Per-signal-date kinds (next_open, vol, range, above_ma_50, atr_pct_20)."""
    if df is None or df.empty:
        return []
    df = df.sort_index()
    idx_dates = [d.date() if hasattr(d, "date") else d for d in df.index]
    idx_pos = {d: i for i, d in enumerate(idx_dates)}
    closes = df["Close"]
    ma50 = closes.rolling(MA_WINDOW, min_periods=MA_WINDOW).mean()
    highs = df["High"].astype(float); lows = df["Low"].astype(float)
    prev_c = closes.shift(1)
    tr = pd.concat([highs - lows, (highs - prev_c).abs(),
                    (lows - prev_c).abs()], axis=1).max(axis=1)
    atr = tr.rolling(ATR_WINDOW, min_periods=ATR_WINDOW).mean()
    atr_p = atr / closes

    out: list[tuple] = []
    for sig in signal_dates:
        sig_d = date.fromisoformat(sig)
        # next trading day strictly after sig_d
        next_pos = next((i for i, d in enumerate(idx_dates) if d > sig_d), None)
        if next_pos is None:
            for k in ("next_open", "next_open_vol", "next_open_range",
                      f"above_ma_{MA_WINDOW}", f"atr_pct_{ATR_WINDOW}"):
                out.append((ticker, k, sig, None))
            continue
        row = df.iloc[next_pos]
        op = float(row["Open"]) if pd.notna(row["Open"]) else None
        vol = float(row["Volume"]) if pd.notna(row["Volume"]) else None
        rng = ((float(row["High"]) - float(row["Low"])) / op
               if op and op > 0 and pd.notna(row["High"]) and pd.notna(row["Low"])
               else None)
        # above_ma_50 keyed off sig_d's close (not next_open day's close —
        # matches is_above_ma() semantics)
        if sig_d in idx_pos:
            i = idx_pos[sig_d]
            ma_v = ma50.iloc[i]; cl_v = closes.iloc[i]
            above = float(cl_v > ma_v) if pd.notna(ma_v) and pd.notna(cl_v) else None
        else:
            above = None
        # atr_pct keyed off the entry day (= next_pos day)
        atr_v = atr_p.iloc[next_pos]
        atr_val = float(atr_v) if pd.notna(atr_v) else None
        # next_open_* and atr_pct keyed by sig_d for next_open kinds, by
        # entry_d for atr_pct (matches market_data.atr_pct() lookup convention)
        entry_d_iso = idx_dates[next_pos].isoformat()
        out.append((ticker, "next_open", sig, op))
        out.append((ticker, "next_open_vol", sig, vol))
        out.append((ticker, "next_open_range", sig, rng))
        out.append((ticker, f"above_ma_{MA_WINDOW}", sig, above))
        out.append((ticker, f"atr_pct_{ATR_WINDOW}", entry_d_iso, atr_val))
    return out


def main() -> None:
    global DL_START, DL_END, SIG_START, SIG_END
    ap = argparse.ArgumentParser()
    ap.add_argument("--dl-start",  default=DL_START,  help="yfinance download start (YYYY-MM-DD)")
    ap.add_argument("--dl-end",    default=DL_END,    help="yfinance download end (YYYY-MM-DD)")
    ap.add_argument("--sig-start", default=SIG_START, help="only warm signals filed on/after this date")
    ap.add_argument("--sig-end",   default=SIG_END,   help="only warm signals filed on/before this date")
    args = ap.parse_args()
    DL_START, DL_END, SIG_START, SIG_END = args.dl_start, args.dl_end, args.sig_start, args.sig_end
    print(f"Window: DL [{DL_START}..{DL_END}]  SIG [{SIG_START}..{SIG_END}]", flush=True)

    conn = sqlite3.connect(DB_PATH)
    close_todo = _missing_tickers_for_close(conn)
    sig_todo = _missing_per_signal_pairs(conn)
    conn.close()

    sig_pair_count = sum(len(v) for v in sig_todo.values())
    print(f"Coverage gaps:", flush=True)
    print(f"  close-cache: {len(close_todo)} tickers under 500 bars", flush=True)
    print(f"  signal-pairs: {len(sig_todo)} tickers, {sig_pair_count} pairs", flush=True)

    # Union: any ticker that needs anything goes into the warm batch
    all_todo = sorted(set(close_todo) | set(sig_todo))
    if not all_todo:
        print("Nothing missing. STRICT_CACHE should be safe to enable.", flush=True)
        return
    print(f"  total tickers to fetch: {len(all_todo)}", flush=True)

    batches = [all_todo[i:i+BATCH_SIZE] for i in range(0, len(all_todo), BATCH_SIZE)]
    print(f"  {len(batches)} batches of up to {BATCH_SIZE}\n", flush=True)

    started = time.time()
    written = 0
    for i, batch in enumerate(batches, 1):
        t0 = time.time()
        df = _download(batch)
        rows: list[tuple] = []
        if df is not None and not df.empty:
            if len(batch) == 1:
                df = pd.concat({batch[0]: df}, axis=1)
            for ticker in batch:
                try:
                    sub = df[ticker].dropna(how="all").sort_index()
                except KeyError:
                    sub = None
                if sub is None or sub.empty:
                    # Download succeeded for the batch but this ticker has no
                    # data — a genuine delisting. Cache None misses at every
                    # buy-day key for the pre-buy kinds so the backtest skips
                    # fast instead of re-probing yfinance on every run.
                    for k in sig_todo.get(ticker, ()):
                        for kind in ("next_open", "next_open_vol",
                                     "next_open_range", f"above_ma_{MA_WINDOW}"):
                            rows.append((ticker, kind, k, None))
                    continue
                # Always emit closes (idempotent if already cached)
                rows.extend(_emit_close_rows(ticker, sub))
                # Per-signal-date emissions if needed
                if ticker in sig_todo:
                    rows.extend(_emit_per_signal_rows(ticker, sub, sig_todo[ticker]))

        if rows:
            _bulk_insert(rows)
            written += len(rows)

        elapsed = time.time() - t0
        total_elapsed = time.time() - started
        pct = 100 * i / len(batches)
        eta = (total_elapsed / max(i, 1)) * (len(batches) - i)
        print(f"  [{i:3d}/{len(batches)}] {pct:5.1f}%  +{len(rows):5d} rows  "
              f"{elapsed:5.1f}s  (ETA {eta/60:.1f} min, written {written:,})",
              flush=True)
        if i < len(batches):
            time.sleep(BATCH_DELAY)

    print(f"\nDone in {(time.time()-started)/60:.1f} min. "
          f"{written:,} rows written.", flush=True)


if __name__ == "__main__":
    main()
