# Momentum Factor Portfolio — Phase 1 Design

**Goal:** A long-only US equity portfolio that ranks stocks by 12-1 month
momentum each month, holds the top N equal-weighted, and rebalances. The
*first* thing the user builds after Form 4 was definitively refuted by
walk-forward + held-out test.

**Why this and not another signal hunt:** Momentum has the strongest
academic evidence of any single equity factor (Jegadeesh-Titman 1993,
replicated thousands of times) and the most persistent post-publication.
Unlike Form 4, there's a known floor — long-only US momentum has produced
~6-8%/yr long-short, ~1-3%/yr long-only-over-market in academic
backtests. Retail reproductions typically capture 40-70% of that after
costs and clean data. This means we know roughly what success looks like
and can calibrate.

**Honest expectations.** Long-only momentum's Sharpe improvement over
SPY is modest (e.g. SPY ~0.4 → portfolio ~0.5-0.7). Drawdowns are
similar to the market (in COVID March 2020 momentum portfolios fell
~30% just like SPY). It is not a money printer. It is a real, measurable
edge that we can verify against benchmarks.

---

## 1. Universe (the #1 place to bias the result)

**Decision: point-in-time universe with liquidity + history filters.**

At each rebalance date D, a ticker is in the universe iff:
- It has a cached `close` price on D (proves it was trading)
- It has ≥252 trading days of cached `close` prior to D (need history for
  the momentum calc + minimum quality threshold)
- Close on D ≥ $5/share (excludes penny stocks where bid-ask spreads
  eat the factor and reverse-splits distort momentum signals)
- 30-day median dollar volume on D ≥ $1M (liquidity floor — at top-50
  with $100K NAV that's $2K/position, well under 1% of ADV)

This is **not** survivorship-bias-free in the academic sense (we still
only know about tickers yfinance kept), but the day-by-day membership
respects "what was tradeable on date D" — tickers delisted by 2020 are
naturally absent from 2021's rebalances. The 2010-2018 warm we ran
populated ~3,500 historical tickers per year, which is the working
universe.

**Open question:** include foreign issuers (ADRs)? Probably yes — they
trade like any other US-listed name. Default: include everything that
passes the filters.

## 2. Factor: 12-1 month momentum

**Decision: standard academic definition.**

```
momentum(ticker, D) = close(D - 1 month) / close(D - 13 months) - 1
```

Excluding the most recent month is critical — short-term reversal
contaminates a 12-month signal. This is the Jegadeesh-Titman / academic
standard. Implemented as: closing price 21 trading days before D,
divided by closing price 252 trading days before D.

Stocks without complete data in that range are dropped from ranking
(filtered out by the ≥252-day history rule above).

## 3. Portfolio construction

**Decisions:**
- **Top N = 50** stocks per rebalance, equal-weighted (each = 2% of NAV).
- **Rebalance: monthly**, on the first trading day of each calendar month.
- **Long-only.** (Can't short in your account; long captures most of the
  factor's positive return anyway.)
- **Hold to next rebalance.** No stops, no take-profits — those are
  signal-strategy concepts and don't apply to a periodic rebalance.
- **Trading:** at each rebalance, compute the new top-50 list; sell
  any current position not in the new list, buy any new-list name not
  currently held. Holdings unchanged across rebalances stay put.

**Top 50 rationale:** academic standard is decile (~10%). For a 3,000-name
universe that's 300 positions — impractical retail. Top 50 is roughly
the top 1.5%. Concentrated enough to capture the factor, diversified
enough to suppress idiosyncratic noise (rough rule: standard error of
the portfolio mean ~ 1/√50 = 14% of single-stock vol).

**Monthly rationale:** academic standard. Quarterly has less turnover
(lower costs) but slower factor capture. Monthly is the default in the
literature.

## 4. Cost model

Reuse the existing Corwin-Schultz half-spread from `broker.py`. No
commissions (modern brokers are free). No market-impact model — at $2K
per trade in a $1M ADV name, market impact is sub-bps.

Turnover is expected to be high (~80-100%/yr is normal for monthly
momentum). Costs need to be tracked seriously — at 5-10bps/side ×
100%/yr turnover, costs eat 10-20bps/yr. A real concern for a strategy
expected to produce 100-300bps/yr alpha.

## 5. Backtest mode (the engine change)

**The existing `backtest.py` event loop doesn't fit this strategy.** It's
built around "Form 4 signal fires → enter → monitor for stop/TP." A
factor portfolio is "every month, snap to new portfolio." Need a small
parallel backtest mode.

**New files:**
```
trading_bot/factors/__init__.py
trading_bot/factors/universe.py     # point-in-time universe filter
trading_bot/factors/momentum.py     # the 12-1 momentum scorer
trading_bot/execution/factor_backtest.py  # the rebalance day loop
scripts/run_momentum.py             # CLI entry point
```

**Reused unchanged:**
- `market_data.price_on_date`, `preload_caches`, the in-RAM cache
- `portfolio` (cash, positions table)
- `broker.place_buy`, `broker.close_position`, the Corwin-Schultz spread
- `BacktestResult.sharpe_by_year` (already added for the WF optimizer)
- The dashboard's optimizer-progress parsing (factor backtest emits
  similar progress lines)

**Not touched:**
- `backtest.py` — Form 4 strategy stays runnable for reference / comparison
- `scoring`, `monitor`, `runner` — all signal-strategy logic, irrelevant here

Estimated new code: ~250 LOC.

## 6. Train / test split

- **In-sample / development:** 2015-01-01 → 2023-12-31 (9 years).
  Already warmed. Use this to verify the engine works, tune the cost
  model, sanity-check the per-year Sharpe profile.
- **Held-out test:** 2024-01-01 → 2026-05-01 (2.4 years). Untouched.
  Run once, report once. Same discipline as the Form 4 walk-forward.

## 7. Evaluation metrics

- **Per-year portfolio Sharpe** (reuse `sharpe_by_year`)
- **CAGR** in-sample vs out-of-sample
- **Max drawdown** in-sample vs out-of-sample
- **Annual turnover** (sanity check on costs)
- **Coverage**: % of rebalance dates where the universe had ≥50 tradeable
  names (should be ~100% post-2015)
- **vs benchmark:** SPY's CAGR + Sharpe + max DD over the same windows

Pass bar: held-out Sharpe ≥ SPY Sharpe (modest improvement is the
realistic best case). Fail bar: held-out Sharpe < 0 or held-out CAGR
< SPY CAGR by >2%. Anything in between = unclear, run more analysis.

## 8. What's deferred to Phase 2 (NOT in scope here)

- **Other factors** (value, quality, low-vol) — different data needs.
  Value + quality require SEC fundamentals (XBRL). Low-vol is
  price-only and easy to add later.
- **Multi-factor combination** — only worth doing once each single
  factor is validated.
- **Sector neutralization, risk-parity weighting, factor timing** —
  refinements that should wait until v1 baseline is measured.

## 9. Order of work (estimate: 2-4 days)

1. **Day 1:** universe.py + momentum.py + a unit-test sanity check
   (top-50 in Jan 2020, eyeball plausibility)
2. **Day 1-2:** factor_backtest.py + run_momentum.py, smoke-test on a
   1-year window
3. **Day 2-3:** full in-sample run 2015-2023, per-year Sharpe report,
   compare to SPY
4. **Day 3-4:** held-out 2024-2026, write up the result

## 10. Decisions — locked

1. **Universe size:** top **100** equal-weighted (1% per name).
2. **Rebalance frequency:** **monthly** (first trading day of each
   calendar month).
3. **Universe inclusivity:** include **ADRs + dual-class** listings —
   anything passing the price/history filters.

## 11. Known v1 limitations to revisit

- **No volume / dollar-volume filter.** Daily volume isn't bulk-cached
  (the warm scripts only write Close prices). Skipping this for v1 means
  the universe may include illiquid micro-caps whose high momentum is
  uninvestable. Mitigated partly by the ≥$5 close filter. Add a
  volume-cache warm + liquidity filter once v1 produces a baseline.
- **yfinance survivor bias remains** at the ticker-availability level
  (tickers that delisted before today and aren't on yfinance are absent
  entirely). Same caveat as Form 4 work; report coverage % alongside
  results so the reader can calibrate.
