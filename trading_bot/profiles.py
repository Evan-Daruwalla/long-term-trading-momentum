"""Risk profiles for parallel simulations.

Three preset profiles vary the rules the bot follows. The differences:

  CONSERVATIVE  — harder to enter (score >= 7), tighter stop, smaller TP,
                  smaller positions. Optimizes for capital preservation.
  NORMAL        — the rules from the original brief (score >= 5, -15% / +30%,
                  5%/10% sizing). Baseline.
  AGGRESSIVE    — easier to enter (score >= 4), wider stop, bigger TP, larger
                  positions. Hard safety caps below — never larger than 15%
                  per position, sector cap stays 20%, max drawdown circuit
                  breaker (not yet implemented).

`use_profile` is a context manager that swaps the module-level constants in
scorer / monitor / runner to the profile's values, then restores them.
This is a deliberately minimal mechanism for v1 — once we move to truly
concurrent multi-bot we'll thread the profile object through directly.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass


@dataclass(frozen=True)
class RiskProfile:
    name: str
    trade_threshold: int = 5
    high_conviction_threshold: int = 8
    standard_position_pct: float = 5.0
    high_conviction_position_pct: float = 10.0
    stop_loss_pct: float = -15.0
    take_profit_pct: float = 30.0
    time_exit_days: int = 60
    sector_cap_pct: float = 20.0
    # Loss-prevention extensions (added 2026-04-28).
    # Both default to 0.0 = disabled, so any profile that omits them keeps
    # the legacy stop_loss / take_profit behavior unchanged.
    #
    #   breakeven_trigger_pct:
    #     once unrealized gain >= this %, the stop is raised to entry price.
    #     Converts "winner that round-tripped to -stop_loss" into a scratch.
    #
    #   trailing_trigger_pct + trailing_distance_pct:
    #     once unrealized gain >= trigger, exit if the close falls more than
    #     `distance` percentage points below the peak close since entry.
    #     Lets winners run further than take_profit while locking gains on
    #     a reversal.
    breakeven_trigger_pct: float = 0.0
    trailing_trigger_pct: float = 0.0
    trailing_distance_pct: float = 0.0
    # R11 (Tier 1.3): vol-scaled stop. 0 = disabled, falls back to
    # stop_loss_pct. Stop = clip(-mult * ATR%(20), [min, max]) per position.
    vol_stop_atr_mult: float = 0.0
    vol_stop_min_pct: float = -5.0
    vol_stop_max_pct: float = -30.0
    # R11 (Tier 1.3): regime-conditional time exit. Multipliers default to
    # 1.0 = unchanged behavior. When set, time_exit_days is scaled by the
    # uptrend/downtrend multiplier based on SPY 200DMA at as_of.
    time_exit_uptrend_mult: float = 1.0
    time_exit_downtrend_mult: float = 1.0


CONSERVATIVE = RiskProfile(
    name="conservative",
    # R7 (2026-04-30): R6 raised threshold 8->9 and time_exit 90->120 → -5.93%
    # (vs R5's +1.26%). Score=9 requires all bonuses (cluster 3+ AND CEO/CFO
    # AND $500K) — too rare; cash sits idle while small-caps run. Reverting
    # both to R5 settings; R5 was the local optimum.
    # R9 (2026-05-05): R8 added 50-day MA trend filter. Since the filter already
    # screens out downtrending entries, we can loosen the score cutoff (8→7)
    # to capture more trend-aligned signals and widen TP (30→40) because
    # trend-confirmed entries are expected to have more room to run.
    # BE trigger raised 8→10 to avoid premature scratch exits on small bounces.
    trade_threshold=7,
    high_conviction_threshold=10,
    standard_position_pct=3.0,
    high_conviction_position_pct=5.0,
    stop_loss_pct=-15.0,
    take_profit_pct=40.0,
    time_exit_days=90,
    breakeven_trigger_pct=10.0,
    trailing_trigger_pct=22.0,
    trailing_distance_pct=10.0,
    # R11 (Tier 1.3): Conservative gets the tightest vol-stop band — most
    # trades, smaller positions, capital preservation > letting winners run.
    vol_stop_atr_mult=2.0,
    vol_stop_min_pct=-6.0,
    vol_stop_max_pct=-20.0,
    # Modest regime tilt: stretch holding period 50% in trend-up, compress
    # to 60% in trend-down. Conservative cares less about chop because the
    # 90-day base is already lenient.
    time_exit_uptrend_mult=1.5,
    time_exit_downtrend_mult=0.6,
)

NORMAL = RiskProfile(
    name="normal",
    # R7 (2026-04-30): R6 added HC=9 -> -5.58% (vs R5's +4.83%). Smaller
    # 5% sizing on score=8 entries hurt more than the more-entries effect
    # helped — score=8 trades were R5's strongest. Reverting HC to default
    # (8) to restore R5 behavior.
    # R9 (2026-05-05): With MA trend filter in R8, entries are already
    # screened for up-trending stocks. Tighten SL (-15→-12) since
    # trend-confirmed entries shouldn't fall as far before rebounding.
    # TP stays at 50 — let trend-followers run. Raise HC threshold 8→9
    # to focus high-conviction sizing on the cleanest signals.
    trade_threshold=7,
    high_conviction_threshold=9,
    standard_position_pct=5.0,
    high_conviction_position_pct=10.0,
    stop_loss_pct=-12.0,
    take_profit_pct=50.0,
    time_exit_days=120,
    breakeven_trigger_pct=10.0,
    trailing_trigger_pct=25.0,
    trailing_distance_pct=12.0,
    # R11 (Tier 1.3): Normal gets a 2.5× ATR stop — wider band than
    # Conservative because Normal already runs at 5/10% sizing and survives
    # one big loss. Goal: stop 0% of n=22 stops cohort from R10 firing on
    # benign noise; the actual losers will still trigger because their TR
    # blew past 2.5σ entering the trade.
    vol_stop_atr_mult=2.5,
    vol_stop_min_pct=-7.0,
    vol_stop_max_pct=-25.0,
    time_exit_uptrend_mult=1.5,
    time_exit_downtrend_mult=0.5,
)

AGGRESSIVE = RiskProfile(
    name="aggressive",
    # R6 (2026-04-30, realistic-cost): R5 with TP=70 / SL=-20 was -23.14%.
    # Only 12/110 closes (11%) reached the +70 TP — math required a 22%
    # win rate to break even, miles from reality. Pre-cost "fat-tail" thesis
    # was a paper artifact. Reframing aggressive's identity: same exit
    # discipline as normal (-15 / +40 / BE=8 / trail=22/10 / time=120) but
    # with **bigger position sizes** (7/15 vs normal's 5/10). The
    # aggressive lever is now *capital allocation*, not *rule looseness*.
    # R9 (2026-05-05): Trend filter in R8 improves entry quality, so we can
    # lean into the capital-allocation identity more. Raise standard size
    # (7→8%) to deploy more capital on trend-confirmed entries. Tighten
    # SL (-15→-12) matching normal's R9 change — trend-filtered entries
    # in downtrend moves should be rare, so -12 stops are safer now.
    # HC threshold stays at 9 (filters the very best entries for 15% sizing).
    trade_threshold=7,
    high_conviction_threshold=9,
    standard_position_pct=8.0,
    high_conviction_position_pct=15.0,
    stop_loss_pct=-12.0,
    take_profit_pct=40.0,
    time_exit_days=120,
    breakeven_trigger_pct=8.0,
    trailing_trigger_pct=22.0,
    trailing_distance_pct=10.0,
    # R11 (Tier 1.3): Aggressive runs 8/15% sizing — biggest singles. Use
    # the widest vol-stop band so we don't get blown out of a CABA-class
    # winner on opening-week chop, but cap at -25% since at 15% sizing a
    # full-stop is -3.75% of NAV.
    vol_stop_atr_mult=3.0,
    vol_stop_min_pct=-8.0,
    vol_stop_max_pct=-25.0,
    # Aggressive leans hardest into regime: 1.75x in uptrend, 0.4x in
    # downtrend — when SPY rolls over we want out fast.
    time_exit_uptrend_mult=1.75,
    time_exit_downtrend_mult=0.4,
)

ALL_PROFILES = [CONSERVATIVE, NORMAL, AGGRESSIVE]


@contextmanager
def use_profile(profile: RiskProfile):
    """Override the relevant module constants for the duration of a backtest."""
    from trading_bot.execution import monitor as m
    from trading_bot.execution import runner as r
    from trading_bot.scoring import scorer as s

    saved = (
        s.TRADE_THRESHOLD, s.HIGH_CONVICTION_THRESHOLD,
        s.STANDARD_POSITION_PCT, s.HIGH_CONVICTION_POSITION_PCT,
        m.STOP_LOSS_PCT, m.TAKE_PROFIT_PCT, m.TIME_EXIT_DAYS,
        m.BREAKEVEN_TRIGGER_PCT, m.TRAILING_TRIGGER_PCT, m.TRAILING_DISTANCE_PCT,
        m.VOL_STOP_ATR_MULT, m.VOL_STOP_MIN_PCT, m.VOL_STOP_MAX_PCT,
        m.TIME_EXIT_UPTREND_MULT, m.TIME_EXIT_DOWNTREND_MULT,
        r.SECTOR_CAP_PCT,
    )
    try:
        s.TRADE_THRESHOLD = profile.trade_threshold
        s.HIGH_CONVICTION_THRESHOLD = profile.high_conviction_threshold
        s.STANDARD_POSITION_PCT = profile.standard_position_pct
        s.HIGH_CONVICTION_POSITION_PCT = profile.high_conviction_position_pct
        m.STOP_LOSS_PCT = profile.stop_loss_pct
        m.TAKE_PROFIT_PCT = profile.take_profit_pct
        m.TIME_EXIT_DAYS = profile.time_exit_days
        m.BREAKEVEN_TRIGGER_PCT = profile.breakeven_trigger_pct
        m.TRAILING_TRIGGER_PCT = profile.trailing_trigger_pct
        m.TRAILING_DISTANCE_PCT = profile.trailing_distance_pct
        m.VOL_STOP_ATR_MULT = profile.vol_stop_atr_mult
        m.VOL_STOP_MIN_PCT = profile.vol_stop_min_pct
        m.VOL_STOP_MAX_PCT = profile.vol_stop_max_pct
        m.TIME_EXIT_UPTREND_MULT = profile.time_exit_uptrend_mult
        m.TIME_EXIT_DOWNTREND_MULT = profile.time_exit_downtrend_mult
        r.SECTOR_CAP_PCT = profile.sector_cap_pct
        yield
    finally:
        (
            s.TRADE_THRESHOLD, s.HIGH_CONVICTION_THRESHOLD,
            s.STANDARD_POSITION_PCT, s.HIGH_CONVICTION_POSITION_PCT,
            m.STOP_LOSS_PCT, m.TAKE_PROFIT_PCT, m.TIME_EXIT_DAYS,
            m.BREAKEVEN_TRIGGER_PCT, m.TRAILING_TRIGGER_PCT, m.TRAILING_DISTANCE_PCT,
            m.VOL_STOP_ATR_MULT, m.VOL_STOP_MIN_PCT, m.VOL_STOP_MAX_PCT,
            m.TIME_EXIT_UPTREND_MULT, m.TIME_EXIT_DOWNTREND_MULT,
            r.SECTOR_CAP_PCT,
        ) = saved
