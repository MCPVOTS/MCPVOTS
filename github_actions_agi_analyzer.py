#!/usr/bin/env python3
"""
GitHub Actions AGI Workflow Analyzer and Upgrader
=================================================
Analyzes and upgrades GitHub Actions workflows to leverage the latest AGI/n8n capabilities.
Provides recommendations for improving auto-update workflows and CI/CD integration.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_actions_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GitHubActionsAGIAnalyzer:
    def __init__(self):
        self.github_dir = Path(".github")
        self.workflows_dir = self.github_dir / "workflows"
        self.actions_dir = self.github_dir / "actions"
        self.analysis_results = {}
        
    async def analyze_workflows(self) -> Dict[str, Any]:
        """Analyze all GitHub Actions workflows"""
        logger.info("🔍 Analyzing GitHub Actions workflows...")
        
        if not self.workflows_dir.exists():
            return {"error": "No .github/workflows directory found"}
        
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_workflows": len(workflow_files),
            "workflow_analysis": {},
            "agi_integration_status": {},
            "upgrade_recommendations": [],
            "best_practices_compliance": {}
        }
        
        for workflow_file in workflow_files:
            try:
                workflow_analysis = await self._analyze_single_workflow(workflow_file)
                analysis["workflow_analysis"][workflow_file.name] = workflow_analysis
                
                # Check AGI integration
                agi_status = self._check_agi_integration(workflow_analysis)
                analysis["agi_integration_status"][workflow_file.name] = agi_status
                
            except Exception as e:
                logger.error(f"❌ Error analyzing {workflow_file.name}: {e}")
                analysis["workflow_analysis"][workflow_file.name] = {"error": str(e)}
        
        # Generate upgrade recommendations
        analysis["upgrade_recommendations"] = self._generate_upgrade_recommendations(analysis)
        
        # Check best practices compliance
        analysis["best_practices_compliance"] = self._check_best_practices_compliance(analysis)
        
        return analysis
    
    async def _analyze_single_workflow(self, workflow_file: Path) -> Dict[str, Any]:
        """Analyze a single workflow file"""
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML
            workflow_data = yaml.safe_load(content)
            
            analysis = {
                "file_size": len(content),
                "line_count": len(content.split('\n')),
                "name": workflow_data.get("name", "Unnamed"),
                "triggers": list(workflow_data.get("on", {}).keys()),
                "jobs": list(workflow_data.get("jobs", {}).keys()),
                "job_count": len(workflow_data.get("jobs", {})),
                "uses_actions": [],
                "environment_variables": list(workflow_data.get("env", {}).keys()),
                "secrets_used": [],
                "agi_keywords": [],
                "n8n_integration": False,
                "trilogy_integration": False,
                "gemini_integration": False,
                "memory_integration": False,
                "auto_update_features": [],
                "security_features": [],
                "performance_optimizations": [],
                "error_handling": [],
                "monitoring_features": []
            }
            
            # Extract used actions
            for job_name, job_data in workflow_data.get("jobs", {}).items():
                for step in job_data.get("steps", []):
                    if "uses" in step:
                        analysis["uses_actions"].append(step["uses"])
            
            # Check for secrets usage
            secrets_pattern = "${{ secrets."
            if secrets_pattern in content:
                import re
                secrets = re.findall(r'\$\{\{\s*secrets\.(\w+)\s*\}\}', content)
                analysis["secrets_used"] = list(set(secrets))
            
            # Check for AGI-related keywords
            agi_keywords = [
                "trilogy", "agi", "ollama", "deerflow", "dgm", "owl", "agent-file",
                "gemini", "n8n", "memory-mcp", "knowledge-graph", "auto-optimizer"
            ]
            
            content_lower = content.lower()
            for keyword in agi_keywords:
                if keyword in content_lower:
                    analysis["agi_keywords"].append(keyword)
            
            # Check specific integrations
            analysis["n8n_integration"] = "n8n" in content_lower
            analysis["trilogy_integration"] = "trilogy" in content_lower
            analysis["gemini_integration"] = "gemini" in content_lower
            analysis["memory_integration"] = "memory" in content_lower or "knowledge" in content_lower
            
            # Check auto-update features
            auto_update_features = [
                "dependency", "security", "optimization", "performance", "learning"
            ]
            for feature in auto_update_features:
                if feature in content_lower:
                    analysis["auto_update_features"].append(feature)
            
            # Check security features
            security_features = [
                "audit", "vulnerability", "security", "secrets", "token"
            ]
            for feature in security_features:
                if feature in content_lower:
                    analysis["security_features"].append(feature)
            
            # Check performance optimizations
            perf_features = [
                "cache", "parallel", "matrix", "artifact", "timeout"
            ]
            for feature in perf_features:
                if feature in content_lower:
                    analysis["performance_optimizations"].append(feature)
            
            # Check error handling
            error_features = [
                "continue-on-error", "if:", "failure", "try", "catch"
            ]
            for feature in error_features:
                if feature in content_lower:
                    analysis["error_handling"].append(feature)
            
            # Check monitoring features
            monitoring_features = [
                "summary", "artifact", "report", "notification", "status"
            ]
            for feature in monitoring_features:
                if feature in content_lower:
                    analysis["monitoring_features"].append(feature)
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def _check_agi_integration(self, workflow_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Check AGI integration status"""
        agi_score = 0
        max_score = 10
        
        # Check for AGI components
        if workflow_analysis.get("trilogy_integration"):
            agi_score += 2
        if workflow_analysis.get("gemini_integration"):
            agi_score += 2
        if workflow_analysis.get("n8n_integration"):
            agi_score += 2
        if workflow_analysis.get("memory_integration"):
            agi_score += 2
        
        # Check for AGI keywords
        agi_keywords_count = len(workflow_analysis.get("agi_keywords", []))
        if agi_keywords_count >= 5:
            agi_score += 2
        elif agi_keywords_count >= 3:
            agi_score += 1
        
        # Determine integration level
        if agi_score >= 8:
            integration_level = "excellent"
        elif agi_score >= 6:
            integration_level = "good"
        elif agi_score >= 4:
            integration_level = "moderate"
        elif agi_score >= 2:
            integration_level = "basic"
        else:
            integration_level = "none"
        
        return {
            "score": agi_score,
            "max_score": max_score,
            "percentage": (agi_score / max_score) * 100,
            "level": integration_level,
            "has_trilogy": workflow_analysis.get("trilogy_integration", False),
            "has_gemini": workflow_analysis.get("gemini_integration", False),
            "has_n8n": workflow_analysis.get("n8n_integration", False),
            "has_memory": workflow_analysis.get("memory_integration", False),
            "agi_keywords_count": agi_keywords_count
        }
    
    def _generate_upgrade_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate upgrade recommendations"""
        recommendations = []
        
        # Check each workflow for upgrade opportunities
        for workflow_name, workflow_data in analysis["workflow_analysis"].items():
            if isinstance(workflow_data, dict) and "error" not in workflow_data:
                workflow_recommendations = []
                
                # AGI Integration recommendations
                agi_status = analysis["agi_integration_status"].get(workflow_name, {})
                if agi_status.get("level") == "none":
                    workflow_recommendations.append({
                        "type": "agi_integration",
                        "priority": "high",
                        "description": "Add AGI integration with Trilogy stack",
                        "implementation": "Add setup-agi-environment action and AGI service integration"
                    })
                elif agi_status.get("level") in ["basic", "moderate"]:
                    workflow_recommendations.append({
                        "type": "agi_enhancement",
                        "priority": "medium",
                        "description": "Enhance existing AGI integration",
                        "implementation": "Add missing AGI components (n8n, memory, etc.)"
                    })
                
                # Auto-update features
                if "auto-update" in workflow_name.lower() or "update" in workflow_name.lower():
                    auto_features = workflow_data.get("auto_update_features", [])
                    if len(auto_features) < 3:
                        workflow_recommendations.append({
                            "type": "auto_update_enhancement",
                            "priority": "medium",
                            "description": "Add comprehensive auto-update features",
                            "implementation": "Add dependency analysis, security scanning, performance optimization"
                        })
                
                # Security features
                security_features = workflow_data.get("security_features", [])
                if len(security_features) < 2:
                    workflow_recommendations.append({
                        "type": "security_enhancement",
                        "priority": "high",
                        "description": "Add security scanning and vulnerability checks",
                        "implementation": "Add npm audit, security patch automation, secret scanning"
                    })
                
                # Performance optimizations
                perf_features = workflow_data.get("performance_optimizations", [])
                if len(perf_features) < 2:
                    workflow_recommendations.append({
                        "type": "performance_optimization",
                        "priority": "medium",
                        "description": "Add performance optimizations",
                        "implementation": "Add caching, parallel execution, artifact management"
                    })
                
                # Error handling
                error_features = workflow_data.get("error_handling", [])
                if len(error_features) < 2:
                    workflow_recommendations.append({
                        "type": "error_handling",
                        "priority": "medium",
                        "description": "Improve error handling and resilience",
                        "implementation": "Add proper error handling, retry logic, failure notifications"
                    })
                
                # Monitoring and reporting
                monitoring_features = workflow_data.get("monitoring_features", [])
                if len(monitoring_features) < 3:
                    workflow_recommendations.append({
                        "type": "monitoring_enhancement",
                        "priority": "low",
                        "description": "Add comprehensive monitoring and reporting",
                        "implementation": "Add step summaries, artifacts, status reports"
                    })
                
                if workflow_recommendations:
                    recommendations.append({
                        "workflow": workflow_name,
                        "recommendations": workflow_recommendations
                    })
        
        return recommendations
    
    def _check_best_practices_compliance(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Check best practices compliance"""
        compliance = {
            "overall_score": 0,
            "max_score": 100,
            "checks": {}
        }
        
        total_workflows = analysis["total_workflows"]
        if total_workflows == 0:
            return compliance
        
        # Check 1: AGI Integration (20 points)
        agi_workflows = sum(1 for status in analysis["agi_integration_status"].values() 
                           if status.get("level") not in ["none", "basic"])
        agi_score = min(20, (agi_workflows / total_workflows) * 20)
        compliance["checks"]["agi_integration"] = {
            "score": agi_score,
            "max_score": 20,
            "description": "AGI integration across workflows",
            "status": "excellent" if agi_score >= 16 else "good" if agi_score >= 10 else "needs_improvement"
        }
        compliance["overall_score"] += agi_score
        
        # Check 2: Security Features (20 points)
        security_workflows = sum(1 for workflow in analysis["workflow_analysis"].values()
                               if isinstance(workflow, dict) and len(workflow.get("security_features", [])) >= 2)
        security_score = min(20, (security_workflows / total_workflows) * 20)
        compliance["checks"]["security_features"] = {
            "score": security_score,
            "max_score": 20,
            "description": "Security scanning and vulnerability management",
            "status": "excellent" if security_score >= 16 else "good" if security_score >= 10 else "needs_improvement"
        }
        compliance["overall_score"] += security_score
        
        # Check 3: Performance Optimization (15 points)
        perf_workflows = sum(1 for workflow in analysis["workflow_analysis"].values()
                           if isinstance(workflow, dict) and len(workflow.get("performance_optimizations", [])) >= 2)
        perf_score = min(15, (perf_workflows / total_workflows) * 15)
        compliance["checks"]["performance_optimization"] = {
            "score": perf_score,
            "max_score": 15,
            "description": "Performance optimizations (caching, parallelization)",
            "status": "excellent" if perf_score >= 12 else "good" if perf_score >= 8 else "needs_improvement"
        }
        compliance["overall_score"] += perf_score
        
        # Check 4: Error Handling (15 points)
        error_workflows = sum(1 for workflow in analysis["workflow_analysis"].values()
                            if isinstance(workflow, dict) and len(workflow.get("error_handling", [])) >= 2)
        error_score = min(15, (error_workflows / total_workflows) * 15)
        compliance["checks"]["error_handling"] = {
            "score": error_score,
            "max_score": 15,
            "description": "Proper error handling and resilience",
            "status": "excellent" if error_score >= 12 else "good" if error_score >= 8 else "needs_improvement"
        }
        compliance["overall_score"] += error_score
        
        # Check 5: Monitoring and Reporting (15 points)
        monitoring_workflows = sum(1 for workflow in analysis["workflow_analysis"].values()
                                 if isinstance(workflow, dict) and len(workflow.get("monitoring_features", [])) >= 3)
        monitoring_score = min(15, (monitoring_workflows / total_workflows) * 15)
        compliance["checks"]["monitoring_reporting"] = {
            "score": monitoring_score,
            "max_score": 15,
            "description": "Comprehensive monitoring and reporting",
            "status": "excellent" if monitoring_score >= 12 else "good" if monitoring_score >= 8 else "needs_improvement"
        }
        compliance["overall_score"] += monitoring_score
        
        # Check 6: Modern Actions Usage (15 points)
        modern_actions_count = 0
        total_actions = 0
        for workflow in analysis["workflow_analysis"].values():
            if isinstance(workflow, dict):
                actions = workflow.get("uses_actions", [])
                total_actions += len(actions)
                # Check for modern action versions (v4, v3)
                modern_actions_count += sum(1 for action in actions if "@v4" in action or "@v3" in action)
        
        modern_score = 15 if total_actions == 0 else min(15, (modern_actions_count / total_actions) * 15)
        compliance["checks"]["modern_actions"] = {
            "score": modern_score,
            "max_score": 15,
            "description": "Usage of modern action versions",
            "status": "excellent" if modern_score >= 12 else "good" if modern_score >= 8 else "needs_improvement"
        }
        compliance["overall_score"] += modern_score
        
        # Determine overall status
        if compliance["overall_score"] >= 80:
            compliance["overall_status"] = "excellent"
        elif compliance["overall_score"] >= 60:
            compliance["overall_status"] = "good"
        elif compliance["overall_score"] >= 40:
            compliance["overall_status"] = "fair"
        else:
            compliance["overall_status"] = "needs_improvement"
        
        return compliance
    
    async def upgrade_workflow(self, workflow_name: str, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Upgrade a specific workflow based on recommendations"""
        logger.info(f"🚀 Upgrading workflow: {workflow_name}")
        
        workflow_file = self.workflows_dir / workflow_name
        if not workflow_file.exists():
            return {"error": f"Workflow file {workflow_name} not found"}
        
        try:
            # Create backup
            backup_file = workflow_file.with_suffix(f".yml.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            workflow_file.rename(backup_file)
            
            # Read original content
            with open(backup_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Apply upgrades
            upgraded_content = original_content
            applied_upgrades = []
            
            for rec in recommendations:
                if rec["type"] == "agi_integration":
                    upgraded_content = self._add_agi_integration(upgraded_content)
                    applied_upgrades.append("agi_integration")
                elif rec["type"] == "security_enhancement":
                    upgraded_content = self._add_security_features(upgraded_content)
                    applied_upgrades.append("security_enhancement")
                elif rec["type"] == "performance_optimization":
                    upgraded_content = self._add_performance_optimizations(upgraded_content)
                    applied_upgrades.append("performance_optimization")
            
            # Write upgraded content
            with open(workflow_file, 'w', encoding='utf-8') as f:
                f.write(upgraded_content)
            
            return {
                "success": True,
                "backup_file": str(backup_file),
                "applied_upgrades": applied_upgrades,
                "upgrade_count": len(applied_upgrades)
            }
            
        except Exception as e:
            # Restore original file if upgrade failed
            if backup_file.exists():
                backup_file.rename(workflow_file)
            return {"error": str(e)}
    
    def _add_agi_integration(self, content: str) -> str:
        """Add AGI integration to workflow"""
        # Add AGI environment setup step
        if "Setup AGI Environment" not in content:
            setup_step = """
    - name: Setup AGI Environment
      uses: ./.github/actions/setup-agi-environment
"""
            # Insert after checkout step
            if "uses: actions/checkout@v4" in content:
                content = content.replace(
                    "uses: actions/checkout@v4",
                    f"uses: actions/checkout@v4{setup_step}"
                )
        
        return content
    
    def _add_security_features(self, content: str) -> str:
        """Add security features to workflow"""
        # Add security audit step
        if "npm audit" not in content:
            audit_step = """
    - name: Security Audit
      run: |
        npm audit --audit-level=moderate
        echo "✅ Security audit completed"
"""
            # Add after npm install if present
            if "npm install" in content:
                content = content.replace("npm install", f"npm install{audit_step}")
        
        return content
    
    def _add_performance_optimizations(self, content: str) -> str:
        """Add performance optimizations to workflow"""
        # Add caching if not present
        if "cache:" not in content and "node-version:" in content:
            content = content.replace(
                "node-version:",
                "node-version:\n        cache: 'npm'"
            )
        
        return content
    
    async def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive analysis report"""
        report = f"""# GitHub Actions AGI Integration Analysis Report

**Generated:** {analysis['timestamp']}

## 📊 Overview

- **Total Workflows:** {analysis['total_workflows']}
- **Best Practices Score:** {analysis['best_practices_compliance']['overall_score']:.1f}/100
- **Overall Status:** {analysis['best_practices_compliance']['overall_status'].upper()}

## 🚀 AGI Integration Status

"""
        
        for workflow_name, agi_status in analysis["agi_integration_status"].items():
            level = agi_status.get("level", "unknown")
            score = agi_status.get("score", 0)
            percentage = agi_status.get("percentage", 0)
            
            status_emoji = {
                "excellent": "🟢",
                "good": "🟡", 
                "moderate": "🟠",
                "basic": "🔴",
                "none": "⚫"
            }.get(level, "❓")
            
            report += f"- **{workflow_name}:** {status_emoji} {level.upper()} ({score}/10 - {percentage:.1f}%)\n"
        
        report += f"""

## 🔍 Best Practices Compliance

"""
        
        for check_name, check_data in analysis["best_practices_compliance"]["checks"].items():
            score = check_data["score"]
            max_score = check_data["max_score"]
            status = check_data["status"]
            description = check_data["description"]
            
            status_emoji = {
                "excellent": "🟢",
                "good": "🟡",
                "needs_improvement": "🔴"
            }.get(status, "❓")
            
            report += f"- **{check_name.replace('_', ' ').title()}:** {status_emoji} {score}/{max_score} - {description}\n"
        
        report += f"""

## 💡 Upgrade Recommendations

"""
        
        total_recommendations = sum(len(rec["recommendations"]) for rec in analysis["upgrade_recommendations"])
        report += f"**Total Recommendations:** {total_recommendations}\n\n"
        
        for workflow_rec in analysis["upgrade_recommendations"]:
            workflow_name = workflow_rec["workflow"]
            recommendations = workflow_rec["recommendations"]
            
            report += f"### {workflow_name}\n\n"
            
            for rec in recommendations:
                priority = rec["priority"].upper()
                rec_type = rec["type"].replace("_", " ").title()
                description = rec["description"]
                implementation = rec["implementation"]
                
                priority_emoji = {
                    "HIGH": "🔴",
                    "MEDIUM": "🟡",
                    "LOW": "🟢"
                }.get(priority, "❓")
                
                report += f"- {priority_emoji} **{rec_type}** ({priority} Priority)\n"
                report += f"  - {description}\n"
                report += f"  - Implementation: {implementation}\n\n"
        
        report += f"""

## 🎯 Next Steps

1. **High Priority Upgrades**: Focus on security and AGI integration improvements
2. **Modernization**: Update to latest action versions and best practices
3. **Performance**: Add caching and parallelization where applicable
4. **Monitoring**: Enhance reporting and observability
5. **Testing**: Validate all changes through comprehensive testing

## 📈 Improvement Roadmap

### Phase 1: Critical Updates (Week 1)
- Security vulnerability scanning
- AGI environment setup
- Error handling improvements

### Phase 2: Enhancement (Week 2-3)
- Performance optimizations
- Comprehensive monitoring
- Auto-update intelligence

### Phase 3: Advanced Features (Week 4+)
- Full AGI stack integration
- Continuous learning implementation
- Advanced workflow orchestration

---
*Generated by GitHub Actions AGI Analyzer*
"""
        
        return report
    
    async def save_analysis(self, analysis: Dict[str, Any]) -> None:
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON analysis
        json_file = f"github_actions_analysis_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        logger.info(f"📄 Analysis saved to {json_file}")
        
        # Save markdown report
        report = await self.generate_report(analysis)
        md_file = f"github_actions_report_{timestamp}.md"
        with open(md_file, 'w') as f:
            f.write(report)
        
        logger.info(f"📄 Report saved to {md_file}")

async def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Actions AGI Workflow Analyzer")
    parser.add_argument("--mode", choices=["analyze", "upgrade", "report"], default="analyze",
                       help="Operation mode")
    parser.add_argument("--workflow", help="Specific workflow to upgrade")
    parser.add_argument("--output", choices=["json", "markdown", "both"], default="both",
                       help="Output format")
    
    args = parser.parse_args()
    
    analyzer = GitHubActionsAGIAnalyzer()
    
    try:
        logger.info("🚀 Starting GitHub Actions AGI Analysis...")
        
        # Run analysis
        analysis = await analyzer.analyze_workflows()
        
        if args.mode == "analyze":
            # Save analysis results
            await analyzer.save_analysis(analysis)
            
            # Display summary
            logger.info(f"""
🎯 ANALYSIS SUMMARY:
- Total Workflows: {analysis['total_workflows']}
- Best Practices Score: {analysis['best_practices_compliance']['overall_score']:.1f}/100
- Status: {analysis['best_practices_compliance']['overall_status'].upper()}
- Total Recommendations: {sum(len(rec['recommendations']) for rec in analysis['upgrade_recommendations'])}
""")
            
        elif args.mode == "upgrade" and args.workflow:
            # Upgrade specific workflow
            workflow_recommendations = next(
                (rec["recommendations"] for rec in analysis["upgrade_recommendations"] 
                 if rec["workflow"] == args.workflow), []
            )
            
            if workflow_recommendations:
                result = await analyzer.upgrade_workflow(args.workflow, workflow_recommendations)
                if result.get("success"):
                    logger.info(f"✅ Successfully upgraded {args.workflow}")
                    logger.info(f"Applied {result['upgrade_count']} upgrades: {', '.join(result['applied_upgrades'])}")
                else:
                    logger.error(f"❌ Failed to upgrade {args.workflow}: {result.get('error')}")
            else:
                logger.info(f"ℹ️ No upgrade recommendations found for {args.workflow}")
        
        elif args.mode == "report":
            # Generate and display report
            report = await analyzer.generate_report(analysis)
            print(report)
        
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())
