@echo off
REM Simple batch script to clone Base repositories
REM Usage: simple_clone.bat

set "BASE_DIR=%~dp0"
set "REPO_LIST=%BASE_DIR%base_repos.txt"
set "LOG_FILE=%BASE_DIR%simple_clone_log.txt"

echo Starting simple Base repositories clone process...
echo %DATE% %TIME% - Starting simple clone process >> "%LOG_FILE%"

if not exist "%REPO_LIST%" (
    echo Error: Repository list file not found: %REPO_LIST%
    exit /b 1
)

REM Large repositories to skip
set LARGE_REPOS=optimism op-geth reth node-reth goleveldb go-ethereum-rpc

for /f "tokens=*" %%i in (%REPO_LIST%) do (
    set "REPO_NAME=%%i"

    REM Check if it's a large repo to skip
    echo %LARGE_REPOS% | findstr /C:"%%i" >nul
    if not errorlevel 1 (
        echo Skipping large repository: %%i
        echo %DATE% %TIME% - Skipping large repo: %%i >> "%LOG_FILE%"
        goto :continue
    )

    if exist "%%i" (
        echo Repository already exists: %%i
        echo %DATE% %TIME% - Already exists: %%i >> "%LOG_FILE%"
    ) else (
        echo Cloning repository: %%i
        echo %DATE% %TIME% - Cloning: %%i >> "%LOG_FILE%"
        git clone https://github.com/base/%%i.git %%i
        if errorlevel 1 (
            echo Failed to clone: %%i
            echo %DATE% %TIME% - Failed clone: %%i >> "%LOG_FILE%"
        ) else (
            echo Successfully cloned: %%i
            echo %DATE% %TIME% - Cloned: %%i >> "%LOG_FILE%"
        )
    )

    REM Small delay to avoid rate limiting
    timeout /t 3 /nobreak >nul

    :continue
)

echo Simple clone process completed. Check %LOG_FILE% for details.
echo %DATE% %TIME% - Simple clone process completed >> "%LOG_FILE%"

pause
