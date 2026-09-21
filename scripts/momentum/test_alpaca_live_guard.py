"""Canary for the paper/live boundary in AlpacaClient (audit finding 26).

Why this exists: until 2026-09-20 the boundary was a DEFAULT, not a guard.
`base_url` fell back to PAPER_BASE_URL, but a single environment variable --
APCA_API_BASE_URL -- redirected it to the live host, and `is_live` was
consulted by no code path at all (only its own definition and a smoke-test
print). Every scheduled cmd.exe inherits the User-scope environment, so a
stray value would have reached rebalance.bat's alpaca_sync step.

No network: AlpacaClient.__init__ builds an httpx.Client but never connects.

Run:
    python -m scripts.momentum.test_alpaca_live_guard
"""
from __future__ import annotations

import os

from trading_bot.execution.alpaca_client import (
    AlpacaClient, AlpacaError, LIVE_BASE_URL, PAPER_BASE_URL,
)

# __init__ refuses to build without credentials, so give it throwaway ones.
# These are not secrets and never leave the process.
os.environ.setdefault("APCA_API_KEY_ID", "test-key-not-a-secret")
os.environ.setdefault("APCA_API_SECRET_KEY", "test-secret-not-a-secret")


def test_default_is_paper() -> None:
    os.environ.pop("APCA_API_BASE_URL", None)
    c = AlpacaClient()
    assert c.base_url == PAPER_BASE_URL, c.base_url
    assert c.is_live is False
    print("  [OK  ] default resolves to the PAPER host")


def test_env_var_cannot_reach_live() -> None:
    """The finding itself: one env var used to be enough."""
    os.environ["APCA_API_BASE_URL"] = LIVE_BASE_URL
    try:
        AlpacaClient()
    except AlpacaError as e:
        assert "REFUSING the LIVE" in str(e), str(e)
        print("  [OK  ] APCA_API_BASE_URL=live is REFUSED")
    else:
        raise AssertionError(
            "APCA_API_BASE_URL reached the LIVE host with no explicit opt-in")
    finally:
        os.environ.pop("APCA_API_BASE_URL", None)


def test_explicit_opt_in_still_possible() -> None:
    """The guard must be deliberate-override-able, not a wall."""
    c = AlpacaClient(base_url=LIVE_BASE_URL, allow_live=True)
    assert c.is_live is True
    print("  [OK  ] allow_live=True in code still permits live (deliberate)")


def test_paper_url_passed_explicitly_is_fine() -> None:
    c = AlpacaClient(base_url=PAPER_BASE_URL)
    assert c.is_live is False
    print("  [OK  ] an explicit PAPER base_url is unaffected")


def main() -> int:
    print("test_alpaca_live_guard")
    test_default_is_paper()
    test_env_var_cannot_reach_live()
    test_explicit_opt_in_still_possible()
    test_paper_url_passed_explicitly_is_fine()
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
