#!/usr/bin/env python3
"""
VOTS Payment MCP Server
Agent-to-Agent payment system for the VOTS ecosystem
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime
import hashlib

# Web3 imports for Base network interaction
from web3 import Web3
from eth_account import Account

# MCP imports
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vots-payment-mcp")

class VOTSPaymentClient:
    """Client for interacting with VOTS payment contracts on Base"""

    def __init__(self, rpc_url: str = "https://mainnet.base.org", private_key: Optional[str] = None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = None
        if private_key:
            self.account = Account.from_key(private_key)

        # Contract addresses (to be deployed)
        self.vots_token_address = os.getenv("VOTS_TOKEN_ADDRESS", "0x0000000000000000000000000000000000000000")
        self.payment_processor_address = os.getenv("VOTS_PAYMENT_PROCESSOR_ADDRESS", "0x0000000000000000000000000000000000000000")

        # Basic ABIs for interaction
        self.vots_token_abi = [
            {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
            {"constant": False, "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
        ]

        self.payment_processor_abi = [
            {"constant": False, "inputs": [{"name": "toAgent", "type": "address"}, {"name": "amount", "type": "uint256"}, {"name": "transactionType", "type": "string"}, {"name": "memo", "type": "string"}], "name": "makeA2APayment", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "agent", "type": "address"}], "name": "getAgentProfile", "outputs": [{"components": [{"name": "agentAddress", "type": "address"}, {"name": "name", "type": "string"}, {"name": "serviceType", "type": "string"}, {"name": "reputation", "type": "uint256"}, {"name": "totalTransactions", "type": "uint256"}, {"name": "totalVolume", "type": "uint256"}, {"name": "totalFeesPaid", "type": "uint256"}, {"name": "totalRewardsEarned", "type": "uint256"}, {"name": "isActive", "type": "bool"}, {"name": "registrationTime", "type": "uint256"}, {"name": "lastActivity", "type": "uint256"}], "name": "", "type": "tuple"}], "type": "function"},
            {"constant": False, "inputs": [{"name": "name", "type": "string"}, {"name": "serviceType", "type": "string"}], "name": "registerAgent", "outputs": [], "type": "function"}
        ]

    def is_connected(self) -> bool:
        """Check if connected to Base network"""
        return self.w3.is_connected()

    def get_balance(self, address: str) -> float:
        """Get VOTS balance for an address"""
        if not self.is_connected():
            return 0.0

        try:
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.vots_token_address),
                abi=self.vots_token_abi
            )
            balance_wei = contract.functions.balanceOf(Web3.to_checksum_address(address)).call()
            return balance_wei / 10**18  # Assuming 18 decimals
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0.0

    def register_agent(self, name: str, service_type: str) -> str:
        """Register as an agent in the VOTS ecosystem"""
        if not self.account or not self.is_connected():
            return "Error: Not connected or no account configured"

        try:
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.payment_processor_address),
                abi=self.payment_processor_abi
            )

            # Build transaction
            txn = contract.functions.registerAgent(name, service_type).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(txn, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)

            return f"Agent registration transaction sent: {tx_hash.hex()}"
        except Exception as e:
            logger.error(f"Error registering agent: {e}")
            return f"Error registering agent: {str(e)}"

    def make_payment(self, to_agent: str, amount_vots: float, transaction_type: str = "service", memo: str = "") -> str:
        """Make an agent-to-agent payment"""
        if not self.account or not self.is_connected():
            return "Error: Not connected or no account configured"

        try:
            # Convert amount to wei (assuming 18 decimals)
            amount_wei = int(amount_vots * 10**18)

            # First approve the payment processor to spend VOTS
            token_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.vots_token_address),
                abi=self.vots_token_abi
            )

            approve_txn = token_contract.functions.approve(
                Web3.to_checksum_address(self.payment_processor_address),
                amount_wei
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })

            signed_approve = self.w3.eth.account.sign_transaction(approve_txn, self.account.key)
            approve_hash = self.w3.eth.send_raw_transaction(signed_approve.raw_transaction)

            # Wait for approval
            self.w3.eth.wait_for_transaction_receipt(approve_hash)

            # Now make the payment
            processor_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.payment_processor_address),
                abi=self.payment_processor_abi
            )

            payment_txn = processor_contract.functions.makeA2APayment(
                Web3.to_checksum_address(to_agent),
                amount_wei,
                transaction_type,
                memo
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price
            })

            signed_payment = self.w3.eth.account.sign_transaction(payment_txn, self.account.key)
            payment_hash = self.w3.eth.send_raw_transaction(signed_payment.raw_transaction)

            return f"VOTS payment transaction sent: {payment_hash.hex()}"
        except Exception as e:
            logger.error(f"Error making payment: {e}")
            return f"Error making payment: {str(e)}"

    def get_agent_profile(self, agent_address: str) -> Dict[str, Any]:
        """Get agent profile information"""
        if not self.is_connected():
            return {"error": "Not connected to network"}

        try:
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.payment_processor_address),
                abi=self.payment_processor_abi
            )

            profile = contract.functions.getAgentProfile(Web3.to_checksum_address(agent_address)).call()

            return {
                "agentAddress": profile[0],
                "name": profile[1],
                "serviceType": profile[2],
                "reputation": profile[3],
                "totalTransactions": profile[4],
                "totalVolume": profile[5] / 10**18,  # Convert from wei
                "totalFeesPaid": profile[6] / 10**18,
                "totalRewardsEarned": profile[7] / 10**18,
                "isActive": profile[8],
                "registrationTime": profile[9],
                "lastActivity": profile[10]
            }
        except Exception as e:
            logger.error(f"Error getting agent profile: {e}")
            return {"error": str(e)}

# Global VOTS client instance
vots_client = None

def get_vots_client() -> VOTSPaymentClient:
    """Get or create VOTS payment client instance"""
    global vots_client
    if vots_client is None:
        rpc_url = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
        private_key = os.getenv("AGENT_PRIVATE_KEY")  # Only set for payment-making agents
        vots_client = VOTSPaymentClient(rpc_url, private_key)
    return vots_client

# MCP Server setup
server = FastMCP("vots-payment-mcp", instructions="VOTS agent-to-agent payment system for the Base network ecosystem")

@server.tool()
async def check_vots_balance(agent_address: str) -> str:
    """Check VOTS token balance for an agent"""
    try:
        client = get_vots_client()
        balance = client.get_balance(agent_address)
        return f"VOTS Balance for {agent_address}: {balance:.4f} VOTS"
    except Exception as e:
        logger.error(f"Error checking balance: {e}")
        return f"Error checking balance: {str(e)}"

@server.tool()
async def register_agent(name: str, service_type: str) -> str:
    """Register as an agent in the VOTS ecosystem"""
    try:
        client = get_vots_client()
        result = client.register_agent(name, service_type)
        return result
    except Exception as e:
        logger.error(f"Error registering agent: {e}")
        return f"Error registering agent: {str(e)}"

@server.tool()
async def make_vots_payment(to_agent: str, amount_vots: float, transaction_type: str = "service", memo: str = "") -> str:
    """Make an agent-to-agent payment with VOTS tokens"""
    try:
        client = get_vots_client()
        result = client.make_payment(to_agent, amount_vots, transaction_type, memo)
        return result
    except Exception as e:
        logger.error(f"Error making payment: {e}")
        return f"Error making payment: {str(e)}"

@server.tool()
async def get_agent_profile(agent_address: str) -> str:
    """Get detailed profile information for an agent"""
    try:
        client = get_vots_client()
        profile = client.get_agent_profile(agent_address)

        if "error" in profile:
            return f"Error getting profile: {profile['error']}"

        response = f"Agent Profile for {agent_address}:\n"
        response += f"Name: {profile['name']}\n"
        response += f"Service Type: {profile['serviceType']}\n"
        response += f"Reputation: {profile['reputation']}/1000\n"
        response += f"Total Transactions: {profile['totalTransactions']}\n"
        response += f"Total Volume: {profile['totalVolume']:.4f} VOTS\n"
        response += f"Total Fees Paid: {profile['totalFeesPaid']:.4f} VOTS\n"
        response += f"Total Rewards Earned: {profile['totalRewardsEarned']:.4f} VOTS\n"
        response += f"Active: {'Yes' if profile['isActive'] else 'No'}\n"
        response += f"Registration Time: {datetime.fromtimestamp(profile['registrationTime']).isoformat()}\n"
        response += f"Last Activity: {datetime.fromtimestamp(profile['lastActivity']).isoformat()}\n"

        return response
    except Exception as e:
        logger.error(f"Error getting agent profile: {e}")
        return f"Error getting agent profile: {str(e)}"

@server.tool()
async def calculate_payment_fee(amount_vots: float) -> str:
    """Calculate the fee for a VOTS payment (0.01%)"""
    fee = amount_vots * 0.0001  # 0.01% = 0.0001
    total = amount_vots + fee

    response = f"VOTS Payment Calculation for {amount_vots:.4f} VOTS:\n"
    response += f"Fee (0.01%): {fee:.6f} VOTS\n"
    response += f"Total Amount: {total:.4f} VOTS\n"
    response += f"Fee Distribution:\n"
    response += f"  • Ecosystem Treasury: {fee * 0.6:.6f} VOTS (60%)\n"
    response += f"  • Receiving Agent: {fee * 0.3:.6f} VOTS (30%)\n"
    response += f"  • Burned: {fee * 0.1:.6f} VOTS (10%)\n"

    return response

@server.tool()
async def get_vots_network_status() -> str:
    """Get VOTS network and contract status"""
    try:
        client = get_vots_client()
        connected = client.is_connected()

        response = f"VOTS Network Status:\n"
        response += f"Connected to Base Network: {'Yes' if connected else 'No'}\n"

        if connected:
            response += f"VOTS Token Contract: {client.vots_token_address}\n"
            response += f"Payment Processor: {client.payment_processor_address}\n"

            if client.account:
                balance = client.get_balance(client.account.address)
                response += f"Agent Balance: {balance:.4f} VOTS\n"
                response += f"Agent Address: {client.account.address}\n"
            else:
                response += "Agent: Not configured (read-only mode)\n"
        else:
            response += "Network connection failed\n"

        return response
    except Exception as e:
        logger.error(f"Error getting network status: {e}")
        return f"Error getting network status: {str(e)}"

@server.tool()
async def discover_agents(service_type: str = "", min_reputation: int = 100) -> str:
    """Discover available agents in the VOTS ecosystem"""
    # This would integrate with the MCP memory system to find agents
    # For now, return a placeholder response
    response = f"Discovering agents"
    if service_type:
        response += f" with service type: {service_type}"
    response += f" and minimum reputation: {min_reputation}\n\n"

    response += "Note: Agent discovery requires integration with MCP memory system.\n"
    response += "Available service types: trading, analysis, data, computation, storage, etc.\n"
    response += "Use get_agent_profile() to check specific agent details.\n"

    return response

async def main():
    """Main MCP server entry point"""
    try:
        logger.info("Starting VOTS Payment MCP Server")
        await server.run_stdio_async()
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
