#!/usr/bin/env python3
"""Analyze MAXX Trade History"""
import json
import os
from datetime import datetime

print('='*60)
print('ANALYZING MAXX TRADE HISTORY')
print('='*60)

# Check all available trade files
files = [
    'data/maxx_trades_database.json',
    'data/maxx_birdeye_trades.json',
    'data/smart_trader_history.json',
    'data/maxx_recent_trades.json'
]

for filename in files:
    if os.path.exists(filename):
        print(f'\n📄 {filename}')
        print('-'*60)

        with open(filename, 'r') as f:
            data = json.load(f)

        if filename == 'maxx_trades_database.json':
            metadata = data.get('metadata', {})
            trades = data.get('trades', [])
            pump_events = data.get('pump_events', [])

            total = metadata.get('total_trades', 0)
            print(f'Total Trades: {total}')
            print(f'Contract: {metadata.get("contract_address", "N/A")}')
            print(f'Pump Events: {len(pump_events)}')

            metrics = data.get('performance_metrics', {})
            print(f'\n📊 Performance:')
            print(f'  Profitable: {metrics.get("profitable_trades", 0)}')
            print(f'  Losses: {metrics.get("loss_trades", 0)}')
            print(f'  Win Rate: {metrics.get("win_rate", 0):.2f}%')
            print(f'  Avg Profit: ${metrics.get("average_profit", 0):.4f}')

        elif filename == 'maxx_birdeye_trades.json':
            print(f'Action: {data.get("action")}')
            print(f'MAXX: {data.get("maxx_tokens", 0):.2f}')
            print(f'USD: ${data.get("amount_usd", 0):.2f}')
            print(f'ETH: {data.get("amount_eth", 0):.6f}')
            print(f'Price: ${data.get("price_usd", 0):.8f}')
            print(f'Time: {data.get("timestamp")}')

        elif filename == 'smart_trader_history.json':
            trades = data.get('trades', [])
            stats = data.get('statistics', {})

            print(f'Total Trades: {len(trades)}')

            if stats:
                print(f'\n📊 Statistics:')
                print(f'  Win Rate: {stats.get("win_rate", 0):.2f}%')
                print(f'  Total P&L: {stats.get("total_pnl_eth", 0):.6f} ETH')
                print(f'  Total P&L USD: ${stats.get("total_pnl_usd", 0):.2f}')
                print(f'  Profitable: {stats.get("profitable_trades", 0)}')
                print(f'  Losses: {stats.get("losing_trades", 0)}')

            if trades:
                print(f'\n🔄 Recent {min(5, len(trades))} Trades:')
                for trade in trades[-5:]:
                    t_type = trade.get('type')
                    reason = trade.get('reason', 'N/A')
                    pnl = trade.get('pnl', 0)
                    timestamp = trade.get('timestamp', 'N/A')
                    print(f'  [{timestamp[:19]}] {t_type}: {reason} | P&L: {pnl:.6f} ETH')

        elif filename == 'maxx_recent_trades.json':
            if data.get('success') and data.get('data'):
                items = data['data'].get('items', [])
                print(f'Recent Trades: {len(items)}')

                buys = [t for t in items if t.get('side') == 'buy']
                sells = [t for t in items if t.get('side') == 'sell']

                print(f'Buys: {len(buys)}')
                print(f'Sells: {len(sells)}')

                if len(sells) > 0:
                    ratio = len(buys) / len(sells)
                    print(f'Buy/Sell Ratio: {ratio:.2f}')

                    if ratio > 1.5:
                        print('📈 BULLISH - More buying pressure!')
                    elif ratio < 0.7:
                        print('📉 BEARISH - More selling pressure!')
                    else:
                        print('⚖️ NEUTRAL - Balanced activity')

                if items:
                    print(f'\n🔄 Last 3 Trades:')
                    for item in items[:3]:
                        side = item.get('side', 'unknown').upper()
                        amount = item.get('amount', 0)
                        price = item.get('price', 0)
                        timestamp = item.get('blockUnixTime', 0)

                        if timestamp:
                            dt = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            dt = 'N/A'

                        emoji = '🟢' if side == 'BUY' else '🔴'
                        print(f'  {emoji} {side}: {amount:.2f} MAXX @ ${price:.8f} - {dt}')
    else:
        print(f'\n❌ {filename} - NOT FOUND')

print('\n' + '='*60)
print('✅ ANALYSIS COMPLETE')
print('='*60)
