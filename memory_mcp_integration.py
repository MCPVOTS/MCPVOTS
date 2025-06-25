#!/usr/bin/env python3
"""
Memory MCP Integration for MCPVots Intelligence System
====================================================
Integrates with existing Memory MCP servers to store and retrieve
knowledge graph data, learning insights, and automation rules.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import websockets

class MemoryMCPIntegration:
    def __init__(self):
        # These should match your existing memory server configurations
        self.memory_servers = {
            "primary": "ws://localhost:8020",    # Primary memory server
            "secondary": "ws://localhost:8021"   # Secondary memory server if available
        }
        
    async def store_ecosystem_knowledge(self, ecosystem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store ecosystem analysis in memory MCP knowledge graph"""
        print("💾 Storing ecosystem knowledge in Memory MCP...")
        
        # Extract entities for knowledge graph storage
        entities_to_create = []
        relations_to_create = []
        observations_to_add = []
        
        # Process repository analysis
        if "repo_analysis" in ecosystem_data:
            repo_data = ecosystem_data["repo_analysis"]
            
            # Create entities for major components
            if "structured_insights" in repo_data:
                insights = repo_data["structured_insights"]
                
                # Create entities from components
                for i, entity_desc in enumerate(insights.get("entities", [])):
                    entities_to_create.append({
                        "name": f"MCPVots_Component_{i}",
                        "entityType": "architectural_component",
                        "observations": [
                            entity_desc,
                            f"Discovered in analysis at {datetime.now().isoformat()}",
                            "Part of MCPVots ecosystem"
                        ]
                    })
                
                # Create technology stack entities
                if "repo_data" in repo_data and "configurations" in repo_data["repo_data"]:
                    configs = repo_data["repo_data"]["configurations"]
                    
                    if "package.json" in configs:
                        pkg_data = configs["package.json"].get("parsed", {})
                        
                        # Node.js project entity
                        entities_to_create.append({
                            "name": "MCPVots_Frontend",
                            "entityType": "frontend_application",
                            "observations": [
                                f"Next.js application: {pkg_data.get('name', 'mcpvots')}",
                                f"Dependencies: {len(pkg_data.get('dependencies', {}))}",
                                f"Dev dependencies: {len(pkg_data.get('devDependencies', {}))}",
                                f"Scripts available: {len(pkg_data.get('scripts', {}))}",
                                "Modern React/TypeScript frontend"
                            ]
                        })
                    
                    if "pyproject.toml" in configs:
                        # Python backend entity
                        entities_to_create.append({
                            "name": "MCPVots_Backend",
                            "entityType": "backend_services",
                            "observations": [
                                "Python-based microservices architecture",
                                "Multiple MCP servers for different capabilities",
                                "FastAPI/WebSocket based communication",
                                "Integrated AI/ML capabilities"
                            ]
                        })
        
        # Process Trilogy AGI insights
        if "trilogy_insights" in ecosystem_data:
            trilogy_data = ecosystem_data["trilogy_insights"]
            
            entities_to_create.append({
                "name": "Trilogy_AGI_System",
                "entityType": "ai_system",
                "observations": [
                    "OWL semantic reasoning integration",
                    "Agent File system for code management",
                    "DGM dynamic graph modeling",
                    "DeerFlow workflow automation",
                    "Integrated with MCPVots ecosystem"
                ]
            })
        
        # Create Gemini AI entity
        entities_to_create.append({
            "name": "Gemini_2_5_Pro",
            "entityType": "ai_model",
            "observations": [
                "1M token context window capability",
                "Integrated via MCP server on port 8015",
                "Provides architectural analysis and insights",
                "Used for code analysis and optimization",
                "Free tier: 60 requests/min, 1000/day"
            ]
        })
        
        # Create relationships
        relations_to_create.extend([
            {
                "from": "MCPVots_Frontend",
                "to": "MCPVots_Backend", 
                "relationType": "communicates_with"
            },
            {
                "from": "MCPVots_Backend",
                "to": "Trilogy_AGI_System",
                "relationType": "integrates_with"
            },
            {
                "from": "Gemini_2_5_Pro",
                "to": "MCPVots_Backend",
                "relationType": "provides_analysis_for"
            },
            {
                "from": "Trilogy_AGI_System",
                "to": "MCPVots_Frontend",
                "relationType": "enhances"
            }
        ])
        
        # Store in Memory MCP
        results = {}
        
        try:
            # Try primary memory server first
            server_url = self.memory_servers["primary"]
            results = await self._store_in_memory_server(
                server_url, entities_to_create, relations_to_create, observations_to_add
            )
            print(f"✅ Stored in primary memory server")
            
        except Exception as e:
            print(f"⚠️ Primary memory server failed: {e}")
            
            # Try secondary server
            try:
                server_url = self.memory_servers["secondary"]
                results = await self._store_in_memory_server(
                    server_url, entities_to_create, relations_to_create, observations_to_add
                )
                print(f"✅ Stored in secondary memory server")
                
            except Exception as e2:
                print(f"❌ All memory servers failed: {e2}")
                results = {"error": f"Memory storage failed: {e}, {e2}"}
        
        return results
    
    async def _store_in_memory_server(self, server_url: str, entities: List[Dict], 
                                    relations: List[Dict], observations: List[Dict]) -> Dict[str, Any]:
        """Store data in a specific memory server"""
        
        try:
            async with websockets.connect(server_url) as websocket:
                results = {"entities_created": 0, "relations_created": 0, "observations_added": 0}
                
                # Create entities
                if entities:
                    create_entities_msg = {
                        "jsonrpc": "2.0",
                        "id": "create_entities",
                        "method": "memory/create_entities",
                        "params": {"entities": entities}
                    }
                    
                    await websocket.send(json.dumps(create_entities_msg))
                    response = await websocket.recv()
                    result = json.loads(response)
                    
                    if "result" in result:
                        results["entities_created"] = len(entities)
                        print(f"   📝 Created {len(entities)} entities")
                    else:
                        print(f"   ⚠️ Entity creation error: {result}")
                
                # Create relations
                if relations:
                    create_relations_msg = {
                        "jsonrpc": "2.0",
                        "id": "create_relations",
                        "method": "memory/create_relations",
                        "params": {"relations": relations}
                    }
                    
                    await websocket.send(json.dumps(create_relations_msg))
                    response = await websocket.recv()
                    result = json.loads(response)
                    
                    if "result" in result:
                        results["relations_created"] = len(relations)
                        print(f"   🔗 Created {len(relations)} relations")
                    else:
                        print(f"   ⚠️ Relations creation error: {result}")
                
                return results
                
        except Exception as e:
            raise Exception(f"Memory server connection failed: {e}")
    
    async def retrieve_ecosystem_knowledge(self, query: str = "MCPVots") -> Dict[str, Any]:
        """Retrieve ecosystem knowledge from Memory MCP"""
        print(f"🔍 Retrieving ecosystem knowledge: {query}")
        
        try:
            server_url = self.memory_servers["primary"]
            async with websockets.connect(server_url) as websocket:
                
                # Search for relevant nodes
                search_msg = {
                    "jsonrpc": "2.0",
                    "id": "search_knowledge",
                    "method": "memory/search_nodes",
                    "params": {"query": query}
                }
                
                await websocket.send(json.dumps(search_msg))
                response = await websocket.recv()
                result = json.loads(response)
                
                if "result" in result:
                    knowledge = result["result"]
                    print(f"✅ Retrieved knowledge: {len(knowledge.get('nodes', []))} nodes found")
                    return knowledge
                else:
                    print(f"❌ Knowledge retrieval failed: {result}")
                    return {"error": result.get("error", "Unknown error")}
                    
        except Exception as e:
            print(f"❌ Memory retrieval failed: {e}")
            return {"error": str(e)}
    
    async def update_learning_observations(self, entity_name: str, new_observations: List[str]) -> Dict[str, Any]:
        """Add new learning observations to an existing entity"""
        print(f"📝 Adding learning observations to {entity_name}")
        
        try:
            server_url = self.memory_servers["primary"]
            async with websockets.connect(server_url) as websocket:
                
                # Add observations
                add_obs_msg = {
                    "jsonrpc": "2.0",
                    "id": "add_observations",
                    "method": "memory/add_observations",
                    "params": {
                        "observations": [{
                            "entityName": entity_name,
                            "contents": new_observations
                        }]
                    }
                }
                
                await websocket.send(json.dumps(add_obs_msg))
                response = await websocket.recv()
                result = json.loads(response)
                
                if "result" in result:
                    print(f"✅ Added {len(new_observations)} observations")
                    return {"success": True, "observations_added": len(new_observations)}
                else:
                    print(f"❌ Failed to add observations: {result}")
                    return {"error": result.get("error", "Unknown error")}
                    
        except Exception as e:
            print(f"❌ Observation update failed: {e}")
            return {"error": str(e)}
    
    async def get_knowledge_graph_summary(self) -> Dict[str, Any]:
        """Get a summary of the current knowledge graph"""
        print("📊 Getting knowledge graph summary...")
        
        try:
            server_url = self.memory_servers["primary"]
            async with websockets.connect(server_url) as websocket:
                
                # Read entire graph
                read_graph_msg = {
                    "jsonrpc": "2.0",
                    "id": "read_graph",
                    "method": "memory/read_graph",
                    "params": {}
                }
                
                await websocket.send(json.dumps(read_graph_msg))
                response = await websocket.recv()
                result = json.loads(response)
                
                if "result" in result:
                    graph_data = result["result"]
                    
                    summary = {
                        "total_entities": len(graph_data.get("entities", [])),
                        "total_relations": len(graph_data.get("relations", [])),
                        "entity_types": {},
                        "relation_types": {}
                    }
                    
                    # Analyze entity types
                    for entity in graph_data.get("entities", []):
                        entity_type = entity.get("entityType", "unknown")
                        summary["entity_types"][entity_type] = summary["entity_types"].get(entity_type, 0) + 1
                    
                    # Analyze relation types
                    for relation in graph_data.get("relations", []):
                        relation_type = relation.get("relationType", "unknown")
                        summary["relation_types"][relation_type] = summary["relation_types"].get(relation_type, 0) + 1
                    
                    print(f"✅ Knowledge graph summary: {summary['total_entities']} entities, {summary['total_relations']} relations")
                    return summary
                    
                else:
                    print(f"❌ Failed to read graph: {result}")
                    return {"error": result.get("error", "Unknown error")}
                    
        except Exception as e:
            print(f"❌ Graph summary failed: {e}")
            return {"error": str(e)}

# Integration with continuous learning
class ContinuousLearningEngine:
    def __init__(self):
        self.memory_integration = MemoryMCPIntegration()
        self.learning_history = []
        
    async def process_new_insights(self, insights: Dict[str, Any]) -> None:
        """Process and store new insights for continuous learning"""
        print("🧠 Processing new insights for continuous learning...")
        
        # Extract learning patterns
        learning_data = {
            "timestamp": datetime.now().isoformat(),
            "insights": insights,
            "patterns_detected": await self._detect_patterns(insights),
            "automation_suggestions": await self._generate_automation_suggestions(insights)
        }
        
        # Store in memory
        await self.memory_integration.store_ecosystem_knowledge(learning_data)
        
        # Update learning history
        self.learning_history.append(learning_data)
        
        # Trigger adaptive responses if needed
        await self._trigger_adaptive_responses(learning_data)
    
    async def _detect_patterns(self, insights: Dict[str, Any]) -> List[str]:
        """Detect recurring patterns in insights"""
        patterns = []
        
        # Simple pattern detection logic
        if "performance" in str(insights).lower():
            patterns.append("performance_optimization_needed")
        
        if "security" in str(insights).lower():
            patterns.append("security_review_required")
        
        if "automation" in str(insights).lower():
            patterns.append("automation_opportunity_identified")
        
        return patterns
    
    async def _generate_automation_suggestions(self, insights: Dict[str, Any]) -> List[str]:
        """Generate automation suggestions based on insights"""
        suggestions = []
        
        # Generate suggestions based on content
        content_str = str(insights).lower()
        
        if "test" in content_str:
            suggestions.append("Implement automated testing pipeline")
        
        if "deploy" in content_str:
            suggestions.append("Set up automated deployment workflow")
        
        if "monitor" in content_str:
            suggestions.append("Configure automated monitoring and alerting")
        
        return suggestions
    
    async def _trigger_adaptive_responses(self, learning_data: Dict[str, Any]) -> None:
        """Trigger adaptive responses based on learning patterns"""
        patterns = learning_data.get("patterns_detected", [])
        
        for pattern in patterns:
            if pattern == "performance_optimization_needed":
                print("🚀 Triggering performance optimization workflow...")
                # Could trigger DeerFlow automation here
                
            elif pattern == "security_review_required":
                print("🔒 Triggering security review workflow...")
                # Could trigger security scanning automation
                
            elif pattern == "automation_opportunity_identified":
                print("⚙️ Triggering automation enhancement workflow...")
                # Could update automation rules

async def test_memory_integration():
    """Test the memory MCP integration"""
    print("🧪 Testing Memory MCP Integration")
    print("=" * 40)
    
    memory_integration = MemoryMCPIntegration()
    
    # Test data
    test_ecosystem_data = {
        "repo_analysis": {
            "structured_insights": {
                "entities": ["Frontend React Application", "Backend Python Services"],
                "relationships": ["Frontend communicates with Backend via WebSocket"],
                "patterns": ["Microservices architecture pattern"]
            },
            "repo_data": {
                "configurations": {
                    "package.json": {
                        "parsed": {
                            "name": "mcpvots",
                            "dependencies": {"react": "^18.0.0"},
                            "devDependencies": {"typescript": "^5.0.0"},
                            "scripts": {"dev": "next dev"}
                        }
                    }
                }
            }
        },
        "trilogy_insights": {
            "owl_reasoning": {"status": "active"},
            "agent_file_insights": {"templates": "managed"},
            "dgm_modeling": {"graphs": "dynamic"},
            "deerflow_automation": {"workflows": "automated"}
        }
    }
    
    try:
        # Test storing knowledge
        store_result = await memory_integration.store_ecosystem_knowledge(test_ecosystem_data)
        print(f"📝 Storage result: {store_result}")
        
        # Test retrieving knowledge
        retrieve_result = await memory_integration.retrieve_ecosystem_knowledge("MCPVots")
        print(f"🔍 Retrieval result: {retrieve_result}")
        
        # Test knowledge graph summary
        summary = await memory_integration.get_knowledge_graph_summary()
        print(f"📊 Graph summary: {summary}")
        
    except Exception as e:
        print(f"❌ Memory integration test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_memory_integration())
