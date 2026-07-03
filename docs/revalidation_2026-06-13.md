# Strategy Re-Validation on Backfilled Clean Data (2026-06-13)

After the systemic history-gap backfill (record Appendix AA) fixed ~1,556 tickers
that were missing 2019-2025 daily data, every pre-backfill backtest number became
stale. This re-runs the canonical in-sample / held-out validation for all 5
systematic strategies on the clean cache, identical methodology to
`v1_vs_v2_clean.py` (5 bps half-spread, monthly rebalance, equal-weight,
fractional shares; Sharpe = mean of per-year annualized Sharpe at 4.5% rf).
Raw results: `var/data_audit/revalidate_2026-06-13.json`
(`scripts/data_audit/revalidate_strategies.py`).

## Executive summary

The strategy picture did **not** collapse — it **clarified**.
**residual_roa_6535's leadership is confirmed as real, not an artifact of dodging
contamination.** It was only 6% phantom-contaminated, barely moved on re-run
(+0.6/+1.2pp), and is now the **in-sample CAGR champion** AND the **best
risk-adjusted sleeve** (top held-out Sharpe 1.21 and top Calmar 1.60, on a
much lower drawdown than any peer). The big correction is **mom_roa_6535**: its
in-sample CAGR **halved (9.86% → 4.89%)** — its apparent in-sample superiority was
largely phantom-inflated — though its held-out remains strong (#1 raw CAGR). The
methodology is sound: **sector_top4 (ETF-based, untouched by a stock backfill)
re-ran to −0.00pp** on held-out, a clean sanity check that the deltas elsewhere
are real signal.

## Results — new clean numbers vs stale

CAGR %, with Δ = new − stale (pp). Held-out = 2024-01→2026-05 (matches stale);
holdout_extended = 2024-01→2026-06-12 (all current clean data).

| Strategy | Window | CAGR | Δ vs stale | Sharpe | maxDD | Calmar | Trades |
|---|---|---:|---:|---:|---:|---:|---:|
| **residual_roa_6535** | in_sample | **+9.47%** | +0.61 | 0.427 | −39.4% | 0.241 | 1928 |
| | holdout | +32.07% | +1.23 | **1.212** | **−20.1%** | **1.597** | 501 |
| | holdout_ext | +34.58% | — | 1.227 | −20.1% | 1.722 | 522 |
| **mom_roa_6535** | in_sample | +4.89% | **−4.97** | 0.238 | −47.6% | 0.103 | 1903 |
| | holdout | **+35.59%** | −0.88 | 1.128 | −30.4% | 1.172 | 499 |
| | holdout_ext | **+37.37%** | — | 1.031 | −30.4% | 1.231 | 515 |
| **sector_top4** | in_sample | +8.14% | +0.27 | 0.374 | −32.0% | 0.255 | 76 |
| | holdout | +17.59% | **−0.00** | 0.906 | −16.2% | 1.085 | 22 |
| | holdout_ext | +18.53% | — | 0.980 | −16.2% | 1.143 | 22 |
| **mom_v1** | in_sample | +5.91% | +1.19 | 0.259 | −46.7% | 0.127 | 3509 |
| | holdout | +24.23% | +2.15 | 0.897 | −33.9% | 0.714 | 938 |
| | holdout_ext | +23.93% | — | 0.765 | −33.9% | 0.705 | 973 |
| **mom_v2** | in_sample | +3.54% | +0.82 | 0.188 | −53.5% | 0.066 | 1977 |
| | holdout | +26.47% | −1.52 | 0.886 | −34.8% | 0.760 | 517 |
| | holdout_ext | +25.69% | — | 0.741 | −34.8% | 0.738 | 534 |

## Clean rankings

- **In-sample CAGR:** residual (9.47) > sector (8.14) > mom_v1 (5.91) > mom_roa (4.89) > mom_v2 (3.54)
- **Held-out CAGR:** mom_roa (35.59) > residual (32.07) > mom_v2 (26.47) > mom_v1 (24.23) > sector (17.59)
- **Held-out Sharpe:** residual (1.21) > mom_roa (1.13) > sector (0.91) ≈ mom_v1 (0.90) ≈ mom_v2 (0.89)
- **Held-out Calmar:** residual (1.60) > mom_roa (1.17) > sector (1.09) > mom_v2 (0.76) > mom_v1 (0.71)

**Winner by lens:** in-sample → residual; raw held-out return → mom_roa; risk-adjusted (Sharpe & Calmar) → **residual, decisively** (its −20% max DD is ~10pp shallower than every stock peer).

## Why each strategy moved

- **residual_roa_6535 (+0.6/+1.2pp):** barely changed — least contaminated (6%
  of live book). Residual/idiosyncratic momentum strips out the market/beta
  component that the gap artifact most distorted, so it was structurally robust
  to the bug. Clean data confirms it, doesn't rescue it.
- **mom_roa_6535 (in-sample −4.97pp):** the biggest correction. Most-contaminated
  sleeve (56% live). On clean data its in-sample edge evaporates (now below
  residual, sector, and even mom_v1). Held-out holds up (#1 raw CAGR) — so it's a
  **held-out / recent-regime specialist, not the all-weather leader** the stale
  in-sample number implied.
- **sector_top4 (≈0pp):** ETF-only universe, untouched by a stock-price backfill.
  The −0.00pp held-out is the **methodology sanity check** — it proves the
  re-validation harness is consistent and the other deltas are real.
- **mom_v1 (+1.2/+2.2pp):** improved both windows — the phantoms it held were a
  net drag (fake-momentum names with poor forward returns), removed on clean data.
- **mom_v2 (+0.8 in / −1.5 held):** mixed; top-50 concentration makes it more
  sensitive to which specific names enter/leave the basket.

## Caveats — what these numbers can and cannot claim

These are honest limits; read the absolute CAGRs as **survivor-biased upper
bounds**, not achievable OOS returns.

1. **Survivorship bias (the dominant caveat, HIGH).** yfinance serves only
   currently-listed tickers, so the backfill filled **survivors only** — names
   delisted 2019-2025 are still absent. The newly-populated 2019-2023 in-sample
   tail and the entire 2024-2026 held-out are therefore biased toward names that
   survived and (often) ran up. This inflates every CAGR here. It is a
   pre-existing, structural limitation (the cache has ~4-6k currently-served
   names, never the full historical universe) that the backfill **extends into
   2019-2025** rather than introduces. Unfixable without a point-in-time / paid
   data source.
2. **Held-out concentration / IPO inflation (MEDIUM).** The held-out now includes
   backfilled recent IPOs with large real trailing momentum (BMNR/INBX/PACS/RAPP,
   +200-700%). A handful of survivor moonshots can drive the held-out CAGR, so the
   held-out edge may be **more concentration-dependent and fragile** than the
   point estimate suggests. The holdout_extended generally rising vs holdout
   (mom_roa 35.6→37.4, residual 32.1→34.6) is consistent with a few names
   continuing to run.
3. **ROA fundamentals were NOT backfilled (MEDIUM, hits mom_roa/residual
   in-sample).** The backfill added PRICE data only; the ROA tilt reads
   fundamentals/XBRL caches, whose 2015-2023 coverage may be thin/recent-biased.
   So the mom_roa/residual in-sample numbers blend clean-price momentum with a
   possibly-incomplete ROA component. residual's in-sample strength is still
   notable, but its ROA contribution there is less certain than its momentum.
4. **Causal-story nuance.** "mom_roa in-sample halved because it was 56%
   contaminated" is directionally right but the 56% is the *live-2026-holdings*
   figure; the in-sample mechanism is the *2019-2023 universe re-composition*
   (survivor names added). The drop is real and large; the precise driver is the
   tail re-composition, not the 2026 book.
5. **Apples-to-apples confirmed.** Same windows, same methodology, backtest ran on
   the 37M-row backfilled cache. sector_top4's −0.00pp held-out proves harness
   consistency.

## Bottom line

- **No sleeve was invalidated; no change to the live lineup is required.** All 5
  systematic sleeves remain reasonable strategies on clean data.
- **residual_roa_6535 is the best-supported choice** — top in-sample, top
  risk-adjusted held-out, shallowest drawdown. Its prior "leader" status survives
  re-validation and is now better-founded (it was confirmed, not contaminated).
- **mom_roa_6535 should be re-framed** from "all-weather in-sample+held-out
  champion" to "held-out / recent-regime specialist" — its in-sample superiority
  was an artifact.
- **Still unvalidated (needs PIT/delisted data, can't fix here):** the absolute
  return *levels* (survivorship-inflated), the held-out's robustness to a few
  concentrated winners, and the ROA component's in-sample contribution.
- The trustworthy forward evidence remains the **live paper-trade**, now clean
  from 2026-06-12 — that is the only truly out-of-sample test from here.
