"""Diagnose why momentum's in-sample alpha (+10%/yr vs SPY) collapsed
to ~0%/yr in held-out (2024-2026).

Hypotheses to test:
  H1: Mega-cap era — SPY's 2024-2025 ran on a handful of names. Equal-weight
      benchmark (RSP) would close the alpha gap.
  H2: Small-cap exposure — momentum top-100 averages smaller market caps than
      SPY. IWM (Russell 2000) might be the right benchmark.
  H3: Sample-size noise — 2.4 years is too short to detect 5-10%/yr alpha
      with high confidence given factor stdev.
  H4: Factor decay — momentum genuinely worked less well 2024+ as everyone
      figured it out / mega-caps dominated.

Outputs a per-year breakdown:
  year | momentum % | SPY % | RSP % | IWM % | alpha-vs-SPY | alpha-vs-RSP
"""
from __future__ import annotations

import json
import statistics
from datetime import date
from pathlib import Path

import yfinance as yf

ROOT = Path(r"D:\ClaudeCode\Trading")
MOMENTUM_RUNS = ROOT / "var" / "momentum" / "runs"


def _yearly_returns(curve: list[tuple[str, float]]) -> dict[str, float]:
    """First-of-year to last-of-year cumulative return, by calendar year.
    Uses the equity-curve points falling in each year — first one in
    January as start, last in December as end."""
    by_year: dict[str, list[tuple[str, float]]] = {}
    for iso, val in curve:
        by_year.setdefault(iso[:4], []).append((iso, val))
    out = {}
    for y, pts in by_year.items():
        if len(pts) < 2:
            continue
        out[y] = (pts[-1][1] / pts[0][1] - 1.0) * 100.0
    return out


def _yearly_daily_sharpe(curve, risk_free_apy=0.045):
    by_year = {}
    prev_val = prev_year = None
    for iso, val in curve:
        y = iso[:4]
        if prev_val and prev_val > 0 and y == prev_year:
            by_year.setdefault(y, []).append(val / prev_val - 1.0)
        prev_val, prev_year = val, y
    out = {}
    rf = risk_free_apy / 252
    for y, rets in by_year.items():
        if len(rets) < 20:
            continue
        sd = statistics.pstdev(rets)
        if sd == 0:
            out[y] = 0.0
        else:
            out[y] = ((statistics.fmean(rets) - rf) / sd) * (252 ** 0.5)
    return out


def _benchmark_curve(ticker: str, start: str, end: str,
                     start_capital: float) -> list[tuple[str, float]]:
    """Construct an equity curve buying $start_capital of ticker at start
    and holding. auto_adjust=True so the closes already include dividends."""
    df = yf.download(ticker, start=start, end=end, auto_adjust=True,
                     progress=False, group_by="ticker", actions=False)
    if df is None or df.empty:
        raise SystemExit(f"yfinance returned nothing for {ticker}")
    if ticker in df.columns.get_level_values(0):
        closes = df[ticker]["Close"].dropna()
    else:
        closes = df["Close"].dropna()
    px0 = float(closes.iloc[0])
    shares = start_capital / px0
    return [(ts.date().isoformat(), float(p) * shares)
            for ts, p in closes.items()]


def _print_yearly_table(label: str, mom_yr: dict, bench_yrs: dict[str, dict]):
    print(f"\n=== {label} ===")
    all_years = sorted(set(mom_yr) | {y for d in bench_yrs.values() for y in d})
    cols = ["Year", "Mom %"] + [f"{b} %" for b in bench_yrs] + \
           [f"alpha-vs-{b}" for b in bench_yrs]
    widths = [6, 9] + [9] * len(bench_yrs) + [13] * len(bench_yrs)
    line = "".join(c.rjust(w) for c, w in zip(cols, widths))
    print(line)
    print("-" * len(line))
    for y in all_years:
        m = mom_yr.get(y)
        row = [y, f"{m:+.2f}" if m is not None else "—"]
        for b, br in bench_yrs.items():
            v = br.get(y)
            row.append(f"{v:+.2f}" if v is not None else "—")
        for b, br in bench_yrs.items():
            v = br.get(y)
            row.append(f"{m-v:+.2f}" if (m is not None and v is not None) else "—")
        print("".join(c.rjust(w) for c, w in zip(row, widths)))
    # Annualized summary
    if mom_yr:
        ms = [v / 100 for v in mom_yr.values()]
        m_cagr = (1 + statistics.fmean(ms))  # approx — use geometric below
        # geometric mean
        prod = 1.0
        for v in ms:
            prod *= (1 + v)
        n = len(ms)
        m_cagr = prod ** (1 / n) - 1
        print(f"  Momentum CAGR  : {m_cagr*100:+.2f}%/yr  ({n} yrs)")
    for b, br in bench_yrs.items():
        if br:
            prod = 1.0
            for v in br.values():
                prod *= (1 + v / 100)
            n = len(br)
            cagr = prod ** (1 / n) - 1
            print(f"  {b} CAGR        : {cagr*100:+.2f}%/yr")


def diagnose(run_file: Path, label: str):
    d = json.loads(run_file.read_text())
    since = d["since"]; until = d["until"]
    curve = d["equity_curve"]
    start_cap = curve[0][1]
    print(f"\n{'#'*70}\n# {label}: {since} -> {until}  curve_len={len(curve)}")
    print(f"# start=${start_cap:,.0f}  end=${curve[-1][1]:,.0f}  "
          f"total={(curve[-1][1]/curve[0][1]-1)*100:+.2f}%")

    # Build benchmark curves
    benches = {}
    for ticker in ["SPY", "RSP", "IWM"]:
        try:
            bc = _benchmark_curve(ticker, since, until, start_cap)
            benches[ticker] = bc
            tret = (bc[-1][1] / bc[0][1] - 1) * 100
            print(f"#   {ticker}: {len(bc)} days, total {tret:+.2f}%")
        except Exception as e:
            print(f"#   {ticker}: FAILED {e}")

    mom_yr = _yearly_returns(curve)
    bench_yrs = {b: _yearly_returns(c) for b, c in benches.items()}
    _print_yearly_table(label, mom_yr, bench_yrs)

    # Per-year Sharpe
    mom_sh = _yearly_daily_sharpe(curve)
    bench_sh = {b: _yearly_daily_sharpe(c) for b, c in benches.items()}
    print(f"\n  Per-year Sharpe — {label}")
    all_years = sorted(set(mom_sh) | {y for d in bench_sh.values() for y in d})
    print(f"  {'Year':<6} {'Mom':>8} " + " ".join(f"{b:>8}" for b in bench_sh))
    for y in all_years:
        row = f"  {y:<6} {mom_sh.get(y, float('nan')):>+8.3f} "
        for b in bench_sh:
            v = bench_sh[b].get(y)
            row += f"{v:>+8.3f} " if v is not None else f"{'—':>8} "
        print(row)


def main():
    runs = [
        ("baseline in-sample",  MOMENTUM_RUNS / "20260526-011759_in_sample.json"),
        ("baseline held-out (with fractional)",
                                MOMENTUM_RUNS / "20260526-025026_mom_frac_holdout.json"),
    ]
    for label, f in runs:
        if not f.exists():
            print(f"MISSING {f}")
            continue
        diagnose(f, label)


if __name__ == "__main__":
    main()
