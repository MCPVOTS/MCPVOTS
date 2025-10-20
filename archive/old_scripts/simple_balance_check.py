#!/usr/bin/env python3
"""
Simple Balance Checker
======================

Check wallet balance using BaseScan API
"""

import requests
import json
from decimal import Decimal

# Configuration
WALLET_ADDRESS = "0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9"
ETHERSCAN_API_KEY = "Y8TCGIBF1V9FIRN6Q2R7XQJUYSUEH8C8MG"  # Etherscan V2 API key
BASE_CHAIN_ID = 8453  # Base chain ID

def check_eth_balance():
    """Check ETH balance using Etherscan V2 API"""
    url = "https://api.etherscan.io/v2/api"
    params = {
        "module": "account",
        "action": "balance",
        "address": WALLET_ADDRESS,
        "tag": "latest",
        "chainid": BASE_CHAIN_ID,
        "apikey": ETHERSCAN_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] == "1":
            balance_wei = int(data["result"])
            balance_eth = Decimal(balance_wei) / Decimal(10**18)
            return balance_eth
        else:
            print(f"Error: {data.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error fetching balance: {e}")
        return None

def main():
    """Main balance check"""
    print("="*60)
    print("WALLET BALANCE CHECK")
    print("="*60)
    print(f"Address: {WALLET_ADDRESS}")
    print()

    # Check ETH balance
    print("Checking ETH balance...")
    eth_balance = check_eth_balance()

    if eth_balance is not None:
        print(f"[OK] ETH Balance: {eth_balance:.6f} ETH")

        # Calculate USD value
        eth_price_usd = 3300  # Approximate ETH price
        eth_usd = float(eth_balance) * eth_price_usd
        print(f"   Value: ${eth_usd:.2f} USD")

        # Trading recommendations
        print("\nTrading Recommendations:")
        if eth_balance < 0.001:
            print("[!] LOW ETH BALANCE (< 0.001 ETH)")
            print("   - Need to add ETH to trade")
            print("   - Current balance is insufficient for gas fees")
        elif eth_balance < 0.01:
            print("[!] Low ETH balance (0.001 - 0.01 ETH)")
            print("   - Recommend very small test trades only")
            print("   - Use minimum position sizes")
        elif eth_balance < 0.1:
            print("[OK] Moderate ETH balance (0.01 - 0.1 ETH)")
            print("   - Can trade with caution")
            print("   - Recommended position size: $1-10")
        else:
            print("[OK] Good ETH balance (> 0.1 ETH)")
            print("   - Ready for active trading")
            print("   - Can use larger position sizes")

    else:
        print("[ERROR] Failed to fetch balance")
        print("Possible reasons:")
        print("  - Network issues")
        print("  - Invalid API key")
        print("  - Rate limiting")

    print("="*60)

if __name__ == "__main__":
    main()