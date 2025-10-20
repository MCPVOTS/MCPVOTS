#!/usr/bin/env python3
"""
Launch AI Ultra Smart Trader
============================

Simple launch script for the AI Ultra Smart Trading System
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai_ultra_smart_trader import AISmartTrader
from ai_trader_config import get_config

async def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description="Launch AI Ultra Smart Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch_ai_ultra_trader.py                    # Run with default settings
  python launch_ai_ultra_trader.py --config dev       # Run in development mode
  python launch_ai_ultra_trader.py --dry-run         # Paper trading mode
        """
    )

    parser.add_argument(
        '--config',
        choices=['dev', 'prod', 'test'],
        default='prod',
        help='Configuration preset to use'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Enable paper trading mode (no real transactions)'
    )

    parser.add_argument(
        '--max-positions',
        type=int,
        help='Override maximum number of positions'
    )

    parser.add_argument(
        '--position-size',
        type=float,
        help='Override maximum position size in USD'
    )

    parser.add_argument(
        '--risk-per-trade',
        type=float,
        help='Override risk per trade (e.g., 0.02 for 2%)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Print startup banner
    print("="*80)
    print("AI ULTRA SMART TRADING SYSTEM V2.0")
    print("="*80)
    print("Advanced AI-powered cryptocurrency trading")
    print("Features:")
    print("- Multi-strategy AI trading")
    print("- Real-time market sentiment analysis")
    print("- Predictive price modeling")
    print("- Dynamic risk management")
    print("- Swarm detection")
    print("- MEV protection")
    print("="*80)
    print()

    # Initialize trader
    trader = AISmartTrader()

    # Apply command line overrides
    if args.dry_run:
        print("📝 PAPER TRADING MODE ENABLED")
        trader.config['paper_trading'] = True

    if args.max_positions:
        trader.config['max_positions'] = args.max_positions
        print(f"📊 Max positions: {args.max_positions}")

    if args.position_size:
        trader.config['max_position_size_usd'] = args.position_size
        print(f"💰 Max position size: ${args.position_size}")

    if args.risk_per_trade:
        trader.config['risk_per_trade'] = args.risk_per_trade
        print(f"⚠️ Risk per trade: {args.risk_per_trade*100}%")

    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        print("🔍 Verbose logging enabled")

    # Load configuration preset
    config_preset = get_config(args.config)
    if args.config == 'dev':
        print("🛠️ Development configuration loaded")
        trader.config.update(config_preset.get('dev', {}))

    # Final warning for live trading
    if not args.dry_run and args.config == 'prod':
        print("\n⚠️ WARNING: LIVE TRADING MODE")
        print("This will execute REAL transactions with REAL money!")
        print("Press Ctrl+C within 5 seconds to cancel...")
        try:
            await asyncio.sleep(5)
        except KeyboardInterrupt:
            print("\nCancelled by user")
            return 0

    # Initialize and run
    try:
        if await trader.initialize():
            await trader.run_ultra_smart_trading()
        else:
            print("❌ Failed to initialize trader")
            return 1
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1
    finally:
        if trader.running:
            await trader.shutdown()

    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))