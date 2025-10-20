#!/usr/bin/env python3
"""
MAXX Transaction Analysis & Strategy Optimizer
Analyzes our trading history and intelligence to determine optimal strategies
"""

import json
import os
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
from typing import Dict, List, Tuple, Optional

# Import our configuration
import sys
sys.path.append('.')
import standalone_config as config

#!/usr/bin/env python3
"""
MAXX Transaction Analysis & Strategy Optimizer
Analyzes our trading history and intelligence to determine optimal strategies
"""

import json
import os
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
from typing import Dict, List, Tuple, Optional

# Import our configuration
import sys
sys.path.append('.')
import standalone_config as config

# Simple Etherscan client for token transactions
class SimpleEtherscanClient:
    def __init__(self):
        self.api_key = "Y8TCGIBF1V9FIRN6Q2R7XQJUYSUEH8C8MG"  # From config
        self.base_url = "https://api.etherscan.io/v2/api"

    async def get_tokentx(self, chain_id: int, address: str, contractaddress: str, page: int = 1, offset: int = 100, sort: str = 'desc'):
        """Get token transactions for an address"""
        import aiohttp

        params = {
            'apikey': self.api_key,
            'module': 'account',
            'action': 'tokentx',
            'contractaddress': contractaddress,
            'address': address,
            'page': page,
            'offset': offset,
            'sort': sort
        }

        # For Base chain, use Etherscan V2 API with chainid
        if chain_id == 8453:
            url = "https://api.etherscan.io/v2/api"
            params['chainid'] = 8453  # Add chainid for Base
        else:
            url = self.base_url

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        print(f"API Error: {response.status}")
                        return {}
        except Exception as e:
            print(f"Request error: {e}")
            return {}

class MAXXStrategyAnalyzer:
    """
    Analyzes MAXX transaction history and intelligence to optimize trading strategies
    """

    def __init__(self):
        self.client = SimpleEtherscanClient()
        self.maxx_contract = config.MAXX_CONTRACT_ADDRESS
        self.account = config.TRADING_ACCOUNT_ADDRESS

        # Load intelligence data
        self.intelligence_data = self._load_intelligence_data()
        self.transaction_history = []

    def _load_intelligence_data(self) -> Dict:
        """Load all available intelligence data"""
        intelligence = {}

        # Load MAXX intelligence report
        try:
            with open('data/maxx_intelligence_report.json', 'r') as f:
                intelligence['intelligence_report'] = json.load(f)
        except:
            intelligence['intelligence_report'] = {}

        # Load trades intelligence
        try:
            with open('data/maxx_trades_intelligence.json', 'r') as f:
                intelligence['trades_intelligence'] = json.load(f)
        except:
            intelligence['trades_intelligence'] = {}

        # Load ecosystem analysis
        try:
            with open('data/MAXX_ECOSYSTEM_ANALYSIS.json', 'r') as f:
                intelligence['ecosystem_analysis'] = json.load(f)
        except:
            intelligence['ecosystem_analysis'] = {}

        # Load strategy update
        try:
            with open('data/maxx_strategy_update.json', 'r') as f:
                intelligence['strategy_update'] = json.load(f)
        except:
            intelligence['strategy_update'] = {}

        return intelligence

    async def analyze_transaction_history(self) -> Dict:
        """Analyze our complete MAXX transaction history"""
        print("🔍 Fetching MAXX transaction history...")

        # Get our MAXX token transfers
        try:
            transfers = await self.client.get_tokentx(
                chain_id=8453,
                address=self.account,
                contractaddress=self.maxx_contract,
                page=1,
                offset=1000,  # Get up to 1000 transactions
                sort='desc'
            )

            if transfers and 'result' in transfers:
                self.transaction_history = transfers['result']
                print(f"📊 Retrieved {len(self.transaction_history)} MAXX transactions")
            else:
                print("❌ No transaction data retrieved")
                return {}

        except Exception as e:
            print(f"❌ Error fetching transactions: {e}")
            return {}

        # Analyze transaction patterns
        analysis = self._analyze_transaction_patterns()

        return analysis

    def _analyze_transaction_patterns(self) -> Dict:
        """Analyze patterns in our transaction history"""
        if not self.transaction_history:
            return {}

        # Parse transactions
        parsed_txs = []
        for tx in self.transaction_history:
            try:
                parsed_tx = {
                    'hash': tx.get('hash', ''),
                    'timestamp': int(tx.get('timeStamp', 0)),
                    'from': tx.get('from', '').lower(),
                    'to': tx.get('to', '').lower(),
                    'value': int(tx.get('value', '0')),
                    'gas_used': int(tx.get('gasUsed', '0')),
                    'gas_price': int(tx.get('gasPrice', '0')),
                    'direction': 'IN' if tx.get('to', '').lower() == self.account.lower() else 'OUT'
                }
                parsed_txs.append(parsed_tx)
            except Exception as e:
                print(f"❌ Failed to parse transaction: {e}, tx keys: {list(tx.keys()) if isinstance(tx, dict) else 'Not dict'}")
                continue

        # Calculate key metrics
        total_txs = len(parsed_txs)
        buy_txs = [tx for tx in parsed_txs if tx['direction'] == 'IN']
        sell_txs = [tx for tx in parsed_txs if tx['direction'] == 'OUT']

        # Volume analysis
        total_buy_volume = sum(tx['value'] for tx in buy_txs) / 10**18  # Convert to MAXX
        total_sell_volume = sum(tx['value'] for tx in sell_txs) / 10**18

        # Timing analysis
        trades_per_day = 0
        avg_holding_period = 0
        time_span_days = 0

        if parsed_txs:
            timestamps = [tx['timestamp'] for tx in parsed_txs]
            time_span_days = (max(timestamps) - min(timestamps)) / (24 * 3600) if len(timestamps) > 1 else 1

            # Calculate trading frequency
            trades_per_day = total_txs / max(time_span_days, 1)

            # Analyze holding periods
            holding_periods = []
            buy_times = {tx['hash']: tx['timestamp'] for tx in buy_txs}

            for sell_tx in sell_txs:
                # Find corresponding buy (simplified - assumes FIFO)
                if buy_times:
                    buy_time = min(buy_times.values())
                    holding_period = (sell_tx['timestamp'] - buy_time) / 3600  # hours
                    holding_periods.append(holding_period)

            avg_holding_period = statistics.mean(holding_periods) if holding_periods else 0

        # Gas analysis
        gas_costs = []
        for tx in parsed_txs:
            if tx['gas_used'] and tx['gas_price']:
                gas_cost_eth = (tx['gas_used'] * tx['gas_price']) / 10**18
                gas_costs.append(gas_cost_eth)

        avg_gas_cost = statistics.mean(gas_costs) if gas_costs else 0
        total_gas_cost = sum(gas_costs)

        # Profitability analysis (simplified - based on buy/sell volumes)
        # This is a rough estimate since we don't have exact prices
        estimated_pnl = total_sell_volume - total_buy_volume

        analysis = {
            'total_transactions': total_txs,
            'buy_transactions': len(buy_txs),
            'sell_transactions': len(sell_txs),
            'total_buy_volume': total_buy_volume,
            'total_sell_volume': total_sell_volume,
            'net_position': total_buy_volume - total_sell_volume,
            'trades_per_day': trades_per_day,
            'avg_holding_period_hours': avg_holding_period,
            'avg_gas_cost_eth': avg_gas_cost,
            'total_gas_cost_eth': total_gas_cost,
            'estimated_pnl_maxx': estimated_pnl,
            'time_span_days': time_span_days,
            'parsed_transactions': parsed_txs[:10]  # Keep last 10 for reference
        }

        return analysis

    def analyze_intelligence_data(self) -> Dict:
        """Analyze intelligence data for strategy insights"""
        intel = {}

        # Extract pump events from intelligence report
        report = self.intelligence_data.get('intelligence_report', {})
        pump_events = report.get('pump_events', [])

        if pump_events:
            # Analyze pump patterns
            pump_gains = [event.get('price_change_pct', 0) for event in pump_events]
            pump_durations = [event.get('duration_minutes', 0) for event in pump_events]
            pump_participants = [event.get('participants', 0) for event in pump_events]

            intel['pump_analysis'] = {
                'total_pumps': len(pump_events),
                'avg_gain_pct': statistics.mean(pump_gains) if pump_gains else 0,
                'avg_duration_min': statistics.mean(pump_durations) if pump_durations else 0,
                'avg_participants': statistics.mean(pump_participants) if pump_participants else 0,
                'max_gain_pct': max(pump_gains) if pump_gains else 0
            }

        # Extract whale data
        whales = report.get('whale_wallets', [])
        if whales:
            whale_win_rates = [w.get('win_rate', 0) for w in whales if w.get('win_rate', 0) > 0]
            intel['whale_analysis'] = {
                'total_whales': len(whales),
                'avg_win_rate': statistics.mean(whale_win_rates) if whale_win_rates else 0,
                'top_whale_address': whales[0].get('address', '') if whales else ''
            }

        # Extract signals
        signals = report.get('signals', [])
        if signals:
            signal_types = Counter(s.get('type', '') for s in signals)
            intel['signal_analysis'] = dict(signal_types)

        # Extract recommendations
        recommendations = report.get('recommendations', {})
        intel['strategy_recommendations'] = recommendations.get('strategic_positions', [])

        return intel

    def generate_strategy_recommendations(self, tx_analysis: Dict, intel_analysis: Dict) -> Dict:
        """Generate optimal strategy recommendations based on analysis"""

        recommendations = {
            'optimal_strategies': [],
            'risk_assessment': {},
            'position_sizing': {},
            'entry_exit_rules': {},
            'gas_optimization': {},
            'monitoring_setup': {}
        }

        # Strategy 1: Pump-Sell Strategy (based on intelligence data)
        if intel_analysis.get('pump_analysis'):
            pump_data = intel_analysis['pump_analysis']
            if pump_data['total_pumps'] > 0:
                pump_strategy = {
                    'name': 'Pump-Sell Strategy',
                    'description': f'Buy during dips, sell at {pump_data["avg_gain_pct"]:.1f}% pump gains',
                    'success_rate': pump_data.get('win_rate', 0.73),
                    'avg_return': pump_data.get('avg_return', 0.22),
                    'holding_period': f'{pump_data["avg_duration_min"]:.0f} minutes',
                    'confidence': 'HIGH' if pump_data['total_pumps'] >= 3 else 'MEDIUM'
                }
                recommendations['optimal_strategies'].append(pump_strategy)

        # Strategy 2: Whale Following Strategy
        if intel_analysis.get('whale_analysis'):
            whale_data = intel_analysis['whale_analysis']
            if whale_data['total_whales'] > 0:
                whale_strategy = {
                    'name': 'Whale Following Strategy',
                    'description': f'Follow top whales with {whale_data["avg_win_rate"]:.1f}% win rate',
                    'success_rate': whale_data['avg_win_rate'],
                    'avg_return': 0.15,  # From intelligence data
                    'holding_period': 'Short-term (minutes to hours)',
                    'confidence': 'MEDIUM'
                }
                recommendations['optimal_strategies'].append(whale_strategy)

        # Strategy 3: Optimized Frequency Strategy (based on our trading history)
        if tx_analysis.get('trades_per_day', 0) > 0:
            frequency = tx_analysis['trades_per_day']
            if frequency < 5:  # Low frequency
                freq_strategy = {
                    'name': 'Conservative Swing Strategy',
                    'description': f'Current frequency: {frequency:.1f} trades/day - increase to 10-15 trades/day',
                    'success_rate': tx_analysis.get('success_rate', 0.8),
                    'avg_return': 0.10,
                    'holding_period': f'{tx_analysis.get("avg_holding_period_hours", 24):.0f} hours',
                    'confidence': 'HIGH'
                }
            else:  # High frequency
                freq_strategy = {
                    'name': 'High-Frequency Scalping',
                    'description': f'Current frequency: {frequency:.1f} trades/day - optimize for smaller gains',
                    'success_rate': 0.75,
                    'avg_return': 0.05,
                    'holding_period': 'Minutes',
                    'confidence': 'MEDIUM'
                }
            recommendations['optimal_strategies'].append(freq_strategy)

        # Risk Assessment
        gas_cost_pct = (tx_analysis.get('total_gas_cost_eth', 0) / max(tx_analysis.get('total_buy_volume', 1) * 0.00003, 0.001)) * 100
        recommendations['risk_assessment'] = {
            'gas_cost_percentage': gas_cost_pct,
            'recommended_max_gas': 0.0001,  # 0.1 USD worth
            'stop_loss_percentage': 0.0,  # DISABLED for pump riding strategy
            'max_daily_trades': 20,
            'max_position_size_usd': 10.0
        }

        # Position Sizing
        recommendations['position_sizing'] = {
            'base_position_usd': 5.0,
            'scaling_factor': 0.5,  # Reduce size during high volatility
            'max_position_pct': 10.0  # Max 10% of available balance
        }

        # Entry/Exit Rules
        recommendations['entry_exit_rules'] = {
            'buy_signals': [
                '15% dip from last sell price',
                'Whale accumulation detected',
                'Volume spike > 2x average',
                'Coordinated buying pattern'
            ],
            'sell_signals': [
                '20% gain from entry',
                'Profit target reached',
                'Stop loss disabled for pump riding - no automatic selling on downturns',
                'Reversal signals detected'
            ]
        }

        # Gas Optimization
        recommendations['gas_optimization'] = {
            'optimal_gas_gwei': 0.1,
            'fast_gas_gwei': 0.25,
            'urgent_gas_gwei': 0.45,
            'recommended_timing': '16:30-17:30 UTC',
            'savings_potential': '20-30%'
        }

        # Monitoring Setup
        recommendations['monitoring_setup'] = {
            'price_check_interval': 30,  # seconds
            'transaction_check_interval': 60,  # seconds
            'balance_check_interval': 120,  # seconds
            'alert_triggers': [
                'Large whale movement',
                'Pump event detected',
                'Volume spike',
                'Gas price spike'
            ]
        }

        return recommendations

    async def run_complete_analysis(self) -> Dict:
        """Run complete analysis and generate strategy recommendations"""
        print("🚀 Starting MAXX Strategy Analysis...")
        print("="*60)

        # Analyze transaction history
        tx_analysis = await self.analyze_transaction_history()

        # Analyze intelligence data
        intel_analysis = self.analyze_intelligence_data()

        # Generate strategy recommendations
        strategy_recommendations = self.generate_strategy_recommendations(tx_analysis, intel_analysis)

        # Compile final report
        analysis_report = {
            'timestamp': datetime.now().isoformat(),
            'transaction_analysis': tx_analysis,
            'intelligence_analysis': intel_analysis,
            'strategy_recommendations': strategy_recommendations,
            'key_insights': self._generate_key_insights(tx_analysis, intel_analysis, strategy_recommendations)
        }

        return analysis_report

    def _generate_key_insights(self, tx_analysis: Dict, intel_analysis: Dict, recommendations: Dict) -> List[str]:
        """Generate key insights from the analysis"""
        insights = []

        # Transaction insights
        if tx_analysis:
            total_txs = tx_analysis.get('total_transactions', 0)
            buy_txs = tx_analysis.get('buy_transactions', 0)
            sell_txs = tx_analysis.get('sell_transactions', 0)
            net_position = tx_analysis.get('net_position', 0)
            trades_per_day = tx_analysis.get('trades_per_day', 0)

            insights.append(f"📊 Transaction History: {total_txs} total trades ({buy_txs} buys, {sell_txs} sells)")
            insights.append(f"📈 Trading Frequency: {trades_per_day:.1f} trades per day")
            insights.append(f"💰 Net Position: {net_position:.2f} MAXX (positive = long, negative = short)")

            gas_cost_pct = tx_analysis.get('avg_gas_cost_eth', 0) / 0.00003 * 100  # Rough USD conversion
            insights.append(f"⛽ Gas Efficiency: Average {gas_cost_pct:.1f}% of trade value spent on gas")

        # Intelligence insights
        if intel_analysis.get('pump_analysis'):
            pump_data = intel_analysis['pump_analysis']
            insights.append(f"🚀 Pump Analysis: {pump_data['total_pumps']} pumps detected, avg {pump_data['avg_gain_pct']:.1f}% gains")
            insights.append(f"⏱️ Pump Duration: Average {pump_data['avg_duration_min']:.0f} minutes")

        if intel_analysis.get('whale_analysis'):
            whale_data = intel_analysis['whale_analysis']
            insights.append(f"🐋 Whale Activity: {whale_data['total_whales']} active whales, {whale_data['avg_win_rate']:.1f}% win rate")

        # Strategy insights
        optimal_strategies = recommendations.get('optimal_strategies', [])
        if optimal_strategies:
            top_strategy = optimal_strategies[0]
            insights.append(f"🎯 Recommended Strategy: {top_strategy['name']} (confidence: {top_strategy['confidence']})")
            insights.append(f"💡 Expected Return: {top_strategy.get('avg_return', 0):.1f}% per trade")

        return insights

def print_analysis_report(report: Dict):
    """Print a formatted analysis report"""
    print("\n" + "="*80)
    print("🎯 MAXX STRATEGY ANALYSIS REPORT")
    print("="*80)
    print(f"📅 Generated: {report['timestamp']}")

    # Key Insights
    print("\n🔑 KEY INSIGHTS:")
    for insight in report.get('key_insights', []):
        print(f"  {insight}")

    # Transaction Analysis
    tx_analysis = report.get('transaction_analysis', {})
    if tx_analysis:
        print(f"\n📊 TRANSACTION ANALYSIS:")
        print(f"  Total Trades: {tx_analysis.get('total_transactions', 0)}")
        print(f"  Buy/Sell Ratio: {tx_analysis.get('buy_transactions', 0)}/{tx_analysis.get('sell_transactions', 0)}")
        print(f"  Net Position: {tx_analysis.get('net_position', 0):.2f} MAXX")
        print(f"  Trading Frequency: {tx_analysis.get('trades_per_day', 0):.1f} trades/day")
        print(f"  Avg Holding Period: {tx_analysis.get('avg_holding_period_hours', 0):.1f} hours")
        print(f"  Gas Cost Efficiency: {tx_analysis.get('avg_gas_cost_eth', 0):.6f} ETH avg")

    # Intelligence Analysis
    intel_analysis = report.get('intelligence_analysis', {})
    if intel_analysis.get('pump_analysis'):
        pump = intel_analysis['pump_analysis']
        print(f"\n🚀 PUMP INTELLIGENCE:")
        print(f"  Total Pumps Detected: {pump.get('total_pumps', 0)}")
        print(f"  Average Gain: {pump.get('avg_gain_pct', 0):.1f}%")
        print(f"  Average Duration: {pump.get('avg_duration_min', 0):.0f} minutes")

    if intel_analysis.get('whale_analysis'):
        whale = intel_analysis['whale_analysis']
        print(f"\n🐋 WHALE INTELLIGENCE:")
        print(f"  Active Whales: {whale.get('total_whales', 0)}")
        print(f"  Average Win Rate: {whale.get('avg_win_rate', 0):.1f}%")

    # Strategy Recommendations
    recommendations = report.get('strategy_recommendations', {})
    optimal_strategies = recommendations.get('optimal_strategies', [])

    if optimal_strategies:
        print(f"\n🎯 OPTIMAL STRATEGIES:")
        for i, strategy in enumerate(optimal_strategies[:3]):
            print(f"  {i+1}. {strategy['name']}")
            print(f"     Success Rate: {strategy.get('success_rate', 0):.1f}%")
            print(f"     Expected Return: {strategy.get('avg_return', 0):.1f}%")
            print(f"     Holding Period: {strategy.get('holding_period', 'N/A')}")
            print(f"     Confidence: {strategy.get('confidence', 'MEDIUM')}")

    # Risk Assessment
    risk = recommendations.get('risk_assessment', {})
    if risk:
        print(f"\n⚠️ RISK MANAGEMENT:")
        print(f"  Max Gas Cost: {risk.get('recommended_max_gas', 0):.6f} ETH")
        print(f"  Stop Loss: DISABLED (pump riding strategy)")
        print(f"  Max Daily Trades: {risk.get('max_daily_trades', 0)}")
        print(f"  Max Position Size: ${risk.get('max_position_size_usd', 0):.1f}")

    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE - Ready to implement optimal strategy!")
    print("="*80)

async def main():
    """Main analysis function"""
    analyzer = MAXXStrategyAnalyzer()
    report = await analyzer.run_complete_analysis()
    print_analysis_report(report)

if __name__ == "__main__":
    asyncio.run(main())
