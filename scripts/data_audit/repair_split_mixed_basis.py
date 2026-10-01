"""Repair a split that left price_cache on a MIXED basis, plus the paper ledger.

Record EG option 1 (MLI 2-for-1, ex 2026-07-01). The paper book never applied the
split and the nightly 30-day refresh re-downloaded part of June on the post-split
basis, so price_cache holds both bases for the same ticker. Fills and marks were
made on whichever basis the cache held when they were computed. This tool restates
the ACCOUNTING only: trades made on the bad data stand, decisions are never
backdated. Unlike scripts/backadjust_split.py (which assumes a clean cliff) it
classifies each fill LEG by its price basis, not by its date.

Usage (dry run is the default and opens the DB read-only):
  python -m scripts.data_audit.repair_split_mixed_basis --ticker MLI --ratio 2 \
      --ex-date 2026-07-01 --basis-cutover 2026-06-05 --already-adjusted 2026-06-01 \
      [--db var/trades_copy_mli.db] [--execute --reason "record EG: ..."]
Exit codes: 0 ok (dry run or executed), 1 preflight refusal or assertion rollback,
2 usage error.

LOT RULE (per leg).  thr = close(ex) * sqrt(N).  A leg is PRE if its price > thr,
POST if < thr; ABORT if any fill is within 10% of thr, or a lot has a POST entry
and a PRE exit.
  pre  -> open : qty*N, entry_price/N (entry_value kept)
  pre  -> post : qty*N, entry_price/N, exit_value = qty_new*exit_price, P&L
                 recomputed, sleeve cash += exit_value_new - exit_value_old
  pre  -> pre  : qty*N, entry_price/N, exit_price/N (exit_value/P&L/cash unchanged)
  post -> any  : untouched

NAV RULE, every paper_nav row d of every affected sleeve s:
  d_cash = sum(exit_value_new - exit_value_old) over s's pre->post lots, exit_date <= d
  d_pos  = sum over s's pre-entry lots open at d of qty_old*(N-1)*close_post(d), but
           only when that row's MLI mark used the post basis:
             d >= ex, OR (d is a post-basis pre-ex date [already-adjusted dates and
             cutover <= d < ex] AND the sleeve was seeded after the rewrite:
             date(initialized_at) > d AND date(initialized_at) >= ex).
  close_post(d) = carry-forward close from the REPAIRED cache (bisect_right, same
  rule as historical_state.last_close_at). A row where both terms are 0 is skipped;
  otherwise a paper_nav_restatement row is inserted FIRST (the seal triggers
  require it), then positions_value += d_pos, cash += d_cash, total_nav += both.
  (The plan text writes d_pos as qty_old*close_post; that equals qty_old*(N-1)*
  close_post only for N=2 -- the (N-1) form is the correct delta for any N.)

initialized_at is an ISO timestamp written in UTC; only its first 10 characters are
compared (the dates involved are far enough from midnight UTC to be unambiguous).
"""
from __future__ import annotations

import argparse
import bisect
import json
import math
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from trading_bot.config import DB_PATH

PRICE_DIV_KINDS = ("close", "next_open")          # divided by N below the cutover
VOLUME_MUL_KINDS = ("volume", "next_open_vol")    # multiplied by N below the cutover
KNOWN_KINDS = frozenset({"close", "volume", "next_open", "next_open_range", "next_open_vol",
                         "above_ma_50", "atr_pct_20", "splits_json", "dividends_json"})
REF_COLS = ("entry_ref_close", "entry_ref_date", "exit_ref_close", "exit_ref_date")
SEAM_TOL = 0.25      # P1 / post-repair seam band (relative)
# P3: a fill must sit at least this far from thr. The two bases sit ~sqrt(N) either
# side of thr (N=2: ~29% below / ~41% above), so 25% wrongly caught real post-basis
# MLI fills (57-70 vs thr 81.2, nearest 14.2% away); 10% still flags a genuinely
# ambiguous price (record EJ, 2026-09-30).
BASIS_MARGIN = 0.10
FORMULA_TOL = 0.01   # P4
GAP_TOL = 0.005      # cash-vs-ledger gap must not move by more than this


class RepairAbort(Exception):
    """An in-transaction assertion failed; the caller ROLLBACKs and exits 1."""


@dataclass
class Args:
    ticker: str
    ratio: float
    ex: str
    cutover: str
    adjusted: tuple
    db: Path
    execute: bool
    reason: str | None


@dataclass
class Lot:
    id: int
    sleeve: str
    status: str
    qty: float
    entry_price: float
    entry_value: float
    entry_date: str
    exit_price: float | None
    exit_value: float | None
    exit_date: str | None
    realized_pnl: float | None
    realized_pnl_pct: float | None
    refs: dict
    cat: str = ""
    qty_new: float = 0.0
    entry_price_new: float = 0.0
    exit_price_new: float | None = None
    exit_value_new: float | None = None
    pnl_new: float | None = None
    pct_new: float | None = None
    cash_delta: float = 0.0


@dataclass
class NavChange:
    sleeve: str
    nav_date: str
    old_total: float
    d_cash: float
    d_pos: float


@dataclass
class Plan:
    failures: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    thr: float | None = None
    ex_close: float | None = None
    seam_before: float | None = None
    seam_after: float | None = None
    last_pre_date: str | None = None
    c1: dict = field(default_factory=dict)          # kind -> (rows, non-NULL rows)
    splits_action: str = ""
    splits_new: str | None = None
    divs_action: str = ""
    divs_new: str | None = None
    lots: list = field(default_factory=list)
    affected: list = field(default_factory=list)
    cash_delta: dict = field(default_factory=dict)
    gaps_before: dict = field(default_factory=dict)
    nav: list = field(default_factory=list)
    latest_close_date: str | None = None
    understatement: float = 0.0
    executed: bool = False


# --------------------------------------------------------------------------- CLI
def _iso(ap: argparse.ArgumentParser, name: str, s: str) -> str:
    try:
        ok = date.fromisoformat(s).isoformat() == s
    except ValueError:
        ok = False
    if not ok:
        ap.error(f"{name} must be an ISO date YYYY-MM-DD, got {s!r}")
    return s


def parse_args(argv=None) -> Args:
    ap = argparse.ArgumentParser(prog="repair_split_mixed_basis", allow_abbrev=False,
                                 description="Repair a mixed-basis split (record EG).")
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--ratio", required=True, type=float, help="Split ratio N (> 1; 2 for 2-for-1).")
    ap.add_argument("--ex-date", required=True, help="First post-split trading day.")
    ap.add_argument("--basis-cutover", required=True,
                    help="First date of the contiguous post-basis run in price_cache.")
    ap.add_argument("--already-adjusted", default="",
                    help="Comma list of dates before the cutover that are ALREADY post-basis.")
    ap.add_argument("--db", default=None, help="DB path (default: the live DB).")
    ap.add_argument("--execute", action="store_true", help="Apply (default: dry run).")
    ap.add_argument("--reason", default=None, help="Required with --execute.")
    ns = ap.parse_args(argv)
    if not (math.isfinite(ns.ratio) and ns.ratio > 1.0):
        ap.error("--ratio must be a finite number > 1")
    ex = _iso(ap, "--ex-date", ns.ex_date)
    cut = _iso(ap, "--basis-cutover", ns.basis_cutover)
    adj = tuple(sorted({_iso(ap, "--already-adjusted", s.strip())
                        for s in ns.already_adjusted.split(",") if s.strip()}))
    if not (cut < ex and all(d < cut for d in adj)):
        ap.error("need every already-adjusted date < --basis-cutover < --ex-date")
    if ns.execute and not (ns.reason and ns.reason.strip()):
        ap.error("--reason is required with --execute")
    db = Path(ns.db) if ns.db else DB_PATH
    if not db.is_file():
        ap.error(f"--db not found: {db}")
    return Args(ns.ticker, float(ns.ratio), ex, cut, adj, db, ns.execute, ns.reason)


def _open(db: Path, rw: bool) -> sqlite3.Connection:
    """Own connection (not trading_bot.db.connect) so --db really redirects.
    mode=rw never CREATES a missing file. isolation_level=None: we issue BEGIN/COMMIT."""
    uri = f"{db.resolve().as_uri()}?mode={'rw' if rw else 'ro'}"
    conn = sqlite3.connect(uri, uri=True, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


# ------------------------------------------------------------------------ reads
def _load_closes(conn, ticker):
    rows = conn.execute("SELECT key_date, price FROM price_cache WHERE ticker=? AND kind='close' "
                        "AND price IS NOT NULL ORDER BY key_date", (ticker,)).fetchall()
    return [r["key_date"] for r in rows], [r["price"] for r in rows]


def _last_close_at(dates, prices, d):
    """Carry-forward close on-or-before d (bisect twin of historical_state.last_close_at)."""
    i = bisect.bisect_right(dates, d)
    return prices[i - 1] if i else None


def _adj_clause(a: Args):
    if not a.adjusted:
        return "", ()
    return f" AND key_date NOT IN ({','.join('?' * len(a.adjusted))})", a.adjusted


def _gap(conn, sleeve):
    """paper_portfolio.cash minus the ledger identity starting - sum(entry) + sum(exit)."""
    r = conn.execute("SELECT starting_cash, cash FROM paper_portfolio WHERE strategy_name=?",
                     (sleeve,)).fetchone()
    e, x = conn.execute("SELECT COALESCE(SUM(entry_value), 0), COALESCE(SUM(exit_value), 0) "
                        "FROM paper_positions WHERE strategy_name=?", (sleeve,)).fetchone()
    return r["cash"] - (r["starting_cash"] - e + x)


def _load_lots(conn, ticker):
    out = []
    for r in conn.execute("SELECT * FROM paper_positions WHERE ticker=? ORDER BY id", (ticker,)):
        keys = r.keys()
        out.append(Lot(id=r["id"], sleeve=r["strategy_name"], status=r["status"], qty=r["qty"],
                       entry_price=r["entry_price"], entry_value=r["entry_value"],
                       entry_date=r["entry_date"], exit_price=r["exit_price"],
                       exit_value=r["exit_value"], exit_date=r["exit_date"],
                       realized_pnl=r["realized_pnl"], realized_pnl_pct=r["realized_pnl_pct"],
                       refs={c: r[c] for c in REF_COLS if c in keys}))
    return out


def _read_events(conn, ticker, kind):
    """('missing'|'ok'|'bad', events) for a per-ticker JSON row (key_date='all')."""
    row = conn.execute("SELECT price FROM price_cache WHERE ticker=? AND kind=? AND key_date='all'",
                       (ticker, kind)).fetchone()
    if row is None:
        return "missing", None
    raw = row[0]
    try:
        ev = json.loads(raw) if isinstance(raw, str) else None
    except ValueError:
        ev = None
    ok = isinstance(ev, list) and all(
        isinstance(e, list) and len(e) == 2 and isinstance(e[0], str)
        and isinstance(e[1], (int, float)) and not isinstance(e[1], bool) for e in ev)
    return ("ok", ev) if ok else ("bad", None)


# ------------------------------------------------------------------- build_plan
def build_plan(conn, a: Args) -> Plan:
    """Preflight P1-P5 then the change plan C1-C5. READS ONLY."""
    t, n = a.ticker, a.ratio
    adj = set(a.adjusted)
    plan = Plan()
    fail, note = plan.failures.append, plan.notes.append
    dates, prices = _load_closes(conn, t)
    by_date = dict(zip(dates, prices))

    # P1 seam present: last un-adjusted pre-cutover close / cutover close ~ N.
    pre_dates = [d for d in dates if d < a.cutover and d not in adj]
    c_px = by_date.get(a.cutover)
    if not pre_dates or c_px is None or c_px <= 0:
        fail(f"[P1] seam not checkable: need a close on {a.cutover} and a close on an "
             f"un-adjusted date before it (cutover close={c_px}, earlier dates={len(pre_dates)})")
    else:
        plan.last_pre_date = pre_dates[-1]
        plan.seam_before = by_date[plan.last_pre_date] / c_px
        if abs(plan.seam_before / n - 1.0) > SEAM_TOL:
            fail(f"[P1] no split seam at the cutover: close {plan.last_pre_date} "
                 f"{by_date[plan.last_pre_date]:.4f} / close {a.cutover} {c_px:.4f} = "
                 f"{plan.seam_before:.4f}, not within 25% of N={n:g}")
        else:
            note(f"[P1] seam present: close {plan.last_pre_date} {by_date[plan.last_pre_date]:.4f} / "
                 f"close {a.cutover} {c_px:.4f} = {plan.seam_before:.4f} (N={n:g})")

    # P2 not already done.
    prefix = f"split-repair {t} {a.ex}"
    try:
        done = conn.execute("SELECT COUNT(*) FROM paper_nav_restatement WHERE substr(reason, 1, ?) = ?",
                            (len(prefix), prefix)).fetchone()[0]
    except sqlite3.OperationalError as e:
        fail(f"[P2] paper_nav_restatement unreadable: {e}")
    else:
        if done:
            fail(f"[P2] already repaired: {done} paper_nav_restatement row(s) with reason "
                 f"starting {prefix!r}")
        else:
            note(f"[P2] not already done: no restatement reason starting {prefix!r}")

    # P3 basis clear. thr uses the ex-date close (ex >= cutover, so never rewritten here).
    plan.ex_close = _last_close_at(dates, prices, a.ex)
    thr = None
    if plan.ex_close is None or plan.ex_close <= 0:
        fail(f"[P3] no close on or before the ex-date {a.ex}; cannot form the basis threshold")
    else:
        thr = plan.thr = plan.ex_close * math.sqrt(n)
    lots = _load_lots(conn, t)
    n_clear = 0
    for lot in lots:
        tag = f"lot {lot.id} ({lot.sleeve})"
        is_open = lot.status == "open"
        if (lot.status not in ("open", "closed") or is_open != (lot.exit_date is None)
                or (not is_open and (lot.exit_price is None or lot.exit_value is None))):
            fail(f"[P3] {tag}: malformed lot (status={lot.status!r}, exit_date={lot.exit_date!r}, "
                 f"exit_price={lot.exit_price!r}, exit_value={lot.exit_value!r})")
            continue
        if thr is None:
            continue
        near = False
        for name, px in [("entry", lot.entry_price)] + ([] if is_open else [("exit", lot.exit_price)]):
            if not px > 0 or abs(px / thr - 1.0) <= BASIS_MARGIN:
                fail(f"[P3] {tag}: {name} price {px} is within 10% of thr {thr:.4f}")
                near = True
        if near:
            continue
        if not is_open and lot.entry_price < thr < lot.exit_price:
            fail(f"[P3] {tag}: post-basis entry {lot.entry_price} with a pre-basis exit {lot.exit_price}")
            continue
        # Fill-reference columns are not restated, so a ref on a PRE-basis LEG would be
        # left on the wrong basis: refuse. A ref on a POST-basis exit leg (lots 3509/5612,
        # exit_ref 2026-09-28) is already on the post basis and stays correct as-is.
        pre_leg_refs = {}
        if lot.entry_price > thr:
            pre_leg_refs.update({k: v for k, v in lot.refs.items() if k.startswith("entry_")})
            if not is_open and lot.exit_price > thr:
                pre_leg_refs.update({k: v for k, v in lot.refs.items() if k.startswith("exit_")})
        if any(v is not None for v in pre_leg_refs.values()):
            fail(f"[P3] {tag}: a pre-basis leg has non-NULL fill-reference columns {pre_leg_refs}; "
                 f"they are not restated")
            continue
        n_clear += 1
    if thr is not None:
        note(f"[P3] basis clear: thr={thr:.4f} (close {plan.ex_close:.4f} on/before {a.ex} * sqrt({n:g})); "
             f"{n_clear}/{len(lots)} {t} lots clear of it")

    # P4 formula holds on every existing closed lot.
    n_closed = n_bad = 0
    for lot in lots:
        if lot.status != "closed" or lot.exit_price is None or lot.exit_value is None \
                or not lot.entry_price > 0:
            continue
        n_closed += 1
        want = ((lot.exit_price - lot.entry_price) * lot.qty,
                (lot.exit_price / lot.entry_price - 1.0) * 100.0,
                lot.exit_price * lot.qty)
        have = (lot.realized_pnl, lot.realized_pnl_pct, lot.exit_value)
        if any(h is None or abs(h - w) > FORMULA_TOL for h, w in zip(have, want)):
            n_bad += 1
            fail(f"[P4] lot {lot.id} ({lot.sleeve}): stored (pnl, pct, exit_value) {have} does not "
                 f"reproduce the close_position formula {want}")
    if not n_bad:
        note(f"[P4] formula holds: {n_closed} closed {t} lots reproduce realized_pnl / pct / exit_value "
             f"within {FORMULA_TOL}")

    # P5 only kinds this tool has a rule for.
    kinds = {r[0] for r in conn.execute("SELECT DISTINCT kind FROM price_cache WHERE ticker=?", (t,))}
    if not kinds:
        fail(f"[P5] no price_cache rows for {t}")
    elif kinds - KNOWN_KINDS:
        fail(f"[P5] unknown price_cache kinds for {t} (no adjustment rule): {sorted(kinds - KNOWN_KINDS)}")
    else:
        note(f"[P5] known kinds: {sorted(kinds)}")

    # C2 inputs are parsed here so an unreadable row is a preflight refusal.
    st, ev = _read_events(conn, t, "splits_json")
    if st == "bad":
        fail("[C2] splits_json row is not a JSON list of [iso_date, ratio]")
    elif st == "missing":
        plan.splits_action = "no splits_json row exists; none created"
    elif any(e[0] == a.ex for e in ev):
        plan.splits_action = f"[{a.ex!r}, ...] already present; row left unchanged"
    else:
        plan.splits_new = json.dumps(sorted(ev + [[a.ex, n]], key=lambda e: e[0]))
        plan.splits_action = f"append [{a.ex}, {n}] ({len(ev)} -> {len(ev) + 1} events, sorted)"
    st, ev = _read_events(conn, t, "dividends_json")
    if st == "bad":
        fail("[C2] dividends_json row is not a JSON list of [iso_date, amount]")
    elif st == "missing":
        plan.divs_action = "no dividends_json row exists; none created"
    else:
        k = sum(1 for e in ev if e[0] < a.ex)
        if k:
            plan.divs_new = json.dumps([[e[0], e[1] / n] if e[0] < a.ex else e for e in ev])
        plan.divs_action = (f"{k} of {len(ev)} amounts dated before {a.ex} divided by {n:g}" if k
                            else f"no amounts dated before {a.ex}; row left unchanged")

    if plan.failures:
        return plan

    # C1 price_cache row counts.
    adj_sql, adj_params = _adj_clause(a)
    for kind in PRICE_DIV_KINDS + VOLUME_MUL_KINDS:
        r = conn.execute("SELECT COUNT(*), COUNT(price) FROM price_cache WHERE ticker=? AND kind=? "
                         f"AND key_date < ?{adj_sql}", (t, kind, a.cutover, *adj_params)).fetchone()
        plan.c1[kind] = (r[0], r[1])

    # C3 lots + C4 cash.
    for lot in lots:
        if not lot.entry_price > thr:
            lot.cat = "post"
            continue
        lot.qty_new = lot.qty * n
        lot.entry_price_new = lot.entry_price / n
        if lot.status == "open":
            lot.cat = "pre_open"
        elif lot.exit_price > thr:
            lot.cat = "pre_pre"
            lot.exit_price_new = lot.exit_price / n
        else:
            lot.cat = "pre_post"
            lot.exit_value_new = lot.qty_new * lot.exit_price
            lot.pnl_new = (lot.exit_price - lot.entry_price_new) * lot.qty_new
            lot.pct_new = (lot.exit_price / lot.entry_price_new - 1.0) * 100.0
            lot.cash_delta = lot.exit_value_new - lot.exit_value
    plan.lots = lots
    plan.affected = sorted({lot.sleeve for lot in lots if lot.cat != "post"})
    for s in plan.affected:
        plan.cash_delta[s] = sum(lot.cash_delta for lot in lots if lot.sleeve == s)
        plan.gaps_before[s] = _gap(conn, s)

    # C5 NAV rows. Needs each affected sleeve's initialized_at (first 10 chars, see module doc).
    init = {}
    for s in plan.affected:
        row = conn.execute("SELECT initialized_at FROM paper_portfolio WHERE strategy_name=?",
                           (s,)).fetchone()
        try:
            init[s] = date.fromisoformat(str(row[0])[:10]).isoformat() if row else None
        except ValueError:
            init[s] = None
        if init[s] is None:
            fail(f"[C5] sleeve {s}: missing paper_portfolio row or unparseable initialized_at "
                 f"({row[0] if row else None!r})")
    if plan.failures:
        return plan
    rep_prices = [p / n if d < a.cutover and d not in adj else p for d, p in zip(dates, prices)]
    close_post_cache: dict = {}

    def close_post(d):
        if d not in close_post_cache:
            close_post_cache[d] = _last_close_at(dates, rep_prices, d)
        return close_post_cache[d]

    for s in plan.affected:
        s_lots = [lot for lot in lots if lot.sleeve == s and lot.cat != "post"]
        seeded_after_rewrite = init[s] >= a.ex
        for r in conn.execute("SELECT nav_date, total_nav FROM paper_nav WHERE strategy_name=? "
                              "ORDER BY nav_date", (s,)).fetchall():
            d = r["nav_date"]
            d_cash = float(sum(lot.cash_delta for lot in s_lots
                               if lot.cat == "pre_post" and lot.exit_date <= d))
            post_basis_mark = d >= a.ex or (
                (d in adj or a.cutover <= d < a.ex) and init[s] > d and seeded_after_rewrite)
            d_pos = 0.0
            if post_basis_mark:
                for lot in s_lots:
                    if lot.entry_date <= d and (lot.exit_date is None or lot.exit_date > d):
                        cp = close_post(d)
                        if cp is None:
                            fail(f"[C5] sleeve {s} {d}: no close on or before {d} to mark lot {lot.id}")
                            continue
                        d_pos += lot.qty * (n - 1.0) * cp
            if abs(d_cash) < 1e-12 and abs(d_pos) < 1e-12:
                continue
            plan.nav.append(NavChange(s, d, r["total_nav"], d_cash, d_pos))

    if dates:
        plan.latest_close_date = dates[-1]
        plan.understatement = sum((lot.qty_new - lot.qty) * rep_prices[-1]
                                  for lot in lots if lot.cat == "pre_open")
    return plan


# ------------------------------------------------------------------- apply_plan
def _apply(conn, a: Args, plan: Plan) -> None:
    t, n = a.ticker, a.ratio
    adj_sql, adj_params = _adj_clause(a)

    # C1 price_cache. NULL / NULL stays NULL; every other kind is untouched.
    for kinds, op in ((PRICE_DIV_KINDS, "/"), (VOLUME_MUL_KINDS, "*")):
        ph = ",".join("?" * len(kinds))
        cur = conn.execute(f"UPDATE price_cache SET price = price {op} ? WHERE ticker=? "
                           f"AND kind IN ({ph}) AND key_date < ?{adj_sql}",
                           (n, t, *kinds, a.cutover, *adj_params))
        want = sum(plan.c1[k][0] for k in kinds)
        if cur.rowcount != want:
            raise RepairAbort(f"[A0] C1 {kinds}: updated {cur.rowcount} rows, planned {want}")

    # C2 metadata.
    for kind, new in (("splits_json", plan.splits_new), ("dividends_json", plan.divs_new)):
        if new is None:
            continue
        cur = conn.execute("UPDATE price_cache SET price=? WHERE ticker=? AND kind=? AND key_date='all'",
                           (new, t, kind))
        if cur.rowcount != 1:
            raise RepairAbort(f"[A0] C2 {kind}: updated {cur.rowcount} rows, planned 1")

    # C3 lots.
    for lot in plan.lots:
        if lot.cat == "pre_open":
            sql, args = "qty=?, entry_price=?", (lot.qty_new, lot.entry_price_new)
        elif lot.cat == "pre_post":
            sql = "qty=?, entry_price=?, exit_value=?, realized_pnl=?, realized_pnl_pct=?"
            args = (lot.qty_new, lot.entry_price_new, lot.exit_value_new, lot.pnl_new, lot.pct_new)
        elif lot.cat == "pre_pre":
            sql, args = "qty=?, entry_price=?, exit_price=?", (lot.qty_new, lot.entry_price_new,
                                                              lot.exit_price_new)
        else:
            continue
        cur = conn.execute(f"UPDATE paper_positions SET {sql} WHERE id=?", (*args, lot.id))
        if cur.rowcount != 1:
            raise RepairAbort(f"[A0] C3 lot {lot.id}: updated {cur.rowcount} rows, planned 1")

    # C4 cash.
    for s, delta in sorted(plan.cash_delta.items()):
        if delta != 0:
            cur = conn.execute("UPDATE paper_portfolio SET cash = cash + ? WHERE strategy_name=?",
                               (delta, s))
            if cur.rowcount != 1:
                raise RepairAbort(f"[A0] C4 sleeve {s}: updated {cur.rowcount} rows, planned 1")

    # C5 NAV rows. The restatement row goes in BEFORE each UPDATE: the seal trigger lives
    # in the DB and refuses to rewrite a sealed row without a fresh one (created_at default).
    tag = f"split-repair {t} {a.ex} x{n:g}: {a.reason}"
    for nc in plan.nav:
        conn.execute("INSERT INTO paper_nav_restatement (strategy_name, nav_date, old_total_nav, "
                     "new_total_nav, reason) VALUES (?,?,?,?,?)",
                     (nc.sleeve, nc.nav_date, nc.old_total, nc.old_total + nc.d_pos + nc.d_cash, tag))
        cur = conn.execute("UPDATE paper_nav SET positions_value = positions_value + ?, "
                           "cash = cash + ?, total_nav = total_nav + ? + ? "
                           "WHERE strategy_name=? AND nav_date=?",
                           (nc.d_pos, nc.d_cash, nc.d_pos, nc.d_cash, nc.sleeve, nc.nav_date))
        if cur.rowcount != 1:
            raise RepairAbort(f"[A0] C5 {nc.sleeve} {nc.nav_date}: updated {cur.rowcount} rows, planned 1")

    # In-transaction asserts.
    for s, g0 in plan.gaps_before.items():
        g1 = _gap(conn, s)
        if abs(g1 - g0) > GAP_TOL:
            raise RepairAbort(f"[A1] cash-vs-ledger gap moved for {s}: {g0:.4f} -> {g1:.4f}")
    dates, prices = _load_closes(conn, t)
    by_date = dict(zip(dates, prices))
    seam = by_date[plan.last_pre_date] / by_date[a.cutover]
    if abs(seam - 1.0) > SEAM_TOL:
        raise RepairAbort(f"[A2] seam after repair is {seam:.4f}, not within 25% of 1 "
                          f"(close {plan.last_pre_date} / close {a.cutover})")
    plan.seam_after = seam


def apply_plan(conn, a: Args) -> Plan:
    """One BEGIN IMMEDIATE transaction. The plan is built INSIDE it (under the write
    lock), so no writer can slip in between the reads and the writes. Any refusal or
    assertion failure ROLLBACKs and is returned in plan.failures."""
    conn.execute("BEGIN IMMEDIATE")
    plan = None
    try:
        plan = build_plan(conn, a)
        if not plan.failures:
            _apply(conn, a, plan)
            conn.execute("COMMIT")
            plan.executed = True
    except (RepairAbort, sqlite3.Error) as e:
        plan = plan if plan is not None else Plan()
        plan.failures.append(f"[ABORT] {type(e).__name__}: {e}")
    finally:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
    return plan


# ---------------------------------------------------------------------- summary
def summary_lines(a: Args, plan: Plan, mode: str) -> list:
    cats = {c: [lot for lot in plan.lots if lot.cat == c]
            for c in ("pre_open", "pre_post", "pre_pre", "post")}
    pp = cats["pre_post"]
    d_ex = sum(lot.cash_delta for lot in pp if lot.exit_date >= a.ex)
    d_pre = sum(lot.cash_delta for lot in pp if lot.exit_date < a.ex)
    L = [f"repair_split_mixed_basis  ticker={a.ticker} ratio={a.ratio:g} ex={a.ex} "
         f"cutover={a.cutover} already_adjusted={list(a.adjusted)}",
         f"db={a.db}  mode={mode}"]
    L += [f"  ok {x}" for x in plan.notes]
    L.append("C1 price_cache (key_date < cutover, not already-adjusted); rows / non-NULL:")
    for kind in PRICE_DIV_KINDS + VOLUME_MUL_KINDS:
        rows, nn = plan.c1[kind]
        L.append(f"    {kind:14s} {'/' if kind in PRICE_DIV_KINDS else '*'}{a.ratio:g}  rows={rows}  non-NULL={nn}")
    L.append(f"C2 splits_json:    {plan.splits_action}")
    L.append(f"C2 dividends_json: {plan.divs_action}")
    L.append(f"C3 lots on {a.ticker}: total={len(plan.lots)}  pre->open={len(cats['pre_open'])}  "
             f"pre->post={len(pp)} (exit>=ex {sum(1 for x in pp if x.exit_date >= a.ex)}, "
             f"exit<ex {sum(1 for x in pp if x.exit_date < a.ex)})  pre->pre={len(cats['pre_pre'])}  "
             f"post-untouched={len(cats['post'])}")
    L.append(f"   sleeves affected={len(plan.affected)}")
    L.append(f"C4 cash delta total={d_ex + d_pre:+.4f}  (pre->post exit>=ex {d_ex:+.4f}, exit<ex {d_pre:+.4f})")
    L.append(f"C5 NAV rows restated={len(plan.nav)} across {len({nc.sleeve for nc in plan.nav})} sleeves  "
             f"(sum d_cash={sum(nc.d_cash for nc in plan.nav):+.4f}, "
             f"sum d_pos={sum(nc.d_pos for nc in plan.nav):+.4f})")
    L.append(f"open-lot understatement: {plan.understatement:.4f} "
             f"[sum (qty_new - qty_old) * repaired close on {plan.latest_close_date}, pre->open lots]")
    last_nav = {}
    for nc in plan.nav:
        last_nav[nc.sleeve] = nc            # plan.nav is ordered by date within a sleeve
    L.append("per sleeve: lots open/post/pre->pre, cash delta, NAV rows restated, last restated row")
    for s in plan.affected:
        mine = [lot for lot in plan.lots if lot.sleeve == s]
        k = lambda c: sum(1 for lot in mine if lot.cat == c)   # noqa: E731
        ln = last_nav.get(s)
        L.append(f"    {s:34s} lots {k('pre_open')}/{k('pre_post')}/{k('pre_pre')}  "
                 f"cash {plan.cash_delta[s]:+.4f}  nav_rows {sum(1 for nc in plan.nav if nc.sleeve == s)}"
                 + (f"  last {ln.nav_date} {ln.d_cash + ln.d_pos:+.4f}" if ln else ""))
    if plan.executed:
        L.append(f"RESULT: EXECUTED and committed. seam after repair = {plan.seam_after:.4f}")
    else:
        L.append("RESULT: DRY RUN - nothing written. Re-run with --execute --reason to apply.")
    return L


def main(argv=None) -> int:
    a = parse_args(argv)
    mode = "EXECUTE" if a.execute else "DRY RUN"
    try:
        conn = _open(a.db, rw=a.execute)
        try:
            if a.execute:
                plan = apply_plan(conn, a)
            else:
                conn.execute("BEGIN")            # one consistent read snapshot
                try:
                    plan = build_plan(conn, a)
                finally:
                    conn.execute("ROLLBACK")
        finally:
            conn.close()
    except sqlite3.Error as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return 1
    if plan.failures:
        print(f"repair_split_mixed_basis  ticker={a.ticker} ex={a.ex}  mode={mode}  db={a.db}")
        for x in plan.notes:
            print(f"  ok {x}")
        for x in plan.failures:
            print(f"  REFUSED {x}")
        print(f"RESULT: REFUSED ({len(plan.failures)} failure(s)) - nothing written (exit 1).")
        return 1
    print("\n".join(summary_lines(a, plan, mode)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
