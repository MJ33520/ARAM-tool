# -*- coding: utf-8 -*-
"""
ARAM 智能助手 - 主入口

单一 tkinter Root 架构：
- TriggerButton: 主 Tk() root，浮动按钮
- Overlay: Toplevel 窗口，攻略显示
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
from gemini_analyzer import analyze_screenshot
from config import (
    OVERLAY_BG_COLOR, OVERLAY_FG_COLOR, OVERLAY_ACCENT_COLOR,
    OVERLAY_TITLE_COLOR, OVERLAY_WIDTH, OVERLAY_MAX_HEIGHT,
    OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE, OVERLAY_OPACITY,
)

# 状态
_is_analyzing = False
_last_result = None


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

        self.btn_analyze = tk.Button(
            btn_frame, text="⚔️ 分析", command=self._on_analyze,
            bg="#1a1a2e", fg="#ffd700", activebackground="#2a2a4e",
            activeforeground="#ffffff", font=("Microsoft YaHei UI", 11, "bold"),
            padx=8, pady=4, cursor="hand2", relief=tk.FLAT, borderwidth=0,
        )
        self.btn_analyze.pack(side=tk.LEFT, padx=(2, 1))

        sep = tk.Label(btn_frame, text="|", bg="#1a1a2e", fg="#333355",
                       font=("Microsoft YaHei UI", 11))
        sep.pack(side=tk.LEFT)

        self.btn_show = tk.Button(
            btn_frame, text="📋 攻略", command=self._on_show,
            bg="#1a1a2e", fg="#00d4ff", activebackground="#2a2a4e",
            activeforeground="#ffffff", font=("Microsoft YaHei UI", 11, "bold"),
            padx=8, pady=4, cursor="hand2", relief=tk.FLAT, borderwidth=0,
        )
        self.btn_show.pack(side=tk.LEFT, padx=(1, 2))

        self.status_label = tk.Label(
            self.root, text="就绪 | 右键拖拽移动",
            bg="#1a1a2e", fg="#666680", font=("Microsoft YaHei UI", 8),
        )
        self.status_label.pack()

        self.root.configure(bg="#00d4ff", highlightthickness=1,
                            highlightbackground="#00d4ff")

        # 拖拽
        self._drag_data = {"x": 0, "y": 0}
        for w in [self.btn_analyze, self.btn_show, sep, self.status_label, btn_frame]:
            w.bind("<Button-3>", self._start_drag)
            w.bind("<B3-Motion>", self._on_drag)

        # ===== 攻略 Toplevel 窗口 =====
        self.overlay = None  # Toplevel 窗口
        self.overlay_text = None  # Text widget
        self._overlay_visible = False  # 显式跟踪攻略窗口可见状态

        # 保持置顶
        self._keep_topmost()

        # 全局热键 (Ctrl+F12)
        self._start_hotkey_listener()

    # ==================== 分析 ====================
    def _on_analyze(self):
        global _is_analyzing
        if _is_analyzing:
            return
        _is_analyzing = True

        self.btn_analyze.configure(text="⏳ ...", state=tk.DISABLED)
        self.status_label.configure(text="正在截图和分析...")
        self.root.update()

        # 隐藏按钮和攻略，避免截图中出现
        self.root.withdraw()
        if self.overlay:
            self.overlay.withdraw()
            self._overlay_visible = False
        self.root.update()
        _time.sleep(0.15)

        # 后台线程执行分析
        thread = threading.Thread(target=self._run_analysis, daemon=True)
        thread.start()

    def _run_analysis(self):
        global _is_analyzing, _last_result
        try:
            t0 = _time.time()
            log.info("🎮 开始分析")

            png_bytes, filepath = capture_screen()
            log.info(f"[截图] ✅ {len(png_bytes)} bytes ({_time.time()-t0:.1f}s)")

            t1 = _time.time()
            log.info("[Gemini] ⏳ 分析中...")
            result = analyze_screenshot(png_bytes)
            log.info(f"[Gemini] ✅ {len(result)} 字符 ({_time.time()-t1:.1f}s)")

            _last_result = result

            # 在主线程中显示结果
            self.root.after(0, lambda: self._show_result(result))
            log.info(f"总耗时 {_time.time()-t0:.1f}s")

        except Exception as e:
            log.error(f"分析出错: {e}")
            log.error(traceback.format_exc())
            self.root.after(0, lambda: self._show_result(f"❌ 分析出错\n\n{str(e)}"))
        finally:
            _is_analyzing = False
            self.root.after(0, self._restore_btn)

    def _restore_btn(self):
        self.root.deiconify()
        self.btn_analyze.configure(text="⚔️ 分析", state=tk.NORMAL)
        self.status_label.configure(text="✅ 完成 | 点📋查看攻略")

    # ==================== 显示攻略 ====================
    def _show_result(self, content: str):
        """在 Toplevel 窗口中显示攻略内容。"""
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
            title_frame, text="⚔️ ARAM 助手 - 阵容分析",
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
            title_frame, text="Esc 隐藏 | 可拖拽",
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
        self.overlay_text.tag_configure(
            "heading", foreground=OVERLAY_TITLE_COLOR,
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE + 3, "bold"),
            spacing1=12, spacing3=4,
        )
        self.overlay_text.tag_configure(
            "subheading", foreground=OVERLAY_ACCENT_COLOR,
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE + 1, "bold"),
            spacing1=8, spacing3=2,
        )
        self.overlay_text.tag_configure(
            "bold", foreground="#ffffff",
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE, "bold"),
        )
        self.overlay_text.tag_configure("normal", foreground=OVERLAY_FG_COLOR)

        # 渲染内容
        self._render_markdown(content)
        self.overlay_text.configure(state=tk.DISABLED)

        # 底部
        bottom = tk.Frame(self.overlay, bg="#0d0d1a")
        bottom.pack(fill=tk.X)
        tk.Label(
            bottom, text="点击按钮重新分析 | Gemini ✨",
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

    def _hide_overlay(self):
        """隐藏攻略窗口。"""
        if self.overlay:
            try:
                self.overlay.withdraw()
            except tk.TclError:
                pass
            self._overlay_visible = False

    def _on_show(self):
        """点击📋按钮：显示/隐藏攻略。"""
        if self.overlay:
            try:
                exists = self.overlay.winfo_exists()
            except (tk.TclError, RuntimeError):
                exists = False
            if not exists:
                # 窗口已被销毁，重建
                self.overlay = None
                self._overlay_visible = False
                if _last_result:
                    self._show_result(_last_result)
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
                    # Windows API 强制前台
                    try:
                        import ctypes
                        self.overlay.update_idletasks()
                        hwnd = int(self.overlay.frame(), 16)
                        ctypes.windll.user32.SetForegroundWindow(hwnd)
                    except Exception:
                        pass
                except tk.TclError:
                    # 窗口状态异常，重建
                    self.overlay = None
                    self._overlay_visible = False
                    if _last_result:
                        self._show_result(_last_result)
        elif _last_result:
            # overlay 为 None 但有历史结果，重建
            self._show_result(_last_result)

    # ==================== Markdown 渲染 ====================
    def _render_markdown(self, text: str):
        import re
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("## "):
                self.overlay_text.insert(tk.END, stripped[3:] + "\n", "heading")
            elif stripped.startswith("### "):
                self.overlay_text.insert(tk.END, stripped[4:] + "\n", "subheading")
            elif stripped.startswith("# "):
                self.overlay_text.insert(tk.END, stripped[2:] + "\n", "heading")
            elif stripped.startswith("- ") or stripped.startswith("* "):
                self.overlay_text.insert(tk.END, "  • ")
                self._insert_bold(stripped[2:] + "\n", "normal")
            elif re.match(r"^\d+\.\s", stripped):
                idx = stripped.index(".") + 1
                self.overlay_text.insert(tk.END, "  " + stripped[:idx] + " ")
                self._insert_bold(stripped[idx:].strip() + "\n", "normal")
            elif stripped.startswith("**") and stripped.endswith("**"):
                self.overlay_text.insert(tk.END, stripped[2:-2] + "\n", "bold")
            elif stripped == "":
                self.overlay_text.insert(tk.END, "\n")
            else:
                self._insert_bold(stripped + "\n", "normal")

    def _insert_bold(self, text: str, base_tag: str):
        import re
        parts = re.split(r"(\*\*.*?\*\*)", text)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                self.overlay_text.insert(tk.END, part[2:-2], "bold")
            else:
                self.overlay_text.insert(tk.END, part, base_tag)

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
        """在后台线程中注册 Ctrl+F12 全局热键，用于切换攻略窗口。"""
        def _listener():
            try:
                user32 = ctypes.windll.user32
                # 热键 ID
                HOTKEY_ID_TOGGLE = 1
                # 修饰键: MOD_CONTROL = 0x0002
                MOD_CONTROL = 0x0002
                # VK_F12 = 0x7B
                VK_F12 = 0x7B

                if not user32.RegisterHotKey(None, HOTKEY_ID_TOGGLE, MOD_CONTROL, VK_F12):
                    log.warning("⚠️ 注册全局热键 Ctrl+F12 失败（可能已被占用）")
                    return

                log.info("✅ 全局热键 Ctrl+F12 已注册（切换攻略窗口）")

                msg = ctypes.wintypes.MSG()
                while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                    if msg.message == 0x0312:  # WM_HOTKEY
                        if msg.wParam == HOTKEY_ID_TOGGLE:
                            log.debug("🔑 热键 Ctrl+F12 触发")
                            try:
                                self.root.after(0, self._on_show)
                            except Exception:
                                pass

                user32.UnregisterHotKey(None, HOTKEY_ID_TOGGLE)
            except Exception as e:
                log.error(f"热键线程异常: {e}")

        t = threading.Thread(target=_listener, daemon=True, name="HotkeyListener")
        t.start()

    def run(self):
        self.root.mainloop()


def main():
    print("=" * 50)
    print("⚔️  ARAM 海克斯大乱斗 智能助手")
    print("=" * 50)

    print(f"\n📌 屏幕左上角 [⚔️ 分析 | 📋 攻略] 按钮")
    print("   ⚔️ 分析 → 截图 + AI 分析（自动识别你的英雄）")
    print("   📋 攻略 → 重新打开/隐藏攻略")
    print("   右键拖拽移动按钮位置")
    print("\n⌨️  全局热键: Ctrl+F12 → 切换显示/隐藏攻略（游戏中也可用）")
    print("\n🔄 无需重启！每局开始时点“⚔️ 分析”即可重新分析")
    print("   AI 会通过加载界面中金色名字自动识别你的英雄")
    print(f"📝 日志: {LOG_FILE}")
    print("❤️  关闭命令行窗口退出")
    print("=" * 50 + "\n")

    log.info("ARAM 助手已启动")
    app = App()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n👋 已退出")
        sys.exit(0)


if __name__ == "__main__":
    main()
