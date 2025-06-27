"""
Nautilus Service Integration for MCPVots
"""

import asyncio
import sys
from pathlib import Path

# Add nautilus integration to path
nautilus_path = Path(__file__).parent.parent.parent.parent / 'nautilus_integration'
sys.path.append(str(nautilus_path))

try:
    from nautilus_mcp_bridge import NautilusSystemOrchestrator
    NAUTILUS_AVAILABLE = True
except ImportError:
    NAUTILUS_AVAILABLE = False

class NautilusService:
    """MCPVots service wrapper for Nautilus Trader"""
    
    def __init__(self):
        self.orchestrator = None
        self.is_running = False
        
    async def start(self):
        """Start Nautilus trading system"""
        if not NAUTILUS_AVAILABLE:
            raise RuntimeError("Nautilus integration not available")
            
        self.orchestrator = NautilusSystemOrchestrator()
        await self.orchestrator.start_system()
        self.is_running = True
        
    async def stop(self):
        """Stop Nautilus trading system"""
        if self.orchestrator:
            await self.orchestrator.stop_system()
        self.is_running = False
        
    def get_status(self):
        """Get current trading status"""
        return {
            'available': NAUTILUS_AVAILABLE,
            'running': self.is_running,
            'performance': self.orchestrator.bridge.performance_metrics if self.orchestrator else {}
        }
