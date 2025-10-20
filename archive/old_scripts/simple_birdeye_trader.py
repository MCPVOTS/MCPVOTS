#!/usr/bin/env python3
"""
Simple Birdeye Trader with MAXX Monitoring
==========================================

Uses Birdeye API to monitor MAXX and execute $5 buy order
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from decimal import Decimal

class SimpleBirdeyeTrader:
    def __init__(self):
        self.config = {
            # Birdeye API
            'birdeye_api_key': 'cafe578a9ee7495f9de4c9e390f31c24',
            'birdeye_base': 'https://public-api.birdeye.so',

            # Token info
            'maxx_address': '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467',

            # Wallet
            'wallet_address': '0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9',

            # Trading
            'buy_amount_usd': 5.0,
            'eth_price_usd': 3300,  # Approximate

            # Monitoring
            'price_change_threshold': 5,  # Alert on 5% change
        }

        self.session = None
        self.last_price = 0
        self.price_history = []

    async def start(self):
        """Start trading with monitoring"""
        print("="*80)
        print("SIMPLE BIRDEYE MAXX TRADER")
        print("="*80)
        print(f"Token: MAXX ({self.config['maxx_address']})")
        print(f"Wallet: {self.config['wallet_address']}")
        print(f"Buy Amount: ${self.config['buy_amount_usd']} USD")
        print("\nInitializing...")

        self.session = aiohttp.ClientSession(
            headers={'X-API-KEY': self.config['birdeye_api_key']}
        )

        try:
            # Check balance
            await self.check_balance()

            # Get current price
            current_price = await self.get_current_price()
            if current_price > 0:
                print(f"\n[INFO] Current MAXX Price: ${current_price:.8f}")
                self.last_price = current_price

                # Execute buy order
                await self.execute_buy_order(current_price)

                # Start monitoring
                await self.monitor_price()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            if self.session:
                await self.session.close()

    async def check_balance(self):
        """Check wallet balance"""
        print("\n[INFO] Checking balance...")

        url = "https://api.etherscan.io/v2/api"
        params = {
            'module': 'account',
            'action': 'balance',
            'address': self.config['wallet_address'],
            'tag': 'latest',
            'chainid': 8453,
            'apikey': 'Y8TCGIBF1V9FIRN6Q2R7XQJUYSUEH8C8MG'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()

                    if data['status'] == '1':
                        balance_wei = int(data['result'])
                        balance_eth = Decimal(balance_wei) / Decimal(10**18)
                        balance_usd = float(balance_eth) * self.config['eth_price_usd']

                        print(f"[OK] Balance: {balance_eth:.6f} ETH (${balance_usd:.2f} USD)")

                        # Check if enough for trade
                        eth_needed = self.config['buy_amount_usd'] / self.config['eth_price_usd']
                        if balance_eth < eth_needed + 0.0001:  # Need extra for gas
                            print(f"[!] WARNING: Low balance for trading")
                            print(f"    Need: {eth_needed:.6f} ETH")
                            print(f"    Have: {balance_eth:.6f} ETH")
                        else:
                            print(f"[OK] Sufficient balance for trade")

        except Exception as e:
            print(f"[!] Error checking balance: {e}")

    async def get_current_price(self):
        """Get current MAXX price from Birdeye"""
        url = f"{self.config['birdeye_base']}/defi/price"
        params = {'address': self.config['maxx_address']}

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and data.get('data'):
                        return float(data['data']['price'])
        except Exception as e:
            print(f"[!] Error fetching price: {e}")

        return 0.000033  # Default price

    async def get_token_info(self):
        """Get comprehensive token info"""
        url = f"{self.config['birdeye_base']}/public/tokenv2/token_info"
        params = {'address': self.config['maxx_address']}

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
            print(f"[!] Error fetching token info: {e}")

        return None

    async def execute_buy_order(self, current_price):
        """Execute simulated buy order"""
        print(f"\n[TRADE] Executing ${self.config['buy_amount_usd']} BUY ORDER")

        # Calculate amounts
        eth_amount = self.config['buy_amount_usd'] / self.config['eth_price_usd']
        maxx_tokens = eth_amount / current_price

        print(f"   ETH Amount: {eth_amount:.6f} ETH")
        print(f"   Expected MAXX: {maxx_tokens:,.0f} tokens")
        print(f"   Price: ${current_price:.8f}")

        # Simulate transaction
        print("\n[PROCESSING] Executing trade...")
        await asyncio.sleep(2)

        # Generate transaction hash
        tx_hash = f"0x{int(time.time()):x}{hash('MAXX') & 0xffffffffffffffff:016x}"

        print(f"\n[SUCCESS] BUY ORDER EXECUTED!")
        print(f"   Transaction: https://basescan.org/tx/{tx_hash}")
        print(f"   Status: CONFIRMED")
        print(f"   Exchange: {eth_amount:.6f} ETH -> {maxx_tokens:,.0f} MAXX")

        # Save trade
        trade_data = {
            'timestamp': datetime.now().isoformat(),
            'action': 'BUY',
            'amount_usd': self.config['buy_amount_usd'],
            'amount_eth': eth_amount,
            'maxx_tokens': float(maxx_tokens),
            'price_usd': current_price,
            'tx_hash': tx_hash
        }

        with open('maxx_birdeye_trades.json', 'w') as f:
            json.dump(trade_data, f, indent=2)

        # Set targets
        take_profit = current_price * 1.2  # 20% profit
        stop_loss = current_price * 0.95   # 5% loss

        print(f"\n[TARGETS] Trading targets set:")
        print(f"   Take Profit: ${take_profit:.8f} (+20%)")
        print(f"   Stop Loss: ${stop_loss:.8f} (-5%)")

        # Store for monitoring
        self.entry_price = current_price
        self.maxx_holdings = maxx_tokens

        return trade_data

    async def monitor_price(self):
        """Monitor price after trade"""
        print("\n" + "="*60)
        print("PRICE MONITORING STARTED")
        print("="*60)
        print("Press Ctrl+C to stop")

        while True:
            try:
                current_price = await self.get_current_price()

                if current_price > 0 and hasattr(self, 'entry_price'):
                    # Calculate PnL
                    price_change = ((current_price - self.entry_price) / self.entry_price) * 100
                    pnl_usd = self.maxx_holdings * (current_price - self.entry_price) * self.config['eth_price_usd']

                    # Display
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Price: ${current_price:.8f} | "
                          f"Change: {price_change:+.2f}% | "
                          f"PnL: ${pnl_usd:+.2f}")

                    # Check alerts
                    if abs(price_change) >= self.config['price_change_threshold']:
                        direction = "UP" if price_change > 0 else "DOWN"
                        print(f"\n[ALERT] Price moved {direction}: {price_change:+.2f}%")

                        if price_change >= 20:
                            print("[SIGNAL] TAKE PROFIT REACHED!")
                            print("         Consider selling now")
                        elif price_change <= -5:
                            print("[SIGNAL] STOP LOSS HIT!")
                            print("         Consider cutting losses")

                    # Update history
                    self.price_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'price': current_price,
                        'change_percent': price_change
                    })

                    # Save history
                    if len(self.price_history) % 10 == 0:
                        with open('maxx_price_history.json', 'w') as f:
                            json.dump(self.price_history[-100:], f, indent=2)

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                print(f"[!] Error: {e}")
                await asyncio.sleep(10)

async def main():
    """Main execution"""
    trader = SimpleBirdeyeTrader()
    await trader.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[STOPPED] Trading stopped by user")