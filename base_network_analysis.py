"""
BASE NETWORK DETAILED ANALYSIS
==============================

Deep dive into Base network opportunities
"""

import requests

def main():
    print('🔍 BASE NETWORK DEEP DIVE')
    print('=' * 35)

    try:
        # Get detailed Base network data
        url = 'https://api.dexscreener.com/latest/dex/search?q=base'
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            data = response.json()
            pairs = data.get('pairs', [])

            print(f'📊 Analyzing {len(pairs)} Base pairs in detail...')

            # Detailed analysis
            opportunities = []
            risky_tokens = []

            for pair in pairs:
                try:
                    base_token = pair.get('baseToken', {})
                    symbol = base_token.get('symbol', '???')
                    name = base_token.get('name', 'Unknown')

                    # Get all available data
                    liquidity = pair.get('liquidity', {}).get('usd', 0)
                    market_cap = pair.get('marketCap', 0)
                    volume_data = pair.get('volume', {})

                    h24 = volume_data.get('h24', 0)
                    h6 = volume_data.get('h6', 0)
                    h1 = volume_data.get('h1', 0)
                    m5 = volume_data.get('m5', 0)

                    # Calculate detailed metrics
                    momentum_score = 0
                    risk_level = 'LOW'
                    flags = []

                    # Liquidity assessment
                    if liquidity >= 10000:
                        momentum_score += 2
                    elif liquidity >= 5000:
                        momentum_score += 1
                    elif liquidity < 1000:
                        flags.append('Very Low Liquidity')
                        risk_level = 'HIGH'

                    # Volume consistency
                    if h24 > 0:
                        if h1 > h24 * 0.3:  # 30% of daily in 1 hour
                            flags.append('Volume Spike')
                            risk_level = 'MEDIUM'
                        elif h1 > h24 * 0.1:  # 10% of daily in 1 hour
                            momentum_score += 1

                    # 5-minute momentum
                    if m5 > 100:
                        momentum_score += 2
                    elif m5 > 50:
                        momentum_score += 1

                    # Market cap assessment
                    if market_cap:
                        if market_cap < 10000:
                            flags.append('Micro Cap')
                            risk_level = 'HIGH'
                        elif market_cap < 50000:
                            momentum_score += 1  # Sweet spot
                        elif market_cap > 1000000:
                            flags.append('Large Cap')

                    # Categorize
                    if momentum_score >= 3 and risk_level != 'HIGH':
                        opportunities.append({
                            'symbol': symbol,
                            'name': name,
                            'momentum_score': momentum_score,
                            'liquidity': liquidity,
                            'market_cap': market_cap,
                            'h24_vol': h24,
                            'h1_vol': h1,
                            'm5_vol': m5,
                            'risk_level': risk_level,
                            'flags': flags
                        })
                    elif flags:
                        risky_tokens.append({
                            'symbol': symbol,
                            'flags': flags,
                            'risk_level': risk_level
                        })

                except Exception as e:
                    continue

            print(f'✅ Analysis complete!')
            print(f'🚀 Viable Base Opportunities: {len(opportunities)}')
            print(f'⚠️ Risky Base Tokens: {len(risky_tokens)}')

            if opportunities:
                print()
                print('🎯 BASE NETWORK OPPORTUNITIES:')
                for opp in sorted(opportunities, key=lambda x: x['momentum_score'], reverse=True):
                    print(f'  {opp["symbol"]} ({opp["name"][:15]})')
                    print(f'    ⚡ Score: {opp["momentum_score"]}/5 | Risk: {opp["risk_level"]}')
                    print(f'    💰 MC: ${opp["market_cap"]:,.0f} | 💧 Liq: ${opp["liquidity"]:,.0f}')
                    print(f'    📊 24h: ${opp["h24_vol"]:,.0f} | 1h: ${opp["h1_vol"]:,.0f} | 5m: ${opp["m5_vol"]:,.0f}')
                    if opp['flags']:
                        print(f'    ⚠️ {opp["flags"]}')
                    print()
            else:
                print()
                print('❌ NO VIABLE BASE OPPORTUNITIES CURRENTLY')
                print('   - All tokens show high risk patterns')
                print('   - Consider Arbitrum for better opportunities')

            if risky_tokens:
                print('🚨 BASE RISK PATTERNS DETECTED:')
                risk_summary = {}
                for token in risky_tokens:
                    for flag in token['flags']:
                        risk_summary[flag] = risk_summary.get(flag, 0) + 1

                for flag, count in sorted(risk_summary.items(), key=lambda x: x[1], reverse=True):
                    print(f'  {flag}: {count} tokens')

        else:
            print(f'❌ API Error: {response.status_code}')

    except Exception as e:
        print(f'❌ Base analysis error: {e}')

    print()
    print('💡 BASE NETWORK VERDICT:')
    if opportunities:
        print('🟢 SOME OPPORTUNITIES EXIST - but verify carefully')
    else:
        print('🔴 HIGH RISK ENVIRONMENT - avoid Base for now')
    print('   Arbitrum showing much stronger momentum')

if __name__ == '__main__':
    main()
