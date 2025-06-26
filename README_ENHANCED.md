import os
# Enhanced MCPVots: Automated Code Improvement with Gemini CLI

## 🚀 Overview

This enhanced version of MCPVots integrates Google's Gemini CLI with advanced AI capabilities to provide automated code improvement, workspace analysis, and continuous optimization using:

- **Gemini 2.5 Pro** with 1M token context window for comprehensive codebase analysis
- **Google Search grounding** for real-time, external context and best practices
- **Trilogy AGI integration** (Ollama, OWL, Agent File, DGM, DeerFlow)
- **Enhanced Memory MCP** with knowledge graph capabilities
- **Automated code improvements** with safety validation
- **Continuous learning** and ecosystem optimization

## ✨ Key Features

### 🔍 Comprehensive Workspace Analysis
- **Full codebase context**: Leverages Gemini's 1M token window to analyze entire codebases
- **Multi-language support**: Python, JavaScript/TypeScript, configuration files, documentation
- **Architecture assessment**: Evaluates system design, patterns, and structural integrity
- **Performance analysis**: Identifies bottlenecks and optimization opportunities
- **Security scanning**: Detects vulnerabilities and recommends hardening measures

### 🌐 Google Search Grounded Recommendations
- **Real-time best practices**: Uses Google Search to ensure recommendations are current
- **Industry standards**: Grounds advice in latest industry standards and emerging practices
- **Technology updates**: Stays current with framework updates and security patches
- **Community insights**: Incorporates community-driven best practices and solutions

### ⚡ Automated Code Improvements
- **Safe automatic fixes**: Applies low-risk improvements automatically
- **Approval-required changes**: Flags major changes for human review
- **Implementation scripts**: Generates executable scripts for complex improvements
- **Progress tracking**: Monitors improvement application and effectiveness

### 🧠 Continuous Learning System
- **Change detection**: Monitors workspace for significant changes
- **Incremental analysis**: Focuses on changed files to maintain efficiency
- **Knowledge graph updates**: Continuously enriches the knowledge base
- **Feedback loops**: Learns from improvement outcomes to refine future recommendations

## 🛠 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd MCPVots
   python setup_enhanced_ecosystem.py quick-start
   ```

2. **Set your API key**:
   ```bash
   # Add to .env file (created during setup)
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Launch the ecosystem**:
   ```bash
   python enhanced_ecosystem_orchestrator.py
   ```

## 📊 Usage Examples

### Basic Workspace Analysis
```python
from gemini_automated_code_improver import GeminiAutomatedCodeImprover

improver = GeminiAutomatedCodeImprover("/path/to/your/project")
analysis = await improver.perform_comprehensive_workspace_analysis()
```

### Automated Improvements
```python
# Generate improvements based on analysis
improvements = await improver.generate_automated_improvements(analysis)

# Apply safe improvements automatically
results = await improver.apply_safe_improvements(improvements)
```

### Testing the System
```bash
# Run comprehensive tests
python test_gemini_code_improver.py

# Quick demo
python test_gemini_code_improver.py demo
```

## 🏗 Architecture

### Core Components

1. **Enhanced Gemini CLI Server** (`servers/enhanced_gemini_cli_server.py`)
   - WebSocket MCP server for Gemini CLI integration
   - Google Search grounding capabilities
   - Workspace automation features

2. **Automated Code Improver** (`gemini_automated_code_improver.py`)
   - Comprehensive workspace analysis engine
   - Improvement generation and application
   - Safety validation and progress tracking

3. **Enhanced Memory System** (`enhanced_memory_knowledge_system_v2.py`)
   - Knowledge graph integration
   - Continuous learning capabilities
   - Memory MCP synchronization

4. **Ecosystem Orchestrator** (`enhanced_ecosystem_orchestrator.py`)
   - Service coordination and health monitoring
   - Automation cycle management
   - Real-time optimization

### Service Architecture
```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│   Gemini CLI    │────│  Code Improvement    │────│  Memory MCP     │
│   + Search      │    │     Engine           │    │ + Knowledge     │
│   Grounding     │    │                      │    │   Graph         │
└─────────────────┘    └──────────────────────┘    └─────────────────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
              ┌────────────────────────────────────────┐
              │        Ecosystem Orchestrator          │
              │     (Health, Automation, Learning)     │
              └────────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│  Trilogy AGI    │    │      Frontend        │    │   Monitoring    │
│  (Ollama/OWL/   │    │   (React/Next.js)    │    │  & Analytics    │
│   Agent/DGM)    │    │                      │    │                 │
└─────────────────┘    └──────────────────────┘    └─────────────────┘
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional  
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Service Configuration
MEMORY_MCP_HOST=localhost
MEMORY_MCP_PORT=8020
GEMINI_CLI_HOST=localhost
GEMINI_CLI_PORT=8015

# Feature Flags
ENABLE_GOOGLE_SEARCH=true
ENABLE_AUTO_IMPROVEMENTS=true
ENABLE_CONTINUOUS_LEARNING=true
```

### MCP Configuration (`mcp-config.json`)
```json
{
  "servers": {
    "enhanced-gemini-cli": {
      "command": "python",
      "args": ["servers/enhanced_gemini_cli_server.py"]
    },
    "memory-mcp-primary": {
      "command": "python",
      "args": ["servers/memory_mcp_server.py", "--port", "8020"]
    }
  },
  "features": {
    "google_search_grounding": true,
    "trilogy_agi_integration": true,
    "automated_code_improvements": true,
    "continuous_learning": true
  }
}
```

## 📈 Monitoring & Health

### Health Checks
The system provides comprehensive health monitoring:

```bash
# Get ecosystem status
curl http://localhost:8015/health

# Check service health
python -c "
import asyncio
from enhanced_ecosystem_orchestrator import EnhancedMCPVotsOrchestrator
async def check():
    orch = EnhancedMCPVotsOrchestrator()
    status = await orch.get_ecosystem_status()
    print(status)
asyncio.run(check())
"
```

### Monitoring Dashboard
- Real-time service health
- Automation cycle status
- Improvement tracking
- Learning progress metrics

## 🔒 Security & Safety

### Safety Features
- **Improvement validation**: Multi-layer safety checks before applying changes
- **Approval workflows**: Major changes require explicit approval
- **Rollback capabilities**: Track and reverse changes if needed
- **Sandboxed execution**: Improvements run in controlled environments

### Security Measures
- **API key encryption**: Secure storage of API credentials
- **Access controls**: Role-based access to different system components
- **Audit logging**: Comprehensive logging of all system activities
- **Vulnerability scanning**: Regular security assessments

## 🧪 Testing

### Test Suite
```bash
# Run all tests
python test_gemini_code_improver.py

# Run specific test categories
python test_gemini_code_improver.py --category=improvements
python test_gemini_code_improver.py --category=memory
python test_gemini_code_improver.py --category=search
```

### Test Coverage
- Service connectivity
- Workspace analysis accuracy
- Improvement generation quality
- Safety validation effectiveness
- Memory integration functionality

## 📚 Advanced Usage

### Custom Analysis Types
```python
# Performance-focused analysis
analysis = await improver.analyze_workspace_with_context("performance")

# Security-focused analysis  
analysis = await improver.analyze_workspace_with_context("security")

# Architecture analysis
analysis = await improver.analyze_workspace_with_context("architecture")
```

### Workflow Automation
```python
# Automate specific workflow tasks
result = await improver.automate_workflow_task(
    "Optimize database queries in user service",
    context={"focus": "performance", "components": ["database", "api"]}
)
```

### Knowledge Graph Integration
```python
# Query knowledge graph
knowledge = await memory_system.query_knowledge_graph(
    "What are the best practices for React performance optimization?"
)

# Add insights to knowledge graph
await memory_system.add_learning_insight(
    "react_optimization",
    "Implemented code splitting which improved load time by 40%"
)
```

## 🔧 n8n Workflow Automation Integration

### Visual Workflow Automation
- **n8n Integration**: Complete visual workflow automation with custom AGI nodes
- **Custom AGI Nodes**: Direct integration with Gemini, Trilogy, Memory, and Ollama
- **Automated Triggers**: Webhook, schedule, and event-based workflow triggers
- **Visual Designer**: Drag-and-drop workflow creation with AGI components

### AGI-Powered Workflows
- **Code Analysis Pipelines**: Automated code review and quality assessment
- **Continuous Learning**: Scheduled AI learning and knowledge integration
- **Deployment Automation**: AI-validated automated deployment pipelines
- **Multi-Modal Processing**: Complex data processing with multiple AGI services

### Quick n8n Setup
```bash
# Complete n8n + AGI ecosystem setup
npm run n8n:setup

# Quick start for development
npm run n8n:quick

# Open n8n dashboard
npm run n8n:dashboard

# Test integration
npm run n8n:test
```

**n8n Dashboard**: http://localhost:5678 (after setup)

## 🚀 Enhanced GitHub Actions with AGI Integration

### Intelligent CI/CD Pipelines

Our GitHub Actions workflows have been enhanced with comprehensive AGI integration, creating the first production-ready AI-driven CI/CD pipeline that continuously learns and improves.

#### Key Features

- **AGI-Powered Code Analysis**: Multi-model AI analysis combining Gemini 2.5 Pro, Trilogy AGI, and traditional tools
- **Intelligent Deployment Decisions**: AGI evaluates code quality, security, and performance to make smart deployment decisions
- **Automated Optimization**: System continuously optimizes dependencies, security, and performance using AI insights
- **Continuous Learning**: Each workflow execution feeds insights back to the AGI knowledge base

#### Enhanced Workflows

1. **Primary AGI-Enhanced CI/CD** (`agi-enhanced-ci.yml`)
   - Comprehensive AGI ecosystem initialization
   - Multi-layer AI code analysis and security scanning
   - AGI-enhanced testing with automatic test generation
   - Intelligent deployment decisions with monitoring
   - Continuous learning and improvement

2. **AGI Auto-Update System** (`agi-auto-update.yml`)
   - Health-driven dependency updates
   - Intelligent security vulnerability patching
   - AI-powered performance optimizations
   - AGI model self-improvement
   - Strategic update planning based on AI analysis

3. **Simplified AGI Integration** (`agi-enhanced-workflow.yml`)
   - Streamlined AGI integration for basic projects
   - Essential AI-enhanced analysis and testing
   - Smart deployment decisions
   - Basic continuous learning

#### AGI Decision Making

The workflows use intelligent decision matrices where AGI evaluates:

| Component | Criteria | AGI Action |
|-----------|----------|------------|
| **Code Quality** | Security score > 70, Performance > 80 | Auto-deploy or enhance |
| **Risk Assessment** | Change impact, test coverage, historical success | Proceed, monitor, or block |
| **Optimization** | Dependency health, performance metrics | Strategic updates |
| **Learning** | Outcome analysis, pattern recognition | Knowledge base updates |

#### Quick Start

```bash
# Enhanced workflows are automatically available after setup
# Trigger AGI-enhanced CI/CD on push to main/develop
git push origin main

# Manual workflow with AGI mode selection
gh workflow run agi-enhanced-ci.yml --ref main -f mode=intelligent

# AGI auto-optimization (scheduled, or manual)
gh workflow run agi-auto-update.yml --ref main -f agi_mode=intelligent
```

#### Monitoring AGI Decisions

- **Workflow Reports**: Comprehensive AGI decision analysis in GitHub Actions summaries
- **Decision Transparency**: Full audit trail of AGI decisions and rationale
- **Learning Insights**: What the AGI learned from each workflow execution
- **Performance Metrics**: Track AGI decision accuracy and improvement over time

See [GITHUB_ACTIONS_AGI_INTEGRATION.md](./GITHUB_ACTIONS_AGI_INTEGRATION.md) for complete documentation.

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes with proper testing
4. **Submit** a pull request with detailed description

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests before committing
python -m pytest tests/

# Run linting
python -m flake8 .
python -m black .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google for Gemini CLI and API
- Trilogy AGI team for AI orchestration capabilities
- MCP community for protocol specifications
- Contributors and testers

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [Full Documentation](./docs/)

---

**🎉 Ready to revolutionize your development workflow with AI-powered code improvements!**
