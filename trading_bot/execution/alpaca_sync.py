"""Mirror a DB paper sleeve's holdings into its Alpaca PAPER account.

For each mapped account (see alpaca_accounts / alpaca_keys.env), this reconciles
the Alpaca paper account to the sleeve's TARGET WEIGHTS, scaled to the account's
own equity. Weight-based (not share-copy) on purpose: Alpaca then fills at real
market prices, so its divergence from the DB sim measures real-world execution
cost — which is the whole reason to mirror.

Mechanics per account:
  1. target weights = each DB open position's market value / sleeve total.
  2. desired qty = weight * alpaca_equity / last_close (FRACTIONAL, 4dp — the DB
     sleeve holds fractional qty too, so this mirrors ~100% of equity instead of
     leaving whole-share rounding cash drag). EXCEPT: non-fractionable names get a
     WHOLE-share target (floor), and untradable/inactive names are dropped — Alpaca
     rejects fractional orders on those, so they'd otherwise silently miss (see
     fractionability.py). Names that can't be targeted are reported per account.
  3. diff vs current Alpaca qty -> SELLs (incl. full exits for dropped names)
     then BUYs, as market DAY orders. Open orders are cancelled first.

SAFETY: dry-run by default (prints the plan, submits nothing). Pass --execute to
send orders. Paper-only — AlpacaClient hard-guards the live host. This never
creates accounts or touches live; it submits PAPER orders to accounts you set up.

  # preview every mapped account:
  .venv\\Scripts\\python.exe -m trading_bot.execution.alpaca_sync --all
  # actually submit for every mapped account:
  .venv\\Scripts\\python.exe -m trading_bot.execution.alpaca_sync --all --execute
"""
from __future__ import annotations

import argparse
import logging
import math
import sqlite3
import sys

from trading_bot.config import DB_PATH
from trading_bot.execution import fractionability, paper_trader
from trading_bot.execution.alpaca_accounts import Account, configured_accounts
from trading_bot.execution.alpaca_client import AlpacaError

log = logging.getLogger(__name__)

MIN_ORDER_USD = 1.0  # skip dust diffs below this notional
CASH_BUFFER = 0.01  # deploy 99% of equity; leaves headroom so market-fill
                    # slippage above the sizing price can't push cash negative
                    # (margin debit). Mirrors the DB sim, which also holds a
                    # small positive cash residual after whole/fractional rounding.


def _latest_closes(tickers: set[str]) -> dict[str, float]:
    if not tickers:
        return {}
    conn = sqlite3.connect(DB_PATH)
    out: dict[str, float] = {}
    for t in tickers:
        row = conn.execute(
            "SELECT price FROM price_cache WHERE ticker=? AND kind='close' "
            "AND price>0 ORDER BY key_date DESC LIMIT 1", (t,)).fetchone()
        if row:
            out[t] = row[0]
    conn.close()
    return out


def target_weights(sleeve: str) -> dict[str, float]:
    """DB sleeve open positions -> {ticker: weight} by current market value.
    Empty until the sleeve has deployed (e.g. the 07-01 cohort before 07-01)."""
    pos = paper_trader.list_open(sleeve)
    if not pos:
        return {}
    px = _latest_closes({p["ticker"] for p in pos})
    vals = {p["ticker"]: p["qty"] * px[p["ticker"]]
            for p in pos if p["ticker"] in px}
    total = sum(vals.values())
    if total <= 0:
        return {}
    return {t: v / total for t, v in vals.items()}


def plan_orders(account: Account) -> tuple[list[tuple], list[tuple], dict]:
    """Return (sells, buys, info). Each leg = (symbol, qty, side). Read-only.

    Broker realism: non-fractionable names get WHOLE-share targets (floor), and
    untradable/inactive names are dropped — otherwise Alpaca rejects the fractional
    order and the weight silently lands in cash. Names we couldn't fully target are
    reported back in info['skipped']."""
    client = account.client()
    try:
        acct = client.get_account()
        equity = float(acct["equity"])
        deployable = equity * (1 - CASH_BUFFER)  # keep a small cash cushion
        cur = {p["symbol"]: float(p["qty"]) for p in client.list_positions()}
        weights = target_weights(account.sleeve)
        px = _latest_closes(set(weights) | set(cur))
        desired: dict[str, float] = {}
        for t, w in weights.items():
            if px.get(t):
                desired[t] = round(w * deployable / px[t], 4)
        fractionability.refresh(set(desired), client)  # fill/refresh the cache
    finally:
        client.close()

    nonfrac, untradable = fractionability.classify(set(desired))
    skipped: dict[str, str] = {}
    for t in list(desired):
        if t in untradable:
            skipped[t] = "untradable/inactive on Alpaca"
            del desired[t]
        elif t in nonfrac:
            whole = float(math.floor(desired[t]))
            if whole <= 0:
                skipped[t] = "non-fractionable, <1 whole share at target weight"
                del desired[t]
            else:
                desired[t] = whole  # whole-share fallback (Option 1)

    sells, buys = [], []
    for sym, held in cur.items():
        tgt = desired.get(sym, 0.0)
        reduce = held - tgt
        if reduce > 1e-6 and px.get(sym, 0) * reduce >= MIN_ORDER_USD:
            qty = round(held if tgt == 0 else reduce, 4)  # full exit for dropped names
            sells.append((sym, qty, "sell"))
    for t, tgt in desired.items():
        add = round(tgt - cur.get(t, 0.0), 4)
        if add > 1e-6 and px.get(t, 0) * add >= MIN_ORDER_USD:
            buys.append((t, add, "buy"))

    info = {"equity": equity, "n_target": len(desired), "n_held": len(cur),
            "skipped": skipped}
    return sells, buys, info


def sync_account(account: Account, *, execute: bool) -> int:
    sells, buys, info = plan_orders(account)
    mode = "EXECUTE" if execute else "DRY-RUN"
    print(f"\n=== ACCT  {account.sleeve}  ({mode}) ===")
    print(f"  Alpaca equity ${info['equity']:,.0f} | target names {info['n_target']} "
          f"| currently held {info['n_held']} | {len(sells)} sells, {len(buys)} buys")
    if info.get("skipped"):
        print(f"  NOT buyable on Alpaca ({len(info['skipped'])}): "
              + ", ".join(f"{t} ({why})" for t, why in info["skipped"].items()))
    if not sells and not buys:
        print("  Already in sync (or sleeve not yet deployed) — nothing to do.")
        return 0
    for sym, qty, side in sells + buys:
        print(f"    {side.upper():4} {sym:6} {qty}")
    if not execute:
        print("  (dry-run: no orders submitted; re-run with --execute)")
        return 0

    client = account.client()
    submitted = failed = 0
    try:
        for o in client.list_orders(status="open"):
            try:
                client.cancel_order(o["id"])
            except AlpacaError:
                pass
        for sym, qty, side in sells + buys:  # sells first frees buying power
            try:
                client.submit_order(symbol=sym, qty=qty, side=side,
                                    type="market", time_in_force="day")
                submitted += 1
            except AlpacaError as e:
                failed += 1
                log.warning("  order rejected %s %s x%s: %s", side, sym, qty, e)
    finally:
        client.close()
    print(f"  submitted {submitted}, rejected {failed}")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="sync every mapped account")
    ap.add_argument("--sleeve", help="sync only the account mapped to this sleeve")
    ap.add_argument("--execute", action="store_true",
                    help="actually submit orders (default: dry-run preview)")
    args = ap.parse_args()
    logging.basicConfig(level=logging.WARNING, format="%(message)s")

    accts = configured_accounts()
    if args.sleeve:
        accts = [a for a in accts if a.sleeve == args.sleeve]
    elif not args.all:
        print("Pass --all or --sleeve NAME. Add --execute to actually trade.")
        return 2
    if not accts:
        print("No matching configured accounts (check alpaca_keys.env).")
        return 2

    rc = 0
    for a in accts:
        rc |= sync_account(a, execute=args.execute)
    if not args.execute:
        print("\nPreview only. Add --execute to submit these PAPER orders.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
