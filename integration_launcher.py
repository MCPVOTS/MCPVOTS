#!/usr/bin/env python3
"""
MCPVots Enhanced Memory & Trilogy AGI Integration Launcher
=========================================================
Comprehensive launcher for the enhanced memory knowledge system,
Trilogy AGI fine-tuning, and automated ecosystem optimization.

This script orchestrates:
- Enhanced Memory Knowledge System
- Trilogy AGI Ollama Fine-Tuning 
- Memory MCP Integration
- Automated Ecosystem Optimization
- Continuous Learning and Improvement

Features:
- Service health monitoring
- Automated startup and recovery
- Performance analytics
- Integration status reporting
- One-command deployment
"""

import asyncio
import json
import logging
import os
import sys
import time
import signal
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import webbrowser

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import our components
try:
    from enhanced_memory_knowledge_system import EnhancedMemoryKnowledgeSystem
    from trilogy_ollama_fine_tuner import TrilogyOllamaFineTuner  
    from memory_mcp_integration import MemoryMCPIntegration
    from automated_ecosystem_optimizer import EcosystemOptimizationService
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some components not available: {e}")
    COMPONENTS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("integration_launcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegrationLauncher:
    """
    Main launcher for MCPVots Enhanced Memory & Trilogy AGI Integration
    """
    
    def __init__(self, workspace_path: str = "c:\\Workspace\\MCPVots"):
        self.workspace_path = Path(workspace_path)
        self.config_path = self.workspace_path / "integration_config.json"
        
        # Component instances
        self.memory_system = None
        self.fine_tuner = None
        self.memory_mcp = None
        self.optimizer = None
        
        # Service configuration
        self.services = {
            "memory_system": {
                "name": "Enhanced Memory Knowledge System",
                "enabled": True,
                "status": "stopped",
                "last_health_check": None
            },
            "fine_tuner": {
                "name": "Trilogy AGI Ollama Fine-Tuner",
                "enabled": True,
                "status": "stopped", 
                "last_health_check": None
            },
            "memory_mcp": {
                "name": "Memory MCP Integration",
                "enabled": True,
                "status": "stopped",
                "last_health_check": None
            },
            "optimizer": {
                "name": "Ecosystem Optimization Service",
                "enabled": True,
                "status": "stopped",
                "last_health_check": None
            }
        }
        
        # Running tasks
        self.running_tasks = {}
        self.shutdown_event = asyncio.Event()
        
        # Load configuration
        self._load_config()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self):
        """Load integration configuration"""
        default_config = {
            "startup_delay": 5,
            "health_check_interval": 60,
            "auto_restart": True,
            "max_restart_attempts": 3,
            "performance_monitoring": True,
            "web_dashboard": True,
            "dashboard_port": 8080,
            "log_level": "INFO"
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Could not load config: {e}, using defaults")
        
        self.config = default_config
        
        # Save config back to file
        self._save_config()
    
    def _save_config(self):
        """Save current configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save config: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown_event.set()
    
    async def start_integration_services(self):
        """Start all integration services"""
        logger.info("🚀 Starting MCPVots Enhanced Memory & Trilogy AGI Integration")
        logger.info("=" * 70)
        
        if not COMPONENTS_AVAILABLE:
            logger.error("❌ Required components not available")
            return False
        
        try:
            # Initialize components
            await self._initialize_components()
            
            # Start services
            await self._start_services()
            
            # Start monitoring
            await self._start_monitoring()
            
            # Start web dashboard if enabled
            if self.config["web_dashboard"]:
                await self._start_web_dashboard()
            
            # Wait for shutdown signal
            await self._wait_for_shutdown()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start integration services: {e}")
            return False
        finally:
            await self._cleanup_services()
    
    async def _initialize_components(self):
        """Initialize all components"""
        logger.info("🔧 Initializing components...")
        
        try:
            # Initialize Enhanced Memory Knowledge System
            if self.services["memory_system"]["enabled"]:
                self.memory_system = EnhancedMemoryKnowledgeSystem(str(self.workspace_path))
                logger.info("✅ Enhanced Memory Knowledge System initialized")
            
            # Initialize Trilogy AGI Fine-Tuner
            if self.services["fine_tuner"]["enabled"]:
                self.fine_tuner = TrilogyOllamaFineTuner(str(self.workspace_path))
                logger.info("✅ Trilogy AGI Fine-Tuner initialized")
            
            # Initialize Memory MCP Integration
            if self.services["memory_mcp"]["enabled"]:
                self.memory_mcp = MemoryMCPIntegration()
                logger.info("✅ Memory MCP Integration initialized")
            
            # Initialize Ecosystem Optimizer
            if self.services["optimizer"]["enabled"]:
                self.optimizer = EcosystemOptimizationService(str(self.workspace_path))
                logger.info("✅ Ecosystem Optimization Service initialized")
            
        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
            raise
    
    async def _start_services(self):
        """Start all enabled services"""
        logger.info("🚀 Starting services...")
        
        # Start Memory System
        if self.memory_system and self.services["memory_system"]["enabled"]:
            try:
                task = asyncio.create_task(
                    self.memory_system.start_continuous_learning_cycle(),
                    name="memory_system"
                )
                self.running_tasks["memory_system"] = task
                self.services["memory_system"]["status"] = "running"
                logger.info("✅ Enhanced Memory Knowledge System started")
            except Exception as e:
                logger.error(f"❌ Failed to start Memory System: {e}")
                self.services["memory_system"]["status"] = "failed"
        
        # Start Ecosystem Optimizer
        if self.optimizer and self.services["optimizer"]["enabled"]:
            try:
                task = asyncio.create_task(
                    self.optimizer.start_optimization_service(),
                    name="optimizer"
                )
                self.running_tasks["optimizer"] = task
                self.services["optimizer"]["status"] = "running"
                logger.info("✅ Ecosystem Optimization Service started")
            except Exception as e:
                logger.error(f"❌ Failed to start Ecosystem Optimizer: {e}")
                self.services["optimizer"]["status"] = "failed"
        
        # Note: Fine-tuner and Memory MCP are used on-demand, not as continuous services
        if self.fine_tuner:
            self.services["fine_tuner"]["status"] = "ready"
            logger.info("✅ Trilogy AGI Fine-Tuner ready")
        
        if self.memory_mcp:
            self.services["memory_mcp"]["status"] = "ready"
            logger.info("✅ Memory MCP Integration ready")
        
        # Wait a moment for services to initialize
        await asyncio.sleep(self.config["startup_delay"])
    
    async def _start_monitoring(self):
        """Start health monitoring"""
        logger.info("🏥 Starting health monitoring...")
        
        task = asyncio.create_task(
            self._health_monitoring_loop(),
            name="health_monitor"
        )
        self.running_tasks["health_monitor"] = task
        logger.info("✅ Health monitoring started")
    
    async def _start_web_dashboard(self):
        """Start web dashboard (placeholder)"""
        logger.info(f"🌐 Web dashboard would start on port {self.config['dashboard_port']}")
        # This would start a FastAPI or Flask web interface
        # For now, just log the intention
    
    async def _wait_for_shutdown(self):
        """Wait for shutdown signal or service failure"""
        logger.info("🔄 Services running. Press Ctrl+C to shutdown...")
        
        while not self.shutdown_event.is_set():
            try:
                # Check if any critical service has failed
                failed_services = [
                    name for name, service in self.services.items() 
                    if service["enabled"] and service["status"] == "failed"
                ]
                
                if failed_services and not self.config["auto_restart"]:
                    logger.error(f"❌ Critical services failed: {failed_services}")
                    break
                
                # Wait a bit before next check
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                break
    
    async def _health_monitoring_loop(self):
        """Continuous health monitoring of services"""
        while not self.shutdown_event.is_set():
            try:
                # Check health of running tasks
                for service_name, task in self.running_tasks.items():
                    if task.done():
                        # Task completed (possibly with error)
                        if task.exception():
                            logger.error(f"❌ Service {service_name} failed: {task.exception()}")
                            self.services[service_name]["status"] = "failed"
                            
                            # Attempt restart if enabled
                            if self.config["auto_restart"]:
                                await self._restart_service(service_name)
                        else:
                            logger.info(f"ℹ️ Service {service_name} completed normally")
                            self.services[service_name]["status"] = "completed"
                
                # Update health check timestamps
                current_time = datetime.now()
                for service in self.services.values():
                    service["last_health_check"] = current_time.isoformat()
                
                # Log status summary
                running_count = sum(1 for s in self.services.values() if s["status"] == "running")
                total_enabled = sum(1 for s in self.services.values() if s["enabled"])
                logger.debug(f"Health check: {running_count}/{total_enabled} services running")
                
                # Wait before next health check
                await asyncio.sleep(self.config["health_check_interval"])
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(30)
    
    async def _restart_service(self, service_name: str):
        """Restart a failed service"""
        logger.info(f"🔄 Attempting to restart service: {service_name}")
        
        try:
            # Cancel existing task
            if service_name in self.running_tasks:
                self.running_tasks[service_name].cancel()
                del self.running_tasks[service_name]
            
            # Restart based on service type
            if service_name == "memory_system" and self.memory_system:
                task = asyncio.create_task(
                    self.memory_system.start_continuous_learning_cycle(),
                    name="memory_system"
                )
                self.running_tasks["memory_system"] = task
                self.services["memory_system"]["status"] = "running"
                
            elif service_name == "optimizer" and self.optimizer:
                task = asyncio.create_task(
                    self.optimizer.start_optimization_service(),
                    name="optimizer"
                )
                self.running_tasks["optimizer"] = task
                self.services["optimizer"]["status"] = "running"
            
            logger.info(f"✅ Service {service_name} restarted successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to restart service {service_name}: {e}")
            self.services[service_name]["status"] = "failed"
    
    async def _cleanup_services(self):
        """Clean up all services"""
        logger.info("🧹 Cleaning up services...")
        
        # Cancel all running tasks
        for service_name, task in self.running_tasks.items():
            if not task.done():
                logger.info(f"Stopping {service_name}...")
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error stopping {service_name}: {e}")
        
        # Update service statuses
        for service in self.services.values():
            if service["status"] in ["running", "ready"]:
                service["status"] = "stopped"
        
        logger.info("✅ All services stopped")
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "services": self.services.copy(),
            "running_tasks": list(self.running_tasks.keys()),
            "config": self.config,
            "component_status": {}
        }
        
        # Get component-specific status
        try:
            if self.memory_system:
                status["component_status"]["memory_system"] = await self.memory_system.get_system_status()
        except Exception as e:
            status["component_status"]["memory_system"] = {"error": str(e)}
        
        try:
            if self.fine_tuner:
                ollama_status = await self.fine_tuner.check_ollama_status()
                deployment_status = await self.fine_tuner.get_deployment_status()
                status["component_status"]["fine_tuner"] = {
                    "ollama": ollama_status,
                    "deployments": deployment_status
                }
        except Exception as e:
            status["component_status"]["fine_tuner"] = {"error": str(e)}
        
        try:
            if self.optimizer:
                status["component_status"]["optimizer"] = await self.optimizer.get_optimization_status()
        except Exception as e:
            status["component_status"]["optimizer"] = {"error": str(e)}
        
        return status
    
    async def run_integration_tests(self) -> Dict[str, Any]:
        """Run comprehensive integration tests"""
        logger.info("🧪 Running integration tests...")
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "test_results": {}
        }
        
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Component initialization
        total_tests += 1
        try:
            if all([self.memory_system, self.fine_tuner, self.memory_mcp, self.optimizer]):
                test_results["test_results"]["component_initialization"] = {
                    "status": "passed",
                    "message": "All components initialized successfully"
                }
                tests_passed += 1
            else:
                test_results["test_results"]["component_initialization"] = {
                    "status": "failed",
                    "message": "Some components failed to initialize"
                }
        except Exception as e:
            test_results["test_results"]["component_initialization"] = {
                "status": "error",
                "message": str(e)
            }
        
        # Test 2: Ollama connectivity
        total_tests += 1
        try:
            if self.fine_tuner:
                ollama_status = await self.fine_tuner.check_ollama_status()
                if ollama_status.get("ollama_status") == "running":
                    test_results["test_results"]["ollama_connectivity"] = {
                        "status": "passed",
                        "message": f"Ollama running with {len(ollama_status.get('available_models', []))} models"
                    }
                    tests_passed += 1
                else:
                    test_results["test_results"]["ollama_connectivity"] = {
                        "status": "failed",
                        "message": f"Ollama not available: {ollama_status.get('error', 'Unknown error')}"
                    }
            else:
                test_results["test_results"]["ollama_connectivity"] = {
                    "status": "skipped",
                    "message": "Fine-tuner not initialized"
                }
        except Exception as e:
            test_results["test_results"]["ollama_connectivity"] = {
                "status": "error",
                "message": str(e)
            }
        
        # Test 3: Memory system functionality
        total_tests += 1
        try:
            if self.memory_system:
                memory_status = await self.memory_system.get_system_status()
                test_results["test_results"]["memory_system"] = {
                    "status": "passed",
                    "message": f"Memory system operational with {memory_status.get('knowledge_entities', 0)} entities"
                }
                tests_passed += 1
            else:
                test_results["test_results"]["memory_system"] = {
                    "status": "failed",
                    "message": "Memory system not initialized"
                }
        except Exception as e:
            test_results["test_results"]["memory_system"] = {
                "status": "error",
                "message": str(e)
            }
        
        # Test 4: Ecosystem optimizer
        total_tests += 1
        try:
            if self.optimizer:
                optimizer_status = await self.optimizer.get_optimization_status()
                test_results["test_results"]["ecosystem_optimizer"] = {
                    "status": "passed",
                    "message": f"Optimizer operational, system health: {optimizer_status.get('system_health', 'unknown')}"
                }
                tests_passed += 1
            else:
                test_results["test_results"]["ecosystem_optimizer"] = {
                    "status": "failed",
                    "message": "Ecosystem optimizer not initialized"
                }
        except Exception as e:
            test_results["test_results"]["ecosystem_optimizer"] = {
                "status": "error",
                "message": str(e)
            }
        
        # Calculate overall status
        if tests_passed == total_tests:
            test_results["overall_status"] = "all_passed"
        elif tests_passed > total_tests * 0.7:
            test_results["overall_status"] = "mostly_passed"
        elif tests_passed > 0:
            test_results["overall_status"] = "some_passed"
        else:
            test_results["overall_status"] = "all_failed"
        
        test_results["summary"] = {
            "tests_passed": tests_passed,
            "total_tests": total_tests,
            "pass_rate": tests_passed / total_tests if total_tests > 0 else 0
        }
        
        logger.info(f"🧪 Integration tests completed: {tests_passed}/{total_tests} passed")
        
        return test_results

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MCPVots Enhanced Memory & Trilogy AGI Integration Launcher")
    parser.add_argument("--workspace", default="c:\\Workspace\\MCPVots", help="Workspace path")
    parser.add_argument("--test-only", action="store_true", help="Run tests only, don't start services")
    parser.add_argument("--status-only", action="store_true", help="Show status only")
    parser.add_argument("--config", help="Configuration file path")
    
    args = parser.parse_args()
    
    # Initialize launcher
    launcher = IntegrationLauncher(args.workspace)
    
    if args.status_only:
        # Show status and exit
        print("📊 MCPVots Integration Status")
        print("=" * 50)
        
        try:
            await launcher._initialize_components()
            status = await launcher.get_integration_status()
            print(json.dumps(status, indent=2, default=str))
        except Exception as e:
            print(f"Error getting status: {e}")
        
        return
    
    if args.test_only:
        # Run tests and exit
        print("🧪 MCPVots Integration Tests")
        print("=" * 50)
        
        try:
            await launcher._initialize_components()
            test_results = await launcher.run_integration_tests()
            print(json.dumps(test_results, indent=2, default=str))
        except Exception as e:
            print(f"Error running tests: {e}")
        
        return
    
    # Start integration services
    print("🚀 MCPVots Enhanced Memory & Trilogy AGI Integration")
    print("=" * 60)
    print("Starting comprehensive integration services...")
    print("Features:")
    print("  ✓ Enhanced Memory Knowledge System")
    print("  ✓ Trilogy AGI Ollama Fine-Tuning")
    print("  ✓ Memory MCP Integration")
    print("  ✓ Automated Ecosystem Optimization")
    print("  ✓ Continuous Learning & Improvement")
    print("")
    
    success = await launcher.start_integration_services()
    
    if success:
        print("✅ Integration services completed successfully")
    else:
        print("❌ Integration services failed")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
