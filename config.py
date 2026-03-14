# -*- coding: utf-8 -*-
"""ARAM 助手 - 配置文件"""

import os
import sys

# ==================== 语言配置 ====================
# "zh" = 中文 (Chinese)
# "en" = English
LANGUAGE = "zh"

# ==================== Gemini API 配置 ====================
# 从环境变量读取 API Key（必须设置）
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    from lang import STRINGS
    s = STRINGS.get(LANGUAGE, STRINGS["zh"])
    print(s["api_key_missing"])
    print(s["api_key_method"])
    print(s["api_key_url"])
    sys.exit(1)

GEMINI_MODEL = "gemini-3.1-flash-lite-preview"

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

# 翻译函数
def T(key: str) -> str:
    """根据 LANGUAGE 获取对应语言文本。"""
    return STRINGS.get(LANGUAGE, STRINGS["zh"]).get(key, key)

ANALYSIS_PROMPT = PROMPTS.get(LANGUAGE, PROMPTS["zh"])
