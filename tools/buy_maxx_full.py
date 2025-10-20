#!/usr/bin/env python3
r"""
Buy MAXX at full capacity: uses all available ETH (minus small gas reserve).
Then master_trading_system handles 6% up → sell, 6% down → buy cycles.

Usage (PowerShell):
  python .\buy_maxx_full.py --dry-run  # Preview
  python .\buy_maxx_full.py --send     # Execute
  python .\buy_maxx_full.py --send --slippage-bps 100  # Custom slippage
"""
from __future__ import annotations

import argparse
import json
import os
from decimal import Decimal

from dotenv import load_dotenv
from web3 import Web3
import requests

from kyber_client import KyberClient
from env_loader import load_env_once


def main():
    load_env_once()
    ap = argparse.ArgumentParser(description="Buy MAXX at full capacity")
    ap.add_argument("--slippage-bps", type=int, default=75, help="Slippage in basis points (75 bps = 0.75%)")
    ap.add_argument("--rpc", default="https://mainnet.base.org", help="Base RPC URL")
    ap.add_argument("--dry-run", action="store_true", help="Preview only, do not send")
    ap.add_argument("--send", action="store_true", help="Send transaction")
    ap.add_argument("--pk", help="Private key override (else use .env PRIVATE_KEY)")
    args = ap.parse_args()

    # Load keys
    pk = args.pk or os.getenv("PRIVATE_KEY")
    if not pk:
        raise SystemExit("No private key. Set PRIVATE_KEY in .env or pass --pk")

    account = Web3().eth.account.from_key(pk)
    user_addr = account.address

    # RPC & contracts
    w3 = Web3(Web3.HTTPProvider(args.rpc))
    maxx_contract = "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"
    weth_contract = "0x4200000000000000000000000000000000000006"

    # Get ETH balance
    eth_wei = w3.eth.get_balance(user_addr)
    eth_amount = Decimal(eth_wei) / Decimal(10**18)

    # Reserve 0.001 ETH (~$3.30) for gas
    gas_reserve = Decimal("0.001")
    available_eth = eth_amount - gas_reserve

    if available_eth <= 0:
        print(f"⚠ Insufficient ETH. Have {eth_amount:.6f}, need at least {gas_reserve:.6f}")
        return

    print(f"Current ETH balance: {eth_amount:.6f} ETH")
    print(f"Gas reserve: {gas_reserve:.6f} ETH")
    print(f"Available to trade: {available_eth:.6f} ETH")

    # Get MAXX price via DexScreener
    try:
        resp = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{maxx_contract}", timeout=10)
        data = resp.json()
        pairs = data.get("pairs") or []
        if pairs:
            price_usd = float(pairs[0].get("priceUsd") or 0)
            if price_usd > 0:
                print(f"MAXX price: ${price_usd:.6f}")
            else:
                print("⚠ Could not fetch MAXX price")
                return
        else:
            print("⚠ No pairs found")
            return
    except Exception as e:
        print(f"⚠ Price fetch failed: {e}")
        return

    usd_value = float(available_eth) * 3300  # ETH @ $3300
    print(f"\nFull buy value: ${usd_value:.2f}")

    # Build swap via Kyber
    kyber = KyberClient(w3=w3, account=account)
    try:
        route = kyber.get_route(
            token_in=weth_contract,
            token_out=maxx_contract,
            amount_in_wei=int(available_eth * Decimal(10**18)),
            slippage_bps=args.slippage_bps,
        )
        if not route:
            print("⚠ No route found")
            return

        print(f"\nRoute summary: {route.get('routeSummary', {})}")

        # Build transaction
        tx_data = kyber.build_tx(
            route_summary=route.get('routeSummary'),
            sender=user_addr,
            recipient=user_addr,
            slippage_bps=args.slippage_bps,
        )
        if not tx_data:
            print("⚠ Failed to build transaction")
            return

        # Minimal EIP-1559 gas params
        gas_price_info = w3.eth.gas_price
        base_fee = w3.eth.fee_history(1, "latest")["baseFeePerGas"][-1]
        max_fee = int(base_fee * 1.2)  # 20% above base
        max_priority = 1  # minimal tip

        tx = {
            "from": user_addr,
            "to": tx_data.get("to"),
            "data": tx_data.get("data"),
            "value": int(tx_data.get("value", 0)),
            "nonce": w3.eth.get_transaction_count(user_addr),
            "gas": int(tx_data.get("gas", 500000) * 1.1),  # +10% buffer
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": max_priority,
            "chainId": 8453,
            "type": 2,
        }

        gas_estimate = w3.eth.estimate_gas(tx)
        tx["gas"] = int(gas_estimate * 1.1)

        print(f"\n=== TRANSACTION PREVIEW ===")
        print(f"Gas: {tx['gas']}")
        print(f"Max fee per gas: {tx['maxFeePerGas'] / 1e9:.2f} Gwei")
        print(f"Max priority fee: {tx['maxPriorityFeePerGas'] / 1e9:.2f} Gwei")
        print(f"Est. gas cost: ${(tx['gas'] * max_fee / 1e9 * 3300 / 1e18):.2f}")

        if args.dry_run:
            print("\n✓ Dry-run complete. Use --send to execute.")
            return

        if args.send:
            signed = w3.eth.account.sign_transaction(tx, pk)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            print(f"\n✓ Sent! Tx hash: {tx_hash.hex()}")
            print(f"  Base scan: https://basescan.org/tx/{tx_hash.hex()}")
        else:
            print("\n⚠ Use --send to execute or --dry-run to preview")

    except Exception as e:
        print(f"⚠ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
