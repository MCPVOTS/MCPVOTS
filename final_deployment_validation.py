#!/usr/bin/env python3
"""
Final Deployment Validation
Validates that all components are ready for production deployment
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Import and apply Unicode fix
from unicode_logging_fix import fix_unicode_logging
fix_unicode_logging()

def validate_monorepo_structure() -> Tuple[bool, List[str]]:
    """Validate monorepo structure is complete"""
    issues = []
    monorepo_path = Path("c:\\Workspace\\agi-monorepo")
    
    required_files = [
        "package.json",
        "nx.json", 
        "docker-compose.yml",
        ".gitignore",
        ".github/workflows/ci-cd.yml",
        "scripts/deploy.sh",
        "scripts/backup.sh",
        "scripts/health-check.sh",
        "monitoring/prometheus.yml"
    ]
    
    required_dirs = [
        "packages/mcpvots",
        "packages/agi-system", 
        "packages/ai-services",
        "configs",
        "monitoring/grafana"
    ]
    
    for file_path in required_files:
        if not (monorepo_path / file_path).exists():
            issues.append(f"Missing required file: {file_path}")
    
    for dir_path in required_dirs:
        if not (monorepo_path / dir_path).exists():
            issues.append(f"Missing required directory: {dir_path}")
    
    return len(issues) == 0, issues

def validate_performance_optimizations() -> Tuple[bool, List[str]]:
    """Validate performance optimization files exist"""
    issues = []
    mcpvots_path = Path("c:\\Workspace\\MCPVots")
    
    required_files = [
        "advanced_cache.py",
        "database_optimizer.py",
        "memory_optimizer.py",
        "unicode_logging_fix.py"
    ]
    
    for file_path in required_files:
        if not (mcpvots_path / file_path).exists():
            issues.append(f"Missing optimization file: {file_path}")
    
    return len(issues) == 0, issues

def validate_reports_generated() -> Tuple[bool, List[str]]:
    """Validate all required reports were generated"""
    issues = []
    mcpvots_path = Path("c:\\Workspace\\MCPVots")
    
    report_patterns = [
        "*workspace_analysis*.json",
        "*ai_issue_resolution*.json", 
        "*monorepo_migration*.json",
        "*performance_optimization*.json",
        "*deployment_system*.json",
        "FINAL_ITERATION_SUMMARY*.md"
    ]
    
    for pattern in report_patterns:
        files = list(mcpvots_path.glob(pattern))
        if not files:
            issues.append(f"No reports found matching pattern: {pattern}")
    
    return len(issues) == 0, issues

def validate_docker_infrastructure() -> Tuple[bool, List[str]]:
    """Validate Docker infrastructure is complete"""
    issues = []
    monorepo_path = Path("c:\\Workspace\\agi-monorepo")
    
    dockerfile_locations = [
        "packages/mcpvots/Dockerfile",
        "packages/agi-system/Dockerfile", 
        "packages/ai-services/Dockerfile.memory"
    ]
    
    for dockerfile in dockerfile_locations:
        if not (monorepo_path / dockerfile).exists():
            issues.append(f"Missing Dockerfile: {dockerfile}")
    
    # Check Docker Compose file has required services
    compose_file = monorepo_path / "docker-compose.yml"
    if compose_file.exists():
        try:
            import yaml
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)
            
            required_services = [
                "agi-frontend", "agi-backend", "memory-service",
                "redis", "postgres", "prometheus", "grafana", "nginx"
            ]
            
            services = compose_data.get("services", {})
            for service in required_services:
                if service not in services:
                    issues.append(f"Missing Docker service: {service}")
        except Exception as e:
            issues.append(f"Could not validate Docker Compose file: {e}")
    else:
        issues.append("Docker Compose file not found")
    
    return len(issues) == 0, issues

def run_comprehensive_validation() -> Dict[str, Any]:
    """Run comprehensive validation of all components"""
    print("🔍 Running Final Deployment Validation...")
    print("=" * 50)
    
    validation_results = {
        "overall_status": "UNKNOWN",
        "validations": {},
        "summary": {},
        "recommendations": []
    }
    
    # Run all validations
    validations = {
        "Monorepo Structure": validate_monorepo_structure,
        "Performance Optimizations": validate_performance_optimizations,
        "Reports Generated": validate_reports_generated,
        "Docker Infrastructure": validate_docker_infrastructure
    }
    
    all_passed = True
    total_issues = 0
    
    for validation_name, validation_func in validations.items():
        print(f"\n📋 Validating {validation_name}...")
        passed, issues = validation_func()
        
        validation_results["validations"][validation_name] = {
            "passed": passed,
            "issues": issues,
            "status": "✅ PASS" if passed else "❌ FAIL"
        }
        
        if passed:
            print(f"   ✅ {validation_name}: PASSED")
        else:
            print(f"   ❌ {validation_name}: FAILED")
            for issue in issues:
                print(f"      - {issue}")
            all_passed = False
            total_issues += len(issues)
    
    # Generate summary
    validation_results["summary"] = {
        "total_validations": len(validations),
        "passed_validations": sum(1 for v in validation_results["validations"].values() if v["passed"]),
        "total_issues": total_issues,
        "overall_passed": all_passed
    }
    
    validation_results["overall_status"] = "PRODUCTION_READY" if all_passed else "NEEDS_ATTENTION"
    
    # Generate recommendations
    if all_passed:
        validation_results["recommendations"] = [
            "🚀 System is PRODUCTION READY!",
            "Execute deployment: cd agi-monorepo && ./scripts/deploy.sh",
            "Monitor with: ./scripts/health-check.sh",
            "Access frontend at: http://localhost",
            "Access monitoring at: http://localhost:3001"
        ]
    else:
        validation_results["recommendations"] = [
            f"Fix {total_issues} identified issues before deployment",
            "Re-run validation after fixes",
            "Review generated reports for additional guidance"
        ]
    
    return validation_results

def display_final_status(results: Dict[str, Any]) -> None:
    """Display final validation status"""
    print("\n" + "=" * 60)
    print("🏁 FINAL VALIDATION RESULTS")
    print("=" * 60)
    
    summary = results["summary"]
    print(f"📊 Validations: {summary['passed_validations']}/{summary['total_validations']} PASSED")
    print(f"🔍 Issues Found: {summary['total_issues']}")
    print(f"🎯 Status: {results['overall_status']}")
    
    print("\n🎯 NEXT STEPS:")
    for i, recommendation in enumerate(results["recommendations"], 1):
        print(f"   {i}. {recommendation}")
    
    if results["overall_status"] == "PRODUCTION_READY":
        print("\n🎉 CONGRATULATIONS! 🎉")
        print("The AGI Ecosystem is PRODUCTION READY!")
        print("All components validated successfully.")
    else:
        print("\n⚠️  ATTENTION REQUIRED")
        print("Please address the identified issues before deployment.")

def main():
    """Main validation entry point"""
    results = run_comprehensive_validation()
    display_final_status(results)
    
    # Save validation results
    results_path = Path("c:\\Workspace\\MCPVots\\final_validation_results.json")
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Validation results saved to: {results_path}")
    
    return 0 if results["overall_status"] == "PRODUCTION_READY" else 1

if __name__ == "__main__":
    exit(main())
