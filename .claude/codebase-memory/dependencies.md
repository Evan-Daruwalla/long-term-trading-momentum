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
- pytest — runs the FROZEN regression tests (see testing.md).
- streamlit — the dashboard (`web.py`, :8501).
- alpaca SDK — the paper-account mirror (`trading_bot/execution/alpaca_client.py`,
  `alpaca_accounts.py`, `alpaca_sync.py`); PAPER only, `--execute`-gated.
- SQLite (stdlib) — `var/trades.db` (~5 GB); no ORM.

## Constraints
- `alpaca_keys.env` (live keys) is never committed/printed/moved (see security.md).
- Don't add a cache writer that ignores the `auto_adjust=False` convention.
