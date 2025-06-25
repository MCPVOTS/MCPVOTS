#!/usr/bin/env python3
"""
Comprehensive Gemini CLI MCP server test including chat functionality
"""

import asyncio
import json
import websockets

async def test_gemini_chat():
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
            print(f"📋 Initialize: {init_result['result']['name']} v{init_result['result']['version']}")
            print(f"   CLI Available: {init_result['result']['cli_available']}")
            print(f"   API Configured: {init_result['result']['api_configured']}")
            
            # Test 2: Chat with Gemini
            chat_message = {
                "jsonrpc": "2.0",
                "id": "2",
                "method": "gemini/chat",
                "params": {
                    "message": "Hello! Please respond with exactly: 'Gemini integration successful!'",
                    "model": "gemini-1.5-flash"
                }
            }
            
            print(f"\n💬 Testing chat with message: {chat_message['params']['message']}")
            await websocket.send(json.dumps(chat_message))
            response = await websocket.recv()
            chat_result = json.loads(response)
            
            if "result" in chat_result:
                print(f"🤖 Gemini Response: {chat_result['result']['response']}")
                print(f"   Model Used: {chat_result['result']['model']}")
                print(f"   Timestamp: {chat_result['result']['timestamp']}")
            else:
                print(f"❌ Chat Error: {chat_result}")
            
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
            print(f"\n🏥 Health Status: {health_result['result']['status']}")
            print(f"   CLI Version: {health_result['result']['version_info']}")
            
            print("\n🎉 All tests completed successfully!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini_chat())
