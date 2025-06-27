#!/usr/bin/env python3
"""
Simple test backend for chat functionality
"""
import asyncio
import json
import websockets
from aiohttp import web
import aiohttp_cors
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockAIService:
    """Mock AI service for testing chat UI"""
    
    async def handle_gemini_websocket(self, websocket):
        """Handle Gemini WebSocket connections"""
        logger.info(f"New WebSocket connection from {websocket.remote_address}")
        try:
            async for message in websocket:
                data = json.loads(message)
                logger.info(f"Received: {data}")
                
                if data.get("method") == "gemini/chat":
                    response = {
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "result": {
                            "response": f"✨ **Gemini 2.5 Test Response:**\n\nI received your message: '{data['params']['message']}'\n\nThis is a test response from the mock Gemini service to verify that the chat UI is working correctly with real backend connections.",
                            "tokens": 45,
                            "model": "gemini-2.5-flash"
                        }
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "error": {"code": -1, "message": "Unknown method"}
                    }
                
                await websocket.send(json.dumps(response))
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")

    async def handle_deepseek_chat(self, request):
        """Handle DeepSeek HTTP requests"""
        try:
            data = await request.json()
            logger.info(f"DeepSeek request: {data}")
            
            response_data = {
                "response": f"🧠 **DeepSeek R1 Test Analysis:**\n\nReceived message: '{data['message']}'\n\n**Step 1: Understanding**\n- Parsed your input successfully\n- Identified test scenario\n\n**Step 2: Response Generation**\n- Generated test response\n- Verified chat connection\n\nThis is a test response from the mock DeepSeek service.",
                "tokens": 52,
                "reasoning": [
                    "Received and parsed user message",
                    "Generated structured test response",
                    "Verified backend connection works"
                ]
            }
            
            return web.json_response(response_data)
        except Exception as e:
            logger.error(f"DeepSeek error: {e}")
            return web.json_response(
                {"error": str(e)}, 
                status=500
            )

    async def handle_health(self, request):
        """Health check endpoint"""
        return web.json_response({"status": "healthy", "services": ["gemini", "deepseek"]})
    
    async def handle_options(self, request):
        """Handle CORS preflight requests"""
        return web.Response(
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Max-Age': '86400'
            }
        )

async def main():
    """Start mock services"""
    service = MockAIService()
    
    # Start WebSocket server for Gemini (port 8025)
    logger.info("Starting Gemini WebSocket server on port 8025...")
    gemini_server = await websockets.serve(
        service.handle_gemini_websocket,
        "localhost",
        8025
    )
    
    # Start HTTP server for DeepSeek (port 8095)
    logger.info("Starting DeepSeek HTTP server on port 8095...")
    app = web.Application()
    
    # Add CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add specific CORS for localhost development
    cors = aiohttp_cors.setup(app, defaults={
        "http://localhost:3000": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        ),
        "http://127.0.0.1:3000": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*", 
            allow_headers="*",
            allow_methods="*"
        ),
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*", 
            allow_methods="*"
        )
    })
    
    # Add routes
    app.router.add_post('/ai/chat', service.handle_deepseek_chat)
    app.router.add_get('/health', service.handle_health)
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8095)
    await site.start()
    
    logger.info("🚀 Mock AI Services are running!")
    logger.info("- Gemini WebSocket: ws://localhost:8025")
    logger.info("- DeepSeek HTTP: http://localhost:8095")
    logger.info("- Health check: http://localhost:8095/health")
    logger.info("Chat UI should now work with real backend connections!")
    
    # Keep running
    await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down mock services...")
