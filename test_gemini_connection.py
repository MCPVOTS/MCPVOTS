#!/usr/bin/env python3
"""
Test Gemini CLI Server Connection
"""
import asyncio
import json
import websockets

async def test_gemini_connection():
    try:
        async with websockets.connect('ws://localhost:8015') as websocket:
            # Send health check
            health_request = {
                "method": "health_check",
                "id": "test_001"
            }
            await websocket.send(json.dumps(health_request))
            health_response = await websocket.recv()
            print(f"Health Check Response: {health_response}")
            
            # Send simple generation request
            generation_request = {
                "method": "generate",
                "params": {
                    "prompt": "Hello, are you working correctly?",
                    "model": "gemini-2.5-pro"
                },
                "id": "test_002"
            }
            await websocket.send(json.dumps(generation_request))
            generation_response = await websocket.recv()
            print(f"Generation Response: {generation_response}")
            
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini_connection())
