# scripts/momentum/warm/

Cache-warming utilities. Run once per data-source addition, not regularly.

| Script | Caches | Run when |
|---|---|---|
| `warm_xbrl.py` | `xbrl_facts` table from SEC EDGAR XBRL API | new tickers or new us-gaap concepts |
| `warm_fundamentals.py` | `fundamentals_cache` (yfinance snapshot, has lookahead) | rarely; mostly for sector + name |
| `warm_volumes.py` | `price_cache` volume column | adding volume data (currently disabled in universe filter) |
| `warm_sectors.py` | `sectors_cache` from yfinance | quarterly refresh |

All idempotent / resumable. Run from project root via
`python -m scripts.momentum.warm.NAME [options]`.

Note: spike-cleanup + universe.MAX_HIST_RATIO filter handle data quality
issues without needing fresh fetches. Re-warming is rarely needed.

> **Undocumented warmers, added 2026-09-20 (audit finding 39).** The table
> above covers 4 of the 7 real scripts here. Also present:
> `warm_held_volumes.py`, `warm_sector_etfs.py`, `warm_vol_letf_etfs.py`.
> The latter two deliberately cache ETF prices; they are kept out of the stock
> universe by `universe.NON_STOCK_TICKERS` at the *read* layer, not by the
> warmers — which is the correct design, not a gap.
>
> **`warm_fundamentals.py` has a known data-poisoning bug** (audit finding 36,
> fixed in a later stage): any transient yfinance error writes an all-NULL row
> that `_already_fetched()` then treats as done forever. Its sibling
> `warm_volumes.py` retries with backoff and refuses to write a fake-success
> row — that is the pattern to copy.
