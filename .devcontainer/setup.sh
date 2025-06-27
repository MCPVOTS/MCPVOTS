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
echo "Happy coding! 🎊"
