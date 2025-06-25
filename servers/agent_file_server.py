#!/usr/bin/env python3
"""
Agent File System MCP Server
Multi-agent file management and coordination system
"""

import asyncio
import json
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import websockets
from websockets.server import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentFileServer:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "agent_files"
        self.base_path.mkdir(exist_ok=True)
        self.agents = {}
        self.file_locks = {}
        self.version_history = {}
        self.collaboration_sessions = {}
        
    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming MCP messages"""
        try:
            data = json.loads(message)
            method = data.get("method")
            params = data.get("params", {})
            msg_id = data.get("id")
            
            if method == "initialize":
                response = await self.initialize(params)
            elif method == "agent_file/register_agent":
                response = await self.register_agent(params)
            elif method == "agent_file/create_file":
                response = await self.create_file(params)
            elif method == "agent_file/read_file":
                response = await self.read_file(params)
            elif method == "agent_file/update_file":
                response = await self.update_file(params)
            elif method == "agent_file/delete_file":
                response = await self.delete_file(params)
            elif method == "agent_file/lock_file":
                response = await self.lock_file(params)
            elif method == "agent_file/unlock_file":
                response = await self.unlock_file(params)
            elif method == "agent_file/get_file_history":
                response = await self.get_file_history(params)
            elif method == "agent_file/start_collaboration":
                response = await self.start_collaboration(params)
            elif method == "agent_file/end_collaboration":
                response = await self.end_collaboration(params)
            elif method == "agent_file/list_files":
                response = await self.list_files(params)
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
        """Initialize the Agent File System"""
        return {
            "jsonrpc": "2.0",
            "result": {
                "name": "Agent File System",
                "version": "1.0.0",
                "capabilities": ["multi-agent-files", "coordination", "version-control", "collaboration"],
                "base_path": str(self.base_path),
                "active_agents": len(self.agents),
                "total_files": len(list(self.base_path.rglob("*"))) if self.base_path.exists() else 0
            }
        }

    async def register_agent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent with the file system"""
        agent_id = params.get("agent_id")
        agent_name = params.get("agent_name", f"Agent_{agent_id}")
        capabilities = params.get("capabilities", [])
        
        if not agent_id:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "agent_id is required"}
            }
        
        # Create agent workspace
        agent_path = self.base_path / agent_id
        agent_path.mkdir(exist_ok=True)
        
        self.agents[agent_id] = {
            "id": agent_id,
            "name": agent_name,
            "capabilities": capabilities,
            "workspace": str(agent_path),
            "registered_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "files_created": 0,
            "files_modified": 0
        }
        
        logger.info(f"Registered agent: {agent_name} ({agent_id})")
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "agent_id": agent_id,
                "workspace": str(agent_path),
                "status": "registered",
                "capabilities": capabilities
            }
        }

    async def create_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new file"""
        agent_id = params.get("agent_id")
        file_path = params.get("file_path")
        content = params.get("content", "")
        
        if not agent_id or not file_path:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "agent_id and file_path are required"}
            }
        
        if agent_id not in self.agents:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Agent not registered"}
            }
        
        # Create file in agent's workspace
        full_path = self.base_path / agent_id / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file already exists
        if full_path.exists():
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "File already exists"}
            }
        
        # Write file
        with open(full_path, 'w') as f:
            f.write(content)
        
        # Update version history
        file_key = f"{agent_id}/{file_path}"
        self.version_history[file_key] = [{
            "version": 1,
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "action": "created",
            "size": len(content)
        }]
        
        # Update agent stats
        self.agents[agent_id]["files_created"] += 1
        self.agents[agent_id]["last_activity"] = datetime.now().isoformat()
        
        logger.info(f"File created: {file_path} by {agent_id}")
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "file_path": file_path,
                "full_path": str(full_path),
                "size": len(content),
                "created_by": agent_id,
                "version": 1,
                "status": "created"
            }
        }

    async def read_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file"""
        agent_id = params.get("agent_id")
        file_path = params.get("file_path")
        
        if not agent_id or not file_path:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "agent_id and file_path are required"}
            }
        
        full_path = self.base_path / agent_id / file_path
        
        if not full_path.exists():
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "File not found"}
            }
        
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            
            file_stats = full_path.stat()
            
            return {
                "jsonrpc": "2.0",
                "result": {
                    "file_path": file_path,
                    "content": content,
                    "size": file_stats.st_size,
                    "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                    "read_by": agent_id
                }
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Error reading file: {e}"}
            }

    async def update_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing file"""
        agent_id = params.get("agent_id")
        file_path = params.get("file_path")
        content = params.get("content", "")
        
        if not agent_id or not file_path:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "agent_id and file_path are required"}
            }
        
        full_path = self.base_path / agent_id / file_path
        
        if not full_path.exists():
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "File not found"}
            }
        
        # Check if file is locked by another agent
        file_key = f"{agent_id}/{file_path}"
        if file_key in self.file_locks and self.file_locks[file_key] != agent_id:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"File locked by {self.file_locks[file_key]}"}
            }
        
        # Update file
        with open(full_path, 'w') as f:
            f.write(content)
        
        # Update version history
        if file_key not in self.version_history:
            self.version_history[file_key] = []
        
        version = len(self.version_history[file_key]) + 1
        self.version_history[file_key].append({
            "version": version,
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "action": "updated",
            "size": len(content)
        })
        
        # Update agent stats
        self.agents[agent_id]["files_modified"] += 1
        self.agents[agent_id]["last_activity"] = datetime.now().isoformat()
        
        logger.info(f"File updated: {file_path} by {agent_id} (v{version})")
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "file_path": file_path,
                "size": len(content),
                "updated_by": agent_id,
                "version": version,
                "status": "updated"
            }
        }

    async def list_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List files in agent workspace"""
        agent_id = params.get("agent_id")
        pattern = params.get("pattern", "*")
        
        if not agent_id:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "agent_id is required"}
            }
        
        agent_path = self.base_path / agent_id
        if not agent_path.exists():
            return {
                "jsonrpc": "2.0",
                "result": {"files": [], "count": 0}
            }
        
        files = []
        for file_path in agent_path.rglob(pattern):
            if file_path.is_file():
                relative_path = file_path.relative_to(agent_path)
                file_stats = file_path.stat()
                files.append({
                    "path": str(relative_path),
                    "size": file_stats.st_size,
                    "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                })
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "agent_id": agent_id,
                "files": files,
                "count": len(files)
            }
        }

    async def lock_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lock a file for exclusive access"""
        agent_id = params.get("agent_id")
        file_path = params.get("file_path")
        
        file_key = f"{agent_id}/{file_path}"
        
        if file_key in self.file_locks:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"File already locked by {self.file_locks[file_key]}"}
            }
        
        self.file_locks[file_key] = agent_id
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "file_path": file_path,
                "locked_by": agent_id,
                "status": "locked"
            }
        }

    async def unlock_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Unlock a file"""
        agent_id = params.get("agent_id")
        file_path = params.get("file_path")
        
        file_key = f"{agent_id}/{file_path}"
        
        if file_key not in self.file_locks:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "File is not locked"}
            }
        
        if self.file_locks[file_key] != agent_id:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "File locked by different agent"}
            }
        
        del self.file_locks[file_key]
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "file_path": file_path,
                "unlocked_by": agent_id,
                "status": "unlocked"
            }
        }

    async def get_file_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get version history for a file"""
        agent_id = params.get("agent_id")
        file_path = params.get("file_path")
        
        file_key = f"{agent_id}/{file_path}"
        history = self.version_history.get(file_key, [])
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "file_path": file_path,
                "history": history,
                "versions": len(history)
            }
        }

    async def start_collaboration(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start a collaboration session"""
        session_id = params.get("session_id")
        agents = params.get("agents", [])
        file_path = params.get("file_path")
        
        if not session_id or not agents:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "session_id and agents are required"}
            }
        
        self.collaboration_sessions[session_id] = {
            "id": session_id,
            "agents": agents,
            "file_path": file_path,
            "started_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "session_id": session_id,
                "agents": agents,
                "status": "started"
            }
        }

    async def end_collaboration(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """End a collaboration session"""
        session_id = params.get("session_id")
        
        if session_id not in self.collaboration_sessions:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "Session not found"}
            }
        
        session = self.collaboration_sessions[session_id]
        session["status"] = "ended"
        session["ended_at"] = datetime.now().isoformat()
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "session_id": session_id,
                "status": "ended"
            }
        }

async def handle_client(websocket: WebSocketServerProtocol, path: str):
    """Handle WebSocket connections"""
    server = AgentFileServer()
    logger.info(f"New Agent File client connected: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            await server.handle_message(websocket, message)
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Agent File client disconnected: {websocket.remote_address}")
    except Exception as e:
        logger.error(f"Error with Agent File client {websocket.remote_address}: {e}")

async def main():
    """Start the Agent File System MCP server"""
    server = await websockets.serve(handle_client, "localhost", 8012)
    logger.info("Agent File System MCP Server started on ws://localhost:8012")
    
    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        logger.info("Agent File server shutting down...")
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
