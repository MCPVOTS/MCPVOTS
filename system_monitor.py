#!/usr/bin/env python3
"""
System Monitor for MCPVots Ecosystem
====================================
Monitors system resources, services, and health metrics
Provides REST API endpoints for monitoring data
"""

import asyncio
import json
import logging
import os
import psutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import aiohttp
from aiohttp import web
import threading
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """Comprehensive system monitoring service"""
    
    def __init__(self, port=8091):
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.site = None
        self.running = False
        self.metrics_history = []
        self.max_history_size = 1000
        self.services_config = self.load_services_config()
        
        # Setup routes
        self.setup_routes()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/health', self.health_handler)
        self.app.router.add_get('/metrics', self.metrics_handler)
        self.app.router.add_get('/system', self.system_handler)
        self.app.router.add_get('/services', self.services_handler)
        self.app.router.add_get('/history', self.history_handler)
        self.app.router.add_get('/dashboard', self.dashboard_handler)

    def load_services_config(self) -> Dict[str, Any]:
        """Load services configuration"""
        try:
            config_file = Path(__file__).parent / "startup_config.json"
            if config_file.exists():
                with open(config_file) as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load services config: {e}")
        
        return {
            "services_to_monitor": [
                {"name": "frontend", "port": 3000},
                {"name": "websocket-proxy", "port": 8080},
                {"name": "trilogy-gateway", "port": 8000}
            ]
        }

    async def health_handler(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "uptime": time.time() - self.start_time,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })

    async def metrics_handler(self, request):
        """Current system metrics"""
        metrics = await self.collect_metrics()
        return web.json_response(metrics)

    async def system_handler(self, request):
        """Detailed system information"""
        system_info = await self.get_system_info()
        return web.json_response(system_info)

    async def services_handler(self, request):
        """Service status information"""
        services_status = await self.check_services_status()
        return web.json_response(services_status)

    async def history_handler(self, request):
        """Historical metrics data"""
        limit = int(request.query.get('limit', 100))
        history = self.metrics_history[-limit:] if self.metrics_history else []
        return web.json_response({
            "history": history,
            "total_points": len(self.metrics_history),
            "returned": len(history)
        })

    async def dashboard_handler(self, request):
        """Simple dashboard HTML"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MCPVots System Monitor</title>
            <meta http-equiv="refresh" content="5">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
                .metric { text-align: center; padding: 10px; background: #e3f2fd; border-radius: 4px; }
                .metric-value { font-size: 24px; font-weight: bold; color: #1976d2; }
                .metric-label { color: #666; font-size: 12px; }
                .status-good { color: #4caf50; }
                .status-warning { color: #ff9800; }
                .status-error { color: #f44336; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>MCPVots System Monitor</h1>
                <div class="card">
                    <h2>System Status</h2>
                    <div id="status">Loading...</div>
                </div>
            </div>
            <script>
                async function updateStatus() {
                    try {
                        const [metrics, services] = await Promise.all([
                            fetch('/metrics').then(r => r.json()),
                            fetch('/services').then(r => r.json())
                        ]);
                        
                        document.getElementById('status').innerHTML = `
                            <div class="metrics">
                                <div class="metric">
                                    <div class="metric-value">${metrics.cpu_percent.toFixed(1)}%</div>
                                    <div class="metric-label">CPU Usage</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value">${metrics.memory_percent.toFixed(1)}%</div>
                                    <div class="metric-label">Memory Usage</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value">${metrics.disk_percent.toFixed(1)}%</div>
                                    <div class="metric-label">Disk Usage</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value">${services.healthy_services}/${services.total_services}</div>
                                    <div class="metric-label">Services Online</div>
                                </div>
                            </div>
                        `;
                    } catch (error) {
                        console.error('Failed to update status:', error);
                    }
                }
                updateStatus();
                setInterval(updateStatus, 5000);
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')

    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "memory_percent": memory_percent,
                "memory_used_gb": round(memory_used_gb, 2),
                "memory_total_gb": round(memory_total_gb, 2),
                "disk_percent": disk_percent,
                "disk_used_gb": round(disk_used_gb, 2),
                "disk_total_gb": round(disk_total_gb, 2),
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "process_count": process_count
            }
            
            # Store in history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history = self.metrics_history[-self.max_history_size:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        try:
            return {
                "platform": psutil.sys.platform,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "uptime_seconds": time.time() - psutil.boot_time(),
                "python_version": psutil.sys.version,
                "cpu_info": {
                    "physical_cores": psutil.cpu_count(logical=False),
                    "logical_cores": psutil.cpu_count(logical=True),
                    "current_freq": psutil.cpu_freq().current if psutil.cpu_freq() else None
                },
                "memory_info": dict(psutil.virtual_memory()._asdict()),
                "disk_partitions": [dict(partition._asdict()) for partition in psutil.disk_partitions()]
            }
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {"error": str(e)}

    async def check_services_status(self) -> Dict[str, Any]:
        """Check status of monitored services"""
        services_status = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "healthy_services": 0,
            "total_services": 0
        }
        
        try:
            services_to_check = self.services_config.get("services_to_monitor", [])
            services_status["total_services"] = len(services_to_check)
            
            for service in services_to_check:
                service_name = service["name"]
                port = service["port"]
                
                try:
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                        health_url = f"http://localhost:{port}/health"
                        async with session.get(health_url) as response:
                            if response.status == 200:
                                services_status["services"][service_name] = {
                                    "status": "healthy",
                                    "port": port,
                                    "response_time": response.headers.get('X-Response-Time'),
                                    "last_check": datetime.now().isoformat()
                                }
                                services_status["healthy_services"] += 1
                            else:
                                services_status["services"][service_name] = {
                                    "status": "unhealthy",
                                    "port": port,
                                    "error": f"HTTP {response.status}",
                                    "last_check": datetime.now().isoformat()
                                }
                except Exception as e:
                    services_status["services"][service_name] = {
                        "status": "unreachable",
                        "port": port,
                        "error": str(e),
                        "last_check": datetime.now().isoformat()
                    }
            
        except Exception as e:
            logger.error(f"Failed to check services status: {e}")
            services_status["error"] = str(e)
        
        return services_status

    async def start(self):
        """Start the monitoring server"""
        self.start_time = time.time()
        self.running = True
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = web.TCPSite(self.runner, 'localhost', self.port)
        await self.site.start()
        
        logger.info(f"System Monitor started on http://localhost:{self.port}")
        logger.info(f"Dashboard available at http://localhost:{self.port}/dashboard")

    async def stop(self):
        """Stop the monitoring server"""
        self.running = False
        
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        
        logger.info("System Monitor stopped")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.stop())

async def main():
    """Main entry point"""
    monitor = SystemMonitor()
    
    try:
        await monitor.start()
        
        # Keep running until interrupted
        while monitor.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Monitor error: {e}")
    finally:
        await monitor.stop()

if __name__ == "__main__":
    asyncio.run(main())
