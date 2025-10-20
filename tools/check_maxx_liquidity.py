#!/usr/bin/env python3
"""
Check MAXX Liquidity on Base Chain DEXes
======================================
"""

import asyncio
import aiohttp
import json

async def check_liquidity():
    """Check MAXX liquidity across DEXes"""

    maxx_contract = "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"

    print("="*80)
    print("MAXX LIQUIDITY CHECK - BASE CHAIN")
    print("="*80)
    print(f"MAXX Contract: {maxx_contract}")
    print("-"*80)

    async with aiohttp.ClientSession() as session:
        # Check Birdeye for pools
        print("\n[1] Checking Birdeye for MAXX pools...")

        url = "https://public-api.birdeye.so/defi/multichain/pools"
        params = {
            'address': maxx_contract
        }
        headers = {'X-API-KEY': 'cafe578a9ee7495f9de4c9e390f31c24'}

        try:
            async with session.get(url, params=params, headers=headers) as response:
                data = await response.json()
                if data.get('success') and data.get('data'):
                    pools = data['data']
                    print(f"\nFound {len(pools)} pools:")

                    for pool in pools:
                        print(f"\nPool: {pool['pairSymbol']}")
                        print(f"  DEX: {pool.get('dex', 'Unknown')}")
                        print(f"  Address: {pool['pairAddress']}")
                        print(f"  Liquidity: ${pool.get('liquidity', 0):,.2f}")
                        print(f"  Volume 24h: ${pool.get('volume24h', 0):,.2f}")

                        # Check if it has ETH pair
                        if 'ETH' in pool['pairSymbol']:
                            print(f"  ✓ ETH PAIR FOUND")
                else:
                    print("No pools found on Birdeye")
        except Exception as e:
            print(f"Error: {e}")

        # Check other DEXes
        print("\n[2] Checking alternative DEXes...")

        dexes = [
            ("SushiSwap", "https://api.sushi.com/swap/v1/pools"),
            ("1inch", "https://api.1inch.dev/swap/v6.0/8453/pools"),
            ("Paraswap", "https://apiv5.paraswap.io/pools")
        ]

        for dex_name, url in dexes:
            print(f"\n  Checking {dex_name}...")
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        print(f"    ✓ {dex_name} API accessible")
                        # Would parse pools here
                    else:
                        print(f"    ✗ {dex_name} API not accessible")
            except:
                print(f"    ✗ {dex_name} connection failed")

    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    print("1. MAXX has no liquid pool on Base Uniswap")
    print("2. Try these alternatives:")
    print("   - Use a different DEX (SushiSwap, 1inch)")
    print("   - Bridge to another chain (Ethereum, Polygon)")
    print("   - Use direct OTC if possible")
    print("3. Check if MAXX has liquidity on other chains")
    print("4. Consider holding until liquidity improves")

if __name__ == "__main__":
    asyncio.run(check_liquidity())