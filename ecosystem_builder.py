#!/usr/bin/env python3
"""
MCPVots Ecosystem Builder
=======================
Comprehensive ecosystem creation and management for MCPVots with Trilogy AGI integration
Advanced orchestration, monitoring, and continuous improvement system
"""

import asyncio
import json
import subprocess
import time
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import threading
import psutil
import os
import yaml
import docker
import websockets
from dataclasses import dataclass, asdict
import aiohttp
import signal
import sys

# Configure advanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ecosystem_builder.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    """Service configuration data class"""
    name: str
    port: int
    command: List[str]
    working_dir: Path
    capabilities: List[str]
    status: str = "pending"
    environment: Dict[str, str] = None
    dependencies: List[str] = None
    health_check_url: str = None
    restart_policy: str = "always"
    timeout: int = 30

@dataclass
class SystemMetrics:
    """System metrics data class"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    active_services: int
    error_count: int
    response_time: float

class MCPVotsEcosystemBuilder:
    """Complete ecosystem builder for MCPVots with advanced integrations"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.workspace_path = Path("c:/Workspace")
        self.services: Dict[str, ServiceConfig] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.health_monitors: Dict[str, threading.Thread] = {}
        self.system_metrics: List[SystemMetrics] = []
        self.running = False
        self.docker_client = None
        
        # Initialize services configuration
        self.initialize_services()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def initialize_services(self):
        """Initialize comprehensive service configurations"""
        
        # MCP Server configurations
        mcp_servers = {
            "github-mcp": ServiceConfig(
                name="github-mcp",
                port=3001,
                command=["node", "github_mcp_server.js"],
                working_dir=self.workspace_path / "MCP-Servers" / "github-mcp",
                capabilities=["repositories", "issues", "pull-requests", "actions"],
                health_check_url="http://localhost:3001/health",
                environment={"NODE_ENV": "production", "LOG_LEVEL": "info"}
            ),
            "memory-mcp": ServiceConfig(
                name="memory-mcp",
                port=3002,
                command=["node", "memory_mcp_server.js"],
                working_dir=self.workspace_path / "MCP-Servers" / "memory-mcp",
                capabilities=["knowledge-graph", "storage", "retrieval", "embeddings"],
                health_check_url="http://localhost:3002/health",
                environment={"NODE_ENV": "production"}
            ),
            "huggingface-mcp": ServiceConfig(
                name="huggingface-mcp",
                port=3003,
                command=["python", "-m", "huggingface_mcp_server"],
                working_dir=self.workspace_path / "MCP-Servers" / "huggingface-mcp",
                capabilities=["models", "inference", "datasets", "training"],
                health_check_url="http://localhost:3003/health",
                environment={"PYTHONPATH": str(self.workspace_path)}
            ),
            "supermemory-mcp": ServiceConfig(
                name="supermemory-mcp",
                port=3004,
                command=["node", "supermemory_mcp_server.js"],
                working_dir=self.workspace_path / "MCP-Servers" / "supermemory-mcp",
                capabilities=["advanced-memory", "context-aware", "personalization"],
                health_check_url="http://localhost:3004/health"
            ),
            "solana-mcp": ServiceConfig(
                name="solana-mcp",
                port=3005,
                command=["python", "-m", "solana_mcp_server"],
                working_dir=self.workspace_path / "MCP-Servers" / "solana-mcp",
                capabilities=["blockchain", "transactions", "smart-contracts", "defi"],
                health_check_url="http://localhost:3005/health",
                environment={"SOLANA_ENV": "mainnet"}
            ),
            "browser-tools-mcp": ServiceConfig(
                name="browser-tools-mcp",
                port=3006,
                command=["node", "browser_tools_server.js"],
                working_dir=self.workspace_path / "MCP-Servers" / "browser-tools-mcp",
                capabilities=["automation", "scraping", "testing", "screenshots"],
                health_check_url="http://localhost:3006/health"
            )
        }

        # Trilogy AGI Services
        trilogy_services = {
            "trilogy-gateway": ServiceConfig(
                name="trilogy-gateway",
                port=8000,
                command=["python", "trilogy_enhanced_gateway_v3.py"],
                working_dir=self.workspace_path,
                capabilities=["gateway", "routing", "load-balancing"],
                health_check_url="http://localhost:8000/health",
                dependencies=["dspy-service", "rl-service"]
            ),
            "dspy-service": ServiceConfig(
                name="dspy-service",
                port=8001,
                command=["python", "simple_dspy_service.py"],
                working_dir=self.workspace_path,
                capabilities=["dspy", "prompting", "optimization"],
                health_check_url="http://localhost:8001/health"
            ),
            "rl-service": ServiceConfig(
                name="rl-service",
                port=8002,
                command=["python", "trilogy_rl_engine.py"],
                working_dir=self.workspace_path,
                capabilities=["reinforcement-learning", "decision-making"],
                health_check_url="http://localhost:8002/health"
            ),
            "deepseek-service": ServiceConfig(
                name="deepseek-service",
                port=8003,
                command=["python", "deepseek_r1_service.py"],
                working_dir=self.workspace_path,
                capabilities=["deepseek", "reasoning", "analysis"],
                health_check_url="http://localhost:8003/health"
            ),
            "mission-control": ServiceConfig(
                name="mission-control",
                port=8005,
                command=["python", "trilogy_mission_control.py"],
                working_dir=self.workspace_path,
                capabilities=["orchestration", "monitoring", "coordination"],
                health_check_url="http://localhost:8005/health",
                dependencies=["trilogy-gateway"]
            )
        }

        # OWL Framework Services
        owl_services = {
            "owl-framework": ServiceConfig(
                name="owl-framework",
                port=8010,
                command=["python", "owl_integration_service.py"],
                working_dir=self.workspace_path / "owl-integration",
                capabilities=["workflow-automation", "task-orchestration"],
                health_check_url="http://localhost:8010/health"
            )
        }

        # Web Services
        web_services = {
            "mcpvots-frontend": ServiceConfig(
                name="mcpvots-frontend",
                port=3000,
                command=["npm", "run", "dev"],
                working_dir=self.base_path,
                capabilities=["frontend", "ui", "dashboard"],
                health_check_url="http://localhost:3000",
                environment={"NODE_ENV": "development"}
            ),
            "websocket-proxy": ServiceConfig(
                name="websocket-proxy",
                port=8080,
                command=["node", "websocket_proxy.js"],
                working_dir=self.base_path,
                capabilities=["websocket", "proxy", "routing"],
                health_check_url="http://localhost:8080/health"
            )
        }

        # Analytics and Monitoring
        monitoring_services = {
            "analytics-dashboard": ServiceConfig(
                name="analytics-dashboard",
                port=8090,
                command=["python", "trilogy_analytics_dashboard.py"],
                working_dir=self.workspace_path,
                capabilities=["analytics", "metrics", "reporting"],
                health_check_url="http://localhost:8090/health"
            ),
            "system-monitor": ServiceConfig(
                name="system-monitor",
                port=8091,
                command=["python", "system_monitor.py"],
                working_dir=self.base_path,
                capabilities=["monitoring", "health-checks", "alerts"],
                health_check_url="http://localhost:8091/health"
            )
        }

        # Combine all services
        self.services.update(mcp_servers)
        self.services.update(trilogy_services)
        self.services.update(owl_services)
        self.services.update(web_services)
        self.services.update(monitoring_services)

        logger.info(f"Initialized {len(self.services)} services")

    async def build_ecosystem(self) -> Dict[str, Any]:
        """Build the complete MCPVots ecosystem"""
        logger.info("🚀 Building MCPVots Comprehensive Ecosystem...")
        
        build_report = {
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "phases": {},
            "services": {},
            "metrics": {},
            "errors": []
        }

        try:
            # Phase 1: Environment Setup
            build_report["phases"]["environment_setup"] = await self.setup_environment()
            
            # Phase 2: Dependency Installation
            build_report["phases"]["dependency_installation"] = await self.install_dependencies()
            
            # Phase 3: Service Creation
            build_report["phases"]["service_creation"] = await self.create_services()
            
            # Phase 4: Service Startup
            build_report["phases"]["service_startup"] = await self.start_services()
            
            # Phase 5: Health Verification
            build_report["phases"]["health_verification"] = await self.verify_health()
            
            # Phase 6: Integration Testing
            build_report["phases"]["integration_testing"] = await self.run_integration_tests()
            
            # Phase 7: Performance Optimization
            build_report["phases"]["performance_optimization"] = await self.optimize_performance()
            
            build_report["status"] = "completed"
            build_report["services"] = {name: asdict(service) for name, service in self.services.items()}
            
        except Exception as e:
            logger.error(f"Ecosystem build failed: {e}")
            build_report["status"] = "failed"
            build_report["errors"].append(str(e))

        # Save build report
        await self.save_build_report(build_report)
        
        return build_report
                "working_dir": self.workspace_path / "MCP-Servers" / "memory-mcp",
                "capabilities": ["knowledge-graph", "storage", "retrieval"],
                "status": "pending"
            },
            "huggingface-mcp": {
                "port": 3003,
                "command": ["python", "-m", "huggingface_mcp_server"],
                "working_dir": self.workspace_path / "MCP-Servers" / "huggingface-mcp",
                "capabilities": ["models", "inference", "datasets"],
                "status": "pending"
            },
            "supermemory-mcp": {
                "port": 3004,
                "command": ["node", "supermemory_mcp_wrapper.cjs"],
                "working_dir": self.workspace_path,
                "capabilities": ["memory", "search", "indexing"],
                "status": "pending"
            },
            "solana-mcp": {
                "port": 3005,
                "command": ["python", "-m", "solana_mcp_server"],
                "working_dir": self.workspace_path / "MCP-Servers" / "solana-mcp",
                "capabilities": ["blockchain", "transactions", "wallets"],
                "status": "pending"
            },
            "browser-mcp": {
                "port": 3006,
                "command": ["npx", "@executeautomation/playwright-mcp-server"],
                "working_dir": self.workspace_path,
                "capabilities": ["automation", "scraping", "interaction"],
                "status": "pending"
            }
        }
        
        self.trilogy_services = {
            "dspy-autonomous": {
                "port": 8000,
                "script": "trilogy_dspy_autonomous_service.py",
                "description": "DSPy Autonomous Operation Service",
                "status": "pending"
            },
            "rl-memory": {
                "port": 8001,
                "script": "trilogy_rl_memory_service.py", 
                "description": "RL Memory Service",
                "status": "pending"
            },
            "conversation": {
                "port": 8002,
                "script": "trilogy_conversation_service.py",
                "description": "Conversation Service",
                "status": "pending"
            },
            "deepseek-r1": {
                "port": 8003,
                "script": "AI-Projects/agi-system/backend/deepseek_r1_http_service.py",
                "description": "DeepSeek R1 + DGM Service",
                "status": "pending"
            },
            "jenova-orchestrator": {
                "port": 8004,
                "script": "trilogy_jenova_orchestrator.py",
                "description": "Jenova Orchestrator",
                "status": "pending"
            },
            "mission-control": {
                "port": 8005,
                "script": "trilogy_mission_control_fixed.py",
                "description": "Mission Control",
                "status": "pending"
            },
            "autonomous-ops": {
                "port": 8006,
                "script": "AI-Projects/agi-system/backend/dspy_autonomous_operation_service.py",
                "description": "Autonomous Operations",
                "status": "pending"
            },
            "self-healing": {
                "port": 8007,
                "script": "trilogy_self_healing.py",
                "description": "Self Healing System",
                "status": "pending"
            },
            "advanced-mcp": {
                "port": 8020,
                "script": "AI-Projects/advanced_mcp_ecosystem.py",
                "description": "Advanced MCP Ecosystem",
                "status": "pending"
            }
        }
        
        self.processes = {}
        self.ecosystem_status = {
            "start_time": datetime.now(),
            "mcp_servers_active": 0,
            "trilogy_services_active": 0,
            "total_connections": 0,
            "health_score": 0.0
        }

    async def build_ecosystem(self):
        """Build the complete MCPVots ecosystem"""
        logger.info("🌟 BUILDING MCPVOTS COMPLETE ECOSYSTEM")
        logger.info("=" * 60)
        
        try:
            # Step 1: Check prerequisites
            await self.check_prerequisites()
            
            # Step 2: Create MCP server infrastructure
            await self.create_mcp_server_infrastructure()
            
            # Step 3: Start MCP servers
            await self.start_mcp_servers()
            
            # Step 4: Initialize Trilogy services
            await self.initialize_trilogy_services()
            
            # Step 5: Start core application
            await self.start_core_application()
            
            # Step 6: Verify integrations
            await self.verify_ecosystem_health()
            
            # Step 7: Generate status report
            await self.generate_ecosystem_report()
            
            logger.info("✅ MCPVots ecosystem built successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to build ecosystem: {str(e)}")
            raise

    async def check_prerequisites(self):
        """Check system prerequisites"""
        logger.info("🔍 Checking prerequisites...")
        
        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Node.js: {result.stdout.strip()}")
            else:
                raise Exception("Node.js not found")
        except:
            logger.error("❌ Node.js is required but not found")
            raise
        
        # Check Python
        try:
            result = subprocess.run(["python", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Python: {result.stdout.strip()}")
            else:
                raise Exception("Python not found")
        except:
            logger.error("❌ Python is required but not found")
            raise
        
        # Check workspace structure
        if self.workspace_path.exists():
            logger.info(f"✅ Workspace found: {self.workspace_path}")
        else:
            logger.error(f"❌ Workspace not found: {self.workspace_path}")
            raise Exception("Workspace directory not found")

    async def create_mcp_server_infrastructure(self):
        """Create MCP server infrastructure"""
        logger.info("🏗️ Creating MCP server infrastructure...")
        
        # Create MCP-Servers directory structure
        mcp_base = self.workspace_path / "MCP-Servers"
        mcp_base.mkdir(exist_ok=True)
        
        # Create individual server directories and basic server files
        for server_name, config in self.mcp_servers.items():
            server_dir = config["working_dir"]
            server_dir.mkdir(parents=True, exist_ok=True)
            
            # Create basic server file if it doesn't exist
            await self.create_mcp_server_file(server_name, config)
            
        logger.info("✅ MCP server infrastructure created")

    async def create_mcp_server_file(self, server_name: str, config: Dict):
        """Create MCP server implementation file"""
        server_file = config["working_dir"] / f"{server_name.replace('-', '_')}_server.py"
        
        if not server_file.exists():
            server_code = self.generate_mcp_server_code(server_name, config)
            with open(server_file, 'w') as f:
                f.write(server_code)
            logger.info(f"  📝 Created {server_name} server file")

    def generate_mcp_server_code(self, server_name: str, config: Dict) -> str:
        """Generate basic MCP server code"""
        capabilities = config.get("capabilities", [])
        port = config.get("port", 3000)
        
        return f'''#!/usr/bin/env python3
"""
{server_name.title()} MCP Server
Generated by MCPVots Ecosystem Builder
"""

import asyncio
import json
import websockets
from datetime import datetime
from typing import Dict, Any, List

class {server_name.title().replace("-", "")}MCPServer:
    """MCP Server for {server_name}"""
    
    def __init__(self, port: int = {port}):
        self.port = port
        self.capabilities = {capabilities}
        self.connections = set()
        
    async def handle_message(self, websocket, message: str):
        """Handle incoming MCP messages"""
        try:
            data = json.loads(message)
            response = await self.process_message(data)
            await websocket.send(json.dumps(response))
        except Exception as e:
            error_response = {{
                "error": {{
                    "code": -1,
                    "message": str(e)
                }}
            }}
            await websocket.send(json.dumps(error_response))
    
    async def process_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process MCP message and return response"""
        message_type = data.get("type", "unknown")
        
        if message_type == "capabilities":
            return {{
                "type": "capabilities_response",
                "capabilities": self.capabilities,
                "server": "{server_name}",
                "timestamp": datetime.now().isoformat()
            }}
        elif message_type == "heartbeat":
            return {{
                "type": "heartbeat_response",
                "timestamp": datetime.now().isoformat()
            }}
        else:
            return {{
                "type": "response",
                "message": f"Processed {{message_type}} request",
                "timestamp": datetime.now().isoformat()
            }}
    
    async def handle_connection(self, websocket, path):
        """Handle new WebSocket connection"""
        self.connections.add(websocket)
        print(f"New connection to {server_name} server: {{len(self.connections)}} total")
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connections.remove(websocket)
            print(f"Connection closed: {{len(self.connections)}} remaining")
    
    async def start_server(self):
        """Start the MCP server"""
        print(f"Starting {server_name} MCP server on port {{self.port}}")
        async with websockets.serve(self.handle_connection, "localhost", self.port):
            print(f"✅ {server_name} MCP server running on ws://localhost:{{self.port}}")
            await asyncio.Future()  # Run forever

if __name__ == "__main__":
    server = {server_name.title().replace("-", "")}MCPServer()
    asyncio.run(server.start_server())
'''

    async def start_mcp_servers(self):
        """Start all MCP servers"""
        logger.info("🚀 Starting MCP servers...")
        
        for server_name, config in self.mcp_servers.items():
            try:
                await self.start_mcp_server(server_name, config)
                self.ecosystem_status["mcp_servers_active"] += 1
            except Exception as e:
                logger.error(f"Failed to start {server_name}: {str(e)}")
                config["status"] = "failed"

    async def start_mcp_server(self, server_name: str, config: Dict):
        """Start individual MCP server"""
        logger.info(f"  Starting {server_name}...")
        
        # Check if already running
        if self.is_port_in_use(config["port"]):
            logger.info(f"  ✅ {server_name} already running on port {config['port']}")
            config["status"] = "running"
            return
        
        # Start the server
        process = subprocess.Popen(
            config["command"],
            cwd=config["working_dir"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes[server_name] = process
        config["status"] = "starting"
        
        # Wait a moment for startup
        await asyncio.sleep(2)
        
        # Verify it's running
        if self.is_port_in_use(config["port"]):
            config["status"] = "running"
            logger.info(f"  ✅ {server_name} started successfully")
        else:
            config["status"] = "failed"
            logger.error(f"  ❌ {server_name} failed to start")

    async def initialize_trilogy_services(self):
        """Initialize Trilogy AGI services"""
        logger.info("🤖 Initializing Trilogy AGI services...")
        
        for service_name, config in self.trilogy_services.items():
            try:
                await self.start_trilogy_service(service_name, config)
                self.ecosystem_status["trilogy_services_active"] += 1
            except Exception as e:
                logger.error(f"Failed to start {service_name}: {str(e)}")
                config["status"] = "failed"

    async def start_trilogy_service(self, service_name: str, config: Dict):
        """Start individual Trilogy service"""
        logger.info(f"  Starting {service_name}...")
        
        # Check if already running
        if self.is_port_in_use(config["port"]):
            logger.info(f"  ✅ {service_name} already running on port {config['port']}")
            config["status"] = "running"
            return
        
        script_path = self.workspace_path / config["script"]
        if not script_path.exists():
            logger.warning(f"  ⚠️ Script not found: {script_path}")
            config["status"] = "missing"
            return
        
        # Start the service
        process = subprocess.Popen(
            ["python", str(script_path)],
            cwd=self.workspace_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes[service_name] = process
        config["status"] = "starting"
        
        # Wait for startup
        await asyncio.sleep(3)
        
        # Verify it's running
        if self.is_port_in_use(config["port"]):
            config["status"] = "running"
            logger.info(f"  ✅ {service_name} started successfully")
        else:
            config["status"] = "failed"
            logger.error(f"  ❌ {service_name} failed to start")

    async def start_core_application(self):
        """Start the core MCPVots application"""
        logger.info("🌐 Starting core MCPVots application...")
        
        # Start the development server
        try:
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=self.base_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes["mcpvots-app"] = process
            await asyncio.sleep(5)
            
            # Check if running
            if self.is_port_in_use(3000):
                logger.info("  ✅ MCPVots application started on http://localhost:3000")
            else:
                logger.error("  ❌ MCPVots application failed to start")
        except Exception as e:
            logger.error(f"Failed to start MCPVots application: {str(e)}")

    async def verify_ecosystem_health(self):
        """Verify the health of the complete ecosystem"""
        logger.info("🏥 Verifying ecosystem health...")
        
        total_services = len(self.mcp_servers) + len(self.trilogy_services)
        healthy_services = 0
        
        # Check MCP servers
        for server_name, config in self.mcp_servers.items():
            if await self.check_service_health(config["port"], "/health"):
                healthy_services += 1
                logger.info(f"  ✅ {server_name}: Healthy")
            else:
                logger.warning(f"  ⚠️ {server_name}: Not responding")
        
        # Check Trilogy services
        for service_name, config in self.trilogy_services.items():
            if await self.check_service_health(config["port"], "/health"):
                healthy_services += 1
                logger.info(f"  ✅ {service_name}: Healthy")
            else:
                logger.warning(f"  ⚠️ {service_name}: Not responding")
        
        self.ecosystem_status["health_score"] = healthy_services / total_services
        logger.info(f"  📊 Health Score: {self.ecosystem_status['health_score']:.1%} ({healthy_services}/{total_services})")

    async def check_service_health(self, port: int, endpoint: str = "/health") -> bool:
        """Check if a service is healthy"""
        try:
            response = requests.get(f"http://localhost:{port}{endpoint}", timeout=2)
            return response.status_code == 200
        except:
            return False

    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return True
        return False

    async def generate_ecosystem_report(self):
        """Generate comprehensive ecosystem status report"""
        logger.info("📊 Generating ecosystem status report...")
        
        report = {
            "ecosystem_status": self.ecosystem_status,
            "mcp_servers": {name: {"status": config["status"], "port": config["port"]} 
                          for name, config in self.mcp_servers.items()},
            "trilogy_services": {name: {"status": config["status"], "port": config["port"]} 
                               for name, config in self.trilogy_services.items()},
            "generated_at": datetime.now().isoformat()
        }
        
        report_file = self.base_path / "ecosystem_status_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"  📄 Report saved to: {report_file}")
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("🎉 MCPVOTS ECOSYSTEM STATUS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"🏥 Health Score: {self.ecosystem_status['health_score']:.1%}")
        logger.info(f"🔌 MCP Servers Active: {self.ecosystem_status['mcp_servers_active']}/{len(self.mcp_servers)}")
        logger.info(f"🤖 Trilogy Services Active: {self.ecosystem_status['trilogy_services_active']}/{len(self.trilogy_services)}")
        logger.info(f"⏱️ Build Time: {datetime.now() - self.ecosystem_status['start_time']}")
        logger.info("=" * 60)

    def cleanup(self):
        """Cleanup running processes"""
        logger.info("🧹 Cleaning up processes...")
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"  ✅ Terminated {name}")
            except:
                process.kill()
                logger.info(f"  🔪 Killed {name}")

async def main():
    """Main entry point"""
    builder = MCPVotsEcosystemBuilder()
    
    try:
        await builder.build_ecosystem()
    except KeyboardInterrupt:
        logger.info("🛑 Build interrupted by user")
    except Exception as e:
        logger.error(f"❌ Build failed: {str(e)}")
    finally:
        builder.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
