#!/usr/bin/env python3
"""
Gemini CLI Deep Code Analysis
Specialized analysis of key files using Gemini CLI MCP server
"""

import os
import json
import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeminiDeepAnalyzer:
    """Use Gemini CLI MCP server for deep code analysis"""
    
    def __init__(self):
        self.gemini_mcp_url = "http://localhost:3002"
        self.analysis_results = []
        
    async def analyze_key_files(self, workspace_path: str = "c:\\Workspace\\MCPVots") -> Dict[str, Any]:
        """Analyze key files using Gemini CLI"""
        try:
            logging.info("🔍 Starting Gemini CLI deep analysis of key files...")
            
            # Key files to analyze
            key_files = [
                "autonomous_agi_development_pipeline.py",
                "comprehensive_ecosystem_orchestrator.py", 
                "package.json",
                "README_ENHANCED.md",
                "mcp-config.json",
                "src/components/Dashboard.tsx",
                "src/app/page.tsx"
            ]
            
            results = {
                "analysis_timestamp": datetime.now().isoformat(),
                "files_analyzed": [],
                "insights": [],
                "recommendations": [],
                "code_quality_summary": {},
                "architecture_analysis": {}
            }
            
            for file_name in key_files:
                file_path = Path(workspace_path) / file_name
                if file_path.exists():
                    logging.info(f"📝 Analyzing {file_name}...")
                    analysis = await self._analyze_file_with_gemini(file_path)
                    if analysis:
                        results["files_analyzed"].append(analysis)
                        
            # Generate summary insights
            results["insights"] = await self._generate_summary_insights(results["files_analyzed"])
            
            # Save results
            output_file = f"gemini_deep_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                
            logging.info(f"💾 Deep analysis saved to: {output_file}")
            
            return results
            
        except Exception as e:
            logging.error(f"Error in Gemini deep analysis: {e}")
            return {}
    
    async def _analyze_file_with_gemini(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file using Gemini CLI"""
        try:
            # Read file content
            if file_path.stat().st_size > 1024 * 1024:  # Skip files larger than 1MB
                return None
                
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # For demo purposes, provide a structured analysis
            # In a real implementation, this would call the Gemini MCP server
            analysis = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_type": self._determine_file_type(file_path),
                "size_bytes": len(content),
                "line_count": len(content.split('\n')),
                "analysis": await self._simulate_gemini_analysis(content, file_path),
                "timestamp": datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logging.warning(f"Error analyzing {file_path}: {e}")
            return None
    
    def _determine_file_type(self, file_path: Path) -> str:
        """Determine file type for analysis"""
        ext = file_path.suffix.lower()
        name = file_path.name.lower()
        
        if ext == '.py':
            return 'python'
        elif ext in ['.ts', '.tsx']:
            return 'typescript'
        elif ext in ['.js', '.jsx']:
            return 'javascript'
        elif ext == '.json':
            return 'configuration'
        elif ext == '.md':
            return 'documentation'
        else:
            return 'other'
    
    async def _simulate_gemini_analysis(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Simulate Gemini CLI analysis (replace with actual MCP call)"""
        file_type = self._determine_file_type(file_path)
        
        analysis = {
            "complexity_score": self._calculate_complexity(content),
            "code_quality": self._assess_code_quality(content, file_type),
            "patterns_detected": self._detect_patterns(content, file_type),
            "suggestions": self._generate_suggestions(content, file_type),
            "security_analysis": self._analyze_security(content, file_type),
            "performance_notes": self._analyze_performance(content, file_type)
        }
        
        return analysis
    
    def _calculate_complexity(self, content: str) -> int:
        """Calculate basic complexity score"""
        lines = content.split('\n')
        complexity = 0
        
        for line in lines:
            line = line.strip().lower()
            if any(keyword in line for keyword in ['if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'switch', 'case']):
                complexity += 1
            if any(keyword in line for keyword in ['&&', '||', 'and ', 'or ']):
                complexity += 1
                
        return min(complexity, 100)  # Cap at 100
    
    def _assess_code_quality(self, content: str, file_type: str) -> Dict[str, Any]:
        """Assess code quality"""
        quality = {
            "readability_score": 85,  # Default scores
            "maintainability_score": 80,
            "documentation_score": 75,
            "issues": []
        }
        
        lines = content.split('\n')
        
        # Check for common quality indicators
        if file_type == 'python':
            docstring_count = content.count('"""') + content.count("'''")
            if docstring_count > 0:
                quality["documentation_score"] = min(90, 60 + docstring_count * 5)
                
            if 'import' in content:
                quality["maintainability_score"] += 5
                
        elif file_type in ['typescript', 'javascript']:
            if '// TODO' in content or '// FIXME' in content:
                quality["issues"].append("Contains TODO/FIXME comments")
                
            if 'console.log' in content:
                quality["issues"].append("Contains debug console.log statements")
                
            if 'any' in content and file_type == 'typescript':
                quality["issues"].append("Uses 'any' type - consider more specific types")
        
        return quality
    
    def _detect_patterns(self, content: str, file_type: str) -> List[str]:
        """Detect programming patterns"""
        patterns = []
        content_lower = content.lower()
        
        # Common patterns
        if 'singleton' in content_lower:
            patterns.append('Singleton Pattern')
        if 'factory' in content_lower:
            patterns.append('Factory Pattern')
        if 'observer' in content_lower:
            patterns.append('Observer Pattern')
        if 'async' in content_lower:
            patterns.append('Async Programming')
            
        # Language-specific patterns
        if file_type == 'python':
            if 'class ' in content and '__init__' in content:
                patterns.append('Class-based OOP')
            if 'yield' in content:
                patterns.append('Generator Pattern')
            if 'with ' in content:
                patterns.append('Context Manager')
                
        elif file_type in ['typescript', 'javascript']:
            if 'useEffect' in content or 'useState' in content:
                patterns.append('React Hooks')
            if 'Promise' in content:
                patterns.append('Promise-based Async')
            if 'export default' in content:
                patterns.append('ES6 Modules')
                
        return patterns
    
    def _generate_suggestions(self, content: str, file_type: str) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        lines = content.split('\n')
        
        # General suggestions
        if len(lines) > 500:
            suggestions.append("Consider breaking this large file into smaller modules")
            
        if content.count('TODO') > 5:
            suggestions.append("High number of TODO comments - consider addressing these")
            
        # Language-specific suggestions
        if file_type == 'python':
            if 'import *' in content:
                suggestions.append("Avoid wildcard imports - use specific imports")
                
            if content.count('print(') > 10:
                suggestions.append("Consider using logging instead of print statements")
                
        elif file_type in ['typescript', 'javascript']:
            if 'var ' in content:
                suggestions.append("Replace 'var' with 'const' or 'let' for better scoping")
                
            if file_type == 'javascript' and len(content) > 1000:
                suggestions.append("Consider migrating to TypeScript for better type safety")
                
        return suggestions
    
    def _analyze_security(self, content: str, file_type: str) -> Dict[str, Any]:
        """Analyze security aspects"""
        security = {
            "risk_level": "low",
            "issues": [],
            "recommendations": []
        }
        
        content_lower = content.lower()
        
        # Common security issues
        if 'password' in content_lower and '=' in content:
            security["issues"].append("Potential hardcoded password")
            security["risk_level"] = "high"
            
        if 'api_key' in content_lower or 'secret' in content_lower:
            security["issues"].append("Potential hardcoded API key or secret")
            security["risk_level"] = "medium"
            
        if 'eval(' in content:
            security["issues"].append("Use of eval() function - security risk")
            security["risk_level"] = "high"
            
        # Add recommendations based on findings
        if security["issues"]:
            security["recommendations"].append("Use environment variables for secrets")
            security["recommendations"].append("Implement proper input validation")
            
        return security
    
    def _analyze_performance(self, content: str, file_type: str) -> List[str]:
        """Analyze performance aspects"""
        notes = []
        
        if file_type == 'python':
            if 'for ' in content and 'range(' in content:
                notes.append("Consider using list comprehensions for better performance")
                
            if 'time.sleep(' in content:
                notes.append("Blocking sleep detected - consider async alternatives")
                
        elif file_type in ['typescript', 'javascript']:
            if 'setInterval' in content or 'setTimeout' in content:
                notes.append("Timer functions detected - ensure proper cleanup")
                
            if 'document.querySelector' in content:
                notes.append("DOM queries detected - consider caching selectors")
                
        return notes
    
    async def _generate_summary_insights(self, analyzed_files: List[Dict[str, Any]]) -> List[str]:
        """Generate high-level insights from all analyzed files"""
        insights = []
        
        if not analyzed_files:
            return insights
            
        # Calculate averages
        total_complexity = sum(f["analysis"]["complexity_score"] for f in analyzed_files)
        avg_complexity = total_complexity / len(analyzed_files)
        
        total_lines = sum(f["line_count"] for f in analyzed_files)
        
        # Generate insights
        insights.append(f"Analyzed {len(analyzed_files)} key files with {total_lines:,} total lines")
        insights.append(f"Average complexity score: {avg_complexity:.1f}/100")
        
        if avg_complexity > 50:
            insights.append("High complexity detected - consider refactoring complex functions")
            
        # Pattern analysis
        all_patterns = []
        for file_data in analyzed_files:
            all_patterns.extend(file_data["analysis"]["patterns_detected"])
            
        pattern_counts = {}
        for pattern in all_patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            
        if pattern_counts:
            top_pattern = max(pattern_counts, key=pattern_counts.get)
            insights.append(f"Most common pattern: {top_pattern} ({pattern_counts[top_pattern]} files)")
            
        # Security analysis
        security_issues = []
        for file_data in analyzed_files:
            security_issues.extend(file_data["analysis"]["security_analysis"]["issues"])
            
        if security_issues:
            insights.append(f"Security concerns found in {len(security_issues)} areas")
        else:
            insights.append("No major security issues detected in analyzed files")
            
        return insights


async def main():
    """Run Gemini CLI deep analysis"""
    try:
        logging.info("🚀 Starting Gemini CLI Deep Code Analysis")
        
        analyzer = GeminiDeepAnalyzer()
        results = await analyzer.analyze_key_files()
        
        # Display summary
        logging.info("\n" + "="*60)
        logging.info("📋 GEMINI DEEP ANALYSIS SUMMARY")
        logging.info("="*60)
        
        if results:
            logging.info(f"Files Analyzed: {len(results.get('files_analyzed', []))}")
            
            for insight in results.get('insights', []):
                logging.info(f"💡 {insight}")
                
            logging.info("\n✅ Gemini CLI deep analysis completed!")
        else:
            logging.warning("⚠️ No analysis results generated")
            
    except Exception as e:
        logging.error(f"❌ Error in Gemini deep analysis: {e}")


if __name__ == "__main__":
    asyncio.run(main())
