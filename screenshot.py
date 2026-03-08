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


if __name__ == "__main__":
    # 测试截图功能
    data, path = capture_screen()
    print(f"截图大小: {len(data)//1024} KB")
    print(f"保存位置: {path}")
