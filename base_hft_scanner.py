#!/usr/bin/env python3
"""
BASE CHAIN HFT OPPORTUNITIES SCANNER
Finds the most traded tokens on Base chain suitable for high-frequency trading
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header():
    print('🚀 BASE CHAIN HFT OPPORTUNITIES SCANNER')
    print('=' * 70)
    print(f'📅 Analysis Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}')
    print('🎯 Focus: High-volume tokens suitable for HFT strategies')
    print()

def get_dexscreener_trending_pairs():
    """Get trending pairs from DexScreener"""
    print('📈 1. DEXSCREENER TRENDING PAIRS')
    print('-' * 50)

    try:
        # Use search endpoint for trending tokens
        trending_terms = ['meme', 'ai', 'defi', 'gaming', 'nft']

        all_trending_pairs = []
        for term in trending_terms:
            try:
                url = f'https://api.dexscreener.com/latest/dex/search?q={term}'
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    if 'pairs' in data:
                        base_pairs = [p for p in data['pairs'] if p.get('chainId') == 'base']
                        all_trending_pairs.extend(base_pairs[:3])  # Limit per search

            except Exception as e:
                continue

        # Remove duplicates and sort by volume
        seen_addresses = set()
        unique_pairs = []
        for pair in all_trending_pairs:
            addr = pair.get('baseToken', {}).get('address')
            if addr and addr not in seen_addresses:
                seen_addresses.add(addr)
                unique_pairs.append(pair)

        sorted_pairs = sorted(unique_pairs, key=lambda x: x.get('volume', {}).get('h24', 0), reverse=True)

        hft_candidates = []
        for i, pair in enumerate(sorted_pairs[:15], 1):  # Top 15 by volume
            base_token = pair.get('baseToken', {})

            token_data = {
                'rank': i,
                'symbol': base_token.get('symbol', ''),
                'name': base_token.get('name', ''),
                'address': base_token.get('address', ''),
                'price': pair.get('priceUsd', 0),
                'volume_24h': pair.get('volume', {}).get('h24', 0),
                'liquidity': pair.get('liquidity', {}).get('usd', 0),
                'price_change_24h': pair.get('priceChange', {}).get('h24', 0),
                'pair_address': pair.get('pairAddress'),
                'dex': pair.get('dexId'),
                'market_cap': pair.get('marketCap', 0),
                'fdv': pair.get('fdv', 0)
            }

            hft_candidates.append(token_data)

            # Print top 10
            if i <= 10:
                print(f'{i:2d}. {token_data["symbol"]:<8} | ${float(token_data["price"]):>10.6f} | Vol: ${token_data["volume_24h"]:>8,.0f} | Liq: ${token_data["liquidity"]:>8,.0f}')

        print(f'✅ Found {len(hft_candidates)} trending pairs on Base')
        print()
        return hft_candidates

    except Exception as e:
        print(f'❌ Trending pairs analysis failed: {e}')
        print()
        return []

def get_dexscreener_search_pairs():
    """Search for popular tokens on Base"""
    print('🔍 2. POPULAR TOKEN SEARCH')
    print('-' * 50)

    try:
        # Search for popular trading pairs
        search_terms = ['WETH', 'USDC', 'USDT', 'WBTC', 'PEPE', 'SHIB', 'UNI', 'AAVE', 'COMP']

        all_pairs = []
        for term in search_terms:
            try:
                url = f'https://api.dexscreener.com/latest/dex/search?q={term}'
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    if 'pairs' in data:
                        base_pairs = [p for p in data['pairs'] if p.get('chainId') == 'base']
                        all_pairs.extend(base_pairs[:2])  # Limit per search

            except Exception as e:
                continue

        # Remove duplicates and sort by volume
        seen_addresses = set()
        unique_pairs = []
        for pair in all_pairs:
            addr = pair.get('baseToken', {}).get('address')
            if addr and addr not in seen_addresses:
                seen_addresses.add(addr)
                unique_pairs.append(pair)

        sorted_pairs = sorted(unique_pairs, key=lambda x: x.get('volume', {}).get('h24', 0), reverse=True)

        popular_tokens = []
        for i, pair in enumerate(sorted_pairs[:15], 1):
            base_token = pair.get('baseToken', {})

            token_data = {
                'rank': i,
                'symbol': base_token.get('symbol', ''),
                'name': base_token.get('name', ''),
                'address': base_token.get('address', ''),
                'price': pair.get('priceUsd', 0),
                'volume_24h': pair.get('volume', {}).get('h24', 0),
                'liquidity': pair.get('liquidity', {}).get('usd', 0),
                'price_change_24h': pair.get('priceChange', {}).get('h24', 0),
                'pair_address': pair.get('pairAddress'),
                'dex': pair.get('dexId'),
                'market_cap': pair.get('marketCap', 0)
            }

            popular_tokens.append(token_data)

            if i <= 10:
                print(f'{i:2d}. {token_data["symbol"]:<8} | ${float(token_data["price"]):>10.6f} | Vol: ${token_data["volume_24h"]:>8,.0f} | Liq: ${token_data["liquidity"]:>8,.0f}')

        print()
        return popular_tokens

    except Exception as e:
        print(f'❌ Popular token search failed: {e}')
        print()
        return []

def analyze_hft_potential(tokens):
    """Analyze HFT potential for each token"""
    print('🎯 3. HFT POTENTIAL ANALYSIS')
    print('-' * 50)

    hft_opportunities = []

    for token in tokens:
        try:
            # Get detailed pair information
            pair_address = token.get('pair_address')
            if not pair_address:
                continue

            pair_url = f'https://api.dexscreener.com/latest/dex/pairs/base/{pair_address}'
            response = requests.get(pair_url, timeout=10)

            if response.status_code == 200:
                pair_data = response.json()
                pair_info = pair_data.get('pair', {})

                # Calculate HFT metrics
                volume_24h = token.get('volume_24h', 0)
                liquidity = token.get('liquidity', 0)
                price_change_24h = token.get('price_change_24h', 0)

                # Volume to liquidity ratio (higher = more active trading)
                volume_liquidity_ratio = volume_24h / liquidity if liquidity > 0 else 0

                # Price volatility (absolute change)
                volatility = abs(price_change_24h)

                # Transaction frequency from pair data
                txns = pair_info.get('txns', {})
                h24_txns = txns.get('h24', {})
                total_txns_24h = h24_txns.get('buys', 0) + h24_txns.get('sells', 0)

                # HFT Score calculation
                # Factors: volume, liquidity, volatility, transaction frequency
                volume_score = min(volume_24h / 10000, 10)  # Cap at 10k volume
                liquidity_score = min(liquidity / 50000, 10)  # Cap at 50k liquidity
                volatility_score = min(volatility * 2, 10)  # Scale volatility
                txn_score = min(total_txns_24h / 10, 10)  # Scale transactions

                hft_score = (volume_score + liquidity_score + volatility_score + txn_score) / 4

                token['hft_score'] = hft_score
                token['volume_liquidity_ratio'] = volume_liquidity_ratio
                token['total_txns_24h'] = total_txns_24h
                token['volatility'] = volatility

                hft_opportunities.append(token)

        except Exception as e:
            continue

    # Sort by HFT score
    hft_opportunities.sort(key=lambda x: x.get('hft_score', 0), reverse=True)

    print('🏆 TOP HFT OPPORTUNITIES (by HFT Score):')
    print()

    for i, token in enumerate(hft_opportunities[:10], 1):
        score = token.get('hft_score', 0)
        volume = token.get('volume_24h', 0)
        liquidity = token.get('liquidity', 0)
        txns = token.get('total_txns_24h', 0)
        volatility = token.get('volatility', 0)

        print(f'{i}. {token["symbol"]:<8} | Score: {score:.1f}/10')
        print(f'   Price: ${float(token["price"]):.6f} | 24h Change: {token["price_change_24h"]:+.1f}%')
        print(f'   Volume: ${volume:,.0f} | Liquidity: ${liquidity:,.0f} | TXs: {txns}')
        print(f'   Vol/Liq Ratio: {token.get("volume_liquidity_ratio", 0):.3f} | Volatility: {volatility:.1f}%')
        print()

    return hft_opportunities

def get_birdeye_volume_data():
    """Get volume data from Birdeye for comparison"""
    print('🦅 4. BIRDEYE VOLUME COMPARISON')
    print('-' * 50)

    try:
        # Try V2 endpoint which might work
        url = 'https://public-api.birdeye.so/defi/token_list?chain=base&limit=50'
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            data = response.json()
            tokens = data.get('data', {}).get('tokens', [])

            # Sort by volume
            sorted_tokens = sorted(tokens, key=lambda x: x.get('volume_24h', 0), reverse=True)

            print('✅ Birdeye top volume tokens on Base:')
            for i, token in enumerate(sorted_tokens[:5], 1):
                print(f'{i}. {token.get("symbol", ""):<8} | Vol: ${token.get("volume_24h", 0):,.0f} | MC: ${token.get("market_cap", 0):,.0f}')

            print()
            return sorted_tokens

    except Exception as e:
        print(f'❌ Birdeye volume data failed: {e}')
        print()
        return []

def print_hft_recommendations(hft_tokens):
    """Print HFT trading recommendations"""
    print('🚀 HFT TRADING RECOMMENDATIONS')
    print('=' * 70)

    if not hft_tokens:
        print('❌ No suitable HFT opportunities found')
        return

    # Get top 5 HFT candidates
    top_candidates = hft_tokens[:5]

    print('🎯 TOP 5 HFT CANDIDATES:')
    print()

    for i, token in enumerate(top_candidates, 1):
        score = token.get('hft_score', 0)
        volume = token.get('volume_24h', 0)
        liquidity = token.get('liquidity', 0)

        if score >= 7:
            rating = "⭐⭐⭐ EXCELLENT"
        elif score >= 5:
            rating = "⭐⭐ GOOD"
        elif score >= 3:
            rating = "⭐ FAIR"
        else:
            rating = "⚠️ POOR"

        print(f'{i}. {token["symbol"]} - {rating} (Score: {score:.1f}/10)')
        print(f'   💰 Volume: ${volume:,.0f}/24h | 💧 Liquidity: ${liquidity:,.0f}')
        print(f'   📊 Address: {token["address"]}')
        print(f'   🎯 DEX: {token["dex"]} | 📈 Change: {token["price_change_24h"]:+.1f}%')
        print()

    print('💡 HFT STRATEGY RECOMMENDATIONS:')
    print('   • Focus on tokens with HFT Score > 5.0')
    print('   • Look for Volume/Liquidity Ratio > 0.1 (active trading)')
    print('   • Monitor volatility for scalping opportunities')
    print('   • Use limit orders to minimize slippage')
    print('   • Consider market making strategies for high-volume pairs')
    print()

    print('⚠️ RISK WARNINGS:')
    print('   • HFT requires fast execution and low latency')
    print('   • High volatility can lead to significant losses')
    print('   • Always use stop-losses and position sizing')
    print('   • Monitor gas fees on Base chain')
    print('   • Test strategies in paper trading first')
    print()

def main():
    """Main HFT analysis function"""
    print_header()

    # Get trending pairs
    trending_tokens = get_dexscreener_trending_pairs()

    # Get popular token pairs
    popular_tokens = get_dexscreener_search_pairs()

    # Combine and deduplicate
    all_tokens = trending_tokens + popular_tokens
    seen_addresses = set()
    unique_tokens = []
    for token in all_tokens:
        addr = token.get('address')
        if addr and addr not in seen_addresses:
            seen_addresses.add(addr)
            unique_tokens.append(token)

    # Analyze HFT potential
    hft_opportunities = analyze_hft_potential(unique_tokens)

    # Get Birdeye comparison data
    birdeye_data = get_birdeye_volume_data()

    # Print recommendations
    print_hft_recommendations(hft_opportunities)

    print(f'⏰ HFT Analysis completed at {datetime.now().strftime("%H:%M:%S UTC")}')

if __name__ == '__main__':
    main()
