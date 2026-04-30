# -*- coding: utf-8 -*-
"""
ARAM 智能助手 - 主入口

单一 tkinter Root 架构：
- TriggerButton: 主 Tk() root，浮动按钮栏（全局分析 | 海克斯 | 攻略 | 数据）
- Global Overlay: Toplevel 窗口，全局攻略显示（常驻）
- Hextech Overlay: Toplevel 窗口，海克斯选择建议（临时，可多次截图刷新）
所有 UI 操作都在主线程中执行，Gemini 分析在后台线程运行。
"""

import os
import sys
import io

# 打包版（--noconsole）启动时无控制台；按 settings.json 的 show_console 值
# 决定要不要 AllocConsole。必须在其它 import 之前做，让启动期日志能输出。
from console_utils import bootstrap_from_settings
bootstrap_from_settings()

# Force utf-8 for stdout and stderr to prevent ascii encoding errors on Windows
if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'encoding') and sys.stderr.encoding and sys.stderr.encoding.lower() not in ('utf-8', 'utf8'):
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import time as _time
import threading
import traceback
import logging
import ctypes
import ctypes.wintypes
import tkinter as tk

# ==================== 日志配置 ====================
# 日志放在用户主目录的 .aram_tool/，打包版（onefile）的临时目录退出会被清，
# 必须用持久化目录才能事后查日志
LOG_DIR = os.path.join(os.path.expanduser("~"), ".aram_tool")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "aram_debug.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8", mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("ARAM")

from screenshot import capture_hextech_cards
from gemini_analyzer import analyze_hextech_choice
from config import (
    OVERLAY_BG_COLOR, OVERLAY_FG_COLOR, OVERLAY_ACCENT_COLOR,
    OVERLAY_TITLE_COLOR, OVERLAY_WIDTH, OVERLAY_MAX_HEIGHT,
    OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE, OVERLAY_OPACITY, T,
    APEXLOL_ENABLED, APEXLOL_CACHE_DIR, APEXLOL_CACHE_TTL_DAYS,
    SHOW_CONSOLE,
)
from console_utils import set_console_visible

# 状态
_is_analyzing = False
_is_hextech_analyzing = False
_global_strategy = None       # 全局攻略文本（缓存）
_hextech_history = []          # 已选海克斯列表


class App:
    """主应用：单一 tk.Tk() root，管理所有窗口。"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ARAM")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)
        self.root.overrideredirect(True)
        self.root.geometry("+10+10")

        # ===== 浮动按钮面板 =====
        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(fill=tk.X)

        # ⚡ 海克斯
        self.btn_hextech = tk.Button(
            btn_frame, text=T("btn_hextech"), command=self._on_hextech,
            bg="#1a1a2e", fg="#ff6b6b", activebackground="#2a2a4e",
            activeforeground="#ffffff", font=("Microsoft YaHei UI", 11, "bold"),
            padx=8, pady=4, cursor="hand2", relief=tk.FLAT, borderwidth=0,
        )
        self.btn_hextech.pack(side=tk.LEFT, padx=(1, 1))

        sep2 = tk.Label(btn_frame, text="|", bg="#1a1a2e", fg="#333355",
                        font=("Microsoft YaHei UI", 11))
        sep2.pack(side=tk.LEFT)

        # 📋 攻略
        self.btn_show = tk.Button(
            btn_frame, text=T("btn_guide"), command=self._on_show,
            bg="#1a1a2e", fg="#00d4ff", activebackground="#2a2a4e",
            activeforeground="#ffffff", font=("Microsoft YaHei UI", 11, "bold"),
            padx=8, pady=4, cursor="hand2", relief=tk.FLAT, borderwidth=0,
        )
        self.btn_show.pack(side=tk.LEFT, padx=(1, 1))

        # ✏️ 纠错/手动指定英雄
        self.btn_fix = tk.Button(
            btn_frame, text=T("btn_fix"), command=self._on_fix,
            bg="#1a1a2e", fg="#ffaa00", activebackground="#2a2a4e",
            activeforeground="#ffffff", font=("Microsoft YaHei UI", 11, "bold"),
            padx=8, pady=4, cursor="hand2", relief=tk.FLAT, borderwidth=0,
        )
        self.btn_fix.pack(side=tk.LEFT, padx=(1, 1))

        sep_fix = tk.Label(btn_frame, text="|", bg="#1a1a2e", fg="#333355",
                        font=("Microsoft YaHei UI", 11))
        sep_fix.pack(side=tk.LEFT)

        # 🔄 数据（ApexLol）
        if APEXLOL_ENABLED:
            sep3 = tk.Label(btn_frame, text="|", bg="#1a1a2e", fg="#333355",
                            font=("Microsoft YaHei UI", 11))
            sep3.pack(side=tk.LEFT)

            self.btn_data = tk.Button(
                btn_frame, text=T("btn_data"), command=self._on_update_data,
                bg="#1a1a2e", fg="#66ff66", activebackground="#2a2a4e",
                activeforeground="#ffffff", font=("Microsoft YaHei UI", 11, "bold"),
                padx=8, pady=4, cursor="hand2", relief=tk.FLAT, borderwidth=0,
            )
            self.btn_data.pack(side=tk.LEFT, padx=(1, 2))

        # ⚙️ 设置
        sep_set = tk.Label(btn_frame, text="|", bg="#1a1a2e", fg="#333355",
                           font=("Microsoft YaHei UI", 11))
        sep_set.pack(side=tk.LEFT)
        self.btn_settings = tk.Button(
            btn_frame, text=T("btn_settings"), command=self._on_settings,
            bg="#1a1a2e", fg="#aaaacc", activebackground="#2a2a4e",
            activeforeground="#ffffff", font=("Microsoft YaHei UI", 11, "bold"),
            padx=6, pady=4, cursor="hand2", relief=tk.FLAT, borderwidth=0,
        )
        self.btn_settings.pack(side=tk.LEFT, padx=(1, 2))

        # ✕ 退出
        sep_exit = tk.Label(btn_frame, text="|", bg="#1a1a2e", fg="#333355",
                            font=("Microsoft YaHei UI", 11))
        sep_exit.pack(side=tk.LEFT)
        self.btn_exit = tk.Button(
            btn_frame, text=T("btn_exit"), command=self._on_exit,
            bg="#1a1a2e", fg="#ff5577", activebackground="#442233",
            activeforeground="#ffffff", font=("Microsoft YaHei UI", 11, "bold"),
            padx=6, pady=4, cursor="hand2", relief=tk.FLAT, borderwidth=0,
        )
        self.btn_exit.pack(side=tk.LEFT, padx=(1, 2))

        self.status_label = tk.Label(
            self.root, text=T("status_ready"),
            bg="#1a1a2e", fg="#666680", font=("Microsoft YaHei UI", 8),
        )
        self.status_label.pack()

        self.root.configure(bg="#00d4ff", highlightthickness=1,
                            highlightbackground="#00d4ff")

        # 拖拽
        self._drag_data = {"x": 0, "y": 0}
        drag_widgets = [self.btn_hextech, self.btn_show, self.btn_fix,
                        sep2, sep_fix, sep_set, self.btn_settings,
                        sep_exit, self.btn_exit,
                        self.status_label, btn_frame]
        if APEXLOL_ENABLED:
            drag_widgets.extend([sep3, self.btn_data])
        for w in drag_widgets:
            w.bind("<Button-3>", self._start_drag)
            w.bind("<B3-Motion>", self._on_drag)

        # ===== 全局攻略 Toplevel 窗口 =====
        self.overlay = None       # 全局攻略 Toplevel
        self.overlay_text = None
        self._overlay_visible = False

        # ===== 海克斯临时 Toplevel 窗口 =====
        self.hextech_overlay = None
        self.hextech_text = None
        self._hextech_visible = False

        # 保持置顶
        self._keep_topmost()

        # ===== 状态与缓存 =====
        self._locked_champion: str = None # 记录手动锁定的英雄名

        # 启动时加载 ApexLol 缓存
        if APEXLOL_ENABLED:
            self._init_apexlol_cache()

        # 启动命令行输入监听线程
        t_input = threading.Thread(target=self._console_input_listener, daemon=True, name="ConsoleInput")
        t_input.start()

        # 启动 LCU 自动对局监控线程
        t_lcu = threading.Thread(target=self._lcu_live_monitor, daemon=True, name="LCUMonitor")
        t_lcu.start()

    def _lcu_live_monitor(self):
        """后台轮询 LCU API，在加载界面即自动触发分析。"""
        global _is_analyzing, _is_hextech_analyzing, _global_strategy, _hextech_history
        _match_analyzed_flag = False
        from lcu_client import get_loading_screen_rosters, get_gameflow_phase
        import time

        
        while True:
            try:
                phase = get_gameflow_phase()
                
                # 在加载界面 (InProgress 或 GameStart) 进行秒级前瞻分析
                # 兼容 WeGame 无畏契约/极速模式：在此模式下客户端可能会在 GameStart 后立即变成 None，以节省内存
                if phase in ("InProgress", "GameStart"):
                    if not _match_analyzed_flag and not _is_analyzing and not _is_hextech_analyzing:
                        # 先不传 override，让 LCU 返回真实英雄
                        rosters = get_loading_screen_rosters()
                        if rosters:
                            lcu_champ = rosters.get("my_champion")
                            # 如果用户之前手动输入过英雄，但 LCU 检测到的不一致，说明换了英雄
                            if self._locked_champion and lcu_champ and lcu_champ != "未知英雄":
                                if self._locked_champion != lcu_champ:
                                    log.info(f"[LCU] 🔄 检测到换人: 手动输入={self._locked_champion} → LCU实际={lcu_champ}，以实际为准")
                                    self._locked_champion = lcu_champ
                                # 用最终确认的英雄名覆盖 rosters
                                rosters = get_loading_screen_rosters(override_my_champion=self._locked_champion)
                            elif self._locked_champion:
                                # LCU 没检测到英雄（未知），保留手动输入
                                rosters = get_loading_screen_rosters(override_my_champion=self._locked_champion)
                            log.info("🚀 发现新对局加载中！LCU 自动捕获 10 人阵容，正在无感生成攻略...")
                            _match_analyzed_flag = True
                            # 在主线程中触发纯文本全量分析
                            self.root.after(0, lambda r=rosters: self._run_lcu_auto_analysis(r))
                        else:
                            log.warning("⚠️ LCU phase 为 InProgress，但获取不到有效阵容信息 (get_loading_screen_rosters 返回 None)")
                    

                    
                else:
                    # 如果不是在游戏中，则重置标记，准备迎接下一局
                    if _match_analyzed_flag:
                        log.info(f"🏁 阶段变更为 {phase}，重置攻略状态。")
                        _match_analyzed_flag = False
                        _hextech_history = []
                        _global_strategy = ""
                        self._locked_champion = None
                        # 在主线程更新界面状态标签
                        self.root.after(0, lambda: self.status_label.configure(text=T("status_idle")))
            except Exception as e:
                import traceback
                log.error(f"[Monitor] LCU Monitor 异常: {e}\n{traceback.format_exc()}")
            time.sleep(3)

    def _run_lcu_auto_analysis(self, rosters: dict, is_correction: bool = False):
        """执行 LCU 纯文本全量分析（无截图界面）"""
        global _is_analyzing, _global_strategy, _hextech_history
        if _is_analyzing:
            return
        
        _is_analyzing = True
        self._detected_champion = rosters.get("my_champion") # 记录当前对局识别到的英雄
        self.status_label.configure(text=T("status_lcu_analyzing"))
        
        # 弹窗提示
        self._on_show()
        if self.overlay_text:
            self.overlay_text.configure(state=tk.NORMAL)
            self.overlay_text.delete(1.0, tk.END)
            self.overlay_text.insert(tk.END, f"🚀 正在基于客户端全量数据极速生成终极阵容攻略，请稍候...")
            self.overlay_text.configure(state=tk.DISABLED)
            
        def _bg_task():
            global _is_analyzing, _global_strategy, _hextech_history
            try:
                from gemini_analyzer import analyze_lcu_rosters
                result = analyze_lcu_rosters(rosters, _hextech_history)
                
                _global_strategy = result
                
                # 在主线程中更新显示
                self.root.after(0, lambda: self._show_global_result(result))
            except Exception as e:
                log.error(f"LCU 分析出错: {e}")
                self.root.after(0, lambda: self._show_global_result(f"❌ LCU 分析出错:\n{e}"))
            finally:
                _is_analyzing = False
                self.root.after(0, lambda: self.status_label.configure(text=T("status_done")))
                
        t = threading.Thread(target=_bg_task, daemon=True)
        t.start()


    def _console_input_listener(self):
        """后台监听命令行输入，支持开局前手动指定英雄。"""
        print("\n" + "="*50)
        print("◆ 终端手动输入已启用！\n   您可以直接在此窗口打字输入英雄名并回车，将立刻为您分析！")
        print("="*50 + "\n")
        
        while True:
            try:
                import sys
                line = sys.stdin.readline()
                if not line:
                    _time.sleep(1)
                    continue
                
                cmd = line.strip()
                if not cmd:
                    continue
                
                # 检查是否正在分析
                if _is_analyzing or _is_hextech_analyzing:
                    print(f"[{_time.strftime('%H:%M:%S')}] ⚠️ 当前已有分析任务在进行中，请稍后再试。")
                    continue
                
                print(f"[{_time.strftime('%H:%M:%S')}] 🔒 英雄已锁定: {cmd}。正在为您生成【极速前瞻攻略】...")
                
                # 记录锁定的英雄
                self._locked_champion = cmd
                
                # 在主线程中触发纯文本极速分析
                self.root.after(0, lambda c=cmd: self._run_quick_guide(c))
                
            except Exception as e:
                log.error(f"命令行输入监听异常: {e}")
                _time.sleep(1)

    def _run_quick_guide(self, champion_name: str):
        """执行极速前瞻分析（无截图界面）"""
        global _is_analyzing, _global_strategy
        if _is_analyzing:
            return
        
        _is_analyzing = True
        self.status_label.configure(text=T("status_quick_analyzing"))
        
        # 弹窗显示前瞻正在进行
        self._on_show()
        if self.overlay_text:
            self.overlay_text.configure(state=tk.NORMAL)
            self.overlay_text.delete(1.0, tk.END)
            self.overlay_text.insert(tk.END, f"🚀 正在为您极速生成【{champion_name}】的前瞻攻略，请稍候...")
            self.overlay_text.configure(state=tk.DISABLED)
            
        def _bg_task():
            global _is_analyzing, _global_strategy, _hextech_history
            try:
                from gemini_analyzer import analyze_champion_quick_guide
                result = analyze_champion_quick_guide(champion_name)
                
                # 将该攻略存入全局变量，方便用户在进入游戏前随时查看
                _global_strategy = result
                _hextech_history = []
                
                # 在主线程中更新显示
                self.root.after(0, lambda: self._show_global_result(result))
            except Exception as e:
                log.error(f"极速分析出错: {e}")
                self.root.after(0, lambda: self._show_global_result(f"❌ 分析出错:\n{e}"))
            finally:
                _is_analyzing = False
                self.root.after(0, self._restore_ui_state)
                
        t = threading.Thread(target=_bg_task, daemon=True)
        t.start()

    def _run_pure_data_guide(self, champion_name: str):
        """纯 ApexLol 数据查表模式（无需 AI 也无需 LCU），直接展示海克斯方案。"""
        global _is_analyzing
        _is_analyzing = True
        self.status_label.configure(text="📊 纯数据模式查表中...")

        def _bg_task():
            try:
                from apexlol_data import extract_top_synergies, resolve_champion_id
                # 先尝试解析英雄别名
                resolved = resolve_champion_id(champion_name)
                lookup_name = resolved if resolved else champion_name

                result = extract_top_synergies(lookup_name)
                if result:
                    header = f"## 📊 纯数据模式（无 AI）\n**英雄**: {champion_name}"
                    if resolved:
                        header += f" → {resolved}"
                    header += "\n\n> 以下数据来自 ApexLol 缓存，无需 AI 即可使用\n\n---\n\n"
                    content = header + result
                else:
                    content = f"❌ 在 ApexLol 缓存中未找到 [{champion_name}] 的数据。\n\n请确认英雄名称是否正确，或点击 🔄 数据 按钮更新 ApexLol 缓存。"

                self.root.after(0, lambda: self._show_global_result(content))
                log.info(f"[纯数据] {champion_name} 查表完成")
            except Exception as e:
                log.error(f"纯数据查表失败: {e}")
                self.root.after(0, lambda: self._show_global_result(f"❌ 纯数据查表失败:\n{e}"))
            finally:
                _is_analyzing = False
                self.root.after(0, self._restore_ui_state)

        t = threading.Thread(target=_bg_task, daemon=True)
        t.start()

    def _on_fix(self):
        """手动指定英雄：3级降级策略 — LCU全局 → AI极速前瞻 → 纯数据查表"""
        global _is_analyzing
        if _is_analyzing:
            return
        import tkinter.simpledialog as sd
        self.root.lift()
        self.root.attributes("-topmost", True)
        name = sd.askstring(T("fix_prompt_title"), T("fix_prompt_msg"), parent=self.root)
        if name and name.strip():
            cmd = name.strip()
            log.info(f"用户手动指定英雄: {cmd}")
            self._locked_champion = cmd
            
            # ===== 第1级：尝试 LCU + AI 全局攻略 =====
            try:
                from lcu_client import get_live_team_rosters, get_loading_screen_rosters
                rosters = get_live_team_rosters(override_my_champion=cmd) or get_loading_screen_rosters(override_my_champion=cmd)
                if rosters:
                    log.info("[指定英雄] 路径A: LCU + AI 全局攻略")
                    self._run_lcu_auto_analysis(rosters, is_correction=True)
                    return
            except Exception as e:
                log.warning(f"[指定英雄] LCU 不可用: {e}")
            
            # ===== 第2级：尝试 AI 极速前瞻（无需 LCU） =====
            try:
                from config import LLM_ENABLED
                if LLM_ENABLED:
                    log.info("[指定英雄] 路径B: AI 极速前瞻（无 LCU 阵容）")
                    self._run_quick_guide(cmd)
                    return
            except Exception:
                pass
            
            # ===== 第3级：纯 ApexLol 数据查表（无需 AI 也无需 LCU） =====
            log.info("[指定英雄] 路径C: 纯 ApexLol 数据查表（无 AI 模式）")
            self._run_pure_data_guide(cmd)
                
        elif name is not None:
            from tkinter import messagebox
            messagebox.showwarning("⚠️", T("fix_error"), parent=self.root)



    # ==================== 海克斯分析 ====================
    def _on_hextech(self):
        global _is_hextech_analyzing, _global_strategy
        if _is_hextech_analyzing:
            return

        # 需要先有全局攻略
        if _global_strategy is None:
            self.status_label.configure(text=T("hextech_no_global"))
            return

        _is_hextech_analyzing = True

        self.btn_hextech.configure(text=T("btn_hextech_analyzing"), state=tk.DISABLED)
        self.status_label.configure(text=T("status_hextech_analyzing"))
        self.root.update()

        # 隐藏UI避免截图中出现
        self.root.withdraw()
        if self.overlay:
            self.overlay.withdraw()
            self._overlay_visible = False
        if self.hextech_overlay:
            self.hextech_overlay.withdraw()
            self._hextech_visible = False
        self.root.update()
        _time.sleep(0.15)

        thread = threading.Thread(target=self._run_hextech_analysis, daemon=True)
        thread.start()

    def _run_hextech_analysis(self):
        global _is_hextech_analyzing
        try:
            t0 = _time.time()
            log.info("⚡ 开始海克斯分析")

            png_bytes, filepath = capture_hextech_cards()
            log.info(f"[截图裁切] ✅ {len(png_bytes)} bytes ({_time.time()-t0:.1f}s)")

            # 截图完成，立即恢复主窗口（让用户在等 AI 分析时仍能看攻略）
            self.root.after(0, self.root.deiconify)

            # 优先使用手动锁定的，否则使用 LCU 确认识别的英雄名
            curr_champ = self._locked_champion or getattr(self, "_detected_champion", None)

            # ===== 直接走 Gemini 截图视觉分析（砍掉了不靠谱的 OCR 中间层） =====
            log.info("[Gemini] ⚡ 海克斯截图分析中...")
            result = analyze_hextech_choice(
                png_bytes, _global_strategy, _hextech_history,
                champion_name=curr_champ
            )
            elapsed = _time.time() - t0
            log.info(f"[Gemini] ⚡ 海克斯分析完成 ({elapsed:.1f}s)")

            # 在主线程中显示结果
            self.root.after(0, lambda: self._show_hextech_result(result))
            log.info(f"海克斯分析总耗时 {_time.time()-t0:.1f}s")

        except Exception as e:
            log.error(f"海克斯分析出错: {e}")
            log.error(traceback.format_exc())
            self.root.after(0, lambda: self._show_hextech_result(
                f"❌ 海克斯分析失败\n\n{str(e)}"))
        finally:
            _is_hextech_analyzing = False
            self.root.after(0, self._restore_hextech_btn)

    def _restore_hextech_btn(self):
        self.root.deiconify()
        self.btn_hextech.configure(text=T("btn_hextech"), state=tk.NORMAL)

    def _on_hextech_close(self, chosen_text: str = None):
        """关闭海克斯临时面板，后台更新全局攻略。"""
        global _global_strategy, _hextech_history

        # 关闭海克斯面板
        if self.hextech_overlay:
            try:
                self.hextech_overlay.destroy()
            except Exception:
                pass
            self.hextech_overlay = None
            self.hextech_text = None
            self._hextech_visible = False

        # 如果有选择内容，记录并后台更新
        if chosen_text and _global_strategy:
            # 从分析结果中提取推荐的符文名（简单解析）
            hextech_name = self._extract_hextech_name(chosen_text)
            if hextech_name:
                _hextech_history.append(hextech_name)
                log.info(f"[海克斯] 已选: {hextech_name}, 历史: {_hextech_history}")
                self.status_label.configure(text=T("status_hextech_done"))

    def _extract_hextech_name(self, analysis_text: str) -> str:
        """从海克斯分析结果中提取推荐的符文名。"""
        import re
        
        # 优先级 1: 匹配箭头指向的推荐项 (例如 **选项1：全能吸取** ← 选这个)
        match = re.search(r'\*\*(?:选项|Option)\s*\w[：:]\s*(.+?)\*\*\s*←', analysis_text)
        if match:
            return match.group(1).strip()
        
        # 优先级 2: 匹配【推荐选择：XXX】格式（OCR+AI 混合输出）
        match = re.search(r'推荐选择[：:]\s*【(.+?)】', analysis_text)
        if match:
            return match.group(1).strip()
        
        # 优先级 3: 匹配加粗的选项行，去掉"选项X："前缀
        match = re.search(r'\*\*(?:选项|Option)\s*\w[：:]\s*(.+?)\*\*', analysis_text)
        if match:
            name = match.group(1).strip()
            return name.split("---")[0].split("(")[0].strip()

        # 优先级 4: 匹配第一个加粗的短语
        match = re.search(r'\*\*(.+?)\*\*', analysis_text)
        if match:
            name = match.group(1).strip()
            # 去掉可能残留的"选项X："前缀
            name = re.sub(r'^(?:选项|Option)\s*\w?[：:]\s*', '', name)
            if 1 < len(name) < 25: 
                return name

        log.warning(f"[海克斯] 提取推荐名失败，AI原文: {analysis_text[:100]}...")
        return None




    # ==================== ApexLol 数据 ====================
    def _init_apexlol_cache(self):
        """启动时加载 ApexLol 缓存，过期或即将过期时自动后台刷新。"""
        try:
            from apexlol_data import load_cache, is_cache_valid, get_cache_info
            import os

            cache_file = os.path.join(APEXLOL_CACHE_DIR, "apexlol_data.json")
            cache_file_exists = os.path.exists(cache_file)

            # 第一步：不管过没过期，只要文件存在就先加载（旧数据也比没数据强）
            if cache_file_exists:
                load_cache(APEXLOL_CACHE_DIR)
                info = get_cache_info(APEXLOL_CACHE_DIR)
                age_hours = info.get('age_hours', 0)
                ttl_hours = APEXLOL_CACHE_TTL_DAYS * 24
                remaining_hours = ttl_hours - age_hours
                log.info(f"[ApexLol] 缓存已加载 ({info.get('champion_count', 0)} 英雄, "
                         f"{age_hours:.0f}h 前更新, 剩余 {remaining_hours:.0f}h)")
                self.status_label.configure(
                    text=T("status_data_loaded").format(info.get('champion_count', 0)))

                # 第二步：检查是否需要自动刷新
                if remaining_hours <= 0:
                    # 已过期 → 立即后台刷新
                    log.info("[ApexLol] 缓存已过期，自动后台刷新中...")
                    self._auto_refresh_data()
                elif remaining_hours <= 24:
                    # 24小时内即将过期 → 预防性后台刷新
                    log.info(f"[ApexLol] 缓存将在 {remaining_hours:.0f}h 后过期，预防性后台刷新中...")
                    self._auto_refresh_data()
            else:
                # 完全没有缓存文件 → 首次使用，自动爬取
                log.info("[ApexLol] 首次使用，自动后台爬取数据...")
                self.status_label.configure(text=T("status_data_missing"))
                self._auto_refresh_data()
        except Exception as e:
            log.warning(f"[ApexLol] 缓存初始化失败: {e}")

    def _auto_refresh_data(self):
        """静默后台刷新 ApexLol 数据（不阻塞主线程，不弹窗）。"""
        if hasattr(self, '_data_updating') and self._data_updating:
            return  # 已经在更新中，不重复触发
        self._data_updating = True
        log.info("[ApexLol] 静默后台刷新启动")

        def _bg():
            try:
                from apexlol_scraper import scrape_all_champions
                from apexlol_data import load_cache
                scrape_all_champions(APEXLOL_CACHE_DIR)
                load_cache(APEXLOL_CACHE_DIR)
                log.info("[ApexLol] [OK] 静默后台刷新完成")
                self.root.after(0, lambda: self.status_label.configure(
                    text=T("status_data_done")))
            except Exception as e:
                log.error(f"[ApexLol] 静默后台刷新失败: {e}")
            finally:
                self._data_updating = False

        threading.Thread(target=_bg, daemon=True, name="ApexLolAutoRefresh").start()

    def _on_update_data(self):
        """点击 🔄 数据按钮：在后台爬取 apexlol.info 数据。"""
        if hasattr(self, '_data_updating') and self._data_updating:
            return
        self._data_updating = True

        self.btn_data.configure(text=T("btn_data_updating"), state=tk.DISABLED)
        self.status_label.configure(text=T("status_data_updating"))

        thread = threading.Thread(target=self._run_data_update, daemon=True)
        thread.start()

    def _run_data_update(self):
        """后台执行数据爬取。"""
        try:
            from apexlol_scraper import scrape_all_champions
            from apexlol_data import load_cache

            def progress(current, total, name):
                self.root.after(0, lambda: self.status_label.configure(
                    text=T("status_data_progress").format(current, total, name)))

            scrape_all_champions(APEXLOL_CACHE_DIR, progress_callback=progress)
            load_cache(APEXLOL_CACHE_DIR)

            self.root.after(0, lambda: self.status_label.configure(
                text=T("status_data_done")))
            log.info("[ApexLol] [OK] 数据更新完成")

        except Exception as e:
            log.error(f"[ApexLol] 数据更新失败: {e}")
            self.root.after(0, lambda: self.status_label.configure(
                text=T("status_data_error")))
        finally:
            self._data_updating = False
            self.root.after(0, lambda: self.btn_data.configure(
                text=T("btn_data"), state=tk.NORMAL))

    # ==================== 显示全局攻略 ====================
    def _show_global_result(self, content: str):
        """在 Toplevel 窗口中显示全局攻略内容。"""
        # 销毁旧窗口
        if self.overlay:
            try:
                self.overlay.destroy()
            except Exception:
                pass
            self.overlay = None
            self._overlay_visible = False

        # 创建新 Toplevel
        self.overlay = tk.Toplevel(self.root)
        self.overlay.title("ARAM 攻略")
        self.overlay.configure(bg=OVERLAY_BG_COLOR)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", OVERLAY_OPACITY)
        self.overlay.overrideredirect(True)

        screen_w = self.root.winfo_screenwidth()
        x_pos = screen_w - OVERLAY_WIDTH - 20
        y_pos = 40

        # 标题栏
        title_frame = tk.Frame(self.overlay, bg="#0d0d1a", cursor="fleur")
        title_frame.pack(fill=tk.X)

        drag_data = {"x": 0, "y": 0}

        def start_drag(e):
            drag_data["x"] = e.x
            drag_data["y"] = e.y

        def on_drag(e):
            x = self.overlay.winfo_x() + e.x - drag_data["x"]
            y = self.overlay.winfo_y() + e.y - drag_data["y"]
            self.overlay.geometry(f"+{x}+{y}")

        title_frame.bind("<Button-1>", start_drag)
        title_frame.bind("<B1-Motion>", on_drag)

        title_label = tk.Label(
            title_frame, text=T("overlay_title"),
            bg="#0d0d1a", fg=OVERLAY_TITLE_COLOR,
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE + 2, "bold"),
            padx=12, pady=8,
        )
        title_label.pack(side=tk.LEFT)
        title_label.bind("<Button-1>", start_drag)
        title_label.bind("<B1-Motion>", on_drag)

        # 关闭按钮
        close_btn = tk.Label(
            title_frame, text="  ✕  ", bg="#0d0d1a", fg="#ff4757",
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE + 2, "bold"),
            cursor="hand2",
        )
        close_btn.pack(side=tk.RIGHT, padx=4)
        close_btn.bind("<Button-1>", lambda e: self._hide_overlay())
        close_btn.bind("<Enter>", lambda e: close_btn.configure(bg="#2a0a0f"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(bg="#0d0d1a"))

        hint = tk.Label(
            title_frame, text=T("overlay_hint"),
            bg="#0d0d1a", fg="#666680",
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE - 2),
        )
        hint.pack(side=tk.RIGHT, padx=8)

        # 分隔线
        tk.Frame(self.overlay, bg=OVERLAY_ACCENT_COLOR, height=2).pack(fill=tk.X)

        # 内容区
        content_frame = tk.Frame(self.overlay, bg=OVERLAY_BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        scrollbar = tk.Scrollbar(content_frame, orient=tk.VERTICAL, bg=OVERLAY_BG_COLOR)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.overlay_text = tk.Text(
            content_frame, bg=OVERLAY_BG_COLOR, fg=OVERLAY_FG_COLOR,
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE), wrap=tk.WORD,
            relief=tk.FLAT, padx=12, pady=8, insertbackground=OVERLAY_FG_COLOR,
            yscrollcommand=scrollbar.set, cursor="arrow",
            spacing1=2, spacing3=2,
        )
        self.overlay_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.overlay_text.yview)

        # 文本样式
        self._setup_text_tags(self.overlay_text)

        # 渲染内容
        self._render_markdown(self.overlay_text, content)
        self.overlay_text.configure(state=tk.DISABLED)

        # 底部
        bottom = tk.Frame(self.overlay, bg="#0d0d1a")
        bottom.pack(fill=tk.X)
        tk.Label(
            bottom, text=T("overlay_footer"),
            bg="#0d0d1a", fg="#444460",
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE - 2), pady=4,
        ).pack()

        # 快捷键
        self.overlay.bind("<Escape>", lambda e: self._hide_overlay())

        # 大小和位置
        self.overlay.update_idletasks()
        h = min(self.overlay_text.winfo_reqheight() + 80, OVERLAY_MAX_HEIGHT)
        self.overlay.geometry(f"{OVERLAY_WIDTH}x{h}+{x_pos}+{y_pos}")
        self.overlay.configure(highlightbackground=OVERLAY_ACCENT_COLOR,
                               highlightthickness=1)
        self._overlay_visible = True

        self.status_label.configure(text=T("status_done"))

    # ==================== 显示海克斯建议 ====================
    def _show_hextech_result(self, content: str):
        """在临时 Toplevel 窗口中显示海克斯选择建议。"""
        # 先恢复主按钮栏
        self.root.deiconify()

        # 销毁旧海克斯面板
        if self.hextech_overlay:
            try:
                self.hextech_overlay.destroy()
            except Exception:
                pass
            self.hextech_overlay = None
            self._hextech_visible = False

        # 保存最新分析结果用于关闭时提取符文名
        self._last_hextech_result = content

        # 创建新 Toplevel（位于屏幕左侧中部）
        self.hextech_overlay = tk.Toplevel(self.root)
        self.hextech_overlay.title("⚡ 海克斯")
        self.hextech_overlay.configure(bg=OVERLAY_BG_COLOR)
        self.hextech_overlay.attributes("-topmost", True)
        self.hextech_overlay.attributes("-alpha", OVERLAY_OPACITY)
        self.hextech_overlay.overrideredirect(True)

        hex_width = 420
        x_pos = 20
        screen_h = self.root.winfo_screenheight()
        y_pos = max(40, (screen_h - 500) // 2)

        # 标题栏（红色调，区别于全局面板）
        title_frame = tk.Frame(self.hextech_overlay, bg="#1a0d0d", cursor="fleur")
        title_frame.pack(fill=tk.X)

        drag_data = {"x": 0, "y": 0}

        def start_drag(e):
            drag_data["x"] = e.x
            drag_data["y"] = e.y

        def on_drag(e):
            x = self.hextech_overlay.winfo_x() + e.x - drag_data["x"]
            y = self.hextech_overlay.winfo_y() + e.y - drag_data["y"]
            self.hextech_overlay.geometry(f"+{x}+{y}")

        title_frame.bind("<Button-1>", start_drag)
        title_frame.bind("<B1-Motion>", on_drag)

        title_label = tk.Label(
            title_frame, text=T("hextech_title"),
            bg="#1a0d0d", fg="#ff6b6b",
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE + 2, "bold"),
            padx=12, pady=8,
        )
        title_label.pack(side=tk.LEFT)
        title_label.bind("<Button-1>", start_drag)
        title_label.bind("<B1-Motion>", on_drag)

        # 关闭按钮
        close_btn = tk.Label(
            title_frame, text="  ✕  ", bg="#1a0d0d", fg="#ff4757",
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE + 2, "bold"),
            cursor="hand2",
        )
        close_btn.pack(side=tk.RIGHT, padx=4)
        close_btn.bind("<Button-1>", lambda e: self._on_hextech_close(content))
        close_btn.bind("<Enter>", lambda e: close_btn.configure(bg="#2a0a0f"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(bg="#1a0d0d"))

        # 分隔线（红色调）
        tk.Frame(self.hextech_overlay, bg="#ff6b6b", height=2).pack(fill=tk.X)

        # 内容区
        content_frame = tk.Frame(self.hextech_overlay, bg=OVERLAY_BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        scrollbar = tk.Scrollbar(content_frame, orient=tk.VERTICAL, bg=OVERLAY_BG_COLOR)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.hextech_text = tk.Text(
            content_frame, bg=OVERLAY_BG_COLOR, fg=OVERLAY_FG_COLOR,
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE), wrap=tk.WORD,
            relief=tk.FLAT, padx=12, pady=8, insertbackground=OVERLAY_FG_COLOR,
            yscrollcommand=scrollbar.set, cursor="arrow",
            spacing1=2, spacing3=2,
        )
        self.hextech_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.hextech_text.yview)

        # 文本样式
        self._setup_text_tags(self.hextech_text)

        # 渲染内容
        self._render_markdown(self.hextech_text, content)
        self.hextech_text.configure(state=tk.DISABLED)

        # 底部按钮栏
        bottom = tk.Frame(self.hextech_overlay, bg="#1a0d0d")
        bottom.pack(fill=tk.X)

        # 🔄 再截一次
        retry_btn = tk.Button(
            bottom, text=T("hextech_btn_retry"), command=self._on_hextech,
            bg="#1a0d0d", fg="#ffd700", activebackground="#2a2a4e",
            activeforeground="#ffffff", font=("Microsoft YaHei UI", 10, "bold"),
            padx=12, pady=6, cursor="hand2", relief=tk.FLAT, borderwidth=0,
        )
        retry_btn.pack(side=tk.LEFT, padx=8, pady=4)

        # ✕ 关闭（确认选择）
        close_btn2 = tk.Button(
            bottom, text=T("hextech_btn_close"), command=lambda: self._on_hextech_close(content),
            bg="#1a0d0d", fg="#ff4757", activebackground="#2a2a4e",
            activeforeground="#ffffff", font=("Microsoft YaHei UI", 10, "bold"),
            padx=12, pady=6, cursor="hand2", relief=tk.FLAT, borderwidth=0,
        )
        close_btn2.pack(side=tk.RIGHT, padx=8, pady=4)

        # 快捷键
        self.hextech_overlay.bind("<Escape>", lambda e: self._on_hextech_close(content))

        # 大小和位置
        self.hextech_overlay.update_idletasks()
        h = min(self.hextech_text.winfo_reqheight() + 100, 500)
        self.hextech_overlay.geometry(f"{hex_width}x{h}+{x_pos}+{y_pos}")
        self.hextech_overlay.configure(highlightbackground="#ff6b6b",
                                       highlightthickness=1)
        self._hextech_visible = True

        self.status_label.configure(text=T("status_hextech_done"))

    # ==================== 全局攻略 显示/隐藏 ====================
    def _hide_overlay(self):
        """隐藏全局攻略窗口。"""
        if self.overlay:
            try:
                self.overlay.withdraw()
            except tk.TclError:
                pass
            self._overlay_visible = False

    def _on_show(self):
        """点击📋按钮：显示/隐藏全局攻略。"""
        if self.overlay:
            try:
                exists = self.overlay.winfo_exists()
            except (tk.TclError, RuntimeError):
                exists = False
            if not exists:
                self.overlay = None
                self._overlay_visible = False
                if _global_strategy:
                    self._show_global_result(_global_strategy)
                return

            if self._overlay_visible:
                self._hide_overlay()
            else:
                try:
                    self.overlay.deiconify()
                    self.overlay.lift()
                    self.overlay.attributes("-topmost", True)
                    self.overlay.focus_force()
                    self._overlay_visible = True
                    try:
                        import ctypes
                        self.overlay.update_idletasks()
                        hwnd = int(self.overlay.frame(), 16)
                        ctypes.windll.user32.SetForegroundWindow(hwnd)
                    except Exception:
                        pass
                except tk.TclError:
                    self.overlay = None
                    self._overlay_visible = False
                    if _global_strategy:
                        self._show_global_result(_global_strategy)
        elif _global_strategy:
            self._show_global_result(_global_strategy)

    # ==================== 共用文本渲染 ====================
    def _setup_text_tags(self, text_widget):
        """为 Text widget 设置样式标签。"""
        text_widget.tag_configure(
            "heading", foreground=OVERLAY_TITLE_COLOR,
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE + 3, "bold"),
            spacing1=12, spacing3=4,
        )
        text_widget.tag_configure(
            "subheading", foreground=OVERLAY_ACCENT_COLOR,
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE + 1, "bold"),
            spacing1=8, spacing3=2,
        )
        text_widget.tag_configure(
            "bold", foreground="#ffffff",
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE, "bold"),
        )
        text_widget.tag_configure("normal", foreground=OVERLAY_FG_COLOR)

    def _render_markdown(self, text_widget, text: str):
        """渲染 Markdown 到指定 Text widget。"""
        import re
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("## "):
                text_widget.insert(tk.END, stripped[3:] + "\n", "heading")
            elif stripped.startswith("### "):
                text_widget.insert(tk.END, stripped[4:] + "\n", "subheading")
            elif stripped.startswith("# "):
                text_widget.insert(tk.END, stripped[2:] + "\n", "heading")
            elif stripped.startswith("- ") or stripped.startswith("* "):
                text_widget.insert(tk.END, "  • ")
                self._insert_bold(text_widget, stripped[2:] + "\n", "normal")
            elif re.match(r"^\d+\.\s", stripped):
                idx = stripped.index(".") + 1
                text_widget.insert(tk.END, "  " + stripped[:idx] + " ")
                self._insert_bold(text_widget, stripped[idx:].strip() + "\n", "normal")
            elif stripped.startswith("**") and stripped.endswith("**"):
                text_widget.insert(tk.END, stripped[2:-2] + "\n", "bold")
            elif stripped == "":
                text_widget.insert(tk.END, "\n")
            else:
                self._insert_bold(text_widget, stripped + "\n", "normal")

    def _insert_bold(self, text_widget, text: str, base_tag: str):
        """处理文本中 **粗体** 标记。"""
        import re
        parts = re.split(r"(\*\*.*?\*\*)", text)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                text_widget.insert(tk.END, part[2:-2], "bold")
            else:
                text_widget.insert(tk.END, part, base_tag)

    # ==================== 工具方法 ====================
    def _keep_topmost(self):
        try:
            self.root.lift()
        except Exception:
            pass

    def _on_settings(self):
        try:
            from settings_ui import open_settings_dialog
            open_settings_dialog(self.root)
        except Exception as e:
            log.error(f"[设置] 打开失败: {e}")
            from tkinter import messagebox
            messagebox.showerror("⚠️", str(e), parent=self.root)

    def _on_exit(self):
        log.info("[退出] 用户点击退出按钮")
        try:
            print(f"\n{T('console_bye')}")
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass
        sys.exit(0)

    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() + event.x - self._drag_data["x"]
        y = self.root.winfo_y() + event.y - self._drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    # ==================== 全局热键 ====================

    def run(self):
        self.root.mainloop()


def main():
    print("=" * 50)
    print(T("console_title"))
    print("=" * 50)

    print(f"\n{T('console_btn_hint')}")
    print(T("console_analyze_hint"))
    print(T("console_guide_hint"))
    print(T("console_drag_hint"))

    print(f"\n{T('console_restart_hint')}")
    print(T("console_hero_hint"))
    print(T("console_log").format(LOG_FILE))
    print(T("console_exit"))
    print("=" * 50 + "\n")

    log.info(T("console_started"))
    app = App()
    # 应用 DOS 窗口显隐偏好（只在 Windows 生效）
    set_console_visible(SHOW_CONSOLE)
    try:
        app.run()
    except KeyboardInterrupt:
        print(f"\n{T('console_bye')}")
        sys.exit(0)


if __name__ == "__main__":
    main()
