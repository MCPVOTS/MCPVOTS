# Electron Memory Optimization Script
Write-Host "Optimizing Electron memory settings..." -ForegroundColor Green

# Set environment variables for current session
$env:ELECTRON_DISABLE_GPU = 0  # Keep GPU enabled for stability
$env:ELECTRON_NO_ATTACH_CONSOLE = 1
$env:ELECTRON_FORCE_WINDOW_MENU_BAR = 0
$env:ELECTRON_DISABLE_SECURITY_WARNINGS = 1
$env:ELECTRON_ENABLE_LOGGING = 0
$env:ELECTRON_DISABLE_DEV_TOOLS = 1
$env:ELECTRON_MAX_MEMORY = 4096  # Increased to 4GB for better compatibility

# Set persistently
[Environment]::SetEnvironmentVariable('ELECTRON_DISABLE_GPU', '0', 'User')
[Environment]::SetEnvironmentVariable('ELECTRON_NO_ATTACH_CONSOLE', '1', 'User')
[Environment]::SetEnvironmentVariable('ELECTRON_FORCE_WINDOW_MENU_BAR', '0', 'User')
[Environment]::SetEnvironmentVariable('ELECTRON_DISABLE_SECURITY_WARNINGS', '1', 'User')
[Environment]::SetEnvironmentVariable('ELECTRON_ENABLE_LOGGING', '0', 'User')
[Environment]::SetEnvironmentVariable('ELECTRON_DISABLE_DEV_TOOLS', '1', 'User')
[Environment]::SetEnvironmentVariable('ELECTRON_MAX_MEMORY', '4096', 'User')

Write-Host "Memory optimization complete. Restart Electron apps to apply changes." -ForegroundColor Green
