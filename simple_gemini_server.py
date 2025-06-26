#!/usr/bin/env python3
"""
Simple Gemini HTTP Server - Reliable Version
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from aiohttp import web

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleGeminiServer:
    def __init__(self, port=8017):
        self.port = port
        self.gemini_cli_path = "C:\\Users\\Aldo7\\AppData\\Roaming\\npm\\gemini.cmd"
        self.api_key = "AIzaSyCIZWULUzZjMuObZ5dg8V57fwhvzLMvevg"
        
    async def health_check(self, request):
        """Health check endpoint"""
        try:
            # Test if Gemini CLI is available
            result = subprocess.run(
                [self.gemini_cli_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5,
                env={**os.environ, 'GEMINI_API_KEY': self.api_key}
            )
            
            cli_available = result.returncode == 0
            
            response_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'gemini_cli_available': cli_available,
                'port': self.port
            }
            
            logger.info(f"Health check: {response_data}")
            return web.json_response(response_data)
            
        except Exception as e:
            error_response = {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            logger.error(f"Health check failed: {error_response}")
            return web.json_response(error_response, status=500)
    
    async def generate(self, request):
        """Generate text using Gemini CLI"""
        try:
            data = await request.json()
            prompt = data.get('prompt', '')
            
            if not prompt:
                return web.json_response({'error': 'Prompt is required'}, status=400)
            
            logger.info(f"Generating response for prompt: {prompt[:100]}...")
            
            # For now, return a mock response to test connectivity
            mock_response = f"Mock Gemini response for: {prompt[:50]}... [Generated at {datetime.now().isoformat()}]"
            
            response_data = {
                'response': mock_response,
                'model': 'gemini-2.5-pro',
                'timestamp': datetime.now().isoformat(),
                'status': 'mock'
            }
            
            logger.info(f"Generated response: {response_data}")
            return web.json_response(response_data)
            
        except Exception as e:
            error_response = {'error': str(e)}
            logger.error(f"Generation error: {error_response}")
            return web.json_response(error_response, status=500)
    
    async def index(self, request):
        """Root endpoint"""
        return web.json_response({
            'service': 'Simple Gemini HTTP Server',
            'version': '1.0.0',
            'status': 'running',
            'port': self.port,
            'endpoints': {
                '/': 'This endpoint',
                '/health': 'Health check',
                '/generate': 'Generate text (POST)'
            }
        })
    
    async def run(self):
        """Run the server"""
        app = web.Application()
        
        # Add routes
        app.router.add_get('/', self.index)
        app.router.add_get('/health', self.health_check)
        app.router.add_post('/generate', self.generate)
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        logger.info(f"🚀 Simple Gemini Server started on http://localhost:{self.port}")
        logger.info("Available endpoints:")
        logger.info("  GET  / - Service info")
        logger.info("  GET  /health - Health check")
        logger.info("  POST /generate - Generate text")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            await runner.cleanup()

async def main():
    server = SimpleGeminiServer(port=8017)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
