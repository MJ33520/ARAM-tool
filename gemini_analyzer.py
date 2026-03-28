# -*- coding: utf-8 -*-
"""ARAM 助手 - Gemini API 分析模块

分析模式：
1. 全局分析：加载界面截图 → 完整攻略（单次API调用，ApexLol数据直接注入）
2. 海克斯选择：海克斯界面截图 → 快速选择建议
3. 全局更新：根据已选海克斯更新全局攻略
"""

import json
import logging
import time as _time
import ssl
import concurrent.futures
from google import genai
from google.genai import types
from config import (
    GEMINI_API_KEY, GEMINI_MODEL, ANALYSIS_PROMPT,
    APEXLOL_ENABLED, APEXLOL_CACHE_DIR, LANGUAGE,
)

log = logging.getLogger("ARAM")

# 初始化客户端
client = genai.Client(api_key=GEMINI_API_KEY)

# ==================== SSL EOF / 超时 自动重试 ====================
MAX_RETRIES = 2       # 最多重试2次（共3次尝试）
RETRY_DELAY = 1.0     # 重试前等待秒数


def _is_retryable(exc: Exception) -> bool:
    """判断是否为可重试的瞬态错误（SSL EOF / 超时）。"""
    msg = str(exc).lower()
    return ("unexpected_eof" in msg or "ssleoferror" in msg 
            or "eof occurred" in msg or isinstance(exc, concurrent.futures.TimeoutError))


def _call_with_retry(*, model, contents, config, label="API", hard_timeout: float = None):
    """带自动重试的 Gemini API 调用封装。
    
    支持两种重试触发：
    1. SSL EOF 等瞬态网络错误
    2. hard_timeout 硬超时（秒）— 超时则中断当前请求并重试
    """
    last_exc = None
    for attempt in range(1 + MAX_RETRIES):
        try:
            if hard_timeout:
                # 用线程池实现硬超时
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(
                        client.models.generate_content,
                        model=model, contents=contents, config=config,
                    )
                    return future.result(timeout=hard_timeout)
            else:
                return client.models.generate_content(
                    model=model, contents=contents, config=config,
                )
        except Exception as e:
            if _is_retryable(e) and attempt < MAX_RETRIES:
                last_exc = e
                reason = "超时" if isinstance(e, (concurrent.futures.TimeoutError, TimeoutError)) else "SSL EOF"
                log.warning(f"[{label}] {reason} ({attempt+1}/{MAX_RETRIES})，{RETRY_DELAY}s 后重试...")
                _time.sleep(RETRY_DELAY)
            else:
                raise
    raise last_exc  # 不应到达，保险兜底



def analyze_champion_quick_guide(champion_name: str) -> str:
    """开局前极速前瞻分析：终端输英雄名 → 数据驱动的海克斯+AI出装（纯文本，无需截图）。"""
    try:
        from lang import QUICK_GUIDE_PROMPTS
        log.info(f"[Gemini] 极速前瞻分析 ({champion_name})...")
        
        # ====== 数据驱动：直接从 ApexLol 硬抽符文方案 ======
        prefilled_augments = ""
        if APEXLOL_ENABLED:
            from apexlol_data import extract_top_synergies
            prefilled_augments = extract_top_synergies(champion_name)
            if prefilled_augments:
                log.info(f"[ApexLol] 已从数据库直接提取符文方案 ({len(prefilled_augments)} 字符)")
        
        prompt = QUICK_GUIDE_PROMPTS.get(LANGUAGE, QUICK_GUIDE_PROMPTS["zh"]).format(
            champion_name=champion_name,
            prefilled_augments=prefilled_augments if prefilled_augments else "（无数据，请根据英雄特性自行推荐3套海克斯符文方案）"
        )

        import time
        t_start = time.time()
        response = _call_with_retry(
            model=GEMINI_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(
                temperature=0.3,
            ),
            label="极速前瞻",
        )
        log.info(f"[Gemini] 极速前瞻分析完成 ({time.time()-t_start:.1f}s)")
        
        # 100% 防御幻觉：由代码直接拼接，绝不指望 AI "原样复述"
        final_output = ""
        if prefilled_augments:
            final_output += prefilled_augments + "\n\n---\n\n"
        final_output += response.text
        
        return final_output

    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        error_msg = f"❌ 极速前瞻失败: {str(e)}\n\n{trace}"
        log.error(error_msg)
        return error_msg


def analyze_lcu_rosters(rosters: dict, hextech_history: list[str] = None) -> str:
    """跳过截图，完全基于 LCU 获取的 10 人阵容进行极速全局全量分析。"""
    try:
        from lang import LCU_FULL_STRATEGY_PROMPTS
        
        my_champion = rosters.get("my_champion", "未知英雄")
        lcu_rosters = rosters.get("live_context", "")
        
        # ====== 数据驱动：直接从 ApexLol 硬抽该英雄的核心符文方案 ======
        prefilled_augments = ""
        if APEXLOL_ENABLED:
            from apexlol_data import extract_top_synergies
            prefilled_augments = extract_top_synergies(my_champion)
            if prefilled_augments:
                log.info(f"[ApexLol] LCU分析已附加 {my_champion} 的海克斯数据 ({len(prefilled_augments)} 字符)")
                
        log.info(f"[Gemini] 纯数据级全局分析 ({my_champion})...")
        prompt = LCU_FULL_STRATEGY_PROMPTS.get(LANGUAGE, LCU_FULL_STRATEGY_PROMPTS["zh"]).format(
            my_champion=my_champion,
            lcu_rosters=lcu_rosters,
            prefilled_augments=prefilled_augments if prefilled_augments else "（无数据，请基于知识推荐3套最强海克斯符文方案）"
        )
        
        # 注入海克斯历史
        if hextech_history:
            history_str = "、".join(hextech_history)
            prompt = f"📜【本局已选海克斯符文历史】: {history_str}\n" + prompt
            log.info(f"[Gemini] 已注入海克斯历史 ({len(hextech_history)}个)")


        import time
        t_start = time.time()
        # 纯文本请求
        response = _call_with_retry(
            model=GEMINI_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(
                temperature=0.4, # 兼顾稳定与战术变化
            ),
            label="纯文本全量分析",
        )
        log.info(f"[Gemini] 纯数据全量分析完成 ({time.time()-t_start:.1f}s)")
        
        # 与极速前瞻一样，强制将 Apexlol 数据拼在最前面
        final_output = ""
        if prefilled_augments:
            final_output += prefilled_augments + "\n\n---\n\n"
        final_output += response.text
        
        return final_output

    except Exception as e:
        error_msg = f"❌ LCU 全量分析失败: {str(e)}"
        log.error(error_msg)
        return error_msg





def analyze_hextech_choice(png_bytes: bytes, global_context: str,
                           hextech_history: list[str], champion_name: str = None) -> str:
    """海克斯选择分析：截图中的3个选项 → 推荐选哪个。"""
    try:
        from lang import HEXTECH_PROMPTS
        log.info(f"[Gemini] 海克斯选择分析 (英雄: {champion_name})...")
        
        history_str = "、".join(hextech_history) if hextech_history else "无"
        
        # 注入该英雄的高胜率符文列表辅助 AI 识别 (2026-03-14 优化)
        prefilled_augments = ""
        if champion_name and APEXLOL_ENABLED:
            from apexlol_data import extract_top_synergies
            prefilled_augments = extract_top_synergies(champion_name)
            if prefilled_augments:
                log.info(f'[海克斯] 为 {champion_name} 注入高胜率"对照表"，增强识别能力')

        prompt = HEXTECH_PROMPTS.get(LANGUAGE, HEXTECH_PROMPTS["zh"]).format(
            hextech_history=history_str,
        )
        
        # 极速模式：只靠截图+对照表+历史，不注入全局攻略摘要
        
        api_contents = [types.Part.from_bytes(data=png_bytes, mime_type="image/jpeg")]
        if prefilled_augments:
            # 物理注入对照表
            api_contents.append(f"🚀【实时建议背景】该英雄的高胜率海克斯名单如下：\n{prefilled_augments}\n\n⚠️ 如果截图中的 3 个选项有命中以上名单的，请给予最高优先级的推荐权重！")
        api_contents.append(prompt)

        response = _call_with_retry(
            model=GEMINI_MODEL,
            contents=api_contents,
            config=types.GenerateContentConfig(temperature=0.2),
            label="海克斯",
            hard_timeout=8.0,  # 8秒硬超时，超时自动重试
        )
        log.info("[Gemini] 海克斯选择分析完成")
        return response.text
    except Exception as e:
        return f"❌ 海克斯分析失败: {str(e)}"





if __name__ == "__main__":
    # 测试：用截图目录中最新的截图进行分析
    import os
    from config import SCREENSHOT_DIR

    files = sorted(
        [f for f in os.listdir(SCREENSHOT_DIR) if f.endswith(".png") or f.endswith(".jpg")],
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
