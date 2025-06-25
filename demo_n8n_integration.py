#!/usr/bin/env python3
"""
n8n AGI Integration Demo
========================
Interactive demonstration of n8n workflow automation with MCPVots AGI ecosystem.
Shows key capabilities and workflows in action.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import websockets
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class N8NDemo:
    def __init__(self):
        self.n8n_integration_url = "ws://localhost:8020"
        self.demo_workflows = []
        
    async def run_interactive_demo(self):
        """Run interactive n8n AGI demo"""
        logger.info("🎭 Starting n8n AGI Integration Demo...")
        
        print(f"\n{'='*60}")
        print(f"🎭 n8n + AGI ECOSYSTEM DEMO")
        print(f"{'='*60}")
        print(f"This demo showcases n8n workflow automation")
        print(f"integrated with the MCPVots AGI ecosystem.")
        print(f"{'='*60}\n")
        
        demo_steps = [
            ("1. Connection Test", self.demo_connection),
            ("2. AGI Nodes Overview", self.demo_agi_nodes),
            ("3. Create Simple Workflow", self.demo_create_workflow),
            ("4. Execute AGI Workflow", self.demo_execute_workflow),
            ("5. Multi-Service Workflow", self.demo_multi_service_workflow),
            ("6. Webhook Integration", self.demo_webhook_integration),
            ("7. Memory Integration", self.demo_memory_integration),
            ("8. Continuous Learning", self.demo_learning_workflow)
        ]
        
        for step_name, step_func in demo_steps:
            try:
                print(f"\n🎬 {step_name}")
                print("-" * 50)
                
                await step_func()
                
                input("Press Enter to continue to next demo step...")
                
            except Exception as e:
                logger.error(f"❌ Demo step failed: {e}")
                
        print(f"\n🎉 Demo completed! Explore more at http://localhost:5678")
        
    async def demo_connection(self):
        """Demo 1: Test connection to n8n integration"""
        print("🔌 Testing connection to n8n integration server...")
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                health_request = {
                    "method": "n8n/health",
                    "params": {}
                }
                
                await websocket.send(json.dumps(health_request))
                response = await websocket.recv()
                health_data = json.loads(response)
                
                print(f"✅ Connection successful!")
                print(f"   Server: {health_data.get('server')}")
                print(f"   Port: {health_data.get('port')}")
                print(f"   Workflows: {health_data.get('workflows', 0)}")
                print(f"   AGI Services: {len(health_data.get('agi_services', []))}")
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("   Make sure the n8n integration server is running!")
            
    async def demo_agi_nodes(self):
        """Demo 2: Show available AGI nodes"""
        print("🧩 Discovering available AGI nodes...")
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                nodes_request = {
                    "method": "n8n/get_agi_nodes",
                    "params": {}
                }
                
                await websocket.send(json.dumps(nodes_request))
                response = await websocket.recv()
                nodes_data = json.loads(response)
                
                agi_nodes = nodes_data.get("agi_nodes", [])
                
                print(f"✅ Found {len(agi_nodes)} AGI nodes:")
                
                for node in agi_nodes:
                    print(f"   🔹 {node['name']} ({node['type']})")
                    print(f"      {node['description']}")
                    print(f"      Parameters: {', '.join(node.get('parameters', []))}")
                    print()
                    
        except Exception as e:
            print(f"❌ Failed to get AGI nodes: {e}")
            
    async def demo_create_workflow(self):
        """Demo 3: Create a simple AGI workflow"""
        print("📋 Creating a simple AGI-powered workflow...")
        
        workflow_config = {
            "name": "Demo: AI Code Analyzer",
            "trigger_type": "manual",
            "nodes": [
                {
                    "type": "agi_gemini",
                    "name": "Analyze Code Quality",
                    "parameters": {
                        "endpoint": "/analyze",
                        "prompt": "Analyze this code for quality and suggest improvements: print('Hello, World!')",
                        "model": "gemini-pro"
                    }
                },
                {
                    "type": "agi_memory",
                    "name": "Store Analysis",
                    "parameters": {
                        "action": "store",
                        "content_type": "code_analysis"
                    }
                }
            ]
        }
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                create_request = {
                    "method": "n8n/create_workflow",
                    "params": workflow_config
                }
                
                await websocket.send(json.dumps(create_request))
                response = await websocket.recv()
                workflow_data = json.loads(response)
                
                if "workflow_id" in workflow_data:
                    print(f"✅ Workflow created successfully!")
                    print(f"   ID: {workflow_data['workflow_id']}")
                    print(f"   Name: {workflow_data['name']}")
                    print(f"   Nodes: {workflow_data.get('nodes', 0)}")
                    
                    # Store for later use
                    self.demo_workflows.append(workflow_data)
                else:
                    print(f"❌ Failed to create workflow: {workflow_data.get('error')}")
                    
        except Exception as e:
            print(f"❌ Workflow creation failed: {e}")
            
    async def demo_execute_workflow(self):
        """Demo 4: Execute the created workflow"""
        print("▶️ Executing the AGI workflow...")
        
        if not self.demo_workflows:
            print("⚠️ No workflows available. Skipping execution demo.")
            return
            
        workflow = self.demo_workflows[0]
        workflow_id = workflow["workflow_id"]
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                execute_request = {
                    "method": "n8n/execute_workflow",
                    "params": {
                        "workflow_id": workflow_id,
                        "input_data": {
                            "demo_execution": True,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                }
                
                await websocket.send(json.dumps(execute_request))
                response = await websocket.recv()
                execution_data = json.loads(response)
                
                if execution_data.get("status") == "completed":
                    print(f"✅ Workflow executed successfully!")
                    print(f"   Execution ID: {execution_data['execution_id']}")
                    print(f"   Nodes executed: {execution_data.get('nodes_executed', 0)}")
                    print(f"   Results: {len(execution_data.get('results', []))} steps completed")
                    
                    # Show sample results
                    if execution_data.get("results"):
                        print(f"\n📊 Sample results:")
                        for i, result in enumerate(execution_data["results"][:2]):
                            print(f"   Step {i+1}: {result.get('node', 'Unknown')} - {result.get('status', 'Unknown')}")
                else:
                    print(f"❌ Workflow execution failed: {execution_data.get('error')}")
                    
        except Exception as e:
            print(f"❌ Workflow execution failed: {e}")
            
    async def demo_multi_service_workflow(self):
        """Demo 5: Create and execute multi-service workflow"""
        print("🔄 Creating multi-service AGI workflow...")
        
        multi_workflow = {
            "name": "Demo: Multi-AGI Processing Pipeline",
            "trigger_type": "manual",
            "nodes": [
                {
                    "type": "agi_gemini",
                    "name": "Initial Analysis",
                    "parameters": {
                        "endpoint": "/chat",
                        "prompt": "What are the best practices for Python code organization?"
                    }
                },
                {
                    "type": "agi_ollama",
                    "name": "Local Processing",
                    "parameters": {
                        "model": "llama2",
                        "prompt": "Summarize the key points from the analysis"
                    }
                },
                {
                    "type": "agi_memory",
                    "name": "Store Knowledge",
                    "parameters": {
                        "action": "store",
                        "content_type": "best_practices"
                    }
                },
                {
                    "type": "agi_deerflow",
                    "name": "Optimize Process",
                    "parameters": {
                        "action": "optimize",
                        "optimization_target": "quality"
                    }
                }
            ]
        }
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                # Create workflow
                create_request = {
                    "method": "n8n/create_workflow",
                    "params": multi_workflow
                }
                
                await websocket.send(json.dumps(create_request))
                create_response = await websocket.recv()
                create_data = json.loads(create_response)
                
                if "workflow_id" in create_data:
                    print(f"✅ Multi-service workflow created!")
                    print(f"   Services: Gemini → Ollama → Memory → DeerFlow")
                    
                    # Execute workflow
                    execute_request = {
                        "method": "n8n/execute_workflow",
                        "params": {
                            "workflow_id": create_data["workflow_id"],
                            "input_data": {"multi_service_demo": True}
                        }
                    }
                    
                    print("   Executing workflow...")
                    await websocket.send(json.dumps(execute_request))
                    execute_response = await websocket.recv()
                    execute_data = json.loads(execute_response)
                    
                    if execute_data.get("status") == "completed":
                        print(f"✅ Multi-service execution completed!")
                        print(f"   All {execute_data.get('nodes_executed', 0)} AGI services processed successfully")
                    else:
                        print(f"⚠️ Execution status: {execute_data.get('status')}")
                        
                else:
                    print(f"❌ Failed to create multi-service workflow")
                    
        except Exception as e:
            print(f"❌ Multi-service workflow demo failed: {e}")
            
    async def demo_webhook_integration(self):
        """Demo 6: Show webhook integration"""
        print("🔗 Demonstrating webhook integration...")
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                # Create webhook
                webhook_request = {
                    "method": "n8n/create_webhook",
                    "params": {
                        "webhook_id": "demo_webhook",
                        "workflow_id": None
                    }
                }
                
                await websocket.send(json.dumps(webhook_request))
                response = await websocket.recv()
                webhook_data = json.loads(response)
                
                if "webhook_url" in webhook_data:
                    print(f"✅ Webhook created successfully!")
                    print(f"   Webhook URL: {webhook_data['webhook_url']}")
                    print(f"   ID: {webhook_data['webhook_id']}")
                    print(f"   Usage: POST to this URL to trigger AGI workflows")
                    
                    # Test webhook trigger
                    trigger_request = {
                        "method": "n8n/trigger_webhook",
                        "params": {
                            "webhook_id": "demo_webhook",
                            "payload": {
                                "message": "Demo webhook trigger",
                                "timestamp": datetime.now().isoformat()
                            }
                        }
                    }
                    
                    await websocket.send(json.dumps(trigger_request))
                    trigger_response = await websocket.recv()
                    trigger_data = json.loads(trigger_response)
                    
                    if trigger_data.get("triggered"):
                        print(f"✅ Webhook triggered successfully!")
                    
                else:
                    print(f"❌ Failed to create webhook")
                    
        except Exception as e:
            print(f"❌ Webhook demo failed: {e}")
            
    async def demo_memory_integration(self):
        """Demo 7: Show memory integration capabilities"""
        print("🧠 Demonstrating AGI memory integration...")
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                # Execute memory node directly
                memory_request = {
                    "method": "n8n/execute_agi_node",
                    "params": {
                        "node_type": "agi_memory",
                        "parameters": {
                            "action": "store",
                            "content_type": "demo_data"
                        },
                        "input_data": {
                            "demo_insight": "n8n integration enables powerful AGI workflow automation",
                            "capabilities": ["visual_workflows", "agi_nodes", "automation"],
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                }
                
                await websocket.send(json.dumps(memory_request))
                response = await websocket.recv()
                memory_data = json.loads(response)
                
                execution_result = memory_data.get("execution_result", {})
                
                if execution_result.get("status") == "completed":
                    print(f"✅ Memory integration working!")
                    print(f"   Service: {execution_result.get('service')}")
                    print(f"   Action: {execution_result.get('action')}")
                    print(f"   Data stored in knowledge graph for future retrieval")
                    
                    # Test retrieval
                    retrieve_request = {
                        "method": "n8n/execute_agi_node",
                        "params": {
                            "node_type": "agi_memory",
                            "parameters": {
                                "action": "retrieve",
                                "query": "n8n integration"
                            },
                            "input_data": {}
                        }
                    }
                    
                    await websocket.send(json.dumps(retrieve_request))
                    retrieve_response = await websocket.recv()
                    retrieve_data = json.loads(retrieve_response)
                    
                    if retrieve_data.get("execution_result", {}).get("status") == "completed":
                        print(f"✅ Memory retrieval successful!")
                        print(f"   Previous insights and data can be accessed by AGI workflows")
                        
                else:
                    print(f"⚠️ Memory operation status: {execution_result.get('status')}")
                    
        except Exception as e:
            print(f"❌ Memory integration demo failed: {e}")
            
    async def demo_learning_workflow(self):
        """Demo 8: Show continuous learning workflow"""
        print("📚 Demonstrating continuous learning workflow...")
        
        learning_workflow = {
            "name": "Demo: AGI Continuous Learning",
            "trigger_type": "manual",
            "nodes": [
                {
                    "type": "agi_memory",
                    "name": "Retrieve Insights",
                    "parameters": {
                        "action": "retrieve",
                        "query": "workflow_patterns"
                    }
                },
                {
                    "type": "agi_trilogy",
                    "name": "Advanced Reasoning",
                    "parameters": {
                        "task_type": "reasoning",
                        "complexity": "medium",
                        "input_data": {"context": "workflow_optimization"}
                    }
                },
                {
                    "type": "agi_dgm",
                    "name": "Self-Improvement",
                    "parameters": {
                        "evolution_type": "workflow_learning",
                        "improvement_goal": "automation_efficiency"
                    }
                }
            ]
        }
        
        try:
            async with websockets.connect(self.n8n_integration_url) as websocket:
                # Create learning workflow
                create_request = {
                    "method": "n8n/create_workflow",
                    "params": learning_workflow
                }
                
                await websocket.send(json.dumps(create_request))
                create_response = await websocket.recv()
                create_data = json.loads(create_response)
                
                if "workflow_id" in create_data:
                    print(f"✅ Learning workflow created!")
                    print(f"   Components: Memory → Trilogy → DGM")
                    print(f"   Purpose: Continuous improvement of AGI capabilities")
                    
                    # Execute learning workflow
                    execute_request = {
                        "method": "n8n/execute_workflow",
                        "params": {
                            "workflow_id": create_data["workflow_id"],
                            "input_data": {
                                "learning_cycle": True,
                                "focus": "n8n_workflow_optimization"
                            }
                        }
                    }
                    
                    print("   Running learning cycle...")
                    await websocket.send(json.dumps(execute_request))
                    execute_response = await websocket.recv()
                    execute_data = json.loads(execute_response)
                    
                    if execute_data.get("status") == "completed":
                        print(f"✅ Learning cycle completed!")
                        print(f"   AGI system has processed new insights")
                        print(f"   Future workflows will benefit from this learning")
                    else:
                        print(f"⚠️ Learning cycle status: {execute_data.get('status')}")
                        
                else:
                    print(f"❌ Failed to create learning workflow")
                    
        except Exception as e:
            print(f"❌ Learning workflow demo failed: {e}")
            
    async def show_demo_summary(self):
        """Show demo summary and next steps"""
        print(f"\n{'='*60}")
        print(f"🎉 n8n AGI INTEGRATION DEMO COMPLETE")
        print(f"{'='*60}")
        print(f"You've seen how n8n integrates with the MCPVots AGI ecosystem:")
        print(f"")
        print(f"✅ Custom AGI nodes for visual workflow creation")
        print(f"✅ Multi-service AGI processing pipelines")
        print(f"✅ Webhook-triggered automation")
        print(f"✅ Memory and knowledge graph integration")
        print(f"✅ Continuous learning and self-improvement")
        print(f"")
        print(f"🚀 NEXT STEPS:")
        print(f"   1. Open n8n dashboard: http://localhost:5678")
        print(f"   2. Explore workflow templates")
        print(f"   3. Create custom AGI workflows")
        print(f"   4. Set up automated triggers")
        print(f"   5. Monitor workflow performance")
        print(f"")
        print(f"📚 DOCUMENTATION:")
        print(f"   • N8N_INTEGRATION.md - Complete integration guide")
        print(f"   • README_ENHANCED.md - System overview")
        print(f"   • COMPREHENSIVE_ARCHITECTURE.md - Technical details")
        print(f"{'='*60}\n")


async def main():
    """Run the n8n AGI integration demo"""
    demo = N8NDemo()
    
    try:
        await demo.run_interactive_demo()
        await demo.show_demo_summary()
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 Demo interrupted by user. Thanks for exploring!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        print(f"\n⚠️ Demo encountered an issue. Please check:")
        print(f"   • n8n integration server is running (port 8020)")
        print(f"   • AGI services are started")
        print(f"   • Network connectivity is available")


if __name__ == "__main__":
    asyncio.run(main())
