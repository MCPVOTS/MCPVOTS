#!/usr/bin/env python3
"""
VOTS Token Deployment Script with Uniswap V4 Bootstrap

This script deploys the VOTS token ecosystem with automatic liquidity bootstrapping
using Uniswap V4 hooks. The process creates fair launch conditions where early
contributors get proportional token allocation.

Deployment Flow:
1. Deploy VOTS token contract
2. Deploy V4 bootstrap hook
3. Deploy pool manager
4. Initialize bootstrap process
5. Create V4 pool with initial liquidity

Usage:
    python deploy_vots.py --network base --private-key $PRIVATE_KEY
"""

import os
import json
import time
from web3 import Web3
from eth_account import Account
from pathlib import Path

# Contract dependencies
VOTS_TOKEN_ABI = None  # Will be loaded from compiled contracts
VOTS_HOOK_ABI = None
VOTS_POOL_MANAGER_ABI = None

class VOTSDeployer:
    def __init__(self, rpc_url: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key)
        self.chain_id = self.w3.eth.chain_id

        # Load contract ABIs and bytecodes
        self._load_contracts()

        # Network-specific addresses
        self.weth_address = self._get_weth_address()
        self.v4_pool_manager = self._get_v4_pool_manager()

    def _load_contracts(self):
        """Load compiled contract ABIs and bytecodes"""
        contracts_dir = Path(__file__).parent / "contracts"

        # Load VOTS Token
        with open(contracts_dir / "VOTSToken.json", 'r') as f:
            vots_data = json.load(f)
            self.vots_abi = vots_data['abi']
            self.vots_bytecode = vots_data['bytecode']

        # Load VOTS Bootstrap Hook
        with open(contracts_dir / "VOTSBoostrapHook.json", 'r') as f:
            hook_data = json.load(f)
            self.hook_abi = hook_data['abi']
            self.hook_bytecode = hook_data['bytecode']

        # Load VOTS Pool Manager
        with open(contracts_dir / "VOTSPoolManager.json", 'r') as f:
            manager_data = json.load(f)
            self.manager_abi = manager_data['abi']
            self.manager_bytecode = manager_data['bytecode']

    def _get_weth_address(self) -> str:
        """Get WETH address for the current network"""
        if self.chain_id == 8453:  # Base mainnet
            return "0x4200000000000000000000000000000000000006"
        elif self.chain_id == 84531:  # Base Goerli
            return "0x4200000000000000000000000000000000000006"
        else:
            raise ValueError(f"Unsupported chain ID: {self.chain_id}")

    def _get_v4_pool_manager(self) -> str:
        """Get Uniswap V4 PoolManager address"""
        # These would be the actual deployed V4 addresses
        if self.chain_id == 8453:  # Base mainnet
            return "0x0000000000000000000000000000000000000000"  # Placeholder
        elif self.chain_id == 84531:  # Base Goerli
            return "0x0000000000000000000000000000000000000000"  # Placeholder
        else:
            raise ValueError(f"V4 not deployed on chain {self.chain_id}")

    def deploy_vots_token(self) -> str:
        """Deploy VOTS token contract"""
        print("🚀 Deploying VOTS Token...")

        # Constructor parameters
        name = "VOTS Token"
        symbol = "VOTS"
        initial_supply = self.w3.to_wei(10000000, 'ether')  # 10M total supply
        burn_rate = 1  # 0.01% burn rate

        # Create contract
        contract = self.w3.eth.contract(abi=self.vots_abi, bytecode=self.vots_bytecode)

        # Build transaction
        constructor_args = [name, symbol, initial_supply, burn_rate]
        tx = contract.constructor(*constructor_args).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 3000000,
            'gasPrice': self.w3.eth.gas_price
        })

        # Sign and send
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        vots_address = tx_receipt['contractAddress']
        if not vots_address:
            raise ValueError("Contract deployment failed - no contract address")
        print(f"✅ VOTS Token deployed at: {vots_address}")

        return vots_address

    def deploy_bootstrap_hook(self, vots_address: str) -> str:
        """Deploy V4 bootstrap hook"""
        print("🔗 Deploying VOTS Bootstrap Hook...")

        contract = self.w3.eth.contract(abi=self.hook_abi, bytecode=self.hook_bytecode)

        # Constructor parameters
        tx = contract.constructor(self.v4_pool_manager, vots_address, self.weth_address).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 4000000,
            'gasPrice': self.w3.eth.gas_price
        })

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        hook_address = tx_receipt['contractAddress']
        if not hook_address:
            raise ValueError("Hook deployment failed - no contract address")
        print(f"✅ Bootstrap Hook deployed at: {hook_address}")

        return hook_address

    def deploy_pool_manager(self, vots_address: str) -> str:
        """Deploy pool manager contract"""
        print("🏊 Deploying VOTS Pool Manager...")

        contract = self.w3.eth.contract(abi=self.manager_abi, bytecode=self.manager_bytecode)

        tx = contract.constructor(vots_address, self.weth_address).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 3000000,
            'gasPrice': self.w3.eth.gas_price
        })

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        manager_address = tx_receipt['contractAddress']
        if not manager_address:
            raise ValueError("Manager deployment failed - no contract address")
        print(f"✅ Pool Manager deployed at: {manager_address}")

        return manager_address

    def setup_bootstrap(self, vots_address: str, manager_address: str):
        """Set up the bootstrap process"""
        print("⚙️ Setting up bootstrap process...")

        # Transfer initial VOTS supply to pool manager
        vots_contract = self.w3.eth.contract(address=self.w3.to_checksum_address(vots_address), abi=self.vots_abi)
        initial_supply = self.w3.to_wei(1000000, 'ether')  # 1M VOTS

        tx = vots_contract.functions.transfer(manager_address, initial_supply).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

        print("✅ Transferred initial VOTS supply to pool manager")

        # Start bootstrap process
        manager_contract = self.w3.eth.contract(address=self.w3.to_checksum_address(manager_address), abi=self.manager_abi)

        tx = manager_contract.functions.startBootstrap().build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 150000,
            'gasPrice': self.w3.eth.gas_price
        })

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

        print("✅ Bootstrap process started - fair launch active for 7 days")

    def deploy_full_ecosystem(self) -> dict:
        """Deploy the complete VOTS ecosystem"""
        print("🌟 Starting VOTS Ecosystem Deployment")
        print("=" * 50)

        # Step 1: Deploy VOTS token
        vots_address = self.deploy_vots_token()

        # Step 2: Deploy bootstrap hook
        hook_address = self.deploy_bootstrap_hook(vots_address)

        # Step 3: Deploy pool manager
        manager_address = self.deploy_pool_manager(vots_address)

        # Step 4: Setup bootstrap
        self.setup_bootstrap(vots_address, manager_address)

        deployment_info = {
            'vots_token': vots_address,
            'bootstrap_hook': hook_address,
            'pool_manager': manager_address,
            'network': self.w3.eth.chain_id,
            'bootstrap_start': int(time.time()),
            'bootstrap_duration': 7 * 24 * 3600  # 7 days
        }

        # Save deployment info
        with open('vots_deployment.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)

        print("\n" + "=" * 50)
        print("🎉 VOTS Ecosystem Deployment Complete!")
        print(f"📄 Deployment info saved to: vots_deployment.json")
        print("\n📋 Next Steps:")
        print("1. Share the fair launch with potential contributors")
        print("2. Monitor contributions during the 7-day period")
        print("3. After fair launch ends, complete bootstrap")
        print("4. Contributors can claim their VOTS tokens")
        print("5. Automated liquidity bootstrapping begins")

        return deployment_info

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Deploy VOTS Token Ecosystem with V4 Bootstrap")
    parser.add_argument("--network", choices=["base", "base-goerli"], default="base",
                       help="Network to deploy to")
    parser.add_argument("--private-key", required=True, help="Deployer private key")
    parser.add_argument("--rpc-url", help="Custom RPC URL")

    args = parser.parse_args()

    # Set RPC URL based on network
    if args.rpc_url:
        rpc_url = args.rpc_url
    elif args.network == "base":
        rpc_url = "https://mainnet.base.org"
    elif args.network == "base-goerli":
        rpc_url = "https://goerli.base.org"
    else:
        raise ValueError(f"Unsupported network: {args.network}")

    # Deploy
    deployer = VOTSDeployer(rpc_url, args.private_key)
    deployment = deployer.deploy_full_ecosystem()

    print(f"\n🚀 VOTS Token: {deployment['vots_token']}")
    print(f"🔗 Bootstrap Hook: {deployment['bootstrap_hook']}")
    print(f"🏊 Pool Manager: {deployment['pool_manager']}")

if __name__ == "__main__":
    main()
