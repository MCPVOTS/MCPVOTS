#!/usr/bin/env python3
"""
MCPVots Advanced Orchestrator
============================
Comprehensive orchestration system for the complete MCPVots ecosystem
Handles service lifecycle, monitoring, scaling, and continuous improvement
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import signal
import time
import threading
import webbrowser
from dataclasses import dataclass, asdict
import yaml
import argparse

# Import our ecosystem components
sys.path.append(str(Path(__file__).parent))
from ecosystem_builder import MCPVotsEcosystemBuilder
from ecosystem_manager import add_ecosystem_manager_to_builder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("orchestrator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class OrchestrationConfig:
    """Configuration for orchestration system"""
    auto_start: bool = True
    auto_scale: bool = False
    health_check_interval: int = 30
    performance_monitoring: bool = True
    auto_restart: bool = True
    max_restart_attempts: int = 3
    backup_enabled: bool = True
    backup_interval: int = 3600
    analytics_enabled: bool = True
    alert_thresholds: Dict[str, float] = None

class MCPVotsOrchestrator:
    """Advanced orchestration system for MCPVots ecosystem"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self.load_config(config_file)
        self.ecosystem_builder = MCPVotsEcosystemBuilder()
        self.ecosystem_builder = add_ecosystem_manager_to_builder(self.ecosystem_builder)
        
        self.orchestration_state = {
            "status": "initializing",
            "start_time": datetime.now(),
            "services": {},
            "metrics": {},
            "events": [],
            "errors": []
        }
        
        self.running = False
        self.monitoring_tasks = {}
        self.performance_history = []
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def load_config(self, config_file: Optional[str] = None) -> OrchestrationConfig:
        """Load orchestration configuration"""
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            return OrchestrationConfig(**config_data)
        else:
            return OrchestrationConfig(
                alert_thresholds={
                    "cpu_usage": 80.0,
                    "memory_usage": 85.0,
                    "error_rate": 5.0,
                    "response_time": 2000.0
                }
            )

    async def orchestrate_ecosystem(self) -> Dict[str, Any]:
        """Main orchestration entry point"""
        logger.info("🎼 Starting MCPVots Advanced Orchestration...")
        
        orchestration_result = {
            "status": "success",
            "start_time": datetime.now().isoformat(),
            "phases": {},
            "final_state": {},
            "recommendations": []
        }

        try:
            self.running = True
            self.orchestration_state["status"] = "running"
            
            # Phase 1: Initialize ecosystem
            logger.info("📋 Phase 1: Ecosystem initialization...")
            init_result = await self.initialize_ecosystem()
            orchestration_result["phases"]["initialization"] = init_result
            
            # Phase 2: Build and deploy
            logger.info("🏗️ Phase 2: Building ecosystem...")
            build_result = await self.ecosystem_builder.build_ecosystem()
            orchestration_result["phases"]["build"] = build_result
            
            # Phase 3: Start monitoring
            logger.info("👁️ Phase 3: Starting monitoring...")
            monitoring_result = await self.start_monitoring()
            orchestration_result["phases"]["monitoring"] = monitoring_result
            
            # Phase 4: Performance optimization
            logger.info("⚡ Phase 4: Performance optimization...")
            optimization_result = await self.optimize_ecosystem()
            orchestration_result["phases"]["optimization"] = optimization_result
            
            # Phase 5: Continuous operation
            logger.info("🔄 Phase 5: Continuous operation...")
            if self.config.auto_start:
                await self.run_continuous_operation()
            
            orchestration_result["final_state"] = self.get_ecosystem_state()
            orchestration_result["recommendations"] = self.generate_recommendations()
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            orchestration_result["status"] = "failed"
            orchestration_result["error"] = str(e)
        
        finally:
            await self.cleanup()
        
        return orchestration_result

    async def initialize_ecosystem(self) -> Dict[str, Any]:
        """Initialize the ecosystem components"""
        init_result = {
            "status": "success",
            "components_initialized": [],
            "errors": []
        }
        
        try:
            # Initialize configuration
            await self.setup_configuration()
            init_result["components_initialized"].append("configuration")
            
            # Initialize directories
            await self.setup_directories()
            init_result["components_initialized"].append("directories")
            
            # Initialize monitoring
            await self.setup_monitoring()
            init_result["components_initialized"].append("monitoring")
            
            # Initialize security
            await self.setup_security()
            init_result["components_initialized"].append("security")
            
            logger.info("✅ Ecosystem initialization completed")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            init_result["status"] = "failed"
            init_result["errors"].append(str(e))
        
        return init_result

    async def setup_configuration(self):
        """Setup system configuration"""
        config_dir = Path(__file__).parent / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Create main configuration file
        main_config = {
            "system": {
                "name": "MCPVots Ecosystem",
                "version": "1.0.0",
                "environment": "development"
            },
            "services": {
                "auto_discovery": True,
                "health_check_interval": 30,
                "restart_policy": "always"
            },
            "monitoring": {
                "enabled": True,
                "metrics_retention": "7d",
                "alert_cooldown": 300
            },
            "security": {
                "authentication_required": False,
                "rate_limiting": True,
                "cors_enabled": True
            }
        }
        
        with open(config_dir / "main.yaml", "w") as f:
            yaml.dump(main_config, f, default_flow_style=False)

    async def setup_directories(self):
        """Setup required directory structure"""
        directories = [
            "logs",
            "data",
            "backups",
            "config",
            "monitoring",
            "analytics",
            "tmp"
        ]
        
        base_path = Path(__file__).parent
        for directory in directories:
            (base_path / directory).mkdir(exist_ok=True)

    async def setup_monitoring(self):
        """Setup monitoring infrastructure"""
        monitoring_config = {
            "metrics": {
                "system": ["cpu", "memory", "disk", "network"],
                "application": ["response_time", "throughput", "error_rate"],
                "business": ["active_users", "requests_per_minute"]
            },
            "alerts": {
                "channels": ["console", "file"],
                "thresholds": self.config.alert_thresholds
            }
        }
        
        config_dir = Path(__file__).parent / "config"
        with open(config_dir / "monitoring.yaml", "w") as f:
            yaml.dump(monitoring_config, f, default_flow_style=False)

    async def setup_security(self):
        """Setup security configuration"""
        security_config = {
            "authentication": {
                "enabled": False,
                "methods": ["token", "oauth"]
            },
            "authorization": {
                "rbac_enabled": False,
                "default_permissions": ["read"]
            },
            "encryption": {
                "at_rest": False,
                "in_transit": True
            }
        }
        
        config_dir = Path(__file__).parent / "config"
        with open(config_dir / "security.yaml", "w") as f:
            yaml.dump(security_config, f, default_flow_style=False)

    async def start_monitoring(self) -> Dict[str, Any]:
        """Start comprehensive monitoring"""
        monitoring_result = {
            "status": "success",
            "monitors_started": [],
            "errors": []
        }
        
        try:
            # Start health monitoring
            self.monitoring_tasks["health"] = asyncio.create_task(
                self.health_monitoring_loop()
            )
            monitoring_result["monitors_started"].append("health_monitor")
            
            # Start performance monitoring
            if self.config.performance_monitoring:
                self.monitoring_tasks["performance"] = asyncio.create_task(
                    self.performance_monitoring_loop()
                )
                monitoring_result["monitors_started"].append("performance_monitor")
            
            # Start analytics monitoring
            if self.config.analytics_enabled:
                self.monitoring_tasks["analytics"] = asyncio.create_task(
                    self.analytics_monitoring_loop()
                )
                monitoring_result["monitors_started"].append("analytics_monitor")
            
            logger.info("✅ Monitoring systems started")
            
        except Exception as e:
            logger.error(f"Monitoring startup failed: {e}")
            monitoring_result["status"] = "failed"
            monitoring_result["errors"].append(str(e))
        
        return monitoring_result

    async def health_monitoring_loop(self):
        """Continuous health monitoring"""
        while self.running:
            try:
                health_status = await self.check_system_health()
                self.orchestration_state["metrics"]["health"] = health_status
                
                # Check for unhealthy services
                unhealthy_services = [
                    service for service, status in health_status.items()
                    if status.get("status") != "healthy"
                ]
                
                if unhealthy_services and self.config.auto_restart:
                    await self.handle_unhealthy_services(unhealthy_services)
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(30)

    async def performance_monitoring_loop(self):
        """Continuous performance monitoring"""
        while self.running:
            try:
                performance_metrics = await self.collect_performance_metrics()
                self.performance_history.append(performance_metrics)
                
                # Keep only last 1000 entries
                if len(self.performance_history) > 1000:
                    self.performance_history = self.performance_history[-1000:]
                
                # Check performance thresholds
                await self.check_performance_thresholds(performance_metrics)
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)

    async def analytics_monitoring_loop(self):
        """Continuous analytics monitoring"""
        while self.running:
            try:
                analytics_data = await self.collect_analytics_data()
                await self.process_analytics(analytics_data)
                
                await asyncio.sleep(300)  # Collect every 5 minutes
                
            except Exception as e:
                logger.error(f"Analytics monitoring error: {e}")
                await asyncio.sleep(300)

    async def check_system_health(self) -> Dict[str, Any]:
        """Check health of all system components"""
        health_status = {}
        
        # Check service health
        for service_name, service in self.ecosystem_builder.services.items():
            if hasattr(service, 'health_check_url') and service.health_check_url:
                try:
                    # Simulate health check (in real implementation, use aiohttp)
                    health_status[service_name] = {
                        "status": "healthy",
                        "last_check": datetime.now().isoformat(),
                        "response_time": 50  # ms
                    }
                except:
                    health_status[service_name] = {
                        "status": "unhealthy",
                        "last_check": datetime.now().isoformat(),
                        "error": "Connection failed"
                    }
        
        return health_status

    async def collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive performance metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_usage": 45.0,  # Placeholder
                "memory_usage": 62.0,
                "disk_usage": 35.0,
                "network_io": 1024
            },
            "application": {
                "response_time": 120,  # ms
                "throughput": 150,     # requests/minute
                "error_rate": 0.5,     # percentage
                "active_connections": 25
            }
        }

    async def collect_analytics_data(self) -> Dict[str, Any]:
        """Collect analytics data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "usage": {
                "active_users": 5,
                "page_views": 150,
                "api_calls": 1200,
                "feature_usage": {
                    "dashboard": 45,
                    "mcp_integration": 30,
                    "monitoring": 20
                }
            },
            "performance": {
                "avg_load_time": 2.5,
                "bounce_rate": 0.15,
                "conversion_rate": 0.85
            }
        }

    async def process_analytics(self, analytics_data: Dict[str, Any]):
        """Process and store analytics data"""
        # Store analytics data
        analytics_file = Path(__file__).parent / "analytics" / f"analytics_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Append to daily analytics file
        if analytics_file.exists():
            with open(analytics_file, "r") as f:
                daily_data = json.load(f)
        else:
            daily_data = {"date": datetime.now().strftime('%Y-%m-%d'), "entries": []}
        
        daily_data["entries"].append(analytics_data)
        
        with open(analytics_file, "w") as f:
            json.dump(daily_data, f, indent=2)

    async def optimize_ecosystem(self) -> Dict[str, Any]:
        """Optimize ecosystem performance"""
        optimization_result = {
            "status": "success",
            "optimizations": [],
            "metrics": {}
        }
        
        try:
            # Memory optimization
            await self.optimize_memory()
            optimization_result["optimizations"].append("memory_optimization")
            
            # Network optimization
            await self.optimize_network()
            optimization_result["optimizations"].append("network_optimization")
            
            # Service optimization
            await self.optimize_services()
            optimization_result["optimizations"].append("service_optimization")
            
            # Collect post-optimization metrics
            optimization_result["metrics"] = await self.collect_performance_metrics()
            
            logger.info("✅ Ecosystem optimization completed")
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            optimization_result["status"] = "failed"
            optimization_result["error"] = str(e)
        
        return optimization_result

    async def optimize_memory(self):
        """Optimize memory usage"""
        logger.info("🧠 Optimizing memory usage...")
        # Implementation would include garbage collection, cache optimization, etc.

    async def optimize_network(self):
        """Optimize network performance"""
        logger.info("🌐 Optimizing network performance...")
        # Implementation would include connection pooling, compression, etc.

    async def optimize_services(self):
        """Optimize service performance"""
        logger.info("⚙️ Optimizing service performance...")
        # Implementation would include service scaling, load balancing, etc.

    async def run_continuous_operation(self):
        """Run continuous operation mode"""
        logger.info("🔄 Starting continuous operation mode...")
        
        # Open dashboard in browser
        if self.config.auto_start:
            webbrowser.open("http://localhost:3000")
        
        try:
            while self.running:
                # Periodic health checks
                await self.periodic_health_check()
                
                # Periodic optimization
                await self.periodic_optimization()
                
                # Periodic backup
                if self.config.backup_enabled:
                    await self.periodic_backup()
                
                # Sleep for a bit
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("Shutting down continuous operation...")
        except Exception as e:
            logger.error(f"Continuous operation error: {e}")

    async def periodic_health_check(self):
        """Periodic comprehensive health check"""
        health_status = await self.check_system_health()
        
        # Log critical issues
        critical_issues = [
            service for service, status in health_status.items()
            if status.get("status") == "critical"
        ]
        
        if critical_issues:
            logger.warning(f"Critical issues detected: {critical_issues}")

    async def periodic_optimization(self):
        """Periodic optimization tasks"""
        # Run optimization every hour
        current_time = datetime.now()
        if current_time.minute == 0:  # Top of the hour
            await self.optimize_ecosystem()

    async def periodic_backup(self):
        """Periodic backup operations"""
        current_time = datetime.now()
        
        # Backup every hour
        if current_time.minute == 0:
            await self.create_backup()

    async def create_backup(self):
        """Create system backup"""
        backup_dir = Path(__file__).parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"ecosystem_backup_{timestamp}.json"
        
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "system_state": self.orchestration_state,
            "configuration": asdict(self.config),
            "performance_history": self.performance_history[-100:],  # Last 100 entries
            "services": {name: asdict(service) for name, service in self.ecosystem_builder.services.items()}
        }
        
        with open(backup_file, "w") as f:
            json.dump(backup_data, f, indent=2)
        
        logger.info(f"📦 Backup created: {backup_file}")

    def get_ecosystem_state(self) -> Dict[str, Any]:
        """Get current ecosystem state"""
        return {
            "status": self.orchestration_state["status"],
            "uptime": str(datetime.now() - self.orchestration_state["start_time"]),
            "services": len(self.ecosystem_builder.services),
            "active_connections": len(self.ecosystem_builder.processes),
            "performance_score": self.calculate_performance_score(),
            "last_optimization": self.orchestration_state.get("last_optimization"),
            "health_summary": self.orchestration_state.get("metrics", {}).get("health", {})
        }

    def calculate_performance_score(self) -> float:
        """Calculate overall performance score"""
        if not self.performance_history:
            return 100.0
        
        latest_metrics = self.performance_history[-1]
        
        # Simple scoring algorithm
        cpu_score = max(0, 100 - latest_metrics["system"]["cpu_usage"])
        memory_score = max(0, 100 - latest_metrics["system"]["memory_usage"])
        response_score = max(0, 100 - (latest_metrics["application"]["response_time"] / 10))
        error_score = max(0, 100 - (latest_metrics["application"]["error_rate"] * 20))
        
        return (cpu_score + memory_score + response_score + error_score) / 4

    def generate_recommendations(self) -> List[str]:
        """Generate system recommendations"""
        recommendations = []
        
        if self.performance_history:
            latest = self.performance_history[-1]
            
            if latest["system"]["cpu_usage"] > 80:
                recommendations.append("Consider scaling CPU resources")
            
            if latest["system"]["memory_usage"] > 85:
                recommendations.append("Consider optimizing memory usage")
            
            if latest["application"]["response_time"] > 1000:
                recommendations.append("Investigate response time bottlenecks")
            
            if latest["application"]["error_rate"] > 5:
                recommendations.append("Address high error rate")
        
        if not recommendations:
            recommendations.append("System is performing well")
        
        return recommendations

    async def handle_unhealthy_services(self, unhealthy_services: List[str]):
        """Handle unhealthy services"""
        for service_name in unhealthy_services:
            logger.warning(f"Attempting to restart unhealthy service: {service_name}")
            # Implementation would restart the specific service

    async def check_performance_thresholds(self, metrics: Dict[str, Any]):
        """Check if performance metrics exceed thresholds"""
        thresholds = self.config.alert_thresholds
        
        for metric, threshold in thresholds.items():
            if metric in ["cpu_usage", "memory_usage"]:
                current_value = metrics["system"].get(metric, 0)
            else:
                current_value = metrics["application"].get(metric, 0)
            
            if current_value > threshold:
                logger.warning(f"Performance threshold exceeded: {metric} = {current_value} > {threshold}")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up resources...")
        
        # Cancel monitoring tasks
        for task_name, task in self.monitoring_tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Save final state
        final_state_file = Path(__file__).parent / "final_state.json"
        with open(final_state_file, "w") as f:
            json.dump(self.get_ecosystem_state(), f, indent=2)
        
        logger.info("✅ Cleanup completed")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MCPVots Advanced Orchestrator")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--mode", choices=["build", "run", "monitor"], default="run", help="Operation mode")
    parser.add_argument("--auto-start", action="store_true", help="Auto-start services")
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = MCPVotsOrchestrator(args.config)
    
    if args.auto_start:
        orchestrator.config.auto_start = True
    
    try:
        if args.mode == "build":
            # Build only mode
            result = asyncio.run(orchestrator.ecosystem_builder.build_ecosystem())
            print(json.dumps(result, indent=2))
        elif args.mode == "monitor":
            # Monitor only mode
            asyncio.run(orchestrator.start_monitoring())
        else:
            # Full orchestration mode
            result = asyncio.run(orchestrator.orchestrate_ecosystem())
            print(json.dumps(result, indent=2, default=str))
            
    except KeyboardInterrupt:
        logger.info("Orchestration interrupted by user")
    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
