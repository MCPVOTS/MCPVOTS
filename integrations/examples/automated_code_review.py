#!/usr/bin/env python3
"""
Automated Code Review Example
=============================
Demonstrates how to use MCPVots integration for automated code reviews
with real GitHub integration and Gemini-powered analysis.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from mcp_tools_integration import MCPVotsIntegratedSystem

async def automated_code_review_example():
    """
    Example: Automated code review for a GitHub repository
    """
    print("🚀 MCPVots Automated Code Review Example")
    print("=" * 50)
    
    # Initialize the integrated system
    system = MCPVotsIntegratedSystem()
    await system.initialize()
    
    # Configuration - can be customized or loaded from environment
    config = {
        "repository": {
            "owner": os.getenv("GITHUB_OWNER", "mcpvots-demo"),
            "name": os.getenv("REPO_NAME", "sample-project"),
            "local_path": os.getenv("REPO_PATH", "C:/Workspace/MCPVots")
        },
        "review_settings": {
            "check_security": True,
            "check_performance": True,
            "check_style": True,
            "suggest_tests": True,
            "check_documentation": True,
            "check_dependencies": True
        },
        "gemini_settings": {
            "model": "gemini-2.5-pro",
            "include_search": True,
            "include_workspace": True
        }
    }
    
    print(f"\n📊 Analyzing repository: {config['repository']['name']}")
    
    # Step 1: Analyze the repository structure
    print("\n1️⃣ Analyzing repository structure...")
    repo_analysis = await system.analyze_and_optimize_repository(
        config['repository']['local_path']
    )
    
    print(f"   ✅ Found {repo_analysis['analysis']['structure']['total_files']} files")
    print(f"   ✅ Languages: {', '.join(repo_analysis['analysis']['structure']['languages'])}")
    print(f"   ✅ Structure score: {repo_analysis['analysis']['structure']['structure_score']}")
    
    # Step 2: Check for open PRs using actual GitHub integration
    print("\n2️⃣ Checking for open pull requests...")
    
    try:
        # Use the GitHub tool to fetch real PRs
        pr_list_result = await system.tools['github'].list_pull_requests(
            owner=config['repository']['owner'],
            repo=config['repository']['name'],
            state="open"
        )
        
        open_prs = pr_list_result.get('pull_requests', [])
        print(f"   ✅ Found {len(open_prs)} open PRs")
        
        # If no real PRs, use demo data
        if not open_prs:
            print("   ℹ️  No open PRs found, using demo data for illustration")
            open_prs = [
                {"number": 42, "title": "Add AI-powered code completion", "author": "developer1"},
                {"number": 43, "title": "Fix memory leak in parser", "author": "developer2"},
                {"number": 44, "title": "Update HuggingFace dependencies", "author": "dependabot"}
            ]
    except Exception as e:
        print(f"   ⚠️  Could not fetch PRs from GitHub: {e}")
        print("   ℹ️  Using demo data for illustration")
        open_prs = [
            {"number": 42, "title": "Add AI-powered code completion", "author": "developer1"},
            {"number": 43, "title": "Fix memory leak in parser", "author": "developer2"},
            {"number": 44, "title": "Update HuggingFace dependencies", "author": "dependabot"}
        ]
    
    # Step 3: Review each PR
    print("\n3️⃣ Reviewing pull requests...")
    
    pr_reviews_summary = []
    for pr in open_prs:
        print(f"\n   📍 Reviewing PR #{pr['number']}: {pr['title']}")
        
        # Create intelligent review
        review_result = await system.create_intelligent_pr_review(
            config['repository']['owner'],
            config['repository']['name'],
            pr['number']
        )
        
        # Display review summary
        feedback = review_result['feedback']
        print(f"      Status: {feedback['approval_status']}")
        print(f"      Summary: {feedback['summary']}")
        
        if feedback['must_fix']:
            print("      ⚠️  Must fix:")
            for fix in feedback['must_fix']:
                print(f"         - {fix}")
        
        if feedback['suggestions']:
            print("      💡 Suggestions:")
            for suggestion in feedback['suggestions']:
                print(f"         - {suggestion}")
        
        # Store review summary
        pr_reviews_summary.append({
            "pr_number": pr['number'],
            "title": pr['title'],
            "status": feedback['approval_status'],
            "summary": feedback['summary']
        })
    
    # Step 4: Generate automation workflows
    print("\n4️⃣ Creating automation workflows...")
    
    workflow_result = await system.execute_complex_workflow(
        "code_review_automation",
        {
            "repository": config['repository']['name'],
            "branch": "main",
            "settings": config['review_settings']
        }
    )
    
    print(f"   ✅ Workflow completed with {len(workflow_result['steps'])} steps")
    
    # Step 5: Generate comprehensive report with insights
    print("\n5️⃣ Generating comprehensive report...")
    
    # Get additional insights from Gemini
    insights_prompt = f"""
    Based on the code review analysis:
    - Repository: {config['repository']['name']}
    - PRs reviewed: {len(open_prs)}
    - Structure score: {repo_analysis['analysis']['structure']['structure_score']}
    
    Provide:
    1. Overall code health assessment
    2. Top 3 improvement priorities
    3. Security considerations
    4. Performance optimization opportunities
    """
    
    gemini_insights = await system._analyze_code_quality_with_gemini(insights_prompt)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "repository": config['repository']['name'],
        "analysis_summary": {
            "total_files": repo_analysis['analysis']['structure']['total_files'],
            "structure_score": repo_analysis['analysis']['structure']['structure_score'],
            "open_prs": len(open_prs),
            "prs_reviewed": len(open_prs),
            "languages": repo_analysis['analysis']['structure']['languages']
        },
        "gemini_insights": gemini_insights,
        "recommendations": workflow_result['results']['recommendations'],
        "automation_opportunities": repo_analysis['automations'],
        "pr_reviews": pr_reviews_summary
    }
    
    # Save report
    report_path = Path("reports") / f"code_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"   ✅ Report saved to: {report_path}")
    
    # Display enhanced summary
    print("\n" + "=" * 50)
    print("📊 Code Review Summary")
    print("=" * 50)
    print(f"Repository: {config['repository']['name']}")
    print(f"Files analyzed: {report['analysis_summary']['total_files']}")
    print(f"Languages: {', '.join(report['analysis_summary']['languages'])}")
    print(f"Structure score: {report['analysis_summary']['structure_score']:.2f}/1.00")
    print(f"PRs reviewed: {report['analysis_summary']['prs_reviewed']}")
    
    print(f"\n🤖 Gemini AI Insights:")
    if isinstance(gemini_insights, dict) and gemini_insights.get('response'):
        print(f"   {gemini_insights['response'][:200]}...")
    
    print(f"\n📋 Top recommendations:")
    for i, rec in enumerate(report['recommendations'][:3], 1):
        print(f"{i}. {rec['recommendation']} (Impact: {rec['impact']})")
    
    print(f"\n🔧 Automation opportunities: {len(report['automation_opportunities'])}")
    for auto in report['automation_opportunities'][:2]:
        print(f"   - {auto['name']}: {auto['description']}")
    
    # Close connections
    if system.gemini_ws:
        await system.gemini_ws.close()

if __name__ == "__main__":
    # Run the example
    asyncio.run(automated_code_review_example())
