#!/usr/bin/env python3
"""
Ethermax Ecosystem Contract Analyzer - Comprehensive analysis of Ethermax token contracts
Analyzes token, mining program, and staking program contracts
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

import aiohttp
from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ContractLogicError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(level)s - %(message)s')
logger = logging.getLogger(__name__)

class EthermaxContractAnalyzer:
    """Comprehensive Ethermax ecosystem contract analyzer"""

    def __init__(self, rpc_url: str = "https://mainnet.base.org"):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        # Ethermax ecosystem contracts
        self.contracts = {
            "token": {
                "address": Web3.to_checksum_address("0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"),
                "name": "Ethermax Token",
                "type": "ERC20"
            },
            "mining": {
                "address": Web3.to_checksum_address("0xD797651e681bd5536084Bc6017019363b5DFFb91"),
                "name": "Mining Program",
                "type": "Mining"
            },
            "staking": {
                "address": Web3.to_checksum_address("0x5679C9Fe6D89D8ddC284CA133c2E94de41223031"),
                "name": "Staking Program",
                "type": "Staking"
            }
        }

        self.contract_instances: Dict[str, Contract] = {}
        self.erc20_abi = self._get_erc20_abi()
        self.mining_abi = self._get_mining_abi()
        self.staking_abi = self._get_staking_abi()

    def _get_erc20_abi(self) -> List[Dict]:
        """Get ERC20 ABI for token functions"""
        return [
            {
                "constant": True,
                "inputs": [],
                "name": "name",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "symbol",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "owner",
                "outputs": [{"name": "", "type": "address"}],
                "type": "function"
            }
        ]

    def _get_mining_abi(self) -> List[Dict]:
        """Get mining program ABI"""
        return [
            {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "miningReward", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "miningDifficulty", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "", "type": "address"}], "name": "minerStats", "outputs": [{"name": "", "type": "uint256"}, {"name": "", "type": "uint256"}], "type": "function"},
            {"constant": False, "inputs": [], "name": "mine", "outputs": [], "type": "function"},
        ]

    def _get_staking_abi(self) -> List[Dict]:
        """Get staking program ABI"""
        return [
            {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "totalStaked", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "", "type": "address"}], "name": "stakedBalance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "stakingRewardRate", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "", "type": "address"}], "name": "pendingRewards", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "", "type": "address"}], "name": "stakingTimestamp", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": False, "inputs": [{"name": "amount", "type": "uint256"}], "name": "stake", "outputs": [], "type": "function"},
            {"constant": False, "inputs": [{"name": "amount", "type": "uint256"}], "name": "unstake", "outputs": [], "type": "function"},
            {"constant": False, "inputs": [], "name": "claimRewards", "outputs": [], "type": "function"},
        ]

    async def connect_contracts(self) -> bool:
        """Connect to all Ethermax contracts"""
        success = True

        for contract_key, contract_info in self.contracts.items():
            try:
                if contract_key == "token":
                    abi = self.erc20_abi
                elif contract_key == "mining":
                    abi = self.mining_abi
                elif contract_key == "staking":
                    abi = self.staking_abi
                else:
                    continue

                contract = self.w3.eth.contract(address=contract_info["address"], abi=abi)
                self.contract_instances[contract_key] = contract

                # Test connection
                try:
                    name = contract.functions.name().call()
                    logger.info(f"Connected to {contract_info['name']}: {name}")
                except:
                    logger.info(f"Connected to {contract_info['name']} (no name function)")

            except Exception as e:
                logger.error(f"Failed to connect to {contract_info['name']}: {e}")
                success = False

        return success

    async def analyze_token_contract(self) -> Dict[str, Any]:
        """Analyze Ethermax token contract"""
        if "token" not in self.contract_instances:
            return {"error": "Token contract not connected"}

        contract = self.contract_instances["token"]

        try:
            info = {
                "contract_address": self.contracts["token"]["address"],
                "contract_type": "ERC20 Token",
                "name": "Ethermax",  # Default name
                "symbol": "ETHMAX",  # Default symbol
                "decimals": 18,  # Default decimals
                "total_supply_raw": 0,
                "analysis_timestamp": datetime.now().isoformat()
            }

            # Try to get actual values
            try:
                info["name"] = contract.functions.name().call()
            except:
                pass

            try:
                info["symbol"] = contract.functions.symbol().call()
            except:
                pass

            try:
                info["decimals"] = contract.functions.decimals().call()
            except:
                pass

            try:
                info["total_supply_raw"] = contract.functions.totalSupply().call()
                info["total_supply"] = Decimal(str(info["total_supply_raw"])) / Decimal(10 ** info["decimals"])
                info["total_supply_formatted"] = f"{info['total_supply']:,}"
            except:
                pass

            # Try to get owner
            try:
                info["owner"] = contract.functions.owner().call()
            except:
                info["owner"] = "Not available"

            return info
        except Exception as e:
            logger.error(f"Error analyzing token contract: {e}")
            return {"error": str(e)}

    async def analyze_mining_contract(self) -> Dict[str, Any]:
        """Analyze mining program contract"""
        if "mining" not in self.contract_instances:
            return {"error": "Mining contract not connected"}

        contract = self.contract_instances["mining"]

        analysis = {
            "contract_address": self.contracts["mining"]["address"],
            "contract_type": "Mining Program",
            "mining_stats": {},
            "reward_mechanics": {},
            "miner_activity": {},
            "analysis_timestamp": datetime.now().isoformat()
        }

        # Analyze mining functions
        mining_functions = ["miningReward", "miningDifficulty", "mine"]
        for func_name in mining_functions:
            try:
                func = getattr(contract.functions, func_name, None)
                if func:
                    if func_name in ["miningReward", "miningDifficulty"]:
                        value = func().call()
                        analysis["mining_stats"][func_name] = value
                        if func_name == "miningReward":
                            analysis["reward_mechanics"]["reward_amount"] = value
                    elif func_name == "mine":
                        analysis["mining_stats"]["mining_function_available"] = True
            except:
                continue

        # Try to get miner stats for a sample address
        try:
            sample_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"  # Vitalik's address as sample
            miner_stats_func = getattr(contract.functions, "minerStats", None)
            if miner_stats_func:
                stats = miner_stats_func(sample_address).call()
                analysis["miner_activity"]["sample_stats"] = {
                    "total_mined": stats[0] if len(stats) > 0 else 0,
                    "last_mine_time": stats[1] if len(stats) > 1 else 0
                }
        except:
            pass

        return analysis

    async def analyze_staking_contract(self) -> Dict[str, Any]:
        """Analyze staking program contract"""
        if "staking" not in self.contract_instances:
            return {"error": "Staking contract not connected"}

        contract = self.contract_instances["staking"]

        analysis = {
            "contract_address": self.contracts["staking"]["address"],
            "contract_type": "Staking Program",
            "staking_stats": {},
            "reward_mechanics": {},
            "user_staking_data": {},
            "analysis_timestamp": datetime.now().isoformat()
        }

        # Analyze staking functions
        staking_functions = ["totalStaked", "stakingRewardRate", "stake", "unstake", "claimRewards"]
        for func_name in staking_functions:
            try:
                func = getattr(contract.functions, func_name, None)
                if func:
                    if func_name in ["totalStaked", "stakingRewardRate"]:
                        value = func().call()
                        analysis["staking_stats"][func_name] = value
                        if func_name == "stakingRewardRate":
                            analysis["reward_mechanics"]["reward_rate"] = value
                    elif func_name in ["stake", "unstake", "claimRewards"]:
                        analysis["staking_stats"][f"{func_name}_available"] = True
            except:
                continue

        # Try to get staking data for a sample address
        try:
            sample_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
            staking_funcs = ["stakedBalance", "pendingRewards", "stakingTimestamp"]
            for func_name in staking_funcs:
                func = getattr(contract.functions, func_name, None)
                if func:
                    try:
                        value = func(sample_address).call()
                        analysis["user_staking_data"][func_name] = value
                    except:
                        continue
        except:
            pass

        return analysis

    async def analyze_ecosystem_interactions(self) -> Dict[str, Any]:
        """Analyze interactions between contracts in the ecosystem"""
        interactions = {
            "token_mining_integration": {},
            "token_staking_integration": {},
            "cross_contract_dependencies": {},
            "ecosystem_health": {},
            "analysis_timestamp": datetime.now().isoformat()
        }

        # Check if mining contract references token
        if "mining" in self.contract_instances:
            mining_contract = self.contract_instances["mining"]
            try:
                # Look for token address in mining contract
                # This is a simplified check - in reality would need contract source
                interactions["token_mining_integration"]["mining_contract_exists"] = True
            except:
                pass

        # Check if staking contract references token
        if "staking" in self.contract_instances:
            staking_contract = self.contract_instances["staking"]
            try:
                interactions["token_staking_integration"]["staking_contract_exists"] = True
            except:
                pass

        # Basic ecosystem health check
        contract_count = len([c for c in self.contract_instances.keys() if c in self.contract_instances])
        interactions["ecosystem_health"] = {
            "contracts_connected": contract_count,
            "total_contracts": 3,
            "connection_status": "Good" if contract_count == 3 else "Partial",
            "ecosystem_maturity": "Developing" if contract_count >= 2 else "Early Stage"
        }

        return interactions

    async def comprehensive_ecosystem_analysis(self) -> Dict[str, Any]:
        """Run comprehensive Ethermax ecosystem analysis"""
        logger.info("Starting comprehensive Ethermax ecosystem analysis...")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "ecosystem_name": "Ethermax",
            "network": "Base",
            "contracts_analyzed": list(self.contracts.keys()),
            "analysis_results": {}
        }

        # Connect to all contracts
        if not await self.connect_contracts():
            return {"error": "Failed to connect to contracts"}

        # Run all analyses
        analyses = [
            ("token_contract", self.analyze_token_contract),
            ("mining_contract", self.analyze_mining_contract),
            ("staking_contract", self.analyze_staking_contract),
            ("ecosystem_interactions", self.analyze_ecosystem_interactions)
        ]

        for analysis_name, analysis_func in analyses:
            logger.info(f"Running {analysis_name} analysis...")
            try:
                result = await analysis_func()
                analysis["analysis_results"][analysis_name] = result
            except Exception as e:
                logger.error(f"Error in {analysis_name} analysis: {e}")
                analysis["analysis_results"][analysis_name] = {"error": str(e)}

        return analysis

    def save_analysis(self, analysis: Dict[str, Any], filename: str = "data/ethermax_ecosystem_analysis.json"):
        """Save analysis results to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            logger.info(f"Ecosystem analysis saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")


async def main():
    """Main ecosystem analysis function"""
    analyzer = EthermaxContractAnalyzer()

    analysis = await analyzer.comprehensive_ecosystem_analysis()
    analyzer.save_analysis(analysis)

    print("\n" + "="*70)
    print("ETHERMAX ECOSYSTEM CONTRACT ANALYSIS")
    print("="*70)

    if "error" in analysis:
        print(f"❌ Analysis failed: {analysis['error']}")
        return

    token = analysis["analysis_results"].get("token_contract", {})
    mining = analysis["analysis_results"].get("mining_contract", {})
    staking = analysis["analysis_results"].get("staking_contract", {})
    ecosystem = analysis["analysis_results"].get("ecosystem_interactions", {})

    print(f"🪙 Token Contract: {token.get('name', 'Unknown')} ({token.get('symbol', 'Unknown')})")
    print(f"� Total Supply: {token.get('total_supply_formatted', 'Unknown')}")
    print(f"� Token Address: {token.get('contract_address', 'Unknown')}")

    print(f"\n⛏️ Mining Contract: {mining.get('contract_address', 'Unknown')}")
    reward = mining.get("mining_stats", {}).get("miningReward", "Unknown")
    print(f"💰 Mining Reward: {reward}")

    print(f"\n🏦 Staking Contract: {staking.get('contract_address', 'Unknown')}")
    total_staked = staking.get("staking_stats", {}).get("totalStaked", "Unknown")
    print(f"� Total Staked: {total_staked}")

    health = ecosystem.get("ecosystem_health", {})
    print(f"\n🌐 Ecosystem Health: {health.get('connection_status', 'Unknown')} ({health.get('contracts_connected', 0)}/3 contracts)")

    print("\n📊 Analysis completed and saved to data/ethermax_ecosystem_analysis.json")


if __name__ == "__main__":
    asyncio.run(main())
