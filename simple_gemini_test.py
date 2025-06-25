#!/usr/bin/env python3
"""
Simple test client for Gemini CLI MCP server
"""

import asyncio
import json
import websockets

async def test_gemini():
    uri = "ws://localhost:8015"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to Gemini CLI MCP Server")
            
            # Test 1: Initialize
            init_message = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "initialize",
                "params": {}
            }
            
            await websocket.send(json.dumps(init_message))
            response = await websocket.recv()
            init_result = json.loads(response)
            print(f"📋 Initialize: {init_result}")
            
            # Test 2: List models
            models_message = {
                "jsonrpc": "2.0",
                "id": "2", 
                "method": "gemini/list_models",
                "params": {}
            }
            
            await websocket.send(json.dumps(models_message))
            response = await websocket.recv()
            models_result = json.loads(response)
            print(f"🤖 Models: {models_result}")
            
            # Test 3: Health check
            health_message = {
                "jsonrpc": "2.0",
                "id": "3",
                "method": "gemini/health",
                "params": {}
            }
            
            await websocket.send(json.dumps(health_message))
            response = await websocket.recv()
            health_result = json.loads(response)
            print(f"🏥 Health: {health_result}")
            
            # Test 4: Chat with Gemini 2.5 Pro
            chat_message = {
                "jsonrpc": "2.0",
                "id": "4",
                "method": "gemini/chat",
                "params": {
                    "message": "Hello! Please explain what makes Gemini 2.5 Pro special in one concise paragraph.",
                    "model": "gemini-2.5-pro"
                }
            }
            
            print("\n💬 Testing Gemini 2.5 Pro Chat...")
            await websocket.send(json.dumps(chat_message))
            response = await websocket.recv()
            chat_result = json.loads(response)
            
            if "result" in chat_result:
                print(f"✅ Chat Success!")
                print(f"📝 Response: {chat_result['result'].get('response', 'No response')}")
                print(f"🤖 Model: {chat_result['result'].get('model', 'Unknown')}")
            else:
                print(f"❌ Chat Error: {chat_result}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
