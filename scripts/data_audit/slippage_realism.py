"""Slippage-realism check (no real fills yet — this is the data-driven proxy).

Two parts, on the backfilled clean cache:
  1. LIQUIDITY SNAPSHOT of the names the sleeves currently hold — median 60-day
     dollar volume per held name, bucketed, to show where the 5 bps half-spread
     assumption is optimistic (thin names cost more to trade).
  2. TC SWEEP for the two best sleeves (residual_roa_6535, mom_roa_6535) on the
     held-out window at half-spreads {5,10,15,25,40} bps — does the edge survive
     realistic transaction costs? (The real slippage_tracker activates once there
     are ~20 real broker fills, post-Aug 2026; this is the until-then proxy.)

SEQUENTIAL factor_backtest. Usage: python -m scripts.data_audit.slippage_realism
"""
from __future__ import annotations

import json
import statistics
import time
from datetime import date
from pathlib import Path

from trading_bot.db import connect
from trading_bot.execution import factor_backtest, market_data
from trading_bot.factors import universe, mom_roa_zscore
from trading_bot.strategies import mom_roa_6535, residual_roa_6535

OUT = Path("var/data_audit/slippage_realism.json")
TC_LEVELS = [5.0, 10.0, 15.0, 25.0, 40.0]
HELDOUT = (date(2024, 1, 1), date(2026, 5, 1))


def liquidity_snapshot() -> dict:
    market_data.preload_caches()
    universe._build_index()
    with connect() as conn:
        held = sorted({r[0] for r in conn.execute(
            "SELECT DISTINCT ticker FROM paper_positions WHERE status='open' "
            "AND strategy_name IN ('mom_v1_paper','mom_v2_paper',"
            "'mom_roa_6535_paper','residual_roa_6535_paper')")})
    as_of = date(2026, 6, 12)
    advs, missing = [], 0
    for tk in held:
        adv = universe.median_dollar_volume(tk, as_of)
        if adv is None:
            missing += 1
        else:
            advs.append((tk, adv))
    advs.sort(key=lambda x: x[1])
    buckets = {"<$1M": 0, "$1-10M": 0, "$10-50M": 0, ">$50M": 0}
    for _, a in advs:
        m = a / 1e6
        if m < 1: buckets["<$1M"] += 1
        elif m < 10: buckets["$1-10M"] += 1
        elif m < 50: buckets["$10-50M"] += 1
        else: buckets[">$50M"] += 1
    return {
        "n_held": len(held), "n_with_volume": len(advs), "n_missing_volume": missing,
        "median_adv_usd": statistics.median([a for _, a in advs]) if advs else None,
        "buckets": buckets,
        "thinnest": [(t, round(a)) for t, a in advs[:8]],
    }


def tc_sweep(label, rank_fn, top_n) -> list[dict]:
    out = []
    for bps in TC_LEVELS:
        factor_backtest.HALF_SPREAD_BPS = bps
        t0 = time.time()
        r = factor_backtest.run_factor_backtest(
            since=HELDOUT[0], until=HELDOUT[1], top_n=top_n,
            starting_cash=100_000.0, rank_fn=rank_fn, rebalance_freq="M")
        curve = r.equity_curve
        years = (HELDOUT[1] - HELDOUT[0]).days / 365.25
        cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
        out.append({"strategy": label, "half_bps": bps, "cagr_pct": round(cagr, 2),
                    "elapsed_sec": round(time.time() - t0, 1)})
        print(f"  {label} half={bps}bps -> CAGR {cagr:+.2f}%", flush=True)
    return out


def main() -> int:
    print("SLIPPAGE REALISM (clean cache)\n" + "=" * 60, flush=True)
    liq = liquidity_snapshot()
    print(f"\nLIQUIDITY of held names: n={liq['n_held']} "
          f"(volume cached for {liq['n_with_volume']}, missing {liq['n_missing_volume']})")
    if liq["median_adv_usd"]:
        print(f"  median 60d ADV = ${liq['median_adv_usd']/1e6:.1f}M")
    print(f"  buckets: {liq['buckets']}")
    print(f"  thinnest: {liq['thinnest']}")

    print("\nTC SWEEP (held-out 2024-01..2026-05):", flush=True)
    sweeps = []
    sweeps += tc_sweep("residual_roa_6535", residual_roa_6535.rank_fn(), 50)
    sweeps += tc_sweep("mom_roa_6535",
                       mom_roa_zscore.make_rank_fn(mom_roa_6535.W_MOM, mom_roa_6535.W_ROA), 50)

    # edge-vs-5bps summary
    print("\n  CAGR vs 5bps baseline:")
    for label in ("residual_roa_6535", "mom_roa_6535"):
        base = next(s["cagr_pct"] for s in sweeps if s["strategy"] == label and s["half_bps"] == 5.0)
        deltas = [f"{s['half_bps']:.0f}bps {s['cagr_pct']:+.1f}% ({s['cagr_pct']-base:+.1f})"
                  for s in sweeps if s["strategy"] == label]
        print(f"    {label}: " + " | ".join(deltas))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"liquidity": liq, "tc_sweep": sweeps}, indent=2))
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
