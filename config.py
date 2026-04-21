# -*- coding: utf-8 -*-
"""ARAM 助手 - 配置文件

支持三种 LLM 提供商，通过 LLM_PROVIDER 切换：
- gemini: 官方 Google Gemini（默认，需 GEMINI_API_KEY）
- openai: OpenAI 兼容 API（OpenAI 官方 / Azure / 自建 OpenAI 协议服务）
- custom: 自定义后端

配置优先级：环境变量 > 用户设置文件 > 代码默认值
用户设置文件：~/.aram_tool/settings.json（可由 ⚙️ 设置界面写入）
"""

import json
import os
import sys

# ==================== 用户设置文件 ====================
USER_SETTINGS_DIR = os.path.join(os.path.expanduser("~"), ".aram_tool")
USER_SETTINGS_PATH = os.path.join(USER_SETTINGS_DIR, "settings.json")


def _load_user_settings() -> dict:
    if not os.path.exists(USER_SETTINGS_PATH):
        return {}
    try:
        with open(USER_SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


_USER = _load_user_settings()


def _clean(v: str) -> str:
    """清除不可见字符 (BOM, 零宽字符, 各种引号和空白符)。"""
    return (v or "").strip(' \t\n\r"\'\u201c\u201d\ufeff\u200b')


def _pick(env_key: str, settings_key: str, default: str = "") -> str:
    """按 env > settings > default 优先级读取配置值（自动去不可见字符）。"""
    v = os.environ.get(env_key)
    if v:
        return _clean(v)
    sv = _USER.get(settings_key)
    if sv:
        return _clean(str(sv))
    return default


def _pick_bool(env_key: str, settings_key: str, default: bool = True) -> bool:
    """按 env > settings > default 读 bool 值。env 接受 true/false/1/0/yes/no/on/off。"""
    v = os.environ.get(env_key)
    if v is not None and v.strip():
        return v.strip().lower() in ("true", "1", "yes", "on")
    sv = _USER.get(settings_key)
    if isinstance(sv, bool):
        return sv
    if isinstance(sv, str) and sv.strip():
        return sv.strip().lower() in ("true", "1", "yes", "on")
    return default


# ==================== 语言配置 ====================
# "zh" = 中文 (Chinese)  "en" = English
LANGUAGE = _pick("LANGUAGE", "language", "zh").lower() or "zh"

# ==================== LLM 提供商选择 ====================
# 可选：gemini | openai | custom
LLM_PROVIDER = _pick("LLM_PROVIDER", "llm_provider", "gemini").lower() or "gemini"

# ==================== Gemini 配置 ====================
GEMINI_API_KEY = _pick("GEMINI_API_KEY", "gemini_api_key", "")
GEMINI_MODEL = _pick("GEMINI_MODEL", "gemini_model", "gemini-3.1-flash-lite-preview")
# 可选代理端点（为空则用官方 SDK 默认）
GEN_AI_ENDPOINT = _pick("GEN_AI_ENDPOINT", "gen_ai_endpoint", "")

# ==================== OpenAI 兼容配置 ====================
OPENAI_API_KEY = _pick("OPENAI_API_KEY", "openai_api_key", "")
OPENAI_MODEL = _pick("OPENAI_MODEL", "openai_model", "gpt-3.5-turbo")
OPENAI_API_ENDPOINT = _pick("OPENAI_API_ENDPOINT", "openai_api_endpoint", "https://api.openai.com/v1").rstrip("/")

# ==================== 自定义后端配置 ====================
CUSTOM_API_KEY = _pick("CUSTOM_API_KEY", "custom_api_key", "")
CUSTOM_MODEL = _pick("CUSTOM_MODEL", "custom_model", "")
CUSTOM_API_ENDPOINT = _pick("CUSTOM_API_ENDPOINT", "custom_api_endpoint", "").rstrip("/")

# ==================== 控制台（DOS 窗口）显隐 ====================
# 启动时显示 Windows cmd/控制台窗口；False 则隐藏（适合打包成桌面快捷方式）
SHOW_CONSOLE = _pick_bool("SHOW_CONSOLE", "show_console", True)


# ==================== 配置校验 ====================
def _check_llm_config():
    """返回 (enabled, reason)。enabled=False 时 reason 说明缺什么。"""
    if LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            return False, "GEMINI_API_KEY 未设置"
        if not GEMINI_API_KEY.startswith("AIza"):
            return False, "GEMINI_API_KEY 格式看起来不对（应以 AIza 开头）"
        return True, None
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            return False, "OPENAI_API_KEY 未设置"
        if not OPENAI_API_ENDPOINT:
            return False, "OPENAI_API_ENDPOINT 未设置"
        return True, None
    if LLM_PROVIDER == "custom":
        if not CUSTOM_API_ENDPOINT:
            return False, "CUSTOM_API_ENDPOINT 未设置"
        return True, None
    return False, f"未知 LLM_PROVIDER: {LLM_PROVIDER}"


_llm_ok, _llm_reason = _check_llm_config()
LLM_ENABLED = _llm_ok

if not LLM_ENABLED:
    print("\n" + "=" * 50)
    print(f"\u26a0\ufe0f  LLM 提供商 [{LLM_PROVIDER}] 配置不完整: {_llm_reason}")
    print("   仍可使用：\U0001f504 数据爬取 + \u270f\ufe0f 纯数据查表模式")
    print("   可点界面 \u2699\ufe0f 设置按钮填写密钥，或参考 CUSTOM_LLM_SETUP.md")
    print("=" * 50 + "\n")


# ==================== 热重载 ====================
# LLM 相关键：会被 reload() 重新计算；语言/UI 相关改动仍需重启
_RELOADABLE_KEYS = (
    "LLM_PROVIDER",
    "GEMINI_API_KEY", "GEMINI_MODEL", "GEN_AI_ENDPOINT",
    "OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_API_ENDPOINT",
    "CUSTOM_API_KEY", "CUSTOM_MODEL", "CUSTOM_API_ENDPOINT",
    "SHOW_CONSOLE",
)


def reload() -> dict:
    """重新读取 ~/.aram_tool/settings.json 并更新模块级 LLM 配置。

    返回发生变化的键集合：{key: (old_value, new_value), ...}。
    语言（LANGUAGE）不在热重载范围内——即使被改，也只记录变化，
    不会立即影响已渲染的 tkinter 控件文案；调用方应据此提示用户"需重启"。
    """
    global _USER, LLM_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL, GEN_AI_ENDPOINT
    global OPENAI_API_KEY, OPENAI_MODEL, OPENAI_API_ENDPOINT
    global CUSTOM_API_KEY, CUSTOM_MODEL, CUSTOM_API_ENDPOINT
    global LANGUAGE, LLM_ENABLED, SHOW_CONSOLE

    old = {k: globals()[k] for k in (_RELOADABLE_KEYS + ("LANGUAGE",))}

    _USER = _load_user_settings()

    LANGUAGE = _pick("LANGUAGE", "language", "zh").lower() or "zh"
    LLM_PROVIDER = _pick("LLM_PROVIDER", "llm_provider", "gemini").lower() or "gemini"
    GEMINI_API_KEY = _pick("GEMINI_API_KEY", "gemini_api_key", "")
    GEMINI_MODEL = _pick("GEMINI_MODEL", "gemini_model", "gemini-3.1-flash-lite-preview")
    GEN_AI_ENDPOINT = _pick("GEN_AI_ENDPOINT", "gen_ai_endpoint", "")
    OPENAI_API_KEY = _pick("OPENAI_API_KEY", "openai_api_key", "")
    OPENAI_MODEL = _pick("OPENAI_MODEL", "openai_model", "gpt-3.5-turbo")
    OPENAI_API_ENDPOINT = _pick("OPENAI_API_ENDPOINT", "openai_api_endpoint",
                                 "https://api.openai.com/v1").rstrip("/")
    CUSTOM_API_KEY = _pick("CUSTOM_API_KEY", "custom_api_key", "")
    CUSTOM_MODEL = _pick("CUSTOM_MODEL", "custom_model", "")
    CUSTOM_API_ENDPOINT = _pick("CUSTOM_API_ENDPOINT", "custom_api_endpoint", "").rstrip("/")
    SHOW_CONSOLE = _pick_bool("SHOW_CONSOLE", "show_console", True)

    ok, _ = _check_llm_config()
    LLM_ENABLED = ok

    new = {k: globals()[k] for k in (_RELOADABLE_KEYS + ("LANGUAGE",))}
    return {k: (old[k], new[k]) for k in old if old[k] != new[k]}

# ==================== 热键配置 ====================
TOGGLE_HOTKEY = "Ctrl+F12"    # 切换悬浮窗显示/隐藏（全局热键，游戏中可用）

# ==================== UI 配置 ====================
OVERLAY_BG_COLOR = "#1a1a2e"       # 悬浮窗背景色（深蓝黑）
OVERLAY_FG_COLOR = "#e0e0e0"       # 悬浮窗前景色（浅灰白）
OVERLAY_ACCENT_COLOR = "#00d4ff"   # 强调色（亮青色）
OVERLAY_TITLE_COLOR = "#ffd700"    # 标题色（金色）
OVERLAY_WIDTH = 520                # 悬浮窗宽度
OVERLAY_MAX_HEIGHT = 750           # 悬浮窗最大高度
OVERLAY_FONT_FAMILY = "Microsoft YaHei UI"  # 字体
OVERLAY_FONT_SIZE = 11             # 字体大小
OVERLAY_OPACITY = 0.92             # 窗口不透明度 (0.0 ~ 1.0)

# ==================== 截图配置 ====================
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ==================== ApexLol 数据增强 ====================
APEXLOL_ENABLED = True                 # 是否启用 apexlol.info 数据增强
APEXLOL_CACHE_DIR = os.path.join(os.path.dirname(__file__), "apexlol_cache")
APEXLOL_CACHE_TTL_DAYS = 7             # 缓存过期天数
os.makedirs(APEXLOL_CACHE_DIR, exist_ok=True)

# ==================== Prompt 配置 ====================
from lang import STRINGS, PROMPTS


def T(key: str) -> str:
    """根据 LANGUAGE 获取对应语言文本。"""
    return STRINGS.get(LANGUAGE, STRINGS["zh"]).get(key, key)


ANALYSIS_PROMPT = PROMPTS.get(LANGUAGE, PROMPTS["zh"])
