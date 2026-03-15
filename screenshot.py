# -*- coding: utf-8 -*-
"""ARAM 助手 - 截图模块"""

import os
import io
import time
import mss
from PIL import Image
from config import SCREENSHOT_DIR


def capture_screen() -> tuple[bytes, str]:
    """
    截取主显示器全屏，压缩为 JPEG。

    Returns:
        tuple: (jpeg_bytes, file_path) - JPEG 格式的字节数据和保存路径
    """
    with mss.mss() as sct:
        # 获取主显示器
        monitor = sct.monitors[1]

        # 截图
        screenshot = sct.grab(monitor)

        # 转为 PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        # 缩放（仅超大分辨率才缩放，保证文字清晰）
        w, h = img.size
        if w > 1920:
            ratio = 1920 / w
            img = img.resize((1920, int(h * ratio)), Image.LANCZOS)

        # 压缩为 JPEG（质量 85，兼顾体积和文字清晰度）
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85, optimize=True)
        jpeg_bytes = buf.getvalue()

        # 保存一份到磁盘（调试用）
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"aram_{timestamp}.jpg"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(jpeg_bytes)

        print(f"[截图] {w}x{h} → {img.size[0]}x{img.size[1]}, {len(jpeg_bytes)//1024}KB, {filepath}")
        return jpeg_bytes, filepath


def capture_hextech_cards() -> tuple[bytes, str]:
    """
    仅截取海克斯选择卡片区域 (大致在屏幕中间区域)。
    裁剪掉顶部记分板和底部UI，极大降低图片大小和 AI 的 Token 消耗，追求极限速度。
    """
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        w, h = img.size
        # 裁剪比例经验值 (去除顶部25%，底部25%，左侧15%，右侧15%)
        left = int(w * 0.15)
        top = int(h * 0.25)
        right = int(w * 0.85)
        bottom = int(h * 0.75)
        img = img.crop((left, top, right, bottom))
        
        # 对裁剪后的图片做极限缩放
        cw, ch = img.size
        if cw > 1280:
            ratio = 1280 / cw
            img = img.resize((1280, int(ch * ratio)), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80, optimize=True)
        jpeg_bytes = buf.getvalue()

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"hextech_{timestamp}.jpg"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(jpeg_bytes)

        print(f"[海克斯裁切] {w}x{h} → {img.size[0]}x{img.size[1]}, {len(jpeg_bytes)//1024}KB, {filepath}")
        return jpeg_bytes, filepath


if __name__ == "__main__":
    # 测试截图功能
    data, path = capture_screen()
    print(f"截图大小: {len(data)//1024} KB")
    print(f"保存位置: {path}")
