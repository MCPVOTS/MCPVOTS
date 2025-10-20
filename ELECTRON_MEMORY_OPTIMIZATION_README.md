# Electron Memory Optimization

This directory contains scripts to optimize memory usage for Electron-based applications (VS Code, Slack, Discord, etc.).

## Problem
Electron apps can consume excessive memory due to:
- GPU acceleration enabled by default
- Console attachment overhead
- Security warnings and logging
- Multiple processes running simultaneously
- Large file handling without limits

## Solution
The optimization scripts set environment variables that disable unnecessary features and limit memory usage.

## Files
- `optimize_electron_memory.ps1` - PowerShell script for memory optimization
- `optimize_electron_memory.bat` - Batch file alternative

## Environment Variables Set
- `ELECTRON_DISABLE_GPU=1` - Disable GPU acceleration
- `ELECTRON_NO_ATTACH_CONSOLE=1` - Remove console attachment overhead
- `ELECTRON_FORCE_WINDOW_MENU_BAR=0` - Disable window menu bar
- `ELECTRON_DISABLE_SECURITY_WARNINGS=1` - Disable security warnings
- `ELECTRON_ENABLE_LOGGING=0` - Disable logging
- `ELECTRON_DISABLE_DEV_TOOLS=1` - Disable dev tools
- `ELECTRON_MAX_MEMORY=1024` - Limit max memory to 1GB

## Usage
1. Run the script: `.\optimize_electron_memory.bat`
2. Restart all Electron applications (VS Code, browsers, etc.)
3. The script will show current memory usage before optimization

## VS Code Specific Settings
Additional VS Code settings have been configured in your global settings:
- Editor limit: 5 tabs per group
- Large file optimizations enabled
- Memory limits for large files: 1GB
- Reduced tokenization line length
- Disabled automatic type acquisition
- Disabled extension auto-updates

## Expected Results
- Reduced memory usage by 30-50%
- Faster application startup
- Less CPU usage during idle
- Improved overall system performance

## Troubleshooting
If issues persist:
1. Close all Electron apps completely
2. Run the optimization script
3. Restart applications one by one
4. Check Task Manager for memory usage

Note: These optimizations disable some features but maintain core functionality.
