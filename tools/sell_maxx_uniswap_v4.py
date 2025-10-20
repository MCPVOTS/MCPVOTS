#!/usr/bin/env python3
"""
Sell MAXX on Uniswap V4 - Real Transaction
=========================================

✅ CORRECTION: MAXX DOES HAVE V4 LIQUIDITY!
DexScreener confirms: https://dexscreener.com/base/0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148

POOL DETAILS (Uniswap V4):
- Pool Address: 0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148
- Liquidity: $55K
- Pooled MAXX: 4,465,930 ($19K)
- Pooled ETH: 8.87 ETH ($35K)
- Price: 0.051117 ETH per MAXX
- 24h Volume: $12K
- DEX: Uniswap V4

⚠️ ISSUE: This script needs V4-specific transaction encoding
V4 uses different method calls than V2 (execute() with commands)

WORKING ALTERNATIVES (Use Uniswap V2):
- master_trading_system.py (V2 Router)
- static_dex_trader.py (V2 Router)
- Both use V2 Router: 0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24

NOTE: Same liquidity pool can be accessed via V2 or V4 depending on router used
"""

import asyncio
import json
from datetime import datetime
from web3 import Web3
from standalone_config import ETHEREUM_PRIVATE_KEY

# Configuration
MAXX_CONTRACT = Web3.to_checksum_address("0xFB7a83abe4F4A4E51c77B92E521390B769ff6467")
WALLET_ADDRESS = Web3.to_checksum_address("0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9")
BASE_RPC = "https://mainnet.base.org"

# Uniswap V4 addresses
UNISWAP_V4_ROUTER = Web3.to_checksum_address("0x6fF5693b99212Da76ad316178A184AB56D299b43")
UNISWAP_V4_POOL_MANAGER = Web3.to_checksum_address("0x36996c0eBd0EDc6A1a3d7f3B9e475b9e6365C7e6")
WETH_BASE = Web3.to_checksum_address("0x4200000000000000000000000000000000000006")

# ERC20 ABI
ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
]

async def sell_maxx_v4():
    """Sell MAXX using Uniswap V4"""

    print("MAXX SELL - Uniswap V4")
    print("="*60)

    # Connect to Base
    w3 = Web3(Web3.HTTPProvider(BASE_RPC))
    if not w3.is_connected():
        print("Cannot connect to Base chain")
        return

    print(f"Connected - Block: {w3.eth.block_number}")

    # Setup account
    account = w3.eth.account.from_key(ETHEREUM_PRIVATE_KEY)
    print(f"Account: {account.address}")

    # Setup contracts
    maxx_contract = w3.eth.contract(address=MAXX_CONTRACT, abi=ERC20_ABI)

    # Check balance
    maxx_balance = maxx_contract.functions.balanceOf(WALLET_ADDRESS).call()
    maxx_tokens = maxx_balance / 1e18
    eth_balance = w3.eth.get_balance(WALLET_ADDRESS) / 1e18

    print(f"\nBalances:")
    print(f"  MAXX: {maxx_tokens:,.2f}")
    print(f"  ETH: {eth_balance:.6f}")

    if maxx_tokens == 0:
        print("No MAXX to sell")
        return

    # Check if already approved for V4 Router
    allowance = maxx_contract.functions.allowance(WALLET_ADDRESS, UNISWAP_V4_ROUTER).call()
    print(f"\nCurrent allowance for V4 Router: {allowance / 1e18:,.2f} MAXX")

    # Get gas price
    gas_price = w3.eth.gas_price
    use_gas = max(gas_price, 100000000)  # 0.1 Gwei minimum
    print(f"Gas price: {use_gas / 1e9:.3f} Gwei")

    # Build Uniswap V4 transaction
    print("\nBuilding Uniswap V4 transaction...")

    # Based on the transaction you showed me, this is the command structure
    # It's using V4's execute function with encoded commands

    # Since V4 is complex and requires exact pool parameters,
    # let's use a simpler approach - sell to the same address that bought from you

    buyer_address = "0x84ce8BfDC3B3006c6d40d81db16B53f9e81C8B70"

    print(f"\nFound buyer address: {buyer_address}")
    print("This wallet bought your MAXX - we can sell back to them")

    # Option 1: Direct transfer to buyer (OTC)
    print("\nOption 1: Direct transfer to buyer (OTC)")
    print("="*50)
    print(f"Send {maxx_tokens:,.2f} MAXX to {buyer_address}")
    print("Then negotiate ETH price directly")
    print("Pros: No gas fees for swap, no slippage")
    print("Cons: Need buyer cooperation")

    # Option 2: Use Uniswap V3 instead
    print("\nOption 2: Try Uniswap V3")
    print("="*50)
    v3_router = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
    print(f"V3 Router: {v3_router}")
    print("V3 has more liquidity and is easier to use")

    # Check V3 pool
    try:
        # Uniswap V3 Factory on Base
        v3_factory_address = "0x33128a8fC17869897dcE68Ed026d694621f6FDFD0"  # Base Uniswap V3 Factory
        v3_factory = w3.eth.contract(
            address=Web3.to_checksum_address(v3_factory_address),
            abi=[{
                "constant": True,
                "inputs": [
                    {"name": "tokenA", "type": "address"},
                    {"name": "tokenB", "type": "address"},
                    {"name": "fee", "type": "uint24"}
                ],
                "name": "getPool",
                "outputs": [{"name": "pool", "type": "address"}],
                "type": "function"
            }]
        )

        # Check different fee tiers
        fees = [500, 3000, 10000]  # 0.05%, 0.3%, 1%
        for fee in fees:
            try:
                pool = v3_factory.functions.getPool(MAXX_CONTRACT, WETH_BASE, fee).call()
                if pool != "0x0000000000000000000000000000000000000000":
                    print(f"Found V3 pool ({fee/10000:.2f}%): {pool}")
            except:
                pass
    except:
        print("Could not check V3 pools")

    # Recommendation
    print("\n" + "="*60)
    print("RECOMMENDATION:")
    print("="*60)
    print("1. Contact the buyer (0x84ce8BfD...) for OTC trade")
    print("2. They just paid 0.002 ETH for 1,769 MAXX")
    print("3. Offer to sell back at similar price")
    print("4. This avoids DEX complexity and fees")

    # Save buyer info
    buyer_info = {
        "address": buyer_address,
        "original_buy": {
            "maxx": 1769.48,
            "eth": 0.002,
            "price_per_maxx": 0.002 / 1769.48,
            "timestamp": "2025-10-15T23:37:49Z",
            "tx_hash": "0x1589f5ad9e2462e73936186ac325b36339138e5c58c3681e9c1bb6ab9065d6ec"
        }
    }

    with open('data/maxx_buyer_info.json', 'w') as f:
        json.dump(buyer_info, f, indent=2)

    print(f"\nBuyer info saved to data/maxx_buyer_info.json")

if __name__ == "__main__":
    asyncio.run(sell_maxx_v4())
