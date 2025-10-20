"""
FLAUNCH MARKET RESEARCH SCRIPT
============================

Analyzes current Flaunch and Base network opportunities
"""

import requests
import time
from datetime import datetime

def main():
    print('🔍 FLAUNCH MARKET RESEARCH')
    print('=' * 50)

    # Check wallet status
    try:
        import flaunch_wallet_config as fw_config
        from web3 import Web3
        from web3.middleware import geth_poa_middleware

        w3 = Web3(Web3.HTTPProvider(fw_config.PROVIDER_URL))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        balance_wei = w3.eth.get_balance(fw_config.FLAUNCH_WALLET_ADDRESS)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        usd_balance = float(balance_eth) * 2500  # Approximate

        print(f'💰 Wallet: {balance_eth:.6f} ETH (${usd_balance:.2f})')
        print(f'🔒 Protected Reserve: ${fw_config.ETH_RESERVE_USD}')
        print(f'📊 Tradable Capital: ${usd_balance - fw_config.ETH_RESERVE_USD:.2f}')
        print()

    except Exception as e:
        print(f'❌ Wallet check failed: {e}')
        print()

    # Analyze Base network opportunities
    print('📊 BASE NETWORK ANALYSIS')
    print('-' * 25)

    try:
        # Get trending pairs on Base
        url = 'https://api.dexscreener.com/latest/dex/search?q=base'
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            data = response.json()
            pairs = data.get('pairs', [])

            print(f'✅ Found {len(pairs)} Base network pairs')

            # Analyze for opportunities with 5-min volume focus
            small_caps = []  # Under $50k market cap
            high_volume = []  # Over $5k daily volume
            momentum_tokens = []  # High 5-min volume

            for pair in pairs[:100]:  # Check first 100
                try:
                    base_token = pair.get('baseToken', {})
                    liquidity = pair.get('liquidity', {}).get('usd', 0)
                    market_cap = pair.get('marketCap', 0)
                    volume_24h = pair.get('volume', {}).get('h24', 0)

                    # Get 5-minute volume data (if available)
                    volume_5m = 0
                    try:
                        # Try to get recent volume data
                        volume_5m = pair.get('volume', {}).get('m5', 0)
                        if not volume_5m:
                            # Estimate from hourly if 5min not available
                            volume_1h = pair.get('volume', {}).get('h1', 0)
                            volume_5m = volume_1h / 12  # Rough estimate
                    except:
                        volume_5m = volume_24h / 288  # Very rough daily to 5min

                    # Small cap opportunities with momentum check
                    if market_cap and 1000 < market_cap < 50000 and liquidity > 2000:
                        momentum_score = 0
                        if volume_5m > 100: momentum_score += 3  # Strong 5min volume
                        elif volume_5m > 50: momentum_score += 2
                        elif volume_5m > 10: momentum_score += 1

                        if volume_24h > 1000: momentum_score += 2  # Good daily volume
                        elif volume_24h > 500: momentum_score += 1

                        if momentum_score >= 3:  # Good momentum
                            small_caps.append({
                                'symbol': base_token.get('symbol', '???'),
                                'name': base_token.get('name', 'Unknown')[:20],
                                'market_cap': market_cap,
                                'liquidity': liquidity,
                                'volume_24h': volume_24h,
                                'volume_5m': volume_5m,
                                'momentum_score': momentum_score
                            })

                    # High volume trending with momentum
                    if volume_24h and volume_24h > 5000 and volume_5m > 50:
                        high_volume.append({
                            'symbol': base_token.get('symbol', '???'),
                            'volume_24h': volume_24h,
                            'volume_5m': volume_5m,
                            'market_cap': market_cap
                        })

                    # Pure momentum tokens (high 5-min volume)
                    if volume_5m > 200 and market_cap and market_cap < 100000:
                        momentum_tokens.append({
                            'symbol': base_token.get('symbol', '???'),
                            'volume_5m': volume_5m,
                            'volume_24h': volume_24h,
                            'market_cap': market_cap,
                            'liquidity': liquidity
                        })

                except Exception as e:
                    continue

            print(f'🚀 Small Cap with Momentum: {len(small_caps)}')
            print(f'📈 High Volume Trending: {len(high_volume)}')
            print(f'⚡ Pure Momentum (5min): {len(momentum_tokens)}')

            # Show top opportunities with momentum focus
            if momentum_tokens:
                print()
                print('⚡ PURE MOMENTUM TOKENS (High 5-min Volume):')
                for token in sorted(momentum_tokens, key=lambda x: x['volume_5m'], reverse=True)[:3]:
                    print(f'  {token["symbol"]}')
                    print(f'    📊 5min Vol: ${token["volume_5m"]:,.0f} | 24h Vol: ${token["volume_24h"]:,.0f}')
                    print(f'    💰 MC: ${token["market_cap"]:,.0f} | 💧 Liq: ${token["liquidity"]:,.0f}')
                    print()

            if small_caps:
                print()
                print('🎯 SMALL CAP WITH MOMENTUM:')
                for opp in sorted(small_caps, key=lambda x: x['momentum_score'], reverse=True)[:3]:
                    print(f'  {opp["symbol"]} ({opp["name"]})')
                    print(f'    💰 MC: ${opp["market_cap"]:,.0f} | 💧 Liq: ${opp["liquidity"]:,.0f}')
                    print(f'    📊 5min: ${opp["volume_5m"]:,.0f} | 24h: ${opp["volume_24h"]:,.0f}')
                    print(f'    ⚡ Momentum Score: {opp["momentum_score"]}/5')
                    print()

            if high_volume:
                print('🔥 HIGH VOLUME TRENDING:')
                for trend in sorted(high_volume, key=lambda x: x['volume_5m'], reverse=True)[:3]:
                    mc = f'${trend["market_cap"]:,.0f}' if trend["market_cap"] else 'N/A'
                    print(f'  {trend["symbol"]}: 5min ${trend["volume_5m"]:,.0f} | 24h ${trend["volume_24h"]:,.0f} | MC: {mc}')

        else:
            print(f'❌ DexScreener error: {response.status_code}')

    except Exception as e:
        print(f'❌ Analysis error: {e}')

    print()
    print('💡 MOMENTUM-FOCUSED RESEARCH:')
    print('• 5-minute volume shows real-time momentum')
    print('• High 5min + 24h volume = genuine interest')
    print('• Avoid tokens with volume drops (honey pots)')
    print('• Small caps with momentum = best risk/reward')

    print()
    print('🛡️ ANTI-HONEY POT STRATEGY:')
    print('• Only trade tokens with consistent volume')
    print('• Check 5min volume > $100 for momentum')
    print('• Verify liquidity > $2k for safety')
    print('• Monitor volume trends before entry')

    print()
    print('🎯 RECOMMENDED STRATEGY:')
    print('• Focus on pure momentum tokens first')
    print('• Start with $2-3 trades to test momentum')
    print('• Exit quickly on volume drops (red flag)')
    print('• Scale up only with proven momentum')

if __name__ == '__main__':
    main()
