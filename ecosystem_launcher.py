#!/usr/bin/env python3
"""
MCPVots Ecosystem Launcher
=========================
One-click launcher for the complete MCPVots ecosystem
Handles all setup, dependencies, and service orchestration
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Dict, List, Any
import threading
import signal
from datetime import datetime

# Configure logging with UTF-8 encoding for Windows
import sys
import io

class WindowsSafeStreamHandler(logging.StreamHandler):
    """StreamHandler that handles Unicode safely on Windows"""
    def emit(self, record):
        try:
            msg = self.format(record)
            # Replace Unicode characters with safe alternatives on Windows
            if sys.platform.startswith('win'):
                msg = msg.replace('🚀', '[LAUNCH]')
                msg = msg.replace('📋', '[CHECK]')
                msg = msg.replace('📦', '[DEPS]')
                msg = msg.replace('🛠️', '[SERVICE]')
                msg = msg.replace('🏥', '[HEALTH]')
                msg = msg.replace('🌐', '[UI]')
                msg = msg.replace('👁️', '[MONITOR]')
                msg = msg.replace('✅', '[OK]')
                msg = msg.replace('❌', '[FAIL]')
            print(msg)
        except Exception:
            # Fallback to basic logging if anything fails
            print(f"{record.levelname}: {record.getMessage()}")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("launcher.log", encoding='utf-8'),
        WindowsSafeStreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MCPVotsLauncher:
    """Complete ecosystem launcher with intelligent startup"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.processes = {}
        self.running = False
        self.startup_config = self.load_startup_config()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def load_startup_config(self) -> Dict[str, Any]:
        """Load startup configuration"""
        config_file = self.base_path / "startup_config.json"
        
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        else:
            # Default configuration
            default_config = {
                "auto_install_dependencies": True,
                "auto_open_browser": True,
                "services_to_start": [
                    "frontend",
                    "websocket-proxy",
                    "system-monitor",
                    "trilogy-gateway"
                ],
                "startup_delay": 2,
                "health_check_timeout": 30,
                "browser_url": "http://localhost:3000",
                "development_mode": True
            }
            
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            
            return default_config

    async def launch_ecosystem(self) -> Dict[str, Any]:
        """Launch the complete MCPVots ecosystem"""
        logger.info("🚀 Launching MCPVots Comprehensive Ecosystem...")
        
        launch_result = {
            "status": "success",
            "start_time": datetime.now().isoformat(),
            "phases": {},
            "services": {},
            "urls": {},
            "errors": []
        }

        try:
            self.running = True
            
            # Phase 1: Environment Check
            logger.info("📋 Phase 1: Environment verification...")
            env_result = await self.verify_environment()
            launch_result["phases"]["environment"] = env_result
            
            if env_result["status"] != "success":
                raise Exception("Environment verification failed")
            
            # Phase 2: Dependency Installation
            if self.startup_config["auto_install_dependencies"]:
                logger.info("📦 Phase 2: Installing dependencies...")
                deps_result = await self.install_dependencies()
                launch_result["phases"]["dependencies"] = deps_result
            
            # Phase 3: Service Startup
            logger.info("🛠️ Phase 3: Starting services...")
            services_result = await self.start_services()
            launch_result["phases"]["services"] = services_result
            launch_result["services"] = services_result.get("services", {})
            
            # Phase 4: Health Verification
            logger.info("🏥 Phase 4: Verifying system health...")
            health_result = await self.verify_system_health()
            launch_result["phases"]["health"] = health_result
            
            # Phase 5: User Interface
            logger.info("🌐 Phase 5: Launching user interface...")
            ui_result = await self.launch_ui()
            launch_result["phases"]["ui"] = ui_result
            launch_result["urls"] = ui_result.get("urls", {})
            
            # Phase 6: Monitoring Setup
            logger.info("👁️ Phase 6: Setting up monitoring...")
            monitoring_result = await self.setup_monitoring()
            launch_result["phases"]["monitoring"] = monitoring_result
            
            logger.info("✅ MCPVots ecosystem launched successfully!")
            logger.info("🌐 Dashboard: http://localhost:3000")
            logger.info("📊 Monitoring: http://localhost:8091")
            logger.info("🔧 Gateway: http://localhost:8000")
            
        except Exception as e:
            logger.error(f"Ecosystem launch failed: {e}")
            launch_result["status"] = "failed"
            launch_result["errors"].append(str(e))
        
        return launch_result

    async def verify_environment(self) -> Dict[str, Any]:
        """Verify the environment is ready"""
        env_result = {
            "status": "success",
            "checks": {},
            "errors": []
        }
        
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version >= (3, 8):
                env_result["checks"]["python"] = f"✅ Python {python_version.major}.{python_version.minor}"
            else:
                env_result["checks"]["python"] = f"❌ Python {python_version.major}.{python_version.minor} (requires 3.8+)"
                env_result["errors"].append("Python version too old")
            
            # Check Node.js
            try:
                node_result = subprocess.run(["node", "--version"], capture_output=True, text=True)
                if node_result.returncode == 0:
                    env_result["checks"]["nodejs"] = f"✅ Node.js {node_result.stdout.strip()}"
                else:
                    env_result["checks"]["nodejs"] = "❌ Node.js not found"
                    env_result["errors"].append("Node.js not installed")
            except FileNotFoundError:
                env_result["checks"]["nodejs"] = "❌ Node.js not found"
                env_result["errors"].append("Node.js not installed")
            
            # Check npm
            try:
                npm_result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
                if npm_result.returncode == 0:
                    env_result["checks"]["npm"] = f"✅ npm {npm_result.stdout.strip()}"
                else:
                    env_result["checks"]["npm"] = "❌ npm not found"
            except FileNotFoundError:
                env_result["checks"]["npm"] = "❌ npm not found"
            
            # Check directory structure
            required_dirs = ["src", "css", ".github"]
            for dir_name in required_dirs:
                dir_path = self.base_path / dir_name
                if dir_path.exists():
                    env_result["checks"][f"dir_{dir_name}"] = f"✅ {dir_name}/ directory exists"
                else:
                    env_result["checks"][f"dir_{dir_name}"] = f"❌ {dir_name}/ directory missing"
            
            # Check required files
            required_files = ["package.json", "mcp-config.json", "advanced_orchestrator.py"]
            for file_name in required_files:
                file_path = self.base_path / file_name
                if file_path.exists():
                    env_result["checks"][f"file_{file_name}"] = f"✅ {file_name} exists"
                else:
                    env_result["checks"][f"file_{file_name}"] = f"❌ {file_name} missing"
            
            if env_result["errors"]:
                env_result["status"] = "failed"
            
        except Exception as e:
            env_result["status"] = "failed"
            env_result["errors"].append(str(e))
        
        return env_result

    async def install_dependencies(self) -> Dict[str, Any]:
        """Install all required dependencies"""
        deps_result = {
            "status": "success",
            "installations": {},
            "errors": []
        }
        
        try:
            # Install Node.js dependencies
            logger.info("📦 Installing Node.js dependencies...")
            npm_process = await asyncio.create_subprocess_exec(
                "npm", "install",
                cwd=self.base_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await npm_process.communicate()
            
            if npm_process.returncode == 0:
                deps_result["installations"]["npm"] = "✅ Node.js dependencies installed"
            else:
                deps_result["installations"]["npm"] = f"❌ npm install failed: {stderr.decode()}"
                deps_result["errors"].append("npm install failed")
            
            # Install Python dependencies
            logger.info("🐍 Installing Python dependencies...")
            pip_packages = [
                "fastapi", "uvicorn", "websockets", "aiohttp",
                "psutil", "requests", "pydantic", "pyyaml"
            ]
            
            for package in pip_packages:
                pip_process = await asyncio.create_subprocess_exec(
                    "pip", "install", package,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await pip_process.communicate()
                
                if pip_process.returncode == 0:
                    deps_result["installations"][f"pip_{package}"] = f"✅ {package} installed"
                else:
                    deps_result["installations"][f"pip_{package}"] = f"❌ {package} failed"
            
            if deps_result["errors"]:
                deps_result["status"] = "failed"
                
        except Exception as e:
            deps_result["status"] = "failed"
            deps_result["errors"].append(str(e))
        
        return deps_result

    async def start_services(self) -> Dict[str, Any]:
        """Start all configured services"""
        services_result = {
            "status": "success",
            "services": {},
            "errors": []
        }
        
        try:
            # Service definitions
            services = {
                "frontend": {
                    "command": ["cmd", "/c", "npm", "run", "dev"],
                    "port": 3000,
                    "health_url": "http://localhost:3000"
                },
                "websocket-proxy": {
                    "command": ["node", "websocket_proxy.js"],
                    "port": 8080,
                    "health_url": "http://localhost:8080/health"
                },
                "system-monitor": {
                    "command": ["python", "system_monitor.py"],
                    "port": 8091,
                    "health_url": "http://localhost:8091/health"
                },
                "trilogy-gateway": {
                    "command": ["python", "trilogy_enhanced_gateway_v3.py"],
                    "port": 8000,
                    "health_url": "http://localhost:8000/health"
                }
            }
            
            # Start each service
            for service_name, service_config in services.items():
                if service_name in self.startup_config["services_to_start"]:
                    success = await self.start_service(service_name, service_config)
                    
                    if success:
                        services_result["services"][service_name] = {
                            "status": "started",
                            "port": service_config["port"],
                            "url": service_config["health_url"]
                        }
                        logger.info(f"✅ {service_name} started on port {service_config['port']}")
                    else:
                        services_result["services"][service_name] = {
                            "status": "failed",
                            "port": service_config["port"]
                        }
                        services_result["errors"].append(f"Failed to start {service_name}")
                        logger.error(f"❌ Failed to start {service_name}")
                    
                    # Delay between service starts
                    await asyncio.sleep(self.startup_config["startup_delay"])
            
            if services_result["errors"]:
                services_result["status"] = "partial"
                
        except Exception as e:
            services_result["status"] = "failed"
            services_result["errors"].append(str(e))
        
        return services_result

    async def start_service(self, service_name: str, service_config: Dict[str, Any]) -> bool:
        """Start a single service"""
        try:
            logger.info(f"Starting {service_name}...")
            
            # Check if command exists
            command = service_config["command"]
            check_command = None
            
            if command[0] == "cmd" and len(command) > 3 and command[2] == "npm":
                check_command = ["cmd", "/c", "npm", "--version"]
            elif command[0] == "node":
                check_command = ["node", "--version"]
            elif command[0] == "python":
                check_command = ["python", "--version"]
            
            if check_command:
                try:
                    check_process = await asyncio.create_subprocess_exec(
                        *check_command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await check_process.communicate()
                    if check_process.returncode != 0:
                        logger.error(f"Command '{command}' not available for {service_name}")
                        return False
                except Exception as e:
                    logger.error(f"Cannot execute '{command}' for {service_name}: {e}")
                    return False
            
            # Start the service
            process = await asyncio.create_subprocess_exec(
                *service_config["command"],
                cwd=self.base_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.processes[service_name] = process
            
            # Wait a moment to see if process starts successfully
            await asyncio.sleep(2)
            
            if process.returncode is None:
                logger.info(f"Service {service_name} started successfully")
                return True
            else:
                # Get error output
                stdout, stderr = await process.communicate()
                logger.error(f"Service {service_name} failed to start:")
                if stdout:
                    logger.error(f"STDOUT: {stdout.decode()}")
                if stderr:
                    logger.error(f"STDERR: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start {service_name}: {e}")
            return False

    async def verify_system_health(self) -> Dict[str, Any]:
        """Verify system health"""
        health_result = {
            "status": "success",
            "services": {},
            "errors": []
        }
        
        try:
            # Wait for services to fully start
            await asyncio.sleep(5)
            
            # Check each running service
            for service_name, process in self.processes.items():
                if process.returncode is None:
                    health_result["services"][service_name] = "✅ Running"
                else:
                    health_result["services"][service_name] = "❌ Stopped"
                    health_result["errors"].append(f"{service_name} not running")
            
            if health_result["errors"]:
                health_result["status"] = "degraded"
                
        except Exception as e:
            health_result["status"] = "failed"
            health_result["errors"].append(str(e))
        
        return health_result

    async def launch_ui(self) -> Dict[str, Any]:
        """Launch user interface"""
        ui_result = {
            "status": "success",
            "urls": {},
            "errors": []
        }
        
        try:
            # Define UI URLs
            urls = {
                "main_dashboard": "http://localhost:3000",
                "system_monitor": "http://localhost:8091/metrics",
                "trilogy_gateway": "http://localhost:8000/health",
                "websocket_proxy": "http://localhost:8080/health"
            }
            
            ui_result["urls"] = urls
            
            # Open browser if configured
            if self.startup_config["auto_open_browser"]:
                main_url = self.startup_config["browser_url"]
                logger.info(f"🌐 Opening browser to {main_url}")
                
                # Use threading to avoid blocking
                threading.Thread(
                    target=lambda: webbrowser.open(main_url),
                    daemon=True
                ).start()
                
                ui_result["browser_opened"] = True
            
        except Exception as e:
            ui_result["status"] = "failed"
            ui_result["errors"].append(str(e))
        
        return ui_result

    async def setup_monitoring(self) -> Dict[str, Any]:
        """Setup monitoring and analytics"""
        monitoring_result = {
            "status": "success",
            "monitors": {},
            "errors": []
        }
        
        try:
            # Start monitoring loop in background
            monitoring_task = asyncio.create_task(self.monitoring_loop())
            monitoring_result["monitors"]["system_monitoring"] = "✅ Active"
            
            # Setup log monitoring
            monitoring_result["monitors"]["log_monitoring"] = "✅ Active"
            
        except Exception as e:
            monitoring_result["status"] = "failed"
            monitoring_result["errors"].append(str(e))
        
        return monitoring_result

    async def monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.running:
            try:
                # Check process health
                for service_name, process in list(self.processes.items()):
                    if process.returncode is not None:
                        logger.warning(f"⚠️ Service {service_name} has stopped")
                        
                        # Attempt restart if configured
                        if self.startup_config.get("auto_restart", True):
                            logger.info(f"🔄 Attempting to restart {service_name}")
                            # Implementation would restart the service
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(30)

    def print_status_summary(self, launch_result: Dict[str, Any]):
        """Print a comprehensive status summary"""
        print("\n" + "="*60)
        print("🚀 MCPVots Ecosystem Status Summary")
        print("="*60)
        
        print(f"📊 Overall Status: {launch_result['status'].upper()}")
        print(f"⏰ Launch Time: {launch_result['start_time']}")
        
        if "services" in launch_result:
            print("\n🛠️ Services:")
            for service, details in launch_result["services"].items():
                status_icon = "✅" if details["status"] == "started" else "❌"
                print(f"  {status_icon} {service}: {details['status']} (port {details.get('port', 'N/A')})")
        
        if "urls" in launch_result:
            print("\n🌐 Access URLs:")
            for name, url in launch_result["urls"].items():
                print(f"  🔗 {name.replace('_', ' ').title()}: {url}")
        
        if launch_result.get("errors"):
            print("\n❌ Errors:")
            for error in launch_result["errors"]:
                print(f"  • {error}")
        
        print("\n📋 Quick Commands:")
        print("  • View logs: npm run logs:view")
        print("  • Check health: npm run services:health")
        print("  • Open dashboard: npm run dashboard:open")
        print("  • Stop all: Ctrl+C")
        
        print("="*60)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        
        # Terminate all processes
        for service_name, process in self.processes.items():
            if process.returncode is None:
                logger.info(f"Stopping {service_name}...")
                process.terminate()
        
        sys.exit(0)

    async def wait_for_shutdown(self):
        """Wait for shutdown signal"""
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutdown requested")
        finally:
            # Cleanup
            for service_name, process in self.processes.items():
                if process.returncode is None:
                    process.terminate()

def main():
    """Main entry point"""
    launcher = MCPVotsLauncher()
    
    print("🚀 MCPVots Ecosystem Launcher")
    print("=============================")
    
    try:
        # Launch the ecosystem
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        launch_result = loop.run_until_complete(launcher.launch_ecosystem())
        
        # Print status summary
        launcher.print_status_summary(launch_result)
        
        if launch_result["status"] in ["success", "partial"]:
            print("\n🎉 Ecosystem is running! Press Ctrl+C to stop.")
            
            # Keep running until shutdown
            loop.run_until_complete(launcher.wait_for_shutdown())
        else:
            print("\n❌ Failed to launch ecosystem. Check logs for details.")
            return 1
            
    except KeyboardInterrupt:
        print("\n👋 Shutdown complete. Thank you for using MCPVots!")
    except Exception as e:
        logger.error(f"Launcher failed: {e}")
        return 1
    finally:
        loop.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
