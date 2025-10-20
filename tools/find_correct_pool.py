#!/usr/bin/env python3
"""
Find the correct MAXX/ETH pool on Base chain
==========================================
"""

import asyncio
import aiohttp
import json

async def find_maxx_pool():
    """Find the actual MAXX/ETH pool"""

    maxx_contract = "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"
    wallet = "0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9"

    print("Finding MAXX/ETH Pool on Base Chain")
    print("="*50)

    async with aiohttp.ClientSession() as session:
        # Method 1: Check Uniswap V2 Factory for pools
        print("\n[1] Checking Uniswap V2 Factory...")

        factory_abi = [
            {
                "constant": True,
                "inputs": [
                    {"name": "tokenA", "type": "address"},
                    {"name": "tokenB", "type": "address"}
                ],
                "name": "getPair",
                "outputs": [{"name": "pair", "type": "address"}],
                "type": "function"
            }
        ]

        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))

        try:
            # Uniswap V2 Factory on Base
            factory_address = w3.to_checksum_address("0x4200000000000000000000000000000000016")
            factory = w3.eth.contract(address=factory_address, abi=factory_abi)

            # WETH on Base
            weth_address = w3.to_checksum_address("0x4200000000000000000000000000000000000006")

            # Get MAXX/WETH pair
            pair_address = factory.functions.getPair(
                w3.to_checksum_address(maxx_contract),
                weth_address
            ).call()

            if pair_address != "0x0000000000000000000000000000000000000000":
                print(f"✓ Found Pool: {pair_address}")

                # Check if pool has liquidity
                pair_abi = [
                    {
                        "constant": True,
                        "inputs": [],
                        "name": "getReserves",
                        "outputs": [
                            {"name": "reserve0", "type": "uint112"},
                            {"name": "reserve1", "type": "uint112"}
                        ],
                        "type": "function"
                    },
                    {
                        "constant": True,
                        "inputs": [],
                        "name": "token0",
                        "outputs": [{"name": "", "type": "address"}],
                        "type": "function"
                    },
                    {
                        "constant": True,
                        "inputs": [],
                        "name": "token1",
                        "outputs": [{"name": "", "type": "address"}],
                        "type": "function"
                    }
                ]

                pair_contract = w3.eth.contract(address=pair_address, abi=pair_abi)
                reserves = pair_contract.functions.getReserves().call()
                token0 = pair_contract.functions.token0().call()

                reserve0 = reserves[0]
                reserve1 = reserves[1]

                # Determine which is MAXX and which is ETH
                if token0.lower() == maxx_contract.lower():
                    maxx_reserve = reserve0 / 1e18
                    eth_reserve = reserve1 / 1e18
                else:
                    maxx_reserve = reserve1 / 1e18
                    eth_reserve = reserve0 / 1e18

                print(f"\nPool Reserves:")
                print(f"  MAXX: {maxx_reserve:,.2f}")
                print(f"  ETH: {eth_reserve:.6f}")

                if maxx_reserve > 0 and eth_reserve > 0:
                    price = eth_reserve / maxx_reserve
                    print(f"  Price: 1 MAXX = {price:.8f} ETH")
                    print(f"  Liquidity: ${(eth_reserve * 3300):,.2f}")

                    # Save correct pool info
                    pool_info = {
                        "pool_address": pair_address,
                        "token0": token0,
                        "token1": weth_address,
                        "maxx_reserve": maxx_reserve,
                        "eth_reserve": eth_reserve,
                        "price": price
                    }

                    with open('maxx_correct_pool.json', 'w') as f:
                        json.dump(pool_info, f, indent=2)

                    print(f"\n✓ Pool info saved to maxx_correct_pool.json")
                    print(f"\nUse this pool address in trading: {pair_address}")
                else:
                    print(f"\n✗ Pool exists but has no liquidity!")
            else:
                print("✗ No pool found for MAXX/WETH on Uniswap V2")

        except Exception as e:
            print(f"Error: {e}")

        # Method 2: Check BaseScan for pool transactions
        print("\n[2] Checking BaseScan for pool transactions...")

        url = "https://api.basescan.org/api"
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': wallet,
            'page': 1,
            'offset': 10,
            'sort': 'desc',
            'apikey': 'Y8TCGIBF1V9FIRN6Q2R7XQJUYSUEH8C8MG'
        }

        try:
            async with session.get(url, params=params) as response:
                data = await response.json()
                if data['status'] == '1' and data['result']:
                    print("\nRecent MAXX transactions:")
                    for tx in data['result'][:5]:
                        if tx['to'].lower() == maxx_contract.lower():
                            print(f"  - IN: {int(tx['value']) / 1e18:.2f} MAXX")
                        elif tx['from'].lower() == maxx_contract.lower():
                            print(f"  - OUT: {int(tx['value']) / 1e18:.2f} MAXX")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(find_maxx_pool())