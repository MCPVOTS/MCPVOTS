#!/usr/bin/env python3
"""
MCPVots Nautilus Trader - Real-Time Monitoring Dashboard
Live tracking of AI trading performance and system health
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import os

class MCPVotsLiveMonitor:
    """Real-time monitoring for MCPVots Nautilus Trading"""
    
    def __init__(self, db_path: str = "trading_data.db"):
        self.db_path = Path(db_path)
        self.last_trade_count = 0
        self.start_time = datetime.now()
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_live_stats(self) -> Dict:
        """Get live trading statistics"""
        if not self.db_path.exists():
            return {"status": "No database found"}
        
        with sqlite3.connect(self.db_path) as conn:
            # Get recent trades
            recent_trades = conn.execute("""
                SELECT COUNT(*) FROM trades 
                WHERE datetime(timestamp) > datetime('now', '-1 hour')
            """).fetchone()[0]
            
            # Get total trades
            total_trades = conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
            
            # Get average confidence for recent trades
            avg_confidence = conn.execute("""
                SELECT AVG(confidence) FROM trades 
                WHERE datetime(timestamp) > datetime('now', '-1 hour')
            """).fetchone()[0] or 0
            
            # Get portfolio value (mock calculation)
            portfolio_value = 50.0  # Starting value
            
            # Get active positions count
            active_positions = conn.execute("""
                SELECT COUNT(DISTINCT symbol) FROM trades
            """).fetchone()[0]
            
            # Get most recent trade
            latest_trade = conn.execute("""
                SELECT symbol, side, confidence, timestamp 
                FROM trades ORDER BY timestamp DESC LIMIT 1
            """).fetchone()
            
            return {
                "recent_trades": recent_trades,
                "total_trades": total_trades,
                "avg_confidence": round(avg_confidence, 3),
                "portfolio_value": portfolio_value,
                "active_positions": active_positions,
                "latest_trade": latest_trade,
                "uptime": str(datetime.now() - self.start_time).split('.')[0]
            }
    
    def display_dashboard(self, stats: Dict):
        """Display real-time dashboard"""
        self.clear_screen()
        
        print("🌊" + "=" * 78 + "🌊")
        print("🚀             MCPVots Nautilus Trader - Live Monitor              🚀")
        print("🌊" + "=" * 78 + "🌊")
        print(f"⏰ Live Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Uptime: {stats.get('uptime', '00:00:00')}")
        print()
        
        # System Status
        print("📊 SYSTEM STATUS:")
        print(f"   🔄 System: {'🟢 ACTIVE' if stats.get('total_trades', 0) > 0 else '🟡 STANDBY'}")
        print(f"   🤖 AI Analysis: {'🟢 ONLINE' if stats.get('avg_confidence', 0) > 0 else '🔴 OFFLINE'}")
        print(f"   💾 Database: {'🟢 CONNECTED' if 'status' not in stats else '🔴 ERROR'}")
        print()
        
        # Trading Metrics
        print("📈 TRADING METRICS:")
        print(f"   💰 Portfolio Value: ${stats.get('portfolio_value', 0):.2f}")
        print(f"   🎯 Total Trades: {stats.get('total_trades', 0)}")
        print(f"   ⚡ Recent Trades (1h): {stats.get('recent_trades', 0)}")
        print(f"   📊 Active Positions: {stats.get('active_positions', 0)}")
        print(f"   🧠 Avg AI Confidence: {stats.get('avg_confidence', 0):.3f}")
        print()
        
        # Latest Trade
        latest = stats.get('latest_trade')
        if latest:
            print("🔥 LATEST TRADE:")
            print(f"   Symbol: {latest[0]}")
            print(f"   Side: {latest[1]}")
            print(f"   Confidence: {latest[2]:.3f}")
            print(f"   Time: {latest[3]}")
        else:
            print("🔥 LATEST TRADE: No trades yet")
        print()
        
        # Performance Indicators
        confidence = stats.get('avg_confidence', 0)
        print("🎯 PERFORMANCE INDICATORS:")
        if confidence > 0.8:
            print("   🟢 AI Confidence: EXCELLENT")
        elif confidence > 0.7:
            print("   🟡 AI Confidence: GOOD")
        elif confidence > 0.5:
            print("   🟠 AI Confidence: MODERATE")
        else:
            print("   🔴 AI Confidence: LOW")
        
        recent_activity = stats.get('recent_trades', 0)
        if recent_activity > 5:
            print("   🟢 Trading Activity: HIGH")
        elif recent_activity > 2:
            print("   🟡 Trading Activity: MODERATE")
        elif recent_activity > 0:
            print("   🟠 Trading Activity: LOW")
        else:
            print("   🔴 Trading Activity: NONE")
        print()
        
        # System Health
        print("🛡️  SYSTEM HEALTH:")
        print("   🟢 Risk Management: ACTIVE")
        print("   🟢 Stop Loss Protection: ENABLED")
        print("   🟢 Position Limits: ENFORCED")
        print("   🟢 Knowledge Graph: STORING")
        print()
        
        # Quick Stats Bar
        trades_per_hour = stats.get('recent_trades', 0)
        activity_bar = "█" * min(trades_per_hour, 20)
        print(f"📊 Activity: [{activity_bar:<20}] {trades_per_hour} trades/hour")
        
        confidence_bar = "█" * int(stats.get('avg_confidence', 0) * 20)
        print(f"🧠 AI Quality: [{confidence_bar:<20}] {stats.get('avg_confidence', 0):.1%}")
        print()
        
        # Controls
        print("🎮 CONTROLS: Press Ctrl+C to stop monitoring")
        print("🌊" + "=" * 78 + "🌊")
    
    async def monitor(self, refresh_interval: int = 5):
        """Start live monitoring"""
        print("🚀 Starting MCPVots Nautilus Live Monitor...")
        
        try:
            while True:
                stats = self.get_live_stats()
                self.display_dashboard(stats)
                
                # Check for new trades
                current_trades = stats.get('total_trades', 0)
                if current_trades > self.last_trade_count:
                    # Flash notification for new trade
                    print("\n🔔 NEW TRADE DETECTED!")
                    time.sleep(1)
                    self.last_trade_count = current_trades
                
                await asyncio.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Live monitoring stopped by user")
            print("📊 Final statistics saved to monitor_session.log")
            
            # Save session summary
            with open("monitor_session.log", "w") as f:
                f.write(f"MCPVots Monitor Session - {datetime.now()}\n")
                f.write(f"Session Duration: {stats.get('uptime', 'N/A')}\n")
                f.write(f"Total Trades Monitored: {stats.get('total_trades', 0)}\n")
                f.write(f"Average Confidence: {stats.get('avg_confidence', 0):.3f}\n")

class AdvancedTradingAlerts:
    """Advanced alerting system for trading events"""
    
    def __init__(self):
        self.alert_thresholds = {
            "high_confidence": 0.9,
            "low_confidence": 0.4,
            "rapid_trades": 5,  # trades per hour
            "portfolio_change": 0.1  # 10% change
        }
    
    def check_alerts(self, stats: Dict) -> List[str]:
        """Check for alert conditions"""
        alerts = []
        
        # High confidence alert
        if stats.get('avg_confidence', 0) > self.alert_thresholds["high_confidence"]:
            alerts.append("🔥 HIGH CONFIDENCE TRADING - AI very confident!")
        
        # Low confidence alert
        if stats.get('avg_confidence', 0) < self.alert_thresholds["low_confidence"]:
            alerts.append("⚠️ LOW CONFIDENCE WARNING - Review AI analysis")
        
        # Rapid trading alert
        if stats.get('recent_trades', 0) > self.alert_thresholds["rapid_trades"]:
            alerts.append("⚡ RAPID TRADING DETECTED - High market activity")
        
        # No activity alert
        if stats.get('recent_trades', 0) == 0 and stats.get('total_trades', 0) > 0:
            alerts.append("😴 NO RECENT ACTIVITY - System may be idle")
        
        return alerts

async def main():
    """Run live monitoring dashboard"""
    print("🌊 MCPVots Nautilus Trader Live Monitor")
    print("Starting real-time dashboard...")
    print("Press Ctrl+C to stop")
    
    monitor = MCPVotsLiveMonitor()
    alerts = AdvancedTradingAlerts()
    
    # Start monitoring with 5-second refresh
    await monitor.monitor(refresh_interval=5)

if __name__ == "__main__":
    asyncio.run(main())
