#!/usr/bin/env python3
"""
Enhanced Automated Trading System for MAXX v2.0
Improved counter-trading strategy with better error handling and rate limiting

LAST WORKING: October 3, 2025 at 12:27 PM
LOG FILE: enhanced_trading_20251003_122712.log

WORKING CONFIGURATION:
- Uses Uniswap V2 Router: 0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24
- MAXX Contract: 0xFB7a83abe4F4A4E51c77B92E521390B769ff6467
- Trading Account: 0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9
- Position Size: 0.0003 ETH (~$1 USD)
- Strategy: Counter-trading (Buy on sells, Sell on buys)

POOL INFO (DexScreener verified):
- Pool: 0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148
- Liquidity: $55K (8.87 ETH + 4.4M MAXX)
- Uniswap V4 pool, but V2 router works fine
- Source: https://dexscreener.com/base/0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148

✅ USE ONLY standalone_config.py configuration values
✅ V2 router proven to work with this pool
"""
import asyncio
import sys
import time
import json
import logging
import os
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import required modules
from master_trading_system import MasterTradingSystem

# Configure enhanced logging
def setup_logger():
    """Setup logger with file and console handlers"""
    log_file = f"enhanced_trading_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler with simpler format (no special characters)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()

class RateLimiter:
    """Simple rate limiter for RPC calls"""
    def __init__(self, calls_per_second: float = 2.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0

    async def wait(self):
        """Wait if needed to respect rate limit"""
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        self.last_call = time.time()

class ConfigManager:
    """Improved configuration manager"""
    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        """Load configuration from standalone_config"""
        try:
            import standalone_config as cfg

            self.config = {
                'PROVIDER_URL': cfg.PROVIDER_URL,
                'CHAIN_ID': cfg.CHAIN_ID,
                'MAXX_CONTRACT_ADDRESS': cfg.MAXX_CONTRACT_ADDRESS,
                'UNISWAP_V2_ROUTER': cfg.UNISWAP_V2_ROUTER,
                'UNISWAP_V2_FACTORY': cfg.UNISWAP_V2_FACTORY,
                'WETH_ADDRESS': cfg.WETH_ADDRESS,
                'MAXX_ETH_POOL': cfg.MAXX_ETH_POOL,
                'TEST_ETH_AMOUNT': cfg.TEST_ETH_AMOUNT,
                'SLIPPAGE_TOLERANCE': cfg.SLIPPAGE_TOLERANCE,
                'GAS_LIMIT': cfg.GAS_LIMIT,
                'GAS_PRICE_GWEI': cfg.GAS_PRICE_GWEI,
                'TRADING_ACCOUNT_ADDRESS': cfg.TRADING_ACCOUNT_ADDRESS,
                'MAX_GAS_PRICE_GWEI': cfg.MAX_GAS_PRICE_GWEI
            }
            logger.info("Configuration loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Set defaults
            self.config = {
                'PROVIDER_URL': 'https://mainnet.base.org',
                'CHAIN_ID': 8453,
                'MAXX_CONTRACT_ADDRESS': os.getenv('MAXX_CONTRACT_ADDRESS', '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467'),
                'TEST_ETH_AMOUNT': Decimal('0.0003'),
                'SLIPPAGE_TOLERANCE': 0.5,
                'GAS_LIMIT': 300000,
                'GAS_PRICE_GWEI': 0.1,
                'MAX_GAS_PRICE_GWEI': 1.0
            }

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

class MarketMonitor:
    """Enhanced market monitor with better signal detection"""

    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.rate_limiter = RateLimiter(calls_per_second=2.0)
        self.price_history = []
        self.last_price = None
        self.price_change_threshold = 0.005  # 0.5% threshold
        self.volume_threshold = Decimal('100')
        self.max_history = 100

    async def monitor_pool_activity(self, trading_system) -> Optional[Dict]:
        """Monitor pool for trading activity with improved error handling"""
        try:
            # Rate limit our calls
            await self.rate_limiter.wait()

            # Get current pool state
            reserves = await self._get_pool_reserves(trading_system)
            if not reserves or reserves[0] == 0:
                return None

            maxx_reserve, eth_reserve = reserves

            # Calculate current price
            current_price = eth_reserve / maxx_reserve

            # Store price history
            self.price_history.append({
                'price': current_price,
                'timestamp': datetime.now(),
                'maxx_reserve': maxx_reserve,
                'eth_reserve': eth_reserve
            })

            # Keep history size manageable
            if len(self.price_history) > self.max_history:
                self.price_history.pop(0)

            # Detect signal
            signal = self._detect_market_signal(current_price)

            if signal:
                logger.info(f"Signal detected: {signal['type']} | Price: {current_price:.8f} | Change: {signal['price_change']*100:.2f}%")
                return signal

            return None

        except Exception as e:
            logger.error(f"Error monitoring pool: {str(e)[:100]}")
            return None

    async def _get_pool_reserves(self, trading_system) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Get pool reserves with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                from static_dex_trader import StaticDEXTrader
                trader = StaticDEXTrader()
                trader.w3 = trading_system.w3

                # Initialize contracts if needed
                if not hasattr(trader, 'pool') or trader.pool is None:
                    trader.pool = trading_system.w3.eth.contract(
                        address=self.config.get('MAXX_ETH_POOL'),
                        abi=trader.pool_abi
                    )
                    trader.maxx_contract = trading_system.maxx_contract
                    trader.weth_contract = trading_system.w3.eth.contract(
                        address=self.config.get('WETH_ADDRESS'),
                        abi=trader.erc20_abi
                    )

                reserves = await trader.get_pool_reserves()
                return reserves

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Retry {attempt + 1}/{max_retries} getting reserves: {str(e)[:50]}")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to get pool reserves after {max_retries} attempts")
                    return None, None

        return None, None

    def _detect_market_signal(self, current_price: Decimal) -> Optional[Dict]:
        """Enhanced signal detection"""
        if len(self.price_history) < 2:
            self.last_price = current_price
            return None

        # Get previous price
        prev_price = self.price_history[-2]['price']

        # Calculate price change
        if prev_price > 0:
            price_change = (current_price - prev_price) / prev_price

            # Check if change exceeds threshold
            if abs(price_change) >= self.price_change_threshold:
                # Determine signal type
                if price_change > 0:
                    signal_type = 'BUY_PRESSURE'  # Price up = market buying
                else:
                    signal_type = 'SELL_PRESSURE'  # Price down = market selling

                self.last_price = current_price

                return {
                    'type': signal_type,
                    'price': current_price,
                    'price_change': abs(price_change),
                    'timestamp': datetime.now(),
                    'confidence': min(abs(price_change) / self.price_change_threshold, 3.0)  # Confidence up to 3x threshold
                }

        return None

class EnhancedAutomatedTrader:
    """Enhanced automated trader v2 with improved features"""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.trading_system = None
        self.market_monitor = MarketMonitor(self.config_manager)
        self.running = False
        self.trade_history = []
        self.last_action = None
        self.cycle_count = 0

        # Trading parameters
        self.position_size_eth = Decimal(str(self.config_manager.get('TEST_ETH_AMOUNT', '0.0003')))
        self.profit_target = 0.02  # 2% profit target
        self.stop_loss = 0.05  # 5% stop loss
        self.max_position_usd = Decimal('10.0')

        # Trading statistics
        self.stats = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit_eth': Decimal('0'),
            'start_time': None,
            'last_signal': None,
            'strategy': 'counter_trading_v2',
            'cycles_completed': 0,
            'errors': 0
        }

        # State tracking
        self.entry_price = None
        self.entry_time = None
        self.last_balance_check = None

    async def initialize(self) -> bool:
        """Initialize the automated trader with better error handling"""
        try:
            logger.info("="*80)
            logger.info("INITIALIZING ENHANCED AUTOMATED TRADER v2.0")
            logger.info("="*80)

            # Initialize trading system
            logger.info("Initializing Master Trading System...")
            self.trading_system = MasterTradingSystem()

            if not await self.trading_system.initialize():
                raise Exception("Failed to initialize trading system")

            # Get initial balances
            eth_balance, maxx_balance = await self.trading_system.get_balances()

            # Log initialization
            logger.info(f"Trading Account: {self.config_manager.get('TRADING_ACCOUNT_ADDRESS')}")
            logger.info(f"Network: Base Chain (ID: {self.config_manager.get('CHAIN_ID')})")
            logger.info(f"Initial Balances - ETH: {eth_balance:.6f}, MAXX: {maxx_balance:,.2f}")
            logger.info(f"Strategy: {self.stats['strategy']}")
            logger.info(f"Position Size: {self.position_size_eth} ETH")
            logger.info(f"Profit Target: {self.profit_target * 100}%")
            logger.info(f"Stop Loss: {self.stop_loss * 100}%")
            logger.info("="*80)

            self.stats['start_time'] = datetime.now()
            return True

        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False

    async def run_counter_trading(self):
        """Main trading loop with improved monitoring"""
        logger.info("\n" + "="*80)
        logger.info("STARTING ENHANCED AUTOMATED TRADING")
        logger.info("Strategy: Counter-trading (Buy on sells, Sell on buys)")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*80 + "\n")

        self.running = True

        while self.running:
            try:
                cycle_start = time.time()
                self.cycle_count += 1

                # Header for cycle
                print(f"\n{'-'*60}")
                print(f"TRADING CYCLE #{self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'-'*60}")

                # Get current state
                current_state = await self._get_current_state()

                # Monitor for signals
                print("📊 Monitoring market activity...")
                signal = await self.market_monitor.monitor_pool_activity(self.trading_system)

                if signal:
                    self.stats['last_signal'] = signal
                    await self._handle_signal(signal, current_state)
                else:
                    # Check existing position
                    if current_state['maxx_balance'] > 0:
                        await self._manage_position(current_state)
                    else:
                        print("No signal detected - holding ETH")

                # Print cycle summary
                await self._print_cycle_summary(current_state)

                # Wait for next cycle with dynamic timing
                cycle_time = time.time() - cycle_start
                base_wait = 30  # Base 30 seconds
                if signal:
                    base_wait = 15  # Shorter wait after signal

                wait_time = max(0, base_wait - cycle_time)
                if wait_time > 0:
                    print(f"\nWaiting {wait_time:.0f}s for next cycle...")
                    for i in range(int(wait_time)):
                        if not self.running:
                            break
                        await asyncio.sleep(1)

            except KeyboardInterrupt:
                logger.info("\n\nShutdown requested by user")
                self.running = False
                break
            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Error in cycle {self.cycle_count}: {e}")
                print(f"Error: {str(e)[:50]}...")
                await asyncio.sleep(5)

        await self.shutdown()

    async def _get_current_state(self) -> Dict:
        """Get current trading state"""
        try:
            eth_balance, maxx_balance = await self.trading_system.get_balances()

            current_price = None
            if maxx_balance > 0:
                try:
                    from static_dex_trader import StaticDEXTrader
                    trader = StaticDEXTrader()
                    trader.w3 = self.trading_system.w3
                    trader.maxx_contract = self.trading_system.maxx_contract
                    current_price = await trader.get_token_price()
                except:
                    pass

            return {
                'eth_balance': eth_balance,
                'maxx_balance': maxx_balance,
                'current_price': current_price,
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error getting state: {e}")
            return {
                'eth_balance': Decimal('0'),
                'maxx_balance': Decimal('0'),
                'current_price': None,
                'timestamp': datetime.now()
            }

    async def _handle_signal(self, signal: Dict, state: Dict):
        """Handle trading signal"""
        signal_type = signal['type']
        confidence = signal.get('confidence', 1.0)

        print(f"\nSIGNAL: {signal_type}")
        print(f"   Price Change: {signal['price_change']*100:.2f}%")
        print(f"   Confidence: {confidence:.2f}x")

        # Determine action based on signal and position
        action = None

        if signal_type == 'SELL_PRESSURE' and state['maxx_balance'] == 0:
            # Market selling - we buy
            if state['eth_balance'] >= self.position_size_eth:
                action = {
                    'type': 'BUY',
                    'reason': f"Market sell pressure detected ({signal['price_change']*100:.2f}% change)",
                    'amount': self.position_size_eth * min(confidence, 1.5),  # Scale with confidence
                    'confidence': confidence
                }
        elif signal_type == 'BUY_PRESSURE' and state['maxx_balance'] > 0:
            # Market buying - we sell
            action = {
                'type': 'SELL',
                'reason': f"Market buy pressure detected ({signal['price_change']*100:.2f}% change)",
                'amount': state['maxx_balance'],
                'confidence': confidence
            }

        if action:
            await self._execute_action(action, state)

    async def _manage_position(self, state: Dict):
        """Manage existing position"""
        if not state['current_price'] or not self.entry_price:
            return

        # Calculate profit/loss
        price_change = (state['current_price'] - self.entry_price) / self.entry_price
        position_age = datetime.now() - self.entry_time if self.entry_time else timedelta(0)

        # Check profit target
        if price_change >= self.profit_target:
            action = {
                'type': 'SELL',
                'reason': f"Profit target reached ({price_change*100:.2f}%)",
                'amount': state['maxx_balance']
            }
            await self._execute_action(action, state)

        # Check stop loss
        elif price_change <= -self.stop_loss:
            action = {
                'type': 'SELL',
                'reason': f"Stop loss triggered ({price_change*100:.2f}%)",
                'amount': state['maxx_balance']
            }
            await self._execute_action(action, state)

        # Check timeout (sell if position held too long)
        elif position_age > timedelta(minutes=30):
            action = {
                'type': 'SELL',
                'reason': f"Position timeout ({position_age})",
                'amount': state['maxx_balance']
            }
            await self._execute_action(action, state)

    async def _execute_action(self, action: Dict, state: Dict):
        """Execute trading action with enhanced feedback"""
        action_type = action['type']

        try:
            print(f"\nEXECUTING {action_type.upper()}")
            print(f"   Reason: {action['reason']}")

            if action_type == 'BUY':
                amount = min(action['amount'], state['eth_balance'])
                if amount > 0:
                    print(f"   Amount: {amount:.6f} ETH")
                    print("   Submitting transaction...")

                    tx_hash = await self.trading_system.buy_maxx(amount)

                    if tx_hash:
                        print(f"   SUCCESS!")
                        print(f"   Tx: https://basescan.org/tx/{tx_hash}")

                        # Update state
                        self.entry_price = state['current_price']
                        self.entry_time = datetime.now()
                        self.last_action = action

                        # Update stats
                        self.stats['total_trades'] += 1
                        self.stats['successful_trades'] += 1

                        # Record trade
                        self.trade_history.append({
                            'type': 'BUY',
                            'amount_eth': float(amount),
                            'price': float(state['current_price']) if state['current_price'] else None,
                            'timestamp': datetime.now(),
                            'reason': action['reason'],
                            'tx_hash': tx_hash,
                            'confidence': action.get('confidence', 1.0)
                        })
                    else:
                        print(f"   FAILED: Transaction failed")
                        self.stats['total_trades'] += 1
                        self.stats['failed_trades'] += 1

            elif action_type == 'SELL':
                amount = action['amount']
                if amount > 0 and state['maxx_balance'] > 0:
                    print(f"   Amount: {amount:,.2f} MAXX")
                    print("   Submitting transaction...")

                    tx_hash = await self.trading_system.sell_maxx(amount)

                    if tx_hash:
                        print(f"   SUCCESS!")
                        print(f"   Tx: https://basescan.org/tx/{tx_hash}")

                        # Calculate profit
                        if self.entry_price and state['current_price']:
                            profit_pct = (state['current_price'] - self.entry_price) / self.entry_price
                            profit_eth = amount * (state['current_price'] - self.entry_price)
                            self.stats['total_profit_eth'] += profit_eth

                            print(f"   Profit: {profit_eth:.6f} ETH ({profit_pct*100:.2f}%)")

                        # Clear position
                        self.entry_price = None
                        self.entry_time = None
                        self.last_action = action

                        # Update stats
                        self.stats['total_trades'] += 1
                        self.stats['successful_trades'] += 1

                        # Record trade
                        self.trade_history.append({
                            'type': 'SELL',
                            'amount_maxx': float(amount),
                            'price': float(state['current_price']) if state['current_price'] else None,
                            'timestamp': datetime.now(),
                            'reason': action['reason'],
                            'tx_hash': tx_hash,
                            'profit_pct': float(profit_pct) if 'profit_pct' in locals() else None,
                            'profit_eth': float(profit_eth) if 'profit_eth' in locals() else None
                        })
                    else:
                        print(f"   FAILED: Transaction failed")
                        self.stats['total_trades'] += 1
                        self.stats['failed_trades'] += 1

        except Exception as e:
            logger.error(f"Error executing {action_type}: {e}")
            print(f"   ERROR: {str(e)[:50]}")

    async def _print_cycle_summary(self, state: Dict):
        """Print enhanced cycle summary"""
        self.stats['cycles_completed'] += 1

        print(f"\nCYCLE #{self.cycle_count} SUMMARY")
        print(f"   Balance: {state['eth_balance']:.6f} ETH | {state['maxx_balance']:,.2f} MAXX")

        if state['maxx_balance'] > 0 and state['current_price']:
            position_value = state['maxx_balance'] * state['current_price']
            print(f"   Position: {position_value:.6f} ETH")

            if self.entry_price:
                profit_pct = (state['current_price'] - self.entry_price) / self.entry_price * 100
                print(f"   P/L: {profit_pct:+.2f}%")

        print(f"   Trades: {self.stats['total_trades']} (Success: {(self.stats['successful_trades']/max(1,self.stats['total_trades'])*100):.1f}%)")

        if self.stats['total_profit_eth'] > 0:
            print(f"   Total Profit: {self.stats['total_profit_eth']:.6f} ETH")

        runtime = datetime.now() - self.stats['start_time']
        print(f"   Runtime: {runtime} | Errors: {self.stats['errors']}")
        print(f"{'-'*60}")

    async def shutdown(self):
        """Enhanced shutdown with detailed statistics"""
        logger.info("\n" + "="*80)
        logger.info("SHUTTING DOWN ENHANCED AUTOMATED TRADER")
        logger.info("="*80)

        if self.stats['start_time']:
            runtime = datetime.now() - self.stats['start_time']
        else:
            runtime = timedelta(0)

        print("\nFINAL STATISTICS")
        print(f"   Runtime: {runtime}")
        print(f"   Cycles Completed: {self.stats['cycles_completed']}")
        print(f"   Total Trades: {self.stats['total_trades']}")
        print(f"   Successful Trades: {self.stats['successful_trades']}")
        print(f"   Failed Trades: {self.stats['failed_trades']}")
        print(f"   Success Rate: {(self.stats['successful_trades']/max(1,self.stats['total_trades'])*100):.1f}%")
        print(f"   Total Profit: {self.stats['total_profit_eth']:.6f} ETH")
        print(f"   Errors Encountered: {self.stats['errors']}")

        # Save trade history
        if self.trade_history:
            filename = f"trade_history_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(self.trade_history, f, indent=2, default=str)
            print(f"\nTrade history saved to: {filename}")

        print("\n" + "="*80)

async def main():
    """Main entry point"""
    trader = EnhancedAutomatedTrader()

    try:
        if await trader.initialize():
            await trader.run_counter_trading()
        else:
            logger.error("Failed to initialize trader")
            return 1
    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    finally:
        await trader.shutdown()

    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))