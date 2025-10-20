#!/usr/bin/env python3
"""
Query MAXX Bot Memory for Context
"""

import asyncio
import json
from maxx_memory_mcp_server import get_memory_store

async def query_memory():
    store = get_memory_store()

    # Get all memories
    memories = store.get_all_memories()

    print('=== MAXX Bot Memory Contents ===')
    for memory in memories:
        print(f'\nID: {memory["id"]}')
        print(f'Category: {memory["category"]}')
        print(f'Content Preview: {memory["content"][:200]}...')
        print(f'Metadata: {memory["metadata"]}')

    # Search for workflow
    workflow_results = store.search_similar([0.1, 0.2, 0.3, 0.4, 0.5] * 10, limit=5)
    print(f'\n=== Workflow Search Results ({len(workflow_results)} found) ===')
    for result in workflow_results:
        print(f'ID: {result["id"]} | Similarity: {result["similarity"]:.3f} | Category: {result["category"]}')

    # Get specific memories by ID
    print('\n=== Detailed Memory Retrieval ===')
    for memory_id in [1, 2, 5]:  # workflow, reactive strategy, capabilities
        memory = store.get_memory(memory_id)
        if memory:
            print(f'\n--- Memory ID {memory_id} ---')
            if memory_id == 1:
                # Parse and display workflow summary
                workflow = json.loads(memory['content'])
                print(f"Bot Name: {workflow['name']}")
                print(f"Version: {workflow['version']}")
                print(f"Description: {workflow['description']}")
                print(f"Core Components: {len(workflow['architecture']['core_components'])}")
                print(f"Trading Strategies: {list(workflow['trading_strategies'].keys())}")
                print(f"Operating Modes: {len(workflow['operating_modes'])}")
            else:
                print(memory['content'][:500])

if __name__ == "__main__":
    asyncio.run(query_memory())