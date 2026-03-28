# -*- coding: utf-8 -*-
"""
ARAM 助手 - LCU API 客户端

通过 League Client Update (LCU) API 直接从英雄联盟客户端读取英雄选择数据。
使用 psutil 从进程命令行参数提取 port 和 token（兼容 WeGame 国服）。
"""

import json
import urllib3
import psutil
import requests
try:
    from logger import log
except ImportError:
    import logging
    log = logging.getLogger("LCU")

# 禁用 SSL 警告（LCU 使用自签名证书）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 英雄 ID → 中文名映射缓存
_champion_names: dict[int, str] = {}
# 英雄 英文ID(如'Tristana') → 中文名映射缓存
_champion_id_to_cn: dict[str, str] = {}
# 符文/海克斯 ID -> 名称映射
_perk_metadata: dict[int, str] = {}



# 连接信息缓存（避免每次都扫描进程）
_cached_port: int | None = None
_cached_token: str | None = None


def _find_lcu_connection() -> tuple[int, str] | None:
    """
    通过 psutil 从 LeagueClientUx.exe 进程命令行参数获取 LCU API 的 port 和 token。
    WeGame 国服的 lockfile 是空的，所以必须从进程参数提取。

    Returns:
        tuple: (port, token) 或 None
    """
    global _cached_port, _cached_token

    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if proc.info['name'] == 'LeagueClientUx.exe':
                args = proc.info['cmdline'] or []
                port = None
                token = None
                for a in args:
                    if a.startswith('--app-port='):
                        port = int(a.split('=')[1])
                    elif a.startswith('--remoting-auth-token='):
                        token = a.split('=')[1]
                if port and token:
                    _cached_port = port
                    _cached_token = token
                    return port, token
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    _cached_port = None
    _cached_token = None
    return None


def _get_connection() -> tuple[int, str] | None:
    """获取 LCU 连接信息（优先使用缓存，不额外验证）。"""
    global _cached_port, _cached_token
    if _cached_port and _cached_token:
        return _cached_port, _cached_token
    return _find_lcu_connection()


def _invalidate_cache():
    """清除连接缓存，下次调用会重新扫描进程。"""
    global _cached_port, _cached_token
    _cached_port = None
    _cached_token = None


def _lcu_request(port: int, token: str, endpoint: str) -> dict | list | None:
    """
    向 LCU API 发送 GET 请求。
    如果连接被拒绝（客户端已关闭），自动清除缓存。

    Args:
        port: LCU API 端口
        token: 认证 token
        endpoint: API 端点路径

    Returns:
        JSON 响应数据或 None
    """
    url = f"https://127.0.0.1:{port}{endpoint}"
    try:
        response = requests.get(
            url,
            auth=("riot", token),
            verify=False,
            timeout=5,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except (requests.exceptions.ConnectionError, ConnectionResetError):
        # 连接被拒绝/重置 = 客户端已关闭，清除缓存
        _invalidate_cache()
        return None
    except Exception:
        return None


def _lcu_post(port: int, token: str, endpoint: str) -> tuple[int, dict | str | None]:
    """
    向 LCU API 发送 POST 请求。

    Args:
        port: LCU API 端口
        token: 认证 token
        endpoint: API 端点路径

    Returns:
        tuple: (status_code, response_data)
    """
    url = f"https://127.0.0.1:{port}{endpoint}"
    try:
        response = requests.post(
            url,
            auth=("riot", token),
            verify=False,
            timeout=5,
        )
        try:
            data = response.json()
        except Exception:
            data = response.text
        return response.status_code, data
    except Exception as e:
        return -1, str(e)


def _load_champion_names():
    """
    从 DDragon 加载英雄 ID → 中文名映射。
    优先使用中文(zh_CN)，失败则用英文。
    """
    global _champion_names, _champion_id_to_cn

    if _champion_names:
        return  # 已加载

    try:
        # 获取最新版本
        versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        resp = requests.get(versions_url, timeout=10)
        latest_version = resp.json()[0]

        # 获取中文英雄数据
        champ_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/zh_CN/champion.json"
        resp = requests.get(champ_url, timeout=10)
        data = resp.json()["data"]

        for champ_key, champ_info in data.items():
            champ_id = int(champ_info["key"])
            champ_name = champ_info["name"]  # 中文名
            _champion_names[champ_id] = champ_name
            # 缓存英文ID到中文名的映射 (例如 'Tristana' -> '麦林炮手')
            _champion_id_to_cn[champ_key] = champ_name


        print(f"[LCU] 已加载 {len(_champion_names)} 个英雄名称 (版本 {latest_version})")

    except Exception as e:
        print(f"[LCU] 加载英雄名称失败: {e}")



def get_champion_name(champion_id: int) -> str:
    """获取英雄中文名。"""
    _load_champion_names()
    return _champion_names.get(champion_id, f"未知英雄(ID:{champion_id})")


# ==================== 英雄选择信息 ====================

def get_champ_select_info() -> dict | None:
    """
    获取当前英雄选择阶段的信息。

    Returns:
        dict 包含:
        - my_team: list[str] - 我方英雄名称列表
        - their_team: list[str] - 对方英雄名称列表
        - phase: str - 当前阶段
        或 None（客户端未运行/不在英雄选择阶段）
    """
    conn = _get_connection()
    if not conn:
        print("[LCU] 未找到 LoL 客户端")
        return None
    port, token = conn
    print(f"[LCU] 连接到客户端 (端口: {port})")

    # 获取英雄选择数据
    session = _lcu_request(port, token, "/lol-champ-select/v1/session")
    if not session:
        print("[LCU] 当前不在英雄选择阶段")
        return None

    # 加载英雄名称
    _load_champion_names()

    # 解析队伍信息
    result = {
        "my_team": [],
        "their_team": [],
        "my_champion": None,
        "phase": session.get("timer", {}).get("phase", "UNKNOWN"),
    }

    local_cell_id = session.get("localPlayerCellId", -1)

    my_team = session.get("myTeam", [])
    for player in my_team:
        champ_id = player.get("championId", 0)
        if champ_id > 0:
            name = get_champion_name(champ_id)
            result["my_team"].append(name)
            if player.get("cellId") == local_cell_id:
                result["my_champion"] = name

    their_team = session.get("theirTeam", [])
    for player in their_team:
        champ_id = player.get("championId", 0)
        if champ_id > 0:
            name = get_champion_name(champ_id)
            result["their_team"].append(name)

    print(f"[LCU] 🎯 我的英雄: {result['my_champion']}")
    print(f"[LCU] 我方: {result['my_team']}")
    print(f"[LCU] 对方: {result['their_team']}")
    print(f"[LCU] 阶段: {result['phase']}")

    return result


def get_lcu_context() -> str | None:
    """
    获取 LCU 数据并格式化为可以附加到 Gemini Prompt 的上下文字符串。
    如果 LCU 不可用，返回 None。
    """
    info = get_champ_select_info()
    if not info:
        return None

    parts = []
    if info["my_champion"]:
        parts.append(f"⭐【我选择的英雄】: {info['my_champion']}（请重点分析这个英雄的出装、符文和打法）")
    if info["my_team"]:
        parts.append(f"【LCU 数据 - 我方英雄】: {', '.join(info['my_team'])}")
    if info["their_team"]:
        parts.append(f"【LCU 数据 - 对方英雄】: {', '.join(info['their_team'])}")

    if parts:
        return "\n".join(parts) + "\n（以上为客户端 API 直接读取的数据，请结合截图进行分析）"
    return None


# ==================== Live Client Data (剧中实时数据) ====================

def get_live_game_data() -> dict | None:
    """
    从 Live Client Data API (端口 2999) 获取实时游戏数据。
    该接口在游戏进行中（InProgress）可用，无需 LCU Token。
    """
    url = "https://127.0.0.1:2999/liveclientdata/allgamedata"
    try:
        # 使用 verify=False 因为 2999 端口也是自签名证书
        response = requests.get(url, verify=False, timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def get_perk_metadata() -> dict[int, str]:
    """获取所有符文/海克斯的名字映射表。"""
    global _perk_metadata
    if _perk_metadata:
        return _perk_metadata

    conn = _get_connection()
    if not conn:
        return {}
    port, token = conn
    
    # 获取所有的符文数据
    perks = _lcu_request(port, token, "/lol-perks/v1/perks")
    if perks and isinstance(perks, list):
        for p in perks:
            pid = p.get("id")
            name = p.get("name")
            if pid and name:
                _perk_metadata[pid] = name
        print(f"[LCU] 已加载 {len(_perk_metadata)} 个符文/海克斯元数据")
    return _perk_metadata


def get_live_player_status() -> str | None:
    """获取游戏中玩家的实时装备、金币和已选海克斯信息。"""
    data = get_live_game_data()
    if not data:
        return None

    active_player = data.get("activePlayer", {})
    all_players = data.get("allPlayers", [])
    
    # 找到当前玩家
    summoner_name = active_player.get("summonerName")
    me = next((p for p in all_players if p.get("summonerName") == summoner_name), None)
    
    if not me:
        return None

    champ_name_en = me.get("championName")
    _load_champion_names()
    cn_name = _champion_id_to_cn.get(champ_name_en, champ_name_en)

    items = [i.get("displayName") for i in me.get("items", [])]
    gold = active_player.get("currentGold", 0)

    # 获取已选的符文 (包含海克斯)
    perk_md = get_perk_metadata()
    actual_runes = []
    
    def flatten_perks(p_obj):
        ids = []
        if isinstance(p_obj, dict):
            for v in p_obj.values():
                if isinstance(v, (int, float)):
                    ids.append(int(v))
                elif isinstance(v, dict):
                    ids.extend(flatten_perks(v))
        elif isinstance(p_obj, list):
            for item in p_obj:
                ids.extend(flatten_perks(item))
        return ids

    all_perk_ids = flatten_perks(me.get("runes", {}))
    for pid in all_perk_ids:
        pname = perk_md.get(pid)
        if pname:
            actual_runes.append(pname)
    
    # 去重
    actual_runes = list(set(actual_runes))

    status = [
        f"🚀【实时对局状态 - 绝对真实数据】",
        f"- 我的英雄: {cn_name}",
        f"- 当前金币: {int(gold)}",
        f"- 已购装备: {', '.join(items) if items else '无'}",
        f"- 探测到的已选海克斯/符文: {', '.join(actual_runes) if actual_runes else '未探测到'}"
    ]
    
    return "\n".join(status)


def get_live_team_rosters() -> dict | None:
    """
    基于 Live Client Data API (无须截屏) 获取当局所有玩家的阵容信息。
    只能在游戏 InProgress 时获取到。
    
    Returns:
        dict 包含:
        - my_team: list[str] (队友英雄名含自己)
        - their_team: list[str] (敌人英雄名)
        - my_champion: str (当前玩家锁定英雄名)
        - live_context: str (组装好的上下文文本片段)
    """
    data = get_live_game_data()
    if not data:
        return None
        
    all_players = data.get("allPlayers", [])
    if not all_players or len(all_players) < 2:
        # 如果获取不到玩家，或者人数不对（比如练习模式可能只有1个，但安全起见）
        return None
        
    active_player = data.get("activePlayer", {})
    summoner_name = active_player.get("summonerName")
    
    _load_champion_names()
    
    my_team = []
    their_team = []
    my_champion = ""
    
    # 获取我的队伍属性 (通常是 'ORDER' 或 'CHAOS')
    my_team_str = ""
    for p in all_players:
        if p.get("summonerName") == summoner_name:
            my_team_str = p.get("team")
            my_champ_en = p.get("championName")
            my_champion = _champion_id_to_cn.get(my_champ_en, my_champ_en)
            break
            
    if not my_team_str: # 如果连自己队伍都找不到
        return None
        
    for p in all_players:
        champ_en = p.get("championName")
        cn_name = _champion_id_to_cn.get(champ_en, champ_en)
        if p.get("team") == my_team_str:
            my_team.append(cn_name)
        else:
            their_team.append(cn_name)
            
    context = [
        f"⭐【我选择的英雄】: {my_champion}（请重点分析我的出装、海克斯和打法）",
        f"【自动捕获: 我方阵容】: {', '.join(my_team)}",
        f"【自动捕获: 敌方阵容】: {', '.join(their_team)}",
    ]
    
    # 注入实时状态 (含实际海克斯)
    live_status = get_live_player_status()
    if live_status:
        context.append(live_status)
        
    context.append("（以上阵容与状态数据已由客户端完全捕获。敌方阵容无视野区已点亮，请直接以该名单进行终极推演）")
    
    return {
        "my_team": my_team,
        "their_team": their_team,
        "my_champion": my_champion,
        "live_context": "\n".join(context)
    }

def get_loading_screen_rosters(override_my_champion: str = None) -> dict | None:
    """
    通过 LCU 的 GameFlow 接口在加载界面（非游戏内）提前获取 10 人阵容。
    这是恢复极速自动分析的关键，不依赖于延迟启动的 2999 端口 API。
    """
    conn = _get_connection()
    if not conn:
        return None
    port, token = conn
    
    session = _lcu_request(port, token, "/lol-gameflow/v1/session")
    if not session:
        return None
        
    game_data = session.get("gameData", {})
    team_one = game_data.get("teamOne", [])
    team_two = game_data.get("teamTwo", [])
    
    if not team_one and not team_two:
        return None
        
    _load_champion_names()
    
    # 查找本地玩家 (通过 LCU 获取本地召唤师信息)
    local_summoner = _lcu_request(port, token, "/lol-summoner/v1/current-summoner")
    local_name = local_summoner.get("displayName", "") if local_summoner else ""
    local_puuid = local_summoner.get("puuid", "") if local_summoner else ""
    
    my_team_players = []
    their_team_players = []
    my_champion = "未知英雄"
    
    # 判断我们在哪个队伍
    my_team_is_one = False
    for p in team_one:
        # 必须确保有值，否则空字符串会错误匹配
        if (local_name and p.get("summonerName") == local_name) or (local_puuid and p.get("puuid") == local_puuid):
            my_team_is_one = True
            break
            
    my_team_data = team_one if my_team_is_one else team_two
    their_team_data = team_two if my_team_is_one else team_one
    
    for p in my_team_data:
        champ_id = p.get("championId", 0)
        cname = get_champion_name(champ_id)
        my_team_players.append(cname)
        if (local_name and p.get("summonerName") == local_name) or (local_puuid and p.get("puuid") == local_puuid):
            my_champion = cname
            
    for p in their_team_data:
        cname = get_champion_name(p.get("championId", 0))
        their_team_players.append(cname)
        
    # 优先级逻辑：如果传入了 override_my_champion（手动纠错），则绝对以手动为准（无条件覆盖 LCU 数据）
    if override_my_champion:
        if my_champion != "未知英雄" and my_champion != override_my_champion:
            log.info(f"[LCU] 🚨 手动纠错强行覆盖 LCU 识别: {my_champion} -> {override_my_champion}")
        my_champion = override_my_champion
        
    context = [
        f"⭐【我选择的英雄】: {my_champion}（请重点分析我的出装、海克斯和打法）",
        f"【自动捕获: 我方阵容】: {', '.join(my_team_players)}",
        f"【自动捕获: 敌方阵容】: {', '.join(their_team_players)}",
        "（以上阵容已由客户端在加载界面瞬间捕获。敌方阵容无视野区已点亮，请直接以该名单进行终极推演）"
    ]
    
    return {
        "my_team": my_team_players,
        "their_team": their_team_players,
        "my_champion": my_champion,
        "live_context": "\n".join(context)
    }

def get_full_board_state() -> str | None:
    """
    获取全局 10 名玩家的完整状态（英雄、装备、已选海克斯）。
    专供游戏内（如 Lv7 以后）截屏分析时注入真实背景上下文，替代 AI 对局势的盲目猜测。
    """
    data = get_live_game_data()
    if not data:
        return None

    all_players = data.get("allPlayers", [])
    if not all_players:
        return None

    active_player = data.get("activePlayer", {})
    summoner_name = active_player.get("summonerName")
    
    _load_champion_names()
    perk_md = get_perk_metadata()
    
    # 辅助函数：拍平从 Live Client Data 获取的 runes IDs
    def flatten_perks(p_obj):
        ids = []
        if isinstance(p_obj, dict):
            for v in p_obj.values():
                if isinstance(v, (int, float)):
                    ids.append(int(v))
                elif isinstance(v, dict):
                    ids.extend(flatten_perks(v))
        elif isinstance(p_obj, list):
            for item in p_obj:
                ids.extend(flatten_perks(item))
        return ids

    # 先找到我的队伍名
    my_team_str = ""
    for p in all_players:
        if p.get("summonerName") == summoner_name:
            my_team_str = p.get("team")
            break

    if not my_team_str:
        return None

    my_team_lines = []
    enemy_team_lines = []
    my_champ_cn = ""

    for p in all_players:
        is_me = p.get("summonerName") == summoner_name
        is_my_team = p.get("team") == my_team_str
        
        champ_en = p.get("championName")
        cn_name = _champion_id_to_cn.get(champ_en, champ_en)
        
        if is_me:
            my_champ_cn = cn_name
            cn_name = f"⭐【我】{cn_name}"
            
        items = [i.get("displayName") for i in p.get("items", [])]
        item_str = ", ".join(items) if items else "无装备"
        
        actual_runes = []
        all_perk_ids = flatten_perks(p.get("runes", {}))
        for pid in all_perk_ids:
            pname = perk_md.get(pid)
            if pname:
                actual_runes.append(pname)
        actual_runes = list(set(actual_runes))
        rune_str = ", ".join(actual_runes) if actual_runes else "无"
        
        line = f"  - {cn_name} | 装备: [{item_str}] | 已选海克斯/符文: [{rune_str}]"
        
        if is_my_team:
            my_team_lines.append(line)
        else:
            enemy_team_lines.append(line)

    status = [
        f"📊【全场 10 人实时状态透视 (基于防Gank雷达扫描绝对真实数据)】",
        "=== 我方阵营 ===",
        *my_team_lines,
        "=== 敌方阵营 ===",
        *enemy_team_lines,
        f"\n⚠️核心指令：这是游戏进行中的分析！请注意场上所有人的出装和海克斯动向。我是 {my_champ_cn}，请根据这些真实数据为我提供下一步的选择建议。"
    ]
    
    return "\n".join(status)


# ==================== 游戏阶段与等级监控 ====================


def get_gameflow_phase() -> str | None:
    """
    获取当前游戏阶段。

    Returns:
        阶段名称字符串（如 "ChampSelect", "InProgress" 等），或 None
    """
    conn = _get_connection()
    if not conn:
        return None
    port, token = conn

    url = f"https://127.0.0.1:{port}/lol-gameflow/v1/gameflow-phase"
    try:
        resp = requests.get(url, auth=("riot", token), verify=False, timeout=2)
        if resp.status_code == 200:
            return str(resp.json()).strip('"')
    except Exception:
        pass
    return None


def get_player_level() -> int | None:
    """从 Live Client Data API 获取当前玩家等级（游戏中可用）。"""
    data = get_live_game_data()
    if not data:
        return None
    return data.get("activePlayer", {}).get("level")


def get_player_augment_count() -> int:
    """
    获取当前玩家已选的海克斯符文数量。
    通过 Live Client Data API 的 runes 字段来检测。
    返回已选海克斯数量（基础符文之外的额外符文）。
    """
    data = get_live_game_data()
    if not data:
        return 0
    
    all_players = data.get("allPlayers", [])
    active_player = data.get("activePlayer", {})
    summoner_name = active_player.get("summonerName")
    
    me = next((p for p in all_players if p.get("summonerName") == summoner_name), None)
    if not me:
        return 0
    
    # runes 里的 generalRunes 通常包含基础符文 + 海克斯增强
    # 基础符文数量通常为 6-9 个，海克斯符文在游戏中会额外出现
    runes_data = me.get("runes", {})
    general_runes = runes_data.get("generalRunes", [])
    
    # 海克斯符文的 perkId 一般 > 100000 (区分基础符文)
    augment_count = sum(1 for r in general_runes if r.get("id", 0) > 100000)
    return augment_count


def get_bench_info() -> dict | None:
    """[DEPRECATED] 获取替补席信息（已废弃，保留空壳避免外部引用报错）"""
    return None


if __name__ == "__main__":
    print("=" * 50)
    print("🔍 LCU API 测试")
    print("=" * 50)

    info = get_champ_select_info()
    if info:
        print(f"\n🎯 我的英雄: {info['my_champion']}")
        print(f"我方英雄: {info['my_team']}")
        print(f"对方英雄: {info['their_team']}")
        print(f"阶段: {info['phase']}")
    else:
        print("\n❌ 无法连接到 LoL 客户端或不在英雄选择阶段")
