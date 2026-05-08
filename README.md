# ⚔️ ARAM Tool - 海克斯大乱斗智能助手

> **[English](README_EN.md)** | 中文

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![LLM](https://img.shields.io/badge/LLM-Gemini%20%7C%20OpenAI%20%7C%20Custom-orange)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
[![Release](https://img.shields.io/github/v/release/Zayia/ARAM-tool?include_prereleases)](https://github.com/Zayia/ARAM-tool/releases)

英雄联盟海克斯大乱斗（ARAM）实时 AI 攻略助手。支持 **Gemini / OpenAI 兼容 / 自定义后端** 三种 LLM，进入加载界面后自动识别双方阵容，输出出装、海克斯符文、打法的完整攻略。

## ✨ 功能

- 🤖 **多 LLM 支持** — Gemini / OpenAI 官方 / Azure / LM Studio / Ollama / 任意 OpenAI 兼容网关 / 自定义 POST JSON 后端
- ⚙️ **图形界面配置** — 浮动栏点 `⚙️` 切换 provider、填 Key、测连通、选模型，保存后**即时生效无需重启**
- 🧪 **连通性测试** — 保存前一键 ping 一次，确认 provider/model/key 可用
- 🔄 **模型列表自动拉取** — Gemini 和 OpenAI provider 都能从 `/models` 端点拉取可用模型
- 📋 **完整攻略输出** — 海克斯符文、6 件装备、技能加点、打法要点、团队策略
- 🖥️ **悬浮窗显示** — 始终置顶、支持拖拽、全局热键 `Ctrl+F12` 切换显示
- 📂 **一键打开日志** — 设置对话框里直接打开 `aram_debug.log`，免去手动找文件
- 🌐 **中英文切换** — UI 文案和 AI 分析语言
- ♻️ **瞬态错误自动重试** — SSL EOF / 5xx / 限流 / "Post EOF" 等触发自动重试

---

## 🚀 快速开始

### 方式 A：直接下载 `.exe`（推荐，无需装 Python）

1. 前往 [Releases](https://github.com/Zayia/ARAM-tool/releases) 下载 `ARAM-Assistant-v*.exe`
   - 每次 push 都会出一个新的 `v{N}` 版本，标记为 latest
2. **直接双击运行** —— 无需解压
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

浮动按钮栏：`⚡海克斯  |  📋攻略  |  ✏️纠错  |  ⚙️  |  ✕`

| 按钮 | 作用 |
|------|------|
| ⚡ 海克斯 | 截图识别当前 3 选 1，给出选择建议 |
| 📋 攻略 | 显示 / 隐藏全局攻略窗口 |
| ✏️ 纠错 | 英雄识别错了时手动指定英雄名（自动 3 级降级：LCU+AI → 仅 AI 前瞻 → 纯数据查表） |
| ⚙️ | 打开设置对话框（LLM provider、模型、密钥、界面语言、ApexLol 数据缓存、打开日志文件） |
| ✕ | 退出程序 |

**拖拽**：右键按住任意按钮 / 分隔符 / 状态栏拖动整个浮动栏。
**全局热键**：`Ctrl+F12` 切换攻略窗口显示/隐藏（游戏全屏也能触发，由 pynput 系统钩子实现）。
**实时日志**：⚙️ 设置 → 「📂 打开日志文件」直接用记事本打开 `~/.aram_tool/aram_debug.log`。

> 早期版本有「DOS 窗口」复选框和 `🔄 数据`按钮，已分别移除/搬入设置。从命令行 `python main.py` 启动时仍可在终端直接打字输入英雄名触发极速前瞻分析。

---

## 🔧 配置 LLM 提供商

**三种方式**，优先级：**环境变量 > `~/.aram_tool/settings.json` > 代码默认值**

1. **⚙️ UI**（推荐）：浮动栏点 `⚙️` → 填写 → 保存，即时生效
2. **环境变量**：`set LLM_PROVIDER=openai` / `set OPENAI_API_KEY=...` 等
3. **直接改 `config.py` 默认值**（不推荐，易误提交密钥）

完整参数清单、常见场景（LM Studio / Ollama / Azure / 代理）、故障排查见 [CUSTOM_LLM_SETUP.md](CUSTOM_LLM_SETUP.md)。

### 海克斯分析超时（慢网关用户）

默认硬超时：图像分析 20 秒、文字分析 12 秒。慢网关或本地大模型可调高：

```cmd
set HEXTECH_IMAGE_TIMEOUT=30
set HEXTECH_TEXT_TIMEOUT=20
```

或写到 `~/.aram_tool/settings.json`：`{ "hextech_image_timeout": 30, "hextech_text_timeout": 20 }`

---

## 🎲 ApexLol 数据缓存

工具会从 [ApexLol.info](https://apexlol.info) 缓存所有英雄的海克斯符文方案与评级数据，AI 分析时引用，避免推荐截图里没有的符文。

- ⚙️ 设置 → 「ApexLol 数据缓存」区可看到缓存状态（英雄数 / 已更新多久 / 剩余 TTL）+「立即更新缓存」按钮
- 缓存 7 天有效，过期会在启动时自动后台刷新
- 没填 LLM Key 时，✏️ 纠错按钮也能走「纯数据查表模式」给建议

---

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `main.py` | 主入口；浮动按钮栏 + Toplevel 窗口 + LCU 监控线程 + pynput 全局热键 |
| `config.py` | 配置读取（env > settings.json > default），`reload()` 支持 LLM 热重载 |
| `llm_client.py` | 统一 LLM 适配层（Gemini / OpenAI / Custom），重试、连通性测试、模型列表拉取 |
| `gemini_analyzer.py` | 4 种分析模式的业务逻辑（全局 / 极速前瞻 / 海克斯图像 / 海克斯文字），走 `LLMClient` |
| `settings_ui.py` | ⚙️ 设置对话框；保存后自动 `config.reload()`；含 ApexLol 缓存管理与「打开日志文件」入口 |
| `lang.py` | 中英文文案 + 所有 AI prompt 模板 |
| `screenshot.py` | mss 截图模块（裁屏幕中央 70%×70% 减少 token） |
| `apexlol_scraper.py` / `apexlol_data.py` | 爬取 ApexLol.info 数据 + 本地缓存 + 中文别名解析 |
| `lcu_client.py` | LCU API 客户端（从 LoL 客户端进程参数读 token，直接拉阵容） |
| `launch.bat` / `launch_by_uv.bat` | Windows 启动脚本（默认 `pythonw` 无 DOS 窗口） |
| `build.bat` | 本地 PyInstaller 打包脚本（`--noconsole --onefile`） |
| `.github/workflows/release.yml` | CI：每次 push 产出独立 `v{run_number}` 正式版，标 latest，自动清理只保留最新 10 个 |

---

## 🏗️ 自行打包

需要 Windows 环境（PyInstaller 不支持跨平台编译）。

**本地打包**：双击 `build.bat`，产出 `dist\ARAM-Assistant.exe`

**CI 打包**：每次 push 自动打包并发布 `v{run_number}` 正式版（标 latest），自动清理只保留最近 10 个；手动推 `v*.*.*` 语义化 tag 也会单独生成对应 release：
```cmd
git tag -a v1.0.0 -m "release notes"
git push origin v1.0.0
```

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
- 打包版没有 DOS 窗口；想看实时日志可在 ⚙️ 设置里点「📂 打开日志文件」
- `~/.aram_tool/settings.json` 含 API Key 明文，权限 0600（Unix；Windows 上 `chmod` 不生效）
- 多显示器：截图默认抓主显示器（`monitors[1]`），副屏玩游戏会截错地方

---

## 📊 数据来源声明

海克斯符文推荐数据来源于 **[ApexLol.info](https://apexlol.info)**。

- 仅在用户**主动点击 ⚙️ → ApexLol 数据缓存 → 立即更新缓存**或缓存过期时爬取，不无差别自动抓取
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
