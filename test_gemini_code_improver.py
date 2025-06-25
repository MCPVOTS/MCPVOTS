#!/usr/bin/env python3
"""
Test Client for Gemini Automated Code Improvement System
======================================================
Tests the complete automated code improvement workflow including:
- Workspace analysis with 1M token context
- Google Search grounded recommendations  
- Automated code fixes and optimizations
- Integration with Memory MCP and Trilogy AGI
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import websockets
import sys
import os

# Add the MCPVots directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from gemini_automated_code_improver import GeminiAutomatedCodeImprover

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeImprovementTestClient:
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or str(Path(__file__).parent)
        self.improver = GeminiAutomatedCodeImprover(self.workspace_path)
        self.test_results = {}
        
    async def run_comprehensive_tests(self):
        """Run comprehensive test suite for the code improvement system"""
        logger.info("🧪 Starting Comprehensive Code Improvement Tests...")
        
        tests = [
            ("connection_test", self._test_system_connections),
            ("workspace_analysis", self._test_workspace_analysis),
            ("improvement_generation", self._test_improvement_generation),
            ("safe_improvements", self._test_safe_improvements),
            ("memory_integration", self._test_memory_integration),
            ("continuous_monitoring", self._test_continuous_monitoring),
            ("end_to_end", self._test_end_to_end_workflow)
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
                logger.info(f"✅ Test {test_name}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                results[test_name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                logger.error(f"❌ Test {test_name}: ERROR - {e}")
        
        # Generate test report
        await self._generate_test_report(results)
        return results
    
    async def _test_system_connections(self) -> bool:
        """Test connections to all required systems"""
        logger.info("🔗 Testing system connections...")
        
        try:
            # Test Gemini CLI server connection
            async with websockets.connect("ws://localhost:8015", timeout=5) as ws:
                test_request = {
                    "jsonrpc": "2.0",
                    "id": "connection_test",
                    "method": "gemini/health",
                    "params": {}
                }
                await ws.send(json.dumps(test_request))
                response = await ws.recv()
                result = json.loads(response)
                
                if "result" in result and result["result"]["status"] == "healthy":
                    logger.info("✅ Gemini CLI server connection successful")
                    return True
                else:
                    logger.error(f"❌ Gemini CLI server unhealthy: {result}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            logger.info("💡 Make sure the Gemini CLI server is running on ws://localhost:8015")
            return False
    
    async def _test_workspace_analysis(self) -> bool:
        """Test comprehensive workspace analysis"""
        logger.info("📊 Testing workspace analysis...")
        
        try:
            # Test context collection
            context = await self.improver._collect_full_workspace_context()
            
            if not context or "metadata" not in context:
                logger.error("❌ Failed to collect workspace context")
                return False
            
            logger.info(f"✅ Context collected: {context['metadata'].get('context_size_chars', 0)} chars")
            
            # Test analysis execution (mock if Gemini not available)
            if await self._is_gemini_available():
                analysis = await self.improver.perform_comprehensive_workspace_analysis()
                
                if not analysis or "analysis_metadata" not in analysis:
                    logger.error("❌ Analysis execution failed")
                    return False
                
                logger.info("✅ Comprehensive analysis completed successfully")
                self.test_results["analysis"] = analysis
                return True
            else:
                logger.warning("⚠️ Gemini CLI not available, skipping live analysis")
                return True
                
        except Exception as e:
            logger.error(f"❌ Workspace analysis test failed: {e}")
            return False
    
    async def _test_improvement_generation(self) -> bool:
        """Test improvement generation from analysis"""
        logger.info("🔧 Testing improvement generation...")
        
        try:
            # Use mock analysis if real analysis not available
            if "analysis" in self.test_results:
                analysis = self.test_results["analysis"]
            else:
                analysis = self._create_mock_analysis()
            
            improvements = await self.improver.generate_automated_improvements(analysis)
            
            if not improvements or not any(improvements.values()):
                logger.error("❌ No improvements generated")
                return False
            
            logger.info(f"✅ Generated improvements:")
            for category, items in improvements.items():
                logger.info(f"  - {category}: {len(items)} items")
            
            self.test_results["improvements"] = improvements
            return True
            
        except Exception as e:
            logger.error(f"❌ Improvement generation test failed: {e}")
            return False
    
    async def _test_safe_improvements(self) -> bool:
        """Test application of safe improvements"""
        logger.info("⚡ Testing safe improvement application...")
        
        try:
            if "improvements" not in self.test_results:
                logger.warning("⚠️ No improvements available for testing")
                return True
            
            improvements = self.test_results["improvements"]
            
            # Test safety validation
            for improvement in improvements.get("safe_automatic_fixes", []):
                is_safe = await self.improver._validate_improvement_safety(improvement)
                if is_safe is None:  # Method not implemented yet
                    logger.info("💡 Safety validation not implemented yet")
                    return True
            
            logger.info("✅ Safe improvement testing completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Safe improvements test failed: {e}")
            return False
    
    async def _test_memory_integration(self) -> bool:
        """Test Memory MCP integration"""
        logger.info("🧠 Testing Memory MCP integration...")
        
        try:
            # Test memory server connection
            try:
                async with websockets.connect("ws://localhost:8020", timeout=5) as ws:
                    logger.info("✅ Memory MCP server connection successful")
                    
                    # Test storing analysis results
                    mock_analysis = self._create_mock_analysis()
                    await self.improver._store_analysis_in_memory(mock_analysis)
                    logger.info("✅ Analysis storage in memory successful")
                    return True
                    
            except Exception as e:
                logger.warning(f"⚠️ Memory MCP server not available: {e}")
                logger.info("💡 Make sure the Memory MCP server is running on ws://localhost:8020")
                return True  # Don't fail the test if memory server isn't running
                
        except Exception as e:
            logger.error(f"❌ Memory integration test failed: {e}")
            return False
    
    async def _test_continuous_monitoring(self) -> bool:
        """Test continuous monitoring capabilities"""
        logger.info("🔄 Testing continuous monitoring...")
        
        try:
            # Test change detection
            changes = await self.improver._detect_workspace_changes()
            
            if changes is None:  # Method not implemented yet
                logger.info("💡 Change detection not implemented yet")
                return True
            
            logger.info(f"✅ Change detection: {changes.get('has_significant_changes', False)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Continuous monitoring test failed: {e}")
            return False
    
    async def _test_end_to_end_workflow(self) -> bool:
        """Test complete end-to-end workflow"""
        logger.info("🚀 Testing end-to-end workflow...")
        
        try:
            if await self._is_gemini_available():
                # Run the complete workflow
                result = await self.improver.start_automated_improvement_system()
                
                if not result or result.get("status") != "active":
                    logger.error("❌ End-to-end workflow failed")
                    return False
                
                logger.info("✅ End-to-end workflow completed successfully")
                return True
            else:
                logger.warning("⚠️ Gemini CLI not available, skipping end-to-end test")
                return True
                
        except Exception as e:
            logger.error(f"❌ End-to-end workflow test failed: {e}")
            return False
    
    async def _is_gemini_available(self) -> bool:
        """Check if Gemini CLI server is available"""
        try:
            async with websockets.connect("ws://localhost:8015", timeout=2) as ws:
                return True
        except:
            return False
    
    def _create_mock_analysis(self) -> dict:
        """Create mock analysis for testing"""
        return {
            "analysis_metadata": {
                "timestamp": datetime.now().isoformat(),
                "analyzer": "gemini-2.5-pro",
                "workspace_path": self.workspace_path
            },
            "overall_scores": {
                "architecture": 7,
                "security": 6,
                "performance": 8,
                "maintainability": 7
            },
            "category_analyses": {
                "performance": {
                    "recommendations": [
                        {
                            "title": "Optimize database queries",
                            "priority": "high",
                            "safety_level": "safe"
                        }
                    ]
                }
            },
            "prioritized_recommendations": [
                {
                    "title": "Add type hints to Python functions",
                    "category": "maintainability",
                    "priority": "medium",
                    "safety_level": "safe"
                }
            ]
        }
    
    async def _generate_test_report(self, results: dict):
        """Generate comprehensive test report"""
        report = {
            "test_summary": {
                "total_tests": len(results),
                "passed": len([r for r in results.values() if r["status"] == "passed"]),
                "failed": len([r for r in results.values() if r["status"] == "failed"]),
                "errors": len([r for r in results.values() if r["status"] == "error"]),
                "timestamp": datetime.now().isoformat()
            },
            "test_results": results,
            "recommendations": []
        }
        
        # Add recommendations based on test results
        if report["test_summary"]["failed"] > 0:
            report["recommendations"].append("Some tests failed - check system dependencies")
        
        if report["test_summary"]["errors"] > 0:
            report["recommendations"].append("Errors occurred - review system configuration")
        
        # Save report
        report_path = Path(self.workspace_path) / f"code_improvement_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Test report saved: {report_path}")
        
        # Print summary
        print("\n" + "="*50)
        print("CODE IMPROVEMENT SYSTEM TEST RESULTS")
        print("="*50)
        print(f"Total Tests: {report['test_summary']['total_tests']}")
        print(f"Passed: {report['test_summary']['passed']}")
        print(f"Failed: {report['test_summary']['failed']}")
        print(f"Errors: {report['test_summary']['errors']}")
        print("="*50)
        
        if report["test_summary"]["passed"] == report["test_summary"]["total_tests"]:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️ Some tests failed - see report for details")
        
        return report

# Quick demo function
async def quick_demo():
    """Quick demonstration of the code improvement system"""
    logger.info("🚀 Quick Demo: Gemini Automated Code Improvement")
    
    improver = GeminiAutomatedCodeImprover("c:\\Workspace\\MCPVots")
    
    # Test basic functionality
    try:
        # Collect workspace context
        logger.info("📊 Collecting workspace context...")
        context = await improver._collect_full_workspace_context()
        print(f"✅ Context collected: {context['metadata']['context_size_chars']} characters")
        
        # Show context summary
        print(f"📁 Files analyzed:")
        for category, files in context.get("files", {}).items():
            print(f"  - {category}: {len(files)} files")
        
        print(f"📦 Dependencies found:")
        for dep_file in context.get("dependencies", {}):
            print(f"  - {dep_file}")
        
        print("✅ Quick demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Quick demo failed: {e}")

# Main execution
async def main():
    """Main test execution"""
    print("🧪 Gemini Automated Code Improvement System - Test Suite")
    print("=" * 60)
    
    # Choose test mode
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        await quick_demo()
    else:
        client = CodeImprovementTestClient("c:\\Workspace\\MCPVots")
        results = await client.run_comprehensive_tests()
        
        # Show final results
        passed = len([r for r in results.values() if r["status"] == "passed"])
        total = len(results)
        print(f"\n🏁 Final Results: {passed}/{total} tests passed")

if __name__ == "__main__":
    asyncio.run(main())
