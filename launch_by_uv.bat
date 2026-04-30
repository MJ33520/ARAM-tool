@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title ARAM 海克斯大乱斗智能助手 (uv版)

cd /d "%~dp0"

:: 1. MODULE: Check for uv
uv --version 2>nul | findstr /R "uv [0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*" >nul
if %errorlevel% neq 0 goto :NO_UV

for /f "delims=" %%i in ('uv --version') do set UV_VER=%%i
echo [INFO] Detected: !UV_VER!
goto :CHECK_ENV

:NO_UV
echo [ERROR] unable to find uv, which is required to run this application.
echo Please visit https://astral.sh to install.
pause
exit /b 1

:CHECK_ENV
:: 2. MODULE: uv env init
if exist pyproject.toml goto :ENV_EXISTS

echo [INFO] Initializing uv environment...
uv venv --python 3.12
uv init
uv add -r requirements.txt
goto :RUN_APP

:ENV_EXISTS
echo [INFO] uv environment already initialized.
goto :RUN_APP

:RUN_APP
:: 3. 读取 show_console 设置（默认 true）；false 时用 pythonw 完全无 DOS 启动
set "SHOW_CONSOLE=true"
set "SETTINGS=%USERPROFILE%\.aram_tool\settings.json"
if exist "%SETTINGS%" (
    for /f "usebackq delims=" %%i in (`powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $j = Get-Content -Raw '%SETTINGS%' | ConvertFrom-Json; if ($null -ne $j.show_console) { $j.show_console.ToString().ToLower() } else { 'true' } } catch { 'true' }"`) do (
        set "SHOW_CONSOLE=%%i"
    )
)

if /i "%SHOW_CONSOLE%"=="false" (
    echo [INFO] show_console=false, launching with pythonw (no DOS window)...
    start "" uv run --python pythonw main.py
    exit /b 0
)

echo [INFO] Starting the application...
uv run main.py
pause
