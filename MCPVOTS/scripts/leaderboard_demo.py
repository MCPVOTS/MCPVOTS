#!/usr/bin/env python3
"""
MCPVOTS Leaderboard Demo
Demonstrates the leaderboard system for MCPVOTS users with rewards
"""

import asyncio
import json
from datetime import datetime
from vots_client_v2 import VOTSAgentClient, AgentType

async def leaderboard_demo():
    """Demonstrate leaderboard functionality"""
    print("🎯 MCPVOTS Leaderboard System Demo")
    print("=" * 50)

    async with VOTSAgentClient() as client:
        try:
            # Register demo agents
            print("\n📝 Registering demo agents...")
            agents = []

            # Create various types of agents with different performance levels
            agent_configs = [
                {
                    "name": "Elite Trading Bot",
                    "type": AgentType.TRADING,
                    "capabilities": ["price_analysis", "market_data", "trading_signals"],
                    "payment_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                    "performance_multiplier": 1.5
                },
                {
                    "name": "Data Analytics Agent",
                    "type": AgentType.ANALYSIS,
                    "capabilities": ["data_processing", "insights", "reporting"],
                    "payment_address": "0x8ba1f109551bD43280301264526176",
                    "performance_multiplier": 1.2
                },
                {
                    "name": "Service Provider Bot",
                    "type": AgentType.SERVICE,
                    "capabilities": ["api_services", "data_feed", "automation"],
                    "payment_address": "0x9c2d45Ee887Bc5432109876543210",
                    "performance_multiplier": 1.0
                },
                {
                    "name": "Creative Agent",
                    "type": AgentType.CREATIVE,
                    "capabilities": ["content_creation", "design", "innovation"],
                    "payment_address": "0x1a2b3c4d5e6f7890abcdef123456",
                    "performance_multiplier": 0.8
                }
            ]

            for config in agent_configs:
                agent_id = await client.register_agent(
                    name=config["name"],
                    agent_type=config["type"],
                    capabilities=config["capabilities"],
                    payment_address=config["payment_address"]
                )
                agents.append({
                    "id": agent_id,
                    "config": config
                })
                print(f"✓ Registered {config['name']}: {agent_id}")

            # Simulate some transactions to build up stats
            print("\n💰 Simulating transactions...")
            for i, agent in enumerate(agents):
                # Simulate different levels of activity
                multiplier = agent["config"]["performance_multiplier"]
                tx_count = int(50 * multiplier)

                for j in range(tx_count):
                    try:
                        # Send payments to other agents
                        to_agent = agents[(i + 1) % len(agents)]["id"]
                        amount = 0.1 + (j * 0.01 * multiplier)

                        tx_id = await client.send_payment(
                            to_agent=to_agent,
                            amount_vots=amount,
                            service_type="demo_service"
                        )
                        print(f"  {agent['config']['name'][:20]} → {amount:.2f} VOTS")

                    except Exception as e:
                        print(f"  Transaction failed: {e}")
                        break

                # Simulate services provided
                services_count = int(20 * multiplier)
                for k in range(services_count):
                    try:
                        await client.list_service(
                            agent_id=agent["id"],
                            name=f"Demo Service {k}",
                            description=f"Service provided by {agent['config']['name']}",
                            price_vots=0.05,
                            service_type="demo",
                            capabilities=["demo"],
                            delivery_time_minutes=5
                        )
                    except Exception as e:
                        print(f"  Service listing failed: {e}")
                        break

            # Get leaderboard rankings
            print("\n🏆 LEADERBOARD RANKINGS")
            print("=" * 50)

            categories = await client.get_leaderboard_categories()
            timeframes = await client.get_leaderboard_timeframes()

            for category in categories:
                print(f"\n📊 {category.upper()} LEADERBOARD")
                print("-" * 30)

                leaderboard = await client.get_leaderboard(
                    category=category,
                    timeframe="all",
                    limit=10
                )

                for entry in leaderboard["leaderboard"]:
                    rank = entry["rank"]
                    name = entry["agent_name"]
                    score = entry["score"]
                    rewards = len(entry["rewards_available"])

                    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."

                    print(f"  {medal} {name[:25]:<25} Score: {score:>8.1f} | Rewards: {rewards}")

            # Show individual agent rankings
            print("\n👤 INDIVIDUAL AGENT RANKINGS")
            print("=" * 50)

            for agent in agents:
                print(f"\n🔍 {agent['config']['name']}")
                print("-" * 30)

                rank_data = await client.get_agent_rank(agent["id"], "overall")

                print(f"  Rank: #{rank_data.get('rank', 'Unranked')}")
                print(f"  Score: {rank_data.get('score', 0):.1f}")
                print(f"  Percentile: {rank_data.get('percentile', 0):.1f}%")

                stats = rank_data.get("stats", {})
                print(f"  Transactions: {stats.get('total_transactions', 0)}")
                print(f"  Earnings (VOTS): {stats.get('total_earnings_vots', 0):.2f}")
                print(f"  Services: {stats.get('services_provided', 0)}")
                print(f"  Reputation: {stats.get('reputation_score', 0):.1f}")

                rewards = rank_data.get("rewards_available", [])
                if rewards:
                    print(f"  🎁 Available Rewards: {len(rewards)}")
                    for reward in rewards[:3]:  # Show first 3
                        print(f"    • {reward['amount']} VOTS - {reward['reason']}")
                else:
                    print("  🎁 No rewards available yet")

            # Demonstrate reward claiming
            print("\n🎁 REWARD CLAIMING DEMO")
            print("=" * 50)

            for agent in agents:
                try:
                    rewards_result = await client.claim_leaderboard_rewards(agent["id"])
                    claimed = rewards_result.get("rewards_claimed", 0)

                    if claimed > 0:
                        print(f"✓ {agent['config']['name']}: Claimed {claimed} VOTS")
                        individual = rewards_result.get("individual_rewards", [])
                        for reward in individual:
                            print(f"  • {reward['amount']} VOTS - {reward['reason']}")
                    else:
                        print(f"✗ {agent['config']['name']}: No rewards to claim")

                except Exception as e:
                    print(f"✗ {agent['config']['name']}: Claim failed - {e}")

            print("\n✅ Leaderboard demo completed successfully!")

        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(leaderboard_demo())
