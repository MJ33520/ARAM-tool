@echo off
chcp 65001 >nul
title ARAM 海克斯大乱斗智能助手

cd /d "%~dp0"

:: 检查 API Key
if "%GEMINI_API_KEY%"=="" (
    echo.
    echo ❌ 请先设置 GEMINI_API_KEY 环境变量！
    echo.
    echo    方法1 - 临时设置（当前窗口有效）:
    echo    set GEMINI_API_KEY=你的密钥
    echo.
    echo    方法2 - 永久设置:
    echo    setx GEMINI_API_KEY "你的密钥"
    echo.
    echo    获取密钥: https://aistudio.google.com/apikey
    echo.
    pause
    exit /b 1
)

python main.py
pause
