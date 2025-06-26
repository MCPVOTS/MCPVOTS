#!/usr/bin/env python3
"""
Autonomous AI Coordinator - DeepSeek R1 & Gemini 2.5 CLI Integration
Leverages both        # Check Gemini 2.5 CLI server availability
        try:
            response = requests.get(
                f"{self.gemini_config['endpoint']}/health",
                timeout=10
            )
            if response.status_code == 200:
                self.gemini_available = True
                logger.info("✅ Gemini 2.5 CLI server is available")
            else:
                logger.warning(f"⚠️ Gemini 2.5 CLI server returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"❌ Gemini 2.5 CLI server connection failed: {e}")ously for enhanced problem-solving capabilities.
"""

import asyncio
import json
import logging
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import requests
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autonomous_ai_coordinator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TaskType(Enum):
    REASONING = "reasoning"
    ANALYSIS = "analysis"
    CODE_GENERATION = "code_generation"
    PROBLEM_SOLVING = "problem_solving"
    RESEARCH = "research"
    PLANNING = "planning"

class ModelType(Enum):
    DEEPSEEK_R1 = "deepseek_r1"
    GEMINI_2_5 = "gemini_2_5"
    BOTH = "both"

@dataclass
class Task:
    id: str
    type: TaskType
    description: str
    input_data: Any
    priority: int = 1
    assigned_model: Optional[ModelType] = None
    status: str = "pending"
    result: Optional[Any] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class AutonomousAICoordinator:
    """
    Coordinates DeepSeek R1 and Gemini 2.5 CLI for autonomous AI operations
    """
    
    def __init__(self):
        self.tasks_queue: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.running = False
        self.deepseek_available = False
        self.gemini_available = False
        
        # Model-specific configurations
        self.deepseek_config = {
            "endpoint": "http://localhost:11434/api/generate",
            "model": "deepseek-r1:1.5b",
            "max_tokens": 2048,
            "temperature": 0.7
        }
        
        self.gemini_config = {
            "endpoint": "http://localhost:8017",
            "websocket_url": "ws://localhost:8017",
            "model": "gemini-2.5-pro",
            "max_tokens": 2048,
            "temperature": 0.7
        }
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize and check availability of both AI models"""
        logger.info("Initializing AI models...")
        
        # Check DeepSeek R1 availability
        try:
            response = requests.post(
                self.deepseek_config["endpoint"],
                json={
                    "model": self.deepseek_config["model"],
                    "prompt": "Hello, are you ready?",
                    "stream": False
                },
                timeout=10
            )
            if response.status_code == 200:
                self.deepseek_available = True
                logger.info("[SUCCESS] DeepSeek R1 is available")
            else:
                logger.warning("❌ DeepSeek R1 not responding")
        except Exception as e:
            logger.warning(f"❌ DeepSeek R1 connection failed: {e}")
        
        # Check Gemini 2.5 CLI server availability
        try:
            response = requests.get(f"{self.gemini_config['endpoint']}/health", timeout=10)
            if response.status_code == 200:
                self.gemini_available = True
                logger.info("[SUCCESS] Gemini 2.5 CLI server is available")
            else:
                logger.warning("[ERROR] Gemini 2.5 CLI server not responding")
        except Exception as e:
            logger.warning(f"❌ Gemini 2.5 CLI server connection failed: {e}")
    
    async def deepseek_inference(self, prompt: str, task_type: TaskType) -> str:
        """Execute inference using DeepSeek R1"""
        if not self.deepseek_available:
            raise Exception("DeepSeek R1 is not available")
        
        # Enhance prompt for DeepSeek's chain-of-thought reasoning
        enhanced_prompt = f"""
Task Type: {task_type.value}

Please use step-by-step reasoning to solve this:

{prompt}

Think through this systematically:
1. Understanding the problem
2. Breaking down the components
3. Reasoning through each step
4. Arriving at a solution

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
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                raise Exception(f"DeepSeek API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"DeepSeek inference failed: {e}")
            raise
    
    async def gemini_inference(self, prompt: str, task_type: TaskType) -> str:
        """Execute inference using Gemini 2.5 CLI server"""
        if not self.gemini_available:
            raise Exception("Gemini 2.5 CLI is not available")
        
        # Enhance prompt for Gemini's multimodal capabilities
        enhanced_prompt = f"""
Task: {task_type.value}

{prompt}

Please provide a comprehensive response leveraging your advanced reasoning and knowledge capabilities.
"""
        
        try:
            # Prepare request payload for Gemini CLI server
            payload = {
                "model": self.gemini_config["model"],
                "prompt": enhanced_prompt,
                "max_tokens": self.gemini_config["max_tokens"],
                "temperature": self.gemini_config["temperature"],
                "stream": False
            }
            
            # Send request to Gemini CLI server
            response = requests.post(
                f"{self.gemini_config['endpoint']}/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", result.get("text", ""))
            else:
                raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Gemini inference failed: {e}")
            raise
    
    def assign_optimal_model(self, task: Task) -> ModelType:
        """Intelligently assign the optimal model for each task"""
        
        # Task-model optimization mapping
        if task.type in [TaskType.REASONING, TaskType.PROBLEM_SOLVING]:
            # DeepSeek R1 excels at step-by-step reasoning
            return ModelType.DEEPSEEK_R1
        
        elif task.type in [TaskType.RESEARCH, TaskType.ANALYSIS]:
            # Gemini 2.5 excels at comprehensive analysis and research
            return ModelType.GEMINI_2_5
        
        elif task.type == TaskType.CODE_GENERATION:
            # Use both for comparison and enhanced results
            return ModelType.BOTH
        
        elif task.type == TaskType.PLANNING:
            # DeepSeek for logical planning
            return ModelType.DEEPSEEK_R1
        
        else:
            # Default to available model or both
            if self.deepseek_available and self.gemini_available:
                return ModelType.BOTH
            elif self.deepseek_available:
                return ModelType.DEEPSEEK_R1
            elif self.gemini_available:
                return ModelType.GEMINI_2_5
            else:
                raise Exception("No AI models available")
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task using the assigned model(s)"""
        logger.info(f"Executing task {task.id}: {task.description}")
        
        task.status = "executing"
        task.assigned_model = self.assign_optimal_model(task)
        
        results = {}
        
        try:
            if task.assigned_model == ModelType.DEEPSEEK_R1:
                results["deepseek"] = await self.deepseek_inference(task.description, task.type)
                
            elif task.assigned_model == ModelType.GEMINI_2_5:
                results["gemini"] = await self.gemini_inference(task.description, task.type)
                
            elif task.assigned_model == ModelType.BOTH:
                # Execute both models concurrently
                deepseek_task = self.deepseek_inference(task.description, task.type)
                gemini_task = self.gemini_inference(task.description, task.type)
                
                deepseek_result, gemini_result = await asyncio.gather(
                    deepseek_task, gemini_task, return_exceptions=True
                )
                
                if not isinstance(deepseek_result, Exception):
                    results["deepseek"] = deepseek_result
                if not isinstance(gemini_result, Exception):
                    results["gemini"] = gemini_result
                
                # Synthesize results if both succeeded
                if "deepseek" in results and "gemini" in results:
                    synthesis_prompt = f"""
                    Please synthesize these two AI responses into a comprehensive solution:
                    
                    DeepSeek R1 Response:
                    {results["deepseek"]}
                    
                    Gemini 2.5 Response:
                    {results["gemini"]}
                    
                    Provide a unified, enhanced response that combines the best of both:
                    """
                    
                    # Use Gemini for synthesis
                    results["synthesis"] = await self.gemini_inference(synthesis_prompt, task.type)
            
            task.status = "completed"
            task.result = results
            task.completed_at = datetime.now()
            
            logger.info(f"✅ Task {task.id} completed successfully")
            return results
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            logger.error(f"❌ Task {task.id} failed: {e}")
            return {"error": str(e)}
    
    def add_task(self, task_type: TaskType, description: str, input_data: Any = None, priority: int = 1) -> str:
        """Add a new task to the queue"""
        task_id = f"task_{int(time.time())}_{len(self.tasks_queue)}"
        task = Task(
            id=task_id,
            type=task_type,
            description=description,
            input_data=input_data,
            priority=priority
        )
        
        # Insert task based on priority (higher priority first)
        inserted = False
        for i, existing_task in enumerate(self.tasks_queue):
            if task.priority > existing_task.priority:
                self.tasks_queue.insert(i, task)
                inserted = True
                break
        
        if not inserted:
            self.tasks_queue.append(task)
        
        logger.info(f"📝 Added task {task_id}: {description}")
        return task_id
    
    async def autonomous_loop(self):
        """Main autonomous execution loop"""
        logger.info("🚀 Starting autonomous AI coordination loop...")
        self.running = True
        
        while self.running:
            try:
                if self.tasks_queue:
                    # Get next task
                    task = self.tasks_queue.pop(0)
                    
                    # Execute task
                    result = await self.execute_task(task)
                    
                    # Move to completed tasks
                    self.completed_tasks.append(task)
                    
                    # Log result summary
                    self._log_task_summary(task)
                    
                else:
                    # No tasks available, wait briefly
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error in autonomous loop: {e}")
                await asyncio.sleep(5)
        
        logger.info("🛑 Autonomous coordination loop stopped")
    
    def _log_task_summary(self, task: Task):
        """Log a summary of completed task"""
        duration = (task.completed_at - task.created_at).total_seconds()
        
        summary = {
            "task_id": task.id,
            "type": task.type.value,
            "status": task.status,
            "duration_seconds": duration,
            "assigned_model": task.assigned_model.value if task.assigned_model else None,
            "timestamp": task.completed_at.isoformat()
        }
        
        # Save to results file
        results_file = "autonomous_ai_results.jsonl"
        with open(results_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(summary) + '\n')
        
        logger.info(f"📊 Task summary: {summary}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current coordinator status"""
        return {
            "running": self.running,
            "models_available": {
                "deepseek_r1": self.deepseek_available,
                "gemini_2_5": self.gemini_available
            },
            "queue_length": len(self.tasks_queue),
            "completed_tasks": len(self.completed_tasks),
            "timestamp": datetime.now().isoformat()
        }
    
    def stop(self):
        """Stop the autonomous coordination"""
        self.running = False
        logger.info("🛑 Stopping autonomous coordination...")

async def main():
    """Main function to demonstrate autonomous AI coordination"""
    coordinator = AutonomousAICoordinator()
    
    # Add some example tasks
    coordinator.add_task(
        TaskType.REASONING,
        "Analyze the efficiency of different sorting algorithms and recommend the best one for large datasets",
        priority=2
    )
    
    coordinator.add_task(
        TaskType.CODE_GENERATION,
        "Create a Python function that implements a binary search tree with insertion, deletion, and search operations",
        priority=3
    )
    
    coordinator.add_task(
        TaskType.RESEARCH,
        "Research the latest trends in artificial intelligence and machine learning for 2025",
        priority=1
    )
    
    coordinator.add_task(
        TaskType.PROBLEM_SOLVING,
        "Design a solution for optimizing database queries in a high-traffic web application",
        priority=2
    )
    
    coordinator.add_task(
        TaskType.PLANNING,
        "Create a comprehensive project plan for developing a new AI-powered mobile application",
        priority=1
    )
    
    # Start autonomous execution
    try:
        await coordinator.autonomous_loop()
    except KeyboardInterrupt:
        coordinator.stop()
        logger.info("👋 Autonomous AI coordination stopped by user")

if __name__ == "__main__":
    asyncio.run(main())
