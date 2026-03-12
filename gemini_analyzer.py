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
from google import genai
from google.genai import types
from config import (
    GEMINI_API_KEY, GEMINI_MODEL, ANALYSIS_PROMPT,
    APEXLOL_ENABLED, APEXLOL_CACHE_DIR, LANGUAGE,
)

log = logging.getLogger("ARAM")

# 初始化客户端
client = genai.Client(api_key=GEMINI_API_KEY)

# ==================== SSL EOF 自动重试 ====================
MAX_RETRIES = 2       # 最多重试2次（共3次尝试）
RETRY_DELAY = 2.0     # 重试前等待秒数


def _is_ssl_eof(exc: Exception) -> bool:
    """判断是否为 SSL EOF 错误（代理偶发中断）。"""
    msg = str(exc).lower()
    return "unexpected_eof" in msg or "ssleoferror" in msg or "eof occurred" in msg


def _call_with_retry(*, model, contents, config, label="API"):
    """带 SSL EOF 自动重试的 Gemini API 调用封装。
    
    仅在遇到 SSL EOF 类错误时自动重试，其他错误直接抛出。
    """
    last_exc = None
    for attempt in range(1 + MAX_RETRIES):
        try:
            return client.models.generate_content(
                model=model, contents=contents, config=config,
            )
        except Exception as e:
            if _is_ssl_eof(e) and attempt < MAX_RETRIES:
                last_exc = e
                log.warning(f"[{label}] SSL EOF, {RETRY_DELAY}s 后重试 ({attempt+1}/{MAX_RETRIES})...")
                _time.sleep(RETRY_DELAY)
            else:
                raise
    raise last_exc  # 不应到达，保险兜底


# ==================== 阶段1：英雄识别 Prompt ====================
_IDENTIFY_PROMPT_ZH = """请识别这张海克斯大乱斗加载界面截图中的所有英雄。

如果这不是英雄联盟的加载界面，也不是游戏内的战绩表（Scoreboard/TAB 界面），请回复：
{"error": "not_loading_screen"}

**情况 A：大乱斗加载界面**
按照之前的层级识别：账号头像 -> 正下方第一行 -> 金色英雄名（我）。

**情况 B：游戏内战绩表 (Scoreboard/TAB)**
识别战绩表中列出的所有英雄名。我方通常在左边或上方。
如果能看到变色（如高亮行），那代表“我”。

**情况 C：英雄选择界面**
识别已确认选定的英雄。

每张英雄卡片在底部的 V 字形区域包含关键信息。请严格按照以下层级识别：
1. **定位锚点**：先找到位于 V 字形孔中间的**圆形账号头像**（Summoner Icon）。
2. **锁定英雄名**：提取账号头像**正下方第一行**的文字。
3. **判定“我”**：在这个位置上，只有颜色为**金色/亮黄色**的英雄名才代表“玩家本人”。如果是白色，则为队友。
⚠️ 排除：忽略头像上方的皮肤名，以及卡片最底部（英雄名下方）的称号。
上面5张 = 我方，下面5张 = 敌方（如果是水平排列）。

请用 JSON 格式回复（不要任何其他文字）：
{"my_team": ["英雄1", "英雄2", "英雄3", "英雄4", "英雄5"], "enemy_team": ["英雄1", "英雄2", "英雄3", "英雄4", "英雄5"], "my_champion": "我的英雄"}

仅返回 JSON，不要返回 markdown 代码块。"""

_IDENTIFY_PROMPT_EN = """Identify all champions in this Hextech Havoc (ARAM) loading screen screenshot.

If this is NOT a League of Legends loading screen (must show 5 champion cards on top and bottom, or champion select screen), reply with pure JSON ONLY:
{"error": "not_loading_screen"}

Each champion card has the champion name at the bottom. ⚠️ NOTE: If there are two lines of text at the bottom, **IGNORE the bottom-most line** (ARAM title), and ONLY extract the line **directly above it** as the champion name.
Top 5 = My team, Bottom 5 = Enemy team.
**My Champion Identification**: Locate the champion whose name is displayed in **GOLD/YELLOW** font color. It is typically positioned directly below a **circular Poro icon**. This distinct color and location are for identifying the user's own champion.

Reply in JSON format ONLY (no other text):
{"my_team": ["champ1", "champ2", "champ3", "champ4", "champ5"], "enemy_team": ["champ1", "champ2", "champ3", "champ4", "champ5"], "my_champion": "my_champ_name"}

Return ONLY the JSON, no markdown code blocks."""


def _get_identify_prompt() -> str:
    return _IDENTIFY_PROMPT_ZH if LANGUAGE == "zh" else _IDENTIFY_PROMPT_EN


def identify_champions(png_bytes: bytes) -> dict | None:
    """阶段1：快速识别截图中的英雄名。"""
    try:
        import time
        t0 = time.time()
        log.info("[Gemini] 阶段1: 快速验证并识别英雄...")
        response = _call_with_retry(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=png_bytes, mime_type="image/jpeg"),
                _get_identify_prompt(),
            ],
            config=types.GenerateContentConfig(
                temperature=0.0,
            ),
            label="识别",
        )

        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        log.info(f"[Gemini] 阶段1完成 ({time.time()-t0:.1f}s)")
        result = json.loads(text)
        return result

    except json.JSONDecodeError as e:
        log.warning(f"[Gemini] 阶段1 JSON 解析失败: {e}, 原文: {text[:100]}")
        return None
    except Exception as e:
        log.error(f"[Gemini] 阶段1失败: {e}")
        return None


def analyze_screenshot(png_bytes: bytes, manual_champion: str = None,
                       hextech_history: list[str] = None) -> str:
    """全局分析：加载界面截图 → 完整攻略。

    极速单次 API 调用架构：
    1. 不分两阶段，避免两轮网络请求的巨大延迟（实测两轮需要8-12秒）。
    2. 将 ApexLol 高分数据「极限压缩」（只保留英雄名 and SS/S/A极海克斯名，丢弃长篇分析文本）。
    3. 上下文从70KB缩减为不到10KB，大幅降低模型的读取延迟(TTFT)，整体分析降至 3-5 秒！

    Args:
        png_bytes: JPEG 格式的截图字节数据
        manual_champion: 用户手动指定的英雄名（纠错用）
        hextech_history: 已选过的海克斯符文列表
    """
    try:
        from lang import PROMPTS
        prompt = ANALYSIS_PROMPT
        
        # 根据实时状态增强 Prompt
        from lcu_client import get_full_board_state
        live_status = get_full_board_state()
        if live_status:
            prompt = live_status + "\n" + prompt
            log.info("[Gemini] 已注入全场 10 人实时游戏数据 (InProgress)")

        # 注入海克斯历史
        if hextech_history:
            history_str = "、".join(hextech_history)
            prompt = f"📜【本局已选海克斯符文历史】: {history_str}\n" + prompt
            log.info(f"[Gemini] 已注入海克斯历史 ({len(hextech_history)}个)")

        # 用户手动纠错或命令行直接起手覆盖
        if manual_champion:
            override_msg = f"⚠️ 核心最高指令：玩家已在此刻手动指令本局强制使用英雄：【{manual_champion}】。\n因为是手动指令起手，你**必须完全忽略**前面关于“必须判断截图是否为大乱斗/加载界面”的拦截规则！哪怕截图只显示了纯桌面聊天软件，你也**绝对不许拦截报错**，必须假装你的‘我方英雄’就是【{manual_champion}】，并基于此直接输出完整的三套海克斯与出装攻略！\n\n"
            prompt = override_msg + prompt


            log.info(f"[Gemini] 用户手动指定英雄: {manual_champion}")

        
        # 极速数据注入（只有不到10KB）
        if APEXLOL_ENABLED:
            apexlol_context = _build_all_champions_context()
            if apexlol_context:
                prompt = apexlol_context + "\n\n" + "=" * 60 + "\n\n" + prompt
                log.info(f"[ApexLol] 注入极限压缩的高分数据: {len(apexlol_context)} 字符")

        log.info("[Gemini] 全局分析（单次调用）...")
        import time
        t2 = time.time()
        response = _call_with_retry(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=png_bytes, mime_type="image/jpeg"),
                prompt,
            ],
            config=types.GenerateContentConfig(
                temperature=0.5,
            ),
            label="全局分析",
        )

        result = response.text
        log.info(f"[Gemini] 分析完成 ({time.time()-t2:.1f}s)")
        
        # 处理快速拒绝的情况（如果是手动指定，哪怕它说不是加载界面，也许它是错判，但也只能返回了）
        if "❌" in result and "加载界面" in result and not manual_champion:
            log.info("[Gemini] 快速拒绝：非加载界面")
            
        return result

    except Exception as e:
        error_msg = f"❌ Gemini API 调用失败: {str(e)}"
        log.error(f"[错误] {error_msg}")
        return error_msg


def analyze_champion_quick_guide(champion_name: str) -> str:
    """开局前极速前瞻分析：终端输英雄名 → 三套海克斯+出装（纯文本，无需截图）。"""
    try:
        from lang import QUICK_GUIDE_PROMPTS
        log.info(f"[Gemini] 极速前瞻分析 ({champion_name})...")
        prompt = QUICK_GUIDE_PROMPTS.get(LANGUAGE, QUICK_GUIDE_PROMPTS["zh"]).format(
            champion_name=champion_name
        )
        
        # 极速定向数据注入（仅注入这一个英雄，不到 1KB）
        if APEXLOL_ENABLED:
            apexlol_context = _build_apexlol_context({"my_champion": champion_name})
            if apexlol_context:
                prompt = apexlol_context + "\n\n" + "=" * 60 + "\n\n" + prompt
                log.info(f"[ApexLol] 注入单英雄定向高分数据: {len(apexlol_context)} 字符")

        import time
        t_start = time.time()
        # 纯文本请求，不需要传 png_bytes
        response = _call_with_retry(
            model=GEMINI_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(
                temperature=0.3, # 降低随机性，更稳定地提取高分数据
            ),
            label="极速前瞻",
        )
        log.info(f"[Gemini] 极速前瞻分析完成 ({time.time()-t_start:.1f}s)")
        return response.text

    except Exception as e:
        error_msg = f"❌ 极速前瞻失败: {str(e)}"
        log.error(error_msg)
        return error_msg


def analyze_lcu_rosters(rosters: dict, hextech_history: list[str] = None) -> str:
    """跳过截图，完全基于 LCU 获取的 10 人阵容进行极速全局全量分析。"""
    try:
        from lang import LCU_FULL_STRATEGY_PROMPTS
        
        my_champion = rosters.get("my_champion", "未知英雄")
        lcu_rosters = rosters.get("live_context", "")
        
        log.info(f"[Gemini] 纯数据级全局分析 ({my_champion})...")
        prompt = LCU_FULL_STRATEGY_PROMPTS.get(LANGUAGE, LCU_FULL_STRATEGY_PROMPTS["zh"]).format(
            my_champion=my_champion,
            lcu_rosters=lcu_rosters
        )
        
        # 注入海克斯历史
        if hextech_history:
            history_str = "、".join(hextech_history)
            prompt = f"📜【本局已选海克斯符文历史】: {history_str}\n" + prompt
            log.info(f"[Gemini] 已注入海克斯历史 ({len(hextech_history)}个)")
            
        # 极速数据注入（只注入这 10 个特定的英雄，不到 3KB）
        if APEXLOL_ENABLED:
            apexlol_context = _build_apexlol_context(rosters)
            if apexlol_context:
                prompt = apexlol_context + "\n\n" + "=" * 60 + "\n\n" + prompt
                log.info(f"[ApexLol] 注入定向本局英雄高分数据: {len(apexlol_context)} 字符")

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
        return response.text

    except Exception as e:
        error_msg = f"❌ LCU 全量分析失败: {str(e)}"
        log.error(error_msg)
        return error_msg





def analyze_hextech_choice(png_bytes: bytes, global_context: str,
                           hextech_history: list[str]) -> str:
    """海克斯选择分析：截图中的3个选项 → 推荐选哪个。"""
    try:
        from lang import HEXTECH_PROMPTS
        log.info("[Gemini] 海克斯选择分析...")
        context_summary = global_context[:800] if global_context else "尚无全局攻略"
        history_str = "、".join(hextech_history) if hextech_history else "无"
        prompt = HEXTECH_PROMPTS.get(LANGUAGE, HEXTECH_PROMPTS["zh"]).format(
            global_context=context_summary,
            hextech_history=history_str,
        )
        
        # =============== 海克斯专属上下文增强 ===============
        from lcu_client import get_full_board_state
        live_status = get_full_board_state()
        if live_status:
            prompt = live_status + "\n\n" + prompt
            log.info("[Gemini] 已注入全场 10 人实时游戏数据至海克斯推演")
        
        response = _call_with_retry(
            model=GEMINI_MODEL,
            contents=[types.Part.from_bytes(data=png_bytes, mime_type="image/jpeg"), prompt],
            config=types.GenerateContentConfig(temperature=0.2),
            label="海克斯",
        )
        log.info("[Gemini] 海克斯选择分析完成")
        return response.text
    except Exception as e:
        return f"❌ 海克斯分析失败: {str(e)}"


def update_global_strategy(current_strategy: str, hextech_history: list[str],
                           latest_hextech: str, timeout: float = 15.0) -> str | None:

    """后台更新全局攻略。"""
    try:
        from lang import STRATEGY_UPDATE_PROMPTS
        import concurrent.futures
        from lcu_client import get_live_player_status
        live_status = get_live_player_status()
        live_info = live_status + "\n" if live_status else ""
        
        history_str = "、".join(hextech_history) if hextech_history else "无"
        
        prompt = live_info + STRATEGY_UPDATE_PROMPTS.get(LANGUAGE, STRATEGY_UPDATE_PROMPTS["zh"]).format(
            current_strategy=current_strategy,
            hextech_history=history_str,
            latest_hextech=latest_hextech,
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                _call_with_retry,
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.5),
                label="策略更新",
            )
            try:
                result = future.result(timeout=timeout).text
                log.info("[Gemini] 全局攻略更新完成")
                return result
            except concurrent.futures.TimeoutError:
                log.warning(f"[Gemini] 全局攻略更新超时（>{timeout}s），放弃")
                return None
    except Exception as e:
        return None


def _build_all_champions_context() -> str:
    """构建极限压缩的全量英雄数据上下文。
    
    大小不到 10KB，不包含分析长文，仅包含 英雄名 -> 高分海克斯名映射。
    让模型知道"哪些海克斯名字是存在的、且适合该英雄的"，防止编造名并指导原则。
    """
    try:
        from apexlol_data import load_cache, is_cache_valid

        if not is_cache_valid(APEXLOL_CACHE_DIR):
            return ""

        cache = load_cache(APEXLOL_CACHE_DIR)
        if not cache:
            return ""

        champions = cache.get("champions", {})
        if not champions:
            return ""

        lines = [
            "📚 以下是来自 apexlol.info 的最高胜率海克斯推荐列表：",
            "⚠️ 你必须优先推荐列表中该英雄对应的海克斯名称！严禁编造列表中不存在的符文名称！",
            "=" * 60,
        ]

        champ_count = 0
        for champ_id, c in champions.items():
            cn_title = c.get("cn_title", champ_id)
            cn_name = c.get("cn_name", "")
            name = f"{cn_title} {cn_name}".strip()
            
            synergies = c.get('synergies', [])
            
            valid_hex = []
            for s in synergies:
                r = str(s.get('rating', '')).strip().upper()
                if r.startswith('SSS') or r.startswith('SS') or r.startswith('S') or r.startswith('A'):
                    names = s.get('hex_names', [])
                    if names:
                        valid_hex.append(names[0])  # 只取第一组合的核心名
                        
            # 去重并最多保留前5个最强符文
            unique_hex = []
            for h in valid_hex:
                if h not in unique_hex:
                    unique_hex.append(h)
            
            if unique_hex:
                champ_count += 1
                lines.append(f"{name}: {', '.join(unique_hex[:5])}")
        
        ctx_str = "\n".join(lines)
        log.info(f"[ApexLol] 构建了 {champ_count} 英雄的极限压缩上下文数据 (约{len(ctx_str)}字符)")
        return ctx_str

    except Exception as e:
        log.error(f"[ApexLol] 构建上下文失败: {e}")
        return ""


# 保留旧的单英雄查询接口（海克斯更新时可能用到）
def _build_apexlol_context(champions: dict) -> str:
    """根据识别出的英雄构建 apexlol 数据上下文。"""
    try:
        from apexlol_data import load_cache, lookup_champions, is_cache_valid

        if not is_cache_valid(APEXLOL_CACHE_DIR):
            log.warning("[ApexLol] 缓存无效或过期，跳过数据增强")
            return ""

        load_cache(APEXLOL_CACHE_DIR)

        all_names = champions.get("my_team", []) + champions.get("enemy_team", []) + champions.get("their_team", [])
        my_champ = champions.get("my_champion", "")
        # 如果是单英雄查询，all_names 可能是空的，需要把 my_champ 放进去
        if not all_names and my_champ:
            all_names = [my_champ]

        return lookup_champions(all_names, highlight_mine=my_champ)

    except Exception as e:
        log.error(f"[ApexLol] 构建上下文失败: {e}")
        return ""


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
