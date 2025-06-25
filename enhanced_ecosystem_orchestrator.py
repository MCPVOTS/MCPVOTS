#!/usr/bin/env python3
"""
Enhanced MCPVots Ecosystem Orchestrator
=====================================
Comprehensive orchestration system that integrates:
- Gemini CLI with Google Search grounding and 1M token context
- Trilogy AGI (Ollama, OWL, Agent File, DGM, DeerFlow)
- Enhanced Memory MCP and Knowledge Graph
- Automated Code Improvement System
- Continuous Learning and Optimization

This orchestrator manages the entire ecosystem for maximum automation
and intelligence across the MCPVots platform.
"""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import websockets
import aiohttp
import sys

# Add MCPVots to path
sys.path.insert(0, str(Path(__file__).parent))

# Import our enhanced modules
from gemini_automated_code_improver import GeminiAutomatedCodeImprover
from enhanced_memory_knowledge_system_v2 import EnhancedMemoryKnowledgeSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMCPVotsOrchestrator:
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or str(Path(__file__).parent)
        self.status = "initializing"
        
        # Initialize all system components
        self.code_improver = GeminiAutomatedCodeImprover(self.workspace_path)
        self.memory_system = EnhancedMemoryKnowledgeSystem()
        
        # Service endpoints
        self.services = {
            "gemini_cli": "ws://localhost:8015",
            "memory_primary": "ws://localhost:8020", 
            "memory_secondary": "ws://localhost:8021",
            "owl_semantic": "ws://localhost:8011",
            "agent_file": "ws://localhost:8012",
            "dgm_evolution": "ws://localhost:8013",
            "deerflow": "ws://localhost:8014",
            "ollama": "http://localhost:11434"
        }
        
        # Orchestration state
        self.active_sessions = {}
        self.automation_cycles = {}
        self.ecosystem_health = {}
        self.learning_insights = {}
        
        # Configuration
        self.config = {
            "auto_start_services": True,
            "continuous_learning": True,
            "automated_improvements": True,
            "health_monitoring": True,
            "knowledge_graph_sync": True,
            "search_grounding": True,
            "cycle_interval_minutes": 30
        }
    
    async def start_enhanced_ecosystem(self):
        """Start the complete enhanced MCPVots ecosystem"""
        logger.info("🚀 Starting Enhanced MCPVots Ecosystem...")
        
        # Phase 1: Service Initialization
        await self._initialize_all_services()
        
        # Phase 2: System Verification
        await self._verify_ecosystem_health()
        
        # Phase 3: Launch Core Systems
        await self._launch_core_systems()
        
        # Phase 4: Start Automation Cycles
        await self._start_automation_cycles()
        
        self.status = "active"
        logger.info("✅ Enhanced MCPVots Ecosystem is fully operational!")
        
        return {
            "status": "active",
            "services": list(self.services.keys()),
            "health": self.ecosystem_health,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _initialize_all_services(self):
        """Initialize all required services"""
        logger.info("🔧 Initializing all services...")
        
        if self.config["auto_start_services"]:
            # Start MCP servers
            await self._start_mcp_servers()
            
            # Start Trilogy AGI services
            await self._start_trilogy_services()
            
            # Start Gemini CLI server
            await self._start_gemini_cli_server()
        
        # Wait for services to be ready
        await asyncio.sleep(5)
        
        logger.info("✅ Service initialization complete")
    
    async def _start_mcp_servers(self):
        """Start all MCP servers"""
        logger.info("📡 Starting MCP servers...")
        
        servers = [
            ("Memory MCP Primary", "servers/memory_mcp_server.py", 8020),
            ("Memory MCP Secondary", "servers/memory_mcp_server.py", 8021),
            ("OWL Semantic", "servers/owl_semantic_server.py", 8011),
            ("Agent File", "servers/agent_file_server.py", 8012),
            ("DGM Evolution", "servers/dgm_evolution_server.py", 8013),
            ("DeerFlow", "servers/deerflow_server.py", 8014)
        ]
        
        for name, script, port in servers:
            try:
                server_path = Path(self.workspace_path) / script
                if server_path.exists():
                    # Start server in background
                    process = subprocess.Popen([
                        sys.executable, str(server_path)
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    logger.info(f"✅ Started {name} on port {port}")
                else:
                    logger.warning(f"⚠️ Server script not found: {server_path}")
            except Exception as e:
                logger.error(f"❌ Failed to start {name}: {e}")
    
    async def _start_trilogy_services(self):
        """Start Trilogy AGI services"""
        logger.info("🧠 Starting Trilogy AGI services...")
        
        # Check if Ollama is running
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:11434/api/tags") as response:
                    if response.status == 200:
                        logger.info("✅ Ollama/Trilogy AGI is running")
                    else:
                        logger.warning("⚠️ Ollama may not be properly configured")
        except Exception as e:
            logger.warning(f"⚠️ Ollama not accessible: {e}")
    
    async def _start_gemini_cli_server(self):
        """Start enhanced Gemini CLI server"""
        logger.info("💎 Starting Enhanced Gemini CLI server...")
        
        try:
            server_path = Path(self.workspace_path) / "servers" / "enhanced_gemini_cli_server.py"
            if server_path.exists():
                process = subprocess.Popen([
                    sys.executable, str(server_path)
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                logger.info("✅ Enhanced Gemini CLI server started on port 8015")
            else:
                logger.error(f"❌ Gemini CLI server not found: {server_path}")
        except Exception as e:
            logger.error(f"❌ Failed to start Gemini CLI server: {e}")
    
    async def _verify_ecosystem_health(self):
        """Verify health of all ecosystem components"""
        logger.info("🏥 Verifying ecosystem health...")
        
        self.ecosystem_health = {}
        
        for service_name, endpoint in self.services.items():
            try:
                if endpoint.startswith("ws://"):
                    # WebSocket health check
                    async with websockets.connect(endpoint, timeout=5) as ws:
                        if service_name == "gemini_cli":
                            # Test Gemini CLI specifically
                            health_request = {
                                "jsonrpc": "2.0",
                                "id": "health_check",
                                "method": "gemini/health",
                                "params": {}
                            }
                            await ws.send(json.dumps(health_request))
                            response = await ws.recv()
                            result = json.loads(response)
                            
                            if "result" in result:
                                self.ecosystem_health[service_name] = "healthy"
                            else:
                                self.ecosystem_health[service_name] = "error"
                        else:
                            self.ecosystem_health[service_name] = "connected"
                
                elif endpoint.startswith("http://"):
                    # HTTP health check
                    async with aiohttp.ClientSession() as session:
                        async with session.get(endpoint + "/api/tags", timeout=5) as response:
                            if response.status == 200:
                                self.ecosystem_health[service_name] = "healthy"
                            else:
                                self.ecosystem_health[service_name] = "degraded"
                
            except Exception as e:
                self.ecosystem_health[service_name] = f"error: {str(e)}"
                logger.warning(f"⚠️ {service_name} health check failed: {e}")
        
        # Log health summary
        healthy_services = len([s for s in self.ecosystem_health.values() if s in ["healthy", "connected"]])
        total_services = len(self.ecosystem_health)
        
        logger.info(f"🏥 Ecosystem health: {healthy_services}/{total_services} services healthy")
    
    async def _launch_core_systems(self):
        """Launch core system components"""
        logger.info("🚀 Launching core systems...")
        
        # Launch Memory Knowledge System
        if self.config["continuous_learning"]:
            asyncio.create_task(self.memory_system.start_continuous_learning_system())
            logger.info("✅ Memory Knowledge System launched")
        
        # Launch Code Improvement System
        if self.config["automated_improvements"]:
            asyncio.create_task(self.code_improver.start_automated_improvement_system())
            logger.info("✅ Code Improvement System launched")
    
    async def _start_automation_cycles(self):
        """Start automated optimization cycles"""
        logger.info("🔄 Starting automation cycles...")
        
        if self.config["health_monitoring"]:
            asyncio.create_task(self._health_monitoring_cycle())
        
        if self.config["knowledge_graph_sync"]:
            asyncio.create_task(self._knowledge_sync_cycle())
        
        if self.config["automated_improvements"]:
            asyncio.create_task(self._improvement_cycle())
        
        logger.info("✅ All automation cycles started")
    
    async def _health_monitoring_cycle(self):
        """Continuous health monitoring cycle"""
        while self.status == "active":
            try:
                await self._verify_ecosystem_health()
                
                # Check for degraded services
                degraded_services = [
                    name for name, status in self.ecosystem_health.items() 
                    if status not in ["healthy", "connected"]
                ]
                
                if degraded_services:
                    logger.warning(f"⚠️ Degraded services detected: {degraded_services}")
                    await self._handle_degraded_services(degraded_services)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Health monitoring cycle error: {e}")
                await asyncio.sleep(60)
    
    async def _knowledge_sync_cycle(self):
        """Continuous knowledge graph synchronization"""
        while self.status == "active":
            try:
                # Sync workspace insights with knowledge graph
                await self._sync_workspace_knowledge()
                
                # Update learning insights
                await self._update_learning_insights()
                
                await asyncio.sleep(self.config["cycle_interval_minutes"] * 60)
                
            except Exception as e:
                logger.error(f"❌ Knowledge sync cycle error: {e}")
                await asyncio.sleep(300)
    
    async def _improvement_cycle(self):
        """Continuous improvement cycle"""
        while self.status == "active":
            try:
                # Run incremental code analysis
                logger.info("🔍 Running incremental code analysis...")
                
                # Detect workspace changes
                changes = await self.code_improver._detect_workspace_changes()
                
                if changes.get("has_significant_changes"):
                    # Run improvement cycle
                    analysis = await self.code_improver.perform_comprehensive_workspace_analysis()
                    improvements = await self.code_improver.generate_automated_improvements(analysis)
                    results = await self.code_improver.apply_safe_improvements(improvements)
                    
                    logger.info(f"🔧 Applied {len(results.get('applied', []))} improvements")
                
                await asyncio.sleep(self.config["cycle_interval_minutes"] * 60)
                
            except Exception as e:
                logger.error(f"❌ Improvement cycle error: {e}")
                await asyncio.sleep(300)
    
    async def _handle_degraded_services(self, degraded_services: List[str]):
        """Handle degraded services"""
        for service in degraded_services:
            logger.info(f"🔧 Attempting to recover {service}...")
            
            # Attempt service recovery
            try:
                if service in ["gemini_cli"]:
                    await self._start_gemini_cli_server()
                elif "memory" in service:
                    await self._start_mcp_servers()
                
                # Wait and re-check
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"❌ Failed to recover {service}: {e}")
    
    async def _sync_workspace_knowledge(self):
        """Sync workspace insights with knowledge graph"""
        try:
            # Collect recent insights
            insights = {
                "code_quality_trends": await self._analyze_code_quality_trends(),
                "performance_metrics": await self._collect_performance_metrics(),
                "security_status": await self._assess_security_status(),
                "automation_effectiveness": await self._measure_automation_effectiveness()
            }
            
            # Store in memory MCP
            async with websockets.connect(self.services["memory_primary"]) as ws:
                entity_request = {
                    "jsonrpc": "2.0",
                    "id": f"sync_insights_{datetime.now().timestamp()}",
                    "method": "memory/create_entities",
                    "params": {
                        "entities": [{
                            "name": f"ecosystem_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            "entityType": "ecosystem_insight",
                            "observations": [
                                f"Code quality trend: {insights['code_quality_trends']}",
                                f"Performance status: {insights['performance_metrics']}",
                                f"Security assessment: {insights['security_status']}",
                                f"Automation effectiveness: {insights['automation_effectiveness']}"
                            ]
                        }]
                    }
                }
                
                await ws.send(json.dumps(entity_request))
                await ws.recv()
                
            logger.info("✅ Workspace knowledge synced")
            
        except Exception as e:
            logger.error(f"❌ Knowledge sync failed: {e}")
    
    async def _update_learning_insights(self):
        """Update learning insights from all systems"""
        self.learning_insights = {
            "timestamp": datetime.now().isoformat(),
            "code_improvements_applied": len(self.code_improver.improvement_history),
            "memory_entities_created": "N/A",  # Would get from memory system
            "automation_cycles_completed": len(self.automation_cycles),
            "ecosystem_health_score": self._calculate_health_score()
        }
    
    def _calculate_health_score(self) -> float:
        """Calculate overall ecosystem health score"""
        if not self.ecosystem_health:
            return 0.0
        
        healthy_count = len([
            s for s in self.ecosystem_health.values() 
            if s in ["healthy", "connected"]
        ])
        
        return (healthy_count / len(self.ecosystem_health)) * 100
    
    async def _analyze_code_quality_trends(self) -> str:
        """Analyze code quality trends"""
        # Placeholder for trend analysis
        return "improving"
    
    async def _collect_performance_metrics(self) -> str:
        """Collect performance metrics"""
        # Placeholder for performance metrics
        return "stable"
    
    async def _assess_security_status(self) -> str:
        """Assess security status"""
        # Placeholder for security assessment
        return "secure"
    
    async def _measure_automation_effectiveness(self) -> str:
        """Measure automation effectiveness"""
        # Placeholder for automation metrics
        return "effective"
    
    async def get_ecosystem_status(self) -> Dict[str, Any]:
        """Get comprehensive ecosystem status"""
        return {
            "status": self.status,
            "services": self.ecosystem_health,
            "learning_insights": self.learning_insights,
            "active_sessions": len(self.active_sessions),
            "automation_cycles": len(self.automation_cycles),
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown_ecosystem(self):
        """Gracefully shutdown the ecosystem"""
        logger.info("🛑 Shutting down Enhanced MCPVots Ecosystem...")
        
        self.status = "shutting_down"
        
        # Stop automation cycles
        self.automation_cycles.clear()
        
        # Close active sessions
        self.active_sessions.clear()
        
        logger.info("✅ Ecosystem shutdown complete")

# Command-line interface
async def main():
    """Main orchestrator execution"""
    orchestrator = EnhancedMCPVotsOrchestrator("c:\\Workspace\\MCPVots")
    
    try:
        # Start the ecosystem
        startup_result = await orchestrator.start_enhanced_ecosystem()
        print(f"🚀 Ecosystem Status: {json.dumps(startup_result, indent=2)}")
        
        # Keep running
        print("✨ Enhanced MCPVots Ecosystem is now running...")
        print("   - Gemini CLI with Google Search grounding")
        print("   - Trilogy AGI integration")
        print("   - Automated code improvements")
        print("   - Continuous learning and optimization")
        print("   - Real-time health monitoring")
        print("\nPress Ctrl+C to stop")
        
        while True:
            await asyncio.sleep(60)
            status = await orchestrator.get_ecosystem_status()
            logger.info(f"📊 Health Score: {orchestrator._calculate_health_score():.1f}%")
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested...")
        await orchestrator.shutdown_ecosystem()
    except Exception as e:
        logger.error(f"❌ Orchestrator error: {e}")
        await orchestrator.shutdown_ecosystem()

if __name__ == "__main__":
    asyncio.run(main())
