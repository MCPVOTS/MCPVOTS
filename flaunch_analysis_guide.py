"""
FLAUNCH TOKEN ANALYSIS GUIDE
============================

Complete guide for analyzing Flaunch tokens before trading.
Learn what to look for and how to evaluate trading opportunities.
"""

import json
from datetime import datetime
from typing import Dict, List, Any

class FlaunchAnalysisGuide:
    """
    Comprehensive guide for Flaunch token analysis
    """

    def __init__(self):
        self.analysis_criteria = self._load_analysis_criteria()

    def _load_analysis_criteria(self) -> Dict[str, Any]:
        """Load analysis criteria and scoring guidelines"""
        return {
            "profitability_indicators": {
                "market_cap": {
                    "excellent": "< $50K",
                    "good": "$50K - $200K",
                    "moderate": "$200K - $1M",
                    "poor": "> $1M"
                },
                "liquidity": {
                    "excellent": "> $50K",
                    "good": "$10K - $50K",
                    "moderate": "$5K - $10K",
                    "poor": "< $5K"
                },
                "volume_24h": {
                    "excellent": "> $10K",
                    "good": "$5K - $10K",
                    "moderate": "$1K - $5K",
                    "poor": "< $1K"
                },
                "holders": {
                    "excellent": "> 100",
                    "good": "50-100",
                    "moderate": "20-50",
                    "poor": "< 20"
                }
            },
            "risk_factors": {
                "contract_verified": {
                    "safe": True,
                    "risky": False,
                    "impact": "high"
                },
                "liquidity_locked": {
                    "safe": True,
                    "risky": False,
                    "impact": "critical"
                },
                "honeypot_risk": {
                    "safe": "low",
                    "moderate": "medium",
                    "risky": "high",
                    "impact": "critical"
                },
                "owner_concentration": {
                    "safe": "< 5%",
                    "moderate": "5-20%",
                    "risky": "> 20%",
                    "impact": "high"
                },
                "token_age": {
                    "very_risky": "< 1 hour",
                    "risky": "1-24 hours",
                    "moderate": "24-72 hours",
                    "safe": "> 72 hours"
                }
            },
            "social_signals": {
                "twitter_mentions": {
                    "excellent": "> 50",
                    "good": "20-50",
                    "moderate": "5-20",
                    "poor": "< 5"
                },
                "telegram_members": {
                    "excellent": "> 1000",
                    "good": "500-1000",
                    "moderate": "100-500",
                    "poor": "< 100"
                },
                "sentiment_score": {
                    "excellent": "> 0.8",
                    "good": "0.6-0.8",
                    "moderate": "0.4-0.6",
                    "poor": "< 0.4"
                }
            },
            "trading_recommendations": {
                "STRONG_BUY": {
                    "criteria": "Profit > 70, Risk < 30, Social > 70",
                    "allocation": "$2-3 per trade",
                    "rationale": "Excellent fundamentals with low risk"
                },
                "BUY": {
                    "criteria": "Profit > 50, Risk < 50, Social > 50",
                    "allocation": "$1-2 per trade",
                    "rationale": "Good profit potential with acceptable risk"
                },
                "WATCH": {
                    "criteria": "Profit > 30, Risk < 60",
                    "allocation": "$0.50-1 per trade",
                    "rationale": "Moderate potential, monitor closely"
                },
                "PASS_LOW_POTENTIAL": {
                    "criteria": "Profit < 30",
                    "allocation": "$0",
                    "rationale": "Low profit potential"
                },
                "AVOID_HIGH_RISK": {
                    "criteria": "Risk > 70",
                    "allocation": "$0",
                    "rationale": "High risk factors detected"
                }
            }
        }

    def print_analysis_guide(self):
        """Print the complete analysis guide"""
        print("🔍 FLAUNCH TOKEN ANALYSIS GUIDE")
        print("=" * 50)
        print()

        print("📊 PROFITABILITY INDICATORS:")
        print("-" * 30)
        for metric, levels in self.analysis_criteria["profitability_indicators"].items():
            print(f"\n{metric.upper()}:")
            for level, threshold in levels.items():
                print(f"  {level.capitalize()}: {threshold}")

        print("\n\n⚠️ RISK FACTORS:")
        print("-" * 30)
        for factor, details in self.analysis_criteria["risk_factors"].items():
            print(f"\n{factor.upper().replace('_', ' ')}:")
            if "safe" in details:
                print(f"  Safe: {details['safe']}")
            if "risky" in details:
                print(f"  Risky: {details['risky']}")
            if "impact" in details:
                print(f"  Impact: {details['impact'].capitalize()}")

        print("\n\n📱 SOCIAL SIGNALS:")
        print("-" * 30)
        for signal, levels in self.analysis_criteria["social_signals"].items():
            print(f"\n{signal.upper().replace('_', ' ')}:")
            for level, threshold in levels.items():
                print(f"  {level.capitalize()}: {threshold}")

        print("\n\n💡 TRADING RECOMMENDATIONS:")
        print("-" * 30)
        for rec_type, details in self.analysis_criteria["trading_recommendations"].items():
            print(f"\n{rec_type}:")
            print(f"  Criteria: {details['criteria']}")
            print(f"  Allocation: {details['allocation']}")
            print(f"  Rationale: {details['rationale']}")

        print("\n\n🎯 ANALYSIS CHECKLIST:")
        print("-" * 30)
        self.print_analysis_checklist()

    def print_analysis_checklist(self):
        """Print a practical checklist for token analysis"""
        checklist = [
            "✅ Verify contract is verified on BaseScan",
            "✅ Check if liquidity is locked (critical for safety)",
            "✅ Assess honeypot risk using tools like DexTools",
            "✅ Review token distribution and owner concentration",
            "✅ Check token age (prefer > 24 hours)",
            "✅ Analyze liquidity depth (> $10K preferred)",
            "✅ Review 24h volume (> $5K shows interest)",
            "✅ Check holder count (> 50 shows distribution)",
            "✅ Monitor social media mentions and sentiment",
            "✅ Review recent transactions for wash trading",
            "✅ Check for audit reports if available",
            "✅ Verify fair launch (no large pre-sales)",
            "✅ Assess team transparency and communication",
            "✅ Check for red flags (anonymous team, no roadmap)",
            "✅ Calculate position size based on risk tolerance",
            "✅ Set stop-loss and take-profit levels",
            "✅ Consider market conditions and timing"
        ]

        for item in checklist:
            print(f"  {item}")

    def get_quick_analysis_tips(self) -> List[str]:
        """Get quick analysis tips for beginners"""
        return [
            "🔴 NEVER invest more than you can afford to lose",
            "🔴 Always verify contracts on BaseScan first",
            "🔴 Check liquidity locks - this prevents rug pulls",
            "🔴 Look for tokens with > $10K liquidity minimum",
            "🔴 Prefer tokens with > 50 holders for distribution",
            "🔴 Watch for high owner concentration (>20% = red flag)",
            "🔴 Check social sentiment before investing",
            "🔴 Start small - $1-2 per trade maximum",
            "🔴 Set stop losses to protect your capital",
            "🔴 Take profits regularly, don't be greedy",
            "🔴 Research the team and their previous projects",
            "🔴 Avoid tokens with anonymous teams",
            "🔴 Check for audit reports when available",
            "🔴 Monitor volume - consistent volume shows real interest",
            "🔴 Be patient - good opportunities take time to find",
            "🔴 Use multiple analysis tools, don't rely on one source"
        ]

    def analyze_token_quick_check(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a quick analysis check on token data
        """
        result = {
            "overall_score": 0,
            "risk_level": "unknown",
            "recommendation": "NEEDS_MORE_ANALYSIS",
            "concerns": [],
            "positives": []
        }

        # Check liquidity
        liquidity = token_data.get("liquidity", 0)
        if liquidity > 50000:
            result["overall_score"] += 25
            result["positives"].append("Excellent liquidity")
        elif liquidity > 10000:
            result["overall_score"] += 15
            result["positives"].append("Good liquidity")
        elif liquidity < 5000:
            result["concerns"].append("Low liquidity - high risk")

        # Check holders
        holders = token_data.get("holders", 0)
        if holders > 100:
            result["overall_score"] += 20
            result["positives"].append("Well distributed")
        elif holders > 50:
            result["overall_score"] += 10
            result["positives"].append("Reasonably distributed")
        elif holders < 20:
            result["concerns"].append("Few holders - concentration risk")

        # Check volume
        volume = token_data.get("volume_24h", 0)
        if volume > 10000:
            result["overall_score"] += 20
            result["positives"].append("High trading volume")
        elif volume > 5000:
            result["overall_score"] += 10
            result["positives"].append("Moderate volume")
        elif volume < 1000:
            result["concerns"].append("Low volume - potential lack of interest")

        # Risk assessment
        risk_score = 0
        if not token_data.get("contract_verified", False):
            risk_score += 30
            result["concerns"].append("Contract not verified")

        if not token_data.get("liquidity_locked", False):
            risk_score += 40
            result["concerns"].append("Liquidity not locked - rug pull risk")

        honeypot = token_data.get("honeypot_risk", "unknown")
        if honeypot == "high":
            risk_score += 50
            result["concerns"].append("High honeypot risk")

        # Determine risk level
        if risk_score > 70:
            result["risk_level"] = "HIGH"
        elif risk_score > 30:
            result["risk_level"] = "MEDIUM"
        else:
            result["risk_level"] = "LOW"

        # Generate recommendation
        if result["risk_level"] == "HIGH":
            result["recommendation"] = "AVOID"
        elif result["overall_score"] > 40 and result["risk_level"] != "HIGH":
            result["recommendation"] = "CONSIDER"
        else:
            result["recommendation"] = "MONITOR"

        return result

def print_pre_trade_checklist():
    """Print a comprehensive pre-trade checklist"""
    print("🚀 FLAUNCH PRE-TRADE CHECKLIST")
    print("=" * 40)
    print()

    checklist_sections = {
        "🔍 DUE DILIGENCE": [
            "☐ Contract verified on BaseScan?",
            "☐ Liquidity locked? (Check on DexTools/Uniswap)",
            "☐ Honeypot check passed? (Use go.plus or similar)",
            "☐ Token distribution checked? (No >20% owner concentration)",
            "☐ Team doxxed and contactable?",
            "☐ Previous projects reviewed?",
            "☐ Audit report available?"
        ],
        "📊 FUNDAMENTAL ANALYSIS": [
            "☐ Market cap reasonable? (<$200K preferred)",
            "☐ Liquidity adequate? (>$10K minimum)",
            "☐ 24h volume shows interest? (>$5K preferred)",
            "☐ Holder count distributed? (>50 holders)",
            "☐ Token age >24 hours?",
            "☐ Fair launch? (No large pre-sales)"
        ],
        "📱 SOCIAL ANALYSIS": [
            "☐ Twitter/Telegram presence?",
            "☐ Community size reasonable?",
            "☐ Sentiment positive?",
            "☐ No red flags in community?",
            "☐ Marketing authentic, not paid promotion?"
        ],
        "💰 RISK MANAGEMENT": [
            "☐ Position size ≤1% of trading capital?",
            "☐ Stop loss set? (20-50% below entry)",
            "☐ Take profit levels defined?",
            "☐ ETH reserve maintained? ($5 minimum)",
            "☐ Emergency exit plan ready?",
            "☐ Maximum loss per trade defined?"
        ],
        "⚡ EXECUTION CHECKS": [
            "☐ Gas fees reasonable?",
            "☐ Slippage settings appropriate? (5-10%)",
            "☐ Trading wallet has sufficient ETH?",
            "☐ Buy/sell limits set correctly?",
            "☐ Test transaction with small amount first?"
        ]
    }

    for section, items in checklist_sections.items():
        print(f"{section}")
        print("-" * len(section))
        for item in items:
            print(f"  {item}")
        print()

    print("💡 PRO TIPS:")
    print("  • Never invest more than you can afford to lose")
    print("  • Start with small positions ($1-2) to test")
    print("  • Take profits regularly - don't hold forever")
    print("  • Use multiple wallets for different risk levels")
    print("  • Keep detailed trading records")
    print("  • Learn from both wins and losses")
    print()

def main():
    """Main guide function"""
    guide = FlaunchAnalysisGuide()

    print("🚀 FLAUNCH TOKEN TRADING ANALYSIS GUIDE")
    print("=" * 50)
    print("Complete guide for safe and profitable Flaunch trading")
    print()

    # Print the comprehensive guide
    guide.print_analysis_guide()

    print("\n\n" + "="*50)
    print("⚡ QUICK ANALYSIS TIPS:")
    print("-" * 30)
    for tip in guide.get_quick_analysis_tips():
        print(f"  {tip}")

    print("\n\n" + "="*50)
    print_pre_trade_checklist()

if __name__ == "__main__":
    main()
