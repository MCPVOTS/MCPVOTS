#!/usr/bin/env python3
"""
Smart Automated MAXX Trading Bot
- Tests buy/sell every 2 minutes
- Analyzes price movement patterns
- Sells ALL on pumps (>10% gain)
- Buys on big dumps (>15% drop)
- Tracks performance in JSON
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from pathlib import Path

from master_trading_system import MasterTradingSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('smart_auto_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmartAutoTrader:
    """Smart automated trading bot with pump/dump detection"""

    def __init__(self):
        self.system = MasterTradingSystem()
        self.history_file = Path("smart_trader_history.json")
        self.trade_history = []
        self.price_history = []
        self.position_entry_price = None
        self.position_entry_time = None

        # Trading parameters
        self.test_buy_amount = Decimal('0.0003')  # ~$1 per test trade
        self.cycle_interval = 120  # 2 minutes

        # Smart thresholds
        self.pump_threshold = 10.0  # Sell ALL if price up 10%
        self.dump_threshold = 15.0  # Buy on price down 15%
        self.take_profit = 5.0      # Take profit at 5%
        self.stop_loss = 8.0        # Stop loss at 8%

        self.load_history()

    def load_history(self):
        """Load trading history from JSON"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.trade_history = data.get('trades', [])
                    self.price_history = data.get('prices', [])
                    logger.info(f"Loaded {len(self.trade_history)} historical trades")
        except Exception as e:
            logger.error(f"Error loading history: {e}")

    def save_history(self):
        """Save trading history to JSON"""
        try:
            data = {
                'trades': self.trade_history,
                'prices': self.price_history,
                'statistics': self.calculate_statistics(),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("History saved")
        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def calculate_statistics(self) -> Dict:
        """Calculate trading statistics"""
        if not self.trade_history:
            return {}

        trades = self.trade_history
        profitable = [t for t in trades if t.get('pnl', 0) > 0]
        losses = [t for t in trades if t.get('pnl', 0) < 0]

        total_pnl = sum(t.get('pnl', 0) for t in trades)

        return {
            'total_trades': len(trades),
            'profitable_trades': len(profitable),
            'losing_trades': len(losses),
            'win_rate': len(profitable) / len(trades) * 100 if trades else 0,
            'total_pnl_eth': total_pnl,
            'total_pnl_usd': total_pnl * 3300,
            'average_gain': sum(t.get('pnl', 0) for t in profitable) / len(profitable) if profitable else 0,
            'average_loss': sum(t.get('pnl', 0) for t in losses) / len(losses) if losses else 0,
        }

    async def get_current_price(self) -> Optional[Decimal]:
        """Estimate current MAXX price from recent trades"""
        try:
            # Use last known trades to estimate price
            if self.price_history:
                return Decimal(str(self.price_history[-1]['price']))
            return None
        except Exception as e:
            logger.error(f"Error getting price: {e}")
            return None

    def detect_pump(self, current_price: Decimal) -> bool:
        """Detect if we're in a pump (price surge)"""
        if not self.position_entry_price or current_price is None:
            return False

        gain_pct = float((current_price - self.position_entry_price) / self.position_entry_price * 100)

        if gain_pct >= self.pump_threshold:
            logger.info(f"🚀 PUMP DETECTED! Price up {gain_pct:.2f}%")
            return True

        return False

    def detect_dump(self) -> bool:
        """Detect if market dumped (big price drop)"""
        if len(self.price_history) < 5:
            return False

        recent_prices = [Decimal(str(p['price'])) for p in self.price_history[-5:]]
        max_price = max(recent_prices)
        current_price = recent_prices[-1]

        drop_pct = float((max_price - current_price) / max_price * 100)

        if drop_pct >= self.dump_threshold:
            logger.info(f"📉 DUMP DETECTED! Price down {drop_pct:.2f}%")
            return True

        return False

    def should_take_profit(self, current_price: Decimal) -> bool:
        """Check if we should take profit"""
        if not self.position_entry_price or current_price is None:
            return False

        gain_pct = float((current_price - self.position_entry_price) / self.position_entry_price * 100)
        return gain_pct >= self.take_profit

    def should_stop_loss(self, current_price: Decimal) -> bool:
        """Check if we should stop loss"""
        if not self.position_entry_price or current_price is None:
            return False

        loss_pct = float((self.position_entry_price - current_price) / self.position_entry_price * 100)
        return loss_pct >= self.stop_loss

    async def execute_buy(self, amount: Decimal, reason: str = "test"):
        """Execute buy order"""
        try:
            logger.info(f"🟢 BUYING {amount} ETH worth of MAXX - Reason: {reason}")

            eth_before, maxx_before = await self.system.get_balances()

            tx_hash = await self.system.buy_maxx(amount)

            if tx_hash:
                await asyncio.sleep(3)
                eth_after, maxx_after = await self.system.get_balances()

                maxx_received = maxx_after - maxx_before
                price = float(amount) / float(maxx_received) if maxx_received > 0 else 0

                # Record trade
                trade = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'BUY',
                    'reason': reason,
                    'eth_spent': float(amount),
                    'maxx_received': float(maxx_received),
                    'price': price,
                    'tx_hash': tx_hash,
                    'success': True
                }
                self.trade_history.append(trade)

                # Record price
                self.price_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'price': price
                })

                # Set position entry
                self.position_entry_price = Decimal(str(price))
                self.position_entry_time = datetime.now()

                logger.info(f"✅ Bought {maxx_received:.2f} MAXX @ {price:.8f} ETH")
                self.save_history()
                return True
            else:
                logger.error("❌ Buy failed")
                return False

        except Exception as e:
            logger.error(f"Buy error: {e}")
            return False

    async def execute_sell(self, amount: Decimal, reason: str = "test"):
        """Execute sell order"""
        try:
            logger.info(f"🔴 SELLING {amount} MAXX - Reason: {reason}")

            eth_before, _ = await self.system.get_balances()

            tx_hash = await self.system.sell_maxx(amount)

            if tx_hash:
                await asyncio.sleep(3)
                eth_after, maxx_after = await self.system.get_balances()

                eth_received = eth_after - eth_before
                price = float(eth_received) / float(amount) if amount > 0 else 0

                # Calculate P&L
                pnl = 0
                if self.position_entry_price:
                    pnl = float((Decimal(str(price)) - self.position_entry_price) * amount)

                # Record trade
                trade = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'SELL',
                    'reason': reason,
                    'maxx_sold': float(amount),
                    'eth_received': float(eth_received),
                    'price': price,
                    'entry_price': float(self.position_entry_price) if self.position_entry_price else 0,
                    'pnl': pnl,
                    'tx_hash': tx_hash,
                    'success': True
                }
                self.trade_history.append(trade)

                # Record price
                self.price_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'price': price
                })

                # Clear position
                if maxx_after == 0:
                    self.position_entry_price = None
                    self.position_entry_time = None

                pnl_usd = pnl * 3300
                logger.info(f"✅ Sold {amount:.2f} MAXX @ {price:.8f} ETH | P&L: {pnl:.6f} ETH (${pnl_usd:.2f})")
                self.save_history()
                return True
            else:
                logger.error("❌ Sell failed")
                return False

        except Exception as e:
            logger.error(f"Sell error: {e}")
            return False

    async def run_trading_cycle(self):
        """Run one trading cycle with smart logic"""
        try:
            logger.info("=" * 60)
            logger.info("Starting trading cycle...")

            # Get current balances
            eth_balance, maxx_balance = await self.system.get_balances()
            logger.info(f"Balances: {eth_balance:.6f} ETH, {maxx_balance:.2f} MAXX")

            # Estimate current price
            current_price = await self.get_current_price()

            # Smart decision making
            if maxx_balance > 0:
                # We have MAXX - check if we should sell

                # Priority 1: Sell ALL on pump
                if current_price and self.detect_pump(current_price):
                    logger.info("🚀 PUMP! Selling ALL MAXX!")
                    return await self.execute_sell(maxx_balance, "PUMP_DETECTED")

                # Priority 2: Take profit
                elif current_price and self.should_take_profit(current_price):
                    logger.info("💰 Taking profit")
                    return await self.execute_sell(maxx_balance, "TAKE_PROFIT")

                # Priority 3: Stop loss (DISABLED for pump riding)
                # elif current_price and self.should_stop_loss(current_price):
                #     logger.info("🛑 Stop loss triggered")
                #     return await self.execute_sell(maxx_balance, "STOP_LOSS")

                # Test sell (50% of holdings)
                else:
                    sell_amount = maxx_balance * Decimal('0.5')
                    if sell_amount > 0:
                        logger.info("📊 Test selling 50% of position")
                        return await self.execute_sell(sell_amount, "TEST_CYCLE")

            else:
                # We don't have MAXX - check if we should buy

                # Priority 1: Buy on dump
                if self.detect_dump():
                    logger.info("📉 DUMP! Buying the dip!")
                    buy_amount = min(self.test_buy_amount * 2, eth_balance - Decimal('0.001'))
                    if buy_amount > 0:
                        return await self.execute_buy(buy_amount, "BUY_DIP")

                # Test buy
                else:
                    if eth_balance >= self.test_buy_amount + Decimal('0.001'):
                        logger.info("📊 Test buying")
                        return await self.execute_buy(self.test_buy_amount, "TEST_CYCLE")
                    else:
                        logger.warning("⚠️ Insufficient ETH for test buy")

            return True

        except Exception as e:
            logger.error(f"Cycle error: {e}")
            return False

    async def run(self):
        """Run the automated trading bot"""
        logger.info("=" * 60)
        logger.info("🤖 SMART AUTO TRADER STARTING")
        logger.info("=" * 60)
        logger.info(f"Test buy amount: {self.test_buy_amount} ETH")
        logger.info(f"Cycle interval: {self.cycle_interval} seconds (2 minutes)")
        logger.info(f"Pump threshold: {self.pump_threshold}% (SELL ALL)")
        logger.info(f"Dump threshold: {self.dump_threshold}% (BUY DIP)")
        logger.info(f"Take profit: {self.take_profit}%")
        logger.info(f"Stop loss: {self.stop_loss}%")
        logger.info("=" * 60)

        # Initialize system
        if not await self.system.initialize():
            logger.error("Failed to initialize trading system")
            return

        cycle = 0
        try:
            while True:
                cycle += 1
                logger.info(f"\n📊 CYCLE #{cycle}")

                await self.run_trading_cycle()

                # Show statistics
                stats = self.calculate_statistics()
                if stats:
                    logger.info(f"Stats: {stats['total_trades']} trades, "
                              f"{stats['win_rate']:.1f}% win rate, "
                              f"P&L: {stats['total_pnl_eth']:.6f} ETH (${stats['total_pnl_usd']:.2f})")

                # Wait for next cycle
                logger.info(f"⏰ Waiting {self.cycle_interval} seconds for next cycle...")
                await asyncio.sleep(self.cycle_interval)

        except KeyboardInterrupt:
            logger.info("\n🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            self.save_history()
            logger.info("History saved. Goodbye!")

async def main():
    """Main entry point"""
    trader = SmartAutoTrader()
    await trader.run()

if __name__ == "__main__":
    asyncio.run(main())
