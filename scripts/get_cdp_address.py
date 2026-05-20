"""One-off helper: create (or fetch) a CDP EVM account and print its 0x address.

Reads CDP_API_KEY_ID / CDP_API_KEY_SECRET / CDP_WALLET_SECRET from .env.
The printed 0x... address is what goes in X402_RECEIVER_ADDRESS.

Usage:
    pip install cdp-sdk
    python scripts/get_cdp_address.py
"""

import asyncio
import sys
from pathlib import Path


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        sys.exit(f"No .env found at {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


async def main() -> None:
    try:
        from cdp import CdpClient
    except ImportError:
        sys.exit("cdp-sdk not installed. Run:  pip install cdp-sdk")

    env = load_env(Path(__file__).resolve().parent.parent / ".env")
    required = ("CDP_API_KEY_ID", "CDP_API_KEY_SECRET", "CDP_WALLET_SECRET")
    missing = [k for k in required if not env.get(k)]
    if missing:
        sys.exit(f"Missing in .env: {', '.join(missing)}")

    async with CdpClient(
        api_key_id=env["CDP_API_KEY_ID"],
        api_key_secret=env["CDP_API_KEY_SECRET"],
        wallet_secret=env["CDP_WALLET_SECRET"],
    ) as cdp:
        # get_or_create is idempotent: reuses the named account on later runs.
        account = await cdp.evm.get_or_create_account(name="nutriref-receiver")
        print()
        print("  CDP account address (use this for X402_RECEIVER_ADDRESS):")
        print(f"  {account.address}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
