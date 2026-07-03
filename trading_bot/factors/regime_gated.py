"""Regime-gated factor: mom_v2 default, mom_then_accruals during mega-cap regimes.

Algorithm:
  1. At each rebalance, check `regime.is_mega_cap_regime(as_of)`
  2. If True (mega-cap leading): use mom_then_accruals.rank_universe
  3. If False (broad/small-cap leading): use momentum.rank_universe (mom_v2 logic)

Hypothesis: in mega-cap regimes (e.g. 2024-26 AI rally), filtering mom-winners
by accruals quality preserves the regime's specific alpha source (profitable
cash machines). In broad regimes (e.g. most of 2015-23), keeping all mom
winners captures the small-cap tail where mom's premium lives.

What "success" means:
  - In-sample CAGR ≥ mom_v2 solo (+21%/yr) — must NOT lose to baseline
  - Held-out CAGR > mom_v2 solo (+26.5%/yr) — should capture the 2024-26 boost
  - If only held-out improves: overfit to that regime, not deployable
  - If both improve: real regime-conditional alpha

Caveat: 62% of in-sample months are gate=True per the smoke test. Given
mom_then_accruals lost in-sample by -14 pp/yr running it 100% of months,
running it 62% of months should still drag — unless the gate happens to
trigger only in the months mom_then_accruals actually wins.
"""
from __future__ import annotations

from datetime import date

from trading_bot.factors import momentum, mom_then_accruals, regime


def rank_universe(tickers: list[str], as_of: date
                  ) -> list[tuple[str, float]]:
    """Switch between momentum and mom_then_accruals based on regime gate."""
    if regime.is_mega_cap_regime(as_of):
        return mom_then_accruals.rank_universe(tickers, as_of)
    return momentum.rank_universe(tickers, as_of)
