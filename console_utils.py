# -*- coding: utf-8 -*-
"""Windows 控制台（DOS / cmd / Windows Terminal）显隐控制。

非 Windows 或无 console 关联（pythonw.exe）时静默 no-op。

策略：
- visible=True：恢复任务栏样式 + ShowWindow(SW_SHOW) + SetWindowPos(SWP_SHOWWINDOW)
- visible=False：三级递进尝试，直到窗口不可见
  1. WS_EX_TOOLWINDOW + SW_HIDE + SWP_HIDEWINDOW（普通情况下够用）
  2. 如果上一步后窗口仍可见（Windows Terminal / 某些 conhost 会把 SW_HIDE
     降级为最小化）→ 重定向 stdout/stderr 到 NUL，FreeConsole() 彻底断开
     控制台关联

FreeConsole 一旦调用，本进程将永久失去控制台访问；后续再点开「显示控制台」
只能通过重启应用恢复。我们在日志里记录这一点，让用户知道。
"""

import logging
import os
import sys

log = logging.getLogger("ARAM")

# ShowWindow
_SW_HIDE = 0
_SW_SHOW = 5

# GetWindowLong / SetWindowLong
_GWL_EXSTYLE = -20
_WS_EX_TOOLWINDOW = 0x00000080
_WS_EX_APPWINDOW = 0x00040000

# SetWindowPos flags
_SWP_NOSIZE = 0x0001
_SWP_NOMOVE = 0x0002
_SWP_NOZORDER = 0x0004
_SWP_HIDEWINDOW = 0x0080
_SWP_SHOWWINDOW = 0x0040
_SWP_FRAMECHANGED = 0x0020

# 一旦执行过 FreeConsole，置 True；防止重复 Free 抛错
_console_freed = False


def _is_windows() -> bool:
    return sys.platform == "win32"


def _redirect_stdio_to_null() -> None:
    """断开控制台前把 stdout/stderr 指到 NUL，避免后续 print() 写到已关闭的 fd 报错。"""
    try:
        nul = open(os.devnull, "w", encoding="utf-8", errors="replace")
        sys.stdout = nul
        sys.stderr = nul
    except Exception as e:
        log.debug(f"[console] 重定向 stdio 失败（不致命）: {e}")


def set_console_visible(visible: bool) -> None:
    """显示或隐藏当前进程关联的 DOS 窗口。"""
    global _console_freed
    if not _is_windows():
        return
    if _console_freed:
        # 已彻底断开，无法再恢复；记日志即可
        if visible:
            log.info("[console] 控制台已断开（FreeConsole），显示需重启应用")
        return
    try:
        import ctypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        hwnd = kernel32.GetConsoleWindow()
        if not hwnd:
            return

        if visible:
            ex = user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, _GWL_EXSTYLE,
                                  (ex & ~_WS_EX_TOOLWINDOW) | _WS_EX_APPWINDOW)
            user32.ShowWindow(hwnd, _SW_SHOW)
            user32.SetWindowPos(
                hwnd, 0, 0, 0, 0, 0,
                _SWP_NOMOVE | _SWP_NOSIZE | _SWP_NOZORDER
                | _SWP_SHOWWINDOW | _SWP_FRAMECHANGED,
            )
            log.debug("[console] 已显示")
            return

        # ===== 隐藏路径 =====
        # 1. 剥任务栏样式
        ex = user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, _GWL_EXSTYLE,
                              (ex | _WS_EX_TOOLWINDOW) & ~_WS_EX_APPWINDOW)
        # 2. SW_HIDE
        user32.ShowWindow(hwnd, _SW_HIDE)
        # 3. SWP_HIDEWINDOW 兜底
        user32.SetWindowPos(
            hwnd, 0, 0, 0, 0, 0,
            _SWP_NOMOVE | _SWP_NOSIZE | _SWP_NOZORDER
            | _SWP_HIDEWINDOW | _SWP_FRAMECHANGED,
        )

        # 检查是否真的隐藏了
        if not user32.IsWindowVisible(hwnd):
            log.debug("[console] 已 SW_HIDE + SWP_HIDEWINDOW")
            return

        # 4. 终极手段：FreeConsole。先重定向 stdio 防崩溃。
        log.info("[console] 常规隐藏无效（可能是 Windows Terminal），"
                 "使用 FreeConsole 断开控制台")
        _redirect_stdio_to_null()
        ok = bool(kernel32.FreeConsole())
        if ok:
            _console_freed = True
            log.info("[console] 已 FreeConsole，控制台已彻底断开")
        else:
            log.warning("[console] FreeConsole 调用失败")
    except Exception as e:
        log.warning(f"[console] 切换控制台显隐失败: {e}")
