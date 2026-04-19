# 🚀 自定义 LLM 提供商配置指南

本项目支持三种 LLM 后端：官方 Google Gemini、OpenAI 兼容 API、完全自定义的服务。

## 📋 目录

- [快速开始](#快速开始)
- [三种配置方式](#三种配置方式)
- [支持的提供商](#支持的提供商)
- [环境变量完整列表](#环境变量完整列表)
- [常见场景](#常见场景)
- [故障排查](#故障排查)

---

## 快速开始

### ✨ 推荐：点界面里的 ⚙️ 按钮

启动程序后，浮动按钮栏右侧有一个 `⚙️` 按钮。点开 → 选 provider → 填密钥 / 模型 / 端点 → 保存 → **重启**即可。

设置写到 `~/.aram_tool/settings.json`（权限 0600），下次启动自动生效。

### 命令行方式

**官方 Gemini（默认）**
```bash
set GEMINI_API_KEY=your_google_api_key
python main.py
```

**OpenAI 官方**
```bash
set LLM_PROVIDER=openai
set OPENAI_API_KEY=sk-xxxxxxxx
set OPENAI_MODEL=gpt-4
python main.py
```

**本地 LM Studio / Ollama**（需要随便填一个 key，本地服务一般不校验）
```bash
set LLM_PROVIDER=openai
set OPENAI_API_KEY=sk-local
set OPENAI_API_ENDPOINT=http://localhost:8000/v1
set OPENAI_MODEL=mistral
python main.py
```

**完全自定义后端**
```bash
set LLM_PROVIDER=custom
set CUSTOM_API_ENDPOINT=http://your-server:5000/api
set CUSTOM_API_KEY=your_custom_key
set CUSTOM_MODEL=your_model_name
python main.py
```

---

## 三种配置方式

> **配置优先级：环境变量 > `~/.aram_tool/settings.json` > 代码默认值**
> 命令行临时设置会覆盖 UI 保存的设置。

### 方式 A：⚙️ 图形界面（推荐）

1. 启动程序 `python main.py`
2. 浮动按钮栏 → 点 `⚙️`
3. 对话框里：
   - **LLM 提供商**：下拉选 gemini / openai / custom
   - **界面语言**：zh / en
   - 根据所选 provider 填写密钥 / 模型 / 端点
   - 勾选「显示密钥」可明文查看已输入内容
4. 点 **保存** → 弹出提示"请重启应用" → 关闭程序重新启动

设置文件位置：
- Linux / macOS: `~/.aram_tool/settings.json`
- Windows: `C:\Users\<你>\.aram_tool\settings.json`

### 方式 B：环境变量

#### Windows CMD
```cmd
set LLM_PROVIDER=openai
set OPENAI_API_KEY=sk-xxx
set OPENAI_MODEL=gpt-3.5-turbo
python main.py
```

#### Windows PowerShell
```powershell
$env:LLM_PROVIDER="openai"
$env:OPENAI_API_KEY="sk-xxx"
python main.py
```

#### Linux/Mac
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-xxx
python main.py
```

永久生效用 `setx KEY VALUE`（Windows）或写入 `~/.bashrc` / `~/.zshrc`（Unix）。

### 方式 C：直接改 `config.py` 默认值

把 `_pick("XXX", "xxx", "默认值")` 里的**默认值**改掉。缺点：易误把密钥提交到 git。**不推荐**。

---

## 支持的提供商

### 1. Google Gemini（官方）

| 参数 | 环境变量 | settings.json 键 | 默认值 |
|-----|--------|-------|--------|
| Provider | `LLM_PROVIDER` | `llm_provider` | `gemini` |
| API Key | `GEMINI_API_KEY` | `gemini_api_key` | — |
| Model | `GEMINI_MODEL` | `gemini_model` | `gemini-3.1-flash-lite-preview` |
| 代理端点（可选） | `GEN_AI_ENDPOINT` | `gen_ai_endpoint` | — |

获取 API Key：<https://aistudio.google.com/apikey>

### 2. OpenAI 兼容 API

| 参数 | 环境变量 | settings.json 键 | 默认值 |
|-----|--------|-------|--------|
| Provider | `LLM_PROVIDER` | `llm_provider` | — |
| API Key | `OPENAI_API_KEY` | `openai_api_key` | — |
| Model | `OPENAI_MODEL` | `openai_model` | `gpt-3.5-turbo` |
| Endpoint | `OPENAI_API_ENDPOINT` | `openai_api_endpoint` | `https://api.openai.com/v1` |

**支持的服务：**
- OpenAI 官方 API
- Azure OpenAI（endpoint 换成 Azure 的）
- LM Studio（本地）
- Ollama（本地，endpoint `http://localhost:11434/v1`）
- 其他任何走 Chat Completions 协议的服务

> **⚠️ 注意**：`OPENAI_API_KEY` 现在**不再自动豁免**本地端点。LM Studio / Ollama 等本地服务虽然不校验 key，但你仍需填写任意非空字符串（例如 `sk-local`）。

### 3. 自定义后端

| 参数 | 环境变量 | settings.json 键 | 默认值 |
|-----|--------|-------|--------|
| Provider | `LLM_PROVIDER` | `llm_provider` | — |
| API Key | `CUSTOM_API_KEY` | `custom_api_key` | — |
| Model | `CUSTOM_MODEL` | `custom_model` | — |
| Endpoint | `CUSTOM_API_ENDPOINT` | `custom_api_endpoint` | — |

请求格式（`POST {endpoint}`）：
```json
{
  "model": "<CUSTOM_MODEL>",
  "prompt": "<所有文本片段拼接>",
  "temperature": 0.3
}
```

响应解析按以下顺序尝试（取到非空字符串即返回）：
1. `choices[0].message.content`（OpenAI 兼容格式）
2. `choices[0].text`
3. 顶层 `text` / `response` / `output` / `content`

> **⚠️ 自定义后端当前不支持图像**。涉及截图的功能（海克斯选择截图分析）会退化；如需图像支持，请用 `openai` provider 连接一个多模态服务。

---

## 环境变量完整列表

### 通用
```bash
LLM_PROVIDER            # gemini | openai | custom（默认 gemini）
LANGUAGE                # zh | en（默认 zh）
```

### Gemini
```bash
GEMINI_API_KEY          # Google Gemini API 密钥
GEMINI_MODEL            # 默认 gemini-3.1-flash-lite-preview
GEN_AI_ENDPOINT         # 自定义代理端点（可选）
```

### OpenAI 兼容
```bash
OPENAI_API_KEY          # 必填（本地服务可填 sk-local 等任意字符串）
OPENAI_MODEL            # 默认 gpt-3.5-turbo
OPENAI_API_ENDPOINT     # 默认 https://api.openai.com/v1
```

### 自定义后端
```bash
CUSTOM_API_KEY          # 可选（若后端需要鉴权）
CUSTOM_MODEL            # 模型名
CUSTOM_API_ENDPOINT     # 完整 API 端点地址（必填）
```

---

## 常见场景

### 场景 1：LM Studio 本地模型

1. 下载安装 LM Studio：<https://lmstudio.ai/>
2. LM Studio 内下载模型（如 Mistral 7B Instruct）
3. 点 "Start Server"，默认地址 `http://localhost:8000`
4. 配 ARAM-tool（任选）：
   - **⚙️ UI**：Provider 选 `openai`，API Key 填 `sk-local`，Endpoint 填 `http://localhost:8000/v1`，Model 填 `mistral`
   - **命令行**：
     ```cmd
     set LLM_PROVIDER=openai
     set OPENAI_API_KEY=sk-local
     set OPENAI_API_ENDPOINT=http://localhost:8000/v1
     set OPENAI_MODEL=mistral
     python main.py
     ```

### 场景 2：Ollama 本地模型

1. 安装 Ollama：<https://ollama.ai/>
2. 拉模型并启动：
   ```bash
   ollama pull mistral
   ollama serve
   ```
3. 配 ARAM-tool（端点 `http://localhost:11434/v1`，key 填 `sk-local`）

### 场景 3：OpenAI 官方

```cmd
set LLM_PROVIDER=openai
set OPENAI_API_KEY=sk-your-actual-key
set OPENAI_MODEL=gpt-4
python main.py
```

### 场景 4：自建 API 服务

```cmd
set LLM_PROVIDER=custom
set CUSTOM_API_ENDPOINT=http://192.168.1.100:5000/api
set CUSTOM_API_KEY=your_secret_key
set CUSTOM_MODEL=your-model-name
python main.py
```

### 场景 5：通过代理访问 Gemini

```cmd
set LLM_PROVIDER=gemini
set GEMINI_API_KEY=your_google_key
set GEN_AI_ENDPOINT=http://proxy-server:8080/gemini/
python main.py
```

---

## 故障排查

### 问题 1：`LLM 提供商 [xxx] 配置不完整`

启动时控制台出现这行警告，说明 provider 对应的必填项没给齐：
- `gemini` → 检查 `GEMINI_API_KEY`（必须以 `AIza` 开头）
- `openai` → 检查 `OPENAI_API_KEY` 和 `OPENAI_API_ENDPOINT`
- `custom` → 检查 `CUSTOM_API_ENDPOINT`

AI 功能会被禁用，但 🔄 数据爬取 + ✏️ 纯数据查表模式仍可用。

### 问题 2：连接超时

- 网络是否通？
- 端点 URL 是否正确？本地服务是否已启动？
- 某些本地代理启动需要几秒，等几秒再试
- Linux / macOS 下 `localhost` 和 `127.0.0.1` 偶尔不一样，换一个试试

### 问题 3：401 / 403 认证失败

- API Key 拼错了
- Key 权限不足
- 本地服务虽然不校验，但现在也需要任意非空字符串（填 `sk-local` 即可）

### 问题 4：404 或 "model not found"

- 模型名拼错了
- 本地服务里没下载该模型
- OpenAI 账户没开通该模型权限

### 问题 5：修改 UI 设置后不生效

设置需要**重启应用**才生效——`config.py` 在启动时读取一次，`LLMClient` 是模块级单例。

---

## 💡 性能对比

| 提供商 | 速度 | 成本 | 质量 | 本地 |
|------|------|------|------|------|
| Gemini Flash | ⚡⚡ 快 | 💰 免费 | ⭐⭐⭐⭐ | ❌ |
| GPT-4 | ⚡ 一般 | 💰💰💰 贵 | ⭐⭐⭐⭐⭐ | ❌ |
| GPT-3.5 | ⚡⚡ 很快 | 💰💰 中等 | ⭐⭐⭐⭐ | ❌ |
| Mistral (本地) | ⚡⚡⚡ 极快 | ✅ 免费 | ⭐⭐⭐ | ✅ |
| Llama 3 (本地) | ⚡⚡⚡ 极快 | ✅ 免费 | ⭐⭐⭐⭐ | ✅ |

> **注意**：海克斯选择分析需要多模态（图像理解）能力。Gemini / GPT-4o 等多模态模型效果最好；纯文本模型（本地 Mistral / Llama）会退化到 OCR + 文本方案。

---

## 📞 支持

有问题或建议欢迎提 Issue：<https://github.com/Zayia/ARAM-tool/issues>
