@echo off
REM Batch script to clone all Base repositories with error handling
REM Usage: clone_all.bat [update] [resume]

setlocal enabledelayedexpansion

set "UPDATE_MODE=%1"
set "RESUME_MODE=%2"
set "BASE_DIR=%~dp0"
set "REPO_LIST=%BASE_DIR%base_repos.txt"
set "LOG_FILE=%BASE_DIR%clone_log.txt"
set "RESUME_FILE=%BASE_DIR%resume_from.txt"

echo Starting Base repositories clone/update process...
echo %DATE% %TIME% - Starting process >> "%LOG_FILE%"

if not exist "%REPO_LIST%" (
    echo Error: Repository list file not found: %REPO_LIST%
    echo %DATE% %TIME% - Error: Repository list not found >> "%LOG_FILE%"
    exit /b 1
)

REM Find starting point if resuming
set "START_PROCESSING=0"
if "%RESUME_MODE%"=="resume" (
    if exist "%RESUME_FILE%" (
        set /p RESUME_FROM=<"%RESUME_FILE%"
        echo Resuming from repository: !RESUME_FROM!
        set "START_PROCESSING=0"
    ) else (
        echo No resume file found, starting from beginning
    )
)

REM Large repositories to skip initially
set "LARGE_REPOS=optimism op-geth reth node-reth goleveldb go-ethereum-rpc"

for /f "tokens=*" %%i in (%REPO_LIST%) do (
    set "REPO_NAME=%%i"

    if "!REPO_NAME!"=="" goto :continue

    REM Check if we should start processing
    if "%RESUME_MODE%"=="resume" (
        if "!START_PROCESSING!"=="0" (
            if "!REPO_NAME!"=="!RESUME_FROM!" (
                set "START_PROCESSING=1"
                echo Found resume point: !REPO_NAME!
            ) else (
                goto :continue
            )
        )
    )

    REM Save current position for resume
    echo !REPO_NAME!> "%RESUME_FILE%"

    REM Check if it's a large repo to skip
    echo !LARGE_REPOS! | findstr /C:"!REPO_NAME!" >nul
    if !errorlevel! equ 0 (
        echo Skipping large repository: !REPO_NAME!
        echo %DATE% %TIME% - Skipping large repo: !REPO_NAME! >> "%LOG_FILE%"
        goto :continue
    )

    if exist "%%i" (
        if "%UPDATE_MODE%"=="update" (
            echo Updating repository: %%i
            echo %DATE% %TIME% - Updating: %%i >> "%LOG_FILE%"
            cd "%%i"
            git pull --rebase --quiet
            if errorlevel 1 (
                echo Failed to update: %%i
                echo %DATE% %TIME% - Failed update: %%i >> "%LOG_FILE%"
            ) else (
                echo Successfully updated: %%i
                echo %DATE% %TIME% - Updated: %%i >> "%LOG_FILE%"
            )
            cd ..
        ) else (
            echo Repository already exists: %%i
            echo %DATE% %TIME% - Already exists: %%i >> "%LOG_FILE%"
        )
    ) else (
        echo Cloning repository: %%i
        echo %DATE% %TIME% - Cloning: %%i >> "%LOG_FILE%"

        REM Retry logic for cloning
        set "RETRY_COUNT=0"
        set "MAX_RETRIES=3"

        :retry_clone
        git clone https://github.com/base/%%i.git %%i --quiet
        if errorlevel 1 (
            set /a "RETRY_COUNT+=1"
            if !RETRY_COUNT! lss !MAX_RETRIES! (
                echo Clone failed, retrying %%i (attempt !RETRY_COUNT!/!MAX_RETRIES!)
                echo %DATE% %TIME% - Retrying clone: %%i >> "%LOG_FILE%"
                REM Clean up failed clone
                if exist "%%i" rmdir /s /q "%%i" 2>nul
                timeout /t 5 /nobreak >nul
                goto :retry_clone
            ) else (
                echo Failed to clone after !MAX_RETRIES! attempts: %%i
                echo %DATE% %TIME% - Failed clone after retries: %%i >> "%LOG_FILE%"
            )
        ) else (
            echo Successfully cloned: %%i
            echo %DATE% %TIME% - Cloned: %%i >> "%LOG_FILE%"
        )
    )

    REM Small delay to avoid rate limiting
    timeout /t 2 /nobreak >nul

    :continue
)

REM Clean up resume file on successful completion
if exist "%RESUME_FILE%" del "%RESUME_FILE%"

echo Process completed. Check %LOG_FILE% for details.
echo %DATE% %TIME% - Process completed >> "%LOG_FILE%"

pause
