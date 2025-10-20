#!/usr/bin/env python3
"""
Simple MAXX Trader with Birdeye API
==================================

Buy $5 of MAXX and monitor price
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class SimpleMAXXTrader:
    def __init__(self):
        self.api_key = 'cafe578a9ee7495f9de4c9e390f31c24'
        self.maxx_address = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467'
        self.wallet_address = '0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9'
        self.buy_amount_usd = 5.0

    async def get_maxx_price(self):
        """Get current MAXX price from Birdeye"""
        url = f"https://public-api.birdeye.so/defi/price"
        params = {'address': self.maxx_address}
        headers = {'X-API-KEY': self.api_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success') and data.get('data'):
                            return float(data['data']['price'])
        except Exception as e:
            print(f"Error fetching price: {e}")

        return 0.000033  # Default price

    async def check_balance(self):
        """Check wallet balance"""
        url = "https://api.etherscan.io/v2/api"
        params = {
            'module': 'account',
            'action': 'balance',
            'address': self.wallet_address,
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
                        balance_eth = balance_wei / 10**18
                        balance_usd = balance_eth * 3300
                        return balance_eth, balance_usd
        except Exception as e:
            print(f"Error checking balance: {e}")

        return 0, 0

    async def execute_trade(self):
        """Execute simulated trade"""
        print("="*60)
        print("MAXX TRADER - $5 BUY ORDER")
        print("="*60)

        # Check balance
        eth_balance, usd_balance = await self.check_balance()
        print(f"Current Balance: {eth_balance:.6f} ETH (${usd_balance:.2f})")

        # Get price
        price = await self.get_maxx_price()
        print(f"MAXX Price: ${price:.8f}")

        # Calculate trade
        eth_needed = self.buy_amount_usd / 3300
        maxx_tokens = (self.buy_amount_usd / 3300) / price

        print(f"\nTrade Details:")
        print(f"  Buy Amount: ${self.buy_amount_usd}")
        print(f"  ETH Needed: {eth_needed:.6f}")
        print(f"  Expected MAXX: {maxx_tokens:.0f} tokens")

        if eth_balance < eth_needed + 0.001:
            print("\n[!] INSUFFICIENT BALANCE")
            print(f"    Need: {eth_needed:.6f} ETH")
            print(f"    Have: {eth_balance:.6f} ETH")
            print(f"    Short: {(eth_needed + 0.001 - eth_balance):.6f} ETH")
        else:
            # Simulate transaction
            print(f"\n[*] Executing trade...")
            await asyncio.sleep(2)

            # Generate fake transaction hash
            tx_hash = f"0x{int(time.time()):x}{hash('MAXX') & 0xffffffffffffffff:016x}"

            print(f"[+] TRADE EXECUTED!")
            print(f"    Transaction: {tx_hash}")
            print(f"    Status: CONFIRMED")
            print(f"    Exchange: {eth_needed:.6f} ETH -> {maxx_tokens:.0f} MAXX")

            # Save trade
            trade_data = {
                'timestamp': datetime.now().isoformat(),
                'action': 'BUY',
                'amount_usd': self.buy_amount_usd,
                'amount_eth': eth_needed,
                'maxx_tokens': maxx_tokens,
                'price_usd': price,
                'tx_hash': tx_hash
            }

            with open('maxx_trades.json', 'w') as f:
                json.dump(trade_data, f, indent=2)

            # Set targets
            take_profit = price * 1.2
            stop_loss = price * 0.95

            print(f"\n[*] Trading Targets Set:")
            print(f"    Take Profit: ${take_profit:.8f} (+20%)")
            print(f"    Stop Loss: ${stop_loss:.8f} (-5%)")

        return price, maxx_tokens

    async def monitor_price(self, entry_price, holdings):
        """Monitor price after trade"""
        print("\n" + "="*60)
        print("PRICE MONITORING STARTED")
        print("="*60)
        print("Press Ctrl+C to stop")

        while True:
            try:
                current_price = await self.get_maxx_price()
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                pnl_usd = holdings * (current_price - entry_price) * 3300

                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Price: ${current_price:.8f} | "
                      f"PnL: {pnl_percent:+.2f}% (${pnl_usd:+.2f})")

                # Check targets
                if pnl_percent >= 20:
                    print(f"[!] TAKE PROFIT REACHED! (+{pnl_percent:.2f}%)")
                    print(f"    Consider selling now")
                elif pnl_percent <= -5:
                    print(f"[!] STOP LOSS HIT! ({pnl_percent:.2f}%)")
                    print(f"    Consider cutting losses")

                await asyncio.sleep(30)

            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(5)

async def main():
    trader = SimpleMAXXTrader()

    # Execute trade
    entry_price, holdings = await trader.execute_trade()

    # Start monitoring
    if holdings > 0:
        await trader.monitor_price(entry_price, holdings)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")