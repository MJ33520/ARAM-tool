# -*- coding: utf-8 -*-
"""ARAM 助手 - ApexLol.info 数据爬取模块

从 https://apexlol.info 爬取英雄海克斯联动分析数据。

⚠️ 数据来源声明：
- 本模块爬取的数据版权归 ApexLol.info 及其数据提供者所有
- 仅在用户主动触发时爬取，控制请求频率，尽量减少对源站的影响
- 本项目与 ApexLol.info 无官方合作关系
"""

import os
import json
import time
import logging
import re
import requests
from bs4 import BeautifulSoup

log = logging.getLogger("ARAM")

BASE_URL = "https://apexlol.info/zh"
HEADERS = {
    "User-Agent": "ARAM-Assistant/1.0 (github.com/MJ33520/ARAM-tool)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
REQUEST_DELAY = 0.4  # 请求间隔（秒），避免给网站造成压力


def get_champion_list() -> list[dict]:
    """从英雄名录页面获取所有英雄的 ID 和中文名。

    Returns:
        [{"id": "Katarina", "cn_title": "不祥之刃", "cn_name": "卡特琳娜"}, ...]
    """
    url = f"{BASE_URL}/champions/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        log.error(f"[ApexLol] 获取英雄列表失败: {e}")
        return []

    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")
    champions = []

    # 英雄链接格式: /zh/champions/ChampionId
    # 文本格式: "S不祥之刃" 或 "不祥之刃"（S 前缀表示有详细数据）
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        match = re.search(r"/champions/([A-Za-z]+)$", href)
        if not match:
            continue

        champ_id = match.group(1)
        text = link.get_text(strip=True)

        # 去掉 S 前缀标记
        if text.startswith("S"):
            text = text[1:]

        # text 是中文标题（如 "不祥之刃"）
        champions.append({
            "id": champ_id,
            "cn_title": text,
        })

    # 去重（同一英雄可能出现多次）
    seen = set()
    unique = []
    for c in champions:
        if c["id"] not in seen:
            seen.add(c["id"])
            unique.append(c)

    log.info(f"[ApexLol] 获取到 {len(unique)} 个英雄")
    return unique


def scrape_champion(champion_id: str) -> dict:
    """爬取单个英雄的海克斯联动分析数据。

    Args:
        champion_id: 英雄 ID（如 "Katarina"）

    Returns:
        {
            "id": "Katarina",
            "synergies": [
                {
                    "hex_names": ["符文名1"],
                    "hex_tiers": ["棱彩阶"],
                    "rating": "S",
                    "analysis": "详细联动分析文本..."
                },
                ...
            ]
        }
    """
    url = f"{BASE_URL}/champions/{champion_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        log.warning(f"[ApexLol] 爬取 {champion_id} 失败: {e}")
        return {"id": champion_id, "synergies": []}

    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")
    synergies = []

    # 查找所有联动卡片
    cards = soup.select(".interaction-card")
    for card in cards:
        entry = {}

        # 提取海克斯名称（可能有多个）
        hex_names = [h.get_text(strip=True) for h in card.select(".hex-name")]
        hex_tiers = [t.get_text(strip=True) for t in card.select(".hex-tier")]
        entry["hex_names"] = hex_names
        entry["hex_tiers"] = hex_tiers

        # 提取评级
        rating_el = card.select_one(".rating-badge")
        entry["rating"] = rating_el.get_text(strip=True).replace("级", "").strip() if rating_el else ""

        # 提取联动标签（支持所有类型：强力联动/陷阱/娱乐/Bug）
        tag_el = card.select_one(".tag-badge")
        entry["tag"] = tag_el.get_text(strip=True) if tag_el else ""

        # 提取分析文本（核心内容）
        notes = card.select(".note")
        analysis_parts = []
        for note in notes:
            text = note.get_text(strip=True)
            if text:
                analysis_parts.append(text)
        entry["analysis"] = "\n".join(analysis_parts)

        # 提取推荐出装（每张联动卡片下方可能有金色边框的装备图标）
        item_elements = card.select(".island-item")
        recommended_items = []
        for item_el in item_elements:
            item_name = item_el.get("data-item-name", "")
            if item_name:
                recommended_items.append(item_name)
        if recommended_items:
            entry["recommended_items"] = recommended_items

        if entry["analysis"]:  # 只保留有内容的卡片
            synergies.append(entry)

    # 提取真实英雄名 (h1 通常是 "不祥之刃 卡特琳娜")
    cn_name = ""
    h1_el = soup.find("h1")
    if h1_el:
        h1_text = h1_el.get_text(strip=True)
        # 取空格最后一段作为英雄名
        parts = h1_text.split()
        if len(parts) > 1:
            cn_name = parts[-1]
        else:
            cn_name = h1_text

    return {"id": champion_id, "cn_name": cn_name, "synergies": synergies}


def scrape_all_champions(cache_dir: str, progress_callback=None) -> dict:
    """爬取所有英雄的联动数据并保存到本地。

    Args:
        cache_dir: 缓存目录路径
        progress_callback: 可选的进度回调 fn(current, total, champion_name)

    Returns:
        完整的英雄数据字典
    """
    os.makedirs(cache_dir, exist_ok=True)

    # 获取英雄列表
    champion_list = get_champion_list()
    if not champion_list:
        log.error("[ApexLol] 无法获取英雄列表")
        return {}

    all_data = {
        "meta": {
            "source": "https://apexlol.info",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "champion_count": len(champion_list),
        },
        "champion_list": champion_list,
        "champions": {},
    }

    total = len(champion_list)
    for i, champ in enumerate(champion_list):
        champ_id = champ["id"]
        cn_title = champ["cn_title"]

        if progress_callback:
            progress_callback(i + 1, total, cn_title)

        log.info(f"[ApexLol] [{i+1}/{total}] 爬取 {cn_title} ({champ_id})...")

        data = scrape_champion(champ_id)
        all_data["champions"][champ_id] = {
            "cn_title": cn_title,
            "cn_name": data.get("cn_name", ""),
            "synergies": data["synergies"],
        }

        # 控制请求频率
        if i < total - 1:
            time.sleep(REQUEST_DELAY)

    # ===== 爬取所有海克斯效果描述 =====
    log.info("[ApexLol] 开始爬取海克斯效果描述...")
    hextech_details = scrape_all_hextech(progress_callback)
    all_data["hextech_details"] = hextech_details
    log.info(f"[ApexLol] ✅ 已爬取 {len(hextech_details)} 个海克斯效果描述")

    # 保存到文件
    cache_file = os.path.join(cache_dir, "apexlol_data.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    log.info(f"[ApexLol] ✅ 已缓存 {total} 个英雄 + {len(hextech_details)} 个海克斯到 {cache_file}")
    return all_data


# ==================== 海克斯详情爬取 ====================

def get_hextech_list() -> list[dict]:
    """从海克斯列表页获取所有海克斯的 ID 和中文名。

    Returns:
        [{"id": "Get_Excited", "name": "罪恶快感"}, ...]
    """
    url = f"{BASE_URL}/hextech/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        log.error(f"[ApexLol] 获取海克斯列表失败: {e}")
        return []

    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")
    hextech_list = []
    seen = set()

    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        match = re.search(r"/zh/hextech/([^/]+)$", href)
        if not match:
            continue
        hex_id = match.group(1)
        name = link.get_text(strip=True)
        if hex_id not in seen and name:
            seen.add(hex_id)
            hextech_list.append({"id": hex_id, "name": name})

    log.info(f"[ApexLol] 获取到 {len(hextech_list)} 个海克斯")
    return hextech_list


def scrape_hextech_detail(hex_id: str) -> dict:
    """爬取单个海克斯的效果描述和特殊机制。

    Args:
        hex_id: 海克斯 ID（如 "Get_Excited", "42"）

    Returns:
        {"name": "罪恶快感", "tier": "黄金阶", "description": "...", "mechanism": "..."}
    """
    url = f"{BASE_URL}/hextech/{hex_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        log.warning(f"[ApexLol] 爬取海克斯 {hex_id} 失败: {e}")
        return {}

    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    result = {}

    # 名称和阶级
    title_section = soup.select_one(".title-section")
    if title_section:
        result["name"] = title_section.get_text(strip=True)
        # 阶级从 header-card 的 class 判断
        header = soup.select_one(".header-card")
        if header:
            classes = header.get("class", [])
            for tier in ["prismatic", "gold", "silver"]:
                if tier in classes:
                    tier_map = {"prismatic": "棱彩阶", "gold": "黄金阶", "silver": "白银阶"}
                    result["tier"] = tier_map.get(tier, tier)
                    break

    # 效果描述
    desc_box = soup.select_one(".description-box")
    if desc_box:
        result["description"] = desc_box.get_text(strip=True)

    # 特殊机制
    mech_box = soup.select_one(".mechanism-box")
    if mech_box:
        text = mech_box.get_text(strip=True)
        if "暂无" not in text:
            result["mechanism"] = text

    return result


def scrape_all_hextech(progress_callback=None) -> dict:
    """爬取所有海克斯的效果描述。

    Returns:
        {"罪恶快感": {"tier": "黄金阶", "description": "...", "mechanism": "..."}, ...}
    """
    hex_list = get_hextech_list()
    if not hex_list:
        return {}

    details = {}
    total = len(hex_list)

    for i, hex_info in enumerate(hex_list):
        hex_id = hex_info["id"]
        hex_name = hex_info["name"]

        if progress_callback:
            progress_callback(i + 1, total, f"海克斯: {hex_name}")

        detail = scrape_hextech_detail(hex_id)
        if detail and detail.get("description"):
            # 以中文名为 key
            display_name = detail.get("name", hex_name)
            # 去掉阶级前缀（如"黄金阶罪恶快感" → "罪恶快感"）
            for prefix in ["棱彩阶", "黄金阶", "白银阶"]:
                if display_name.startswith(prefix):
                    display_name = display_name[len(prefix):]
                    break
            details[display_name] = {
                "tier": detail.get("tier", ""),
                "description": detail.get("description", ""),
            }
            if detail.get("mechanism"):
                details[display_name]["mechanism"] = detail["mechanism"]

        if i < total - 1:
            time.sleep(REQUEST_DELAY * 0.5)  # 海克斯页面较轻，间隔可以短一点

    return details


if __name__ == "__main__":
    # 测试：爬取单个英雄
    logging.basicConfig(level=logging.DEBUG)
    print("=== 测试爬取卡特琳娜 ===")
    data = scrape_champion("Katarina")
    print(f"找到 {len(data['synergies'])} 条联动数据")
    for s in data["synergies"][:3]:
        print(f"\n  [{s.get('rating', '?')}] {' + '.join(s['hex_names'])}")
        print(f"  {s['analysis'][:100]}...")
