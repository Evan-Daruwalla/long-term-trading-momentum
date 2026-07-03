"""Per-year and per-dimension breakdown of R9 results.

Goal: identify whether profitability is concentrated in a recent regime
(overfit) or whether there's a structural failure in specific
years/sectors/score-tiers/exit-reasons.

Reads var/sim_archive/runs/20260505-192744/{profile}.json (R9-50DMA-tuned).
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

RUN_DIR = Path("var/form4/archive/runs/20260505-192744")
PROFILES = ["conservative", "normal", "aggressive"]


def _year(date_str: str) -> str:
    return date_str[:4]


def _bucket(items: list, key) -> dict:
    """Group items by key(item) -> list of pnl_pct."""
    out: dict = defaultdict(list)
    for it in items:
        k = key(it)
        if k is not None:
            out[k].append(it["realized_pnl_pct"])
    return dict(out)


def _stats(vals: list[float]) -> dict:
    if not vals:
        return {"n": 0}
    wins = sum(1 for v in vals if v > 0)
    return {
        "n":     len(vals),
        "win%":  100.0 * wins / len(vals),
        "avg%":  mean(vals),
        "med%":  sorted(vals)[len(vals)//2],
        "sum%":  sum(vals),
    }


def _print_block(title: str, groups: dict, sort_key=lambda kv: kv[0]):
    print(f"\n  {title}")
    rows = sorted(groups.items(), key=sort_key)
    print(f"    {'bucket':<22} {'n':>4} {'win%':>6} {'avg%':>7} {'med%':>7} {'sum%':>8}")
    for k, vals in rows:
        s = _stats(vals)
        print(f"    {str(k):<22} {s['n']:>4} {s['win%']:>5.1f}% {s['avg%']:>6.1f}% "
              f"{s['med%']:>6.1f}% {s['sum%']:>7.1f}%")


def diagnose(profile: str) -> None:
    data = json.loads((RUN_DIR / f"{profile}.json").read_text())
    closed = data["closed_positions"]

    print(f"\n{'='*70}")
    print(f"  PROFILE: {profile.upper()}  "
          f"closed={len(closed)}  total_pnl%={data['total_pnl_pct']:+.2f}")
    print(f"{'='*70}")

    # By entry year
    by_year = _bucket(closed, lambda p: _year(p["entry_date"]))
    _print_block("By entry year", by_year)

    # By exit reason
    by_exit = _bucket(closed, lambda p: p["exit_reason"])
    _print_block("By exit reason", by_exit, sort_key=lambda kv: -len(kv[1]))

    # By score tier
    by_score = _bucket(closed, lambda p: f"score={p['entry_score']}")
    _print_block("By entry score", by_score)

    # By sector
    by_sector = _bucket(closed, lambda p: p.get("sector") or "UNKNOWN")
    _print_block("By sector", by_sector, sort_key=lambda kv: -sum(kv[1]))

    # Cross-cut: exit reason × year
    print("\n  Exit reason × entry year (avg pnl%, n):")
    yrs = sorted({_year(p["entry_date"]) for p in closed})
    exits = sorted({p["exit_reason"] for p in closed})
    print(f"    {'exit':<18} " + " ".join(f"{y:>10}" for y in yrs))
    for ex in exits:
        cells = []
        for y in yrs:
            vals = [p["realized_pnl_pct"] for p in closed
                    if p["exit_reason"] == ex and _year(p["entry_date"]) == y]
            if vals:
                cells.append(f"{mean(vals):+5.1f}% n={len(vals):<3}")
            else:
                cells.append(f"{'-':>10}")
        print(f"    {ex:<18} " + " ".join(f"{c:>10}" for c in cells))


if __name__ == "__main__":
    for p in PROFILES:
        diagnose(p)
