@echo off
REM Continue cloning remaining Base repositories
REM This script clones repositories that haven't been cloned yet

setlocal enabledelayedexpansion

set "BASE_DIR=%~dp0"
set "REPO_LIST=%BASE_DIR%base_repos.txt"
set "LOG_FILE=%BASE_DIR%clone_log.txt"

echo Continuing Base repositories clone process...
echo %DATE% %TIME% - Continuing clone process >> "%LOG_FILE%"

if not exist "%REPO_LIST%" (
    echo Error: Repository list file not found: %REPO_LIST%
    echo %DATE% %TIME% - Error: Repository list not found >> "%LOG_FILE%"
    exit /b 1
)

for /f "usebackq tokens=*" %%i in ("%REPO_LIST%") do (
    set "REPO_NAME=%%i"
    set "REPO_NAME=!REPO_NAME: =!"

    if "!REPO_NAME!"=="" goto :continue

    REM Check if repository already exists
    if exist "!REPO_NAME!" (
        echo Repository already exists: !REPO_NAME!
        echo %DATE% %TIME% - Already exists: !REPO_NAME! >> "%LOG_FILE%"
        goto :continue
    )

    echo Cloning repository: !REPO_NAME!
    echo %DATE% %TIME% - Cloning: !REPO_NAME! >> "%LOG_FILE%"

    git clone https://github.com/base/!REPO_NAME!.git !REPO_NAME!
    if !errorlevel! equ 0 (
        echo Successfully cloned: !REPO_NAME!
        echo %DATE% %TIME% - Cloned: !REPO_NAME! >> "%LOG_FILE%"
    ) else (
        echo Failed to clone: !REPO_NAME!
        echo %DATE% %TIME% - Failed clone: !REPO_NAME! >> "%LOG_FILE%"
    )

    REM Small delay to avoid rate limiting
    timeout /t 2 /nobreak >nul

    :continue
)

echo Clone continuation completed. Check %LOG_FILE% for details.
echo %DATE% %TIME% - Continuation completed >> "%LOG_FILE%"

pause
