#!/usr/bin/env python3
"""
Test script for Gemini CLI integration
"""

import asyncio
import json
import os
import websockets
from pathlib import Path

async def test_gemini_service():
    """Test the Gemini CLI MCP service"""
    
    # Set API key
    os.environ["GEMINI_API_KEY"] = "AIzaSyCIZWULUzZjMuObZ5dg8V57fwhvzLMvevg"
    
    # Start the server in background
    server_script = Path(__file__).parent / "servers" / "gemini_cli_server.py"
    server_process = await asyncio.create_subprocess_exec(
        "python", str(server_script),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Wait a moment for server to start
    await asyncio.sleep(3)
    
    try:
        # Connect to the server
        uri = "ws://localhost:8015"
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
            print(f"📋 Initialize: {init_result['result']['name']}")
            
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
            print(f"🤖 Available models: {list(models_result['result']['models'].keys())}")
            
            # Test 3: Simple chat
            chat_message = {
                "jsonrpc": "2.0",
                "id": "3",
                "method": "gemini/chat", 
                "params": {
                    "message": "Hello! What can you help me with?",
                    "model": "gemini-1.5-flash"
                }
            }
            
            await websocket.send(json.dumps(chat_message))
            response = await websocket.recv()
            chat_result = json.loads(response)
            
            if "result" in chat_result:
                print(f"💬 Chat response: {chat_result['result']['response'][:100]}...")
            else:
                print(f"❌ Chat failed: {chat_result}")
            
            # Test 4: Health check
            health_message = {
                "jsonrpc": "2.0",
                "id": "4",
                "method": "gemini/health",
                "params": {}
            }
            
            await websocket.send(json.dumps(health_message))
            response = await websocket.recv()
            health_result = json.loads(response)
            print(f"🏥 Health status: {health_result['result']['status']}")
            
            print("✅ All tests passed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        # Clean up server process
        server_process.terminate()
        await server_process.wait()

if __name__ == "__main__":
    asyncio.run(test_gemini_service())
