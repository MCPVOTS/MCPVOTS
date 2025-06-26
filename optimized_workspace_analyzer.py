#!/usr/bin/env python3
"""
Optimized Comprehensive Workspace Analysis with Gemini CLI
Handles large workspaces efficiently with sampling and intelligent categorization
"""

import os
import json
import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict, Counter
import mimetypes
import hashlib
import random

# Configure logging for Windows
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('optimized_workspace_analysis.log', encoding='utf-8')
    ]
)

def safe_log(message: str, level=logging.INFO):
    """Safely log messages with Unicode handling"""
    try:
        logging.log(level, str(message).encode('ascii', 'ignore').decode('ascii'))
    except Exception:
        logging.log(level, "Log message encoding error")

class OptimizedWorkspaceAnalyzer:
    """Optimized analyzer for large workspaces with intelligent sampling"""
    
    def __init__(self, workspace_path: str = "c:\\Workspace"):
        self.workspace_path = Path(workspace_path)
        self.analysis_start_time = time.time()
        self.results = {
            "metadata": {
                "analysis_type": "optimized_comprehensive",
                "start_time": datetime.now().isoformat(),
                "workspace_path": str(self.workspace_path),
                "analyzer_version": "2.0.0"
            },
            "summary": {},
            "projects": {},
            "file_analysis": {},
            "tech_stack_analysis": {},
            "code_quality_insights": {},
            "optimization_recommendations": []
        }
        
        # Configuration for large workspace handling
        self.config = {
            "max_files_to_analyze": 10000,  # Limit for deep analysis
            "sample_percentage": 0.1,  # Sample 10% of files for detailed analysis
            "priority_extensions": {
                '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', 
                '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.swift',
                '.kt', '.scala', '.clj', '.hs', '.ml', '.r', '.sql'
            },
            "project_indicators": {
                'package.json', 'requirements.txt', 'pom.xml', 'build.gradle',
                'Cargo.toml', 'go.mod', 'composer.json', 'setup.py',
                'pyproject.toml', 'CMakeLists.txt', 'Makefile'
            },
            "ignore_patterns": {
                'node_modules', '.git', '__pycache__', '.vscode', '.idea',
                'dist', 'build', 'target', '.pytest_cache', '.mypy_cache',
                'venv', 'env', '.env', 'vendor', 'bower_components'
            }
        }
        
        safe_log("🚀 Optimized Workspace Analyzer initialized for large-scale analysis")
    
    async def analyze_workspace_optimized(self) -> Dict[str, Any]:
        """Perform optimized comprehensive workspace analysis"""
        try:
            safe_log("🔍 Starting optimized comprehensive workspace analysis...")
            
            # Phase 1: Fast file discovery and smart categorization
            safe_log("Phase 1: Smart File Discovery and Categorization")
            file_inventory = await self._smart_file_discovery()
            
            # Phase 2: Project identification and prioritization
            safe_log("Phase 2: Project Identification and Prioritization")
            projects = await self._identify_and_prioritize_projects(file_inventory)
            
            # Phase 3: Intelligent sampling and analysis
            safe_log("Phase 3: Intelligent Sampling and Deep Analysis")
            sampled_analysis = await self._intelligent_sampling_analysis(file_inventory, projects)
            
            # Phase 4: Tech stack and architecture analysis
            safe_log("Phase 4: Technology Stack and Architecture Analysis")
            tech_analysis = await self._analyze_technology_landscape(projects, file_inventory)
            
            # Phase 5: Code quality and patterns analysis
            safe_log("Phase 5: Code Quality and Pattern Analysis")
            quality_analysis = await self._analyze_code_quality_patterns(sampled_analysis)
            
            # Phase 6: Generate insights and recommendations
            safe_log("Phase 6: Generate Insights and Recommendations")
            insights = await self._generate_optimization_insights(projects, tech_analysis, quality_analysis)
            
            # Compile final results
            self.results.update({
                "summary": {
                    "total_files": file_inventory["total_files"],
                    "analyzed_files": len(sampled_analysis.get("analyzed_files", [])),
                    "total_projects": len(projects),
                    "analysis_duration": time.time() - self.analysis_start_time,
                    "sampling_ratio": self.config["sample_percentage"]
                },
                "file_inventory": file_inventory,
                "projects": projects,
                "sampled_analysis": sampled_analysis,
                "tech_analysis": tech_analysis,
                "quality_analysis": quality_analysis,
                "insights": insights
            })
            
            # Save results
            await self._save_analysis_results()
            
            safe_log(f"✅ Optimized analysis completed in {time.time() - self.analysis_start_time:.2f} seconds")
            return self.results
            
        except Exception as e:
            safe_log(f"❌ Error in optimized workspace analysis: {e}", logging.ERROR)
            raise
    
    async def _smart_file_discovery(self) -> Dict[str, Any]:
        """Smart file discovery with efficient categorization"""
        try:
            safe_log("📁 Discovering files with smart categorization...")
            
            file_categories = defaultdict(list)
            extension_counts = Counter()
            size_stats = {"total_size": 0, "file_sizes": []}
            ignored_count = 0
            
            # Walk through workspace efficiently
            for root, dirs, files in os.walk(self.workspace_path):
                # Skip ignored directories
                dirs[:] = [d for d in dirs if not self._should_ignore_path(Path(root) / d)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    if self._should_ignore_path(file_path):
                        ignored_count += 1
                        continue
                    
                    try:
                        ext = file_path.suffix.lower()
                        file_size = file_path.stat().st_size
                        
                        # Categorize file
                        category = self._categorize_file(file_path)
                        file_categories[category].append({
                            "path": str(file_path),
                            "size": file_size,
                            "extension": ext,
                            "modified": file_path.stat().st_mtime
                        })
                        
                        extension_counts[ext] += 1
                        size_stats["total_size"] += file_size
                        size_stats["file_sizes"].append(file_size)
                        
                    except (OSError, PermissionError):
                        continue
            
            # Calculate statistics
            total_files = sum(len(files) for files in file_categories.values())
            avg_file_size = size_stats["total_size"] / total_files if total_files > 0 else 0
            
            inventory = {
                "total_files": total_files,
                "ignored_files": ignored_count,
                "categories": dict(file_categories),
                "extension_distribution": dict(extension_counts.most_common(50)),
                "size_statistics": {
                    "total_size_mb": size_stats["total_size"] / (1024 * 1024),
                    "average_file_size": avg_file_size,
                    "largest_files": sorted(size_stats["file_sizes"], reverse=True)[:10]
                },
                "category_summary": {cat: len(files) for cat, files in file_categories.items()}
            }
            
            safe_log(f"📊 Discovered {total_files} files in {len(file_categories)} categories")
            safe_log(f"📊 Top file types: {dict(extension_counts.most_common(5))}")
            
            return inventory
            
        except Exception as e:
            safe_log(f"Error in smart file discovery: {e}", logging.ERROR)
            raise
    
    async def _identify_and_prioritize_projects(self, file_inventory: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and prioritize projects for analysis"""
        try:
            safe_log("🎯 Identifying and prioritizing projects...")
            
            projects = {}
            project_roots = set()
            
            # Find project roots based on configuration files
            config_files = file_inventory["categories"].get("config", [])
            
            for config_file in config_files:
                file_path = Path(config_file["path"])
                filename = file_path.name
                
                if filename in self.config["project_indicators"]:
                    project_root = file_path.parent
                    project_name = project_root.name
                    
                    if project_root not in project_roots:
                        project_roots.add(project_root)
                        
                        # Analyze project
                        project_info = await self._analyze_project_structure(project_root, filename)
                        projects[project_name] = {
                            "root_path": str(project_root),
                            "config_file": filename,
                            "priority": self._calculate_project_priority(project_info),
                            "info": project_info
                        }
            
            # Sort projects by priority
            sorted_projects = dict(sorted(
                projects.items(), 
                key=lambda x: x[1]["priority"], 
                reverse=True
            ))
            
            safe_log(f"🏗️ Identified {len(projects)} projects")
            for name, info in list(sorted_projects.items())[:5]:
                safe_log(f"   • {name} (priority: {info['priority']:.2f})", )
                safe_log(f"   • {name} (priority: {info['priority']:.2f})")
            
            return sorted_projects
            
        except Exception as e:
            safe_log(f"Error in project identification: {e}", logging.ERROR)
            return {}
    
    async def _intelligent_sampling_analysis(self, file_inventory: Dict[str, Any], projects: Dict[str, Any]) -> Dict[str, Any]:
        """Perform intelligent sampling for detailed analysis"""
        try:
            safe_log("🎲 Performing intelligent sampling analysis...")
            
            # Collect files for sampling
            all_code_files = []
            for category in ["code", "scripts"]:
                if category in file_inventory["categories"]:
                    all_code_files.extend(file_inventory["categories"][category])
            
            # Prioritize files for sampling
            prioritized_files = self._prioritize_files_for_sampling(all_code_files, projects)
            
            # Sample files intelligently
            max_files = min(self.config["max_files_to_analyze"], len(prioritized_files))
            sampled_files = prioritized_files[:max_files]
            
            safe_log(f"🔬 Analyzing {len(sampled_files)} sampled files out of {len(all_code_files)} total")
            
            # Analyze sampled files
            analysis_results = {
                "analyzed_files": [],
                "language_distribution": Counter(),
                "complexity_metrics": [],
                "pattern_analysis": defaultdict(list),
                "import_dependencies": defaultdict(set),
                "function_analysis": []
            }
            
            for i, file_info in enumerate(sampled_files[:1000]):  # Limit to prevent timeout
                if i % 100 == 0:
                    safe_log(f"   📝 Analyzed {i}/{len(sampled_files)} files...")
                
                file_analysis = await self._analyze_code_file(file_info)
                if file_analysis:
                    analysis_results["analyzed_files"].append(file_analysis)
                    
                    # Update statistics
                    lang = file_analysis.get("language", "unknown")
                    analysis_results["language_distribution"][lang] += 1
                    
                    if "complexity" in file_analysis:
                        analysis_results["complexity_metrics"].append(file_analysis["complexity"])
                    
                    # Pattern detection
                    patterns = file_analysis.get("patterns", [])
                    for pattern in patterns:
                        analysis_results["pattern_analysis"][pattern].append(file_info["path"])
                    
                    # Dependencies
                    imports = file_analysis.get("imports", [])
                    for imp in imports:
                        analysis_results["import_dependencies"][lang].add(imp)
            
            # Convert sets to lists for JSON serialization
            analysis_results["import_dependencies"] = {
                k: list(v) for k, v in analysis_results["import_dependencies"].items()
            }
            
            safe_log(f"📊 Sampled analysis complete: {len(analysis_results['analyzed_files'])} files analyzed")
            return analysis_results
            
        except Exception as e:
            safe_log(f"Error in intelligent sampling: {e}", logging.ERROR)
            return {}
    
    async def _analyze_technology_landscape(self, projects: Dict[str, Any], file_inventory: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the overall technology landscape"""
        try:
            safe_log("🔧 Analyzing technology landscape...")
            
            tech_landscape = {
                "languages": Counter(),
                "frameworks": Counter(),
                "databases": Counter(),
                "cloud_services": Counter(),
                "build_tools": Counter(),
                "testing_frameworks": Counter(),
                "architecture_patterns": Counter()
            }
            
            # Analyze each project's technology stack
            for project_name, project_info in projects.items():
                project_tech = await self._extract_project_technologies(project_info)
                
                # Aggregate technology usage
                for category, technologies in project_tech.items():
                    if category in tech_landscape:
                        for tech in technologies:
                            tech_landscape[category][tech] += 1
            
            # Analyze file extensions for language detection
            extensions = file_inventory.get("extension_distribution", {})
            language_mapping = {
                '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
                '.java': 'Java', '.go': 'Go', '.rs': 'Rust', '.cpp': 'C++',
                '.c': 'C', '.cs': 'C#', '.php': 'PHP', '.rb': 'Ruby',
                '.swift': 'Swift', '.kt': 'Kotlin', '.scala': 'Scala'
            }
            
            for ext, count in extensions.items():
                if ext in language_mapping:
                    tech_landscape["languages"][language_mapping[ext]] += count
            
            # Convert Counters to dicts for JSON serialization
            tech_landscape = {k: dict(v.most_common(20)) for k, v in tech_landscape.items()}
            
            safe_log(f"🛠️ Technology landscape analysis complete")
            safe_log(f"   Languages: {list(tech_landscape['languages'].keys())[:5]}")
            
            return tech_landscape
            
        except Exception as e:
            safe_log(f"Error in technology landscape analysis: {e}", logging.ERROR)
            return {}
    
    async def _analyze_code_quality_patterns(self, sampled_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code quality and patterns from sampled files"""
        try:
            safe_log("📈 Analyzing code quality patterns...")
            
            quality_metrics = {
                "average_complexity": 0,
                "pattern_usage": {},
                "code_smells": Counter(),
                "best_practices": Counter(),
                "technical_debt_indicators": Counter(),
                "security_patterns": Counter()
            }
            
            analyzed_files = sampled_analysis.get("analyzed_files", [])
            if not analyzed_files:
                return quality_metrics
            
            # Calculate average complexity
            complexities = [f.get("complexity", 0) for f in analyzed_files if "complexity" in f]
            if complexities:
                quality_metrics["average_complexity"] = sum(complexities) / len(complexities)
            
            # Analyze patterns
            pattern_analysis = sampled_analysis.get("pattern_analysis", {})
            quality_metrics["pattern_usage"] = {
                pattern: len(files) for pattern, files in pattern_analysis.items()
            }
            
            # Detect code smells and best practices
            for file_analysis in analyzed_files:
                # Code smells detection
                if file_analysis.get("complexity", 0) > 10:
                    quality_metrics["code_smells"]["high_complexity"] += 1
                
                if file_analysis.get("line_count", 0) > 1000:
                    quality_metrics["code_smells"]["large_file"] += 1
                
                # Best practices detection
                if "test" in file_analysis.get("filename", "").lower():
                    quality_metrics["best_practices"]["testing"] += 1
                
                if any(pattern in file_analysis.get("patterns", []) for pattern in ["singleton", "factory", "observer"]):
                    quality_metrics["best_practices"]["design_patterns"] += 1
            
            # Convert Counters to dicts
            quality_metrics["code_smells"] = dict(quality_metrics["code_smells"])
            quality_metrics["best_practices"] = dict(quality_metrics["best_practices"])
            quality_metrics["technical_debt_indicators"] = dict(quality_metrics["technical_debt_indicators"])
            quality_metrics["security_patterns"] = dict(quality_metrics["security_patterns"])
            
            safe_log(f"📊 Code quality analysis complete")
            safe_log(f"   Average complexity: {quality_metrics['average_complexity']:.2f}")
            
            return quality_metrics
            
        except Exception as e:
            safe_log(f"Error in code quality analysis: {e}", logging.ERROR)
            return {}
    
    async def _generate_optimization_insights(self, projects: Dict[str, Any], tech_analysis: Dict[str, Any], quality_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimization insights and recommendations"""
        try:
            safe_log("💡 Generating optimization insights...")
            
            insights = {
                "code_optimization": [],
                "architecture_recommendations": [],
                "technology_modernization": [],
                "performance_improvements": [],
                "security_enhancements": [],
                "development_process": []
            }
            
            # Code optimization insights
            avg_complexity = quality_analysis.get("average_complexity", 0)
            if avg_complexity > 8:
                insights["code_optimization"].append({
                    "type": "complexity_reduction",
                    "description": f"High average complexity ({avg_complexity:.1f}). Consider refactoring complex functions.",
                    "priority": "high",
                    "impact": "maintainability"
                })
            
            # Technology modernization
            languages = tech_analysis.get("languages", {})
            if "JavaScript" in languages and languages["JavaScript"] > languages.get("TypeScript", 0) * 2:
                insights["technology_modernization"].append({
                    "type": "typescript_migration",
                    "description": "High JavaScript usage. Consider migrating to TypeScript for better type safety.",
                    "priority": "medium",
                    "impact": "code_quality"
                })
            
            # Architecture recommendations
            if len(projects) > 10:
                insights["architecture_recommendations"].append({
                    "type": "monorepo_consideration",
                    "description": f"Large number of projects ({len(projects)}). Consider monorepo architecture.",
                    "priority": "medium",
                    "impact": "maintenance"
                })
            
            # Performance improvements
            pattern_usage = quality_analysis.get("pattern_usage", {})
            if pattern_usage.get("synchronous_operations", 0) > 50:
                insights["performance_improvements"].append({
                    "type": "async_optimization",
                    "description": "High synchronous operation usage. Consider async/await patterns.",
                    "priority": "medium",
                    "impact": "performance"
                })
            
            # Security enhancements
            security_patterns = quality_analysis.get("security_patterns", {})
            if len(security_patterns) == 0:
                insights["security_enhancements"].append({
                    "type": "security_audit",
                    "description": "No security patterns detected. Conduct security audit.",
                    "priority": "high",
                    "impact": "security"
                })
            
            # Development process improvements
            test_coverage = quality_analysis.get("best_practices", {}).get("testing", 0)
            total_files = sum(len(files) for files in projects.values()) if projects else 1
            if test_coverage / total_files < 0.3:
                insights["development_process"].append({
                    "type": "testing_improvement",
                    "description": "Low test coverage. Implement comprehensive testing strategy.",
                    "priority": "high",
                    "impact": "reliability"
                })
            
            safe_log(f"💡 Generated {sum(len(v) for v in insights.values())} optimization insights")
            return insights
            
        except Exception as e:
            safe_log(f"Error generating insights: {e}", logging.ERROR)
            return {}
    
    def _should_ignore_path(self, path: Path) -> bool:
        """Check if a path should be ignored"""
        path_str = str(path).lower()
        return any(ignore in path_str for ignore in self.config["ignore_patterns"])
    
    def _categorize_file(self, file_path: Path) -> str:
        """Categorize a file based on its extension and content"""
        ext = file_path.suffix.lower()
        filename = file_path.name.lower()
        
        # Code files
        if ext in self.config["priority_extensions"]:
            return "code"
        
        # Configuration files
        if ext in {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.xml'}:
            return "config"
        
        # Documentation
        if ext in {'.md', '.rst', '.txt', '.doc', '.docx', '.pdf'}:
            return "documentation"
        
        # Scripts
        if ext in {'.sh', '.bat', '.ps1', '.fish', '.zsh'} or filename.startswith('makefile'):
            return "scripts"
        
        # Data files
        if ext in {'.csv', '.json', '.xml', '.sql', '.db', '.sqlite'}:
            return "data"
        
        # Media files
        if ext in {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp'}:
            return "media"
        
        # Hidden files
        if filename.startswith('.'):
            return "hidden"
        
        return "other"
    
    def _calculate_project_priority(self, project_info: Dict[str, Any]) -> float:
        """Calculate project priority for analysis"""
        score = 0.0
        
        # Size factor
        file_count = project_info.get("file_count", 0)
        score += min(file_count / 100, 10)  # Max 10 points for size
        
        # Recency factor
        last_modified = project_info.get("last_modified", 0)
        days_since_modified = (time.time() - last_modified) / (24 * 3600)
        score += max(0, 10 - days_since_modified / 30)  # More recent = higher score
        
        # Technology relevance
        tech_stack = project_info.get("tech_stack", [])
        modern_tech = {'typescript', 'react', 'nextjs', 'python', 'fastapi', 'go', 'rust'}
        relevance = len(set(tech_stack) & modern_tech)
        score += relevance * 2
        
        return score
    
    def _prioritize_files_for_sampling(self, files: List[Dict], projects: Dict[str, Any]) -> List[Dict]:
        """Prioritize files for intelligent sampling"""
        prioritized = []
        
        # Priority 1: Files in high-priority projects
        high_priority_paths = {
            info["root_path"] for info in projects.values() 
            if info["priority"] > 15
        }
        
        # Priority 2: Important file types
        important_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go'}
        
        # Priority 3: Main/index files
        important_names = {'main', 'index', 'app', 'server', 'client'}
        
        for file_info in files:
            file_path = Path(file_info["path"])
            priority_score = 0
            
            # Project priority
            if any(str(file_path).startswith(path) for path in high_priority_paths):
                priority_score += 10
            
            # Extension priority
            if file_path.suffix.lower() in important_extensions:
                priority_score += 5
            
            # Name priority
            if any(name in file_path.stem.lower() for name in important_names):
                priority_score += 3
            
            # Size consideration (prefer medium-sized files)
            size = file_info.get("size", 0)
            if 1000 <= size <= 50000:  # 1KB to 50KB
                priority_score += 2
            
            file_info["priority_score"] = priority_score
            prioritized.append(file_info)
        
        # Sort by priority score
        return sorted(prioritized, key=lambda x: x["priority_score"], reverse=True)
    
    async def _analyze_project_structure(self, project_root: Path, config_file: str) -> Dict[str, Any]:
        """Analyze individual project structure"""
        try:
            project_info = {
                "config_file": config_file,
                "file_count": 0,
                "tech_stack": [],
                "last_modified": 0,
                "structure": {}
            }
            
            # Count files and get modification time
            for root, dirs, files in os.walk(project_root):
                dirs[:] = [d for d in dirs if not self._should_ignore_path(Path(root) / d)]
                
                for file in files:
                    file_path = Path(root) / file
                    if not self._should_ignore_path(file_path):
                        project_info["file_count"] += 1
                        try:
                            mtime = file_path.stat().st_mtime
                            project_info["last_modified"] = max(project_info["last_modified"], mtime)
                        except OSError:
                            pass
            
            # Extract tech stack from config file
            config_path = project_root / config_file
            if config_path.exists():
                project_info["tech_stack"] = await self._extract_tech_stack_from_config(config_path, config_file)
            
            return project_info
            
        except Exception as e:
            safe_log(f"Error analyzing project {project_root}: {e}", logging.WARNING)
            return {"error": str(e)}
    
    async def _extract_tech_stack_from_config(self, config_path: Path, config_file: str) -> List[str]:
        """Extract technology stack from configuration file"""
        try:
            tech_stack = []
            
            if config_file == "package.json":
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                dependencies = data.get("dependencies", {})
                dev_dependencies = data.get("devDependencies", {})
                all_deps = {**dependencies, **dev_dependencies}
                
                # Extract framework information
                if "react" in all_deps:
                    tech_stack.append("react")
                if "next" in all_deps or "nextjs" in all_deps:
                    tech_stack.append("nextjs")
                if "vue" in all_deps:
                    tech_stack.append("vue")
                if "angular" in all_deps:
                    tech_stack.append("angular")
                if "express" in all_deps:
                    tech_stack.append("express")
                if "typescript" in all_deps or "@types" in str(all_deps):
                    tech_stack.append("typescript")
                else:
                    tech_stack.append("javascript")
            
            elif config_file in ["requirements.txt", "pyproject.toml", "setup.py"]:
                tech_stack.append("python")
                
                if config_path.name == "requirements.txt":
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        if "django" in content:
                            tech_stack.append("django")
                        if "flask" in content:
                            tech_stack.append("flask")
                        if "fastapi" in content:
                            tech_stack.append("fastapi")
            
            elif config_file == "go.mod":
                tech_stack.append("go")
            
            elif config_file == "Cargo.toml":
                tech_stack.append("rust")
            
            elif config_file in ["pom.xml", "build.gradle"]:
                tech_stack.append("java")
            
            return tech_stack
            
        except Exception as e:
            safe_log(f"Error extracting tech stack from {config_path}: {e}", logging.WARNING)
            return []
    
    async def _analyze_code_file(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze individual code file"""
        try:
            file_path = Path(file_info["path"])
            
            # Basic file analysis
            analysis = {
                "path": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix,
                "size": file_info.get("size", 0),
                "language": self._detect_language(file_path),
                "line_count": 0,
                "complexity": 0,
                "patterns": [],
                "imports": []
            }
            
            # Read and analyze file content (with size limit)
            if analysis["size"] > 1024 * 1024:  # Skip files larger than 1MB
                return analysis
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                lines = content.split('\n')
                analysis["line_count"] = len(lines)
                
                # Basic complexity analysis
                analysis["complexity"] = self._calculate_basic_complexity(content, analysis["language"])
                
                # Pattern detection
                analysis["patterns"] = self._detect_patterns(content, analysis["language"])
                
                # Import analysis
                analysis["imports"] = self._extract_imports(content, analysis["language"])
                
            except (UnicodeDecodeError, PermissionError, OSError):
                pass
            
            return analysis
            
        except Exception as e:
            safe_log(f"Error analyzing file {file_info.get('path', 'unknown')}: {e}", logging.WARNING)
            return None
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        ext = file_path.suffix.lower()
        language_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.jsx': 'javascript', '.tsx': 'typescript', '.java': 'java',
            '.go': 'go', '.rs': 'rust', '.cpp': 'cpp', '.c': 'c',
            '.cs': 'csharp', '.php': 'php', '.rb': 'ruby',
            '.swift': 'swift', '.kt': 'kotlin', '.scala': 'scala'
        }
        return language_map.get(ext, 'unknown')
    
    def _calculate_basic_complexity(self, content: str, language: str) -> int:
        """Calculate basic cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        # Language-specific complexity indicators
        if language in ['python', 'javascript', 'typescript']:
            complexity += content.count('if ')
            complexity += content.count('elif ')
            complexity += content.count('else ')
            complexity += content.count('for ')
            complexity += content.count('while ')
            complexity += content.count('try:')
            complexity += content.count('except ')
            complexity += content.count('and ')
            complexity += content.count('or ')
        
        elif language == 'java':
            complexity += content.count('if (')
            complexity += content.count('else ')
            complexity += content.count('for (')
            complexity += content.count('while (')
            complexity += content.count('switch (')
            complexity += content.count('case ')
            complexity += content.count('catch (')
        
        return complexity
    
    def _detect_patterns(self, content: str, language: str) -> List[str]:
        """Detect common programming patterns"""
        patterns = []
        content_lower = content.lower()
        
        # Common patterns across languages
        if 'singleton' in content_lower:
            patterns.append('singleton')
        if 'factory' in content_lower:
            patterns.append('factory')
        if 'observer' in content_lower:
            patterns.append('observer')
        if 'strategy' in content_lower:
            patterns.append('strategy')
        if 'decorator' in content_lower:
            patterns.append('decorator')
        
        # Language-specific patterns
        if language == 'python':
            if '__init__' in content:
                patterns.append('class_initialization')
            if 'async def' in content:
                patterns.append('async_programming')
            if 'yield' in content:
                patterns.append('generator')
        
        elif language in ['javascript', 'typescript']:
            if 'async function' in content or 'async ' in content:
                patterns.append('async_programming')
            if 'Promise' in content:
                patterns.append('promises')
            if 'useEffect' in content or 'useState' in content:
                patterns.append('react_hooks')
        
        return patterns
    
    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract import statements"""
        imports = []
        lines = content.split('\n')
        
        for line in lines[:50]:  # Check first 50 lines
            line = line.strip()
            
            if language == 'python':
                if line.startswith('import ') or line.startswith('from '):
                    imports.append(line)
            
            elif language in ['javascript', 'typescript']:
                if line.startswith('import ') or line.startswith('const ') and 'require(' in line:
                    imports.append(line)
            
            elif language == 'java':
                if line.startswith('import '):
                    imports.append(line)
        
        return imports[:10]  # Limit to first 10 imports
    
    async def _extract_project_technologies(self, project_info: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract detailed technology information from project"""
        technologies = {
            "languages": project_info.get("tech_stack", []),
            "frameworks": [],
            "databases": [],
            "cloud_services": [],
            "build_tools": [],
            "testing_frameworks": []
        }
        
        # Analyze based on tech stack
        tech_stack = project_info.get("tech_stack", [])
        
        for tech in tech_stack:
            if tech in ['react', 'vue', 'angular', 'nextjs', 'express', 'django', 'flask', 'fastapi']:
                technologies["frameworks"].append(tech)
            elif tech in ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite']:
                technologies["databases"].append(tech)
        
        return technologies
    
    async def _save_analysis_results(self):
        """Save analysis results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"optimized_workspace_analysis_{timestamp}.json"
            
            # Add metadata
            self.results["metadata"]["end_time"] = datetime.now().isoformat()
            self.results["metadata"]["total_duration"] = time.time() - self.analysis_start_time
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
            
            safe_log(f"💾 Analysis results saved to: {filename}")
            
            # Also save a summary report
            summary_filename = f"workspace_summary_{timestamp}.md"
            await self._generate_summary_report(summary_filename)
            
        except Exception as e:
            safe_log(f"Error saving analysis results: {e}", logging.ERROR)
    
    async def _generate_summary_report(self, filename: str):
        """Generate a human-readable summary report"""
        try:
            summary = self.results.get("summary", {})
            projects = self.results.get("projects", {})
            tech_analysis = self.results.get("tech_analysis", {})
            insights = self.results.get("insights", {})
            
            report = f"""# Optimized Workspace Analysis Report
            
## 📊 Summary
- **Total Files Analyzed**: {summary.get('total_files', 0):,}
- **Sampled Files**: {summary.get('analyzed_files', 0):,}
- **Projects Identified**: {summary.get('total_projects', 0)}
- **Analysis Duration**: {summary.get('analysis_duration', 0):.2f} seconds
- **Sampling Ratio**: {summary.get('sampling_ratio', 0):.1%}

## 🏗️ Projects Overview
{len(projects)} projects identified and prioritized:

"""
            
            # Add top projects
            for i, (name, info) in enumerate(list(projects.items())[:10]):
                report += f"- **{name}** (Priority: {info.get('priority', 0):.1f})\n"
                report += f"  - Path: `{info.get('root_path', 'Unknown')}`\n"
                report += f"  - Config: {info.get('config_file', 'Unknown')}\n"
                report += f"  - Tech Stack: {', '.join(info.get('info', {}).get('tech_stack', []))}\n\n"
            
            # Add technology landscape
            report += "\n## 🛠️ Technology Landscape\n\n"
            
            languages = tech_analysis.get("languages", {})
            if languages:
                report += "### Programming Languages\n"
                for lang, count in list(languages.items())[:10]:
                    report += f"- **{lang}**: {count:,} files\n"
                report += "\n"
            
            frameworks = tech_analysis.get("frameworks", {})
            if frameworks:
                report += "### Frameworks & Libraries\n"
                for fw, count in list(frameworks.items())[:10]:
                    report += f"- **{fw}**: {count} projects\n"
                report += "\n"
            
            # Add optimization insights
            report += "\n## 💡 Optimization Insights\n\n"
            
            for category, category_insights in insights.items():
                if category_insights:
                    report += f"### {category.replace('_', ' ').title()}\n"
                    for insight in category_insights[:5]:  # Limit to top 5
                        report += f"- **{insight.get('type', 'Unknown').replace('_', ' ').title()}** (Priority: {insight.get('priority', 'Unknown')})\n"
                        report += f"  {insight.get('description', 'No description')}\n"
                        report += f"  *Impact: {insight.get('impact', 'Unknown')}*\n\n"
            
            report += f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            safe_log(f"📄 Summary report saved to: {filename}")
            
        except Exception as e:
            safe_log(f"Error generating summary report: {e}", logging.ERROR)


async def main():
    """Main function to run optimized workspace analysis"""
    try:
        safe_log("🚀 Starting Optimized Comprehensive Workspace Analysis")
        
        # Initialize analyzer
        analyzer = OptimizedWorkspaceAnalyzer()
        
        # Run analysis
        results = await analyzer.analyze_workspace_optimized()
        
        # Display summary
        safe_log("\n" + "="*60)
        safe_log("📋 ANALYSIS COMPLETE - SUMMARY")
        safe_log("="*60)
        
        summary = results.get("summary", {})
        safe_log(f"Total Files: {summary.get('total_files', 0):,}")
        safe_log(f"Analyzed Files: {summary.get('analyzed_files', 0):,}")
        safe_log(f"Projects Found: {summary.get('total_projects', 0)}")
        safe_log(f"Analysis Duration: {summary.get('analysis_duration', 0):.2f} seconds")
        
        # Display top technologies
        tech_analysis = results.get("tech_analysis", {})
        languages = tech_analysis.get("languages", {})
        if languages:
            safe_log(f"\nTop Languages: {', '.join(list(languages.keys())[:5])}")
        
        # Display insights summary
        insights = results.get("insights", {})
        total_insights = sum(len(v) for v in insights.values())
        safe_log(f"Optimization Insights Generated: {total_insights}")
        
        safe_log("\n✅ Optimized workspace analysis completed successfully!")
        safe_log("Check the generated JSON and Markdown files for detailed results.")
        
    except KeyboardInterrupt:
        safe_log("\n⚠️ Analysis interrupted by user")
    except Exception as e:
        safe_log(f"❌ Error in workspace analysis: {e}", logging.ERROR)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
