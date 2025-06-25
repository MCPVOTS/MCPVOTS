#!/usr/bin/env python3
"""
Quick Demo: Gemini 2.5 Pro Workspace Intelligence
=================================================
A focused demonstration of how Gemini 2.5 Pro can help with workspace analysis
"""

import asyncio
import json
import os
import pathlib
from datetime import datetime
import websockets

async def quick_workspace_demo():
    """Quick demonstration of workspace intelligence capabilities"""
    workspace_path = pathlib.Path("c:\\Workspace\\MCPVots")
    
    print("🚀 Quick Demo: Gemini 2.5 Pro Workspace Intelligence")
    print("=" * 60)
    print(f"📁 Analyzing: {workspace_path}")
    print("🤖 Model: Gemini 2.5 Pro (1M token context window)")
    print("=" * 60)
    
    # 1. Quick file scan
    print("\n📋 PHASE 1: Technology Discovery")
    print("-" * 30)
    
    tech_files = {}
    total_files = 0
    
    for root, dirs, files in os.walk(workspace_path):
        # Skip node_modules and other large directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'dist']]
        
        for file in files:
            total_files += 1
            ext = pathlib.Path(file).suffix.lower()
            if ext:
                tech_files[ext] = tech_files.get(ext, 0) + 1
    
    print(f"✅ Scanned {total_files} files")
    print("🏆 Top file types:")
    for ext, count in sorted(tech_files.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {ext}: {count} files")
    
    # 2. Key configuration analysis
    print("\n⚙️ PHASE 2: Configuration Analysis")
    print("-" * 30)
    
    key_configs = ['package.json', 'pyproject.toml', 'next.config.mjs', 'tailwind.config.ts']
    found_configs = []
    
    for config in key_configs:
        config_path = workspace_path / config
        if config_path.exists():
            found_configs.append(config)
            print(f"✅ {config}")
        else:
            print(f"❌ {config}")
    
    # 3. Read package.json for tech stack insight
    package_json_path = workspace_path / "package.json"
    tech_stack = {}
    
    if package_json_path.exists():
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
                
            tech_stack = {
                "name": package_data.get("name", "Unknown"),
                "dependencies": list(package_data.get("dependencies", {}).keys()),
                "dev_dependencies": list(package_data.get("devDependencies", {}).keys()),
                "scripts": list(package_data.get("scripts", {}).keys())
            }
            
            print(f"\n📦 Project: {tech_stack['name']}")
            print(f"📚 Dependencies: {len(tech_stack['dependencies'])}")
            print(f"🛠️ Dev Dependencies: {len(tech_stack['dev_dependencies'])}")
            print(f"🏃 Scripts: {len(tech_stack['scripts'])}")
            
        except Exception as e:
            print(f"⚠️ Error reading package.json: {e}")
    
    # 4. Gemini Analysis
    print("\n🤖 PHASE 3: Gemini 2.5 Pro Analysis")
    print("-" * 30)
    
    analysis_data = {
        "workspace_path": str(workspace_path),
        "total_files": total_files,
        "file_types": dict(list(tech_files.items())[:15]),  # Top 15 file types
        "configurations_found": found_configs,
        "tech_stack": tech_stack
    }
    
    prompt = f"""
    Analyze this workspace and provide actionable insights:

    WORKSPACE DATA:
    {json.dumps(analysis_data, indent=2)}

    Please provide:
    1. **Tech Stack Assessment**: What type of project is this and what technologies are being used?
    2. **Modern Stack Evaluation**: How modern and well-structured is this setup?
    3. **Quick Wins**: 3 immediate improvements that could be made
    4. **Architecture Insights**: What does the file structure tell us about the project architecture?
    5. **Development Workflow**: What development practices are evident?
    6. **Next Steps**: Priority recommendations for improvement

    Keep it concise but actionable - focus on the most impactful insights.
    """
    
    try:
        async with websockets.connect("ws://localhost:8015") as websocket:
            message = {
                "jsonrpc": "2.0",
                "id": "quick_demo",
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
                analysis = result["result"].get("response", "")
                model = result["result"].get("model", "")
                
                print(f"✅ Analysis complete using {model}")
                print("\n📊 GEMINI INSIGHTS:")
                print("=" * 50)
                print(analysis)
                
                # Save results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = workspace_path / f"quick_analysis_{timestamp}.json"
                
                results = {
                    "timestamp": datetime.now().isoformat(),
                    "workspace_data": analysis_data,
                    "gemini_analysis": analysis,
                    "model_used": model
                }
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                print(f"\n💾 Results saved to: {output_file}")
                
            else:
                error = result.get("error", "Unknown error")
                print(f"❌ Gemini analysis failed: {error}")
                
    except Exception as e:
        print(f"❌ Failed to connect to Gemini: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Quick Demo Complete!")
    print("💡 This demonstrates Gemini 2.5 Pro's ability to:")
    print("   • Understand complex project structures")
    print("   • Provide actionable technical insights")
    print("   • Analyze multiple data sources simultaneously")
    print("   • Generate comprehensive recommendations")
    print("=" * 60)

async def focused_code_search_demo():
    """Demonstrate intelligent code search capabilities"""
    workspace_path = pathlib.Path("c:\\Workspace\\MCPVots")
    
    print("\n🔍 BONUS: Focused Code Search Demo")
    print("=" * 40)
    
    # Search for React components
    react_files = []
    for root, dirs, files in os.walk(workspace_path / "src"):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith(('.tsx', '.jsx')):
                file_path = pathlib.Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for React components
                    if 'export' in content and ('function' in content or 'const' in content):
                        react_files.append({
                            "file": str(file_path.relative_to(workspace_path)),
                            "size": len(content),
                            "has_hooks": 'useState' in content or 'useEffect' in content
                        })
                except Exception:
                    pass
    
    if react_files:
        print(f"✅ Found {len(react_files)} React components")
        print("🧩 Component analysis:")
        for comp in react_files[:5]:
            hooks_indicator = "🪝" if comp['has_hooks'] else "📄"
            print(f"   {hooks_indicator} {comp['file']} ({comp['size']} chars)")
        
        # Quick Gemini analysis of React architecture
        prompt = f"""
        Analyze these React components and provide insights:
        
        COMPONENTS FOUND: {len(react_files)}
        SAMPLE COMPONENTS: {json.dumps(react_files[:3], indent=2)}
        
        Quick assessment:
        1. Component architecture quality
        2. Modern React patterns usage
        3. Potential improvements
        """
        
        try:
            async with websockets.connect("ws://localhost:8015") as websocket:
                message = {
                    "jsonrpc": "2.0",
                    "id": "react_analysis",
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
                    print(f"\n🤖 React Architecture Insights:")
                    print("-" * 30)
                    analysis = result["result"].get("response", "")
                    # Show first few lines
                    lines = analysis.split('\n')[:6]
                    for line in lines:
                        if line.strip():
                            print(f"   {line.strip()}")
                    print("   ... (truncated)")
                    
        except Exception as e:
            print(f"⚠️ React analysis failed: {e}")
    else:
        print("❌ No React components found")

if __name__ == "__main__":
    async def main():
        await quick_workspace_demo()
        await focused_code_search_demo()
    
    asyncio.run(main())
