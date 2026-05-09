# -*- coding: utf-8 -*-
"""ARAM 助手 - ARAM Mayhem 核心出装数据查询模块

读取 arammayhem_scraper 抓取的本地缓存，提供：
- load_cache / is_cache_valid / get_cache_info：缓存生命周期管理（模仿 apexlol_data 同名 API）
- extract_top_builds(champion_name)：按登场率排序拼成 Markdown，喂给 LLM prompt
"""

import os
import json
import time
import logging
import re

log = logging.getLogger("ARAM")

# 模块级缓存：load_cache 一次后常驻
_cache: dict | None = None


def _normalize_alias(name: str) -> str:
    """归一化英雄名，跟 arammayhem_scraper 里同名工具一致。"""
    if not name:
        return ""
    return re.sub(r"[\s'._-]", "", name).lower()


def load_cache(cache_dir: str) -> dict:
    """加载本地缓存到模块级 `_cache`。"""
    global _cache
    cache_file = os.path.join(cache_dir, "arammayhem_data.json")

    if not os.path.exists(cache_file):
        log.warning(f"[Mayhem] 缓存文件不存在: {cache_file}")
        return {}

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            _cache = json.load(f)
        n_champ = len(_cache.get("champions", {}))
        log.info(f"[Mayhem] 缓存加载成功: {n_champ} 个英雄")
        return _cache
    except Exception as e:
        log.error(f"[Mayhem] 缓存加载失败: {e}")
        return {}


def is_cache_valid(cache_dir: str, ttl_days: int = 7) -> bool:
    """检查缓存是否存在且未过期。"""
    cache_file = os.path.join(cache_dir, "arammayhem_data.json")
    try:
        if not os.path.exists(cache_file):
            return False
        mtime = os.path.getmtime(cache_file)
        age_days = (time.time() - mtime) / 86400
        return age_days < ttl_days
    except Exception:
        return False


def get_cache_info(cache_dir: str) -> dict:
    """读缓存元信息（给设置面板状态条用）。"""
    cache_file = os.path.join(cache_dir, "arammayhem_data.json")
    if not os.path.exists(cache_file):
        return {"exists": False}
    try:
        mtime = os.path.getmtime(cache_file)
        age_hours = (time.time() - mtime) / 3600
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "exists": True,
            "age_hours": age_hours,
            "champion_count": len(data.get("champions", {})),
            "scraped_at": data.get("meta", {}).get("scraped_at", ""),
        }
    except Exception as e:
        log.warning(f"[Mayhem] 读缓存元信息失败: {e}")
        return {"exists": False}


def _resolve_slug(champion_name: str) -> str | None:
    """把任意英雄名（LCU 英文 / 中文称号 / 中文俗称）解析成 mayhem slug。

    1. 先用 alias_to_slug（缓存里有 LCU 英文名的归一化映射）
    2. 失败再尝试 cn_title / cn_name 中文匹配
    """
    if not _cache or not champion_name:
        return None

    # 1) 英文路径：归一化后查 alias_to_slug
    n = _normalize_alias(champion_name)
    if n:
        slug = _cache.get("alias_to_slug", {}).get(n)
        if slug:
            return slug

    # 2) 中文路径：扫所有英雄的 cn_title / cn_name
    for slug, info in _cache.get("champions", {}).items():
        if champion_name == info.get("cn_title") or champion_name == info.get("cn_name"):
            return slug

    # 3) 兜底：尝试用 ApexLol 的中文别名表先解析成英文再走 (1)
    try:
        from apexlol_data import CHAMPION_ALIASES
        eng = CHAMPION_ALIASES.get(champion_name)
        if eng:
            slug = _cache.get("alias_to_slug", {}).get(_normalize_alias(eng))
            if slug:
                return slug
    except Exception:
        pass

    return None


def extract_top_builds(champion_name: str, top_n: int = 5) -> str:
    """从缓存中按登场率降序取前 N 套核心出装，返回 Markdown 字符串。

    输出形如：
        ### 🛡️ 核心出装方案（来源: arammayhem.com）

        #### 🥇 方案 1：黯炎火炬 + 兰德里的折磨 + 瑞莱的冰晶节杖
        - 登场率：23.69% | 胜率：52.88%
        ...

    数据为空时返回空字符串，由调用方决定是否拼进 prompt。
    """
    if not _cache:
        return ""

    slug = _resolve_slug(champion_name)
    if not slug:
        log.warning(
            f"[Mayhem] extract_top_builds: 无法把 '{champion_name}' 解析成 slug"
            f"（ApexLol 中文别名也没匹配上）"
        )
        return ""

    info = _cache.get("champions", {}).get(slug)
    if not info:
        log.warning(f"[Mayhem] extract_top_builds: slug={slug} 不在缓存中")
        return ""

    builds = info.get("core_builds", [])
    if not builds:
        log.warning(
            f"[Mayhem] extract_top_builds: slug={slug} 在缓存中但 core_builds 为空"
            f"——可能是上次抓取失败（arammayhem 改版/网络）"
        )
        return ""

    # 按登场率降序排（pickrate 已经是 float）
    sorted_builds = sorted(builds, key=lambda b: b.get("pickrate", 0.0), reverse=True)

    cn_title = info.get("cn_title") or slug
    medals = ["🥇", "🥈", "🥉", "🏅", "🏅", "🏅", "🏅", "🏅"]

    lines = [
        f"### 🛡️ 核心出装方案（来源: arammayhem.com，{cn_title}）",
        "",
    ]
    for i, b in enumerate(sorted_builds[:top_n]):
        items = b.get("items", [])
        pick = b.get("pickrate", 0.0)
        win = b.get("winrate", 0.0)
        medal = medals[i] if i < len(medals) else "🏅"
        items_str = " + ".join(items) if items else "（数据缺失）"
        lines.append(f"#### {medal} 方案 {i + 1}：{items_str}")
        lines.append(f"- 登场率：{pick:.2f}% | 胜率：{win:.2f}%")
        lines.append("")

    return "\n".join(lines)
