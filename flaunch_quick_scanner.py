"""
FLAUNCH QUICK TOKEN SCANNER
===========================

Fast token analysis for quick trading decisions.
Analyze multiple tokens rapidly before making trades.
"""

import asyncio
import sys
import time
from typing import List, Dict, Any
from flaunch_token_analyzer import FlaunchTokenAnalyzer, TokenAnalysis
from flaunch_analysis_guide import FlaunchAnalysisGuide

class FlaunchQuickScanner:
    """
    Fast token scanning for quick analysis
    """

    def __init__(self):
        self.analyzer = FlaunchTokenAnalyzer()
        self.guide = FlaunchAnalysisGuide()

    async def quick_scan_token(self, token_address: str) -> Dict[str, Any]:
        """
        Perform a quick scan of a single token
        """
        print(f"🔍 Quick scanning: {token_address[:12]}...")

        # Get basic analysis
        analysis = await self.analyzer.analyze_token(token_address)

        # Get quick check result
        token_data = {
            "liquidity": analysis.liquidity,
            "holders": analysis.holders,
            "volume_24h": analysis.volume_24h,
            "contract_verified": analysis.key_metrics.get("contract_verified", False),
            "liquidity_locked": analysis.key_metrics.get("liquidity_locked", False),
            "honeypot_risk": analysis.key_metrics.get("honeypot_risk", "unknown")
        }

        quick_result = self.guide.analyze_token_quick_check(token_data)

        return {
            "token": f"{analysis.token_name} ({analysis.symbol})",
            "address": token_address,
            "profit_potential": analysis.profit_potential,
            "risk_score": analysis.risk_score,
            "recommendation": analysis.recommendation,
            "quick_check": quick_result,
            "key_metrics": {
                "liquidity": f"${analysis.liquidity:.0f}",
                "holders": analysis.holders,
                "volume": f"${analysis.volume_24h:.0f}",
                "price_change": f"{analysis.price_change_24h:.1f}%"
            }
        }

    async def scan_multiple_tokens(self, token_addresses: List[str]) -> List[Dict[str, Any]]:
        """
        Scan multiple tokens in parallel
        """
        print(f"🚀 Scanning {len(token_addresses)} tokens...")

        # Scan all tokens in parallel
        tasks = [self.quick_scan_token(address) for address in token_addresses]
        results = await asyncio.gather(*tasks)

        # Sort by profit potential
        results.sort(key=lambda x: x["profit_potential"], reverse=True)

        return results

    def print_scan_results(self, results: List[Dict[str, Any]]):
        """
        Print formatted scan results
        """
        print("\n📊 FLAUNCH TOKEN SCAN RESULTS")
        print("=" * 50)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['token']}")
            print(f"   Address: {result['address']}")
            print(f"   Profit Potential: {result['profit_potential']:.1f}/100")
            print(f"   Risk: {result['risk_score']:.1f}/100")
            print(f"   Recommendation: {result['recommendation']}")

            # Quick check summary
            qc = result['quick_check']
            print(f"   Quick Check: {qc['recommendation']} ({qc['risk_level']} risk)")

            # Key metrics
            km = result['key_metrics']
            print(f"   Liquidity: {km['liquidity']} | Holders: {km['holders']} | Volume: {km['volume']}")

            # Show top concerns/positives
            if qc['concerns']:
                print(f"   ⚠️ Concerns: {', '.join(qc['concerns'][:2])}")
            if qc['positives']:
                print(f"   ✅ Positives: {', '.join(qc['positives'][:2])}")

            print()

def get_example_tokens() -> List[str]:
    """Get example tokens for scanning"""
    return [
        "0x84ce8BfDC3B3006c6d40d81db16B53f9e81C8B70",  # User's wallet
        "0x1234567890123456789012345678901234567890",  # Example 1
        "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",  # Example 2
        "0x9876543210987654321098765432109876543210",  # Example 3
        "0xfedcba0987654321fedcba0987654321fedcba0987",  # Example 4
    ]

async def main():
    """Main scanner function"""
    scanner = FlaunchQuickScanner()

    print("⚡ FLAUNCH QUICK TOKEN SCANNER")
    print("=" * 40)
    print("Fast analysis for quick trading decisions")
    print()

    # Get tokens to scan
    if len(sys.argv) > 1:
        # Use command line arguments as token addresses
        tokens_to_scan = sys.argv[1:]
    else:
        # Use example tokens
        print("🔍 Using example tokens for demonstration...")
        tokens_to_scan = get_example_tokens()

    print(f"🎯 Scanning {len(tokens_to_scan)} tokens...")
    print()

    # Perform scan
    start_time = time.time()
    results = await scanner.scan_multiple_tokens(tokens_to_scan)
    scan_time = time.time() - start_time

    # Print results
    scanner.print_scan_results(results)

    print(f"⏱️ Scan completed in {scan_time:.2f} seconds")
    print("\n💡 INTERPRETING RESULTS:")
    print("-" * 30)
    print("• STRONG_BUY: Excellent opportunity, consider $2-3 allocation")
    print("• BUY: Good potential, $1-2 allocation recommended")
    print("• WATCH: Monitor closely, small position possible")
    print("• PASS_LOW_POTENTIAL: Skip this token")
    print("• AVOID_HIGH_RISK: High risk, do not trade")
    print()
    print("⚠️ REMEMBER: Always do full due diligence before trading!")
    print("🔗 Use flaunch_token_analyzer.py for detailed analysis")

if __name__ == "__main__":
    asyncio.run(main())
