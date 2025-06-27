#!/usr/bin/env python3
"""Quick test of the WebSocket connection"""
import asyncio
import websockets
import json

async def test_websocket():
    try:
        uri = "ws://localhost:8025"
        async with websockets.connect(uri) as websocket:
            # Send test message
            test_message = {
                "jsonrpc": "2.0",
                "id": 123,
                "method": "gemini/chat",
                "params": {
                    "message": "Hello, test connection!",
                    "model": "gemini-2.5-flash"
                }
            }
            
            await websocket.send(json.dumps(test_message))
            response = await websocket.recv()
            
            print("✅ WebSocket test successful!")
            print("Response:", json.loads(response))
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
