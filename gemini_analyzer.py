# -*- coding: utf-8 -*-
"""ARAM 助手 - 分析模块（原 Gemini 专用，现走统一 LLMClient）

三种分析模式：
1. 全局分析：加载界面截图 → 完整攻略
2. 海克斯选择：海克斯界面截图 → 快速选择建议
3. 全局更新：根据已选海克斯更新全局攻略

历史兼容：文件名保留 gemini_analyzer，供 main.py 以原路径 import。
底层通过 llm_client.LLMClient 支持 Gemini / OpenAI / 自定义三种后端。
"""

import logging
import time as _time

from config import (
    APEXLOL_ENABLED, LANGUAGE,
)
from llm_client import get_client

log = logging.getLogger("ARAM")


def _llm():
    """懒加载 LLM 客户端；LLM 未配置时抛异常，由调用方捕获并返回降级结果。"""
    return get_client()


def analyze_champion_quick_guide(champion_name: str) -> str:
    """开局前极速前瞻分析：输入英雄名 → 数据驱动的海克斯+AI出装（纯文本，无需截图）。"""
    try:
        from lang import QUICK_GUIDE_PROMPTS
        log.info(f"[LLM] 极速前瞻分析 ({champion_name})...")

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

        t_start = _time.time()
        response_text = _llm().generate(
            contents=[prompt],
            temperature=0.3,
            label="极速前瞻",
        )
        log.info(f"[LLM] 极速前瞻分析完成 ({_time.time()-t_start:.1f}s)")

        # 100% 防御幻觉：由代码直接拼接，绝不指望 AI "原样复述"
        final_output = ""
        if prefilled_augments:
            final_output += prefilled_augments + "\n\n---\n\n"
        final_output += response_text

        return final_output

    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        error_msg = f"\u274c 极速前瞻失败: {str(e)}\n\n{trace}"
        log.error(error_msg)
        return error_msg


def analyze_lcu_rosters(rosters: dict, hextech_history: list = None) -> str:
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

        log.info(f"[LLM] 纯数据级全局分析 ({my_champion})...")
        prompt = LCU_FULL_STRATEGY_PROMPTS.get(LANGUAGE, LCU_FULL_STRATEGY_PROMPTS["zh"]).format(
            my_champion=my_champion,
            lcu_rosters=lcu_rosters,
            prefilled_augments=prefilled_augments if prefilled_augments else "（无数据，请基于知识推荐3套最强海克斯符文方案）"
        )

        # 注入海克斯历史
        if hextech_history:
            history_str = "、".join(hextech_history)
            prompt = f"\U0001f4dc【本局已选海克斯符文历史】: {history_str}\n" + prompt
            log.info(f"[LLM] 已注入海克斯历史 ({len(hextech_history)}个)")

        t_start = _time.time()
        response_text = _llm().generate(
            contents=[prompt],
            temperature=0.4,  # 兼顾稳定与战术变化
            label="纯文本全量分析",
        )
        log.info(f"[LLM] 纯数据全量分析完成 ({_time.time()-t_start:.1f}s)")

        final_output = ""
        if prefilled_augments:
            final_output += prefilled_augments + "\n\n---\n\n"
        final_output += response_text

        return final_output

    except Exception as e:
        error_msg = f"\u274c LCU 全量分析失败: {str(e)}"
        log.error(error_msg)
        return error_msg


def analyze_hextech_choice(png_bytes: bytes, global_context: str,
                           hextech_history: list, champion_name: str = None) -> str:
    """海克斯选择分析：截图中的3个选项 → 推荐选哪个。"""
    try:
        from lang import HEXTECH_IMAGE_PROMPTS
        log.info(f"[LLM] 海克斯选择分析 (英雄: {champion_name})...")

        history_str = "、".join(hextech_history) if hextech_history else "无"

        # 注入该英雄的高胜率符文列表辅助 AI 识别
        prefilled_augments = ""
        if champion_name and APEXLOL_ENABLED:
            from apexlol_data import extract_top_synergies
            prefilled_augments = extract_top_synergies(champion_name)
            if prefilled_augments:
                log.info(f'[海克斯] 为 {champion_name} 注入高胜率"对照表"')

        prompt = HEXTECH_IMAGE_PROMPTS.get(LANGUAGE, HEXTECH_IMAGE_PROMPTS["zh"]).format(
            hextech_history=history_str,
        )

        # contents 顺序：图片 -> 对照表/防幻觉指令 -> prompt
        contents = [(png_bytes, "image/jpeg")]
        if prefilled_augments:
            contents.append(
                f"\U0001f680【高胜率对照表】该英雄的强势海克斯如下：\n{prefilled_augments}\n\n"
                f"\U0001f6d1【绝对核心指令 / 严禁幻觉】：\n"
                f"你**必须、绝对只能**从上方截图里**真实显示出来的 3 个选项**中进行三选一！\n"
                f"即使对照表里有再好的海克斯（比如'速度恶魔'等），只要**截图中没有出现**，你**绝对不可推荐**！\n"
                f"你的任务是：观察截图中的选项 -> 与对照表对比 -> 在**真正可用**的选项里挑一个最好的。\n"
                f"如果违背此项，胡乱推荐截图外的内容，将导致严重错误！"
            )
        contents.append(prompt)

        response_text = _llm().generate(
            contents=contents,
            temperature=0.2,
            label="海克斯",
            hard_timeout=8.0,  # 8秒硬超时
            max_retries=1,     # 防止卡死停摆，只重试一次
        )
        log.info("[LLM] 海克斯选择分析完成")
        return response_text
    except Exception as e:
        return f"\u274c 海克斯分析失败: {str(e)}"


def analyze_hextech_text(ocr_names: list, hextech_history: list,
                         champion_name: str = None) -> str:
    """纯文字海克斯分析：OCR 识别出的符文名 + ApexLol 数据 → AI 给建议（无截图，极速）。"""
    try:
        from lang import HEXTECH_TEXT_PROMPTS
        log.info(f"[LLM] 纯文字海克斯分析 (英雄: {champion_name}, 选项: {ocr_names})...")

        history_str = "、".join(hextech_history) if hextech_history else "无"

        # 注入 ApexLol 数据
        prefilled_augments = ""
        if champion_name and APEXLOL_ENABLED:
            from apexlol_data import extract_top_synergies
            prefilled_augments = extract_top_synergies(champion_name)

        options_text = "、".join(ocr_names)
        prompt = HEXTECH_TEXT_PROMPTS.get(LANGUAGE, HEXTECH_TEXT_PROMPTS["zh"]).format(
            hextech_history=history_str,
            options_text=options_text,
        )

        # 注入每个选项的真实效果描述（防止AI幻觉）
        effect_lines = []
        if APEXLOL_ENABLED:
            try:
                from apexlol_data import get_hextech_description
                for name in ocr_names:
                    desc = get_hextech_description(name)
                    if desc:
                        effect_lines.append(f"- 【{name}】: {desc}")
                    else:
                        effect_lines.append(f"- 【{name}】: (效果未知)")
            except Exception:
                pass

        contents = []
        if effect_lines:
            contents.append("\U0001f4cb【各候选选项的真实游戏机制/效果】（供参考）\n"
                            + "\n".join(effect_lines) + "\n")
        if prefilled_augments:
            contents.append(
                f"\U0001f680【高胜率对照表】该英雄的强势海克斯如下：\n{prefilled_augments}\n\n"
            )
        contents.append(prompt)

        response_text = _llm().generate(
            contents=contents,
            temperature=0.2,
            label="海克斯文字",
            hard_timeout=5.0,
            max_retries=1,
        )
        log.info("[LLM] 纯文字海克斯分析完成")
        return response_text
    except Exception as e:
        return f"\u274c 海克斯分析失败: {str(e)}"


if __name__ == "__main__":
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
        result = analyze_hextech_choice(data, "", [])
        print("\n" + "=" * 60)
        print(result)
    else:
        print("screenshots/ 目录下没有测试截图")
