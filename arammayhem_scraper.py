# -*- coding: utf-8 -*-
"""ARAM 助手 - ARAM Mayhem 核心出装数据爬取模块

从 https://arammayhem.com/zh-cn 抓取每个英雄的"核心出装"统计数据
（多套出装方案 + 登场率 + 胜率），喂给 LLM prompt 提升出装推荐质量。

⚠️ 数据来源声明：
- 数据版权归 arammayhem.com 及其数据来源方所有
- 仅在用户主动触发或缓存过期时爬取，控制请求频率减少对源站影响
- 本项目与 arammayhem.com 无官方合作关系
"""

import os
import json
import time
import logging
import re
import requests
from bs4 import BeautifulSoup

log = logging.getLogger("ARAM")

BASE_URL = "https://arammayhem.com"
TIER_LIST_URL = f"{BASE_URL}/zh-cn/tier-list"
CHAMPION_URL = f"{BASE_URL}/zh-cn/champions/{{slug}}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ARAM-Tool/1.0 (github.com/Zayia/ARAM-tool)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
REQUEST_DELAY = 0.4  # 请求间隔（秒），避免给网站造成压力

# 英雄称号 / data-search 里出现的英文 stop words，不做别名（避免 'the' 'of' 占用映射）
_ALIAS_STOPWORDS = frozenset({
    "the", "of", "a", "an", "and", "in", "on", "to", "at", "is",
    "from", "for", "with", "by", "or", "as",
})


def _normalize_alias(name: str) -> str:
    """归一化英雄名以便查询：去空格、去标点、转小写。
    用于把 LCU 的 'RenataGlasc' / 'Bel'Veth' 都映射到 mayhem 的简化 slug。
    """
    if not name:
        return ""
    return re.sub(r"[\s'._-]", "", name).lower()


def get_champion_slugs() -> list[dict]:
    """从 tier-list 页面获取所有英雄的 slug、中文称号和搜索别名。

    Returns:
        [{
            "slug": "renata",
            "cn_title": "炼金男爵",                    # h1 主名（中文称号）
            "aliases": ["renata", "renataglasc"],     # 归一化别名（用于 LCU 名查询）
        }, ...]
    """
    try:
        resp = requests.get(TIER_LIST_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        log.error(f"[Mayhem] 获取英雄列表失败: {e}")
        return []

    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")
    champions = []
    seen = set()

    for a in soup.find_all("a", href=True):
        m = re.match(r"^/zh-cn/champions/([a-z0-9-]+)$", a["href"])
        if not m:
            continue
        slug = m.group(1)
        if slug in seen:
            continue
        seen.add(slug)

        # 卡片里的中文称号：text-[11px] font-semibold 那个 div
        title_div = a.find("div", class_=re.compile(r"text-\[11px\]"))
        cn_title = title_div.get_text(strip=True) if title_div else ""

        # 从 data-search 提取所有英文/罗马字别名（中文混在一起，按 ASCII 单词切）
        # 形如: "renata renata glasc 炼金男爵 レナータ・グラスク 레나타 ..."
        search_text = a.get("data-search", "")
        ascii_tokens = re.findall(r"[a-zA-Z]+", search_text)

        # 生成别名集合（归一化）：
        # 1. slug 自身（必有）
        # 2. 长度 ≥4 的单 ASCII token（覆盖 'morgana' 'masteryi' 等；过滤 'the'/'of' 等 stop words）
        # 3. 相邻 2-token / 3-token 滑窗拼接（覆盖 'renataglasc' 'tahmkench' 'aurelionsol'）
        # 这样 LCU 给的 PascalCase 名（无论简写还是完整）都能被反查到
        aliases = []
        seen_alias = set()

        def _add(s: str, *, allow_short: bool = False) -> None:
            n = _normalize_alias(s)
            if not n or n in seen_alias:
                return
            if n in _ALIAS_STOPWORDS:
                return
            if not allow_short and len(n) < 4:
                return
            aliases.append(n)
            seen_alias.add(n)

        _add(slug, allow_short=True)  # slug 必加，即使是 'vi' 'yi' 这种 2 字母
        for tok in ascii_tokens:
            _add(tok)
        for i in range(len(ascii_tokens) - 1):
            _add(ascii_tokens[i] + ascii_tokens[i + 1])
        for i in range(len(ascii_tokens) - 2):
            _add(ascii_tokens[i] + ascii_tokens[i + 1] + ascii_tokens[i + 2])

        champions.append({
            "slug": slug,
            "cn_title": cn_title,
            "aliases": aliases,
        })

    log.info(f"[Mayhem] 获取到 {len(champions)} 个英雄")
    return champions


def scrape_champion_builds(slug: str) -> dict:
    """爬取单个英雄页面的"核心出装" Card。

    Args:
        slug: arammayhem 上的英雄 slug（如 "morgana"）

    Returns:
        {
            "slug": "morgana",
            "cn_title": "堕落天使",
            "cn_name": "莫甘娜",
            "core_builds": [
                {"items": ["黯炎火炬", "兰德里的折磨", "瑞莱的冰晶节杖"],
                 "pickrate": 23.69, "winrate": 52.88},
                ...
            ]
        }
    """
    url = CHAMPION_URL.format(slug=slug)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        log.warning(f"[Mayhem] 爬取 {slug} 失败: {e}")
        return {"slug": slug, "cn_title": "", "cn_name": "", "core_builds": []}

    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    # 主名（h1）+ 副名（紧邻的 <p>）
    cn_title = ""
    cn_name = ""
    h1 = soup.find("h1")
    if h1:
        cn_title = h1.get_text(strip=True)
        next_p = h1.find_next_sibling("p")
        if next_p:
            cn_name = next_p.get_text(strip=True)

    # 找"核心出装" Card —— 用 data-slot 语义属性，比 Tailwind class 稳
    core_card = None
    for card in soup.select("[data-slot='card']"):
        title_el = card.select_one("[data-slot='card-title']")
        if title_el and "核心出装" in title_el.get_text(strip=True):
            core_card = card
            break

    core_builds = []
    if core_card:
        content = core_card.select_one("[data-slot='card-content']")
        if content:
            for sol in content.select(".space-y-2 > div"):
                # 装备名：直接抽 img[alt]
                items = [img.get("alt", "") for img in sol.find_all("img") if img.get("alt")]

                # 登场率 / 胜率
                pickrate = None
                winrate = None
                for span in sol.find_all("span", recursive=True):
                    txt = span.get_text(strip=True)
                    if not txt:
                        continue
                    if txt.startswith("登场率"):
                        inner = span.find("span")
                        if inner:
                            m = re.search(r"([\d.]+)", inner.get_text())
                            if m:
                                pickrate = float(m.group(1))
                    elif txt.startswith("胜率"):
                        inner = span.find("span")
                        if inner:
                            m = re.search(r"([\d.]+)", inner.get_text())
                            if m:
                                winrate = float(m.group(1))

                if items:  # 至少要有装备数据才记
                    core_builds.append({
                        "items": items,
                        "pickrate": pickrate if pickrate is not None else 0.0,
                        "winrate": winrate if winrate is not None else 0.0,
                    })

    # 抓到 0 套方案：可能是 arammayhem 改版了 selector，打 ERROR 让问题不被静默吞掉
    if not core_builds:
        log.error(
            f"[Mayhem] {slug} 解析到 0 套核心出装"
            f"——可能是 arammayhem 改版导致 selector 失效。"
            f"如多个英雄都失败，请到 GitHub 报 issue: "
            f"https://github.com/Zayia/ARAM-tool/issues"
        )

    return {
        "slug": slug,
        "cn_title": cn_title,
        "cn_name": cn_name,
        "core_builds": core_builds,
    }


def scrape_all_builds(cache_dir: str, progress_callback=None) -> dict:
    """爬取所有英雄的核心出装数据并保存到本地。

    Args:
        cache_dir: 缓存目录路径（~/.aram_tool/arammayhem_cache）
        progress_callback: 可选 fn(current, total, champion_name)

    Returns:
        完整数据字典
    """
    os.makedirs(cache_dir, exist_ok=True)

    champion_list = get_champion_slugs()
    if not champion_list:
        log.error("[Mayhem] 无法获取英雄列表")
        return {}

    all_data = {
        "meta": {
            "source": "https://arammayhem.com",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "champion_count": len(champion_list),
        },
        # 别名 → slug 反查表，运行时 LCU 英文名查 slug 就靠它
        "alias_to_slug": {},
        "champions": {},
    }

    total = len(champion_list)
    for i, champ in enumerate(champion_list):
        slug = champ["slug"]
        cn_title = champ["cn_title"]

        if progress_callback:
            progress_callback(i + 1, total, cn_title or slug)

        log.info(f"[Mayhem] [{i+1}/{total}] 爬取 {cn_title} ({slug})...")

        data = scrape_champion_builds(slug)
        all_data["champions"][slug] = {
            "cn_title": data.get("cn_title") or cn_title,
            "cn_name": data.get("cn_name", ""),
            "core_builds": data.get("core_builds", []),
        }

        # 把这个英雄的所有别名注册到反查表
        for alias in champ.get("aliases", []):
            all_data["alias_to_slug"][alias] = slug

        if i < total - 1:
            time.sleep(REQUEST_DELAY)

    # 落盘
    cache_file = os.path.join(cache_dir, "arammayhem_data.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    builds_total = sum(len(c.get("core_builds", [])) for c in all_data["champions"].values())
    log.info(f"[Mayhem] ✅ 已缓存 {total} 英雄 / {builds_total} 套出装方案 → {cache_file}")
    return all_data


if __name__ == "__main__":
    # 调试：跑一个小样本
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    print("=== 测试爬取 Morgana ===")
    r = scrape_champion_builds("morgana")
    print(f"  cn_title: {r['cn_title']}")
    print(f"  cn_name:  {r['cn_name']}")
    print(f"  核心出装: {len(r['core_builds'])} 套")
    for i, b in enumerate(r["core_builds"], 1):
        print(f"    {i}. {b['items']}  登场率={b['pickrate']}%  胜率={b['winrate']}%")
