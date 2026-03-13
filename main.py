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
import time as _time
import threading
import traceback
import logging
import ctypes
import ctypes.wintypes
import tkinter as tk

# ==================== 日志配置 ====================
LOG_DIR = os.path.dirname(os.path.abspath(__file__))
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

from screenshot import capture_screen
from gemini_analyzer import analyze_screenshot, analyze_hextech_choice, update_global_strategy
from config import (
    OVERLAY_BG_COLOR, OVERLAY_FG_COLOR, OVERLAY_ACCENT_COLOR,
    OVERLAY_TITLE_COLOR, OVERLAY_WIDTH, OVERLAY_MAX_HEIGHT,
    OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE, OVERLAY_OPACITY, T,
    APEXLOL_ENABLED, APEXLOL_CACHE_DIR, APEXLOL_CACHE_TTL_DAYS,
)

# 状态
_is_analyzing = False
_is_hextech_analyzing = False
_global_strategy = None       # 全局攻略文本（缓存）
_hextech_history = []          # 已选海克斯列表
_is_auto_grabbing = False     # 是否在后台自动抢英雄


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

        # ⚔️ 全局分析
        self.btn_analyze = tk.Button(
            btn_frame, text=T("btn_analyze"), command=self._on_analyze,
            bg="#1a1a2e", fg="#ffd700", activebackground="#2a2a4e",
            activeforeground="#ffffff", font=("Microsoft YaHei UI", 11, "bold"),
            padx=8, pady=4, cursor="hand2", relief=tk.FLAT, borderwidth=0,
        )
        self.btn_analyze.pack(side=tk.LEFT, padx=(2, 1))

        sep1 = tk.Label(btn_frame, text="|", bg="#1a1a2e", fg="#333355",
                        font=("Microsoft YaHei UI", 11))
        sep1.pack(side=tk.LEFT)

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

        # ✏️ 纠错 (Fix)
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

        # 🔄 抢英雄 (Auto-Grab)
        self.btn_grab = tk.Button(
            btn_frame, text="🔄 抢英雄", command=self._on_toggle_grab,
            bg="#1a1a2e", fg="#00ff00", activebackground="#2a2a4e",
            activeforeground="#ffffff", font=("Microsoft YaHei UI", 11, "bold"),
            padx=8, pady=4, cursor="hand2", relief=tk.FLAT, borderwidth=0,
        )
        self.btn_grab.pack(side=tk.LEFT, padx=(1, 1))

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

        self.status_label = tk.Label(
            self.root, text=T("status_ready"),
            bg="#1a1a2e", fg="#666680", font=("Microsoft YaHei UI", 8),
        )
        self.status_label.pack()

        self.root.configure(bg="#00d4ff", highlightthickness=1,
                            highlightbackground="#00d4ff")

        # 拖拽
        self._drag_data = {"x": 0, "y": 0}
        drag_widgets = [self.btn_analyze, self.btn_hextech, self.btn_show, self.btn_fix, self.btn_grab,
                        sep1, sep2, sep_fix, self.status_label, btn_frame]
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
        
        # 全局热键 (Ctrl+F12)
        self._start_hotkey_listener()

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
        global _is_analyzing, _is_hextech_analyzing
        _match_analyzed_flag = False
        from lcu_client import get_loading_screen_rosters, get_gameflow_phase
        import time
        
        while True:
            try:
                phase = get_gameflow_phase()
                
                # 在加载界面 (InProgress) 进行秒级前瞻分析
                if phase == "InProgress":
                    if not _match_analyzed_flag and not _is_analyzing and not _is_hextech_analyzing:
                        rosters = get_loading_screen_rosters()
                        if rosters:
                            log.info("🚀 发现新对局加载中！LCU 自动捕获 10 人阵容，正在无感生成攻略...")
                            _match_analyzed_flag = True
                            # 在主线程中触发纯文本全量分析
                            self.root.after(0, lambda r=rosters: self._run_lcu_auto_analysis(r))
                else:
                    # 如果不是在游戏中，则重置标记，准备迎接下一局
                    _match_analyzed_flag = False
            except Exception as e:
                pass
            time.sleep(3)

    def _run_lcu_auto_analysis(self, rosters: dict):
        """执行 LCU 纯文本全量分析（无截图界面）"""
        global _is_analyzing, _global_strategy, _hextech_history
        if _is_analyzing:
            return
        
        _is_analyzing = True
        self.btn_analyze.configure(text=T("btn_analyzing"), state=tk.DISABLED)
        self.status_label.configure(text="全自动 LCU 数据分析中...")
        
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
                self.root.after(0, self._restore_analyze_btn)
                
        t = threading.Thread(target=_bg_task, daemon=True)
        t.start()


    def _console_input_listener(self):
        """后台监听命令行输入，支持开局前手动指定英雄。"""
        print("\n" + "="*50)
        print("💻 终端手动输入已启用！\n您可以直接在此窗口打字输入英雄名并回车，将立刻为您分析！")
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
        self.btn_analyze.configure(text=T("btn_analyzing"), state=tk.DISABLED)
        self.status_label.configure(text=T("status_analyzing"))
        
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
                self.root.after(0, self._restore_analyze_btn)
                
        t = threading.Thread(target=_bg_task, daemon=True)
        t.start()


    # ==================== 全局分析 ====================
    def _on_analyze(self, manual_champion: str = None):
        global _is_analyzing
        if _is_analyzing:
            return
            
        # 1. 检查当前游戏阶段 (v1.7.0 分流逻辑)
        from lcu_client import get_gameflow_phase
        current_phase = get_gameflow_phase()
        log.info(f"[UI] 分析按钮触发，当前阶段: {current_phase}")
        
        # 如果是 ChampSelect 或之前，或者虽然是 InProgress 但用户之前手动锁定了英雄且我们只想看英雄建议
        # 核心逻辑：加载阶段（GameStart/LoadingScreen）不应截图，因为 LCU 暗中处理了
        # 我们这里只在 InProgress 阶段保留截图分析逻辑
        if current_phase not in ["InProgress"]:
            # 非对局中：执行“极速前瞻”逻辑 (文字分析)
            # 优先使用锁定的英雄，或者 LCU 当前选中的英雄
            target = manual_champion or self._locked_champion
            if not target:
                from lcu_client import get_champ_select_info
                info = get_champ_select_info()
                if info and info.get("my_champion"):
                    target = info["my_champion"]
            
            if target:
                log.info(f"[UI] 非对局中阶段，执行极速前瞻: {target}")
                self._run_quick_guide(target)
                return
            else:
                self.status_label.configure(text="❌ 未检测到英雄，请先锁定英雄或输入英雄名。")
                return

        # 2. 如果是 InProgress 阶段，则执行“截图全量分析” (Tab 战绩表分析)
        _is_analyzing = True
        self.btn_analyze.configure(text=T("btn_analyzing"), state=tk.DISABLED)
        self.status_label.configure(text=T("status_analyzing"))
        self.root.update()

        # 隐藏按钮和攻略，避免截图中出现
        self.root.withdraw()
        if self.overlay:
            self.overlay.withdraw()
            self._overlay_visible = False
        if self.hextech_overlay:
            self.hextech_overlay.withdraw()
            self._hextech_visible = False
        self.root.update()
        _time.sleep(0.15)

        # 后台线程执行分析
        thread = threading.Thread(target=self._run_analysis, args=(manual_champion,), daemon=True)
        thread.start()

    def _on_fix(self):
        """手动纠错：弹窗询问英雄名，并重新强制分析"""
        global _is_analyzing
        if _is_analyzing:
            return
            
        import tkinter.simpledialog as sd
        # 弹窗时需要将主窗口抬高，否则对话框可能被遮挡
        self.root.lift()
        self.root.attributes("-topmost", True)
        
        name = sd.askstring(
            T("fix_prompt_title"),
            T("fix_prompt_msg"),
            parent=self.root
        )
        
        if name and name.strip():
            cmd = name.strip()
            log.info(f"用户手动请求锁定/纠错英雄，英雄名: {cmd}")
            # 更新锁定英雄并在主线程中重新触发全局分析（点击分析按钮，走截图全量分析流程）
            self._locked_champion = cmd
            self._on_analyze()
        else:
            if name is not None: # 不为None说明点了确定但没输入
                from tkinter import messagebox
                messagebox.showwarning("⚠️", T("fix_error"), parent=self.root)

    def _on_toggle_grab(self):
        """切换后台自动抢替补席状态"""
        global _is_auto_grabbing
        if _is_auto_grabbing:
            _is_auto_grabbing = False
            self.btn_grab.configure(text="🔄 抢英雄", fg="#00ff00")
            self.status_label.configure(text="已停止自动监控替补席。")
        else:
            _is_auto_grabbing = True
            self.btn_grab.configure(text="⏳ 抢选中", fg="#ffaa00")
            self.status_label.configure(text="后台监控替补席中，发现心愿单英雄将自动秒抢 (不消耗API额度)！")
            thread = threading.Thread(target=self._grab_loop, daemon=True)
            thread.start()

    def _grab_loop(self):
        """后台轮询抢选英雄"""
        global _is_auto_grabbing
        import time, json
        from lcu_client import get_bench_info, swap_bench_champion
        
        wishlist_file = os.path.join(LOG_DIR, "grab_wishlist.json")
        
        while _is_auto_grabbing:
            try:
                if not os.path.exists(wishlist_file):
                    self.root.after(0, lambda: self.status_label.configure(text="❌ 未找到 grab_wishlist.json！请先在当前目录下配置。"))
                    _is_auto_grabbing = False
                    self.root.after(0, lambda: self.btn_grab.configure(text="🔄 抢英雄", fg="#00ff00"))
                    break
                
                with open(wishlist_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    wishlist = set(data.get("wishlist", []))
                
                if not wishlist:
                    time.sleep(1)
                    continue

                bench_info = get_bench_info()
                if not bench_info:
                    time.sleep(1)
                    continue
                
                my_champ = bench_info.get("my_champion_name", "")
                # 如果当前操作的就是心愿单里的英雄，则暂停抢夺以防误操作换出去
                if my_champ in wishlist:
                    time.sleep(1)
                    continue
                
                bench = bench_info.get("bench", [])
                for b in bench:
                    if b["name"] in wishlist:
                        success, current_msg = swap_bench_champion(b["id"])
                        if success:
                            msg = f"🎉 成功帮您秒抢到【{b['name']}】！"
                            log.info(msg)
                            self.root.after(0, lambda m=msg: self.status_label.configure(text=m))
                            # 抢到就自动停止轮询
                            _is_auto_grabbing = False
                            self.root.after(0, lambda: self.btn_grab.configure(text="🔄 抢英雄", fg="#00ff00"))
                            break
            except Exception as e:
                log.error(f"抢英雄监控失败: {e}")
                time.sleep(2)
            
            # 使用本地 LCU 接口轮询，不耗费任何网络 API Token，0.5秒一次毫无压力
            time.sleep(0.5)

    def _run_analysis(self, manual_champion: str = None):
        global _is_analyzing, _global_strategy, _hextech_history
        try:
            t0 = _time.time()
            
            # 使用传入的、或之前控制台/纠错口锁定的英雄
            target_champion = manual_champion or self._locked_champion
            
            # 智能分流：如果能获取到 10 人名单，首选纯文字极速分析
            from lcu_client import get_live_team_rosters
            rosters = get_live_team_rosters()
            
            if rosters:
                log.info("[LCU] 🎲 成功捕获 10 人阵容名单，自动切入纯文本极速流！")
                from gemini_analyzer import analyze_lcu_rosters
                result = analyze_lcu_rosters(rosters, _hextech_history)
                log.info(f"[Gemini] ✅ 极速文本分析完成 ({_time.time()-t0:.1f}s)")
            else:
                log.info(f"🎮 [回退截图流] 开始全局分析 {'(已锁定英雄: '+target_champion+')' if target_champion else ''}")
                png_bytes, filepath = capture_screen()
                log.info(f"[截图] ✅ {len(png_bytes)} bytes ({_time.time()-t0:.1f}s)")

                t1 = _time.time()
                log.info("[Gemini] ⏳ 全局截屏分析中...")
                result = analyze_screenshot(
                    png_bytes, 
                    manual_champion=target_champion,
                    hextech_history=_hextech_history
                )
                log.info(f"[Gemini] ✅ {len(result)} 字符 ({_time.time()-t1:.1f}s)")

            _global_strategy = result

            
            # 只有在非游戏中（InProgress）阶段才重置历史，确保游戏内更新能继承记忆
            from lcu_client import get_gameflow_phase
            if get_gameflow_phase() != "InProgress":
                # 重置历史
                _hextech_history = []
                # 加载界面分析完毕后，说明游戏开始了，可以解锁英雄，以便下局使用
                if not manual_champion and self._locked_champion:
                    log.info(f"🔓 解除英雄锁定: {self._locked_champion}")
                    self._locked_champion = None

            # 在主线程中显示结果
            self.root.after(0, lambda: self._show_global_result(result))
            log.info(f"总耗时 {_time.time()-t0:.1f}s")

        except Exception as e:
            log.error(f"全局分析出错: {e}")
            log.error(traceback.format_exc())
            self.root.after(0, lambda: self._show_global_result(
                f"{T('analysis_error')}\n\n{str(e)}"))
        finally:
            _is_analyzing = False
            self.root.after(0, self._restore_analyze_btn)

    def _restore_analyze_btn(self):
        self.root.deiconify()
        self.btn_analyze.configure(text=T("btn_analyze"), state=tk.NORMAL)
        self.status_label.configure(text=T("status_done"))

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

            png_bytes, filepath = capture_screen()
            log.info(f"[截图] ✅ {len(png_bytes)} bytes ({_time.time()-t0:.1f}s)")

            t1 = _time.time()
            log.info("[Gemini] ⚡ 海克斯分析中...")
            result = analyze_hextech_choice(
                png_bytes, _global_strategy, _hextech_history
            )
            elapsed = _time.time() - t1
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

                # 后台更新全局攻略
                thread = threading.Thread(
                    target=self._run_strategy_update,
                    args=(hextech_name,),
                    daemon=True,
                )
                thread.start()

    def _extract_hextech_name(self, analysis_text: str) -> str:
        """从海克斯分析结果中提取推荐的符文名。"""
        import re
        # 优先级 1: 匹配箭头指向的推荐项 (例如 **选项1：全能吸取** ← 选这个)
        match = re.search(r'\*\*(?:选项|Option)\s*\w[：:]\s*(.+?)\*\*\s*←', analysis_text)
        if match:
            return match.group(1).strip()
        
        # 优先级 2: 匹配加粗的选项行 (例如 **选项1：全能吸取**)
        match = re.search(r'\*\*(?:选项|Option)\s*\w[：:]\s*(.+?)\*\*', analysis_text)
        if match:
            # 过滤干扰词
            name = match.group(1).strip()
            return name.split("---")[0].split("(")[0].strip()

        # 优先级 3: 匹配第一个加粗的短语（通常是第一个推荐项）
        match = re.search(r'\*\*(.+?)\*\*', analysis_text)
        if match:
            name = match.group(1).strip()
            if 1 < len(name) < 25: 
                return name

        log.warning(f"[海克斯] 提取推荐名失败，AI原文: {analysis_text[:100]}...")
        return None


    def _run_strategy_update(self, latest_hextech: str):
        """后台线程：更新全局攻略。"""
        global _global_strategy
        try:
            updated = update_global_strategy(
                _global_strategy, _hextech_history, latest_hextech, timeout=5.0
            )
            if updated:
                _global_strategy = updated
                log.info("[更新] 全局攻略已更新")
                # 如果全局面板可见，刷新内容
                self.root.after(0, lambda: self._refresh_global_overlay(updated))
                self.root.after(0, lambda: self.status_label.configure(
                    text=T("status_hextech_updated")))
            else:
                log.info("[更新] 全局攻略更新超时或失败，保持原攻略")
                self.root.after(0, lambda: self.status_label.configure(
                    text=T("status_done")))
        except Exception as e:
            log.error(f"[更新] 全局攻略更新异常: {e}")

    def _refresh_global_overlay(self, content: str):
        """刷新全局攻略面板内容（不重建窗口）。"""
        if self.overlay and self.overlay_text:
            try:
                self.overlay_text.configure(state=tk.NORMAL)
                self.overlay_text.delete("1.0", tk.END)
                self._render_markdown(self.overlay_text, content)
                self.overlay_text.configure(state=tk.DISABLED)
            except Exception:
                pass

    # ==================== ApexLol 数据 ====================
    def _init_apexlol_cache(self):
        """启动时加载 ApexLol 缓存，如果不存在则提示。"""
        try:
            from apexlol_data import load_cache, is_cache_valid, get_cache_info

            if is_cache_valid(APEXLOL_CACHE_DIR, APEXLOL_CACHE_TTL_DAYS):
                load_cache(APEXLOL_CACHE_DIR)
                info = get_cache_info(APEXLOL_CACHE_DIR)
                log.info(f"[ApexLol] 缓存已加载 ({info.get('champion_count', 0)} 英雄, "
                         f"{info.get('age_hours', 0):.0f}h 前更新)")
                self.status_label.configure(
                    text=T("status_data_loaded").format(info.get('champion_count', 0)))
            else:
                log.info("[ApexLol] 缓存不存在或已过期，请点击 🔄 更新数据")
                self.status_label.configure(text=T("status_data_missing"))
        except Exception as e:
            log.warning(f"[ApexLol] 缓存初始化失败: {e}")

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
            log.info("[ApexLol] ✅ 数据更新完成")

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
        screen_h = self.root.winfo_screenheight()
        x_pos = 20
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
            self.root.attributes("-topmost", True)
            self.root.after(3000, self._keep_topmost)
        except Exception:
            pass

    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() + event.x - self._drag_data["x"]
        y = self.root.winfo_y() + event.y - self._drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    # ==================== 全局热键 ====================
    def _start_hotkey_listener(self):
        """在后台线程中注册 Ctrl+F12 全局热键，用于恢复UI和切换攻略窗口。"""
        def _listener():
            try:
                user32 = ctypes.windll.user32
                HOTKEY_ID_TOGGLE = 1
                MOD_CONTROL = 0x0002
                VK_F12 = 0x7B

                if not user32.RegisterHotKey(None, HOTKEY_ID_TOGGLE, MOD_CONTROL, VK_F12):
                    log.warning("⚠️ 注册全局热键 Ctrl+F12 失败（可能已被占用）")
                    return

                log.info("✅ 全局热键 Ctrl+F12 已注册（恢复UI + 切换攻略窗口）")

                msg = ctypes.wintypes.MSG()
                while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                    if msg.message == 0x0312:  # WM_HOTKEY
                        if msg.wParam == HOTKEY_ID_TOGGLE:
                            log.debug("🔑 热键 Ctrl+F12 触发")
                            try:
                                self.root.after(0, self._recover_and_show)
                            except Exception:
                                pass

                user32.UnregisterHotKey(None, HOTKEY_ID_TOGGLE)
            except Exception as e:
                log.error(f"热键线程异常: {e}")

        t = threading.Thread(target=_listener, daemon=True, name="HotkeyListener")
        t.start()

    def _recover_and_show(self):
        """恢复所有UI元素 + 切换攻略显示。

        确保浮动按钮栏始终可见，然后切换攻略窗口。
        """
        try:
            # 1. 恢复主按钮栏（即使正常状态也安全调用）
            self.root.deiconify()
            self.root.lift()
            self.root.attributes("-topmost", True)

            # 2. 切换攻略窗口
            self._on_show()
        except Exception as e:
            log.error(f"恢复UI失败: {e}")

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
    print(f"\n{T('console_hotkey_hint')}")
    print(f"\n{T('console_restart_hint')}")
    print(T("console_hero_hint"))
    print(T("console_log").format(LOG_FILE))
    print(T("console_exit"))
    print("=" * 50 + "\n")

    log.info(T("console_started"))
    app = App()
    try:
        app.run()
    except KeyboardInterrupt:
        print(f"\n{T('console_bye')}")
        sys.exit(0)


if __name__ == "__main__":
    main()
