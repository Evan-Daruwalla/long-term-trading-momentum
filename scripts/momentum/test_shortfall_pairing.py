"""Tests for the M6.2 implementation-shortfall path. Fixture DB only; live DB untouched.

Covers the three things that are wrong-by-default here and fail QUIETLY:

  1. The SIGN. A sell that fills BELOW the sim's price is a cost, so its sign
     flips. Get it backwards and the sell legs cancel the buy legs instead of
     adding to them, which looks like "execution is fine."
  2. WHICH LEG a fill pairs to. A sell must pair to exit_price; pairing it to
     entry_price compares two unrelated trades and still returns a number
     (record CT.1, the legacy path's defect).
  3. RE-RUNNING the live write. This is a command Evan runs by hand, so a second
     run is a realistic accident; duplicated rows would silently distort every
     later mean without failing anything.

Run:
    python -m scripts.momentum.test_shortfall_pairing
"""
from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

from scripts.momentum import slippage_tracker as st

POSITIONS_SCHEMA = """
CREATE TABLE paper_positions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  strategy_name TEXT NOT NULL, ticker TEXT NOT NULL, status TEXT NOT NULL,
  qty REAL NOT NULL, entry_price REAL NOT NULL, entry_value REAL NOT NULL,
  entry_date TEXT NOT NULL, exit_price REAL, exit_value REAL, exit_date TEXT
);
"""

CSV_HEADER = ("ticker,side,qty,filled_avg_price,filled_at,account,order_id,"
              "sleeve,status,qty_filled,submitted_at\n")


def _fixture() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(POSITIONS_SCHEMA)
    # AAA: bought at the 07-07 rebalance for $100.
    conn.execute("INSERT INTO paper_positions (strategy_name, ticker, status, qty, "
                 "entry_price, entry_value, entry_date) "
                 "VALUES ('sleeve_a','AAA','open',10,100.0,1000.0,'2026-07-07')")
    # BBB: entered earlier at $50, SOLD at the 08-03 rebalance for $200. The two
    # prices are deliberately far apart so pairing to the wrong leg is obvious.
    conn.execute("INSERT INTO paper_positions (strategy_name, ticker, status, qty, "
                 "entry_price, entry_value, entry_date, exit_price, exit_value, "
                 "exit_date) VALUES ('sleeve_a','BBB','closed',10,50.0,500.0,"
                 "'2026-07-07',200.0,2000.0,'2026-08-03')")
    conn.commit()
    return conn


def _csv(rows: list[str]) -> Path:
    p = Path(tempfile.mkdtemp(prefix="shortfall_")) / "fills.csv"
    p.write_text(CSV_HEADER + "".join(rows), encoding="utf-8")
    return p


def test_sign_convention() -> None:
    # Buy: paid 101 where the sim booked 100 -> 100bps WORSE.
    assert abs(st.shortfall_bps(100.0, 101.0, "buy") - 100.0) < 1e-9
    # Buy: paid 99 -> 100bps BETTER.
    assert abs(st.shortfall_bps(100.0, 99.0, "buy") + 100.0) < 1e-9
    # Sell: received 99 where the sim booked 100 -> WORSE, so POSITIVE.
    assert abs(st.shortfall_bps(100.0, 99.0, "sell") - 100.0) < 1e-9
    # Sell: received 101 -> BETTER, so negative.
    assert abs(st.shortfall_bps(100.0, 101.0, "sell") + 100.0) < 1e-9
    print("  [OK  ] sign: worse-than-sim is positive for BOTH buy and sell")


def test_pairs_sell_to_exit_not_entry() -> None:
    conn = _fixture()
    csv = _csv([
        "AAA,buy,10,101.0,2026-07-07T18:20:00Z,ACCT1,o1,sleeve_a,filled,10,"
        "2026-07-07T18:20:00Z\n",
        "BBB,sell,10,198.0,2026-08-04T13:30:00Z,ACCT1,o2,sleeve_a,filled,10,"
        "2026-08-04T08:00:00Z\n",
    ])
    paired, unpaired = st.pair_alpaca_csv(csv, conn)
    assert not unpaired, unpaired
    by_ticker = {p["ticker"]: p for p in paired}

    assert by_ticker["AAA"]["sim_px"] == 100.0, by_ticker["AAA"]
    assert abs(by_ticker["AAA"]["bps"] - 100.0) < 1e-9, by_ticker["AAA"]

    # The whole point: 200.0 (exit_price), NOT 50.0 (entry_price).
    assert by_ticker["BBB"]["sim_px"] == 200.0, \
        f"sell paired to the wrong leg: {by_ticker['BBB']}"
    assert abs(by_ticker["BBB"]["bps"] - 100.0) < 1e-9, by_ticker["BBB"]

    # And the queue-shift mapping held: Alpaca's 08-04 -> the 08-03 rebalance.
    assert by_ticker["BBB"]["rebalance"] == "2026-08-03", by_ticker["BBB"]
    print("  [OK  ] pairing: buy->entry_price, sell->exit_price, 08-04 batch->08-03")
    conn.close()


def test_unpaired_is_reported_not_dropped() -> None:
    conn = _fixture()
    csv = _csv([
        # No sim leg: the mirror trimmed a name the sim did not close that day.
        "CCC,sell,5,10.0,2026-08-04T13:30:00Z,ACCT1,o3,sleeve_a,filled,5,"
        "2026-08-04T08:00:00Z\n",
        # A batch date with no rebalance mapping at all.
        "AAA,buy,10,101.0,2026-09-09T13:30:00Z,ACCT1,o4,sleeve_a,filled,10,"
        "2026-09-09T13:30:00Z\n",
        # AAA's sim buy leg exists, but on 2026-07-07, not the 08-03 rebalance
        # this fill maps to. That is a DATE MISMATCH, a different finding from
        # "the sim never bought this name" - and it must not be paired across
        # dates (the legacy path's defect, record CT.1).
        "AAA,buy,10,101.0,2026-08-04T13:30:00Z,ACCT1,o5,sleeve_a,filled,10,"
        "2026-08-04T08:00:00Z\n",
    ])
    paired, unpaired = st.pair_alpaca_csv(csv, conn)
    assert not paired, paired
    assert len(unpaired) == 3, unpaired
    by_order = {u["order_id"]: u["reason"] for u in unpaired}
    assert by_order["o3"].startswith("no sim leg"), by_order["o3"]
    assert by_order["o4"].startswith("unknown batch"), by_order["o4"]
    assert by_order["o5"].startswith("date mismatch"), by_order["o5"]
    assert "2026-07-07" in by_order["o5"], by_order["o5"]
    print("  [OK  ] unpaired fills carry a reason instead of vanishing")
    print("  [OK  ] the three unpaired causes are told apart, not given one "
          "canned reason")
    conn.close()


def test_write_is_idempotent() -> None:
    conn = _fixture()
    csv = _csv([
        "AAA,buy,10,101.0,2026-07-07T18:20:00Z,ACCT1,o1,sleeve_a,filled,10,"
        "2026-07-07T18:20:00Z\n",
        "BBB,sell,10,198.0,2026-08-04T13:30:00Z,ACCT1,o2,sleeve_a,filled,10,"
        "2026-08-04T08:00:00Z\n",
    ])
    paired, _ = st.pair_alpaca_csv(csv, conn)

    n, skipped = st.write_slippage_log(paired, conn)
    assert (n, skipped) == (2, 0), (n, skipped)
    n2, skipped2 = st.write_slippage_log(paired, conn)
    assert (n2, skipped2) == (0, 2), f"re-run must not duplicate: {(n2, skipped2)}"
    assert conn.execute("SELECT COUNT(*) FROM slippage_log").fetchone()[0] == 2
    print("  [OK  ] write: 2 rows, re-run appends 0 and skips 2")

    # Every row must announce the metric. A row that reads as "slippage" is the
    # failure this whole redefinition exists to prevent.
    n_labelled = conn.execute(
        "SELECT COUNT(*) FROM slippage_log "
        "WHERE note LIKE 'implementation-shortfall%'").fetchone()[0]
    assert n_labelled == 2, n_labelled
    print("  [OK  ] every written row is labelled implementation-shortfall")
    conn.close()


def main() -> int:
    print("Running shortfall-pairing tests (fixture DB only)...")
    test_sign_convention()
    test_pairs_sell_to_exit_not_entry()
    test_unpaired_is_reported_not_dropped()
    test_write_is_idempotent()
    print("\nAll shortfall-pairing tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
