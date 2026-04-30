@echo off
chcp 65001 >nul
title ARAM 海克斯大乱斗智能助手
setlocal enabledelayedexpansion

cd /d "%~dp0"

REM 读取用户设置中的 show_console（默认 true）
REM 如果 show_console=false → 用 pythonw（无 DOS 窗口从启动就不存在，根本不会被「最小化」）
REM 否则用 python，正常显示 DOS 窗口
set "SHOW_CONSOLE=true"
set "SETTINGS=%USERPROFILE%\.aram_tool\settings.json"
if exist "%SETTINGS%" (
    for /f "usebackq delims=" %%i in (`powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $j = Get-Content -Raw '%SETTINGS%' | ConvertFrom-Json; if ($null -ne $j.show_console) { $j.show_console.ToString().ToLower() } else { 'true' } } catch { 'true' }"`) do (
        set "SHOW_CONSOLE=%%i"
    )
)

if /i "%SHOW_CONSOLE%"=="false" (
    REM 无 DOS 窗口启动；start "" 让 pythonw 完全脱离当前 cmd
    start "" pythonw main.py
    exit /b 0
)

REM 默认：显示 DOS 窗口
python main.py
pause
