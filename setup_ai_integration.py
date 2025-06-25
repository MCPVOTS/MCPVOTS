#!/usr/bin/env python3
"""
MCPVots Repository Setup for Claude Opus 4
Comprehensive setup script for AI-driven development integration
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

def run_command(command: str, capture_output: bool = True) -> str:
    """Run a shell command and return output"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=True)
            return ""
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Error: {e.stderr if capture_output else e}")
        sys.exit(1)

def check_prerequisites() -> Dict[str, bool]:
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    requirements = {
        "git": False,
        "node": False,
        "npm": False,
        "python": False,
        "gh": False  # GitHub CLI
    }
    
    for tool in requirements:
        try:
            if tool == "gh":
                subprocess.run(["gh", "--version"], capture_output=True, check=True)
            else:
                subprocess.run([tool, "--version"], capture_output=True, check=True)
            requirements[tool] = True
            print(f"✅ {tool} is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {tool} is not installed")
    
    return requirements

def setup_git_configuration():
    """Configure Git for AI operations"""
    print("🔧 Setting up Git configuration for AI operations...")
    
    # Copy AI git configuration
    if Path(".gitconfig.ai").exists():
        print("✅ AI Git configuration found")
        
        # Set up git hooks
        hooks_dir = Path(".githooks")
        if hooks_dir.exists():
            run_command("git config core.hooksPath .githooks")
            
            # Make hooks executable (Unix-like systems)
            if os.name != 'nt':  # Not Windows
                for hook_file in hooks_dir.glob("*"):
                    if hook_file.is_file():
                        os.chmod(hook_file, 0o755)
            
            print("✅ Git hooks configured")
        
        # Set commit template
        if Path(".gitmessage").exists():
            run_command("git config commit.template .gitmessage")
            print("✅ Commit template configured")
    
    # Configure AI-specific settings
    run_command("git config ai.enabled true")
    run_command("git config ai.actor 'Claude Opus 4'")
    print("✅ AI Git settings configured")

def setup_github_integration():
    """Set up GitHub integration"""
    print("🐙 Setting up GitHub integration...")
    
    try:
        # Check if GitHub CLI is authenticated
        run_command("gh auth status")
        print("✅ GitHub CLI is authenticated")
        
        # Set up GitHub-specific configurations
        repo_info = run_command("gh repo view --json owner,name")
        repo_data = json.loads(repo_info)
        
        print(f"✅ Repository: {repo_data['owner']['login']}/{repo_data['name']}")
        
        # Enable GitHub Actions
        try:
            run_command("gh api repos/{owner}/{repo}/actions/permissions -X PUT -F enabled=true")
            print("✅ GitHub Actions enabled")
        except:
            print("⚠️  Could not enable GitHub Actions (may already be enabled)")
        
    except:
        print("⚠️  GitHub CLI not authenticated. Run 'gh auth login' to authenticate.")

def install_dependencies():
    """Install project dependencies"""
    print("📦 Installing project dependencies...")
    
    # Install Node.js dependencies
    if Path("package.json").exists():
        print("Installing npm dependencies...")
        run_command("npm install", capture_output=False)
        print("✅ npm dependencies installed")
    
    # Install Python dependencies for AI operations
    python_deps = [
        "aiohttp",
        "pyyaml",
        "requests"
    ]
    
    print("Installing Python dependencies for AI operations...")
    for dep in python_deps:
        try:
            run_command(f"pip install {dep}", capture_output=False)
        except:
            print(f"⚠️  Could not install {dep}")
    
    print("✅ Python dependencies installed")

def setup_environment_files():
    """Set up environment configuration files"""
    print("🌍 Setting up environment configuration...")
    
    # Create .env template if it doesn't exist
    env_template = Path(".env.template")
    env_file = Path(".env.local")
    
    if env_template.exists() and not env_file.exists():
        env_content = env_template.read_text()
        env_file.write_text(env_content)
        print("✅ Environment file created from template")
    
    # Set up AI configuration
    ai_config = Path(".ai-config")
    if ai_config.exists():
        print("✅ AI configuration found")
    else:
        print("⚠️  AI configuration not found - using defaults")

def setup_vscode_integration():
    """Set up VS Code integration"""
    print("🔧 Setting up VS Code integration...")
    
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    # VS Code settings for AI development
    vscode_settings = {
        "git.enableSmartCommit": True,
        "git.confirmSync": False,
        "git.autofetch": True,
        "git.autorefresh": True,
        "terminal.integrated.defaultProfile.windows": "PowerShell",
        "terminal.integrated.defaultProfile.linux": "bash",
        "terminal.integrated.defaultProfile.osx": "zsh",
        "editor.formatOnSave": True,
        "editor.codeActionsOnSave": {
            "source.fixAll.eslint": True
        },
        "ai.development.enabled": True,
        "ai.development.actor": "Claude Opus 4"
    }
    
    settings_file = vscode_dir / "settings.json"
    if not settings_file.exists():
        settings_file.write_text(json.dumps(vscode_settings, indent=2))
        print("✅ VS Code settings configured")
    
    # VS Code tasks for AI operations
    tasks = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "AI: Run Operations Manager",
                "type": "shell",
                "command": "python",
                "args": ["ai_operations_manager.py"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared"
                }
            },
            {
                "label": "AI: Generate Status Report",
                "type": "shell",
                "command": "python",
                "args": ["-c", "import asyncio; from ai_operations_manager import AIOperationsManager; asyncio.run(AIOperationsManager().create_ai_status_report())"],
                "group": "build"
            },
            {
                "label": "AI: Health Check",
                "type": "shell",
                "command": "python",
                "args": ["-c", "import asyncio; from ai_operations_manager import AIOperationsManager; asyncio.run(AIOperationsManager().monitor_system_health())"],
                "group": "test"
            }
        ]
    }
    
    tasks_file = vscode_dir / "tasks.json"
    if not tasks_file.exists():
        tasks_file.write_text(json.dumps(tasks, indent=2))
        print("✅ VS Code tasks configured")

def validate_setup():
    """Validate the setup"""
    print("🔍 Validating setup...")
    
    validations = []
    
    # Check Git configuration
    try:
        ai_enabled = run_command("git config ai.enabled")
        validations.append(("Git AI configuration", ai_enabled == "true"))
    except:
        validations.append(("Git AI configuration", False))
    
    # Check if hooks are working
    hooks_path = run_command("git config core.hooksPath") if os.name != 'nt' else ""
    validations.append(("Git hooks", hooks_path == ".githooks"))
    
    # Check npm dependencies
    validations.append(("npm dependencies", Path("node_modules").exists()))
    
    # Check Python dependencies
    try:
        import aiohttp
        validations.append(("Python dependencies", True))
    except ImportError:
        validations.append(("Python dependencies", False))
    
    # Check AI configuration
    validations.append(("AI configuration", Path(".ai-config").exists()))
    
    # Check GitHub Actions
    validations.append(("GitHub Actions", Path(".github/workflows").exists()))
    
    print("\n📋 Setup Validation Results:")
    all_good = True
    for name, status in validations:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {name}")
        if not status:
            all_good = False
    
    if all_good:
        print("\n🎉 Setup completed successfully!")
        print("Repository is ready for Claude Opus 4 operations.")
    else:
        print("\n⚠️  Some setup items need attention.")
    
    return all_good

def create_ai_status_dashboard():
    """Create a simple AI status dashboard"""
    print("📊 Creating AI status dashboard...")
    
    dashboard_content = """# 🤖 Claude Opus 4 Integration Status

This repository is configured for AI-driven development with Claude Opus 4.

## Quick Status Check

Run the following commands to check AI system status:

```bash
# Check AI configuration
git config --get ai.enabled

# Run AI operations manager
python ai_operations_manager.py

# Check repository health
python -c "import asyncio; from ai_operations_manager import AIOperationsManager; print(asyncio.run(AIOperationsManager().assess_repository_state()))"

# View AI commit history
git ai-log

# Get AI statistics
git ai-stats
```

## Available AI Operations

- 🔄 Automated dependency updates
- 🔒 Security vulnerability scanning and fixes
- 📊 System health monitoring
- 📚 Documentation updates
- ⚡ Performance optimizations
- 🧪 Automated testing
- 🚀 Deployment automation

## GitHub Actions

- AI Development Workflow: `.github/workflows/ai-development.yml`
- AI Auto-Update: `.github/workflows/ai-auto-update.yml`

## Configuration Files

- AI Config: `.ai-config`
- Git Config: `.gitconfig.ai`
- Commit Template: `.gitmessage`
- Git Hooks: `.githooks/`

## Monitoring

Check the AI operations log:
```bash
tail -f ai-operations.log
```

---
*Last updated: {timestamp}*
""".format(timestamp=run_command("date"))
    
    Path("AI_STATUS.md").write_text(dashboard_content)
    print("✅ AI status dashboard created")

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup MCPVots for Claude Opus 4 integration")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-github", action="store_true", help="Skip GitHub integration")
    parser.add_argument("--validate-only", action="store_true", help="Only run validation")
    
    args = parser.parse_args()
    
    print("🤖 MCPVots AI Integration Setup")
    print("=" * 40)
    
    if args.validate_only:
        validate_setup()
        return
    
    # Check prerequisites
    prereqs = check_prerequisites()
    missing_prereqs = [tool for tool, installed in prereqs.items() if not installed]
    
    if missing_prereqs:
        print(f"\n❌ Missing prerequisites: {', '.join(missing_prereqs)}")
        print("Please install missing tools and run setup again.")
        sys.exit(1)
    
    # Run setup steps
    try:
        setup_git_configuration()
        
        if not args.skip_github:
            setup_github_integration()
        
        if not args.skip_deps:
            install_dependencies()
        
        setup_environment_files()
        setup_vscode_integration()
        create_ai_status_dashboard()
        
        # Final validation
        if validate_setup():
            print("\n🎉 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Review AI configuration in .ai-config")
            print("2. Set up GitHub token if needed: gh auth login")
            print("3. Run: python ai_operations_manager.py")
            print("4. Check AI status: cat AI_STATUS.md")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
