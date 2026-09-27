"""Regression test: a PER-TICKER rate limit is retried and, if it persists, fails.

Record DY (2026-09-23). yfinance rate-limits the nightly refresh from ~batch 15
of 30, and it does so ticker by ticker inside batches that still return rows.
Neither existing guard (all-3-attempts-raised, wholly-empty batch) fires, the
refresh exits 0, and the back half of the alphabet never gets its closes, so
every day since 09-21 sat below the coverage floor.

Fakes yf.download with a request budget: once it is spent, every other ticker
comes back with no rows while the batch itself still returns rows - the
observed shape (09-22: K-Z 46%). A wholly-empty batch would trip the OLD guard
and prove nothing. Fixture DB, no network.
  1. limit mid-run, clears on retry -> every live ticker gets today's close, exit 0.
  2. limit never clears             -> exit 1, REFRESH INCOMPLETE.
  3. one live ticker never served   -> below 5%, exit 0 (warning only).
  4. a ticker with no close in the window (delisted) is never retried.

Run:
    python -m scripts.momentum.test_refresh_rate_limit
"""
from __future__ import annotations

import logging
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from trading_bot import db as dbmod
from trading_bot.execution import market_data

LIVE = [f"T{i:03d}" for i in range(60)]
DEAD = "DEAD"
TODAY = date.today()


class _FakeYF:
    """Serves `budget` ticker-requests, then only even-numbered tickers."""

    def __init__(self, budget: int, never: set[str] = frozenset()):
        self.budget, self.never, self.requested = budget, set(never), []

    def download(self, tickers, **_kw):
        tickers = list(tickers)
        idx = pd.DatetimeIndex([pd.Timestamp(TODAY - timedelta(days=1)),
                                pd.Timestamp(TODAY)])
        served = {}
        for t in tickers:
            self.requested.append(t)
            if t in self.never or t == DEAD:
                continue
            limited = self.budget <= 0
            self.budget -= 1
            if not limited or int(t[1:]) % 2 == 0:
                served[t] = pd.DataFrame({"Close": [10.0, 11.0],
                                          "Volume": [100.0, 100.0]}, index=idx)
        if not served:
            return pd.DataFrame()
        if len(tickers) == 1:
            return served[tickers[0]]
        return pd.concat(served, axis=1)


def _fixture() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="pm_ratelimit_"))
    dbmod.close_thread_connection()
    dbmod.DB_PATH = tmp / "trades.db"
    dbmod.VAR_DIR = tmp
    dbmod.init_db()
    market_data._ensure_cache_schema()
    old = (TODAY - timedelta(days=5)).isoformat()
    with dbmod.connect() as c:
        for t in LIVE:
            c.execute("INSERT INTO price_cache (ticker, kind, key_date, price) "
                      "VALUES (?, 'close', ?, 9.0)", (t, old))
        c.execute("INSERT INTO price_cache (ticker, kind, key_date, price) "
                  "VALUES (?, 'close', '2020-01-02', 1.0)", (DEAD,))
    return tmp


def _run(fake: _FakeYF) -> tuple[int, int, str]:
    from scripts.momentum import daily_price_refresh as dpr
    tmp = _fixture()
    dpr.VAR_DIR = tmp
    dpr.BATCH_SIZE = 7          # 61 tickers -> no single-ticker main batch
    dpr.yf = fake
    dpr.time.sleep = lambda _s: None
    sys.argv = ["daily_price_refresh"]
    msgs: list[str] = []
    h = logging.Handler()
    h.emit = lambda r: msgs.append(r.getMessage())
    dpr.log.addHandler(h)
    try:
        rc = dpr.main()
    finally:
        dpr.log.removeHandler(h)
    with dbmod.connect() as c:
        n_today = c.execute("SELECT count(*) FROM price_cache WHERE kind='close' "
                            "AND key_date=?", (TODAY.isoformat(),)).fetchone()[0]
    return rc, n_today, "\n".join(msgs)


def main() -> int:
    failures: list[str] = []
    passed: list[str] = []

    def check(cond, msg):
        print(f"  [{'OK  ' if cond else 'FAIL'}] {msg}")
        (passed if cond else failures).append(msg)

    print("Running refresh rate-limit tests...")

    # 1. Budget runs out after 25 of 60 in the main pass; the retry pass gets a
    #    fresh budget (the fake is re-armed by the first retry request).
    #    Every main batch still returns rows, so the old guards stay silent.
    fake = _FakeYF(budget=25)
    orig = fake.download

    def rearm(tickers, **kw):
        if len(fake.requested) >= len(LIVE) + 1 and fake.budget <= 0:
            fake.budget = 10_000
        return orig(tickers, **kw)
    fake.download = rearm
    rc, n, log_text = _run(fake)
    check(n == len(LIVE), f"limit that clears: all {len(LIVE)} live tickers get "
                          f"today's close (got {n})")
    check(rc == 0, f"limit that clears: exit 0 (got {rc})")
    check("Retry 1" in log_text, "the retry is logged")
    check(fake.requested.count(DEAD) == 1,
          f"delisted ticker is requested once, never retried "
          f"(requested {fake.requested.count(DEAD)}x)")

    # 2. Budget never recovers: odd tickers past the budget stay missing.
    rc, n, log_text = _run(_FakeYF(budget=25))
    check(rc == 1 and "REFRESH INCOMPLETE" in log_text,
          f"limit that never clears: exit 1 + REFRESH INCOMPLETE (got rc {rc})")
    check(n == 42, f"...with 25 + 17 even-numbered (T026-T058) written (got {n})")

    # 3. One live ticker never served: 1/60 = 1.7% < 5%.
    rc, n, log_text = _run(_FakeYF(budget=10_000, never={"T059"}))
    check(rc == 0 and "T059" in log_text,
          f"one missing name: exit 0 with a warning naming it (got rc {rc})")

    dbmod.close_thread_connection()
    n_all = len(passed) + len(failures)
    print(f"\n{'PASS' if not failures else 'FAIL'}: {len(passed)}/{n_all} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
