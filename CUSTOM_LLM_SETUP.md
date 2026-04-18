# 🚀 自定义 LLM 提供商配置指南

本项目现已支持多个 LLM 提供商，包括官方 Google Gemini、OpenAI 兼容 API、以及完全自定义的后端服务。

## 📋 目录

- [快速开始](#快速开始)
- [配置方式](#配置方式)
- [支持的提供商](#支持的提供商)
- [环境变量完整列表](#环境变量完整列表)
- [常见场景](#常见场景)

---

## 快速开始

### 方式 1️⃣ 官方 Google Gemini（默认）

```bash
set GEMINI_API_KEY=your_google_api_key
python main.py
```

### 方式 2️⃣ OpenAI 兼容 API

```bash
set LLM_PROVIDER=openai
set OPENAI_API_KEY=your_openai_key
set OPENAI_MODEL=gpt-3.5-turbo
python main.py
```

### 方式 3️⃣ 本地代理（LM Studio）

```bash
set LLM_PROVIDER=openai
set OPENAI_API_ENDPOINT=http://localhost:8000/v1
set OPENAI_MODEL=mistral
python main.py
```

### 方式 4️⃣ 完全自定义后端

```bash
set LLM_PROVIDER=custom
set CUSTOM_API_ENDPOINT=http://your-server:5000/api
set CUSTOM_API_KEY=your_custom_key
set CUSTOM_MODEL=your_model_name
python main.py
```

---

## 配置方式

### 📍 方式 A：环境变量（推荐）

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
$env:OPENAI_MODEL="gpt-3.5-turbo"
python main.py
```

#### Linux/Mac
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-xxx
export OPENAI_MODEL=gpt-3.5-turbo
python main.py
```

### 📍 方式 B：直接修改 config.py

编辑 `config.py` 文件中的以下配置：

```python
# config.py

# 选择提供商
LLM_PROVIDER = "openai"  # 或 "gemini" / "custom"

# 对应提供商的配置
OPENAI_API_KEY = "your_api_key"
OPENAI_API_ENDPOINT = "http://localhost:8000/v1"
OPENAI_MODEL = "mistral"
```

---

## 支持的提供商

### 1. Google Gemini（官方）

| 参数 | 环境变量 | 默认值 |
|-----|--------|--------|
| Provider | `LLM_PROVIDER` | `gemini` |
| API Key | `GEMINI_API_KEY` | 从环境变量读取 |
| Model | `GEMINI_MODEL` | `gemini-3.1-flash-lite-preview` |
| Endpoint | `GEN_AI_ENDPOINT` | `https://generativelanguage.googleapis.com/v1beta/models/` |

获取 API Key：https://aistudio.google.com/apikey

### 2. OpenAI 兼容 API

| 参数 | 环境变量 | 默认值 |
|-----|--------|--------|
| Provider | `LLM_PROVIDER` | `openai` |
| API Key | `OPENAI_API_KEY` | - |
| Model | `OPENAI_MODEL` | `gpt-3.5-turbo` |
| Endpoint | `OPENAI_API_ENDPOINT` | `https://api.openai.com/v1` |

**支持的服务：**
- OpenAI 官方 API
- Azure OpenAI
- LM Studio（本地）
- Ollama（本地）
- 其他 OpenAI 兼容服务

### 3. 自定义后端

| 参数 | 环境变量 | 默认值 |
|-----|--------|--------|
| Provider | `LLM_PROVIDER` | `custom` |
| API Key | `CUSTOM_API_KEY` | - |
| Model | `CUSTOM_MODEL` | - |
| Endpoint | `CUSTOM_API_ENDPOINT` | - |

---

## 环境变量完整列表

### Gemini 相关
```bash
GEMINI_API_KEY          # Google Gemini API 密钥
GEMINI_MODEL            # Gemini 模型名（默认：gemini-3.1-flash-lite-preview）
GEN_AI_ENDPOINT         # 自定义 Gemini 代理端点（可选）
```

### OpenAI 相关
```bash
OPENAI_API_KEY          # OpenAI API 密钥
OPENAI_MODEL            # 使用的模型（默认：gpt-3.5-turbo）
OPENAI_API_ENDPOINT     # API 端点地址（默认：https://api.openai.com/v1）
```

### 自定义后端相关
```bash
CUSTOM_API_KEY          # 自定义后端 API 密钥
CUSTOM_MODEL            # 模型名称
CUSTOM_API_ENDPOINT     # 完整 API 端点地址
```

### 其他
```bash
LLM_PROVIDER            # LLM 提供商：gemini | openai | custom
LANGUAGE                # 界面语言：zh | en
```

---

## 常见场景

### 场景 1：使用 LM Studio 本地模型

1. **下载并安装 LM Studio**
   - 访问：https://lmstudio.ai/
   - 安装并启动

2. **在 LM Studio 中下载一个模型**
   - 例如：Mistral 7B Instruct

3. **启动本地服务器**
   - LM Studio 中点击 "Start Server"
   - 默认地址：`http://localhost:8000`

4. **配置 ARAM-tool**
   ```bash
   set LLM_PROVIDER=openai
   set OPENAI_API_ENDPOINT=http://localhost:8000/v1
   set OPENAI_MODEL=mistral
   python main.py
   ```

### 场景 2：使用 Ollama 本地模型

1. **安装 Ollama**
   - 访问：https://ollama.ai/
   - 下载并安装

2. **拉取一个模型**
   ```bash
   ollama pull mistral
   ollama serve
   ```

3. **配置 ARAM-tool**
   ```bash
   set LLM_PROVIDER=openai
   set OPENAI_API_ENDPOINT=http://localhost:11434/v1
   set OPENAI_MODEL=mistral
   python main.py
   ```

### 场景 3：使用 OpenAI 官方 API

```bash
set LLM_PROVIDER=openai
set OPENAI_API_KEY=sk-your-actual-key
set OPENAI_MODEL=gpt-4
python main.py
```

### 场景 4：使用自建 API 服务

假设你有一个自建的 API 服务运行在 `http://192.168.1.100:5000`

```bash
set LLM_PROVIDER=custom
set CUSTOM_API_ENDPOINT=http://192.168.1.100:5000/api
set CUSTOM_API_KEY=your_secret_key
set CUSTOM_MODEL=your-model-name
python main.py
```

### 场景 5：通过代理访问 Gemini

如果你需要使用代理访问 Google Gemini：

```bash
set LLM_PROVIDER=gemini
set GEMINI_API_KEY=your_google_key
set GEN_AI_ENDPOINT=http://proxy-server:8080/gemini/
python main.py
```

---

## 🔍 故障排查

### 问题 1：连接超时

**症状：** 程序卡住或报超时错误

**解决方案：**
- 检查网络连接
- 确认 API 端点地址正确
- 检查本地代理是否已启动（如使用 LM Studio）
- 增加超时时间设置

### 问题 2：认证失败

**症状：** 401 或 403 错误

**解决方案：**
- 检查 API Key 是否正确
- 确认 API Key 有相应权限
- 对于本地代理（LM Studio/Ollama），通常不需要 Key

### 问题 3：模型不存在

**症状：** 404 或"model not found"错误

**解决方案：**
- 确认模型名拼写正确
- 确认模型已下载（对于本地服务）
- 查看官方文档获取支持的模型列表

### 问题 4：API 端点错误

**症状：** "Connection refused" 或 "Invalid endpoint"

**解决方案：**
- 检查端点 URL 是否以 `/` 结尾
- 确认服务器已启动
- 检查防火墙设置
- 尝试使用 `localhost` 而非 `127.0.0.1`（或反之）

---

## 💡 性能对比

| 提供商 | 速度 | 成本 | 质量 | 离线 |
|------|------|------|------|------|
| Gemini | ⚡ 快 | 💰 免费 | ⭐⭐⭐⭐ | ❌ |
| GPT-4 | ⚡ 快 | 💰💰💰 贵 | ⭐⭐⭐⭐⭐ | ❌ |
| GPT-3.5 | ⚡⚡ 很快 | 💰💰 中等 | ⭐⭐⭐⭐ | ❌ |
| Mistral | ⚡⚡⚡ 极快 | ✅ 免费 | ⭐⭐⭐ | ✅ |
| Llama 2 | ⚡⚡⚡ 极快 | ✅ 免费 | ⭐⭐⭐ | ✅ |

---

## 📞 支持

如遇到问题或有改进建议，欢迎提交 Issue！