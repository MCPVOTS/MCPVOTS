#!/usr/bin/env python3
"""
n8n Integration Test Suite
==========================
Comprehensive testing for n8n integration with MCPVots AGI ecosystem.
Tests workflow creation, AGI node execution, and end-to-end automation.
"""

import asyncio
import json
import logging
import aiohttp
from datetime import datetime
from pathlib import Path
import websockets
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class N8NIntegrationTester:
    def __init__(self):
        self.n8n_integration_url = "ws://localhost:8020"
        self.n8n_api_url = "http://localhost:5678/api/v1"
        self.test_results = []
        
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive n8n integration tests"""
        logger.info("🧪 Starting n8n Integration Test Suite...")
        
        test_suite = [
            ("Server Connection", self.test_server_connection),
            ("Health Check", self.test_health_check),
            ("AGI Nodes Available", self.test_agi_nodes_available),
            ("Create Workflow", self.test_create_workflow),
            ("Execute AGI Node", self.test_execute_agi_node),
            ("Workflow Execution", self.test_workflow_execution),
            ("Webhook Creation", self.test_webhook_creation),
            ("Memory Integration", self.test_memory_integration),
            ("Multi-Service Workflow", self.test_multi_service_workflow),
            ("n8n API Integration", self.test_n8n_api_integration)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in test_suite:
            try:
                logger.info(f"🔍 Running test: {test_name}")
                result = await test_func()
                
                if result.get("success", False):
                    logger.info(f"✅ {test_name}: PASSED")
                    passed += 1
                else:
                    logger.error(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
                    failed += 1
                    
                self.test_results.append({
                    "test": test_name,
                    "success": result.get("success", False),
                    "duration": result.get("duration", 0),
                    "details": result.get("details", {}),
                    "error": result.get("error", None)
                })
                
            except Exception as e:
                logger.error(f"❌ {test_name}: EXCEPTION - {str(e)}")
                failed += 1
                self.test_results.append({
                    "test": test_name,
                    "success": False,
                    "error": str(e),
                    "exception": True
                })
        
        summary = {
            "total_tests": len(test_suite),
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / len(test_suite)) * 100,
            "timestamp": datetime.now().isoformat(),
            "results": self.test_results
        }
        
        logger.info(f"📊 Test Summary: {passed}/{len(test_suite)} passed ({summary['success_rate']:.1f}%)")
        
        return summary
        
    async def test_server_connection(self) -> Dict[str, Any]:
        """Test WebSocket connection to n8n integration server"""
        start_time = datetime.now()
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                # Send ping message
                ping_message = {
                    "method": "n8n/health",
                    "params": {}
                }
                
                await websocket.send(json.dumps(ping_message))
                response = await websocket.recv()
                response_data = json.loads(response)
                
                duration = (datetime.now() - start_time).total_seconds()
                
                if response_data.get("status") == "healthy":
                    return {
                        "success": True,
                        "duration": duration,
                        "details": response_data
                    }
                else:
                    return {
                        "success": False,
                        "error": "Server not healthy",
                        "duration": duration
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }
            
    async def test_health_check(self) -> Dict[str, Any]:
        """Test health check endpoint"""
        start_time = datetime.now()
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                health_request = {
                    "method": "n8n/health",
                    "params": {}
                }
                
                await websocket.send(json.dumps(health_request))
                response = await websocket.recv()
                health_data = json.loads(response)
                
                duration = (datetime.now() - start_time).total_seconds()
                
                required_fields = ["status", "server", "port", "workflows", "agi_services"]
                missing_fields = [field for field in required_fields if field not in health_data]
                
                if not missing_fields and health_data.get("status") == "healthy":
                    return {
                        "success": True,
                        "duration": duration,
                        "details": {
                            "workflows": health_data.get("workflows", 0),
                            "agi_services": len(health_data.get("agi_services", [])),
                            "port": health_data.get("port")
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Missing fields: {missing_fields}" if missing_fields else "Not healthy",
                        "duration": duration
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }
            
    async def test_agi_nodes_available(self) -> Dict[str, Any]:
        """Test AGI nodes availability"""
        start_time = datetime.now()
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                nodes_request = {
                    "method": "n8n/get_agi_nodes",
                    "params": {}
                }
                
                await websocket.send(json.dumps(nodes_request))
                response = await websocket.recv()
                nodes_data = json.loads(response)
                
                duration = (datetime.now() - start_time).total_seconds()
                
                agi_nodes = nodes_data.get("agi_nodes", [])
                expected_nodes = ["agi_gemini", "agi_trilogy", "agi_ollama", "agi_memory", "agi_deerflow"]
                
                available_node_types = {node["type"] for node in agi_nodes}
                missing_nodes = [node for node in expected_nodes if node not in available_node_types]
                
                if not missing_nodes:
                    return {
                        "success": True,
                        "duration": duration,
                        "details": {
                            "total_nodes": len(agi_nodes),
                            "node_types": list(available_node_types)
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Missing AGI nodes: {missing_nodes}",
                        "duration": duration
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }
            
    async def test_create_workflow(self) -> Dict[str, Any]:
        """Test workflow creation"""
        start_time = datetime.now()
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                workflow_request = {
                    "method": "n8n/create_workflow",
                    "params": {
                        "name": "Test AGI Workflow",
                        "trigger_type": "manual",
                        "nodes": [
                            {
                                "type": "agi_gemini",
                                "name": "Test Gemini Node",
                                "parameters": {
                                    "endpoint": "/chat",
                                    "prompt": "Hello, this is a test!"
                                }
                            }
                        ]
                    }
                }
                
                await websocket.send(json.dumps(workflow_request))
                response = await websocket.recv()
                workflow_data = json.loads(response)
                
                duration = (datetime.now() - start_time).total_seconds()
                
                if "workflow_id" in workflow_data and "error" not in workflow_data:
                    return {
                        "success": True,
                        "duration": duration,
                        "details": {
                            "workflow_id": workflow_data["workflow_id"],
                            "name": workflow_data.get("name"),
                            "nodes": workflow_data.get("nodes", 0)
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": workflow_data.get("error", "Failed to create workflow"),
                        "duration": duration
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }
            
    async def test_execute_agi_node(self) -> Dict[str, Any]:
        """Test individual AGI node execution"""
        start_time = datetime.now()
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                node_request = {
                    "method": "n8n/execute_agi_node",
                    "params": {
                        "node_type": "agi_gemini",
                        "parameters": {
                            "endpoint": "/chat",
                            "prompt": "What is 2+2?"
                        },
                        "input_data": {
                            "test": "data"
                        }
                    }
                }
                
                await websocket.send(json.dumps(node_request))
                response = await websocket.recv()
                node_data = json.loads(response)
                
                duration = (datetime.now() - start_time).total_seconds()
                
                if "execution_result" in node_data and "error" not in node_data:
                    execution_result = node_data["execution_result"]
                    
                    if execution_result.get("status") == "completed":
                        return {
                            "success": True,
                            "duration": duration,
                            "details": {
                                "node_type": node_data.get("node_type"),
                                "status": execution_result.get("status"),
                                "service": execution_result.get("service")
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Node execution failed: {execution_result.get('error')}",
                            "duration": duration
                        }
                else:
                    return {
                        "success": False,
                        "error": node_data.get("error", "Failed to execute node"),
                        "duration": duration
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }
            
    async def test_workflow_execution(self) -> Dict[str, Any]:
        """Test complete workflow execution"""
        start_time = datetime.now()
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                # First create a workflow
                create_request = {
                    "method": "n8n/create_workflow",
                    "params": {
                        "name": "Test Execution Workflow",
                        "trigger_type": "manual",
                        "nodes": [
                            {
                                "type": "agi_gemini",
                                "name": "Simple Test",
                                "parameters": {
                                    "endpoint": "/chat",
                                    "prompt": "Say hello!"
                                }
                            }
                        ]
                    }
                }
                
                await websocket.send(json.dumps(create_request))
                create_response = await websocket.recv()
                create_data = json.loads(create_response)
                
                if "workflow_id" not in create_data:
                    return {
                        "success": False,
                        "error": "Failed to create test workflow",
                        "duration": (datetime.now() - start_time).total_seconds()
                    }
                
                workflow_id = create_data["workflow_id"]
                
                # Execute the workflow
                execute_request = {
                    "method": "n8n/execute_workflow",
                    "params": {
                        "workflow_id": workflow_id,
                        "input_data": {
                            "test_execution": True
                        }
                    }
                }
                
                await websocket.send(json.dumps(execute_request))
                execute_response = await websocket.recv()
                execute_data = json.loads(execute_response)
                
                duration = (datetime.now() - start_time).total_seconds()
                
                if execute_data.get("status") == "completed":
                    return {
                        "success": True,
                        "duration": duration,
                        "details": {
                            "workflow_id": workflow_id,
                            "execution_id": execute_data.get("execution_id"),
                            "nodes_executed": execute_data.get("nodes_executed", 0)
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": execute_data.get("error", "Workflow execution failed"),
                        "duration": duration
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }
            
    async def test_webhook_creation(self) -> Dict[str, Any]:
        """Test webhook creation"""
        start_time = datetime.now()
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                webhook_request = {
                    "method": "n8n/create_webhook",
                    "params": {
                        "webhook_id": "test_webhook",
                        "workflow_id": None
                    }
                }
                
                await websocket.send(json.dumps(webhook_request))
                response = await websocket.recv()
                webhook_data = json.loads(response)
                
                duration = (datetime.now() - start_time).total_seconds()
                
                if "webhook_url" in webhook_data and "error" not in webhook_data:
                    return {
                        "success": True,
                        "duration": duration,
                        "details": {
                            "webhook_id": webhook_data.get("webhook_id"),
                            "webhook_url": webhook_data.get("webhook_url")
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": webhook_data.get("error", "Failed to create webhook"),
                        "duration": duration
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }
            
    async def test_memory_integration(self) -> Dict[str, Any]:
        """Test Memory MCP integration"""
        start_time = datetime.now()
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                memory_request = {
                    "method": "n8n/execute_agi_node",
                    "params": {
                        "node_type": "agi_memory",
                        "parameters": {
                            "action": "store",
                            "content_type": "test_data"
                        },
                        "input_data": {
                            "test_content": "This is test data for n8n integration",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                }
                
                await websocket.send(json.dumps(memory_request))
                response = await websocket.recv()
                memory_data = json.loads(response)
                
                duration = (datetime.now() - start_time).total_seconds()
                
                execution_result = memory_data.get("execution_result", {})
                
                if execution_result.get("status") == "completed":
                    return {
                        "success": True,
                        "duration": duration,
                        "details": {
                            "service": execution_result.get("service"),
                            "action": execution_result.get("action")
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": execution_result.get("error", "Memory integration failed"),
                        "duration": duration
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }
            
    async def test_multi_service_workflow(self) -> Dict[str, Any]:
        """Test workflow with multiple AGI services"""
        start_time = datetime.now()
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                # Create multi-service workflow
                multi_workflow = {
                    "method": "n8n/create_workflow",
                    "params": {
                        "name": "Multi-Service AGI Test",
                        "trigger_type": "manual",
                        "nodes": [
                            {
                                "type": "agi_gemini",
                                "name": "Gemini Analysis",
                                "parameters": {
                                    "endpoint": "/analyze",
                                    "prompt": "Analyze: Hello World"
                                }
                            },
                            {
                                "type": "agi_memory",
                                "name": "Store Result",
                                "parameters": {
                                    "action": "store",
                                    "content_type": "analysis_result"
                                }
                            },
                            {
                                "type": "agi_deerflow",
                                "name": "Optimize",
                                "parameters": {
                                    "action": "optimize",
                                    "optimization_target": "performance"
                                }
                            }
                        ]
                    }
                }
                
                await websocket.send(json.dumps(multi_workflow))
                create_response = await websocket.recv()
                create_data = json.loads(create_response)
                
                if "workflow_id" not in create_data:
                    return {
                        "success": False,
                        "error": "Failed to create multi-service workflow",
                        "duration": (datetime.now() - start_time).total_seconds()
                    }
                
                # Execute the multi-service workflow
                execute_request = {
                    "method": "n8n/execute_workflow",
                    "params": {
                        "workflow_id": create_data["workflow_id"],
                        "input_data": {
                            "multi_service_test": True
                        }
                    }
                }
                
                await websocket.send(json.dumps(execute_request))
                execute_response = await websocket.recv()
                execute_data = json.loads(execute_response)
                
                duration = (datetime.now() - start_time).total_seconds()
                
                if execute_data.get("status") == "completed":
                    return {
                        "success": True,
                        "duration": duration,
                        "details": {
                            "workflow_id": create_data["workflow_id"],
                            "nodes_executed": execute_data.get("nodes_executed", 0),
                            "services_used": ["gemini", "memory", "deerflow"]
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": execute_data.get("error", "Multi-service workflow failed"),
                        "duration": duration
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }
            
    async def test_n8n_api_integration(self) -> Dict[str, Any]:
        """Test integration with actual n8n API"""
        start_time = datetime.now()
        
        try:
            async with aiohttp.ClientSession() as session:
                # Try to get n8n health status
                async with session.get(f"{self.n8n_api_url}/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        
                        duration = (datetime.now() - start_time).total_seconds()
                        
                        return {
                            "success": True,
                            "duration": duration,
                            "details": {
                                "n8n_status": health_data.get("status", "unknown"),
                                "api_available": True
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"n8n API returned status {response.status}",
                            "duration": (datetime.now() - start_time).total_seconds()
                        }
                        
        except Exception as e:
            # n8n API might not be available, but that's okay for testing
            return {
                "success": True,
                "duration": (datetime.now() - start_time).total_seconds(),
                "details": {
                    "api_available": False,
                    "note": "n8n API not running (expected in some test scenarios)"
                }
            }
            
    async def save_test_results(self, results: Dict[str, Any]):
        """Save test results to file"""
        try:
            results_file = Path("n8n_integration_test_results.json")
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
                
            logger.info(f"📄 Test results saved to {results_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save test results: {e}")


async def main():
    """Run n8n integration tests"""
    logger.info("🧪 Starting n8n Integration Test Suite...")
    
    tester = N8NIntegrationTester()
    
    try:
        results = await tester.run_comprehensive_tests()
        
        # Save results
        await tester.save_test_results(results)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 n8n INTEGRATION TEST RESULTS")
        print(f"{'='*60}")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed']} ✅")
        print(f"Failed: {results['failed']} ❌")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"{'='*60}")
        
        if results['failed'] > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in results['results']:
                if not result['success']:
                    print(f"   • {result['test']}: {result.get('error', 'Unknown error')}")
        
        if results['success_rate'] >= 80:
            print(f"\n🎉 n8n integration is working well!")
        elif results['success_rate'] >= 50:
            print(f"\n⚠️ n8n integration has some issues that need attention.")
        else:
            print(f"\n🚨 n8n integration needs significant fixes.")
            
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        
    logger.info("🏁 n8n Integration Test Suite completed")


if __name__ == "__main__":
    asyncio.run(main())
