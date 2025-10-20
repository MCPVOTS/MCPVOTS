#!/usr/bin/env python3
"""
Check Wallet Balance
===================

Quick script to check current wallet balance
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from master_trading_system import MasterTradingSystem

async def main():
    """Check wallet balance"""
    print("="*60)
    print("WALLET BALANCE CHECK")
    print("="*60)

    system = MasterTradingSystem()

    if await system.initialize():
        try:
            eth_balance, maxx_balance = await system.get_balances()

            print(f"Address: {system.account.address}")
            print(f"ETH Balance: {eth_balance:.6f} ETH")
            print(f"MAXX Balance: {maxx_balance:,.2f} MAXX")

            # Calculate USD value (assuming ETH ~ $3300)
            eth_usd = float(eth_balance) * 3300
            print(f"\nPortfolio Value:")
            print(f"ETH Value: ${eth_usd:.2f} USD")

            if maxx_balance > 0:
                # Get current MAXX price (simplified)
                maxx_price = 0.000033  # Approximate price in ETH
                maxx_usd = float(maxx_balance) * maxx_price * 3300
                print(f"MAXX Value: ${maxx_usd:.2f} USD")
                total_usd = eth_usd + maxx_usd
                print(f"\nTotal Portfolio Value: ${total_usd:.2f} USD")
            else:
                print(f"\nTotal Portfolio Value: ${eth_usd:.2f} USD")

            print("="*60)

            # Trading recommendations based on balance
            print("\nTrading Recommendations:")
            if eth_balance < 0.001:
                print("⚠️ LOW ETH BALANCE - Need to add ETH to trade")
            elif eth_balance < 0.01:
                print("⚠️ Low ETH balance - Recommend small test trades only")
            else:
                print("✅ Sufficient ETH balance for trading")

            if maxx_balance > 0:
                print("✅ You have MAXX tokens - Can sell if profitable")

        except Exception as e:
            print(f"Error checking balance: {e}")
    else:
        print("❌ Failed to initialize trading system")

if __name__ == "__main__":
    asyncio.run(main())