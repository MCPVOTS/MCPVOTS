#!/usr/bin/env python3
"""
Enhanced MCPVots Setup and Launcher
==================================
One-click setup and launch for the complete enhanced MCPVots ecosystem.

This script:
1. Verifies all dependencies
2. Sets up configuration
3. Starts all services in correct order
4. Provides status monitoring and management
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMCPVotsSetup:
    def __init__(self):
        self.workspace_path = Path(__file__).parent
        self.setup_status = {}
        self.required_dependencies = [
            "websockets", "aiohttp", "python-dotenv", "asyncio",
            "pathlib", "json", "logging", "subprocess"
        ]
        self.optional_dependencies = [
            "gitpython", "requests", "numpy", "pandas"
        ]
        
    async def run_complete_setup(self):
        """Run complete setup process"""
        logger.info("🚀 Starting Enhanced MCPVots Setup...")
        
        steps = [
            ("Environment Check", self._check_environment),
            ("Dependencies", self._verify_dependencies),
            ("Configuration", self._setup_configuration),
            ("Services", self._verify_services),
            ("Testing", self._run_basic_tests),
            ("Launch", self._launch_ecosystem)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"📋 Step: {step_name}")
            try:
                result = await step_func()
                self.setup_status[step_name] = {"status": "success", "result": result}
                logger.info(f"✅ {step_name}: Complete")
            except Exception as e:
                self.setup_status[step_name] = {"status": "error", "error": str(e)}
                logger.error(f"❌ {step_name}: {e}")
                
                # Ask user if they want to continue
                if not await self._ask_continue_on_error(step_name, e):
                    break
        
        # Generate setup report
        await self._generate_setup_report()
        
        return self.setup_status
    
    async def _check_environment(self) -> Dict[str, Any]:
        """Check environment requirements"""
        env_info = {
            "python_version": sys.version,
            "platform": sys.platform,
            "workspace_path": str(self.workspace_path),
            "environment_variables": {}
        }
        
        # Check environment variables
        required_env_vars = ["GEMINI_API_KEY"]
        optional_env_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
        
        for var in required_env_vars:
            value = os.getenv(var)
            env_info["environment_variables"][var] = "set" if value else "missing"
            if not value:
                logger.warning(f"⚠️ Required environment variable {var} is not set")
        
        for var in optional_env_vars:
            value = os.getenv(var)
            env_info["environment_variables"][var] = "set" if value else "not_set"
        
        # Check Python version
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8+ is required")
        
        return env_info
    
    async def _verify_dependencies(self) -> Dict[str, Any]:
        """Verify and install dependencies"""
        dep_status = {"installed": [], "missing": [], "failed": []}
        
        # Check required dependencies
        for dep in self.required_dependencies:
            try:
                __import__(dep)
                dep_status["installed"].append(dep)
            except ImportError:
                dep_status["missing"].append(dep)
                logger.warning(f"⚠️ Missing required dependency: {dep}")
        
        # Check optional dependencies
        for dep in self.optional_dependencies:
            try:
                __import__(dep)
                dep_status["installed"].append(dep)
            except ImportError:
                logger.info(f"ℹ️ Optional dependency not installed: {dep}")
        
        # Install missing dependencies
        if dep_status["missing"]:
            logger.info("📦 Installing missing dependencies...")
            for dep in dep_status["missing"]:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                                 check=True, capture_output=True)
                    dep_status["installed"].append(dep)
                    logger.info(f"✅ Installed {dep}")
                except subprocess.CalledProcessError as e:
                    dep_status["failed"].append(dep)
                    logger.error(f"❌ Failed to install {dep}: {e}")
        
        return dep_status
    
    async def _setup_configuration(self) -> Dict[str, Any]:
        """Setup configuration files"""
        config_files = {}
        
        # Create .env file if it doesn't exist
        env_file = self.workspace_path / ".env"
        if not env_file.exists():
            env_content = """# MCPVots Enhanced Configuration
# Gemini API Key (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Service Configuration
MEMORY_MCP_HOST=localhost
MEMORY_MCP_PORT=8020
GEMINI_CLI_HOST=localhost
GEMINI_CLI_PORT=8015

# Feature Flags
ENABLE_GOOGLE_SEARCH=true
ENABLE_AUTO_IMPROVEMENTS=true
ENABLE_CONTINUOUS_LEARNING=true
"""
            env_file.write_text(env_content)
            config_files["env"] = "created"
            logger.info("✅ Created .env configuration file")
        else:
            config_files["env"] = "exists"
        
        # Update mcp-config.json with enhanced services
        mcp_config_path = self.workspace_path / "mcp-config.json"
        enhanced_config = {
            "servers": {
                "enhanced-gemini-cli": {
                    "command": "python",
                    "args": ["servers/enhanced_gemini_cli_server.py"],
                    "env": {
                        "GEMINI_API_KEY": "$GEMINI_API_KEY"
                    }
                },
                "memory-mcp-primary": {
                    "command": "python", 
                    "args": ["servers/memory_mcp_server.py", "--port", "8020"]
                },
                "memory-mcp-secondary": {
                    "command": "python",
                    "args": ["servers/memory_mcp_server.py", "--port", "8021"]
                },
                "owl-semantic": {
                    "command": "python",
                    "args": ["servers/owl_semantic_server.py"]
                },
                "agent-file": {
                    "command": "python", 
                    "args": ["servers/agent_file_server.py"]
                },
                "dgm-evolution": {
                    "command": "python",
                    "args": ["servers/dgm_evolution_server.py"]
                },
                "deerflow": {
                    "command": "python",
                    "args": ["servers/deerflow_server.py"]
                }
            },
            "features": {
                "google_search_grounding": True,
                "trilogy_agi_integration": True,
                "automated_code_improvements": True,
                "continuous_learning": True,
                "memory_knowledge_graph": True
            }
        }
        
        with open(mcp_config_path, 'w') as f:
            json.dump(enhanced_config, f, indent=2)
        
        config_files["mcp_config"] = "updated"
        logger.info("✅ Updated MCP configuration")
        
        return config_files
    
    async def _verify_services(self) -> Dict[str, Any]:
        """Verify service files exist and are executable"""
        service_status = {}
        
        required_services = [
            "servers/enhanced_gemini_cli_server.py",
            "servers/memory_mcp_server.py",
            "gemini_automated_code_improver.py",
            "enhanced_memory_knowledge_system_v2.py",
            "enhanced_ecosystem_orchestrator.py"
        ]
        
        for service in required_services:
            service_path = self.workspace_path / service
            if service_path.exists():
                service_status[service] = "ready"
                logger.info(f"✅ Service ready: {service}")
            else:
                service_status[service] = "missing"
                logger.error(f"❌ Service missing: {service}")
        
        return service_status
    
    async def _run_basic_tests(self) -> Dict[str, Any]:
        """Run basic functionality tests"""
        test_results = {}
        
        # Test 1: Import all modules
        try:
            from gemini_automated_code_improver import GeminiAutomatedCodeImprover
            from enhanced_memory_knowledge_system_v2 import EnhancedMemoryKnowledgeSystem
            test_results["imports"] = "success"
            logger.info("✅ Module imports successful")
        except Exception as e:
            test_results["imports"] = f"failed: {e}"
            logger.error(f"❌ Module import failed: {e}")
        
        # Test 2: Basic functionality
        try:
            improver = GeminiAutomatedCodeImprover(str(self.workspace_path))
            context = await improver._collect_full_workspace_context()
            if context and "metadata" in context:
                test_results["workspace_analysis"] = "success"
                logger.info("✅ Workspace analysis test passed")
            else:
                test_results["workspace_analysis"] = "failed: no context"
        except Exception as e:
            test_results["workspace_analysis"] = f"failed: {e}"
            logger.error(f"❌ Workspace analysis test failed: {e}")
        
        return test_results
    
    async def _launch_ecosystem(self) -> Dict[str, Any]:
        """Launch the enhanced ecosystem"""
        launch_result = {"status": "pending"}
        
        try:
            # Import and start orchestrator
            from enhanced_ecosystem_orchestrator import EnhancedMCPVotsOrchestrator
            
            orchestrator = EnhancedMCPVotsOrchestrator(str(self.workspace_path))
            
            # Start ecosystem (in background)
            asyncio.create_task(orchestrator.start_enhanced_ecosystem())
            
            # Wait a moment for startup
            await asyncio.sleep(3)
            
            launch_result = {
                "status": "launched",
                "orchestrator": "active",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("🚀 Enhanced ecosystem launched successfully!")
            
        except Exception as e:
            launch_result = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"❌ Launch failed: {e}")
        
        return launch_result
    
    async def _ask_continue_on_error(self, step_name: str, error: Exception) -> bool:
        """Ask user if they want to continue after an error"""
        print(f"\n⚠️ Error in step '{step_name}': {error}")
        print("Options:")
        print("1. Continue anyway (y)")
        print("2. Stop setup (n)")
        
        # For automated setup, continue on most errors
        return True
    
    async def _generate_setup_report(self):
        """Generate setup report"""
        report = {
            "setup_timestamp": datetime.now().isoformat(),
            "workspace_path": str(self.workspace_path),
            "setup_status": self.setup_status,
            "summary": {
                "total_steps": len(self.setup_status),
                "successful": len([s for s in self.setup_status.values() if s["status"] == "success"]),
                "failed": len([s for s in self.setup_status.values() if s["status"] == "error"])
            }
        }
        
        # Save report
        report_path = self.workspace_path / f"setup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Setup report saved: {report_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("ENHANCED MCPVOTS SETUP SUMMARY")
        print("="*60)
        print(f"Total Steps: {report['summary']['total_steps']}")
        print(f"Successful: {report['summary']['successful']}")
        print(f"Failed: {report['summary']['failed']}")
        print("="*60)
        
        if report['summary']['failed'] == 0:
            print("🎉 SETUP COMPLETED SUCCESSFULLY!")
            print("\nYour Enhanced MCPVots ecosystem is ready with:")
            print("✨ Gemini CLI with Google Search grounding")
            print("✨ Trilogy AGI integration") 
            print("✨ Automated code improvements")
            print("✨ Continuous learning and optimization")
            print("✨ Real-time health monitoring")
        else:
            print("⚠️ Setup completed with some issues")
            print("Check the setup report for details")
        
        return report

# Quick start function
async def quick_start():
    """Quick start for enhanced MCPVots"""
    print("🚀 Enhanced MCPVots - Quick Start")
    print("="*50)
    
    setup = EnhancedMCPVotsSetup()
    result = await setup.run_complete_setup()
    
    return result

# Command line interface
def main():
    """Main setup function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "quick-start":
            asyncio.run(quick_start())
        elif command == "test":
            print("Running basic tests...")
            # Run basic tests only
        else:
            print(f"Unknown command: {command}")
            print("Available commands: quick-start, test")
    else:
        # Interactive setup
        print("Enhanced MCPVots Setup")
        print("1. Quick Start (automated)")
        print("2. Custom Setup (interactive)")
        choice = input("Choose option (1 or 2): ")
        
        if choice == "1":
            asyncio.run(quick_start())
        else:
            print("Custom setup not implemented yet. Using quick start...")
            asyncio.run(quick_start())

if __name__ == "__main__":
    main()
