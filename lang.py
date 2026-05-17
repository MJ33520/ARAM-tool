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
        "console_btn_hint": "📌 屏幕左上角 [⚡ 海克斯 | 📋 攻略 | ✏️ 纠错 | 🔄 数据] 按钮",
        "console_analyze_hint": "   ⚡ 海克斯 → 截图识别3选1海克斯，给出选择建议",
        "console_guide_hint": "   📋 攻略 → 重新打开/隐藏攻略",
        "console_drag_hint": "      右键拖拽移动按钮位置",
        "console_restart_hint": "🔄 无需重启！每局加载时自动分析阵容并生成攻略",
        "console_hero_hint": "      AI 会通过 LCU 接口自动获取你的英雄，无需截图",
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
        # 设置
        "btn_settings": "⚙️",
        "btn_exit": "✕",
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
        "btn_history": "📜 记录",
        "status_history_empty": "⚠️ 暂无海克斯记录",
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
        "console_drag_hint": "      Right-click drag to move buttons",
        "console_restart_hint": "🔄 No restart needed! Click ⚔️ Analyze at the start of each game",
        "console_hero_hint": "      AI auto-identifies your champion by the golden name on loading screen",
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
        # Settings
        "btn_settings": "⚙️",
        "btn_exit": "✕",
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
        "btn_history": "📜 History",
        "status_history_empty": "⚠️ No hextech history",
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

### 🎲 对局玩法与装备建议（请不要再输出任何海克斯符文推荐内容！只需提供装备、打法和团队策略即可）



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
- **Matchup Tips**: How to deal with each threatening enemy champion, one sentence each

## 🗡️ Teammate Recommendations
One line per teammate:
- **Champion** | Augments: ①xx ②xx ③xx ④xx | Build: ①xx→②xx→③xx→④xx→⑤xx→⑥xx
  - 💡 Quick tip

## 🎯 Team Strategy
- **Early Lv1-6**: Playstyle and tempo
- **Mid Lv7-12**: Augment power spikes and how to capitalize
- **Late Lv13+**: Win condition
- **⚠️ Watch Out**: Enemy's 1-2 most lethal abilities/combos

Format requirements:
1. Use **official English item names**
2. Each augment build has exactly 4 augments (3 builds = 12 total), exactly 6 items
3. Every recommendation MUST have reasoning! Don't just list names
4. The 3 augment builds must be clearly differentiated

Answer in English with clear formatting.
""",
}

# ==================== 海克斯选择 Prompt ====================
HEXTECH_IMAGE_PROMPTS = {
    "zh": """你是英雄联盟海克斯大乱斗的专家。我正在选海克斯强化符文。

截图中有出现的海克斯强化符文选项。请告诉我选哪个。

已选海克斯：{hextech_history}

⚠️ 如果系统在最上方提供了真实的高分数据字典（apexlol.info 数据），你**绝对必须**看准截图里的选项，优先推荐字典里出现过的海克斯！严禁推荐任何普通符文。

请用以下格式回复（简短！）：

## ⚡ 推荐选择
**推荐选择：【符文名】**
- 理由：一句话（结合数据字典中的评分和流派）

### 其他可选的选项
- 【符文名】：不选原因（一句话）
- 【符文名】：不选原因（一句话）

注意：极简回复，只讨论截图里真实可见的选项，绝对不要虚构！
""",
    "en": """You are a League of Legends Hextech Havoc expert. I'm choosing a hextech augment.

The screenshot shows hextech augment options. Tell me which one to pick.

Already chosen augments: {hextech_history}

⚠️ You MUST prioritize the available options shown in the screenshot. Do NOT invent augments!

Reply in this format (be brief!):

## ⚡ Recommended
**Recommend: [Augment Name]**
- Reason: one sentence why

### Other Options
- [Name]: why not (one sentence)
- [Name]: why not (one sentence)

Note: Give conclusions directly! Do not invent options that are not in the screenshot!
""",
}

HEXTECH_TEXT_PROMPTS = {
    "zh": """你是英雄联盟海克斯大乱斗的专家。我正在选海克斯强化符文。

以下是我目前可以**候选提取出来的选项**：
【{options_text}】

已选海克斯：{hextech_history}

⚠️ 绝对核心指令：你**绝对必须**只从上述**候选选项**中挑选！哪怕候选里只有1个或2个选项，你也只能在它们之中选！如果提供的高分参考表里有更好的海克斯，但不在候选选项中，你**绝对不可推荐**！严禁出现候选列表以外的选项（严禁出现其它选项、选项3、选项4等幻觉）！

请用以下格式回复（简短！）：

## ⚡ 推荐选择
**推荐选择：【符文名】**
- 理由：一句话

### 不推荐的选项（如果有）
- 【符文名】：不选原因
- 【符文名】：不选原因

注意：极简回复！只许讨论候选列表里的名字！
""",
    "en": """You are a Hextech Havoc expert. I'm choosing a hextech augment.

Here are the **ONLY candidate options** available:
[{options_text}]

Already chosen augments: {hextech_history}

⚠️ CRITICAL: You MUST ONLY pick from the candidate options listed above! Even if there's only 1 option. Do NOT recommend anything outside this list! No hallucinations!

Reply in this format (brief!):

## ⚡ Recommended
**Recommend: [Augment Name]**
- Reason: one sentence why

### Not Recommended
- [Name]: why not

Note: ONLY discuss the candidate options!
""",
}

# ==================== 全局策略更新 Prompt ====================
STRATEGY_UPDATE_PROMPTS = {
    "zh": """你是海克斯大乱斗攻略更新助手。根据玩家最新选择的海克斯符文，输出一段**简短的更新补充**（不超过 200 字），而非完整攻略。

当前攻略（仅供参考，不要重复输出）：
{current_strategy}

已选海克斯历史：{hextech_history}
最新选择：{latest_hextech}

【你的任务】
只输出以下格式的**更新章节**，不要重复原攻略内容：

### 📊 Lv{latest_hextech}后攻略更新
- **已选海克斯评价**: 这个符文选得好/一般，原因是…
- **出装调整**: 是否需要因为新符文而调整出装顺序
- **下一个海克斯方向**: 接下来应该优先选什么类型的符文
- **打法微调**: 一句话说明打法变化（如有）
""",
    "en": """Update the strategy based on the newly chosen hextech augment.

Current strategy:
{current_strategy}

Chosen augments so far: {hextech_history}
Latest pick: {latest_hextech}

Output a brief update section only. Focus on:
1. Build order changes due to new augment
2. Playstyle adjustments needed
3. Future augment direction changes
""",
}

# ==================== 极速前瞻攻略 Prompt ====================
QUICK_GUIDE_PROMPTS = {
    "zh": """你是一位英雄联盟 **海克斯大乱斗（ARAM）** 模式的资深攻略分析师。
⚠️ 重要：这是 **大乱斗模式**，只有一条路（嚎哭深渊），**没有野区、没有打野、没有对线分路、没有回城购物（只能死后购物）**！所有建议必须100%针对大乱斗！

这是关于英雄【{champion_name}】的极速前瞻攻略。

### 🎲 海克斯符文流派（以供参考）
{prefilled_augments}
*(如果上方显示"无数据"，你也不需要推荐海克斯，只需提供出装和打法即可)*

【你的任务】
直接输出以下模块，不要输出任何寒暄，**绝对不要输出海克斯符文推荐**：

### 🛒🛡️ 按海克斯方案分别给出装（仅前3套非陷阱方案）
查看上方海克斯数据中排名前3的非陷阱方案：
- 如果已给出"搭配出装"，以它为基础**补齐到完整6件终局出装**
- 如果没给出装数据，你来结合该符文组合特性**生成完整出装**
- 排名第4及以后的不需要补充出装

#### 🥇 方案1（写出海克斯组合名）
- **完整出装**: ①→②→③→④→⑤→⑥
- 💡 出装思路（一句话）

#### 🥈 方案2（写出海克斯组合名）
- **完整出装**: ①→②→③→④→⑤→⑥
- 💡 出装思路（一句话）

#### 🥉 方案3（写出海克斯组合名）
- **完整出装**: ①→②→③→④→⑤→⑥
- 💡 出装思路（一句话）

### ⚡ 技能加点与召唤师技能
- **加点建议**: 主X副Y，简解原因。
- **召唤师技能**: 推荐 2 个最适合**大乱斗**的技能，简说理由。

### 💡 大乱斗核心打法
一句话总结该英雄在大乱斗中的定位和关键操作。
""",
    "en": """You are a League of Legends Hextech Havoc expert analyst.
Quick preview for champion: [{champion_name}].

[Context]
{prefilled_augments}

[Your Task]
Do NOT output hextech augments. For top 3 non-trap combos, provide full 6-item builds:

#### 🥇 Build 1 (combo name)
- **Full build**: ①→②→③→④→⑤→⑥

#### 🥈 Build 2 (combo name)
- **Full build**: ①→②→③→④→⑤→⑥

#### 🥉 Build 3 (combo name)
- **Full build**: ①→②→③→④→⑤→⑥

### ⚡ Skills & Summoner Spells
- **Skill Priority**: Max X then Y, why.
- **Summoner Spells**: 2 optimal for ARAM.

### 💡 Playstyle Summary
(One sentence)
""",
}




# ==================== 极速前瞻攻略 Prompt ====================
QUICK_GUIDE_PROMPTS = {
    "zh": """你是一位英雄联盟 **海克斯大乱斗（ARAM）** 模式的资深攻略分析师。
⚠️ 重要：这是 **大乱斗模式**，只有一条路（嚎哭深渊），**没有野区、没有打野、没有对线分路、没有回城购物（只能死后购物）**！所有建议必须100%针对大乱斗！

这是关于英雄【{champion_name}】的极速前瞻攻略。

### 🎲 海克斯符文流派（以供参考）
{prefilled_augments}
*(如果上方显示“无数据”，你也不需要推荐海克斯，只需提供出装和打法即可)*

【你的任务】
直接输出以下模块，不要输出任何寒暄，**绝对不要输出海克斯符文推荐**：

### 🛡️ 大乱斗核心出装（6件）
严格符合该英雄主流定位（AD出AD装，AP出AP装，坦克出肉装），且必须适配大乱斗节奏（没有回城，注意续航和团战能力）。
1. **装备完整名** — 出装理由
...
6. **装备完整名** — 出装理由

### ⚡ 技能加点与召唤师技能
- **加点建议**: 主X副Y，简解原因。
- **召唤师技能**: 推荐 2 个最适合**大乱斗**的技能（可选：闪现/雪球/疾跑/虚弱/净化/屏障/治疗/引燃），简说理由。

### 💡 大乱斗核心打法
一句话总结该英雄在大乱斗中的定位和关键操作。
""",
    "en": """You are a League of Legends Hextech Havoc expert analyst.
This is a quick preview for champion: [{champion_name}].

[Context]
The following hextech augment builds are popular for this champion. **Use this as context for your item and playstyle recommendations**:
{prefilled_augments}

[Your Task]
Output ONLY the following 3 sections. **Do NOT output hextech augments** (the system handles that):

### 🛡️ Core Build (6 items)
Give 6 core items with brief reasons matching the champion's role and the augments above.

### ⚡ Skills & Summoner Spells
- **Skill Priority**: Max X then Y, why.
- **Summoner Spells**: Recommend 2 optimal spells for ARAM and briefly explain why.

### 💡 Playstyle Summary
(One sentence summary)
""",
}

# ==================== LCU 纯数据全量策略 Prompt ====================
LCU_FULL_STRATEGY_PROMPTS = {
    "zh": """你是一位英雄联盟 **海克斯大乱斗（ARAM）** 模式的最强王者导师。
⚠️ 重要：这是 **大乱斗模式**，只有一条路（嚎哭深渊），**没有野区、没有打野、没有对线分路、没有回城购物（只能死后购物）**！所有建议必须100%针对大乱斗！

这是一把刚刚开始的对局！我通过游戏客户端接口（LCU）获取了确切的双方十人阵容。

【局势情报】
双方阵容与我的英雄状态如下：
{lcu_rosters}

### 🎲 海克斯符文推荐
{prefilled_augments}
*(如果上方提示“无数据”，请基于你的知识为该英雄推荐 3 套最强海克斯符文方案，确保适配大乱斗节奏)*

【你的任务】
直接输出以下模块，不要输出任何寒暄：

### 🧠 阵容针对性解析
1. **敌方阵容画像**: 一句话概括敌方阵容特点（前排多/脆皮多/AP为主/AD为主/控制链强等）
2. **符文流派推荐**: 如果上方能提取到 ApexLol 方案，请将其按本局适配度重新排序；若上方提示“无数据”，你必须凭借知识在这里输出 3 套适合该英雄的大乱斗海克斯方案！
3. **出装调整方向**: 基于选定的最优符文流派，出装思路需要做哪些针对性调整（例如：敌方3坦→加破甲，敌方高爆发→补护盾/生命）

### 🛒 出门装建议
根据上方阵容分析结果，推荐开局第一次购买的 2-3 件装备（总金额不超过 3400 金币），注明出装理由。

### 🛡️ 大乱斗核心出装（6件）
**实战数据参考（来源 arammayhem.com）**：
{prefilled_builds}
（如上方提示"无数据"，凭借知识自行推荐；否则**优先采用胜率/登场率 Top1-2 的方案**作为核心，然后基于本局阵容做 1-2 件针对性调整，**而不是从头猜出装**）

严格按照上方阵容分析和符文流派给出针对性出装！注意大乱斗没有回城，需要考虑续航。
1. **装备完整名** — 针对敌方阵容/搭配符文的出装理由
...
6. **装备完整名** — 终局神器

### ⚡ 技能与细节
- **加点建议**: 主X副Y，为什么
- **召唤师技能**: 推荐 2 个最适合本局大乱斗的召唤师技能（可选：闪现/雪球/疾跑/虚弱/治疗/屏障/净化/引燃，**没有传送**）
- **最大威胁**: 敌方阵容中对我威胁最大的 1-2 个英雄，以及该如何应对

### 🗡️ 团队配合建议
用一两句话告诉我，咱们这个我方阵容，谁去开团，谁去抗伤，我应该和谁打配合。

### 🎯 大乱斗打法节奏
- **前期Lv1-6**: 该抢血还是猥琐？
- **中期发力期**: 有了什么核心装备/海克斯之后可以起飞？
- **后期团战**: 我在这套阵容里的终局制胜手段。
""",
    "en": """You are a League of Legends Hextech Havoc Challenger coach.
A match just started! I fetched the exact 10-player rosters via the LCU API.

[Match Context]
Rosters and my champion state:
{lcu_rosters}

[Data Guide]
The following are the highest win-rate Hextech augment builds for this champion. **Use them as your core reference for the build and playstyle**:
{prefilled_augments}

[Your Task]
Output ONLY the following sections. **Do NOT output any hextech augment recommendations** (the system handles it automatically).

### 🛡️ Core Build (6 Items)
**Real-match data reference (source: arammayhem.com)**:
{prefilled_builds}
(If "no data" above, recommend based on champion knowledge; otherwise **prioritize the Top1-2 builds by pickrate/winrate** as your core, then adapt 1-2 items to the current matchup — **don't guess from scratch**.)

Strictly adapt this based on the enemy team composition and the provided Data Guide!
1. **Item Name** — Why against their team / synergy with augments
... (6 items)

### ⚡ Skills & Matchups
- **Skill Priority**: Max X then Y, why
- **Summoner Spells**: Best 2 spells for this match, why
- **Matchup Threat**: The 1-2 most dangerous enemies to me and how to counter.

### 🗡️ Team Synergy
Who engages? Who peels? Who should I follow?

### 🎯 Game Rhythm
- **Early**: Playstyle.
- **Mid**: Powerspikes.
- **Late**: Win condition in teamfights.
""",
}

