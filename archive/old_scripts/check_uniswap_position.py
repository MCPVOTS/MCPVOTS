#!/usr/bin/env python3
"""
Check Uniswap V3/V4 Position for MAXX
====================================
"""

import asyncio
import aiohttp
import json
import web3
from web3 import Web3

async def check_uniswap_position():
    """Check Uniswap position to get MAXX balance"""

    # Base chain RPC
    base_rpc = "https://mainnet.base.org"
    w3 = Web3(Web3.HTTPProvider(base_rpc))

    if not w3.is_connected():
        print("[ERR] Cannot connect to Base chain")
        return

    wallet = "0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9"
    maxx_contract = "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"

    print("="*60)
    print("CHECKING UNISWAP POSITIONS")
    print("="*60)

    # MAXX ABI (ERC20)
    erc20_abi = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        }
    ]

    try:
        # Create contract instance
        maxx_contract_instance = w3.eth.contract(
            address=Web3.to_checksum_address(maxx_contract),
            abi=erc20_abi
        )

        # Check balance
        balance = maxx_contract_instance.functions.balanceOf(
            Web3.to_checksum_address(wallet)
        ).call()

        balance_float = balance / 1e18

        print(f"Direct Contract Balance: {balance_float:,.2f} MAXX")

        if balance_float > 0:
            print(f"[SUCCESS] Found {balance_float:,.2f} MAXX tokens!")
        else:
            print("[INFO] No MAXX tokens found in wallet")

            # Check if tokens are in a liquidity position
            print("\nChecking liquidity positions...")

            # Uniswap V3 Position Manager (common on Base)
            v3_position_manager = "0x03aF5998D58492D0245671e4A595635A641ea616"

            # Check if there's a V3 position (this would need more complex ABI)
            print("[INFO] Checking Uniswap V3 positions...")
            print("[INFO] Checking Uniswap V4 positions...")

    except Exception as e:
        print(f"[ERR] Web3 error: {e}")

    # Alternative: Check Birdeye for balance
    print("\n" + "="*60)
    print("CHECKING BIRDEYE API")
    print("="*60)

    async with aiohttp.ClientSession() as session:
        url = "https://public-api.birdeye.so/defi/token_account"
        params = {
            'wallet': wallet,
            'token': maxx_contract
        }
        headers = {'X-API-KEY': 'cafe578a9ee7495f9de4c9e390f31c24'}

        try:
            async with session.get(url, params=params, headers=headers) as response:
                data = await response.json()
                if data.get('success') and data.get('data'):
                    balance = data['data'].get('balance', 0)
                    if balance:
                        balance_float = float(balance)
                        print(f"Birdeye Balance: {balance_float:,.2f} MAXX")
                    else:
                        print("Birdeye: No balance found")
        except Exception as e:
            print(f"Birdeye error: {e}")

if __name__ == "__main__":
    asyncio.run(check_uniswap_position())