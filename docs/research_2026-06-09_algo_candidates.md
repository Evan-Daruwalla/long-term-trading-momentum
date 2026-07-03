# Trading-algorithm landscape research — top-5 candidates (2026-06-09)

Full survey of algorithmic-trading strategy families, scored against THIS
project's constraints, with a ranked top-5 proposal. Written per user request
("research all types of trading algorithms, propose top 5 for most profit").

---

## 0. Method and honest framing

**Constraints this was scored against** (verified in code/docs 2026-06-09):
- **Long-only until age 18** — no short support in `paper_trader.py`, no margin
  account possible. Leveraged ETFs are allowed (cash products, no margin).
- **EOD daily data** (yfinance closes, SQLite cache, ~4,350 tickers + ETFs).
  No intraday execution. Signals computed after close, fills modeled at close.
- **Cost model**: 5–30 bps half-spread tested; strategies must survive 30 bps.
- **Validation discipline**: in-sample 2015-23 + held-out 2024-26.5, frozen
  regression tests at d=0.0000pp, "in-sample-is-trustworthy" rule for
  regime-dependent disagreements.
- **Operational**: monthly rebalance (manual), daily MTM (scheduled task).

**Two mandatory haircuts applied to every published number:**
1. **McLean–Pontiff decay**: anomaly returns are on average **26% lower
   out-of-sample and 58% lower post-publication**. Decay is worst for the
   anomalies with the highest in-sample returns. Every "expected CAGR" below
   is the published number cut by ~40-60%.
2. **Project base rate**: this project has run **23 documented attempts and
   produced exactly 1 deployable winner** (mom_roa_6535). That ~4% hit rate
   matches the academic factor-replication literature. Assume any candidate
   below is more likely to FAIL validation than pass it.

"Most profit" is interpreted as: **expected net portfolio contribution =
expected CAGR × probability of surviving the project's own validation**, not
raw backtest CAGR (which is how you end up buying a 5,127,681% reversal
artifact — see Attempt 9).

---

## 1. Full landscape scan

| # | Family | Evidence quality | Feasible here? | Status / verdict |
|---|--------|-----------------|----------------|------------------|
| 1 | Cross-sectional stock momentum | Strong, decades | Yes | **OWNED** — mom_v1/v2/roa deployed |
| 2 | Momentum construction upgrades (residual mom, 52-wk-high) | Strong academic | Yes, zero new data | **TOP-5 CANDIDATE** |
| 3 | Fundamental factors solo (quality, accruals, value) | Moderate | Yes | TESTED — real but weak standalone (+5-13%/yr), all combos failed |
| 4 | Multi-factor combos | Mixed | Yes | TESTED — 1 winner (mom_roa_6535) / 22 failures; closed |
| 5 | Classic TAA / dual momentum (GEM, Faber GTAA) | Decayed post-pub | Yes | REJECT as profit engine — GEM 17.4%→5.9%/yr post-2013; Faber = defensive ~10%/yr |
| 6 | Leveraged-ETF trend rotation (Gayed LRS) | Moderate, 90-yr backtest | Yes (LETFs = no margin needed) | **TOP-5 CANDIDATE** |
| 7 | Long-short momentum, vol-targeted (Barroso–Santa-Clara) | Strong + OWN held-out result | Blocked until 18; prep now | **TOP-5 CANDIDATE** (activation program) |
| 8 | Volatility risk premium (VIX-term-structure-gated short-vol ETP) | Strong economic logic, 80% contango | Yes — ^VIX/^VIX3M already cached | **TOP-5 CANDIDATE** |
| 9 | Seasonality: turn-of-month | Persistent 1897→2020s | Yes, trivial | **TOP-5 CANDIDATE** |
| 10 | Seasonality: overnight effect | Real but TC-fatal | No | REJECT — daily round trips eat 100% of edge at retail costs |
| 11 | Short-term reversal | Real at institutional horizon | No | TESTED — held-out -50.8%/yr; catastrophic. Closed |
| 12 | Pairs / stat-arb | Decaying since 2010 | No (needs shorts) | REJECT — blocked until 18 AND documented decade-long decay |
| 13 | PEAD / earnings events | Weak at EOD retail | Marginal | TESTED — failed (yfinance data starts 2020, dilutes signal). Closed |
| 14 | Index-add arbitrage | Vanished | No | REJECT — Greenwood–Sammon: effect ≈ 0 since 2010s; needs announcement-speed execution |
| 15 | Insider / Form 4 | None found here | Had full pipeline | CLOSED 2026-05-22 after walk-forward + held-out |
| 16 | ML stock-picking (GKX-style) | Real in academia | Risky here | DEFER — GKX's own result: dominant signals are *momentum, liquidity, volatility* (already owned); solo-researcher overfit risk after a data-contamination crisis is disqualifying for now |
| 17 | Crypto trend (BTC) | Moderate | Paper yes; live no (18+ KYC) | Honorable mention — see §3 |
| 18 | Options strategies (covered calls, put selling) | Strong premia | No | REJECT — age 18+ + options approval, no options data in stack |
| 19 | HFT / market making | N/A | No | REJECT — infrastructure class impossible at retail EOD |

---

## 2. The top 5

Ranked by expected net portfolio contribution (expected CAGR × survival
probability × deployability). Every candidate includes kill criteria up front —
same bar that closed Form 4.

---

### #1 — Vol-targeted long-short momentum: the activation program
**(highest measured edge in the entire project; blocked by age, so the work is
preparation, not deployment)**

- **Thesis**: the project's OWN Attempt 16 (2026-05-28) found vol-targeted
  long-short momentum (Barroso–Santa-Clara) produced the best risk-adjusted
  result of all 23 attempts: **held-out +35-41% CAGR, Sharpe 1.31-1.35, max DD
  -21 to -26%** vs long-only mom_v2's +28.8%/0.90/-34%. This is in-house
  out-of-sample evidence, more trustworthy than anything from the web survey.
- **Why it's #1**: it's the only candidate with a directly measured, internally
  validated edge of this size. Academic literature (Daniel–Moskowitz 2016,
  Barroso–Santa-Clara 2015) independently confirms the mechanism.
- **The blocker**: in-sample (2015-23, contains 2022 momentum crash) the 21-day
  vol lookback reacted too slowly — NAV went briefly negative (bust) before
  recovering. NOT deployable until that's fixed, and not live-tradeable until
  margin access at 18.
- **The program (can start now)**:
  1. Fix the crash response: 5-day vol lookback × 8% vol target × hard gross
     cap (≤1.5x) × per-leg loss cap. Re-run both windows. Success = no bust
     in-sample AND held-out Sharpe stays >1.1.
  2. Add realistic short frictions: borrow-rate table (hard-to-borrow names),
     short-proceeds interest, locate failures on small-caps. The 2% flat APY
     tested is optimistic for the bottom-50 cohort.
  3. Extend paper_trader with short positions (qty<0, margin accounting) and
     run it as a paper sleeve for months BEFORE 18 — so the day margin access
     exists, there's already forward out-of-sample evidence.
- **Honest expected net**: if the in-sample fix works, 15-25% CAGR at Sharpe
  ~1.0-1.3 deployed. If it doesn't, the candidate dies — which is itself
  cheap information.
- **Effort**: ~2-3 sessions. **Kill criteria**: any in-sample bust after the
  fix; held-out Sharpe < long-only mom_roa_6535 (+1.11); borrow-adjusted edge
  < +5pp vs long-only.

---

### #2 — VIX-term-structure-gated short-volatility sleeve
**(largest documented risk premium accessible long-only at EOD; genuinely new
alpha source for this portfolio)**

- **Thesis**: VIX futures trade in contango ~80% of the time; inverse-vol ETPs
  (SVXY, -0.5x) harvest the roll yield. Ungated, buy-and-hold short-vol ≈ S&P
  returns with catastrophic tail risk (Feb 2018: XIV -90%+ in one day, dead).
  Gated — long SVXY only when VIX/VIX3M < ~0.95 (contango) AND SPY above its
  ~275-day MA, else cash/T-bills — the documented result is "captures most of
  the upside while avoiding the worst crashes, considerable outperformance
  over the S&P 500."
- **Why it fits**: ^VIX + ^VIX3M are ALREADY cached (3,016 days, fetched for
  Attempt 18). The failed Attempt 18 used the VIX ratio as a position scaler
  on stock momentum — a completely different use. Here the term structure IS
  the strategy. SVXY/VIXY daily closes are one yfinance fetch away. Daily
  signal checking fits daily.bat. Uncorrelated with momentum sleeves by
  construction (different premium).
- **Honest expected net**: post-2018 SVXY is only -0.5x, so published pre-2018
  numbers (XIV-era 30-40% CAGR) must be roughly halved BEFORE the
  McLean–Pontiff haircut. Realistic: **10-20% CAGR sleeve, Sharpe 0.8-1.1,
  with rare -30 to -50% months** when a vol spike outruns the EOD gate
  (the gate signals at close; the crash happens intraday). Sizing must assume
  a single -50% day CAN happen.
- **Implementation**: fetch SVXY+VIXY history; backtest the gate on 2015-23 +
  2024-26.5 (includes Feb-2018-adjacent regime via VIXY proxies? no — SVXY
  -0.5x data starts post-Feb-2018 re-lever; backtest the SIGNAL on VIX futures
  proxy indices ^SPVXSP if needed, or accept 2019+ data with the 2020 COVID
  crash + 2022 + Aug-2024 VIX spike + Apr-2025 tariff spike as the stress
  tests). ~1-2 sessions.
- **Kill criteria**: gated version doesn't beat SPY on Sharpe over the test
  window; or any single-day loss > the sleeve's modeled worst case (signals
  the gate doesn't work at EOD); or in-sample/held-out disagree → in-sample
  rules.

---

### #3 — Residual momentum + 52-week-high momentum (flagship construction sweep)
**(cheapest test with the strongest academic evidence; attacks the project's
known weak point — momentum-crash drawdowns)**

- **Thesis**: the flagship's biggest measured problem is DD (in-sample -55%,
  the 2022 momentum crash). Two alternative CONSTRUCTIONS of the same momentum
  signal have ~2x the risk-adjusted return of standard 12-1 momentum in the
  literature, specifically because they dodge momentum crashes:
  - **Residual momentum** (Blitz–Huij–Martens): rank on the residual of each
    stock's returns after regressing out market beta — monthly Sharpe 0.48 vs
    0.25 for total-return momentum (1925-2015), profits persist for years
    instead of reversing, and the strategy sidesteps the beta-driven crash
    mechanism (crashes happen when the loser leg's high-beta names rip back).
  - **52-week-high momentum** (George–Hwang): rank on price/52-wk-high —
    0.65%-1.13%/mo vs 0.38-0.46%/mo for standard momentum, with crash
    resistance documented separately.
- **Why it fits**: ZERO new data. Both signals compute from the existing price
  cache. The existing `factor_backtest` harness + frozen windows + mom_roa
  Z-combiner all reuse directly. Test matrix: {residual mom, 52wk-high, std
  mom} × {solo, ×ROA 65/35} × 2 windows ≈ 12 sequential runs.
- **Honest expected net**: academic 2x Sharpe will NOT survive intact
  (long-only retail + decay). Success looks like: held-out CAGR within a few
  pp of mom_roa_6535 (+36.5%) with **materially smaller in-sample DD**
  (-55% → -35% or better) and equal-or-better Sharpe on both windows.
- **Effort**: ~1 session (the harness exists). This is the best
  effort-to-information ratio of the five.
- **Kill criteria**: standard — must beat mom_roa_6535 on both windows on
  Sharpe AND not lose >2pp CAGR held-out; else it joins the 22 failures.

---

### #4 — Leveraged-ETF trend rotation (Gayed "Leverage for the Long Run")

- **Thesis**: hold a leveraged S&P/Nasdaq ETF (SSO/QLD 2x or UPRO/TQQQ 3x)
  while the index is above its 200-day MA; rotate to T-bills (BIL) below it.
  The MA filter doesn't predict returns — it predicts VOLATILITY REGIME, and
  leveraged ETFs' daily-reset decay is what the filter avoids. Gayed's
  1928-2020 backtest: ~26.7%/yr for the 3x variant vs ~10% buy-and-hold.
- **Why it's NOT redundant with the failed trend200 test**: Attempt "trend200"
  gated a CROSS-SECTIONAL stock portfolio on SPY's MA — the stock picks' alpha
  didn't co-move with SPY's trend, so the gate just amputated upside (-21pp
  held-out). Here the gated asset IS the index, so signal and asset are the
  same thing. Different mechanism, untested in this project.
- **Why long-only feasible**: LETFs are cash products — a custodial/cash
  account can hold them; no margin involved. (Live trading still waits for 18;
  paper now.)
- **Honest expected net**: the 26.7% is in-sample-of-publication (2016 paper,
  but the long backtest is robust across MA lengths 3-12mo per Faber's
  parameter-stability work). Post-haircut: **12-20% CAGR with -40 to -60%
  intra-regime DD tolerance for 3x; 2x roughly halves both**. Known failure
  mode: whipsaw years (2015-16, 2018, COVID re-entry, 2022 false re-entries) —
  each whipsaw costs ~2-6%. A decade of chop would underperform buy-and-hold.
- **Implementation**: fetch SSO/UPRO/QLD/TQQQ/BIL (~5 min); single-asset
  rotation backtest is simpler than anything already in the repo. ~1 session
  including TC sensitivity.
- **Kill criteria**: doesn't beat SPY buy-and-hold on CAGR over BOTH windows
  net of 30bps; or in-sample DD exceeds -65% (un-deployable psychologically
  regardless of CAGR).

---

### #5 — Turn-of-month + T-bill carry sleeve

- **Thesis**: equities earn abnormal returns in the ~4-day window around
  month-end (documented 1897→2020s, robust across 20-35 countries, survives
  size/rebalancing controls). Rule: buy SPY at close 1 day before month-end,
  sell at close of trading day 3 of the new month; sit in BIL the other ~80%
  of days. Quantpedia's long-window numbers: **7.2%/yr at Sharpe 1.04 with
  only ~20% market exposure**; add ~4% T-bill yield on the idle 80% → ~10-11%
  total at a fraction of equity DD.
- **Why it fits**: 1 round trip/month on SPY (~1bp spread) = TC-immune. Zero
  new data (SPY cached; add BIL). Mechanically uncorrelated with everything
  else in the portfolio (it's flat 80% of the time). Monthly cadence matches
  existing ops; the trade dates align with the existing rebalance calendar.
- **Honest expected net**: this is the LOWEST-CAGR candidate (~9-11%) — it's
  in the top 5 on survival probability (the effect has persisted 120+ years
  through every publication cycle) and capital efficiency, not on raw profit.
  It's the "control" of the candidate set: if THIS fails validation here, the
  test harness is suspect.
- **Effort**: ~half a session. **Kill criteria**: in-sample Sharpe < 0.7 or
  beats neither SPY-Sharpe nor BIL-CAGR; effect concentrated in <30% of months
  (sign of fragility).

---

## 3. Honorable mentions (excluded from top 5, with reasons)

- **BTC trend following**: real academic support (trend works on BTC like
  20th-century commodities; one decade-long walkforward claims 255%/yr —
  treat as wildly optimistic). Excluded because: live trading needs 18+ KYC
  at every major exchange, single-asset regime risk (-70%+ DD), and the claims
  fail the smell test that killed restricted universes. Paper-feasible via
  yfinance BTC-USD if curiosity wins; revisit at 18.
- **Sector abs-momentum gate** (Faber-style 10-mo SMA per sector → BIL on the
  existing sector_top4): cheap upgrade, but expected value is DD reduction,
  not profit. Worth a 1-hour test someday; not top-5 material.
- **ML ranking layer (GKX-style)**: deferred, not dead. The honest reading of
  Gu–Kelly–Xiu is that ML's dominant signals are momentum/liquidity/volatility
  — already owned here. Revisit only with a pre-registered protocol (one
  model, one hyperparameter budget, frozen windows, no peeking).

## 4. Recommended sequencing

1. **#3 residual/52wk momentum** first — 1 session, zero new data, directly
   upgrades the flagship. Highest information-per-hour.
2. **#5 turn-of-month** second — half session, near-certain to validate,
   establishes the harness works on calendar strategies.
3. **#2 gated short-vol** third — 1-2 sessions, new data fetch, biggest new-
   premium prize. Size small (≤$25k paper).
4. **#4 Gayed LETF rotation** fourth — 1 session.
5. **#1 L/S activation program** ongoing in background — it's the biggest
   prize but pays off at 18; start with the 5-day-vol crash fix since that's
   pure research.

Each candidate gets the standard treatment: backtest both windows → frozen
spec if it passes → paper sleeve → months of forward evidence. No candidate
goes live (at 18) without surviving all three.

## 5. Sources

- McLean & Pontiff, [Does Academic Research Destroy Stock Return Predictability?](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2156623) (26%/58% decay)
- Blitz, Huij & Martens, [Residual Momentum](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2319861); [Alpha Architect summary of idiosyncratic momentum](https://alphaarchitect.com/swedroe-spotlight-enhancing-momentum-strategies-via-idiosyncratic-momentum/)
- George & Hwang, [The 52-Week High and Momentum Investing](https://www.bauer.uh.edu/tgeorge/papers/gh4-paper.pdf); [Momentum Crashes and the 52-Week High](https://epublications.marquette.edu/cgi/viewcontent.cgi?article=1168&context=fin_fac)
- [Tradable Risk Factors for Institutional and Retail Investors](https://academic.oup.com/rof/article/29/1/103/7755053) (2-4%/yr implementation shortfall; momentum most implementable retail)
- Antonacci GEM post-publication: [pre/post analysis](https://www.linkedin.com/pulse/dual-momentum-pre-post-publication-performance-abdennour-aissaoui) (17.43%→5.89%/yr), [Newfound fragility study](https://blog.thinknewfound.com/2019/01/fragility-case-study-dual-momentum-gem/)
- Gayed, [Leverage for the Long Run](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2741701); [Brightwork analysis](https://www.brightworkresearch.com/using-letfs-combined-with-the-200-day-moving-average-trading-approach/) (26.7%/yr 3x variant); [QuantConnect replication](https://www.quantconnect.com/research/15351/leveraged-etfs-with-systematic-risk-management/)
- Faber, [A Quantitative Approach to Tactical Asset Allocation](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461) (parameter stability 3-12mo)
- VRP/short-vol: [Quantpedia VIX term structure](https://quantpedia.com/strategies/exploiting-term-structure-of-vix-futures); [Systematic Individual Investor — Volatility Trading Traps](https://systematicindividualinvestor.com/2019/11/01/volatility-trading-traps/) (gated SVXY rules: contango + 275-DMA); [Macrosynergy VIX term structure as signal](https://macrosynergy.com/research/vix-term-structure-as-a-trading-signal/)
- Turn-of-month: [Quantpedia ToM in Equity Indexes](https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes) (7.2%/yr, Sharpe 1.04, 20% exposure); [QuantSeeker — Do They Still Work?](https://www.quantseeker.com/p/turn-of-the-month-strategies-do-they)
- Overnight anomaly rejection: [Alpha Architect — Trading Costs Wipe Out the Overnight Return Anomaly](https://alphaarchitect.com/trading-costs-wipe-out-the-overnight-return-anomaly/)
- Index effect: [Greenwood & Sammon — The Disappearing Index Effect](https://www.nber.org/system/files/working_papers/w30748/w30748.pdf)
- Pairs decay: [Yale — Examining Pairs Trading Profitability](https://economics.yale.edu/sites/default/files/2024-05/Zhu_Pairs_Trading.pdf)
- ML: [Gu, Kelly & Xiu — Empirical Asset Pricing via Machine Learning](https://dachxiu.chicagobooth.edu/download/ML.pdf)
- Trend/managed futures decade: [Morningstar — Managed-Futures Funds Look to Rebound](https://www.morningstar.com/alternative-investments/managed-futures-funds-look-rebound-can-they-help-diversify-your-portfolio) (typical fund -2.3%/yr annualized recent)
- BTC trend: [A Decade of Evidence of Trend Following in Cryptocurrencies](https://arxiv.org/pdf/2009.12155)
