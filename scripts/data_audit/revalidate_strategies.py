"""Re-validate all 5 systematic strategies on the BACKFILLED (clean) cache.

After the 2026-06-13 history-gap backfill (record Appendix AA), every pre-backfill
backtest number is stale (the momentum sleeves were ~half phantom-contaminated).
This re-runs the canonical in-sample / held-out validation for all 5 systematic
strategies on the clean data, using the EXACT methodology of v1_vs_v2_clean.py
(5 bps half-spread, monthly rebalance, same metric defs and windows) so the new
numbers are apples-to-apples with the stale ones.

SEQUENTIAL by construction: one process, one factor_backtest at a time. NEVER
parallelize factor_backtest (it wipes shared positions/portfolio_state tables).

Output: var/data_audit/revalidate_2026-06-13.json + a printed comparison table
(new clean vs stale HANDOFF numbers, with deltas).

Usage: python -m scripts.data_audit.revalidate_strategies
"""
from __future__ import annotations

import json
import statistics
import time
import traceback
from datetime import date
from pathlib import Path

from trading_bot.strategies import (
    momentum_v1, momentum_v2, mom_roa_6535, residual_roa_6535, sector_top4,
)

OUT_PATH = Path("var/data_audit/revalidate_2026-06-13.json")

WINDOWS = [
    ("in_sample",        date(2015, 1, 1), date(2023, 12, 31)),
    ("holdout",          date(2024, 1, 1), date(2026, 5, 1)),   # canonical (matches stale)
    ("holdout_extended", date(2024, 1, 1), date(2026, 6, 12)),  # all current clean data
]

STRATEGIES = [
    ("mom_v1", momentum_v1),
    ("mom_v2", momentum_v2),
    ("mom_roa_6535", mom_roa_6535),
    ("residual_roa_6535", residual_roa_6535),
    ("sector_top4", sector_top4),
]

# Stale HANDOFF numbers (pre-backfill) for the comparison. (in_sample, holdout)
# CAGR% only — the headline the docs cite.
STALE_CAGR = {
    "mom_v1":            {"in_sample": 4.72,  "holdout": 22.08},
    "mom_v2":            {"in_sample": 2.72,  "holdout": 27.99},
    "mom_roa_6535":      {"in_sample": 9.86,  "holdout": 36.47},
    "residual_roa_6535": {"in_sample": 8.86,  "holdout": 30.84},
    "sector_top4":       {"in_sample": 7.87,  "holdout": 17.59},
}


def _max_drawdown(curve):
    peak = curve[0][1]
    max_dd = 0.0
    for _, val in curve:
        if val > peak:
            peak = val
        dd = (val / peak - 1.0) * 100
        if dd < max_dd:
            max_dd = dd
    return max_dd


def _sharpe_by_year(curve, risk_free_apy=0.045):
    by_year: dict[str, list[float]] = {}
    pv = py = None
    for iso, v in curve:
        y = iso[:4]
        if pv and pv > 0 and y == py:
            by_year.setdefault(y, []).append(v / pv - 1.0)
        pv, py = v, y
    out = {}
    rf = risk_free_apy / 252
    for y, rets in by_year.items():
        if len(rets) < 20:
            continue
        sd = statistics.pstdev(rets)
        if sd > 0:
            out[y] = ((statistics.fmean(rets) - rf) / sd) * (252 ** 0.5)
    return out


def _calmar(cagr_pct, max_dd_pct):
    if max_dd_pct >= 0:
        return float("inf")
    return cagr_pct / abs(max_dd_pct)


def run_one(label, mod, window_label, since, until):
    print(f"  >>> {label} / {window_label}  ({since}->{until})", flush=True)
    t0 = time.time()
    r = mod.run(since=since, until=until)
    curve = r.equity_curve
    total_pct = (curve[-1][1] / curve[0][1] - 1) * 100
    years = (until - since).days / 365.25
    cagr = ((curve[-1][1] / curve[0][1]) ** (1 / years) - 1) * 100
    sh = _sharpe_by_year(curve)
    mean_sh = statistics.fmean(sh.values()) if sh else 0.0
    max_dd = _max_drawdown(curve)
    out = {
        "strategy": label, "window": window_label,
        "total_pct": round(total_pct, 4), "cagr_pct": round(cagr, 4),
        "max_dd_pct": round(max_dd, 4), "mean_sharpe": round(mean_sh, 4),
        "calmar": round(_calmar(cagr, max_dd), 4),
        "closed": r.closed_count, "elapsed_sec": round(time.time() - t0, 1),
    }
    print(f"      CAGR {cagr:+.2f}%  Sharpe {mean_sh:+.3f}  maxDD {max_dd:+.1f}%  "
          f"trades {r.closed_count}  ({out['elapsed_sec']}s)", flush=True)
    return out


def main() -> int:
    print("RE-VALIDATION on backfilled clean data (sequential)\n" + "=" * 70, flush=True)
    runs = []
    started = time.time()
    for label, mod in STRATEGIES:
        for window_label, since, until in WINDOWS:
            try:
                runs.append(run_one(label, mod, window_label, since, until))
            except Exception as e:
                print(f"      FAILED {label}/{window_label}: {e}", flush=True)
                traceback.print_exc()
                runs.append({"strategy": label, "window": window_label, "error": str(e)})

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"runs": runs, "stale_cagr": STALE_CAGR}, indent=2))

    # Comparison table: new clean CAGR vs stale, both windows.
    print("\n" + "=" * 78)
    print("  CAGR: NEW (clean) vs STALE (pre-backfill), by window")
    print("=" * 78)
    print(f"  {'strategy':<20} {'window':<10} {'new':>9} {'stale':>9} {'delta':>9} {'trades':>7}")
    print("  " + "-" * 70)
    for label, _ in STRATEGIES:
        for window_label, _, _ in WINDOWS:
            r = next((x for x in runs if x["strategy"] == label and x["window"] == window_label), None)
            if not r or "error" in r:
                print(f"  {label:<20} {window_label:<10} {'ERR':>9}")
                continue
            stale = STALE_CAGR.get(label, {}).get(window_label)
            ds = f"{r['cagr_pct']-stale:+.2f}pp" if stale is not None else "  (n/a)"
            ss = f"{stale:+.2f}%" if stale is not None else "   —"
            print(f"  {label:<20} {window_label:<10} {r['cagr_pct']:>+8.2f}% {ss:>9} {ds:>9} {r['closed']:>7}")
        print("  " + "-" * 70)
    print(f"\nTotal elapsed: {(time.time()-started)/60:.1f} min  ->  {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
