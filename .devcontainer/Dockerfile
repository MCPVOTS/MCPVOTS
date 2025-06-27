FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=development

# Update system and install basic dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    vim \
    nano \
    htop \
    tree \
    jq \
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install global npm packages
RUN npm install -g \
    yarn \
    pnpm \
    @next/bundle-analyzer \
    typescript \
    tsx \
    eslint \
    prettier \
    nodemon \
    pm2

# Install Python packages for advanced AI modules
RUN pip3 install --no-cache-dir \
    # Core ML/AI packages
    torch \
    torchvision \
    transformers \
    numpy \
    pandas \
    scikit-learn \
    scipy \
    matplotlib \
    seaborn \
    plotly \
    # Trading and financial packages
    ccxt \
    yfinance \
    quantlib \
    ta-lib \
    # Network and async packages
    aiohttp \
    asyncio \
    websockets \
    requests \
    # Database packages
    sqlite3 \
    sqlalchemy \
    redis \
    # MCP and protocol packages
    fastapi \
    uvicorn \
    pydantic \
    # Quantum computing simulation
    qiskit \
    # Graph and knowledge base packages
    networkx \
    py2neo \
    # Development and testing
    pytest \
    pytest-asyncio \
    black \
    isort \
    pylint \
    mypy \
    # Jupyter and notebook packages
    jupyter \
    jupyterlab \
    ipykernel

# Install Rust (for some Python packages that require compilation)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install additional tools for MCP development
RUN curl -fsSL https://get.docker.com | sh

# Install specialized trading tools
RUN pip3 install --no-cache-dir \
    nautilus_trader \
    backtrader \
    zipline-reloaded \
    pyfolio \
    empyrical

# Create workspace directory
WORKDIR /workspace

# Create Python virtual environment for the project
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install additional development tools
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Set up user permissions
RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid vscode --shell /bin/bash --create-home vscode \
    && chown -R vscode:vscode /opt/venv

# Switch to vscode user
USER vscode

# Set up shell configuration
RUN echo 'export PATH="/opt/venv/bin:$PATH"' >> ~/.bashrc \
    && echo 'export PATH="/opt/venv/bin:$PATH"' >> ~/.zshrc

# Create directories for the project
RUN mkdir -p /home/vscode/.config

WORKDIR /workspace
