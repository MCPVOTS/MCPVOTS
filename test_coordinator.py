#!/usr/bin/env python3
"""
Test the Autonomous AI Coordinator
"""

import asyncio
from autonomous_ai_coordinator import AutonomousAICoordinator, TaskType

async def test_coordinator():
    print("🧪 Testing Autonomous AI Coordinator...")
    
    # Initialize coordinator
    coordinator = AutonomousAICoordinator()
    
    # Check status
    status = coordinator.get_status()
    print(f"📊 Coordinator Status: {status}")
    
    # Add a simple test task
    task_id = coordinator.add_task(
        TaskType.REASONING,
        "What is 2 + 2? Please explain your reasoning.",
        priority=1
    )
    
    print(f"📝 Added test task: {task_id}")
    
    # Execute one task manually to test
    if coordinator.tasks_queue:
        task = coordinator.tasks_queue[0]
        print(f"🔄 Executing task: {task.description}")
        
        result = await coordinator.execute_task(task)
        print(f"✅ Task result: {result}")
    
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_coordinator())
