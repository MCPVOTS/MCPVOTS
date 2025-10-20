#!/usr/bin/env python3
"""
VOTS Token Contract - Hybrid Incentive System

Implements the hybrid tokenomics model where:
- USDC handles payments (Base Pay)
- VOTS handles incentives, governance, and reputation

Token Features:
- Fixed supply: 1,000,000 VOTS
- Governance voting
- Staking for reputation
- Service listing fees
- Platform fee buybacks
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from web3 import Web3
from eth_account import Account

# VOTS Token Contract ABI (simplified for demo)
VOTS_CONTRACT_ABI = [
    {
        "inputs": [
            {"name": "name", "type": "string"},
            {"name": "symbol", "type": "string"},
            {"name": "initialSupply", "type": "uint256"}
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "recipient", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

@dataclass
class VOTSAllocation:
    """VOTS token allocation structure"""
    community_rewards: float = 400000  # 40%
    agent_incentives: float = 300000   # 30%
    team_allocation: float = 200000    # 20%
    treasury: float = 100000           # 10%

    @property
    def total_supply(self) -> float:
        return (self.community_rewards + self.agent_incentives +
                self.team_allocation + self.treasury)

@dataclass
class VOTSStake:
    """VOTS staking position"""
    staker: str
    amount: float
    stake_type: str  # "reputation", "governance", "service_listing"
    lock_period_days: int
    start_time: datetime
    end_time: datetime
    rewards_earned: float = 0.0
    is_active: bool = True

    @property
    def days_remaining(self) -> int:
        if not self.is_active:
            return 0
        remaining = self.end_time - datetime.now()
        return max(0, remaining.days)

@dataclass
class GovernanceProposal:
    """Governance proposal structure"""
    id: str
    title: str
    description: str
    proposer: str
    proposal_type: str  # "fee_change", "feature_add", "parameter_update"
    changes: Dict[str, Any]
    start_time: datetime
    end_time: datetime
    status: str = "active"  # "active", "passed", "rejected", "executed"
    votes_for: float = 0.0
    votes_against: float = 0.0
    total_votes: float = 0.0

@dataclass
class VOTSTransaction:
    """VOTS token transaction"""
    id: str
    from_address: str
    to_address: str
    amount: float
    transaction_type: str  # "transfer", "stake", "unstake", "burn", "mint"
    fee: float = 0.0
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

class VOTSTokenContract:
    """
    VOTS Token Contract Implementation

    Hybrid tokenomics:
    - Fixed supply: 1,000,000 VOTS
    - USDC for payments, VOTS for incentives
    - Governance and staking mechanisms
    """

    def __init__(
        self,
        contract_address: str = "0x1234567890123456789012345678901234567890",
        rpc_url: str = "https://mainnet.base.org",
        private_key: Optional[str] = None
    ):
        self.contract_address = contract_address
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=VOTS_CONTRACT_ABI
        )

        # Load account if private key provided
        if private_key:
            self.account = Account.from_key(private_key)
        else:
            self.account = None

        # Token economics
        self.allocation = VOTSAllocation()
        self.total_supply = self.allocation.total_supply

        # State management (use database in production)
        self.balances: Dict[str, float] = {}
        self.stakes: Dict[str, VOTSStake] = {}
        self.proposals: Dict[str, GovernanceProposal] = {}
        self.transactions: List[VOTSTransaction] = []

        # Platform fees collected (for buybacks)
        self.collected_usdc_fees = 0.0

        # Initialize allocations
        self._initialize_allocations()

    def _initialize_allocations(self):
        """Initialize token allocations"""
        # Community rewards pool
        self.balances["community_rewards"] = self.allocation.community_rewards

        # Agent incentives pool
        self.balances["agent_incentives"] = self.allocation.agent_incentives

        # Team allocation (vested)
        self.balances["team_allocation"] = self.allocation.team_allocation

        # Treasury
        self.balances["treasury"] = self.allocation.treasury

    # Balance and Transfer Functions
    def balance_of(self, address: str) -> float:
        """Get VOTS balance for address"""
        return self.balances.get(address, 0.0)

    def transfer(self, from_address: str, to_address: str, amount: float) -> bool:
        """Transfer VOTS tokens"""
        if self.balance_of(from_address) < amount:
            raise ValueError("Insufficient VOTS balance")

        # Update balances
        self.balances[from_address] -= amount
        self.balances[to_address] = self.balances.get(to_address, 0.0) + amount

        # Record transaction
        tx = VOTSTransaction(
            id=f"tx_{len(self.transactions)}",
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            transaction_type="transfer"
        )
        self.transactions.append(tx)

        return True

    # Staking Functions
    def stake_tokens(
        self,
        staker: str,
        amount: float,
        stake_type: str,
        lock_period_days: int
    ) -> str:
        """Stake VOTS tokens for benefits"""
        if self.balance_of(staker) < amount:
            raise ValueError("Insufficient VOTS balance")

        stake_id = f"stake_{staker}_{len([s for s in self.stakes.values() if s.staker == staker])}"

        stake = VOTSStake(
            staker=staker,
            amount=amount,
            stake_type=stake_type,
            lock_period_days=lock_period_days,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(days=lock_period_days)
        )

        # Lock tokens
        self.balances[staker] -= amount
        self.stakes[stake_id] = stake

        # Record transaction
        tx = VOTSTransaction(
            id=f"stake_{len(self.transactions)}",
            from_address=staker,
            to_address="staking_contract",
            amount=amount,
            transaction_type="stake",
            metadata={"stake_id": stake_id, "stake_type": stake_type}
        )
        self.transactions.append(tx)

        return stake_id

    def unstake_tokens(self, stake_id: str) -> float:
        """Unstake VOTS tokens and claim rewards"""
        if stake_id not in self.stakes:
            raise ValueError("Stake not found")

        stake = self.stakes[stake_id]

        if stake.days_remaining > 0:
            raise ValueError(f"Stake still locked for {stake.days_remaining} days")

        # Calculate rewards (simplified)
        reward_multiplier = self._calculate_stake_reward(stake)
        rewards = stake.amount * reward_multiplier * (stake.lock_period_days / 365)

        # Return staked amount + rewards
        total_return = stake.amount + rewards

        # Update balances
        self.balances[stake.staker] = self.balances.get(stake.staker, 0.0) + total_return

        # Mint rewards from community pool
        if self.balances["community_rewards"] >= rewards:
            self.balances["community_rewards"] -= rewards
        else:
            # If community pool depleted, reduce rewards
            rewards = self.balances["community_rewards"]
            self.balances["community_rewards"] = 0

        # Mark stake as inactive
        stake.is_active = False
        stake.rewards_earned = rewards

        # Record transaction
        tx = VOTSTransaction(
            id=f"unstake_{len(self.transactions)}",
            from_address="staking_contract",
            to_address=stake.staker,
            amount=total_return,
            transaction_type="unstake",
            metadata={"stake_id": stake_id, "rewards": rewards}
        )
        self.transactions.append(tx)

        return total_return

    def _calculate_stake_reward(self, stake: VOTSStake) -> float:
        """Calculate staking reward multiplier"""
        base_apy = 0.15  # 15% base APY

        # Bonus for longer locks
        lock_bonus = min(stake.lock_period_days / 365, 1.0) * 0.1  # Up to 10% bonus

        # Bonus for reputation staking
        type_bonus = 0.05 if stake.stake_type == "reputation" else 0.0

        return base_apy + lock_bonus + type_bonus

    # Governance Functions
    def create_proposal(
        self,
        proposer: str,
        title: str,
        description: str,
        proposal_type: str,
        changes: Dict[str, Any],
        voting_period_days: int = 7
    ) -> str:
        """Create a governance proposal"""
        # Check proposer has minimum VOTS for proposal creation
        min_proposal_vots = 100  # Require 100 VOTS to create proposals
        if self.balance_of(proposer) < min_proposal_vots:
            raise ValueError(f"Minimum {min_proposal_vots} VOTS required to create proposals")

        proposal_id = f"prop_{len(self.proposals)}"

        proposal = GovernanceProposal(
            id=proposal_id,
            title=title,
            description=description,
            proposer=proposer,
            proposal_type=proposal_type,
            changes=changes,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(days=voting_period_days)
        )

        self.proposals[proposal_id] = proposal

        return proposal_id

    def vote_on_proposal(self, voter: str, proposal_id: str, support: bool, votes: float):
        """Vote on a governance proposal"""
        if proposal_id not in self.proposals:
            raise ValueError("Proposal not found")

        proposal = self.proposals[proposal_id]

        if proposal.status != "active":
            raise ValueError("Proposal is not active")

        if datetime.now() > proposal.end_time:
            raise ValueError("Voting period has ended")

        # Check voter has enough voting power
        voter_balance = self.balance_of(voter)
        staked_balance = sum(s.amount for s in self.stakes.values()
                           if s.staker == voter and s.is_active)

        total_voting_power = voter_balance + staked_balance

        if votes > total_voting_power:
            raise ValueError("Insufficient voting power")

        # Record vote
        if support:
            proposal.votes_for += votes
        else:
            proposal.votes_against += votes

        proposal.total_votes += votes

    def execute_proposal(self, proposal_id: str) -> bool:
        """Execute a passed proposal"""
        if proposal_id not in self.proposals:
            raise ValueError("Proposal not found")

        proposal = self.proposals[proposal_id]

        if proposal.status != "active":
            raise ValueError("Proposal not active")

        if datetime.now() < proposal.end_time:
            raise ValueError("Voting period not ended")

        # Check if proposal passed (simple majority)
        if proposal.votes_for > proposal.votes_against:
            proposal.status = "passed"
            # In production, this would trigger actual changes
            self._apply_proposal_changes(proposal)
            return True
        else:
            proposal.status = "rejected"
            return False

    def _apply_proposal_changes(self, proposal: GovernanceProposal):
        """Apply the changes from a passed proposal"""
        # This would implement the actual changes based on proposal type
        # For demo, just log the changes
        print(f"Applying proposal changes: {proposal.changes}")

    # Platform Fee Integration
    def process_platform_fee(self, usdc_amount: float, fee_percentage: float = 0.02):
        """Process platform fee from USDC payments and convert to VOTS buyback"""
        fee_amount = usdc_amount * fee_percentage
        self.collected_usdc_fees += fee_amount

        # Convert USDC to VOTS (simplified conversion)
        # In production, this would use DEX oracles for fair price
        vots_to_mint = fee_amount * 100  # Assume 1 USDC = 100 VOTS

        # Mint VOTS from treasury
        if self.balances["treasury"] >= vots_to_mint:
            self.balances["treasury"] -= vots_to_mint
            self.balances["community_rewards"] += vots_to_mint

            # Record mint transaction
            tx = VOTSTransaction(
                id=f"fee_mint_{len(self.transactions)}",
                from_address="treasury",
                to_address="community_rewards",
                amount=vots_to_mint,
                transaction_type="mint",
                metadata={"source": "platform_fees", "usdc_amount": fee_amount}
            )
            self.transactions.append(tx)

            return vots_to_mint

        return 0.0

    # Agent Incentives
    def reward_agent(self, agent_address: str, reward_amount: float, reason: str):
        """Reward agent for platform contributions"""
        if self.balances["agent_incentives"] >= reward_amount:
            self.balances["agent_incentives"] -= reward_amount
            self.balances[agent_address] = self.balances.get(agent_address, 0.0) + reward_amount

            # Record transaction
            tx = VOTSTransaction(
                id=f"reward_{len(self.transactions)}",
                from_address="agent_incentives",
                to_address=agent_address,
                amount=reward_amount,
                transaction_type="mint",
                metadata={"reason": reason}
            )
            self.transactions.append(tx)

            return True

        return False

    # Service Listing Fees
    def charge_listing_fee(self, agent_address: str, fee_amount: float) -> bool:
        """Charge VOTS fee for service listings"""
        if self.balance_of(agent_address) >= fee_amount:
            # Burn the fee
            self.balances[agent_address] -= fee_amount

            # Record burn transaction
            tx = VOTSTransaction(
                id=f"listing_fee_{len(self.transactions)}",
                from_address=agent_address,
                to_address="burn_address",
                amount=fee_amount,
                transaction_type="burn",
                metadata={"purpose": "service_listing"}
            )
            self.transactions.append(tx)

            return True

        return False

    # Analytics and Reporting
    def get_token_stats(self) -> Dict[str, Any]:
        """Get comprehensive token statistics"""
        total_staked = sum(s.amount for s in self.stakes.values() if s.is_active)
        active_stakes = len([s for s in self.stakes.values() if s.is_active])
        active_proposals = len([p for p in self.proposals.values() if p.status == "active"])

        return {
            "total_supply": self.total_supply,
            "circulating_supply": self.total_supply - total_staked,
            "total_staked": total_staked,
            "active_stakes": active_stakes,
            "active_proposals": active_proposals,
            "collected_usdc_fees": self.collected_usdc_fees,
            "pool_balances": {
                "community_rewards": self.balances.get("community_rewards", 0),
                "agent_incentives": self.balances.get("agent_incentives", 0),
                "team_allocation": self.balances.get("team_allocation", 0),
                "treasury": self.balances.get("treasury", 0)
            }
        }

    def get_staking_stats(self, address: str) -> Dict[str, Any]:
        """Get staking statistics for an address"""
        user_stakes = [s for s in self.stakes.values() if s.staker == address and s.is_active]

        total_staked = sum(s.amount for s in user_stakes)
        total_rewards_earned = sum(s.rewards_earned for s in self.stakes.values()
                                 if s.staker == address)

        return {
            "total_staked": total_staked,
            "active_stakes": len(user_stakes),
            "total_rewards_earned": total_rewards_earned,
            "stakes": [asdict(s) for s in user_stakes]
        }

# Example usage and testing
def demo_tokenomics():
    """Demonstrate the VOTS tokenomics system"""
    print("🚀 VOTS Tokenomics Demo")
    print("=" * 50)

    # Initialize token contract
    vots = VOTSTokenContract()

    print(f"Total Supply: {vots.total_supply} VOTS")
    print(f"Initial allocations: {vots.get_token_stats()['pool_balances']}")
    print()

    # Simulate agent registration
    agent1 = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    agent2 = "0x742d35Cc6634C0532925a3b844Bc454e4438f44f"

    print("👤 Agent Registration & Rewards")
    print("-" * 30)

    # Reward agents for successful deliveries
    vots.reward_agent(agent1, 100, "successful_service_delivery")
    vots.reward_agent(agent2, 150, "high_quality_service")

    print(f"Agent1 balance: {vots.balance_of(agent1)} VOTS")
    print(f"Agent2 balance: {vots.balance_of(agent2)} VOTS")
    print()

    # Simulate staking
    print("🔒 Staking for Reputation")
    print("-" * 30)

    stake_id1 = vots.stake_tokens(agent1, 25, "reputation", 30)  # Leave 75 for governance
    stake_id2 = vots.stake_tokens(agent2, 25, "governance", 90)  # Leave 125 for governance

    print(f"Agent1 staked 25 VOTS for reputation (30 days)")
    print(f"Agent2 staked 25 VOTS for governance (90 days)")
    print()

    # Simulate platform fees
    print("💰 Platform Fee Processing")
    print("-" * 30)

    # Process fees from USDC payments
    vots.process_platform_fee(1000, 0.02)  # 2% fee on $1000 payment
    vots.process_platform_fee(500, 0.02)   # 2% fee on $500 payment

    print(f"Collected USDC fees: ${vots.collected_usdc_fees}")
    print(f"Community rewards pool: {vots.balance_of('community_rewards')} VOTS")
    print()

    # Simulate service listing
    print("📋 Service Listing Fees")
    print("-" * 30)

    # Agent lists premium service
    vots.charge_listing_fee(agent1, 10)  # 10 VOTS listing fee

    print(f"Agent1 balance after listing fee: {vots.balance_of(agent1)} VOTS")
    print()

    # Simulate governance
    print("🗳️ Governance Proposals")
    print("-" * 30)

    # Create proposal (use agent2 who has enough unstaked VOTS)
    prop_id = vots.create_proposal(
        proposer=agent2,
        title="Reduce Platform Fees",
        description="Lower platform fees from 2% to 1.5%",
        proposal_type="fee_change",
        changes={"platform_fee": 0.015}
    )

    print(f"Created proposal: {prop_id}")

    # Voting (use available balances)
    agent1_balance = vots.balance_of(agent1)  # 40 VOTS
    agent2_balance = vots.balance_of(agent2)  # 75 VOTS

    vots.vote_on_proposal(agent1, prop_id, True, min(agent1_balance, 40))   # Vote for with available balance
    vots.vote_on_proposal(agent2, prop_id, False, min(agent2_balance, 75))  # Vote against with available balance

    proposal = vots.proposals[prop_id]
    print(f"Votes for: {proposal.votes_for}, Votes against: {proposal.votes_against}")
    print()

    # Final statistics
    print("📊 Final Token Statistics")
    print("-" * 30)
    stats = vots.get_token_stats()
    print(f"Total Supply: {stats['total_supply']}")
    print(f"Circulating Supply: {stats['circulating_supply']}")
    print(f"Total Staked: {stats['total_staked']}")
    print(f"Active Stakes: {stats['active_stakes']}")
    print(f"Collected USDC Fees: ${stats['collected_usdc_fees']}")

if __name__ == "__main__":
    demo_tokenomics()
