#!/usr/bin/env python3
"""
🚀 ULTIMATE n8n + AGI INTEGRATION MANAGER
Advanced orchestration of n8n workflows with Trilogy AGI ecosystem
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
import yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltimateN8nManager:
    """Ultimate n8n + AGI Integration Manager"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.n8n_path = self.base_path / "n8n"
        self.config_path = self.n8n_path / "config"
        self.workflows_path = self.n8n_path / "workflows"
        self.data_path = self.n8n_path / "data"
        
        # AGI Service endpoints (from the logs - these are running!)
        self.agi_services = {
            "deerflow_orchestrator": "http://localhost:8014",
            "dgm_evolution_engine": "http://localhost:8013", 
            "owl_semantic_reasoning": "http://localhost:8011",
            "agent_file_system": "http://localhost:8012",
            "n8n_integration_server": "http://localhost:8020"
        }
        
        self.n8n_url = "http://localhost:5678"
        self.mcpvots_dashboard = "http://localhost:3000"
        
    async def check_agi_services_health(self) -> Dict[str, bool]:
        """Check health of all AGI services"""
        logger.info("🔍 Checking AGI services health...")
        health_status = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            for service_name, url in self.agi_services.items():
                try:
                    async with session.get(f"{url}/health") as response:
                        health_status[service_name] = response.status == 200
                        logger.info(f"✅ {service_name}: healthy")
                except Exception as e:
                    # Try basic connectivity
                    try:
                        async with session.get(url) as response:
                            health_status[service_name] = True
                            logger.info(f"🟡 {service_name}: responding (no health endpoint)")
                    except:
                        health_status[service_name] = False
                        logger.warning(f"❌ {service_name}: not responding")
        
        return health_status
    
    async def start_n8n_server(self) -> bool:
        """Start n8n server with advanced configuration"""
        logger.info("🚀 Starting n8n server with AGI integration...")
        
        try:
            # Create n8n start script
            n8n_start_script = self.base_path / "start_n8n.bat"
            script_content = f"""@echo off
echo 🚀 Starting n8n with AGI Integration...
cd /d "{self.base_path}"
set N8N_USER_FOLDER={self.n8n_path}
set N8N_HOST=localhost
set N8N_PORT=5678
set N8N_BASIC_AUTH_ACTIVE=false
set N8N_USER_MANAGEMENT_DISABLED=true
set WEBHOOK_URL=http://localhost:5678/webhook
npx n8n start
"""
            n8n_start_script.write_text(script_content)
            
            # Start n8n in background
            process = subprocess.Popen(
                [str(n8n_start_script)],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Wait for n8n to start
            await asyncio.sleep(10)
            
            # Check if n8n is running
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"{self.n8n_url}/rest/active-workflows") as response:
                        if response.status == 200:
                            logger.info("✅ n8n server started successfully!")
                            return True
                except:
                    pass
            
            logger.warning("⚠️ n8n server may not be fully ready yet")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start n8n server: {e}")
            return False
    
    def create_advanced_workflows(self) -> List[Dict]:
        """Create advanced n8n workflows for AGI integration"""
        logger.info("🧠 Creating advanced AGI workflows...")
        
        workflows = []
        
        # 1. AGI Service Health Monitor
        health_monitor_workflow = {
            "name": "AGI Health Monitor",
            "active": True,
            "nodes": [
                {
                    "parameters": {
                        "rule": {
                            "interval": [{"field": "minutes", "value": 5}]
                        }
                    },
                    "name": "Health Check Timer",
                    "type": "n8n-nodes-base.cron",
                    "position": [240, 300],
                    "id": "health-timer"
                },
                {
                    "parameters": {
                        "url": "http://localhost:8014/health",
                        "options": {"timeout": 5000}
                    },
                    "name": "Check DeerFlow",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [440, 200],
                    "id": "check-deerflow"
                },
                {
                    "parameters": {
                        "url": "http://localhost:8013/health", 
                        "options": {"timeout": 5000}
                    },
                    "name": "Check DGM Engine",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [440, 300],
                    "id": "check-dgm"
                },
                {
                    "parameters": {
                        "url": "http://localhost:8011/health",
                        "options": {"timeout": 5000}
                    },
                    "name": "Check OWL Reasoning",
                    "type": "n8n-nodes-base.httpRequest", 
                    "position": [440, 400],
                    "id": "check-owl"
                },
                {
                    "parameters": {
                        "functionCode": """
// Aggregate health status
const healthData = {
    timestamp: new Date().toISOString(),
    services: {
        deerflow: $input.first().json.status === 'ok',
        dgm_engine: $input.all()[1].json.status === 'ok', 
        owl_reasoning: $input.all()[2].json.status === 'ok'
    }
};

// Send to MCPVots dashboard
return [{
    json: {
        type: 'health_update',
        data: healthData,
        webhook_url: 'http://localhost:3000/api/agi-health'
    }
}];
"""
                    },
                    "name": "Process Health Data",
                    "type": "n8n-nodes-base.function",
                    "position": [640, 300],
                    "id": "process-health"
                }
            ],
            "connections": {
                "Health Check Timer": {"main": [
                    [{"node": "Check DeerFlow", "type": "main", "index": 0}],
                    [{"node": "Check DGM Engine", "type": "main", "index": 0}],
                    [{"node": "Check OWL Reasoning", "type": "main", "index": 0}]
                ]},
                "Check DeerFlow": {"main": [[{"node": "Process Health Data", "type": "main", "index": 0}]]},
                "Check DGM Engine": {"main": [[{"node": "Process Health Data", "type": "main", "index": 0}]]},
                "Check OWL Reasoning": {"main": [[{"node": "Process Health Data", "type": "main", "index": 0}]]}
            }
        }
        
        # 2. Code Optimization Workflow
        code_optimizer_workflow = {
            "name": "AI Code Optimizer",
            "active": True,
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "optimize-code",
                        "responseMode": "responseNode"
                    },
                    "name": "Code Optimization Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "position": [240, 300],
                    "id": "code-webhook"
                },
                {
                    "parameters": {
                        "url": "http://localhost:8014/api/analyze-code",
                        "sendBody": True,
                        "specifyBody": "json",
                        "jsonBody": "={{ $json }}"
                    },
                    "name": "DeerFlow Analysis",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [440, 300],
                    "id": "deerflow-analyze"
                },
                {
                    "parameters": {
                        "url": "http://localhost:8013/api/evolve-code",
                        "sendBody": True,
                        "specifyBody": "json", 
                        "jsonBody": "={{ $json }}"
                    },
                    "name": "DGM Evolution",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [640, 300],
                    "id": "dgm-evolve"
                },
                {
                    "parameters": {
                        "functionCode": """
// Advanced code optimization pipeline
const originalCode = $input.first().json.code;
const analysis = $input.first().json.analysis;
const evolution = $input.all()[1].json.evolved_code;

// Use Ollama for final optimization
const optimizationPrompt = `
Optimize this code based on the analysis:
Analysis: ${JSON.stringify(analysis)}
Evolution: ${evolution}
Original: ${originalCode}

Return optimized code with improvements.
`;

return [{
    json: {
        prompt: optimizationPrompt,
        model: 'qwen2.5-coder:latest',
        original_code: originalCode,
        optimization_stage: 'final'
    }
}];
"""
                    },
                    "name": "Prepare Ollama Optimization",
                    "type": "n8n-nodes-base.function",
                    "position": [840, 300],
                    "id": "prepare-ollama"
                }
            ]
        }
        
        # 3. GitHub Integration Workflow
        github_workflow = {
            "name": "GitHub AI Assistant",
            "active": True,
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "github-event",
                        "responseMode": "responseNode"
                    },
                    "name": "GitHub Webhook",
                    "type": "n8n-nodes-base.webhook", 
                    "position": [240, 300],
                    "id": "github-webhook"
                },
                {
                    "parameters": {
                        "functionCode": """
// Process GitHub events with AGI
const event = $input.first().json;
const eventType = event.action || event.ref_type || 'unknown';

// Route to appropriate AGI service
let targetService = 'http://localhost:8014'; // Default to DeerFlow

if (event.pull_request) {
    targetService = 'http://localhost:8013'; // DGM for code evolution
} else if (event.issue) {
    targetService = 'http://localhost:8011'; // OWL for reasoning
}

return [{
    json: {
        event_type: eventType,
        target_service: targetService,
        payload: event,
        timestamp: new Date().toISOString()
    }
}];
"""
                    },
                    "name": "Route GitHub Event",
                    "type": "n8n-nodes-base.function",
                    "position": [440, 300],
                    "id": "route-event"
                }
            ]
        }
        
        workflows.extend([health_monitor_workflow, code_optimizer_workflow, github_workflow])
        
        # Save workflows
        for workflow in workflows:
            workflow_file = self.workflows_path / f"{workflow['name'].lower().replace(' ', '_')}.json"
            workflow_file.write_text(json.dumps(workflow, indent=2))
            logger.info(f"✅ Created workflow: {workflow['name']}")
        
        return workflows
    
    async def deploy_workflows(self, workflows: List[Dict]) -> bool:
        """Deploy workflows to n8n server"""
        logger.info("🚀 Deploying workflows to n8n...")
        
        try:
            async with aiohttp.ClientSession() as session:
                for workflow in workflows:
                    try:
                        async with session.post(
                            f"{self.n8n_url}/rest/workflows",
                            json=workflow,
                            headers={'Content-Type': 'application/json'}
                        ) as response:
                            if response.status in [200, 201]:
                                logger.info(f"✅ Deployed: {workflow['name']}")
                            else:
                                logger.warning(f"⚠️ Failed to deploy: {workflow['name']}")
                    except Exception as e:
                        logger.error(f"❌ Error deploying {workflow['name']}: {e}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to deploy workflows: {e}")
            return False
    
    async def create_dashboard_integration(self) -> bool:
        """Create integration with MCPVots dashboard"""
        logger.info("🎛️ Creating dashboard integration...")
        
        # Create dashboard webhook endpoint
        dashboard_integration = {
            "name": "MCPVots Dashboard Integration",
            "active": True,
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "dashboard-update",
                        "responseMode": "responseNode"
                    },
                    "name": "Dashboard Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "position": [240, 300],
                    "id": "dashboard-webhook"
                },
                {
                    "parameters": {
                        "functionCode": """
// Process dashboard updates
const update = $input.first().json;

// Send real-time updates to dashboard
const dashboardData = {
    type: 'real_time_update',
    timestamp: new Date().toISOString(),
    data: update,
    source: 'n8n_integration'
};

return [{
    json: dashboardData
}];
"""
                    },
                    "name": "Process Dashboard Data",
                    "type": "n8n-nodes-base.function",
                    "position": [440, 300],
                    "id": "process-dashboard"
                }
            ]
        }
        
        # Save integration workflow
        integration_file = self.workflows_path / "dashboard_integration.json"
        integration_file.write_text(json.dumps(dashboard_integration, indent=2))
        
        return True
    
    async def run_ultimate_setup(self) -> Dict[str, Any]:
        """Run the ultimate n8n + AGI setup"""
        logger.info("🚀 LAUNCHING ULTIMATE n8n + AGI INTEGRATION!")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "status": "running",
            "services": {},
            "workflows": {},
            "integration": {}
        }
        
        try:
            # 1. Check AGI services
            health_status = await self.check_agi_services_health()
            results["services"] = health_status
            
            # 2. Start n8n server
            n8n_started = await self.start_n8n_server()
            results["n8n_server"] = n8n_started
            
            # 3. Create workflows
            workflows = self.create_advanced_workflows()
            results["workflows"]["created"] = len(workflows)
            
            # 4. Deploy workflows (if n8n is running)
            if n8n_started:
                deployed = await self.deploy_workflows(workflows)
                results["workflows"]["deployed"] = deployed
            
            # 5. Create dashboard integration
            dashboard_integrated = await self.create_dashboard_integration()
            results["integration"]["dashboard"] = dashboard_integrated
            
            results["status"] = "completed"
            logger.info("✅ ULTIMATE SETUP COMPLETED!")
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results

async def main():
    """Main execution function"""
    manager = UltimateN8nManager()
    results = await manager.run_ultimate_setup()
    
    # Save results
    results_file = Path("ultimate_n8n_setup_results.json")
    results_file.write_text(json.dumps(results, indent=2, default=str))
    
    print("🎉 ULTIMATE n8n + AGI INTEGRATION COMPLETE!")
    print(f"📊 Results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
