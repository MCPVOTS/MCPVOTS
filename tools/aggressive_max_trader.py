#!/usr/bin/env python3
"""
AGGRESSIVE MAX PROFIT MAXX TRADER
- Buys/Sells ALL every cycle
- Tracks all Ethermax whale activity in SQLite
- Analyzes patterns for maximum profit
- 2-minute cycles for high-action token
"""

import asyncio
import sqlite3
import json
import logging
import requests
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from pathlib import Path

from master_trading_system import MasterTradingSystem
from kyber_client import KyberClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('aggressive_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WhaleTracker:
    """Track whale activity in SQLite database"""

    def __init__(self, db_path='ethermax_whales.db'):
        self.db_path = db_path
        self.conn = None
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for whale tracking"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # Whale wallets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whale_wallets (
                wallet_address TEXT PRIMARY KEY,
                total_trades INTEGER DEFAULT 0,
                total_volume_usd REAL DEFAULT 0,
                total_bought_maxx REAL DEFAULT 0,
                total_sold_maxx REAL DEFAULT 0,
                net_position REAL DEFAULT 0,
                first_seen TEXT,
                last_seen TEXT,
                is_pump_coordinator INTEGER DEFAULT 0,
                risk_score REAL DEFAULT 0
            )
        ''')

        # Whale trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whale_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address TEXT,
                timestamp TEXT,
                trade_type TEXT,
                maxx_amount REAL,
                eth_amount REAL,
                usd_value REAL,
                price REAL,
                tx_hash TEXT,
                FOREIGN KEY (wallet_address) REFERENCES whale_wallets(wallet_address)
            )
        ''')

        # Market events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                price_before REAL,
                price_after REAL,
                price_change_pct REAL,
                volume_spike INTEGER DEFAULT 0,
                coordinated_activity INTEGER DEFAULT 0,
                description TEXT
            )
        ''')

        # Our trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS our_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                trade_type TEXT,
                maxx_amount REAL,
                eth_amount REAL,
                price REAL,
                pnl_eth REAL,
                pnl_usd REAL,
                reason TEXT,
                tx_hash TEXT,
                success INTEGER DEFAULT 1
            )
        ''')

        self.conn.commit()
        logger.info(f"Whale tracker database initialized: {self.db_path}")

    def add_whale_trade(self, wallet: str, trade_type: str, maxx_amount: float,
                       eth_amount: float, usd_value: float, price: float, tx_hash: str = ""):
        """Add a whale trade to database"""
        cursor = self.conn.cursor()

        # Insert trade
        cursor.execute('''
            INSERT INTO whale_trades
            (wallet_address, timestamp, trade_type, maxx_amount, eth_amount, usd_value, price, tx_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (wallet, datetime.now().isoformat(), trade_type, maxx_amount, eth_amount, usd_value, price, tx_hash))

        # Update or insert whale wallet
        cursor.execute('SELECT * FROM whale_wallets WHERE wallet_address = ?', (wallet,))
        existing = cursor.fetchone()

        if existing:
            # Update existing
            cursor.execute('''
                UPDATE whale_wallets SET
                    total_trades = total_trades + 1,
                    total_volume_usd = total_volume_usd + ?,
                    total_bought_maxx = total_bought_maxx + ?,
                    total_sold_maxx = total_sold_maxx + ?,
                    net_position = total_bought_maxx - total_sold_maxx,
                    last_seen = ?
                WHERE wallet_address = ?
            ''', (usd_value,
                  maxx_amount if trade_type == 'BUY' else 0,
                  maxx_amount if trade_type == 'SELL' else 0,
                  datetime.now().isoformat(),
                  wallet))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO whale_wallets
                (wallet_address, total_trades, total_volume_usd, total_bought_maxx, total_sold_maxx,
                 net_position, first_seen, last_seen)
                VALUES (?, 1, ?, ?, ?, ?, ?, ?)
            ''', (wallet, usd_value,
                  maxx_amount if trade_type == 'BUY' else 0,
                  maxx_amount if trade_type == 'SELL' else 0,
                  maxx_amount if trade_type == 'BUY' else -maxx_amount,
                  datetime.now().isoformat(),
                  datetime.now().isoformat()))

        self.conn.commit()

    def log_market_event(self, event_type: str, price_before: float, price_after: float, description: str = ""):
        """Log a market event"""
        cursor = self.conn.cursor()
        price_change = ((price_after - price_before) / price_before * 100) if price_before > 0 else 0

        cursor.execute('''
            INSERT INTO market_events
            (timestamp, event_type, price_before, price_after, price_change_pct, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), event_type, price_before, price_after, price_change, description))

        self.conn.commit()

    def log_our_trade(self, trade_type: str, maxx_amount: float, eth_amount: float,
                     price: float, pnl_eth: float, reason: str, tx_hash: str = ""):
        """Log our own trade"""
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO our_trades
            (timestamp, trade_type, maxx_amount, eth_amount, price, pnl_eth, pnl_usd, reason, tx_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), trade_type, maxx_amount, eth_amount, price,
              pnl_eth, pnl_eth * 3300, reason, tx_hash))

        self.conn.commit()

    def get_whale_summary(self) -> List[Dict]:
        """Get summary of top whales"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT wallet_address, total_trades, total_volume_usd, net_position, last_seen
            FROM whale_wallets
            ORDER BY total_volume_usd DESC
            LIMIT 10
        ''')

        whales = []
        for row in cursor.fetchall():
            whales.append({
                'wallet': row[0],
                'trades': row[1],
                'volume': row[2],
                'position': row[3],
                'last_seen': row[4]
            })
        return whales

    def get_our_stats(self) -> Dict:
        """Get our trading statistics"""
        cursor = self.conn.cursor()

        cursor.execute('SELECT COUNT(*), SUM(pnl_eth), SUM(pnl_usd) FROM our_trades WHERE success = 1')
        row = cursor.fetchone()

        cursor.execute('SELECT COUNT(*) FROM our_trades WHERE pnl_eth > 0')
        wins = cursor.fetchone()[0]

        return {
            'total_trades': row[0] or 0,
            'total_pnl_eth': row[1] or 0,
            'total_pnl_usd': row[2] or 0,
            'wins': wins,
            'win_rate': (wins / row[0] * 100) if row[0] else 0
        }

class AggressiveMaxTrader:
    """Aggressive trader that buys/sells ALL every cycle"""

    def __init__(self):
        self.system = MasterTradingSystem()
        self.kyber = None
        self.whale_tracker = WhaleTracker()
        self.cycle_interval = 30  # 30 seconds - fast reaction time
        self.last_price = None
        self.position_entry_price = None
        self.last_sell_price = None  # Track price when we sold
        self.highest_price_since_sell = None  # Track highest price after selling
        # Track cost basis in ETH for realized P&L
        self.last_buy_eth_spent = None

        # Reserve and sizing
        self.eth_reserve = Decimal('0.001')  # Always leave 0.001 ETH in wallet

        # Smart thresholds
        self.profit_target = 10.0  # Sell if up 10% from entry
        self.dip_threshold = 15.0  # Buy if down 15% from high after sell

    async def fetch_market_data(self) -> Optional[Dict]:
        """Fetch current market data from DexScreener"""
        try:
            pool = '0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148'
            url = f'https://api.dexscreener.com/latest/dex/pairs/base/{pool}'

            response = requests.get(url, timeout=10)
            data = response.json()

            pair = None
            if isinstance(data, dict):
                if 'pair' in data and isinstance(data['pair'], dict):
                    pair = data['pair']
                elif 'pairs' in data and isinstance(data['pairs'], list) and data['pairs']:
                    pair = data['pairs'][0]

            if pair:
                return {
                    'price': float(pair.get('priceUsd', 0) or 0),
                    'liquidity': float((pair.get('liquidity') or {}).get('usd', 0) or 0),
                    'volume_24h': float((pair.get('volume') or {}).get('h24', 0) or 0),
                    'price_change_1h': float((pair.get('priceChange') or {}).get('h1', 0) or 0),
                    'price_change_6h': float((pair.get('priceChange') or {}).get('h6', 0) or 0),
                    'price_change_24h': float((pair.get('priceChange') or {}).get('h24', 0) or 0),
                    'buys_24h': int(((pair.get('txns') or {}).get('h24') or {}).get('buys', 0) or 0),
                    'sells_24h': int(((pair.get('txns') or {}).get('h24') or {}).get('sells', 0) or 0)
                }
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
        return None

    async def analyze_and_trade(self):
        """Analyze market and execute SMART trades with profit target and dip buying"""
        try:
            logger.info("="*60)
            logger.info("ANALYZING MARKET...")

            # Get market data
            market = await self.fetch_market_data()
            if not market:
                logger.warning("Failed to fetch market data")
                return

            current_price = market['price']
            logger.info(f"Current Price: ${current_price:.8f}")
            logger.info(f"24h Change: {market['price_change_24h']:.2f}%")
            logger.info(f"Liquidity: ${market['liquidity']:,.2f}")
            logger.info(f"Volume 24h: ${market['volume_24h']:,.2f}")
            logger.info(f"Buys: {market['buys_24h']}, Sells: {market['sells_24h']}")

            # VERIFY balances before any action
            eth_balance, maxx_balance = await self.system.get_balances()
            logger.info(f"VERIFIED Balances: {eth_balance:.6f} ETH, {maxx_balance:,.2f} MAXX")

            # STRATEGY: Smart buy/sell based on price movements
            if maxx_balance > 0:
                # WE HAVE MAXX - CHECK IF WE SHOULD SELL

                # Calculate profit if we sell now
                profit_pct = 0
                if self.position_entry_price and self.position_entry_price > 0:
                    profit_pct = ((Decimal(str(current_price)) - self.position_entry_price) / self.position_entry_price * 100)
                    logger.info(f"Current Profit: {profit_pct:.2f}%")

                # SELL if profit target met (10% gain)
                should_sell = profit_pct >= Decimal(str(self.profit_target))

                if should_sell:
                    logger.info(f" PROFIT TARGET MET! Selling ALL {maxx_balance:,.2f} MAXX")
                else:
                    logger.info(f" Holding MAXX (need +{self.profit_target:.1f}% gain, currently at {profit_pct:.2f}%)")
                    self.last_price = current_price
                    return

                eth_before = eth_balance
                # Execute sell via Kyber (off-thread), converting MAXX using on-chain decimals
                try:
                    maxx_decimals = self.system.maxx_contract.functions.decimals().call()
                except Exception:
                    maxx_decimals = 18
                maxx_amount_wei = int(Decimal(str(maxx_balance)) * (10 ** maxx_decimals))
                tx_hash = await asyncio.to_thread(self.kyber.sell_maxx_to_eth, maxx_amount_wei)

                if tx_hash:
                    await asyncio.sleep(5)  # Wait for confirmation
                    eth_after, _ = await self.system.get_balances()
                    eth_received = eth_after - eth_before

                    # Calculate realized P&L in ETH using tracked cost basis
                    pnl_eth = float(eth_received - (self.last_buy_eth_spent or Decimal('0')))

                    self.whale_tracker.log_our_trade(
                        'SELL', float(maxx_balance), float(eth_received),
                        current_price, float(pnl_eth), 'SMART_SELL_PROFIT', tx_hash
                    )

                    logger.info(f"SOLD! Received {eth_received:.6f} ETH | P&L: {pnl_eth:.6f} ETH (${pnl_eth*3300:.2f})")
                    # Track price for buy-back decision
                    self.last_sell_price = Decimal(str(current_price))
                    self.highest_price_since_sell = Decimal(str(current_price))
                    self.position_entry_price = None
                    self.last_buy_eth_spent = None

                    logger.info(f"Now watching for {self.dip_threshold:.1f}% dip to buy back in...")
                else:
                    logger.error("SELL FAILED")

            else:
                # WE DON'T HAVE MAXX - CHECK IF WE SHOULD BUY

                # Update highest price tracking
                if self.last_sell_price:
                    if not self.highest_price_since_sell or Decimal(str(current_price)) > self.highest_price_since_sell:
                        self.highest_price_since_sell = Decimal(str(current_price))
                        logger.info(f"New high since sell: ${self.highest_price_since_sell:.8f}")

                    # Calculate dip from highest
                    dip_pct = ((self.highest_price_since_sell - Decimal(str(current_price))) / self.highest_price_since_sell * 100)
                    logger.info(f"Dip from high: {dip_pct:.2f}%")

                    # BUY if dipped 15% from highest after sell
                    should_buy = dip_pct >= Decimal(str(self.dip_threshold))

                    if not should_buy:
                        logger.info(f" Waiting for dip (need {self.dip_threshold:.1f}% drop, currently {dip_pct:.2f}%)")
                        self.last_price = current_price
                        return

                    logger.info(f" DIP DETECTED! Buying now!")
                else:
                    # First buy - just go for it
                    logger.info(f" Initial buy - entering position")

                # ALWAYS KEEP 0.001 ETH RESERVE
                reserve_eth = self.eth_reserve
                available_eth = eth_balance - reserve_eth

                if available_eth > Decimal('0'):
                    buy_amount = available_eth

                    logger.info(f" BUYING WITH {buy_amount:.6f} ETH (keeping {reserve_eth:.6f} ETH reserve)")

                    maxx_before = maxx_balance
                    # Execute buy via Kyber (off-thread), converting ETH amount to wei
                    eth_amount_wei = int(Decimal(str(buy_amount)) * (10 ** 18))
                    tx_hash = await asyncio.to_thread(self.kyber.buy_eth_to_maxx, eth_amount_wei)

                    if tx_hash:
                        await asyncio.sleep(5)  # Wait for confirmation
                        _, maxx_after = await self.system.get_balances()
                        maxx_received = maxx_after - maxx_before

                        self.whale_tracker.log_our_trade(
                            'BUY', float(maxx_received), float(buy_amount),
                            current_price, 0, 'SMART_BUY_DIP', tx_hash
                        )

                        logger.info(f"BOUGHT! Received {maxx_received:,.2f} MAXX @ ${current_price:.8f}")

                        # Set entry price for profit calculations
                        self.position_entry_price = Decimal(str(current_price))
                        self.last_buy_eth_spent = Decimal(str(buy_amount))

                        # Reset tracking
                        self.highest_price_since_sell = None

                        logger.info(f"Now watching for {self.profit_target:.1f}% profit to sell...")
                    else:
                        logger.error("BUY FAILED")
                else:
                    logger.warning(f"Insufficient ETH after reserve: {available_eth:.6f} <= 0")

            self.last_price = current_price

        except Exception as e:
            logger.error(f"Trade error: {e}")

    async def show_stats(self):
        """Show trading statistics"""
        stats = self.whale_tracker.get_our_stats()
        logger.info("\n" + "="*60)
        logger.info(" TRADING STATISTICS")
        logger.info("="*60)
        logger.info(f"Total Trades: {stats['total_trades']}")
        logger.info(f"Wins: {stats['wins']}")
        logger.info(f"Win Rate: {stats['win_rate']:.2f}%")
        logger.info(f"Total P&L: {stats['total_pnl_eth']:.6f} ETH (${stats['total_pnl_usd']:.2f})")

        # Show whale summary
        whales = self.whale_tracker.get_whale_summary()
        if whales:
            logger.info("\n TOP WHALES:")
            for i, whale in enumerate(whales[:5], 1):
                logger.info(f"  {i}. {whale['wallet'][:10]}... | Vol: ${whale['volume']:,.2f} | Pos: {whale['position']:,.0f} MAXX")

    async def run(self):
        """Run the aggressive trading bot"""
        logger.info("="*60)
        logger.info(" AGGRESSIVE MAX PROFIT TRADER STARTING")
        logger.info("="*60)
        logger.info(f"Strategy: BUY/SELL ALL every {self.cycle_interval} seconds")
        logger.info(f"Target: ETHERMAX (MAXX) - High action token")
        logger.info(f"Whale tracking: ENABLED")
        logger.info(f"Safety: ALWAYS KEEPS 0.001 ETH RESERVE")
        logger.info("="*60)

        # Initialize system
        if not await self.system.initialize():
            logger.error("Failed to initialize")
            return

        # Create Kyber client using the same Web3/account (inherit gas settings via system)
        try:
            self.kyber = KyberClient(self.system.w3, self.system.account, self.system)
            logger.info("KyberSwap client initialized (V4-preferred)")
        except Exception as e:
            logger.error(f"Failed to init Kyber client: {e}")
            return

        cycle = 0
        try:
            while True:
                cycle += 1
                logger.info(f"\n CYCLE #{cycle} @ {datetime.now().strftime('%H:%M:%S')}")

                await self.analyze_and_trade()

                # Show stats every 5 cycles
                if cycle % 5 == 0:
                    await self.show_stats()

                logger.info(f"\nWaiting {self.cycle_interval} seconds until next cycle...")
                await asyncio.sleep(self.cycle_interval)

        except KeyboardInterrupt:
            logger.info("\nBot stopped by user")
        finally:
            await self.show_stats()
            logger.info("Goodbye!")

async def main():
    trader = AggressiveMaxTrader()
    await trader.run()

if __name__ == "__main__":
    asyncio.run(main())
