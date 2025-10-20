#!/usr/bin/env python3
"""
Create MAXX Bot MD JSON Documentation from MCP Memory
"""

import asyncio
import json
from maxx_memory_mcp_server import get_memory_store

async def create_md_json():
    store = get_memory_store()

    # Get all stored memories
    memories = store.get_all_memories()

    # Create comprehensive MD JSON structure
    md_json = {
        'title': 'MAXX Trading Bot Ecosystem - Complete Documentation',
        'version': '2.0',
        'last_updated': '2025-10-17',
        'sections': []
    }

    # Process each memory into sections
    for memory in memories:
        section = {
            'id': memory['id'],
            'category': memory['category'],
            'metadata': memory['metadata'],
            'content': memory['content']
        }

        if memory['category'] == 'bot_workflow':
            # Parse the workflow JSON
            workflow_data = json.loads(memory['content'])
            section['title'] = 'Bot Architecture & Workflow'
            section['summary'] = workflow_data['description']
            section['architecture'] = workflow_data['architecture']
            section['strategies'] = workflow_data['trading_strategies']
            section['modes'] = workflow_data['operating_modes']
            section['risk_management'] = workflow_data['risk_management']
            section['commands'] = workflow_data['quick_commands']
            section['warnings'] = workflow_data['safety_warnings']

        elif memory['category'] == 'trading_strategy':
            strategy_type = memory['metadata'].get('strategy_type', 'unknown')
            section['title'] = f"{strategy_type.title()} Strategy"
            section['risk_level'] = memory['metadata'].get('risk_level', 'unknown')
            section['automation_level'] = memory['metadata'].get('automation_level', 'unknown')

        elif memory['category'] == 'system_capabilities':
            capabilities_data = json.loads(memory['content'])
            section['title'] = 'System Capabilities'
            section['features'] = capabilities_data

        md_json['sections'].append(section)

    # Add debugging context for the client-side error
    md_json['debugging_context'] = {
        'client_error_analysis': {
            'possible_causes': [
                'Three.js initialization failure',
                'WebSocket connection issues',
                'OnchainKit provider configuration',
                'React hydration mismatch',
                'Missing environment variables',
                'Mini-app validation requirements'
            ],
            'checklist': [
                'Verify Three.js refs are properly initialized',
                'Check WebSocket connection to trading bot',
                'Validate OnchainKit MiniKit configuration',
                'Ensure dynamic rendering for SSR compatibility',
                'Check browser console for specific error messages',
                'Verify Farcaster frame context availability'
            ]
        },
        'system_status': {
            'nextjs_build': 'successful',
            'tailwind_compilation': 'working',
            'websocket_server': 'available',
            'mcp_memory': 'functional',
            'trading_bot': 'ready'
        }
    }

    # Write to file
    with open('data/MAXX_BOT_DOCUMENTATION.md.json', 'w', encoding='utf-8') as f:
        json.dump(md_json, f, indent=2, ensure_ascii=False)

    print('Created data/MAXX_BOT_DOCUMENTATION.md.json with comprehensive bot documentation')
    print(f'Total sections: {len(md_json["sections"])}')
    print(f'File size: {len(json.dumps(md_json))} characters')

if __name__ == "__main__":
    asyncio.run(create_md_json())
