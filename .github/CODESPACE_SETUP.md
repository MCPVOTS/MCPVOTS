# MCPVots GitHub Codespaces Setup Guide

## 🚀 Quick Launch

### Option 1: One-Click Launch
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=clean-main&repo=kabrony/MCPVots)

### Option 2: From Repository
1. Go to [MCPVots Repository](https://github.com/kabrony/MCPVots)
2. Click the green **"Code"** button
3. Select **"Codespaces"** tab
4. Click **"Create codespace on clean-main"**

### Option 3: GitHub CLI
```bash
gh codespace create --repo kabrony/MCPVots --branch clean-main
gh codespace code
```

## 🏗️ Environment Details

### Pre-installed Tools & Languages
- **Node.js 18** with npm, yarn, pnpm
- **Python 3.11** with virtual environment
- **Git** with GitHub CLI
- **Docker** for containerization
- **Zsh** with Oh My Zsh configuration

### VS Code Extensions Included
- **Python Development**: Python, Pylint, Black, isort, Ruff
- **JavaScript/TypeScript**: TypeScript, Prettier, ESLint
- **AI Development**: GitHub Copilot, Copilot Chat
- **Web Development**: Tailwind CSS, Auto Rename Tag
- **Collaboration**: Live Share, Remote Repositories
- **Containers**: Docker extension

### Advanced AI Module Support
- **Quantum Computing**: Qiskit pre-installed
- **Machine Learning**: PyTorch, Transformers, scikit-learn
- **Trading**: Nautilus Trader, ccxt, yfinance
- **Graph Processing**: NetworkX for knowledge graphs
- **Async Programming**: aiohttp, asyncio for real-time operations

## 🎯 Quick Start Commands

### After Codespace Launch
```bash
# View the setup completion
# (Setup runs automatically on first launch)

# Start the main development server
npm run dev

# Test advanced AI modules
npm run ai:modules-test

# Run full ecosystem
npm run ecosystem:run

# Setup n8n workflow integration
npm run n8n:setup
```

### Individual AI Module Testing
```bash
# Test quantum strategy module
npm run ai:quantum-demo

# Test neural meta-learning
npm run ai:neural-demo

# Test distributed swarm
npm run ai:swarm-demo

# Test temporal knowledge graph
npm run ai:temporal-demo

# Test self-modifying code
npm run ai:code-demo

# Test autonomous orchestrator
npm run ai:orchestrator-demo
```

## 🔧 Development Workflow

### 1. Frontend Development
- **Main Dashboard**: `http://localhost:3000` (Next.js)
- **Vite Development**: `http://localhost:5173`
- **Hot reload** enabled for both React and Next.js

### 2. Backend Services
All AGI services auto-forward on these ports:
- **8000-8008**: Core AGI services
- **3001-3006**: MCP protocol servers
- **5678**: n8n workflow dashboard

### 3. Database & Storage
- **SQLite**: For local development and AI module storage
- **Redis**: Available for caching and real-time features
- **PostgreSQL**: Client tools pre-installed

## 📊 Port Forwarding

### Automatically Forwarded Ports
| Port | Service | Description |
|------|---------|-------------|
| 3000 | Next.js | Main frontend dashboard |
| 5173 | Vite | Development server |
| 8000-8008 | AGI Services | Core AI modules |
| 3001-3006 | MCP Servers | Protocol integration |
| 5678 | n8n | Workflow automation |

### Access Your Applications
- All ports are automatically forwarded with HTTPS
- Click on the **"Ports"** tab in VS Code to see active services
- Services are accessible via `https://<codespace-name>-<port>.app.github.dev`

## 🧠 Advanced AI Features

### Pre-configured AI Modules
1. **Quantum Strategy Evolution** - Quantum-inspired trading algorithms
2. **Neural Meta-Learning** - Few-shot learning systems
3. **Distributed Trading Swarm** - Multi-agent coordination
4. **Temporal Knowledge Graph** - Causal reasoning engine
5. **Self-Modifying Code** - Autonomous code generation
6. **Autonomous Orchestrator** - System coordination

### AI Development Tools
- **Jupyter Lab**: `jupyter lab --allow-root`
- **TensorBoard**: For ML experiment tracking
- **Model Context Protocol**: Pre-configured MCP servers
- **Real-time Data**: WebSocket support for live trading data

## 🔍 Troubleshooting

### Common Issues

#### Slow Initial Setup
- **First launch** takes 3-5 minutes for environment setup
- **Subsequent launches** are much faster (< 30 seconds)
- Check the terminal for setup progress

#### Port Not Accessible
```bash
# Check if service is running
ps aux | grep <service_name>

# Restart a specific service
npm run <service_script>

# Check port usage
netstat -tulpn | grep <port>
```

#### Python Environment Issues
```bash
# Activate virtual environment
source /opt/venv/bin/activate

# Check Python path
which python

# Reinstall packages if needed
pip install -r requirements.txt
```

#### Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version
```

### Getting Help
```bash
# View environment info
cat .devcontainer/setup.sh

# Check system resources
htop

# View logs
tail -f logs/*.log

# Test all AI modules
npm run ai:modules-test
```

## 💡 Pro Tips

### 1. Prebuilds for Faster Launch
- Enable **prebuilds** in repository settings
- Reduces launch time from minutes to seconds
- Automatically rebuilds on push to main branch

### 2. Persistent Storage
- Use `/workspaces/<repo>` for persistent files
- Home directory (`~`) is preserved between sessions
- Database files are automatically persistent

### 3. Secrets Management
- Add API keys in repository **Secrets**
- Access via `process.env.SECRET_NAME` in code
- Never commit secrets to the repository

### 4. Resource Management
- **2-core machine**: Free tier, good for development
- **4-core machine**: Better for AI training
- **8+ core machine**: For heavy computational workloads

### 5. Multiple Codespaces
- Can run multiple codespaces simultaneously
- Use different branches for different features
- Share codespaces with team members

## 🚀 Advanced Features

### Custom Development Container
```bash
# Rebuild container with changes
Ctrl+Shift+P → "Codespaces: Rebuild Container"

# Or from command line
gh codespace rebuild
```

### VS Code Settings Sync
- Settings are automatically synced if enabled
- Extensions install automatically
- GitHub Copilot works out of the box

### GPU Support (Optional)
```json
// In devcontainer.json for ML workloads
"hostRequirements": {
  "gpu": true
}
```

## 📚 Documentation Links

- **MCPVots Main Docs**: [README.md](../README.md)
- **AI Integration Guide**: [INTEGRATION_GUIDE.md](../advanced_ai_modules/INTEGRATION_GUIDE.md)
- **Cleanup Summary**: [CLEANUP_COMPLETE.md](../CLEANUP_COMPLETE.md)
- **GitHub Codespaces Docs**: [docs.github.com/codespaces](https://docs.github.com/en/codespaces)

## 🎊 Ready to Code!

Your MCPVots Codespace includes everything needed for advanced AI trading development:
- ✅ Full development environment
- ✅ All dependencies pre-installed  
- ✅ AI modules ready to test
- ✅ Documentation accessible
- ✅ GitHub Copilot enabled
- ✅ Real-time collaboration ready

Happy coding! 🚀
