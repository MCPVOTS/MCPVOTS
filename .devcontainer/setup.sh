#!/bin/bash

# MCPVots Advanced AI Development Environment Setup Script
echo "🚀 Setting up MCPVots Advanced AI Development Environment..."

# Activate virtual environment
source /opt/venv/bin/activate

# Update pip
pip install --upgrade pip

# Install project dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Install Python dependencies for advanced AI modules
echo "🧠 Installing Advanced AI module dependencies..."
pip install -r requirements.txt 2>/dev/null || echo "⚠️ requirements.txt not found, using default packages"

# Install additional AI/ML packages if not already installed
echo "🤖 Installing additional AI/ML packages..."
pip install --no-cache-dir \
    torch \
    transformers \
    numpy \
    pandas \
    scikit-learn \
    networkx \
    asyncio \
    aiohttp \
    fastapi \
    uvicorn \
    sqlalchemy \
    pytest \
    pytest-asyncio \
    black \
    isort \
    pylint

# Set up pre-commit hooks (if available)
echo "🔧 Setting up development tools..."
npm run type-check 2>/dev/null || echo "⚠️ TypeScript check skipped"

# Create necessary directories
mkdir -p logs
mkdir -p data
mkdir -p temp

# Set proper permissions
chmod +x .devcontainer/setup.sh 2>/dev/null || true

# Initialize git hooks if needed
git config --global --add safe.directory /workspace

# Create usage tracking script
echo "📊 Creating usage tracking system..."
cat > ~/monitor_usage.sh << 'EOF'
#!/bin/bash
echo "📊 MCPVots Codespace Usage Monitor"
echo "================================="
echo "💻 Machine: ${CODESPACE_MACHINE:-'2-core'}"
if [ -f ~/codespace_usage.log ]; then
    echo "⏰ Started: $(head -1 ~/codespace_usage.log)"
    START_TIME=$(date -d "$(head -1 ~/codespace_usage.log | cut -d: -f2-)" +%s 2>/dev/null || echo $(date +%s))
    CURRENT_TIME=$(date +%s)
    HOURS=$(echo "scale=2; ($CURRENT_TIME - $START_TIME) / 3600" | bc -l 2>/dev/null || echo "0.0")
    echo "🕒 Session: ${HOURS} hours"
    echo "💰 Cost (after free): \$$(echo "$HOURS * 0.18" | bc -l)"
else
    echo "⚠️ No usage log found"
fi
echo "📈 Pro quota: 180 core-hours/month (90 hours on 2-core)"
EOF

chmod +x ~/monitor_usage.sh
echo "alias monitor='~/monitor_usage.sh'" >> ~/.bashrc
echo "alias monitor='~/monitor_usage.sh'" >> ~/.zshrc

# Display environment information
echo "📊 Environment Information:"
echo "  Node.js: $(node --version)"
echo "  npm: $(npm --version)"
echo "  Python: $(python --version)"
echo "  pip: $(pip --version)"

echo "✅ MCPVots Development Environment Setup Complete!"
echo ""
echo "🎯 Quick Start Commands:"
echo "  npm run dev              # Start frontend development server"
echo "  npm run ai:modules-test  # Test advanced AI modules"
echo "  npm run ecosystem:run    # Start full ecosystem"
echo "  npm run n8n:setup        # Setup n8n integration"
echo ""
echo "📚 Documentation:"
echo "  npm run ai:integration-guide  # Open AI modules integration guide"
echo "  cat README.md                 # View main documentation"
echo ""
echo "🔧 Development Tools:"
echo "  All VS Code extensions are pre-installed"
echo "  GitHub Copilot is available"
echo "  Python environment is activated"
echo "  All ports are forwarded automatically"
echo ""
echo "💡 GitHub Pro Tips:"
echo "  Your Pro account includes 180 core-hours/month"
echo "  2-core machine = 90 hours/month (RECOMMENDED)"
echo "  Auto-stop after 30min idle saves your quota"
echo "  Type 'monitor' to check your usage anytime"
echo ""
echo "⚡ Quick Commands:"
echo "  npm run ai:modules-test  # Test advanced AI modules"
echo "  npm run dev              # Start development server"
echo "  npm run ecosystem:run    # Start full ecosystem"
echo "  monitor                  # Check Codespace usage"
echo ""
echo "Happy coding! 🎊"
