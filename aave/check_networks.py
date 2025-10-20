#!/usr/bin/env python3
"""
Check AAVE contracts on different networks
"""

import requests

print('🔍 Checking AAVE contracts on different networks...')
print()

# Check Ethereum mainnet AAVE
try:
    eth_response = requests.get('https://api.etherscan.io/api?module=token&action=tokeninfo&contractaddress=0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9&apikey=Y8TCGIBF1V9FIRN6Q2R7XQJUYSUEH8C8MG', timeout=10)
    if eth_response.status_code == 200:
        eth_data = eth_response.json()
        if eth_data.get('status') == '1':
            print('📊 Ethereum Mainnet AAVE:')
            print('   Contract: 0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9')
            result = eth_data.get('result', [{}])[0]
            print(f'   Symbol: {result.get("symbol", "AAVE")}')
            print(f'   Name: {result.get("tokenName", "AAVE")}')
        print()
except Exception as e:
    print(f'❌ Ethereum check failed: {e}')
    print()

# Check Base chain AAVE
try:
    base_response = requests.get('https://api.basescan.org/api?module=token&action=tokeninfo&contractaddress=0x63706e401c06ac8513145b7687A14804d17f814b&apikey=Y8TCGIBF1V9FIRN6Q2R7XQJUYSUEH8C8MG', timeout=10)
    if base_response.status_code == 200:
        base_data = base_response.json()
        if base_data.get('status') == '1':
            print('📊 Base Chain AAVE:')
            print('   Contract: 0x63706e401c06ac8513145b7687A14804d17f814b')
            result = base_data.get('result', [{}])[0]
            print(f'   Symbol: {result.get("symbol", "Unknown")}')
            print(f'   Name: {result.get("tokenName", "Unknown")}')
        else:
            print('❌ Base AAVE contract not found or invalid')
        print()
except Exception as e:
    print(f'❌ Base check failed: {e}')
    print()

print('💡 Base is an Ethereum Layer 2 network - cheaper gas, faster transactions')
print('💡 Ethereum mainnet has the original AAVE token')
print('🤔 Which network do you want to use for AAVE trading?')
