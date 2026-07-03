"""Cross-strategy ensemble — meta-level voting between strategies.

Different from factor combos: instead of mixing signals, this mixes
strategy OUTPUTS. Each component strategy ranks the universe; the
ensemble counts votes (1 strategy = 1 vote per top-N pick) and ranks
by vote count.

Hypothesis: agreement between independent strategies (mom_v1 = top-100
mom, mom_v2 = top-50 mom, mom_roa_6535 = top-50 mom+ROA) reflects HIGH
CONVICTION. Stocks all three agree on may have stronger edge than any
single strategy's picks.

Variants:
  - intersection: only tickers in ALL component top-Ns (very selective)
  - majority: tickers in 2+ components (moderate)
  - union: tickers in ANY component (broad)
  - weighted: vote count weighted by component strength

Standalone module — call make_rank_fn(*strategies, ...) to build a
rank_fn for factor_backtest.
"""
from __future__ import annotations

from datetime import date

from trading_bot.factors import momentum, roa, mom_roa_zscore


def _component_picks(rank_fn, tickers, as_of, top_n):
    """Return set of ticker symbols that this rank_fn picks in top_n."""
    ranked = rank_fn(tickers, as_of)
    return {t for t, _ in ranked[:top_n]}


def make_ensemble_rank_fn(mode: str = "majority",
                          mom_v1_top: int = 100,
                          mom_v2_top: int = 50,
                          mom_roa_top: int = 50):
    """Build a rank_fn for factor_backtest.

    mode:
      - "intersection": only tickers in ALL 3 strategy top-Ns
      - "majority":     tickers in >= 2 of 3
      - "union":        tickers in any (1+)
      - "weighted":     all picks ranked by vote count (3 > 2 > 1)

    All component strategies use the SAME universe (tickers arg passed by
    the engine). Returns a rank_fn that returns (ticker, vote_count) tuples.
    """
    mom_roa_rank = mom_roa_zscore.make_rank_fn(0.65, 0.35)

    def _ranker(tickers: list[str], as_of: date) -> list[tuple[str, float]]:
        # Get top-N picks from each component (all using same input universe)
        v1_picks = _component_picks(momentum.rank_universe, tickers, as_of, mom_v1_top)
        v2_picks = _component_picks(momentum.rank_universe, tickers, as_of, mom_v2_top)
        roa_picks = _component_picks(mom_roa_rank, tickers, as_of, mom_roa_top)

        # Compute vote counts
        all_candidates = v1_picks | v2_picks | roa_picks
        votes = {}
        for t in all_candidates:
            n = (1 if t in v1_picks else 0) + \
                (1 if t in v2_picks else 0) + \
                (1 if t in roa_picks else 0)
            votes[t] = n

        if mode == "intersection":
            qualified = {t for t, n in votes.items() if n == 3}
        elif mode == "majority":
            qualified = {t for t, n in votes.items() if n >= 2}
        elif mode == "union":
            qualified = set(votes.keys())
        elif mode == "weighted":
            qualified = set(votes.keys())
        else:
            raise ValueError(f"Unknown ensemble mode: {mode}")

        # Rank descending by vote count, then by ticker for determinism
        scored = [(t, float(votes[t])) for t in qualified]
        scored.sort(key=lambda r: (-r[1], r[0]))
        return scored
    _ranker.__name__ = f"ensemble_{mode}"
    return _ranker
