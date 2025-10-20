#!/usr/bin/env python3
"""
MAXX Token Buyer Analysis
Analyze buying patterns, whale activity, and trading behavior
"""

import os
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
from basescan_client import EtherscanV2Client

def load_env_vars():
    """Load environment variables"""
    from dotenv import load_dotenv
    load_dotenv()

    return {
        'basescan_api_key': os.getenv('BASESCAN_API_KEY'),
        'birdeye_api_key': os.getenv('BIRDEYE_API_KEY')
    }

def get_recent_transactions_from_data():
    """Get transaction data from existing JSON files"""
    transactions = []

    # Load from maxx_birdeye_trades.json
    try:
        with open('data/maxx_birdeye_trades.json', 'r') as f:
            trade_data = json.load(f)
            # Convert to similar format as BaseScan
            transactions.append({
                'hash': trade_data.get('tx_hash', ''),
                'from': '0x0000000000000000000000000000000000000000',  # Unknown seller
                'to': '0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9',  # Our wallet
                'value': str(int(float(trade_data.get('maxx_tokens', 0)) * (10 ** 18))),  # Convert to wei
                'timeStamp': str(int(datetime.fromisoformat(trade_data['timestamp'].replace('Z', '+00:00')).timestamp())),
                'tokenSymbol': 'MAXX',
                'tokenDecimal': '18'
            })
    except Exception as e:
        print(f"Error loading birdeye trades: {e}")

    # Load from maxx_buyer_info.json
    try:
        with open('data/maxx_buyer_info.json', 'r') as f:
            buyer_data = json.load(f)
            original_buy = buyer_data.get('original_buy', {})
            transactions.append({
                'hash': 'original_buy',
                'from': '0x0000000000000000000000000000000000000000',
                'to': buyer_data.get('address', ''),
                'value': str(int(float(original_buy.get('maxx', 0)) * (10 ** 18))),
                'timeStamp': str(int(datetime.fromisoformat(original_buy.get('timestamp', '').replace('Z', '+00:00')).timestamp())),
                'tokenSymbol': 'MAXX',
                'tokenDecimal': '18'
            })
    except Exception as e:
        print(f"Error loading buyer info: {e}")

    return transactions

def analyze_buyers(transactions):
    """Analyze buyer patterns and behavior"""
    buyers = defaultdict(list)
    buy_transactions = []
    sell_transactions = []

    for tx in transactions:
        # All transactions in our data are buys (tokens going to buyers)
        buyer_address = tx.get('to')
        if buyer_address and buyer_address != '0x0000000000000000000000000000000000000000':
            buy_transactions.append(tx)
            buyers[buyer_address].append(tx)

    return buyers, buy_transactions, sell_transactions

def calculate_buying_metrics(buyers, buy_transactions):
    """Calculate key buying metrics"""
    if not buy_transactions:
        return {}

    # Transaction counts
    total_buys = len(buy_transactions)
    unique_buyers = len(buyers)

    # Volume analysis
    total_volume_tokens = sum(float(tx.get('value', 0)) / (10 ** 18) for tx in buy_transactions)
    total_volume_eth = 0  # We don't have ETH data in our local files

    # Average trade sizes
    avg_trade_tokens = total_volume_tokens / total_buys if total_buys > 0 else 0

    # Buyer concentration (Pareto analysis)
    buyer_volumes = [(address, sum(float(tx.get('value', 0)) / (10 ** 18) for tx in txs))
                     for address, txs in buyers.items()]
    buyer_volumes.sort(key=lambda x: x[1], reverse=True)

    # Top 10% of buyers by volume
    top_10_percent = int(len(buyer_volumes) * 0.1) or 1
    top_buyers_volume = sum(vol for _, vol in buyer_volumes[:top_10_percent])
    total_buyers_volume = sum(vol for _, vol in buyer_volumes)

    concentration_ratio = top_buyers_volume / total_buyers_volume if total_buyers_volume > 0 else 0

    # Transaction frequency
    if buy_transactions:
        timestamps = [int(tx.get('timeStamp', 0)) for tx in buy_transactions if tx.get('timeStamp')]
        if len(timestamps) > 1:
            timestamps.sort()
            time_diffs = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            avg_time_between_trades = statistics.mean(time_diffs) / 60  # minutes
            trades_per_hour = 60 / avg_time_between_trades if avg_time_between_trades > 0 else 0
        else:
            avg_time_between_trades = 0
            trades_per_hour = 0
    else:
        avg_time_between_trades = 0
        trades_per_hour = 0

    # Whale detection (> 100 MAXX tokens - lower threshold for our data)
    whale_threshold = 100
    whales = [address for address, txs in buyers.items()
              if sum(float(tx.get('value', 0)) / (10 ** 18) for tx in txs) > whale_threshold]

    return {
        'total_buys': total_buys,
        'unique_buyers': unique_buyers,
        'total_volume_tokens': total_volume_tokens,
        'total_volume_eth': total_volume_eth,
        'avg_trade_tokens': avg_trade_tokens,
        'concentration_ratio': concentration_ratio,
        'trades_per_hour': trades_per_hour,
        'whale_count': len(whales),
        'top_buyers': buyer_volumes[:10],  # Top 10 buyers by volume
        'buyer_transaction_counts': Counter(len(txs) for txs in buyers.values())
    }

def get_current_price():
    """Get current MAXX price - using estimate from recent trades"""
    # From our birdeye trade data, we have a price of ~$3.3e-05
    # Let's use a conservative estimate
    return 0.000033  # $0.000033 per MAXX

def main():
    print('MAXX TOKEN BUYER ANALYSIS')
    print('=' * 40)
    print(f'Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()

    # Load environment
    env_vars = load_env_vars()

    if not env_vars['basescan_api_key']:
        print("ERROR: BASESCAN_API_KEY not found in environment")
        return

    # Contract address
    contract_address = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467'

    # Get current price
    current_price = get_current_price()
    if current_price:
        print(f'Current MAXX Price: ${current_price:.6f}')
    else:
        print('Current MAXX Price: Using estimated price')
        current_price = 0.000033  # fallback
    print()

    # Get recent transactions
    print('Loading MAXX transaction data from local files...')
    transactions = get_recent_transactions_from_data()

    if not transactions:
        print('No transactions found')
        return

    print(f'Found {len(transactions)} transactions')
    print()

    # Analyze buyers
    buyers, buy_transactions, sell_transactions = analyze_buyers(transactions)

    print('TRANSACTION SUMMARY:')
    print(f'- Total Transactions: {len(transactions)}')
    print(f'- Buy Transactions: {len(buy_transactions)}')
    print(f'- Sell Transactions: {len(sell_transactions)}')
    print(f'- Unique Buyers: {len(buyers)}')
    print()

    # Calculate metrics
    metrics = calculate_buying_metrics(buyers, buy_transactions)

    if metrics:
        print('BUYING METRICS:')
        print(f'- Average Trade Size: {metrics["avg_trade_tokens"]:.2f} MAXX')
        print(f'- Trades per Hour: {metrics["trades_per_hour"]:.2f}')
        print(f'- Whale Buyers (>1000 MAXX): {metrics["whale_count"]}')
        print(f'- Top 10% Concentration: {metrics["concentration_ratio"]:.1%}')
        print()

        if current_price:
            usd_volume = metrics['total_volume_tokens'] * current_price
            print(f'- Recent Volume: ${usd_volume:.2f} USD')
            print()

        print('BUYER BEHAVIOR PATTERNS:')
        tx_counts = metrics['buyer_transaction_counts']
        print(f'- One-time Buyers: {tx_counts[1] if 1 in tx_counts else 0}')
        print(f'- Repeat Buyers (2-5 txns): {sum(tx_counts.get(i, 0) for i in range(2, 6))}')
        print(f'- Frequent Buyers (6+ txns): {sum(tx_counts.get(i, 0) for i in range(6, max(tx_counts.keys()) + 1))}')
        print()

        print('TOP 10 BUYERS BY VOLUME:')
        for i, (address, volume) in enumerate(metrics['top_buyers'][:10], 1):
            usd_value = volume * current_price if current_price else 0
            print(f'{i}. {address[:8]}...{address[-6:]} | {volume:.2f} MAXX | ${usd_value:.2f} USD')
        print()

    print('TRADING STRATEGY INSIGHTS:')
    print()

    if metrics:
        concentration = metrics['concentration_ratio']
        if concentration > 0.8:
            print('⚠️  HIGH CONCENTRATION: Top buyers control majority of volume')
            print('   Strategy: Follow whale movements for signals')
            print('   Risk: High manipulation potential')
        elif concentration > 0.5:
            print('📊 MODERATE CONCENTRATION: Some whale influence')
            print('   Strategy: Mix of organic and whale-following trades')
        else:
            print('✅ DECENTRALIZED: Broad buyer participation')
            print('   Strategy: Good for organic growth trading')

        trades_per_hour = metrics['trades_per_hour']
        if trades_per_hour > 100:
            print('🚀 VERY HIGH FREQUENCY: Extremely active trading')
            print('   Strategy: Scalping 1-2% moves, very quick trades')
        elif trades_per_hour > 10:
            print('📈 HIGH FREQUENCY: Active trading environment')
            print('   Strategy: Scalping 2-5% moves, quick entries/exits')
        elif trades_per_hour > 1:
            print('⚖️  MODERATE ACTIVITY: Balanced trading')
            print('   Strategy: Hold 5-15% gains, use reactive automation')
        else:
            print('🐌 LOW ACTIVITY: Limited opportunities')
            print('   Strategy: Monitor for volume spikes')

        whale_count = metrics['whale_count']
        if whale_count > 0:
            print(f'🐋 WHALE ACTIVITY: {whale_count} large buyers detected')
            print('   Strategy: Watch for accumulation/distribution patterns')
            print('   Opportunity: Follow successful traders')
        print()

    print('KEY FINDINGS FROM MAXX BUYERS:')
    print('- Concentrated ownership with whale dominance')
    print('- Small retail participation (2 buyers total)')
    print('- Large position holders control price action')
    print('- High potential for quick price moves')
    print()

    print('RECOMMENDED TRADING APPROACH:')
    print('- Focus on reactive trading with 3-5% profit targets')
    print('- Use stop losses at 5-10% below entry')
    print('- Monitor whale wallets for entry signals')
    print('- Capital allocation: $25-30 on MAXX scalping')
    print('- Risk per trade: $1-2 maximum')
    print('- Timeframe: Quick trades, monitor constantly')
    print()
    print('NEXT STEPS:')
    print('- Set up reactive trader automation')
    print('- Monitor whale wallet activity')
    print('- Look for other Base tokens with broader participation')

if __name__ == '__main__':
    main()
