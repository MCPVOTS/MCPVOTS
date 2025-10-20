#!/usr/bin/env python3
"""
Ethermax Ecosystem Burn Analyzer
Comprehensive analysis of burn functions across all Ethermax contracts
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ContractLogicError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(level)s - %(message)s')
logger = logging.getLogger(__name__)

class EthermaxContractAnalyzer:
    """Analyzer for all Ethermax ecosystem contracts"""

    def __init__(self):
        self.contracts = {
            "Ethermax Token": "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467",
            "Mining Program": "0xD797651e681bd5536084Bc6017019363b5DFFb91",
            "Staking Program": "0x5679C9Fe6D89D8ddC284CA133c2E94de41223031"
        }
        self.rpc_url = "https://mainnet.base.org"
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.extended_abi = self._get_extended_abi()

    def _get_extended_abi(self) -> List[Dict]:
        """Get extended ABI including burn and supply control functions"""
        return [
            # ERC20 standard
            {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "owner", "outputs": [{"name": "", "type": "address"}], "type": "function"},

            # Burn functions
            {"constant": False, "inputs": [{"name": "amount", "type": "uint256"}], "name": "burn", "outputs": [], "type": "function"},
            {"constant": False, "inputs": [{"name": "account", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "burnFrom", "outputs": [], "type": "function"},
            {"constant": False, "inputs": [{"name": "amount", "type": "uint256"}], "name": "_burn", "outputs": [], "type": "function"},
            {"constant": False, "inputs": [{"name": "account", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "_burnFrom", "outputs": [], "type": "function"},

            # Supply control functions
            {"constant": True, "inputs": [], "name": "maxSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "MAX_SUPPLY", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "cap", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "CAP", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},

            # Tax/fee functions
            {"constant": True, "inputs": [], "name": "burnFee", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "taxFee", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "liquidityFee", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
        ]

    async def analyze_contract_burn_functions(self, contract_name: str, address: str) -> Dict[str, Any]:
        """Analyze burn functions for a specific contract"""
        try:
            checksum_address = Web3.to_checksum_address(address)
            contract = self.w3.eth.contract(address=checksum_address, abi=self.extended_abi)

            analysis = {
                "contract_name": contract_name,
                "address": address,
                "burn_functions_found": [],
                "burn_mechanisms": [],
                "tax_burn_enabled": False,
                "burn_events_count": 0,
                "total_burned": 0,
                "burn_efficiency": "None"
            }

            # Get basic info
            try:
                analysis["token_name"] = contract.functions.name().call()
                analysis["token_symbol"] = contract.functions.symbol().call()
                analysis["decimals"] = contract.functions.decimals().call()
                analysis["total_supply"] = contract.functions.totalSupply().call()
            except:
                analysis["contract_type"] = "Non-ERC20"

            # Check for burn functions
            burn_functions = ["burn", "burnFrom", "_burn", "_burnFrom"]
            for func_name in burn_functions:
                try:
                    func = getattr(contract.functions, func_name, None)
                    if func:
                        analysis["burn_functions_found"].append(func_name)
                        analysis["burn_mechanisms"].append(f"Direct {func_name}")
                except:
                    continue

            # Check for burn taxes/fees
            fee_functions = ["burnFee", "taxFee", "liquidityFee"]
            for fee_name in fee_functions:
                try:
                    func = getattr(contract.functions, fee_name, None)
                    if func:
                        fee_value = func().call()
                        if fee_name == "burnFee" and fee_value > 0:
                            analysis["tax_burn_enabled"] = True
                            analysis["burn_mechanisms"].append(f"{fee_name}: {fee_value}%")
                        elif fee_value > 0:
                            analysis["burn_mechanisms"].append(f"{fee_name}: {fee_value}%")
                except:
                    continue

            # Analyze burn events (transfers to dead address)
            try:
                latest_block = self.w3.eth.block_number
                from_block = max(0, latest_block - 10000)  # Last 10k blocks

                burn_address = "0x000000000000000000000000000000000000dEaD"

                # Try to get Transfer events
                try:
                    transfer_events = contract.events.Transfer.get_logs(
                        fromBlock=from_block,
                        toBlock=latest_block,
                        argument_filters={'to': burn_address}
                    )
                    analysis["burn_events_count"] = len(transfer_events)
                    if transfer_events:
                        total_burned = sum(event['args']['value'] for event in transfer_events)
                        analysis["total_burned"] = total_burned
                        analysis["burn_efficiency"] = "Active"
                except:
                    analysis["burn_events_analysis"] = "Event analysis failed"

            except Exception as e:
                analysis["burn_events_error"] = str(e)

            # Determine burn capability
            if analysis["burn_functions_found"] or analysis["tax_burn_enabled"]:
                analysis["burn_capability"] = "HIGH" if len(analysis["burn_functions_found"]) > 1 else "MEDIUM"
            else:
                analysis["burn_capability"] = "LOW"

            return analysis

        except Exception as e:
            return {
                "contract_name": contract_name,
                "address": address,
                "error": str(e),
                "burn_capability": "UNKNOWN"
            }

    async def analyze_all_contracts(self) -> Dict[str, Any]:
        """Analyze all Ethermax contracts for burn functionality"""
        logger.info("Starting comprehensive Ethermax contract burn analysis...")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "ecosystem": "Ethermax",
            "network": "Base",
            "contracts_analyzed": len(self.contracts),
            "contract_analyses": {}
        }

        for contract_name, address in self.contracts.items():
            logger.info(f"Analyzing {contract_name}...")
            contract_analysis = await self.analyze_contract_burn_functions(contract_name, address)
            analysis["contract_analyses"][contract_name] = contract_analysis

        # Generate summary
        analysis["summary"] = self._generate_summary(analysis["contract_analyses"])

        return analysis

    def _generate_summary(self, analyses: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate summary of burn capabilities across all contracts"""
        summary = {
            "total_contracts": len(analyses),
            "contracts_with_burn": 0,
            "contracts_with_tax_burn": 0,
            "total_burn_functions": 0,
            "burn_capability_distribution": {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0},
            "burn_mechanisms_found": set(),
            "overall_ecosystem_burn_rating": "Unknown"
        }

        for contract_name, analysis in analyses.items():
            if "error" not in analysis:
                burn_functions = analysis.get("burn_functions_found", [])
                tax_burn = analysis.get("tax_burn_enabled", False)
                capability = analysis.get("burn_capability", "UNKNOWN")

                summary["total_burn_functions"] += len(burn_functions)
                summary["burn_capability_distribution"][capability] += 1

                if burn_functions or tax_burn:
                    summary["contracts_with_burn"] += 1

                if tax_burn:
                    summary["contracts_with_tax_burn"] += 1

                # Collect burn mechanisms
                mechanisms = analysis.get("burn_mechanisms", [])
                summary["burn_mechanisms_found"].update(mechanisms)

        # Calculate overall rating
        high_burn_contracts = summary["burn_capability_distribution"]["HIGH"]
        if high_burn_contracts >= 2:
            summary["overall_ecosystem_burn_rating"] = "Excellent"
        elif summary["contracts_with_burn"] >= 1:
            summary["overall_ecosystem_burn_rating"] = "Good"
        elif summary["total_burn_functions"] > 0:
            summary["overall_ecosystem_burn_rating"] = "Basic"
        else:
            summary["overall_ecosystem_burn_rating"] = "None"

        summary["burn_mechanisms_found"] = list(summary["burn_mechanisms_found"])

        return summary

    def save_analysis(self, analysis: Dict[str, Any], filename: str = "data/ethermax_burn_analysis.json"):
        """Save analysis results to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            logger.info(f"Ethermax burn analysis saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")


async def main():
    """Main Ethermax burn analysis function"""
    analyzer = EthermaxContractAnalyzer()

    analysis = await analyzer.analyze_all_contracts()
    analyzer.save_analysis(analysis)

    print("\n" + "="*80)
    print("ETHERMAX ECOSYSTEM BURN ANALYSIS")
    print("="*80)

    if "error" in analysis:
        print(f"❌ Analysis failed: {analysis['error']}")
        return

    summary = analysis.get("summary", {})
    contracts = analysis.get("contract_analyses", {})

    print(f"📊 Contracts Analyzed: {summary.get('total_contracts', 0)}")
    print(f"🔥 Contracts with Burn: {summary.get('contracts_with_burn', 0)}")
    print(f"💰 Tax Burn Enabled: {summary.get('contracts_with_tax_burn', 0)}")
    print(f"⚡ Total Burn Functions: {summary.get('total_burn_functions', 0)}")
    print(f"🏆 Ecosystem Burn Rating: {summary.get('overall_ecosystem_burn_rating', 'Unknown')}")

    print(f"\nBurn Capability Distribution:")
    for capability, count in summary.get('burn_capability_distribution', {}).items():
        print(f"  {capability}: {count}")

    print(f"\n🔧 Burn Mechanisms Found:")
    for mechanism in summary.get('burn_mechanisms_found', []):
        print(f"  • {mechanism}")

    print(f"\n📋 Contract Details:")
    for contract_name, contract_data in contracts.items():
        print(f"\n{contract_name} ({contract_data.get('address', 'Unknown')}):")
        if "error" in contract_data:
            print(f"  ❌ Error: {contract_data['error']}")
        else:
            burn_funcs = contract_data.get('burn_functions_found', [])
            tax_burn = contract_data.get('tax_burn_enabled', False)
            capability = contract_data.get('burn_capability', 'UNKNOWN')
            events = contract_data.get('burn_events_count', 0)

            print(f"  🔥 Burn Functions: {', '.join(burn_funcs) if burn_funcs else 'None'}")
            print(f"  💰 Tax Burn: {'Yes' if tax_burn else 'No'}")
            print(f"  ⚡ Capability: {capability}")
            print(f"  📊 Burn Events: {events}")

    print("\n📊 Analysis completed and saved to data/ethermax_burn_analysis.json")


if __name__ == "__main__":
    asyncio.run(main())
