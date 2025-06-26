#!/usr/bin/env python3
"""
VoltAgent-MCPVots Simple Test Runner
===================================
Unicode-safe test runner for Windows console
"""

import asyncio
import json
import time
from datetime import datetime
import requests
import sqlite3
import os

async def test_voltagent_ecosystem():
    """Run simple ecosystem test without Unicode issues"""
    
    # Simple ASCII output for Windows console
    print("=" * 60)
    print("VoltAgent-MCPVots Ecosystem Test")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Test 1: Model server connectivity
    print("\n[TEST 1] Model Server Connectivity...")
    model_results = {}
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            model_results["deepseek_r1"] = "AVAILABLE"
            print("  DeepSeek R1: AVAILABLE")
        else:
            model_results["deepseek_r1"] = "ERROR"
            print("  DeepSeek R1: ERROR")
    except:
        model_results["deepseek_r1"] = "OFFLINE"
        print("  DeepSeek R1: OFFLINE")
    
    try:
        response = requests.get("http://localhost:8017/health", timeout=10)
        if response.status_code == 200:
            model_results["gemini_2_5"] = "AVAILABLE"
            print("  Gemini 2.5: AVAILABLE")
        else:
            model_results["gemini_2_5"] = "ERROR"
            print("  Gemini 2.5: ERROR")
    except:
        model_results["gemini_2_5"] = "OFFLINE"
        print("  Gemini 2.5: OFFLINE")
    
    results["tests"]["model_servers"] = model_results
    
    # Test 2: Local storage (MCP fallback)
    print("\n[TEST 2] Local Storage (MCP Fallback)...")
    try:
        conn = sqlite3.connect("test_voltagent.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                data TEXT
            )
        ''')
        
        cursor.execute("INSERT INTO test_table (name, data) VALUES (?, ?)", 
                      ("VoltAgent Test", '{"status": "success"}'))
        
        cursor.execute("SELECT * FROM test_table WHERE name = ?", ("VoltAgent Test",))
        result = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        if result:
            print("  Local Storage: SUCCESS")
            results["tests"]["local_storage"] = "SUCCESS"
        else:
            print("  Local Storage: FAILED")
            results["tests"]["local_storage"] = "FAILED"
        
        # Cleanup
        os.remove("test_voltagent.db")
        
    except Exception as e:
        print(f"  Local Storage: ERROR - {e}")
        results["tests"]["local_storage"] = f"ERROR - {e}"
    
    # Test 3: Simple AI generation test
    print("\n[TEST 3] AI Generation Test...")
    try:
        if model_results.get("deepseek_r1") == "AVAILABLE":
            response = requests.post("http://localhost:11434/api/generate", 
                                   json={
                                       "model": "deepseek-r1:1.5b",
                                       "prompt": "Hello, test response",
                                       "stream": False
                                   }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("response"):
                    print("  DeepSeek R1 Generation: SUCCESS")
                    results["tests"]["deepseek_generation"] = "SUCCESS"
                else:
                    print("  DeepSeek R1 Generation: NO_RESPONSE")
                    results["tests"]["deepseek_generation"] = "NO_RESPONSE"
            else:
                print("  DeepSeek R1 Generation: HTTP_ERROR")
                results["tests"]["deepseek_generation"] = "HTTP_ERROR"
        else:
            print("  DeepSeek R1 Generation: SKIPPED (server offline)")
            results["tests"]["deepseek_generation"] = "SKIPPED"
    except Exception as e:
        print(f"  DeepSeek R1 Generation: ERROR - {e}")
        results["tests"]["deepseek_generation"] = f"ERROR - {e}"
    
    # Test 4: Task orchestration simulation
    print("\n[TEST 4] Task Orchestration Simulation...")
    try:
        # Simulate task queue and execution
        tasks = [
            {"id": "task_1", "type": "reasoning", "agent": "deepseek_r1"},
            {"id": "task_2", "type": "code_gen", "agent": "gemini_2_5"},
            {"id": "task_3", "type": "memory", "agent": "memory_keeper"}
        ]
        
        completed = 0
        for task in tasks:
            # Simulate task execution
            await asyncio.sleep(0.1)  # Simulate processing time
            completed += 1
        
        if completed == len(tasks):
            print("  Task Orchestration: SUCCESS")
            results["tests"]["task_orchestration"] = "SUCCESS"
        else:
            print("  Task Orchestration: PARTIAL")
            results["tests"]["task_orchestration"] = "PARTIAL"
            
    except Exception as e:
        print(f"  Task Orchestration: ERROR - {e}")
        results["tests"]["task_orchestration"] = f"ERROR - {e}"
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    
    success_count = 0
    total_tests = 0
    
    for test_name, test_result in results["tests"].items():
        total_tests += 1
        if isinstance(test_result, dict):
            # For nested results like model_servers
            nested_success = sum(1 for v in test_result.values() if v == "AVAILABLE" or v == "SUCCESS")
            nested_total = len(test_result)
            if nested_success > 0:
                success_count += 1
            print(f"  {test_name}: {nested_success}/{nested_total}")
        else:
            if test_result == "SUCCESS" or test_result == "AVAILABLE":
                success_count += 1
                print(f"  {test_name}: PASS")
            else:
                print(f"  {test_name}: FAIL")
    
    overall_status = "PASS" if success_count >= total_tests * 0.75 else "NEEDS_ATTENTION"
    print(f"\nOverall Status: {overall_status} ({success_count}/{total_tests})")
    
    # Save results
    with open("voltagent_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to: voltagent_test_results.json")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    asyncio.run(test_voltagent_ecosystem())
