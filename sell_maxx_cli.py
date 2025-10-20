#!/usr/bin/env python3
"""
Sell MAXX via Kyber using a provided private key.

- Reuses MasterTradingSystem gas policy and routing.
- Accepts MAXX amount, gas limit, slippage, and optional gas knobs.
"""
import argparse
import asyncio
import sys
import os
from decimal import Decimal

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import standalone_config as config  # noqa: E402
from tools.master_trading_system import MasterTradingSystem  # noqa: E402


async def run_sell(pk: str,
                   maxx_amount: Decimal | None,
                   sell_all: bool,
                   gas_limit: int | None,
                   slippage_bps: int,
                   headroom_pct: float | None,
                   priority_gwei: float | None,
                   max_fee_gwei: float | None,
                   wait_for_receipt: bool | None):
    config.ETHEREUM_PRIVATE_KEY = pk
    if gas_limit is not None:
        try:
            config.GAS_LIMIT = int(gas_limit)
        except Exception:
            pass

    system = MasterTradingSystem()
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

    if sell_all:
        _, maxx_bal = await system.get_balances()
        amt = Decimal(maxx_bal)
    else:
        if maxx_amount is None or maxx_amount <= 0:
            print("Provide --maxx amount or use --all")
            return 2
        amt = maxx_amount

    # Ensure router allowance to avoid TransferHelper: TRANSFER_FROM_FAILED
    ok_approval = await system.approve_maxx_spending(amt)
    if not ok_approval:
        print("Approval failed or not confirmed; cannot proceed with sell")
        return 2

    txh = await system.sell_maxx(amt, gas_limit=gas_limit, slippage_bps=slippage_bps)
    if txh:
        print(f"SELL_TX: {txh}")
        print(f"Explorer: https://basescan.org/tx/{txh}")
        return 0
    print("Sell failed")
    return 2


def main():
    ap = argparse.ArgumentParser(description="Sell MAXX using a provided private key")
    ap.add_argument("--pk", default=os.environ.get("ETHEREUM_PRIVATE_KEY"), help="Private key hex (or set ETHEREUM_PRIVATE_KEY env)")
    ap.add_argument("--maxx", type=float, default=None, help="MAXX amount to sell (ignored if --all)")
    ap.add_argument("--all", action="store_true", help="Sell ALL MAXX holdings")
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

    maxx_amt = Decimal(str(args.maxx)) if args.maxx is not None else None

    return asyncio.run(
        run_sell(
            pk=args.pk,
            maxx_amount=maxx_amt,
            sell_all=bool(args.all),
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
