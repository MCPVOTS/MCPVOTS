#!/usr/bin/env python3
"""
Base Chain Token Discovery Script
Finds active tokens on Base chain for trading opportunities
"""

import requests
import json
import time
from datetime import datetime

def get_known_base_tokens():
    """Get known active tokens on Base chain"""
    known_tokens = [
        '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467',  # MAXX
        '0x4ed4e862860bed51a9570b96d89af5e1b0efefeed',  # DEGEN
        # Add more known tokens
    ]
    return known_tokens

def get_dexscreener_trending_pairs(chain='base', limit=50):
    """Get trending pairs from DexScreener"""
    # Try multiple search terms to find active tokens
    search_terms = ['base', 'defi']  # Reduced for speed

    all_pairs = []

    for term in search_terms:
        try:
            url = f'https://api.dexscreener.com/latest/dex/search?q={term}'
            print(f"Trying search term: {term}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'pairs' in data:
                    # Filter for Base chain only
                    base_pairs = [p for p in data['pairs'] if p.get('chainId') == 'base']
                    all_pairs.extend(base_pairs)
                    print(f"Found {len(base_pairs)} Base pairs for '{term}'")
        except Exception as e:
            print(f"Error with term '{term}': {e}")
            continue

        time.sleep(0.2)  # Rate limiting

    # Remove duplicates based on pair address
    unique_pairs = []
    seen_addresses = set()
    for pair in all_pairs:
        address = pair.get('pairAddress', '')
        if address not in seen_addresses:
            unique_pairs.append(pair)
            seen_addresses.add(address)

    return {'pairs': unique_pairs[:limit]} if unique_pairs else None
    # Try multiple search terms to find active tokens
    search_terms = ['base', 'defi']  # Reduced for speed

    all_pairs = []

    for term in search_terms:
        try:
            url = f'https://api.dexscreener.com/latest/dex/search?q={term}'
            print(f"Trying search term: {term}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'pairs' in data:
                    # Filter for Base chain only
                    base_pairs = [p for p in data['pairs'] if p.get('chainId') == 'base']
                    all_pairs.extend(base_pairs)
                    print(f"Found {len(base_pairs)} Base pairs for '{term}'")
        except Exception as e:
            print(f"Error with term '{term}': {e}")
            continue

        time.sleep(0.2)  # Rate limiting

    # Remove duplicates based on pair address
    unique_pairs = []
    seen_addresses = set()
    for pair in all_pairs:
        address = pair.get('pairAddress', '')
        if address not in seen_addresses:
            unique_pairs.append(pair)
            seen_addresses.add(address)

    return {'pairs': unique_pairs[:limit]} if unique_pairs else None

def analyze_token_for_trading(token_data):
    """Analyze if a token is suitable for high-frequency trading"""
    if not token_data or 'pairs' not in token_data:
        return None

    # Focus on the most liquid pair for each token
    pairs = token_data['pairs']
    if not pairs:
        return None

    # Prioritize Uniswap V4 pairs
    uniswap_v4_pairs = [p for p in pairs if p.get('dexId') == 'uniswap']
    if uniswap_v4_pairs:
        pairs = uniswap_v4_pairs

    # Sort by liquidity
    pairs.sort(key=lambda x: float(x.get('liquidity', {}).get('usd', 0)), reverse=True)
    pair = pairs[0]

    base_token = pair.get('baseToken', {})
    symbol = base_token.get('symbol', 'UNKNOWN')
    address = base_token.get('address', '')

    # Skip if it's a stablecoin or major token
    skip_symbols = ['WETH', 'USDC', 'USDT', 'DAI', 'WBTC', 'ETH']
    if symbol in skip_symbols:
        return None

    price_usd = float(pair.get('priceUsd', 0))
    volume_24h = pair.get('volume', {}).get('h24', 0)
    change_24h = pair.get('priceChange', {}).get('h24', 0)
    liquidity = pair.get('liquidity', {}).get('usd', 0)
    txns_24h = pair.get('txns', {}).get('h24', {})

    if isinstance(txns_24h, dict):
        total_txns = txns_24h.get('buys', 0) + txns_24h.get('sells', 0)
    else:
        total_txns = 0

    # Criteria for high-frequency trading
    min_liquidity = 10000  # $10k minimum
    min_volume = 1000     # $1k daily volume minimum
    min_txns = 10         # At least 10 transactions per day

    if (liquidity >= min_liquidity and
        volume_24h >= min_volume and
        total_txns >= min_txns and
        price_usd > 0.000001):  # Not dust tokens

        return {
            'symbol': symbol,
            'address': address,
            'price_usd': price_usd,
            'volume_24h': volume_24h,
            'change_24h': change_24h,
            'liquidity': liquidity,
            'txns_24h': total_txns,
            'txns_per_hour': total_txns / 24 if total_txns > 0 else 0,
            'dex': pair.get('dexId', 'unknown'),
            'url': pair.get('url', '')
        }

    return None

def main():
    print('BASE CHAIN TOKEN DISCOVERY')
    print('=' * 40)
    print(f'Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()

    # Get trending pairs
    print('Fetching trending tokens from DexScreener...')
    trending_data = get_dexscreener_trending_pairs()

    # Also check known active tokens
    print('Checking known active tokens...')
    known_tokens = get_known_base_tokens()
    for address in known_tokens:
        token_url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
        try:
            response = requests.get(token_url, timeout=5)
            if response.status_code == 200:
                token_data = response.json()
                print(f"Fetched data for {address}: {len(token_data.get('pairs', []))} pairs")
                if 'pairs' in token_data:
                    # Add to trending_data
                    if trending_data and 'pairs' in trending_data:
                        trending_data['pairs'].extend(token_data['pairs'])
                    else:
                        trending_data = token_data
            else:
                print(f"Failed to fetch {address}: {response.status_code}")
        except Exception as e:
            print(f"Error fetching known token {address}: {e}")
            continue

        time.sleep(0.1)

    if not trending_data or 'pairs' not in trending_data:
        print('Failed to fetch trending data')
        return

    pairs = trending_data['pairs']
    print(f'Found {len(pairs)} trending pairs')

    # Debug: print some pairs
    for i, pair in enumerate(pairs[:5]):
        base_token = pair.get('baseToken', {})
        symbol = base_token.get('symbol', 'UNKNOWN')
        dex = pair.get('dexId', 'unknown')
        liquidity = pair.get('liquidity', {}).get('usd', 0)
        print(f"  {i+1}. {symbol} on {dex}, liquidity: ${liquidity}")

    # Analyze each token
    trading_opportunities = []
    analyzed_addresses = set()

    for pair in pairs:
        base_token = pair.get('baseToken', {})
        address = base_token.get('address', '')

        if address in analyzed_addresses:
            continue
        analyzed_addresses.add(address)

        print(f"Analyzing token {base_token.get('symbol', 'UNKNOWN')} at {address}")

        # Get full token data
        token_url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
        try:
            response = requests.get(token_url, timeout=5)
            if response.status_code == 200:
                token_data = response.json()
                analysis = analyze_token_for_trading(token_data)
                if analysis:
                    trading_opportunities.append(analysis)
                    print(f"Found opportunity: {analysis['symbol']}")
                else:
                    print(f"No opportunity for {base_token.get('symbol', 'UNKNOWN')}")
        except Exception as e:
            print(f"Error analyzing {address}: {e}")
            continue

        time.sleep(0.1)  # Rate limiting

    # Sort by trading activity (txns per hour)
    trading_opportunities.sort(key=lambda x: x['txns_per_hour'], reverse=True)

    print(f'\nFOUND {len(trading_opportunities)} HIGH-FREQUENCY TRADING OPPORTUNITIES:')
    print('(Prioritizing Uniswap V4 pools for Base chain)')
    print()

    for i, token in enumerate(trading_opportunities[:10], 1):  # Top 10
        symbol = token['symbol']
        price = token['price_usd']
        volume = token['volume_24h']
        change = token['change_24h']
        liquidity = token['liquidity']
        txns_hr = token['txns_per_hour']
        dex = token['dex']

        print(f'{i}. {symbol:<8} | Price: ${price:.6f} | Change: {change:+.1f}% | Volume: ${volume:,.0f} | Liq: ${liquidity:,.0f} | Txns/hr: {txns_hr:.1f} | DEX: {dex}')

    print()
    print('TRADING RECOMMENDATIONS FOR $50 CAPITAL:')
    print()

    if trading_opportunities:
        # MAXX is our primary if available
        maxx_token = next((t for t in trading_opportunities if t['symbol'] == 'MAXX'), None)

        if maxx_token:
            print('PRIMARY STRATEGY - MAXX SCALPING:')
            print(f'- Focus on {maxx_token["symbol"]} (most active)')
            print(f'- Current activity: {maxx_token["txns_per_hour"]:.1f} txns/hour')
            print('- Allocate $25-30 for scalping trades')
            print('- Target 5-10 trades per day')
            print()

        print('SECONDARY STRATEGIES:')
        print('- Allocate $10-15 for momentum trading on top 3-5 tokens')
        print('- Use reactive trader for automated entries/exits')
        print('- Monitor volume spikes for quick profits')
        print()

        print('RISK MANAGEMENT:')
        print('- Max $2-3 risk per trade')
        print('- Stop losses at 5-10% below entry')
        print('- Take profits at 3-5% gains')
        print('- Daily loss limit: $5-10')
        print()

        print('TOOLS TO USE:')
        print('- maxx_trader_fix.py: Reactive trading automation')
        print('- market_data_service.py: Real-time price monitoring')
        print('- whale_tracker.py: Follow successful traders')
        print('- strategy_optimizer.py: Performance analysis')

if __name__ == '__main__':
    main()
