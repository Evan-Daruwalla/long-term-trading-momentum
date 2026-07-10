"""Experiment-integrity reporting (read-only) — PRD M4.

Kill-switch tracker (M4.1) for the LLM-overlay experiments. Reads the shared
decision logs READ-ONLY and reports, per experiment: decisions to date with
scores and verdicts, pick count vs the >=30-pick kill threshold, months elapsed
vs the 12-month clock, and a score-vs-forward-return table so Evan can eyeball
whether the LLM's scores actually predict forward moves.

Two experiments, each a decision log shared by three sleeves (control / cash-veto
/ cascade):
  stock  : llm_overlay_log   -> mom_roa_top1_paper (control) /
           llm_overlay_mom_roa_top1_paper (cash) / llm_cascade_top1_paper (cascade)
  sector : sector_overlay_log -> sector_top4_paper (control) /
           llm_overlay_sector_top4_paper (cash) / llm_cascade_sector4_paper (cascade)

The kill-switch clock runs from the FIRST logged decision, not the 2026-07-01
cohort P&L reset (the reset restarted sleeve NAVs but did not wipe the decision
history; the "do scores predict returns?" question spans all decisions).

Forward returns are UNREALIZED / INTERIM: decision-date close -> latest cached
close, no annualization, no significance testing — an honest eyeball table only.

Reads price_cache + the decision logs READ-ONLY (file:...?mode=ro). Never writes
the DB; `--md` writes docs/experiment_report_<date>.md.

Usage:
  python -m scripts.momentum.experiment_report
  python -m scripts.momentum.experiment_report --md
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import date

from trading_bot.config import DB_PATH, PROJECT_ROOT

KILL_PICKS = 30
KILL_MONTHS = 12

EXPERIMENTS = [
    {"name": "stock", "log": "llm_overlay_log", "approve": "BUY", "veto": "VETO",
     "control": "mom_roa_top1_paper", "cash": "llm_overlay_mom_roa_top1_paper",
     "cascade": "llm_cascade_top1_paper"},
    {"name": "sector", "log": "sector_overlay_log", "approve": "HOLD", "veto": "VETO",
     "control": "sector_top4_paper", "cash": "llm_overlay_sector_top4_paper",
     "cascade": "llm_cascade_sector4_paper"},
]


def _ro_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _last_close(conn: sqlite3.Connection, ticker: str, d: str):
    r = conn.execute(
        "SELECT price, key_date FROM price_cache WHERE ticker=? AND kind='close' "
        "AND key_date<=? AND price IS NOT NULL ORDER BY key_date DESC LIMIT 1",
        (ticker, d)).fetchone()
    return (r["price"], r["key_date"]) if r else (None, None)


def _months_between(a: date, b: date) -> float:
    return (b - a).days / 30.44


def report_experiment(conn: sqlite3.Connection, exp: dict, today: str) -> list[str]:
    rows = conn.execute(
        f"SELECT decision_date, ticker, score, verdict, invalidation_level "
        f"FROM {exp['log']} ORDER BY decision_date, ticker").fetchall()
    lines: list[str] = []
    title = f"## {exp['name']} overlay  (log: {exp['log']})"
    lines.append(title)
    lines.append(f"sleeves: control={exp['control']} | cash-veto={exp['cash']} | "
                 f"cascade={exp['cascade']}")
    if not rows:
        lines.append("  no decisions logged yet.")
        return lines

    dates = sorted({r["decision_date"] for r in rows})
    first = date.fromisoformat(dates[0])
    months = _months_between(first, date.fromisoformat(today))
    n_dec = len(rows)
    n_appr = sum(1 for r in rows if r["verdict"] == exp["approve"])
    n_veto = sum(1 for r in rows if r["verdict"] == exp["veto"])
    lines.append(
        f"kill-switch: decisions={n_dec}/{KILL_PICKS}  "
        f"rebalance-dates={len(dates)}  months={months:.1f}/{KILL_MONTHS}  "
        f"(first {dates[0]}, latest {dates[-1]})  approve={n_appr} veto={n_veto}")
    if n_dec >= KILL_PICKS or months >= KILL_MONTHS:
        lines.append("  ** kill-switch review threshold reached — evaluate scores-vs-returns "
                     "and treatment-vs-control now. **")

    # Score-vs-forward-return table (unrealized/interim).
    lines.append("  score-vs-forward-return (UNREALIZED/INTERIM: decision close -> latest close):")
    lines.append(f"    {'date':10s} {'ticker':6s} {'score':>5s} {'verdict':7s} "
                 f"{'fwd_ret':>8s}  {'entry->latest':>16s}")
    appr_rets: list[float] = []
    veto_rets: list[float] = []
    for r in rows:
        p0, d0 = _last_close(conn, r["ticker"], r["decision_date"])
        p1, d1 = _last_close(conn, r["ticker"], today)
        if p0 and p1 and p0 != 0:
            ret = (p1 / p0 - 1.0) * 100.0
            (appr_rets if r["verdict"] == exp["approve"] else veto_rets).append(ret)
            retstr = f"{ret:+7.1f}%"
            pxstr = f"{p0:.2f}->{p1:.2f}"
        else:
            retstr = "   n/a"
            pxstr = "no close"
        lines.append(f"    {r['decision_date']:10s} {r['ticker']:6s} "
                     f"{r['score']:>5.0f} {r['verdict']:7s} {retstr:>8s}  {pxstr:>16s}")

    def _mean(xs):
        return sum(xs) / len(xs) if xs else float("nan")
    lines.append(f"  mean forward return: approve({exp['approve']})={_mean(appr_rets):+.1f}% "
                 f"(n={len(appr_rets)})  veto={_mean(veto_rets):+.1f}% (n={len(veto_rets)})")
    lines.append("  [reading: a working stock BUY signal wants approve>veto; a working veto "
                 "wants veto names to UNDERperform. n is tiny - noise, not proof.]")
    lines.extend(divergence_lines(conn, exp))
    return lines


def divergence_lines(conn: sqlite3.Connection, exp: dict) -> list[str]:
    """Control-vs-treatment NAV divergence (M4.2), %-from-inception + gap vs
    control in $ and pp. All three sleeves share the 2026-07-06 cohort inception
    and a $100k start, so %-from-inception is directly comparable."""
    out = ["  control-vs-treatment NAV divergence (paper_nav, %-from-inception):"]
    sleeves = [("control", exp["control"]), ("cash-veto", exp["cash"]),
               ("cascade", exp["cascade"])]
    data: dict[str, tuple[str, float, float]] = {}
    for label, s in sleeves:
        nav = conn.execute(
            "SELECT nav_date, total_nav FROM paper_nav WHERE strategy_name=? "
            "ORDER BY nav_date DESC LIMIT 1", (s,)).fetchone()
        start = conn.execute(
            "SELECT starting_cash FROM paper_portfolio WHERE strategy_name=?", (s,)).fetchone()
        if nav and start and start["starting_cash"]:
            pct = (nav["total_nav"] / start["starting_cash"] - 1.0) * 100.0
            data[label] = (nav["nav_date"], nav["total_nav"], pct)
    if "control" not in data:
        out.append("    (no control NAV yet)")
        return out
    _cd, cnav, cpct = data["control"]
    for label, s in sleeves:
        if label not in data:
            out.append(f"    {label:10s} {s:34s} (no NAV yet)")
            continue
        d, nav, pct = data[label]
        gap = "" if label == "control" else (
            f"   gap vs control: ${nav - cnav:+,.0f} / {pct - cpct:+.2f}pp")
        out.append(f"    {label:10s} {s:34s} nav@{d}=${nav:>10,.0f} ({pct:+.2f}%){gap}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true",
                    help="Also write docs/experiment_report_<date>.md")
    args = ap.parse_args()

    conn = _ro_connect()
    today = date.today().isoformat()
    out: list[str] = [f"# LLM-overlay experiment report - {today}",
                      "Read-only; forward returns are unrealized/interim.", ""]
    for exp in EXPERIMENTS:
        out.extend(report_experiment(conn, exp, today))
        out.append("")

    text = "\n".join(out)
    print(text)

    if args.md:
        path = PROJECT_ROOT / "docs" / f"experiment_report_{today}.md"
        path.write_text(text + "\n", encoding="utf-8")
        print(f"\nWrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
