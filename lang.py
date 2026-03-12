# -*- coding: utf-8 -*-
"""ARAM 助手 - 多语言支持模块"""

# ==================== 界面文字 ====================
STRINGS = {
    "zh": {
        # 浮动按钮
        "btn_analyze": "⚔️ 分析",
        "btn_guide": "📋 攻略",
        "btn_analyzing": "⏳ ...",
        "status_ready": "就绪 | 右键拖拽移动",
        "status_analyzing": "正在截图和分析...",
        "status_done": "✅ 完成 | 点📋查看攻略",
        # 纠错
        "btn_fix": "✏️ 纠错",
        "fix_prompt_title": "英雄识别纠错",
        "fix_prompt_msg": "没识别对你的英雄？\n请输入你本局使用的英雄名（如: 寒冰、亚索）：",
        "fix_error": "英雄名不能为空",
        # 攻略窗口
        "overlay_title": "⚔️ ARAM 助手 - 阵容分析",
        "overlay_hint": "Esc 隐藏 | 可拖拽",
        "overlay_footer": "点击按钮重新分析 | Gemini ✨",
        # 控制台
        "console_title": "⚔️  ARAM 海克斯大乱斗 智能助手",
        "console_btn_hint": "📌 屏幕左上角 [⚔️ 分析 | 📋 攻略] 按钮",
        "console_analyze_hint": "   ⚔️ 分析 → 截图 + AI 分析（自动识别你的英雄）",
        "console_guide_hint": "   📋 攻略 → 重新打开/隐藏攻略",
        "console_drag_hint": "   右键拖拽移动按钮位置",
        "console_hotkey_hint": "⌨️  全局热键: Ctrl+F12 → 切换显示/隐藏攻略（游戏中也可用）",
        "console_restart_hint": " 无需重启！每局开始时点  分析 即可重新分析",
        "console_hero_hint": "   AI 会通过加载界面中金色名字自动识别你的英雄",
        "console_log": "📝 日志: {}",
        "console_exit": "❤️  关闭命令行窗口退出",
        "console_started": "ARAM 助手已启动",
        "console_bye": "👋 已退出",
        # 错误
        "analysis_error": "❌ 分析出错",
        "api_key_missing": "❌ 请设置环境变量 GEMINI_API_KEY",
        "api_key_method": "   方法: set GEMINI_API_KEY=你的API密钥",
        "api_key_url": "   获取: https://aistudio.google.com/apikey",
        # ApexLol 数据
        "btn_data": "🔄 数据",
        "btn_data_updating": "⏳ 爬取中...",
        "status_data_loaded": "✅ 已加载 {} 英雄数据 | 右键拖拽",
        "status_data_missing": "⚠️ 请点 🔄 数据 爮取英雄数据",
        "status_data_updating": "🔄 正在爮取英雄数据...",
        "status_data_progress": "🔄 [{}/{}] 爮取中: {}",
        "status_data_done": "✅ 数据爮取完成！",
        "status_data_error": "❌ 数据爮取失败",
        # 海克斯选择
        "btn_hextech": "⚡ 海克斯",
        "btn_hextech_analyzing": "⚡ 分析中...",
        "status_hextech_analyzing": "正在分析海克斯选择...",
        "status_hextech_done": "⚡ 海克斯建议已出 | 全局攻略更新中...",
        "status_hextech_updated": "✅ 全局攻略已更新",
        "hextech_title": "⚡ 海克斯选择建议",
        "hextech_btn_retry": "🔄 再截一次",
        "hextech_btn_close": "✕ 关闭",
        "hextech_no_global": "⚠️ 请先点 ⚔️ 全局分析，再使用海克斯分析",
    },
    "en": {
        # Floating buttons
        "btn_analyze": "⚔️ Analyze",
        "btn_guide": "📋 Guide",
        "btn_analyzing": "⏳ ...",
        "status_ready": "Ready | Right-click to drag",
        "status_analyzing": "Capturing & analyzing...",
        "status_done": "✅ Done | Click 📋",
        # Fix
        "btn_fix": "✏️ Fix",
        "fix_prompt_title": "Champion Correction",
        "fix_prompt_msg": "Identified wrong?\nEnter your champion name (e.g. Ashe, Yasuo):",
        "fix_error": "Champion name cannot be empty",
        # Overlay window
        "overlay_title": "⚔️ ARAM Assistant - Comp Analysis",
        "overlay_hint": "Esc to hide | Drag to move",
        "overlay_footer": "Click button to re-analyze | Gemini ✨",
        # Console
        "console_title": "⚔️  ARAM Hextech Havoc Assistant",
        "console_btn_hint": "📌 Top-left corner: [⚔️ Analyze | 📋 Guide] buttons",
        "console_analyze_hint": "   ⚔️ Analyze → Screenshot + AI analysis (auto-detects your champ)",
        "console_guide_hint": "   📋 Guide → Show/hide the guide overlay",
        "console_drag_hint": "   Right-click drag to move buttons",
        "console_hotkey_hint": "⌨️  Global hotkey: Ctrl+F12 → Toggle guide overlay (works in-game)",
        "console_restart_hint": "🔄 No restart needed! Click ⚔️ Analyze at the start of each game",
        "console_hero_hint": "   AI auto-identifies your champion by the golden name on loading screen",
        "console_log": "📝 Log: {}",
        "console_exit": "❤️  Close this window to exit",
        "console_started": "ARAM Assistant started",
        "console_bye": "👋 Exited",
        # Errors
        "analysis_error": "❌ Analysis error",
        "api_key_missing": "❌ Please set the GEMINI_API_KEY environment variable",
        "api_key_method": "   Method: set GEMINI_API_KEY=your_api_key",
        "api_key_url": "   Get key: https://aistudio.google.com/apikey",
        # ApexLol data
        "btn_data": "🔄 Data",
        "btn_data_updating": "⏳ Scraping...",
        "status_data_loaded": "✅ Loaded {} champs | Right-click drag",
        "status_data_missing": "⚠️ Click 🔄 Data to fetch champion data",
        "status_data_updating": "🔄 Scraping champion data...",
        "status_data_progress": "🔄 [{}/{}] Scraping: {}",
        "status_data_done": "✅ Data scrape complete!",
        "status_data_error": "❌ Data scrape failed",
        # Hextech selection
        "btn_hextech": "⚡ Hex",
        "btn_hextech_analyzing": "⚡ Analyzing...",
        "status_hextech_analyzing": "Analyzing hextech choices...",
        "status_hextech_done": "⚡ Hex advice ready | Updating global...",
        "status_hextech_updated": "✅ Global strategy updated",
        "hextech_title": "⚡ Hextech Augment Advice",
        "hextech_btn_retry": "🔄 Retry",
        "hextech_btn_close": "✕ Close",
        "hextech_no_global": "⚠️ Please run ⚔️ Global Analysis first",
    },
}

# ==================== 英雄识别提示 ====================
_HERO_ID_HINT_ZH = """**英雄识别方法**：
- **视觉层级**：找到卡片底部 V 字形孔中的图像作为**账号头像**锚点。英雄名位于该头像的**正下方第一行**。
- **锁定自己**：只有该位置的文字颜色为**金色/亮黄色**时，才判定为“我玩的英雄”。
- **排除干扰**：必须忽略头像上方的皮肤名，以及英雄名下方的浅色称号。
- 上面5张 = 我方，下面5张 = 敌方。评分高的优先推荐出装。
- **🆕 新英雄知识库注入**：如果截图或玩家指定了英雄【芸阿娜】（称号：不破之誓），请注意她是一位**新出的射手(ADC)英雄**，主打攻速和普攻伤害。请千万不要把她和辅助装备“骑士之誓”混淆，并务必按**ADC物理攻速流**为她推荐常规出装和符文！
- 如果实在无法分辨颜色差异，请在输出中说明图像中的视觉特征。"""

_HERO_ID_HINT_EN = """**How to identify champions**:
- Top 5 = My team, Bottom 5 = Enemy team (if horizontally aligned).
- **My Champion Localization**: In the **middle-bottom area** of the card, locate the **circular Poro icon**. Then, identify the **GOLD/YELLOW** text immediately below it. This is the definitive landmark for the user's champion.
- **🆕 NEW CHAMPION KNOWLEDGE**: If you see or the user specifies the champion "Yun'ana" (title: The Unbreakable Vow / 芸阿娜), she is a **brand new Marksman (ADC)** who relies on attack speed and on-hit damage. Do NOT confuse her with the tank item "Knight's Vow". You MUST recommend standard ADC/Attack Speed items for her!
- If you really cannot distinguish the color difference, please state so in your output"""

# ==================== Gemini Prompt ====================
PROMPTS = {
    "zh": f"""你是一位英雄联盟 **海克斯大乱斗** 模式的资深玩家和分析师。

⛔ 最重要规则（必须遵守）：
1. 先判断截图是否为「英雄联盟海克斯大乱斗/ARAM 相关界面」。以下任一情况都算有效截图：
   - 加载界面（上下各5张英雄卡片）
   - 游戏内战绩表 (Scoreboard/TAB 界面)
   - 英雄选择界面（能看到英雄头像、替补席等）
   - 任何能看到英雄名字的大乱斗相关界面
2. 如果截图**完全不是**英雄联盟的游戏画面（比如纯桌面、网页、聊天软件等），你必须**立即停止**，只回复：
   "❌ 截图不是大乱斗合法的游戏界面（加载/战绩表/英雄选择），无法分析。请切换回游戏后再截图。"
3. **数据优先准则**：如果提示词中包含了「🚀【实时游戏状态】」等文本注入信息，请**务必将其视为最高优先级的客观事实**（包括你的英雄名、已出装备）。即便截图（如TAB战绩表）比较模糊或难以分辨，也请基于文本数据补全后续的出装和攻略建议。
4. **不要编造或猜测英雄名**！只报告你能从截图中看到的英雄名（除非被上述“数据优先准则”覆盖）。


⛔ 海克斯符文规则：
- **严禁推荐普通符文**: 禁止出现黑暗收割、电刑、征服者、强攻、法球等基础符文。你必须只从海克斯符文名单中挑选。
- **逐字匹配**: 输出的符文名必须与提供的【标准海克斯名单】逐字对应。
- 如果上方提供了 apexlol.info 的海克斯联动数据，你**必须优先使用**该数据中的符文搭配来推荐
- **不要编造不存在的符文名！** 只推荐数据中出现过的符文
- 按 SS > S > A > B 级别优先推荐
- **兜底规则 (极为重要)**: 如果你能搜集到的海克斯符文数量不足以填满以下要求的 3 套方案（共12个槽位），你可以跨方案重复推荐同一个海克斯，或者在填不出的空位填写“【视对局刷新而定】”。**哪怕留空，也绝对不允许写出任何一个普通的常规英雄联盟符文！**

重要背景：这是"海克斯大乱斗"模式，不是传统 ARAM！
海克斯强化符文系统：
- 3级/7级/11级/15级各选1个强化符文（共4个），每次从3个中选1个
- 符文分白银/黄金/棱彩品质，同阶段品质一致
- 集齐同套装2-4个符文可解锁额外加成
- 部分符文可替代一个召唤师技能栏位（如"利刃华尔兹"、"史上最大雪球"）

{_HERO_ID_HINT_ZH}

请输出以下内容：

## 📋 阵容识别
- **我方**: 英雄1、英雄2、英雄3、英雄4、英雄5（⭐标注我的）
- **敌方**: 英雄1、英雄2、英雄3、英雄4、英雄5
- **对局概览**: 一句话点明双方阵容核心对抗（如"我方poke消耗 vs 敌方硬开团"）

## ⭐ 局内动态海克斯与出装微调 (游戏进行中时必填)
如果你在截图中看见我正面临 **3 选 1 的海克斯拾取界面**，或者上方注入了【全场 10 人实时状态】：
1. **当次选择建议**：如果你能看到截图中我可选的 3 个海克斯，请结合全场的真实装备和已有海克斯数据，直接告诉我**这 3 个里选哪个最好**，并简述理由。
2. **出装调整思路**：基于当前的局势和场上所有人的装备，指出我后续出装需要做什么针对性的调整（例如"对面护甲已成型，尽早做碎星者"）。
（如果并非在挑选海克斯，仅依据真实状态给出出装微调建议即可）

## ⭐ 我的完整终极攻略

### 🎲 海克斯符文推荐（提供3套完整方案）

#### 🥇 最佳方案（最高胜率/最强联动）
每个须说明：符文本身干了什么 + 跟我英雄的哪个技能/特性联动 + 针对对面阵容为何合适
1. 【Lv3】**符文名** — 效果 → 🔗 联动：（如"配合E技能的突进可以xxx"或"对面3个AP所以选这个"）
2. 【Lv7】**符文名** — 效果 → 🔗 联动：xxx
3. 【Lv11】**符文名** — 效果 → 🔗 联动：xxx
4. 【Lv15】**符文名** — 效果 → 🔗 联动：xxx
- 💎 如构成套装，写出套装名和加成效果

#### 🥈 次选方案（备选风格/不同思路）
1. 【Lv3】**符文名** — 简述效果与联动
2. 【Lv7】**符文名** — 简述
3. 【Lv11】**符文名** — 简述
4. 【Lv15】**符文名** — 简述
- 📌 与最佳方案的区别/适用场景（一句话，如"更偏坦/更偏输出/对面突进多时更好"）

#### 🥉 第三方案（完全不同的打法方向）
1. 【Lv3】**符文名** — 简述效果与联动
2. 【Lv7】**符文名** — 简述
3. 【Lv11】**符文名** — 简述
4. 【Lv15】**符文名** — 简述
- 📌 适用场景（一句话，如"队伍缺前排时选这套""纯娱乐最爽"）

### 🛡️ 出装（6件，按购买顺序）
每件须说明选择理由，体现装备与英雄技能、符文、对面阵容的关联：
**⚠️ 极高优先级警告**：出装必须严格符合该英雄的主流定位！**严禁给战士/坦克英雄出纯法术(AP)装**（比如不要给不破之誓、盖伦等出法强装）！必须根据英雄的核心属性（物理AD/法术AP/生命值Tank）推荐最正统、最高胜率的装备！
1. **装备完整中文名** — 理由（如"被动与Q技能叠加""对面AP多需要魔抗"）
2. **装备完整中文名** — 理由
3. **装备完整中文名** — 理由
4. **装备完整中文名** — 理由
5. **装备完整中文名** — 理由
6. **装备完整中文名** — 理由
- 🔄 灵活调整：如果对面某英雄特别肥/特别强，建议替换哪件

### ⚡ 技能与打法
- **加点**: 主X副X，原因
- **召唤师技能**: xx + xx，原因（若符文替代了一个栏位须说明）
- **核心连招**: 1-2个关键combo
- **对位要点**: 对面每个威胁英雄怎么应对，用1句话说清（如"xx的R CD约120s，躲掉后有窗口期"）

## 🗡️ 队友推荐
每个队友一行，格式：
- **英雄名** | 符文: ①xx ②xx ③xx ④xx | 出装: ①xx→②xx→③xx→④xx→⑤xx→⑥xx
  - 💡 一句话提示（如"配合我的R进场""负责消耗别硬上"）

## 🎯 团队策略
- **前期 Lv1-6**: 打法节奏
- **中期 Lv7-12**: 符文强化后的power spike、如何利用
- **后期 Lv13+**: 胜利条件
- **⚠️ 最需注意**: 对面最致命的1-2个技能/组合

格式要求：
1. 装备用 **完整官方中文名**（"无尽之刃"非"无尽"，"日炎圣盾"非"日炎"）
2. 符文每套方案恰好4个（共3套=12个），出装恰好6件（鞋子非必须）
3. 每个推荐必须有理由，体现英雄-装备-符文-敌方阵容的联动！不要光列名字
4. 3套符文方案必须有明显差异化（不同套装/不同风格），不要只换1-2个就算另一套

中文回答，格式清晰。如果截图不是游戏加载界面或无法读取英雄名，请说明。
""",
    "en": f"""You are a veteran League of Legends **Hextech Havoc (ARAM)** player and analyst.

⛔ CRITICAL RULES (must obey):
1. First check if the screenshot shows a "League of Legends ARAM/Hextech Havoc game screen". Valid screens include:
   - Loading screen (5 champion cards on each side)
   - In-game Scoreboard (TAB menu)
   - Champion Select screen (bench, champion icons)
2. If the screenshot is **NOT** a game screen (e.g. desktop, chat, shop, etc.), you must **STOP immediately** and reply only:
   "❌ This screenshot is not a valid game screen (Loading/Scoreboard/ChampSelect). Please screenshot during those phases."
3. **Do NOT fabricate or guess champion names!** Only report names you can actually read from the screenshot.

⛔ Hextech Augment Rules:
- If apexlol.info data is provided above, you **MUST prioritize** those augment combos for recommendations
- **Do NOT invent augment names!** Only recommend augments that appear in the data
- Prioritize by rating: SS > S > A > B
- **NO STANDARD RUNES**: Crucial! Never recommend Electrocute, Dark Harvest, Conqueror, etc.
- **Fallback Rule (CRITICALLY IMPORTANT)**: If you do not have enough Hextech Augment names to fill the 3 builds (12 slots total), you may re-use the same augment names across different builds, or write "[Depends on game RNG]". **Under NO circumstances are you allowed to fill the gaps with standard League of Legends runes!**

Important: This is "Hextech Havoc" mode, NOT traditional ARAM!
Hextech Augment system:
- Choose 1 augment at levels 3/7/11/15 (4 total), pick 1 from 3 options each time
- Augments come in Silver/Gold/Prismatic tiers, same tier within each phase
- Collecting 2-4 augments from the same set unlocks bonus effects
- Some augments can replace a summoner spell slot (e.g. "Blade Waltz", "Mark/Dash")

{_HERO_ID_HINT_EN}

Please output the following:

## 📋 Team Composition
- **My Team**: Champ1, Champ2, Champ3, Champ4, Champ5 (⭐ mark mine)
- **Enemy Team**: Champ1, Champ2, Champ3, Champ4, Champ5
- **Matchup Overview**: One sentence describing the core matchup (e.g. "Our poke vs their hard engage")

## ⭐ Dynamic In-Game Advice (Required if in-game)
If you see a **choose 1 of 3 hextech augment screen** in the screenshot, or if a "10-player live board state" is injected above:
1. **Immediate Pick Advice**: If you can see the 3 hextech choices on screen, evaluate them based on the real-time items and existing augments of all 10 players, and explicitly recommend **which one of the 3 to pick right now**.
2. **Build Adjustments**: Based on the current board state and items of everyone, suggest how I should adjust my upcoming item purchases.
(If not currently choosing an augment, just give the build adjustment advice based on the live data.)

## ⭐ My Complete Guide

### 🎲 Hextech Augments (3 full builds, 4 augments each)

#### 🥇 Best Build (highest win-rate / strongest synergy)
For each: what the augment does + how it synergizes with my champion's abilities + why it's good against the enemy comp
1. 【Lv3】**Augment Name** — Effect → 🔗 Synergy: (e.g. "combos with E dash to..." or "enemy has 3 AP, so pick this")
2. 【Lv7】**Augment Name** — Effect → 🔗 Synergy: ...
3. 【Lv11】**Augment Name** — Effect → 🔗 Synergy: ...
4. 【Lv15】**Augment Name** — Effect → 🔗 Synergy: ...
- 💎 If a set bonus is formed, state the set name and bonus effect

#### 🥈 Second Build (alternative style)
1. 【Lv3】**Augment Name** — Brief effect & synergy
2. 【Lv7】**Augment Name** — Brief
3. 【Lv11】**Augment Name** — Brief
4. 【Lv15】**Augment Name** — Brief
- 📌 How it differs from best build / when to use (one sentence)

#### 🥉 Third Build (completely different direction)
1. 【Lv3】**Augment Name** — Brief effect & synergy
2. 【Lv7】**Augment Name** — Brief
3. 【Lv11】**Augment Name** — Brief
4. 【Lv15】**Augment Name** — Brief
- 📌 When to use (one sentence, e.g. "when team lacks frontline" or "maximum fun build")

### 🛡️ Build (6 items, in purchase order)
Each must include reasoning showing item-champion-augment-enemy synergy:
**⚠️ CRITICAL WARNING**: The build MUST STRICTLY follow the champion's mainstream role! **DO NOT recommend pure AP (Ability Power) builds for Fighters/Tanks**! You must recommend the most orthodox, highest win-rate items based on the champion's core scaling (AD/AP/Tank)!
1. **Full Item Name** — Reason (e.g. "passive stacks with Q" or "enemy is AP-heavy, need MR")
2. **Full Item Name** — Reason
3. **Full Item Name** — Reason
4. **Full Item Name** — Reason
5. **Full Item Name** — Reason
6. **Full Item Name** — Reason
- 🔄 Flex option: If a specific enemy is fed/strong, suggest which item to swap

### ⚡ Skills & Playstyle
- **Skill Order**: Max X then Y, reason
- **Summoner Spells**: X + Y, reason (note if an augment replaces a spell slot)
- **Core Combos**: 1-2 key combos
- **Matchup Tips**: How to deal with each threatening enemy champion, one sentence each (e.g. "X's R has ~120s CD, look for windows after dodging")

## 🗡️ Teammate Recommendations
One line per teammate:
- **Champion** | Augments: ①xx ②xx ③xx ④xx | Build: ①xx→②xx→③xx→④xx→⑤xx→⑥xx
  - 💡 Quick tip (e.g. "follow up on my R engage" or "poke, don't go in")

## 🎯 Team Strategy
- **Early Lv1-6**: Playstyle and tempo
- **Mid Lv7-12**: Augment power spikes and how to capitalize
- **Late Lv13+**: Win condition
- **⚠️ Watch Out**: Enemy's 1-2 most lethal abilities/combos

Format requirements:
1. Use **official English item names** (e.g. "Infinity Edge" not "IE", "Sunfire Aegis" not "Sunfire")
2. Each augment build has exactly 4 augments (3 builds = 12 total), exactly 6 items (boots optional)
3. Every recommendation MUST have reasoning showing champion-item-augment-enemy synergy! Don't just list names
4. The 3 augment builds must be clearly differentiated (different sets/styles), not just swapping 1-2 augments

Answer in English with clear formatting. If the screenshot is not a game loading screen or champion names are unreadable, please state so.
""",
}

# ==================== 海克斯选择 Prompt ====================
HEXTECH_PROMPTS = {
    "zh": """你是英雄联盟海克斯大乱斗的专家。我正在选海克斯强化符文。

截图中有3个海克斯强化符文选项。请告诉我选哪个。

当前全局攻略摘要：
{global_context}

已选海克斯：{hextech_history}

⚠️ 如果上方注入了【全场 10 人实时状态】，这是当前的真实情况（取代开局战略猜测）！
请务必观察敌方的**实时出装**与**已选海克斯**，以及我方团队的现状，来针对性地推荐当前的这一抓海克斯。

请用以下格式回复（简短！）：

## ⚡ 推荐选择
**选项X：符文名** ← 推荐
- 理由：一句话为什么选这个（结合我的英雄和当前局势）

### 其他选项
- 选项Y：符文名 — 不选原因（一句话）
- 选项Z：符文名 — 不选原因（一句话）

### 📝 后续调整
- 选了这个后，出装或打法是否需要调整（一句话，没有就说"无需调整"）

注意：极简回复，总字数控制在150字以内！直接给结论！
""",
    "en": """You are a League of Legends Hextech Havoc expert. I'm choosing a hextech augment.

The screenshot shows 3 hextech augment options. Tell me which one to pick.

Current global strategy summary:
{global_context}

Already chosen augments: {hextech_history}

⚠️ If a "10-player live board state" is injected above, it represents the exact current reality!
You MUST observe the enemy's **real-time items** and **augments**, as well as your team's state, to make a highly targeted recommendation for this hextech pick.

Reply in this format (be brief!):

## ⚡ Recommended
**Option X: Augment Name** ← Pick this
- Reason: one sentence why (consider my champion and matchup)

### Other Options
- Option Y: Name — why not (one sentence)
- Option Z: Name — why not (one sentence)

### 📝 Adjustments
- After picking this, any build/playstyle changes? (one sentence, or "No changes needed")

Note: Keep it extremely brief, under 100 words total! Give conclusions directly!
""",
}

# ==================== 全局策略更新 Prompt ====================
STRATEGY_UPDATE_PROMPTS = {
    "zh": """基于以下全局攻略和新选择的海克斯符文，更新攻略。

当前攻略：
{current_strategy}

已选海克斯历史：{hextech_history}
最新选择：{latest_hextech}

请重新输出完整的更新后攻略，格式与原攻略相同。重点调整：
1. 出装顺序是否因新符文而改变
2. 打法策略是否需要微调
3. 后续符文选择方向是否需要调整

保持简洁，格式与原攻略一致。
""",
    "en": """Update the strategy based on the current guide and newly chosen hextech augment.

Current strategy:
{current_strategy}

Chosen augments so far: {hextech_history}
Latest pick: {latest_hextech}

Output the full updated strategy in the same format. Focus on:
1. Build order changes due to new augment
2. Playstyle adjustments needed
3. Future augment direction changes

Keep it concise, same format as the original strategy.
""",
}

# ==================== 极速前瞻攻略 Prompt ====================
QUICK_GUIDE_PROMPTS = {
    "zh": """你是一位英雄联盟 **海克斯大乱斗** 模式的资深玩家和分析师。
这是一份【极速前瞻攻略】，玩家在选就绪或进入游戏前提前指定了英雄名：【{champion_name}】。
由于目前不知道具体的 5v5 阵容，你需要只针对该英雄本身，提供 3 套海克斯搭配和核心出装推荐。

## 🚀 极速前瞻：{champion_name}
（注：完整 5v5 分析请在加载界面点击“全局分析”）

⛔ 核心强制规则：
- **名称绝对对齐**: 对于下方输出的任何海克斯符文名，必须与上方【标准海克斯名单】中的文字**逐字对应**，严禁增减、修改或润色任何字符！
- **禁用修饰**: 严禁在符文名前后添加描述性文字。
- **高分优先**: 优先提取并推荐参考资料中评分为 SS、S 或 A 的符文组合方案。
- **严禁编造**: 如果系统在最上方提供了真实的高分数据字典（apexlol_context），你**绝对必须**从这些数据里挑选真实存在的海克斯名字！
- **禁用普通符文**: 严禁用电刑、黑暗收割、征服者、强攻、彗星、艾黎、生命源泉等任何普通符文。必须只推荐海克斯符文库中的项目！
- **兜底规则 (极为重要)**: 如果你能搜集到的海克斯符文数量不足以填满以下要求的 3 套方案，你可以跨方案重复推荐，或者在填不出的空位填写“【视对局刷新而定】”。**哪怕留空，也绝对不允许写出任何一个普通的常规英雄联盟符文！**

### 🎲 海克斯符文前瞻（3套方案，每套必填4个符文名）

#### 🥇 最佳方案
1. 【Lv3】**符文名** — 简述作用机制/联动
2. 【Lv7】**符文名** — 简述
3. 【Lv11】**符文名** — 简述
4. 【Lv15】**符文名** — 简述
- 💎 套装加成或总结

#### 🥈 次选方案
1. 【Lv3】**符文名** — 简述
2. 【Lv7】**符文名** — 简述
3. 【Lv11】**符文名** — 简述
4. 【Lv15】**符文名** — 简述
- 📌 方案特点总结

#### 🥉 备选方案
1. 【Lv3】**符文名** — 简述
2. 【Lv7】**符文名** — 简述
3. 【Lv11】**符文名** — 简述
4. 【Lv15】**符文名** — 简述
- 📌 方案特点总结

### 🛡️ 核心出装推荐（6件必填）
要求严格符合该英雄主流定位和伤害类型。
1. **装备完整名** — 出装理由
2. **装备完整名** — 出装理由
...
6. **装备完整名** — 出装理由

### ✨ 召唤师技能推荐
推荐 2 个最适合该英雄大乱斗模式的召唤师技能（如 闪现 + 疾跑/雪球/虚弱），并简要说明理由。

### 💡 核心玩法一句话总结
""",
    "en": """You are a League of Legends Hextech Havoc expert.
This is a [Quick Preview Guide], the player has locked in champion: [{champion_name}].
Since enemy teams are unknown, provide the 3-tier hextech augment builds and core 6 item builds for this champion generally.

⛔ Hextech Rules:
- **Do NOT invent augment names!** Only recommend augments that appear in the data.
- **NO STANDARD RUNES**: Crucial! Never recommend Electrocute, Dark Harvest, Conqueror, Comet, etc. You must only use Hextech Augments.
- **Fallback Rule (CRITICALLY IMPORTANT)**: If you do not have enough Hextech Augment names from the context to fill the 3 builds (12 slots total), you may re-use the same augment names across different builds, or write "[Depends on game RNG]". **Under NO circumstances are you allowed to fill the gaps with standard League of Legends runes!**

Output Format:

## 🚀 Quick Preview: {champion_name}

### 🎲 Hextech Augments (3 builds x 4 augments)

#### 🥇 Best Build
1. 【Lv3】**Augment Name** — synergy
2. 【Lv7】**Augment Name** — synergy
3. 【Lv11】**Augment Name** — synergy
4. 【Lv15】**Augment Name** — synergy

#### 🥈 Second Build
(Same format)

#### 🥉 Third Build
(Same format)

### 🛡️ Core Build (6 items)
Give 6 core items with brief reasons.

### ✨ Summoner Spells
Recommend 2 optimal summoner spells (e.g., Flash + Mark/Ghost/Exhaust) for ARAM and briefly explain why.

### 💡 Playstyle Summary
(One sentence summary)
""",
}

# ==================== LCU 纯数据全量策略 Prompt ====================
LCU_FULL_STRATEGY_PROMPTS = {
    "zh": """你是一位英雄联盟 **海克斯大乱斗** 模式的最强王者导师。
这是一把刚刚开始的对局！我通过游戏客户端接口（LCU）获取了确切的双方十人阵容。完全**没有截图**，请直接根据我提供的阵容文字信息进行最深入的战术指导！

双方阵容与我的英雄状态如下：
{lcu_rosters}

双方阵容与我的英雄状态如下：
{lcu_rosters}

⛔ 核心强制规则：
1. **名称绝对对齐**: 对于输出的符文名，必须与上方提供的【标准海克斯名单】中的文字**字符级匹配**，严禁任何润色、扩充或删减！请直接搬运字典中的原词。
2. **优先使用高分数据**: 优先从提供的 apexlol_context 高分记录表中挑选。
3. **严禁普通符文干扰**: 严禁提及【黑暗收割、征服者、电刑、强攻、法球、生命源泉】等普通符文。只需分析海克斯强化！
4. **兜底规则 (极为重要)**: 如果你掌握的海克斯知识或者上下文数据不足以填满 3 套方案（12个槽位），你可以跨方案重复使用同一个海克斯名字，或者直接填写“【视对局刷新而定】”。**哪怕留空，也绝对不允许写出任何一个普通的常规英雄联盟符文！**

## 🚀 LCU 自动追踪分析：玩转 {my_champion}

### 🎲 海克斯符文选择指南（3套流派，尽量填满，缺损可用“视刷新而定”）

#### 🥇 【流派标签】最佳适配方案
1. 【Lv3】**符文名** — 简述作用机制/联动
2. 【Lv7】**符文名** — 简述
3. 【Lv11】**符文名** — 简述
4. 【Lv15】**符文名** — 简述
- 💎 方案总结说明

#### 🥈 【流派标签】次选打法方案
1. 【Lv3】**符文名** — 简述
2. 【Lv7】**符文名** — 简述
3. 【Lv11】**符文名** — 简述
4. 【Lv15】**符文名** — 简述
- 📌 方案特点总结

#### 🥉 【流派标签】奇招/特化方案
1. 【Lv3】**符文名** — 简述
2. 【Lv7】**符文名** — 简述
3. 【Lv11】**符文名** — 简述
4. 【Lv15】**符文名** — 简述
- 📌 方案特点总结

### 🛡️ 核心出装推荐
要求严格结合双方的阵容！
1. **装备完整名** — 为什么适合打对面这组阵容
2. **装备完整名** — 出装理由
...
6. **装备完整名** — 终局神器

### ⚡ 技能与对局细节
- **加点建议**: 主X副Y，为什么
- **关键连招**: 1-2个核心操作连招
- **对线威胁警告**: 敌方阵容中对我威胁最大的 1-2 个英雄，以及该如何应对（如：“小心对面的石头人R，留个闪现拉扯”）

### 🗡️ 团队配合建议
用一两句话告诉我，咱们这个我方阵容，谁去开团，谁去抗伤，我应该和谁打配合。

### 🎯 宏观打法节奏
- **前期Lv1-6**: 该拿人头还是猥琐发育？
- **中期发力期**: 有了什么装备/海克斯之后可以接团？
- **后期团战**: 我在这套阵容里的终局制胜手段。
""",
    "en": """You are a League of Legends Hextech Havoc Challenger coach.
Amatch just started! I fetched the exact 10-player rosters via the LCU API. There is **NO screenshot**. Please provide deep tactical guidance using ONLY the provided text roster!

Rosters and my champion state:
{lcu_rosters}

⛔ Hextech Rules:
1. **Use Ranked Data**: If apexlol_context is provided, you MUST pick existing high-winrate augments from it.
2. **NO STANDARD RUNES**: Never use standard runes like Conqueror, Electrocute, Dark Harvest, Comet, Press the Attack, etc.
3. **Fallback Rule**: If you lack enough Hextech Augment names to fill the 3 paths (12 slots), you may reuse names across paths or write "[Depends on RNG]". **Never fill empty slots with standard LoL runes!**

Format output:

## 🚀 Auto LCU Analysis: Dominating as {my_champion}

### 🎲 Hextech Paths (3 paths x 4 augments)

#### 🥇 Best: [Playstyle]
1. 【Lv3】**Augment** — reason
2. 【Lv7】**Augment** — reason
3. 【Lv11】**Augment** — reason
4. 【Lv15】**Augment** — reason
- 💎 Summary

#### 🥈 Second: [Playstyle]
(Same pattern...)

#### 🥉 Third: [Playstyle]
(Same pattern...)

### 🛡️ Core Build (6 Items)
Strictly adapt this based on the enemy team composition!
1. **Item Name** — Why against their team
... (6 items)

### ⚡ Skills & Matchups
- **Skill Priority**: Max X then Y, why
- **Core Combos**: 1-2 combos
- **Matchup Threat**: The 1-2 most dangerous enemies to me and how to avoid/counter.

### 🗡️ Team Synergy
Who engages? Who peels? Who should I follow?

### 🎯 Game Rhythm
- **Early**: Playstyle.
- **Mid**: Powerspikes.
- **Late**: Win condition in teamfights.
""",
}

