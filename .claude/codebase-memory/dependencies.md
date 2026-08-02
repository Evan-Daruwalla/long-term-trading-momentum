# dependencies — Trading

Last updated 2026-07-15. Canonical home for the dependency set; facts from
CLAUDE.md + architecture.md. Exact version pins live in the repo's requirements
file — not duplicated here (drift). After ANY dependency change, run the frozen
tests (d=±0.0000pp) before trusting.

## Runtime + libraries
- Python via a local venv — ALWAYS invoke as `.venv\Scripts\python.exe -m <module>`
  from the repo root (see tooling.md).
- **yfinance** — market-data source. **CRITICAL: `auto_adjust=False`** (closes
  split-adjusted, dividend-UNadjusted; the #1 data invariant — see data.md).
- pandas / numpy — factor computation, backtests.
- **pytest is NOT installed** (corrected 2026-07-28). The frozen regression tests
  run as a module: `.venv\Scripts\python.exe -m trading_bot.strategies.test_strategies`
  (`__main__` block in `test_strategies.py`). See testing.md.
- streamlit + plotly — the dashboard (`web.py`, :8501).
- httpx — HTTP client (yfinance-adjacent calls + the Alpaca wrapper).
- markdown — HTML twins (`scripts/render_record_html.py`, reused by
  `render_daily_report_html.py`). Was installed-but-unpinned; added to
  `requirements.txt` 2026-07-28.
- watchdog — `scripts/watch_record_html.py` auto-render-on-save. Was
  installed-but-unpinned; added to `requirements.txt` 2026-07-28.
- rich — console output.
- **No alpaca package is installed** (corrected 2026-07-28 — there is no
  `alpaca-py`/`alpaca-trade-api` dependency). `trading_bot/execution/alpaca_client.py`
  is deliberately a small hand-rolled **httpx** wrapper over the REST API
  (see its module docstring, line 3); `alpaca_accounts.py` / `alpaca_sync.py`
  build on it. PAPER only, `--execute`-gated.
- SQLite (stdlib) — `var/trades.db` (~5 GB); no ORM.

## Constraints
- `alpaca_keys.env` (live keys) is never committed/printed/moved (see security.md).
- Don't add a cache writer that ignores the `auto_adjust=False` convention.
