#!/usr/bin/env python3
"""
Gemini CLI Automated Code Improvement System for MCPVots
======================================================
Leverages Gemini 2.5 Pro's 1M token context window and Google Search grounding
to automatically analyze, optimize, and improve code across the entire workspace.

Features:
- Full workspace context analysis with 1M token window
- Google Search grounded recommendations
- Automated code fixes and optimizations
- Continuous monitoring and improvement cycles
- Integration with Trilogy AGI and Memory MCP
- CI/CD automation and deployment optimizations
"""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
import websockets
import aiohttp
import tempfile
import hashlib
import ast
import re
from concurrent.futures import ThreadPoolExecutor
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    logger.warning("GitPython not available - git integration disabled")

class GeminiAutomatedCodeImprover:
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or os.getcwd()
        self.gemini_server = "ws://localhost:8015"
        self.memory_server = "ws://localhost:8020"
        
        # Analysis tracking
        self.analysis_cache = {}
        self.improvement_history = {}
        self.active_improvements = {}
        
        # Configuration
        self.config = {
            "analysis_depth": "comprehensive",
            "auto_apply_safe_fixes": True,
            "require_approval_for_major_changes": True,
            "continuous_monitoring": True,
            "google_search_grounding": True,
            "max_context_tokens": 1000000,
            "improvement_categories": [
                "performance", "security", "maintainability", 
                "architecture", "testing", "documentation",
                "automation", "deployment"
            ]
        }
        
        # File patterns to analyze
        self.file_patterns = {
            "python": ["*.py"],
            "javascript": ["*.js", "*.jsx", "*.ts", "*.tsx"],
            "config": ["*.json", "*.yaml", "*.yml", "*.toml"],
            "documentation": ["*.md", "*.rst", "*.txt"],
            "docker": ["Dockerfile*", "docker-compose*.yml"],
            "ci_cd": [".github/**/*.yml", ".github/**/*.yaml", "*.jenkinsfile"]
        }
        
    async def start_automated_improvement_system(self):
        """Start the automated code improvement system"""
        logger.info("🚀 Starting Gemini Automated Code Improvement System...")
        
        # Initialize connections
        await self._verify_connections()
        
        # Perform initial comprehensive analysis
        initial_analysis = await self.perform_comprehensive_workspace_analysis()
        
        # Generate improvement roadmap
        roadmap = await self._generate_improvement_roadmap(initial_analysis)
        
        # Start continuous improvement cycles
        if self.config["continuous_monitoring"]:
            await self._start_continuous_improvement_cycles()
        
        return {
            "status": "active",
            "initial_analysis": initial_analysis,
            "improvement_roadmap": roadmap,
            "timestamp": datetime.now().isoformat()
        }
    
    async def perform_comprehensive_workspace_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive workspace analysis using Gemini's full context window"""
        logger.info("🔍 Starting comprehensive workspace analysis...")
        
        # Collect all workspace context
        workspace_context = await self._collect_full_workspace_context()
        
        # Build comprehensive analysis prompt
        analysis_prompt = self._build_comprehensive_analysis_prompt(workspace_context)
        
        # Execute analysis with Gemini 2.5 Pro
        analysis_result = await self._execute_gemini_analysis(
            analysis_prompt, 
            "comprehensive_analysis",
            use_search_grounding=True
        )
        
        # Process and structure results
        structured_analysis = await self._structure_analysis_results(analysis_result)
        
        # Store in memory MCP
        await self._store_analysis_in_memory(structured_analysis)
        
        logger.info("✅ Comprehensive workspace analysis complete")
        return structured_analysis
    
    async def _collect_full_workspace_context(self) -> Dict[str, Any]:
        """Collect comprehensive workspace context for 1M token analysis"""
        logger.info("📊 Collecting full workspace context...")
        
        context = {
            "metadata": {
                "workspace_path": self.workspace_path,
                "analysis_timestamp": datetime.now().isoformat(),
                "total_files": 0,
                "total_lines": 0
            },
            "structure": {},
            "files": {},
            "dependencies": {},
            "git_info": {},
            "config_files": {},
            "documentation": {}
        }
        
        # Get directory structure
        context["structure"] = await self._get_directory_structure()
        
        # Analyze all relevant files
        for category, patterns in self.file_patterns.items():
            context["files"][category] = await self._collect_files_by_pattern(patterns)
        
        # Collect dependency information
        context["dependencies"] = await self._analyze_dependencies()
        
        # Get git information
        context["git_info"] = await self._get_git_information()
        
        # Analyze configuration files
        context["config_files"] = await self._analyze_config_files()
        
        # Collect documentation
        context["documentation"] = await self._collect_documentation()
        
        # Calculate context size and optimize if needed
        context_size = len(json.dumps(context))
        if context_size > 800000:  # Leave room for prompt and response
            context = await self._optimize_context_size(context)
        
        context["metadata"]["context_size_chars"] = len(json.dumps(context))
        logger.info(f"📈 Context collected: {context['metadata']['context_size_chars']} characters")
        
        return context
    
    def _build_comprehensive_analysis_prompt(self, workspace_context: Dict[str, Any]) -> str:
        """Build comprehensive analysis prompt for Gemini"""
        prompt = f"""
You are an expert software architect and code quality engineer with access to Google Search for the latest best practices. Analyze this entire codebase comprehensively using your 1M token context window.

WORKSPACE CONTEXT:
{json.dumps(workspace_context, indent=2)}

ANALYSIS REQUIREMENTS:
1. **Architecture Analysis**: Evaluate overall system architecture, design patterns, and structural integrity
2. **Code Quality**: Assess code quality, maintainability, and adherence to best practices
3. **Performance**: Identify performance bottlenecks and optimization opportunities
4. **Security**: Detect security vulnerabilities and recommend hardening measures
5. **Testing**: Evaluate test coverage and quality of testing strategies
6. **Documentation**: Assess documentation quality and completeness
7. **Dependencies**: Analyze dependency management and security
8. **Automation**: Identify opportunities for CI/CD and workflow automation
9. **Deployment**: Evaluate deployment strategies and infrastructure

For each category, provide:
- Current state assessment (score 1-10)
- Specific issues identified with file paths and line numbers where applicable
- Prioritized recommendations with implementation steps
- Industry best practices (use Google Search for latest standards)
- Estimated impact and effort for each recommendation

SEARCH GROUNDING: Use Google Search to ensure all recommendations are based on current industry best practices and emerging standards.

OUTPUT FORMAT: Provide a structured JSON response with detailed analysis and actionable recommendations.
"""
        return prompt
    
    async def _execute_gemini_analysis(self, prompt: str, analysis_type: str, 
                                     use_search_grounding: bool = True) -> Dict[str, Any]:
        """Execute analysis using Gemini CLI with full capabilities"""
        try:
            # Connect to Gemini MCP server
            async with websockets.connect(self.gemini_server) as ws:
                request = {
                    "jsonrpc": "2.0",
                    "id": f"analysis_{analysis_type}_{datetime.now().timestamp()}",
                    "method": "gemini/enhanced_chat",
                    "params": {
                        "message": prompt,
                        "model": "gemini-2.5-pro",
                        "session_id": f"workspace_analysis_{analysis_type}",
                        "include_search": use_search_grounding,
                        "include_workspace": True,
                        "context_type": "code_analysis"
                    }
                }
                
                await ws.send(json.dumps(request))
                response = await ws.recv()
                result = json.loads(response)
                
                if "result" in result:
                    return result["result"]
                else:
                    logger.error(f"Gemini analysis error: {result.get('error', 'Unknown error')}")
                    return {"error": result.get("error", "Analysis failed")}
                    
        except Exception as e:
            logger.error(f"Failed to execute Gemini analysis: {e}")
            return {"error": str(e)}
    
    async def _structure_analysis_results(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Structure and enhance analysis results"""
        structured = {
            "analysis_metadata": {
                "timestamp": datetime.now().isoformat(),
                "analyzer": "gemini-2.5-pro",
                "workspace_path": self.workspace_path
            },
            "overall_scores": {},
            "category_analyses": {},
            "prioritized_recommendations": [],
            "quick_fixes": [],
            "major_improvements": [],
            "automation_opportunities": []
        }
        
        # Extract and structure the Gemini response
        if "response" in raw_result:
            response_text = raw_result["response"]
            
            # Try to parse JSON if it's in the response
            try:
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_content = response_text[json_start:json_end]
                    parsed_analysis = json.loads(json_content)
                    structured.update(parsed_analysis)
                else:
                    # Parse structured text response
                    structured = await self._parse_text_analysis(response_text)
            except json.JSONDecodeError:
                # Fallback to text parsing
                structured["raw_analysis"] = response_text
                structured = await self._parse_text_analysis(response_text)
        
        return structured
    
    async def generate_automated_improvements(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate automated code improvements based on analysis"""
        logger.info("🔧 Generating automated improvements...")
        
        improvements = {
            "safe_automatic_fixes": [],
            "approval_required_changes": [],
            "automation_scripts": [],
            "deployment_optimizations": []
        }
        
        # Process each category of recommendations
        for category, recommendations in analysis.get("category_analyses", {}).items():
            category_improvements = await self._generate_category_improvements(
                category, recommendations
            )
            
            # Classify improvements by safety level
            for improvement in category_improvements:
                if improvement.get("safety_level") == "safe":
                    improvements["safe_automatic_fixes"].append(improvement)
                elif improvement.get("safety_level") == "requires_approval":
                    improvements["approval_required_changes"].append(improvement)
                elif improvement.get("type") == "automation":
                    improvements["automation_scripts"].append(improvement)
                elif improvement.get("type") == "deployment":
                    improvements["deployment_optimizations"].append(improvement)
        
        # Generate implementation scripts
        for improvement in improvements["safe_automatic_fixes"]:
            script = await self._generate_improvement_script(improvement)
            improvement["implementation_script"] = script
        
        return improvements
    
    async def apply_safe_improvements(self, improvements: Dict[str, Any]) -> Dict[str, Any]:
        """Apply safe improvements automatically"""
        logger.info("⚡ Applying safe improvements...")
        
        results = {
            "applied": [],
            "failed": [],
            "skipped": []
        }
        
        for improvement in improvements.get("safe_automatic_fixes", []):
            try:
                # Validate improvement is still safe
                if await self._validate_improvement_safety(improvement):
                    # Apply the improvement
                    result = await self._apply_single_improvement(improvement)
                    
                    if result["success"]:
                        results["applied"].append(improvement)
                        logger.info(f"✅ Applied: {improvement.get('title', 'Improvement')}")
                    else:
                        results["failed"].append({
                            "improvement": improvement,
                            "error": result["error"]
                        })
                        logger.error(f"❌ Failed: {result['error']}")
                else:
                    results["skipped"].append({
                        "improvement": improvement,
                        "reason": "Safety validation failed"
                    })
            except Exception as e:
                results["failed"].append({
                    "improvement": improvement,
                    "error": str(e)
                })
                logger.error(f"❌ Error applying improvement: {e}")
        
        return results
    
    async def _start_continuous_improvement_cycles(self):
        """Start continuous improvement monitoring"""
        logger.info("🔄 Starting continuous improvement cycles...")
        
        while self.config["continuous_monitoring"]:
            try:
                # Wait for file changes or time-based cycle
                await asyncio.sleep(3600)  # Check every hour
                
                # Detect changes since last analysis
                changes = await self._detect_workspace_changes()
                
                if changes["has_significant_changes"]:
                    logger.info("📈 Significant changes detected, running incremental analysis...")
                    
                    # Run incremental analysis
                    incremental_analysis = await self._run_incremental_analysis(changes)
                    
                    # Generate and apply improvements
                    improvements = await self.generate_automated_improvements(incremental_analysis)
                    await self.apply_safe_improvements(improvements)
                    
                    # Update memory with new insights
                    await self._update_memory_with_improvements(improvements)
                
            except Exception as e:
                logger.error(f"Error in continuous improvement cycle: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _get_directory_structure(self) -> Dict[str, Any]:
        """Get comprehensive directory structure"""
        structure = {}
        workspace_path = Path(self.workspace_path)
        
        for item in workspace_path.rglob("*"):
            if item.is_file() and not self._should_ignore_file(item):
                rel_path = item.relative_to(workspace_path)
                structure[str(rel_path)] = {
                    "type": "file",
                    "size": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
        
        return structure
    
    async def _collect_files_by_pattern(self, patterns: List[str]) -> Dict[str, Any]:
        """Collect files matching specific patterns"""
        files = {}
        workspace_path = Path(self.workspace_path)
        
        for pattern in patterns:
            for file_path in workspace_path.rglob(pattern):
                if file_path.is_file() and not self._should_ignore_file(file_path):
                    try:
                        rel_path = str(file_path.relative_to(workspace_path))
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        
                        files[rel_path] = {
                            "content": content[:10000],  # Limit content size
                            "size": len(content),
                            "lines": len(content.splitlines()),
                            "modified": datetime.fromtimestamp(
                                file_path.stat().st_mtime
                            ).isoformat()
                        }
                    except Exception as e:
                        logger.warning(f"Could not read {file_path}: {e}")
        
        return files
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored in analysis"""
        ignore_patterns = [
            "node_modules", ".git", "__pycache__", ".pytest_cache",
            "venv", ".venv", "env", ".env", "dist", "build",
            ".next", ".cache", "coverage", "logs", "*.log"
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in ignore_patterns)
    
    async def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies"""
        dependencies = {}
        workspace_path = Path(self.workspace_path)
        
        # Python dependencies
        for req_file in ["requirements.txt", "pyproject.toml", "Pipfile"]:
            req_path = workspace_path / req_file
            if req_path.exists():
                dependencies[req_file] = req_path.read_text()
        
        # Node.js dependencies
        package_json = workspace_path / "package.json"
        if package_json.exists():
            dependencies["package.json"] = json.loads(package_json.read_text())
        
        return dependencies
    
    async def _get_git_information(self) -> Dict[str, Any]:
        """Get git repository information"""
        git_info = {}
        
        if not GIT_AVAILABLE:
            git_info = {"error": "GitPython not installed"}
            return git_info
        
        try:
            repo = git.Repo(self.workspace_path)
            git_info = {
                "branch": repo.active_branch.name,
                "commit": repo.head.commit.hexsha[:8],
                "modified_files": [item.a_path for item in repo.index.diff(None)],
                "untracked_files": repo.untracked_files,
                "remote_url": next(repo.remote().urls) if repo.remotes else None
            }
        except Exception as e:
            git_info = {"error": f"Not a git repository or error: {e}"}
        
        return git_info
    
    async def _store_analysis_in_memory(self, analysis: Dict[str, Any]):
        """Store analysis results in Memory MCP"""
        try:
            async with websockets.connect(self.memory_server) as ws:
                # Create entity for this analysis
                entity_request = {
                    "jsonrpc": "2.0",
                    "id": f"store_analysis_{datetime.now().timestamp()}",
                    "method": "memory/create_entities",
                    "params": {
                        "entities": [{
                            "name": f"workspace_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            "entityType": "analysis",
                            "observations": [
                                f"Comprehensive analysis completed at {analysis['analysis_metadata']['timestamp']}",
                                f"Overall architecture score: {analysis.get('overall_scores', {}).get('architecture', 'N/A')}",
                                f"Security score: {analysis.get('overall_scores', {}).get('security', 'N/A')}",
                                f"Performance score: {analysis.get('overall_scores', {}).get('performance', 'N/A')}",
                                f"Total recommendations: {len(analysis.get('prioritized_recommendations', []))}"
                            ]
                        }]
                    }
                }
                
                await ws.send(json.dumps(entity_request))
                response = await ws.recv()
                logger.info("📝 Analysis stored in Memory MCP")
                
        except Exception as e:
            logger.error(f"Failed to store analysis in memory: {e}")

    async def _generate_category_improvements(self, category: str, recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate improvements for a specific category"""
        improvements = []
        
        for rec in recommendations.get("recommendations", []):
            improvement = {
                "title": rec.get("title", ""),
                "category": category,
                "priority": rec.get("priority", "medium"),
                "safety_level": rec.get("safety_level", "requires_approval"),
                "description": rec.get("description", ""),
                "implementation_steps": rec.get("implementation_steps", []),
                "estimated_effort": rec.get("estimated_effort", "unknown"),
                "expected_impact": rec.get("expected_impact", "unknown")
            }
            improvements.append(improvement)
        
        return improvements
    
    async def _generate_improvement_script(self, improvement: Dict[str, Any]) -> str:
        """Generate implementation script for an improvement"""
        script_template = f"""
#!/usr/bin/env python3
# Auto-generated improvement script
# Title: {improvement.get('title', 'Untitled')}
# Category: {improvement.get('category', 'General')}
# Priority: {improvement.get('priority', 'Medium')}

import os
import sys
from pathlib import Path

def apply_improvement():
    \"\"\"Apply the improvement: {improvement.get('title', 'Untitled')}\"\"\"
    print(f"Applying improvement: {improvement.get('title', 'Untitled')}")
    
    # Implementation steps:
    # {chr(10).join(f"# - {step}" for step in improvement.get('implementation_steps', []))}
    
    # TODO: Implement specific improvement logic
    pass

if __name__ == "__main__":
    apply_improvement()
"""
        return script_template
    
    async def _validate_improvement_safety(self, improvement: Dict[str, Any]) -> bool:
        """Validate that an improvement is safe to apply automatically"""
        # Safety checks
        safety_criteria = [
            improvement.get("safety_level") == "safe",
            improvement.get("priority") in ["low", "medium"],
            "delete" not in improvement.get("title", "").lower(),
            "remove" not in improvement.get("title", "").lower(),
            len(improvement.get("implementation_steps", [])) > 0
        ]
        
        return all(safety_criteria)
    
    async def _apply_single_improvement(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a single improvement"""
        try:
            # For now, just simulate the application
            logger.info(f"Applying improvement: {improvement.get('title', 'Untitled')}")
            
            # TODO: Implement actual improvement application logic
            # This would include file modifications, script execution, etc.
            
            return {
                "success": True,
                "improvement": improvement,
                "changes_made": ["Simulated improvement application"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "improvement": improvement,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _detect_workspace_changes(self) -> Dict[str, Any]:
        """Detect changes in the workspace since last analysis"""
        # This would typically compare file modification times, git status, etc.
        # For now, return a mock result
        return {
            "has_significant_changes": False,
            "changed_files": [],
            "new_files": [],
            "deleted_files": [],
            "last_check": datetime.now().isoformat()
        }
    
    async def _run_incremental_analysis(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Run incremental analysis on changed files"""
        # Focus analysis on changed files only
        incremental_context = {
            "changed_files": changes.get("changed_files", []),
            "analysis_type": "incremental",
            "timestamp": datetime.now().isoformat()
        }
        
        # Build focused analysis prompt
        prompt = f"""
        Analyze the following changed files for potential improvements:
        
        CHANGED FILES:
        {json.dumps(incremental_context, indent=2)}
        
        Focus on:
        1. Code quality issues in changed files
        2. Performance impacts of changes
        3. Security implications
        4. Integration issues with existing code
        
        Provide quick, actionable recommendations.
        """
        
        # Execute focused analysis
        return await self._execute_gemini_analysis(prompt, "incremental", True)
    
    async def _update_memory_with_improvements(self, improvements: Dict[str, Any]):
        """Update Memory MCP with improvement insights"""
        try:
            async with websockets.connect(self.memory_server) as ws:
                # Create observations about improvements
                observations = []
                
                for category, items in improvements.items():
                    if items:
                        observations.append(f"Generated {len(items)} {category} improvements")
                        for item in items[:3]:  # Limit to avoid too much data
                            observations.append(f"Improvement: {item.get('title', 'Untitled')}")
                
                entity_request = {
                    "jsonrpc": "2.0",
                    "id": f"store_improvements_{datetime.now().timestamp()}",
                    "method": "memory/create_entities",
                    "params": {
                        "entities": [{
                            "name": f"improvement_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            "entityType": "improvement",
                            "observations": observations
                        }]
                    }
                }
                
                await ws.send(json.dumps(entity_request))
                response = await ws.recv()
                logger.info("📝 Improvements stored in Memory MCP")
                
        except Exception as e:
            logger.error(f"Failed to update memory with improvements: {e}")
    
    async def _parse_text_analysis(self, text: str) -> Dict[str, Any]:
        """Parse text-based analysis results"""
        # Simple text parsing for analysis results
        analysis = {
            "raw_analysis": text,
            "overall_scores": {},
            "category_analyses": {},
            "prioritized_recommendations": []
        }
        
        # Extract scores using regex
        import re
        score_pattern = r"(\w+)\s*(?:score|rating):\s*(\d+(?:\.\d+)?)"
        scores = re.findall(score_pattern, text.lower())
        
        for category, score in scores:
            try:
                analysis["overall_scores"][category] = float(score)
            except ValueError:
                pass
        
        # Extract recommendations
        lines = text.split('\n')
        current_recommendations = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('*'):
                recommendation = line.lstrip('-* ').strip()
                if recommendation:
                    current_recommendations.append({
                        "title": recommendation,
                        "priority": "medium",
                        "safety_level": "requires_approval"
                    })
        
        analysis["prioritized_recommendations"] = current_recommendations
        return analysis
    
    async def _analyze_config_files(self) -> Dict[str, Any]:
        """Analyze configuration files"""
        config_files = {}
        workspace_path = Path(self.workspace_path)
        
        config_patterns = [
            "*.json", "*.yaml", "*.yml", "*.toml", "*.ini",
            "*.cfg", "*.conf", "Dockerfile*", "docker-compose*"
        ]
        
        for pattern in config_patterns:
            for config_file in workspace_path.rglob(pattern):
                if config_file.is_file() and not self._should_ignore_file(config_file):
                    try:
                        rel_path = str(config_file.relative_to(workspace_path))
                        content = config_file.read_text(encoding='utf-8', errors='ignore')
                        
                        config_files[rel_path] = {
                            "content": content[:5000],  # Limit size
                            "size": len(content),
                            "type": config_file.suffix
                        }
                    except Exception as e:
                        logger.warning(f"Could not read config file {config_file}: {e}")
        
        return config_files
    
    async def _collect_documentation(self) -> Dict[str, Any]:
        """Collect documentation files"""
        docs = {}
        workspace_path = Path(self.workspace_path)
        
        doc_patterns = ["*.md", "*.rst", "*.txt", "docs/**/*"]
        
        for pattern in doc_patterns:
            for doc_file in workspace_path.rglob(pattern):
                if doc_file.is_file() and not self._should_ignore_file(doc_file):
                    try:
                        rel_path = str(doc_file.relative_to(workspace_path))
                        content = doc_file.read_text(encoding='utf-8', errors='ignore')
                        
                        docs[rel_path] = {
                            "content": content[:5000],  # Limit size
                            "size": len(content),
                            "lines": len(content.splitlines())
                        }
                    except Exception as e:
                        logger.warning(f"Could not read documentation {doc_file}: {e}")
        
        return docs
    
    async def _optimize_context_size(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize context size to fit within token limits"""
        logger.info("⚡ Optimizing context size for token limits...")
        
        # Prioritize important files and truncate others
        optimized_context = context.copy()
        
        # Keep metadata and structure
        # Reduce file content sizes
        for category in optimized_context.get("files", {}):
            files = optimized_context["files"][category]
            for file_path in files:
                if files[file_path].get("size", 0) > 2000:
                    # Truncate large files
                    content = files[file_path].get("content", "")
                    files[file_path]["content"] = content[:2000] + "\n... (truncated)"
        
        # Reduce documentation
        for doc_path in optimized_context.get("documentation", {}):
            doc = optimized_context["documentation"][doc_path]
            if doc.get("size", 0) > 1000:
                content = doc.get("content", "")
                doc["content"] = content[:1000] + "\n... (truncated)"
        
        return optimized_context
    
    async def _verify_connections(self):
        """Verify connections to all required services"""
        logger.info("🔗 Verifying system connections...")
        
        # Test Gemini CLI connection
        try:
            async with websockets.connect(self.gemini_server, timeout=5) as ws:
                logger.info("✅ Gemini CLI server connected")
        except Exception as e:
            logger.error(f"❌ Gemini CLI server not available: {e}")
            raise ConnectionError("Gemini CLI server required for operation")
        
        # Test Memory MCP connection (optional)
        try:
            async with websockets.connect(self.memory_server, timeout=5) as ws:
                logger.info("✅ Memory MCP server connected")
        except Exception as e:
            logger.warning(f"⚠️ Memory MCP server not available: {e}")
    
    async def _generate_improvement_roadmap(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive improvement roadmap"""
        roadmap = {
            "immediate_actions": [],
            "short_term_goals": [],
            "long_term_objectives": [],
            "estimated_timeline": {},
            "resource_requirements": {}
        }
        
        # Process recommendations into roadmap
        recommendations = analysis.get("prioritized_recommendations", [])
        
        for rec in recommendations:
            priority = rec.get("priority", "medium")
            
            if priority == "high" or rec.get("safety_level") == "safe":
                roadmap["immediate_actions"].append(rec)
            elif priority == "medium":
                roadmap["short_term_goals"].append(rec)
            else:
                roadmap["long_term_objectives"].append(rec)
        
        # Estimate timeline
        roadmap["estimated_timeline"] = {
            "immediate": f"{len(roadmap['immediate_actions'])} items - 1-2 weeks",
            "short_term": f"{len(roadmap['short_term_goals'])} items - 1-2 months", 
            "long_term": f"{len(roadmap['long_term_objectives'])} items - 3-6 months"
        }
        
        return roadmap
# Example usage and testing
async def main():
    """Main function for testing"""
    improver = GeminiAutomatedCodeImprover("c:\\Workspace\\MCPVots")
    
    # Start the automated improvement system
    result = await improver.start_automated_improvement_system()
    print(f"🚀 System started: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
