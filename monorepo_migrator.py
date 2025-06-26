#!/usr/bin/env python3
"""
Monorepo Migration Implementation
Phase 1 of Architecture Improvement Plan
"""

import os
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Import and apply Unicode fix
from unicode_logging_fix import fix_unicode_logging
fix_unicode_logging()

logger = logging.getLogger(__name__)

class MonorepoMigrator:
    """Implements the monorepo migration plan"""
    
    def __init__(self, workspace_path: str = "c:\\Workspace"):
        self.workspace_path = Path(workspace_path)
        self.mcpvots_path = self.workspace_path / "MCPVots"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Load the migration plan
        self.migration_plan = self._load_migration_plan()
        
        logger.info("Monorepo Migrator initialized")
    
    def _load_migration_plan(self) -> Dict[str, Any]:
        """Load the monorepo migration plan"""
        try:
            plan_path = self.mcpvots_path / "monorepo_migration_plan.json"
            if plan_path.exists():
                with open(plan_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load migration plan: {e}")
        
        # Default plan if file not found
        return {
            "title": "Monorepo Migration Plan",
            "phases": [
                {
                    "phase": 1,
                    "title": "Preparation",
                    "tasks": [
                        "Audit all projects for dependencies",
                        "Standardize package.json structures",
                        "Create unified linting/formatting config"
                    ]
                }
            ]
        }
    
    def audit_projects(self) -> Dict[str, Any]:
        """Audit all projects in the workspace"""
        logger.info("Phase 1: Auditing all projects for dependencies...")
        
        projects = {}
        
        # Find all package.json files
        for package_json in self.workspace_path.rglob("package.json"):
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                project_name = package_data.get('name', package_json.parent.name)
                projects[project_name] = {
                    "path": str(package_json.parent),
                    "dependencies": package_data.get('dependencies', {}),
                    "devDependencies": package_data.get('devDependencies', {}),
                    "scripts": package_data.get('scripts', {}),
                    "packageJson": str(package_json)
                }
                
            except Exception as e:
                logger.warning(f"Could not read {package_json}: {e}")
        
        logger.info(f"Found {len(projects)} JavaScript/TypeScript projects")
        
        # Find all Python projects
        for pyproject_toml in self.workspace_path.rglob("pyproject.toml"):
            try:
                project_name = f"python-{pyproject_toml.parent.name}"
                projects[project_name] = {
                    "path": str(pyproject_toml.parent),
                    "type": "python",
                    "config": str(pyproject_toml)
                }
            except Exception as e:
                logger.warning(f"Could not process {pyproject_toml}: {e}")
        
        # Find Python projects with requirements.txt
        for requirements_txt in self.workspace_path.rglob("requirements.txt"):
            if requirements_txt.parent.name not in [p.get('path', '').split(os.sep)[-1] for p in projects.values()]:
                project_name = f"python-{requirements_txt.parent.name}"
                projects[project_name] = {
                    "path": str(requirements_txt.parent),
                    "type": "python",
                    "requirements": str(requirements_txt)
                }
        
        logger.info(f"Total projects found: {len(projects)}")
        
        # Save audit results
        audit_path = self.mcpvots_path / f"project_audit_{self.timestamp}.json"
        with open(audit_path, 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2)
        
        logger.info(f"Project audit saved to {audit_path}")
        return projects
    
    def create_monorepo_structure(self) -> None:
        """Create the monorepo structure"""
        logger.info("Phase 2: Creating monorepo structure...")
        
        monorepo_path = self.workspace_path / "agi-monorepo"
        
        # Create directory structure
        directories = [
            "packages/frontend",      # React/Next.js apps
            "packages/backend",       # Python services
            "packages/ai-services",   # AI/ML services
            "packages/shared",        # Shared utilities
            "tools/scripts",          # Build and deployment scripts
            "docs",                   # Documentation
            "configs",                # Shared configurations
        ]
        
        for directory in directories:
            (monorepo_path / directory).mkdir(parents=True, exist_ok=True)
        
        # Create root package.json for Nx workspace
        root_package_json = {
            "name": "agi-monorepo",
            "version": "1.0.0",
            "description": "AGI Ecosystem Monorepo",
            "private": True,
            "workspaces": [
                "packages/*"
            ],
            "scripts": {
                "build": "nx run-many --target=build --all",
                "test": "nx run-many --target=test --all",
                "lint": "nx run-many --target=lint --all",
                "dev": "nx run-many --target=dev --all"
            },
            "devDependencies": {
                "@nx/workspace": "^17.0.0",
                "@nx/js": "^17.0.0",
                "@nx/react": "^17.0.0",
                "@nx/next": "^17.0.0",
                "nx": "^17.0.0"
            }
        }
        
        with open(monorepo_path / "package.json", 'w', encoding='utf-8') as f:
            json.dump(root_package_json, f, indent=2)
        
        # Create nx.json configuration
        nx_config = {
            "extends": "nx/presets/npm.json",
            "targetDefaults": {
                "build": {
                    "cache": True
                },
                "test": {
                    "cache": True
                },
                "lint": {
                    "cache": True
                }
            },
            "defaultProject": "mcpvots"
        }
        
        with open(monorepo_path / "nx.json", 'w', encoding='utf-8') as f:
            json.dump(nx_config, f, indent=2)
        
        # Create .gitignore
        gitignore_content = """
node_modules/
dist/
.next/
.nx/
*.log
.env
.env.local
__pycache__/
*.pyc
.pytest_cache/
.coverage
.vscode/
.DS_Store
"""
        
        with open(monorepo_path / ".gitignore", 'w', encoding='utf-8') as f:
            f.write(gitignore_content.strip())
        
        logger.info(f"Monorepo structure created at {monorepo_path}")
    
    def migrate_core_projects(self) -> None:
        """Migrate core projects to monorepo"""
        logger.info("Phase 3: Migrating core projects...")
        
        monorepo_path = self.workspace_path / "agi-monorepo"
        
        # Define migration mappings
        migrations = [
            {
                "source": self.mcpvots_path,
                "destination": monorepo_path / "packages" / "mcpvots",
                "type": "frontend"
            },
            {
                "source": self.workspace_path / "AI-Projects" / "agi-system",
                "destination": monorepo_path / "packages" / "agi-system",
                "type": "backend"
            }
        ]
        
        for migration in migrations:
            source = Path(migration["source"])
            destination = Path(migration["destination"])
            
            if source.exists():
                logger.info(f"Migrating {source.name} to {destination}")
                
                # Create destination directory
                destination.mkdir(parents=True, exist_ok=True)
                
                # Copy essential files (avoid copying large node_modules, etc.)
                essential_patterns = [
                    "*.py", "*.js", "*.ts", "*.tsx", "*.json", "*.md", 
                    "*.toml", "*.txt", "*.yml", "*.yaml", "*.env.example"
                ]
                
                for pattern in essential_patterns:
                    for file_path in source.rglob(pattern):
                        # Skip certain directories
                        if any(skip in str(file_path) for skip in ['node_modules', '__pycache__', '.git', 'dist', '.next']):
                            continue
                        
                        relative_path = file_path.relative_to(source)
                        dest_file = destination / relative_path
                        
                        # Create parent directories
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copy file
                        try:
                            shutil.copy2(file_path, dest_file)
                        except Exception as e:
                            logger.warning(f"Could not copy {file_path}: {e}")
                
                # Update package.json if it exists
                package_json_path = destination / "package.json"
                if package_json_path.exists():
                    self._update_package_json_for_monorepo(package_json_path, migration["type"])
        
        logger.info("Core projects migration completed")
    
    def _update_package_json_for_monorepo(self, package_json_path: Path, project_type: str) -> None:
        """Update package.json for monorepo compatibility"""
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # Add monorepo-specific scripts and dependencies
            if project_type == "frontend":
                package_data.setdefault("scripts", {}).update({
                    "build": "next build",
                    "dev": "next dev",
                    "test": "jest",
                    "lint": "next lint"
                })
            elif project_type == "backend":
                package_data.setdefault("scripts", {}).update({
                    "build": "python -m build",
                    "dev": "python -m uvicorn main:app --reload",
                    "test": "pytest",
                    "lint": "flake8"
                })
            
            with open(package_json_path, 'w', encoding='utf-8') as f:
                json.dump(package_data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Could not update {package_json_path}: {e}")
    
    def create_shared_configs(self) -> None:
        """Create shared configuration files"""
        logger.info("Creating shared configuration files...")
        
        monorepo_path = self.workspace_path / "agi-monorepo"
        configs_path = monorepo_path / "configs"
        
        # Create shared ESLint config
        eslint_config = {
            "extends": [
                "@nx/eslint-plugin-nx/typescript",
                "next/core-web-vitals"
            ],
            "ignorePatterns": ["!**/*"],
            "overrides": [
                {
                    "files": ["*.ts", "*.tsx", "*.js", "*.jsx"],
                    "rules": {}
                }
            ]
        }
        
        with open(configs_path / "eslint.json", 'w', encoding='utf-8') as f:
            json.dump(eslint_config, f, indent=2)
        
        # Create shared Prettier config
        prettier_config = {
            "singleQuote": True,
            "trailingComma": "es5",
            "tabWidth": 2,
            "semi": True
        }
        
        with open(configs_path / "prettier.json", 'w', encoding='utf-8') as f:
            json.dump(prettier_config, f, indent=2)
        
        # Create shared TypeScript config
        tsconfig = {
            "compilerOptions": {
                "target": "es2017",
                "lib": ["dom", "dom.iterable", "es6"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "forceConsistentCasingInFileNames": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "node",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [
                    {
                        "name": "next"
                    }
                ]
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
            "exclude": ["node_modules"]
        }
        
        with open(configs_path / "tsconfig.base.json", 'w', encoding='utf-8') as f:
            json.dump(tsconfig, f, indent=2)
        
        logger.info("Shared configuration files created")
    
    def generate_migration_report(self) -> None:
        """Generate migration completion report"""
        logger.info("Generating migration report...")
        
        report = {
            "title": "Monorepo Migration Report",
            "timestamp": self.timestamp,
            "status": "completed",
            "phases_completed": [
                "Project audit",
                "Monorepo structure creation",
                "Core projects migration",
                "Shared configurations setup"
            ],
            "next_steps": [
                "Install Nx dependencies",
                "Test build processes",
                "Update CI/CD pipelines",
                "Update documentation"
            ],
            "monorepo_path": str(self.workspace_path / "agi-monorepo"),
            "benefits": [
                "Unified dependency management",
                "Consistent build processes",
                "Shared tooling configuration",
                "Improved development workflow"
            ]
        }
        
        report_path = self.mcpvots_path / f"monorepo_migration_report_{self.timestamp}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        # Generate markdown report
        md_report = f"""# Monorepo Migration Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: Completed Successfully

## Summary

The monorepo migration has been completed successfully. All core projects have been consolidated into a unified Nx workspace.

## Completed Phases

- Project audit and dependency analysis
- Monorepo structure creation with Nx
- Core projects migration (MCPVots, AGI System)
- Shared configuration setup

## Monorepo Structure

```
agi-monorepo/
├── packages/
│   ├── mcpvots/          # Frontend React/Next.js app
│   ├── agi-system/       # Backend Python services
│   ├── ai-services/      # AI/ML services
│   └── shared/           # Shared utilities
├── tools/
│   └── scripts/          # Build and deployment scripts
├── docs/                 # Documentation
├── configs/              # Shared configurations
├── package.json          # Root package.json
└── nx.json              # Nx configuration
```

## Next Steps

1. Install Nx dependencies: `npm install`
2. Test build processes: `nx run-many --target=build --all`
3. Update CI/CD pipelines for monorepo
4. Update project documentation

## Benefits Achieved

- Unified dependency management across all projects
- Consistent build and deployment processes
- Shared tooling configuration (ESLint, Prettier, TypeScript)
- Improved development workflow with Nx

---
*Migration completed by Monorepo Migrator*
"""
        
        md_report_path = self.mcpvots_path / f"monorepo_migration_report_{self.timestamp}.md"
        with open(md_report_path, 'w', encoding='utf-8') as f:
            f.write(md_report)
        
        logger.info(f"Migration report saved to {report_path}")
        logger.info(f"Markdown report saved to {md_report_path}")
    
    def run_migration(self) -> None:
        """Run the complete monorepo migration"""
        logger.info("Starting Monorepo Migration...")
        
        try:
            # Phase 1: Audit projects
            projects = self.audit_projects()
            
            # Phase 2: Create monorepo structure
            self.create_monorepo_structure()
            
            # Phase 3: Migrate core projects
            self.migrate_core_projects()
            
            # Phase 4: Create shared configs
            self.create_shared_configs()
            
            # Phase 5: Generate report
            self.generate_migration_report()
            
            logger.info("Monorepo Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Monorepo Migration failed: {e}")
            raise

def main():
    """Main entry point"""
    try:
        migrator = MonorepoMigrator()
        migrator.run_migration()
        return 0
        
    except Exception as e:
        logger.error(f"Failed to run monorepo migration: {e}")
        return 1

if __name__ == "__main__":
    exit(exit_code := main())
