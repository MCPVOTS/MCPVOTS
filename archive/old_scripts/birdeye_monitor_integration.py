#!/usr/bin/env python3
"""
Birdeye Integration for MAXX Master Trading System
================================================

Adds real-time price monitoring and market data to the existing trading system
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BirdeyeMonitor:
    """Birdeye API monitor for real-time data"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://public-api.birdeye.so"
        self.session = None
        self.callbacks = []

    async def initialize(self):
        """Initialize the monitor"""
        self.session = aiohttp.ClientSession(
            headers={'X-API-KEY': self.api_key}
        )
        logger.info("Birdeye monitor initialized")

    async def get_token_price(self, address):
        """Get current token price"""
        url = f"{self.base_url}/defi/price"
        params = {'address': address}

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and data.get('data'):
                        return float(data['data']['price'])
        except Exception as e:
            logger.error(f"Error getting price: {e}")

        return 0

    async def get_token_info(self, address):
        """Get comprehensive token information"""
        url = f"{self.base_url}/public/tokenv2/token_info"
        params = {'address': address}

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and data.get('data'):
                        token = data['data']
                        return {
                            'price': token.get('price', 0),
                            'price_change_24h': token.get('priceChange24h', 0),
                            'volume_24h': token.get('volume24h', 0),
                            'market_cap': token.get('mc', 0),
                            'liquidity': token.get('liquidity', 0),
                            'holders': token.get('holder', 0)
                        }
        except Exception as e:
            logger.error(f"Error getting token info: {e}")

        return None

    async def add_price_callback(self, callback):
        """Add callback for price updates"""
        self.callbacks.append(callback)

    async def start_monitoring(self, token_address, interval=30):
        """Start monitoring token price"""
        logger.info(f"Starting price monitoring for {token_address}")

        last_price = 0

        while True:
            try:
                current_price = await self.get_token_price(token_address)

                if current_price > 0:
                    # Calculate price change
                    if last_price > 0:
                        price_change = ((current_price - last_price) / last_price) * 100

                        # Trigger callbacks for significant changes
                        if abs(price_change) >= 5:  # 5% change threshold
                            for callback in self.callbacks:
                                await callback({
                                    'price': current_price,
                                    'change_percent': price_change,
                                    'timestamp': datetime.now(),
                                    'address': token_address
                                })

                    last_price = current_price

                await asyncio.sleep(interval)

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(5)


# Integrate with existing master trading system
async def integrate_birdeye_monitor(trading_system):
    """Integrate Birdeye monitor into the trading system"""

    # Initialize Birdeye monitor with API key from environment
    api_key = 'cafe578a9ee7495f9de4c9e390f31c24'
    monitor = BirdeyeMonitor(api_key)

    # Price change alert handler
    async def price_alert(data):
        price = data['price']
        change = data['change_percent']

        print(f"\n[PRICE ALERT] MAXX: ${price:.8f} ({change:+.2f}%)")

        # Get current balances
        eth_balance, maxx_balance = await trading_system.get_balances()

        # Generate trading signal based on price change
        if change > 10:  # 10% pump
            print("[SIGNAL] Strong upward momentum detected!")
            print("         Consider selling some holdings for profit")
        elif change < -10:  # 10% dump
            print("[SIGNAL] Sharp drop detected!")
            print("         Consider buying the dip")

    # Set up monitoring
    await monitor.initialize()
    await monitor.add_price_callback(price_alert)

    # Start monitoring in background
    monitor_task = asyncio.create_task(
        monitor.start_monitoring('0xFB7a83abe4F4A4E51c77B92E521390B769ff6467')
    )

    return monitor_task


# Enhanced trading strategy with Birdeye data
class EnhancedTradingStrategy:
    """Enhanced trading strategy using Birdeye data"""

    def __init__(self):
        self.min_profit_threshold = 0.15  # 15% profit
        self.max_loss_threshold = 0.05   # 5% loss
        self.position_size_limit = 0.5   # 50% of balance
        self.monitor = None

    async def analyze_market(self, trading_system, token_data):
        """Analyze market conditions and generate trading decisions"""

        current_price = token_data['price']
        price_change_24h = token_data['price_change_24h']
        volume_24h = token_data['volume_24h']
        liquidity = token_data['liquidity']

        # Get current balances
        eth_balance, maxx_balance = await trading_system.get_balances()

        decisions = []

        # Decision 1: Buy on dip
        if price_change_24h < -20 and maxx_balance == 0:
            if eth_balance > 0.001:  # Minimum balance check
                buy_amount = min(eth_balance * 0.1, Decimal('0.001'))
                decisions.append({
                    'action': 'BUY',
                    'amount': buy_amount,
                    'reason': f"24h dip of {price_change_24h:.1f}%",
                    'confidence': 0.8
                })

        # Decision 2: Sell on profit
        if maxx_balance > 0:
            # Calculate current position value
            position_value_eth = maxx_balance * current_price
            position_value_usd = float(position_value_eth) * 3300

            # Need entry price - would store this in ChromaDB
            entry_price_estimate = current_price * (1 - abs(price_change_24h) / 100)
            potential_pnl = ((current_price - entry_price_estimate) / entry_price_estimate) * 100

            if potential_pnl > 30:  # 30% profit
                decisions.append({
                    'action': 'SELL_PARTIAL',
                    'amount': maxx_balance * Decimal('0.5'),  # Sell 50%
                    'reason': f"Potential profit: {potential_pnl:.1f}%",
                    'confidence': 0.85
                })
            elif potential_pnl < -15:  # 15% loss
                decisions.append({
                    'action': 'HOLD',
                    'amount': maxx_balance,
                    'reason': f"Loss position - wait for recovery",
                    'confidence': 0.7
                })

        # Decision 3: Volume-based signals
        if volume_24h > 10000 and liquidity > 50000:
            # High volume and liquidity = good trading conditions
            if price_change_24h > 0:
                decisions.append({
                    'action': 'BUY_SMALL',
                    'amount': min(eth_balance * 0.05, Decimal('0.0005')),
                    'reason': "High volume and momentum",
                    'confidence': 0.6
                })

        return decisions


# Wrapper function for existing master trading system
async def enhance_master_system_with_birdeye():
    """Enhance the master trading system with Birdeye monitoring"""

    # Import the master trading system
    from master_trading_system import MasterTradingSystem
    import standalone_config as config

    # Create trading system
    system = MasterTradingSystem()

    # Initialize system
    if await system.initialize():
        print("Master Trading System initialized successfully")

        # Initialize Birdeye monitoring
        monitor_task = await integrate_birdeye_monitor(system)

        # Create enhanced strategy
        strategy = EnhancedTradingStrategy()

        print("\n" + "="*60)
        print("ENHANCED MAXX TRADING SYSTEM")
        print("="*60)
        print("Features:")
        print("- Real-time price monitoring via Birdeye API")
        print("- Automated trading decisions")
        print("- Volume and momentum analysis")
        print("- Profit/loss optimization")
        print("\nPress Ctrl+C to stop")
        print("-"*60)

        # Run enhanced interactive mode
        while True:
            try:
                # Get current data
                monitor = BirdeyeMonitor('cafe578a9ee7495f9de4c9e390f31c24')
                await monitor.initialize()
                token_data = await monitor.get_token_info('0xFB7a83abe4F4A4E51c77B92E521390B769ff6467')

                if token_data:
                    print(f"\n[MARKET DATA]")
                    print(f"Price: ${token_data['price']:.8f}")
                    print(f"24h Change: {token_data['price_change_24h']:+.2f}%")
                    print(f"Volume 24h: ${token_data['volume_24h']:,.0f}")
                    print(f"Liquidity: ${token_data['liquidity']:,.0f}")

                    # Analyze and show decisions
                    decisions = await strategy.analyze_market(system, token_data)

                    if decisions:
                        print(f"\n[TRADING DECISIONS]")
                        for decision in decisions:
                            print(f"- {decision['action']}: {decision['reason']}")
                            print(f"  Confidence: {decision['confidence']*100:.0f}%")

                    # Show current balances
                    eth_balance, maxx_balance = await system.get_balances()
                    print(f"\n[BALANCES]")
                    print(f"ETH: {eth_balance:.6f}")
                    print(f"MAXX: {maxx_balance:,.2f}")

                # Interactive options
                print(f"\n[OPTIONS]")
                print(f"1. Execute buy (${config.TEST_ETH_AMOUNT} ETH)")
                print(f"2. Execute sell (all MAXX)")
                print(f"3. View detailed status")
                print(f"4. Exit")

                # In production, you would actually execute trades here
                # For now, showing the structure

                await asyncio.sleep(30)

            except KeyboardInterrupt:
                print("\nStopping...")
                break

        # Cancel monitoring task
        monitor_task.cancel()

    else:
        print("Failed to initialize trading system")


if __name__ == "__main__":
    # Run enhanced system
    asyncio.run(enhance_master_system_with_birdeye())