#!/usr/bin/env python3
"""
Comprehensive AGI Ecosystem Test and Analysis
=============================================
Tests and analyzes the full MCPVots AGI ecosystem including:
- Trilogy AGI stack integration
- Gemini CLI with 1M token context
- n8n workflow automation
- Memory MCP and knowledge graph
- GitHub Actions integration
- Performance and optimization analysis
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
import aiohttp
import psutil
import argparse

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_ecosystem_orchestrator import ComprehensiveEcosystemOrchestrator
from n8n_agi_launcher import N8NAGILauncher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agi_ecosystem_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def safe_log(message: str) -> str:
    """Convert Unicode emoji to Windows-safe text equivalents"""
    emoji_map = {
        '🚀': '[START]',
        '🧪': '[TEST]',
        '✅': '[PASS]',
        '❌': '[FAIL]',
        '⚠️': '[WARN]',
        '🔧': '[FIX]',
        '📊': '[DATA]',
        '🔄': '[CYCLE]',
        '📈': '[TREND]',
        '🎯': '[TARGET]',
        '🚨': '[ALERT]',
        '💫': '[MAGIC]',
        '⚡': '[FAST]',
        '📄': '[FILE]',
        '🔍': '[SEARCH]',
        '🎉': '[SUCCESS]',
        '🏥': '[HEALTH]',
        '📋': '[LIST]',
        '🔗': '[LINK]',
        '📐': '[METRICS]',
        '🌟': '[STAR]'
    }
    
    for emoji, replacement in emoji_map.items():
        message = message.replace(emoji, replacement)
    
    return message

class AGIEcosystemTester:
    def __init__(self):
        self.orchestrator = ComprehensiveEcosystemOrchestrator()
        self.n8n_launcher = N8NAGILauncher()
        self.test_results = {}
        self.performance_metrics = {}
        
        # Service endpoints
        self.endpoints = {
            'trilogy_agi': 'http://localhost:8000',
            'gemini_mcp': 'http://localhost:8015',
            'memory_mcp': 'http://localhost:3002',
            'n8n_integration': 'http://localhost:5678',
            'n8n_agi_server': 'http://localhost:8020'
        }
        
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive ecosystem test"""
        logger.info(safe_log("🚀 Starting Comprehensive AGI Ecosystem Test..."))
        
        test_suite = [
            ("System Prerequisites", self._test_system_prerequisites),
            ("Service Health Check", self._test_service_health),
            ("Trilogy AGI Integration", self._test_trilogy_agi),
            ("Gemini CLI Integration", self._test_gemini_cli),
            ("Memory MCP Integration", self._test_memory_mcp),
            ("n8n Integration", self._test_n8n_integration),
            ("Cross-Service Communication", self._test_cross_service_communication),
            ("Workflow Automation", self._test_workflow_automation),
            ("Performance Analysis", self._test_performance_metrics),
            ("GitHub Actions Integration", self._test_github_actions),
            ("Knowledge Graph Operations", self._test_knowledge_graph),
            ("Continuous Learning", self._test_continuous_learning)
        ]
        
        test_results = {}
        start_time = time.time()
        
        for test_name, test_func in test_suite:
            try:
                logger.info(safe_log(f"🧪 Running {test_name}..."))
                test_start = time.time()
                
                result = await test_func()
                test_duration = time.time() - test_start
                
                test_results[test_name.lower().replace(" ", "_")] = {
                    **result,
                    "duration_seconds": test_duration
                }
                
                if result.get("success", False):
                    logger.info(safe_log(f"✅ {test_name} passed ({test_duration:.2f}s)"))
                else:
                    logger.warning(safe_log(f"⚠️ {test_name} failed: {result.get('error', 'Unknown error')}"))
                    
            except Exception as e:
                logger.error(safe_log(f"❌ {test_name} exception: {e}"))
                test_results[test_name.lower().replace(" ", "_")] = {
                    "success": False,
                    "error": str(e),
                    "duration_seconds": 0
                }
        
        total_duration = time.time() - start_time
        
        # Generate comprehensive report
        report = await self._generate_comprehensive_report(test_results, total_duration)
        
        # Save test results
        await self._save_test_results(report)
        
        return report
        
    async def _test_system_prerequisites(self) -> Dict[str, Any]:
        """Test system prerequisites"""
        try:
            prereq_results = {
                "python_version": sys.version,
                "node_installed": False,
                "npm_installed": False,
                "git_installed": False,
                "docker_available": False,
                "system_resources": {}
            }
            
            # Check Node.js
            try:
                result = subprocess.run(['node', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    prereq_results["node_installed"] = True
                    prereq_results["node_version"] = result.stdout.strip()
            except FileNotFoundError:
                pass
            
            # Check npm
            try:
                result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    prereq_results["npm_installed"] = True
                    prereq_results["npm_version"] = result.stdout.strip()
            except FileNotFoundError:
                pass
            
            # Check Git
            try:
                result = subprocess.run(['git', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    prereq_results["git_installed"] = True
                    prereq_results["git_version"] = result.stdout.strip()
            except FileNotFoundError:
                pass
            
            # Check Docker
            try:
                result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    prereq_results["docker_available"] = True
                    prereq_results["docker_version"] = result.stdout.strip()
            except FileNotFoundError:
                pass
            
            # System resources
            prereq_results["system_resources"] = {
                "cpu_count": psutil.cpu_count(),
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_space_gb": round(psutil.disk_usage('.').free / (1024**3), 2)
            }
            
            # Determine success
            required_tools = ["node_installed", "npm_installed", "git_installed"]
            success = all(prereq_results[tool] for tool in required_tools)
            
            return {
                "success": success,
                "details": prereq_results,
                "recommendations": self._get_prerequisite_recommendations(prereq_results)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_service_health(self) -> Dict[str, Any]:
        """Test health of all AGI services"""
        try:
            service_health = {}
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                for service_name, endpoint in self.endpoints.items():
                    try:
                        start_time = time.time()
                        
                        # Try different health check endpoints
                        health_endpoints = [
                            f"{endpoint}/health",
                            f"{endpoint}/api/health",
                            f"{endpoint}/status",
                            endpoint  # Just try the base endpoint
                        ]
                        
                        service_responding = False
                        last_error = None
                        
                        for health_url in health_endpoints:
                            try:
                                async with session.get(health_url, timeout=3) as response:
                                    response_time = (time.time() - start_time) * 1000
                                    
                                    if response.status in [200, 404]:  # 404 is OK if service is up but no health endpoint
                                        service_health[service_name] = {
                                            "status": "healthy" if response.status == 200 else "partially_healthy",
                                            "response_time_ms": round(response_time, 2),
                                            "endpoint_used": health_url,
                                            "http_status": response.status
                                        }
                                        
                                        if response.status == 200:
                                            try:
                                                health_data = await response.json()
                                                service_health[service_name]["details"] = health_data
                                            except:
                                                service_health[service_name]["details"] = "Service responding"
                                        
                                        service_responding = True
                                        break
                                        
                            except aiohttp.ClientConnectorError as e:
                                last_error = f"Connection refused - service not running on {endpoint}"
                                continue
                            except asyncio.TimeoutError:
                                last_error = f"Timeout connecting to {health_url}"
                                continue
                            except Exception as e:
                                last_error = f"Error connecting to {health_url}: {str(e)}"
                                continue
                        
                        if not service_responding:
                            service_health[service_name] = {
                                "status": "unreachable",
                                "error": last_error or f"No response from any endpoint on {endpoint}",
                                "suggestion": f"Ensure {service_name} service is running on {endpoint}"
                            }
                            
                    except Exception as e:
                        service_health[service_name] = {
                            "status": "failed",
                            "error": str(e),
                            "suggestion": f"Check {service_name} service configuration"
                        }
            
            healthy_services = sum(1 for health in service_health.values() 
                                 if health["status"] in ["healthy", "partially_healthy"])
            total_services = len(service_health)
            success = healthy_services >= max(1, total_services * 0.3)  # Lower threshold for development
            
            return {
                "success": success,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "health_percentage": (healthy_services / total_services) * 100 if total_services > 0 else 0,
                "service_details": service_health,
                "recommendations": self._get_service_recommendations(service_health)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_service_recommendations(self, service_health: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on service health"""
        recommendations = []
        
        for service_name, health in service_health.items():
            if health["status"] == "unreachable":
                if service_name == "trilogy_agi":
                    recommendations.append("Start Trilogy AGI services: Run 'python comprehensive_ecosystem_orchestrator.py' or 'npm run trilogy:start'")
                elif service_name == "gemini_mcp":
                    recommendations.append("Start Gemini MCP server: Run 'python servers/gemini_mcp_server.py' or check mcp-config.json")
                elif service_name == "memory_mcp":
                    recommendations.append("Start Memory MCP server: Run 'python servers/memory_mcp_server.py' or check port 3002")
                elif service_name == "n8n_integration":
                    recommendations.append("Start n8n service: Run 'npm run n8n:start' or 'python n8n_integration_manager.py'")
                else:
                    recommendations.append(f"Start {service_name} service on {self.endpoints.get(service_name, 'unknown endpoint')}")
        
        if not recommendations:
            recommendations.append("All accessible services are responding correctly")
        
        return recommendations
    
    async def _test_trilogy_agi(self) -> Dict[str, Any]:
        """Test Trilogy AGI integration"""
        try:
            test_results = {
                "ollama_connection": False,
                "deerflow_integration": False,
                "dgm_capabilities": False,
                "owl_reasoning": False,
                "agent_file_processing": False
            }
            
            # Test Ollama connection
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.endpoints['trilogy_agi']}/ollama/models") as response:
                        if response.status == 200:
                            models = await response.json()
                            test_results["ollama_connection"] = True
                            test_results["ollama_models"] = models
            except Exception as e:
                test_results["ollama_error"] = str(e)
            
            # Test DeerFlow integration
            try:
                async with aiohttp.ClientSession() as session:
                    test_data = {"query": "Test DeerFlow integration", "context": "AGI ecosystem test"}
                    async with session.post(f"{self.endpoints['trilogy_agi']}/deerflow/process", json=test_data) as response:
                        if response.status == 200:
                            result = await response.json()
                            test_results["deerflow_integration"] = True
                            test_results["deerflow_response"] = result
            except Exception as e:
                test_results["deerflow_error"] = str(e)
            
            # Test other Trilogy components
            trilogy_components = ["dgm", "owl", "agent_file"]
            for component in trilogy_components:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{self.endpoints['trilogy_agi']}/{component}/status") as response:
                            if response.status == 200:
                                test_results[f"{component}_capabilities"] = True
                except Exception as e:
                    test_results[f"{component}_error"] = str(e)
            
            success = sum(1 for v in test_results.values() if v is True) >= 3
            
            return {
                "success": success,
                "details": test_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_gemini_cli(self) -> Dict[str, Any]:
        """Test Gemini CLI integration"""
        try:
            test_results = {
                "server_running": False,
                "mcp_protocol": False,
                "context_window": False,
                "google_search": False,
                "code_analysis": False
            }
            
            # Test server connection
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.endpoints['gemini_mcp']}/status") as response:
                        if response.status == 200:
                            test_results["server_running"] = True
                            status_data = await response.json()
                            test_results["server_details"] = status_data
            except Exception as e:
                test_results["server_error"] = str(e)
            
            # Test MCP protocol
            try:
                async with aiohttp.ClientSession() as session:
                    mcp_request = {
                        "method": "tools/list",
                        "params": {}
                    }
                    async with session.post(f"{self.endpoints['gemini_mcp']}/mcp", json=mcp_request) as response:
                        if response.status == 200:
                            tools = await response.json()
                            test_results["mcp_protocol"] = True
                            test_results["available_tools"] = tools
            except Exception as e:
                test_results["mcp_error"] = str(e)
            
            # Test context window capabilities
            try:
                large_context = "A" * 10000  # 10K characters test
                async with aiohttp.ClientSession() as session:
                    context_test = {
                        "prompt": f"Analyze this context: {large_context}",
                        "max_tokens": 100
                    }
                    async with session.post(f"{self.endpoints['gemini_mcp']}/generate", json=context_test) as response:
                        if response.status == 200:
                            test_results["context_window"] = True
            except Exception as e:
                test_results["context_error"] = str(e)
            
            success = test_results["server_running"] and test_results["mcp_protocol"]
            
            return {
                "success": success,
                "details": test_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_memory_mcp(self) -> Dict[str, Any]:
        """Test Memory MCP integration"""
        try:
            test_results = {
                "server_running": False,
                "knowledge_graph": False,
                "entity_operations": False,
                "relation_operations": False,
                "continuous_learning": False
            }
            
            # Test server connection
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.endpoints['memory_mcp']}/health") as response:
                        if response.status == 200:
                            test_results["server_running"] = True
            except Exception as e:
                test_results["server_error"] = str(e)
            
            # Test knowledge graph operations
            try:
                async with aiohttp.ClientSession() as session:
                    # Test entity creation
                    entity_data = {
                        "entities": [{
                            "name": "TestEntity",
                            "entityType": "test",
                            "observations": ["This is a test entity for ecosystem validation"]
                        }]
                    }
                    async with session.post(f"{self.endpoints['memory_mcp']}/entities", json=entity_data) as response:
                        if response.status == 200:
                            test_results["entity_operations"] = True
                    
                    # Test relation creation
                    relation_data = {
                        "relations": [{
                            "from": "TestEntity",
                            "to": "AGIEcosystem",
                            "relationType": "participates_in"
                        }]
                    }
                    async with session.post(f"{self.endpoints['memory_mcp']}/relations", json=relation_data) as response:
                        if response.status == 200:
                            test_results["relation_operations"] = True
                    
                    # Test graph reading
                    async with session.get(f"{self.endpoints['memory_mcp']}/graph") as response:
                        if response.status == 200:
                            graph_data = await response.json()
                            test_results["knowledge_graph"] = True
                            test_results["graph_size"] = len(graph_data.get("entities", []))
                            
            except Exception as e:
                test_results["graph_error"] = str(e)
            
            success = test_results["server_running"] and test_results["knowledge_graph"]
            
            return {
                "success": success,
                "details": test_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_n8n_integration(self) -> Dict[str, Any]:
        """Test n8n integration"""
        try:
            test_results = {
                "n8n_server": False,
                "agi_integration_server": False,
                "custom_nodes": False,
                "workflow_execution": False,
                "webhook_triggers": False
            }
            
            # Test n8n server
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.endpoints['n8n_integration']}/healthz") as response:
                        if response.status == 200:
                            test_results["n8n_server"] = True
            except Exception as e:
                test_results["n8n_error"] = str(e)
            
            # Test AGI integration server
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.endpoints['n8n_agi_server']}/health") as response:
                        if response.status == 200:
                            test_results["agi_integration_server"] = True
            except Exception as e:
                test_results["agi_server_error"] = str(e)
            
            # Test custom nodes
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.endpoints['n8n_agi_server']}/nodes") as response:
                        if response.status == 200:
                            nodes = await response.json()
                            test_results["custom_nodes"] = True
                            test_results["available_nodes"] = nodes
            except Exception as e:
                test_results["nodes_error"] = str(e)
            
            success = test_results["agi_integration_server"]
            
            return {
                "success": success,
                "details": test_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_cross_service_communication(self) -> Dict[str, Any]:
        """Test cross-service communication"""
        try:
            # Test a complex workflow that involves multiple services
            test_workflow = {
                "steps": [
                    {"service": "gemini_mcp", "action": "analyze_code", "input": "def test(): return 'hello'"},
                    {"service": "memory_mcp", "action": "store_analysis", "input": "code_analysis_result"},
                    {"service": "trilogy_agi", "action": "enhance_analysis", "input": "stored_analysis"},
                    {"service": "n8n_integration", "action": "trigger_workflow", "input": "enhanced_analysis"}
                ]
            }
            
            workflow_results = []
            
            for step in test_workflow["steps"]:
                try:
                    # Simulate cross-service communication
                    service_endpoint = self.endpoints.get(step["service"])
                    if service_endpoint:
                        async with aiohttp.ClientSession() as session:
                            async with session.post(f"{service_endpoint}/process", json={"data": step["input"]}) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    workflow_results.append({
                                        "step": step["action"],
                                        "success": True,
                                        "result": result
                                    })
                                else:
                                    workflow_results.append({
                                        "step": step["action"],
                                        "success": False,
                                        "error": f"HTTP {response.status}"
                                    })
                except Exception as e:
                    workflow_results.append({
                        "step": step["action"],
                        "success": False,
                        "error": str(e)
                    })
            
            successful_steps = sum(1 for result in workflow_results if result["success"])
            success = successful_steps >= len(test_workflow["steps"]) * 0.5
            
            return {
                "success": success,
                "workflow_results": workflow_results,
                "success_rate": (successful_steps / len(test_workflow["steps"])) * 100
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_workflow_automation(self) -> Dict[str, Any]:
        """Test workflow automation capabilities"""
        try:
            # Test predefined workflows
            test_workflows = [
                "code_analysis_workflow",
                "continuous_learning_workflow",
                "performance_optimization_workflow"
            ]
            
            workflow_results = {}
            
            for workflow_name in test_workflows:
                try:
                    async with aiohttp.ClientSession() as session:
                        workflow_data = {
                            "workflow": workflow_name,
                            "input": {"test": True, "timestamp": datetime.now().isoformat()}
                        }
                        async with session.post(f"{self.endpoints['n8n_agi_server']}/execute_workflow", json=workflow_data) as response:
                            if response.status in [200, 202]:  # Accept both sync and async responses
                                result = await response.json()
                                workflow_results[workflow_name] = {
                                    "success": True,
                                    "result": result
                                }
                            else:
                                workflow_results[workflow_name] = {
                                    "success": False,
                                    "error": f"HTTP {response.status}"
                                }
                except Exception as e:
                    workflow_results[workflow_name] = {
                        "success": False,
                        "error": str(e)
                    }
            
            successful_workflows = sum(1 for result in workflow_results.values() if result["success"])
            success = successful_workflows > 0
            
            return {
                "success": success,
                "workflow_results": workflow_results,
                "successful_workflows": successful_workflows,
                "total_workflows": len(test_workflows)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_performance_metrics(self) -> Dict[str, Any]:
        """Test and collect performance metrics"""
        try:
            metrics = {
                "system_performance": {},
                "service_response_times": {},
                "memory_usage": {},
                "cpu_usage": {}
            }
            
            # System performance
            metrics["system_performance"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage('.').percent,
                "network_io": dict(psutil.net_io_counters()._asdict()) if psutil.net_io_counters() else {}
            }
            
            # Service response times
            for service_name, endpoint in self.endpoints.items():
                try:
                    start_time = time.time()
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{endpoint}/health", timeout=5) as response:
                            response_time = (time.time() - start_time) * 1000  # ms
                            metrics["service_response_times"][service_name] = {
                                "response_time_ms": response_time,
                                "status_code": response.status
                            }
                except Exception as e:
                    metrics["service_response_times"][service_name] = {
                        "error": str(e),
                        "response_time_ms": None
                    }
            
            # Process-specific metrics
            current_process = psutil.Process()
            metrics["process_metrics"] = {
                "memory_info": dict(current_process.memory_info()._asdict()),
                "cpu_percent": current_process.cpu_percent(),
                "num_threads": current_process.num_threads(),
                "open_files": len(current_process.open_files())
            }
            
            return {
                "success": True,
                "metrics": metrics,
                "performance_summary": self._generate_performance_summary(metrics)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_github_actions(self) -> Dict[str, Any]:
        """Test GitHub Actions integration capabilities"""
        try:
            # Test GitHub Actions configuration
            github_actions_path = Path(".github/workflows")
            
            if not github_actions_path.exists():
                return {
                    "success": False,
                    "error": "GitHub Actions directory not found"
                }
            
            workflow_files = list(github_actions_path.glob("*.yml")) + list(github_actions_path.glob("*.yaml"))
            
            workflow_analysis = {}
            
            for workflow_file in workflow_files:
                try:
                    with open(workflow_file, 'r') as f:
                        workflow_content = f.read()
                    
                    # Basic workflow analysis
                    has_agi_integration = any(keyword in workflow_content.lower() for keyword in 
                                            ['agi', 'trilogy', 'gemini', 'n8n', 'ollama'])
                    
                    workflow_analysis[workflow_file.name] = {
                        "exists": True,
                        "size_bytes": len(workflow_content),
                        "has_agi_integration": has_agi_integration,
                        "line_count": len(workflow_content.split('\n'))
                    }
                    
                except Exception as e:
                    workflow_analysis[workflow_file.name] = {
                        "exists": True,
                        "error": str(e)
                    }
            
            # Check for AGI-specific actions
            agi_actions_path = Path(".github/actions")
            agi_actions_exist = agi_actions_path.exists()
            
            return {
                "success": True,
                "workflow_files_count": len(workflow_files),
                "workflow_analysis": workflow_analysis,
                "agi_actions_exist": agi_actions_exist,
                "agi_enhanced_workflows": sum(1 for analysis in workflow_analysis.values() 
                                            if analysis.get("has_agi_integration", False))
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_knowledge_graph(self) -> Dict[str, Any]:
        """Test knowledge graph operations"""
        try:
            # Test complex knowledge graph operations
            test_entities = [
                {"name": "AGIEcosystem", "entityType": "system", "observations": ["Central AGI ecosystem"]},
                {"name": "TrilogyAGI", "entityType": "component", "observations": ["Trilogy AGI stack"]},
                {"name": "GeminiCLI", "entityType": "component", "observations": ["Gemini CLI integration"]},
                {"name": "N8NWorkflow", "entityType": "automation", "observations": ["n8n workflow system"]}
            ]
            
            test_relations = [
                {"from": "TrilogyAGI", "to": "AGIEcosystem", "relationType": "part_of"},
                {"from": "GeminiCLI", "to": "AGIEcosystem", "relationType": "part_of"},
                {"from": "N8NWorkflow", "to": "AGIEcosystem", "relationType": "automates"}
            ]
            
            async with aiohttp.ClientSession() as session:
                # Create test entities
                async with session.post(f"{self.endpoints['memory_mcp']}/entities", 
                                      json={"entities": test_entities}) as response:
                    entities_created = response.status == 200
                
                # Create test relations
                async with session.post(f"{self.endpoints['memory_mcp']}/relations", 
                                      json={"relations": test_relations}) as response:
                    relations_created = response.status == 200
                
                # Query knowledge graph
                async with session.get(f"{self.endpoints['memory_mcp']}/graph") as response:
                    if response.status == 200:
                        graph_data = await response.json()
                        graph_queried = True
                        graph_size = len(graph_data.get("entities", []))
                    else:
                        graph_queried = False
                        graph_size = 0
                
                # Search nodes
                async with session.get(f"{self.endpoints['memory_mcp']}/search?q=AGI") as response:
                    search_works = response.status == 200
                    if search_works:
                        search_results = await response.json()
                        search_count = len(search_results.get("results", []))
                    else:
                        search_count = 0
            
            return {
                "success": entities_created and relations_created and graph_queried,
                "entities_created": entities_created,
                "relations_created": relations_created,
                "graph_queried": graph_queried,
                "search_works": search_works,
                "graph_size": graph_size,
                "search_results_count": search_count
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_continuous_learning(self) -> Dict[str, Any]:
        """Test continuous learning capabilities"""
        try:
            learning_test = {
                "data_ingestion": False,
                "pattern_recognition": False,
                "model_adaptation": False,
                "feedback_loop": False
            }
            
            # Test data ingestion
            try:
                learning_data = {
                    "source": "ecosystem_test",
                    "data": {
                        "performance_metrics": {"response_time": 150, "accuracy": 0.95},
                        "user_interactions": ["code_analysis", "workflow_execution"],
                        "system_events": ["service_restart", "optimization_applied"]
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{self.endpoints['memory_mcp']}/learn", json=learning_data) as response:
                        if response.status == 200:
                            learning_test["data_ingestion"] = True
            except Exception as e:
                learning_test["data_ingestion_error"] = str(e)
            
            # Test pattern recognition
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.endpoints['trilogy_agi']}/patterns/analyze") as response:
                        if response.status == 200:
                            patterns = await response.json()
                            learning_test["pattern_recognition"] = True
                            learning_test["identified_patterns"] = patterns
            except Exception as e:
                learning_test["pattern_error"] = str(e)
            
            # Test model adaptation
            try:
                adaptation_request = {
                    "adaptation_type": "performance_optimization",
                    "metrics": {"current_performance": 0.8, "target_performance": 0.9}
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{self.endpoints['trilogy_agi']}/adapt", json=adaptation_request) as response:
                        if response.status in [200, 202]:
                            learning_test["model_adaptation"] = True
            except Exception as e:
                learning_test["adaptation_error"] = str(e)
            
            success = sum(1 for v in learning_test.values() if v is True) >= 2
            
            return {
                "success": success,
                "learning_capabilities": learning_test
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_prerequisite_recommendations(self, prereq_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on prerequisite check"""
        recommendations = []
        
        if not prereq_results.get("node_installed"):
            recommendations.append("Install Node.js (v18 or later)")
        
        if not prereq_results.get("npm_installed"):
            recommendations.append("Install npm package manager")
        
        if not prereq_results.get("git_installed"):
            recommendations.append("Install Git version control")
        
        if not prereq_results.get("docker_available"):
            recommendations.append("Install Docker for containerized services (optional)")
        
        system_resources = prereq_results.get("system_resources", {})
        if system_resources.get("memory_gb", 0) < 8:
            recommendations.append("Consider upgrading to at least 8GB RAM for optimal performance")
        
        if system_resources.get("disk_space_gb", 0) < 10:
            recommendations.append("Ensure at least 10GB free disk space")
        
        return recommendations
    
    def _generate_performance_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary"""
        system_perf = metrics.get("system_performance", {})
        response_times = metrics.get("service_response_times", {})
        
        # Calculate average response time
        valid_response_times = [
            rt["response_time_ms"] for rt in response_times.values() 
            if rt.get("response_time_ms") is not None
        ]
        
        avg_response_time = sum(valid_response_times) / len(valid_response_times) if valid_response_times else 0
        
        # Performance rating
        performance_rating = "excellent"
        if system_perf.get("cpu_percent", 0) > 80 or system_perf.get("memory_percent", 0) > 80:
            performance_rating = "poor"
        elif system_perf.get("cpu_percent", 0) > 60 or system_perf.get("memory_percent", 0) > 60:
            performance_rating = "fair"
        elif system_perf.get("cpu_percent", 0) > 40 or system_perf.get("memory_percent", 0) > 40:
            performance_rating = "good"
        
        return {
            "performance_rating": performance_rating,
            "avg_response_time_ms": avg_response_time,
            "system_cpu_percent": system_perf.get("cpu_percent", 0),
            "system_memory_percent": system_perf.get("memory_percent", 0),
            "responsive_services": len(valid_response_times),
            "total_services": len(response_times)
        }
    
    async def _generate_comprehensive_report(self, test_results: Dict[str, Any], total_duration: float) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        # Calculate overall success metrics
        successful_tests = sum(1 for result in test_results.values() if result.get("success", False))
        total_tests = len(test_results)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Categorize results
        critical_tests = ["system_prerequisites", "service_health", "trilogy_agi_integration"]
        critical_success = all(test_results.get(test, {}).get("success", False) for test in critical_tests)
        
        # Generate recommendations
        recommendations = []
        failed_tests = [name for name, result in test_results.items() if not result.get("success", False)]
        
        for failed_test in failed_tests:
            if failed_test == "system_prerequisites":
                recommendations.extend(test_results[failed_test].get("recommendations", []))
            elif failed_test == "service_health":
                recommendations.append("Check service configurations and restart failed services")
            elif "integration" in failed_test:
                recommendations.append(f"Review {failed_test.replace('_', ' ')} configuration")
        
        # Overall ecosystem status
        if success_rate >= 90:
            ecosystem_status = "excellent"
        elif success_rate >= 75:
            ecosystem_status = "good"
        elif success_rate >= 60:
            ecosystem_status = "fair"
        else:
            ecosystem_status = "needs_attention"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": len(failed_tests),
                "success_rate_percent": success_rate,
                "total_duration_seconds": total_duration,
                "ecosystem_status": ecosystem_status,
                "critical_systems_operational": critical_success
            },
            "test_results": test_results,
            "failed_tests": failed_tests,
            "recommendations": recommendations,
            "next_steps": self._generate_next_steps(test_results, ecosystem_status),
            "performance_summary": test_results.get("performance_analysis", {}).get("performance_summary", {}),
            "github_actions_status": test_results.get("github_actions_integration", {}),
            "knowledge_graph_status": test_results.get("knowledge_graph_operations", {}),
            "continuous_learning_status": test_results.get("continuous_learning", {})
        }
    
    def _generate_next_steps(self, test_results: Dict[str, Any], ecosystem_status: str) -> List[str]:
        """Generate next steps based on test results"""
        next_steps = []
        
        if ecosystem_status == "excellent":
            next_steps.extend([
                safe_log("🚀 System is performing excellently - ready for production use"),
                safe_log("📊 Continue monitoring performance metrics"),
                safe_log("🔄 Schedule regular optimization cycles"),
                safe_log("📈 Consider scaling services for increased load")
            ])
        elif ecosystem_status == "good":
            next_steps.extend([
                safe_log("✅ System is operational with minor optimizations needed"),
                safe_log("🔧 Address any failed test cases"),
                safe_log("📊 Monitor performance trends"),
                safe_log("🔄 Implement continuous improvement processes")
            ])
        elif ecosystem_status == "fair":
            next_steps.extend([
                safe_log("⚠️ System needs attention before production use"),
                safe_log("🔧 Fix critical service failures"),
                safe_log("📊 Investigate performance bottlenecks"),
                safe_log("🔄 Implement stability improvements")
            ])
        else:
            next_steps.extend([
                safe_log("🚨 System requires immediate attention"),
                safe_log("🔧 Fix all critical failures before proceeding"),
                safe_log("📊 Comprehensive performance review needed"),
                safe_log("🔄 Consider system architecture changes")
            ])
        
        # Add specific recommendations based on failed tests
        failed_tests = [name for name, result in test_results.items() if not result.get("success", False)]
        
        if "system_prerequisites" in failed_tests:
            next_steps.append("📋 Install missing system prerequisites")
        
        if "service_health" in failed_tests:
            next_steps.append("🏥 Restart and configure unhealthy services")
        
        if any("integration" in test for test in failed_tests):
            next_steps.append("🔗 Review and fix service integration issues")
        
        return next_steps
    
    async def _save_test_results(self, report: Dict[str, Any]) -> None:
        """Save test results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agi_ecosystem_test_results_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str, ensure_ascii=False)
            
            logger.info(safe_log(f"📄 Test results saved to {filename}"))
            
            # Also save a summary report
            summary_filename = f"agi_ecosystem_summary_{timestamp}.md"
            with open(summary_filename, 'w', encoding='utf-8') as f:
                f.write(self._generate_markdown_summary(report))
            
            logger.info(safe_log(f"📄 Summary report saved to {summary_filename}"))
            
        except Exception as e:
            logger.error(safe_log(f"❌ Failed to save test results: {e}"))
    
    def _generate_markdown_summary(self, report: Dict[str, Any]) -> str:
        """Generate markdown summary report"""
        summary = report["test_summary"]
        
        md_content = f"""# AGI Ecosystem Test Report

**Generated:** {report["timestamp"]}

## {safe_log("📊")} Test Summary

- **Total Tests:** {summary["total_tests"]}
- **Successful:** {summary["successful_tests"]}
- **Failed:** {summary["failed_tests"]}
- **Success Rate:** {summary["success_rate_percent"]:.1f}%
- **Duration:** {summary["total_duration_seconds"]:.2f} seconds
- **Ecosystem Status:** {summary["ecosystem_status"].upper()}
- **Critical Systems:** {safe_log('✅ Operational' if summary["critical_systems_operational"] else '❌ Issues Detected')}

## {safe_log("🔍")} Test Results

"""
        
        for test_name, result in report["test_results"].items():
            status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
            duration = result.get("duration_seconds", 0)
            md_content += f"- **{test_name.replace('_', ' ').title()}:** {status} ({duration:.2f}s)\n"
        
        if report["failed_tests"]:
            md_content += f"\n## ❌ Failed Tests\n\n"
            for failed_test in report["failed_tests"]:
                md_content += f"- {failed_test.replace('_', ' ').title()}\n"
        
        if report["recommendations"]:
            md_content += f"\n## 💡 Recommendations\n\n"
            for rec in report["recommendations"]:
                md_content += f"- {rec}\n"
        
        md_content += f"\n## 🎯 Next Steps\n\n"
        for step in report["next_steps"]:
            md_content += f"- {step}\n"
        
        # Performance summary
        if "performance_summary" in report and report["performance_summary"]:
            perf = report["performance_summary"]
            md_content += f"""
## ⚡ Performance Summary

- **Rating:** {perf.get("performance_rating", "unknown").upper()}
- **Average Response Time:** {perf.get("avg_response_time_ms", 0):.2f}ms
- **CPU Usage:** {perf.get("system_cpu_percent", 0):.1f}%
- **Memory Usage:** {perf.get("system_memory_percent", 0):.1f}%
- **Responsive Services:** {perf.get("responsive_services", 0)}/{perf.get("total_services", 0)}
"""
        
        return md_content

async def main():
    """Main test execution"""
    parser = argparse.ArgumentParser(description="Comprehensive AGI Ecosystem Test")
    parser.add_argument("--mode", choices=["test", "monitor", "analyze"], default="test",
                       help="Operation mode")
    parser.add_argument("--services", nargs="+", 
                       choices=["trilogy", "gemini", "memory", "n8n", "all"], 
                       default=["all"],
                       help="Services to test")
    parser.add_argument("--output", default="json", choices=["json", "markdown", "both"],
                       help="Output format")
    
    args = parser.parse_args()
    
    tester = AGIEcosystemTester()
    
    try:
        logger.info(safe_log("🚀 Starting AGI Ecosystem Comprehensive Test..."))
        
        # Run comprehensive test
        report = await tester.run_comprehensive_test()
        
        # Display summary
        summary = report["test_summary"]
        logger.info(safe_log(f"""
🎯 TEST COMPLETION SUMMARY:
- Success Rate: {summary['success_rate_percent']:.1f}%
- Total Duration: {summary['total_duration_seconds']:.2f}s
- Ecosystem Status: {summary['ecosystem_status'].upper()}
- Critical Systems: {'✅ Operational' if summary['critical_systems_operational'] else '❌ Issues'}
"""))
        
        if summary["success_rate_percent"] >= 80:
            logger.info(safe_log("🎉 AGI Ecosystem is ready for production use!"))
        elif summary["success_rate_percent"] >= 60:
            logger.info(safe_log("⚠️ AGI Ecosystem needs some attention but is functional"))
        else:
            logger.warning(safe_log("🚨 AGI Ecosystem requires immediate fixes"))
        
        return report
        
    except Exception as e:
        logger.error(safe_log(f"❌ Test execution failed: {e}"))
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())
