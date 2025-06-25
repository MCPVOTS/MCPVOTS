#!/usr/bin/env python3
"""
Intelligent Code Search and Indexing with Gemini 2.5 Pro
========================================================
Advanced code search, pattern detection, and knowledge extraction
using Gemini's massive context window and multimodal capabilities.
"""

import asyncio
import json
import os
import pathlib
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import websockets

class IntelligentCodeSearcher:
    def __init__(self, workspace_path: str = "c:\\Workspace"):
        self.workspace_path = pathlib.Path(workspace_path)
        self.gemini_uri = "ws://localhost:8015"
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala',
            '.sql', '.html', '.css', '.scss', '.sass', '.less', '.vue',
            '.svelte', '.json', '.yaml', '.yml', '.toml', '.xml', '.md'
        }
        self.max_file_size = 50000  # 50KB limit per file for analysis
    
    async def search_and_analyze(self, query: str, search_type: str = "semantic") -> Dict[str, Any]:
        """
        Perform intelligent code search and analysis
        
        Args:
            query: Search query or pattern to find
            search_type: 'semantic', 'pattern', 'function', 'class', 'api', 'security'
        """
        print(f"🔍 Starting {search_type} search for: {query}")
        
        # 1. Index all code files
        code_index = await self.index_code_files()
        
        # 2. Perform initial search
        matches = await self.find_matches(query, code_index, search_type)
        
        # 3. Get Gemini analysis
        analysis = await self.get_gemini_code_analysis(query, matches, search_type)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "search_type": search_type,
            "total_files_indexed": len(code_index),
            "matches_found": len(matches),
            "matches": matches,
            "gemini_analysis": analysis,
            "recommendations": await self.generate_recommendations(analysis)
        }
    
    async def index_code_files(self) -> Dict[str, Any]:
        """Create comprehensive code index"""
        print("📋 Indexing code files...")
        index = {}
        
        for root, dirs, files in os.walk(self.workspace_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in ['node_modules', '__pycache__', 'dist', 'build', '.git']]
            
            for file in files:
                file_path = pathlib.Path(root) / file
                if file_path.suffix.lower() in self.code_extensions:
                    try:
                        if file_path.stat().st_size > self.max_file_size:
                            continue  # Skip large files
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        relative_path = file_path.relative_to(self.workspace_path)
                        index[str(relative_path)] = {
                            "path": str(file_path),
                            "size": len(content),
                            "lines": len(content.split('\n')),
                            "extension": file_path.suffix.lower(),
                            "content": content,
                            "functions": await self.extract_functions(content, file_path.suffix),
                            "classes": await self.extract_classes(content, file_path.suffix),
                            "imports": await self.extract_imports(content, file_path.suffix),
                            "comments": await self.extract_comments(content, file_path.suffix)
                        }
                    except Exception as e:
                        print(f"⚠️ Skipping {file_path}: {e}")
        
        return index
    
    async def extract_functions(self, content: str, ext: str) -> List[Dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        
        if ext == '.py':
            pattern = r'def\s+(\w+)\s*\([^)]*\):'
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                functions.append({
                    "name": match.group(1),
                    "line": content[:match.start()].count('\n') + 1,
                    "signature": match.group(0)
                })
        
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            # Function declarations and arrow functions
            patterns = [
                r'function\s+(\w+)\s*\([^)]*\)',
                r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
                r'(\w+)\s*:\s*\([^)]*\)\s*=>'
            ]
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    functions.append({
                        "name": match.group(1),
                        "line": content[:match.start()].count('\n') + 1,
                        "signature": match.group(0)
                    })
        
        return functions
    
    async def extract_classes(self, content: str, ext: str) -> List[Dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        
        if ext == '.py':
            pattern = r'class\s+(\w+)(?:\([^)]*\))?:'
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                classes.append({
                    "name": match.group(1),
                    "line": content[:match.start()].count('\n') + 1,
                    "signature": match.group(0)
                })
        
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?'
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                classes.append({
                    "name": match.group(1),
                    "line": content[:match.start()].count('\n') + 1,
                    "signature": match.group(0)
                })
        
        return classes
    
    async def extract_imports(self, content: str, ext: str) -> List[str]:
        """Extract import statements"""
        imports = []
        
        if ext == '.py':
            patterns = [
                r'import\s+([^\n]+)',
                r'from\s+([^\s]+)\s+import'
            ]
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            patterns = [
                r'import\s+[^;]+from\s+[\'"]([^\'"]+)[\'"]',
                r'import\s+[\'"]([^\'"]+)[\'"]'
            ]
        else:
            return imports
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            imports.extend([match.group(1) for match in matches])
        
        return imports
    
    async def extract_comments(self, content: str, ext: str) -> List[Dict[str, Any]]:
        """Extract comments and docstrings"""
        comments = []
        
        if ext == '.py':
            # Python docstrings and comments
            patterns = [
                (r'"""([^"]+)"""', 'docstring'),
                (r"'''([^']+)'''", 'docstring'),
                (r'#\s*([^\n]+)', 'comment')
            ]
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            patterns = [
                (r'/\*\*([^*]+)\*/', 'jsdoc'),
                (r'/\*([^*]+)\*/', 'block_comment'),
                (r'//\s*([^\n]+)', 'comment')
            ]
        else:
            return comments
        
        for pattern, comment_type in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                comments.append({
                    "type": comment_type,
                    "content": match.group(1).strip(),
                    "line": content[:match.start()].count('\n') + 1
                })
        
        return comments
    
    async def find_matches(self, query: str, code_index: Dict[str, Any], search_type: str) -> List[Dict[str, Any]]:
        """Find matches based on search type"""
        matches = []
        
        for file_path, file_info in code_index.items():
            file_matches = []
            
            if search_type == "semantic":
                # Search in content, comments, and function names
                if query.lower() in file_info["content"].lower():
                    file_matches.append("content")
                if any(query.lower() in comment["content"].lower() for comment in file_info["comments"]):
                    file_matches.append("comments")
                if any(query.lower() in func["name"].lower() for func in file_info["functions"]):
                    file_matches.append("functions")
            
            elif search_type == "function":
                # Search for function names
                for func in file_info["functions"]:
                    if query.lower() in func["name"].lower():
                        file_matches.append(f"function: {func['name']} (line {func['line']})")
            
            elif search_type == "class":
                # Search for class names
                for cls in file_info["classes"]:
                    if query.lower() in cls["name"].lower():
                        file_matches.append(f"class: {cls['name']} (line {cls['line']})")
            
            elif search_type == "api":
                # Search for API calls and endpoints
                api_patterns = [
                    r'@app\.\w+\([\'"]([^\'"]+)[\'"]',  # Flask/FastAPI routes
                    r'app\.\w+\([\'"]([^\'"]+)[\'"]',    # Express routes
                    r'fetch\([\'"]([^\'"]+)[\'"]',       # Fetch calls
                    r'axios\.\w+\([\'"]([^\'"]+)[\'"]',  # Axios calls
                ]
                for pattern in api_patterns:
                    if re.search(pattern, file_info["content"]):
                        file_matches.append("api_usage")
            
            elif search_type == "security":
                # Search for security-related patterns
                security_patterns = [
                    r'password\s*=',
                    r'secret\s*=',
                    r'api_key\s*=',
                    r'token\s*=',
                    r'auth\s*=',
                    r'subprocess\.',
                    r'eval\(',
                    r'exec\(',
                    r'os\.system',
                ]
                for pattern in security_patterns:
                    if re.search(pattern, file_info["content"], re.IGNORECASE):
                        file_matches.append(f"security_concern: {pattern}")
            
            if file_matches:
                matches.append({
                    "file": file_path,
                    "matches": file_matches,
                    "file_info": {
                        "size": file_info["size"],
                        "lines": file_info["lines"],
                        "extension": file_info["extension"],
                        "functions_count": len(file_info["functions"]),
                        "classes_count": len(file_info["classes"]),
                        "imports_count": len(file_info["imports"])
                    },
                    "preview": file_info["content"][:500] + "..." if len(file_info["content"]) > 500 else file_info["content"]
                })
        
        return matches
    
    async def get_gemini_code_analysis(self, query: str, matches: List[Dict[str, Any]], search_type: str) -> Dict[str, Any]:
        """Get Gemini analysis of code search results"""
        print("🤖 Getting Gemini code analysis...")
        
        # Prepare context for Gemini
        context = {
            "query": query,
            "search_type": search_type,
            "matches_count": len(matches),
            "matches": matches[:10]  # Limit to top 10 matches for context
        }
        
        prompt = f"""
        Analyze these code search results and provide insights:

        SEARCH QUERY: {query}
        SEARCH TYPE: {search_type}
        
        RESULTS:
        {json.dumps(context, indent=2)}

        Please provide:
        1. **Code Pattern Analysis**: What patterns do you see in the matches?
        2. **Architecture Insights**: How do these code pieces fit together?
        3. **Quality Assessment**: Code quality observations
        4. **Security Analysis**: Any security concerns or good practices?
        5. **Optimization Opportunities**: Performance or structure improvements
        6. **Best Practices**: Are best practices being followed?
        7. **Refactoring Suggestions**: Specific refactoring recommendations
        8. **Integration Points**: How different components interact
        9. **Testing Considerations**: Testing strategies for this code
        10. **Documentation**: Documentation quality and suggestions

        Focus on actionable insights and specific recommendations for improvement.
        """
        
        try:
            async with websockets.connect(self.gemini_uri) as websocket:
                message = {
                    "jsonrpc": "2.0",
                    "id": "code_analysis",
                    "method": "gemini/chat",
                    "params": {
                        "message": prompt,
                        "model": "gemini-2.5-pro"
                    }
                }
                
                await websocket.send(json.dumps(message))
                response = await websocket.recv()
                result = json.loads(response)
                
                if "result" in result:
                    return {
                        "analysis": result["result"].get("response", ""),
                        "model": result["result"].get("model", ""),
                        "timestamp": result["result"].get("timestamp", "")
                    }
                else:
                    return {"error": result.get("error", "Unknown error")}
                    
        except Exception as e:
            return {"error": f"Failed to get Gemini analysis: {str(e)}"}
    
    async def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations from analysis"""
        if "error" in analysis:
            return ["Error in analysis - check Gemini connection"]
        
        # Extract key recommendations from analysis
        recommendations = []
        analysis_text = analysis.get("analysis", "")
        
        # Look for recommendation patterns
        if "refactor" in analysis_text.lower():
            recommendations.append("Consider refactoring identified code sections")
        if "security" in analysis_text.lower():
            recommendations.append("Review security practices and implementations")
        if "performance" in analysis_text.lower():
            recommendations.append("Optimize performance bottlenecks")
        if "test" in analysis_text.lower():
            recommendations.append("Improve test coverage")
        if "documentation" in analysis_text.lower():
            recommendations.append("Enhance code documentation")
        
        return recommendations if recommendations else ["Review Gemini analysis for detailed insights"]

# Predefined search queries for common use cases
COMMON_SEARCHES = {
    "security_audit": {
        "query": "security vulnerability authentication password",
        "type": "security"
    },
    "api_endpoints": {
        "query": "endpoint route handler",
        "type": "api"
    },
    "database_queries": {
        "query": "SELECT INSERT UPDATE DELETE",
        "type": "pattern"
    },
    "error_handling": {
        "query": "try catch exception error",
        "type": "pattern"
    },
    "async_patterns": {
        "query": "async await Promise",
        "type": "pattern"
    },
    "utility_functions": {
        "query": "utility helper function",
        "type": "function"
    }
}

async def main():
    """Run intelligent code search"""
    searcher = IntelligentCodeSearcher()
    
    print("🔍 Intelligent Code Search and Analysis with Gemini 2.5 Pro")
    print("=" * 60)
    
    # Example searches
    searches = [
        ("authentication", "security"),
        ("async", "pattern"),
        ("Component", "class")
    ]
    
    for query, search_type in searches:
        print(f"\n🔍 Searching for: {query} (type: {search_type})")
        try:
            results = await searcher.search_and_analyze(query, search_type)
            
            print(f"✅ Found {results['matches_found']} matches in {results['total_files_indexed']} files")
            
            if results['matches_found'] > 0:
                print("📄 Top matches:")
                for i, match in enumerate(results['matches'][:3]):
                    print(f"   {i+1}. {match['file']} - {', '.join(match['matches'])}")
            
            if results['gemini_analysis'].get('analysis'):
                print("🤖 Gemini insights available")
                print(f"💡 Recommendations: {len(results['recommendations'])}")
            
        except Exception as e:
            print(f"❌ Search failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
