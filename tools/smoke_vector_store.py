#!/usr/bin/env python3
import asyncio
from ethermax_chromadb import get_chromadb_instance

W1 = "0x1111111111111111111111111111111111111111"
W2 = "0x2222222222222222222222222222222222222222"

async def main():
    chroma = await get_chromadb_instance()

    # Add identity
    await chroma.add_identity_tracking(
        W1,
        {
            "identity_type": "test",
            "confidence_score": 0.42,
            "risk_level": "low",
            "behavioral_patterns": {
                "trading_frequency": 3,
                "avg_transaction_size": 1.2,
                "preferred_tokens": ["MAXX"],
                "timing_patterns": {
                    "most_active_hours": [1, 2],
                    "day_of_week_patterns": [1],
                    "coordination_timing": "none",
                },
                "coordination_score": 0.1,
            },
        },
    )

    # Add funding connection
    await chroma.add_funding_connection(
        W1,
        W2,
        {
            "relationship_type": "test",
            "relationship_metrics": {
                "relationship_strength": 0.2,
                "frequency_score": 0.1,
                "amount_consistency": 0.3,
            },
            "transaction_details": {"amount_eth": 0.01, "gas_used": 21000},
            "manipulation_indicators": {"circular_funding": False, "wash_trading_score": 0},
        },
    )

    # Add trade history
    await chroma.add_trade_history(
        W1,
        {
            "trade_details": {
                "amount_maxx": 1000,
                "amount_eth": 0.002,
                "slippage_percent": 0.5,
                "trade_type": "BUY",
            },
            "performance_metrics": {"pnl_percent": 0.0, "holding_period_minutes": 0},
            "market_conditions": {"price_impact_percent": 0.1, "volume_24h": 10000},
            "manipulation_analysis": {"coordinated_buying": False, "volume_spike": False},
        },
    )

    stats = await chroma.get_collection_stats()
    print("VECTOR_STORE_STATS", stats)
    await chroma.close()

if __name__ == "__main__":
    asyncio.run(main())
