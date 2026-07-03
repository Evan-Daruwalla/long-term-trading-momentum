"""Thin Alpaca Trading API client (paper by default).

Deliberately a small httpx wrapper, not the alpaca-py SDK: the project already
depends on httpx and the Trading API is plain REST, so a ~150-line client keeps
the dependency surface flat and the behavior auditable.

CREDENTIALS come from the environment (never hard-coded, never committed):
  APCA_API_KEY_ID      - your Alpaca key id
  APCA_API_SECRET_KEY  - your Alpaca secret
  APCA_API_BASE_URL    - optional; defaults to the PAPER endpoint
                         (https://paper-api.alpaca.markets). Point at
                         https://api.alpaca.markets only when going live.

The default base URL is the PAPER endpoint on purpose: nothing in this module
can touch a live account unless you explicitly set APCA_API_BASE_URL to the
live host. This module does NOT place orders on its own — callers do, and the
caller (you) owns that decision.

Every response carries an `X-Request-ID`; Alpaca asks you to persist recent ones
for support tickets (they can't be queried later). We log each one and append it
to var/alpaca_request_ids.log so the last calls are always recoverable.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

import httpx

from trading_bot.config import VAR_DIR

log = logging.getLogger(__name__)

PAPER_BASE_URL = "https://paper-api.alpaca.markets"
LIVE_BASE_URL = "https://api.alpaca.markets"
_REQUEST_ID_LOG = VAR_DIR / "alpaca_request_ids.log"


class AlpacaError(RuntimeError):
    """Non-2xx response from the Trading API. Carries status + request id so a
    support ticket can quote the X-Request-ID Alpaca asks for."""

    def __init__(self, status: int, request_id: str | None, body: str):
        self.status = status
        self.request_id = request_id
        self.body = body
        super().__init__(f"Alpaca {status} (X-Request-ID={request_id}): {body}")


class AlpacaClient:
    def __init__(self, *, base_url: str | None = None,
                 key_id: str | None = None, secret_key: str | None = None,
                 timeout: float = 15.0):
        self.base_url = (base_url or os.environ.get("APCA_API_BASE_URL")
                         or PAPER_BASE_URL).rstrip("/")
        self._key = key_id or os.environ.get("APCA_API_KEY_ID")
        self._secret = secret_key or os.environ.get("APCA_API_SECRET_KEY")
        if not self._key or not self._secret:
            raise AlpacaError(
                0, None,
                "Missing credentials. Set APCA_API_KEY_ID and APCA_API_SECRET_KEY "
                "in the environment (paper keys from the Alpaca dashboard).")
        self._client = httpx.Client(
            base_url=self.base_url, timeout=timeout,
            headers={"APCA-API-KEY-ID": self._key,
                     "APCA-API-SECRET-KEY": self._secret})

    @property
    def is_live(self) -> bool:
        return self.base_url == LIVE_BASE_URL

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "AlpacaClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ---- core request + X-Request-ID persistence ----
    def _request(self, method: str, path: str, **kw) -> Any:
        resp = self._client.request(method, path, **kw)
        rid = resp.headers.get("X-Request-ID")
        self._persist_request_id(method, path, resp.status_code, rid)
        if resp.status_code >= 400:
            raise AlpacaError(resp.status_code, rid, resp.text)
        return resp.json() if resp.content else None

    def _persist_request_id(self, method: str, path: str,
                            status: int, rid: str | None) -> None:
        line = (f"{datetime.now(timezone.utc).isoformat()} {method} {path} "
                f"-> {status} X-Request-ID={rid}")
        log.info(line)
        try:
            VAR_DIR.mkdir(parents=True, exist_ok=True)
            with _REQUEST_ID_LOG.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except OSError:
            pass  # logging the id is best-effort; never break a call over it

    # ---- read endpoints ----
    def get_account(self) -> dict:
        return self._request("GET", "/v2/account")

    def list_positions(self) -> list[dict]:
        return self._request("GET", "/v2/positions") or []

    def get_position(self, symbol: str) -> dict:
        return self._request("GET", f"/v2/positions/{symbol}")

    def get_asset(self, symbol: str) -> dict:
        """Asset reference data — tradable / fractionable / status / exchange."""
        return self._request("GET", f"/v2/assets/{symbol}")

    def list_orders(self, *, status: str = "open", limit: int = 100) -> list[dict]:
        return self._request("GET", "/v2/orders",
                             params={"status": status, "limit": limit}) or []

    # ---- order entry (caller-driven; defaults to paper via base_url) ----
    def submit_order(self, *, symbol: str, qty: float | None = None,
                     notional: float | None = None, side: str = "buy",
                     type: str = "market", time_in_force: str = "day",
                     **extra) -> dict:
        """Submit an order. Exactly one of qty / notional must be given.
        Honors the configured base_url, so this is a paper order unless
        APCA_API_BASE_URL points at the live host."""
        if (qty is None) == (notional is None):
            raise ValueError("Pass exactly one of qty= or notional=.")
        body: dict[str, Any] = {"symbol": symbol, "side": side, "type": type,
                                "time_in_force": time_in_force, **extra}
        if qty is not None:
            body["qty"] = str(qty)
        else:
            body["notional"] = str(notional)
        return self._request("POST", "/v2/orders", json=body)

    def cancel_order(self, order_id: str) -> None:
        self._request("DELETE", f"/v2/orders/{order_id}")


def _smoke_test() -> int:
    """Connectivity check: GET /v2/account. Turns the docs' 403 into a 200 once
    your keys are set. Run:
      .venv\\Scripts\\python.exe -m trading_bot.execution.alpaca_client
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        client = AlpacaClient()
    except AlpacaError as e:
        print(e)
        return 2
    print(f"Endpoint: {client.base_url}  ({'LIVE' if client.is_live else 'PAPER'})")
    try:
        acct = client.get_account()
    except AlpacaError as e:
        print(f"FAILED: {e}")
        print("403 = bad/empty keys; 200 = you're connected.")
        return 1
    finally:
        client.close()
    print("Connected. Account:")
    for k in ("account_number", "status", "currency", "cash",
              "portfolio_value", "buying_power", "pattern_day_trader"):
        print(f"  {k:18} {acct.get(k)}")
    print(f"Recent X-Request-IDs persisted to {_REQUEST_ID_LOG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_smoke_test())
