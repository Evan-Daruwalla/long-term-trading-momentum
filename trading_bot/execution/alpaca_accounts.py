"""Multi-account Alpaca paper config: one paper account per sleeve.

Alpaca caps a login at 3 paper accounts, and a single account can't isolate
per-sleeve P&L (positions commingle), so we map exactly one sleeve -> one paper
account. The three key pairs live in `alpaca_keys.env` at the project root
(gitignored); this module loads them and hands back a ready AlpacaClient per
sleeve.

Env-file format (see alpaca_keys.env):
  ALPACA_ACCT{N}_KEY_ID / ALPACA_ACCT{N}_SECRET / ALPACA_ACCT{N}_SLEEVE   (N=1..3)

Verify all configured accounts:
  .venv\\Scripts\\python.exe -m trading_bot.execution.alpaca_accounts
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from trading_bot.config import PROJECT_ROOT
from trading_bot.execution.alpaca_client import AlpacaClient, AlpacaError

log = logging.getLogger(__name__)

KEYS_FILE = PROJECT_ROOT / "alpaca_keys.env"
MAX_ACCOUNTS = 3  # Alpaca's per-login paper-account cap


def load_keys_file(path=KEYS_FILE) -> None:
    """Populate os.environ from the keys file (no python-dotenv dependency).
    Does NOT overwrite variables already set in the real environment, so a
    Windows User env var still wins over the file if both exist."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


@dataclass(frozen=True)
class Account:
    n: int
    sleeve: str
    key_id: str
    secret: str

    def client(self) -> AlpacaClient:
        # base_url omitted -> AlpacaClient defaults to the PAPER host.
        return AlpacaClient(key_id=self.key_id, secret_key=self.secret)


def configured_accounts() -> list[Account]:
    """Return the accounts that have BOTH a key id and secret filled in.
    Slots left blank in the keys file are skipped (not yet set up)."""
    load_keys_file()
    out: list[Account] = []
    for n in range(1, MAX_ACCOUNTS + 1):
        key_id = os.environ.get(f"ALPACA_ACCT{n}_KEY_ID", "").strip()
        secret = os.environ.get(f"ALPACA_ACCT{n}_SECRET", "").strip()
        sleeve = os.environ.get(f"ALPACA_ACCT{n}_SLEEVE", "").strip()
        if key_id and secret and sleeve:
            out.append(Account(n=n, sleeve=sleeve, key_id=key_id, secret=secret))
    return out


def account_for_sleeve(sleeve: str) -> Account | None:
    return next((a for a in configured_accounts() if a.sleeve == sleeve), None)


def _verify() -> int:
    """Ping /v2/account on every configured account so you can confirm all
    three key pairs work before any routing is wired."""
    logging.basicConfig(level=logging.WARNING, format="%(message)s")
    accts = configured_accounts()
    if not accts:
        print(f"No accounts configured yet. Paste keys into {KEYS_FILE} "
              f"(ALPACA_ACCT1_KEY_ID / _SECRET, etc.) then re-run.")
        return 2
    print(f"Found {len(accts)}/{MAX_ACCOUNTS} configured account(s):\n")
    failures = 0
    for a in accts:
        try:
            with a.client() as c:
                acct = c.get_account()
            print(f"  [OK]   ACCT{a.n}  {a.sleeve:30}  "
                  f"#{acct.get('account_number')}  {acct.get('status')}  "
                  f"cash=${float(acct.get('cash', 0)):,.0f}")
        except AlpacaError as e:
            failures += 1
            print(f"  [FAIL] ACCT{a.n}  {a.sleeve:30}  {e}")
    blank = MAX_ACCOUNTS - len(accts)
    if blank:
        print(f"\n  ({blank} slot(s) still blank in {KEYS_FILE.name}.)")
    print("\nAll good — keys work." if failures == 0
          else f"\n{failures} account(s) failed — check those keys (403 = wrong/paper-vs-live).")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_verify())
