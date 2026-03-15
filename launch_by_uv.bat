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
goto :CHECK_KEY

:ENV_EXISTS
echo [INFO] uv environment already initialized.
goto :CHECK_KEY

:CHECK_KEY
:: 3. Check API Key
if not "%GEMINI_API_KEY%"=="" goto :RUN_APP

:NO_KEY
echo.
echo [ERROR] 请先设置 GEMINI_API_KEY 环境变量！
echo.
echo    当前系统未检测到 GEMINI_API_KEY 环境变量。
echo.
echo    临时设置方法（当前窗口有效）:
echo    set GEMINI_API_KEY=你的密钥
echo.
echo    永久设置方法:
echo    setx GEMINI_API_KEY "你的密钥"
echo.
echo    获取密钥: https://aistudio.google.com/apikey
echo.
pause
exit /b 1

:RUN_APP
:: 4. Run the application
echo [INFO] Starting the application...
uv run main.py

pause
