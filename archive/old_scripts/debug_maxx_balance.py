#!/usr/bin/env python3
"""
Debug MAXX Balance - Check specific transaction
=============================================
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def debug_maxx_balance():
    """Debug MAXX balance issue"""

    wallet = "0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9"
    maxx_contract = "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"
    api_key = "Y8TCGIBF1V9FIRN6Q2R7XQJUYSUEH8C8MG"

    async with aiohttp.ClientSession() as session:
        print("="*60)
        print("DEBUGGING MAXX BALANCE")
        print("="*60)
        print(f"Wallet: {wallet}")
        print(f"MAXX Contract: {maxx_contract}")
        print("-"*60)

        # Check all recent transactions to wallet
        print("\n[1] Checking ALL incoming transactions...")
        url = "https://api.basescan.org/api"
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': wallet,
            'page': 1,
            'offset': 20,
            'sort': 'desc',
            'apikey': api_key
        }

        try:
            async with session.get(url, params=params) as response:
                data = await response.json()
                if data['status'] == '1' and data['result']:
                    print(f"Found {len(data['result'])} token transactions:\n")

                    maxx_balance = 0
                    for i, tx in enumerate(data['result'][:10]):
                        value = int(tx['value']) / 1e18
                        token_name = tx.get('tokenName', 'Unknown')
                        token_symbol = tx.get('tokenSymbol', 'Unknown')
                        contract_addr = tx['contractAddress']

                        direction = "IN" if tx['to'].lower() == wallet.lower() else "OUT"

                        print(f"[{i+1}] {token_symbol} ({token_name[:20]})")
                        print(f"    Direction: {direction}")
                        print(f"    Amount: {value:,.2f}")
                        print(f"    From: {tx['from']}")
                        print(f"    To: {tx['to']}")
                        print(f"    Contract: {contract_addr}")
                        print(f"    Time: {datetime.fromtimestamp(int(tx['timeStamp']))}")
                        print(f"    Hash: {tx['hash']}")
                        print()

                        # If it's MAXX, update balance
                        if contract_addr.lower() == maxx_contract.lower():
                            if direction == "IN":
                                maxx_balance += value
                            else:
                                maxx_balance -= value

                    print("="*60)
                    print(f"CALCULATED MAXX BALANCE: {maxx_balance:,.2f} MAXX")
                    print("="*60)

                    # Also check ETH balance
                    eth_url = "https://api.etherscan.io/v2/api"
                    eth_params = {
                        'module': 'account',
                        'action': 'balance',
                        'address': wallet,
                        'tag': 'latest',
                        'chainid': 8453,
                        'apikey': api_key
                    }

                    async with session.get(eth_url, params=eth_params) as eth_response:
                        eth_data = await eth_response.json()
                        if eth_data['status'] == '1':
                            eth_balance = int(eth_data['result']) / 1e18
                            print(f"ETH BALANCE: {eth_balance:.6f} ETH")
                            print(f"ETH USD VALUE: ${eth_balance * 3300:.2f}")

        except Exception as e:
            print(f"Error: {e}")

        # Now let's specifically check for the transaction mentioned
        print("\n" + "="*60)
        print("CHECKING SPECIFIC TRANSACTION FROM UNISWAP V4")
        print("="*60)

        # Look for transactions from Uniswap V4 Pool Manager
        url2 = "https://api.basescan.org/api"
        params2 = {
            'module': 'account',
            'action': 'tokentx',
            'address': wallet,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'desc',
            'apikey': api_key
        }

        try:
            async with session.get(url2, params=params2) as response:
                data = await response.json()
                if data['status'] == '1' and data['result']:
                    for tx in data['result']:
                        if 'Pool Manager' in tx.get('tokenName', '') or tx['from'].lower().startswith('0x84ce8bfd'):
                            value = int(tx['value']) / 1e18
                            print(f"Found Uniswap V4 transaction:")
                            print(f"  Amount: {value:,.2f} MAXX")
                            print(f"  From: {tx['from']}")
                            print(f"  To: {tx['to']}")
                            print(f"  Hash: {tx['hash']}")
                            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_maxx_balance())