#!/usr/bin/env python3
"""
MCPVots Enhanced Memory & Trilogy AGI Setup Script
=================================================
Automated setup and configuration for the enhanced memory knowledge system,
Trilogy AGI fine-tuning, and ecosystem optimization.

This script will:
1. Check system requirements
2. Install dependencies
3. Configure services
4. Set up databases and storage
5. Initialize components
6. Run integration tests
7. Start services
"""

import asyncio
import json
import logging
import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPVotsSetup:
    """Setup manager for MCPVots Enhanced Memory & Trilogy AGI Integration"""
    
    def __init__(self, workspace_path: str = "c:\\Workspace\\MCPVots"):
        self.workspace_path = Path(workspace_path)
        self.requirements = {
            "python_version": (3, 8),
            "required_packages": [
                "aiohttp",
                "asyncio", 
                "sqlite3",
                "websockets",
                "psutil",
                "numpy",
                "requests"
            ],
            "optional_packages": [
                "gitpython",
                "neo4j",
                "redis"
            ],
            "system_requirements": {
                "memory_gb": 4,
                "disk_gb": 10,
                "cpu_cores": 2
            }
        }
        
        self.setup_status = {
            "system_check": False,
            "dependencies": False,
            "directories": False,
            "databases": False,
            "configuration": False,
            "services": False,
            "tests": False
        }
    
    async def run_complete_setup(self) -> bool:
        """Run the complete setup process"""
        logger.info("🚀 Starting MCPVots Enhanced Memory & Trilogy AGI Setup")
        logger.info("=" * 60)
        
        try:
            # Step 1: System requirements check
            if not await self._check_system_requirements():
                logger.error("❌ System requirements not met")
                return False
            
            # Step 2: Install dependencies
            if not await self._install_dependencies():
                logger.error("❌ Dependency installation failed")
                return False
            
            # Step 3: Create directory structure
            if not await self._create_directories():
                logger.error("❌ Directory creation failed")
                return False
            
            # Step 4: Initialize databases
            if not await self._initialize_databases():
                logger.error("❌ Database initialization failed")
                return False
            
            # Step 5: Create configuration files
            if not await self._create_configuration():
                logger.error("❌ Configuration creation failed")
                return False
            
            # Step 6: Check external services
            if not await self._check_external_services():
                logger.warning("⚠️ Some external services not available")
            
            # Step 7: Run integration tests
            if not await self._run_setup_tests():
                logger.error("❌ Setup tests failed")
                return False
            
            # Step 8: Create startup scripts
            if not await self._create_startup_scripts():
                logger.error("❌ Startup script creation failed")
                return False
            
            logger.info("✅ MCPVots Enhanced Memory & Trilogy AGI Setup completed successfully!")
            logger.info("")
            logger.info("🎯 Next Steps:")
            logger.info("1. Start Ollama service: 'ollama serve'")
            logger.info("2. Run integration: 'python integration_launcher.py'")
            logger.info("3. Check status: 'python integration_launcher.py --status-only'")
            logger.info("4. Run tests: 'python integration_launcher.py --test-only'")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    async def _check_system_requirements(self) -> bool:
        """Check system requirements"""
        logger.info("🔍 Checking system requirements...")
        
        try:
            # Check Python version
            python_version = sys.version_info[:2]
            required_version = self.requirements["python_version"]
            
            if python_version < required_version:
                logger.error(f"Python {required_version[0]}.{required_version[1]}+ required, found {python_version[0]}.{python_version[1]}")
                return False
            
            logger.info(f"✅ Python version: {python_version[0]}.{python_version[1]}")
            
            # Check available memory
            try:
                import psutil
                memory_gb = psutil.virtual_memory().total / (1024**3)
                required_memory = self.requirements["system_requirements"]["memory_gb"]
                
                if memory_gb < required_memory:
                    logger.warning(f"⚠️ Low memory: {memory_gb:.1f}GB available, {required_memory}GB recommended")
                else:
                    logger.info(f"✅ Memory: {memory_gb:.1f}GB available")
            except ImportError:
                logger.warning("⚠️ Could not check memory requirements (psutil not installed)")
            
            # Check disk space
            try:
                disk_usage = shutil.disk_usage(self.workspace_path.parent)
                disk_gb = disk_usage.free / (1024**3)
                required_disk = self.requirements["system_requirements"]["disk_gb"]
                
                if disk_gb < required_disk:
                    logger.warning(f"⚠️ Low disk space: {disk_gb:.1f}GB free, {required_disk}GB required")
                else:
                    logger.info(f"✅ Disk space: {disk_gb:.1f}GB free")
            except Exception as e:
                logger.warning(f"⚠️ Could not check disk space: {e}")
            
            # Check CPU cores
            try:
                import os
                cpu_cores = os.cpu_count()
                required_cores = self.requirements["system_requirements"]["cpu_cores"]
                
                if cpu_cores < required_cores:
                    logger.warning(f"⚠️ Low CPU cores: {cpu_cores} available, {required_cores} recommended")
                else:
                    logger.info(f"✅ CPU cores: {cpu_cores} available")
            except Exception as e:
                logger.warning(f"⚠️ Could not check CPU cores: {e}")
            
            self.setup_status["system_check"] = True
            return True
            
        except Exception as e:
            logger.error(f"System requirements check failed: {e}")
            return False
    
    async def _install_dependencies(self) -> bool:
        """Install required Python packages"""
        logger.info("📦 Installing dependencies...")
        
        try:
            # Check which packages are already installed
            installed_packages = []
            missing_packages = []
            
            for package in self.requirements["required_packages"]:
                try:
                    __import__(package)
                    installed_packages.append(package)
                except ImportError:
                    missing_packages.append(package)
            
            logger.info(f"✅ Already installed: {len(installed_packages)} packages")
            
            if missing_packages:
                logger.info(f"📥 Installing {len(missing_packages)} missing packages...")
                
                # Create requirements.txt for missing packages
                requirements_content = "\n".join([
                    "aiohttp>=3.8.0",
                    "websockets>=10.0",
                    "psutil>=5.8.0", 
                    "numpy>=1.21.0",
                    "requests>=2.25.0"
                ])
                
                requirements_file = self.workspace_path / "requirements_enhanced.txt"
                with open(requirements_file, 'w') as f:
                    f.write(requirements_content)
                
                # Install using pip
                cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("✅ Required packages installed successfully")
                else:
                    logger.error(f"❌ Package installation failed: {result.stderr}")
                    return False
            
            # Try to install optional packages
            for package in self.requirements["optional_packages"]:
                try:
                    if package == "gitpython":
                        subprocess.run([sys.executable, "-m", "pip", "install", "GitPython"], 
                                     capture_output=True, check=False)
                    elif package == "neo4j":
                        subprocess.run([sys.executable, "-m", "pip", "install", "neo4j"], 
                                     capture_output=True, check=False)
                    elif package == "redis":
                        subprocess.run([sys.executable, "-m", "pip", "install", "redis"], 
                                     capture_output=True, check=False)
                except Exception:
                    logger.warning(f"⚠️ Optional package {package} could not be installed")
            
            self.setup_status["dependencies"] = True
            return True
            
        except Exception as e:
            logger.error(f"Dependency installation failed: {e}")
            return False
    
    async def _create_directories(self) -> bool:
        """Create required directory structure"""
        logger.info("📁 Creating directory structure...")
        
        try:
            directories = [
                "data",
                "models", 
                "fine_tuned",
                "training_data",
                "logs",
                "optimization_reports",
                "backups",
                "config",
                "scripts",
                "docs"
            ]
            
            for dirname in directories:
                dir_path = self.workspace_path / dirname
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created directory: {dir_path}")
            
            logger.info(f"✅ Created {len(directories)} directories")
            
            self.setup_status["directories"] = True
            return True
            
        except Exception as e:
            logger.error(f"Directory creation failed: {e}")
            return False
    
    async def _initialize_databases(self) -> bool:
        """Initialize SQLite databases"""
        logger.info("🗄️ Initializing databases...")
        
        try:
            import sqlite3
            
            databases = [
                "enhanced_memory.db",
                "fine_tuning.db", 
                "ecosystem_optimizer.db"
            ]
            
            for db_name in databases:
                db_path = self.workspace_path / "data" / db_name
                
                # Create database with basic structure
                with sqlite3.connect(db_path) as conn:
                    conn.execute("SELECT 1")  # Test connection
                
                logger.debug(f"Initialized database: {db_name}")
            
            logger.info(f"✅ Initialized {len(databases)} databases")
            
            self.setup_status["databases"] = True
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    async def _create_configuration(self) -> bool:
        """Create configuration files"""
        logger.info("⚙️ Creating configuration files...")
        
        try:
            # Integration configuration
            integration_config = {
                "startup_delay": 5,
                "health_check_interval": 60,
                "auto_restart": True,
                "max_restart_attempts": 3,
                "performance_monitoring": True,
                "web_dashboard": True,
                "dashboard_port": 8080,
                "log_level": "INFO"
            }
            
            with open(self.workspace_path / "integration_config.json", 'w') as f:
                json.dump(integration_config, f, indent=2)
            
            # Memory system configuration
            memory_config = {
                "fine_tuning_threshold": 50,
                "confidence_threshold": 0.7,
                "batch_size": 10,
                "learning_rate": 0.001,
                "validation_split": 0.2
            }
            
            with open(self.workspace_path / "memory_config.json", 'w') as f:
                json.dump(memory_config, f, indent=2)
            
            # Optimization configuration
            optimization_config = {
                "monitoring_interval": 30,
                "optimization_interval": 300,
                "git_monitoring": True,
                "auto_deployment": False,
                "performance_thresholds": {
                    "cpu_usage": 80.0,
                    "memory_usage": 85.0,
                    "disk_usage": 90.0,
                    "response_time": 2.0,
                    "error_rate": 0.05
                }
            }
            
            with open(self.workspace_path / "optimization_config.json", 'w') as f:
                json.dump(optimization_config, f, indent=2)
            
            # Environment variables template
            env_template = """# MCPVots Enhanced Memory & Trilogy AGI Configuration
# Copy this to .env and update with your values

# Gemini API Key (for advanced analysis)
GEMINI_API_KEY=your_gemini_api_key_here

# Ollama Configuration
OLLAMA_ENDPOINT=http://localhost:11434

# Memory MCP Configuration
MEMORY_MCP_PRIMARY=ws://localhost:8020
MEMORY_MCP_SECONDARY=ws://localhost:8021

# Neo4j Configuration (if using)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# Redis Configuration (if using)
REDIS_URL=redis://localhost:6379

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/integration.log
"""
            
            with open(self.workspace_path / ".env.example", 'w') as f:
                f.write(env_template)
            
            logger.info("✅ Configuration files created")
            
            self.setup_status["configuration"] = True
            return True
            
        except Exception as e:
            logger.error(f"Configuration creation failed: {e}")
            return False
    
    async def _check_external_services(self) -> bool:
        """Check external service availability"""
        logger.info("🔗 Checking external services...")
        
        services_status = {}
        
        # Check Ollama
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                services_status["ollama"] = {
                    "status": "available",
                    "models": len(models)
                }
                logger.info(f"✅ Ollama available with {len(models)} models")
            else:
                services_status["ollama"] = {"status": "error", "code": response.status_code}
                logger.warning("⚠️ Ollama returned error status")
        except Exception as e:
            services_status["ollama"] = {"status": "unavailable", "error": str(e)}
            logger.warning("⚠️ Ollama not available - install and start Ollama service")
        
        # Check Neo4j (if available)
        try:
            import requests
            response = requests.get("http://localhost:7474", timeout=3)
            services_status["neo4j"] = {"status": "available"}
            logger.info("✅ Neo4j available")
        except Exception:
            services_status["neo4j"] = {"status": "unavailable"}
            logger.info("ℹ️ Neo4j not available (optional)")
        
        # Check Redis (if available)
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            services_status["redis"] = {"status": "available"}
            logger.info("✅ Redis available")
        except Exception:
            services_status["redis"] = {"status": "unavailable"}
            logger.info("ℹ️ Redis not available (optional)")
        
        # Save services status
        with open(self.workspace_path / "config" / "services_status.json", 'w') as f:
            json.dump(services_status, f, indent=2)
        
        return True
    
    async def _run_setup_tests(self) -> bool:
        """Run basic setup tests"""
        logger.info("🧪 Running setup tests...")
        
        try:
            test_results = {}
            
            # Test 1: Import components
            try:
                from enhanced_memory_knowledge_system import EnhancedMemoryKnowledgeSystem
                from trilogy_ollama_fine_tuner import TrilogyOllamaFineTuner
                from memory_mcp_integration import MemoryMCPIntegration
                from automated_ecosystem_optimizer import EcosystemOptimizationService
                
                test_results["component_imports"] = "passed"
                logger.info("✅ Component imports successful")
            except ImportError as e:
                test_results["component_imports"] = f"failed: {e}"
                logger.error(f"❌ Component import failed: {e}")
                return False
            
            # Test 2: Database connectivity
            try:
                import sqlite3
                for db_name in ["enhanced_memory.db", "fine_tuning.db", "ecosystem_optimizer.db"]:
                    db_path = self.workspace_path / "data" / db_name
                    with sqlite3.connect(db_path) as conn:
                        conn.execute("SELECT 1")
                
                test_results["database_connectivity"] = "passed"
                logger.info("✅ Database connectivity test passed")
            except Exception as e:
                test_results["database_connectivity"] = f"failed: {e}"
                logger.error(f"❌ Database connectivity test failed: {e}")
                return False
            
            # Test 3: Configuration files
            try:
                config_files = [
                    "integration_config.json",
                    "memory_config.json", 
                    "optimization_config.json"
                ]
                
                for config_file in config_files:
                    config_path = self.workspace_path / config_file
                    if not config_path.exists():
                        raise FileNotFoundError(f"Config file missing: {config_file}")
                    
                    with open(config_path, 'r') as f:
                        json.load(f)  # Validate JSON
                
                test_results["configuration_files"] = "passed"
                logger.info("✅ Configuration files test passed")
            except Exception as e:
                test_results["configuration_files"] = f"failed: {e}"
                logger.error(f"❌ Configuration files test failed: {e}")
                return False
            
            # Test 4: Directory structure
            try:
                required_dirs = ["data", "models", "fine_tuned", "training_data", "logs"]
                for dirname in required_dirs:
                    dir_path = self.workspace_path / dirname
                    if not dir_path.exists():
                        raise FileNotFoundError(f"Directory missing: {dirname}")
                
                test_results["directory_structure"] = "passed"
                logger.info("✅ Directory structure test passed")
            except Exception as e:
                test_results["directory_structure"] = f"failed: {e}"
                logger.error(f"❌ Directory structure test failed: {e}")
                return False
            
            # Save test results
            with open(self.workspace_path / "logs" / "setup_tests.json", 'w') as f:
                json.dump(test_results, f, indent=2)
            
            self.setup_status["tests"] = True
            logger.info("✅ All setup tests passed")
            return True
            
        except Exception as e:
            logger.error(f"Setup tests failed: {e}")
            return False
    
    async def _create_startup_scripts(self) -> bool:
        """Create startup scripts"""
        logger.info("📜 Creating startup scripts...")
        
        try:
            # Windows batch script
            batch_script = """@echo off
echo Starting MCPVots Enhanced Memory ^& Trilogy AGI Integration
echo ============================================================

cd /d "%~dp0"

echo Checking Python...
python --version
if errorlevel 1 (
    echo Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo Starting integration services...
python integration_launcher.py

pause
"""
            
            with open(self.workspace_path / "start_integration.bat", 'w') as f:
                f.write(batch_script)
            
            # PowerShell script
            ps_script = """# MCPVots Enhanced Memory & Trilogy AGI Integration Launcher
Write-Host "Starting MCPVots Enhanced Memory & Trilogy AGI Integration" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Set-Location $PSScriptRoot

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "Python version: $pythonVersion" -ForegroundColor Blue
} catch {
    Write-Host "Python not found! Please install Python 3.8+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start services
Write-Host "Starting integration services..." -ForegroundColor Yellow
python integration_launcher.py

Read-Host "Press Enter to exit"
"""
            
            with open(self.workspace_path / "start_integration.ps1", 'w') as f:
                f.write(ps_script)
            
            # Linux/macOS shell script
            shell_script = """#!/bin/bash
echo "Starting MCPVots Enhanced Memory & Trilogy AGI Integration"
echo "============================================================"

cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found! Please install Python 3.8+"
    exit 1
fi

echo "Python version: $(python3 --version)"

# Start services
echo "Starting integration services..."
python3 integration_launcher.py
"""
            
            with open(self.workspace_path / "start_integration.sh", 'w') as f:
                f.write(shell_script)
            
            # Make shell script executable (on Unix-like systems)
            try:
                import stat
                script_path = self.workspace_path / "start_integration.sh"
                script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
            except Exception:
                pass  # Windows or other issue
            
            # Create status check script
            status_script = """#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from integration_launcher import IntegrationLauncher

async def main():
    launcher = IntegrationLauncher()
    await launcher._initialize_components()
    status = await launcher.get_integration_status()
    
    print("MCPVots Integration Status")
    print("=" * 30)
    
    for service_name, service_info in status["services"].items():
        status_emoji = "✅" if service_info["status"] in ["running", "ready"] else "❌"
        print(f"{status_emoji} {service_info['name']}: {service_info['status']}")
    
    print(f"\\nRunning tasks: {len(status['running_tasks'])}")
    if status["running_tasks"]:
        for task in status["running_tasks"]:
            print(f"  - {task}")

if __name__ == "__main__":
    asyncio.run(main())
"""
            
            with open(self.workspace_path / "check_status.py", 'w') as f:
                f.write(status_script)
            
            logger.info("✅ Startup scripts created")
            
            self.setup_status["services"] = True
            return True
            
        except Exception as e:
            logger.error(f"Startup script creation failed: {e}")
            return False
    
    async def get_setup_status(self) -> Dict[str, Any]:
        """Get current setup status"""
        return {
            "setup_status": self.setup_status,
            "workspace_path": str(self.workspace_path),
            "completion_percentage": sum(self.setup_status.values()) / len(self.setup_status) * 100,
            "next_steps": self._get_next_steps()
        }
    
    def _get_next_steps(self) -> List[str]:
        """Get recommended next steps based on setup status"""
        steps = []
        
        if not self.setup_status["system_check"]:
            steps.append("Run system requirements check")
        elif not self.setup_status["dependencies"]:
            steps.append("Install required dependencies")
        elif not self.setup_status["directories"]:
            steps.append("Create directory structure")
        elif not self.setup_status["databases"]:
            steps.append("Initialize databases")
        elif not self.setup_status["configuration"]:
            steps.append("Create configuration files")
        elif not self.setup_status["tests"]:
            steps.append("Run setup tests")
        elif not self.setup_status["services"]:
            steps.append("Create startup scripts")
        else:
            steps.extend([
                "Install and start Ollama: 'ollama serve'",
                "Run integration: 'python integration_launcher.py'",
                "Check status: 'python check_status.py'"
            ])
        
        return steps

async def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="MCPVots Enhanced Memory & Trilogy AGI Setup")
    parser.add_argument("--workspace", default="c:\\Workspace\\MCPVots", help="Workspace path")
    parser.add_argument("--status-only", action="store_true", help="Show setup status only")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies only")
    
    args = parser.parse_args()
    
    setup = MCPVotsSetup(args.workspace)
    
    if args.status_only:
        status = await setup.get_setup_status()
        print("MCPVots Setup Status")
        print("=" * 30)
        print(json.dumps(status, indent=2))
        return
    
    if args.check_deps:
        success = await setup._check_system_requirements()
        if success:
            await setup._install_dependencies()
        return
    
    # Run complete setup
    success = await setup.run_complete_setup()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("\nTo get started:")
        print("1. Start Ollama: 'ollama serve'")
        print("2. Run integration: 'python integration_launcher.py'")
        print("3. Or use startup script: './start_integration.bat' (Windows) or './start_integration.sh' (Linux/macOS)")
    else:
        print("\n❌ Setup failed. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
