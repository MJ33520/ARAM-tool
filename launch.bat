@echo off
chcp 65001 >nul
title ARAM 海克斯大乱斗智能助手

cd /d "%~dp0"

:: LLM 配置检查由 config.py 在启动时自行输出。
:: 若未配置任何 provider，程序仍会启动；可在浮动按钮栏点 ⚙️ 填写密钥，
:: 或参考 CUSTOM_LLM_SETUP.md 通过环境变量 / settings.json 配置。

python main.py
pause
