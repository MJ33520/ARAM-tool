# -*- coding: utf-8 -*-
"""ARAM 助手 - 悬浮窗 UI 模块"""

import tkinter as tk
from tkinter import font as tkfont
import re
import threading
from config import (
    OVERLAY_BG_COLOR,
    OVERLAY_FG_COLOR,
    OVERLAY_ACCENT_COLOR,
    OVERLAY_TITLE_COLOR,
    OVERLAY_WIDTH,
    OVERLAY_MAX_HEIGHT,
    OVERLAY_FONT_FAMILY,
    OVERLAY_FONT_SIZE,
    OVERLAY_OPACITY,
    TOGGLE_HOTKEY,
)


class OverlayWindow:
    """半透明置顶悬浮窗，用于显示分析结果。支持 F10 一键切换显示/隐藏。"""

    def __init__(self):
        self.root = None
        self.text_widget = None
        self._drag_data = {"x": 0, "y": 0}
        self._visible = False
        self._content = ""           # 缓存当前内容
        self._title = ""             # 缓存当前标题
        self._tk_thread = None       # tkinter 运行线程
        self._ready_event = threading.Event()  # 窗口就绪信号

    def _create_window(self, content: str, title: str):
        """在独立线程中创建 tkinter 窗口。"""
        self.root = tk.Tk()
        self.root.title("ARAM Assistant")

        # 窗口配置
        self.root.configure(bg=OVERLAY_BG_COLOR)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", OVERLAY_OPACITY)
        self.root.overrideredirect(True)  # 无边框

        # 计算窗口位置（屏幕右上角）
        screen_w = self.root.winfo_screenwidth()
        x_pos = screen_w - OVERLAY_WIDTH - 20
        y_pos = 40

        # ==================== 标题栏 ====================
        title_frame = tk.Frame(self.root, bg="#0d0d1a", cursor="fleur")
        title_frame.pack(fill=tk.X)

        title_frame.bind("<Button-1>", self._start_drag)
        title_frame.bind("<B1-Motion>", self._on_drag)

        title_label = tk.Label(
            title_frame,
            text=title,
            bg="#0d0d1a",
            fg=OVERLAY_TITLE_COLOR,
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE + 2, "bold"),
            padx=12, pady=8,
        )
        title_label.pack(side=tk.LEFT)
        title_label.bind("<Button-1>", self._start_drag)
        title_label.bind("<B1-Motion>", self._on_drag)

        # 关闭按钮
        close_btn = tk.Label(
            title_frame, text="  ✕  ", bg="#0d0d1a", fg="#ff4757",
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE + 2, "bold"), cursor="hand2",
        )
        close_btn.pack(side=tk.RIGHT, padx=4)
        close_btn.bind("<Button-1>", lambda e: self.toggle_visibility())
        close_btn.bind("<Enter>", lambda e: close_btn.configure(bg="#2a0a0f"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(bg="#0d0d1a"))

        # 提示
        hint_label = tk.Label(
            title_frame, text=f"Esc 隐藏 | 可拖拽",
            bg="#0d0d1a", fg="#666680",
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE - 2),
        )
        hint_label.pack(side=tk.RIGHT, padx=8)

        # 分隔线
        separator = tk.Frame(self.root, bg=OVERLAY_ACCENT_COLOR, height=2)
        separator.pack(fill=tk.X)

        # ==================== 内容区域 ====================
        content_frame = tk.Frame(self.root, bg=OVERLAY_BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        scrollbar = tk.Scrollbar(content_frame, orient=tk.VERTICAL, bg=OVERLAY_BG_COLOR)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget = tk.Text(
            content_frame,
            bg=OVERLAY_BG_COLOR, fg=OVERLAY_FG_COLOR,
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE),
            wrap=tk.WORD, padx=14, pady=10,
            borderwidth=0, highlightthickness=0,
            yscrollcommand=scrollbar.set, cursor="arrow",
            selectbackground="#2a2a4e", selectforeground="#ffffff",
            spacing1=2, spacing3=2,
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_widget.yview)

        # 文本样式
        self.text_widget.tag_configure(
            "heading", foreground=OVERLAY_TITLE_COLOR,
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE + 3, "bold"),
            spacing1=12, spacing3=4,
        )
        self.text_widget.tag_configure(
            "subheading", foreground=OVERLAY_ACCENT_COLOR,
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE + 1, "bold"),
            spacing1=8, spacing3=2,
        )
        self.text_widget.tag_configure(
            "bold", foreground="#ffffff",
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE, "bold"),
        )
        self.text_widget.tag_configure(
            "bullet", foreground="#b0b0cc", lmargin1=20, lmargin2=32,
        )
        self.text_widget.tag_configure("normal", foreground=OVERLAY_FG_COLOR)

        # 渲染内容
        self._render_markdown(content)
        self.text_widget.configure(state=tk.DISABLED)

        # ==================== 底部状态栏 ====================
        bottom_frame = tk.Frame(self.root, bg="#0d0d1a")
        bottom_frame.pack(fill=tk.X)

        status_label = tk.Label(
            bottom_frame,
            text=f"点击按钮重新分析 | Gemini ✨",
            bg="#0d0d1a", fg="#444460",
            font=(OVERLAY_FONT_FAMILY, OVERLAY_FONT_SIZE - 2), pady=4,
        )
        status_label.pack()

        # 快捷键
        self.root.bind("<Escape>", lambda e: self.toggle_visibility())

        # 窗口大小和位置
        self.root.update_idletasks()
        content_height = min(self.text_widget.winfo_reqheight() + 80, OVERLAY_MAX_HEIGHT)
        self.root.geometry(f"{OVERLAY_WIDTH}x{content_height}+{x_pos}+{y_pos}")
        self.root.configure(highlightbackground=OVERLAY_ACCENT_COLOR, highlightthickness=1)

        self._visible = True
        self._ready_event.set()  # 通知窗口已就绪

        # 强制置顶（Windows API）
        try:
            import ctypes
            hwnd = int(self.root.frame(), 16) if hasattr(self.root, 'frame') else None
            if hwnd:
                ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass

        # 定时刷新置顶（防止被全屏游戏遮挡）
        def _keep_topmost():
            try:
                if self.root and self._visible:
                    self.root.lift()
                    self.root.attributes("-topmost", True)
                    self.root.after(3000, _keep_topmost)
            except Exception:
                pass
        self.root.after(1000, _keep_topmost)

        self.root.mainloop()

        # mainloop 退出后清理
        self.root = None
        self.text_widget = None
        self._visible = False
        self._ready_event.clear()

    def show(self, content: str, title: str = "⚔️ ARAM 助手 - 阵容分析"):
        """显示悬浮窗。如果已有窗口则销毁重建。"""
        self._content = content
        self._title = title

        # 如果已有窗口在运行，先销毁
        self._destroy_existing()
        self._ready_event.clear()

        # 在新线程中创建窗口
        self._tk_thread = threading.Thread(
            target=self._create_window, args=(content, title), daemon=True,
        )
        self._tk_thread.start()

        # 等待窗口就绪
        self._ready_event.wait(timeout=5)

    def toggle_visibility(self):
        """切换悬浮窗的显示/隐藏状态（线程安全）。"""
        if not self.root:
            return

        def _toggle():
            try:
                if self._visible:
                    self.root.withdraw()
                    self._visible = False
                else:
                    self.root.deiconify()
                    self.root.lift()
                    self.root.attributes("-topmost", True)
                    self._visible = True
            except Exception:
                pass

        try:
            self.root.after(0, _toggle)
        except Exception:
            pass

    def _render_markdown(self, text: str):
        """将简单的 Markdown 文本渲染到 Text 控件中。"""
        lines = text.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## "):
                self.text_widget.insert(tk.END, stripped[3:] + "\n", "heading")
            elif stripped.startswith("### "):
                self.text_widget.insert(tk.END, stripped[4:] + "\n", "subheading")
            elif stripped.startswith("# "):
                self.text_widget.insert(tk.END, stripped[2:] + "\n", "heading")
            elif stripped.startswith("- ") or stripped.startswith("* "):
                content = stripped[2:]
                self._insert_with_bold("  • " + content + "\n", "bullet")
            elif re.match(r"^\d+\.\s", stripped):
                self._insert_with_bold("  " + stripped + "\n", "bullet")
            elif stripped.startswith("**") and stripped.endswith("**"):
                self.text_widget.insert(tk.END, stripped.strip("*") + "\n", "bold")
            elif stripped == "":
                self.text_widget.insert(tk.END, "\n")
            else:
                self._insert_with_bold(stripped + "\n", "normal")

    def _insert_with_bold(self, text: str, base_tag: str):
        """处理文本中的 **粗体** 标记。"""
        parts = re.split(r"(\*\*.*?\*\*)", text)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                self.text_widget.insert(tk.END, part[2:-2], "bold")
            else:
                self.text_widget.insert(tk.END, part, base_tag)

    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag(self, event):
        if self.root:
            x = self.root.winfo_x() + event.x - self._drag_data["x"]
            y = self.root.winfo_y() + event.y - self._drag_data["y"]
            self.root.geometry(f"+{x}+{y}")

    def hide(self):
        """隐藏窗口（不销毁，避免影响其他 tkinter 窗口）。"""
        try:
            if self.root and self._visible:
                self.root.withdraw()
                self._visible = False
        except Exception:
            pass

    def _destroy_existing(self):
        """安全关闭已有窗口。"""
        try:
            if self.root:
                self.root.quit()  # 退出 mainloop
                import time; time.sleep(0.1)
                try:
                    self.root.destroy()
                except Exception:
                    pass
                self.root = None
                self.text_widget = None
                self._visible = False
        except Exception:
            self.root = None
            self.text_widget = None
            self._visible = False


# 全局单例
_overlay = OverlayWindow()


def show_overlay(content: str, title: str = "⚔️ ARAM 助手 - 阵容分析"):
    """对外接口：显示悬浮窗。"""
    _overlay.show(content, title)


def hide_overlay():
    """对外接口：隐藏悬浮窗。"""
    _overlay.hide()


def toggle_overlay():
    """对外接口：切换悬浮窗显示/隐藏。"""
    _overlay.toggle_visibility()


if __name__ == "__main__":
    test_content = """## 📋 阵容识别

**我方阵容**: 亚索、拉克丝、盲僧、莫甘娜、金克丝
**敌方阵容**: 提莫、安妮、德莱文、锤石、瑟庄妮

## ⭐ 我的英雄详细攻略 (亚索)

- **海克斯强化符文推荐**：
  - 🥇 利刃华尔兹 — 突进 + 不可选取，完美配合亚索的近战打法
  - 🥈 珠光护手 — 技能可以暴击，Q 技能收益极高
  - 🥉 玻璃大炮 — 减少生命值换取真伤，适合自信操作
  - 4. 最终形态 — 大招后获得护盾和吸血，增强生存
- **出装**: 多兰之刃 → 狂战士胫甲 → 无尽之刃 → 不朽盾弓 → 春哥甲
- **技能加点**: Q > E > W，主 Q 副 E
- **召唤师技能**: 闪现 + 屏障（或用利刃华尔兹替代屏障）
- **打法**: 利用风墙挡住德莱文的斧头和安妮的 Q，等瑟庄妮 R 交了再进场

## 🗡️ 队友出装与符文推荐

- **拉克丝**: 符文推荐：炼狱导管、精准狙击手、冰寒 | 法师之靴 → 卢登 → 灭世者死帽
- **盲僧**: 符文推荐：利刃华尔兹、歌利亚巨人、巨像的勇气 | 铁板靴 → 渴血战斧 → 黑切
- **莫甘娜**: 符文推荐：炼狱导管、蛋白粉奶昔、最终形态 | 法师之靴 → 中娅 → 卢登
- **金克丝**: 符文推荐：火力全开、连拨击锤、珠光护手 | 狂战士胫甲 → 无尽 → 急速火炮

## 🎯 策略建议

- 3 级和 7 级符文选择后是我方的 power spike，可以主动开团
- 注意规避瑟庄妮的 R 大招开团，保持分散站位
- 后期以金克丝和亚索为主要输出，利用强化符文的加成打出优势
"""
    show_overlay(test_content)
