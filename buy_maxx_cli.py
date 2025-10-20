#!/usr/bin/env python3
"""
Buy MAXX via Kyber using a provided private key.

- Reuses MasterTradingSystem gas policy and routing.
- Accepts ETH amount, gas limit, slippage, and optional gas knobs.
"""
import argparse
import asyncio
import sys
import os
from decimal import Decimal

# Ensure local imports
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import standalone_config as config  # noqa: E402
from tools.master_trading_system import MasterTradingSystem  # noqa: E402


async def run_buy(pk: str,
                  eth_amount: Decimal,
                  gas_limit: int | None,
                  slippage_bps: int,
                  headroom_pct: float | None,
                  priority_gwei: float | None,
                  max_fee_gwei: float | None,
                  wait_for_receipt: bool | None):
    # Patch PK and optional config knobs
    config.ETHEREUM_PRIVATE_KEY = pk
    if gas_limit is not None:
        try:
            config.GAS_LIMIT = int(gas_limit)
        except Exception:
            pass

    system = MasterTradingSystem()
    # Optional gas policy overrides on the system instance
    if headroom_pct is not None:
        system.base_fee_headroom_pct = float(headroom_pct)
    if priority_gwei is not None:
        system.priority_fee_gwei = float(priority_gwei)
    if max_fee_gwei is not None:
        system.max_fee_gwei = float(max_fee_gwei)
    if wait_for_receipt is not None:
        system.wait_for_receipt = bool(wait_for_receipt)

    ok = await system.initialize()
    if not ok:
        print("Init failed")
        return 1

    txh = await system.buy_maxx(eth_amount, gas_limit=gas_limit, slippage_bps=slippage_bps)
    if txh:
        print(f"BUY_TX: {txh}")
        print(f"Explorer: https://basescan.org/tx/{txh}")
        return 0
    print("Buy failed")
    return 2


def main():
    ap = argparse.ArgumentParser(description="Buy MAXX with ETH using a provided private key")
    ap.add_argument("--pk", default=os.environ.get("ETHEREUM_PRIVATE_KEY"), help="Private key hex (or set ETHEREUM_PRIVATE_KEY env)")
    ap.add_argument("--eth", required=True, type=float, help="ETH amount to spend (e.g., 0.001)")
    ap.add_argument("--slippage-bps", type=int, default=75, help="Kyber slippage in bps (75 = 0.75%)")
    ap.add_argument("--gas-limit", type=int, default=None, help="Optional gas limit override (e.g., 300000)")
    ap.add_argument("--headroom-pct", type=float, default=None, help="Base fee headroom pct (e.g., 0.0..0.05)")
    ap.add_argument("--priority-gwei", type=float, default=None, help="Priority fee gwei (e.g., 0.0..0.002)")
    ap.add_argument("--max-fee-gwei", type=float, default=None, help="Max fee per gas gwei cap")
    ap.add_argument("--no-wait", action="store_true", help="Do not wait for receipt")
    args = ap.parse_args()

    if not args.pk:
        print("Missing --pk or ETHEREUM_PRIVATE_KEY env")
        return 2
    if args.eth <= 0:
        print("--eth must be > 0")
        return 2

    return asyncio.run(
        run_buy(
            pk=args.pk,
            eth_amount=Decimal(str(args.eth)),
            gas_limit=args.gas_limit,
            slippage_bps=int(args.slippage_bps),
            headroom_pct=args.headroom_pct,
            priority_gwei=args.priority_gwei,
            max_fee_gwei=args.max_fee_gwei,
            wait_for_receipt=(False if args.no_wait else None)
        )
    )


if __name__ == "__main__":
    sys.exit(main())
