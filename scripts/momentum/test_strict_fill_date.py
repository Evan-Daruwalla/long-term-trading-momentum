"""Tests for the strict_fill_date fill guard. Source + pure logic only; no DB.

Why this guard exists: market_data.last_close_on_or_before carries forward
silently, so on an evening whose publication is still incomplete a rebalance
leg fills against a bar days old. On 2026-08-24 that put 41 exits across 19
sleeves on the 08-21 close, worth $457.00 of proceeds the true bar did not
support. An aggregate coverage floor cannot catch it (08-24 finished at 5,144
closes against a 5,000 floor while five held names were still missing), so the
guard is per-ticker on the fill path.

Covers:
  1. The predicate itself: stale -> skip, same-day -> fill, and OFF by default
     so the seeders/backdater replay history byte-identically.
  2. rebalance() still defaults strict_fill_date=False (the three historical
     callers must not change behaviour).
  3. BOTH legs (sell and buy) route through the predicate, so the guard cannot
     be dropped from one of them by a later edit.
  4. The live ladder actually opts in.

Run:
    python -m scripts.momentum.test_strict_fill_date
"""
from __future__ import annotations

import inspect
from datetime import date
from pathlib import Path

from scripts.momentum import paper_rebalance

AS_OF = date(2026, 8, 24)
STALE = date(2026, 8, 21)          # the real 08-24 carry-forward bar


def test_predicate() -> None:
    f = paper_rebalance._stale_fill
    assert f(STALE, AS_OF, True) is True, "stale bar must be skipped when strict"
    assert f(AS_OF, AS_OF, True) is False, "as_of's own bar must fill when strict"
    assert f(STALE, AS_OF, False) is False, "strict OFF must preserve carry-forward"
    assert f(AS_OF, AS_OF, False) is False
    assert f(None, AS_OF, True) is True, "missing ref date is not as_of's bar"
    print("  [OK  ] predicate: stale->skip, same-day->fill, OFF->carry-forward")


def test_default_is_off() -> None:
    p = inspect.signature(paper_rebalance.rebalance).parameters["strict_fill_date"]
    assert p.default is False, f"default must stay False, got {p.default!r}"
    print("  [OK  ] rebalance(strict_fill_date=) defaults False - seeders unchanged")


def test_both_legs_guarded() -> None:
    src = Path(paper_rebalance.__file__).read_text(encoding="utf-8")
    uses = src.count("_stale_fill(ref_dt, as_of, strict_fill_date)")
    assert uses == 2, f"expected the guard on both sell and buy legs, found {uses}"
    sell_i = src.index("Skip sell %s: stale bar")
    buy_i = src.index("Skip buy %s: stale bar")
    assert sell_i < buy_i, "sanity: sell leg precedes buy leg"
    print("  [OK  ] both legs (sell + buy) route through the guard")


def test_ladder_opts_in() -> None:
    ladder = Path(paper_rebalance.__file__).with_name("ladder_forward_rebalance.py")
    src = ladder.read_text(encoding="utf-8")
    assert "strict_fill_date=True" in src, \
        "the live ladder must opt in to the guard"
    print("  [OK  ] ladder_forward_rebalance opts in (strict_fill_date=True)")


# Every module that rebalances a LIVE sleeve on a schedule. The replay callers
# (seed_residual_cadence_ladder, seed_residual_wsweep, backdate_sleeves) are
# deliberately absent: they must keep filling off carried-forward bars to
# reproduce history byte-identically, which is what test_default_is_off guards.
LIVE_SCHEDULED_CALLERS = ("ladder_forward_rebalance.py", "monthly_rebalance.py")


def test_every_live_caller_opts_in() -> None:
    """Audit 2026-09-20, finding 25.

    The guard shipped 2026-08-26 opted in exactly ONE of the two live callers.
    The monthly path -- the one that trades the whole roster -- was missed and
    stayed unguarded for 25 days. A per-caller assertion is the only thing that
    makes a third live caller fail loudly instead of silently reopening it."""
    here = Path(paper_rebalance.__file__).parent
    missing = [
        name for name in LIVE_SCHEDULED_CALLERS
        if "strict_fill_date=True" not in (here / name).read_text(encoding="utf-8")
    ]
    assert not missing, (
        f"live scheduled caller(s) not opted in to strict_fill_date: {missing}. "
        "A live rebalance may fill off a stale bar (see the 2026-08-24 incident)."
    )
    print(f"  [OK  ] all {len(LIVE_SCHEDULED_CALLERS)} live scheduled callers opt in")


def main() -> int:
    print("test_strict_fill_date")
    test_predicate()
    test_default_is_off()
    test_both_legs_guarded()
    test_ladder_opts_in()
    test_every_live_caller_opts_in()
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
