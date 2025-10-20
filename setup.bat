@echo off
REM MAXX Ecosystem Setup Script for Windows
REM Batch script to set up the development environment

setlocal enabledelayedexpansion

echo 🚀 MAXX Ecosystem Setup Script
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python first.
    pause
    exit /b 1
)

REM Parse command line arguments
set CLEAN=0
set DEV=0
set TEST=0
set RUN=0
set VALIDATE=0

:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="-Clean" set CLEAN=1
if /i "%~1"=="-Dev" set DEV=1
if /i "%~1"=="-Test" set TEST=1
if /i "%~1"=="-Run" set RUN=1
if /i "%~1"=="-Validate" set VALIDATE=1
shift
goto :parse_args

:args_done

REM Handle specific commands
if %CLEAN%==1 goto :clean
if %TEST%==1 goto :test
if %RUN%==1 goto :run
if %VALIDATE%==1 goto :validate

REM Default setup behavior
echo Setting up MAXX Ecosystem development environment...

REM Create directories
echo 📁 Creating necessary directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups
if not exist "reports" mkdir reports
if not exist "docs" mkdir docs
echo   Created necessary directories

REM Set up environment file
echo ⚙️  Setting up environment configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo   Created .env from .env.example
        echo   ⚠️  Please edit .env with your configuration!
    ) else (
        echo   Creating basic .env file...
        (
            echo # MAXX Ecosystem Environment Configuration
            echo # Blockchain Configuration
            echo ETHEREUM_PRIVATE_KEY=your_private_key_here
            echo PROVIDER_URL=https://mainnet.base.org
            echo BASESCAN_API_KEY=your_basescan_api_key
            echo.
            echo # MAXX Token Configuration
            echo MAXX_CONTRACT_ADDRESS=0xFB7a83abe4F4A4E51c77B92E521390B769ff6467
            echo.
            echo # Trading Configuration
            echo BUY_THRESHOLD=0.02
            echo SELL_THRESHOLD=0.05
            echo MAX_POSITION_SIZE=0.1
            echo STOP_LOSS_PCT=0.03
            echo.
            echo # Notifications
            echo DISCORD_WEBHOOK_URL=your_discord_webhook_url
            echo.
            echo # Database
            echo DB_PATH=./data/ecosystem.db
        ) > ".env"
        echo   Created basic .env file
        echo   ⚠️  Please edit .env with your configuration!
    )
) else (
    echo   .env file already exists
)

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if %DEV%==1 (
    echo   Installing development dependencies...
    pip install -r requirements.txt
)
echo   Dependencies installed successfully

echo.
echo ✅ Setup completed successfully!
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Run validation: setup.bat -Validate
echo 3. Run tests: setup.bat -Test
echo 4. Start application: setup.bat -Run
echo.
echo Available commands:
echo   setup.bat -Dev      # Install development dependencies
echo   setup.bat -Clean    # Clean temporary files
echo   setup.bat -Test     # Run tests
echo   setup.bat -Run      # Start application
echo   setup.bat -Validate # Validate refactor
goto :end

:clean
echo 🧹 Cleaning up temporary files...
REM Remove Python cache files
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.egg-info 2>nul

REM Remove build artifacts
if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"

REM Remove test artifacts
if exist ".coverage" del ".coverage"
if exist "htmlcov" rd /s /q "htmlcov"
if exist ".pytest_cache" rd /s /q ".pytest_cache"
if exist ".mypy_cache" rd /s /q ".mypy_cache"

echo   Cleanup completed
goto :end

:test
echo 🧪 Running tests...
pytest
goto :end

:run
echo 🚀 Starting MAXX Ecosystem...
if exist "main.py" (
    python main.py
) else (
    echo   ❌ main.py not found.
    exit /b 1
)
goto :end

:validate
echo 🔍 Validating refactor...
if exist "validate_refactor.py" (
    python validate_refactor.py
) else (
    echo   ❌ validate_refactor.py not found.
    exit /b 1
)
goto :end

:end
pause