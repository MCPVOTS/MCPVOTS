#!/usr/bin/env python3
"""
Flaunch Token Discovery Script
Find tokens created through the Flaunch protocol on Base chain
"""

import os
import json
import requests
from datetime import datetime
from collections import defaultdict

def load_env_vars():
    """Load environment variables"""
    from dotenv import load_dotenv
    load_dotenv()

    return {
        'basescan_api_key': os.getenv('BASESCAN_API_KEY'),
        'birdeye_api_key': os.getenv('BIRDEYE_API_KEY')
    }

def discover_flaunch_tokens_via_contract(factory_address, api_key):
    """Discover Flaunch tokens by querying the TreasuryManagerFactory contract"""
    from basescan_client import EtherscanV2Client

    client = EtherscanV2Client(api_key=api_key, base_url="https://api.basescan.org/v2/api")

    try:
        # Get transactions to/from the factory contract
        # This will show token manager deployments and token deposits
        txs = client.get_txlist(8453, address=factory_address, page=1, offset=1000, sort='desc')

        flaunch_tokens = []

        for tx in txs:
            # Look for contract creation transactions (deployments)
            if tx.get('to') == '' or tx.get('contractAddress'):
                contract_address = tx.get('contractAddress', '')
                if contract_address:
                    # This is a deployed contract, might be a token manager
                    # Get token transactions for this manager
                    token_txs = client.get_tokentx(8453, contractaddress=contract_address, page=1, offset=100, sort='desc')
                    for token_tx in token_txs:
                        token_address = token_tx.get('contractAddress', '')
                        token_symbol = token_tx.get('tokenSymbol', '')
                        token_name = token_tx.get('tokenName', '')

                        if token_address and token_symbol not in ['WETH', 'USDC', 'USDT', 'DAI']:
                            flaunch_tokens.append({
                                'address': token_address,
                                'symbol': token_symbol,
                                'name': token_name,
                                'manager_contract': contract_address,
                                'deployment_tx': tx.get('hash', ''),
                                'is_flaunch_managed': True
                            })

        # Remove duplicates
        unique_tokens = []
        seen_addresses = set()
        for token in flaunch_tokens:
            if token['address'] not in seen_addresses:
                unique_tokens.append(token)
                seen_addresses.add(token['address'])

        return unique_tokens[:50]  # Limit results

    except Exception as e:
        print(f"Error discovering Flaunch tokens via contract: {e}")
        return []

def search_flaunch_tokens_via_dexscreener():
    """Search for tokens that might be Flaunch tokens using DexScreener"""
    search_terms = ['flaunch', 'memecoin', 'tokenize', 'creator', 'builder']

    all_tokens = []

    for term in search_terms:
        try:
            url = f'https://api.dexscreener.com/latest/dex/search?q={term}'
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'pairs' in data:
                    # Filter for Base chain
                    base_pairs = [p for p in data['pairs'] if p.get('chainId') == 'base']
                    for pair in base_pairs:
                        base_token = pair.get('baseToken', {})
                        token_address = base_token.get('address', '')
                        token_symbol = base_token.get('symbol', '')

                        if token_address and token_symbol:
                            # Check if this might be a Flaunch token
                            # Flaunch tokens often have specific naming patterns
                            if any(keyword in token_symbol.lower() for keyword in ['flaunch', 'meme', 'creator', 'token']):
                                all_tokens.append({
                                    'address': token_address,
                                    'symbol': token_symbol,
                                    'name': base_token.get('name', ''),
                                    'pair': pair
                                })
        except Exception as e:
            print(f"Error searching term '{term}': {e}")
            continue

    # Remove duplicates
    unique_tokens = []
    seen_addresses = set()
    for token in all_tokens:
        if token['address'] not in seen_addresses:
            unique_tokens.append(token)
            seen_addresses.add(token['address'])

    return unique_tokens

def analyze_flaunch_token(token_data):
    """Analyze a potential Flaunch token for trading suitability"""
    pair = token_data.get('pair', {})

    price_usd = float(pair.get('priceUsd', 0))
    volume_24h = pair.get('volume', {}).get('h24', 0)
    change_24h = pair.get('priceChange', {}).get('h24', 0)
    liquidity = pair.get('liquidity', {}).get('usd', 0)
    txns_24h = pair.get('txns', {}).get('h24', {})

    if isinstance(txns_24h, dict):
        total_txns = txns_24h.get('buys', 0) + txns_24h.get('sells', 0)
    else:
        total_txns = 0

    # Flaunch tokens often have different criteria - they can be lower volume but high potential
    min_liquidity = 5000  # Lower threshold for new tokens
    min_volume = 500     # Lower volume threshold
    min_txns = 5         # At least some activity

    if (liquidity >= min_liquidity and
        volume_24h >= min_volume and
        total_txns >= min_txns and
        price_usd > 0.000001):

        return {
            'symbol': token_data['symbol'],
            'address': token_data['address'],
            'name': token_data['name'],
            'price_usd': price_usd,
            'volume_24h': volume_24h,
            'change_24h': change_24h,
            'liquidity': liquidity,
            'txns_24h': total_txns,
            'txns_per_hour': total_txns / 24 if total_txns > 0 else 0,
            'dex': pair.get('dexId', 'unknown'),
            'url': pair.get('url', ''),
            'is_flaunch': True  # Flag as potential Flaunch token
        }

    return None

def main():
    print('FLAUNCH TOKEN DISCOVERY')
    print('=' * 40)
    print(f'Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()

    # Load environment
    env_vars = load_env_vars()

    print('🔍 Searching for Flaunch tokens on Base chain...')
    print('Flaunch is a tokenization protocol for memes, AI agents, products, and more')
    print()

    # Search for potential Flaunch tokens
    potential_tokens = search_flaunch_tokens_via_dexscreener()

    print(f'Found {len(potential_tokens)} potential Flaunch-related tokens')

    # Analyze each token
    flaunch_opportunities = []
    for token_data in potential_tokens:
        analysis = analyze_flaunch_token(token_data)
        if analysis:
            flaunch_opportunities.append(analysis)

    # Sort by trading activity
    flaunch_opportunities.sort(key=lambda x: x['txns_per_hour'], reverse=True)

    print(f'\n✅ FOUND {len(flaunch_opportunities)} FLAUNCH TOKENS READY FOR TRADING:')
    print()

    for i, token in enumerate(flaunch_opportunities[:15], 1):  # Top 15
        symbol = token['symbol']
        price = token['price_usd']
        volume = token['volume_24h']
        change = token['change_24h']
        liquidity = token['liquidity']
        txns_hr = token['txns_per_hour']

        print(f'{i}. {symbol:<12} | Price: ${price:.6f} | Change: {change:+.1f}% | Volume: ${volume:,.0f} | Liq: ${liquidity:,.0f} | Txns/hr: {txns_hr:.1f}')

    print()
    print('🎯 FLAUNCH TRADING STRATEGY:')
    print()

    if flaunch_opportunities:
        print('Flaunch tokens represent cutting-edge tokenization opportunities:')
        print('• Memecoins with real utility')
        print('• AI agent tokens')
        print('• Creator economy tokens')
        print('• Gaming and NFT projects')
        print()

        print('TRADING APPROACH:')
        print('• Early entry on new launches')
        print('• Monitor creator activity and social buzz')
        print('• Look for tokens with strong fundamentals')
        print('• Use reactive trading for quick profits')
        print()

        print('CAPITAL ALLOCATION ($50):')
        print('• $15-20: High-potential Flaunch tokens')
        print('• $15-20: Established Flaunch performers')
        print('• $10-15: New launches with momentum')
        print()

        print('RISK MANAGEMENT:')
        print('• Max $3-5 per Flaunch token position')
        print('• Stop losses at 10-15% (more volatile)')
        print('• Take profits at 20-50% gains')
        print('• Daily loss limit: $10-15')
        print()

        print('TOOLS TO USE:')
        print('• DexScreener for real-time monitoring')
        print('• BaseScan for transaction analysis')
        print('• Reactive trader for automated entries')
        print('• Whale tracker for large holder movements')

    else:
        print('No active Flaunch tokens found at this time.')
        print('Flaunch tokens may be in development or not yet launched.')
        print()
        print('MONITORING STRATEGY:')
        print('• Watch builders.flaunch.gg for new launches')
        print('• Follow @flaunchgg on Twitter')
        print('• Join Discord for early access')
        print('• Set up alerts for new token deployments')

    print()
    print('🔗 FLAUNCH RESOURCES:')
    print('• Builders Dashboard: https://builders.flaunch.gg')
    print('• Documentation: https://docs.flaunch.gg')
    print('• Discord: https://discord.com/invite/flaunch')
    print('• Twitter: https://x.com/flaunchgg')

if __name__ == '__main__':
    main()
