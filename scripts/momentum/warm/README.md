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
