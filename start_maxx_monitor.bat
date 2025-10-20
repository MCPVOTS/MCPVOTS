@echo off
echo ========================================
echo MAXX 24/7 Trading Monitor Launcher
echo ========================================
echo.
echo Starting monitor...
echo Press Ctrl+C to stop
echo.

:loop
python maxx_247_monitor.py
echo.
echo Monitor stopped or crashed. Restarting in 10 seconds...
timeout /t 10 /nobreak > nul
goto loop