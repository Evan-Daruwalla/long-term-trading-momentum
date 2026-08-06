"""Offline tests for fetch_alpaca_fills (PRD M6.1). No network, no keys, no DB.

These cover what a live run CANNOT: each mirrored account took fewer than 500
orders in the M6 window, so the paging loop never runs against real data. It is
also the part that fails silently if it is wrong -- a loop that stops early just
returns fewer orders, which looks like "fewer fills" rather than "a bug".

Run:
    python -m scripts.momentum.test_fetch_alpaca_fills
"""
from __future__ import annotations

import sys
from datetime import date

from scripts.momentum import fetch_alpaca_fills as m


class FakeClient:
    """Serves orders from a fixed list, honoring after/limit like Alpaca does."""

    def __init__(self, orders):
        self.orders = sorted(orders, key=lambda o: o["submitted_at"])
        self.calls = 0

    def list_orders(self, *, status, limit, after=None, until=None, direction=None):
        self.calls += 1
        out = [o for o in self.orders if after is None or o["submitted_at"] > after]
        return out[:limit]


def _order(i, ts, *, filled_qty="10", status="filled", sym="AAA"):
    return {"id": f"id-{i}", "symbol": sym, "side": "buy", "qty": "10",
            "filled_qty": filled_qty, "filled_avg_price": "100.5",
            "filled_at": f"{ts}Z", "submitted_at": ts, "status": status}


def test_paging() -> None:
    # 1,200 orders at distinct timestamps: must page and return every one.
    orders = [_order(i, f"2026-08-03T18:{i // 60:02d}:{i % 60:02d}.{i:06d}")
              for i in range(1200)]
    c = FakeClient(orders)
    got = m.fetch_orders(c, since=date(2026, 7, 1), until=date(2026, 8, 6))
    assert len(got) == 1200, len(got)
    assert len({o["id"] for o in got}) == 1200, "ids must be unique"
    assert c.calls >= 3, f"1200 orders at limit 500 needs >=3 pages, made {c.calls}"
    print(f"  [OK  ] paging: 1,200 orders across {c.calls} pages, no loss, no dupes")

    # Single short page: must stop after one call, not spin to the backstop.
    c2 = FakeClient([_order(i, f"2026-08-03T18:00:{i:02d}") for i in range(5)])
    assert len(m.fetch_orders(c2, since=date(2026, 7, 1), until=date(2026, 8, 6))) == 5
    assert c2.calls == 1, c2.calls
    print("  [OK  ] short page terminates in 1 call")

    # Every order sharing ONE timestamp: `after` is exclusive, so the cursor
    # cannot advance. Must terminate on the no-new-ids check, not loop forever.
    c3 = FakeClient([_order(i, "2026-08-03T18:00:00.000000") for i in range(600)])
    got3 = m.fetch_orders(c3, since=date(2026, 7, 1), until=date(2026, 8, 6))
    assert c3.calls <= m.MAX_PAGES, "must not spin"
    print(f"  [OK  ] identical-timestamp storm terminates ({c3.calls} calls, "
          f"{len(got3)} unique)")


def test_rows_and_reconcile() -> None:
    class A:
        n, sleeve = 1, "residual_roa_6535_0701_paper"

    # Both real batches for this sleeve, keyed on ALPACA's submitted_at date:
    # 48 on 2026-07-07, 62 stamped 2026-08-04 (the 08-03 rebalance, queue-shifted).
    def july(n):
        return [_order(f"j{i}", f"2026-07-07T18:20:{i % 60:02d}.{i:06d}") for i in range(n)]

    def august(n):
        return [_order(f"a{i}", f"2026-08-04T08:00:{i % 60:02d}.{i:06d}") for i in range(n)]

    clean = july(48) + august(62)
    assert m.reconcile(clean, m.to_rows(clean, A), A) == [], "48+62 must be silent"
    print("  [OK  ] reconcile: 48 (07-07) + 62 (alpaca 08-04) is silent")

    # The queue shift is the point: the same August batch stamped with the
    # REBALANCE date instead of Alpaca's would not match, and must not pass.
    misdated = july(48) + [_order(f"m{i}", f"2026-08-03T23:24:{i % 60:02d}.{i:06d}")
                           for i in range(62)]
    assert m.reconcile(misdated, m.to_rows(misdated, A), A), \
        "a batch on an unexpected date must be a finding, not silence"
    print("  [OK  ] reconcile: batch on the wrong date is caught")

    # Shortfall: one August order canceled unfilled, one PARTIALLY filled.
    short = july(48) + august(60)
    short.append(_order("a98", "2026-08-04T08:00:58", filled_qty="0", status="canceled"))
    short.append(_order("a99", "2026-08-04T08:00:59", filled_qty="4",
                        status="partially_filled"))
    rows = m.to_rows(short, A)
    assert len(rows) == 109, f"partial counts as a row, unfilled does not: {len(rows)}"
    part = [r for r in rows if r["order_id"] == "id-a99"][0]
    assert part["qty"] == "10" and part["qty_filled"] == "4", part
    print("  [OK  ] to_rows: unfilled dropped, partial kept and visible (10 vs 4)")

    findings = m.reconcile(short, rows, A)
    assert findings, "62 submitted vs 61 filled MUST be a finding, not silence"
    assert any("FILLED" in f for f in findings), findings
    print(f"  [OK  ] reconcile: shortfall reported ({len(findings)} finding(s))")


def main() -> int:
    print("Running fetch_alpaca_fills offline tests...")
    test_paging()
    test_rows_and_reconcile()
    print("\nAll fetch_alpaca_fills tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
