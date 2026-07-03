"""Cross-sectional factor portfolios (momentum, value, quality, ...).

Different shape of strategy from the Form 4 signal-event model in
trading_bot/execution: factor portfolios rank the whole universe each
rebalance and snap to a new equal-weighted top-N basket, no per-position
stops or take-profits.
"""
