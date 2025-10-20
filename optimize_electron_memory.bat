@echo off
echo Optimizing Electron memory settings for all Electron apps...
echo.

REM Set environment variables
set ELECTRON_DISABLE_GPU=1
set ELECTRON_NO_ATTACH_CONSOLE=1
set ELECTRON_FORCE_WINDOW_MENU_BAR=0
set ELECTRON_DISABLE_SECURITY_WARNINGS=1
set ELECTRON_ENABLE_LOGGING=0
set ELECTRON_DISABLE_DEV_TOOLS=1
set ELECTRON_MAX_MEMORY=1024

echo Environment variables set. Please restart your Electron applications.
echo.
echo Current memory usage will be displayed below...
echo.

powershell -Command "Get-Process | Where-Object { $_.Name -match 'code|slack|discord|skype|teams|zoom|spotify|atom|sublime|brave' } | Where-Object { $_.WorkingSet -gt 50MB } | Select-Object Name, Id, @{Name='WorkingSetMB';Expression={[math]::Round($_.WorkingSet/1MB,1)}}, @{Name='PrivateMemoryMB';Expression={[math]::Round($_.PrivateMemorySize/1MB,1)}} | Sort-Object WorkingSetMB -Descending | Format-Table -AutoSize"

echo.
echo Optimization complete! Restart VS Code and other Electron apps to apply changes.
pause
