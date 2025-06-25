#!/usr/bin/env python3
"""
MCPVots WebSocket Server
Implements the Model Context Protocol over WebSocket
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import Dict, Any, Optional
from websockets.server import WebSocketServerProtocol

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self):
        self.connections: Dict[str, WebSocketServerProtocol] = {}
        self.tools = {
            "echo": {
                "description": "Echo back the input message",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    },
                    "required": ["message"]
                }
            },
            "get_time": {
                "description": "Get the current server time",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "health_check": {
                "description": "Check server health status",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
        self.resources = {
            "server_info": {
                "description": "Information about the MCP server",
                "mimeType": "application/json"
            }
        }

    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new WebSocket connection"""
        client_id = f"client_{len(self.connections)}"
        self.connections[client_id] = websocket
        logger.info(f"New client connected: {client_id}")

        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Clean up connection
            for cid, conn in list(self.connections.items()):
                if conn == websocket:
                    del self.connections[cid]
                    break

    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming JSON-RPC message"""
        try:
            data = json.loads(message)
            logger.info(f"Received: {data}")

            # Validate JSON-RPC structure
            if not isinstance(data, dict) or data.get("jsonrpc") != "2.0":
                await self.send_error(websocket, None, -32600, "Invalid Request")
                return

            method = data.get("method")
            params = data.get("params", {})
            request_id = data.get("id")

            # Handle different MCP methods
            if method == "initialize":
                await self.handle_initialize(websocket, params, request_id)
            elif method == "tools/list":
                await self.handle_list_tools(websocket, request_id)
            elif method == "tools/call":
                await self.handle_call_tool(websocket, params, request_id)
            elif method == "resources/list":
                await self.handle_list_resources(websocket, request_id)
            elif method == "resources/read":
                await self.handle_read_resource(websocket, params, request_id)
            else:
                await self.send_error(websocket, request_id, -32601, f"Method not found: {method}")

        except json.JSONDecodeError:
            await self.send_error(websocket, None, -32700, "Parse error")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_error(websocket, None, -32603, "Internal error")

    async def handle_initialize(self, websocket: WebSocketServerProtocol, params: Dict[str, Any], request_id: Optional[str]):
        """Handle initialization request"""
        client_info = params.get("clientInfo", {})
        protocol_version = params.get("protocolVersion", "2024-11-05")
        
        logger.info(f"Initializing client: {client_info}")

        response = {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": protocol_version,
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    },
                    "resources": {
                        "subscribe": True,
                        "listChanged": True
                    }
                },
                "serverInfo": {
                    "name": "MCPVots Server",
                    "version": "2.0.0"
                }
            },
            "id": request_id
        }

        await self.send_response(websocket, response)

    async def handle_list_tools(self, websocket: WebSocketServerProtocol, request_id: Optional[str]):
        """Handle tools/list request"""
        tools_list = [
            {
                "name": name,
                "description": tool["description"],
                "inputSchema": tool["inputSchema"]
            }
            for name, tool in self.tools.items()
        ]

        response = {
            "jsonrpc": "2.0",
            "result": {
                "tools": tools_list
            },
            "id": request_id
        }

        await self.send_response(websocket, response)

    async def handle_call_tool(self, websocket: WebSocketServerProtocol, params: Dict[str, Any], request_id: Optional[str]):
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in self.tools:
            await self.send_error(websocket, request_id, -32602, f"Unknown tool: {tool_name}")
            return

        # Execute the tool
        try:
            result = await self.execute_tool(tool_name, arguments)
            response = {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                },
                "id": request_id
            }
            await self.send_response(websocket, response)

        except Exception as e:
            await self.send_error(websocket, request_id, -32603, f"Tool execution failed: {str(e)}")

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a specific tool"""
        if tool_name == "echo":
            return {"echoed": arguments.get("message", "")}
        
        elif tool_name == "get_time":
            return {
                "current_time": datetime.now().isoformat(),
                "timezone": "UTC"
            }
        
        elif tool_name == "health_check":
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "connections": len(self.connections),
                "uptime": "running"
            }
        
        else:
            raise Exception(f"Tool {tool_name} not implemented")

    async def handle_list_resources(self, websocket: WebSocketServerProtocol, request_id: Optional[str]):
        """Handle resources/list request"""
        resources_list = [
            {
                "uri": f"mcpvots://{name}",
                "name": name,
                "description": resource["description"],
                "mimeType": resource["mimeType"]
            }
            for name, resource in self.resources.items()
        ]

        response = {
            "jsonrpc": "2.0",
            "result": {
                "resources": resources_list
            },
            "id": request_id
        }

        await self.send_response(websocket, response)

    async def handle_read_resource(self, websocket: WebSocketServerProtocol, params: Dict[str, Any], request_id: Optional[str]):
        """Handle resources/read request"""
        uri = params.get("uri", "")
        
        if uri == "mcpvots://server_info":
            content = {
                "server": "MCPVots MCP Server",
                "version": "2.0.0",
                "capabilities": ["tools", "resources"],
                "status": "running",
                "connections": len(self.connections)
            }
        else:
            await self.send_error(websocket, request_id, -32602, f"Unknown resource: {uri}")
            return

        response = {
            "jsonrpc": "2.0",
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(content, indent=2)
                    }
                ]
            },
            "id": request_id
        }

        await self.send_response(websocket, response)

    async def send_response(self, websocket: WebSocketServerProtocol, response: Dict[str, Any]):
        """Send JSON-RPC response"""
        await websocket.send(json.dumps(response))

    async def send_error(self, websocket: WebSocketServerProtocol, request_id: Optional[str], code: int, message: str):
        """Send JSON-RPC error response"""
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        }
        await websocket.send(json.dumps(error_response))

async def main():
    """Start the MCP WebSocket server"""
    server = MCPServer()
    
    logger.info("Starting MCPVots WebSocket server on ws://localhost:3001")
    
    async with websockets.serve(
        server.handle_connection,
        "localhost",
        3001,
        ping_interval=20,
        ping_timeout=10
    ):
        logger.info("MCP Server is running...")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
