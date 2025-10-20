#!/usr/bin/env python3
"""
VOTS Token Burn Mechanism Market Analysis - Complete Integration Demo

This script demonstrates the complete integration of Flaunch burn mechanisms
for VOTS token market analysis via MCPVOTS a2a. It showcases how burn data
provides market analysis at price through advanced algorithmic analysis.

Usage Examples:
    python vots_burn_analysis_demo.py --demo
    python vots_burn_analysis_demo.py --token 0x1c93d155bd388241f9ab5df500d69eb529ce9583 --price 0.001234
"""

import argparse
import json
from datetime import datetime
from mcpvots_a2a_integration import MCPVOTSIntegration
from flaunch_burn_analyzer import FlaunchBurnAnalyzer

def run_demo():
    """Run a comprehensive demo of VOTS burn mechanism analysis"""

    print("🚀 VOTS Token Burn Mechanism Market Analysis Demo")
    print("=" * 60)

    # Initialize components
    analyzer = FlaunchBurnAnalyzer()
    mcpvots = MCPVOTSIntegration(analyzer)

    # Example VOTS token (using a real Flaunch token for demo)
    demo_token = "0x1c93d155bd388241f9ab5df500d69eb529ce9583"  # FLOKI token

    print(f"📍 Analyzing Token: {demo_token}")
    print("💡 This demo uses FLOKI token data to showcase VOTS analysis capabilities\n")

    # Scenario 1: General market analysis
    print("📊 Scenario 1: General Market Analysis")
    analysis = mcpvots.get_vots_market_analysis(demo_token)
    display_key_metrics(analysis)

    # Scenario 2: Price-specific analysis
    print("\n💰 Scenario 2: Price-Specific Analysis ($0.001500)")
    price_analysis = mcpvots.get_vots_market_analysis(demo_token, 0.001500)
    display_price_specific_analysis(price_analysis)

    # Scenario 3: Burn strategy recommendations
    print("\n🎯 Scenario 3: Burn Strategy Recommendations")
    strategy = analyzer.get_burn_strategy(demo_token)
    display_strategy_recommendations(strategy)

    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("\n🔑 Key Takeaways:")
    print("• Burn mechanisms provide deflationary pressure")
    print("• Royalty NFT holders control burn operations")
    print("• Price analysis incorporates burn efficiency")
    print("• Strategy recommendations optimize timing")
    print("• MCPVOTS a2a enables market analysis at requested price")

def display_key_metrics(analysis):
    """Display key VOTS analysis metrics"""

    if "error" in analysis:
        print(f"❌ Error: {analysis['error']}")
        return

    vots = analysis.get('vots_analysis', {})
    burn_stats = analysis.get('burn_data', {}).get('burnStats', {})

    print(f"   VOTS Price: ${vots.get('calculated_vots_price', 0):.6f}")
    print(f"   Confidence: {vots.get('confidence_score', 0):.1f}%")
    print(f"   24h Burn Rate: {burn_stats.get('burnRate24h', 'N/A')}")
    print(f"   Burn Efficiency: {burn_stats.get('burnEfficiency', 'N/A')}%")

def display_price_specific_analysis(analysis):
    """Display price-specific analysis results"""

    if "error" in analysis or "price_specific_analysis" not in analysis:
        print("❌ Price-specific analysis not available")
        return

    psa = analysis["price_specific_analysis"]
    price_analysis = psa["price_analysis"]
    recommendations = psa["recommendations"]

    alignment = price_analysis["price_alignment"]
    print(f"   Price Alignment: {alignment['alignment_score']}")
    print(f"   Difference: {price_analysis['price_difference_percentage']:.2f}%")

    print("   Top Recommendations:")
    for rec in recommendations[:2]:
        print(f"     • {rec['type']}: {rec['action']} ({rec['confidence']}%)")

def display_strategy_recommendations(strategy):
    """Display burn strategy recommendations"""

    if not strategy or "strategyRecommendations" not in strategy:
        print("❌ Strategy recommendations not available")
        return

    recommendations = strategy["strategyRecommendations"][:3]

    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec['name']}")
        print(f"      Risk: {rec['riskLevel']} | Confidence: {rec['confidenceScore']}%")
        print(f"      Horizon: {rec['timeHorizon']}")

def run_live_analysis(token_address, requested_price=None):
    """Run live analysis on a specific token"""

    print(f"🔍 Running Live VOTS Analysis for: {token_address}")

    analyzer = FlaunchBurnAnalyzer()
    mcpvots = MCPVOTSIntegration(analyzer)

    analysis = mcpvots.get_vots_market_analysis(token_address, requested_price)

    if requested_price:
        print(f"💰 Requested Price Analysis: ${requested_price:.6f}")

    mcpvots.display_comprehensive_analysis(analysis)

def export_sample_data():
    """Export sample analysis data for integration testing"""

    analyzer = FlaunchBurnAnalyzer()
    mcpvots = MCPVOTSIntegration(analyzer)

    # Sample token for demo
    sample_token = "0x1c93d155bd388241f9ab5df500d69eb529ce9583"

    print("📤 Exporting sample analysis data...")

    # General analysis
    analysis = mcpvots.get_vots_market_analysis(sample_token)
    with open('sample_vots_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2, default=str)

    # Price-specific analysis
    price_analysis = mcpvots.get_vots_market_analysis(sample_token, 0.001234)
    with open('sample_price_analysis.json', 'w') as f:
        json.dump(price_analysis, f, indent=2, default=str)

    print("✅ Sample data exported:")
    print("   • sample_vots_analysis.json")
    print("   • sample_price_analysis.json")

def main():
    parser = argparse.ArgumentParser(description="VOTS Token Burn Mechanism Market Analysis Demo")
    parser.add_argument("--demo", action="store_true", help="Run comprehensive demo")
    parser.add_argument("--token", help="Live token address to analyze")
    parser.add_argument("--price", type=float, help="Specific price for analysis")
    parser.add_argument("--export", action="store_true", help="Export sample analysis data")

    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.export:
        export_sample_data()
    elif args.token:
        run_live_analysis(args.token, args.price)
    else:
        print("VOTS Burn Mechanism Market Analysis")
        print("Usage:")
        print("  python vots_burn_analysis_demo.py --demo          # Run demo")
        print("  python vots_burn_analysis_demo.py --export        # Export samples")
        print("  python vots_burn_analysis_demo.py --token <addr>  # Live analysis")

if __name__ == "__main__":
    main()
