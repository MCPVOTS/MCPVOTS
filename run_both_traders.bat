@echo off
REM Run Both Trading Systems Simultaneously
REM ===============================
REM This script runs your main MAXX trader and Flaunch trader at the same time
REM Each uses a separate wallet and operates independently

echo 🚀 Starting Dual Trading Systems
echo ================================
echo Main MAXX Trader: maxx_trader_fix.py
echo Flaunch Trader: flaunch_separate_trader.py
echo ================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please run setup first.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start both systems in parallel
echo Starting main MAXX trading system...
start "MAXX Trader" cmd /k "python maxx_trader_fix.py --mode reactive --sell-gain-pct 0.12 --rebuy-drop-pct 0.10 --usd-reserve 10 --spend-all --ws-enable --ws-port 8080 --log-level INFO"

timeout /t 3 /nobreak > nul

echo Starting Flaunch separate trading system...
start "Flaunch Trader" cmd /k "python flaunch_separate_trader.py"

echo.
echo ✅ Both trading systems started!
echo.
echo 📊 Monitoring:
echo - Main MAXX Trader: Check the MAXX Trader window
echo - Flaunch Trader: Check the Flaunch Trader window
echo.
echo 🛑 To stop both systems:
echo - Close both command windows
echo - Or press Ctrl+C in each window
echo.
echo 💡 Tips:
echo - Each system uses a separate wallet
echo - They don't interfere with each other
echo - Monitor both for performance
echo - Start with small amounts while testing
echo.

pause
