"""Payer-side client: makes a real x402 micropayment against a running NutriRef endpoint.

This is the *consumer* side — it simulates an AI agent paying per request. It is
separate from the server: it needs its own wallet (the payer) funded with a small
amount of Base Sepolia USDC. That wallet is distinct from the CDP receiver address
the server settles payments TO.

Setup:
    pip install -e ".[payer]"        # installs x402 + eth-account
    # add PAYER_PRIVATE_KEY=0x... to .env  (a funded Base Sepolia test wallet)

Usage:
    python scripts/pay_and_call.py                         # search?q=banana
    python scripts/pay_and_call.py search "greek yogurt"
    python scripts/pay_and_call.py detail 2012128
    python scripts/pay_and_call.py compare 2012128 2011468
    python scripts/pay_and_call.py recipe 2012128:150 2011468:100

Override the target with BASE_URL env var (default http://127.0.0.1:8000).
"""

import asyncio
import json
import os
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


def build_request(argv: list[str]) -> tuple[str, str, dict | None]:
    """Return (http_method, path, json_body) from CLI args."""
    cmd = argv[0] if argv else "search"

    if cmd == "search":
        q = argv[1] if len(argv) > 1 else "banana"
        return "GET", f"/v1/nutrition/search?q={q}", None

    if cmd == "detail":
        if len(argv) < 2:
            sys.exit("detail requires an fdc_id")
        return "GET", f"/v1/nutrition/detail/{argv[1]}", None

    if cmd == "compare":
        ids = [int(x) for x in argv[1:]]
        if len(ids) < 2:
            sys.exit("compare requires at least 2 fdc_ids")
        return "POST", "/v1/nutrition/compare", {"fdc_ids": ids}

    if cmd == "recipe":
        ingredients = []
        for spec in argv[1:]:
            fdc_id, _, grams = spec.partition(":")
            if not grams:
                sys.exit("recipe ingredients must be fdc_id:grams, e.g. 2012128:150")
            ingredients.append({"fdc_id": int(fdc_id), "grams": float(grams)})
        if not ingredients:
            sys.exit("recipe requires at least 1 ingredient")
        return "POST", "/v1/nutrition/recipe", {"ingredients": ingredients}

    sys.exit(f"Unknown command: {cmd} (use search|detail|compare|recipe)")


async def main() -> None:
    try:
        from eth_account import Account
        from x402.client import x402Client
        from x402.http import decode_payment_response_header
        from x402.http.clients.httpx import wrapHttpxWithPayment
        from x402.mechanisms.evm.exact import register_exact_evm_client
    except ImportError:
        sys.exit('Payer deps missing. Run:  pip install -e ".[payer]"')

    repo_root = Path(__file__).resolve().parent.parent
    env = load_env(repo_root / ".env")

    private_key = env.get("PAYER_PRIVATE_KEY")
    if not private_key or "PASTE" in private_key:
        sys.exit("Set PAYER_PRIVATE_KEY in .env to a funded Base Sepolia test wallet key.")

    base_url = os.environ.get("BASE_URL", "http://127.0.0.1:8000")
    method, path, body = build_request(sys.argv[1:])

    account = Account.from_key(private_key)
    print(f"Payer wallet: {account.address}")
    print(f"Calling: {method} {base_url}{path}")

    # An x402Client with the EVM "exact" scheme registered against the payer key.
    x402 = x402Client()
    register_exact_evm_client(x402, account)

    async with wrapHttpxWithPayment(x402, base_url=base_url, timeout=30.0) as http:
        if method == "GET":
            resp = await http.get(path)
        else:
            resp = await http.post(path, json=body)

    print(f"\nHTTP {resp.status_code}")
    if resp.status_code != 200:
        print(resp.text)
        sys.exit(1)

    print(json.dumps(resp.json(), indent=2))

    settle = resp.headers.get("X-PAYMENT-RESPONSE")
    if settle:
        print("\nSettlement (X-PAYMENT-RESPONSE):")
        print(json.dumps(decode_payment_response_header(settle), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
