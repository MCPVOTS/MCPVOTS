#!/usr/bin/env python3
"""
Gemini 2.5 Pro Workspace Intelligence Suite
===========================================
Comprehensive demonstration of Gemini's 1M token context window
for workspace analysis, code search, and tech stack optimization.
"""

import asyncio
import json
import pathlib
from datetime import datetime
from typing import Dict, Any

from tech_stack_analyzer import TechStackAnalyzer
from intelligent_code_searcher import IntelligentCodeSearcher

class WorkspaceIntelligenceSuite:
    def __init__(self, workspace_path: str = "c:\\Workspace"):
        self.workspace_path = pathlib.Path(workspace_path)
        self.analyzer = TechStackAnalyzer(workspace_path)
        self.searcher = IntelligentCodeSearcher(workspace_path)
        self.results = {}
    
    async def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run the complete workspace intelligence suite"""
        print("🚀 Starting Comprehensive Workspace Intelligence Analysis")
        print("=" * 70)
        print(f"📁 Workspace: {self.workspace_path}")
        print(f"🤖 AI Model: Gemini 2.5 Pro (1M token context)")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # 1. Tech Stack Analysis
        print("\n🔧 PHASE 1: Technology Stack Analysis")
        print("-" * 40)
        try:
            tech_analysis = await self.analyzer.analyze_workspace()
            self.results["tech_stack"] = tech_analysis
            
            print(f"✅ Technologies discovered: {tech_analysis['summary']['tech_count']}")
            print(f"✅ Gemini analysis: {'Available' if tech_analysis['summary']['analysis_available'] else 'Failed'}")
            
            # Show top technologies
            if tech_analysis.get('tech_inventory'):
                print("🏆 Top Technologies Found:")
                for tech, files in list(tech_analysis['tech_inventory'].items())[:5]:
                    print(f"   • {tech}: {len(files)} files")
                    
        except Exception as e:
            print(f"❌ Tech stack analysis failed: {e}")
            self.results["tech_stack"] = {"error": str(e)}
        
        # 2. Security Analysis
        print("\n🔒 PHASE 2: Security Analysis")
        print("-" * 40)
        try:
            security_analysis = await self.searcher.search_and_analyze(
                "password secret key token auth", "security"
            )
            self.results["security"] = security_analysis
            
            print(f"✅ Security scan complete: {security_analysis['matches_found']} potential issues found")
            if security_analysis['matches_found'] > 0:
                print("⚠️  Security concerns detected:")
                for match in security_analysis['matches'][:3]:
                    print(f"   • {match['file']}: {', '.join(match['matches'])}")
                    
        except Exception as e:
            print(f"❌ Security analysis failed: {e}")
            self.results["security"] = {"error": str(e)}
        
        # 3. API Analysis
        print("\n🌐 PHASE 3: API and Integration Analysis")
        print("-" * 40)
        try:
            api_analysis = await self.searcher.search_and_analyze(
                "endpoint route api fetch axios", "api"
            )
            self.results["api"] = api_analysis
            
            print(f"✅ API analysis complete: {api_analysis['matches_found']} endpoints/integrations found")
            if api_analysis['matches_found'] > 0:
                print("🔗 API patterns found:")
                for match in api_analysis['matches'][:3]:
                    print(f"   • {match['file']}")
                    
        except Exception as e:
            print(f"❌ API analysis failed: {e}")
            self.results["api"] = {"error": str(e)}
        
        # 4. Architecture Analysis
        print("\n🏗️ PHASE 4: Architecture and Pattern Analysis")
        print("-" * 40)
        try:
            arch_analysis = await self.searcher.search_and_analyze(
                "class component module service", "class"
            )
            self.results["architecture"] = arch_analysis
            
            print(f"✅ Architecture analysis complete: {arch_analysis['matches_found']} components found")
            if arch_analysis['matches_found'] > 0:
                print("🏛️ Architecture components:")
                for match in arch_analysis['matches'][:3]:
                    print(f"   • {match['file']}: {match['file_info']['classes_count']} classes, {match['file_info']['functions_count']} functions")
                    
        except Exception as e:
            print(f"❌ Architecture analysis failed: {e}")
            self.results["architecture"] = {"error": str(e)}
        
        # 5. Generate comprehensive report
        print("\n📊 PHASE 5: Comprehensive Report Generation")
        print("-" * 40)
        try:
            report = await self.generate_comprehensive_report()
            self.results["comprehensive_report"] = report
            print("✅ Comprehensive report generated")
            
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
            self.results["comprehensive_report"] = {"error": str(e)}
        
        # Save all results
        output_file = await self.save_results()
        
        print("\n" + "=" * 70)
        print("🎉 WORKSPACE INTELLIGENCE ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"📄 Full results saved to: {output_file}")
        print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show executive summary
        await self.show_executive_summary()
        
        return self.results
    
    async def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report using all analysis results"""
        print("🤖 Generating comprehensive insights with Gemini 2.5 Pro...")
        
        # Combine all analysis results
        combined_data = {
            "workspace_path": str(self.workspace_path),
            "analysis_timestamp": datetime.now().isoformat(),
            "tech_stack_summary": self.results.get("tech_stack", {}).get("summary", {}),
            "security_findings": {
                "issues_found": self.results.get("security", {}).get("matches_found", 0),
                "critical_files": [m["file"] for m in self.results.get("security", {}).get("matches", [])[:5]]
            },
            "api_summary": {
                "endpoints_found": self.results.get("api", {}).get("matches_found", 0),
                "integration_files": [m["file"] for m in self.results.get("api", {}).get("matches", [])[:5]]
            },
            "architecture_summary": {
                "components_found": self.results.get("architecture", {}).get("matches_found", 0),
                "main_files": [m["file"] for m in self.results.get("architecture", {}).get("matches", [])[:5]]
            }
        }
        
        prompt = f"""
        Based on this comprehensive workspace analysis, provide strategic insights and recommendations:

        WORKSPACE ANALYSIS DATA:
        {json.dumps(combined_data, indent=2)}

        Please provide a strategic analysis including:

        ## EXECUTIVE SUMMARY
        - Overall workspace health and maturity
        - Key strengths and weaknesses
        - Critical issues requiring immediate attention

        ## TECHNOLOGY ASSESSMENT
        - Modern vs legacy technology usage
        - Technology stack coherence and integration
        - Missing critical technologies or tools

        ## SECURITY POSTURE
        - Security risks and vulnerabilities
        - Compliance considerations
        - Recommended security improvements

        ## ARCHITECTURE EVALUATION
        - Code organization and structure quality
        - Scalability and maintainability assessment
        - Architectural debt and technical debt

        ## PERFORMANCE & OPTIMIZATION
        - Performance bottlenecks and optimization opportunities
        - Resource utilization efficiency
        - Scaling considerations

        ## DEVELOPMENT WORKFLOW
        - Development process maturity
        - CI/CD and automation opportunities
        - Testing and quality assurance gaps

        ## STRATEGIC ROADMAP
        - Priority 1: Immediate actions (next 30 days)
        - Priority 2: Short-term improvements (next 90 days)
        - Priority 3: Long-term strategic initiatives (next year)

        ## INVESTMENT RECOMMENDATIONS
        - Where to invest development resources
        - Technologies to adopt or upgrade
        - Skills and training needs

        Focus on actionable, specific recommendations with clear business impact.
        """
        
        try:
            import websockets
            async with websockets.connect("ws://localhost:8015") as websocket:
                message = {
                    "jsonrpc": "2.0",
                    "id": "comprehensive_report",
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
                        "strategic_analysis": result["result"].get("response", ""),
                        "model": result["result"].get("model", ""),
                        "timestamp": result["result"].get("timestamp", ""),
                        "data_analyzed": combined_data
                    }
                else:
                    return {"error": result.get("error", "Unknown error")}
                    
        except Exception as e:
            return {"error": f"Failed to generate comprehensive report: {str(e)}"}
    
    async def show_executive_summary(self):
        """Show executive summary of all analyses"""
        print("\n📋 EXECUTIVE SUMMARY")
        print("=" * 50)
        
        # Tech Stack Summary
        tech_summary = self.results.get("tech_stack", {}).get("summary", {})
        print(f"🔧 Technologies: {tech_summary.get('tech_count', 'Unknown')} discovered")
        
        # Security Summary
        security_count = self.results.get("security", {}).get("matches_found", 0)
        security_status = "🟢 Good" if security_count < 5 else "🟡 Review Needed" if security_count < 15 else "🔴 Critical"
        print(f"🔒 Security: {security_status} ({security_count} potential issues)")
        
        # API Summary
        api_count = self.results.get("api", {}).get("matches_found", 0)
        print(f"🌐 APIs: {api_count} endpoints/integrations found")
        
        # Architecture Summary
        arch_count = self.results.get("architecture", {}).get("matches_found", 0)
        print(f"🏗️ Architecture: {arch_count} components analyzed")
        
        # Comprehensive Report Status
        report_status = "✅ Available" if "strategic_analysis" in self.results.get("comprehensive_report", {}) else "❌ Failed"
        print(f"📊 Strategic Report: {report_status}")
        
        if "strategic_analysis" in self.results.get("comprehensive_report", {}):
            print("\n🎯 KEY INSIGHTS:")
            analysis = self.results["comprehensive_report"]["strategic_analysis"]
            # Extract first few key points
            lines = analysis.split('\n')[:8]
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    print(f"   • {line.strip()}")
            print("   ... (see full strategic analysis in saved report)")
    
    async def save_results(self) -> str:
        """Save all analysis results to a comprehensive report file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"workspace_intelligence_report_{timestamp}.json"
        filepath = self.workspace_path / filename
        
        # Add metadata
        self.results["metadata"] = {
            "analysis_timestamp": datetime.now().isoformat(),
            "workspace_path": str(self.workspace_path),
            "gemini_model": "gemini-2.5-pro",
            "analysis_version": "1.0.0",
            "phases_completed": list(self.results.keys())
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        return str(filepath)

async def main():
    """Run the complete workspace intelligence suite"""
    suite = WorkspaceIntelligenceSuite()
    
    try:
        results = await suite.run_comprehensive_analysis()
        print(f"\n✅ Analysis complete! Results available in memory and saved to file.")
        
    except KeyboardInterrupt:
        print("\n⏹️ Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
