# -*- coding: utf-8 -*-
"""Windows 控制台窗口显隐控制。

仅在 Windows 下生效。非 Windows / 无 console 关联（pythonw.exe / 已 FreeConsole）
时静默 no-op。

用三重手段确保「真隐藏」而不是「最小化」：
1. 去掉任务栏样式（WS_EX_APPWINDOW → WS_EX_TOOLWINDOW）
2. ShowWindow(SW_HIDE) —— 经典隐藏
3. SetWindowPos(SWP_HIDEWINDOW) —— 兜底强制隐藏
这些组合能避开 Windows Terminal / 某些 conhost 把 SW_HIDE 降级为最小化的情况。
"""

import logging
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


def set_console_visible(visible: bool) -> None:
    """显示或隐藏当前进程关联的 DOS / cmd / Windows Terminal 窗口。"""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        hwnd = kernel32.GetConsoleWindow()
        if not hwnd:
            return

        if visible:
            # 恢复任务栏样式
            ex = user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, _GWL_EXSTYLE,
                                  (ex & ~_WS_EX_TOOLWINDOW) | _WS_EX_APPWINDOW)
            user32.ShowWindow(hwnd, _SW_SHOW)
            user32.SetWindowPos(
                hwnd, 0, 0, 0, 0, 0,
                _SWP_NOMOVE | _SWP_NOSIZE | _SWP_NOZORDER
                | _SWP_SHOWWINDOW | _SWP_FRAMECHANGED,
            )
        else:
            # 1) 先剥掉任务栏样式，防止任务栏残留
            ex = user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, _GWL_EXSTYLE,
                                  (ex | _WS_EX_TOOLWINDOW) & ~_WS_EX_APPWINDOW)
            # 2) 经典 SW_HIDE
            user32.ShowWindow(hwnd, _SW_HIDE)
            # 3) 兜底：SWP_HIDEWINDOW 强制窗口置隐藏（某些终端宿主会忽略 SW_HIDE）
            user32.SetWindowPos(
                hwnd, 0, 0, 0, 0, 0,
                _SWP_NOMOVE | _SWP_NOSIZE | _SWP_NOZORDER
                | _SWP_HIDEWINDOW | _SWP_FRAMECHANGED,
            )
        log.debug(f"[console] 切换成功: {'显示' if visible else '隐藏'}")
    except Exception as e:
        log.warning(f"[console] 切换控制台显隐失败: {e}")
