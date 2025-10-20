#!/usr/bin/env python3
"""Fetch and analyze MAXX pool data"""
import requests
import json

print('Fetching MAXX trade data from DexScreener...')

pool_address = '0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148'
url = f'https://api.dexscreener.com/latest/dex/pairs/base/{pool_address}'

try:
    response = requests.get(url, timeout=10)
    data = response.json()

    if data and 'pair' in data:
        pair = data['pair']

        print('\n' + '='*60)
        print('MAXX/ETH POOL ANALYSIS')
        print('='*60)
        print(f'Pool: {pair.get("pairAddress")}')
        print(f'DEX: {pair.get("dexId")} (Uniswap V4)')

        liquidity_usd = pair.get("liquidity", {}).get("usd", 0)
        print(f'\nLiquidity: ${liquidity_usd:,.2f}')

        volume_24h = pair.get("volume", {}).get("h24", 0)
        print(f'Volume 24h: ${volume_24h:,.2f}')
        print(f'Price USD: ${pair.get("priceUsd", 0)}')

        # Price changes
        changes = pair.get('priceChange', {})
        print(f'\nPrice Changes:')
        print(f'  5m: {changes.get("m5", 0):.2f}%')
        print(f'  1h: {changes.get("h1", 0):.2f}%')
        print(f'  6h: {changes.get("h6", 0):.2f}%')
        print(f'  24h: {changes.get("h24", 0):.2f}%')

        # Transaction counts
        txns = pair.get('txns', {})
        h24 = txns.get('h24', {})
        print(f'\nTransactions (24h):')
        print(f'  Buys: {h24.get("buys", 0)}')
        print(f'  Sells: {h24.get("sells", 0)}')

        buys = h24.get('buys', 0)
        sells = h24.get('sells', 0)
        if sells > 0:
            ratio = buys / sells
            print(f'  Buy/Sell Ratio: {ratio:.2f}')

            if ratio > 1.3:
                print('  BULLISH - More buyers!')
            elif ratio < 0.7:
                print('  BEARISH - More sellers!')
            else:
                print('  NEUTRAL')

        # Save to file
        with open('data/maxx_pool_analysis.json', 'w') as f:
            json.dump(data, f, indent=2)

        print(f'\nSaved to data/maxx_pool_analysis.json')
        print('='*60)

    else:
        print('No pool data found')

except Exception as e:
    print(f'Error: {e}')
