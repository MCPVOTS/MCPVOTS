#!/usr/bin/env python3
"""
Check Base Chain Wallet Balance
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_eth_price():
    """Get current ETH price in USD"""
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('ethereum', {}).get('usd', 0)
        return 0
    except Exception as e:
        print(f"Error getting ETH price: {e}")
        return 0

def get_wallet_balance():
    """Get wallet balance from BaseScan"""
    wallet_address = os.getenv('WALLET_PUBLIC_KEY')
    api_key = os.getenv('BASESCAN_API_KEY')

    if not wallet_address or not api_key:
        print("❌ Wallet address or API key not found in .env")
        return None

    try:
        # Get ETH balance
        url = f"https://api.basescan.org/api?module=account&action=balance&address={wallet_address}&tag=latest&apikey={api_key}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == '1':
                balance_wei = int(data.get('result', '0'))
                balance_eth = balance_wei / 10**18
                return balance_eth
            else:
                print(f"❌ API Error: {data.get('message')}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Error checking balance: {e}")
        return None

def main():
    print("🔍 Checking Base Chain Wallet Balance")
    print("=" * 50)

    # Get wallet address
    wallet_address = os.getenv('WALLET_PUBLIC_KEY')
    if not wallet_address:
        print("❌ WALLET_PUBLIC_KEY not found in .env")
        return

    print(f"📱 Wallet: {wallet_address[:10]}...{wallet_address[-8:]}")

    # Get ETH balance
    eth_balance = get_wallet_balance()
    if eth_balance is None:
        return

    print(f"💰 ETH Balance: {eth_balance:.6f} ETH")

    # Get ETH price
    eth_price = get_eth_price()
    if eth_price > 0:
        usd_value = eth_balance * eth_price
        print(f"💵 USD Value: ${usd_value:.2f}")

        # Calculate trading capital (above $5 reserve)
        reserve_usd = 5.0
        if usd_value > reserve_usd:
            trading_capital = usd_value - reserve_usd
            trading_eth = trading_capital / eth_price
            print(f"🛡️  Reserve: ${reserve_usd:.2f} ({reserve_usd/eth_price:.6f} ETH)")
            print(f"⚡ Trading Capital: ${trading_capital:.2f} ({trading_eth:.6f} ETH)")
            print(f"🎯 Available for AAVE Bot: ${trading_capital:.2f}")
        else:
            print(f"⚠️  Insufficient balance for trading (need >${reserve_usd:.2f})")
            print(f"💡 Current balance only allows ${usd_value:.2f} after $5 reserve")
    else:
        print("❌ Could not get ETH price")

if __name__ == '__main__':
    main()
