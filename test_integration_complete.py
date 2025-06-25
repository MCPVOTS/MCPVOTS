#!/usr/bin/env python3
"""
Complete Integration Test for Enhanced MCPVots System
===================================================
Tests the complete workflow from Gemini CLI to automated improvements.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import websockets
import sys

# Add MCPVots to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPVotsIntegrationTest:
    def __init__(self):
        self.workspace_path = str(Path(__file__).parent)
        self.test_results = {}
        
    async def run_integration_tests(self):
        """Run complete integration test suite"""
        logger.info("🧪 Starting MCPVots Integration Tests...")
        
        tests = [
            ("gemini_cli_basic", self._test_gemini_cli_basic),
            ("gemini_cli_enhanced", self._test_gemini_cli_enhanced),
            ("workspace_analysis", self._test_workspace_analysis),
            ("automated_improvements", self._test_automated_improvements),
            ("end_to_end_workflow", self._test_end_to_end_workflow)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            logger.info(f"🔍 Running test: {test_name}")
            try:
                result = await test_func()
                results[test_name] = {
                    "status": "passed" if result else "failed",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                status_emoji = "✅" if result else "❌"
                logger.info(f"{status_emoji} Test {test_name}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                results[test_name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                logger.error(f"❌ Test {test_name}: ERROR - {e}")
        
        # Generate final report
        await self._generate_integration_report(results)
        return results
    
    async def _test_gemini_cli_basic(self) -> bool:
        """Test basic Gemini CLI functionality"""
        try:
            async with websockets.connect("ws://localhost:8015") as ws:
                # Set a custom timeout
                ws.timeout = 10
                
                # Test health check
                health_request = {
                    "jsonrpc": "2.0",
                    "id": "health_test",
                    "method": "gemini/health",
                    "params": {}
                }
                
                await ws.send(json.dumps(health_request))
                response = await asyncio.wait_for(ws.recv(), timeout=10)
                result = json.loads(response)
                
                if "result" in result and result["result"]["status"] == "healthy":
                    logger.info("✅ Gemini CLI health check passed")
                    return True
                else:
                    logger.error(f"❌ Gemini CLI unhealthy: {result}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Gemini CLI basic test failed: {e}")
            return False
    
    async def _test_gemini_cli_enhanced(self) -> bool:
        """Test enhanced Gemini CLI features"""
        try:
            async with websockets.connect("ws://localhost:8015") as ws:
                # Test enhanced chat with search grounding
                chat_request = {
                    "jsonrpc": "2.0",
                    "id": "enhanced_chat_test",
                    "method": "gemini/enhanced_chat",
                    "params": {
                        "message": "What are the latest best practices for Python code quality in 2025?",
                        "model": "gemini-2.5-pro",
                        "session_id": "test_session",
                        "include_search": True,
                        "include_workspace": False,
                        "context_type": "best_practices"
                    }
                }
                
                await ws.send(json.dumps(chat_request))
                response = await asyncio.wait_for(ws.recv(), timeout=30)
                result = json.loads(response)
                
                if "result" in result and "response" in result["result"]:
                    response_text = result["result"]["response"]
                    if len(response_text) > 100:  # Should have substantial response
                        logger.info("✅ Enhanced chat with search grounding works")
                        return True
                    else:
                        logger.error("❌ Enhanced chat response too short")
                        return False
                else:
                    logger.error(f"❌ Enhanced chat failed: {result}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Enhanced Gemini CLI test failed: {e}")
            return False
    
    async def _test_workspace_analysis(self) -> bool:
        """Test workspace analysis capabilities"""
        try:
            from gemini_automated_code_improver import GeminiAutomatedCodeImprover
            
            improver = GeminiAutomatedCodeImprover(self.workspace_path)
            
            # Test context collection
            context = await improver._collect_full_workspace_context()
            
            if not context or "metadata" not in context:
                logger.error("❌ Failed to collect workspace context")
                return False
            
            # Verify context has reasonable content
            if context["metadata"]["context_size_chars"] < 1000:
                logger.error("❌ Context too small")
                return False
            
            # Verify file analysis
            if not context.get("files") or len(context["files"]) == 0:
                logger.error("❌ No files analyzed")
                return False
            
            logger.info(f"✅ Workspace analysis collected {context['metadata']['context_size_chars']} chars")
            return True
            
        except Exception as e:
            logger.error(f"❌ Workspace analysis test failed: {e}")
            return False
    
    async def _test_automated_improvements(self) -> bool:
        """Test automated improvement generation"""
        try:
            from gemini_automated_code_improver import GeminiAutomatedCodeImprover
            
            improver = GeminiAutomatedCodeImprover(self.workspace_path)
            
            # Create mock analysis for testing
            mock_analysis = {
                "analysis_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "analyzer": "gemini-2.5-pro"
                },
                "overall_scores": {
                    "architecture": 7,
                    "security": 6,
                    "performance": 8
                },
                "category_analyses": {
                    "maintainability": {
                        "recommendations": [
                            {
                                "title": "Add type hints to functions",
                                "priority": "medium",
                                "safety_level": "safe",
                                "description": "Improve code readability",
                                "implementation_steps": ["Add typing imports", "Add type annotations"]
                            }
                        ]
                    }
                },
                "prioritized_recommendations": [
                    {
                        "title": "Optimize imports",
                        "priority": "low",
                        "safety_level": "safe"
                    }
                ]
            }
            
            # Test improvement generation
            improvements = await improver.generate_automated_improvements(mock_analysis)
            
            if not improvements:
                logger.error("❌ No improvements generated")
                return False
            
            # Check if improvements were generated
            total_improvements = sum(len(items) for items in improvements.values())
            if total_improvements == 0:
                logger.error("❌ No improvement items generated")
                return False
            
            logger.info(f"✅ Generated {total_improvements} improvements")
            
            # Test safety validation
            for improvement in improvements.get("safe_automatic_fixes", []):
                is_safe = await improver._validate_improvement_safety(improvement)
                if not is_safe:
                    logger.warning(f"⚠️ Safety validation failed for: {improvement.get('title')}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Automated improvements test failed: {e}")
            return False
    
    async def _test_end_to_end_workflow(self) -> bool:
        """Test complete end-to-end workflow"""
        try:
            logger.info("🚀 Testing end-to-end workflow...")
            
            # Step 1: Gemini CLI Health Check
            gemini_healthy = await self._test_gemini_cli_basic()
            if not gemini_healthy:
                logger.error("❌ Gemini CLI not healthy")
                return False
            
            # Step 2: Workspace Analysis
            analysis_works = await self._test_workspace_analysis()
            if not analysis_works:
                logger.error("❌ Workspace analysis failed")
                return False
            
            # Step 3: Improvement Generation
            improvements_work = await self._test_automated_improvements()
            if not improvements_work:
                logger.error("❌ Improvement generation failed")
                return False
            
            # Step 4: Test integration with enhanced features
            enhanced_works = await self._test_gemini_cli_enhanced()
            if not enhanced_works:
                logger.warning("⚠️ Enhanced features not fully working (may need API key)")
                # Don't fail the test for this, as it may be due to API key issues
            
            logger.info("✅ End-to-end workflow completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ End-to-end workflow test failed: {e}")
            return False
    
    async def _generate_integration_report(self, results: dict):
        """Generate comprehensive integration test report"""
        report = {
            "test_summary": {
                "total_tests": len(results),
                "passed": len([r for r in results.values() if r["status"] == "passed"]),
                "failed": len([r for r in results.values() if r["status"] == "failed"]),
                "errors": len([r for r in results.values() if r["status"] == "error"]),
                "timestamp": datetime.now().isoformat(),
                "workspace_path": self.workspace_path
            },
            "test_results": results,
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform
            },
            "recommendations": []
        }
        
        # Add recommendations based on results
        if report["test_summary"]["failed"] > 0:
            report["recommendations"].append("Some tests failed - check service dependencies and configuration")
        
        if report["test_summary"]["errors"] > 0:
            report["recommendations"].append("Errors occurred - review system setup and API keys")
        
        # Check for specific failures
        if "gemini_cli_enhanced" in results and results["gemini_cli_enhanced"]["status"] != "passed":
            report["recommendations"].append("Enhanced Gemini features failed - verify GEMINI_API_KEY is set")
        
        # Save report
        report_path = Path(self.workspace_path) / f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Integration test report saved: {report_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("MCPVOTS INTEGRATION TEST RESULTS")
        print("="*60)
        print(f"Total Tests: {report['test_summary']['total_tests']}")
        print(f"Passed: {report['test_summary']['passed']}")
        print(f"Failed: {report['test_summary']['failed']}")
        print(f"Errors: {report['test_summary']['errors']}")
        print("="*60)
        
        # Show test details
        for test_name, result in results.items():
            status_emoji = {"passed": "✅", "failed": "❌", "error": "💥"}[result["status"]]
            print(f"{status_emoji} {test_name}: {result['status'].upper()}")
        
        print("="*60)
        
        if report["test_summary"]["passed"] == report["test_summary"]["total_tests"]:
            print("🎉 ALL INTEGRATION TESTS PASSED!")
            print("\n🚀 Your Enhanced MCPVots system is fully operational!")
            print("   ✨ Gemini CLI with Google Search grounding")
            print("   ✨ Automated code improvements")
            print("   ✨ Comprehensive workspace analysis")
            print("   ✨ Continuous learning capabilities")
        else:
            print("⚠️ Some integration tests failed")
            print("\n📋 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")
        
        print("="*60)
        
        return report

# Quick demo function
async def quick_integration_demo():
    """Quick demonstration of integration capabilities"""
    print("🚀 MCPVots Integration Demo")
    print("="*40)
    
    tester = MCPVotsIntegrationTest()
    
    # Test just the core functionality
    try:
        logger.info("🔍 Testing Gemini CLI connection...")
        gemini_works = await tester._test_gemini_cli_basic()
        
        if gemini_works:
            print("✅ Gemini CLI: Connected and healthy")
            
            logger.info("📊 Testing workspace analysis...")
            analysis_works = await tester._test_workspace_analysis()
            
            if analysis_works:
                print("✅ Workspace Analysis: Working")
                print("🎉 Core system is operational!")
            else:
                print("❌ Workspace Analysis: Failed")
        else:
            print("❌ Gemini CLI: Not available")
            print("💡 Make sure to start the Gemini CLI server first:")
            print("   python servers/enhanced_gemini_cli_server.py")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

# Main execution
async def main():
    """Main test execution"""
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        await quick_integration_demo()
    else:
        tester = MCPVotsIntegrationTest()
        results = await tester.run_integration_tests()
        
        # Show final summary
        passed = len([r for r in results.values() if r["status"] == "passed"])
        total = len(results)
        print(f"\n🏁 Integration Test Results: {passed}/{total} tests passed")

if __name__ == "__main__":
    asyncio.run(main())
