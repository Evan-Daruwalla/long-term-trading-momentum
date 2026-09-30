"""Tests for the strict_fill_date fill guard.

Why this guard exists: market_data.last_close_on_or_before carries forward
silently, so on an evening whose publication is still incomplete a rebalance
leg fills against a bar days old. On 2026-08-24 that put 41 exits across 19
sleeves on the 08-21 close, worth $457.00 of proceeds the true bar did not
support. An aggregate coverage floor cannot catch it (08-24 finished at 5,144
closes against a 5,000 floor while five held names were still missing), so the
guard is per-ticker on the fill path.

Record EE item 6 (2026-09-29): the old version of this test kept a hand-written
allowlist of two live callers. It could not fail when a THIRD caller appeared,
and the three LLM-experiment ops modules (which sell and buy real sleeve
positions) were never on it. The allowlist is now DISCOVERY: every python module
the scheduled .bat files run is either named in NON_FILLING (it never fills a
sleeve) or must opt in to strict_fill_date=True. A new, unclassified module
therefore fails here instead of silently reopening the hole.

Covers:
  1. The predicate itself: stale -> skip, same-day -> fill, and OFF by default
     so the seeders/backdater replay history byte-identically.
  2. rebalance() still defaults strict_fill_date=False (the three historical
     callers must not change behaviour).
  3. BOTH legs (sell and buy) route through the predicate, so the guard cannot
     be dropped from one of them by a later edit.
  4. The live ladder actually opts in.
  5. Discovery: every filling module the .bat files run opts in.
  6. market_data.fill_close / StaleBarSkip on a fixture DB.
  7. The three ops modules: a stale bar on EITHER leg raises BEFORE the first
     trade (holding kept, sleeve not stamped), and a stale stop-check skips
     without failing (rc 0). Fixture DB only.

Run:
    python -m scripts.momentum.test_strict_fill_date
"""
from __future__ import annotations

import argparse
import inspect
import re
import tempfile
from datetime import date
from pathlib import Path
from unittest import mock

# Redirect the DB BEFORE anything imports market_data: its import runs
# _ensure_cache_schema() against whichever DB_PATH is set, and every fixture
# test below reads and writes through trading_bot.db.connect(). Nothing in this
# file touches var/trades.db.
from trading_bot import db as dbmod

_TMP = Path(tempfile.mkdtemp(prefix="strictfill_"))
dbmod.close_thread_connection()
dbmod.DB_PATH = _TMP / "trades.db"
dbmod.VAR_DIR = _TMP
dbmod.init_db()

from scripts.momentum import paper_rebalance  # noqa: E402

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


# ---------------------------------------------------------------------------
# Discovery (replaces the hand-written LIVE_SCHEDULED_CALLERS allowlist)
# ---------------------------------------------------------------------------

MOMENTUM_DIR = Path(paper_rebalance.__file__).parent
REPO_ROOT = MOMENTUM_DIR.parents[1]
BATS = ("rebalance.bat", "ladder_rebalance.bat", "daily.bat")

# Only lines that START with the interpreter are commands. `^\s*` already skips
# REM and echo lines (the echoed retry hints in the monthly .bat start with the
# word echo); the explicit prefix check below just says so out loud.
_PY_MODULE_LINE = re.compile(r"^\s*\.venv\\Scripts\\python\.exe\s+-m\s+(\S+)",
                             re.IGNORECASE)

# Modules the .bat files run that NEVER fill a sleeve position at a price.
NON_FILLING = {
    "paper_mtm", "verify_run", "stamp_rebalance_log", "check_month_gate",
    "daily_price_refresh", "check_coverage", "mtm_catchup", "check_anomalies",
    "check_cache_gaps", "ops_stamp", "seed_spy_benchmark", "alpaca_sync",
    "check_held_split_seams", "graphify",
}

# The modules that MUST show up in discovery. If the regex or a .bat edit ever
# makes discovery lose one, the test fails instead of passing vacuously.
LIVE_FILLING = {
    "llm_overlay_ops", "sector_overlay_ops", "llm_cascade_ops",
    "monthly_rebalance", "ladder_forward_rebalance",
}


def discover_modules() -> list[str]:
    """Dotted module names of every `.venv\\Scripts\\python.exe -m <mod>` line
    in the scheduled .bat files, in file order, de-duplicated."""
    found: list[str] = []
    for bat in BATS:
        text = (MOMENTUM_DIR / bat).read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if line.lstrip().lower().startswith(("rem", "echo", "::")):
                continue
            m = _PY_MODULE_LINE.match(line)
            if m and m.group(1) not in found:
                found.append(m.group(1))
    return found


def test_every_live_caller_opts_in() -> None:
    """Audit 2026-09-20 finding 25 + record EE item 6.

    The guard shipped 2026-08-26 opted in exactly ONE of the two live callers;
    the monthly path -- the one that trades the whole roster -- was missed and
    stayed unguarded for 25 days. Then the three LLM ops modules were never on
    the allowlist at all. Discovery makes an unclassified module fail loudly."""
    modules = discover_modules()
    names = {m.rsplit(".", 1)[-1] for m in modules}
    print(f"    discovered {len(modules)} modules: {', '.join(modules)}")

    lost = sorted(LIVE_FILLING - names)
    assert not lost, (
        f"discovery lost live filling module(s) {lost}: the .bat regex or the "
        "files changed, and the check below would pass vacuously")

    filling = [m for m in modules if m.rsplit(".", 1)[-1] not in NON_FILLING]
    problems = []
    for mod in filling:
        src_path = REPO_ROOT.joinpath(*mod.split(".")).with_suffix(".py")
        if not src_path.is_file():
            problems.append(f"{mod}: not in NON_FILLING and no source at {src_path}")
        elif "strict_fill_date=True" not in src_path.read_text(encoding="utf-8"):
            problems.append(f"{mod}: not in NON_FILLING and does not opt in to "
                            "strict_fill_date=True (classify it, or opt it in)")
    assert not problems, (
        "a scheduled module may fill off a stale bar (2026-08-24 incident): "
        + "; ".join(problems))
    print(f"  [OK  ] discovery: {len(modules)} scheduled modules, "
          f"{len(filling)} filling ones all opt in")


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _seed_close(ticker: str, key_date: date, price: float) -> None:
    from trading_bot.execution import market_data
    market_data._ensure_cache_schema()
    with dbmod.connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO price_cache (ticker, kind, key_date, price) "
            "VALUES (?, 'close', ?, ?)", (ticker, key_date.isoformat(), price))


def _sleeve_holding(name: str, ticker: str, bar_date: date) -> None:
    """A fixture sleeve holding 10 shares of `ticker`, whose latest close is the
    `bar_date` bar."""
    from trading_bot.execution import paper_trader
    paper_trader.init(strategy_name=name, starting_cash=100_000.0)
    paper_trader.buy(strategy_name=name, ticker=ticker, qty=10.0,
                     fill_price=100.0, as_of=STALE)
    _seed_close(ticker, bar_date, 20.0)


def _snapshot(name: str):
    from trading_bot.execution import paper_trader
    pf = paper_trader.get(name)
    held = [(p["ticker"], p["qty"]) for p in paper_trader.list_open(name)]
    return (round(pf.cash, 6), held, pf.last_rebalanced_at)


def test_fill_close() -> None:
    from trading_bot.execution import market_data

    _seed_close("FRESH", AS_OF, 10.0)
    _seed_close("STALEX", STALE, 20.0)

    assert market_data.fill_close("FRESH", AS_OF, strict_fill_date=True) == 10.0, \
        "strict must fill on as_of's own bar"
    assert market_data.fill_close("STALEX", AS_OF, strict_fill_date=False) == 20.0, \
        "strict OFF must keep the carry-forward"
    assert market_data.fill_close("NOBAR", AS_OF, strict_fill_date=False) is None

    try:
        market_data.fill_close("STALEX", AS_OF, strict_fill_date=True)
    except market_data.StaleBarSkip as exc:
        assert exc.ticker == "STALEX" and exc.ref_dt == STALE and exc.as_of == AS_OF, \
            (exc.ticker, exc.ref_dt, exc.as_of)
    else:
        raise AssertionError("strict fill on a stale bar must raise StaleBarSkip")

    try:
        market_data.fill_close("NOBAR", AS_OF, strict_fill_date=True)
    except market_data.StaleBarSkip as exc:
        assert exc.ref_dt is None, exc.ref_dt      # a missing bar is not as_of's bar
    else:
        raise AssertionError("strict fill with no bar at all must raise StaleBarSkip")
    print("  [OK  ] fill_close: same-day fills, stale/missing raise StaleBarSkip, "
          "OFF carries forward")


def test_single_position_prechecks_before_trading() -> None:
    """The heart of item 6. _set_single_position SELLS the held name, then buys
    the target. If only the target is stale and it is priced after the sell, the
    sleeve ends in cash. Both names are priced before the first trade."""
    from scripts.momentum import llm_overlay_ops as ops

    kw = dict(entry_score=1.0, as_of=AS_OF, dry_run=False, strict_fill_date=True)

    # A: the HELD name's bar is stale.
    _sleeve_holding("sf_a", "HELDA", STALE)
    _seed_close("NEWA", AS_OF, 30.0)
    before = _snapshot("sf_a")
    try:
        ops._set_single_position(strategy_name="sf_a", target="NEWA", **kw)
    except ops.market_data.StaleBarSkip:
        pass
    else:
        raise AssertionError("stale held bar must raise StaleBarSkip")
    assert _snapshot("sf_a") == before, "stale HELD leg: sleeve changed"

    # B: the held name is fresh, the TARGET is stale. The old order sold first.
    _sleeve_holding("sf_b", "HELDB", AS_OF)
    _seed_close("NEWB", STALE, 30.0)
    before = _snapshot("sf_b")
    try:
        ops._set_single_position(strategy_name="sf_b", target="NEWB", **kw)
    except ops.market_data.StaleBarSkip:
        pass
    else:
        raise AssertionError("stale target bar must raise StaleBarSkip")
    assert _snapshot("sf_b") == before, \
        "stale TARGET leg: the holding was sold before the target was priced"

    # C: already holds the target -> the no-change branch wins, stale or not.
    _sleeve_holding("sf_c", "HELDC", STALE)
    n = ops._set_single_position(strategy_name="sf_c", target="HELDC", **kw)
    assert n == 0 and _snapshot("sf_c")[2] is not None, \
        "no-change branch must stay ahead of the pre-check and still stamp"

    # D: strict OFF (the default) keeps the carry-forward: no raise.
    _sleeve_holding("sf_d", "HELDD", STALE)
    _seed_close("NEWD", STALE, 30.0)
    n = ops._set_single_position(strategy_name="sf_d", target="NEWD",
                                 entry_score=1.0, as_of=AS_OF, dry_run=True)
    assert n == 2, f"strict OFF dry-run should sell+buy on carried bars, got {n}"

    # E: strict ON with two fresh bars proceeds (dry run, so no network sector lookup).
    _sleeve_holding("sf_e", "HELDE", AS_OF)
    _seed_close("NEWE", AS_OF, 30.0)
    n = ops._set_single_position(strategy_name="sf_e", target="NEWE",
                                 entry_score=1.0, as_of=AS_OF, dry_run=True,
                                 strict_fill_date=True)
    assert n == 2, f"strict ON with fresh bars should sell+buy, got {n}"
    print("  [OK  ] _set_single_position: stale held/target raises before any trade; "
          "no-change stamps; OFF carries forward; fresh proceeds")


def test_stop_checks_skip_stale_and_keep_rc0() -> None:
    """A stop is a fill. A stale bar must not stop a position out at a
    carried-forward price, and a skip must not fail the daily run (rc 0)."""
    from scripts.momentum import llm_overlay_ops as ops
    from scripts.momentum import sector_overlay_ops as sec_ops
    from trading_bot.execution import paper_trader
    from trading_bot.strategies import llm_overlay, sector_overlay

    var_dir = Path(tempfile.mkdtemp(prefix="strictfill_var_"))
    stub = lambda ticker, as_of: {"invalidation_level": 50.0}   # noqa: E731

    cases = [
        ("llm_overlay", ops, llm_overlay, llm_overlay.OVERLAY_STRATEGY, "STOPL"),
        ("sector_overlay", sec_ops, sector_overlay,
         sector_overlay.TREATMENT_STRATEGY, "STOPS"),
    ]
    for label, module, strat_mod, strat, ticker in cases:
        _sleeve_holding(strat, ticker, STALE)      # close 20 <= stop 50
        args = argparse.Namespace(settled=False, as_of=AS_OF.isoformat(),
                                  dry_run=False)
        # _ops_status lives in llm_overlay_ops for all three modules.
        with mock.patch.object(strat_mod, "latest_decision_for", stub), \
                mock.patch.object(ops, "VAR_DIR", var_dir, create=True):
            rc = module.cmd_check_invalidation(args)
            assert rc == 0, f"{label}: stale stop-check must keep rc 0, got {rc}"
            assert [p["ticker"] for p in paper_trader.list_open(strat)] == [ticker], \
                f"{label}: a stale bar stopped the position out"
            log_txt = (var_dir / "ops_status.log").read_text(encoding="utf-8")
            assert f"{strat} STALE-SKIP {ticker} ref {STALE.isoformat()}" in log_txt, \
                (label, log_txt)

            _seed_close(ticker, AS_OF, 20.0)       # now the bar is fresh
            rc = module.cmd_check_invalidation(args)
            assert rc == 0, rc
            assert paper_trader.list_open(strat) == [], \
                f"{label}: a fresh bar at/below the stop must still stop out"
    print("  [OK  ] stop checks: stale bar skipped (rc 0, [OPS] line), fresh bar "
          "still stops out")


def test_precheck_precedes_first_trade_everywhere() -> None:
    """Source-order guard for the paths the fixture tests do not drive (the two
    multi-leg sector rebalances), plus 'every rebalance command opts in'."""
    from scripts.momentum import llm_cascade_ops, llm_overlay_ops, sector_overlay_ops

    # Multi-leg: every sell AND buy is priced before the first trade or stamp.
    for label, fn in (("sector_overlay_ops.cmd_rebalance",
                       sector_overlay_ops.cmd_rebalance),
                      ("llm_cascade_ops.cmd_rebalance_sector",
                       llm_cascade_ops.cmd_rebalance_sector)):
        src = inspect.getsource(fn)
        pre = src.index("fill_close(")
        first = min(src.index(m) for m in ("paper_trader.sell(",
                                           "paper_trader.buy(",
                                           "paper_trader.mark_rebalanced("))
        assert pre < first, f"{label}: fill_close pre-check comes after a trade"
        assert "StaleBarSkip" in src and "strict_fill_date=True" in src, label

    # Single-name: pre-check sits after the no-change branch, before the sell.
    src = inspect.getsource(llm_overlay_ops._set_single_position)
    assert src.index("no change") < src.index("fill_close(") \
        < src.index("paper_trader.sell("), "_set_single_position pre-check order"

    # Every rebalance command passes strict_fill_date=True and maps a skip to rc 4.
    for label, fn, n in (("llm_overlay_ops.cmd_rebalance",
                          llm_overlay_ops.cmd_rebalance, 2),
                         ("llm_cascade_ops.cmd_rebalance_stock",
                          llm_cascade_ops.cmd_rebalance_stock, 1)):
        src = inspect.getsource(fn)
        assert src.count("strict_fill_date=True") == n, \
            f"{label}: expected {n} strict_fill_date=True, found " \
            f"{src.count('strict_fill_date=True')}"
        assert src.count("_stale_skip(") == n, f"{label}: StaleBarSkip not mapped"
    assert llm_overlay_ops.STALE_SKIP_RC == 4
    print("  [OK  ] pre-check precedes every trade; rebalance commands opt in "
          "and map a skip to rc 4")


def main() -> int:
    print("test_strict_fill_date")
    tests = [
        test_predicate,
        test_default_is_off,
        test_both_legs_guarded,
        test_ladder_opts_in,
        test_every_live_caller_opts_in,
        test_fill_close,
        test_single_position_prechecks_before_trading,
        test_stop_checks_skip_stale_and_keep_rc0,
        test_precheck_precedes_first_trade_everywhere,
    ]
    failed = []
    for t in tests:
        try:
            t()
        except Exception as exc:                      # report every failure
            failed.append(t.__name__)
            print(f"  [FAIL] {t.__name__}: {type(exc).__name__}: {exc}")
    if failed:
        print(f"FAILED {len(failed)} of {len(tests)}: {', '.join(failed)}")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
