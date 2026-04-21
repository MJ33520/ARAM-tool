@echo off
chcp 65001 >nul
title Build ARAM Assistant (local)

cd /d "%~dp0"

echo [INFO] 检查 PyInstaller...
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] 未检测到 PyInstaller，正在安装...
    pip install pyinstaller || goto :fail
)

echo [INFO] 开始打包（--noconsole，打出来不会有 DOS 窗口）...
pyinstaller ^
  --noconsole ^
  --onefile ^
  --name "ARAM-Assistant" ^
  --collect-all google ^
  --collect-all google.genai ^
  --hidden-import google.genai ^
  main.py

if %errorlevel% neq 0 goto :fail

echo.
echo [OK] 打包完成
echo   输出文件: dist\ARAM-Assistant.exe
echo   体积较大（~80-120MB）是正常的，已包含 Python 解释器和所有依赖
echo.
pause
exit /b 0

:fail
echo.
echo [ERROR] 打包失败，请查看上方日志
pause
exit /b 1
