#!/usr/bin/env python3
"""
Store MAXX Mini-App Update Guide in MCP Memory System
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import the memory store directly
from maxx_memory_mcp_server import get_memory_store, VectorMemoryStore

async def store_mini_app_guide():
    """Store comprehensive guide for updating MAXX mini-app"""

    store = get_memory_store()

    # Generate a simple vector (in production, use embeddings)
    def simple_vector(text: str, dim: int = 128) -> list:
        """Generate simple vector from text hash"""
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        # Convert to float vector
        vector = []
        for i in range(dim):
            byte_val = hash_bytes[i % len(hash_bytes)]
            vector.append((byte_val / 255.0) - 0.5)  # Normalize to -0.5 to 0.5
        return vector

    guide_entries = [
        {
            "content": """MAXX Mini-App Core Architecture:
- Framework: Next.js 15.5.6 with App Router and TypeScript
- Wallet: RainbowKit v2.2.9 with multi-network support
- Blockchain: Wagmi v2.18.1 + Viem v2.38.3 for Ethereum interactions
- Styling: Tailwind CSS with responsive breakpoints
- 3D Effects: Three.js v0.180.0 for cyberpunk particle background
- Real-time: WebSocket connection to MAXX trading bot backend
- Networks: Base (primary), Ethereum, Sepolia, Polygon, Arbitrum, Optimism""",
            "category": "system",
            "metadata": {"type": "architecture", "priority": "high"}
        },

        {
            "content": """File Structure for MAXX Mini-App:
app/
├── page.tsx          # Main dashboard with wallet, trading data, Base names
├── providers.tsx     # RainbowKit provider with 6-network configuration
└── components/       # Reusable UI components (DemoComponents.tsx)

Key Configuration Files:
- package.json: RainbowKit v2.2.9, Wagmi v2.18.1, Three.js dependencies
- tailwind.config.js: Custom cyberpunk colors and animations
- .vscode/mcp.json: MCP server configuration for memory management""",
            "category": "system",
            "metadata": {"type": "file_structure", "priority": "high"}
        },

        {
            "content": """Adding New Networks to Wallet:
1. Import chain from 'viem/chains' in app/providers.tsx
2. Add to chains array in getDefaultConfig (Base always first)
3. Test wallet modal displays new network
4. Update MCP_MEMORY_CURRENT.md with network changes

Example:
import { base, mainnet, polygon } from 'viem/chains';
const config = getDefaultConfig({
  chains: [base, mainnet, polygon], // Add new chains here
  // ... other config
});""",
            "category": "trading",
            "metadata": {"type": "network_config", "priority": "medium"}
        },

        {
            "content": """Wallet Button Styling Updates:
Location: app/page.tsx ConnectButton.Custom component

Current styling: cyberpunk-button with neon effects, compact px-3 py-1 text-sm
Responsive classes: max-w-sm sm:max-w-md for different screen sizes

To modify:
1. Update className in button element
2. Test on mobile/desktop breakpoints
3. Ensure Base name resolution still works
4. Check wallet modal positioning""",
            "category": "system",
            "metadata": {"type": "ui_styling", "priority": "medium"}
        },

        {
            "content": """Base Name Resolution Implementation:
Contract: 0x4cCb0BB02FCABA27e82a56646E81d8c5bC4119a5 (Basenames)
Network: Only works on Base network (chainId 8453)

Code pattern:
const { data: baseName } = useReadContract({
  address: '0x4cCb0BB02FCABA27e82a56646E81d8c5bC4119a5',
  abi: BasenamesAbi,
  functionName: 'getName',
  args: [account?.address],
  chainId: base.id,
});

Fallback: truncateAddress(account?.address) if no Base name""",
            "category": "system",
            "metadata": {"type": "base_names", "priority": "high"}
        },

        {
            "content": """Responsive Design Patterns:
Breakpoints: sm:640px, md:768px, lg:1024px, xl:1280px

Container pattern:
<div className="max-w-sm sm:max-w-md md:max-w-lg lg:max-w-xl">

Grid layouts:
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

Always test on actual mobile devices, not just browser dev tools.""",
            "category": "system",
            "metadata": {"type": "responsive_design", "priority": "medium"}
        },

        {
            "content": """Testing Wallet Functionality:
1. Start dev server: npm run dev
2. Open wallet modal - verify all 6 networks appear
3. Test connection on each network
4. Switch networks and verify persistence
5. Check Base name resolution on Base network
6. Test responsive design: mobile (384px), tablet (448px), desktop (576px+)
7. Verify WebSocket connection to MAXX bot
8. Test wallet disconnection/reconnection
9. Check Three.js performance on mobile devices""",
            "category": "analysis",
            "metadata": {"type": "testing", "priority": "high"}
        },

        {
            "content": """WebSocket Integration for Real-time Data:
Connection: ws://localhost:8080 (MAXX bot backend)
Data: Live tick data, performance metrics, trading status

Error handling needed:
- Connection drops
- Invalid data format
- Backend unavailable
- Mobile network issues

Reconnection logic: Exponential backoff, max retry attempts""",
            "category": "system",
            "metadata": {"type": "websocket", "priority": "medium"}
        },

        {
            "content": """Performance Optimization Checklist:
1. Three.js background: Lazy load on desktop only
2. WebSocket: Implement reconnection with backoff
3. Bundle size: Code split large components
4. Images: Optimize and lazy load
5. Mobile: Reduce animations on slow devices
6. Memory: Clean up event listeners and timers

Monitor: Chrome DevTools Performance tab, Lighthouse scores""",
            "category": "system",
            "metadata": {"type": "performance", "priority": "medium"}
        },

        {
            "content": """Troubleshooting Common Issues:

Wallet modal not showing networks:
- Check chains array in providers.tsx
- Verify RainbowKit version compatibility
- Check browser console for errors

Base names not resolving:
- Must be connected to Base network
- Contract address: 0x4cCb0BB02FCABA27e82a56646E81d8c5bC4119a5
- ABI must include getName function

WebSocket connection issues:
- MAXX bot must be running on port 8080
- Check firewall settings
- Verify WebSocket URL in component""",
            "category": "analysis",
            "metadata": {"type": "troubleshooting", "priority": "high"}
        }
    ]

    print("Storing MAXX Mini-App Update Guide in memory system...")

    stored_count = 0
    for entry in guide_entries:
        try:
            vector = simple_vector(entry["content"])
            memory_id = store.store_memory(
                content=entry["content"],
                vector=vector,
                metadata=entry["metadata"],
                category=entry["category"]
            )
            stored_count += 1
            print(f"✓ Stored memory {memory_id}: {entry['metadata']['type']}")
        except Exception as e:
            print(f"✗ Failed to store memory: {e}")

    print(f"\n✅ Successfully stored {stored_count} guide entries in MCP memory system!")

    # Test retrieval
    print("\n🔍 Testing memory retrieval...")
    test_vector = simple_vector("wallet configuration")
    results = store.search_similar(test_vector, limit=3)

    print(f"Found {len(results)} similar memories for 'wallet configuration':")
    for result in results:
        print(f"  - {result['metadata'].get('type', 'unknown')}: {result['content'][:100]}...")

if __name__ == "__main__":
    asyncio.run(store_mini_app_guide())