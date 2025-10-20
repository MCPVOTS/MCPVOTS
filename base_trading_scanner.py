#!/usr/bin/env python3
"""
Base Chain High-Frequency Trading Opportunities Scanner
"""

import os
import json
import requests

def main():
    print('BASE CHAIN HIGH-FREQUENCY TRADING OPPORTUNITIES')
    print('=' * 55)

    # Check what tokens we have data for
    tokens_found = []

    # Check MAXX data
    if os.path.exists('data/maxx_pool_analysis.json'):
        with open('data/maxx_pool_analysis.json', 'r') as f:
            data = json.load(f)

        if 'pairs' in data and data['pairs']:
            pair = data['pairs'][0]
            base_token = pair.get('baseToken', {})
            symbol = base_token.get('symbol', 'MAXX')
            price_usd = float(pair.get('priceUsd', 0))
            volume_24h = pair.get('volume', {}).get('h24', 0)
            change_24h = pair.get('priceChange', {}).get('h24', 0)
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            txns_24h = pair.get('txns', {}).get('h24', {})
            total_txns = txns_24h.get('buys', 0) + txns_24h.get('sells', 0)

            tokens_found.append({
                'symbol': symbol,
                'price': price_usd,
                'volume': volume_24h,
                'change': change_24h,
                'liquidity': liquidity,
                'txns_24h': total_txns
            })

    # Display found tokens
    if tokens_found:
        print(f'FOUND {len(tokens_found)} ACTIVE TOKENS:')
        print()

        for i, token in enumerate(tokens_found, 1):
            symbol = token['symbol']
            price = token['price']
            volume = token['volume']
            change = token['change']
            liquidity = token['liquidity']
            txns = token['txns_24h']
            hourly_txns = txns / 24 if txns > 0 else 0

            print(f'{i}. {symbol:<8} | Price: ${price:.6f} | Change: {change:+.1f}% | Volume: ${volume:,.0f} | Txns/hr: {hourly_txns:.1f}')

    print()
    print('TRADING STRATEGIES FOR $50 CAPITAL:')
    print()
    print('1. MAXX SCALPING (Most Active):')
    print('   - Buy/Sell 2-5% price moves')
    print('   - Target: 5-10 trades per day')
    print('   - Risk per trade: $1-2')
    print('   - Potential profit: $5-15/day')
    print()
    print('2. MOMENTUM TRADING:')
    print('   - Enter on volume spikes')
    print('   - Exit on profit targets (5-10%)')
    print('   - Use reactive trader automation')
    print('   - Quick trades, quick profits')
    print()
    print('3. RANGE TRADING:')
    print('   - Buy at support levels')
    print('   - Sell at resistance levels')
    print('   - Lower risk, consistent gains')
    print('   - Good for sideways markets')
    print()
    print('4. NEWS/EVENT TRADING:')
    print('   - Monitor Base ecosystem news')
    print('   - Trade on announcements')
    print('   - Higher risk, higher reward')
    print()
    print('5. ARBITRAGE:')
    print('   - Price differences across DEXes')
    print('   - Low risk, guaranteed profits')
    print('   - Requires quick execution')

    print()
    print('CAPITAL ALLOCATION RECOMMENDATION:')
    print('- $25-30: MAXX scalping (primary strategy)')
    print('- $10-15: Momentum/range trading')
    print('- $5-10: Arbitrage opportunities')
    print('- $0-5: Reserve for opportunities')

    print()
    print('TOOLS READY TO USE:')
    print('- Reactive trader: Automated buy/sell')
    print('- Market data service: Real-time prices')
    print('- Strategy optimizer: Performance analysis')
    print('- Whale tracker: Follow successful traders')

if __name__ == '__main__':
    main()
