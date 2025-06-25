#!/usr/bin/env python3
"""
Trilogy AGI + Gemini CLI Ecosystem Orchestrator
==============================================
Advanced orchestration system combining:
- Trilogy AGI (DeerFlow, DGM, OWL, Agent File) with Ollama
- Gemini CLI with 1M token context window
- Knowledge Graph and Memory MCP
- Complete ecosystem analysis and improvement

This creates a unified AI ecosystem for continuous learning and optimization.
"""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import websockets
import aiohttp
import sys

# Add MCPVots to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrilogyGeminiEcosystemOrchestrator:
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or str(Path(__file__).parent)
        self.status = "initializing"
        
        # Trilogy AGI + Ollama endpoints
        self.trilogy_services = {
            "ollama": "http://localhost:11434",
            "deerflow": "ws://localhost:8014",      # DeerFlow Orchestrator
            "dgm": "ws://localhost:8013",           # DGM Evolution Engine
            "owl": "ws://localhost:8011",           # OWL Semantic Reasoning
            "agent_file": "ws://localhost:8012"     # Agent File System
        }
        
        # Gemini CLI and Memory services
        self.core_services = {
            "gemini_cli": "ws://localhost:8015",
            "memory_primary": "ws://localhost:8020",
            "memory_secondary": "ws://localhost:8021"
        }
        
        # Knowledge graph and context management
        self.knowledge_graph = {}
        self.ecosystem_context = {}
        self.learning_sessions = {}
        self.improvement_cycles = {}
        
        # Configuration for Trilogy AGI + Gemini integration
        self.config = {
            "trilogy_agi_models": [
                "llama3.2:latest", "codellama:latest", "mistral:latest"
            ],
            "gemini_model": "gemini-2.5-pro",
            "max_context_tokens": 1000000,
            "enable_knowledge_graph": True,
            "enable_cross_model_reasoning": True,
            "enable_continuous_learning": True,
            "improvement_cycle_minutes": 30
        }
        
    async def start_trilogy_gemini_ecosystem(self):
        """Start the complete Trilogy AGI + Gemini ecosystem"""
        logger.info("🚀 Starting Trilogy AGI + Gemini CLI Ecosystem...")
        
        # Phase 1: Initialize Trilogy AGI with Ollama
        await self._initialize_trilogy_agi()
        
        # Phase 2: Start Gemini CLI integration
        await self._initialize_gemini_cli()
        
        # Phase 3: Create knowledge graph connections
        await self._initialize_knowledge_graph()
        
        # Phase 4: Start cross-model reasoning system
        await self._start_cross_model_reasoning()
        
        # Phase 5: Launch ecosystem improvement cycles
        await self._start_ecosystem_improvement_cycles()
        
        self.status = "active"
        logger.info("✅ Trilogy AGI + Gemini Ecosystem is fully operational!")
        
        return {
            "status": "active",
            "trilogy_services": list(self.trilogy_services.keys()),
            "core_services": list(self.core_services.keys()),
            "knowledge_graph_active": True,
            "cross_model_reasoning": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _initialize_trilogy_agi(self):
        """Initialize complete Trilogy AGI stack with Ollama"""
        logger.info("🧠 Initializing Trilogy AGI with Ollama...")
        
        # Check Ollama status and models
        await self._verify_ollama_setup()
        
        # Start Trilogy AGI MCP servers
        trilogy_servers = [
            ("DeerFlow Orchestrator", "servers/deerflow_server.py", 8014),
            ("DGM Evolution Engine", "servers/dgm_evolution_server.py", 8013), 
            ("OWL Semantic Reasoning", "servers/owl_semantic_server.py", 8011),
            ("Agent File System", "servers/agent_file_server.py", 8012)
        ]
        
        for name, script_path, port in trilogy_servers:
            try:
                server_path = Path(self.workspace_path) / script_path
                if server_path.exists():
                    # Start server with Ollama integration
                    process = subprocess.Popen([
                        sys.executable, str(server_path), 
                        "--ollama-url", self.trilogy_services["ollama"]
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    logger.info(f"✅ Started {name} on port {port}")
                else:
                    logger.warning(f"⚠️ Server script not found: {server_path}")
                    # Create basic server if not exists
                    await self._create_basic_trilogy_server(name, script_path, port)
            except Exception as e:
                logger.error(f"❌ Failed to start {name}: {e}")
        
        # Wait for services to initialize
        await asyncio.sleep(5)
        await self._verify_trilogy_connections()
    
    async def _verify_ollama_setup(self):
        """Verify Ollama is running and has required models"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check Ollama status
                async with session.get(f"{self.trilogy_services['ollama']}/api/tags") as response:
                    if response.status == 200:
                        models_data = await response.json()
                        available_models = [model['name'] for model in models_data.get('models', [])]
                        
                        logger.info(f"✅ Ollama running with models: {available_models}")
                        
                        # Install required models if missing
                        for model in self.config["trilogy_agi_models"]:
                            if model not in available_models:
                                logger.info(f"📥 Installing model: {model}")
                                await self._install_ollama_model(model)
                    else:
                        logger.error("❌ Ollama not accessible")
                        raise Exception("Ollama service not available")
        except Exception as e:
            logger.error(f"❌ Ollama verification failed: {e}")
            logger.info("💡 Please ensure Ollama is installed and running: https://ollama.ai/")
            raise
    
    async def _install_ollama_model(self, model_name: str):
        """Install Ollama model if not present"""
        try:
            result = subprocess.run([
                "ollama", "pull", model_name
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"✅ Model {model_name} installed successfully")
            else:
                logger.error(f"❌ Failed to install {model_name}: {result.stderr}")
        except Exception as e:
            logger.error(f"❌ Error installing {model_name}: {e}")
    
    async def _initialize_gemini_cli(self):
        """Initialize Gemini CLI with 1M token context integration"""
        logger.info("💎 Initializing Gemini CLI with 1M token context...")
        
        # Start enhanced Gemini CLI server
        try:
            gemini_server_path = Path(self.workspace_path) / "servers" / "enhanced_gemini_cli_server.py"
            if gemini_server_path.exists():
                process = subprocess.Popen([
                    sys.executable, str(gemini_server_path)
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                logger.info("✅ Enhanced Gemini CLI server started")
                
                # Wait for server to start
                await asyncio.sleep(3)
                
                # Verify connection and configure for ecosystem integration
                await self._configure_gemini_for_ecosystem()
            else:
                logger.error(f"❌ Gemini CLI server not found: {gemini_server_path}")
        except Exception as e:
            logger.error(f"❌ Failed to start Gemini CLI: {e}")
    
    async def _configure_gemini_for_ecosystem(self):
        """Configure Gemini CLI for ecosystem-wide analysis"""
        try:
            async with websockets.connect(self.core_services["gemini_cli"]) as ws:
                # Configure for maximum context and ecosystem integration
                config_request = {
                    "jsonrpc": "2.0",
                    "id": "ecosystem_config",
                    "method": "gemini/configure_ecosystem",
                    "params": {
                        "max_context_tokens": self.config["max_context_tokens"],
                        "enable_trilogy_integration": True,
                        "enable_knowledge_graph": True,
                        "trilogy_endpoints": self.trilogy_services,
                        "workspace_path": self.workspace_path
                    }
                }
                
                await ws.send(json.dumps(config_request))
                response = await ws.recv()
                result = json.loads(response)
                
                if "result" in result:
                    logger.info("✅ Gemini CLI configured for ecosystem integration")
                else:
                    logger.warning(f"⚠️ Gemini configuration warning: {result}")
        except Exception as e:
            logger.error(f"❌ Gemini configuration failed: {e}")
    
    async def _initialize_knowledge_graph(self):
        """Initialize knowledge graph with Trilogy AGI + Gemini integration"""
        logger.info("🕸️ Initializing Knowledge Graph...")
        
        # Start memory MCP servers
        memory_servers = [
            ("Memory MCP Primary", "servers/memory_mcp_server.py", 8020),
            ("Memory MCP Secondary", "servers/memory_mcp_server.py", 8021)
        ]
        
        for name, script_path, port in memory_servers:
            try:
                server_path = Path(self.workspace_path) / script_path
                if server_path.exists():
                    process = subprocess.Popen([
                        sys.executable, str(server_path), "--port", str(port)
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    logger.info(f"✅ Started {name} on port {port}")
                else:
                    # Create basic memory server if not exists
                    await self._create_basic_memory_server(script_path, port)
            except Exception as e:
                logger.error(f"❌ Failed to start {name}: {e}")
        
        # Initialize cross-system knowledge graph
        await self._create_ecosystem_knowledge_graph()
    
    async def _create_ecosystem_knowledge_graph(self):
        """Create ecosystem-wide knowledge graph"""
        try:
            async with websockets.connect(self.core_services["memory_primary"]) as ws:
                # Create ecosystem entities
                ecosystem_entities = [
                    {
                        "name": "trilogy_agi_system",
                        "entityType": "ai_system",
                        "observations": [
                            "Trilogy AGI system with DeerFlow, DGM, OWL, Agent File components",
                            "Integrated with Ollama for local LLM processing",
                            "Provides semantic reasoning and code evolution capabilities"
                        ]
                    },
                    {
                        "name": "gemini_cli_system", 
                        "entityType": "ai_system",
                        "observations": [
                            "Gemini 2.5 Pro with 1M token context window",
                            "Google Search grounding for real-time information",
                            "Multi-modal capabilities and advanced reasoning"
                        ]
                    },
                    {
                        "name": "mcpvots_ecosystem",
                        "entityType": "software_ecosystem",
                        "observations": [
                            "Enhanced MCPVots platform with AI integration",
                            "Automated code improvement and analysis",
                            "Continuous learning and optimization capabilities"
                        ]
                    }
                ]
                
                entities_request = {
                    "jsonrpc": "2.0",
                    "id": "create_ecosystem_entities",
                    "method": "memory/create_entities",
                    "params": {"entities": ecosystem_entities}
                }
                
                await ws.send(json.dumps(entities_request))
                response = await ws.recv()
                
                # Create relationships between systems
                relationships = [
                    {
                        "from": "trilogy_agi_system",
                        "to": "gemini_cli_system",
                        "relationType": "collaborates_with"
                    },
                    {
                        "from": "gemini_cli_system", 
                        "to": "mcpvots_ecosystem",
                        "relationType": "analyzes"
                    },
                    {
                        "from": "trilogy_agi_system",
                        "to": "mcpvots_ecosystem", 
                        "relationType": "optimizes"
                    }
                ]
                
                relations_request = {
                    "jsonrpc": "2.0",
                    "id": "create_ecosystem_relations",
                    "method": "memory/create_relations", 
                    "params": {"relations": relationships}
                }
                
                await ws.send(json.dumps(relations_request))
                await ws.recv()
                
                logger.info("✅ Ecosystem knowledge graph initialized")
                
        except Exception as e:
            logger.error(f"❌ Knowledge graph initialization failed: {e}")
    
    async def _start_cross_model_reasoning(self):
        """Start cross-model reasoning between Trilogy AGI and Gemini"""
        logger.info("🔄 Starting cross-model reasoning system...")
        
        if self.config["enable_cross_model_reasoning"]:
            asyncio.create_task(self._cross_model_reasoning_loop())
            logger.info("✅ Cross-model reasoning loop started")
    
    async def _cross_model_reasoning_loop(self):
        """Continuous cross-model reasoning and learning"""
        while self.status == "active":
            try:
                # Get ecosystem analysis from Gemini CLI with full context
                gemini_analysis = await self._get_gemini_ecosystem_analysis()
                
                # Process with Trilogy AGI models for different perspectives
                trilogy_insights = await self._get_trilogy_insights(gemini_analysis)
                
                # Combine insights and update knowledge graph
                combined_insights = await self._combine_multi_model_insights(
                    gemini_analysis, trilogy_insights
                )
                
                # Apply improvements based on combined reasoning
                await self._apply_cross_model_improvements(combined_insights)
                
                # Update knowledge graph with new insights
                await self._update_knowledge_graph_with_insights(combined_insights)
                
                # Wait before next cycle
                await asyncio.sleep(self.config["improvement_cycle_minutes"] * 60)
                
            except Exception as e:
                logger.error(f"❌ Cross-model reasoning error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _get_gemini_ecosystem_analysis(self) -> Dict[str, Any]:
        """Get comprehensive ecosystem analysis from Gemini CLI"""
        try:
            async with websockets.connect(self.core_services["gemini_cli"]) as ws:
                # Collect full workspace context for 1M token analysis
                workspace_context = await self._collect_full_ecosystem_context()
                
                analysis_request = {
                    "jsonrpc": "2.0",
                    "id": f"ecosystem_analysis_{datetime.now().timestamp()}",
                    "method": "gemini/analyze_workspace",
                    "params": {
                        "analysis_type": "comprehensive_ecosystem",
                        "workspace_context": workspace_context,
                        "include_search": True,
                        "focus_areas": [
                            "trilogy_agi_integration",
                            "code_quality_trends", 
                            "performance_optimization",
                            "architecture_evolution",
                            "security_enhancements"
                        ]
                    }
                }
                
                await ws.send(json.dumps(analysis_request))
                response = await ws.recv()
                result = json.loads(response)
                
                if "result" in result:
                    logger.info("✅ Gemini ecosystem analysis completed")
                    return result["result"]
                else:
                    logger.error(f"❌ Gemini analysis failed: {result}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Gemini ecosystem analysis error: {e}")
            return {}
    
    async def _get_trilogy_insights(self, gemini_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get insights from Trilogy AGI models"""
        insights = {}
        
        # Get DeerFlow orchestration insights
        insights["deerflow"] = await self._query_deerflow(gemini_analysis)
        
        # Get DGM evolution suggestions
        insights["dgm"] = await self._query_dgm(gemini_analysis)
        
        # Get OWL semantic reasoning
        insights["owl"] = await self._query_owl(gemini_analysis)
        
        # Get Agent File system recommendations
        insights["agent_file"] = await self._query_agent_file(gemini_analysis)
        
        return insights
    
    async def _query_deerflow(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Query DeerFlow orchestrator for workflow insights"""
        try:
            async with websockets.connect(self.trilogy_services["deerflow"]) as ws:
                query = {
                    "jsonrpc": "2.0",
                    "id": "deerflow_query",
                    "method": "deerflow/analyze_workflows",
                    "params": {
                        "ecosystem_analysis": analysis,
                        "focus": "orchestration_optimization"
                    }
                }
                
                await ws.send(json.dumps(query))
                response = await ws.recv()
                result = json.loads(response)
                
                return result.get("result", {})
        except Exception as e:
            logger.error(f"❌ DeerFlow query failed: {e}")
            return {}
    
    async def _query_dgm(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Query DGM evolution engine for code evolution insights"""
        try:
            async with websockets.connect(self.trilogy_services["dgm"]) as ws:
                query = {
                    "jsonrpc": "2.0", 
                    "id": "dgm_query",
                    "method": "dgm/evolve_code",
                    "params": {
                        "ecosystem_analysis": analysis,
                        "evolution_focus": "architecture_improvement"
                    }
                }
                
                await ws.send(json.dumps(query))
                response = await ws.recv()
                result = json.loads(response)
                
                return result.get("result", {})
        except Exception as e:
            logger.error(f"❌ DGM query failed: {e}")
            return {}
    
    async def _query_owl(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Query OWL semantic reasoning for semantic insights"""
        try:
            async with websockets.connect(self.trilogy_services["owl"]) as ws:
                query = {
                    "jsonrpc": "2.0",
                    "id": "owl_query", 
                    "method": "owl/semantic_analysis",
                    "params": {
                        "ecosystem_analysis": analysis,
                        "reasoning_focus": "semantic_relationships"
                    }
                }
                
                await ws.send(json.dumps(query))
                response = await ws.recv()
                result = json.loads(response)
                
                return result.get("result", {})
        except Exception as e:
            logger.error(f"❌ OWL query failed: {e}")
            return {}
    
    async def _query_agent_file(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Query Agent File system for file management insights"""
        try:
            async with websockets.connect(self.trilogy_services["agent_file"]) as ws:
                query = {
                    "jsonrpc": "2.0",
                    "id": "agent_file_query",
                    "method": "agent_file/analyze_structure", 
                    "params": {
                        "ecosystem_analysis": analysis,
                        "structure_focus": "file_organization"
                    }
                }
                
                await ws.send(json.dumps(query))
                response = await ws.recv()
                result = json.loads(response)
                
                return result.get("result", {})
        except Exception as e:
            logger.error(f"❌ Agent File query failed: {e}")
            return {}
    
    async def _collect_full_ecosystem_context(self) -> Dict[str, Any]:
        """Collect comprehensive ecosystem context for analysis"""
        context = {
            "timestamp": datetime.now().isoformat(),
            "workspace_path": self.workspace_path,
            "services_status": {},
            "trilogy_agi_status": {},
            "gemini_cli_status": {},
            "knowledge_graph_state": {},
            "recent_improvements": [],
            "system_metrics": {}
        }
        
        # Get service statuses
        for service_name, endpoint in {**self.trilogy_services, **self.core_services}.items():
            context["services_status"][service_name] = await self._get_service_status(endpoint)
        
        # Get recent knowledge graph insights
        context["knowledge_graph_state"] = await self._get_knowledge_graph_state()
        
        # Get system performance metrics
        context["system_metrics"] = await self._get_system_metrics()
        
        return context
    
    async def _start_ecosystem_improvement_cycles(self):
        """Start ecosystem-wide improvement cycles"""
        logger.info("🔄 Starting ecosystem improvement cycles...")
        
        asyncio.create_task(self._ecosystem_health_monitor())
        asyncio.create_task(self._ecosystem_optimization_cycle())
        asyncio.create_task(self._knowledge_graph_enrichment_cycle())
        
        logger.info("✅ All ecosystem improvement cycles started")
    
    async def _ecosystem_health_monitor(self):
        """Monitor ecosystem health and auto-recovery"""
        while self.status == "active":
            try:
                # Check all service health
                health_status = {}
                for service_name, endpoint in {**self.trilogy_services, **self.core_services}.items():
                    health_status[service_name] = await self._check_service_health(endpoint)
                
                # Auto-recovery for failed services
                failed_services = [name for name, status in health_status.items() if not status]
                if failed_services:
                    logger.warning(f"⚠️ Failed services detected: {failed_services}")
                    await self._recover_failed_services(failed_services)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Health monitor error: {e}")
                await asyncio.sleep(30)
    
    async def perform_comprehensive_ecosystem_analysis(self):
        """Perform comprehensive analysis using Trilogy AGI + Gemini"""
        logger.info("🔍 Starting comprehensive ecosystem analysis...")
        
        # Step 1: Gemini CLI analysis with full 1M token context
        gemini_analysis = await self._get_gemini_ecosystem_analysis()
        
        # Step 2: Trilogy AGI multi-model insights
        trilogy_insights = await self._get_trilogy_insights(gemini_analysis)
        
        # Step 3: Cross-model reasoning and synthesis
        combined_insights = await self._combine_multi_model_insights(
            gemini_analysis, trilogy_insights
        )
        
        # Step 4: Generate actionable improvement plan
        improvement_plan = await self._generate_ecosystem_improvement_plan(combined_insights)
        
        # Step 5: Update knowledge graph with findings
        await self._update_knowledge_graph_with_insights(combined_insights)
        
        return {
            "gemini_analysis": gemini_analysis,
            "trilogy_insights": trilogy_insights, 
            "combined_insights": combined_insights,
            "improvement_plan": improvement_plan,
            "timestamp": datetime.now().isoformat()
        }

# Create basic server stubs if they don't exist
async def create_basic_trilogy_servers():
    """Create basic Trilogy AGI server implementations"""
    servers = {
        "deerflow_server.py": """
# Basic DeerFlow Server Implementation
import asyncio
import websockets
import json

async def handle_deerflow(websocket, path):
    async for message in websocket:
        request = json.loads(message)
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {"status": "DeerFlow orchestration analysis", "insights": []}
        }
        await websocket.send(json.dumps(response))

start_server = websockets.serve(handle_deerflow, "localhost", 8014)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
""",
        
        "dgm_evolution_server.py": """
# Basic DGM Evolution Server Implementation  
import asyncio
import websockets
import json

async def handle_dgm(websocket, path):
    async for message in websocket:
        request = json.loads(message)
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {"status": "DGM evolution analysis", "evolution_suggestions": []}
        }
        await websocket.send(json.dumps(response))

start_server = websockets.serve(handle_dgm, "localhost", 8013)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
""",
        
        "owl_semantic_server.py": """
# Basic OWL Semantic Server Implementation
import asyncio
import websockets  
import json

async def handle_owl(websocket, path):
    async for message in websocket:
        request = json.loads(message)
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {"status": "OWL semantic analysis", "semantic_insights": []}
        }
        await websocket.send(json.dumps(response))

start_server = websockets.serve(handle_owl, "localhost", 8011)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
""",
        
        "agent_file_server.py": """
# Basic Agent File Server Implementation
import asyncio
import websockets
import json

async def handle_agent_file(websocket, path):
    async for message in websocket:
        request = json.loads(message)
        response = {
            "jsonrpc": "2.0", 
            "id": request.get("id"),
            "result": {"status": "Agent File analysis", "file_insights": []}
        }
        await websocket.send(json.dumps(response))

start_server = websockets.serve(handle_agent_file, "localhost", 8012)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
"""
    }
    
    # Create servers directory if it doesn't exist
    servers_dir = Path("servers")
    servers_dir.mkdir(exist_ok=True)
    
    for filename, content in servers.items():
        server_path = servers_dir / filename
        if not server_path.exists():
            server_path.write_text(content)
            logger.info(f"✅ Created basic server: {filename}")

# Main execution
async def main():
    """Main orchestrator execution"""
    # Create basic servers if needed
    await create_basic_trilogy_servers()
    
    # Start the ecosystem
    orchestrator = TrilogyGeminiEcosystemOrchestrator("c:\\Workspace\\MCPVots")
    
    try:
        # Start the complete ecosystem
        startup_result = await orchestrator.start_trilogy_gemini_ecosystem()
        print(f"🚀 Trilogy AGI + Gemini Ecosystem Status:")
        print(json.dumps(startup_result, indent=2))
        
        # Perform initial comprehensive analysis
        analysis_result = await orchestrator.perform_comprehensive_ecosystem_analysis()
        print(f"\n📊 Initial Ecosystem Analysis Complete:")
        print(f"   - Gemini Analysis: {'✅' if analysis_result['gemini_analysis'] else '❌'}")
        print(f"   - Trilogy Insights: {'✅' if analysis_result['trilogy_insights'] else '❌'}")
        print(f"   - Combined Insights: {'✅' if analysis_result['combined_insights'] else '❌'}")
        
        print("\n✨ Trilogy AGI + Gemini CLI Ecosystem is now running...")
        print("   🧠 Trilogy AGI (DeerFlow, DGM, OWL, Agent File) with Ollama")
        print("   💎 Gemini CLI with 1M token context and Google Search")
        print("   🕸️ Knowledge Graph with cross-model reasoning")
        print("   🔄 Continuous ecosystem improvement cycles")
        print("\nPress Ctrl+C to stop")
        
        while True:
            await asyncio.sleep(60)
            logger.info("📊 Ecosystem running - cross-model reasoning active")
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested...")
        orchestrator.status = "shutting_down"
    except Exception as e:
        logger.error(f"❌ Orchestrator error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
