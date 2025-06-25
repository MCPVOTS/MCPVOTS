# MCPVots Integration System

## Overview

The MCPVots Integration System combines the Enhanced Gemini CLI Server with Claude's MCP tools to create a powerful AI-driven development and automation platform.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCPVots Integrated System                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐         ┌─────────────────────────────┐  │
│  │  Enhanced Gemini │         │      MCP Tools Suite        │  │
│  │   CLI Server     │◄────────┤                             │  │
│  │                  │         │  • GitHub Integration       │  │
│  │  • Gemini 2.5    │         │  • FileSystem Operations   │  │
│  │  • Web Search    │         │  • Solana Blockchain       │  │
│  │  • Workspace     │         │  • Memory/Knowledge Graph  │  │
│  │    Analysis      │         │  • Browser Automation      │  │
│  │                  │         │  • HuggingFace AI          │  │
│  └─────────────────┘         └─────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Integration Patterns                        │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │  • Code Review Automation                               │  │
│  │  • Workspace Optimization                               │  │
│  │  • Blockchain Integration                               │  │
│  │  • AI Model Enhancement                                 │  │
│  │  • Complex Workflow Orchestration                       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. **Intelligent Code Review Automation**
- Combines GitHub API with Gemini's code analysis
- Historical context from knowledge graph
- Automated PR feedback and suggestions

### 2. **Workspace Analysis & Optimization**
- FileSystem tools for structure analysis
- Gemini-powered code quality assessment
- Automated refactoring suggestions

### 3. **Blockchain Integration**
- Solana blockchain connectivity
- Smart contract generation with Gemini
- DeFi protocol monitoring

### 4. **AI-Enhanced Development**
- HuggingFace model integration
- Trilogy AGI capabilities
- Custom model fine-tuning

### 5. **Knowledge Graph Memory**
- Persistent context storage
- Learning from past interactions
- Pattern recognition

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mcpvots.git
cd mcpvots

# Install dependencies
pip install -r requirements.txt

# Start the Enhanced Gemini CLI Server
python gemini_cli_server_enhanced.py

# Run the integration system
python integrations/mcp_tools_integration.py
```

## Usage Examples

### 1. Repository Analysis
```python
system = MCPVotsIntegratedSystem()
await system.initialize()

# Analyze and optimize a repository
results = await system.analyze_and_optimize_repository("path/to/repo")
```

### 2. Intelligent PR Review
```python
# Create an AI-powered PR review
review = await system.create_intelligent_pr_review(
    owner="username",
    repo="repository",
    pr_number=123
)
```

### 3. Complex Workflow Execution
```python
# Execute a predefined workflow
result = await system.execute_complex_workflow(
    "code_review_automation",
    {"repository": "myrepo", "branch": "main"}
)
```

## Integration Patterns

### Code Review Automation
- **Tools**: GitHub, FileSystem, Memory
- **Model**: Gemini 2.5 Pro
- **Workflow**: Analyzes PRs with historical context

### Workspace Optimization
- **Tools**: FileSystem, Memory, Browser
- **Model**: Gemini 2.5 Pro
- **Workflow**: Optimizes project structure and code quality

### Blockchain Integration
- **Tools**: Solana, Memory, FileSystem
- **Model**: Gemini 1.5 Pro
- **Workflow**: Integrates blockchain features into applications

### AI Model Enhancement
- **Tools**: HuggingFace, Memory, FileSystem
- **Model**: Gemini 2.5 Pro
- **Workflow**: Enhances AI capabilities with custom models

## API Reference

### Core Methods

#### `analyze_and_optimize_repository(repo_path: str)`
Performs comprehensive repository analysis including:
- Structure analysis
- Code quality assessment
- GitHub integration status
- Optimization recommendations
- Automation workflow creation

#### `create_intelligent_pr_review(owner: str, repo: str, pr_number: int)`
Creates AI-powered PR reviews with:
- File change analysis
- Historical context lookup
- Gemini-generated feedback
- Automated GitHub posting

#### `deploy_ai_enhanced_feature(feature_spec: Dict[str, Any])`
Deploys AI-enhanced features using:
- HuggingFace model selection
- Gemini code generation
- Trilogy AGI integration
- Automated deployment

#### `automate_blockchain_integration(integration_spec: Dict[str, Any])`
Automates blockchain integration with:
- Requirement analysis
- Smart contract generation
- Integration layer creation
- Testnet deployment

## Configuration

Create a `config.json` file:

```json
{
    "gemini": {
        "ws_url": "ws://localhost:8015",
        "api_key": "your_gemini_api_key"
    },
    "github": {
        "token": "your_github_token"
    },
    "solana": {
        "network": "devnet",
        "rpc_url": "https://api.devnet.solana.com"
    },
    "huggingface": {
        "token": "your_hf_token"
    }
}
```

## Best Practices

1. **Error Handling**: Always implement proper error handling for tool failures
2. **Rate Limiting**: Respect API rate limits for external services
3. **Caching**: Use the memory/knowledge graph for caching expensive operations
4. **Security**: Never commit sensitive API keys or tokens
5. **Testing**: Test workflows in isolated environments first

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [github.com/yourusername/mcpvots/issues](https://github.com/yourusername/mcpvots/issues)
- Documentation: [mcpvots.readthedocs.io](https://mcpvots.readthedocs.io)
