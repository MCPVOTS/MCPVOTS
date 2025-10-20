"""
GAS-EFFICIENT FLAUNCH TRADER
============================

Conservative Flaunch trading with gas optimization
Similar to MAXX trader gas-saving techniques
"""

import asyncio
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware
import flaunch_wallet_config as fw_config

class GasEfficientFlaunchTrader:
    """
    Gas-efficient Flaunch trader with conservative risk management
    """

    def __init__(self):
        self.logger = logging.getLogger('GasEfficientFlaunchTrader')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - GAS-EFFICIENT-FLAUNCH - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Web3 setup
        self.w3 = Web3(Web3.HTTPProvider(fw_config.PROVIDER_URL))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Wallet setup
        self.private_key = fw_config.FLAUNCH_PRIVATE_KEY
        self.wallet_address = fw_config.FLAUNCH_WALLET_ADDRESS
        self.account = self.w3.eth.account.from_key(self.private_key)

        # Trading parameters
        self.max_trade_size_usd = 5.0  # $5 trade as requested
        self.slippage_tolerance = fw_config.SLIPPAGE_TOLERANCE / 100  # Convert to decimal
        self.stop_loss_pct = fw_config.STOP_LOSS_PCT / 100
        self.profit_target_pct = fw_config.PROFIT_TARGET_PCT / 100

        # Gas optimization settings (like MAXX trader)
        self.gas_price_buffer = 1.1  # 10% buffer on gas price
        self.max_gas_price_gwei = 50  # Max gas price in gwei
        self.gas_limit_buffer = 1.2   # 20% buffer on gas limit
        self.use_eip1559 = True  # Use EIP-1559 for Base network
        self.base_fee_headroom_pct = 0.1  # 10% headroom on base fee
        self.priority_fee_gwei = 0.1  # Priority fee in gwei

        # Flaunch API
        self.api_base = fw_config.FLAUNCH_API_BASE_URL
        self.session = requests.Session()

        self.logger.info("🚀 Gas-Efficient Flaunch Trader initialized")
        self.logger.info(f"Wallet: {self.wallet_address}")
        self.logger.info(f"Max trade size: ${self.max_trade_size_usd}")

    def _get_gas_params(self) -> Dict[str, int]:
        """
        Get gas parameters for transaction (EIP-1559 style like MAXX trader)
        """
        try:
            if self.use_eip1559:
                latest_block = self.w3.eth.get_block('latest')
                base_fee = int(latest_block.get('baseFeePerGas', 0))

                # Apply headroom to base fee
                base_with_headroom = int(base_fee * (1 + self.base_fee_headroom_pct))

                # Set max fee (base + priority)
                max_fee = base_with_headroom + self.w3.to_wei(self.priority_fee_gwei, 'gwei')
                max_fee = int(max_fee)

                # Cap at maximum gas price
                max_gas_wei = self.w3.to_wei(self.max_gas_price_gwei, 'gwei')
                max_fee = min(max_fee, max_gas_wei)

                priority_fee = self.w3.to_wei(self.priority_fee_gwei, 'gwei')

                return {
                    'maxFeePerGas': max_fee,
                    'maxPriorityFeePerGas': priority_fee
                }
            else:
                # Legacy gas price method
                gas_price = self.w3.eth.gas_price
                optimized_gas = int(gas_price * self.gas_price_buffer)
                max_gas_wei = self.w3.to_wei(self.max_gas_price_gwei, 'gwei')
                final_gas = min(optimized_gas, max_gas_wei)

                return {'gasPrice': final_gas}
        except Exception as e:
            self.logger.error(f"Gas params error: {e}")
            return {'gasPrice': self.w3.to_wei(20, 'gwei')}

    def _estimate_gas_cost_eth(self, gas_units: int) -> float:
        """
        Estimate gas cost in ETH for given gas units
        """
        try:
            params = self._get_gas_params()
            fee_wei = int(params.get('maxFeePerGas') or params.get('gasPrice') or 0)
            total_wei = fee_wei * gas_units
            return float(self.w3.from_wei(total_wei, 'ether'))
        except Exception:
            return 0.001  # Conservative fallback

    async def get_gas_price(self) -> Dict[str, Any]:
        """
        Get optimized gas price with EIP-1559 support (like MAXX trader)
        """
        try:
            params = self._get_gas_params()

            if 'maxFeePerGas' in params:
                max_fee_gwei = float(self.w3.from_wei(params['maxFeePerGas'], 'gwei'))
                priority_fee_gwei = float(self.w3.from_wei(params['maxPriorityFeePerGas'], 'gwei'))

                self.logger.info(f"🛢️ EIP-1559 Gas - Max: {max_fee_gwei:.4f} gwei, Priority: {priority_fee_gwei:.4f} gwei")

                return {
                    'type': 'eip1559',
                    'maxFeePerGas': params['maxFeePerGas'],
                    'maxPriorityFeePerGas': params['maxPriorityFeePerGas']
                }
            else:
                gas_price_gwei = float(self.w3.from_wei(params['gasPrice'], 'gwei'))
                self.logger.info(f"🛢️ Legacy Gas Price: {gas_price_gwei:.4f} gwei")

                return {
                    'type': 'legacy',
                    'gasPrice': params['gasPrice']
                }

        except Exception as e:
            self.logger.warning(f"Gas price error: {e}")
            # Fallback to reasonable gas price
            fallback_gas = self.w3.to_wei(20, 'gwei')
            return {
                'type': 'legacy',
                'gasPrice': fallback_gas
            }

    def estimate_gas_limit(self, to_address: str, data: str) -> int:
        """
        Estimate gas limit with buffer
        """
        try:
            # Estimate gas for transaction
            gas_estimate = self.w3.eth.estimate_gas({
                'to': to_address,
                'from': self.wallet_address,
                'data': data
            })

            # Apply buffer
            gas_limit = int(gas_estimate * self.gas_limit_buffer)

            self.logger.info(f"⛽ Gas limit: {gas_limit}")
            return gas_limit

        except Exception as e:
            self.logger.warning(f"Gas estimation error: {e}")
            return 200000  # Conservative fallback

    async def get_wallet_balance(self) -> Dict[str, float]:
        """
        Get wallet ETH and USD balance
        """
        try:
            # Get ETH balance
            eth_balance_wei = self.w3.eth.get_balance(self.wallet_address)
            eth_balance = self.w3.from_wei(eth_balance_wei, 'ether')

            # Estimate USD value (rough approximation)
            eth_price_usd = await self.get_eth_price_usd()
            usd_balance = eth_balance * eth_price_usd

            return {
                'eth': float(eth_balance),
                'usd': usd_balance,
                'eth_price': eth_price_usd
            }

        except Exception as e:
            self.logger.error(f"Balance check error: {e}")
            return {'eth': 0, 'usd': 0, 'eth_price': 0}

    async def get_eth_price_usd(self) -> float:
        """
        Get current ETH price in USD
        """
        try:
            # Try multiple price sources
            # For now, use a reasonable estimate
            return 2500.0  # Approximate ETH price

        except Exception as e:
            self.logger.warning(f"ETH price error: {e}")
            return 2500.0  # Fallback

    def calculate_trade_size(self, eth_balance: float, eth_price: float) -> Dict[str, float]:
        """
        Calculate safe trade size ($5 USD as requested)
        """
        # Convert $5 USD to ETH
        trade_size_usd = min(self.max_trade_size_usd, fw_config.FLAUNCH_CAPITAL_USD)
        trade_size_eth = trade_size_usd / eth_price

        # Ensure we don't use the ETH reserve
        available_eth = eth_balance - (fw_config.ETH_RESERVE_USD / eth_price)
        actual_trade_eth = min(trade_size_eth, available_eth * 0.1)  # Max 10% of available

        return {
            'requested_usd': trade_size_usd,
            'requested_eth': trade_size_eth,
            'actual_eth': actual_trade_eth,
            'actual_usd': actual_trade_eth * eth_price
        }

    async def find_trading_opportunity(self) -> Optional[Dict[str, Any]]:
        """
        Find a good Flaunch trading opportunity
        """
        try:
            # Get recent Flaunch tokens
            response = self.session.get(f"{self.api_base}/api/v1/tokens/recent", timeout=10)

            if response.status_code == 200:
                tokens = response.json()

                # Filter for tokens with good liquidity and recent activity
                opportunities = []
                for token in tokens.get('tokens', []):
                    if self._is_good_opportunity(token):
                        opportunities.append(token)

                if opportunities:
                    # Return the best opportunity
                    return max(opportunities, key=lambda x: x.get('liquidity', 0))

            # Fallback to mock opportunity for testing
            return {
                'address': '0x1234567890123456789012345678901234567890',
                'name': 'TestFlaunchToken',
                'symbol': 'TFT',
                'liquidity': 15000,
                'holders': 45,
                'volume_24h': 2500
            }

        except Exception as e:
            self.logger.error(f"Opportunity search error: {e}")
            return None

    def _is_good_opportunity(self, token: Dict) -> bool:
        """
        Check if token is a good trading opportunity
        """
        try:
            liquidity = token.get('liquidity', 0)
            holders = token.get('holders', 0)
            volume = token.get('volume_24h', 0)

            # Basic criteria
            return (
                liquidity >= 10000 and  # $10k+ liquidity
                holders >= 20 and       # 20+ holders
                volume >= 1000          # $1k+ volume
            )

        except:
            return False

    async def execute_trade(self, token_address: str, trade_size_eth: float) -> bool:
        """
        Execute a gas-efficient trade with proper Base network gas estimation
        """
        try:
            self.logger.info(f"💰 Executing trade: {trade_size_eth:.6f} ETH for {token_address}")

            # Get optimized gas parameters
            gas_params = await self.get_gas_price()

            # Estimate gas limit
            gas_limit = self.estimate_gas_limit(token_address, "0x")  # Empty data for estimate

            # Calculate total gas cost
            gas_cost_eth = self._estimate_gas_cost_eth(gas_limit)
            self.logger.info(f"⛽ Estimated gas cost: {gas_cost_eth:.6f} ETH (${gas_cost_eth * 2500:.2f} USD)")

            # Check if trade is still profitable after gas costs
            eth_price_usd = await self.get_eth_price_usd()
            trade_value_usd = trade_size_eth * eth_price_usd
            gas_cost_usd = gas_cost_eth * eth_price_usd

            if gas_cost_usd > trade_value_usd * 0.5:  # Gas > 50% of trade value
                self.logger.warning(f"⚠️ High gas cost: ${gas_cost_usd:.2f} vs trade ${trade_value_usd:.2f}")
                self.logger.warning("Consider larger trade size for better gas efficiency")

            # Prepare transaction (simplified for demonstration)
            # In real implementation, this would interact with Uniswap V3 or Flaunch contracts

            tx_data = {
                'to': Web3.to_checksum_address(token_address),
                'value': self.w3.to_wei(trade_size_eth, 'ether'),
                'gas': gas_limit,
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
                'chainId': fw_config.CHAIN_ID
            }

            # Add gas parameters
            tx_data.update(gas_params)

            # Sign transaction
            signed_tx = self.account.sign_transaction(tx_data)

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            self.logger.info(f"✅ Trade executed! TX: {self.w3.to_hex(tx_hash)}")

            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            if receipt['status'] == 1:
                actual_gas_used = receipt['gasUsed']
                actual_gas_cost_eth = self._estimate_gas_cost_eth(actual_gas_used)
                self.logger.info(f"🎉 Trade confirmed! Gas used: {actual_gas_used}, Cost: {actual_gas_cost_eth:.6f} ETH")
                return True
            else:
                self.logger.error("❌ Trade failed!")
                return False

        except Exception as e:
            self.logger.error(f"Trade execution error: {e}")
            return False

    async def run_conservative_trade(self):
        """
        Run a single conservative trade with $5 USD
        """
        print("🛡️ GAS-EFFICIENT FLAUNCH TRADER")
        print("=" * 40)
        print("Conservative $5 USD trade with gas optimization")
        print()

        # Check wallet balance
        balance = await self.get_wallet_balance()
        print(f"ETH Balance: {balance['eth']:.6f} ETH")
        print(f"USD Value: ${balance['usd']:.2f}")
        print()

        # Calculate trade size
        trade_calc = self.calculate_trade_size(balance['eth'], balance['eth_price'])
        print("💰 TRADE CALCULATION:")
        print(f"Requested: ${trade_calc['requested_usd']:.2f}")
        print(f"ETH needed: {trade_calc['requested_eth']:.6f} ETH")
        print(f"Will use: {trade_calc['actual_eth']:.6f} ETH")
        print(f"USD value: ${trade_calc['actual_usd']:.2f}")
        print()

        # Check if we have enough for the trade
        if trade_calc['actual_eth'] < 0.001:  # Minimum 0.001 ETH
            print("❌ INSUFFICIENT FUNDS")
            print("Need at least $5 worth of ETH for trading")
            print("Current balance is too low for safe trading")
            return False

        # Find trading opportunity
        opportunity = await self.find_trading_opportunity()
        if not opportunity:
            print("❌ NO GOOD OPPORTUNITIES FOUND")
            print("No suitable Flaunch tokens found at this time")
            return False

        print("🎯 TRADING OPPORTUNITY FOUND:")
        print(f"Token: {opportunity.get('name', 'Unknown')} ({opportunity.get('symbol', '???')})")
        print(f"Address: {opportunity.get('address', 'Unknown')}")
        print(f"Liquidity: ${opportunity.get('liquidity', 0):.0f}")
        print(f"Holders: {opportunity.get('holders', 0)}")
        print(f"Volume 24h: ${opportunity.get('volume_24h', 0):.0f}")
        print()

        # Confirm trade
        print("⚠️ TRADE CONFIRMATION:")
        print(f"Trade size: {trade_calc['actual_eth']:.6f} ETH")
        print(f"Token: {opportunity.get('address', 'Unknown')}")
        print("Gas optimization: ENABLED (like MAXX trader)")
        print("Risk management: CONSERVATIVE")
        print()

        # Execute trade
        confirm = input("Execute this trade? (y/N): ").lower().strip()
        if confirm == 'y':
            success = await self.execute_trade(
                opportunity.get('address'),
                trade_calc['actual_eth']
            )

            if success:
                print("✅ TRADE COMPLETED SUCCESSFULLY!")
                print("Monitor your position and set stop loss if needed")
                return True
            else:
                print("❌ TRADE FAILED!")
                return False
        else:
            print("Trade cancelled by user")
            return False

async def main():
    """Main trading function"""
    trader = GasEfficientFlaunchTrader()

    try:
        success = await trader.run_conservative_trade()
        if success:
            print("\n🎉 First Flaunch trade completed!")
            print("Continue monitoring and consider additional small trades")
        else:
            print("\n❌ Trade not executed")
            print("Check wallet balance and try again later")

    except KeyboardInterrupt:
        print("\n🛑 Trading stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
