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
:: 3. Run the application
:: LLM 配置检查由 config.py 在启动时自行输出。未配置时程序仍会启动；
:: 可在 UI 浮动按钮栏点 ⚙️ 填写密钥，或参考 CUSTOM_LLM_SETUP.md。
echo [INFO] Starting the application...
uv run main.py

pause
