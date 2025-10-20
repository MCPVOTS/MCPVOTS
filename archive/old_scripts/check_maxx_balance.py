#!/usr/bin/env python3
"""
MAXX Balance Checker - Base Chain
=================================
"""

import asyncio
import aiohttp
import json

async def check_maxx_balance():
    """Check MAXX token balance on Base chain"""

    wallet = "0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9"
    maxx_contract = "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"
    api_key = "Y8TCGIBF1V9FIRN6Q2R7XQJUYSUEH8C8MG"

    async with aiohttp.ClientSession() as session:
        # Method 1: Try BaseScan token balance
        print("[1] Checking BaseScan token balance...")
        url1 = "https://api.basescan.org/api"
        params1 = {
            'module': 'account',
            'action': 'tokenbalance',
            'contractaddress': maxx_contract,
            'address': wallet,
            'tag': 'latest',
            'apikey': api_key
        }

        try:
            async with session.get(url1, params=params1) as response:
                data = await response.json()
                if data['status'] == '1' and data['result']:
                    balance = int(data['result']) / 1e18
                    print(f"[OK] BaseScan Balance: {balance:,.2f} MAXX")
                    return balance
        except Exception as e:
            print(f"[ERR] BaseScan failed: {e}")

        # Method 2: Try Etherscan V2 with chainid
        print("\n[2] Checking Etherscan V2...")
        url2 = "https://api.etherscan.io/v2/api"
        params2 = {
            'module': 'account',
            'action': 'tokenbalance',
            'contractaddress': maxx_contract,
            'address': wallet,
            'tag': 'latest',
            'chainid': 8453,
            'apikey': api_key
        }

        try:
            async with session.get(url2, params=params2) as response:
                data = await response.json()
                if data['status'] == '1' and data['result']:
                    balance = int(data['result']) / 1e18
                    print(f"[OK] Etherscan V2 Balance: {balance:,.2f} MAXX")
                    return balance
        except Exception as e:
            print(f"[ERR] Etherscan V2 failed: {e}")

        # Method 3: Check recent transactions to infer balance
        print("\n[3] Checking recent token transactions...")
        url3 = "https://api.basescan.org/api"
        params3 = {
            'module': 'account',
            'action': 'tokentx',
            'address': wallet,
            'page': 1,
            'offset': 50,
            'sort': 'desc',
            'apikey': api_key
        }

        try:
            async with session.get(url3, params=params3) as response:
                data = await response.json()
                if data['status'] == '1' and data['result']:
                    maxx_balance = 0
                    for tx in data['result']:
                        # Look for MAXX transactions
                        if tx['contractAddress'].lower() == maxx_contract.lower():
                            value = int(tx['value']) / 1e18
                            if tx['to'].lower() == wallet.lower():
                                maxx_balance += value
                                print(f"  IN: +{value:,.2f} MAXX")
                            else:
                                maxx_balance -= value
                                print(f"  OUT: -{value:,.2f} MAXX")

                    print(f"[OK] Calculated Balance: {maxx_balance:,.2f} MAXX")
                    return maxx_balance
        except Exception as e:
            print(f"[ERR] Transaction check failed: {e}")

        # Method 4: Use Moralis API (alternative)
        print("\n[4] Trying alternative method...")
        # This would require a Moralis API key

        print("\n[ERR] All methods failed. Check API keys and network.")
        return 0

if __name__ == "__main__":
    asyncio.run(check_maxx_balance())