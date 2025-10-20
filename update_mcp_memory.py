#!/usr/bin/env python3
"""
MAXX Ecosystem Memory Update Script
Updates the MCP memory system with latest analysis data and intelligence
"""

import json
import os
import hashlib
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import sys

# Add current directory to path
sys.path.append('.')

from maxx_memory_mcp_server import get_memory_store

class MemoryUpdater:
    """Updates MCP memory with latest ecosystem data"""

    def __init__(self):
        self.store = get_memory_store()
        self.data_dir = "data"

    def simple_embedding(self, text: str, dim: int = 384) -> List[float]:
        """Create a simple deterministic embedding from text"""
        # Use SHA256 hash to create deterministic vector
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to float vector
        vector = []
        for i in range(dim):
            # Use bytes to create float values between -1 and 1
            byte_val = hash_bytes[i % len(hash_bytes)]
            float_val = (byte_val / 255.0) * 2 - 1
            vector.append(float_val)

        return vector

    def load_json_file(self, filename: str) -> Dict[str, Any]:
        """Load JSON file safely"""
        try:
            with open(os.path.join(self.data_dir, filename), 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return {}

    def extract_ecosystem_analysis_content(self, data: Dict) -> str:
        """Extract meaningful content from ecosystem analysis"""
        content_parts = []

        # Basic info
        content_parts.append(f"MAXX Ecosystem Analysis - {data.get('analysis_timestamp', 'Unknown')}")
        content_parts.append(f"System: {data.get('system_name', 'Unknown')}")
        content_parts.append(f"Version: {data.get('version', 'Unknown')}")

        # Architecture
        arch = data.get('system_architecture', {})
        core = arch.get('core_components', {})

        content_parts.append("\nCore Components:")
        for comp_name, comp_data in core.items():
            content_parts.append(f"- {comp_name}: {comp_data.get('description', 'No description')}")
            features = comp_data.get('features', [])
            if features:
                content_parts.append(f"  Features: {', '.join(features)}")

        # Data flow
        data_flow = arch.get('data_flow', {})
        inputs = data_flow.get('input_sources', [])
        if inputs:
            content_parts.append(f"\nData Sources: {len(inputs)} configured")

        # Performance metrics
        perf = data.get('performance_metrics', {})
        if perf:
            content_parts.append(f"\nPerformance: {perf.get('overall_status', 'Unknown')}")
            uptime = perf.get('system_uptime', {})
            if uptime:
                content_parts.append(f"Uptime: {uptime.get('percentage', 0):.1f}%")

        return "\n".join(content_parts)

    def extract_intelligence_content(self, data: Dict) -> str:
        """Extract intelligence report content"""
        content_parts = []

        content_parts.append("MAXX Intelligence Report")
        content_parts.append(f"Generated: {data.get('timestamp', 'Unknown')}")

        # Pump events
        pump_events = data.get('pump_events', [])
        if pump_events:
            content_parts.append(f"\nPump Events Detected: {len(pump_events)}")
            for event in pump_events[:5]:  # Top 5
                content_parts.append(f"- {event.get('description', 'Unknown pump')}")
                content_parts.append(f"  Gain: {event.get('price_change_pct', 0):.1f}%")

        # Whale data
        whales = data.get('whale_wallets', [])
        if whales:
            content_parts.append(f"\nWhale Wallets: {len(whales)}")
            for whale in whales[:3]:  # Top 3
                content_parts.append(f"- {whale.get('address', 'Unknown')[:10]}...")
                content_parts.append(f"  Win Rate: {whale.get('win_rate', 0):.1f}%")

        # Signals
        signals = data.get('signals', [])
        if signals:
            content_parts.append(f"\nActive Signals: {len(signals)}")

        return "\n".join(content_parts)

    def extract_trading_content(self, data: Dict) -> str:
        """Extract trading intelligence content"""
        content_parts = []

        content_parts.append("MAXX Trading Intelligence")

        # Performance metrics
        metrics = data.get('performance_metrics', {})
        if metrics:
            content_parts.append(f"Win Rate: {metrics.get('win_rate', 0):.1f}%")
            content_parts.append(f"Total Trades: {metrics.get('total_trades', 0)}")
            content_parts.append(f"Avg Profit: ${metrics.get('average_profit', 0):.4f}")

        # Recent trades
        trades = data.get('recent_trades', [])
        if trades:
            content_parts.append(f"\nRecent Trades: {len(trades)}")
            for trade in trades[:3]:
                content_parts.append(f"- {trade.get('type', 'Unknown')}: {trade.get('amount', 0):.2f} MAXX")

        return "\n".join(content_parts)

    def extract_burn_analysis_content(self, data: Dict) -> str:
        """Extract burn analysis content"""
        content_parts = []

        content_parts.append("Ethermax Burn Analysis")
        content_parts.append(f"Generated: {data.get('timestamp', 'Unknown')}")

        # Burn metrics
        burn_metrics = data.get('burn_metrics', {})
        if burn_metrics:
            content_parts.append(f"Total Burns: {burn_metrics.get('total_burns', 0)}")
            content_parts.append(f"Total MAXX Burned: {burn_metrics.get('total_maxx_burned', 0):.2f}")
            content_parts.append(f"Burn Rate: {burn_metrics.get('burn_rate_per_hour', 0):.2f} MAXX/hour")

        # Burn events
        burn_events = data.get('burn_events', [])
        if burn_events:
            content_parts.append(f"\nBurn Events: {len(burn_events)}")
            for event in burn_events[:3]:
                content_parts.append(f"- Burned: {event.get('amount', 0):.2f} MAXX")

        return "\n".join(content_parts)

    def update_memory_from_file(self, filename: str, category: str, content_extractor):
        """Update memory from a specific file"""
        print(f"Processing {filename}...")

        data = self.load_json_file(filename)
        if not data:
            return

        # Extract content
        content = content_extractor(data)
        if not content:
            return

        # Create embedding
        vector = self.simple_embedding(content)

        # Store in memory
        memory_id = self.store.store_memory(
            content=content,
            vector=vector,
            metadata={
                'source_file': filename,
                'timestamp': datetime.now().isoformat(),
                'data_timestamp': data.get('timestamp') or data.get('analysis_timestamp')
            },
            category=category
        )

        print(f"  ✓ Stored memory {memory_id} for {filename}")

    def update_all_memories(self):
        """Update all memories with latest data"""
        print("🚀 Updating MAXX MCP Memory with latest data...")
        print("=" * 60)

        # Define file mappings with their extractors and categories
        file_mappings = [
            ('MAXX_ECOSYSTEM_ANALYSIS.json', 'ecosystem_analysis', self.extract_ecosystem_analysis_content),
            ('maxx_intelligence_report.json', 'intelligence', self.extract_intelligence_content),
            ('maxx_trades_intelligence.json', 'trading_intelligence', self.extract_trading_content),
            ('ethermax_burn_analysis.json', 'burn_analysis', self.extract_burn_analysis_content),
            ('ethermax_ecosystem_analysis.json', 'ecosystem_analysis', self.extract_ecosystem_analysis_content),
            ('a2a_ecosystem_analysis.json', 'ecosystem_analysis', self.extract_ecosystem_analysis_content),
            ('maxx_strategy_update.json', 'strategy', lambda x: f"Strategy Update: {json.dumps(x, indent=2)}"),
            ('maxx_pool_analysis.json', 'pool_analysis', lambda x: f"Pool Analysis: {json.dumps(x, indent=2)}"),
            ('maxx_birdeye_trades.json', 'trade_data', lambda x: f"Birdeye Trades: {json.dumps(x, indent=2)}"),
            ('trading_stats.json', 'trading_stats', lambda x: f"Trading Stats: {json.dumps(x, indent=2)}"),
            ('reactive_state.json', 'trading_state', lambda x: f"Reactive State: {json.dumps(x, indent=2)}"),
        ]

        updated_count = 0
        for filename, category, extractor in file_mappings:
            try:
                self.update_memory_from_file(filename, category, extractor)
                updated_count += 1
            except Exception as e:
                print(f"  ❌ Error processing {filename}: {e}")

        print(f"\n✅ Memory update complete! Updated {updated_count} data sources.")

        # Show final stats
        self.show_memory_stats()

    def show_memory_stats(self):
        """Show current memory statistics"""
        print("\n📊 Updated Memory Statistics:")
        print("-" * 40)

        if not self.store or not self.store.conn:
            print("Memory store not initialized")
            return

        cursor = self.store.conn.cursor()
        cursor.execute('SELECT category, COUNT(*) FROM memory_vectors GROUP BY category ORDER BY COUNT(*) DESC')
        categories = cursor.fetchall()

        for cat, count in categories:
            print(f"{cat}: {count}")

        cursor.execute('SELECT COUNT(*) FROM memory_vectors')
        total = cursor.fetchone()[0]
        print(f"\nTotal memories: {total}")

def main():
    """Main update function"""
    updater = MemoryUpdater()
    updater.update_all_memories()

if __name__ == "__main__":
    main()
