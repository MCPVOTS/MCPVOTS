"""
BROAD MARKET SCANNER
====================

Scans multiple networks for genuine trading opportunities
"""

import requests
from datetime import datetime, timedelta
import time

def scan_network(network_name, search_query, min_liquidity=2000):
    """Scan a specific network for opportunities"""
    try:
        url = f'https://api.dexscreener.com/latest/dex/search?q={search_query}'
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return []

        data = response.json()
        pairs = data.get('pairs', [])

        opportunities = []

        for pair in pairs[:50]:  # Check first 50 per network
            try:
                base_token = pair.get('baseToken', {})
                symbol = base_token.get('symbol', '???')
                name = base_token.get('name', 'Unknown')

                # Basic filters
                liquidity = pair.get('liquidity', {}).get('usd', 0)
                market_cap = pair.get('marketCap', 0)
                volume_24h = pair.get('volume', {}).get('h24', 0)

                if liquidity < min_liquidity:
                    continue

                # Volume analysis
                volume_data = pair.get('volume', {})
                h1 = volume_data.get('h1', 0)
                m5 = volume_data.get('m5', 0)

                # Momentum calculation
                momentum_score = 0
                if volume_24h > 1000:
                    momentum_score += 1
                if h1 > 100:
                    momentum_score += 2
                if m5 > 50:
                    momentum_score += 2
                if market_cap and 1000 < market_cap < 100000:
                    momentum_score += 1

                # Risk assessment
                risk_flags = []
                if liquidity < 5000:
                    risk_flags.append("LowLiq")
                if market_cap and market_cap < 5000:
                    risk_flags.append("MicroCap")
                if h1 > 0 and volume_24h > 0 and h1 > volume_24h * 0.5:
                    risk_flags.append("Spike")

                opportunities.append({
                    'network': network_name,
                    'symbol': symbol,
                    'name': name,
                    'liquidity': liquidity,
                    'market_cap': market_cap,
                    'volume_24h': volume_24h,
                    'volume_1h': h1,
                    'volume_5m': m5,
                    'momentum_score': momentum_score,
                    'risk_flags': risk_flags
                })

            except:
                continue

        return opportunities

    except Exception as e:
        print(f"❌ Error scanning {network_name}: {e}")
        return []

def main():
    print('🌍 BROAD MARKET SCANNER')
    print('=' * 40)
    print('Scanning multiple networks for opportunities...')
    print()

    # Networks to scan
    networks = [
        ('Ethereum', 'ethereum'),
        ('Base', 'base'),
        ('Arbitrum', 'arbitrum'),
        ('Optimism', 'optimism'),
        ('Polygon', 'polygon'),
        ('BSC', 'bsc'),
        ('Avalanche', 'avalanche')
    ]

    all_opportunities = []
    network_summaries = {}

    for network_name, search_query in networks:
        print(f'📡 Scanning {network_name}...')
        opportunities = scan_network(network_name, search_query)
        all_opportunities.extend(opportunities)

        # Network summary
        genuine = len([o for o in opportunities if o['momentum_score'] >= 4 and len(o['risk_flags']) == 0])
        risky = len([o for o in opportunities if len(o['risk_flags']) > 0])

        network_summaries[network_name] = {
            'total': len(opportunities),
            'genuine': genuine,
            'risky': risky
        }

        print(f'   Found {len(opportunities)} pairs ({genuine} genuine, {risky} risky)')

    print()
    print('📊 NETWORK SUMMARY:')
    print('-' * 20)
    for network, stats in network_summaries.items():
        status = '🟢' if stats['genuine'] > stats['risky'] else '🟡' if stats['genuine'] > 0 else '🔴'
        print(f'{status} {network}: {stats["total"]} total, {stats["genuine"]} genuine, {stats["risky"]} risky')

    # Find best opportunities across all networks
    genuine_opportunities = [o for o in all_opportunities if o['momentum_score'] >= 4 and len(o['risk_flags']) == 0]

    print()
    if genuine_opportunities:
        print('🚀 TOP GENUINE OPPORTUNITIES ACROSS ALL NETWORKS:')
        print('-' * 50)

        # Sort by momentum score
        sorted_opps = sorted(genuine_opportunities, key=lambda x: x['momentum_score'], reverse=True)

        for opp in sorted_opps[:10]:  # Top 10
            print(f'🌐 {opp["network"]} - {opp["symbol"]} ({opp["name"][:15]})')
            print(f'   ⚡ Momentum: {opp["momentum_score"]}/6')
            print(f'   💰 MC: ${opp["market_cap"]:,.0f} | 💧 Liq: ${opp["liquidity"]:,.0f}')
            print(f'   📊 24h: ${opp["volume_24h"]:,.0f} | 1h: ${opp["volume_1h"]:,.0f} | 5m: ${opp["volume_5m"]:,.0f}')
            print()

        # Best network recommendation
        network_scores = {}
        for opp in genuine_opportunities:
            network = opp['network']
            network_scores[network] = network_scores.get(network, 0) + opp['momentum_score']

        best_network = max(network_scores.items(), key=lambda x: x[1]) if network_scores else None

        if best_network:
            print(f'🎯 BEST NETWORK RIGHT NOW: {best_network[0]} (Score: {best_network[1]})')

    else:
        print('⚠️ NO GENUINE OPPORTUNITIES FOUND')
        print('   - All networks showing high risk or low activity')
        print('   - Consider waiting for better market conditions')

    # Market sentiment analysis
    total_pairs = len(all_opportunities)
    genuine_count = len(genuine_opportunities)
    risky_count = len([o for o in all_opportunities if len(o['risk_flags']) > 0])

    print()
    print('💡 MARKET SENTIMENT ANALYSIS:')
    print('-' * 30)

    if genuine_count > risky_count * 1.5:
        print('🟢 BULLISH: More genuine opportunities than risks')
    elif genuine_count > risky_count * 0.5:
        print('🟡 NEUTRAL: Balanced risk/reward across networks')
    else:
        print('🔴 BEARISH: High risk environment across markets')

    print(f'📊 Total pairs scanned: {total_pairs}')
    print(f'✅ Genuine opportunities: {genuine_count}')
    print(f'⚠️ Risky tokens: {risky_count}')

    print()
    print('🎯 TRADING RECOMMENDATION:')
    if genuine_opportunities:
        print('• Focus on top opportunities above')
        print('• Start with small positions ($2-3)')
        print('• Monitor momentum closely')
        print('• Use stop losses on all trades')
    else:
        print('• Wait for genuine momentum to develop')
        print('• Avoid trading in current high-risk environment')
        print('• Monitor scanner daily for opportunities')

if __name__ == '__main__':
    main()
