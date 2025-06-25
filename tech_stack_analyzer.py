#!/usr/bin/env python3
"""
Advanced Tech Stack Analyzer using Gemini 2.5 Pro
==================================================
Leverages Gemini's 1M token context window to analyze entire workspace
and provide comprehensive tech stack insights, recommendations, and optimization suggestions.
"""

import asyncio
import json
import os
import pathlib
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
import websockets

class TechStackAnalyzer:
    def __init__(self, workspace_path: str = "c:\\Workspace"):
        self.workspace_path = pathlib.Path(workspace_path)
        self.gemini_uri = "ws://localhost:8015"
        self.tech_patterns = {
            # Frontend Technologies
            "package.json": ["Node.js", "npm", "JavaScript/TypeScript"],
            "yarn.lock": ["Yarn", "JavaScript/TypeScript"],
            "next.config.js": ["Next.js", "React"],
            "next.config.mjs": ["Next.js", "React"],
            "vite.config.ts": ["Vite", "Modern Build Tool"],
            "tailwind.config.ts": ["Tailwind CSS", "Utility-First CSS"],
            "biome.json": ["Biome", "Linter/Formatter"],
            "eslint": ["ESLint", "JavaScript Linting"],
            "jest.config.js": ["Jest", "Testing Framework"],
            
            # Backend Technologies
            "requirements.txt": ["Python", "pip"],
            "pyproject.toml": ["Python", "Modern Python Project"],
            "Pipfile": ["Python", "Pipenv"],
            "poetry.lock": ["Python", "Poetry"],
            "Cargo.toml": ["Rust", "Cargo"],
            "go.mod": ["Go", "Go Modules"],
            "pom.xml": ["Java", "Maven"],
            "build.gradle": ["Java/Kotlin", "Gradle"],
            "composer.json": ["PHP", "Composer"],
            
            # Databases
            "*.db": ["SQLite", "Database"],
            "*.sql": ["SQL", "Database Scripts"],
            "migrations/": ["Database Migrations"],
            
            # DevOps & Infrastructure
            "Dockerfile": ["Docker", "Containerization"],
            "docker-compose.yml": ["Docker Compose", "Multi-container"],
            ".github/": ["GitHub Actions", "CI/CD"],
            "terraform/": ["Terraform", "Infrastructure as Code"],
            "k8s/": ["Kubernetes", "Container Orchestration"],
            "helm/": ["Helm", "Kubernetes Package Manager"],
            
            # AI/ML Technologies
            "*.ipynb": ["Jupyter Notebooks", "Data Science"],
            "model.pkl": ["Machine Learning Models"],
            "*.h5": ["Keras/TensorFlow Models"],
            "*.pt": ["PyTorch Models"],
            
            # Configuration
            ".env": ["Environment Configuration"],
            "*.yaml": ["YAML Configuration"],
            "*.yml": ["YAML Configuration"],
            "*.toml": ["TOML Configuration"],
            "*.ini": ["INI Configuration"],
        }
    
    async def analyze_workspace(self) -> Dict[str, Any]:
        """Perform comprehensive workspace analysis using Gemini 2.5 Pro"""
        print("🔍 Starting comprehensive workspace analysis...")
        
        # 1. Discover all technology files
        tech_inventory = await self.discover_technologies()
        
        # 2. Read key configuration files
        config_analysis = await self.analyze_configurations()
        
        # 3. Analyze project structure
        structure_analysis = await self.analyze_project_structure()
        
        # 4. Get dependency insights
        dependency_analysis = await self.analyze_dependencies()
        
        # 5. Use Gemini to provide comprehensive analysis
        gemini_analysis = await self.get_gemini_analysis({
            "tech_inventory": tech_inventory,
            "configurations": config_analysis,
            "structure": structure_analysis,
            "dependencies": dependency_analysis
        })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "workspace_path": str(self.workspace_path),
            "tech_inventory": tech_inventory,
            "configurations": config_analysis,
            "structure": structure_analysis,
            "dependencies": dependency_analysis,
            "gemini_analysis": gemini_analysis,
            "summary": await self.generate_summary(gemini_analysis)
        }
    
    async def discover_technologies(self) -> Dict[str, List[str]]:
        """Discover all technologies in the workspace"""
        print("📋 Discovering technologies...")
        discovered = {}
        
        for root, dirs, files in os.walk(self.workspace_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'dist', 'build']]
            
            for file in files:
                file_path = pathlib.Path(root) / file
                relative_path = file_path.relative_to(self.workspace_path)
                
                # Check against our patterns
                for pattern, technologies in self.tech_patterns.items():
                    if self.matches_pattern(file, pattern):
                        tech_key = technologies[0] if technologies else pattern
                        if tech_key not in discovered:
                            discovered[tech_key] = []
                        discovered[tech_key].append(str(relative_path))
        
        return discovered
    
    def matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches the pattern"""
        if pattern.endswith('/'):
            return False  # Directory patterns handled separately
        elif '*' in pattern:
            import fnmatch
            return fnmatch.fnmatch(filename.lower(), pattern.lower())
        else:
            return filename.lower() == pattern.lower()
    
    async def analyze_configurations(self) -> Dict[str, Any]:
        """Analyze key configuration files"""
        print("⚙️ Analyzing configurations...")
        configs = {}
        
        config_files = [
            "package.json", "pyproject.toml", "requirements.txt",
            "docker-compose.yml", "next.config.mjs", "tailwind.config.ts",
            "vite.config.ts", "biome.json", ".env.example"
        ]
        
        for config_file in config_files:
            file_path = self.workspace_path / config_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        configs[config_file] = {
                            "path": str(file_path),
                            "size": len(content),
                            "content": content[:1000] + "..." if len(content) > 1000 else content
                        }
                except Exception as e:
                    configs[config_file] = {"error": str(e)}
        
        return configs
    
    async def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project structure and organization"""
        print("🏗️ Analyzing project structure...")
        structure = {
            "directories": [],
            "file_counts": {},
            "size_analysis": {}
        }
        
        for root, dirs, files in os.walk(self.workspace_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            relative_root = pathlib.Path(root).relative_to(self.workspace_path)
            if str(relative_root) != '.':
                structure["directories"].append(str(relative_root))
            
            # Count files by extension
            for file in files:
                ext = pathlib.Path(file).suffix.lower()
                if ext:
                    structure["file_counts"][ext] = structure["file_counts"].get(ext, 0) + 1
        
        return structure
    
    async def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies"""
        print("📦 Analyzing dependencies...")
        deps = {}
        
        # Python dependencies
        if (self.workspace_path / "requirements.txt").exists():
            deps["python_requirements"] = await self.read_requirements()
        
        if (self.workspace_path / "pyproject.toml").exists():
            deps["python_pyproject"] = await self.read_pyproject()
        
        # Node.js dependencies  
        if (self.workspace_path / "package.json").exists():
            deps["nodejs_package"] = await self.read_package_json()
        
        return deps
    
    async def read_requirements(self) -> List[str]:
        """Read Python requirements.txt"""
        try:
            with open(self.workspace_path / "requirements.txt", 'r') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception:
            return []
    
    async def read_pyproject(self) -> Dict[str, Any]:
        """Read Python pyproject.toml"""
        try:
            import tomllib
            with open(self.workspace_path / "pyproject.toml", 'rb') as f:
                return tomllib.load(f)
        except Exception:
            return {}
    
    async def read_package_json(self) -> Dict[str, Any]:
        """Read Node.js package.json"""
        try:
            with open(self.workspace_path / "package.json", 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    async def get_gemini_analysis(self, workspace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive analysis from Gemini 2.5 Pro"""
        print("🤖 Getting Gemini 2.5 Pro analysis...")
        
        prompt = f"""
        Analyze this comprehensive workspace technology stack data and provide insights:

        WORKSPACE DATA:
        {json.dumps(workspace_data, indent=2)}

        Please provide:
        1. **Tech Stack Summary**: What technologies are being used and their purposes
        2. **Architecture Analysis**: How the components work together
        3. **Modern Stack Assessment**: How modern/current are the technologies
        4. **Optimization Opportunities**: Specific recommendations for improvements
        5. **Security Considerations**: Potential security issues or recommendations
        6. **Performance Insights**: Performance optimization opportunities
        7. **Best Practices**: Are current configurations following best practices?
        8. **Missing Technologies**: What might be missing for a complete modern stack
        9. **Integration Opportunities**: How to better integrate existing technologies
        10. **Future Roadmap**: Suggested next steps for evolution

        Focus on actionable insights and specific recommendations.
        """
        
        try:
            async with websockets.connect(self.gemini_uri) as websocket:
                message = {
                    "jsonrpc": "2.0",
                    "id": "analysis",
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
    
    async def generate_summary(self, gemini_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        return {
            "status": "completed" if "analysis" in gemini_analysis else "error",
            "tech_count": len(await self.discover_technologies()),
            "analysis_available": "analysis" in gemini_analysis,
            "model_used": gemini_analysis.get("model", "unknown")
        }
    
    async def save_analysis(self, analysis: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save analysis to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tech_stack_analysis_{timestamp}.json"
        
        filepath = self.workspace_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        return str(filepath)

async def main():
    """Run the tech stack analysis"""
    analyzer = TechStackAnalyzer()
    
    print("🚀 Starting Advanced Tech Stack Analysis with Gemini 2.5 Pro")
    print(f"📁 Analyzing workspace: {analyzer.workspace_path}")
    print("=" * 60)
    
    try:
        # Run the analysis
        analysis = await analyzer.analyze_workspace()
        
        # Save results
        output_file = await analyzer.save_analysis(analysis)
        
        print("\n" + "=" * 60)
        print("✅ Analysis Complete!")
        print(f"📄 Results saved to: {output_file}")
        print(f"🔍 Technologies discovered: {analysis['summary']['tech_count']}")
        print(f"🤖 Gemini analysis: {'✅ Available' if analysis['summary']['analysis_available'] else '❌ Failed'}")
        
        # Show quick summary
        if analysis['summary']['analysis_available']:
            print("\n🎯 Quick Insights:")
            gemini_response = analysis['gemini_analysis']['analysis']
            # Show first few lines of analysis
            lines = gemini_response.split('\n')[:5]
            for line in lines:
                if line.strip():
                    print(f"   {line.strip()}")
            print(f"   ... (see full analysis in {output_file})")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
