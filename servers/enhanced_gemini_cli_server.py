#!/usr/bin/env python3
"""
Enhanced Gemini CLI MCP Server for MCPVots
=========================================
Enhanced integration with Google Search grounding, workspace automation,
and integration with Trilogy AGI and Memory MCP systems.
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import websockets
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedGeminiCLIService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.cli_path = Path(__file__).parent.parent / "gemini-cli" / "packages" / "cli" / "dist" / "index.js"
        self.conversation_history = {}
        self.active_sessions = {}
        self.workspace_context = {}
        
        # Enhanced capabilities
        self.search_enabled = True
        self.trilogy_integration = True
        self.memory_mcp_integration = True
        
        # Model definitions with enhanced capabilities
        self.models = {
            "gemini-2.5-pro": {
                "name": "Gemini 2.5 Pro",
                "capabilities": [
                    "text", "vision", "code", "reasoning", "massive-context",
                    "google-search", "workspace-analysis", "automation"
                ],
                "context_window": 1000000,
                "description": "Most advanced model with 1M token context window and Google Search integration"
            },
            "gemini-1.5-pro": {
                "name": "Gemini 1.5 Pro",
                "capabilities": ["text", "vision", "code", "reasoning", "google-search"],
                "context_window": 1048576,
                "description": "Most capable model for complex tasks with Search"
            },
            "gemini-1.5-flash": {
                "name": "Gemini 1.5 Flash",
                "capabilities": ["text", "vision", "code", "fast-response", "google-search"],
                "context_window": 1048576,
                "description": "Fast and efficient model with Search capabilities"
            }
        }
        
        # Workspace automation rules
        self.automation_rules = {
            "code_analysis": {
                "trigger": "file_change",
                "actions": ["analyze_code", "suggest_improvements", "update_documentation"]
            },
            "performance_monitoring": {
                "trigger": "deployment",
                "actions": ["monitor_metrics", "detect_issues", "suggest_optimizations"]
            },
            "knowledge_update": {
                "trigger": "learning_event",
                "actions": ["update_memory_mcp", "refine_models", "share_insights"]
            }
        }
    
    async def enhanced_chat(self, message: str, model: str = "gemini-2.5-pro", 
                           session_id: str = "default", **kwargs) -> Dict[str, Any]:
        """Enhanced chat with Google Search grounding and workspace context"""
        
        # Determine if we should include Google Search
        include_search = kwargs.get("include_search", self._should_use_search(message))
        
        # Determine if we should include workspace context
        include_workspace = kwargs.get("include_workspace", self._should_include_workspace(message))
        
        # Build enhanced prompt
        enhanced_message = await self._build_enhanced_prompt(
            message, include_search, include_workspace, **kwargs
        )
        
        # Execute chat with enhanced capabilities
        result = await self._execute_enhanced_chat(enhanced_message, model, session_id)
        
        # Post-process and trigger automations
        await self._post_process_response(result, message, **kwargs)
        
        return result
    
    async def analyze_workspace_with_context(self, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze workspace with full 1M token context window"""
        logger.info(f"🔍 Starting {analysis_type} workspace analysis...")
        
        # Collect workspace context
        workspace_context = await self._collect_comprehensive_workspace_context()
        
        # Build analysis prompt based on type
        analysis_prompts = {
            "comprehensive": self._get_comprehensive_analysis_prompt(),
            "architecture": self._get_architecture_analysis_prompt(),
            "performance": self._get_performance_analysis_prompt(),
            "security": self._get_security_analysis_prompt(),
            "automation": self._get_automation_analysis_prompt()
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["comprehensive"])
        
        # Combine prompt with workspace context
        full_prompt = f"""
        {prompt}
        
        WORKSPACE CONTEXT:
        {workspace_context}
        
        Please provide a detailed analysis with specific, actionable recommendations.
        Include code examples and implementation steps where appropriate.
        """
        
        # Execute analysis with Gemini 2.5 Pro
        result = await self._execute_enhanced_chat(
            full_prompt, 
            "gemini-2.5-pro", 
            f"workspace_analysis_{analysis_type}_{datetime.now().timestamp()}"
        )
        
        # Store results and trigger follow-up actions
        await self._store_analysis_results(result, analysis_type)
        await self._trigger_analysis_automations(result, analysis_type)
        
        return result
    
    async def automate_workflow_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Automate a specific workflow task using Gemini CLI"""
        logger.info(f"⚙️ Automating workflow task: {task_description}")
        
        # Build automation prompt
        automation_prompt = f"""
        You are an expert automation engineer. Help automate this workflow task:
        
        TASK: {task_description}
        CONTEXT: {json.dumps(context or {}, indent=2)}
        
        Please provide:
        1. Step-by-step automation plan
        2. Required tools and technologies
        3. Implementation code/scripts
        4. Testing and validation approach
        5. Integration with existing MCPVots ecosystem
        6. Error handling and rollback procedures
        
        Focus on practical, implementable solutions that integrate with:
        - Trilogy AGI (Ollama)
        - Memory MCP and knowledge graph
        - React/TypeScript frontend
        - Python backend services
        """
        
        # Execute with enhanced capabilities
        result = await self.enhanced_chat(
            automation_prompt,
            model="gemini-2.5-pro",
            include_search=True,
            include_workspace=True,
            context_type="automation"
        )
        
        # Generate automation artifacts
        artifacts = await self._generate_automation_artifacts(result, task_description)
        
        return {
            "task": task_description,
            "automation_plan": result,
            "artifacts": artifacts,
            "timestamp": datetime.now().isoformat()
        }
    
    async def integrate_with_trilogy_agi(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with Trilogy AGI systems"""
        logger.info(f"🤖 Integrating with Trilogy AGI: {operation}")
        
        integration_prompts = {
            "fine_tune": f"""
            Help optimize this data for Trilogy AGI fine-tuning:
            {json.dumps(data, indent=2)}
            
            Provide optimized training data, hyperparameters, and training strategy.
            """,
            "memory_update": f"""
            Process this data for Memory MCP and knowledge graph storage:
            {json.dumps(data, indent=2)}
            
            Extract entities, relationships, and structured insights.
            """,
            "workflow_optimize": f"""
            Analyze this workflow data and suggest Trilogy AGI optimizations:
            {json.dumps(data, indent=2)}
            
            Focus on automation, efficiency, and intelligent decision-making.
            """
        }
        
        prompt = integration_prompts.get(operation, f"Process this data for Trilogy AGI: {data}")
        
        result = await self.enhanced_chat(
            prompt,
            model="gemini-2.5-pro",
            include_search=True,
            context_type="trilogy_integration"
        )
        
        # Execute integration based on operation
        integration_result = await self._execute_trilogy_integration(operation, result, data)
        
        return {
            "operation": operation,
            "gemini_analysis": result,
            "integration_result": integration_result,
            "timestamp": datetime.now().isoformat()
        }
    
    # Enhanced helper methods
    
    def _should_use_search(self, message: str) -> bool:
        """Determine if Google Search should be used for this message"""
        search_triggers = [
            "latest", "recent", "current", "new", "updates", "trends",
            "best practices", "compare", "alternatives", "examples",
            "documentation", "tutorial", "guide", "how to"
        ]
        return any(trigger in message.lower() for trigger in search_triggers)
    
    def _should_include_workspace(self, message: str) -> bool:
        """Determine if workspace context should be included"""
        workspace_triggers = [
            "this project", "this code", "this repository", "this workspace",
            "mcpvots", "trilogy", "architecture", "structure", "implementation"
        ]
        return any(trigger in message.lower() for trigger in workspace_triggers)
    
    async def _build_enhanced_prompt(self, message: str, include_search: bool, 
                                   include_workspace: bool, **kwargs) -> str:
        """Build enhanced prompt with additional context"""
        prompt_parts = []
        
        # Add search grounding if requested
        if include_search:
            prompt_parts.append("Use Google Search to ground your response with current, accurate information.")
        
        # Add workspace context if requested  
        if include_workspace and not self.workspace_context:
            self.workspace_context = await self._collect_workspace_context()
        
        if include_workspace and self.workspace_context:
            prompt_parts.append(f"WORKSPACE CONTEXT:\n{self.workspace_context}")
        
        # Add context type specific instructions
        context_type = kwargs.get("context_type", "general")
        if context_type in self._get_context_instructions():
            prompt_parts.append(self._get_context_instructions()[context_type])
        
        # Add the original message
        prompt_parts.append(f"USER REQUEST: {message}")
        
        return "\n\n".join(prompt_parts)
    
    async def _execute_enhanced_chat(self, message: str, model: str, session_id: str) -> Dict[str, Any]:
        """Execute chat with enhanced error handling and capabilities"""
        try:
            # Use node to execute Gemini CLI directly for better control
            cmd = [
                "node", str(self.cli_path),
                "--non-interactive",
                "--model", model
            ]
            
            # Set up environment
            env = os.environ.copy()
            if self.api_key:
                env["GEMINI_API_KEY"] = self.api_key
            
            # Create temporary file for input
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(message)
                temp_file = f.name
            
            try:
                # Execute CLI command
                result = subprocess.run(
                    cmd + [f"--input", temp_file],
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=120  # 2 minute timeout
                )
                
                if result.returncode == 0:
                    response_text = result.stdout.strip()
                    return {
                        "response": response_text,
                        "model": model,
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat(),
                        "success": True
                    }
                else:
                    error_msg = result.stderr or f"CLI exited with code {result.returncode}"
                    logger.error(f"Gemini CLI error: {error_msg}")
                    return {
                        "error": error_msg,
                        "model": model,
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat(),
                        "success": False
                    }
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Enhanced chat execution failed: {e}")
            return {
                "error": str(e),
                "model": model,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    async def _collect_comprehensive_workspace_context(self) -> str:
        """Collect comprehensive workspace context for analysis"""
        workspace_path = Path("c:/Workspace/MCPVots")
        context_parts = []
        
        # Configuration files
        config_files = [
            "package.json", "pyproject.toml", "mcp-config.json", 
            ".env.example", "tailwind.config.ts", "next.config.mjs"
        ]
        
        for file_name in config_files:
            file_path = workspace_path / file_name
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    context_parts.append(f"=== {file_name} ===\n{content}\n")
                except Exception as e:
                    logger.warning(f"Could not read {file_name}: {e}")
        
        # Key source files
        source_files = [
            "src/app/page.tsx",
            "src/app/layout.tsx", 
            "servers/gemini_cli_server.py",
            "memory_mcp_integration.py",
            "advanced_orchestrator.py"
        ]
        
        for file_name in source_files:
            file_path = workspace_path / file_name
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    # Truncate very long files
                    if len(content) > 10000:
                        content = content[:10000] + "\n... [file truncated] ..."
                    context_parts.append(f"=== {file_name} ===\n{content}\n")
                except Exception as e:
                    logger.warning(f"Could not read {file_name}: {e}")
        
        # Directory structure
        structure = self._get_directory_structure(workspace_path)
        context_parts.insert(0, f"=== DIRECTORY STRUCTURE ===\n{structure}\n")
        
        return "\n".join(context_parts)
    
    async def _collect_workspace_context(self) -> str:
        """Collect essential workspace context"""
        return await self._collect_comprehensive_workspace_context()
    
    def _get_directory_structure(self, path: Path, max_depth: int = 3) -> str:
        """Get directory structure as string"""
        structure = []
        
        def _walk_dir(current_path: Path, depth: int = 0):
            if depth > max_depth:
                return
                
            indent = "  " * depth
            try:
                items = sorted(current_path.iterdir())
                for item in items[:50]:  # Limit items to prevent overwhelming output
                    if item.name.startswith('.'):
                        continue
                        
                    if item.is_dir():
                        structure.append(f"{indent}{item.name}/")
                        if depth < max_depth:
                            _walk_dir(item, depth + 1)
                    else:
                        structure.append(f"{indent}{item.name}")
                        
                if len(items) > 50:
                    structure.append(f"{indent}... and {len(items) - 50} more items")
                    
            except PermissionError:
                structure.append(f"{indent}[Permission Denied]")
        
        _walk_dir(path)
        return "\n".join(structure)
    
    def _get_context_instructions(self) -> Dict[str, str]:
        """Get context-specific instructions"""
        return {
            "automation": """
            Focus on practical automation solutions that can be implemented immediately.
            Consider integration with existing tools and systems.
            Provide working code examples and implementation steps.
            """,
            "analysis": """
            Provide comprehensive analysis with specific metrics and recommendations.
            Include both technical and business impact considerations.
            Suggest concrete next steps and implementation priorities.
            """,
            "trilogy_integration": """
            Focus on integration with Trilogy AGI components (Ollama, OWL, Agent File, DGM, DeerFlow).
            Consider memory MCP and knowledge graph implications.
            Provide specific integration patterns and best practices.
            """
        }
    
    def _get_comprehensive_analysis_prompt(self) -> str:
        """Get comprehensive analysis prompt"""
        return """
        Perform a comprehensive analysis of this MCPVots repository including:
        
        1. Architecture Assessment
        2. Technology Stack Evaluation  
        3. Integration Quality Review
        4. Performance Optimization Opportunities
        5. Security and Best Practices Review
        6. Scalability and Maintainability Analysis
        7. Automation Opportunities
        8. Next Steps and Recommendations
        
        Provide specific, actionable insights with code examples.
        """
    
    def _get_architecture_analysis_prompt(self) -> str:
        """Get architecture-specific analysis prompt"""
        return """
        Analyze the architecture of this MCPVots system focusing on:
        
        1. Frontend/Backend separation and communication
        2. MCP server integration patterns
        3. Trilogy AGI integration architecture
        4. Memory and knowledge graph systems
        5. Service orchestration and coordination
        6. Scalability and extensibility
        
        Provide architecture diagrams, patterns, and improvement recommendations.
        """
    
    def _get_performance_analysis_prompt(self) -> str:
        """Get performance analysis prompt"""
        return """
        Analyze performance aspects of this MCPVots system:
        
        1. Frontend performance and optimization
        2. Backend service efficiency
        3. MCP communication overhead
        4. Memory usage and optimization
        5. Database and storage performance
        6. Network and latency considerations
        
        Provide specific performance metrics and optimization strategies.
        """
    
    def _get_security_analysis_prompt(self) -> str:
        """Get security analysis prompt"""
        return """
        Perform security analysis of this MCPVots system:
        
        1. Authentication and authorization
        2. API security and validation
        3. Data protection and privacy
        4. Network security
        5. Dependency vulnerabilities
        6. Deployment security
        
        Provide security recommendations and implementation guidance.
        """
    
    def _get_automation_analysis_prompt(self) -> str:
        """Get automation analysis prompt"""
        return """
        Identify automation opportunities in this MCPVots system:
        
        1. Development workflow automation
        2. Testing and quality assurance automation
        3. Deployment and CI/CD automation
        4. Monitoring and alerting automation
        5. Performance optimization automation
        6. Knowledge management automation
        
        Provide specific automation scripts and implementation plans.
        """
    
    async def _post_process_response(self, result: Dict[str, Any], original_message: str, **kwargs):
        """Post-process response and trigger automations"""
        # Store conversation in memory if successful
        if result.get("success"):
            await self._store_conversation_memory(original_message, result)
        
        # Trigger relevant automations
        await self._trigger_response_automations(result, original_message, **kwargs)
    
    async def _store_analysis_results(self, result: Dict[str, Any], analysis_type: str):
        """Store analysis results in knowledge graph"""
        # Implementation for storing analysis results
        logger.info(f"📊 Storing {analysis_type} analysis results")
    
    async def _trigger_analysis_automations(self, result: Dict[str, Any], analysis_type: str):
        """Trigger automations based on analysis results"""
        # Implementation for triggering automations
        logger.info(f"⚙️ Triggering {analysis_type} automations")
    
    async def _generate_automation_artifacts(self, result: Dict[str, Any], task: str) -> Dict[str, Any]:
        """Generate automation artifacts from analysis"""
        # Implementation for generating artifacts
        return {"scripts": [], "configs": [], "documentation": []}
    
    async def _execute_trilogy_integration(self, operation: str, result: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration with Trilogy AGI"""
        # Implementation for Trilogy AGI integration
        return {"status": "completed", "operation": operation}
    
    async def _store_conversation_memory(self, message: str, result: Dict[str, Any]):
        """Store conversation in memory system"""
        # Implementation for memory storage
        pass
    
    async def _trigger_response_automations(self, result: Dict[str, Any], message: str, **kwargs):
        """Trigger automations based on response"""
        # Implementation for automation triggers
        pass

# MCP Server implementation
class EnhancedGeminiMCPServer:
    def __init__(self):
        self.service = EnhancedGeminiCLIService()
        self.active_connections = []
    
    async def handle_websocket(self, websocket, path):
        """Handle WebSocket MCP connections"""
        self.active_connections.append(websocket)
        logger.info("🔗 New MCP client connected")
        
        try:
            await websocket.send(json.dumps({
                "jsonrpc": "2.0",
                "method": "initialized",
                "params": {
                    "capabilities": {
                        "enhanced_chat": True,
                        "workspace_analysis": True,
                        "google_search": True,
                        "trilogy_integration": True,
                        "automation": True
                    }
                }
            }))
            
            async for message in websocket:
                try:
                    request = json.loads(message)
                    response = await self._handle_mcp_request(request)
                    await websocket.send(json.dumps(response))
                except Exception as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -1, "message": str(e)}
                    }
                    await websocket.send(json.dumps(error_response))
                    
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.active_connections.remove(websocket)
            logger.info("🔌 MCP client disconnected")
    
    async def _handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "gemini/enhanced_chat":
            result = await self.service.enhanced_chat(**params)
        elif method == "gemini/analyze_workspace":
            result = await self.service.analyze_workspace_with_context(**params)
        elif method == "gemini/automate_workflow":
            result = await self.service.automate_workflow_task(**params)
        elif method == "gemini/trilogy_integration":
            result = await self.service.integrate_with_trilogy_agi(**params)
        elif method == "gemini/list_models":
            result = {"models": list(self.service.models.keys())}
        elif method == "gemini/health":
            result = {"status": "healthy", "timestamp": datetime.now().isoformat()}
        else:
            result = {"error": f"Unknown method: {method}"}
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }

# Main server
async def main():
    server = EnhancedGeminiMCPServer()
    
    # Start WebSocket server
    start_server = websockets.serve(
        server.handle_websocket,
        "localhost",
        8015,
        ping_interval=30,
        ping_timeout=10
    )
    
    logger.info("🚀 Enhanced Gemini CLI MCP Server starting on ws://localhost:8015")
    
    await start_server
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
