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

**方式A: 命令行启动**

在项目根目录下打开终端，执行：

```
python main.py
```

**方式 B：直接启动（需自行管理 Python 环境）**

适用于已经手动配置好 Python 环境及依赖的用户。

- **脚本启动**：直接双击运行 `launch.bat`。

**方式 C：使用 `uv` 自动化启动**

适用于希望自动管理依赖、避免环境污染的用户。此方式通过 `launch_by_uv.bat` 实现一键配置与运行。

1. **安装 uv**：确保系统已安装 Python 包管理器 [uv](https://docs.astral.sh/uv/getting-started/installation/)。
2. **配置路径文件**（请确保文件内仅包含配置信息，无多余空格或换行）：
   - **LOL_LAUNCHER_PATH**：在项目根目录下创建一个名为 `LOL_LAUNCHER_PATH` 的文件，写入英雄联盟客户端的完整路径。
     - *示例：`D:\Tencent\WeGameApps\英雄联盟\Launcher\Client.exe`*
   - **GEMINI_API_KEY**：在项目根目录下创建一个名为 `GEMINI_API_KEY` 的文件，写入你的 API 密钥。
     - *示例：`vK9mR2xT5zW8nL4pQ-jA1sB6dF3gH0vC9uN2mY5`*
3. **执行启动**：
   - **双击 `launch_by_uv.bat`**：脚本将自动检查 `uv` 环境、安装依赖、加载配置并启动游戏及程序。

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
| `gemini_analyzer.py` | Gemini API 调用模块（含 SSL 自动重试） |
| `apexlol_scraper.py` | ApexLol.info 数据爬取模块 |
| `apexlol_data.py` | 数据缓存管理与查询 |
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

## 📊 数据来源声明

本工具的海克斯符文推荐数据来源于 **[ApexLol.info](https://apexlol.info)**。

- 数据仅在用户**主动点击 🔄 数据 按钮**时爬取，不会自动抓取
- 爬取频率受限（每次请求间隔 0.4 秒），尽量减少对源站的负载
- 数据本地缓存 7 天，避免重复请求
- 本项目与 ApexLol.info **没有官方合作关系**，所有数据版权归 ApexLol.info 及其数据提供者所有
- 如果 ApexLol.info 的运营方认为本项目的数据引用方式不当，请通过 GitHub Issues 联系我，我会立即处理

## ⚠️ 免责声明

- 本工具为个人学习项目，仅供参考，不保证分析结果的准确性
- 本工具与 Riot Games 或 League of Legends 没有任何官方关联
- 本工具**不读取、不修改任何游戏数据**，仅通过截取屏幕截图 + AI 分析提供参考建议。但不排除 Riot 可能将此类第三方工具误判为违规，**使用本工具请自行评估封号风险**
- 使用本工具时请遵守游戏的使用条款

## 📄 License

MIT
