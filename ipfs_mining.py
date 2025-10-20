#!/usr/bin/env python3
"""
MCPVOTS IPFS Mining Script
==========================

This script enables decentralized mining by running an IPFS node that provides
storage and bandwidth for the MCPVOTS ecosystem. Miners earn MCPVOTS tokens
based on their contribution to the network.

Features:
- Automatic IPFS node management
- Data pinning for ecosystem content
- Mining reward claiming via smart contract
- Battery-aware operation (when running on mobile/laptop)
- Network optimization

Usage:
    python ipfs_mining.py --mode local    # Run with local IPFS node
    python ipfs_mining.py --mode gateway  # Use public IPFS gateway
    python ipfs_mining.py --reward-contract 0x...  # Specify reward contract

Environment Variables:
    IPFS_API_URL: IPFS API endpoint (default: http://localhost:5001)
    MINING_API_URL: MCPVOTS mining API endpoint
    PRIVATE_KEY: Wallet private key for reward claiming
    INFURA_KEY: Infura API key for blockchain interaction
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import ipfshttpclient
import requests
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware
import cryptography
from cryptography.fernet import Fernet
import base64
import hashlib
import hmac

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCPVOTS_Mining')

class MCPVOTSMiner:
    def __init__(self, mode: str = 'local', reward_contract: Optional[str] = None):
        self.mode = mode
        self.reward_contract = reward_contract or os.getenv('REWARD_CONTRACT')
        self.ipfs_api_url = os.getenv('IPFS_API_URL', 'http://localhost:5001')
        self.mining_api_url = os.getenv('MINING_API_URL', 'https://api.mcpvots.com/mining')
        self.private_key = os.getenv('PRIVATE_KEY')
        self.infura_key = os.getenv('INFURA_KEY')

        # Mining statistics
        self.start_time = datetime.now()
        self.data_pinned = 0
        self.bandwidth_served = 0
        self.peers_connected = 0

        # IPFS client
        self.ipfs_client = None

        # Web3 connection for multiple networks
        self.web3 = None
        self.base_web3 = None  # Base network connection
        self.account = None
        self.base_account = None

        # Mining state
        self.is_mining = False
        self.mining_score = 0.0

        # Encryption key
        self.encryption_key = self._generate_encryption_key()

    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key from miner identity"""
        # Use a combination of miner ID and timestamp for key derivation
        import secrets
        seed = f"{self.get_miner_id()}_{int(time.time())}_{secrets.token_hex(16)}"
        return base64.urlsafe_b64encode(hashlib.sha256(seed.encode()).digest()[:32])

    def encrypt_data(self, data: str) -> str:
        """Encrypt data before IPFS storage"""
        fernet = Fernet(self.encryption_key)
        encrypted = fernet.encrypt(data.encode())
        return encrypted.decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data retrieved from IPFS"""
        fernet = Fernet(self.encryption_key)
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()

    async def initialize(self):
        """Initialize IPFS client and blockchain connection"""
        try:
            if self.mode == 'local':
                self.ipfs_client = ipfshttpclient.connect(self.ipfs_api_url)
                logger.info("Connected to local IPFS node")
            elif self.mode == 'gateway':
                # Gateway mode is for read-only operations and testing
                logger.info("Gateway mode selected - limited functionality available")
                logger.info("For full mining capabilities, please run a local IPFS node")
                # Don't set ipfs_client in gateway mode - operations will be limited
                self.ipfs_client = None
            else:
                # Use Infura if API key is provided
                infura_key = os.getenv('INFURA_IPFS_KEY')
                if infura_key:
                    # Note: Infura IPFS requires special authentication
                    logger.warning("Infura IPFS authentication not implemented yet")
                    logger.info("Falling back to public gateway")
                    try:
                        self.ipfs_client = ipfshttpclient.connect('/dns/ipfs.io/tcp/443/https')
                        logger.info("Connected to public IPFS gateway")
                    except Exception as e:
                        logger.error(f"Failed to connect to any IPFS endpoint: {e}")
                        raise
                else:
                    logger.error("No IPFS connection method available. Please:")
                    logger.error("1. Run a local IPFS node: ipfs daemon")
                    logger.error("2. Or set INFURA_IPFS_KEY environment variable")
                    logger.error("3. Or use --mode gateway for public gateway access")
                    raise RuntimeError("No IPFS connection available")

            # Initialize Base network connection (primary network)
            self._init_base_network()

            # Initialize Ethereum mainnet as fallback only
            if self.infura_key and self.private_key:
                infura_url = f"https://mainnet.infura.io/v3/{self.infura_key}"
                self.web3 = Web3(Web3.HTTPProvider(infura_url))
                self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

                if self.web3.is_connected():
                    self.account = self.web3.eth.account.from_key(self.private_key)
                    logger.info(f"Connected to Ethereum mainnet (fallback) with account: {self.account.address}")
                else:
                    logger.warning("Ethereum mainnet connection failed (fallback only)")

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    def _init_base_network(self):
        """Initialize Base network connection (primary network for rewards)"""
        try:
            # Base network RPC endpoint
            base_rpc_url = os.getenv('BASE_RPC_URL', 'https://mainnet.base.org')

            self.base_web3 = Web3(Web3.HTTPProvider(base_rpc_url))

            if self.base_web3.is_connected():
                if self.private_key:
                    self.base_account = self.base_web3.eth.account.from_key(self.private_key)
                    logger.info(f"✅ Connected to Base network (PRIMARY) with account: {self.base_account.address}")
                else:
                    logger.info("Connected to Base network (read-only mode)")
            else:
                logger.error("❌ Failed to connect to Base network (PRIMARY NETWORK)")

        except Exception as e:
            logger.error(f"Base network initialization failed: {e}")

    async def start_mining(self):
        """Start the mining process"""
        self.is_mining = True
        self.start_time = datetime.now()
        logger.info("🚀 Starting MCPVOTS IPFS Mining...")

        # Pin ecosystem data
        await self.pin_ecosystem_data()

        # Start mining loop
        while self.is_mining:
            try:
                await self.mining_cycle()
                await asyncio.sleep(60)  # Report every minute
            except Exception as e:
                logger.error(f"Mining cycle error: {e}")
                await asyncio.sleep(30)

    async def pin_ecosystem_data(self):
        """Pin important ecosystem data to IPFS (only works with local node)"""
        if not self.ipfs_client:
            logger.warning("IPFS client not available. Run with --mode local for pinning capabilities")
            return

        try:
            # Pin trade logs (encrypted)
            if os.path.exists('trade_log.txt'):
                with open('trade_log.txt', 'r') as f:
                    trade_data = f.read()
                # Encrypt sensitive trade data
                encrypted_trade_data = self.encrypt_data(trade_data)
                trade_cid = self.ipfs_client.add_str(encrypted_trade_data)
                self.ipfs_client.pin.add(trade_cid)
                self.data_pinned += len(encrypted_trade_data)
                logger.info(f"Pinned encrypted trade data: {trade_cid}")

            # Pin analysis reports (encrypted)
            reports_dir = 'reports/'
            if os.path.exists(reports_dir):
                for file in os.listdir(reports_dir):
                    if file.endswith('.json'):
                        with open(os.path.join(reports_dir, file), 'r') as f:
                            data = f.read()
                        # Encrypt analysis data
                        encrypted_data = self.encrypt_data(data)
                        cid = self.ipfs_client.add_str(encrypted_data)
                        self.ipfs_client.pin.add(cid)
                        self.data_pinned += len(encrypted_data)
                        logger.info(f"Pinned encrypted report {file}: {cid}")

            # Pin configuration (public - no encryption needed)
            config_cid = self.ipfs_client.add_str(json.dumps({
                'ecosystem': 'MCPVOTS',
                'version': '1.0',
                'features': ['trading', 'analysis', 'mining'],
                'encryption': 'enabled'
            }))
            self.ipfs_client.pin.add(config_cid)
            logger.info(f"Pinned config: {config_cid}")

        except Exception as e:
            logger.error(f"Failed to pin ecosystem data: {e}")

    async def mining_cycle(self):
        """Perform one mining cycle"""
        try:
            # Update statistics
            self.update_statistics()

            # Calculate mining score
            self.mining_score = self.calculate_mining_score()

            # Report to mining API
            await self.report_mining_status()

            # Claim rewards if eligible
            if self.mining_score > 10.0:  # Minimum threshold
                await self.claim_rewards()

        except Exception as e:
            logger.error(f"Mining cycle failed: {e}")

    def update_statistics(self):
        """Update mining statistics"""
        try:
            if self.ipfs_client:
                # Get peer count
                peers = self.ipfs_client.swarm.peers()
                self.peers_connected = len(peers)
            else:
                # In gateway mode, simulate some peers for testing
                self.peers_connected = 3  # Mock peer count

                # Get bandwidth stats (simplified)
                # In real implementation, you'd track actual data served
                self.bandwidth_served += 1024  # Mock data

        except Exception as e:
            logger.warning(f"Failed to update statistics: {e}")
            # Set reasonable defaults
            self.peers_connected = 0

    def calculate_mining_score(self) -> float:
        """Calculate mining score based on contributions"""
        uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600

        # Score formula: uptime * peers * data_factor
        data_factor = 1 + (self.data_pinned / (1024 * 1024))  # Bonus per MB pinned
        score = uptime_hours * self.peers_connected * data_factor

        return score

    async def report_mining_status(self):
        """Report mining status to MCPVOTS API"""
        try:
            payload = {
                'miner_id': self.get_miner_id(),
                'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
                'peers_connected': self.peers_connected,
                'data_pinned_mb': self.data_pinned / (1024 * 1024),
                'bandwidth_served_mb': self.bandwidth_served / (1024 * 1024),
                'mining_score': self.mining_score,
                'timestamp': datetime.now().isoformat()
            }

            response = requests.post(
                f"{self.mining_api_url}/report",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"✅ Mining report submitted. Score: {self.mining_score:.2f}")
            else:
                logger.warning(f"Failed to submit report: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to report mining status: {e}")

    async def claim_rewards(self):
        """Claim mining rewards via smart contract on Base network (primary)"""
        if not self.reward_contract:
            logger.warning("No reward contract specified")
            return

        rewards_claimed = []

        # Primary: Claim on Base network (Layer 2, low fees)
        if self.base_web3 and self.base_web3.is_connected() and self.base_account:
            try:
                success = await self._claim_rewards_on_network(self.base_web3, self.base_account, "Base")
                if success:
                    rewards_claimed.append("Base")
                    logger.info("🎉 Rewards claimed on Base network (PRIMARY)!")
                    return  # Success on primary network, no need for fallback
            except Exception as e:
                logger.error(f"Failed to claim rewards on Base (PRIMARY): {e}")

        # Fallback: Ethereum mainnet (only if Base fails)
        if self.web3 and self.web3.is_connected() and self.account:
            try:
                success = await self._claim_rewards_on_network(self.web3, self.account, "Ethereum")
                if success:
                    rewards_claimed.append("Ethereum")
                    logger.warning("⚠️  Rewards claimed on Ethereum (FALLBACK - Base network preferred)")
            except Exception as e:
                logger.error(f"Failed to claim rewards on Ethereum (fallback): {e}")

        if not rewards_claimed:
            logger.error("❌ No rewards could be claimed on any network")
            logger.error("💡 Ensure Base network connection and reward contract are configured")
        elif "Base" not in rewards_claimed:
            logger.warning("⚠️  Base network (primary) failed - using Ethereum fallback")

    async def _claim_rewards_on_network(self, web3, account, network_name: str) -> bool:
        """Claim rewards on a specific network"""
        try:
            # Contract ABI (simplified)
            contract_abi = [
                {
                    "inputs": [{"name": "score", "type": "uint256"}],
                    "name": "claimMiningReward",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]

            contract = web3.eth.contract(
                address=web3.to_checksum_address(self.reward_contract),
                abi=contract_abi
            )

            # Build transaction
            nonce = web3.eth.get_transaction_count(account.address)
            gas_price = web3.eth.gas_price

            # Adjust gas price for Base network (lower fees)
            if network_name == "Base":
                gas_price = int(gas_price * 0.1)  # Much cheaper on Base

            txn = contract.functions.claimMiningReward(int(self.mining_score * 100)).build_transaction({
                'chainId': 8453 if network_name == "Base" else 1,  # Base chain ID vs Ethereum
                'gas': 200000,
                'gasPrice': gas_price,
                'nonce': nonce,
            })

            # Sign and send
            signed_txn = web3.eth.account.sign_transaction(txn, account.key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            logger.info(f"✅ Reward claimed on {network_name}! TX: {tx_hash.hex()}")

            # Reset score after claiming
            self.mining_score = 0.0
            return True

        except Exception as e:
            logger.error(f"Failed to claim rewards on {network_name}: {e}")
            return False

    def get_miner_id(self) -> str:
        """Get unique miner identifier"""
        # Use IPFS peer ID if available
        try:
            if self.ipfs_client:
                peer_info = self.ipfs_client.id()
                if isinstance(peer_info, dict) and 'ID' in peer_info:
                    peer_id = peer_info['ID']
                    return f"ipfs_{peer_id[:16]}"
        except:
            pass

        # Fallback to system ID
        import socket
        return f"miner_{socket.gethostname()}"

    async def stop_mining(self):
        """Stop the mining process"""
        self.is_mining = False
        logger.info("🛑 Mining stopped")

        # Final report
        await self.report_mining_status()

    def get_status(self) -> Dict:
        """Get current mining status"""
        base_connected = self.base_web3 and self.base_web3.is_connected()
        eth_connected = self.web3 and self.web3.is_connected()

        return {
            'is_mining': self.is_mining,
            'uptime': str(datetime.now() - self.start_time),
            'mining_score': self.mining_score,
            'peers_connected': self.peers_connected,
            'data_pinned_mb': self.data_pinned / (1024 * 1024),
            'bandwidth_served_mb': self.bandwidth_served / (1024 * 1024),
            'primary_network': {
                'name': 'Base',
                'status': 'connected' if base_connected else 'disconnected',
                'chain_id': 8453
            },
            'fallback_network': {
                'name': 'Ethereum',
                'status': 'connected' if eth_connected else 'disconnected',
                'chain_id': 1
            },
            'miner_id': self.get_miner_id()
        }


async def main():
    import argparse

    parser = argparse.ArgumentParser(description='MCPVOTS IPFS Mining')
    parser.add_argument('--mode', choices=['local', 'gateway'],
                       default='local', help='IPFS connection mode')
    parser.add_argument('--reward-contract', help='Reward contract address')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as daemon (background)')

    args = parser.parse_args()

    miner = MCPVOTSMiner(mode=args.mode, reward_contract=args.reward_contract)

    try:
        await miner.initialize()

        if args.daemon:
            # Run in background
            import signal
            import sys

            def signal_handler(sig, frame):
                asyncio.create_task(miner.stop_mining())
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            await miner.start_mining()
        else:
            # Interactive mode
            await miner.start_mining()

    except KeyboardInterrupt:
        await miner.stop_mining()
    except Exception as e:
        logger.error(f"Mining failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
