# -*- coding: utf-8 -*-
"""ARAM 助手 - ApexLol 数据查询模块

管理本地缓存的 apexlol.info 数据，提供英雄联动信息查询。
"""

import os
import json
import time
import logging

log = logging.getLogger("ARAM")

# ==================== 英雄名称映射 ====================
# 中文标题 -> 英文 ID（爬取时自动构建，这里是常用别名的手动补充）
CHAMPION_ALIASES = {
    # 常用简称 -> ID
    "卡特": "Katarina", "火男": "Brand", "剑圣": "MasterYi",
    "大嘴": "KogMaw", "小法": "Veigar", "女枪": "MissFortune",
    "老鼠": "Twitch", "锤石": "Thresh", "狗头": "Nasus",
    "牛头": "Alistar", "猴子": "MonkeyKing", "蛮王": "Tryndamere",
    "石头人": "Malphite", "机器人": "Blitzcrank", "稻草人": "Fiddlesticks",
    "酒桶": "Gragas", "皇子": "JarvanIV", "螳螂": "Khazix",
    "人马": "Hecarim", "薇恩": "Vayne", "亚索": "Yasuo",
    "永恩": "Yone", "艾克": "Ekko", "EZ": "Ezreal",
    "ez": "Ezreal", "VN": "Vayne", "vn": "Vayne",
    "ADC": None,  # 通用标签不映射
}

# 全局缓存
_cache = None
_name_to_id = None


def _build_name_map(data: dict) -> dict:
    """从缓存数据构建 名称 -> ID 的映射表。"""
    name_map = {}

    # 从 champion_list 构建
    for champ in data.get("champion_list", []):
        champ_id = champ["id"]
        cn_title = champ.get("cn_title", "")

        # 中文标题 -> ID（如 "不祥之刃" -> "Katarina"）
        if cn_title:
            name_map[cn_title] = champ_id

        # 英文 ID 本身（大小写不敏感）
        name_map[champ_id.lower()] = champ_id

    # 从 champions 数据构建
    for champ_id, info in data.get("champions", {}).items():
        cn_title = info.get("cn_title", "")
        if cn_title:
            name_map[cn_title] = champ_id
            
        cn_name = info.get("cn_name", "")
        if cn_name:
            name_map[cn_name] = champ_id

    # 加入手动别名
    for alias, cid in CHAMPION_ALIASES.items():
        if cid:
            name_map[alias] = cid

    return name_map


def load_cache(cache_dir: str) -> dict:
    """加载本地缓存数据。"""
    global _cache, _name_to_id

    cache_file = os.path.join(cache_dir, "apexlol_data.json")
    if not os.path.exists(cache_file):
        log.warning("[ApexLol] 缓存文件不存在")
        return {}

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            _cache = json.load(f)
        _name_to_id = _build_name_map(_cache)
        log.info(f"[ApexLol] ✅ 已加载缓存 ({len(_cache.get('champions', {}))} 英雄)")
        return _cache
    except Exception as e:
        log.error(f"[ApexLol] 加载缓存失败: {e}")
        return {}


def is_cache_valid(cache_dir: str, ttl_days: int = 7) -> bool:
    """检查缓存是否有效（文件存在且未过期）。"""
    cache_file = os.path.join(cache_dir, "apexlol_data.json")
    if not os.path.exists(cache_file):
        return False

    try:
        mtime = os.path.getmtime(cache_file)
        age_days = (time.time() - mtime) / 86400
        return age_days < ttl_days
    except Exception:
        return False


def resolve_champion_id(name: str) -> str | None:
    """将英雄名（中文/英文/别名）解析为英文 ID。"""
    global _name_to_id
    if _name_to_id is None:
        return None

    # 精确匹配
    if name in _name_to_id:
        return _name_to_id[name]

    # 大小写不敏感匹配
    lower = name.lower()
    if lower in _name_to_id:
        return _name_to_id[lower]

    # 模糊匹配：包含关系
    for key, cid in _name_to_id.items():
        if name in key or key in name:
            return cid

    return None


def lookup_champion(name: str) -> str:
    """查询单个英雄的海克斯联动分析文本。

    Args:
        name: 英雄名（中文标题、英文 ID 或别名）

    Returns:
        格式化的联动分析文本，未找到返回空字符串
    """
    global _cache
    if not _cache:
        return ""

    champ_id = resolve_champion_id(name)
    if not champ_id:
        return ""

    champ_data = _cache.get("champions", {}).get(champ_id)
    if not champ_data or not champ_data.get("synergies"):
        return ""

    cn_title = champ_data.get("cn_title", champ_id)
    
    # --- 提取并去重所有合法的海克斯名称，构建【官方词典】 ---
    all_valid_names = []
    for s in champ_data["synergies"]:
        for hname in s.get("hex_names", []):
            if hname and hname not in all_valid_names:
                all_valid_names.append(hname)
    
    lines = [f"【{cn_title}({champ_id}) 海克斯联动分析 - 来源: apexlol.info】"]
    if all_valid_names:
        lines.append(f"📜 [标准海克斯名单 - 严禁修改字符]: {', '.join(all_valid_names)}")
        lines.append("-" * 30)

    for s in champ_data["synergies"]:
        # 使用更清晰的 | 分隔符，防止 AI 误判为一句话
        hex_names = " | ".join(s.get("hex_names", []))
        rating = s.get("rating", "")
        tiers = " / ".join(s.get("hex_tiers", []))
        tag = s.get("tag", "")

        header_parts = []
        if rating:
            header_parts.append(f"[{rating}级]")
        header_parts.append(hex_names)
        if tiers:
            header_parts.append(f"({tiers})")
        if tag:
            header_parts.append(f"- {tag}")

        lines.append(f"\n▸ {' '.join(header_parts)}")
        lines.append(f"  {s.get('analysis', '')}")

    return "\n".join(lines)


def lookup_champions(names: list[str], highlight_mine: str = None) -> str:
    """批量查询多个英雄的联动数据，拼接为 Gemini 可用的参考文本。

    Args:
        names: 英雄名列表
        highlight_mine: 我的英雄名（会放在最前面并额外标注）

    Returns:
        拼接后的参考文本
    """
    sections = []

    # 先处理"我的英雄"
    if highlight_mine:
        my_data = lookup_champion(highlight_mine)
        if my_data:
            sections.append(f"=== ⭐ 我的英雄 ===\n{my_data}")

    # 处理其余英雄
    for name in names:
        if highlight_mine and name == highlight_mine:
            continue
        data = lookup_champion(name)
        if data:
            sections.append(data)

    if not sections:
        return ""

    header = (
        "📚 以下是来自 apexlol.info 的海克斯联动分析数据（专业玩家社区贡献的机制级分析）。\n"
        "请重点参考这些数据来推荐海克斯符文，特别注意隐藏的联动机制（如某技能能触发特定符文效果等）。\n"
        "注意：这些数据是参考建议，请结合当前阵容做出最佳判断。\n"
        "=" * 60
    )

    return header + "\n\n" + "\n\n".join(sections)


def get_cache_info(cache_dir: str) -> dict:
    """获取缓存状态信息。"""
    cache_file = os.path.join(cache_dir, "apexlol_data.json")
    if not os.path.exists(cache_file):
        return {"exists": False}

    try:
        mtime = os.path.getmtime(cache_file)
        age_hours = (time.time() - mtime) / 3600
        size_mb = os.path.getsize(cache_file) / (1024 * 1024)

        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            "exists": True,
            "age_hours": round(age_hours, 1),
            "size_mb": round(size_mb, 2),
            "champion_count": len(data.get("champions", {})),
            "scraped_at": data.get("meta", {}).get("scraped_at", "unknown"),
        }
    except Exception:
        return {"exists": False}
