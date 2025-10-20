#!/usr/bin/env python3
"""
Quick Launch MAXX Intelligence
=============================

Run comprehensive MAXX token analysis
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from maxx_intelligence_analyzer import MAXXIntelligenceAnalyzer

async def quick_analysis():
    """Run quick analysis with key outputs"""
    print("="*80)
    print("QUICK MAXX INTELLIGENCE SCAN")
    print("="*80)
    print("Analyzing for pump patterns and whale activity...")
    print()

    analyzer = MAXXIntelligenceAnalyzer()

    # Collect recent trades (last 24 hours for demo)
    print("Step 1: Fetching recent trades...")
    current_time = int(__import__('time').time())
    trades = await analyzer._fetch_trades_in_range(
        current_time - 86400,  # Last 24 hours
        current_time
    )

    print(f"Found {len(trades)} recent trades")

    if trades:
        # Basic analysis
        print("\nStep 2: Quick analysis...")

        # Calculate basic metrics
        total_volume = sum(t['value_usd'] for t in trades)
        avg_trade = total_volume / len(trades) if trades else 0
        unique_wallets = len(set(t['from_address'] for t in trades))

        print(f"\n📊 QUICK STATS:")
        print(f"Total Volume (24h): ${total_volume:.2f}")
        print(f"Average Trade Size: ${avg_trade:.2f}")
        print(f"Unique Wallets: {unique_wallets}")

        # Find large trades
        large_trades = [t for t in trades if t['value_usd'] > 50]
        if large_trades:
            print(f"\n🐳 LARGE TRADES DETECTED:")
            for trade in large_trades[:5]:
                print(f"  - ${trade['value_usd']:.2f} from {trade['from_address'][:10]}...")

        # Check for pump indicators
        hourly_volume = {}
        for trade in trades:
            hour = trade['timestamp'] // 3600
            hourly_volume[hour] = hourly_volume.get(hour, 0) + trade['value_usd']

        if hourly_volume:
            max_hour_volume = max(hourly_volume.values())
            avg_hour_volume = sum(hourly_volume.values()) / len(hourly_volume)
            pump_indicator = max_hour_volume / avg_hour_volume if avg_hour_volume > 0 else 1

            print(f"\n🚀 PUMP INDICATORS:")
            print(f"Peak Hour Volume: ${max_hour_volume:.2f}")
            print(f"Average Hour Volume: ${avg_hour_volume:.2f}")
            print(f"Pump Score: {min(pump_indicator, 10):.2f}/10")

            if pump_indicator > 3:
                print("⚠️ PUMP ACTIVITY DETECTED!")

        # Save quick report
        quick_report = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'total_trades_24h': len(trades),
            'total_volume_24h': total_volume,
            'unique_wallets': unique_wallets,
            'large_trades': len(large_trades),
            'pump_score': min(pump_indicator, 10) if 'pump_indicator' in locals() else 0
        }

        with open('maxx_quick_intel.json', 'w') as f:
            import json
            json.dump(quick_report, f, indent=2)

        print(f"\n✅ Quick report saved to maxx_quick_intel.json")

        # Trading recommendations
        print("\n💡 TRADING RECOMMENDATIONS:")
        if large_trades:
            print("- Monitor whale wallets for entry points")
        if pump_indicator > 2:
            print("- Set buy orders for dip entries")
            print("- Be ready for quick profit taking")
        print("- Use optimal gas pricing for savings")
        print("- Follow coordinated buying patterns")

    print("\n" + "="*80)
    print("For full analysis, run: python maxx_intelligence_analyzer.py")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(quick_analysis())