#!/usr/bin/env python3
"""
Simple HTTP Gemini CLI Server
============================
A lightweight HTTP server that interfaces with the Gemini CLI for the MCPVots ecosystem.
Compatible with the autonomous AI coordinator.
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import aiohttp
from aiohttp import web
import aiohttp_cors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleGeminiCLIServer:
    def __init__(self, api_key: Optional[str] = None, port: int = 8016):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        
        # Check for Gemini CLI installation
        self.cli_available = self.check_cli_availability()
        
    def check_cli_availability(self) -> bool:
        """Check if Gemini CLI is available"""
        try:
            # Try to find gemini CLI in common locations
            possible_paths = [
                "gemini",
                "npx @google/generative-ai-cli",
                str(Path.home() / ".npm" / "_npx" / "gemini"),
                "C:\\Users\\{username}\\AppData\\Roaming\\npm\\gemini.cmd".format(
                    username=os.getenv("USERNAME", "")
                )
            ]
            
            for path in possible_paths:
                try:
                    result = subprocess.run(
                        [path, "--version"] if not path.startswith("npx") else [path, "version"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        logger.info(f"✅ Gemini CLI found at: {path}")
                        self.cli_command = path
                        return True
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
            
            logger.warning("⚠️ Gemini CLI not found. Please install with: npm install -g @google/generative-ai-cli")
            return False
            
        except Exception as e:
            logger.error(f"Error checking CLI availability: {e}")
            return False
    
    def setup_routes(self):
        """Setup HTTP routes"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add routes
        cors.add(self.app.router.add_get('/health', self.health_check))
        cors.add(self.app.router.add_post('/generate', self.generate))
        cors.add(self.app.router.add_get('/models', self.list_models))
        
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "service": "Simple Gemini CLI Server",
            "cli_available": self.cli_available,
            "timestamp": datetime.now().isoformat()
        })
    
    async def list_models(self, request):
        """List available models"""
        models = {
            "gemini-2.5-pro": {
                "name": "Gemini 2.5 Pro",
                "capabilities": ["text", "vision", "code", "reasoning", "massive-context"],
                "context_window": 1000000,
                "description": "Most advanced model with 1M token context window"
            },
            "gemini-1.5-pro": {
                "name": "Gemini 1.5 Pro", 
                "capabilities": ["text", "vision", "code", "reasoning"],
                "context_window": 1048576,
                "description": "Most capable model for complex tasks"
            },
            "gemini-1.5-flash": {
                "name": "Gemini 1.5 Flash",
                "capabilities": ["text", "vision", "code", "fast-response"],
                "context_window": 1048576,
                "description": "Fast and efficient model for quick responses"
            }
        }
        return web.json_response({"models": models})
    
    async def generate(self, request):
        """Generate response using Gemini CLI"""
        try:
            data = await request.json()
            prompt = data.get("prompt", "")
            model = data.get("model", "gemini-2.5-pro")
            temperature = data.get("temperature", 0.7)
            max_tokens = data.get("max_tokens", 2048)
            
            if not prompt:
                return web.json_response(
                    {"error": "Prompt is required"}, 
                    status=400
                )
            
            if not self.cli_available:
                return web.json_response(
                    {"error": "Gemini CLI is not available"}, 
                    status=503
                )
            
            # Call Gemini CLI
            response_text = await self.call_gemini_cli(
                prompt, model, temperature, max_tokens
            )
            
            return web.json_response({
                "response": response_text,
                "model": model,
                "timestamp": datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return web.json_response(
                {"error": "Invalid JSON payload"}, 
                status=400
            )
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return web.json_response(
                {"error": f"Generation failed: {str(e)}"}, 
                status=500
            )
    
    async def call_gemini_cli(self, prompt: str, model: str, temperature: float, max_tokens: int) -> str:
        """Call the Gemini CLI and return response"""
        try:
            # Create temporary file for prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            # Prepare CLI command
            cmd = [
                self.cli_command if hasattr(self, 'cli_command') else "gemini",
                "generate",
                "--model", model,
                "--temperature", str(temperature),
                "--max-tokens", str(max_tokens),
                "--input", prompt_file
            ]
            
            # Execute CLI command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "GEMINI_API_KEY": self.api_key} if self.api_key else os.environ
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up temp file
            try:
                os.unlink(prompt_file)
            except:
                pass
            
            if process.returncode == 0:
                return stdout.decode().strip()
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Gemini CLI error: {error_msg}")
                raise Exception(f"CLI error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error calling Gemini CLI: {e}")
            # Fallback response for testing
            return f"⚠️ Gemini CLI unavailable. Mock response for: {prompt[:100]}..."
    
    async def start_server(self):
        """Start the HTTP server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        logger.info(f"🚀 Simple Gemini CLI Server running on http://localhost:{self.port}")
        return runner

async def main():
    """Main entry point"""
    server = SimpleGeminiCLIServer(port=8016)
    runner = await server.start_server()
    
    try:
        # Keep server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down server...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
