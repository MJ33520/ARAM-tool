# -*- coding: utf-8 -*-
"""ARAM 助手 - 配置文件 (模板)"""

import os
import sys

# ==================== 语言配置 ====================
# "zh" = 中文 (Chinese)
# "en" = English
LANGUAGE = "zh"

# ==================== Gemini API 配置 ====================
# 从环境变量或此处填写的字符串读取 API Key
# 建议通过系统环境变量设置 GEMINI_API_KEY
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

if GEMINI_API_KEY == "YOUR_API_KEY_HERE" or not GEMINI_API_KEY:
    # 如果没设置环境变量也没填这里的占位符，会报错
    # 但是对于 GitHub 发布，这里必须是空的/占位符
    pass

GEMINI_MODEL = "gemini-2.5-pro"

# ==================== 热键配置 ====================
TOGGLE_HOTKEY = "Ctrl+F12"    # 切换悬浮窗显示/隐藏

# ==================== UI 配置 ====================
OVERLAY_BG_COLOR = "#1a1a2e"
OVERLAY_FG_COLOR = "#e0e0e0"
OVERLAY_ACCENT_COLOR = "#00d4ff"
OVERLAY_TITLE_COLOR = "#ffd700"
OVERLAY_WIDTH = 520
OVERLAY_MAX_HEIGHT = 750
OVERLAY_FONT_FAMILY = "Microsoft YaHei UI"
OVERLAY_FONT_SIZE = 11
OVERLAY_OPACITY = 0.92

# ==================== 截图配置 ====================
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")

# ==================== ApexLol 数据增强 ====================
APEXLOL_ENABLED = True                 
APEXLOL_CACHE_DIR = os.path.join(os.path.dirname(__file__), "apexlol_cache")
APEXLOL_CACHE_TTL_DAYS = 7             
