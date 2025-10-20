#!/usr/bin/env python3
"""
Find tradable tokens on Base chain for aggressive daily profit trading
"""

import requests
from datetime import datetime

print('🔍 Finding Best Tokens on Base Chain for Daily Profit Trading')
print('=' * 70)
print(f'📅 Analysis Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}')
print()

def get_top_tokens_base():
    """Get top tokens by market cap on Base chain"""
    print('📊 1. TOP TOKENS BY MARKET CAP ON BASE')
    print('-' * 50)

    try:
        # Get top tokens from DexScreener (Base chain)
        url = "https://api.dexscreener.com/latest/dex/tokens"
        params = {
            'chainIds': 'base',
            'limit': 50
        }

        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            pairs = data.get('pairs', [])

            # Filter for high volume pairs
            high_volume_pairs = [p for p in pairs if p.get('volume', {}).get('h24', 0) > 10000]  # >$10k volume

            # Sort by 24h volume
            high_volume_pairs.sort(key=lambda x: x.get('volume', {}).get('h24', 0), reverse=True)

            print('✅ High Volume Tokens on Base Chain:')
            print()

            for i, pair in enumerate(high_volume_pairs[:20], 1):  # Top 20
                base_token = pair.get('baseToken', {})
                quote_token = pair.get('quoteToken', {})

                token_symbol = base_token.get('symbol', 'Unknown')
                token_name = base_token.get('name', 'Unknown')
                token_address = base_token.get('address', 'Unknown')

                price_usd = pair.get('priceUsd', '0')
                volume_24h = pair.get('volume', {}).get('h24', 0)
                price_change_24h = pair.get('priceChange', {}).get('h24', 0)

                # Skip if not a real token or stable coins
                if token_symbol in ['WETH', 'USDC', 'USDT', 'DAI', 'cbETH'] or 'USD' in token_symbol:
                    continue

                print(f'{i:2d}. {token_symbol:<8} | ${float(price_usd):>8.4f} | 24h Vol: ${volume_24h:>10,.0f} | Change: {price_change_24h:>+6.1f}%')
                print(f'    Name: {token_name}')
                print(f'    Contract: {token_address}')
                print()

            return high_volume_pairs[:20]

    except Exception as e:
        print(f'❌ Failed to get top tokens: {e}')
        return []

def analyze_trading_opportunities(pairs):
    """Analyze which tokens are good for daily profit trading"""
    print('🎯 2. TRADING OPPORTUNITIES ANALYSIS')
    print('-' * 50)

    opportunities = []

    for pair in pairs:
        base_token = pair.get('baseToken', {})
        token_symbol = base_token.get('symbol', 'Unknown')

        # Skip stable coins and wrapped tokens
        if token_symbol in ['WETH', 'USDC', 'USDT', 'DAI', 'cbETH'] or 'USD' in token_symbol:
            continue

        price_change_24h = pair.get('priceChange', {}).get('h24', 0)
        volume_24h = pair.get('volume', {}).get('h24', 0)
        price_usd = float(pair.get('priceUsd', '0'))

        # Calculate volatility score (price change magnitude)
        volatility_score = abs(price_change_24h)

        # Calculate liquidity score (volume relative to market cap)
        market_cap = price_usd * pair.get('marketCap', 0) if pair.get('marketCap') else volume_24h * 10
        liquidity_score = min(volume_24h / max(market_cap, 1), 1.0) if market_cap > 0 else 0

        # Daily profit potential score (combination of volatility and liquidity)
        profit_potential = (volatility_score * 0.6) + (liquidity_score * 0.4)

        opportunities.append({
            'symbol': token_symbol,
            'price_change_24h': price_change_24h,
            'volume_24h': volume_24h,
            'price_usd': price_usd,
            'volatility_score': volatility_score,
            'liquidity_score': liquidity_score,
            'profit_potential': profit_potential,
            'contract': base_token.get('address', 'Unknown')
        })

    # Sort by profit potential
    opportunities.sort(key=lambda x: x['profit_potential'], reverse=True)

    print('✅ Best Tokens for Daily Profit Trading:')
    print()

    for i, opp in enumerate(opportunities[:10], 1):  # Top 10
        print(f'{i}. {opp["symbol"]:<8} | Profit Potential: {opp["profit_potential"]:.1f}/10')
        print(f'   Price: ${opp["price_usd"]:.4f} | 24h Change: {opp["price_change_24h"]:+.1f}%')
        print(f'   Volume: ${opp["volume_24h"]:,.0f} | Volatility: {opp["volatility_score"]:.1f}%')
        print(f'   Contract: {opp["contract"]}')
        print()

    return opportunities[:10]

def recommend_tokens_for_bot(opportunities):
    """Recommend tokens for the aggressive daily profit bot"""
    print('🚀 3. RECOMMENDATIONS FOR AGGRESSIVE DAILY PROFIT BOT')
    print('-' * 60)

    if not opportunities:
        print('❌ No suitable tokens found for trading')
        return

    # Pick top 3 recommendations
    recommendations = opportunities[:3]

    print('✅ TOP 3 TOKENS RECOMMENDED FOR YOUR BOT:')
    print()

    for i, rec in enumerate(recommendations, 1):
        print(f'🏆 RECOMMENDATION #{i}: {rec["symbol"]}')
        print(f'   💰 Price: ${rec["price_usd"]:.4f}')
        print(f'   📈 24h Change: {rec["price_change_24h"]:+.1f}%')
        print(f'   💹 Volume: ${rec["volume_24h"]:,.0f}')
        print(f'   🎯 Profit Potential: {rec["profit_potential"]:.1f}/10')
        print(f'   📋 Contract: {rec["contract"]}')
        print()

    print('🎮 BOT CONFIGURATION SUGGESTIONS:')
    print(f'   • Trade {recommendations[0]["symbol"]} as primary token')
    print(f'   • Use ${min(10, rec["price_usd"] * 100):.0f} max position size')
    print(f'   • 3% sell gains, 2% rebuy drops (aggressive settings)')
    print(f'   • $5 ETH reserve maintained')
    print()

    return recommendations

def main():
    # Get top tokens on Base
    pairs = get_top_tokens_base()

    if pairs:
        # Analyze trading opportunities
        opportunities = analyze_trading_opportunities(pairs)

        # Make recommendations
        recommendations = recommend_tokens_for_bot(opportunities)

        print('✅ Analysis Complete!')
        print('🎯 Ready to configure bot for Base chain token trading')
        print('💡 Base offers cheap gas (~$0.50-2 per trade) vs Ethereum (~$20-50)')

    else:
        print('❌ Could not retrieve token data from Base chain')

if __name__ == '__main__':
    main()
