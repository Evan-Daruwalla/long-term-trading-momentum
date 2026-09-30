"""Tests for the trading-day guards + the catch-up date fix (record EE items 4, 5, 6).

The failures this pins (2026-09-29 daily audit, record EE):

  * item 4 -- ladder_forward_rebalance wrote NAV rows on SUB-FLOOR price coverage
    (38 rows on 2026-09-28 that nobody re-marked). The ladder now gates
    compute_nav/write_nav on the same coverage_status() the daily gate and
    mtm_catchup use; below the floor it still rebalances but leaves the NAV to
    mtm_catchup. That only works if mtm_catchup can then mark the day, and
    mark_rebalanced stamps UTC: a 20:31 CDT run stamps the NEXT UTC day, so
    mtm_catchup's [:10] slice read 2026-09-29 for a 2026-09-28 rebalance and
    would never mark it. It now converts the stamp to a LOCAL date.
  * item 5 -- monthly_rebalance had no trading-day guard. On a holiday the
    rebalance.bat still ran the LLM ops legs + alpaca_sync and the MTM phase
    wrote a holiday NAV row for every sleeve. main() now returns 3 on a
    non-trading day BEFORE any import/preload/leg, and the .bat stops on 3.
  * item 6 -- rc 4 from the *_ops modules means STALE-SKIP (a sleeve kept its
    holding). The .bat must NOT treat it as a failure: RC_FAIL would stamp
    PARTIAL and verify_run would then fail every night for the rest of the
    month with no automatic retry.

Everything here runs against a TEMP fixture DB (never var/trades.db) and never
calls main() of the ladder or the monthly dispatcher: helpers + source text only.

Run:
    python -m scripts.momentum.test_trading_day_guards
"""
from __future__ import annotations

import inspect
import sqlite3
import sys
import tempfile
import traceback
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

MOM = Path(__file__).resolve().parent
BAT = MOM / "rebalance.bat"

# Fixture calendar (only key_date/kind/price matter to coverage_status).
BASELINE_DAYS = [date(2026, 9, 8) + timedelta(days=i) for i in range(10)]  # 5,200 each
SETTLED = date(2026, 9, 21)     # 5,100 closes -> at/above the 5,000 hard floor
PENDING = date(2026, 9, 22)     # 4,400 closes -> a trading day, but BELOW the floor
HOLIDAY = date(2026, 9, 23)     # 200 stray closes -> not a trading day
EMPTY = date(2026, 9, 26)       # no rows at all


def _fixture_db() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="tdguard_"))
    path = tmp / "fixture.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE price_cache (ticker TEXT, kind TEXT, key_date TEXT, price REAL)")
    conn.execute("CREATE TABLE paper_portfolio (strategy_name TEXT PRIMARY KEY, "
                 "last_rebalanced_at TEXT)")

    def fill(d: date, n: int) -> None:
        conn.executemany("INSERT INTO price_cache VALUES (?, 'close', ?, 10.0)",
                         ((f"T{i}", d.isoformat()) for i in range(n)))

    for d in BASELINE_DAYS:
        fill(d, 5200)
    fill(SETTLED, 5100)
    fill(PENDING, 4400)
    fill(HOLIDAY, 200)
    conn.commit()
    conn.close()
    return path


def _point_coverage_at(path: Path) -> None:
    """_ro_connect() reads the DB_PATH global of check_coverage at call time."""
    from scripts.momentum import check_coverage
    check_coverage.DB_PATH = path


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


# --------------------------------------------------------------------- ladder
def test_ladder_gate_values() -> None:
    from scripts.momentum import ladder_forward_rebalance as lad
    ok, n, floor = lad._coverage_gate(PENDING)
    assert (ok, n, floor) == (False, 4400, 5000), \
        f"sub-floor day must gate OFF, got {(ok, n, floor)}"
    ok, n, floor = lad._coverage_gate(SETTLED)
    assert (ok, n, floor) == (True, 5100, 5000), \
        f"5,100 closes + a 10-day baseline must gate ON, got {(ok, n, floor)}"
    print("  [OK  ] ladder gate: 4,400 closes -> False, 5,100 closes + baseline -> True")


def test_ladder_write_nav_is_under_cov_ok() -> None:
    from scripts.momentum import ladder_forward_rebalance as lad
    params = inspect.signature(lad._rebalance_sleeves).parameters
    assert "cov_ok" in params, "_rebalance_sleeves must take cov_ok"
    assert params["cov_ok"].default is inspect.Parameter.empty, \
        "cov_ok must be REQUIRED (a default would fail open)"
    body = inspect.getsource(lad._rebalance_sleeves).splitlines()
    gate = next((i for i, l in enumerate(body) if l.strip() == "if cov_ok:"), None)
    assert gate is not None, "no `if cov_ok:` in _rebalance_sleeves"
    for needle in ("paper_mtm.compute_nav(", "paper_mtm.write_nav("):
        idx = [i for i, l in enumerate(body) if needle in l]
        assert len(idx) == 1, f"expected exactly one {needle}, found {len(idx)}"
        assert idx[0] > gate and _indent(body[idx[0]]) > _indent(body[gate]), \
            f"{needle} is not nested under `if cov_ok:`"
    reb = [i for i, l in enumerate(body) if "paper_rebalance.rebalance(" in l]
    assert len(reb) == 1 and reb[0] < gate and _indent(body[reb[0]]) <= _indent(body[gate]), \
        "the rebalance leg must stay UNCONDITIONAL (only the NAV write is gated)"
    src = inspect.getsource(lad)
    assert src.count("paper_mtm.write_nav(") == 1, "a second, ungated write_nav exists"
    print("  [OK  ] write_nav/compute_nav nested under `if cov_ok:`; rebalance leg unconditional")


def test_ladder_main_wires_gate() -> None:
    from scripts.momentum import ladder_forward_rebalance as lad
    body = inspect.getsource(lad.main)
    g = body.find("_coverage_gate(")
    c = body.find("_rebalance_sleeves(")
    assert g != -1, "main() never calls _coverage_gate"
    assert -1 < g < c, "the gate must be computed BEFORE the sleeves are rebalanced"
    call = body[c:body.index(")", c)]
    assert "cov_ok" in call, f"main() does not pass cov_ok: {call!r}"
    print("  [OK  ] ladder main(): gate computed before the sleeve loop and passed in")


# -------------------------------------------------------------------- monthly
def test_trading_day_ok_values() -> None:
    from scripts.momentum import monthly_rebalance as mon
    assert mon.trading_day_ok(HOLIDAY) == (False, 200), mon.trading_day_ok(HOLIDAY)
    assert mon.trading_day_ok(EMPTY) == (False, 0), mon.trading_day_ok(EMPTY)
    # BELOW the coverage floor but a real trading day: the monthly run must go
    # ahead (rebalance.bat: no coverage gate BY DESIGN, ~4,400 of ~5,200 closes).
    assert mon.trading_day_ok(PENDING) == (True, 4400), mon.trading_day_ok(PENDING)
    assert mon.trading_day_ok(SETTLED) == (True, 5100), mon.trading_day_ok(SETTLED)
    print("  [OK  ] trading_day_ok: 200 -> False, 0 -> False, 4,400 -> True, 5,100 -> True")


def test_monthly_guard_precedes_heavy_work() -> None:
    from scripts.momentum import monthly_rebalance as mon
    body = inspect.getsource(mon.main)
    asof = body.index("date.fromisoformat(args.as_of)")
    guard = body.find("trading_day_ok(")
    pre = body.index("preload_caches()")
    imp = body.index("from scripts.momentum import paper_rebalance")
    assert guard != -1, "main() never calls trading_day_ok"
    assert asof < guard < imp < pre, \
        "trading_day_ok must run after --as-of parsing and BEFORE the imports/preload"
    tail = body[guard:imp]
    assert "return 3" in tail, "the non-trading-day branch must return 3 before the imports"
    print("  [OK  ] monthly main(): trading_day_ok after --as-of, before imports/preload, returns 3")


# ---------------------------------------------------------------- mtm_catchup
def test_catchup_uses_local_date_of_stamp() -> None:
    from scripts.momentum import mtm_catchup
    path = _fixture_db()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    inception = date(2026, 5, 1)

    def stamp(name: str, value) -> date:
        conn.execute("INSERT INTO paper_portfolio VALUES (?, ?)", (name, value))
        return mtm_catchup._last_rebalance(conn, name, inception)

    utc = datetime(2026, 9, 29, 1, 31, 38, tzinfo=timezone.utc)
    got = stamp("evening_run", utc.isoformat())          # 20:31 CDT on 09-28
    offset = utc.astimezone().utcoffset()
    assert got == utc.astimezone().date(), f"stamp not converted to a local date: {got}"
    if offset <= timedelta(hours=-2):                    # any US zone
        assert got == date(2026, 9, 28), \
            f"2026-09-29T01:31:38+00:00 is 2026-09-28 local (UTC{offset}); got {got}"
    assert stamp("date_only", "2026-07-06") == date(2026, 7, 6)
    assert stamp("naive_dt", "2026-07-06 18:00:00") == date(2026, 7, 6)
    assert stamp("garbage", "not-a-date") == inception
    assert stamp("null_stamp", None) == inception
    conn.close()
    print(f"  [OK  ] mtm_catchup._last_rebalance: 01:31Z stamp -> {got} local "
          f"(UTC{offset.total_seconds() / 3600:+g}h); date-only/naive unchanged; "
          "garbage/NULL -> inception")


# ---------------------------------------------------------------- rebalance.bat
def _bat_lines() -> list[str]:
    raw = BAT.read_bytes()
    text = raw.decode("ascii")            # raises on ANY non-ASCII byte
    assert raw.count(b"\n") == raw.count(b"\r\n"), "mixed/bare LF line endings in the .bat"
    return text.splitlines()


def _py_legs(lines: list[str]) -> list[int]:
    return [i for i, l in enumerate(lines)
            if l.lstrip().lower().startswith(r".venv\scripts\python.exe")]


def test_bat_stops_on_rc3_before_next_leg() -> None:
    lines = _bat_lines()
    legs = _py_legs(lines)
    m = next(i for i in legs if "-m scripts.momentum.monthly_rebalance" in lines[i])
    n = next(i for i in legs if i > m)
    rc3 = [i for i, l in enumerate(lines) if l.strip() == 'if "%STEP_RC%"=="3" goto not_trading_day']
    assert len(rc3) == 1, f"expected exactly one rc-3 branch, found {len(rc3)}"
    assert m < rc3[0] < n, "the rc-3 branch must sit between the dispatcher and the NEXT python leg"
    assert any(lines[i].strip() == "set STEP_RC=%errorlevel%" for i in range(m + 1, rc3[0])), \
        "rc-3 branch is not preceded by the dispatcher's own `set STEP_RC=%errorlevel%`"
    print("  [OK  ] .bat: rc-3 branch sits right after the dispatcher, before the next python leg")


def test_bat_not_trading_day_block() -> None:
    lines = _bat_lines()
    labels = [i for i, l in enumerate(lines) if l.strip() == ":not_trading_day"]
    assert len(labels) == 1, f"expected one :not_trading_day label, found {len(labels)}"
    L = labels[0]
    prev = next(i for i in range(L - 1, -1, -1) if lines[i].strip())
    assert lines[prev].strip() == "exit /b 0", \
        "`exit /b 0` must come right before :not_trading_day so a normal run never falls into it"
    block = [l for l in lines[L + 1:] if l.strip()]
    assert block and block[-1].strip() == "exit /b 3", "the block must end with `exit /b 3`"
    echoes = [l for l in block if l.strip().lower().startswith("echo")]
    assert len(echoes) >= 3, f"expected >= 3 plain echo lines, found {len(echoes)}"
    for l in echoes:
        assert not any(c in l for c in "<>|&"), f"redirect/pipe char in echo text: {l!r}"
    joined = "\n".join(block)
    for bad in ("RC_FAIL", "stamp_rebalance_log", "python.exe"):
        assert bad not in joined, f"{bad!r} inside the not-trading-day block: it must trade/stamp nothing"
    print("  [OK  ] .bat: `exit /b 0` then :not_trading_day + >=3 plain echoes + `exit /b 3`")


OPS_LEGS = (
    ("llm_overlay_ops rebalance --mode control", "leg_control_done"),
    ("llm_overlay_ops rebalance --mode overlay", "leg_treatment_done"),
    ("sector_overlay_ops rebalance", "leg_sector_done"),
    ("llm_cascade_ops rebalance-stock", "leg_cascade_stock_done"),
    ("llm_cascade_ops rebalance-sector", "leg_cascade_sector_done"),
)


def test_bat_rc4_is_stale_skip_not_failure() -> None:
    lines = _bat_lines()
    legs = _py_legs(lines)
    stamp_i = next(i for i, l in enumerate(lines)
                   if l.lstrip().lower().startswith(r".venv\scripts\python.exe")
                   and "stamp_rebalance_log" in l)
    for needle, label in OPS_LEGS:
        i = next(k for k in legs if needle in lines[k])
        assert lines[i + 1].strip() == "set STEP_RC=%errorlevel%", f"{needle}: no STEP_RC capture"
        assert lines[i + 2].strip() == 'if "%STEP_RC%"=="4" set STALE_SKIP=1', \
            f"{needle}: rc 4 must set STALE_SKIP=1, got {lines[i + 2]!r}"
        assert lines[i + 3].strip() == f'if "%STEP_RC%"=="4" goto {label}', \
            f"{needle}: rc 4 must skip the failure branch, got {lines[i + 3]!r}"
        assert lines[i + 4].lstrip().startswith('if not "%STEP_RC%"=="0"'), \
            f"{needle}: the existing nonzero branch must remain for every other rc"
        lab = [k for k, l in enumerate(lines) if l.strip() == f":{label}"]
        assert len(lab) == 1 and lab[0] > i + 4, f"{needle}: label :{label} missing or misplaced"
        nxt = next((k for k in legs if k > i), 10 ** 9)
        assert lab[0] < nxt, f"{needle}: label :{label} lies beyond the next python leg"
        assert "RC_FAIL" not in "\n".join(lines[i + 2:i + 4]), f"{needle}: rc 4 must not set RC_FAIL"
    init = [k for k, l in enumerate(lines) if l.strip() == "set STALE_SKIP=0"]
    first_ops = min(next(k for k in legs if n in lines[k]) for n, _ in OPS_LEGS)
    assert init and init[0] < first_ops, "STALE_SKIP must be initialised before the first ops leg"
    warn = [k for k, l in enumerate(lines)
            if l.strip().startswith('if "%STALE_SKIP%"=="1" echo STALE-SKIP')]
    assert len(warn) == 1 and warn[0] < stamp_i, \
        "the STALE-SKIP echo must be a single-line `if` placed before the stamp"
    assert warn[0] > max(next(k for k in legs if n in lines[k]) for n, _ in OPS_LEGS), \
        "the STALE-SKIP echo must come after the last ops leg"
    print("  [OK  ] .bat: rc 4 on all 5 ops legs sets STALE_SKIP without RC_FAIL; echo before the stamp")


TESTS = (
    test_ladder_gate_values,
    test_ladder_write_nav_is_under_cov_ok,
    test_ladder_main_wires_gate,
    test_trading_day_ok_values,
    test_monthly_guard_precedes_heavy_work,
    test_catchup_uses_local_date_of_stamp,
    test_bat_stops_on_rc3_before_next_leg,
    test_bat_not_trading_day_block,
    test_bat_rc4_is_stale_skip_not_failure,
)


def main() -> int:
    print("test_trading_day_guards (fixture DB only; no main() of any trading module)")
    _point_coverage_at(_fixture_db())
    failed = 0
    for t in TESTS:
        try:
            t()
        except Exception as e:                      # AssertionError, AttributeError, ...
            failed += 1
            print(f"  [FAIL] {t.__name__}: {type(e).__name__}: {e}")
            if not isinstance(e, (AssertionError, AttributeError, StopIteration)):
                traceback.print_exc()
    print(f"\n{len(TESTS) - failed} passed, {failed} failed, {len(TESTS)} total")
    print("ALL PASS" if not failed else "FAILED")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
