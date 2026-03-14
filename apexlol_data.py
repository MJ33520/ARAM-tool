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
    "阿尼维亚": "Anivia", "安妮": "Annie", "阿菲利奥斯": "Aphelios", "艾瑞莉娅": "Irelia",
    "艾希": "Ashe", "奥恩": "Ornn", "奥拉夫": "Olaf", "奥瑞利安索尔": "AurelionSol",
    "奥莉安娜": "Orianna", "阿兹尔": "Azir", "艾克": "Ekko", "安贝萨": "Ambessa",
    # ===== B =====
    "巴德": "Bard", "贝尔维斯": "Belveth", "布兰德": "Brand", "布隆": "Braum",
    "布里茨": "Blitzcrank",
    # ===== C =====
    "才藏": "Hwei", "铸星龙王": "AurelionSol",
    # ===== D =====
    "大嘴": "KogMaw", "大头": "Heimerdinger", "黛安娜": "Diana", "刀妹": "Irelia",
    "德莱厄斯": "Darius", "德莱文": "Draven", "迪亚娜": "Diana",
    # ===== E =====
    "厄加特": "Urgot", "厄斐琉斯": "Aphelios", "俄洛伊": "Illaoi",
    "恕瑞玛皇帝": "Azir",
    # ===== F =====
    "菲奥娜": "Fiora", "菲兹": "Fizz", "弗拉基米尔": "Vladimir", "弗雷尔卓德之心": "Braum",
    "费德提克": "Fiddlesticks",
    # ===== G =====
    "盖伦": "Garen", "甘普朗克": "Gangplank", "格雷福斯": "Graves", "格温": "Gwen",
    "古拉加斯": "Gragas", "光辉女郎": "Lux",
    # ===== H =====
    "海克斯科技枪": None, "赫卡里姆": "Hecarim", "黑默丁格": "Heimerdinger",
    "厚嘴": "KogMaw",
    # ===== I/J =====
    "吉格斯": "Ziggs", "基兰": "Zilean", "贾克斯": "Jax", "嘉文四世": "JarvanIV",
    "锦鲤": "Nami", "金克丝": "Jinx", "金克斯": "Jinx", "杰斯": "Jayce", "劫": "Zed",
    "疾风剑豪": "Yasuo", "嘉文": "JarvanIV",
    "加里奥": "Galio", "佐伊": "Zoe",
    # ===== K =====
    "卡尔玛": "Karma", "卡尔萨斯": "Karthus", "卡莉斯塔": "Kalista", "卡密尔": "Camille",
    "卡萨丁": "Kassadin", "卡莎": "Kaisa", "卡兹克": "Khazix", "卡特琳娜": "Katarina",
    "卡特": "Katarina", "卡西奥佩娅": "Cassiopeia", "卡蜜尔": "Camille",
    "凯南": "Kennen", "凯尔": "Kayle", "凯隐": "Kayn", "凯特琳": "Caitlyn",
    "科加斯": "Chogath", "克烈": "Kled", "奎因": "Quinn", "克格莫": "KogMaw",
    "寇格": "KogMaw", "孔": "Wukong",
    # ===== L =====
    "拉克丝": "Lux", "拉莫斯": "Rammus", "兰博": "Rumble", "乐芙兰": "Leblanc",
    "雷克塞": "RekSai", "雷克顿": "Renekton", "雷恩加尔": "Rengar", "李青": "LeeSin",
    "莉莉娅": "Lillia", "丽桑卓": "Lissandra", "露露": "Lulu", "璐璐": "Lulu",
    "龙女": "Shyvana", "龙王": "AurelionSol", "洛": "Rakan", "卢锡安": "Lucian",
    "卢安": "Lucian",
    # ===== M =====
    "玛尔扎哈": "Malzahar", "冒险家": "Ezreal", "美杜莎": "Cassiopeia",
    "梦魇": "Nocturne", "蒙多": "DrMundo", "蒙多医生": "DrMundo",
    "魔腾": "Mordekaiser", "莫甘娜": "Morgana", "莫德凯撒": "Mordekaiser",
    "墨菲特": "Malphite", "沐恩": "Milio",
    # ===== N =====
    "纳尔": "Gnar", "内瑟斯": "Nasus", "娜美": "Nami", "奈德丽": "Nidalee",
    "妮蔻": "Neeko", "诺克萨斯之手": "Darius", "诺手": "Darius",
    "努努": "Nunu", "女枪": "MissFortune", "女刀": "Katarina",
    # ===== O =====
    "欧拉夫": "Olaf",
    # ===== P =====
    "派克": "Pyke", "潘森": "Pantheon", "泡芙": "Lulu", "皮城女警": "Caitlyn",
    "琴女": "Sona",
    # ===== Q =====
    "奇亚娜": "Qiyana", "琪亚娜": "Qiyana", "千珏": "Kindred", "青钢影": "Camille",
    "球女": "Orianna", "曲奇": "Zac",
    # ===== R =====
    "瑞兹": "Ryze", "瑞文": "Riven", "锐雯": "Riven", "芮尔": "Rell",
    "人马": "Hecarim", "瑞尔": "Rell",
    # ===== S =====
    "赛恩": "Sion", "赛拉斯": "Sylas", "赛娜": "Senna", "塞拉芬妮": "Seraphine",
    "萨勒芬妮": "Seraphine", "塞特": "Sett", "沙漠皇帝": "Azir",
    "厄运小姐": "MissFortune", "莎弥拉": "Samira",
    "慎": "Shen", "石头人": "Malphite", "狮子狗": "Rengar",
    "斯卡纳": "Skarner", "斯维因": "Swain", "索拉卡": "Soraka", "孙悟空": "MonkeyKing",
    "松果": "Ivern", "索恩": "Sion",
    "蛇女": "Cassiopeia", "深海泰坦": "Nautilus",
    "时光老人": "Zilean", "时光": "Zilean",
    "机器人": "Blitzcrank", "稻草人": "Fiddlesticks",
    "酒桶": "Gragas", "皇子": "JarvanIV", "螳螂": "Khazix",
    "薇恩": "Vayne",
    # ===== T =====
    "塔里克": "Taric", "塔姆": "TahmKench", "塔莉垭": "Taliyah",
    "泰达米尔": "Tryndamere", "泰坦": "Nautilus",
    "探险家": "Ezreal", "提莫": "Teemo", "铁男": "Mordekaiser",
    "图奇": "Twitch", "崔斯特": "TwistedFate", "崔丝塔娜": "Tristana",
    "特朗德尔": "Trundle", "陶器": "Galio",
    # ===== V/W =====
    "薇古丝": "Vex", "薇": "Vi", "维克托": "Viktor", "维克兹": "VelKoz",
    "维嘉": "Veigar", "小法": "Veigar", "小法师": "Veigar",
    "韦鲁斯": "Varus", "蔚": "Vi", "沃里克": "Warwick",
    "乌迪尔": "Udyr", "武器大师": "Jax",
    "沃利贝尔": "Volibear", "狗熊": "Volibear",
    "微光": "Milio",
    # ===== X =====
    "霞": "Xayah", "希尔科": "Silco", "希维尔": "Sivir", "辛吉德": "Singed",
    "辛德拉": "Syndra", "锤石": "Thresh", "希瓦娜": "Shyvana",
    "许尔马": "Xayah", "小鱼人": "Fizz", "小炮": "Tristana",
    "瑟庄妮": "Sejuani", "虚空之女": "Kaisa",
    "猩红收割者": "Vladimir", "兴奋": "Jinx",
    # ===== Y =====
    "亚索": "Yasuo", "亚托克斯": "Aatrox", "伊芙琳": "Evelynn", "伊泽瑞尔": "Ezreal",
    "易": "MasterYi", "易大师": "MasterYi", "剑圣": "MasterYi",
    "永恩": "Yone", "约里克": "Yorick", "约德尔": None, "尤米": "Yuumi",
    "悠米": "Yuumi", "瑶": "Lillia", "影流之主": "Zed",
    # ===== Z =====
    "扎克": "Zac", "寨安": "Zaun", "泽拉斯": "Xerath",
    "赵信": "XinZhao", "蜘蛛女皇": "Elise", "猪妹": "Sejuani",
    "诸葛亮": None, "烬": "Jhin", "炸弹人": "Ziggs",
    "祖安怒兽": "Warwick",
    "艾翠丝": "Elise", "伊莉丝": "Elise",
    "佐拉": "Zyra", "婕拉": "Zyra",
    "老鼠": "Twitch", "猴子": "MonkeyKing", "蛮王": "Tryndamere",
    "狗头": "Nasus", "牛头": "Alistar",
    # ===== 英文简称 =====
    "EZ": "Ezreal", "ez": "Ezreal", "VN": "Vayne", "vn": "Vayne",
    "ADC": None,
}


# 全局缓存
_cache = None
_name_to_id = None


def _fix_mojibake(s: str) -> str:
    """尝试修复双重编码的乱码字符串（如 ä¸\\x8dç¥¥ä¹\\x8bå\\x88\\x83 -> 不祥之刃）"""
    if not isinstance(s, str):
        return s
    try:
        # 第一层尝试：完美转换
        return s.encode('latin1').decode('utf-8')
    except Exception:
        pass
    try:
        # 第二层尝试：容错转换（丢弃尾部无法解析的损坏字节，保留前面的正常汉字）
        return s.encode('latin1', errors='ignore').decode('utf-8', errors='ignore')
    except Exception:
        return s


def _build_name_map(data: dict) -> dict:
    """从缓存数据构建 名称 -> ID 的映射表。"""
    name_map = {}

    # 从 champion_list 构建
    for champ in data.get("champion_list", []):
        champ_id = champ["id"]
        cn_title = _fix_mojibake(champ.get("cn_title", ""))

        # 中文标题 -> ID（如 "不祥之刃" -> "Katarina"）
        if cn_title:
            name_map[cn_title] = champ_id

        # 英文 ID 本身（大小写不敏感）
        name_map[champ_id.lower()] = champ_id

    # 从 champions 数据构建
    for champ_id, info in data.get("champions", {}).items():
        cn_title = _fix_mojibake(info.get("cn_title", ""))
        if cn_title:
            name_map[cn_title] = champ_id
            
        cn_name = _fix_mojibake(info.get("cn_name", ""))
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


# ==================== 评分排序权重 ====================
_RATING_ORDER = {"sss": 0, "ss": 1, "s": 2, "a": 3, "b": 4, "c": 5}

def _parse_rating_key(rating_str: str) -> int:
    """将 'S 级'、'SS 级' 等字符串解析为排序权重（越小越强）。"""
    if not rating_str:
        return 99
    cleaned = rating_str.strip().upper().replace("级", "").replace(" ", "")
    for key, val in _RATING_ORDER.items():
        if cleaned.startswith(key.upper()):
            return val
    return 99


def extract_top_synergies(champion_name: str, top_n: int = 3) -> str:
    """
    从 ApexLol 缓存中按评分排序，直接提取该英雄的前 N 组海克斯联动方案。
    返回格式化的 Markdown 字符串，可直接作为"预填答案"嵌入 prompt。
    
    这是"数据驱动"的核心函数：符文方案不靠 AI 猜，而是从真实数据中硬抽。
    """
    global _cache
    if not _cache:
        return ""
    
    champ_id = resolve_champion_id(champion_name)
    if not champ_id:
        return ""
    
    champ_data = _cache.get("champions", {}).get(champ_id)
    if not champ_data or not champ_data.get("synergies"):
        return ""
    
    cn_title = _fix_mojibake(champ_data.get("cn_title", champ_id))
    synergies = champ_data["synergies"]
    
    # 按评级从高到低排序（SSS > SS > S > A > B > C > D）
    sorted_syns = sorted(synergies, key=lambda s: _parse_rating_key(s.get("rating", "")))
    
    # 直接展示全部方案，按评级高低依次排列，有几个放几个
    if not sorted_syns:
        return ""
    
    lines = [
        f"### 🎲 海克斯符文推荐：{cn_title}（数据来源: apexlol.info，按胜率排序）",
        ""
    ]
    
    for i, syn in enumerate(sorted_syns):
        hex_names = [_fix_mojibake(h) for h in syn.get("hex_names", [])]
        rating = _fix_mojibake(syn.get("rating", "")).upper()
        if not rating: rating = "未知"
        tiers = " / ".join([_fix_mojibake(t) for t in syn.get("hex_tiers", [])])
        tag = _fix_mojibake(syn.get("tag", ""))
        analysis = _fix_mojibake(syn.get("analysis", ""))
        
        hex_display = " + ".join(hex_names) if hex_names else "未知"
        
        # 使用等级作为头衔，例如 【SSS 级推荐】
        lines.append(f"#### 🏆 【{rating} 级方案】 {f'({tiers})' if tiers else ''}")
        lines.append(f"- **核心组合**: {hex_display}")
        if tag:
            lines.append(f"- **流派标签**: {tag}")
        if analysis:
            lines.append(f"- **机制解析**: {analysis}")
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
