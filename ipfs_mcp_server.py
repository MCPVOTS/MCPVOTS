#!/usr/bin/env python3
"""
MCPVOTS IPFS Mining MCP Server
Enables AI agents to interact with IPFS mining operations
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

# MCP imports
from mcp.server.fastmcp import FastMCP

# Import our IPFS miner
from ipfs_mining import MCPVOTSMiner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ipfs-mcp-server")

class IPFSMiningMCPServer:
    """MCP Server for IPFS Mining Operations"""

    def __init__(self):
        self.miner: Optional[MCPVOTSMiner] = None
        self.server = FastMCP("MCPVOTS IPFS Mining Server")

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register MCP tools for IPFS operations"""

        @self.server.tool()
        async def initialize_miner(mode: str = "local", reward_contract: Optional[str] = None) -> str:
            """Initialize the IPFS miner with specified configuration"""
            try:
                self.miner = MCPVOTSMiner(mode=mode, reward_contract=reward_contract)
                await self.miner.initialize()
                return f"✅ IPFS Miner initialized in {mode} mode"
            except Exception as e:
                logger.error(f"Failed to initialize miner: {e}")
                return f"❌ Failed to initialize miner: {str(e)}"

        @self.server.tool()
        async def start_mining() -> str:
            """Start IPFS mining operations"""
            if not self.miner:
                return "❌ Miner not initialized. Call initialize_miner first."

            try:
                # Start mining in background
                asyncio.create_task(self.miner.start_mining())
                return "✅ IPFS Mining started successfully"
            except Exception as e:
                logger.error(f"Failed to start mining: {e}")
                return f"❌ Failed to start mining: {str(e)}"

        @self.server.tool()
        async def stop_mining() -> str:
            """Stop IPFS mining operations"""
            if not self.miner:
                return "❌ Miner not initialized."

            try:
                await self.miner.stop_mining()
                return "🛑 IPFS Mining stopped successfully"
            except Exception as e:
                logger.error(f"Failed to stop mining: {e}")
                return f"❌ Failed to stop mining: {str(e)}"

        @self.server.tool()
        async def get_mining_status() -> str:
            """Get current mining status and statistics"""
            if not self.miner:
                return "❌ Miner not initialized."

            try:
                status = self.miner.get_status()
                return json.dumps(status, indent=2)
            except Exception as e:
                logger.error(f"Failed to get mining status: {e}")
                return f"❌ Failed to get status: {str(e)}"

        @self.server.tool()
        async def pin_content(content: str, encrypt: bool = True) -> str:
            """Pin content to IPFS with optional encryption"""
            if not self.miner:
                return "❌ Miner not initialized."

            try:
                if encrypt:
                    encrypted_content = self.miner.encrypt_data(content)
                    cid = self.miner.ipfs_client.add_str(encrypted_content)
                else:
                    cid = self.miner.ipfs_client.add_str(content)

                self.miner.ipfs_client.pin.add(cid)
                self.miner.data_pinned += len(content)

                return f"✅ Content pinned successfully. CID: {cid}"
            except Exception as e:
                logger.error(f"Failed to pin content: {e}")
                return f"❌ Failed to pin content: {str(e)}"

        @self.server.tool()
        async def unpin_content(cid: str) -> str:
            """Unpin content from IPFS"""
            if not self.miner:
                return "❌ Miner not initialized."

            try:
                self.miner.ipfs_client.pin.rm(cid)
                return f"✅ Content unpinned successfully: {cid}"
            except Exception as e:
                logger.error(f"Failed to unpin content: {e}")
                return f"❌ Failed to unpin content: {str(e)}"

        @self.server.tool()
        async def get_content(cid: str, decrypt: bool = True) -> str:
            """Retrieve content from IPFS with optional decryption"""
            if not self.miner:
                return "❌ Miner not initialized."

            try:
                content = self.miner.ipfs_client.cat(cid).decode('utf-8')

                if decrypt:
                    content = self.miner.decrypt_data(content)

                return f"📄 Retrieved content from {cid}:\n{content}"
            except Exception as e:
                logger.error(f"Failed to get content: {e}")
                return f"❌ Failed to retrieve content: {str(e)}"

        @self.server.tool()
        async def list_pinned_content() -> str:
            """List all pinned content on the IPFS node"""
            if not self.miner:
                return "❌ Miner not initialized."

            try:
                pinned = self.miner.ipfs_client.pin.ls()
                result = "📌 Pinned Content:\n"

                for item in pinned:
                    result += f"- {item['Hash']}\n"

                return result
            except Exception as e:
                logger.error(f"Failed to list pinned content: {e}")
                return f"❌ Failed to list pinned content: {str(e)}"

        @self.server.tool()
        async def claim_rewards() -> str:
            """Claim mining rewards via smart contract"""
            if not self.miner:
                return "❌ Miner not initialized."

            try:
                await self.miner.claim_rewards()
                return "🎉 Rewards claimed successfully!"
            except Exception as e:
                logger.error(f"Failed to claim rewards: {e}")
                return f"❌ Failed to claim rewards: {str(e)}"

        @self.server.tool()
        async def get_network_info() -> str:
            """Get IPFS network information and peer count"""
            if not self.miner:
                return "❌ Miner not initialized."

            try:
                info = self.miner.ipfs_client.id()
                peers = len(self.miner.ipfs_client.swarm.peers())

                result = f"""🌐 IPFS Network Info:
Peer ID: {info['ID']}
Public Key: {info.get('PublicKey', 'N/A')}
Agent Version: {info.get('AgentVersion', 'N/A')}
Protocol Version: {info.get('ProtocolVersion', 'N/A')}
Addresses: {', '.join(info.get('Addresses', []))}
Connected Peers: {peers}
"""

                return result
            except Exception as e:
                logger.error(f"Failed to get network info: {e}")
                return f"❌ Failed to get network info: {str(e)}"

        @self.server.tool()
        async def pin_ecosystem_data() -> str:
            """Pin important ecosystem data to IPFS"""
            if not self.miner:
                return "❌ Miner not initialized."

            try:
                await self.miner.pin_ecosystem_data()
                return "✅ Ecosystem data pinned successfully"
            except Exception as e:
                logger.error(f"Failed to pin ecosystem data: {e}")
                return f"❌ Failed to pin ecosystem data: {str(e)}"

    async def run(self):
        """Run the MCP server"""
        logger.info("🚀 Starting MCPVOTS IPFS Mining MCP Server...")
        await self.server.run()
        logger.info("🛑 MCPVOTS IPFS Mining MCP Server stopped")


async def main():
    """Main entry point"""
    server = IPFSMiningMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
