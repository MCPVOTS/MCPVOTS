#!/usr/bin/env python3
"""
VoltAgent Integration for MCPVots
Combines DeepSeek R1 + Gemini 2.5 CLI with VoltAgent orchestration
"""

import asyncio
import json
import logging
import subprocess
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voltagent_integration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentType(Enum):
    DEEPSEEK_REASONING = "deepseek_reasoning"
    GEMINI_RESEARCH = "gemini_research"
    SUPERVISOR = "supervisor"
    SYNTHESIS = "synthesis"

class TaskType(Enum):
    REASONING = "reasoning"
    ANALYSIS = "analysis"
    CODE_GENERATION = "code_generation"
    PROBLEM_SOLVING = "problem_solving"
    RESEARCH = "research"
    PLANNING = "planning"
    SYNTHESIS = "synthesis"

@dataclass
class AgentTask:
    id: str
    type: TaskType
    description: str
    agent_type: AgentType
    input_data: Any = None
    priority: int = 1
    status: str = "pending"
    result: Optional[Any] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    parent_task_id: Optional[str] = None
    subtasks: List[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.subtasks is None:
            self.subtasks = []

class VoltAgentMCPIntegration:
    """
    VoltAgent-style integration for MCPVots ecosystem
    Orchestrates DeepSeek R1 and Gemini 2.5 as specialized agents
    """
    
    def __init__(self):
        self.agents = {}
        self.tasks_queue: List[AgentTask] = []
        self.completed_tasks: List[AgentTask] = []
        self.running = False
        
        # Model configurations
        self.deepseek_config = {
            "endpoint": "http://localhost:11434/api/generate",
            "model": "deepseek-r1:1.5b",
            "max_tokens": 2048,
            "temperature": 0.7
        }
        
        self.gemini_config = {
            "endpoint": "http://localhost:8017",
            "model": "gemini-2.5-pro",
            "max_tokens": 2048,
            "temperature": 0.7
        }
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize specialized AI agents"""
        logger.info("Initializing VoltAgent-style AI agents...")
        
        # DeepSeek Reasoning Agent
        self.agents[AgentType.DEEPSEEK_REASONING] = {
            "name": "DeepSeek Reasoning Agent",
            "description": "Specialized in step-by-step logical reasoning and problem solving",
            "capabilities": ["reasoning", "problem_solving", "step_by_step_analysis"],
            "available": self._check_deepseek_availability(),
            "config": self.deepseek_config
        }
        
        # Gemini Research Agent
        self.agents[AgentType.GEMINI_RESEARCH] = {
            "name": "Gemini Research Agent", 
            "description": "Specialized in comprehensive research and analysis",
            "capabilities": ["research", "analysis", "comprehensive_responses"],
            "available": self._check_gemini_availability(),
            "config": self.gemini_config
        }
        
        # Supervisor Agent (coordinates other agents)
        self.agents[AgentType.SUPERVISOR] = {
            "name": "Supervisor Agent",
            "description": "Coordinates tasks between specialized agents",
            "capabilities": ["task_routing", "coordination", "delegation"],
            "available": True,
            "config": None
        }
        
        # Synthesis Agent (combines responses)
        self.agents[AgentType.SYNTHESIS] = {
            "name": "Synthesis Agent",
            "description": "Combines and synthesizes responses from multiple agents",
            "capabilities": ["synthesis", "combination", "enhancement"],
            "available": True,
            "config": None
        }
        
        # Log agent status
        for agent_type, agent in self.agents.items():
            status = "AVAILABLE" if agent["available"] else "UNAVAILABLE"
            logger.info(f"[{status}] {agent['name']}: {agent['description']}")
    
    def _check_deepseek_availability(self) -> bool:
        """Check if DeepSeek R1 is available"""
        try:
            response = requests.post(
                self.deepseek_config["endpoint"],
                json={
                    "model": self.deepseek_config["model"],
                    "prompt": "Health check",
                    "stream": False
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"DeepSeek availability check failed: {e}")
            return False
    
    def _check_gemini_availability(self) -> bool:
        """Check if Gemini CLI server is available"""
        try:
            response = requests.get(f"{self.gemini_config['endpoint']}/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Gemini availability check failed: {e}")
            return False
    
    async def execute_deepseek_task(self, task: AgentTask) -> str:
        """Execute task using DeepSeek Reasoning Agent"""
        if not self.agents[AgentType.DEEPSEEK_REASONING]["available"]:
            raise Exception("DeepSeek Reasoning Agent is not available")
        
        enhanced_prompt = f"""
[VoltAgent Task Execution]
Agent: DeepSeek Reasoning Agent
Task Type: {task.type.value}
Task ID: {task.id}

Please provide step-by-step reasoning for:

{task.description}

Use your specialized reasoning capabilities to:
1. Understand the problem thoroughly
2. Break down into logical components  
3. Apply systematic reasoning
4. Provide a clear solution

Response:
"""
        
        try:
            response = requests.post(
                self.deepseek_config["endpoint"],
                json={
                    "model": self.deepseek_config["model"],
                    "prompt": enhanced_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.deepseek_config["temperature"],
                        "num_predict": self.deepseek_config["max_tokens"]
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                raise Exception(f"DeepSeek API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"DeepSeek task execution failed: {e}")
            raise
    
    async def execute_gemini_task(self, task: AgentTask) -> str:
        """Execute task using Gemini Research Agent"""
        if not self.agents[AgentType.GEMINI_RESEARCH]["available"]:
            raise Exception("Gemini Research Agent is not available")
        
        enhanced_prompt = f"""
[VoltAgent Task Execution]
Agent: Gemini Research Agent
Task Type: {task.type.value}
Task ID: {task.id}

Please provide comprehensive analysis for:

{task.description}

Use your specialized research capabilities to provide detailed, well-structured information.

Response:
"""
        
        try:
            payload = {
                "model": self.gemini_config["model"],
                "prompt": enhanced_prompt,
                "max_tokens": self.gemini_config["max_tokens"],
                "temperature": self.gemini_config["temperature"],
                "stream": False
            }
            
            response = requests.post(
                f"{self.gemini_config['endpoint']}/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                raise Exception(f"Gemini API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Gemini task execution failed: {e}")
            raise
    
    def route_task(self, description: str, task_type: TaskType) -> AgentType:
        """Route task to appropriate agent (VoltAgent-style task routing)"""
        
        # Task routing logic based on agent specializations
        if task_type in [TaskType.REASONING, TaskType.PROBLEM_SOLVING]:
            return AgentType.DEEPSEEK_REASONING
        
        elif task_type in [TaskType.RESEARCH, TaskType.ANALYSIS]:
            return AgentType.GEMINI_RESEARCH
        
        elif task_type == TaskType.CODE_GENERATION:
            # For code generation, we'll use both agents and synthesize
            return AgentType.SUPERVISOR  # Supervisor will delegate to both
        
        elif task_type == TaskType.PLANNING:
            return AgentType.DEEPSEEK_REASONING
        
        else:
            # Default routing
            available_agents = [
                agent_type for agent_type, agent in self.agents.items()
                if agent["available"] and agent_type in [AgentType.DEEPSEEK_REASONING, AgentType.GEMINI_RESEARCH]
            ]
            
            if available_agents:
                return available_agents[0]
            else:
                raise Exception("No suitable agents available")
    
    async def execute_supervisor_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute complex task using supervisor agent (delegates to subagents)"""
        logger.info(f"Supervisor executing complex task: {task.id}")
        
        results = {}
        
        # Create subtasks for both agents
        deepseek_subtask = AgentTask(
            id=f"{task.id}_deepseek",
            type=task.type,
            description=task.description,
            agent_type=AgentType.DEEPSEEK_REASONING,
            parent_task_id=task.id
        )
        
        gemini_subtask = AgentTask(
            id=f"{task.id}_gemini", 
            type=task.type,
            description=task.description,
            agent_type=AgentType.GEMINI_RESEARCH,
            parent_task_id=task.id
        )
        
        # Execute both subtasks concurrently
        try:
            deepseek_result, gemini_result = await asyncio.gather(
                self.execute_deepseek_task(deepseek_subtask),
                self.execute_gemini_task(gemini_subtask),
                return_exceptions=True
            )
            
            if not isinstance(deepseek_result, Exception):
                results["deepseek"] = deepseek_result
            
            if not isinstance(gemini_result, Exception):
                results["gemini"] = gemini_result
            
            # Synthesize results
            if "deepseek" in results and "gemini" in results:
                synthesis_task = AgentTask(
                    id=f"{task.id}_synthesis",
                    type=TaskType.SYNTHESIS,
                    description=f"Synthesize responses for: {task.description}",
                    agent_type=AgentType.SYNTHESIS,
                    input_data=results,
                    parent_task_id=task.id
                )
                
                synthesis_result = await self.execute_synthesis_task(synthesis_task)
                results["synthesis"] = synthesis_result
            
            return results
            
        except Exception as e:
            logger.error(f"Supervisor task execution failed: {e}")
            return {"error": str(e)}
    
    async def execute_synthesis_task(self, task: AgentTask) -> str:
        """Execute synthesis using the best available agent"""
        if "deepseek" in task.input_data and "gemini" in task.input_data:
            synthesis_prompt = f"""
            [VoltAgent Synthesis Task]
            Task: Combine and enhance the following responses
            
            DeepSeek Reasoning Agent Response:
            {task.input_data["deepseek"]}
            
            Gemini Research Agent Response:
            {task.input_data["gemini"]}
            
            Please provide a unified, enhanced response that combines the best insights from both agents:
            """
            
            # Use Gemini for synthesis (it's better at comprehensive responses)
            if self.agents[AgentType.GEMINI_RESEARCH]["available"]:
                synthesis_task = AgentTask(
                    id=f"synthesis_{int(time.time())}",
                    type=TaskType.RESEARCH,
                    description=synthesis_prompt,
                    agent_type=AgentType.GEMINI_RESEARCH
                )
                return await self.execute_gemini_task(synthesis_task)
            else:
                # Fallback to simple combination
                return f"Combined Response:\n\nDeepSeek Analysis:\n{task.input_data['deepseek']}\n\nGemini Analysis:\n{task.input_data['gemini']}"
        else:
            return "Insufficient data for synthesis"
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a task using the appropriate agent"""
        logger.info(f"Executing VoltAgent task {task.id}: {task.type.value}")
        
        task.status = "executing"
        start_time = time.time()
        
        try:
            if task.agent_type == AgentType.DEEPSEEK_REASONING:
                result = await self.execute_deepseek_task(task)
                return {"agent": "deepseek", "response": result}
            
            elif task.agent_type == AgentType.GEMINI_RESEARCH:
                result = await self.execute_gemini_task(task)
                return {"agent": "gemini", "response": result}
            
            elif task.agent_type == AgentType.SUPERVISOR:
                return await self.execute_supervisor_task(task)
            
            elif task.agent_type == AgentType.SYNTHESIS:
                result = await self.execute_synthesis_task(task)
                return {"agent": "synthesis", "response": result}
            
            else:
                raise Exception(f"Unknown agent type: {task.agent_type}")
                
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            logger.error(f"Task {task.id} failed: {e}")
            return {"error": str(e)}
        
        finally:
            task.completed_at = datetime.now()
            execution_time = time.time() - start_time
            logger.info(f"Task {task.id} completed in {execution_time:.2f}s")
    
    def add_task(self, task_type: TaskType, description: str, priority: int = 1) -> str:
        """Add a new task (VoltAgent-style task creation)"""
        task_id = f"voltagent_task_{int(time.time())}_{len(self.tasks_queue)}"
        
        # Route task to appropriate agent
        agent_type = self.route_task(description, task_type)
        
        task = AgentTask(
            id=task_id,
            type=task_type,
            description=description,
            agent_type=agent_type,
            priority=priority
        )
        
        # Insert based on priority
        inserted = False
        for i, existing_task in enumerate(self.tasks_queue):
            if task.priority > existing_task.priority:
                self.tasks_queue.insert(i, task)
                inserted = True
                break
        
        if not inserted:
            self.tasks_queue.append(task)
        
        logger.info(f"Added VoltAgent task {task_id} -> {agent_type.value}: {description}")
        return task_id
    
    def get_status(self) -> Dict[str, Any]:
        """Get VoltAgent integration status"""
        return {
            "framework": "VoltAgent Integration",
            "running": self.running,
            "agents": {
                agent_type.value: {
                    "name": agent["name"],
                    "available": agent["available"],
                    "capabilities": agent["capabilities"]
                }
                for agent_type, agent in self.agents.items()
            },
            "queue_length": len(self.tasks_queue),
            "completed_tasks": len(self.completed_tasks),
            "timestamp": datetime.now().isoformat()
        }
    
    async def run_demo(self):
        """Run a comprehensive VoltAgent integration demo"""
        print("=" * 80)
        print("🚀 VoltAgent Integration Demo - MCPVots Ecosystem")
        print("=" * 80)
        
        # Show status
        status = self.get_status()
        print(f"\n📊 VoltAgent Status:")
        for agent_name, agent_info in status["agents"].items():
            availability = "✅ AVAILABLE" if agent_info["available"] else "❌ UNAVAILABLE"
            print(f"   {availability} {agent_info['name']}")
            print(f"      Capabilities: {', '.join(agent_info['capabilities'])}")
        
        # Add demonstration tasks
        print(f"\n📝 Adding VoltAgent tasks...")
        
        task_ids = [
            self.add_task(TaskType.REASONING, "Solve: If a train leaves station A at 60mph and another leaves station B at 80mph, when do they meet?", priority=3),
            self.add_task(TaskType.RESEARCH, "Explain the evolution of AI agents and their applications in 2025", priority=2),
            self.add_task(TaskType.CODE_GENERATION, "Create a Python class for a binary search tree with proper documentation", priority=3),
            self.add_task(TaskType.PROBLEM_SOLVING, "Design an algorithm to efficiently detect cycles in a linked list", priority=1)
        ]
        
        print(f"✓ Added {len(task_ids)} tasks to VoltAgent queue")
        
        # Execute tasks
        print(f"\n🔄 Executing VoltAgent tasks...")
        print("-" * 60)
        
        task_number = 1
        while self.tasks_queue:
            task = self.tasks_queue.pop(0)
            
            print(f"\n[VOLTAGENT TASK {task_number}]")
            print(f"ID: {task.id}")
            print(f"Type: {task.type.value}")
            print(f"Agent: {task.agent_type.value}")
            print(f"Description: {task.description}")
            
            result = await self.execute_task(task)
            task.result = result
            self.completed_tasks.append(task)
            
            if "error" not in result:
                print(f"Status: ✅ SUCCESS")
                if "agent" in result:
                    print(f"Executed by: {result['agent']}")
                    response = result.get('response', '')
                    print(f"Response: {response[:300]}{'...' if len(response) > 300 else ''}")
                elif "synthesis" in result:
                    print(f"Multi-agent execution with synthesis:")
                    for key, value in result.items():
                        if key != "synthesis":
                            print(f"  {key}: {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
                    print(f"  synthesis: {result['synthesis'][:200]}{'...' if len(result['synthesis']) > 200 else ''}")
            else:
                print(f"Status: ❌ FAILED - {result['error']}")
            
            task_number += 1
            print("-" * 60)
        
        # Final status
        print(f"\n🏁 VoltAgent Demo Complete!")
        print(f"   Framework: VoltAgent Integration for MCPVots")
        print(f"   Tasks Executed: {len(self.completed_tasks)}")
        print(f"   Available Agents: {sum(1 for agent in self.agents.values() if agent['available'])}")
        print("=" * 80)

async def main():
    """Main demo function"""
    integration = VoltAgentMCPIntegration()
    await integration.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
