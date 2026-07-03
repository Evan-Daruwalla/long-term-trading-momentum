# Paper-Trading Operations Guide

Built 2026-05-27. **Updated 2026-05-28 after data audit + v1-v2 parallel decision.**

## Strategies running in parallel
1. **mom_v1_paper** (top-100, more diversified) — inceptioned 2026-05-01
2. **mom_v2_paper** (top-50, more concentrated) — inceptioned 2026-05-01

Both use the same frozen momentum signal (12-1 month). Both start with $100K paper.
Compare their forward-OOS performance over time. See `memory/data_audit_2026-05-28.md`
for why we're running both: clean-data backtest shows v1 wins in-sample (9 yr,
better risk-adjusted), v2 wins held-out (2.4 yr) — needs live data to decide.

## Daily procedure (every US trading day, ~30 min after market close)

```cmd
D:\ClaudeCode\Trading\scripts\momentum\daily.bat
```

What it does:
1. Refreshes last 30 days of closes for the entire universe (~4,200 tickers,
   takes 5-8 min via yfinance)
2. Marks-to-market BOTH paper portfolios against the latest closes
3. Appends a row to `paper_nav` table per strategy

Expected output:
- `MTM 2026-MM-DD strategy=mom_v1_paper`
- `MTM 2026-MM-DD strategy=mom_v2_paper`
- TOTAL NAV reported for each

If you skip days, the next run catches up automatically (refresh window is
30 days, MTM reads whatever's in `paper_nav`).

## Monthly procedure (first US trading day of each month, after market close)

```cmd
D:\ClaudeCode\Trading\scripts\momentum\rebalance.bat
```

What it does:
1. Refreshes prices (same as daily)
2. Computes today's top-100 picks for v1 and top-50 picks for v2
3. Diffs against open positions; sells exits, buys new (BOTH sleeves)
4. Logs new NAV rows reflecting post-rebalance state

Idempotent — re-running same day with same universe is a no-op. Safe to re-run
if you're unsure whether it ran.

## Verifying state

```cmd
.venv\Scripts\python.exe -c "import sqlite3; from trading_bot.config import DB_PATH; c=sqlite3.connect(DB_PATH); print('Open positions:', c.execute(\"SELECT COUNT(*) FROM paper_positions WHERE strategy_name='mom_v2_paper' AND status='open'\").fetchone()[0]); pf=c.execute(\"SELECT cash, starting_cash, last_rebalanced_at FROM paper_portfolio WHERE strategy_name='mom_v2_paper'\").fetchone(); print(f'Cash: \${pf[0]:.2f}, Starting: \${pf[1]:.0f}, Last rebal: {pf[2]}'); nav=c.execute(\"SELECT MAX(nav_date), total_nav FROM paper_nav WHERE strategy_name='mom_v2_paper'\").fetchone(); print(f'Latest NAV: {nav[0]} \${nav[1]:,.0f}')"
```

For a friendlier view, the SQL tables are:
- `paper_portfolio` (1 row): cash + starting_cash + timestamps
- `paper_positions`: per-trade open/close history
- `paper_nav`: one row per trading day's MTM

## When things go wrong

### Price refresh fails (yfinance rate limit / network)
- `daily.bat` continues with stale prices (MTM warns about stale)
- `rebalance.bat` ABORTS (rebalance with stale ranks would create bad trades)
- Action: wait an hour, re-run

### MTM shows large stale_count
- Means many positions don't have a recent cached close
- Could be: yfinance dropped a delisted ticker, or your refresh hasn't run in
  a while
- Action: run `daily_price_refresh.py` manually with `--days 60` to widen the
  catch-up window

### Rebalance picks fewer than 50 names
- Universe might be smaller than usual (rare — universe is ~2,700-3,200 names)
- Or momentum has insufficient history for many names (check log line:
  "Ranked top-N momentum")
- Action: investigate `tradeable_universe()` output for that as_of

### "table paper_X doesn't exist"
- Schema migration didn't run
- Action: `.venv\Scripts\python.exe -c "from trading_bot.db import init_db; init_db()"`

## What's not built (deferred, do post-deployment)

### Slippage realism check (build after first month)
After ~20 rebalance fills, compare the assumed 5 bps half-spread to actual
yfinance close-vs-next-open-vs-close differences for our specific picks.
Mom_v2's picks are volatile small/mid-caps (median 60-day stdev ~3-5%/day),
where real fills could be 10-30 bps off the close depending on order timing.

Action when ready: write a script that for each closed paper position, pulls
the open/close/volume for that day from yfinance, computes implied spread,
aggregates statistics, and compares to the 5 bps backtest assumption.

### Automated scheduler
Not built deliberately — manual run keeps you aware of state in the early
weeks. After ~3 months of routine, set up Windows Task Scheduler:

```cmd
REM Daily: 4:30 PM ET = 21:30 UTC = 16:30 ET market close + 30 min
schtasks /create /tn "MomV2 Daily" /tr "D:\ClaudeCode\Trading\scripts\momentum\daily.bat" /sc daily /st 16:30 /sd 06/01/2026

REM Monthly: 1st of each month, same time
schtasks /create /tn "MomV2 Monthly Rebal" /tr "D:\ClaudeCode\Trading\scripts\momentum\rebalance.bat" /sc monthly /d 1 /st 16:30 /sd 06/01/2026
```

(These are the commands you'd run elevated. Don't enable yet.)

## Performance expectations (from backtest)

Don't expect mom_v2's backtested CAGR to materialize exactly:
- Backtest in-sample CAGR: +21.0%/yr, mean yearly Sharpe +0.23
- Backtest held-out CAGR: +26.5%/yr, mean yearly Sharpe +0.87 (likely
  regime-favorable, expect mean reversion)
- Realistic expectation: +15-22%/yr, Sharpe +0.5-0.8

What to watch for in the first 3 months:
- Drawdowns up to -30% are normal (mom_v2 has had bigger in-sample)
- Sector concentration in Tech/Healthcare (currently ~66%) is normal — mom_v2
  has no sector cap
- Small-cap picks are normal — mom's edge lives in the volatile tail

What would indicate something's wrong:
- Cash > $5,000 after rebalance (sizing math is broken)
- Open positions ≠ 50 (rebalance logic broken)
- NAV moves >5%/day with no corresponding market move (data error)
- Same picks every month (rebalance not actually running)

## Inception state (2026-05-01 first rebalance)

```
strategy_name:        mom_v2_paper
starting_cash:        $100,000
first_rebalance_date: 2026-05-01
top_n:                50
initial_picks:        ['HL', 'PRPO', 'VSAT', 'SLGL', 'SEDG', 'SATS', 'GCT',
                       'GSAT', 'UCTT', 'CLS', 'DK', 'LASR', 'ARIS', 'SNSE',
                       'CENX', 'SION', 'FBRX', 'MKSI', 'RHLD', 'CLMT',
                       'PVLA', 'PRAX', 'AGX', 'INBX', 'CDE', 'NKTR', 'TTMI',
                       'STX', 'PARR', ... + 21 more]
sector_distribution:  Technology 17, Healthcare 16, Industrials 6,
                      Basic Materials 5, Energy 3, Comm Services 3
post_rebalance_NAV:   $99,950.07 (cost: 5bps × 1.0 side = 0.05%)
```

## Files

- `trading_bot/db.py` — schema (paper_portfolio, paper_positions, paper_nav)
- `trading_bot/execution/paper_trader.py` — paper portfolio API
- `scripts/momentum/paper_rebalance.py` — monthly rebalance
- `scripts/momentum/paper_mtm.py` — daily MTM logger
- `scripts/momentum/daily_price_refresh.py` — universe price refresh
- `scripts/momentum/daily.bat` — convenience wrapper (refresh + MTM)
- `scripts/momentum/rebalance.bat` — convenience wrapper (refresh + rebal + MTM)
- `trading_bot/strategies/momentum_v2.py` — frozen strategy spec
