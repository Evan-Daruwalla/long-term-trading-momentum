"""Quality gate applied at signal-load time.

Drops likely-uninformative insider trades before scoring/clustering:
  - size      : < $50K (catches director qualifying buys, routine 10b5-1)
  - role      : pure 10%-owners with no officer/director flag (fund/family
                rebalancing, not informed conviction)

Applied at SQL level in both `scoring.scorer` and `scoring.clusters` so
that cluster counts and dollar totals inherit the cut.

Motivation: Cohen, Malloy, Pomorski (2012) "Decoding Inside Information"
finds opportunistic insider trades predict returns (~7%/yr alpha) while
routine trades don't. Without their insider-history methodology we use
size + role as a proxy for opportunistic.

NULLs in role columns coerce to 0 — defensive against partial Form 4
parses; the cost is dropping a small number of legitimate but unparsed
signals.
"""
from __future__ import annotations

QUALITY_FILTER_SQL = (
    "AND total_value >= 50000 "
    "AND (COALESCE(is_officer, 0) = 1 OR COALESCE(is_director, 0) = 1) "
    "AND COALESCE(is_ten_percent_owner, 0) = 0"
)
