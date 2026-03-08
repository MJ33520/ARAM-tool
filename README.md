# ⚔️ ARAM Tool - 海克斯大乱斗智能助手

> **[English](README_EN.md)** | 中文

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Gemini](https://img.shields.io/badge/AI-Gemini-orange?logo=google)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)

基于 **Gemini AI** 的英雄联盟海克斯大乱斗（ARAM）实时分析助手。在加载界面截图后，AI 自动识别双方阵容，为你提供出装、符文、打法的完整攻略。

## ✨ 功能

- 🎮 **一键截图分析** — 点击浮动按钮，自动截图并发送给 Gemini AI
- 🤖 **智能阵容识别** — AI 从加载界面读取所有英雄名，自动识别你的英雄
- 📋 **完整攻略输出** — 海克斯符文、6件装备、技能加点、打法要点、团队策略
- 🗡️ **队友推荐** — 为每个队友提供符文和出装建议
- 🖥️ **悬浮窗显示** — 始终置顶的攻略窗口，支持拖拽和快捷键
- 🌐 **中英文切换** — 一行配置切换界面语言和 AI 分析语言

## 🚀 快速开始

### 1. 获取 Gemini API Key

前往 [Google AI Studio](https://aistudio.google.com/apikey) 免费获取 API Key。

### 2. 设置环境变量

```cmd
setx GEMINI_API_KEY "你的API密钥"
```

### 3. 安装依赖

```cmd
pip install -r requirements.txt
```

### 4. 启动

双击 `launch.bat`，或：

```cmd
python main.py
```

## 🎮 使用方法

1. 启动助手后，屏幕左上角出现 `[⚔️ 分析 | 📋 攻略]` 浮动按钮
2. 进入大乱斗加载界面后，点击 **⚔️ 分析**
3. 等待 15-30 秒，AI 分析完成后自动弹出攻略窗口
4. 按 **Ctrl+F12** 可随时切换攻略窗口的显示/隐藏

## 🌐 语言切换

编辑 `config.py`，修改 `LANGUAGE` 的值：

```python
LANGUAGE = "zh"   # 中文（默认）
LANGUAGE = "en"   # English
```

切换后，界面文字、控制台提示和 AI 分析结果的语言都会相应改变。

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `main.py` | 主入口，浮动按钮和攻略窗口 |
| `config.py` | 配置文件（API Key、语言、UI） |
| `lang.py` | 多语言字符串和 Prompt（中/英） |
| `screenshot.py` | 截图模块 |
| `gemini_analyzer.py` | Gemini API 调用模块 |
| `overlay_ui.py` | 独立攻略窗口 UI（备用） |
| `launch.bat` | Windows 启动脚本 |

## 🔧 要求

- **操作系统**: Windows 10/11
- **Python**: 3.10+
- **网络**: 能访问 Google Gemini API
- **游戏**: 英雄联盟（国服/国际服）

## 📝 注意事项

- 截图分析需要在 **加载界面** 触发（可以看到所有英雄卡片的时候）
- 每次分析耗时约 15-30 秒，取决于网络和 API 响应速度
- 浮动按钮可以右键拖拽移动位置
- 攻略窗口按 Esc 隐藏，点 📋 重新显示

## 📄 License

MIT
