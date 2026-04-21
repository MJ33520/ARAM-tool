# ⚔️ ARAM Tool - 海克斯大乱斗智能助手

> **[English](README_EN.md)** | 中文

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![LLM](https://img.shields.io/badge/LLM-Gemini%20%7C%20OpenAI%20%7C%20Custom-orange)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
[![Release](https://img.shields.io/github/v/release/Zayia/ARAM-tool?include_prereleases)](https://github.com/Zayia/ARAM-tool/releases)

英雄联盟海克斯大乱斗（ARAM）实时 AI 攻略助手。支持 **Gemini / OpenAI 兼容 / 自定义后端** 三种 LLM，进入加载界面后自动识别双方阵容，输出出装、海斗符文、打法的完整攻略。

## ✨ 功能

- 🤖 **多 LLM 支持** — Gemini / OpenAI 官方 / Azure / LM Studio / Ollama / 任意 OpenAI 兼容网关 / 自定义 POST JSON 后端
- ⚙️ **图形界面配置** — 浮动栏点 `⚙️` 切换 provider、填 Key、测连通、选模型，保存后**即时生效无需重启**
- 🧪 **连通性测试** — 保存前一键 ping 一次，确认 provider/model/key 可用
- 🔄 **模型列表自动拉取** — Gemini 和 OpenAI provider 都能从 `/models` 端点拉取可用模型
- 📋 **完整攻略输出** — 海克斯符文、6件装备、技能加点、打法要点、团队策略
- 🖥️ **悬浮窗显示** — 始终置顶、支持拖拽、全局热键 `Ctrl+F12` 切换显示
- ✕ **一键退出 / 控制台显隐** — 浮动栏的 `✕` 按钮关闭整个程序；`⚙️` 里可选是否显示 DOS 窗口
- 🌐 **中英文切换** — UI 文案和 AI 分析语言
- ♻️ **瞬态错误自动重试** — SSL EOF / 503 / 502 / 504 / 429 / rate limit 触发 2 次自动重试

---

## 🚀 快速开始

### 方式 A：直接下载 `.exe`（推荐，无需装 Python）

1. 前往 [Releases](https://github.com/Zayia/ARAM-tool/releases) 下载 `ARAM-Assistant-*-windows.zip`
   - `v*` tag 是稳定版
   - `dev-latest` 是滚动最新构建
2. 解压双击 `ARAM-Assistant.exe`
3. 首次启动点浮动栏 `⚙️` 按钮配置 LLM 提供商和 API Key
4. [获取 Gemini API Key](https://aistudio.google.com/apikey)（免费）或填任意 OpenAI 兼容密钥

### 方式 B：从源码运行（开发 / 自定义）

```cmd
git clone https://github.com/Zayia/ARAM-tool.git
cd ARAM-tool
pip install -r requirements.txt
python main.py
```

启动后点浮动栏 `⚙️` 按钮配置 LLM。

---

## 🎮 使用方法

浮动按钮栏：`⚡海克斯  |  📋攻略  |  ✏️纠错  |  🔄数据  |  ⚙️  |  ✕`

| 按钮 | 作用 |
|------|------|
| ⚡ 海克斯 | 截图识别当前 3 选 1，给出选择建议 |
| 📋 攻略 | 显示 / 隐藏全局攻略窗口 |
| ✏️ 纠错 | 英雄识别错了时手动指定英雄名 |
| 🔄 数据 | 从 ApexLol 拉取英雄海克斯数据（本地缓存 7 天） |
| ⚙️ | 打开设置对话框（LLM provider、模型、密钥、界面语言、控制台开关） |
| ✕ | 退出程序 |

**拖拽**：右键按住任意按钮 / 分隔符 / 状态栏拖动整个浮动栏。
**全局热键**：`Ctrl+F12` 切换攻略窗口显示/隐藏（游戏中也能触发）。
**控制台**：⚙️ 中「显示控制台窗口 (DOS)」复选框——勾选显示黑色 DOS 窗口查看实时日志，取消勾选彻底隐藏。

---

## 🔧 配置 LLM 提供商

**三种方式**，优先级：**环境变量 > `~/.aram_tool/settings.json` > 代码默认值**

1. **⚙️ UI**（推荐）：浮动栏点 `⚙️` → 填写 → 保存，即时生效
2. **环境变量**：`set LLM_PROVIDER=openai` / `set OPENAI_API_KEY=...` 等
3. **直接改 `config.py` 默认值**（不推荐，易误提交密钥）

完整参数清单、常见场景（LM Studio / Ollama / Azure / 代理）、故障排查见 [CUSTOM_LLM_SETUP.md](CUSTOM_LLM_SETUP.md)。

---

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `main.py` | 主入口；浮动按钮栏和所有 Toplevel 窗口 |
| `config.py` | 配置读取（env > settings.json > default）、`reload()` 支持热重载 |
| `llm_client.py` | 统一 LLM 适配层（Gemini / OpenAI / Custom）、重试、`test_*()`、模型列表拉取 |
| `gemini_analyzer.py` | 3 种分析模式的业务逻辑（全局 / 海克斯选择 / 更新），走 `LLMClient` |
| `settings_ui.py` | ⚙️ 设置对话框（Toplevel）、保存后自动 `config.reload()` |
| `console_utils.py` | DOS 窗口的 AllocConsole / 真·隐藏（SW_HIDE → SWP_HIDEWINDOW → FreeConsole） |
| `lang.py` | 中英文文案 + 所有 AI prompt |
| `screenshot.py` | mss 截图模块 |
| `apexlol_scraper.py` / `apexlol_data.py` | 爬取 ApexLol.info 数据 + 本地缓存 |
| `lcu_client.py` | LCU API 客户端（直接从 LoL 客户端读英雄） |
| `launch.bat` / `launch_by_uv.bat` | Windows 启动脚本（source 运行） |
| `build.bat` | 本地 PyInstaller 打包脚本（`--noconsole --onefile`） |
| `.github/workflows/release.yml` | CI：每次 push 产出 `dev-latest`，`v*` tag 出正式 release |

---

## 🏗️ 自行打包

需要 Windows 环境（PyInstaller 不支持跨平台编译）。

**本地打包**：双击 `build.bat`，产出 `dist\ARAM-Assistant.exe`

**CI 打包**：推 `v*` tag 自动出正式 release
```cmd
git tag -a v0.2.0 -m "release notes"
git push origin v0.2.0
```
任意分支 push 会刷新 `dev-latest` 滚动 pre-release。

---

## 🔧 要求

- **操作系统**：Windows 10/11
- **Python**（仅源码运行）：3.10+
- **网络**：能访问所选 LLM 的 API 端点
- **游戏**：英雄联盟（国服 / 国际服均可）

---

## 📝 注意事项

- 海克斯截图分析需要在**加载界面 / 海克斯选择界面**触发（能看到选项卡片）
- 单次分析耗时 5-30 秒，取决于 provider 和网络
- 打包版默认无 DOS 窗口；可在 ⚙️ 里开启（仅 Windows 生效）
- `~/.aram_tool/settings.json` 含 API Key 明文，权限 0600（Unix）

---

## 📊 数据来源声明

海克斯符文推荐数据来源于 **[ApexLol.info](https://apexlol.info)**。

- 仅在用户**主动点击 🔄 数据 按钮**时爬取，不自动抓取
- 请求间隔 0.4 秒，减少源站压力
- 本地缓存 7 天避免重复请求
- 本项目与 ApexLol.info 无官方合作关系，数据版权归原站
- 若源站运营方认为数据引用方式不当，请通过 GitHub Issues 联系

---

## ⚠️ 免责声明

- 个人学习项目，仅供参考，不保证分析准确性
- 与 Riot Games / League of Legends 无官方关联
- 工具**不读取、不修改任何游戏数据**，仅通过截图 + AI 分析提供参考
- 不排除 Riot 误判为违规工具——**使用需自行评估封号风险**
- 使用请遵守游戏条款

---

## Contributors

- **[Zayia](https://github.com/Zayia)** - Project logic & review
- **Antigravity (AI) / Claude** - Implementation & Optimization

欢迎提交 Pull Request！

---

## 📄 License

MIT
