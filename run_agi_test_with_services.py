#!/usr/bin/env python3
"""
AGI Ecosystem Test Runner with Service Auto-Start
================================================
This script automatically starts required AGI services and then runs the comprehensive test.
It's designed to work on Windows and handle Unicode encoding issues gracefully.
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_ecosystem_orchestrator import ComprehensiveEcosystemOrchestrator
from test_agi_ecosystem_comprehensive import AGIEcosystemTester, safe_log

# Configure logging for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agi_test_runner.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AGITestRunner:
    def __init__(self):
        self.orchestrator = ComprehensiveEcosystemOrchestrator()
        self.tester = AGIEcosystemTester()
        
    async def run_with_service_startup(self):
        """Run tests with automatic service startup"""
        logger.info(safe_log("🚀 Starting AGI Ecosystem Test Runner"))
        
        try:
            # Step 1: Start the ecosystem services
            logger.info("Starting AGI ecosystem services...")
            startup_result = await self.orchestrator.start_comprehensive_ecosystem()
            
            if startup_result.get("success", False):
                logger.info(safe_log("✅ AGI ecosystem services started successfully"))
                
                # Wait a bit for services to fully initialize
                logger.info("Waiting for services to initialize...")
                await asyncio.sleep(10)
                
            else:
                logger.warning(safe_log("⚠️ Some services may not have started properly"))
                logger.info("Proceeding with tests to check service status...")
            
            # Step 2: Run comprehensive tests
            logger.info(safe_log("🧪 Running comprehensive AGI ecosystem tests"))
            test_report = await self.tester.run_comprehensive_test()
            
            # Step 3: Display results
            summary = test_report.get("test_summary", {})
            logger.info(safe_log(f"""
🎯 TEST EXECUTION COMPLETE:
- Success Rate: {summary.get('success_rate_percent', 0):.1f}%
- Total Duration: {summary.get('total_duration_seconds', 0):.2f}s
- Ecosystem Status: {summary.get('ecosystem_status', 'unknown').upper()}
- Services Running: {summary.get('healthy_services', 0)}/{summary.get('total_services', 0)}
"""))
            
            # Provide actionable feedback
            if summary.get('success_rate_percent', 0) >= 70:
                logger.info(safe_log("🎉 AGI Ecosystem is functioning well!"))
            elif summary.get('success_rate_percent', 0) >= 40:
                logger.info(safe_log("⚠️ AGI Ecosystem is partially functional"))
                self._print_recommendations(test_report)
            else:
                logger.warning(safe_log("🚨 AGI Ecosystem needs attention"))
                self._print_recommendations(test_report)
            
            return test_report
            
        except Exception as e:
            logger.error(safe_log(f"❌ Test runner failed: {e}"))
            return {"success": False, "error": str(e)}
    
    def _print_recommendations(self, test_report: Dict[str, Any]):
        """Print actionable recommendations"""
        logger.info(safe_log("📋 RECOMMENDATIONS:"))
        
        # Check service health recommendations
        service_health = test_report.get("test_results", {}).get("service_health", {})
        recommendations = service_health.get("recommendations", [])
        
        for i, rec in enumerate(recommendations[:5], 1):  # Show top 5 recommendations
            logger.info(f"  {i}. {rec}")
        
        # Check next steps
        next_steps = test_report.get("next_steps", [])
        if next_steps:
            logger.info(safe_log("📈 NEXT STEPS:"))
            for i, step in enumerate(next_steps[:3], 1):  # Show top 3 next steps
                logger.info(f"  {i}. {step}")

async def main():
    """Main entry point"""
    runner = AGITestRunner()
    
    # Check if we're running with specific arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            logger.info("Running quick test mode (services health check only)")
            # Just run service health test
            tester = AGIEcosystemTester()
            result = await tester._test_service_health()
            
            if result.get("success", False):
                logger.info(safe_log(f"✅ Quick test passed: {result['healthy_services']}/{result['total_services']} services healthy"))
            else:
                logger.warning(safe_log("⚠️ Quick test failed: Issues detected with services"))
                
            return result
    
    # Run full test with service startup
    return await runner.run_with_service_startup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(safe_log(f"❌ Unexpected error: {e}"))
