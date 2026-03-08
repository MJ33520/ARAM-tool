# -*- coding: utf-8 -*-
"""ARAM 助手 - Gemini API 分析模块"""

from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL, ANALYSIS_PROMPT


# 初始化客户端
client = genai.Client(api_key=GEMINI_API_KEY)


def analyze_screenshot(png_bytes: bytes) -> str:
    """
    将截图发送给 Gemini 进行分析，返回推荐文本。

    Args:
        png_bytes: PNG 格式的截图字节数据

    Returns:
        str: Gemini 返回的分析和推荐文本
    """
    try:
        print("[分析] 正在发送截图给 Gemini...")

        prompt = ANALYSIS_PROMPT

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(
                    data=png_bytes,
                    mime_type="image/jpeg",
                ),
                prompt,
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=2048,
                ),
                temperature=0.5,
            ),
        )

        result = response.text
        print("[分析] Gemini 分析完成")
        return result

    except Exception as e:
        error_msg = f"❌ Gemini API 调用失败: {str(e)}"
        print(f"[错误] {error_msg}")
        return error_msg


if __name__ == "__main__":
    # 测试：用截图目录中最新的截图进行分析
    import os
    from config import SCREENSHOT_DIR

    files = sorted(
        [f for f in os.listdir(SCREENSHOT_DIR) if f.endswith(".png")],
        reverse=True,
    )

    if files:
        latest = os.path.join(SCREENSHOT_DIR, files[0])
        print(f"使用截图: {latest}")
        with open(latest, "rb") as f:
            data = f.read()
        result = analyze_screenshot(data)
        print("\n" + "=" * 60)
        print(result)
    else:
        print("截图目录为空，请先运行 screenshot.py 获取截图")
