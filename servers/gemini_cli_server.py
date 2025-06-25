#!/usr/bin/env python3
"""
Gemini        self.models = {
        self.models = {
            "gemini-2.5-pro": {
                "name": "Gemini 2.5 Pro",
                "capabilities": ["text", "vision", "code", "reasoning", "massive-context"],
                "context_window": 1000000,
                "description": "Most advanced model with 1M token context window - free with personal Google account"
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
            },
            "gemini-2.0-exp": {
                "name": "Gemini 2.0 Experimental",
                "capabilities": ["text", "vision", "code", "reasoning", "multimodal"],
                "context_window": 2097152,
                "description": "Experimental model with enhanced capabilities"
            }
        }2.5-pro": {
                "name": "Gemini 2.5 Pro",
                "capabilities": ["text", "vision", "code", "reasoning", "multimodal", "large-context"],
                "context_window": 1048576,
                "description": "Latest and most capable model with 1M token context window - FREE for developers"
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
            },
            "gemini-2.0-exp": {
                "name": "Gemini 2.0 Experimental",
                "capabilities": ["text", "vision", "code", "reasoning", "multimodal"],
                "context_window": 2097152,
                "description": "Experimental model with enhanced capabilities"
            }
        }vice for MCPVots
==========================================
Provides Google Gemini AI capabilities through the official CLI
Integrates with Trilogy AGI and MCP ecosystem
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiCLIService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        # Fix the path to point to the correct location
        self.cli_path = Path(__file__).parent.parent / "gemini-cli" / "packages" / "cli" / "dist" / "index.js"
        self.conversation_history = {}
        self.active_sessions = {}
        self.models = {
            "gemini-2.5-pro": {
                "name": "Gemini 2.5 Pro",
                "capabilities": ["text", "vision", "code", "reasoning", "massive-context"],
                "context_window": 1000000,
                "description": "Latest and most capable model with 1M token context window - Free tier: 60 requests/min, 1000/day"
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
            },
            "gemini-2.0-exp": {
                "name": "Gemini 2.0 Experimental",
                "capabilities": ["text", "vision", "code", "reasoning", "multimodal"],
                "context_window": 2097152,
                "description": "Experimental model with enhanced capabilities"
            }
        }
        
        # Initialize environment
        self.setup_environment()

    def setup_environment(self):
        """Setup the Gemini CLI environment"""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not provided")
        
        # Set API key in environment
        os.environ["GEMINI_API_KEY"] = self.api_key
        
        # Ensure CLI is available
        if not self.cli_path.exists():
            logger.warning(f"Gemini CLI not found at {self.cli_path}")
            # Try to find it in the current directory
            alt_path = Path.cwd() / "gemini-cli" / "packages" / "cli" / "dist" / "index.js"
            if alt_path.exists():
                self.cli_path = alt_path
                logger.info(f"Found Gemini CLI at {self.cli_path}")
            else:
                logger.error("Gemini CLI not found - please ensure it's built")

    async def handle_message(self, websocket, message: str):
        """Handle incoming MCP messages"""
        try:
            data = json.loads(message)
            method = data.get("method")
            params = data.get("params", {})
            msg_id = data.get("id")
            
            if method == "initialize":
                response = await self.initialize(params)
            elif method == "gemini/chat":
                response = await self.chat(params)
            elif method == "gemini/generate":
                response = await self.generate(params)
            elif method == "gemini/analyze_image":
                response = await self.analyze_image(params)
            elif method == "gemini/analyze_code":
                response = await self.analyze_code(params)
            elif method == "gemini/start_conversation":
                response = await self.start_conversation(params)
            elif method == "gemini/continue_conversation":
                response = await self.continue_conversation(params)
            elif method == "gemini/list_models":
                response = await self.list_models(params)
            elif method == "gemini/get_model_info":
                response = await self.get_model_info(params)
            elif method == "gemini/configure":
                response = await self.configure(params)
            elif method == "gemini/health":
                response = await self.health_check(params)
            else:
                response = {"error": {"code": -32601, "message": "Method not found"}}
            
            if msg_id:
                response["id"] = msg_id
                
            await websocket.send(json.dumps(response))
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": data.get("id") if 'data' in locals() else None
            }
            await websocket.send(json.dumps(error_response))

    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the Gemini CLI service"""
        return {
            "jsonrpc": "2.0",
            "result": {
                "name": "Gemini CLI Service",
                "version": "1.0.0",
                "capabilities": [
                    "text-generation",
                    "image-analysis", 
                    "code-analysis",
                    "conversation",
                    "multi-modal",
                    "reasoning"
                ],
                "available_models": list(self.models.keys()),
                "cli_available": self.cli_path.exists(),
                "api_configured": bool(self.api_key)
            }
        }

    async def chat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simple chat interaction with Gemini"""
        message = params.get("message")
        model = params.get("model", "gemini-2.5-pro")  # Default to Gemini 2.5 Pro
        
        if not message:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "message is required"}
            }
        
        try:
            # Use the CLI with the correct syntax
            result = await self.run_gemini_cli([
                "--model", model,
                "--prompt", message
            ])
            
            return {
                "jsonrpc": "2.0",
                "result": {
                    "message": message,
                    "response": result.get("response", ""),
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    "usage": result.get("usage", {})
                }
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Chat failed: {str(e)}"}
            }

    async def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content with Gemini"""
        prompt = params.get("prompt")
        model = params.get("model", "gemini-2.5-pro")  # Default to Gemini 2.5 Pro
        max_tokens = params.get("max_tokens", 1000)
        temperature = params.get("temperature", 0.7)
        
        if not prompt:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "prompt is required"}
            }
        
        try:
            # Create a temporary file for the prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            try:
                result = await self.run_gemini_cli([
                    "generate",
                    "--model", model,
                    "--file", prompt_file,
                    "--max-tokens", str(max_tokens),
                    "--temperature", str(temperature)
                ])
                
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "prompt": prompt,
                        "generated_text": result.get("generated_text", ""),
                        "model": model,
                        "parameters": {
                            "max_tokens": max_tokens,
                            "temperature": temperature
                        },
                        "timestamp": datetime.now().isoformat(),
                        "usage": result.get("usage", {})
                    }
                }
                
            finally:
                # Clean up temp file
                os.unlink(prompt_file)
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Generation failed: {str(e)}"}
            }

    async def analyze_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an image with Gemini"""
        image_path = params.get("image_path")
        prompt = params.get("prompt", "Describe this image in detail.")
        model = params.get("model", "gemini-1.5-pro")
        
        if not image_path:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "image_path is required"}
            }
        
        if not Path(image_path).exists():
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Image file not found"}
            }
        
        try:
            result = await self.run_gemini_cli([
                "analyze",
                "--model", model,
                "--image", image_path,
                "--prompt", prompt
            ])
            
            return {
                "jsonrpc": "2.0",
                "result": {
                    "image_path": image_path,
                    "prompt": prompt,
                    "analysis": result.get("analysis", ""),
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    "usage": result.get("usage", {})
                }
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Image analysis failed: {str(e)}"}
            }

    async def analyze_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code with Gemini"""
        code = params.get("code")
        file_path = params.get("file_path")
        language = params.get("language", "auto")
        analysis_type = params.get("analysis_type", "review")
        model = params.get("model", "gemini-1.5-pro")
        
        if not code and not file_path:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Either code or file_path is required"}
            }
        
        try:
            args = ["analyze-code", "--model", model, "--type", analysis_type]
            
            if file_path:
                args.extend(["--file", file_path])
            else:
                # Create temp file for code
                with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                args.extend(["--file", temp_file])
            
            result = await self.run_gemini_cli(args)
            
            # Clean up temp file if created
            if not file_path and 'temp_file' in locals():
                os.unlink(temp_file)
            
            return {
                "jsonrpc": "2.0",
                "result": {
                    "code": code,
                    "file_path": file_path,
                    "language": language,
                    "analysis_type": analysis_type,
                    "analysis": result.get("analysis", ""),
                    "suggestions": result.get("suggestions", []),
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    "usage": result.get("usage", {})
                }
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Code analysis failed: {str(e)}"}
            }

    async def start_conversation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new conversation session"""
        session_id = params.get("session_id")
        model = params.get("model", "gemini-1.5-flash")
        system_prompt = params.get("system_prompt", "")
        
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.conversation_history[session_id] = {
            "model": model,
            "messages": [],
            "system_prompt": system_prompt,
            "created_at": datetime.now().isoformat()
        }
        
        if system_prompt:
            self.conversation_history[session_id]["messages"].append({
                "role": "system",
                "content": system_prompt,
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "session_id": session_id,
                "model": model,
                "status": "started",
                "message_count": len(self.conversation_history[session_id]["messages"])
            }
        }

    async def continue_conversation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Continue an existing conversation"""
        session_id = params.get("session_id")
        message = params.get("message")
        
        if not session_id or session_id not in self.conversation_history:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Invalid session_id"}
            }
        
        if not message:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "message is required"}
            }
        
        try:
            conversation = self.conversation_history[session_id]
            
            # Add user message
            conversation["messages"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Prepare conversation context
            context = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation["messages"]
            ])
            
            # Get response from Gemini
            result = await self.run_gemini_cli([
                "chat",
                "--model", conversation["model"],
                "--message", context
            ])
            
            response_text = result.get("response", "")
            
            # Add assistant response
            conversation["messages"].append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "jsonrpc": "2.0",
                "result": {
                    "session_id": session_id,
                    "user_message": message,
                    "assistant_response": response_text,
                    "message_count": len(conversation["messages"]),
                    "model": conversation["model"],
                    "usage": result.get("usage", {})
                }
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Conversation failed: {str(e)}"}
            }

    async def list_models(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available Gemini models"""
        return {
            "jsonrpc": "2.0",
            "result": {
                "models": self.models,
                "count": len(self.models)
            }
        }

    async def get_model_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a specific model"""
        model_name = params.get("model")
        
        if not model_name:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "model name is required"}
            }
        
        if model_name not in self.models:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Model not found"}
            }
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "model": model_name,
                "info": self.models[model_name]
            }
        }

    async def configure(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configure Gemini CLI settings"""
        api_key = params.get("api_key")
        
        if api_key:
            self.api_key = api_key
            os.environ["GEMINI_API_KEY"] = api_key
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "api_configured": bool(self.api_key),
                "cli_available": self.cli_path.exists()
            }
        }

    async def health_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Health check for the service"""
        try:
            # Try a simple version check
            result = await self.run_gemini_cli(["--version"])
            
            return {
                "jsonrpc": "2.0",
                "result": {
                    "status": "healthy",
                    "api_accessible": True,
                    "cli_functional": True,
                    "cli_path": str(self.cli_path),
                    "version_info": result.get("response", "unknown"),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "result": {
                    "status": "unhealthy",
                    "api_accessible": False,
                    "cli_functional": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }

    async def run_gemini_cli(self, args: List[str]) -> Dict[str, Any]:
        """Run the Gemini CLI with given arguments"""
        try:
            # Construct the full command
            cmd = ["node", str(self.cli_path)] + args
            
            # Run the command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=os.environ.copy()
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"CLI command failed: {stderr.decode()}")
            
            output = stdout.decode().strip()
            
            # Try to parse JSON output
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                # If not JSON, return as text
                return {"response": output}
                
        except Exception as e:
            logger.error(f"Failed to run Gemini CLI: {e}")
            raise

async def handle_client(websocket):
    """Handle WebSocket connections"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not set")
        return
    
    server = GeminiCLIService(api_key)
    logger.info(f"New Gemini CLI client connected: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            await server.handle_message(websocket, message)
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Gemini CLI client disconnected: {websocket.remote_address}")
    except Exception as e:
        logger.error(f"Error with Gemini CLI client {websocket.remote_address}: {e}")

async def main():
    """Start the Gemini CLI MCP server"""
    # Set API key from environment or argument
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("Please set GEMINI_API_KEY environment variable")
        return
    
    # Use the standard websockets API
    logger.info("Starting Gemini CLI MCP Server on ws://localhost:8015")
    logger.info(f"API Key configured: {'*' * (len(api_key) - 8) + api_key[-8:]}")
    
    try:
        async with websockets.serve(handle_client, "localhost", 8015):
            logger.info("Gemini CLI MCP Server started successfully")
            await asyncio.Future()  # Keep the server running
    except KeyboardInterrupt:
        logger.info("Gemini CLI server shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
