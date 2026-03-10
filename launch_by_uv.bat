@echo off
setlocal
setlocal enabledelayedexpansion
chcp 65001 >nul

:: 1. MODULE: Check for uv
uv --version 2>nul | findstr /R "uv [0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*" >nul

if %errorlevel% neq 0 (
    echo [ERROR] unable to find uv, which is required to run this application.
    echo Please visit https://astral.sh to install.
    pause
    exit /b
) else (
    for /f "delims=" %%i in ('uv --version') do set UV_VER=%%i
    echo [INFO] Detected: !UV_VER!
)
 
:: 2. MODULE: uv env init
if not exist pyproject.toml (
    echo [INFO] Initializing uv environment...
    uv venv --python 3.12
    uv init
    uv add -r requirements.txt
) else (
    echo [INFO] uv environment already initialized.
)


:: 3. GEMINI_API_KEY Check
if not exist GEMINI_API_KEY (
    echo [ERROR] GEMINI_API_KEY file not found in the current directory.
    echo Please save your Gemini API key in the GEMINI_API_KEY file and try again.
    pause
    exit /b
) else (
    set /p API_KEY=<GEMINI_API_KEY
    if "!API_KEY!"=="" (
        echo [ERROR] GEMINI_API_KEY file is empty. Please add your Gemini API key to the file and try again.
        pause
        exit /b
    ) else (
        echo [INFO] Found Gemini API Key: !API_KEY:~0,4!************ (hidden for security)
        set GEMINI_API_KEY=!API_KEY!
    )
)

:: 4. LOL LAUNCH
if not exist LOL_LAUNCHER_PATH (
    echo [ERROR] LOL_LAUNCHER.exe not found in the current directory.
    echo Please save the absolute path of the lol launcher file in the LOL_LUNCHER_PATH file
    pause
    exit /b
) else (
    :: find the process name from the path
    tasklist | findstr /i "Client.exe" >nul 2>&1

    :: check if the process is running
    if !errorlevel!==1 (
        set /p EXE_PATH=<LOL_LAUNCHER_PATH
        if not exist "!EXE_PATH!" (
            echo [ERROR] LOL_LAUNCHER: Client.exe not found at the specified path: !EXE_PATH!
            pause
            exit /b
        ) else (
            echo [INFO] Found LOL_LAUNCHER: Client.exe at: !EXE_PATH!
            echo [INFO] LOL_LAUNCHER: Client.exe is not running, starting it now ...
            start "" "!EXE_PATH!"
        )
    ) else (
        echo [INFO] LOL_LAUNCHER: Client.exe is already running.
    )
)

:: 5. Run the application
echo [INFO] Starting the application...
uv run main.py

pause
