@echo off
chcp 65001 >nul
title ARAM 海克斯大乱斗智能助手

cd /d "%~dp0"

REM 直接用 pythonw 启动，无 DOS 窗口；日志写入 %USERPROFILE%\.aram_tool\aram_debug.log
REM 想看实时日志或在控制台直接输入英雄名时，改用：python main.py
start "" pythonw main.py
exit /b 0
