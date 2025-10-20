#!/usr/bin/env python3
"""
Find AAVE contract on Base chain
"""

import requests

print('🔍 Finding correct AAVE contract on Base chain...')
print()

# Search for AAVE on Base chain
try:
    search_response = requests.get('https://api.basescan.org/api?module=token&action=search&query=aave&apikey=Y8TCGIBF1V9FIRN6Q2R7XQJUYSUEH8C8MG', timeout=10)
    if search_response.status_code == 200:
        search_data = search_response.json()
        if search_data.get('status') == '1':
            results = search_data.get('result', [])
            print('📊 AAVE tokens found on Base chain:')
            for token in results[:5]:  # Show first 5 results
                print(f'   {token.get("symbol", "Unknown")}: {token.get("contractAddress", "N/A")}')
                print(f'     Name: {token.get("tokenName", "Unknown")}')
                print()
        else:
            print('❌ No AAVE tokens found on Base chain')
    else:
        print('❌ Search API failed')
except Exception as e:
    print(f'❌ Search failed: {e}')

print()
print('💡 If AAVE is not on Base, we may need to bridge from Ethereum mainnet')
print('💡 Base has cheaper gas but may not have all tokens')
