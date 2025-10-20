"""
MOMENTUM SCANNER
================

Scans for tokens with genuine momentum to avoid honey pots
"""

import requests
from datetime import datetime

def main():
    print('🔍 MOMENTUM SCANNER - ANTI HONEY POT')
    print('=' * 45)

    try:
        # Get Base network pairs via search
        url = 'https://api.dexscreener.com/latest/dex/search?q=base'
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            data = response.json()
            pairs = data.get('pairs', [])

            print(f'📊 Scanning {len(pairs)} Base network pairs...')

            momentum_tokens = []
            suspicious_tokens = []

            for pair in pairs:
                try:
                    base_token = pair.get('baseToken', {})
                    symbol = base_token.get('symbol', '???')
                    name = base_token.get('name', 'Unknown')

                    # Volume analysis
                    volume_data = pair.get('volume', {})
                    h24 = volume_data.get('h24', 0)
                    h6 = volume_data.get('h6', 0)
                    h1 = volume_data.get('h1', 0)
                    m5 = volume_data.get('m5', 0)

                    # Liquidity and market data
                    liquidity = pair.get('liquidity', {}).get('usd', 0)
                    market_cap = pair.get('marketCap', 0)

                    # Calculate momentum indicators
                    momentum_score = 0
                    risk_flags = []

                    # Volume consistency check
                    if h24 > 0 and h1 > 0:
                        hourly_avg = h24 / 24
                        momentum_ratio = h1 / hourly_avg

                        if momentum_ratio > 3:
                            momentum_score += 3  # Strong momentum
                        elif momentum_ratio > 2:
                            momentum_score += 2  # Good momentum
                        elif momentum_ratio > 1.5:
                            momentum_score += 1  # Mild momentum

                    # 5-minute volume check
                    if m5 > 200:
                        momentum_score += 2
                    elif m5 > 100:
                        momentum_score += 1

                    # Liquidity check
                    if liquidity < 1000:
                        risk_flags.append("Low liquidity")
                    elif liquidity > 10000:
                        momentum_score += 1  # Established liquidity

                    # Market cap check
                    if market_cap and market_cap < 10000:
                        risk_flags.append("Very small cap")
                    elif market_cap and market_cap < 50000:
                        momentum_score += 1  # Sweet spot

                    # Suspicious pattern detection
                    if h1 > 0 and h6 > 0 and h24 > 0:
                        if h1 > h6 * 0.8 and h6 < h24 * 0.3:
                            risk_flags.append("Volume spike then drop")
                        if m5 > h1 * 0.5:
                            risk_flags.append("Artificial 5min pump")

                    # Categorize token
                    if momentum_score >= 4 and len(risk_flags) == 0:
                        momentum_tokens.append({
                            'symbol': symbol,
                            'name': name,
                            'momentum_score': momentum_score,
                            'h1_volume': h1,
                            'h24_volume': h24,
                            'm5_volume': m5,
                            'liquidity': liquidity,
                            'market_cap': market_cap,
                            'risk_flags': risk_flags
                        })
                    elif len(risk_flags) > 0:
                        suspicious_tokens.append({
                            'symbol': symbol,
                            'risk_flags': risk_flags,
                            'momentum_score': momentum_score
                        })

                except Exception as e:
                    continue

            # Results
            print(f'✅ Analysis complete!')
            print(f'⚡ Genuine Momentum Tokens: {len(momentum_tokens)}')
            print(f'🚨 Suspicious Tokens: {len(suspicious_tokens)}')

            # Show momentum opportunities
            if momentum_tokens:
                print()
                print('🚀 GENUINE MOMENTUM OPPORTUNITIES:')
                for token in sorted(momentum_tokens, key=lambda x: x['momentum_score'], reverse=True):
                    print(f'  {token["symbol"]} ({token["name"][:15]})')
                    print(f'    ⚡ Score: {token["momentum_score"]}/7')
                    print(f'    📊 1h: ${token["h1_volume"]:,.0f} | 5m: ${token["m5_volume"]:,.0f}')
                    print(f'    💰 MC: ${token["market_cap"]:,.0f} | 💧 Liq: ${token["liquidity"]:,.0f}')
                    if token["risk_flags"]:
                        print(f'    ⚠️  Flags: {", ".join(token["risk_flags"])}')
                    print()

            # Show suspicious tokens (educational)
            if suspicious_tokens:
                print('🚨 SUSPICIOUS PATTERNS DETECTED:')
                for token in suspicious_tokens[:3]:
                    print(f'  {token["symbol"]}: {", ".join(token["risk_flags"])}')

            # Market assessment
            print()
            if len(momentum_tokens) > 0:
                print('💡 MARKET STATUS: ACTIVE')
                print('   Genuine opportunities available!')
            elif len(suspicious_tokens) > len(momentum_tokens) * 2:
                print('💡 MARKET STATUS: RISKY')
                print('   Many suspicious patterns - exercise caution')
            else:
                print('💡 MARKET STATUS: CONSOLIDATING')
                print('   Wait for genuine momentum to develop')

        else:
            print(f'❌ API Error: {response.status_code}')

    except Exception as e:
        print(f'❌ Scanner error: {e}')

    print()
    print('🛡️ HONEY POT AVOIDANCE:')
    print('• Only trade tokens with momentum_score >= 4')
    print('• Zero risk flags required')
    print('• Consistent volume across timeframes')
    print('• Established liquidity preferred')

if __name__ == '__main__':
    main()
