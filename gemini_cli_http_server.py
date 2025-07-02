#!/usr/bin/env python3
"""
Simple Gemini CLI HTTP Server
Provides HTTP API interface for Gemini CLI integration
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import time
from datetime import datetime
from aiohttp import web, ClientTimeout
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiCLIServer:
    def __init__(self, port=8017):
        self.port = port
        self.app = web.Application()
        self.gemini_cli_path = "C:\\Users\\Aldo7\\AppData\\Roaming\\npm\\gemini.cmd"
        self.setup_routes()
        
    def setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/generate', self.generate)
        self.app.router.add_get('/models', self.list_models)
        
    async def index(self, request):
        """Root endpoint"""
        return web.json_response({
            'service': 'Gemini CLI HTTP Server',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': [
                '/health - Health check',
                '/generate - Generate text (POST)',
                '/models - List available models'
            ]
        })
    
    async def health_check(self, request):
        """Health check endpoint"""
        try:
            # Quick test of Gemini CLI availability
            result = subprocess.run(
                [self.gemini_cli_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            cli_available = result.returncode == 0
            
            return web.json_response({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'gemini_cli_available': cli_available,
                'port': self.port
            })
        except Exception as e:
            return web.json_response({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=500)
    
    async def generate(self, request):
        """Generate text using Gemini CLI"""
        try:
            data = await request.json()
            prompt = data.get('prompt', '')
            model = data.get('model', 'gemini-2.5-pro')
            max_tokens = data.get('max_tokens', 2048)
            temperature = data.get('temperature', 0.7)
            
            if not prompt:
                return web.json_response({
                    'error': 'Prompt is required'
                }, status=400)
            
            # Generate response using Gemini CLI
            response = await self.generate_response(prompt, model)
            
            return web.json_response({
                'response': response,
                'model': model,
                'timestamp': datetime.now().isoformat(),
                'prompt_length': len(prompt),
                'response_length': len(response)
            })
            
        except json.JSONDecodeError:
            return web.json_response({
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.error(f"Error in generate endpoint: {e}")
            return web.json_response({
                'error': str(e)
            }, status=500)
    
    async def generate_response(self, prompt: str, model: str = "gemini-2.5-pro") -> str:
        """Generate response using Gemini CLI"""
        try:
            # Set up environment with API key
            env = os.environ.copy()
            env['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY')
            
            # Create a temporary file for the prompt to avoid shell injection
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(prompt)
                temp_file = f.name
            
            try:
                # Run Gemini CLI with the prompt file
                process = await asyncio.create_subprocess_exec(
                    self.gemini_cli_path, '--file', temp_file, '--no-stream',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env
                )
                
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
                
                if process.returncode == 0:
                    # Parse the CLI output to extract the actual response
                    output = stdout.decode('utf-8')
                    response = self.parse_gemini_output(output)
                    return response if response else "No response generated"
                else:
                    error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                    logger.error(f"Gemini CLI error: {error_msg}")
                    return f"CLI Error: {error_msg}"
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                
        except asyncio.TimeoutError:
            return "Request timed out"
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"
    
    def parse_gemini_output(self, output: str) -> str:
        """Parse Gemini CLI output to extract the actual response"""
        lines = output.strip().split('\n')
        
        # Look for the start of the actual response
        response_started = False
        response_lines = []
        
        for line in lines:
            # Skip the ASCII art header and loading indicators
            if any(indicator in line for indicator in ['██', '═', '─', '🤖', '💡', '🚀', '⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']):
                continue
            
            # Skip empty lines and tips
            if not line.strip() or 'Quick Tips:' in line or 'Type your question' in line:
                continue
                
            # Skip version and ready messages
            if any(skip in line for skip in ['Version:', 'Ready! Start chatting', 'Enhanced with']):
                continue
            
            # Start collecting the actual response
            if line.strip() and not response_started:
                response_started = True
            
            if response_started:
                response_lines.append(line.rstrip())
        
        # Join the response lines
        response = '\n'.join(response_lines).strip()
        
        # Clean up any remaining artifacts
        response = response.replace('Gemini가 생각중입니다...', '').strip()
        
        return response
    
    async def list_models(self, request):
        """List available models"""
        return web.json_response({
            'models': [
                {
                    'id': 'gemini-2.5-pro',
                    'name': 'Gemini 2.5 Pro',
                    'description': 'Latest Gemini model with enhanced capabilities'
                },
                {
                    'id': 'gemini-1.5-pro',
                    'name': 'Gemini 1.5 Pro',
                    'description': 'Previous generation Gemini model'
                }
            ]
        })
    
    async def run(self):
        """Run the server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        logger.info(f"🚀 Gemini CLI HTTP Server started on http://localhost:{self.port}")
        logger.info("Available endpoints:")
        logger.info("  GET  / - Service info")
        logger.info("  GET  /health - Health check")
        logger.info("  POST /generate - Generate text")
        logger.info("  GET  /models - List models")
        
        # Keep the server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down server...")
        finally:
            await runner.cleanup()

async def main():
    """Main function"""
    server = GeminiCLIServer(port=8017)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
