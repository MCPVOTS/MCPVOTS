#!/usr/bin/env python3
"""
Example usage of Flaunch Token Creator

This script demonstrates how to create different types of Flaunch tokens
with various parameters and configurations.
"""

import os
import sys
from flaunch_token_creator import FlaunchTokenCreator

def example_basic_token():
    """Create a basic token with default parameters"""
    print("🚀 Creating basic Flaunch token...")

    # Set required environment variables
    os.environ['PRIVATE_KEY'] = 'your_private_key_here'  # Replace with actual key
    os.environ['WALLET_ADDRESS'] = '0xYourWalletAddress'  # Replace with actual address

    creator = FlaunchTokenCreator()

    result = creator.create_token(
        name="Example Token",
        symbol="EXAMPLE",
        initial_market_cap=5000,  # $5k - no protocol fees
        fair_launch_percent=60,   # 60% fair launch
        creator_fee_percent=50    # 50% creator fees
    )

    if result["success"]:
        print("✅ Basic token created successfully!")
        print(f"Token: {result['name']} (${result['symbol']})")
    else:
        print("❌ Token creation failed:", result.get("error"))

def example_premium_token():
    """Create a premium token with custom metadata"""
    print("\n🎯 Creating premium token with custom metadata...")

    creator = FlaunchTokenCreator()

    result = creator.create_token(
        name="Premium DeFi Token",
        symbol="PREMIUM",
        initial_market_cap=25000,  # $25k - will incur protocol fees
        fair_launch_percent=70,    # 70% fair launch (more fair)
        fair_launch_duration=3600, # 1 hour fair launch
        creator_fee_percent=75,    # 75% creator fees (high reward)
        description="A premium DeFi token with advanced features and high creator rewards",
        image_url="https://example.com/premium-token.png",
        external_url="https://premium-defi.com"
    )

    if result["success"]:
        print("✅ Premium token created!")
        print(f"Token: {result['name']} (${result['symbol']})")
        print("💰 High creator fee share: 75%")
        print("🛡️ Extended fair launch: 1 hour")

def example_community_token():
    """Create a community-focused token"""
    print("\n🌐 Creating community token...")

    creator = FlaunchTokenCreator()

    result = creator.create_token(
        name="Community Coin",
        symbol="COMMUNITY",
        initial_market_cap=10000,  # $10k - protocol fee threshold
        fair_launch_percent=50,    # 50% fair launch
        creator_fee_percent=10,    # Only 10% creator fees
        description="A token owned and governed by the community",
        external_url="https://community-coin.org"
    )

    if result["success"]:
        print("✅ Community token created!")
        print(f"Token: {result['name']} (${result['symbol']})")
        print("🤝 Low creator fees: 10% (community focused)")
        print("📊 Balanced fair launch: 50%")

def demonstrate_royalty_nft_concept():
    """Explain the Royalty NFT concept"""
    print("\n👑 Understanding Royalty NFTs:")
    print("=" * 50)
    print("After creating your token, you receive a Royalty NFT that:")
    print("• Represents ownership of future trading fees")
    print("• Can be sold to investors for immediate capital")
    print("• Can be fractionalized among community members")
    print("• Provides passive ETH income from all trading")
    print("• Can be used as collateral or in DeFi protocols")
    print("\n💡 Example: Sell 50% of your Royalty NFT to raise funds")
    print("   Keep 50% for continued passive income")

def demonstrate_progressive_bid_wall():
    """Explain the Progressive Bid Wall mechanism"""
    print("\n🛡️ Understanding Progressive Bid Wall (PBW):")
    print("=" * 50)
    print("Flaunch tokens include automatic price protection:")
    print("• Trading fees create buy orders below current price")
    print("• Protects against extreme price dumps")
    print("• Community benefits from remaining fees")
    print("• Uses Uniswap V4 hooks for advanced mechanics")
    print("\n📈 Result: More stable price action and community benefits")

def main():
    """Run all examples"""
    print("🎉 Flaunch Token Creator Examples")
    print("=" * 40)

    # Check if environment is set up
    if not os.getenv('PRIVATE_KEY') or os.getenv('PRIVATE_KEY') == 'your_private_key_here':
        print("⚠️  Please set your PRIVATE_KEY environment variable first!")
        print("   export PRIVATE_KEY='0x...'")
        print("\n📝 These examples will show the process without actually creating tokens.")
        print("   Remove the 'your_private_key_here' check to run live transactions.\n")

    # Run examples (commented out to prevent accidental token creation)
    # example_basic_token()
    # example_premium_token()
    # example_community_token()

    # Show concepts
    demonstrate_royalty_nft_concept()
    demonstrate_progressive_bid_wall()

    print("\n🚀 Ready to create your own Flaunch tokens!")
    print("   Run: python flaunch_token_creator.py --help")

if __name__ == "__main__":
    main()
