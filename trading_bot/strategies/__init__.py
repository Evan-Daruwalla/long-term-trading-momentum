"""Frozen strategy versions.

Each module here pins a specific strategy configuration as immutable,
documents its baseline numbers, and exposes a single `run(since, until)`
entry point. Use these for regression-testing and live deployment; use
the parameterized scripts/momentum/* runners for experiments.

Convention: filename = `<strategy>_v<N>.py`. Bump version when params
change in a way that produces different results (i.e., almost any change).
"""
