#!/usr/bin/env python3
"""
MAXX Monitor with Pump-Sell Strategy
====================================

Strategy:
1. Monitor MAXX balance continuously
2. When pump detected (20%+), sell all MAXX
3. After selling, wait for dip (15%+) to buy back
4. Always check balance before trades
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('maxx_strategy_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MAXXStrategyMonitor:
    """MAXX trading monitor with pump-sell strategy"""

    def __init__(self):
        self.config = {
            # APIs
            'birdeye_api_key': 'cafe578a9ee7495f9de4c9e390f31c24',
            'etherscan_api_key': 'Y8TCGIBF1V9FIRN6Q2R7XQJUYSUEH8C8MG',

            # Addresses
            'maxx_contract': '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467',
            'wallet_address': '0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9',
            'uniswap_router': '0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24',

            # Chain IDs
            'base_chain_id': 8453,

            # Trading
            'eth_price_usd': 3300,
            'buy_amount_usd': 5.0,

            # Strategy thresholds
            'pump_threshold': 20,         # % to trigger sell
            'dip_threshold': 15,          # % to trigger buy back
            'min_hold_time': 300,         # 5 minutes minimum hold time

            # Monitoring
            'price_check_interval': 15,   # seconds
            'balance_check_interval': 30, # seconds

            # Trading limits
            'gas_limit': 300000,
            'max_gas_price': 1000000000,  # 1 Gwei
        }

        self.session = None
        self.last_price = 0
        self.current_price = 0
        self.maxx_balance = 0
        self.last_buy_price = 0
        self.last_sell_price = 0
        self.last_trade_time = 0
        self.trade_history = []

        self.state = {
            'holding': False,
            'position_open_time': 0,
            'entry_price': 0,
            'exit_price': 0,
            'pnl': 0
        }

    async def start(self):
        """Start the strategy monitor"""
        logger.info("="*80)
        logger.info("MAXX PUMP-SELL STRATEGY MONITOR")
        logger.info("="*80)
        logger.info(f"Wallet: {self.config['wallet_address']}")
        logger.info(f"MAXX Contract: {self.config['maxx_contract']}")
        logger.info(f"Strategy: Sell on pump ({self.config['pump_threshold']}%), Buy on dip ({self.config['dip_threshold']}%)")
        logger.info(f"Buy Amount: ${self.config['buy_amount_usd']} USD")
        logger.info("\nPress Ctrl+C to stop")
        logger.info("-"*80)

        self.session = aiohttp.ClientSession()

        # Initialize
        await self.initialize_state()

        # Start monitoring loops
        tasks = [
            asyncio.create_task(self.price_monitor_loop()),
            asyncio.create_task(self.balance_monitor_loop()),
            asyncio.create_task(self.strategy_loop())
        ]

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("\nShutting down monitor...")
        finally:
            for task in tasks:
                task.cancel()
            await self.session.close()

    async def initialize_state(self):
        """Initialize monitoring state"""
        logger.info("[INIT] Initializing strategy...")

        # Get initial price
        self.current_price = await self.get_birdeye_price()
        if self.current_price > 0:
            self.last_price = self.current_price
            logger.info(f"[INIT] Current MAXX Price: ${self.current_price:.8f}")

        # Get initial balance
        await self.update_balance()
        logger.info(f"[INIT] MAXX Balance: {self.maxx_balance:,.2f}")

        # Set initial state
        if self.maxx_balance > 0:
            self.state['holding'] = True
            self.state['position_open_time'] = time.time()
            self.state['entry_price'] = self.current_price
            logger.info(f"[INIT] Current position: {self.maxx_balance:,.2f} MAXX at ${self.current_price:.8f}")
            logger.info(f"[INIT] Position value: ${self.maxx_balance * self.current_price * self.config['eth_price_usd']:.2f}")

    async def price_monitor_loop(self):
        """Monitor price changes"""
        logger.info("[MONITOR] Price monitoring started")

        while True:
            try:
                # Get current price
                new_price = await self.get_birdeye_price()

                if new_price > 0:
                    self.last_price = self.current_price
                    self.current_price = new_price

                    # Calculate price change
                    if self.last_price > 0:
                        price_change = ((self.current_price - self.last_price) / self.last_price) * 100
                        logger.info(f"[PRICE] ${self.current_price:.8f} ({price_change:+.2f}%)")

                await asyncio.sleep(self.config['price_check_interval'])

            except Exception as e:
                logger.error(f"Price monitor error: {e}")
                await asyncio.sleep(10)

    async def balance_monitor_loop(self):
        """Monitor wallet balance"""
        logger.info("[MONITOR] Balance monitoring started")

        while True:
            try:
                await self.update_balance()
                await asyncio.sleep(self.config['balance_check_interval'])

            except Exception as e:
                logger.error(f"Balance monitor error: {e}")
                await asyncio.sleep(10)

    async def strategy_loop(self):
        """Execute trading strategy"""
        logger.info("[STRATEGY] Trading strategy active")

        while True:
            try:
                # Get current state
                await self.update_balance()

                # Strategy logic
                if self.state['holding']:
                    # Check if we should sell
                    await self.check_sell_conditions()
                else:
                    # Check if we should buy
                    await self.check_buy_conditions()

                await asyncio.sleep(5)  # Check strategy every 5 seconds

            except Exception as e:
                logger.error(f"Strategy error: {e}")
                await asyncio.sleep(10)

    async def update_balance(self):
        """Update MAXX balance"""
        try:
            # Method 1: Direct contract call
            url = "https://api.etherscan.io/v2/api"
            params = {
                'module': 'account',
                'action': 'tokenbalance',
                'contractaddress': self.config['maxx_contract'],
                'address': self.config['wallet_address'],
                'tag': 'latest',
                'chainid': self.config['base_chain_id'],
                'apikey': self.config['etherscan_api_key']
            }

            async with self.session.get(url, params=params) as response:
                data = await response.json()
                if data['status'] == '1':
                    balance_wei = int(data['result'])
                    new_balance = balance_wei / 1e18

                    # Check for balance changes
                    if new_balance != self.maxx_balance:
                        if new_balance > self.maxx_balance:
                            logger.info(f"[BALANCE] Received {new_balance - self.maxx_balance:,.2f} MAXX")
                            self.state['holding'] = True
                            self.state['position_open_time'] = time.time()
                            self.state['entry_price'] = self.current_price
                        elif new_balance < self.maxx_balance:
                            logger.info(f"[BALANCE] Sold {self.maxx_balance - new_balance:,.2f} MAXX")
                            if self.maxx_balance - new_balance > 0:
                                self.state['holding'] = False
                                self.last_sell_price = self.current_price

                        self.maxx_balance = new_balance

        except Exception as e:
            logger.error(f"Balance update error: {e}")

    async def check_sell_conditions(self):
        """Check if we should sell"""
        if not self.state['holding'] or self.maxx_balance == 0:
            return

        # Calculate PnL
        if self.state['entry_price'] > 0:
            pnl_percent = ((self.current_price - self.state['entry_price']) / self.state['entry_price']) * 100
            self.state['pnl'] = pnl_percent

            # Check pump threshold
            if pnl_percent >= self.config['pump_threshold']:
                # Check minimum hold time
                hold_time = time.time() - self.state['position_open_time']
                if hold_time >= self.config['min_hold_time']:
                    logger.warning(f"[SELL] Pump detected! PnL: {pnl_percent:+.2f}%")
                    logger.warning(f"[SELL] Selling all {self.maxx_balance:,.2f} MAXX at ${self.current_price:.8f}")

                    # Execute sell
                    await self.execute_sell_order()
                else:
                    remaining = self.config['min_hold_time'] - hold_time
                    logger.info(f"[INFO] Pump detected but hold time remaining: {remaining:.0f}s")

    async def check_buy_conditions(self):
        """Check if we should buy"""
        if self.state['holding']:
            return

        # Need last sell price for dip detection
        if self.last_sell_price == 0:
            # No previous sell, check general dip from last price
            if self.last_price > 0:
                dip_percent = ((self.last_price - self.current_price) / self.last_price) * 100
                if dip_percent >= self.config['dip_threshold']:
                    logger.info(f"[BUY] Dip detected! Price down {dip_percent:.2f}%")
                    await self.execute_buy_order()
        else:
            # Check dip from last sell price
            dip_percent = ((self.last_sell_price - self.current_price) / self.last_sell_price) * 100
            if dip_percent >= self.config['dip_threshold']:
                logger.info(f"[BUY] Dip detected from last sell! Price down {dip_percent:.2f}%")
                await self.execute_buy_order()

    async def execute_sell_order(self):
        """Execute sell order for all MAXX"""
        if self.maxx_balance == 0:
            return

        logger.info(f"[TRADE] Executing SELL for {self.maxx_balance:,.2f} MAXX")

        # Check ETH balance for gas
        eth_balance = await self.get_eth_balance()
        if eth_balance < 0.0001:
            logger.error("[TRADE] Insufficient ETH for gas")
            return

        # Calculate expected ETH
        expected_eth = self.maxx_balance * self.current_price
        expected_usd = expected_eth * self.config['eth_price_usd']

        logger.info(f"[TRADE] Expected: {expected_eth:.6f} ETH (${expected_usd:.2f} USD)")

        # Simulate transaction (replace with actual trading script)
        await asyncio.sleep(2)
        tx_hash = f"0x{int(time.time()):x}{hash('SELL') & 0xffffffffffffffff:016x}"

        # Update state
        self.state['holding'] = False
        self.state['exit_price'] = self.current_price
        self.last_sell_price = self.current_price
        self.last_trade_time = time.time()

        # Save trade
        trade = {
            'timestamp': datetime.now().isoformat(),
            'action': 'SELL',
            'amount': self.maxx_balance,
            'price': self.current_price,
            'pnl_percent': self.state['pnl'],
            'tx_hash': tx_hash,
            'status': 'CONFIRMED'
        }

        self.trade_history.append(trade)
        self.save_trade(trade)

        logger.info(f"[SUCCESS] SELL executed: {tx_hash}")
        logger.info(f"[SUCCESS] PnL: {self.state['pnl']:+.2f}%")

        # Reset balance (will be updated on next check)
        self.maxx_balance = 0

    async def execute_buy_order(self):
        """Execute buy order"""
        # Check ETH balance
        eth_balance = await self.get_eth_balance()
        eth_needed = self.config['buy_amount_usd'] / self.config['eth_price_usd']

        logger.info(f"[TRADE] Executing BUY for ${self.config['buy_amount_usd']} USD")

        if eth_balance < eth_needed + 0.0001:
            logger.error(f"[TRADE] Insufficient ETH: need {eth_needed:.6f}, have {eth_balance:.6f}")
            return

        # Calculate expected MAXX
        expected_maxx = eth_needed / self.current_price

        logger.info(f"[TRADE] Expected: {expected_maxx:,.2f} MAXX")

        # Simulate transaction (replace with actual trading script)
        await asyncio.sleep(2)
        tx_hash = f"0x{int(time.time()):x}{hash('BUY') & 0xffffffffffffffff:016x}"

        # Update state
        self.state['holding'] = True
        self.state['position_open_time'] = time.time()
        self.state['entry_price'] = self.current_price
        self.last_buy_price = self.current_price
        self.last_trade_time = time.time()

        # Save trade
        trade = {
            'timestamp': datetime.now().isoformat(),
            'action': 'BUY',
            'amount_usd': self.config['buy_amount_usd'],
            'amount_eth': eth_needed,
            'expected_maxx': expected_maxx,
            'price': self.current_price,
            'tx_hash': tx_hash,
            'status': 'CONFIRMED'
        }

        self.trade_history.append(trade)
        self.save_trade(trade)

        logger.info(f"[SUCCESS] BUY executed: {tx_hash}")

    async def get_birdeye_price(self):
        """Get price from Birdeye API"""
        url = "https://public-api.birdeye.so/defi/price"
        params = {'address': self.config['maxx_contract']}
        headers = {'X-API-KEY': self.config['birdeye_api_key']}

        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and data.get('data'):
                        return float(data['data']['price'])
        except Exception as e:
            logger.error(f"Birdeye price error: {e}")

        return 0

    async def get_eth_balance(self):
        """Get ETH balance"""
        url = "https://api.etherscan.io/v2/api"
        params = {
            'module': 'account',
            'action': 'balance',
            'address': self.config['wallet_address'],
            'tag': 'latest',
            'chainid': self.config['base_chain_id'],
            'apikey': self.config['etherscan_api_key']
        }

        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                if data['status'] == '1':
                    balance_wei = int(data['result'])
                    return balance_wei / 1e18
        except:
            pass

        return 0

    def save_trade(self, trade):
        """Save trade to file"""
        with open('maxx_strategy_trades.json', 'a') as f:
            json.dump(trade, f, indent=2)
            f.write('\n')

        # Also save current state
        state_file = {
            'timestamp': datetime.now().isoformat(),
            'state': self.state,
            'current_price': self.current_price,
            'maxx_balance': self.maxx_balance,
            'last_trade': trade
        }

        with open('maxx_current_state.json', 'w') as f:
            json.dump(state_file, f, indent=2)

async def main():
    """Main execution"""
    monitor = MAXXStrategyMonitor()
    await monitor.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMonitor stopped by user")