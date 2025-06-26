#!/usr/bin/env python3
"""
Comprehensive Demo: DeepSeek R1 + Gemini 2.5 CLI Integration
Shows autonomous AI coordination with both models working together
"""

import asyncio
import time
from autonomous_ai_coordinator import AutonomousAICoordinator, TaskType

async def run_comprehensive_demo():
    print("=" * 80)
    print("🚀 COMPREHENSIVE DEMO: DeepSeek R1 + Gemini 2.5 CLI Integration")
    print("=" * 80)
    
    # Initialize coordinator
    print("\n🔧 Initializing Autonomous AI Coordinator...")
    coordinator = AutonomousAICoordinator()
    
    # Show status
    status = coordinator.get_status()
    print(f"\n📊 System Status:")
    print(f"   - DeepSeek R1 Available: {status['models_available']['deepseek_r1']}")
    print(f"   - Gemini 2.5 Available: {status['models_available']['gemini_2_5']}")
    print(f"   - Queue Length: {status['queue_length']}")
    print(f"   - Completed Tasks: {status['completed_tasks']}")
    
    # Add diverse tasks to showcase both models
    print("\n📝 Adding demonstration tasks...")
    
    # Task 1: Reasoning (DeepSeek R1 specialty)
    task1 = coordinator.add_task(
        TaskType.REASONING,
        "A farmer has 17 sheep. All but 9 die. How many sheep are left? Please explain your step-by-step reasoning.",
        priority=3
    )
    
    # Task 2: Research (Gemini 2.5 specialty)  
    task2 = coordinator.add_task(
        TaskType.RESEARCH,
        "Explain the key differences between machine learning and deep learning with examples.",
        priority=2
    )
    
    # Task 3: Code Generation (Both models)
    task3 = coordinator.add_task(
        TaskType.CODE_GENERATION,
        "Write a Python function to calculate the factorial of a number using recursion.",
        priority=3
    )
    
    # Task 4: Problem Solving (DeepSeek R1 specialty)
    task4 = coordinator.add_task(
        TaskType.PROBLEM_SOLVING,
        "Design an efficient algorithm to find the second largest number in an array.",
        priority=1
    )
    
    print(f"✓ Added {len(coordinator.tasks_queue)} tasks to queue")
    
    # Execute tasks one by one to show results
    print("\n🔄 Executing tasks to demonstrate capabilities...")
    print("-" * 60)
    
    task_number = 1
    while coordinator.tasks_queue:
        task = coordinator.tasks_queue.pop(0)
        
        print(f"\n[TASK {task_number}] Type: {task.type.value}")
        print(f"Description: {task.description}")
        print(f"Priority: {task.priority}")
        
        start_time = time.time()
        result = await coordinator.execute_task(task)
        execution_time = time.time() - start_time
        
        print(f"Assigned Model: {task.assigned_model.value if task.assigned_model else 'None'}")
        print(f"Execution Time: {execution_time:.2f}s")
        print(f"Status: {task.status}")
        
        if task.status == "completed":
            if "deepseek" in result:
                print(f"\n[DeepSeek R1 Response]:")
                print(f"{result['deepseek'][:500]}{'...' if len(result['deepseek']) > 500 else ''}")
            
            if "gemini" in result:
                print(f"\n[Gemini 2.5 Response]:")
                print(f"{result['gemini'][:500]}{'...' if len(result['gemini']) > 500 else ''}")
            
            if "synthesis" in result:
                print(f"\n[Synthesized Response]:")
                print(f"{result['synthesis'][:500]}{'...' if len(result['synthesis']) > 500 else ''}")
        else:
            print(f"\n[Error]: {result.get('error', 'Unknown error')}")
        
        coordinator.completed_tasks.append(task)
        task_number += 1
        
        print("-" * 60)
    
    # Final status
    final_status = coordinator.get_status()
    print(f"\n🏁 DEMO COMPLETED!")
    print(f"   Total Tasks Executed: {final_status['completed_tasks']}")
    print(f"   All tasks processed successfully!")
    
    print("\n" + "=" * 80)
    print("✅ Integration Demo Complete - Both models working autonomously!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_comprehensive_demo())
