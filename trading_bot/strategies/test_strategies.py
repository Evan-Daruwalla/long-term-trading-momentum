"""Regression tests for frozen momentum strategies.

Runs each strategy on a fixed short window (one quarter) and asserts the
numbers match the recorded baseline within tight tolerances. Catches
silent drift in:
  - factor_backtest.run_factor_backtest (sizing, fills, MTM)
  - factors.momentum.rank_universe (lookback, skip, scoring)
  - factors.universe.tradeable_universe (filter logic, cache index)
  - market_data._MEM_PRICE (cache contents — if someone clears the DB
    these tests will fail fast, which is the desired behavior).

The tolerance is generous (5 bps on returns) because float arithmetic
order can shift slightly with cache rebuild, but a real bug will produce
deltas of percent or more, not bps.

Run via:
    python -m trading_bot.strategies.test_strategies
Or use pytest (works without configuration).
"""
from __future__ import annotations

import sys
from datetime import date

from trading_bot.strategies import momentum_v1, momentum_v2


# Short windows = fast tests (~5-10 sec each, ~30s total). The reference
# values were captured 2026-05-26 against the locked codebase.
TEST_WINDOWS = {
    "2023_Q4": (date(2023, 10, 1), date(2023, 12, 31)),
    "2025_H1": (date(2025, 1, 1),  date(2025, 6, 30)),
}

# Reference numbers captured on 2026-05-28 (RE-BASELINED after data audit).
# Format: {strategy_name: {window_name: (total_pnl_pct, closed_count)}}
# Update ONLY when the strategy is intentionally re-baselined; mismatches
# otherwise are bugs.
#
# 2026-05-28 RE-BASELINE: previous values (12.6237/67, 12.2794/37 on Q4 2023)
# were captured on contaminated data. Spike cleanup + universe.MAX_HIST_RATIO
# filter rejected ~673 corrupt tickers (yfinance unadjusted reverse-split
# artifacts) that the old strategy was buying. 2023_Q4 results improved
# (mom_v1 +1.84pp, mom_v2 +2.39pp) because the strategy is no longer holding
# data-corrupt tickers. 2025_H1 unchanged (current penny stocks already
# excluded by $5 min_price). See memory/data_audit_2026-05-28.md.
#
# 2026-06-01 RE-BASELINE (2025_H1 only): added universe.MAX_PRICE_USD filter
# ($5000 cap + allowlist). It rejected BKGM, a current-price ghost stuck at
# ~$10,000 (real history $14-$11k) that MAX_HIST_RATIO missed and that was
# ranking #1 by momentum across 2025_H1 — i.e. both sleeves were BUYING a data
# ghost and booking phantom returns. Removing it: mom_v1 2025_H1 +2.1865->
# +2.3022% (154->153 trades), mom_v2 +12.1738->+12.4171% (90->93 trades).
# 2023_Q4 unchanged (BKGM's jump wasn't in that lookback). NOTE: this ghost
# also contaminated the 2024-2026 HELD-OUT validation — see
# docs/audit_2026-06-01.md for the re-measured held-out CAGRs.
#
# 2026-06-13 RE-BASELINE (all 4): history-gap backfill. ~1,556 tickers (incl.
# AAPL, GOOGL, FN, CIEN) had only 2010-2018 + a 2026 burst cached — a multi-year
# hole — so their 12-1 momentum was measured against a stale pre-gap bar and
# phantom-ranked into the sleeves (~half of every momentum sleeve's live book).
# Backfilled the missing 2019-present daily closes from yfinance (auto_adjust=
# False), re-ran the spike cleanup (614 rows). With COMPLETE data the picks
# change in both windows: mom_v1 2023_Q4 +14.4673->+14.5547 (64->70), 2025_H1
# +2.3022->+1.8792 (153->156); mom_v2 2023_Q4 +14.6655->+14.4062 (36->38),
# 2025_H1 +12.4171->+10.2194 (93->87). The 2025_H1 drops confirm the OLD numbers
# were inflated by phantom holdings. See record Appendix AA, memory/data_audit.
EXPECTED: dict[str, dict[str, tuple[float, int]]] = {
    "momentum_v1": {
        "2023_Q4": (14.5547, 70),
        "2025_H1": (1.8792, 156),
    },
    "momentum_v2": {
        "2023_Q4": (14.4062, 38),
        "2025_H1": (10.2194, 87),
    },
}

TOL_PCT = 0.05    # 5 bps tolerance on total_pnl_pct
TOL_TRADES = 0    # exact match required on trade counts


def _capture() -> dict[str, dict[str, tuple[float, int]]]:
    """First-run capture: runs each strategy x window and prints the values
    that should populate EXPECTED. Use this to bootstrap or re-baseline."""
    out: dict[str, dict[str, tuple[float, int]]] = {}
    for name, mod in [("momentum_v1", momentum_v1),
                      ("momentum_v2", momentum_v2)]:
        out[name] = {}
        for label, (since, until) in TEST_WINDOWS.items():
            r = mod.run(since=since, until=until)
            tpnl = (r.equity_curve[-1][1] / r.equity_curve[0][1] - 1) * 100
            out[name][label] = (round(tpnl, 4), r.closed_count)
            print(f"  {name}/{label}: tpnl={tpnl:+.4f}%, closed={r.closed_count}")
    return out


def _check(strategy_name: str, mod) -> list[str]:
    """Run strategy on each window, compare to EXPECTED. Returns failures."""
    failures = []
    for label, (since, until) in TEST_WINDOWS.items():
        exp_pnl, exp_trades = EXPECTED[strategy_name][label]
        if exp_pnl is None:
            print(f"  SKIP {strategy_name}/{label}: no baseline yet")
            continue
        r = mod.run(since=since, until=until)
        tpnl = (r.equity_curve[-1][1] / r.equity_curve[0][1] - 1) * 100
        delta_pnl = tpnl - exp_pnl
        delta_trades = r.closed_count - exp_trades
        ok = abs(delta_pnl) <= TOL_PCT and abs(delta_trades) <= TOL_TRADES
        status = "OK  " if ok else "FAIL"
        print(f"  [{status}] {strategy_name}/{label}: "
              f"tpnl={tpnl:+.4f}% (exp {exp_pnl:+.4f}%, d= {delta_pnl:+.4f}pp)  "
              f"trades={r.closed_count} (exp {exp_trades}, d= {delta_trades:+d})")
        if not ok:
            failures.append(
                f"{strategy_name}/{label}: pnl d=={delta_pnl:+.4f}pp "
                f"(tol {TOL_PCT}), trades d=={delta_trades:+d} (tol {TOL_TRADES})")
    return failures


def main(argv: list[str]) -> int:
    if "--capture" in argv:
        print("CAPTURING new baseline (will overwrite EXPECTED).")
        print("Copy these values into EXPECTED in this file:\n")
        captured = _capture()
        print("\nEXPECTED = {")
        for sname, w in captured.items():
            print(f'    "{sname}": {{')
            for lbl, (p, c) in w.items():
                print(f'        "{lbl}": ({p}, {c}),')
            print(f"    }},")
        print("}")
        return 0

    print("Running strategy regression tests...")
    all_failures: list[str] = []
    for name, mod in [("momentum_v1", momentum_v1),
                      ("momentum_v2", momentum_v2)]:
        all_failures.extend(_check(name, mod))

    if all_failures:
        print(f"\nFAILED: {len(all_failures)} regression(s)")
        for f in all_failures:
            print(f"  - {f}")
        return 1
    print("\nAll regression tests passed.")
    return 0


# pytest entry points (auto-discovered if pytest is run)
def test_momentum_v1():
    assert _check("momentum_v1", momentum_v1) == []


def test_momentum_v2():
    assert _check("momentum_v2", momentum_v2) == []


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
