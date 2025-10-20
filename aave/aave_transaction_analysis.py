#!/usr/bin/env python3
"""
AAVE COMPREHENSIVE TRANSACTION ANALYSIS
Deep dive into AAVE token transaction history and patterns on Base chain
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
    print('🚀 AAVE COMPREHENSIVE TRANSACTION ANALYSIS')
    print('=' * 70)
    print(f'📅 Analysis Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}')
    print('🎯 Token: AAVE | Address: 0x63706e401c06ac8513145b7687A14804d17f814b')
    print()

def get_aave_pair_details():
    """Get detailed AAVE pair information from DexScreener"""
    print('📊 1. AAVE PAIR DETAILS')
    print('-' * 50)

    try:
        # AAVE pair address from our previous analysis
        pair_address = "0x63706e401c06ac8513145b7687A14804d17f814b"  # This might need to be updated

        # First, let's search for AAVE pairs to get the correct pair address
        search_url = 'https://api.dexscreener.com/latest/dex/search?q=AAVE'
        search_response = requests.get(search_url, timeout=15)

        if search_response.status_code == 200:
            search_data = search_response.json()
            if 'pairs' in search_data:
                base_pairs = [p for p in search_data['pairs'] if p.get('chainId') == 'base']
                if base_pairs:
                    # Get the highest volume AAVE pair
                    sorted_pairs = sorted(base_pairs, key=lambda x: x.get('volume', {}).get('h24', 0), reverse=True)
                    pair_address = sorted_pairs[0].get('pairAddress')

        print(f'🔍 Using pair address: {pair_address}')

        # Get detailed pair information
        pair_url = f'https://api.dexscreener.com/latest/dex/pairs/base/{pair_address}'
        pair_response = requests.get(pair_url, timeout=15)

        if pair_response.status_code == 200:
            pair_data = pair_response.json()
            pair_info = pair_data.get('pair', {})

            # Extract key metrics
            base_token = pair_info.get('baseToken', {})
            quote_token = pair_info.get('quoteToken', {})

            print('✅ AAVE Pair Information:')
            print(f'   Symbol: {base_token.get("symbol")}')
            print(f'   Name: {base_token.get("name")}')
            print(f'   Address: {base_token.get("address")}')
            print(f'   Pair: {base_token.get("symbol")}/{quote_token.get("symbol")}')
            print(f'   DEX: {pair_info.get("dexId")}')
            price_usd = pair_info.get("priceUsd", 0)
            print(f'   Price: ${float(price_usd) if isinstance(price_usd, (int, float, str)) and str(price_usd).replace(".", "").isdigit() else 0:.6f}')
            price_change_h24 = pair_info.get("priceChange", {}).get("h24", 0)
            print(f'   24h Change: {float(price_change_h24) if isinstance(price_change_h24, (int, float, str)) and str(price_change_h24).replace(".", "").replace("-", "").isdigit() else 0:+.2f}%')
            volume_h24 = pair_info.get("volume", {}).get("h24", 0)
            print(f'   Volume 24h: ${float(volume_h24) if isinstance(volume_h24, (int, float, str)) and str(volume_h24).replace(".", "").isdigit() else 0:,.0f}')
            liquidity_usd = pair_info.get("liquidity", {}).get("usd", 0)
            print(f'   Liquidity: ${float(liquidity_usd) if isinstance(liquidity_usd, (int, float, str)) and str(liquidity_usd).replace(".", "").isdigit() else 0:,.0f}')
            market_cap = pair_info.get("marketCap", 0)
            print(f'   Market Cap: ${float(market_cap) if isinstance(market_cap, (int, float, str)) and str(market_cap).replace(".", "").isdigit() else 0:,.0f}')
            fdv = pair_info.get("fdv", 0)
            print(f'   FDV: ${float(fdv) if isinstance(fdv, (int, float, str)) and str(fdv).replace(".", "").isdigit() else 0:,.0f}')
            print()

            return pair_info

    except Exception as e:
        print(f'❌ Pair details analysis failed: {e}')
        print()
        return {}

def analyze_transaction_patterns(pair_info):
    """Analyze transaction patterns in detail"""
    print('📈 2. TRANSACTION PATTERN ANALYSIS')
    print('-' * 50)

    try:
        txns = pair_info.get('txns', {})

        print('📊 Transaction Summary by Timeframe:')
        print()

        timeframes = ['h1', 'h6', 'h24']
        for timeframe in timeframes:
            if timeframe in txns:
                tx_data = txns[timeframe]
                buys = tx_data.get('buys', 0)
                sells = tx_data.get('sells', 0)
                total = buys + sells

                if total > 0:
                    buy_ratio = (buys / total) * 100
                    sell_ratio = (sells / total) * 100

                    print(f'   {timeframe.upper()}: {total} total TXs')
                    print(f'      Buys: {buys} ({buy_ratio:.1f}%) | Sells: {sells} ({sell_ratio:.1f}%)')

                    if buy_ratio > sell_ratio:
                        sentiment = "🐂 BULLISH"
                    elif sell_ratio > buy_ratio:
                        sentiment = "🐻 BEARISH"
                    else:
                        sentiment = "⚖️  NEUTRAL"

                    print(f'      Sentiment: {sentiment}')
                    print()

        # Analyze volume patterns
        volume = pair_info.get('volume', {})
        print('💰 Volume Analysis:')
        print(f'   24h Volume: ${volume.get("h24", 0):,.0f}')
        print(f'   6h Volume: ${volume.get("h6", 0):,.0f}')
        print(f'   1h Volume: ${volume.get("h1", 0):,.0f}')
        print()

        # Calculate volume trends
        h24_vol = volume.get('h24', 0)
        h6_vol = volume.get('h6', 0)
        h1_vol = volume.get('h1', 0)

        if h24_vol > 0:
            h6_to_h24_ratio = (h6_vol / h24_vol) * 4  # 6h volume as percentage of 24h
            h1_to_h24_ratio = (h1_vol / h24_vol) * 24  # 1h volume as percentage of 24h

            print('📈 Volume Trends:')
            print(f'   6h volume = {h6_to_h24_ratio:.1f}% of 24h total')
            print(f'   1h volume = {h1_to_h24_ratio:.1f}% of 24h total')

            if h1_to_h24_ratio > 10:
                print('   🔥 HIGH RECENT ACTIVITY')
            elif h1_to_h24_ratio < 2:
                print('   ❄️  LOW RECENT ACTIVITY')
            print()

        return txns

    except Exception as e:
        print(f'❌ Transaction pattern analysis failed: {e}')
        print()
        return {}

def analyze_price_patterns(pair_info):
    """Analyze price patterns and volatility"""
    print('💹 3. PRICE PATTERN ANALYSIS')
    print('-' * 50)

    try:
        price_change = pair_info.get('priceChange', {})
        current_price = pair_info.get('priceUsd', 0)

        print('📊 Price Changes:')
        current_price = pair_info.get("priceUsd", 0)
        print(f'   Current Price: ${float(current_price) if isinstance(current_price, (int, float, str)) and str(current_price).replace(".", "").isdigit() else 0:.6f}')
        h1_change = price_change.get('h1', 0)
        print(f'   1h Change: {float(h1_change) if isinstance(h1_change, (int, float, str)) and str(h1_change).replace(".", "").replace("-", "").isdigit() else 0:+.2f}%')
        h6_change = price_change.get('h6', 0)
        print(f'   6h Change: {float(h6_change) if isinstance(h6_change, (int, float, str)) and str(h6_change).replace(".", "").replace("-", "").isdigit() else 0:+.2f}%')
        h24_change = price_change.get('h24', 0)
        print(f'   24h Change: {float(h24_change) if isinstance(h24_change, (int, float, str)) and str(h24_change).replace(".", "").replace("-", "").isdigit() else 0:+.2f}%')
        print()

        # Calculate volatility
        changes = [price_change.get('h1', 0), price_change.get('h6', 0), price_change.get('h24', 0)]
        avg_change = sum(abs(c) for c in changes) / len(changes) if changes else 0

        print('📈 Volatility Analysis:')
        print(f'   Average Absolute Change: {avg_change:.2f}%')

        if avg_change > 5:
            volatility = "🔥 HIGH VOLATILITY"
        elif avg_change > 2:
            volatility = "⚠️  MEDIUM VOLATILITY"
        else:
            volatility = "✅ LOW VOLATILITY"

        print(f'   Volatility Level: {volatility}')
        print()

        # Price momentum
        h1_change = price_change.get('h1', 0)
        h6_change = price_change.get('h6', 0)

        if h1_change > 0 and h6_change > 0:
            momentum = "🚀 STRONG UPTREND"
        elif h1_change < 0 and h6_change < 0:
            momentum = "📉 STRONG DOWNTREND"
        elif abs(h1_change) > abs(h6_change):
            momentum = "🔄 REVERSAL SIGNAL"
        else:
            momentum = "➡️  CONTINUATION"

        print(f'   Price Momentum: {momentum}')
        print()

        return price_change

    except Exception as e:
        print(f'❌ Price pattern analysis failed: {e}')
        print()
        return {}

def analyze_liquidity_depth(pair_info):
    """Analyze liquidity depth and market efficiency"""
    print('💧 4. LIQUIDITY DEPTH ANALYSIS')
    print('-' * 50)

    try:
        liquidity = pair_info.get('liquidity', {})
        volume = pair_info.get('volume', {})

        usd_liquidity = liquidity.get('usd', 0)
        h24_volume = volume.get('h24', 0)

        print('🏊 Liquidity Metrics:')
        print(f'   Total Liquidity: ${usd_liquidity:,.0f}')
        print(f'   24h Volume: ${h24_volume:,.0f}')

        if usd_liquidity > 0:
            volume_to_liquidity_ratio = h24_volume / usd_liquidity
            print(f'   Volume/Liquidity Ratio: {volume_to_liquidity_ratio:.3f}')

            if volume_to_liquidity_ratio > 1:
                efficiency = "🔥 EXCELLENT (High turnover)"
            elif volume_to_liquidity_ratio > 0.5:
                efficiency = "✅ GOOD (Active trading)"
            elif volume_to_liquidity_ratio > 0.1:
                efficiency = "⚠️  FAIR (Moderate activity)"
            else:
                efficiency = "❌ POOR (Low activity)"

            print(f'   Market Efficiency: {efficiency}')
            print()

            # Slippage estimation
            # For a $1000 trade
            trade_size = 1000
            estimated_slippage = (trade_size / usd_liquidity) * 100
            print('💸 Slippage Estimation (for $1000 trade):')
            print(f'   Estimated Slippage: {estimated_slippage:.2f}%')

            if estimated_slippage < 0.1:
                slippage_rating = "✅ EXCELLENT (<0.1%)"
            elif estimated_slippage < 0.5:
                slippage_rating = "✅ GOOD (<0.5%)"
            elif estimated_slippage < 1:
                slippage_rating = "⚠️  FAIR (<1%)"
            else:
                slippage_rating = "❌ HIGH (>1%)"

            print(f'   Slippage Rating: {slippage_rating}')
            print()

        return liquidity

    except Exception as e:
        print(f'❌ Liquidity analysis failed: {e}')
        print()
        return {}

def get_birdeye_token_info():
    """Get additional AAVE information from Birdeye"""
    print('🦅 5. BIRDEYE ADDITIONAL DATA')
    print('-' * 50)

    try:
        # AAVE contract address on Base
        aave_address = "0x63706e401c06ac8513145b7687A14804d17f814b"

        # Try to get token info
        token_url = f'https://public-api.birdeye.so/defi/token_overview?address={aave_address}'
        token_response = requests.get(token_url, timeout=15)

        if token_response.status_code == 200:
            token_data = token_response.json()
            data = token_data.get('data', {})

            print('✅ Birdeye Token Overview:')
            print(f'   Price: ${data.get("price", 0):.6f}')
            print(f'   Market Cap: ${data.get("mc", 0):,.0f}')
            print(f'   24h Volume: ${data.get("v24h", 0):,.0f}')
            print(f'   24h Change: {data.get("priceChange24h", 0):+.2f}%')
            print(f'   Holders: {data.get("holder", 0):,.0f}')
            print()

            return data
        else:
            print(f'❌ Birdeye API failed: {token_response.status_code}')
            print()
            return {}

    except Exception as e:
        print(f'❌ Birdeye analysis failed: {e}')
        print()
        return {}

def generate_hft_recommendations(pair_info, txns, price_changes, liquidity):
    """Generate HFT trading recommendations for AAVE"""
    print('🎯 6. HFT TRADING RECOMMENDATIONS')
    print('=' * 50)

    try:
        volume_24h = pair_info.get('volume', {}).get('h24', 0)
        liquidity_usd = pair_info.get('liquidity', {}).get('usd', 0)
        price_change_24h = pair_info.get('priceChange', {}).get('h24', 0)

        # Calculate key metrics
        volume_liquidity_ratio = volume_24h / liquidity_usd if liquidity_usd > 0 else 0
        h24_txns = txns.get('h24', {})
        total_txns_24h = h24_txns.get('buys', 0) + h24_txns.get('sells', 0)

        # HFT Suitability Score
        volume_score = min(volume_24h / 50000, 10)  # Scale volume
        liquidity_score = min(liquidity_usd / 100000, 10)  # Scale liquidity
        txn_score = min(total_txns_24h / 500, 10)  # Scale transactions
        volatility_score = min(abs(price_change_24h) * 5, 10)  # Scale volatility

        hft_score = (volume_score + liquidity_score + txn_score + volatility_score) / 4

        print('🏆 AAVE HFT SUITABILITY SCORE:')
        print(f'   Overall Score: {hft_score:.1f}/10')

        if hft_score >= 8:
            rating = "⭐⭐⭐ EXCELLENT for HFT"
        elif hft_score >= 6:
            rating = "⭐⭐ GOOD for HFT"
        elif hft_score >= 4:
            rating = "⭐ FAIR for HFT"
        else:
            rating = "⚠️ POOR for HFT"

        print(f'   Rating: {rating}')
        print()

        print('📊 Key Metrics:')
        print(f'   • Daily Volume: ${volume_24h:,.0f}')
        print(f'   • Liquidity: ${liquidity_usd:,.0f}')
        print(f'   • Daily Transactions: {total_txns_24h:,}')
        print(f'   • 24h Price Change: {price_change_24h:+.2f}%')
        print(f'   • Volume/Liquidity Ratio: {volume_liquidity_ratio:.3f}')
        print()

        print('🎯 RECOMMENDED HFT STRATEGIES:')
        print()

        if hft_score >= 7:
            print('   🚀 HIGH-FREQUENCY SCALPING:')
            print('   • Target 0.1-0.3% price movements')
            print('   • Use limit orders with tight spreads')
            print('   • Capitalize on high transaction frequency')
            print()

        if volume_liquidity_ratio > 0.5:
            print('   💰 MARKET MAKING:')
            print('   • Provide liquidity on both sides')
            print('   • Profit from bid-ask spreads')
            print('   • Low risk with high volume')
            print()

        if abs(price_change_24h) > 3:
            print('   📈 MOMENTUM TRADING:')
            print('   • Follow short-term price trends')
            print('   • Use technical indicators for entry/exit')
            print('   • Higher risk, higher reward')
            print()

        print('⚙️ TECHNICAL SETUP:')
        print('   • Minimum position size: $100-500')
        print('   • Stop loss: 1-2%')
        print('   • Target profit: 0.2-0.5% per trade')
        print('   • Max trades per hour: 10-20')
        print()

        print('⚠️ RISK MANAGEMENT:')
        print('   • Monitor gas fees (Base is cheap)')
        print('   • Use position sizing (1-2% of capital per trade)')
        print('   • Implement circuit breakers for high volatility')
        print('   • Paper trade first to test strategies')
        print()

    except Exception as e:
        print(f'❌ HFT recommendations failed: {e}')
        print()

def main():
    """Main AAVE analysis function"""
    print_header()

    # Get AAVE pair details
    pair_info = get_aave_pair_details()

    if not pair_info:
        print('❌ Could not retrieve AAVE pair information')
        return

    # Analyze transaction patterns
    txns = analyze_transaction_patterns(pair_info)

    # Analyze price patterns
    price_changes = analyze_price_patterns(pair_info)

    # Analyze liquidity
    liquidity = analyze_liquidity_depth(pair_info)

    # Get additional Birdeye data
    birdeye_data = get_birdeye_token_info()

    # Generate HFT recommendations
    generate_hft_recommendations(pair_info, txns, price_changes, liquidity)

    print(f'⏰ AAVE Analysis completed at {datetime.now().strftime("%H:%M:%S UTC")}')

if __name__ == '__main__':
    main()
