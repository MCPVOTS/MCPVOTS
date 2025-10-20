@echo off
REM Base Repositories Daily Update Script
REM This script updates all cloned Base repositories

echo Starting Base repositories daily update...
echo %DATE% %TIME% - Starting update >> update_log.txt

powershell.exe -ExecutionPolicy Bypass -File "%~dp0clone_base_repos.ps1" -UpdateOnly

echo %DATE% %TIME% - Update completed >> update_log.txt
echo Update completed. Check update_log.txt for details.

pause
