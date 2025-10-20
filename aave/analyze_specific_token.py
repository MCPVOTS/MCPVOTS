#!/usr/bin/env python3
"""
Analyze specific token for Base chain trading
Token: 0x1111111111166b7FE7bd91427724B487980aFc69
"""

import requests
from datetime import datetime

def analyze_token(token_address):
    """Analyze a specific token on Base chain"""
    print('🔍 Analyzing Token for Base Chain Trading')
    print('=' * 60)
    print(f'📅 Analysis Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}')
    print(f'🎯 Token Contract: {token_address}')
    print()

    try:
        # Get token info from DexScreener
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            data = response.json()
            pairs = data.get('pairs', [])

            if pairs:
                # Get the main pair (usually highest volume)
                main_pair = pairs[0]  # First pair is usually the main one

                base_token = main_pair.get('baseToken', {})
                quote_token = main_pair.get('quoteToken', {})

                token_symbol = base_token.get('symbol', 'Unknown')
                token_name = base_token.get('name', 'Unknown')

                print('📊 TOKEN INFORMATION')
                print('-' * 30)
                print(f'🏷️  Symbol: {token_symbol}')
                print(f'📝 Name: {token_name}')
                print(f'📋 Contract: {token_address}')
                print()

                # Price and market data
                price_usd = main_pair.get('priceUsd', '0')
                price_change_24h = main_pair.get('priceChange', {}).get('h24', 0)
                price_change_6h = main_pair.get('priceChange', {}).get('h6', 0)
                price_change_1h = main_pair.get('priceChange', {}).get('h1', 0)

                volume_24h = main_pair.get('volume', {}).get('h24', 0)
                volume_6h = main_pair.get('volume', {}).get('h6', 0)

                liquidity = main_pair.get('liquidity', {}).get('usd', 0)
                market_cap = main_pair.get('marketCap', 0)

                print('💰 PRICE & MARKET DATA')
                print('-' * 30)
                print(f'💵 Current Price: ${float(price_usd):.6f}')
                print(f'📈 24h Change: {price_change_24h:+.2f}%')
                print(f'📊 6h Change: {price_change_6h:+.2f}%')
                print(f'⚡ 1h Change: {price_change_1h:+.2f}%')
                print(f'💹 24h Volume: ${volume_24h:,.0f}')
                print(f'🏊 Liquidity: ${liquidity:,.0f}')
                print(f'🏢 Market Cap: ${market_cap:,.0f}' if market_cap else '🏢 Market Cap: N/A')
                print()

                # Trading analysis
                print('🎯 TRADING ANALYSIS')
                print('-' * 30)

                # Volatility assessment
                volatility_score = abs(price_change_24h)
                if volatility_score > 10:
                    volatility_level = "HIGH"
                    volatility_desc = "Very volatile - good for swing trading"
                elif volatility_score > 5:
                    volatility_level = "MEDIUM"
                    volatility_desc = "Moderate volatility - suitable for day trading"
                else:
                    volatility_level = "LOW"
                    volatility_desc = "Low volatility - better for long-term holding"

                print(f'📊 Volatility (24h): {volatility_level} ({volatility_score:.1f}%)')
                print(f'💡 Assessment: {volatility_desc}')

                # Volume assessment
                if volume_24h > 100000:  # >$100k
                    volume_level = "HIGH"
                    volume_desc = "Excellent liquidity - easy to trade"
                elif volume_24h > 10000:  # >$10k
                    volume_level = "MEDIUM"
                    volume_desc = "Good liquidity - manageable trading"
                else:
                    volume_level = "LOW"
                    volume_desc = "Low liquidity - may have slippage issues"

                print(f'💹 Volume Level: {volume_level} (${volume_24h:,.0f})')
                print(f'💡 Assessment: {volume_desc}')

                # Profit potential score (0-10)
                profit_potential = min(10, (volatility_score * 0.4) + (min(volume_24h / 100000, 1) * 6))

                print(f'🎯 Profit Potential: {profit_potential:.1f}/10')
                print()

                # Trading recommendations
                print('🚀 TRADING RECOMMENDATIONS')
                print('-' * 35)

                if profit_potential > 7:
                    print('✅ EXCELLENT for aggressive daily profit trading!')
                elif profit_potential > 5:
                    print('✅ GOOD candidate for daily profit trading')
                elif profit_potential > 3:
                    print('⚠️  MODERATE potential - consider with caution')
                else:
                    print('❌ LOW potential - not recommended for active trading')

                # Position sizing recommendations
                max_position_usd = min(10, float(price_usd) * 1000)  # Max $10 or 1000 tokens worth
                print(f'💰 Recommended Max Position: ${max_position_usd:.0f}')

                # Strategy recommendations
                if volatility_score > 8:
                    print('🎮 Strategy: Scalp trades (2-3% gains/losses)')
                    sell_gain_pct = 0.02
                    rebuy_drop_pct = 0.02
                elif volatility_score > 5:
                    print('🎮 Strategy: Day swing (3-5% gains/losses)')
                    sell_gain_pct = 0.03
                    rebuy_drop_pct = 0.03
                else:
                    print('🎮 Strategy: Position trading (5-8% gains/losses)')
                    sell_gain_pct = 0.05
                    rebuy_drop_pct = 0.04

                print(f'📈 Sell Gain Target: {sell_gain_pct*100:.0f}%')
                print(f'📉 Rebuy Drop Target: {rebuy_drop_pct*100:.0f}%')
                print()

                # Gas cost analysis
                print('⛽ GAS COST ANALYSIS (Base Chain)')
                print('-' * 35)
                print('✅ Base Chain Benefits:')
                print('   • Gas cost per trade: ~$0.50-2.00')
                print('   • Transaction time: 2-3 seconds')
                print('   • Much cheaper than Ethereum mainnet!')
                print()

                return {
                    'symbol': token_symbol,
                    'name': token_name,
                    'contract': token_address,
                    'price_usd': float(price_usd),
                    'profit_potential': profit_potential,
                    'max_position_usd': max_position_usd,
                    'sell_gain_pct': sell_gain_pct,
                    'rebuy_drop_pct': rebuy_drop_pct,
                    'volatility_score': volatility_score,
                    'volume_24h': volume_24h
                }

            else:
                print('❌ No trading pairs found for this token')
                return None

        else:
            print(f'❌ API request failed: {response.status_code}')
            return None

    except Exception as e:
        print(f'❌ Analysis failed: {e}')
        return None

def main():
    token_address = "0x1111111111166b7FE7bd91427724B487980aFc69"
    result = analyze_token(token_address)

    if result:
        print('✅ Analysis Complete!')
        print('🎯 Ready to configure bot for this token')
        print()
        print('📋 SUMMARY:')
        print(f'   Token: {result["symbol"]} ({result["name"]})')
        print(f'   Profit Potential: {result["profit_potential"]:.1f}/10')
        print(f'   Max Position: ${result["max_position_usd"]:.0f}')
        print(f'   Strategy: {result["sell_gain_pct"]*100:.0f}% gains, {result["rebuy_drop_pct"]*100:.0f}% drops')
    else:
        print('❌ Could not analyze token')

if __name__ == '__main__':
    main()
