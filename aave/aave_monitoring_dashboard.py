#!/usr/bin/env python3
"""
AAVE MONITORING DASHBOARD
CLI tool to view AAVE monitoring data and statistics
"""

import sqlite3
import os
import argparse
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import json


class AAVEMonitoringDashboard:
    """CLI dashboard for viewing AAVE monitoring data"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.getcwd(), 'data', 'aave_monitoring.db')
        self.db_path = db_path
        self.db_connection = None

    def connect_db(self):
        """Connect to the AAVE monitoring database"""
        try:
            if not os.path.exists(self.db_path):
                print(f"❌ Database not found: {self.db_path}")
                return False

            self.db_connection = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def get_latest_price_data(self) -> Optional[Dict[str, Any]]:
        """Get the latest AAVE price data"""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT timestamp, price_usd, price_change_24h, volume_24h, market_cap
                FROM aave_price_history
                ORDER BY timestamp DESC
                LIMIT 1
            ''')

            row = cursor.fetchone()
            if row:
                return {
                    'timestamp': row[0],
                    'price_usd': row[1],
                    'price_change_24h': row[2],
                    'volume_24h': row[3],
                    'market_cap': row[4]
                }
        except Exception as e:
            print(f"❌ Failed to get latest price data: {e}")

        return None

    def get_price_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get price history for the last N hours"""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            since_time = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

            cursor.execute('''
                SELECT timestamp, price_usd, price_change_24h, volume_24h
                FROM aave_price_history
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            ''', (since_time,))

            prices = []
            for row in cursor.fetchall():
                prices.append({
                    'timestamp': row[0],
                    'price_usd': row[1],
                    'price_change_24h': row[2],
                    'volume_24h': row[3]
                })

            return prices
        except Exception as e:
            print(f"❌ Failed to get price history: {e}")
            return []

    def get_transaction_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Get transaction analysis for the last N hours"""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()
            since_time = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

            cursor.execute('''
                SELECT timeframe, buy_tx_count, sell_tx_count, total_tx_count, buy_sell_ratio
                FROM aave_volume_analysis
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (since_time,))

            analysis = {}
            for row in cursor.fetchall():
                timeframe = row[0]
                if timeframe not in analysis:
                    analysis[timeframe] = {
                        'total_buys': 0,
                        'total_sells': 0,
                        'total_tx': 0,
                        'avg_buy_sell_ratio': 0,
                        'count': 0
                    }

                analysis[timeframe]['total_buys'] += row[1]
                analysis[timeframe]['total_sells'] += row[2]
                analysis[timeframe]['total_tx'] += row[3]
                analysis[timeframe]['avg_buy_sell_ratio'] += row[4]
                analysis[timeframe]['count'] += 1

            # Calculate averages
            for tf, data in analysis.items():
                if data['count'] > 0:
                    data['avg_buy_sell_ratio'] /= data['count']
                    data['buy_ratio'] = (data['total_buys'] / data['total_tx'] * 100) if data['total_tx'] > 0 else 0
                    data['sell_ratio'] = (data['total_sells'] / data['total_tx'] * 100) if data['total_tx'] > 0 else 0

            return analysis
        except Exception as e:
            print(f"❌ Failed to get transaction analysis: {e}")
            return {}

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()

            # Count total records
            cursor.execute('SELECT COUNT(*) FROM aave_price_history')
            price_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM aave_volume_analysis')
            volume_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM aave_monitoring_log')
            log_count = cursor.fetchone()[0]

            # Get latest log entry
            cursor.execute('''
                SELECT timestamp, level, message
                FROM aave_monitoring_log
                ORDER BY timestamp DESC
                LIMIT 1
            ''')
            latest_log = cursor.fetchone()

            return {
                'total_price_updates': price_count,
                'total_volume_updates': volume_count,
                'total_log_entries': log_count,
                'latest_log': {
                    'timestamp': latest_log[0] if latest_log else None,
                    'level': latest_log[1] if latest_log else None,
                    'message': latest_log[2] if latest_log else None
                }
            }
        except Exception as e:
            print(f"❌ Failed to get monitoring stats: {e}")
            return {}

    def display_dashboard(self):
        """Display the main dashboard"""
        print("\n" + "="*80)
        print("🚀 AAVE MONITORING DASHBOARD")
        print("="*80)

        if not self.connect_db():
            return

        # Latest price data
        latest_price = self.get_latest_price_data()
        if latest_price:
            print(f"\n💎 CURRENT AAVE PRICE")
            print(f"   Price: ${latest_price['price_usd']:.6f}")
            print(f"   24h Change: {latest_price['price_change_24h']:+.2f}%")
            print(f"   24h Volume: ${latest_price['volume_24h']:,.0f}")
            print(f"   Market Cap: ${latest_price['market_cap']:,.0f}")
            print(f"   Last Update: {latest_price['timestamp']}")
        else:
            print("\n❌ No price data available")

        # Transaction analysis
        tx_analysis = self.get_transaction_analysis()
        if tx_analysis:
            print(f"\n📊 TRANSACTION ANALYSIS (Last 24h)")
            for timeframe, data in tx_analysis.items():
                print(f"   {timeframe.upper()}: {data['total_tx']} txns")
                print(f"      Buys: {data['total_buys']} ({data['buy_ratio']:.1f}%)")
                print(f"      Sells: {data['total_sells']} ({data['sell_ratio']:.1f}%)")
                print(f"      Buy/Sell Ratio: {data['avg_buy_sell_ratio']:.2f}")
                sentiment = "🐂 BULLISH" if data['buy_ratio'] > data['sell_ratio'] else "🐻 BEARISH" if data['sell_ratio'] > data['buy_ratio'] else "⚖️  NEUTRAL"
                print(f"      Sentiment: {sentiment}")
                print()
        else:
            print("\n❌ No transaction data available")

        # Monitoring stats
        stats = self.get_monitoring_stats()
        if stats:
            print(f"📈 MONITORING STATISTICS")
            print(f"   Price Updates: {stats['total_price_updates']}")
            print(f"   Volume Updates: {stats['total_volume_updates']}")
            print(f"   Log Entries: {stats['total_log_entries']}")
            if stats['latest_log']['timestamp']:
                print(f"   Last Log: [{stats['latest_log']['level']}] {stats['latest_log']['message'][:60]}...")
                print(f"   Log Time: {stats['latest_log']['timestamp']}")

        print("\n" + "="*80)

    def display_price_chart(self, hours: int = 24):
        """Display a simple ASCII price chart"""
        prices = self.get_price_history(hours)
        if not prices:
            print("❌ No price history available")
            return

        print(f"\n📈 AAVE PRICE CHART (Last {hours}h)")
        print("-" * 60)

        # Simple ASCII chart
        if len(prices) > 1:
            min_price = min(p['price_usd'] for p in prices)
            max_price = max(p['price_usd'] for p in prices)
            price_range = max_price - min_price

            if price_range > 0:
                chart_width = 50
                for i, price_data in enumerate(prices):
                    if i % max(1, len(prices) // 10) == 0:  # Show every 10th point
                        normalized = (price_data['price_usd'] - min_price) / price_range
                        bar_length = int(normalized * chart_width)
                        bar = "█" * bar_length
                        timestamp = price_data['timestamp'][:16]  # YYYY-MM-DD HH:MM
                        print(f"{timestamp} | {bar} ${price_data['price_usd']:.4f}")
            else:
                print("Price range too small for chart")

        print(f"\nPrice Range: ${min_price:.4f} - ${max_price:.4f}")

    def export_data(self, output_file: str, format: str = 'json'):
        """Export monitoring data to file"""
        if not self.connect_db():
            return

        data = {
            'latest_price': self.get_latest_price_data(),
            'price_history': self.get_price_history(24),
            'transaction_analysis': self.get_transaction_analysis(24),
            'monitoring_stats': self.get_monitoring_stats(),
            'export_time': datetime.now(timezone.utc).isoformat()
        }

        try:
            if format.lower() == 'json':
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                print(f"✅ Data exported to {output_file} (JSON)")
            else:
                print(f"❌ Unsupported format: {format}")
        except Exception as e:
            print(f"❌ Export failed: {e}")


def main():
    parser = argparse.ArgumentParser(description='AAVE Monitoring Dashboard')
    parser.add_argument('--db-path', type=str,
                       help='Path to AAVE monitoring database')
    parser.add_argument('--chart', action='store_true',
                       help='Display price chart')
    parser.add_argument('--hours', type=int, default=24,
                       help='Hours of history to show (default: 24)')
    parser.add_argument('--export', type=str,
                       help='Export data to file (specify filename)')
    parser.add_argument('--format', type=str, default='json',
                       choices=['json'], help='Export format (default: json)')

    args = parser.parse_args()

    dashboard = AAVEMonitoringDashboard(args.db_path)

    if args.export:
        dashboard.export_data(args.export, args.format)
    elif args.chart:
        if dashboard.connect_db():
            dashboard.display_price_chart(args.hours)
    else:
        dashboard.display_dashboard()


if __name__ == '__main__':
    main()
