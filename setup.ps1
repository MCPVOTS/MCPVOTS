# MAXX Ecosystem Setup Script for Windows
# PowerShell script to set up the development environment

param(
    [switch]$Dev,
    [switch]$Clean,
    [switch]$Test,
    [switch]$Run,
    [switch]$Validate
)

Write-Host "🚀 MAXX Ecosystem Setup Script" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Function to check if command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to create directories
function Initialize-Directories {
    Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow

    $dirs = @("data", "logs", "backups", "reports", "docs")
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "  Created: $dir" -ForegroundColor Gray
        }
    }
}

# Function to set up environment file
function Initialize-Environment {
    Write-Host "⚙️  Setting up environment configuration..." -ForegroundColor Yellow

    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Host "  Created .env from .env.example" -ForegroundColor Gray
            Write-Host "  ⚠️  Please edit .env with your configuration!" -ForegroundColor Red
        } else {
            Write-Host "  Creating basic .env file..." -ForegroundColor Gray
            @"
# MAXX Ecosystem Environment Configuration
# Blockchain Configuration
ETHEREUM_PRIVATE_KEY=your_private_key_here
PROVIDER_URL=https://mainnet.base.org
BASESCAN_API_KEY=your_basescan_api_key

# MAXX Token Configuration
MAXX_CONTRACT_ADDRESS=0xFB7a83abe4F4A4E51c77B92E521390B769ff6467

# Trading Configuration
BUY_THRESHOLD=0.02
SELL_THRESHOLD=0.05
MAX_POSITION_SIZE=0.1
STOP_LOSS_PCT=0.03

# Notifications
DISCORD_WEBHOOK_URL=your_discord_webhook_url

# Database
DB_PATH=./data/ecosystem.db
"@ | Out-File -FilePath ".env" -Encoding UTF8
            Write-Host "  Created basic .env file" -ForegroundColor Gray
            Write-Host "  ⚠️  Please edit .env with your configuration!" -ForegroundColor Red
        }
    } else {
        Write-Host "  .env file already exists" -ForegroundColor Gray
    }
}

# Function to install dependencies
function Install-Dependencies {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow

    if (Test-Command "pip") {
        if ($Dev) {
            pip install -r requirements.txt
            Write-Host "  Installed development dependencies" -ForegroundColor Gray
        } else {
            pip install -r requirements.txt
            Write-Host "  Installed production dependencies" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ❌ pip not found. Please install Python and pip first." -ForegroundColor Red
        exit 1
    }
}

# Function to clean up
function Clean-Project {
    Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Yellow

    # Remove Python cache files
    Get-ChildItem -Path . -Recurse -Include "__pycache__", "*.pyc" -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Recurse -Include "*.egg-info" -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

    # Remove build artifacts
    if (Test-Path "build") { Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue }
    if (Test-Path "dist") { Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue }

    # Remove test artifacts
    if (Test-Path ".coverage") { Remove-Item -Path ".coverage" -Force -ErrorAction SilentlyContinue }
    if (Test-Path "htmlcov") { Remove-Item -Path "htmlcov" -Recurse -Force -ErrorAction SilentlyContinue }
    if (Test-Path ".pytest_cache") { Remove-Item -Path ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue }
    if (Test-Path ".mypy_cache") { Remove-Item -Path ".mypy_cache" -Recurse -Force -ErrorAction SilentlyContinue }

    Write-Host "  Cleanup completed" -ForegroundColor Gray
}

# Function to run tests
function Invoke-Tests {
    Write-Host "🧪 Running tests..." -ForegroundColor Yellow

    if (Test-Command "pytest") {
        pytest
    } else {
        Write-Host "  ❌ pytest not found. Please install dependencies first." -ForegroundColor Red
        exit 1
    }
}

# Function to run the application
function Start-Application {
    Write-Host "🚀 Starting MAXX Ecosystem..." -ForegroundColor Yellow

    if (Test-Path "main.py") {
        python main.py
    } else {
        Write-Host "  ❌ main.py not found." -ForegroundColor Red
        exit 1
    }
}

# Function to validate refactor
function Invoke-Validation {
    Write-Host "🔍 Validating refactor..." -ForegroundColor Yellow

    if (Test-Path "validate_refactor.py") {
        python validate_refactor.py
    } else {
        Write-Host "  ❌ validate_refactor.py not found." -ForegroundColor Red
        exit 1
    }
}

# Function to check code quality
function Invoke-CodeQuality {
    Write-Host "📊 Running code quality checks..." -ForegroundColor Yellow

    # Format code
    if (Test-Command "black") {
        Write-Host "  Formatting with black..." -ForegroundColor Gray
        black .
    }

    # Sort imports
    if (Test-Command "isort") {
        Write-Host "  Sorting imports with isort..." -ForegroundColor Gray
        isort .
    }

    # Lint code
    if (Test-Command "flake8") {
        Write-Host "  Linting with flake8..." -ForegroundColor Gray
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    }

    # Type checking
    if (Test-Command "mypy") {
        Write-Host "  Type checking with mypy..." -ForegroundColor Gray
        mypy . --ignore-missing-imports
    }

    # Security check
    if (Test-Command "bandit") {
        Write-Host "  Security check with bandit..." -ForegroundColor Gray
        bandit -r . -f json -o bandit-report.json
    }
}

# Main execution logic
if ($Clean) {
    Clean-Project
    exit 0
}

if ($Test) {
    Invoke-Tests
    exit 0
}

if ($Run) {
    Start-Application
    exit 0
}

if ($Validate) {
    Invoke-Validation
    exit 0
}

# Default setup behavior
Write-Host "Setting up MAXX Ecosystem development environment..." -ForegroundColor Green

Initialize-Directories
Initialize-Environment
Install-Dependencies

Write-Host ""
Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your configuration" -ForegroundColor White
Write-Host "2. Run validation: .\setup.ps1 -Validate" -ForegroundColor White
Write-Host "3. Run tests: .\setup.ps1 -Test" -ForegroundColor White
Write-Host "4. Start application: .\setup.ps1 -Run" -ForegroundColor White
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  .\setup.ps1 -Dev      # Install development dependencies" -ForegroundColor White
Write-Host "  .\setup.ps1 -Clean    # Clean temporary files" -ForegroundColor White
Write-Host "  .\setup.ps1 -Test     # Run tests" -ForegroundColor White
Write-Host "  .\setup.ps1 -Run      # Start application" -ForegroundColor White
Write-Host "  .\setup.ps1 -Validate # Validate refactor" -ForegroundColor White