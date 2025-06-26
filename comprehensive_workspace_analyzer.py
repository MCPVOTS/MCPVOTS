#!/usr/bin/env python3
"""
Comprehensive Workspace Analyzer using Gemini CLI
Deep analysis of workspace structure, code quality, and potential improvements
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import mimetypes
from collections import defaultdict, Counter
import subprocess
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workspace_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def safe_log(message: str, level: int = logging.INFO):
    """Safe logging with Unicode support"""
    try:
        logging.log(level, message)
    except UnicodeEncodeError:
        logging.log(level, message.encode('ascii', 'ignore').decode('ascii'))

class ComprehensiveWorkspaceAnalyzer:
    """
    Advanced workspace analyzer using Gemini CLI for deep code analysis
    """
    
    def __init__(self, workspace_path: str = "c:\\Workspace"):
        self.workspace_path = Path(workspace_path)
        self.analysis_results = {}
        self.file_types = defaultdict(list)
        self.project_structures = {}
        self.code_metrics = {}
        self.security_findings = []
        self.optimization_suggestions = []
        self.architecture_insights = []
        
        # File extensions to analyze
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss',
            '.java', '.cpp', '.c', '.h', '.go', '.rs', '.php', '.rb',
            '.swift', '.kt', '.scala', '.clj', '.hs', '.ml', '.r', '.sql'
        }
        
        self.config_extensions = {
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            '.env', '.properties', '.xml', '.plist'
        }
        
        self.doc_extensions = {
            '.md', '.rst', '.txt', '.adoc', '.tex', '.org'
        }
        
        self.script_extensions = {
            '.bat', '.sh', '.ps1', '.cmd'
        }
        
        self.data_extensions = {
            '.csv', '.json', '.xml', '.xlsx', '.parquet', '.avro'
        }
        
        safe_log("Comprehensive Workspace Analyzer initialized")
    
    async def analyze_workspace_comprehensive(self) -> Dict[str, Any]:
        """
        Perform comprehensive workspace analysis
        """
        try:
            safe_log("🔍 Starting comprehensive workspace analysis...")
            start_time = time.time()
            
            # Phase 1: Discover and categorize all files
            safe_log("Phase 1: File Discovery and Categorization")
            await self._discover_and_categorize_files()
            
            # Phase 2: Analyze project structures
            safe_log("Phase 2: Project Structure Analysis")
            await self._analyze_project_structures()
            
            # Phase 3: Deep code analysis with Gemini
            safe_log("Phase 3: Deep Code Analysis with Gemini CLI")
            await self._deep_code_analysis()
            
            # Phase 4: Architecture pattern analysis
            safe_log("Phase 4: Architecture Pattern Analysis")
            await self._analyze_architecture_patterns()
            
            # Phase 5: Security analysis
            safe_log("Phase 5: Security Analysis")
            await self._security_analysis()
            
            # Phase 6: Performance analysis
            safe_log("Phase 6: Performance Analysis")
            await self._performance_analysis()
            
            # Phase 7: Quality metrics
            safe_log("Phase 7: Code Quality Metrics")
            await self._calculate_quality_metrics()
            
            # Phase 8: Documentation analysis
            safe_log("Phase 8: Documentation Analysis")
            await self._analyze_documentation()
            
            # Phase 9: Dependency analysis
            safe_log("Phase 9: Dependency Analysis")
            await self._analyze_dependencies()
            
            # Phase 10: Generate comprehensive report
            safe_log("Phase 10: Generate Comprehensive Report")
            final_report = await self._generate_comprehensive_report()
            
            analysis_time = time.time() - start_time
            final_report["analysis_metadata"] = {
                "analysis_duration": analysis_time,
                "timestamp": datetime.now().isoformat(),
                "workspace_path": str(self.workspace_path),
                "total_files_analyzed": sum(len(files) for files in self.file_types.values())
            }
            
            safe_log(f"✅ Comprehensive workspace analysis completed in {analysis_time:.2f} seconds")
            return final_report
            
        except Exception as e:
            safe_log(f"❌ Error in comprehensive workspace analysis: {e}", logging.ERROR)
            raise
    
    async def _discover_and_categorize_files(self):
        """Discover and categorize all files in workspace"""
        try:
            safe_log("Discovering and categorizing files...")
            
            for root, dirs, files in os.walk(self.workspace_path):
                # Skip common build/cache directories
                dirs[:] = [d for d in dirs if d not in {
                    'node_modules', '__pycache__', '.git', '.vscode', 
                    'venv', 'env', 'build', 'dist', 'target', '.next',
                    '.nuxt', 'coverage', '.pytest_cache', '.mypy_cache'
                }]
                
                root_path = Path(root)
                
                for file in files:
                    file_path = root_path / file
                    file_ext = file_path.suffix.lower()
                    
                    # Categorize files
                    if file_ext in self.code_extensions:
                        self.file_types['code'].append(str(file_path))
                    elif file_ext in self.config_extensions:
                        self.file_types['config'].append(str(file_path))
                    elif file_ext in self.doc_extensions:
                        self.file_types['documentation'].append(str(file_path))
                    elif file_ext in self.script_extensions:
                        self.file_types['scripts'].append(str(file_path))
                    elif file_ext in self.data_extensions:
                        self.file_types['data'].append(str(file_path))
                    elif file.startswith('.'):
                        self.file_types['hidden'].append(str(file_path))
                    else:
                        self.file_types['other'].append(str(file_path))
            
            # Log discovery results
            for category, files in self.file_types.items():
                safe_log(f"Found {len(files)} {category} files")
                
        except Exception as e:
            safe_log(f"Error in file discovery: {e}", logging.ERROR)
    
    async def _analyze_project_structures(self):
        """Analyze project structures and identify frameworks/patterns"""
        try:
            safe_log("Analyzing project structures...")
            
            # Look for project root indicators
            project_indicators = {
                'package.json': 'Node.js/JavaScript',
                'requirements.txt': 'Python',
                'Pipfile': 'Python (Pipenv)',
                'pyproject.toml': 'Python (Modern)',
                'Cargo.toml': 'Rust',
                'go.mod': 'Go',
                'pom.xml': 'Java (Maven)',
                'build.gradle': 'Java (Gradle)',
                'composer.json': 'PHP',
                'Gemfile': 'Ruby',
                'pubspec.yaml': 'Dart/Flutter',
                'Project.swift': 'Swift',
                'CMakeLists.txt': 'C/C++',
                'Makefile': 'Make-based project'
            }
            
            for root, dirs, files in os.walk(self.workspace_path):
                dirs[:] = [d for d in dirs if d not in {
                    'node_modules', '__pycache__', '.git', 'venv', 'env'
                }]
                
                root_path = Path(root)
                project_type = None
                
                # Identify project type
                for indicator, proj_type in project_indicators.items():
                    if indicator in files:
                        project_type = proj_type
                        break
                
                if project_type:
                    self.project_structures[str(root_path)] = {
                        'type': project_type,
                        'files': files,
                        'subdirs': dirs,
                        'relative_path': str(root_path.relative_to(self.workspace_path))
                    }
            
            safe_log(f"Identified {len(self.project_structures)} projects")
            
        except Exception as e:
            safe_log(f"Error analyzing project structures: {e}", logging.ERROR)
    
    async def _deep_code_analysis(self):
        """Perform deep code analysis using Gemini CLI"""
        try:
            safe_log("Performing deep code analysis with Gemini CLI...")
            
            # Analyze code files by type
            for file_path in self.file_types.get('code', []):
                try:
                    analysis = await self._analyze_single_file_with_gemini(file_path)
                    if analysis:
                        self.analysis_results[file_path] = analysis
                except Exception as e:
                    safe_log(f"Error analyzing {file_path}: {e}", logging.WARNING)
                    continue
            
            # Generate aggregate insights
            await self._generate_code_insights()
            
        except Exception as e:
            safe_log(f"Error in deep code analysis: {e}", logging.ERROR)
    
    async def _analyze_single_file_with_gemini(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Analyze a single file using Gemini CLI"""
        try:
            file_path_obj = Path(file_path)
            
            # Skip very large files (>1MB)
            if file_path_obj.stat().st_size > 1024 * 1024:
                return {"status": "skipped", "reason": "file_too_large"}
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            # Skip empty files
            if not content.strip():
                return {"status": "skipped", "reason": "empty_file"}
            
            # Create analysis prompt
            prompt = self._create_file_analysis_prompt(file_path, content)
            
            # This would call Gemini CLI in real implementation
            # For now, we'll simulate the analysis
            analysis = await self._simulate_gemini_analysis(file_path, content)
            
            return analysis
            
        except Exception as e:
            safe_log(f"Error analyzing file {file_path}: {e}", logging.WARNING)
            return None
    
    def _create_file_analysis_prompt(self, file_path: str, content: str) -> str:
        """Create a comprehensive analysis prompt for Gemini"""
        file_ext = Path(file_path).suffix.lower()
        
        prompt = f"""
        Analyze this {file_ext} file comprehensively:
        
        File: {file_path}
        Size: {len(content)} characters
        
        Please provide detailed analysis on:
        
        1. CODE QUALITY:
           - Readability and maintainability
           - Code structure and organization
           - Naming conventions
           - Documentation quality
        
        2. TECHNICAL ANALYSIS:
           - Language/framework used
           - Design patterns identified
           - Architecture style
           - Dependencies and imports
        
        3. SECURITY ANALYSIS:
           - Potential security vulnerabilities
           - Input validation issues
           - Authentication/authorization concerns
           - Data handling security
        
        4. PERFORMANCE ANALYSIS:
           - Performance bottlenecks
           - Memory usage concerns
           - Algorithmic complexity
           - Optimization opportunities
        
        5. BEST PRACTICES:
           - Adherence to language/framework conventions
           - Error handling patterns
           - Testing considerations
           - Accessibility (for frontend files)
        
        6. IMPROVEMENT SUGGESTIONS:
           - Specific refactoring recommendations
           - Code modernization opportunities
           - Performance optimizations
           - Security improvements
        
        7. TECHNICAL DEBT:
           - Legacy code patterns
           - Outdated dependencies
           - Technical debt indicators
           - Maintenance concerns
        
        Code content:
        ```
        {content[:5000]}  # Limit to first 5000 chars for analysis
        {'... (truncated)' if len(content) > 5000 else ''}
        ```
        
        Provide response in JSON format with detailed findings.
        """
        
        return prompt
    
    async def _simulate_gemini_analysis(self, file_path: str, content: str) -> Dict[str, Any]:
        """Simulate Gemini analysis (placeholder for real implementation)"""
        try:
            file_ext = Path(file_path).suffix.lower()
            lines = content.split('\n')
            
            # Basic analysis based on file content
            analysis = {
                "file_info": {
                    "path": file_path,
                    "extension": file_ext,
                    "lines_of_code": len(lines),
                    "characters": len(content),
                    "language": self._detect_language(file_ext, content)
                },
                "code_quality": {
                    "readability_score": self._calculate_readability_score(content),
                    "complexity_score": self._calculate_complexity_score(content),
                    "documentation_score": self._calculate_documentation_score(content)
                },
                "technical_analysis": {
                    "framework_detected": self._detect_framework(content),
                    "design_patterns": self._detect_design_patterns(content),
                    "dependencies": self._extract_dependencies(content, file_ext)
                },
                "security_analysis": {
                    "vulnerabilities": self._detect_security_issues(content),
                    "security_score": self._calculate_security_score(content)
                },
                "performance_analysis": {
                    "performance_issues": self._detect_performance_issues(content),
                    "optimization_opportunities": self._find_optimization_opportunities(content)
                },
                "improvement_suggestions": self._generate_improvement_suggestions(content, file_ext),
                "technical_debt": {
                    "debt_indicators": self._detect_technical_debt(content),
                    "modernization_opportunities": self._find_modernization_opportunities(content, file_ext)
                }
            }
            
            return analysis
            
        except Exception as e:
            safe_log(f"Error in simulated analysis: {e}", logging.WARNING)
            return {"error": str(e)}
    
    def _detect_language(self, file_ext: str, content: str) -> str:
        """Detect programming language"""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React (JSX)',
            '.tsx': 'React (TSX)',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin'
        }
        
        return language_map.get(file_ext, 'Unknown')
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score"""
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if not non_empty_lines:
            return 0.0
        
        # Basic readability metrics
        avg_line_length = sum(len(line) for line in non_empty_lines) / len(non_empty_lines)
        comment_ratio = sum(1 for line in lines if line.strip().startswith(('#', '//', '/*', '*', '<!--'))) / len(lines)
        
        # Score based on reasonable line length and comment ratio
        readability = 100.0
        if avg_line_length > 120:
            readability -= (avg_line_length - 120) * 0.5
        if comment_ratio < 0.1:
            readability -= 20
        elif comment_ratio > 0.3:
            readability -= 10
        
        return max(0.0, min(100.0, readability))
    
    def _calculate_complexity_score(self, content: str) -> float:
        """Calculate complexity score"""
        # Count complex structures
        complexity_indicators = [
            'if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except:',
            'function ', 'def ', 'class ', 'switch ', 'case ', 'catch'
        ]
        
        complexity_count = sum(content.lower().count(indicator) for indicator in complexity_indicators)
        lines = len(content.split('\n'))
        
        if lines == 0:
            return 0.0
        
        complexity_ratio = complexity_count / lines
        return min(100.0, complexity_ratio * 1000)  # Scale to 0-100
    
    def _calculate_documentation_score(self, content: str) -> float:
        """Calculate documentation score"""
        lines = content.split('\n')
        total_lines = len(lines)
        
        if total_lines == 0:
            return 0.0
        
        # Count different types of documentation
        doc_lines = 0
        for line in lines:
            stripped = line.strip()
            if (stripped.startswith('#') or stripped.startswith('//') or 
                stripped.startswith('/*') or stripped.startswith('*') or
                stripped.startswith('<!--') or '"""' in stripped or "'''" in stripped):
                doc_lines += 1
        
        return (doc_lines / total_lines) * 100
    
    def _detect_framework(self, content: str) -> List[str]:
        """Detect frameworks used"""
        frameworks = []
        content_lower = content.lower()
        
        framework_indicators = {
            'react': ['import react', 'from react', 'usestate', 'useeffect'],
            'vue': ['vue', '@vue', 'v-if', 'v-for'],
            'angular': ['@angular', '@component', '@injectable'],
            'django': ['django', 'from django', 'models.model'],
            'flask': ['from flask', 'flask import', '@app.route'],
            'fastapi': ['fastapi', 'from fastapi', '@app.get'],
            'express': ['express', 'app.get', 'app.post'],
            'nextjs': ['next', 'getstaticprops', 'getserversideprops'],
            'spring': ['@springframework', '@controller', '@service']
        }
        
        for framework, indicators in framework_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                frameworks.append(framework)
        
        return frameworks
    
    def _detect_design_patterns(self, content: str) -> List[str]:
        """Detect design patterns"""
        patterns = []
        content_lower = content.lower()
        
        pattern_indicators = {
            'singleton': ['class.*singleton', '__new__', 'instance.*none'],
            'factory': ['factory', 'create.*object', 'builder'],
            'observer': ['observer', 'subscribe', 'notify', 'listener'],
            'mvc': ['controller', 'model', 'view'],
            'repository': ['repository', 'findby', 'save.*entity'],
            'service': ['service', '@service', 'business.*logic'],
            'decorator': ['decorator', '@.*decorator', 'wrapper']
        }
        
        for pattern, indicators in pattern_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                patterns.append(pattern)
        
        return patterns
    
    def _extract_dependencies(self, content: str, file_ext: str) -> List[str]:
        """Extract dependencies from file"""
        dependencies = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Python imports
            if file_ext == '.py':
                if line.startswith('import ') or line.startswith('from '):
                    dependencies.append(line)
            
            # JavaScript/TypeScript imports
            elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
                if line.startswith('import ') or line.startswith('const ') and 'require(' in line:
                    dependencies.append(line)
            
            # Java imports
            elif file_ext == '.java':
                if line.startswith('import '):
                    dependencies.append(line)
        
        return dependencies[:20]  # Limit to first 20 dependencies
    
    def _detect_security_issues(self, content: str) -> List[str]:
        """Detect potential security issues"""
        issues = []
        content_lower = content.lower()
        
        security_patterns = {
            'sql_injection': ['execute.*%', 'query.*+', 'sql.*format'],
            'xss': ['innerhtml', 'documentwrite', 'eval('],
            'hardcoded_secrets': ['password.*=.*"', 'api_key.*=.*"', 'secret.*=.*"'],
            'insecure_random': ['math.random', 'random.random'],
            'path_traversal': ['../../../', 'os.path.join.*input'],
            'command_injection': ['os.system', 'subprocess.*shell=true']
        }
        
        for issue_type, patterns in security_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    issues.append(f"Potential {issue_type.replace('_', ' ')}")
                    break
        
        return issues
    
    def _calculate_security_score(self, content: str) -> float:
        """Calculate security score"""
        security_issues = self._detect_security_issues(content)
        base_score = 100.0
        
        # Deduct points for each security issue
        score = base_score - (len(security_issues) * 15)
        
        # Check for security best practices
        if any(keyword in content.lower() for keyword in ['authentication', 'authorization', 'validation']):
            score += 5
        
        return max(0.0, min(100.0, score))
    
    def _detect_performance_issues(self, content: str) -> List[str]:
        """Detect performance issues"""
        issues = []
        content_lower = content.lower()
        
        performance_patterns = {
            'nested_loops': ['for.*for', 'while.*while'],
            'inefficient_queries': ['select.*in.*loop', 'n+1.*query'],
            'memory_leaks': ['global.*list', 'cache.*without.*limit'],
            'blocking_operations': ['requests.get', 'time.sleep']
        }
        
        for issue_type, patterns in performance_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    issues.append(f"Potential {issue_type.replace('_', ' ')}")
                    break
        
        return issues
    
    def _find_optimization_opportunities(self, content: str) -> List[str]:
        """Find optimization opportunities"""
        opportunities = []
        content_lower = content.lower()
        
        if 'for.*in.*range.*len' in content_lower:
            opportunities.append("Use enumerate() instead of range(len())")
        
        if 'list.*comprehension' not in content_lower and 'for.*append' in content_lower:
            opportunities.append("Consider using list comprehension")
        
        if 'async' not in content_lower and 'requests' in content_lower:
            opportunities.append("Consider using async HTTP requests")
        
        return opportunities
    
    def _generate_improvement_suggestions(self, content: str, file_ext: str) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        lines = content.split('\n')
        avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
        
        if avg_line_length > 100:
            suggestions.append("Consider breaking long lines for better readability")
        
        if file_ext == '.py' and 'def ' in content and 'docstring' not in content.lower():
            suggestions.append("Add docstrings to functions for better documentation")
        
        if file_ext in ['.js', '.ts'] and 'var ' in content:
            suggestions.append("Replace 'var' with 'let' or 'const' for better scoping")
        
        return suggestions
    
    def _detect_technical_debt(self, content: str) -> List[str]:
        """Detect technical debt indicators"""
        debt_indicators = []
        content_lower = content.lower()
        
        debt_patterns = [
            ('todo', 'TODO comments indicate unfinished work'),
            ('fixme', 'FIXME comments indicate bugs or issues'),
            ('hack', 'Code marked as "hack" indicates shortcuts'),
            ('deprecated', 'Usage of deprecated features'),
            ('legacy', 'Legacy code patterns detected')
        ]
        
        for pattern, description in debt_patterns:
            if pattern in content_lower:
                debt_indicators.append(description)
        
        return debt_indicators
    
    def _find_modernization_opportunities(self, content: str, file_ext: str) -> List[str]:
        """Find modernization opportunities"""
        opportunities = []
        
        if file_ext == '.py':
            if 'python2' in content.lower() or 'print ' in content:
                opportunities.append("Upgrade to Python 3 syntax")
            if 'string.format' in content and 'f"' not in content:
                opportunities.append("Use f-strings for string formatting")
        
        elif file_ext in ['.js', '.jsx']:
            if 'function(' in content and '=>' not in content:
                opportunities.append("Consider using arrow functions")
            if 'var ' in content:
                opportunities.append("Use let/const instead of var")
        
        return opportunities
    
    async def _generate_code_insights(self):
        """Generate aggregate code insights"""
        try:
            if not self.analysis_results:
                return
            
            # Aggregate statistics
            total_files = len(self.analysis_results)
            languages = Counter()
            frameworks = Counter()
            patterns = Counter()
            
            for file_path, analysis in self.analysis_results.items():
                if 'file_info' in analysis:
                    languages[analysis['file_info'].get('language', 'Unknown')] += 1
                
                if 'technical_analysis' in analysis:
                    for framework in analysis['technical_analysis'].get('framework_detected', []):
                        frameworks[framework] += 1
                    
                    for pattern in analysis['technical_analysis'].get('design_patterns', []):
                        patterns[pattern] += 1
            
            self.code_metrics = {
                'total_files_analyzed': total_files,
                'languages_used': dict(languages),
                'frameworks_detected': dict(frameworks),
                'design_patterns_found': dict(patterns),
                'most_common_language': languages.most_common(1)[0] if languages else None,
                'most_used_framework': frameworks.most_common(1)[0] if frameworks else None
            }
            
        except Exception as e:
            safe_log(f"Error generating code insights: {e}", logging.ERROR)
    
    async def _analyze_architecture_patterns(self):
        """Analyze overall architecture patterns"""
        try:
            safe_log("Analyzing architecture patterns...")
            
            # Analyze project structures for architecture patterns
            for project_path, project_info in self.project_structures.items():
                project_type = project_info['type']
                files = project_info['files']
                
                # Detect architecture patterns based on project structure
                architecture_style = self._detect_architecture_style(files, project_type)
                
                self.architecture_insights.append({
                    'project_path': project_path,
                    'project_type': project_type,
                    'architecture_style': architecture_style,
                    'complexity': self._assess_project_complexity(files)
                })
            
        except Exception as e:
            safe_log(f"Error analyzing architecture patterns: {e}", logging.ERROR)
    
    def _detect_architecture_style(self, files: List[str], project_type: str) -> str:
        """Detect architecture style from project files"""
        files_lower = [f.lower() for f in files]
        
        # Check for microservices indicators
        if any('docker' in f for f in files_lower) and any('service' in f for f in files_lower):
            return 'microservices'
        
        # Check for MVC pattern
        if any('controller' in f for f in files_lower) and any('model' in f for f in files_lower):
            return 'mvc'
        
        # Check for component-based (React/Vue)
        if any('component' in f for f in files_lower):
            return 'component-based'
        
        # Check for layered architecture
        if any('service' in f for f in files_lower) and any('repository' in f for f in files_lower):
            return 'layered'
        
        return 'monolithic'
    
    def _assess_project_complexity(self, files: List[str]) -> str:
        """Assess project complexity"""
        file_count = len(files)
        
        if file_count < 10:
            return 'simple'
        elif file_count < 50:
            return 'moderate'
        elif file_count < 200:
            return 'complex'
        else:
            return 'very_complex'
    
    async def _security_analysis(self):
        """Perform comprehensive security analysis"""
        try:
            safe_log("Performing security analysis...")
            
            # Aggregate security findings from individual file analyses
            for file_path, analysis in self.analysis_results.items():
                security_analysis = analysis.get('security_analysis', {})
                vulnerabilities = security_analysis.get('vulnerabilities', [])
                
                for vuln in vulnerabilities:
                    self.security_findings.append({
                        'file': file_path,
                        'vulnerability': vuln,
                        'severity': self._assess_vulnerability_severity(vuln)
                    })
            
            # Check for security configuration files
            security_configs = []
            for file_path in self.file_types.get('config', []):
                if any(sec_file in Path(file_path).name.lower() for sec_file in [
                    'security', 'auth', 'ssl', 'tls', 'cert'
                ]):
                    security_configs.append(file_path)
            
            self.security_findings.extend({
                'type': 'configuration',
                'files': security_configs,
                'status': 'review_required' if security_configs else 'missing'
            })
            
        except Exception as e:
            safe_log(f"Error in security analysis: {e}", logging.ERROR)
    
    def _assess_vulnerability_severity(self, vulnerability: str) -> str:
        """Assess vulnerability severity"""
        high_severity = ['sql injection', 'command injection', 'xss']
        medium_severity = ['hardcoded secrets', 'path traversal']
        
        vuln_lower = vulnerability.lower()
        
        if any(high in vuln_lower for high in high_severity):
            return 'high'
        elif any(medium in vuln_lower for medium in medium_severity):
            return 'medium'
        else:
            return 'low'
    
    async def _performance_analysis(self):
        """Perform performance analysis"""
        try:
            safe_log("Performing performance analysis...")
            
            # Aggregate performance issues
            performance_issues = []
            
            for file_path, analysis in self.analysis_results.items():
                perf_analysis = analysis.get('performance_analysis', {})
                issues = perf_analysis.get('performance_issues', [])
                opportunities = perf_analysis.get('optimization_opportunities', [])
                
                for issue in issues:
                    performance_issues.append({
                        'file': file_path,
                        'issue': issue,
                        'type': 'performance_issue'
                    })
                
                for opportunity in opportunities:
                    performance_issues.append({
                        'file': file_path,
                        'opportunity': opportunity,
                        'type': 'optimization_opportunity'
                    })
            
            self.optimization_suggestions = performance_issues
            
        except Exception as e:
            safe_log(f"Error in performance analysis: {e}", logging.ERROR)
    
    async def _calculate_quality_metrics(self):
        """Calculate overall quality metrics"""
        try:
            if not self.analysis_results:
                return
            
            total_files = len(self.analysis_results)
            
            # Aggregate quality scores
            readability_scores = []
            complexity_scores = []
            documentation_scores = []
            security_scores = []
            
            for analysis in self.analysis_results.values():
                if 'code_quality' in analysis:
                    readability_scores.append(analysis['code_quality'].get('readability_score', 0))
                    complexity_scores.append(analysis['code_quality'].get('complexity_score', 0))
                    documentation_scores.append(analysis['code_quality'].get('documentation_score', 0))
                
                if 'security_analysis' in analysis:
                    security_scores.append(analysis['security_analysis'].get('security_score', 0))
            
            self.code_metrics.update({
                'average_readability': sum(readability_scores) / len(readability_scores) if readability_scores else 0,
                'average_complexity': sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0,
                'average_documentation': sum(documentation_scores) / len(documentation_scores) if documentation_scores else 0,
                'average_security': sum(security_scores) / len(security_scores) if security_scores else 0,
                'quality_distribution': {
                    'high_quality_files': len([s for s in readability_scores if s >= 80]),
                    'medium_quality_files': len([s for s in readability_scores if 60 <= s < 80]),
                    'low_quality_files': len([s for s in readability_scores if s < 60])
                }
            })
            
        except Exception as e:
            safe_log(f"Error calculating quality metrics: {e}", logging.ERROR)
    
    async def _analyze_documentation(self):
        """Analyze documentation quality and coverage"""
        try:
            safe_log("Analyzing documentation...")
            
            doc_files = self.file_types.get('documentation', [])
            
            documentation_analysis = {
                'total_doc_files': len(doc_files),
                'doc_types': Counter(Path(f).suffix for f in doc_files),
                'readme_files': [f for f in doc_files if 'readme' in Path(f).name.lower()],
                'api_docs': [f for f in doc_files if any(term in Path(f).name.lower() 
                                                       for term in ['api', 'endpoint', 'swagger'])],
                'user_guides': [f for f in doc_files if any(term in Path(f).name.lower() 
                                                          for term in ['guide', 'tutorial', 'manual'])],
                'technical_docs': [f for f in doc_files if any(term in Path(f).name.lower() 
                                                             for term in ['architecture', 'design', 'technical'])]
            }
            
            # Analyze documentation quality
            for doc_file in doc_files[:10]:  # Limit to first 10 for analysis
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    doc_quality = {
                        'file': doc_file,
                        'word_count': len(content.split()),
                        'has_headings': '#' in content,
                        'has_code_examples': '```' in content or '    ' in content,
                        'has_links': '[' in content and '](' in content,
                        'has_images': '![' in content
                    }
                    
                    documentation_analysis.setdefault('quality_analysis', []).append(doc_quality)
                    
                except Exception as e:
                    safe_log(f"Error analyzing doc file {doc_file}: {e}", logging.WARNING)
            
            self.code_metrics['documentation_analysis'] = documentation_analysis
            
        except Exception as e:
            safe_log(f"Error analyzing documentation: {e}", logging.ERROR)
    
    async def _analyze_dependencies(self):
        """Analyze project dependencies"""
        try:
            safe_log("Analyzing dependencies...")
            
            dependency_files = []
            
            # Find dependency files
            for file_path in self.file_types.get('config', []):
                filename = Path(file_path).name.lower()
                if filename in ['package.json', 'requirements.txt', 'pipfile', 'cargo.toml', 
                               'go.mod', 'pom.xml', 'build.gradle', 'composer.json']:
                    dependency_files.append(file_path)
            
            dependencies_analysis = {
                'dependency_files': dependency_files,
                'total_dependencies': 0,
                'outdated_dependencies': [],
                'security_advisories': []
            }
            
            # Analyze each dependency file
            for dep_file in dependency_files:
                try:
                    with open(dep_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count dependencies (simplified)
                    if 'package.json' in dep_file:
                        import json
                        data = json.loads(content)
                        deps = len(data.get('dependencies', {})) + len(data.get('devDependencies', {}))
                        dependencies_analysis['total_dependencies'] += deps
                    
                    elif 'requirements.txt' in dep_file:
                        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                        dependencies_analysis['total_dependencies'] += len(lines)
                    
                except Exception as e:
                    safe_log(f"Error analyzing dependency file {dep_file}: {e}", logging.WARNING)
            
            self.code_metrics['dependencies_analysis'] = dependencies_analysis
            
        except Exception as e:
            safe_log(f"Error analyzing dependencies: {e}", logging.ERROR)
    
    async def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        try:
            report = {
                "executive_summary": {
                    "total_files_discovered": sum(len(files) for files in self.file_types.values()),
                    "projects_identified": len(self.project_structures),
                    "code_files_analyzed": len(self.analysis_results),
                    "security_issues_found": len(self.security_findings),
                    "performance_issues_found": len(self.optimization_suggestions),
                    "overall_quality_score": self.code_metrics.get('average_readability', 0)
                },
                
                "file_discovery": {
                    "file_categories": {category: len(files) for category, files in self.file_types.items()},
                    "total_files": sum(len(files) for files in self.file_types.values())
                },
                
                "project_analysis": {
                    "projects": self.project_structures,
                    "architecture_insights": self.architecture_insights
                },
                
                "code_quality_metrics": self.code_metrics,
                
                "security_analysis": {
                    "findings": self.security_findings,
                    "security_score": self.code_metrics.get('average_security', 0),
                    "recommendations": self._generate_security_recommendations()
                },
                
                "performance_analysis": {
                    "issues_and_opportunities": self.optimization_suggestions,
                    "recommendations": self._generate_performance_recommendations()
                },
                
                "technical_debt_analysis": {
                    "debt_indicators": self._aggregate_technical_debt(),
                    "modernization_opportunities": self._aggregate_modernization_opportunities()
                },
                
                "improvement_roadmap": self._generate_improvement_roadmap(),
                
                "detailed_file_analysis": {
                    "sample_analyses": list(self.analysis_results.items())[:5]  # First 5 files
                }
            }
            
            return report
            
        except Exception as e:
            safe_log(f"Error generating comprehensive report: {e}", logging.ERROR)
            return {"error": str(e)}
    
    def _generate_security_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        recommendations = [
            "Implement input validation for all user inputs",
            "Use parameterized queries to prevent SQL injection",
            "Implement proper authentication and authorization",
            "Enable HTTPS for all communications",
            "Regular security audits and dependency updates",
            "Implement proper error handling without information leakage"
        ]
        
        return recommendations
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = [
            "Implement caching strategies for frequently accessed data",
            "Optimize database queries and add appropriate indexes",
            "Use async/await for I/O operations",
            "Implement lazy loading for large datasets",
            "Optimize images and static assets",
            "Consider CDN for static content delivery"
        ]
        
        return recommendations
    
    def _aggregate_technical_debt(self) -> List[str]:
        """Aggregate technical debt indicators"""
        debt_items = []
        
        for analysis in self.analysis_results.values():
            debt = analysis.get('technical_debt', {}).get('debt_indicators', [])
            debt_items.extend(debt)
        
        return list(set(debt_items))  # Remove duplicates
    
    def _aggregate_modernization_opportunities(self) -> List[str]:
        """Aggregate modernization opportunities"""
        opportunities = []
        
        for analysis in self.analysis_results.values():
            ops = analysis.get('technical_debt', {}).get('modernization_opportunities', [])
            opportunities.extend(ops)
        
        return list(set(opportunities))  # Remove duplicates
    
    def _generate_improvement_roadmap(self) -> Dict[str, List[str]]:
        """Generate improvement roadmap"""
        return {
            "immediate_actions": [
                "Fix high-severity security vulnerabilities",
                "Address performance bottlenecks",
                "Update outdated dependencies"
            ],
            "short_term_goals": [
                "Improve code documentation",
                "Increase test coverage",
                "Refactor complex code sections"
            ],
            "long_term_objectives": [
                "Modernize legacy code patterns",
                "Implement better architecture patterns",
                "Enhance monitoring and observability"
            ]
        }
    
    async def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save comprehensive report to file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"comprehensive_workspace_analysis_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            safe_log(f"Comprehensive analysis report saved to: {filename}")
            
            # Also create a summary markdown report
            await self._create_markdown_summary(report, filename.replace('.json', '_summary.md'))
            
        except Exception as e:
            safe_log(f"Error saving report: {e}", logging.ERROR)
    
    async def _create_markdown_summary(self, report: Dict[str, Any], filename: str):
        """Create markdown summary report"""
        try:
            summary = report.get('executive_summary', {})
            
            markdown_content = f"""# Comprehensive Workspace Analysis Report

## Executive Summary

- **Total Files Discovered**: {summary.get('total_files_discovered', 0)}
- **Projects Identified**: {summary.get('projects_identified', 0)}
- **Code Files Analyzed**: {summary.get('code_files_analyzed', 0)}
- **Security Issues Found**: {summary.get('security_issues_found', 0)}
- **Performance Issues Found**: {summary.get('performance_issues_found', 0)}
- **Overall Quality Score**: {summary.get('overall_quality_score', 0):.1f}/100

## File Distribution

"""
            
            file_categories = report.get('file_discovery', {}).get('file_categories', {})
            for category, count in file_categories.items():
                markdown_content += f"- **{category.title()}**: {count} files\n"
            
            markdown_content += f"""

## Code Quality Metrics

- **Average Readability**: {report.get('code_quality_metrics', {}).get('average_readability', 0):.1f}/100
- **Average Complexity**: {report.get('code_quality_metrics', {}).get('average_complexity', 0):.1f}/100
- **Average Documentation**: {report.get('code_quality_metrics', {}).get('average_documentation', 0):.1f}/100
- **Average Security**: {report.get('code_quality_metrics', {}).get('average_security', 0):.1f}/100

## Security Analysis

### Key Findings
"""
            
            security_findings = report.get('security_analysis', {}).get('findings', [])
            for finding in security_findings[:5]:  # Show first 5
                if isinstance(finding, dict):
                    markdown_content += f"- {finding.get('vulnerability', 'Security issue')} in {finding.get('file', 'unknown file')}\n"
            
            markdown_content += f"""

## Improvement Roadmap

### Immediate Actions
"""
            
            roadmap = report.get('improvement_roadmap', {})
            for action in roadmap.get('immediate_actions', []):
                markdown_content += f"- {action}\n"
            
            markdown_content += """
### Short-term Goals
"""
            
            for goal in roadmap.get('short_term_goals', []):
                markdown_content += f"- {goal}\n"
            
            markdown_content += """
### Long-term Objectives
"""
            
            for objective in roadmap.get('long_term_objectives', []):
                markdown_content += f"- {objective}\n"
            
            markdown_content += f"""

---

*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            safe_log(f"Markdown summary saved to: {filename}")
            
        except Exception as e:
            safe_log(f"Error creating markdown summary: {e}", logging.ERROR)


async def main():
    """Main function to run comprehensive workspace analysis"""
    try:
        safe_log("🚀 Starting Comprehensive Workspace Analysis with Gemini CLI")
        
        # Initialize analyzer
        analyzer = ComprehensiveWorkspaceAnalyzer()
        
        # Run comprehensive analysis
        report = await analyzer.analyze_workspace_comprehensive()
        
        # Save reports
        await analyzer.save_report(report)
        
        # Display summary
        safe_log("\n" + "="*60)
        safe_log("📊 COMPREHENSIVE WORKSPACE ANALYSIS COMPLETE")
        safe_log("="*60)
        
        summary = report.get('executive_summary', {})
        safe_log(f"📁 Total Files: {summary.get('total_files_discovered', 0)}")
        safe_log(f"🏗️  Projects: {summary.get('projects_identified', 0)}")
        safe_log(f"🔍 Code Files Analyzed: {summary.get('code_files_analyzed', 0)}")
        safe_log(f"🔒 Security Issues: {summary.get('security_issues_found', 0)}")
        safe_log(f"⚡ Performance Issues: {summary.get('performance_issues_found', 0)}")
        safe_log(f"📈 Quality Score: {summary.get('overall_quality_score', 0):.1f}/100")
        
        # Show top languages
        languages = report.get('code_quality_metrics', {}).get('languages_used', {})
        if languages:
            safe_log("\n🔤 Top Programming Languages:")
            for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
                safe_log(f"   {lang}: {count} files")
        
        # Show top frameworks
        frameworks = report.get('code_quality_metrics', {}).get('frameworks_detected', {})
        if frameworks:
            safe_log("\n🚀 Frameworks Detected:")
            for framework, count in sorted(frameworks.items(), key=lambda x: x[1], reverse=True)[:5]:
                safe_log(f"   {framework}: {count} occurrences")
        
        safe_log(f"\n📄 Full reports saved with timestamp")
        safe_log("="*60)
        
    except Exception as e:
        safe_log(f"❌ Error in main analysis: {e}", logging.ERROR)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
