"""Why are score=9 trades losing?

Pulls all closed positions from R9 with score>=8 and slices the entry_components
JSON to find which signal patterns predict losses vs wins.

The hypothesis: certain components (e.g. cluster_3plus, ceo_cfo) might be
*negatively* correlated with returns, but the additive scoring treats them as
positive contributors — pushing bad signals into score=9.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

RUN_DIR = Path("var/form4/archive/runs/20260505-192744")


def load_all_closed() -> list[dict]:
    out = []
    for p in ["conservative", "normal", "aggressive"]:
        data = json.loads((RUN_DIR / f"{p}.json").read_text())
        for pos in data["closed_positions"]:
            pos["_profile"] = p
            try:
                pos["_components"] = json.loads(pos["entry_components"])
            except (TypeError, ValueError):
                pos["_components"] = {}
            out.append(pos)
    return out


def stats(vals):
    if not vals:
        return None
    wins = sum(1 for v in vals if v > 0)
    return f"n={len(vals):3d}  win%={100*wins/len(vals):4.1f}  avg%={mean(vals):+6.1f}  sum%={sum(vals):+7.1f}"


def main():
    closed = load_all_closed()
    print(f"Total closed positions: {len(closed)}")

    # 1) For each component flag, conditional return
    print("\n" + "="*70)
    print("  PER-COMPONENT CONDITIONAL RETURN (across all closed trades)")
    print("="*70)
    component_keys = {"any_buy", "cluster_2plus", "cluster_3plus",
                      "ceo_cfo", "over_500k"}
    for k in sorted(component_keys):
        with_flag = [p["realized_pnl_pct"] for p in closed
                     if p["_components"].get(k, 0) >= 1]
        without_flag = [p["realized_pnl_pct"] for p in closed
                        if p["_components"].get(k, 0) == 0]
        print(f"\n  {k}:")
        print(f"    has flag:  {stats(with_flag)}")
        print(f"    no flag:   {stats(without_flag)}")

    # 2) Specifically for score=9 trades, look at component distribution
    print("\n" + "="*70)
    print("  SCORE=9 TRADES: which components are firing?")
    print("="*70)
    s9 = [p for p in closed if p["entry_score"] == 9]
    s9_winners = [p for p in s9 if p["realized_pnl_pct"] > 0]
    s9_losers  = [p for p in s9 if p["realized_pnl_pct"] <= 0]

    print(f"  Total score=9: {len(s9)}  winners={len(s9_winners)}  losers={len(s9_losers)}")

    print("\n  Component frequency (winners vs losers):")
    print(f"    {'component':<18} {'winners':>10} {'losers':>10}")
    for k in sorted(component_keys):
        w = sum(1 for p in s9_winners if p["_components"].get(k, 0) >= 1)
        l = sum(1 for p in s9_losers  if p["_components"].get(k, 0) >= 1)
        wpct = 100*w/max(1,len(s9_winners))
        lpct = 100*l/max(1,len(s9_losers))
        print(f"    {k:<18} {w:>4}/{len(s9_winners):<3} ({wpct:4.0f}%) "
              f"{l:>4}/{len(s9_losers):<3} ({lpct:4.0f}%)")

    # 3) Top 10 worst score>=8 trades
    print("\n  TOP 10 WORST SCORE>=8 TRADES (any profile):")
    s89 = sorted([p for p in closed if p["entry_score"] >= 8],
                 key=lambda p: p["realized_pnl_pct"])[:10]
    print(f"    {'ticker':<8} {'profile':<12} {'score':<6} {'pnl%':>7} "
          f"{'sector':<22} {'exit':<14} components")
    for p in s89:
        comp = ",".join(f"{k}:{v}" for k, v in p["_components"].items() if v)
        print(f"    {p['ticker']:<8} {p['_profile']:<12} {p['entry_score']:<6} "
              f"{p['realized_pnl_pct']:>+6.1f}% {(p.get('sector') or 'UNKNOWN'):<22} "
              f"{p['exit_reason']:<14} {comp}")

    # 4) Score=8/9 by sector (the toxic combo)
    print("\n" + "="*70)
    print("  SCORE>=8 BY SECTOR  (where high-conviction goes wrong)")
    print("="*70)
    by_sec = defaultdict(list)
    for p in closed:
        if p["entry_score"] >= 8:
            by_sec[p.get("sector") or "UNKNOWN"].append(p["realized_pnl_pct"])
    rows = sorted(by_sec.items(), key=lambda kv: sum(kv[1]))
    for sec, vals in rows:
        print(f"    {sec:<22} {stats(vals)}")

    # 5) HC sizing impact: simulate uniform sizing on Normal/Aggressive
    #    Compute "what if score=9 trades had been at standard pct, not HC pct?"
    #    Normal: HC=10%, std=5% (2x). Aggressive: HC=15%, std=8% (~1.9x).
    print("\n" + "="*70)
    print("  WHAT IF: HC SIZING DISABLED (uniform position sizes)")
    print("="*70)
    for prof, hc_thresh, hc_pct, std_pct in [
        ("normal",     9, 10, 5),
        ("aggressive", 9, 15, 8),
    ]:
        data = json.loads((RUN_DIR / f"{prof}.json").read_text())
        actual_total = data["total_pnl_pct"]
        ratio = std_pct / hc_pct
        # Approximate adjustment: HC trades' realized $ would scale by `ratio`
        # if positioned at std pct instead.
        adj_realized = 0.0
        for pos in data["closed_positions"]:
            r = pos["realized_pnl"]
            if pos["entry_score"] >= hc_thresh:
                r = r * ratio
            adj_realized += r
        # Also adjust open positions value (approximate)
        adj_open = 0.0
        for pos in data["open_positions"]:
            mv_pnl = (pos.get("unrealized_pnl")
                      if "unrealized_pnl" in pos else 0.0)
            if pos["entry_score"] >= hc_thresh:
                mv_pnl = mv_pnl * ratio
            adj_open += mv_pnl
        adj_total_dollars = adj_realized + adj_open
        adj_pct = 100 * adj_total_dollars / data["starting_cash"]
        print(f"  {prof}: actual={actual_total:+.2f}%   "
              f"HC-disabled estimate={adj_pct:+.2f}%")


if __name__ == "__main__":
    main()
