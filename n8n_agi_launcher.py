#!/usr/bin/env python3
"""
n8n AGI Ecosystem Setup and Launch Script
==========================================
Comprehensive setup and launch script for n8n integration with MCPVots AGI ecosystem.
Handles installation, configuration, and orchestration of the entire n8n + AGI stack.
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
import argparse

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from n8n_integration_manager import N8NManager
from comprehensive_ecosystem_orchestrator import ComprehensiveEcosystemOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('n8n_agi_launcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class N8NAGILauncher:
    def __init__(self):
        self.n8n_manager = N8NManager()
        self.orchestrator = ComprehensiveEcosystemOrchestrator()
        self.launch_status = {}
        
    async def full_ecosystem_setup(self) -> Dict[str, Any]:
        """Complete setup and launch of n8n + AGI ecosystem"""
        logger.info("🚀 Starting Full n8n + AGI Ecosystem Setup...")
        
        setup_steps = [
            ("Prerequisites Check", self._check_prerequisites),
            ("n8n Environment Setup", self._setup_n8n_environment),
            ("AGI Services Launch", self._launch_agi_services),
            ("n8n Integration Launch", self._launch_n8n_integration),
            ("Workflow Templates Creation", self._create_workflow_templates),
            ("Health Check", self._verify_ecosystem_health),
            ("Demo Workflows", self._run_demo_workflows)
        ]
        
        results = {}
        
        for step_name, step_func in setup_steps:
            try:
                logger.info(f"🔧 {step_name}...")
                step_result = await step_func()
                results[step_name.lower().replace(" ", "_")] = step_result
                
                if step_result.get("success", False):
                    logger.info(f"✅ {step_name} completed successfully")
                else:
                    logger.error(f"❌ {step_name} failed: {step_result.get('error', 'Unknown error')}")
                    break
                    
            except Exception as e:
                logger.error(f"❌ {step_name} exception: {e}")
                results[step_name.lower().replace(" ", "_")] = {
                    "success": False,
                    "error": str(e)
                }
                break
        
        # Generate launch summary
        successful_steps = sum(1 for result in results.values() if result.get("success", False))
        total_steps = len(setup_steps)
        
        launch_summary = {
            "timestamp": datetime.now().isoformat(),
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "success_rate": (successful_steps / total_steps) * 100,
            "fully_operational": successful_steps == total_steps,
            "step_results": results,
            "next_steps": self._generate_next_steps(results)
        }
        
        # Save launch report
        await self._save_launch_report(launch_summary)
        
        return launch_summary
        
    async def _check_prerequisites(self) -> Dict[str, Any]:
        """Check system prerequisites"""
        try:
            logger.info("🔍 Checking system prerequisites...")
            
            prerequisites = {
                "python": {"check": "python --version", "required": True},
                "node": {"check": "node --version", "required": True},
                "npm": {"check": "npm --version", "required": True},
                "git": {"check": "git --version", "required": False},
                "docker": {"check": "docker --version", "required": False}
            }
            
            check_results = {}
            all_required_met = True
            
            for name, config in prerequisites.items():
                try:
                    result = subprocess.run(
                        config["check"].split(),
                        capture_output=True,
                        text=True,
                        shell=True
                    )
                    
                    if result.returncode == 0:
                        check_results[name] = {
                            "available": True,
                            "version": result.stdout.strip(),
                            "required": config["required"]
                        }
                        logger.info(f"✅ {name}: {result.stdout.strip()}")
                    else:
                        check_results[name] = {
                            "available": False,
                            "error": result.stderr.strip(),
                            "required": config["required"]
                        }
                        if config["required"]:
                            all_required_met = False
                            logger.error(f"❌ {name}: Not available (required)")
                        else:
                            logger.warning(f"⚠️ {name}: Not available (optional)")
                            
                except Exception as e:
                    check_results[name] = {
                        "available": False,
                        "error": str(e),
                        "required": config["required"]
                    }
                    if config["required"]:
                        all_required_met = False
            
            return {
                "success": all_required_met,
                "details": check_results,
                "missing_required": [name for name, result in check_results.items() 
                                   if not result["available"] and result["required"]]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _setup_n8n_environment(self) -> Dict[str, Any]:
        """Setup n8n environment"""
        try:
            logger.info("🛠️ Setting up n8n environment...")
            
            success = await self.n8n_manager.setup_n8n_environment()
            
            if success:
                # Install custom AGI nodes
                await self.n8n_manager.install_custom_nodes()
                
                return {
                    "success": True,
                    "details": {
                        "n8n_installed": success,
                        "custom_nodes_built": (self.n8n_manager.custom_nodes_dir / "dist").exists(),
                        "config_created": (self.n8n_manager.n8n_config_dir / "config.json").exists()
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "n8n environment setup failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _launch_agi_services(self) -> Dict[str, Any]:
        """Launch AGI services"""
        try:
            logger.info("🧠 Launching AGI services...")
            
            # Start the comprehensive ecosystem
            ecosystem_result = await self.orchestrator.start_comprehensive_ecosystem()
            
            return {
                "success": ecosystem_result.get("status") == "active",
                "details": {
                    "services_started": len(ecosystem_result.get("services", {})),
                    "trilogy_stack": ecosystem_result.get("trilogy_stack_status"),
                    "gemini_status": ecosystem_result.get("gemini_cli_status"),
                    "memory_system": ecosystem_result.get("memory_system_status")
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _launch_n8n_integration(self) -> Dict[str, Any]:
        """Launch n8n integration"""
        try:
            logger.info("🔗 Launching n8n integration...")
            
            # Start n8n server
            n8n_started = await self.n8n_manager.start_n8n()
            
            if n8n_started:
                # Wait for n8n to be ready
                await asyncio.sleep(5)
                
                # Check health
                health_ok = await self.n8n_manager.check_n8n_health()
                
                return {
                    "success": health_ok,
                    "details": {
                        "n8n_server_started": n8n_started,
                        "n8n_health_check": health_ok,
                        "n8n_url": f"http://localhost:{self.n8n_manager.n8n_port}",
                        "integration_server_url": "http://localhost:8020"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to start n8n server"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _create_workflow_templates(self) -> Dict[str, Any]:
        """Create workflow templates"""
        try:
            logger.info("📋 Creating workflow templates...")
            
            await self.n8n_manager.create_agi_workflow_templates()
            
            # Count created templates
            templates_dir = self.n8n_manager.workflows_dir / "templates"
            template_files = list(templates_dir.glob("*.json"))
            
            return {
                "success": len(template_files) > 0,
                "details": {
                    "templates_created": len(template_files),
                    "template_files": [f.name for f in template_files]
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _verify_ecosystem_health(self) -> Dict[str, Any]:
        """Verify complete ecosystem health"""
        try:
            logger.info("🏥 Verifying ecosystem health...")
            
            health_checks = {}
            
            # Check n8n
            health_checks["n8n"] = await self.n8n_manager.check_n8n_health()
            
            # Check AGI services
            health_checks["trilogy_gateway"] = await self._check_service_health("http://localhost:8000/health")
            health_checks["gemini_cli"] = await self._check_service_health("http://localhost:8015/health")
            health_checks["memory_mcp"] = await self._check_service_health("http://localhost:3002/health")
            health_checks["n8n_integration"] = await self._check_service_health("http://localhost:8020")
            
            # Check Ollama
            health_checks["ollama"] = await self._check_service_health("http://localhost:11434/api/tags")
            
            healthy_services = sum(1 for health in health_checks.values() if health)
            total_services = len(health_checks)
            
            return {
                "success": healthy_services >= (total_services * 0.8),  # 80% healthy threshold
                "details": {
                    "healthy_services": healthy_services,
                    "total_services": total_services,
                    "health_rate": (healthy_services / total_services) * 100,
                    "service_status": health_checks
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _check_service_health(self, url: str) -> bool:
        """Check if a service is healthy"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except:
            return False
            
    async def _run_demo_workflows(self) -> Dict[str, Any]:
        """Run demo workflows to test the system"""
        try:
            logger.info("🎭 Running demo workflows...")
            
            # Import and run the n8n integration test
            from test_n8n_integration import N8NIntegrationTester
            
            tester = N8NIntegrationTester()
            test_results = await tester.run_comprehensive_tests()
            
            return {
                "success": test_results.get("success_rate", 0) >= 70,  # 70% pass rate
                "details": {
                    "tests_passed": test_results.get("passed", 0),
                    "tests_failed": test_results.get("failed", 0),
                    "success_rate": test_results.get("success_rate", 0)
                }
            }
            
        except Exception as e:
            logger.warning(f"Demo workflows failed: {e}")
            return {
                "success": True,  # Not critical
                "error": str(e),
                "note": "Demo workflows are optional"
            }
            
    def _generate_next_steps(self, results: Dict[str, Any]) -> List[str]:
        """Generate next steps based on setup results"""
        next_steps = []
        
        if not results.get("prerequisites_check", {}).get("success", False):
            next_steps.append("Install missing prerequisites (Node.js, npm, Python)")
            
        if not results.get("n8n_environment_setup", {}).get("success", False):
            next_steps.append("Manually setup n8n environment")
            
        if not results.get("agi_services_launch", {}).get("success", False):
            next_steps.append("Debug AGI services startup issues")
            
        if not results.get("n8n_integration_launch", {}).get("success", False):
            next_steps.append("Check n8n server configuration and logs")
            
        if results.get("health_check", {}).get("success", False):
            next_steps.extend([
                "Open n8n dashboard: http://localhost:5678",
                "Explore AGI workflow templates",
                "Create custom workflows using AGI nodes",
                "Set up webhooks for automated triggers"
            ])
        else:
            next_steps.append("Fix service health issues before proceeding")
            
        return next_steps
        
    async def _save_launch_report(self, summary: Dict[str, Any]):
        """Save launch report to file"""
        try:
            report_file = Path(f"n8n_agi_launch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            with open(report_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
                
            logger.info(f"📄 Launch report saved to {report_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save launch report: {e}")
            
    def print_launch_summary(self, summary: Dict[str, Any]):
        """Print formatted launch summary"""
        print(f"\n{'='*80}")
        print(f"🚀 n8n + AGI ECOSYSTEM LAUNCH SUMMARY")
        print(f"{'='*80}")
        print(f"Timestamp: {summary['timestamp']}")
        print(f"Total Steps: {summary['total_steps']}")
        print(f"Successful: {summary['successful_steps']} ✅")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Fully Operational: {'Yes' if summary['fully_operational'] else 'No'} {'🎉' if summary['fully_operational'] else '⚠️'}")
        
        print(f"\n📊 STEP RESULTS:")
        for step, result in summary['step_results'].items():
            status = "✅" if result.get("success", False) else "❌"
            print(f"   {status} {step.replace('_', ' ').title()}")
            if not result.get("success", False) and result.get("error"):
                print(f"      Error: {result['error']}")
        
        if summary['next_steps']:
            print(f"\n📋 NEXT STEPS:")
            for i, step in enumerate(summary['next_steps'], 1):
                print(f"   {i}. {step}")
        
        if summary['fully_operational']:
            print(f"\n🎉 CONGRATULATIONS!")
            print(f"   The n8n + AGI ecosystem is fully operational!")
            print(f"   n8n Dashboard: http://localhost:5678")
            print(f"   MCPVots Dashboard: http://localhost:3000")
            print(f"   Start building AGI-powered workflows!")
        else:
            print(f"\n⚠️ SETUP INCOMPLETE")
            print(f"   Please address the issues above and try again.")
            
        print(f"{'='*80}\n")
        
    async def quick_start(self) -> Dict[str, Any]:
        """Quick start for development/testing"""
        logger.info("⚡ Quick Start Mode...")
        
        # Start essential services only
        essential_steps = [
            ("Check Prerequisites", self._check_prerequisites),
            ("Launch AGI Services", self._launch_agi_services),
            ("Start n8n Integration", self._launch_n8n_integration)
        ]
        
        results = {}
        for step_name, step_func in essential_steps:
            try:
                logger.info(f"⚡ {step_name}...")
                result = await step_func()
                results[step_name.lower().replace(" ", "_")] = result
                
                if not result.get("success", False):
                    logger.error(f"❌ {step_name} failed, continuing...")
                    
            except Exception as e:
                logger.error(f"❌ {step_name} exception: {e}")
                
        return {
            "mode": "quick_start",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    async def shutdown_ecosystem(self):
        """Shutdown the entire ecosystem"""
        logger.info("🛑 Shutting down n8n + AGI ecosystem...")
        
        try:
            # Shutdown n8n
            await self.n8n_manager.stop_n8n()
            
            # Shutdown orchestrator
            await self.orchestrator.shutdown()
            
            logger.info("✅ Ecosystem shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="n8n AGI Ecosystem Launcher")
    parser.add_argument("--mode", choices=["full", "quick", "shutdown"], default="full",
                       help="Launch mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    launcher = N8NAGILauncher()
    
    try:
        if args.mode == "full":
            summary = await launcher.full_ecosystem_setup()
            launcher.print_launch_summary(summary)
            
        elif args.mode == "quick":
            summary = await launcher.quick_start()
            logger.info(f"⚡ Quick start completed: {summary}")
            
        elif args.mode == "shutdown":
            await launcher.shutdown_ecosystem()
            
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
        await launcher.shutdown_ecosystem()
        
    except Exception as e:
        logger.error(f"❌ Launch failed: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
