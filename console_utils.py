# -*- coding: utf-8 -*-
"""Windows 控制台窗口显隐控制。

仅在 Windows 下生效：调用 kernel32.GetConsoleWindow() + user32.ShowWindow()。
其它平台或无 console 关联（例如用 pythonw.exe 启动）时静默 no-op。
"""

import logging
import sys

log = logging.getLogger("ARAM")

_SW_HIDE = 0
_SW_SHOW = 5


def set_console_visible(visible: bool) -> None:
    """隐藏或显示当前进程关联的 DOS / cmd 窗口。"""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if not hwnd:
            return  # 无 console 关联（pythonw / GUI 启动）
        ctypes.windll.user32.ShowWindow(hwnd, _SW_SHOW if visible else _SW_HIDE)
        log.debug(f"[console] 已切换控制台显示: {'显示' if visible else '隐藏'}")
    except Exception as e:
        log.warning(f"[console] 切换控制台显隐失败: {e}")
