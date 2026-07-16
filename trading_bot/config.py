"""Static configuration: paths, SEC/EDGAR ingest settings, and the fill-cost model.

The canonical `DB_PATH`/`VAR_DIR` used across the codebase, plus the calibrated
transaction-cost constants the backtest fill model reads: per-fill half-spread
(Corwin-Schultz high-low estimator), SEC Section 31 + FINRA TAF fees, cash-sweep
APY, and the ADV liquidity guard - each pinned to a published rate with its
source cited inline, not hand-tuned per run.

The trailing TREND_/LIQUIDITY_FILTER_* flags belong to the retired Form-4
insider strategy (closed 2026-05-22); kept because the backtest engine imports them.
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VAR_DIR = PROJECT_ROOT / "var"
DB_PATH = VAR_DIR / "trades.db"

# SEC fair-access policy requires a User-Agent identifying the requester.
# https://www.sec.gov/os/accessing-edgar-data
SEC_USER_AGENT = "Evan Daruwalla evandaruwalla1@gmail.com"

# SEC caps clients at 10 req/sec. We sleep between requests to stay well under.
SEC_REQUEST_DELAY_SECONDS = 0.15

EDGAR_ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"

# Codes we ingest. P = open-market purchase (positive signal),
# S = open-market sale (used for the sell-veto rule). Everything else
# (A=grant, M=option exercise, F=tax withholding, G=gift, etc.) is noise.
INGESTED_TRANSACTION_CODES = {"P", "S"}
PURCHASE_TRANSACTION_CODES = {"P"}
SELL_TRANSACTION_CODES = {"S"}

# Fill-cost modeling. Calibrated to real published rates and per-ticker
# observable data, not hand-picked constants.

# Half-spread is computed per fill from that ticker's next-open daily range:
#   half_spread_bps = SPREAD_RANGE_FACTOR * (high - low) / open * 10000
# The 0.05 factor follows the Corwin-Schultz (2012) high-low spread
# estimator convention — bid-ask is typically ~5% of the daily H-L range
# for U.S. equities. Penny stocks naturally pay more (wider H-L), liquid
# names pay less. No hand-tuned constant per fill.
SPREAD_RANGE_FACTOR = 0.05

# SEC Section 31 fee on sale proceeds. Rate set by SEC release 2024-25,
# effective May 22 2024: $27.80 per $1,000,000 of sales = 2.78 bps.
# https://www.sec.gov/news/press-release/2024-25
SEC_FEE_BPS = 2.78

# FINRA Trading Activity Fee (TAF), per share on sells, no cap modeled.
# Rate from FINRA Rule 7510 (effective 2024).
TAF_PER_SHARE = 0.000166

# Cash earns interest via a sweep / T-bill ladder. 4.5% APY approximates
# the average 3-month T-bill yield for the 2024-2026 backtest window
# (FRED series DGS3MO ranged 4.0-5.4% during the period). Accrued daily.
CASH_INTEREST_APY = 0.045

# Liquidity guard: skip a buy if the order's share count exceeds this
# fraction of the next-open day's reported volume. 5% ADV is the standard
# threshold in market-impact literature where temporary impact starts to
# dominate the spread. None disables the check.
MAX_VOLUME_FRACTION = 0.05

# Trend filter (R8+): reject insider-buy entries where the entry day's
# close is below the N-day moving average. The recurring failure mode
# through R1-R7 was a fat tail of stop-loss exits — many insider buys
# were "value traps" in extended downtrends. This is a single boolean
# gate, not a score component, so it doesn't interact with profile tuning.
TREND_FILTER_ENABLED = True
TREND_FILTER_WINDOW = 50

# R10: liquidity floor. R9 diagnosis showed monotonic loser-concentration
# in the <$5M next-open dollar-volume tier — distressed microcaps where
# insider buying is desperation, not conviction. Filter applied in runner.py
# after the trend filter, before broker.place_buy.
LIQUIDITY_FILTER_ENABLED = True
LIQUIDITY_MIN_DOLLAR_VOLUME = 5_000_000.0
