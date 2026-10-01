"""Fixture test for scripts.data_audit.repair_split_mixed_basis (record EG option 1).

Builds throwaway temp DBs (dbmod.init_db + market_data._ensure_cache_schema, then
plain sqlite3 inserts) and drives the tool through `tool.main(argv)` with `--db`
pointing at the temp file. It NEVER opens var/trades.db: dbmod.DB_PATH is
redirected BEFORE market_data is imported (that import runs _ensure_cache_schema
at import time against whatever DB_PATH is current).

Fixture: ticker XYZ, N=2, already-adjusted date A=2026-06-01 < cutover
C=2026-06-05 < ex-date D=2026-07-01. The initial price_cache is MIXED-BASIS like
the real MLI one: rows before C are pre-split except A, which (like every row
from C on) is on the post-split basis. The three split-like seams of the real
case are reproduced (05-29->06-01, 06-01->06-02, 06-04->06-05).

Sleeves:
  seeded  initialized AFTER D (replay-seeded): its stored marks for the
          post-basis pre-D dates (A and C..06-30) used the rewritten cache, so
          those NAV rows MUST change.
  live    initialized 05-01, marked in real time on the pre basis before D:
          its pre-D NAV rows must NOT change. Carries a deliberate $7.50
          cash-vs-ledger gap that must survive the repair untouched.
  mid     initialized 06-20 (before D, so NOT seeded after the rewrite): pre-D
          rows must NOT change either (exercises the date(init) >= ex clause).
  clean   only post lots + another ticker: nothing may change.
Lots: pre->open, pre->post exiting >= D, pre->post exiting between C and D (in
the seeded sleeve), pre->pre, post->post, post->open, and a different ticker.

The ground truth for the NAV rows is derived from first principles (post-repair
lots replayed, every XYZ position marked at nom(d)/2), NOT from the tool's rule:
after the repair EVERY paper_nav row of EVERY sleeve must equal that truth.

Run:
    .venv\\Scripts\\python.exe -m scripts.data_audit.test_repair_split_mixed_basis
"""
from __future__ import annotations

import contextlib
import io
import shutil
import sqlite3
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

from trading_bot import db as dbmod
from scripts.data_audit import repair_split_mixed_basis as tool
from scripts.data_audit.check_held_split_seams import near_split_ratio

T = "XYZ"
OTHER = "OTH"
OTHER_PX = 131.0
N = 2.0
A = "2026-06-01"       # already adjusted (post basis) although before the cutover
C = "2026-06-05"       # basis cutover: first row of the contiguous post-basis run
D = "2026-07-01"       # ex-date
START = 10_000.0
TOL = 1e-9

SPLITS_BEFORE = '[["2026-09-01", 1.5], ["2019-01-15", 3.0]]'            # unsorted on purpose
SPLITS_AFTER = '[["2019-01-15", 3.0], ["2026-07-01", 2.0], ["2026-09-01", 1.5]]'
DIVS_BEFORE = '[["2026-03-10", 0.4], ["2026-06-10", 0.5], ["2026-07-10", 0.25]]'
DIVS_AFTER = '[["2026-03-10", 0.2], ["2026-06-10", 0.25], ["2026-07-10", 0.25]]'
OLD_DAYS = ["2019-01-02", "2020-03-16"]


def _weekdays(start: date, end: date) -> list[str]:
    out, d = [], start
    while d <= end:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


DAYS = _weekdays(date(2026, 5, 18), date(2026, 7, 10))
K = {d: i for i, d in enumerate(DAYS)}


def nom(d: str) -> float:
    """The 'true' pre-split-basis price level of day d."""
    return 120.0 + 0.25 * K[d]


def cached_post(d: str) -> bool:
    return d == A or d >= C


def cache_close(d: str) -> float:
    return nom(d) / 2 if cached_post(d) else nom(d)


def true_px(d: str) -> float:
    return nom(d) / 2


def pre_fill(d: str) -> float:
    return round(nom(d) * 1.001, 2)


def post_fill(d: str) -> float:
    return round(nom(d) / 2 * 1.001, 4)


class TLot:
    def __init__(self, id, sleeve, kind, qty, e_date, x_date=None, ticker=T):
        self.id, self.sleeve, self.kind, self.qty = id, sleeve, kind, qty
        self.e_date, self.x_date, self.ticker = e_date, x_date, ticker
        if ticker == OTHER:
            self.e_px = 130.0
        elif kind.startswith("pre"):
            self.e_px = pre_fill(e_date)
        else:
            self.e_px = post_fill(e_date)
        if x_date is None:
            self.x_px = None
        elif kind in ("pre_post", "post_post"):
            self.x_px = post_fill(x_date)
        else:                                  # pre_pre
            self.x_px = pre_fill(x_date)

    @property
    def is_pre(self) -> bool:
        return self.ticker == T and self.kind.startswith("pre")

    @property
    def entry_value(self) -> float:
        return self.qty * self.e_px

    @property
    def exit_value_old(self):
        return None if self.x_px is None else self.x_px * self.qty

    @property
    def qty_new(self) -> float:
        return self.qty * N if self.is_pre else self.qty

    @property
    def exit_value_new(self):
        if self.x_px is None:
            return None
        return self.qty_new * self.x_px if self.kind == "pre_post" else self.exit_value_old


LOTS = [
    TLot(1, "seeded", "pre_open", 10, "2026-05-20"),
    TLot(2, "seeded", "pre_post", 5, "2026-05-26", "2026-06-12"),   # exits between C and D
    TLot(3, "seeded", "pre_post", 8, "2026-05-27", "2026-07-08"),   # exits >= D
    TLot(4, "seeded", "post_post", 20, "2026-06-08", "2026-06-22"),
    TLot(5, "seeded", "pre_pre", 4, "2026-05-19", "2026-06-03"),
    TLot(6, "seeded", "post_open", 3, "2026-07-06"),
    TLot(7, "seeded", "other_open", 3, "2026-05-20", ticker=OTHER),
    TLot(11, "live", "pre_open", 6, "2026-05-21"),
    TLot(12, "live", "pre_post", 7, "2026-05-28", "2026-07-02"),
    TLot(13, "live", "pre_pre", 5, "2026-05-22", "2026-06-16"),
    TLot(14, "live", "post_open", 4, "2026-07-03"),
    TLot(21, "mid", "pre_open", 4, "2026-06-22"),
    TLot(31, "clean", "post_open", 2, "2026-07-06"),
    TLot(32, "clean", "other_open", 10, "2026-05-20", ticker=OTHER),
]

SLEEVES = {
    "seeded": dict(init="2026-07-08T15:30:00+00:00", nav_start="2026-05-18", gap=0.0, replayed=True),
    "live": dict(init="2026-05-01T14:00:00+00:00", nav_start="2026-05-18", gap=7.5, replayed=False),
    "mid": dict(init="2026-06-20T14:00:00+00:00", nav_start="2026-06-22", gap=0.0, replayed=False),
    "clean": dict(init="2026-05-01T14:00:00+00:00", nav_start="2026-05-18", gap=0.0, replayed=False),
}
AFFECTED = ["live", "mid", "seeded"]


def stored_px(sleeve: str, d: str, ticker: str) -> float:
    """The mark the pipeline stored: replayed sleeves read the REWRITTEN cache,
    live-marked ones read the pre basis until the ex-date."""
    if ticker == OTHER:
        return OTHER_PX
    if SLEEVES[sleeve]["replayed"]:
        return cache_close(d)
    return nom(d) if d < D else cache_close(d)


def replay(sleeve: str, d: str, new: bool) -> dict:
    """cash/positions_value/total_nav/n_open at d. new=False: as originally
    stored; new=True: first-principles truth after the repair."""
    cash = START + SLEEVES[sleeve]["gap"]
    pv, n = 0.0, 0
    for lt in LOTS:
        if lt.sleeve != sleeve or lt.e_date > d:
            continue
        cash -= lt.entry_value
        if lt.x_date is not None and lt.x_date <= d:
            cash += lt.exit_value_new if new else lt.exit_value_old
        else:
            n += 1
            if new:
                px = true_px(d) if lt.ticker == T else OTHER_PX
                pv += lt.qty_new * px
            else:
                pv += lt.qty * stored_px(sleeve, d, lt.ticker)
    return {"cash": cash, "positions_value": pv, "total_nav": cash + pv, "n_open": n}


def populate(con: sqlite3.Connection) -> None:
    pc = []
    for d in DAYS:
        k, post = K[d], cached_post(d)
        mult = 2.0 if post else 1.0
        pc += [(T, "close", d, cache_close(d)),
               (T, "next_open", d, round(nom(d) * 1.002, 6) / mult),
               (T, "volume", d, (1000.0 + k) * mult),
               (T, "next_open_vol", d, (600.0 + k) * mult),
               (T, "next_open_range", d, 0.0125 + 0.0001 * k),
               (T, "above_ma_50", d, float(k % 2)),
               (T, "atr_pct_20", d, 2.5),
               (OTHER, "close", d, OTHER_PX),
               (OTHER, "volume", d, 5000.0 + k)]
    for d in OLD_DAYS:                                    # deep history, pre basis
        pc += [(T, "close", d, 100.0), (T, "volume", d, 777.0), (T, "next_open", d, 100.5)]
    pc += [(T, "close", "2026-05-23", None), (T, "volume", "2026-05-23", None),
           (T, "next_open", "2026-05-23", None), (T, "next_open_vol", "2026-05-23", None)]
    pc += [(T, "splits_json", "all", SPLITS_BEFORE), (T, "dividends_json", "all", DIVS_BEFORE),
           (OTHER, "splits_json", "all", "[]"), (OTHER, "dividends_json", "all", "[[\"2026-06-10\", 1.0]]")]
    con.executemany("INSERT INTO price_cache (ticker, kind, key_date, price) VALUES (?,?,?,?)", pc)

    for sl, spec in SLEEVES.items():
        mine = [lt for lt in LOTS if lt.sleeve == sl]
        cash = START + spec["gap"] - sum(lt.entry_value for lt in mine) \
            + sum(lt.exit_value_old for lt in mine if lt.x_px is not None)
        con.execute("INSERT INTO paper_portfolio (strategy_name, starting_cash, cash, "
                    "initialized_at, last_rebalanced_at) VALUES (?,?,?,?,?)",
                    (sl, START, cash, spec["init"], "2026-07-01T22:03:00+00:00"))
    for lt in LOTS:
        closed = lt.x_px is not None
        con.execute(
            "INSERT INTO paper_positions (id, strategy_name, ticker, status, qty, entry_price, "
            "entry_value, entry_date, entry_score, sector, exit_price, exit_value, exit_date, "
            "exit_reason, realized_pnl, realized_pnl_pct) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (lt.id, lt.sleeve, lt.ticker, "closed" if closed else "open", lt.qty, lt.e_px,
             lt.entry_value, lt.e_date, 1.5, "Industrials",
             lt.x_px, lt.exit_value_old, lt.x_date, "rebalance" if closed else None,
             (lt.x_px - lt.e_px) * lt.qty if closed else None,
             (lt.x_px / lt.e_px - 1.0) * 100.0 if closed else None))
    for sl, spec in SLEEVES.items():
        for d in DAYS:
            if d < spec["nav_start"]:
                continue
            r = replay(sl, d, new=False)
            con.execute("INSERT INTO paper_nav (strategy_name, nav_date, cash, positions_value, "
                        "total_nav, n_open_positions) VALUES (?,?,?,?,?,?)",
                        (sl, d, r["cash"], r["positions_value"], r["total_nav"], r["n_open"]))


def make_fixture(tmp: Path, tag: str, mutate=None) -> Path:
    path = tmp / f"{tag}.db"
    dbmod.close_thread_connection()
    dbmod.DB_PATH = path          # redirect BEFORE market_data is imported (see module doc)
    dbmod.VAR_DIR = tmp
    dbmod.init_db()
    from trading_bot.execution import market_data
    market_data._ensure_cache_schema()
    dbmod.close_thread_connection()
    con = sqlite3.connect(path)
    populate(con)
    if mutate is not None:
        mutate(con)
    con.commit()
    con.close()
    return path


def ro(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"{Path(path).as_uri()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def snapshot(path: Path) -> dict:
    con = ro(path)
    try:
        names = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {n: [tuple(r) for r in con.execute(f'SELECT * FROM "{n}" ORDER BY rowid')]
                for n in names}
    finally:
        con.close()


def query(path: Path, sql: str, *a) -> list[sqlite3.Row]:
    con = ro(path)
    try:
        return con.execute(sql, a).fetchall()
    finally:
        con.close()


def base_argv(path: Path, cutover: str = C, adjusted: str = A, ratio: str = "2") -> list[str]:
    return ["--ticker", T, "--ratio", ratio, "--ex-date", D, "--basis-cutover", cutover,
            "--already-adjusted", adjusted, "--db", str(path)]


def exec_argv(path: Path, **kw) -> list[str]:
    return base_argv(path, **kw) + ["--execute", "--reason", "fixture test"]


def run(argv: list[str]) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = tool.main(argv)
        except SystemExit as e:
            rc = e.code if isinstance(e.code, int) else 1
    return rc, out.getvalue() + err.getvalue()


def gap(path: Path, sleeve: str) -> float:
    r = query(path, "SELECT starting_cash, cash FROM paper_portfolio WHERE strategy_name=?", sleeve)[0]
    e, x = query(path, "SELECT COALESCE(SUM(entry_value),0), COALESCE(SUM(exit_value),0) "
                       "FROM paper_positions WHERE strategy_name=?", sleeve)[0]
    return r["cash"] - (r["starting_cash"] - e + x)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="pm_splitrepair_"))
    failures: list[str] = []
    passed: list[str] = []

    def check(cond, msg):
        print(f"  [{'OK  ' if cond else 'FAIL'}] {msg}")
        (passed if cond else failures).append(msg)

    def close(a, b, tol=TOL):
        return a is not None and b is not None and abs(a - b) <= tol

    print("Running repair_split_mixed_basis fixture tests...")

    # ---- 0. the fixture really is mixed-basis (3 seams, like the real MLI case) ----
    print("fixture sanity")
    base = make_fixture(tmp, "base")
    series = query(base, "SELECT key_date, price FROM price_cache WHERE ticker=? AND kind='close' "
                         "AND price IS NOT NULL ORDER BY key_date", T)
    seams = [(series[i - 1]["key_date"], series[i]["key_date"])
             for i in range(1, len(series))
             if near_split_ratio(series[i]["price"] / series[i - 1]["price"])]
    check(seams == [("2026-05-29", "2026-06-01"), ("2026-06-01", "2026-06-02"),
                    ("2026-06-04", "2026-06-05")],
          f"pre-repair fixture has exactly the 3 MLI-style seams: {seams}")
    snap0 = snapshot(base)
    orig_lots = {r["id"]: dict(r) for r in query(base, "SELECT * FROM paper_positions")}
    orig_pf = {r["strategy_name"]: dict(r) for r in query(base, "SELECT * FROM paper_portfolio")}
    orig_nav = {(r["strategy_name"], r["nav_date"]): dict(r)
                for r in query(base, "SELECT * FROM paper_nav")}
    orig_pc = {(r["ticker"], r["kind"], r["key_date"]): r["price"]
               for r in query(base, "SELECT * FROM price_cache")}
    gaps0 = {s: gap(base, s) for s in SLEEVES}
    check(close(gaps0["live"], 7.5, 1e-6) and all(abs(gaps0[s]) < 1e-6 for s in ("seeded", "mid", "clean")),
          f"fixture cash-vs-ledger gaps: {gaps0}")

    # ---- 1. refusals and usage errors write nothing ----
    print("refusals")
    for label, cut in (("a post-basis date (06-10)", "2026-06-10"), ("a pre-basis date (06-04)", "2026-06-04")):
        rc, out = run(exec_argv(base, cutover=cut))
        check(rc == 1 and "[P1]" in out, f"wrong cutover {label} is refused with P1 (rc={rc})")
        check(snapshot(base) == snap0, "  ...and the DB is byte-for-byte unchanged")
    rc, out = run(base_argv(base) + ["--execute"])
    check(rc == 2, f"--execute without --reason is a usage error (rc={rc})")
    rc, out = run(base_argv(base, ratio="1"))
    check(rc == 2, f"--ratio 1 is a usage error (rc={rc})")
    rc, out = run(base_argv(base, cutover="2026-07-02"))
    check(rc == 2, f"cutover after the ex-date is a usage error (rc={rc})")
    rc, out = run(base_argv(tmp / "missing.db"))
    check(rc == 2, f"a missing --db is a usage error (rc={rc})")
    check(snapshot(base) == snap0, "usage errors wrote nothing")

    for tag, mut, code in (
            ("p3_near", lambda c: c.execute("UPDATE paper_positions SET entry_price=95.0 WHERE id=1"), "[P3]"),
            ("p3_postpre", lambda c: c.execute("UPDATE paper_positions SET exit_price=123.0 WHERE id=4"), "[P3]"),
            ("p4", lambda c: c.execute("UPDATE paper_positions SET realized_pnl=realized_pnl+1.0 WHERE id=2"), "[P4]"),
            ("p5", lambda c: c.execute("INSERT INTO price_cache VALUES (?,?,?,?)",
                                       (T, "mystery", "2026-06-10", 1.0)), "[P5]"),
            ("c2", lambda c: c.execute("UPDATE price_cache SET price='not json' "
                                       "WHERE ticker=? AND kind='splits_json'", (T,)), "[C2]")):
        p = make_fixture(tmp, tag, mut)
        s = snapshot(p)
        rc, out = run(exec_argv(p))
        check(rc == 1 and code in out and snapshot(p) == s,
              f"{code} refusal ({tag}): rc={rc}, DB unchanged")

    # ---- 2. the dry run writes nothing and prints the summary ----
    print("dry run")
    rc, out = run(base_argv(base))
    check(rc == 0, f"dry run exits 0 (rc={rc})")
    check(snapshot(base) == snap0, "dry run leaves the DB unchanged")
    cash_total = sum(lt.exit_value_new - lt.exit_value_old for lt in LOTS if lt.kind == "pre_post")
    n_nav = 0
    for sl in AFFECTED:
        for d in DAYS:
            if d < SLEEVES[sl]["nav_start"]:
                continue
            o, t = replay(sl, d, False), replay(sl, d, True)
            if abs(t["total_nav"] - o["total_nav"]) > TOL or abs(t["cash"] - o["cash"]) > TOL:
                n_nav += 1
    check("DRY RUN" in out, "summary says DRY RUN")
    check("pre->open=3" in out and "pre->post=3" in out and "pre->pre=2" in out
          and "post-untouched=4" in out, "summary lot counts 3 / 3 / 2 / 4")
    check("sleeves affected=3" in out, "summary: 3 affected sleeves")
    check(f"{cash_total:+.4f}" in out, f"summary prints the cash delta {cash_total:+.4f}")
    check(f"NAV rows restated={n_nav}" in out, f"summary prints NAV rows restated={n_nav}")

    # ---- 3. the execute path ----
    print("execute")
    rc, out = run(exec_argv(base))
    check(rc == 0, f"execute exits 0 (rc={rc})")
    if rc != 0:
        print(out)
    check("EXECUTED" in out, "summary says EXECUTED")

    # price_cache: every row exact
    new_pc = {(r["ticker"], r["kind"], r["key_date"]): r["price"]
              for r in query(base, "SELECT * FROM price_cache")}
    check(set(new_pc) == set(orig_pc), "price_cache: no row added or removed")
    bad = []
    for key, old in orig_pc.items():
        tk, kind, kd = key
        if tk != T:
            exp = old
        elif kind in ("close", "next_open") and old is not None and kd < C and kd != A:
            exp = old / N
        elif kind in ("volume", "next_open_vol") and old is not None and kd < C and kd != A:
            exp = old * N
        elif kind == "splits_json":
            exp = SPLITS_AFTER
        elif kind == "dividends_json":
            exp = DIVS_AFTER
        else:
            exp = old
        if new_pc[key] != exp:
            bad.append((key, old, new_pc[key], exp))
    check(not bad, f"price_cache: all {len(orig_pc)} rows exactly as specified {bad[:2]}")
    check(all(new_pc[(T, k, "2026-05-23")] is None for k in ("close", "volume", "next_open", "next_open_vol")),
          "price_cache: NULL rows stay NULL")
    check(all(new_pc[(T, "close", d)] == true_px(d) for d in DAYS),
          "price_cache: every XYZ close now equals the true post-basis level nom(d)/2")
    check(new_pc[(T, "close", "2019-01-02")] == 50.0 and new_pc[(T, "volume", "2019-01-02")] == 1554.0,
          "price_cache: deep history halved / doubled")
    ser2 = query(base, "SELECT key_date, price FROM price_cache WHERE ticker=? AND kind='close' "
                       "AND price IS NOT NULL ORDER BY key_date", T)
    seams2 = [(ser2[i - 1]["key_date"], ser2[i]["key_date"]) for i in range(1, len(ser2))
              if near_split_ratio(ser2[i]["price"] / ser2[i - 1]["price"])]
    check(not seams2, f"full-history seam scan after the repair: 0 split-like seams {seams2}")

    # lots: every column exact
    new_lots = {r["id"]: dict(r) for r in query(base, "SELECT * FROM paper_positions")}
    lot_bad = []
    for lt in LOTS:
        exp = dict(orig_lots[lt.id])
        if lt.is_pre:
            exp["qty"] = lt.qty * N
            exp["entry_price"] = lt.e_px / N
            if lt.kind == "pre_post":
                exp["exit_value"] = exp["qty"] * lt.x_px
                exp["realized_pnl"] = (lt.x_px - exp["entry_price"]) * exp["qty"]
                exp["realized_pnl_pct"] = (lt.x_px / exp["entry_price"] - 1.0) * 100.0
            if lt.kind == "pre_pre":
                exp["exit_price"] = lt.x_px / N
        got = new_lots[lt.id]
        for col, e in exp.items():
            g = got[col]
            ok = (g == e) if not isinstance(e, float) else close(g, e)
            if not ok:
                lot_bad.append((lt.id, col, g, e))
        if lt.is_pre and not (got["qty"] == lt.qty * N and got["entry_price"] == lt.e_px / N):
            lot_bad.append((lt.id, "qty/entry_price exact", got["qty"], got["entry_price"]))
    check(not lot_bad, f"paper_positions: every column of all {len(LOTS)} lots as specified {lot_bad[:3]}")
    check(all(close(new_lots[lt.id]["entry_value"], lt.entry_value, 0) for lt in LOTS),
          "paper_positions: entry_value never touched")
    check(all(close(new_lots[lt.id]["qty"] * new_lots[lt.id]["entry_price"], lt.entry_value, 1e-9)
              for lt in LOTS if lt.is_pre), "qty_new * entry_price_new == entry_value for pre lots")
    for lt in LOTS:
        if lt.kind == "pre_post":
            g = new_lots[lt.id]
            check(close(g["realized_pnl"], (g["exit_price"] - g["entry_price"]) * g["qty"])
                  and close(g["exit_value"], g["exit_price"] * g["qty"]),
                  f"lot {lt.id} (pre->post): P&L formula holds on the restated row")

    # cash: per sleeve, exactly the exit-value delta; ledger gap unchanged
    new_pf = {r["strategy_name"]: dict(r) for r in query(base, "SELECT * FROM paper_portfolio")}
    for sl in SLEEVES:
        delta = sum(lt.exit_value_new - lt.exit_value_old for lt in LOTS
                    if lt.sleeve == sl and lt.kind == "pre_post")
        check(close(new_pf[sl]["cash"], orig_pf[sl]["cash"] + delta),
              f"cash {sl}: {orig_pf[sl]['cash']:.4f} + {delta:.4f} -> {new_pf[sl]['cash']:.4f}")
        check(abs(gap(base, sl) - gaps0[sl]) <= 0.005, f"ledger gap {sl} unchanged ({gap(base, sl):.4f})")
        check(all(new_pf[sl][c] == orig_pf[sl][c] for c in
                  ("starting_cash", "initialized_at", "last_rebalanced_at")),
              f"paper_portfolio {sl}: other columns untouched")

    # NAV rows: every row of every sleeve equals the first-principles truth
    new_nav = {(r["strategy_name"], r["nav_date"]): dict(r)
               for r in query(base, "SELECT * FROM paper_nav")}
    nav_bad, changed = [], set()
    for (sl, d), old in orig_nav.items():
        tru = replay(sl, d, new=True)
        got = new_nav[(sl, d)]
        for col, tv in (("cash", tru["cash"]), ("positions_value", tru["positions_value"]),
                        ("total_nav", tru["total_nav"])):
            if not close(got[col], tv):
                nav_bad.append((sl, d, col, got[col], tv))
        if got["n_open_positions"] != old["n_open_positions"]:
            nav_bad.append((sl, d, "n_open_positions"))
        if any(abs(got[c] - old[c]) > TOL for c in ("cash", "positions_value", "total_nav")):
            changed.add((sl, d))
    check(set(new_nav) == set(orig_nav), "paper_nav: no row added or removed")
    check(not nav_bad, f"paper_nav: all {len(orig_nav)} rows equal the first-principles truth {nav_bad[:3]}")
    by_sleeve = {s: sorted(d for (sl, d) in changed if sl == s) for s in SLEEVES}
    check(by_sleeve["clean"] == [], "paper_nav: clean sleeve untouched")
    check(all(d >= D for d in by_sleeve["live"]) and by_sleeve["live"],
          f"live sleeve: no pre-D row changed (first changed {by_sleeve['live'][:1]})")
    check(all(d >= D for d in by_sleeve["mid"]) and by_sleeve["mid"],
          f"mid sleeve (init before D): no pre-D row changed (first changed {by_sleeve['mid'][:1]})")
    must = {A, "2026-06-05", "2026-06-10", "2026-06-30"}
    must_not = {"2026-05-20", "2026-06-02", "2026-06-03", "2026-06-04"}
    check(must <= set(by_sleeve["seeded"]) and not (must_not & set(by_sleeve["seeded"])),
          "seeded sleeve: post-basis pre-D rows (06-01, 06-05, 06-10, 06-30) changed; "
          "pre-basis rows (05-20, 06-02..06-04) did not")
    # the A-row (06-01) of the seeded sleeve moved by exactly the open pre lots' qty_old * close(A)
    exp_a = sum(lt.qty * true_px(A) for lt in LOTS if lt.sleeve == "seeded" and lt.is_pre
                and lt.e_date <= A and (lt.x_date is None or lt.x_date > A))
    check(close(new_nav[("seeded", A)]["total_nav"] - orig_nav[("seeded", A)]["total_nav"], exp_a),
          f"seeded 06-01 total_nav moved by qty_old*close = {exp_a:.4f}")

    # restatement log: exactly one row per changed (sleeve, date), exact old/new totals
    rest = query(base, "SELECT * FROM paper_nav_restatement ORDER BY id")
    rkeys = [(r["strategy_name"], r["nav_date"]) for r in rest]
    check(len(rkeys) == len(set(rkeys)) and set(rkeys) == changed,
          f"restatement log: one row per changed NAV row ({len(rest)} rows == {len(changed)} changed)")
    prefix = f"split-repair {T} {D} x2: fixture test"
    check(all(r["reason"] == prefix for r in rest), f"restatement reason is {prefix!r}")
    check(all(close(r["old_total_nav"], orig_nav[(r["strategy_name"], r["nav_date"])]["total_nav"], 0)
              and close(r["new_total_nav"], new_nav[(r["strategy_name"], r["nav_date"])]["total_nav"])
              for r in rest), "restatement old/new totals match the NAV rows")

    # nothing outside the five touched tables moved
    snap1 = snapshot(base)
    touched = {"price_cache", "paper_positions", "paper_portfolio", "paper_nav",
               "paper_nav_restatement", "sqlite_sequence"}
    check(all(snap1[t] == snap0[t] for t in snap0 if t not in touched),
          "tables outside price_cache/paper_* are unchanged")

    # ---- 4. a second execute is refused ----
    print("second execute")
    rc, out = run(exec_argv(base))
    check(rc == 1 and "[P2]" in out, f"second execute is refused with P2 (rc={rc})")
    check(snapshot(base) == snap1, "...and the DB is unchanged by it")
    rc, out = run(base_argv(base))
    check(rc == 1 and "[P2]" in out, f"a second dry run reports P2 too (rc={rc})")

    # ---- 5. an in-transaction failure rolls EVERYTHING back ----
    print("atomicity")
    p = make_fixture(tmp, "boom", lambda c: c.execute(
        "CREATE TRIGGER boom BEFORE UPDATE ON paper_positions WHEN OLD.id = 3 "
        "BEGIN SELECT RAISE(ABORT, 'boom'); END"))
    s = snapshot(p)
    rc, out = run(exec_argv(p))
    check(rc == 1 and "boom" in out, f"SQL failure mid-transaction (after price_cache was updated): rc={rc}")
    check(snapshot(p) == s, "...price_cache, lots, cash and NAV are all rolled back")

    p = make_fixture(tmp, "skew", lambda c: c.execute(
        "CREATE TRIGGER skew AFTER UPDATE OF cash ON paper_portfolio "
        "WHEN abs(NEW.cash - OLD.cash - 1.0) > 1e-9 "
        "BEGIN UPDATE paper_portfolio SET cash = cash + 1.0 WHERE strategy_name = NEW.strategy_name; END"))
    s = snapshot(p)
    rc, out = run(exec_argv(p))
    check(rc == 1 and "gap" in out.lower(), f"ledger-gap assertion fires when cash drifts: rc={rc}")
    check(snapshot(p) == s, "...and the whole transaction is rolled back")

    dbmod.close_thread_connection()
    shutil.rmtree(tmp, ignore_errors=True)
    n = len(passed) + len(failures)
    print(f"\n{'PASS' if not failures else 'FAIL'}: {len(passed)}/{n} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
