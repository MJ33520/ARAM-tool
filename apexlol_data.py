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
# 完整的中文名/别名 -> 英文 ID 映射（防止 mojibake 导致名称匹配失败）
CHAMPION_ALIASES = {
    # ===== A =====
    "阿卡丽": "Akali", "阿克尚": "Akshan", "阿利斯塔": "Alistar", "阿木木": "Amumu",
    "阿尼维亚": "Anivia", "冰鸟": "Anivia", "安妮": "Annie", "火女": "Annie",
    "阿菲利奥斯": "Aphelios", "艾瑞莉娅": "Irelia",
    "艾希": "Ashe", "寒冰": "Ashe", "寒冰射手": "Ashe",
    "奥恩": "Ornn", "奥拉夫": "Olaf", "奥瑞利安索尔": "AurelionSol",
    "奥莉安娜": "Orianna", "阿兹尔": "Azir", "艾克": "Ekko", "安贝萨": "Ambessa",
    "艾翁": "Ivern", "阿狸": "Ahri", "狐狸": "Ahri",
    "哭哭": "Amumu",
    # ===== B =====
    "巴德": "Bard", "贝尔维斯": "Belveth", "布兰德": "Brand", "布隆": "Braum",
    "布里茨": "Blitzcrank", "波比": "Poppy", "豹女": "Nidalee",
    "盲僧": "LeeSin",
    # ===== C =====
    "铸星龙王": "AurelionSol",
    # ===== D =====
    "大嘴": "KogMaw", "大头": "Heimerdinger", "大树": "Maokai",
    "刀妹": "Irelia", "德莱厄斯": "Darius", "德莱文": "Draven",
    "迪亚娜": "Diana", "黛安娜": "Diana",
    # ===== E =====
    "厄斐琉斯": "Aphelios", "俄洛伊": "Illaoi",
    "厄运小姐": "MissFortune",
    # ===== F =====
    "菲奥娜": "Fiora", "菲兹": "Fizz", "费德提克": "Fiddlesticks",
    "弗拉基米尔": "Vladimir", "弗雷尔卓德之心": "Braum",
    # ===== G =====
    "甘普朗克": "Gangplank", "船长": "Gangplank", "橘子": "Gangplank",
    "盖伦": "Garen", "格雷福斯": "Graves", "格温": "Gwen",
    "古拉加斯": "Gragas", "纳尔": "Gnar",
    "加里奥": "Galio",
    # ===== H =====
    "赫卡里姆": "Hecarim", "黑默丁格": "Heimerdinger",
    # ===== J =====
    "贾克斯": "Jax", "武器大师": "Jax", "武器": "Jax",
    "嘉文四世": "JarvanIV", "嘉文": "JarvanIV", "皇子": "JarvanIV",
    "杰斯": "Jayce", "劫": "Zed", "疾风剑豪": "Yasuo",
    "金克丝": "Jinx", "金克斯": "Jinx",
    "烬": "Jhin", "锦鲤": "Nami",
    "机器人": "Blitzcrank",
    "酒桶": "Gragas", "剑姬": "Fiora", "剑魔": "Aatrox",
    # ===== K =====
    "卡尔玛": "Karma", "卡莎": "Kaisa", "卡萨丁": "Kassadin",
    "卡特琳娜": "Katarina", "卡特": "Katarina", "女刀": "Katarina",
    "卡西奥佩娅": "Cassiopeia", "蛇女": "Cassiopeia",
    "卡蜜尔": "Camille", "青钢影": "Camille",
    "凯南": "Kennen", "凯尔": "Kayle", "凯隐": "Kayn", "凯特琳": "Caitlyn",
    "科加斯": "Chogath", "克烈": "Kled", "奎因": "Quinn", "克格莫": "KogMaw",
    "寇格": "KogMaw", "凯特灵": "Caitlyn",
    "卡兹克": "Khazix", "螳螂": "Khazix",
    # ===== L =====
    "拉克丝": "Lux", "拉莫斯": "Rammus", "兰博": "Rumble", "乐芙兰": "Leblanc",
    "雷克塞": "RekSai", "雷克顿": "Renekton", "雷恩加尔": "Rengar", "李青": "LeeSin",
    "莉莉娅": "Lillia", "丽桑卓": "Lissandra", "露露": "Lulu", "璐璐": "Lulu",
    "龙女": "Shyvana", "龙王": "AurelionSol", "洛": "Rakan", "卢锡安": "Lucian",
    "卢安": "Lucian",
    # ===== M =====
    "玛尔扎哈": "Malzahar", "马尔扎哈": "Malzahar",
    "冒险家": "Ezreal", "美杜莎": "Cassiopeia",
    "梦魇": "Nocturne", "蒙多": "DrMundo", "蒙多医生": "DrMundo",
    "魔腾": "Nocturne", "莫甘娜": "Morgana", "莫德凯撒": "Mordekaiser", "铁铠冥魂": "Mordekaiser",
    "墨菲特": "Malphite", "沐恩": "Milio", "微光": "Milio",
    "男枪": "Graves", "猫咪": "Yuumi", "木木": "Amumu",
    # ===== N =====
    "内瑟斯": "Nasus", "娜美": "Nami", "奈德丽": "Nidalee",
    "妮蔻": "Neeko", "诺克萨斯之手": "Darius", "诺手": "Darius", "小手": "Darius",
    "努努": "Nunu", "女枪": "MissFortune", "奶妈": "Soraka",
    "鸟人": "Quinn",
    # ===== O =====
    "欧拉夫": "Olaf",
    # ===== P =====
    "派克": "Pyke", "潘森": "Pantheon", "泡芙": "Lulu", "皮城女警": "Caitlyn",
    "琴女": "Sona", "爬行者": "KogMaw", "螃蟹": "Urgot",
    # ===== Q =====
    "奇亚娜": "Qiyana", "琪亚娜": "Qiyana", "千珏": "Kindred",
    "球女": "Orianna", "曲奇": "Zac",
    # ===== R =====
    "瑞兹": "Ryze", "瑞文": "Riven", "锐雯": "Riven", "芮尔": "Rell",
    "人马": "Hecarim", "瑞尔": "Rell",
    # ===== S =====
    "赛恩": "Sion", "赛拉斯": "Sylas", "赛娜": "Senna", "塞拉芬妮": "Seraphine",
    "萨勒芬妮": "Seraphine", "塞特": "Sett", "沙漠皇帝": "Azir",
    "莎弥拉": "Samira",
    "慎": "Shen", "石头人": "Malphite", "狮子狗": "Rengar",
    "斯卡纳": "Skarner", "斯维因": "Swain", "乌鸦": "Swain", "索拉卡": "Soraka", "孙悟空": "MonkeyKing",
    "松果": "Ivern", "索恩": "Sion", "日女": "Leona", "曙光": "Leona", "死歌": "Karthus",
    "星妈": "Soraka", "瞎子": "LeeSin", "瞎": "LeeSin",
    "深海泰坦": "Nautilus",
    "时光老人": "Zilean", "时光": "Zilean",
    "稻草人": "Fiddlesticks",
    # ===== T =====
    "塔里克": "Taric", "塔姆": "TahmKench", "塔莉垭": "Taliyah",
    "泰达米尔": "Tryndamere", "泰坦": "Nautilus",
    "探险家": "Ezreal", "提莫": "Teemo", "铁男": "Mordekaiser",
    "铁铠冥魂": "Mordekaiser",
    "图奇": "Twitch", "崔斯特": "TwistedFate", "崔丝塔娜": "Tristana",
    "特朗德尔": "Trundle", "陶器": "Galio",
    # ===== V/W =====
    "薇古丝": "Vex", "薇": "Vi", "维克托": "Viktor", "维克兹": "VelKoz",
    "维嘉": "Veigar", "小法": "Veigar", "小法师": "Veigar",
    "韦鲁斯": "Varus", "蔚": "Vi", "沃里克": "Warwick",
    "乌迪尔": "Udyr",
    "沃利贝尔": "Volibear", "狗熊": "Volibear",
    "薇恩": "Vayne", "暗夜猎手": "Vayne",
    # ===== X =====
    "霞": "Xayah", "希尔科": "Silco", "希维尔": "Sivir", "辛吉德": "Singed",
    "辛德拉": "Syndra", "锤石": "Thresh", "希瓦娜": "Shyvana",
    "瑟庄妮": "Sejuani", "虚空之女": "Kaisa",
    "猩红收割者": "Vladimir", "吸血鬼": "Vladimir",
    "小鱼": "Fizz", "小鱼人": "Fizz", "小炮": "Tristana",
    # ===== Y =====
    "亚索": "Yasuo", "快乐风男": "Yasuo", "亚托克斯": "Aatrox",
    "伊芙琳": "Evelynn", "寡妇": "Evelynn",
    "伊泽瑞尔": "Ezreal",
    "易": "MasterYi", "易大师": "MasterYi", "剑圣": "MasterYi",
    "永恩": "Yone", "约里克": "Yorick", "约德尔": None, "尤米": "Yuumi",
    "悠米": "Yuumi", "瑶": "Lillia", "影流之主": "Zed",
    "永岚": "YongLan",
    # ===== Z =====
    "扎克": "Zac", "泽拉斯": "Xerath",
    "赵信": "XinZhao", "蜘蛛女皇": "Elise", "蜘蛛": "Elise", "猪妹": "Sejuani",
    "炸弹人": "Ziggs",
    "祖安怒兽": "Warwick",
    "艾翠丝": "Elise", "伊莉丝": "Elise",
    "佐拉": "Zyra", "婕拉": "Zyra", "佐伊": "Zoe",
    "老鼠": "Twitch", "猴子": "MonkeyKing", "蛮王": "Tryndamere",
    "狗头": "Nasus", "牛头": "Alistar",
    # ===== 新英雄 =====
    "不破之誓": "Yunara", "芸阿娜": "Yunara", "云阿娜": "Yunara",
    "极光": "Aurora", "奥罗拉": "Aurora", "欧若拉": "Aurora", "双界灵兔": "Aurora",
    "斯莫德": "Smolder", "小龙": "Smolder",
    # ===== 英文简称 =====
    "EZ": "Ezreal", "ez": "Ezreal", "VN": "Vayne", "vn": "Vayne",
    "TF": "TwistedFate", "tf": "TwistedFate",
    "MF": "MissFortune", "mf": "MissFortune",
    "ADC": None,
}


# 全局缓存
_cache = None
_name_to_id = None


def _fix_mojibake(s: str) -> str:
    """尝试修复双重编码的乱码字符串。
    
    如果字符串是正常 UTF-8（如刚爬取的新数据），直接原样返回。
    只有确实是 latin1→utf8 双重编码时才修复。
    """
    if not isinstance(s, str):
        return s
    try:
        # 只有能完整 encode 为 latin1 时，才说明是双重编码
        return s.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        # encode('latin1') 失败 = 字符串已经是正常 UTF-8，直接返回
        return s


def _build_name_map(data: dict) -> dict:
    """从缓存数据构建 中文名/英文名 -> 英文ID 的查找字典。"""
    name_map = {}
    champions = data.get("champions", {})
    for champ_id, champ_data in champions.items():
        name_map[champ_id] = champ_id
        name_map[champ_id.lower()] = champ_id

        cn_title = champ_data.get("cn_title", "")
        if cn_title:
            fixed_title = _fix_mojibake(cn_title)
            name_map[cn_title] = champ_id
            if fixed_title != cn_title:
                name_map[fixed_title] = champ_id

        cn_name = champ_data.get("cn_name", "")
        if cn_name:
            fixed_name = _fix_mojibake(cn_name)
            name_map[cn_name] = champ_id
            if fixed_name != cn_name:
                name_map[fixed_name] = champ_id
            parts = fixed_name.split()
            if len(parts) > 1:
                name_map[parts[-1]] = champ_id

    return name_map


def load_cache(cache_dir: str) -> dict:
    """加载本地缓存数据。"""
    global _cache, _name_to_id
    cache_file = os.path.join(cache_dir, "apexlol_data.json")

    if not os.path.exists(cache_file):
        log.warning(f"[ApexLol] 缓存文件不存在: {cache_file}")
        return {}

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            _cache = json.load(f)
        _name_to_id = _build_name_map(_cache)
        champion_count = len(_cache.get("champions", {}))
        log.info(f"[ApexLol] 缓存加载成功: {champion_count} 个英雄")
        return _cache
    except Exception as e:
        log.error(f"[ApexLol] 缓存加载失败: {e}")
        return {}


def is_cache_valid(cache_dir: str, ttl_days: int = 7) -> bool:
    """检查缓存是否存在且未过期。"""
    cache_file = os.path.join(cache_dir, "apexlol_data.json")
    try:
        if not os.path.exists(cache_file):
            return False
        mtime = os.path.getmtime(cache_file)
        age_days = (time.time() - mtime) / 86400
        return age_days < ttl_days
    except Exception:
        return False


def resolve_champion_id(name: str) -> str | None:
    """将英雄名（中文/英文/别名）解析为英文 ID。"""
    global _name_to_id

    if name in CHAMPION_ALIASES:
        cid = CHAMPION_ALIASES[name]
        if cid:
            log.debug(f"[ApexLol] 别名直接匹配: {name} -> {cid}")
            return cid

    if _name_to_id is None:
        log.debug(f"[ApexLol] 缓存未加载，仅使用别名表查找: {name}")
        return None

    if name in _name_to_id:
        return _name_to_id[name]

    lower = name.lower()
    if lower in _name_to_id:
        return _name_to_id[lower]

    for key, cid in _name_to_id.items():
        if name in key or key in name:
            log.debug(f"[ApexLol] 模糊匹配成功: {name} -> {cid} (匹配项: {key})")
            return cid

    log.warning(f"[ApexLol] 英雄名解析失败: {name}")
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

    cn_title = _fix_mojibake(champ_data.get("cn_title", champ_id))

    all_valid_names = []
    for s in champ_data["synergies"]:
        for hname in s.get("hex_names", []):
            fixed = _fix_mojibake(hname)
            if fixed and fixed not in all_valid_names:
                all_valid_names.append(fixed)

    lines = [f"【{cn_title}({champ_id}) 海克斯联动分析 - 来源: apexlol.info】"]
    if all_valid_names:
        lines.append(f"📜 [标准海克斯名单 - 严禁修改字符]: {', '.join(all_valid_names)}")
        lines.append("-" * 30)

    for s in champ_data["synergies"]:
        hex_names = " | ".join([_fix_mojibake(h) for h in s.get("hex_names", [])])
        rating = _fix_mojibake(s.get("rating", ""))
        tag = _fix_mojibake(s.get("tag", ""))
        analysis = _fix_mojibake(s.get("analysis", ""))
        tag_info = f" [{tag}]" if tag else ""
        lines.append(f"  [{rating}]{tag_info} {hex_names}")
        lines.append(f"    {analysis}")
        lines.append("")

    return "\n".join(lines)


def lookup_champions(names: list[str], highlight_mine: str = None) -> str:
    """批量查询多个英雄的联动数据，拼接为 Gemini 可用的参考文本。"""
    sections = []

    ordered = list(names)
    if highlight_mine and highlight_mine in ordered:
        ordered.remove(highlight_mine)
        ordered.insert(0, highlight_mine)

    for name in ordered:
        text = lookup_champion(name)
        if not text:
            continue
        if name == highlight_mine:
            text = f"⭐ [你的英雄] ⭐\n{text}"
        sections.append(text)

    if not sections:
        return ""

    header = (
        "=" * 60 + "\n"
        "📊 以下是来自 apexlol.info 的真实高分英雄联动数据（由玩家社区贡献的机制级分析）。\n"
        "请根据以下数据推荐海克斯符文，特别注意隐藏的联动机制（如某技能能触发特定符文效果等）。\n"
        "注意：这些数据是参考建议，请结合当前阵容做出最佳判断。\n"
        "=" * 60
    )
    return header + "\n\n" + "\n\n".join(sections)


# ==================== 评分排序权重 ====================
_RATING_ORDER = {"sss": 0, "ss": 1, "s": 2, "a": 3, "b": 4, "c": 5, "d": 6}


def _parse_rating_key(rating_str: str) -> int:
    """将 'S 级'、'SS 级' 等字符串解析为排序权重（越小越强）。"""
    if not rating_str:
        return 99
    cleaned = _fix_mojibake(rating_str).strip().upper().replace("级", "").replace(" ", "")
    for key, val in _RATING_ORDER.items():
        if cleaned.startswith(key.upper()):
            return val
    return 99


def extract_top_synergies(champion_name: str, top_n: int = 8) -> str:
    """从 ApexLol 缓存中按评分排序，直接提取该英雄的前 N 组海克斯联动方案。
    返回格式化的 Markdown 字符串，可直接作为"预填答案"嵌入 prompt。

    这是"数据驱动"的核心函数：符文方案不靠 AI 猜，而是从真实数据中硬抽。
    会自动将"陷阱"标签的方案分离出来，单独以警告形式展示。
    """
    global _cache
    if not _cache:
        return ""

    champ_id = resolve_champion_id(champion_name)
    if not champ_id:
        log.warning(f"[ApexLol] extract_top_synergies: 英雄名 {champion_name} 解析失败")
        return ""

    champ_data = _cache.get("champions", {}).get(champ_id)
    if not champ_data or not champ_data.get("synergies"):
        log.warning(f"[ApexLol] extract_top_synergies: {champ_id} 在缓存中无联动数据")
        return ""

    cn_title = _fix_mojibake(champ_data.get("cn_title", champ_id))
    synergies = champ_data["synergies"]
    
    # 分为陷阱和正常两组
    traps = [s for s in synergies if "陷阱" in _fix_mojibake(s.get("tag", ""))]
    normals = [s for s in synergies if "陷阱" not in _fix_mojibake(s.get("tag", ""))]
    
    # 各自按评分排序（SSS > SS > S > A > B > C > D）
    traps_sorted = sorted(traps, key=lambda s: _parse_rating_key(s.get("rating", "")))
    normals_sorted = sorted(normals, key=lambda s: _parse_rating_key(s.get("rating", "")))
    
    # 陷阱在前，正常在后
    sorted_syns = traps_sorted + normals_sorted
    
    if not sorted_syns:
        return ""
    
    lines = [
        f"### 🎲 海克斯符文推荐：{cn_title}（数据来源: apexlol.info）",
        ""
    ]
    
    for i, syn in enumerate(sorted_syns[:top_n]):
        hex_names = [_fix_mojibake(h) for h in syn.get("hex_names", [])]
        raw_rating = _fix_mojibake(syn.get("rating", "")).upper()
        # 去掉原始数据中可能自带的"级"字，避免 "S 级 级" 的重复
        rating = raw_rating.replace("级", "").strip() if raw_rating else "未知"
        tiers = " / ".join([_fix_mojibake(t) for t in syn.get("hex_tiers", [])])
        tag = _fix_mojibake(syn.get("tag", ""))
        analysis = _fix_mojibake(syn.get("analysis", ""))
        
        hex_display = " + ".join(hex_names) if hex_names else "未知"
        rec_items = [_fix_mojibake(it) for it in syn.get("recommended_items", [])]
        
        # 根据标签决定图标
        is_trap = "陷阱" in tag
        icon = "❌" if is_trap else "🏆"
        tag_display = "⚠️陷阱" if is_trap else tag
        
        lines.append(f"#### {icon} 【{rating}级方案】 {f'({tiers})' if tiers else ''}")
        lines.append(f"- **核心组合**: {hex_display}")
        if tag_display:
            lines.append(f"- **流派标签**: {tag_display}")
        if rec_items:
            lines.append(f"- **搭配出装**: {' → '.join(rec_items)}")
        if analysis:
            lines.append(f"- **机制解析**: {analysis}")
        lines.append("")
    
    # 如果 top_n 之外还有陷阱未展示，也追加警告
    remaining_traps = [s for s in traps_sorted if s not in sorted_syns[:top_n]]
    if remaining_traps:
        lines.append("#### ⚠️ 其他需要避开的陷阱海克斯")
        for syn in remaining_traps:
            hex_names = [_fix_mojibake(h) for h in syn.get("hex_names", [])]
            analysis = _fix_mojibake(syn.get("analysis", ""))
            hex_display = " + ".join(hex_names) if hex_names else "未知"
            reason = analysis[:80] + "..." if len(analysis) > 80 else analysis
            lines.append(f"- ❌ {hex_display}：{reason}")
        lines.append("")
    
    return "\n".join(lines)


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


def get_hextech_description(hextech_name: str) -> str:
    """获取指定海克斯的官方效果描述和特殊机制。

    Args:
        hextech_name: 海克斯中文名 (如 "罪恶快感", "速度恶魔")

    Returns:
        包含描述和机制的文本，如果没找到则返回空字符串。
    """
    global _cache
    if not _cache:
        return ""

    details = _cache.get("hextech_details", {})
    # 模糊匹配
    fixed_name = _fix_mojibake(hextech_name)
    for k, v in details.items():
        fixed_k = _fix_mojibake(k)
        if fixed_name in fixed_k or fixed_k in fixed_name:
            desc = _fix_mojibake(v.get("description", ""))
            mech = _fix_mojibake(v.get("mechanism", ""))
            
            result_parts = []
            if desc:
                result_parts.append(desc)
            if mech:
                result_parts.append(f"[特殊机制] {mech}")
            return " | ".join(result_parts)

    return ""


# ==================== OCR 本地海克斯快速推荐 ====================
_ocr_engine = None


def _get_ocr():
    """懒加载 OCR 引擎（首次约1s，后续0ms）。"""
    global _ocr_engine
    if _ocr_engine is None:
        from rapidocr_onnxruntime import RapidOCR
        _ocr_engine = RapidOCR()
    return _ocr_engine


def _fuzzy_match_augment(ocr_text: str, valid_names: list[str]) -> str | None:
    """将 OCR 识别的文本模糊匹配到标准海克斯名。"""
    import difflib
    
    ocr_text = ocr_text.strip()
    if not ocr_text or len(ocr_text) < 2:
        return None
        
    # 黑名单拦截：游戏中大量出现的无用极短干扰词（避免错误包含匹配）
    blacklist = ['刷新', '重随', '重新', '选择', '技能', '攻击', '伤害', '护甲', '魔抗', '生命', '回复', '确认', '取消', '物理', '魔法', '综合']
    for b in blacklist:
        if ocr_text == b:
            return None
            
    # 精确匹配（最优先）
    for name in valid_names:
        if ocr_text == name:
            return name
            
    # 包含匹配（OCR少读了字，或者名字包含OCR）
    # 为防止 "刷新" 去匹配 "终极刷新"，只有在长度相近时才接受包含匹配
    for name in valid_names:
        if name in ocr_text or ocr_text in name:
            if len(ocr_text) >= 2 and abs(len(name) - len(ocr_text)) <= 2:
                return name
                
    # 相似度模糊匹配（处理1~2个错别字）
    best_match = None
    best_score = 0
    for name in valid_names:
        # difflib 的 ratio 计算匹配度
        r = difflib.SequenceMatcher(None, ocr_text, name).ratio()
        if r > best_score:
            best_score = r
            best_match = name
            
    # 阈值：极短词需要几乎全对，长词可以容忍较多错误（应对复杂背景下的严重乱码，如"珠元护子"）
    threshold = 0.8 if len(ocr_text) <= 3 else 0.45
    if best_score >= threshold:
        return best_match
        
    return None


def ocr_hextech_names(image_path: str, champion_name: str = None) -> list[str] | None:
    """OCR 识别截图中的海克斯符文名（仅读名，不做推荐）。

    Returns:
        匹配到的海克斯名列表，失败返回 None
    """
    global _cache
    if not _cache:
        return None

    # 构建全局海克斯名单
    all_augment_names = []
    for cid, cdata in _cache.get("champions", {}).items():
        for syn in cdata.get("synergies", []):
            for hname in syn.get("hex_names", []):
                fixed = _fix_mojibake(hname)
                if fixed and fixed not in all_augment_names:
                    all_augment_names.append(fixed)

    if not all_augment_names:
        return None

    # OCR 识别：裁剪画面中部区域，避免顶部计分板、底部聊天框及状态栏干扰
    try:
        import cv2
        img = cv2.imread(image_path)
        ocr = _get_ocr()
        
        if img is not None:
            H, W = img.shape[:2]
            # 截取中心垂直30%到70%，水平10%到90%的区域 (确保包含了所有的海克斯选项)
            crop_img = img[int(H * 0.3):int(H * 0.7), int(W * 0.1):int(W * 0.9)]
            result, _ = ocr(crop_img)
        else:
            # 万一读图失败，退回直接传路径
            result, _ = ocr(image_path)
            
        if not result:
            log.warning("[OCR] 未识别到任何文本")
            return None
    except Exception as e:
        log.error(f"[OCR] 引擎异常: {e}")
        return None

    # 匹配海克斯名
    matched = []
    for bbox, text, confidence in result:
        if confidence < 0.7 or len(text) > 8:
            continue
        name = _fuzzy_match_augment(text, all_augment_names)
        if name and name not in matched:
            matched.append(name)

    if not matched:
        log.warning(f"[OCR] 未匹配到已知海克斯名。OCR结果: {[r[1] for r in result if r[2]>0.7]}")
        return None

    log.info(f"[OCR] ✅ 识别到 {len(matched)} 个海克斯: {matched}")
    return matched


def ocr_hextech_recommend(image_path: str, champion_name: str,
                          hextech_history: list[str] = None) -> str | None:
    """纯本地 OCR + ApexLol 查表的海克斯推荐（无网络，<2s）。

    Returns:
        格式化的推荐文本，如果 OCR 失败或无法匹配则返回 None（交给 AI 兜底）
    """
    global _cache
    if not _cache:
        return None

    champ_id = resolve_champion_id(champion_name)
    if not champ_id:
        return None

    champ_data = _cache.get("champions", {}).get(champ_id)
    if not champ_data or not champ_data.get("synergies"):
        return None

    # 1. 构建全局海克斯名单（所有英雄的联动数据中的符文名）
    all_augment_names = []
    for cid, cdata in _cache.get("champions", {}).items():
        for syn in cdata.get("synergies", []):
            for hname in syn.get("hex_names", []):
                fixed = _fix_mojibake(hname)
                if fixed and fixed not in all_augment_names:
                    all_augment_names.append(fixed)

    if not all_augment_names:
        return None

    # 2. OCR 识别截图中的文字
    try:
        ocr = _get_ocr()
        result, _ = ocr(image_path)
        if not result:
            log.warning("[OCR] 未识别到任何文本")
            return None
    except Exception as e:
        log.error(f"[OCR] 引擎异常: {e}")
        return None

    # 3. 从 OCR 结果中匹配海克斯名（只取高置信度的短文本=标题）
    matched_augments = []
    for bbox, text, confidence in result:
        if confidence < 0.7 or len(text) > 8:  # 符文名通常2-6个中文字
            continue
        matched = _fuzzy_match_augment(text, all_augment_names)
        if matched and matched not in matched_augments:
            matched_augments.append(matched)

    if not matched_augments:
        log.warning(f"[OCR] 未能匹配到任何已知海克斯名。OCR结果: {[r[1] for r in result if r[2]>0.7]}")
        return None

    log.info(f"[OCR] ✅ 识别到 {len(matched_augments)} 个海克斯: {matched_augments}")

    # 4. 对匹配到的海克斯，从 ApexLol 数据中查评级并排序
    cn_title = _fix_mojibake(champ_data.get("cn_title", champ_id))
    history_str = "、".join(hextech_history) if hextech_history else "无"

    # 为每个识别到的符文查找相关方案（优先本英雄，兜底跨英雄）
    augment_info = []
    for aug_name in matched_augments:
        best_syn = None
        best_rating = 99
        is_my_champ = False
        # 先在本英雄里找
        for syn in champ_data["synergies"]:
            hex_names_fixed = [_fix_mojibake(h) for h in syn.get("hex_names", [])]
            if aug_name in hex_names_fixed:
                rating_val = _parse_rating_key(syn.get("rating", ""))
                if rating_val < best_rating:
                    best_rating = rating_val
                    best_syn = syn
                    is_my_champ = True
        # 本英雄没有，全局搜索（取最佳评级作为参考）
        if not best_syn:
            for cid, cdata in _cache.get("champions", {}).items():
                for syn in cdata.get("synergies", []):
                    hex_names_fixed = [_fix_mojibake(h) for h in syn.get("hex_names", [])]
                    if aug_name in hex_names_fixed:
                        rating_val = _parse_rating_key(syn.get("rating", ""))
                        if rating_val < best_rating:
                            best_rating = rating_val
                            best_syn = syn
        if best_syn:
            augment_info.append((aug_name, best_syn, best_rating, is_my_champ))

    # 按评级排序（越小越强），本英雄数据优先
    augment_info.sort(key=lambda x: (0 if x[3] else 1, x[2]))

    # 5. 格式化输出
    lines = [f"## ⚡ 海克斯推荐（{cn_title} - 本地极速版）"]
    lines.append(f"已选历史: {history_str}")
    lines.append("")

    if not augment_info:
        lines.append("⚠️ 识别到的海克斯不在 ApexLol 数据库中，建议按直觉选择")
        return "\n".join(lines)

    # 推荐第一个（评级最高的）
    top_name, top_syn, _, top_is_mine = augment_info[0]
    raw_rating = _fix_mojibake(top_syn.get("rating", "")).upper().replace("级", "").strip()
    tag = _fix_mojibake(top_syn.get("tag", ""))
    is_trap = "陷阱" in tag
    analysis = _fix_mojibake(top_syn.get("analysis", ""))
    rec_items = [_fix_mojibake(it) for it in top_syn.get("recommended_items", [])]
    hex_combo = " + ".join([_fix_mojibake(h) for h in top_syn.get("hex_names", [])])

    if is_trap:
        lines.append(f"### ❌ 警告：【{top_name}】是陷阱！避开！")
        lines.append(f"- 评级: {raw_rating}级 | 标签: ⚠️陷阱")
        if analysis:
            lines.append(f"- 原因: {analysis}")
        # 推荐非陷阱的
        non_trap = [x for x in augment_info if "陷阱" not in _fix_mojibake(x[1].get("tag", ""))]
        if non_trap:
            rec_name, rec_syn, _, _ = non_trap[0]
            rec_rating = _fix_mojibake(rec_syn.get("rating", "")).upper().replace("级", "").strip()
            rec_tag = _fix_mojibake(rec_syn.get("tag", ""))
            rec_analysis = _fix_mojibake(rec_syn.get("analysis", ""))
            lines.append(f"\n### 🏆 推荐选择：【{rec_name}】")
            lines.append(f"- 评级: {rec_rating}级 | 标签: {rec_tag}")
            if rec_analysis:
                lines.append(f"- 解析: {rec_analysis}")
    else:
        lines.append(f"### 🏆 推荐选择：【{top_name}】← 选这个")
        lines.append(f"- 评级: {raw_rating}级 | 标签: {tag}")
        lines.append(f"- 所属组合: {hex_combo}")
        if rec_items:
            lines.append(f"- 搭配出装: {' → '.join(rec_items)}")
        if analysis:
            lines.append(f"- 解析: {analysis}")

    # 列出其他选项
    others = [x for x in augment_info if x is not augment_info[0]]
    if is_trap and 'non_trap' in dir() and non_trap:
        others = [x for x in others if x is not non_trap[0]]
    if others:
        lines.append("\n### 其他选项")
        for name, syn, _, is_mine in others:
            r = _fix_mojibake(syn.get("rating", "")).upper().replace("级", "").strip()
            t = _fix_mojibake(syn.get("tag", ""))
            trap_mark = " ⚠️陷阱" if "陷阱" in t else ""
            lines.append(f"- {name}: {r}级{trap_mark} — {t}")

    return "\n".join(lines)
