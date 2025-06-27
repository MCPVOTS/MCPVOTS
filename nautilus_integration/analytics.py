#!/usr/bin/env python3
"""
MCPVots Nautilus Trader - Advanced Analytics Dashboard
Real-time trading performance visualization and AI insights
"""

import asyncio
import json
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import seaborn as sns

class MCPVotsTradingAnalytics:
    """Advanced analytics for MCPVots Nautilus Trading"""
    
    def __init__(self, db_path: str = "trading_data.db"):
        self.db_path = Path(db_path)
        sns.set_style("darkgrid")
        plt.style.use("dark_background")
    
    def get_trading_summary(self) -> Dict:
        """Get comprehensive trading summary"""
        if not self.db_path.exists():
            return {"error": "No trading data found"}
        
        with sqlite3.connect(self.db_path) as conn:
            # Get all trades
            trades_df = pd.read_sql_query("""
                SELECT * FROM trades ORDER BY timestamp DESC
            """, conn)
            
            if trades_df.empty:
                return {"message": "No trades executed yet"}
            
            # Calculate metrics
            total_trades = len(trades_df)
            buy_trades = len(trades_df[trades_df['side'].str.contains('BUY')])
            sell_trades = len(trades_df[trades_df['side'].str.contains('SELL')])
            
            # Average confidence
            avg_confidence = trades_df['confidence'].mean()
            
            # Most traded symbol
            most_traded = trades_df['symbol'].mode().iloc[0] if not trades_df.empty else "N/A"
            
            # Recent performance
            recent_trades = trades_df.head(10)
            
            return {
                "total_trades": total_trades,
                "buy_trades": buy_trades,
                "sell_trades": sell_trades,
                "avg_confidence": round(avg_confidence, 3),
                "most_traded_symbol": most_traded,
                "recent_trades": recent_trades.to_dict('records'),
                "confidence_distribution": trades_df['confidence'].describe().to_dict(),
                "symbol_distribution": trades_df['symbol'].value_counts().to_dict()
            }
    
    def create_performance_chart(self):
        """Create trading performance visualization"""
        if not self.db_path.exists():
            print("📊 No trading data available for charting")
            return
        
        with sqlite3.connect(self.db_path) as conn:
            trades_df = pd.read_sql_query("""
                SELECT symbol, confidence, side, timestamp, quantity, price 
                FROM trades ORDER BY timestamp
            """, conn)
            
            if trades_df.empty:
                print("📊 No trades to visualize")
                return
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('🌊 MCPVots Nautilus Trader Analytics', fontsize=16, color='cyan')
        
        # 1. Confidence distribution
        ax1.hist(trades_df['confidence'], bins=20, alpha=0.7, color='green', edgecolor='white')
        ax1.set_title('📊 Trade Confidence Distribution', color='white')
        ax1.set_xlabel('Confidence Score', color='white')
        ax1.set_ylabel('Number of Trades', color='white')
        ax1.axvline(0.7, color='red', linestyle='--', label='Confidence Threshold')
        ax1.legend()
        
        # 2. Trades by symbol
        symbol_counts = trades_df['symbol'].value_counts()
        ax2.bar(symbol_counts.index, symbol_counts.values, color='orange', alpha=0.7)
        ax2.set_title('🚀 Trades by Symbol', color='white')
        ax2.set_xlabel('Symbol', color='white')
        ax2.set_ylabel('Number of Trades', color='white')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Buy vs Sell signals
        side_counts = trades_df['side'].value_counts()
        colors = ['green' if 'BUY' in side else 'red' for side in side_counts.index]
        ax3.pie(side_counts.values, labels=side_counts.index, autopct='%1.1f%%', 
                colors=colors, startangle=90)
        ax3.set_title('📈 Buy vs Sell Signals', color='white')
        
        # 4. Trade timeline
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
        trades_timeline = trades_df.groupby(trades_df['timestamp'].dt.date).size()
        ax4.plot(trades_timeline.index, trades_timeline.values, 
                marker='o', color='cyan', linewidth=2, markersize=6)
        ax4.set_title('⏰ Trading Activity Timeline', color='white')
        ax4.set_xlabel('Date', color='white')
        ax4.set_ylabel('Number of Trades', color='white')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('mcpvots_trading_analytics.png', 
                   facecolor='black', edgecolor='white', dpi=300)
        print("📊 Analytics chart saved as 'mcpvots_trading_analytics.png'")
        plt.show()
    
    def generate_ai_insights(self, summary: Dict) -> str:
        """Generate AI insights from trading data"""
        insights = []
        
        # Confidence analysis
        avg_conf = summary.get('avg_confidence', 0)
        if avg_conf > 0.8:
            insights.append("🎯 Excellent AI confidence - high-quality signals")
        elif avg_conf > 0.7:
            insights.append("✅ Good AI confidence - reliable trading decisions")
        else:
            insights.append("⚠️ Lower AI confidence - consider refining analysis")
        
        # Trading balance
        buy_ratio = summary.get('buy_trades', 0) / max(summary.get('total_trades', 1), 1)
        if buy_ratio > 0.7:
            insights.append("📈 Bullish trading pattern - mostly buying signals")
        elif buy_ratio < 0.3:
            insights.append("📉 Bearish trading pattern - mostly selling signals")
        else:
            insights.append("⚖️ Balanced trading approach")
        
        # Volume analysis
        total_trades = summary.get('total_trades', 0)
        if total_trades > 10:
            insights.append("🔄 Active trading system - good market participation")
        elif total_trades > 5:
            insights.append("📊 Moderate trading activity")
        else:
            insights.append("🐌 Low trading volume - system being conservative")
        
        # Most traded asset
        most_traded = summary.get('most_traded_symbol', 'N/A')
        if most_traded != 'N/A':
            insights.append(f"⭐ {most_traded} is the most favored trading pair")
        
        return "\n".join([f"   {insight}" for insight in insights])

async def main():
    """Run analytics dashboard"""
    print("📊 MCPVots Nautilus Trader Analytics Dashboard")
    print("=" * 60)
    
    analytics = MCPVotsTradingAnalytics()
    
    # Get trading summary
    summary = analytics.get_trading_summary()
    
    if "error" in summary or "message" in summary:
        print(f"ℹ️  {summary.get('error', summary.get('message'))}")
        return
    
    # Display summary
    print(f"📈 Total Trades: {summary['total_trades']}")
    print(f"🔵 Buy Trades: {summary['buy_trades']}")
    print(f"🔴 Sell Trades: {summary['sell_trades']}")
    print(f"🎯 Average Confidence: {summary['avg_confidence']:.3f}")
    print(f"⭐ Most Traded: {summary['most_traded_symbol']}")
    
    print(f"\n🧠 AI Insights:")
    insights = analytics.generate_ai_insights(summary)
    print(insights)
    
    print(f"\n📊 Symbol Distribution:")
    for symbol, count in summary['symbol_distribution'].items():
        print(f"   {symbol}: {count} trades")
    
    print(f"\n📋 Recent Trades:")
    for trade in summary['recent_trades'][:5]:
        print(f"   {trade['symbol']} {trade['side']} @ {trade['confidence']:.2f} confidence")
    
    # Create visualization
    print(f"\n📊 Generating performance charts...")
    analytics.create_performance_chart()
    
    print(f"\n🎉 Analytics dashboard complete!")

if __name__ == "__main__":
    asyncio.run(main())
