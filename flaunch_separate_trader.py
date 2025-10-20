#!/usr/bin/env python3
"""
Flaunch Separate Trading Bot
============================

Independent Flaunch trading system using separate wallet from main MAXX trader.
Can run simultaneously without interfering with existing trading operations.

Features:
- Separate wallet configuration
- Independent database and logging
- Isolated from main trading system
- Conservative risk management for $20 capital
"""

import asyncio
import json
import logging
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
import os
import sys
from dataclasses import dataclass

# Import Flaunch wallet configuration
try:
    import flaunch_wallet_config as fw_config
except ImportError:
    print("❌ Error: flaunch_wallet_config.py not found!")
    print("Please create flaunch_wallet_config.py with your Flaunch wallet settings.")
    sys.exit(1)

# Validate configuration
config_issues = fw_config.validate_config()
if config_issues:
    print("❌ Configuration Issues:")
    for issue in config_issues:
        print(f"  - {issue}")
    print("\nPlease fix flaunch_wallet_config.py before running.")
    sys.exit(1)

@dataclass
class FlaunchTrade:
    """Represents a Flaunch trading position"""
    token_address: str
    token_name: str
    symbol: str
    entry_price: float
    amount_usd: float
    entry_time: datetime
    status: str  # 'active', 'sold', 'stopped'
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl_usd: float = 0.0
    pnl_pct: float = 0.0

class FlaunchSeparateTrader:
    """
    Independent Flaunch trading bot with separate wallet
    """

    def __init__(self):
        # Load configuration from separate config file
        self.private_key = fw_config.FLAUNCH_PRIVATE_KEY
        self.wallet_address = fw_config.FLAUNCH_WALLET_ADDRESS
        self.capital = fw_config.FLAUNCH_CAPITAL_USD
        self.eth_reserve = fw_config.ETH_RESERVE_USD  # Always maintain $5 ETH reserve

        # API settings
        self.api_base = fw_config.FLAUNCH_API_BASE_URL
        self.session = requests.Session()

        # Trading parameters
        self.max_position_size = fw_config.MAX_POSITION_SIZE_USD
        self.max_concurrent_trades = fw_config.MAX_CONCURRENT_TRADES
        self.daily_trade_limit = fw_config.DAILY_TRADE_LIMIT
        self.stop_loss_pct = fw_config.STOP_LOSS_PCT
        self.profit_target_pct = fw_config.PROFIT_TARGET_PCT

        # Database setup (separate from main system)
        self.db_file = fw_config.FLAUNCH_DB_FILE
        self.init_database()

        # Active positions tracking
        self.active_trades: Dict[str, FlaunchTrade] = {}
        self.daily_trades_today = 0
        self.daily_pnl = 0.0

        # Setup logging (separate log file)
        self.setup_logging()

        self.logger.info("🚀 Flaunch Separate Trader initialized")
        self.logger.info(f"💰 Capital: ${self.capital}")
        self.logger.info(f"🏦 Wallet: {self.wallet_address[:10]}...")
        self.logger.info("✅ Independent from main MAXX trading system")

    def setup_logging(self):
        """Setup separate logging for Flaunch trading"""
        self.logger = logging.getLogger('FlaunchTrader')
        self.logger.setLevel(getattr(logging, fw_config.FLAUNCH_LOG_LEVEL))

        # File handler for Flaunch trading
        fh = logging.FileHandler(fw_config.FLAUNCH_LOG_FILE)
        fh.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - FLAUNCH - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def init_database(self):
        """Initialize separate database for Flaunch trades"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Create trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flaunch_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_address TEXT UNIQUE,
                token_name TEXT,
                symbol TEXT,
                entry_price REAL,
                amount_usd REAL,
                entry_time TEXT,
                status TEXT,
                exit_price REAL,
                exit_time TEXT,
                pnl_usd REAL,
                pnl_pct REAL,
                notes TEXT
            )
        ''')

        # Create daily stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                trades_count INTEGER,
                total_pnl REAL,
                win_rate REAL,
                notes TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def save_trade(self, trade: FlaunchTrade):
        """Save trade to separate database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO flaunch_trades
            (token_address, token_name, symbol, entry_price, amount_usd,
             entry_time, status, exit_price, exit_time, pnl_usd, pnl_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade.token_address,
            trade.token_name,
            trade.symbol,
            trade.entry_price,
            trade.amount_usd,
            trade.entry_time.isoformat(),
            trade.status,
            trade.exit_price,
            trade.exit_time.isoformat() if trade.exit_time else None,
            trade.pnl_usd,
            trade.pnl_pct
        ))

        conn.commit()
        conn.close()

    def load_active_trades(self):
        """Load active trades from database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM flaunch_trades
            WHERE status = 'active'
        ''')

        for row in cursor.fetchall():
            trade = FlaunchTrade(
                token_address=row[1],
                token_name=row[2],
                symbol=row[3],
                entry_price=row[4],
                amount_usd=row[5],
                entry_time=datetime.fromisoformat(row[6]),
                status=row[7],
                exit_price=row[8],
                exit_time=datetime.fromisoformat(row[9]) if row[9] else None,
                pnl_usd=row[10],
                pnl_pct=row[11]
            )
            self.active_trades[row[1]] = trade

        conn.close()

    async def monitor_new_launches(self):
        """
        Monitor for new Flaunch token launches
        """
        self.logger.info("🔍 Starting Flaunch launch monitoring (separate wallet)...")

        while True:
            try:
                # Check if we've hit daily limits
                if self.daily_trades_today >= self.daily_trade_limit:
                    self.logger.info("Daily trade limit reached, waiting for next day...")
                    await asyncio.sleep(3600)  # Wait 1 hour
                    continue

                if len(self.active_trades) >= self.max_concurrent_trades:
                    self.logger.info("Max concurrent trades reached, waiting...")
                    await asyncio.sleep(300)  # Wait 5 minutes
                    continue

                # Look for profitable launch opportunities
                opportunities = await self.scan_launch_opportunities()

                for opp in opportunities:
                    if self.should_trade_opportunity(opp):
                        await self.execute_launch_trade(opp)
                        self.daily_trades_today += 1

                        if self.daily_trades_today >= self.daily_trade_limit:
                            break

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in launch monitoring: {e}")
                await asyncio.sleep(120)

    async def scan_launch_opportunities(self) -> List[Dict]:
        """
        Scan for new launch opportunities
        """
        opportunities = []

        try:
            # This would integrate with launch monitoring
            # For now, simulate finding opportunities

            # Simulate a potential opportunity
            sample_opp = {
                "job_id": f"flaunch_{int(time.time())}",
                "name": "QuickProfit Token",
                "symbol": "QPT",
                "market_cap": 8000,
                "has_revenue_manager": True,
                "sniper_protection": True,
                "profit_score": 75,
                "estimated_profit": 2.8
            }

            # Only add if it meets criteria
            if sample_opp["profit_score"] >= 60:
                opportunities.append(sample_opp)

        except Exception as e:
            self.logger.error(f"Error scanning opportunities: {e}")

        return opportunities

    def should_trade_opportunity(self, opportunity: Dict) -> bool:
        """
        Determine if we should trade this opportunity
        """
        # Check profit score
        if opportunity.get("profit_score", 0) < 60:
            return False

        # Check wallet balance and ETH reserve
        balance_info = self.check_wallet_balance()
        if not balance_info["can_trade"] or not balance_info["reserve_protected"]:
            self.logger.warning("Cannot trade: ETH reserve not protected or insufficient balance")
            return False

        # Check position size against available balance
        trade_size = min(self.max_position_size, self.capital * 0.1)
        if trade_size > balance_info["available_for_trading"]:
            self.logger.warning(f"Trade size ${trade_size} exceeds available balance ${balance_info['available_for_trading']}")
            return False

        # Check if we can afford it
        if trade_size > balance_info["available_for_trading"] * 0.5:  # Don't use more than 50% of available
            return False

        return True

    async def execute_launch_trade(self, opportunity: Dict):
        """
        Execute a trade for a launch opportunity
        """
        try:
            trade_size = min(self.max_position_size, self.capital * 0.1)

            self.logger.info(f"🎯 Executing Flaunch trade: {opportunity['symbol']} (${trade_size:.2f})")

            # Wait for launch completion (placeholder)
            token_address = await self.wait_for_token_launch(opportunity['job_id'])

            if token_address:
                # Execute buy (placeholder)
                success = await self.execute_buy(token_address, trade_size)

                if success:
                    # Create trade record
                    trade = FlaunchTrade(
                        token_address=token_address,
                        token_name=opportunity['name'],
                        symbol=opportunity['symbol'],
                        entry_price=0.0001,  # Placeholder price
                        amount_usd=trade_size,
                        entry_time=datetime.now(),
                        status='active'
                    )

                    self.active_trades[token_address] = trade
                    self.save_trade(trade)

                    # Start monitoring
                    asyncio.create_task(self.monitor_position(token_address))

                    self.logger.info(f"✅ Trade executed: {opportunity['symbol']}")

        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")

    async def wait_for_token_launch(self, job_id: str) -> Optional[str]:
        """
        Wait for token launch to complete
        """
        # Placeholder - in real implementation, this would poll the Flaunch API
        await asyncio.sleep(5)  # Simulate waiting

        # Return a mock token address
        return f"0x{job_id[-40:].zfill(40)}"

    async def execute_buy(self, token_address: str, amount_usd: float) -> bool:
        """
        Execute buy order (placeholder implementation)
        """
        try:
            self.logger.info(f"💰 Buying {token_address} for ${amount_usd:.2f}")

            # Placeholder - in real implementation, this would:
            # 1. Check wallet balance
            # 2. Calculate token amount
            # 3. Execute swap transaction
            # 4. Wait for confirmation

            await asyncio.sleep(2)  # Simulate transaction time
            return True

        except Exception as e:
            self.logger.error(f"Error executing buy: {e}")
            return False

    async def monitor_position(self, token_address: str):
        """
        Monitor an active position
        """
        trade = self.active_trades.get(token_address)
        if not trade:
            return

        while trade and trade.status == 'active':
            try:
                # Get current price (placeholder)
                current_price = await self.get_token_price(token_address)

                if current_price:
                    # Calculate P&L
                    price_change_pct = (current_price - trade.entry_price) / trade.entry_price

                    # Check exit conditions
                    if price_change_pct >= self.profit_target_pct:
                        await self.close_position(token_address, "PROFIT_TARGET")
                    elif price_change_pct <= -self.stop_loss_pct:
                        await self.close_position(token_address, "STOP_LOSS")

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Error monitoring {token_address}: {e}")
                await asyncio.sleep(60)

    async def get_token_price(self, token_address: str) -> Optional[float]:
        """
        Get current token price (placeholder)
        """
        # Placeholder - in real implementation, this would:
        # 1. Query DexScreener API
        # 2. Or use on-chain price feeds
        # 3. Return current price in USD

        return 0.00015  # Mock price

    async def close_position(self, token_address: str, reason: str):
        """
        Close a trading position
        """
        trade = self.active_trades.get(token_address)
        if not trade:
            return

        try:
            # Get exit price
            exit_price = await self.get_token_price(token_address) or trade.entry_price

            # Calculate P&L
            trade.exit_price = exit_price
            trade.exit_time = datetime.now()
            trade.pnl_pct = (exit_price - trade.entry_price) / trade.entry_price
            trade.pnl_usd = trade.amount_usd * trade.pnl_pct
            trade.status = 'closed'

            # Execute sell (placeholder)
            await self.execute_sell(token_address, trade.amount_usd)

            # Update daily P&L
            self.daily_pnl += trade.pnl_usd

            # Save to database
            self.save_trade(trade)

            # Remove from active trades
            del self.active_trades[token_address]

            self.logger.info(f"💰 Closed {trade.symbol}: {reason} | P&L: ${trade.pnl_usd:.2f} ({trade.pnl_pct:.1%})")

        except Exception as e:
            self.logger.error(f"Error closing position {token_address}: {e}")

    async def execute_sell(self, token_address: str, amount_usd: float):
        """
        Execute sell order (placeholder)
        """
        self.logger.info(f"📈 Selling {token_address} position")
        await asyncio.sleep(2)  # Simulate transaction

    def check_wallet_balance(self) -> Dict:
        """
        Check wallet ETH balance and ensure reserve is maintained
        """
        try:
            # Placeholder - in real implementation, this would check actual balance
            # For now, assume we have enough
            mock_balance_usd = 20.0  # Mock $20 total balance

            available_for_trading = max(0, mock_balance_usd - self.eth_reserve)
            can_trade = available_for_trading >= 1.0  # Need at least $1 for trades

            return {
                "total_balance_usd": mock_balance_usd,
                "eth_reserve_usd": self.eth_reserve,
                "available_for_trading": available_for_trading,
                "can_trade": can_trade,
                "reserve_protected": mock_balance_usd >= self.eth_reserve
            }
        except Exception as e:
            self.logger.error(f"Error checking wallet balance: {e}")
            return {
                "total_balance_usd": 0,
                "eth_reserve_usd": self.eth_reserve,
                "available_for_trading": 0,
                "can_trade": False,
                "reserve_protected": False
            }

    def get_trading_stats(self) -> Dict:
        """
        Get trading statistics
        """
        total_trades = self.daily_trades_today
        active_trades = len(self.active_trades)

        # Include wallet balance info
        balance_info = self.check_wallet_balance()

        return {
            "total_trades_today": total_trades,
            "active_trades": active_trades,
            "daily_pnl": self.daily_pnl,
            "remaining_capital": self.capital - sum(t.amount_usd for t in self.active_trades.values()),
            "wallet_address": self.wallet_address[:10] + "...",
            "is_independent": True,
            "eth_reserve_protected": balance_info["reserve_protected"],
            "available_for_trading": balance_info["available_for_trading"]
        }

    async def emergency_stop(self):
        """
        Emergency stop all trading
        """
        self.logger.warning("🚨 Emergency stop activated!")

        # Close all positions
        for token_address in list(self.active_trades.keys()):
            await self.close_position(token_address, "EMERGENCY_STOP")

        self.logger.warning("All positions closed due to emergency stop")

    async def run_trading_loop(self):
        """
        Main trading loop
        """
        self.logger.info("🎯 Starting Flaunch Separate Trading Loop")
        self.logger.info("=" * 50)

        # Load existing trades
        self.load_active_trades()

        # Start monitoring
        monitor_task = asyncio.create_task(self.monitor_new_launches())

        try:
            await monitor_task
        except KeyboardInterrupt:
            self.logger.info("Shutting down Flaunch trader...")
            await self.emergency_stop()
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            await self.emergency_stop()

def main():
    """Main function"""
    print("🚀 FLAUNCH SEPARATE TRADER")
    print("=" * 40)
    print("Independent wallet trading system")
    print("Does NOT interfere with main MAXX trader")
    print()

    # Initialize trader
    trader = FlaunchSeparateTrader()

    # Show stats
    stats = trader.get_trading_stats()
    print("📊 Current Status:")
    print(f"  Wallet: {stats['wallet_address']}")
    print(f"  Trading Capital: ${fw_config.FLAUNCH_CAPITAL_USD}")
    print(f"  ETH Reserve: ${fw_config.ETH_RESERVE_USD} (ALWAYS PROTECTED)")
    print(f"  Available for Trading: ${stats['available_for_trading']:.2f}")
    print(f"  Reserve Protected: {'✅' if stats['eth_reserve_protected'] else '❌'}")
    print(f"  Active Trades: {stats['active_trades']}")
    print(f"  Today's Trades: {stats['total_trades_today']}")
    print(f"  Daily P&L: ${stats['daily_pnl']:.2f}")
    print()

    print("🔄 Starting trading loop...")
    print("Press Ctrl+C to stop")
    print()

    # Run the trading loop
    asyncio.run(trader.run_trading_loop())

if __name__ == "__main__":
    main()
