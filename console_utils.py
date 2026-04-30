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


def _rebind_stdio_to_console() -> None:
    """AllocConsole 后重新把 stdin/stdout/stderr 绑到新分配的控制台。"""
    try:
        sys.stdout = open("CONOUT$", "w", encoding="utf-8", errors="replace", buffering=1)
        sys.stderr = open("CONOUT$", "w", encoding="utf-8", errors="replace", buffering=1)
    except Exception as e:
        log.debug(f"[console] 重绑 stdout/stderr 到 CONOUT$ 失败: {e}")
    try:
        sys.stdin = open("CONIN$", "r", encoding="utf-8", errors="replace")
    except Exception:
        pass  # stdin 失败不致命


def ensure_console_allocated() -> bool:
    """若当前进程无控制台（--noconsole 打包 / pythonw 启动），分配一个并绑定 stdio。

    返回是否分配了新控制台（已有则返回 False）。
    AllocConsole 之后强制 ShowWindow + SetWindowPos，因为有些 Windows 终端
    宿主会把新分配的控制台启动为隐藏状态。
    """
    global _console_freed
    if not _is_windows():
        return False
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        if kernel32.GetConsoleWindow():
            return False  # 已有控制台
        if not kernel32.AllocConsole():
            log.warning("[console] AllocConsole 返回 0（失败）")
            return False
        _console_freed = False
        _rebind_stdio_to_console()

        # 强制让新分配的窗口可见并提到前台
        hwnd = kernel32.GetConsoleWindow()
        if hwnd:
            # 先恢复任务栏样式
            ex = user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, _GWL_EXSTYLE,
                                  (ex & ~_WS_EX_TOOLWINDOW) | _WS_EX_APPWINDOW)
            user32.ShowWindow(hwnd, _SW_SHOW)
            user32.SetWindowPos(
                hwnd, 0, 0, 0, 0, 0,
                _SWP_NOMOVE | _SWP_NOSIZE | _SWP_NOZORDER
                | _SWP_SHOWWINDOW | _SWP_FRAMECHANGED,
            )
        log.debug("[console] 已 AllocConsole + ShowWindow")
        return True
    except Exception as e:
        log.warning(f"[console] AllocConsole 失败: {e}")
    return False


def bootstrap_from_settings() -> None:
    """启动时极早调用：不走 config，手工读 settings.json + env 决定是否分配控制台。

    打包版（--noconsole）默认无控制台，若用户设置 show_console=True，
    此函数会在 main.py 的其它 import 之前 AllocConsole，让启动期日志
    能正常打印到新控制台。
    """
    if not _is_windows():
        return
    try:
        import ctypes
        import json as _json
        kernel32 = ctypes.windll.kernel32
        if kernel32.GetConsoleWindow():
            return  # 源码运行，cmd 已提供控制台

        # show_console 默认 True；env > settings.json > default
        show = True
        path = os.path.join(os.path.expanduser("~"), ".aram_tool", "settings.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = _json.load(f)
                    if isinstance(data, dict) and "show_console" in data:
                        show = bool(data["show_console"])
            except Exception:
                pass
        env = os.environ.get("SHOW_CONSOLE")
        if env is not None and env.strip():
            show = env.strip().lower() in ("true", "1", "yes", "on")

        if show:
            ensure_console_allocated()
    except Exception as e:
        # 启动期不要崩，静默降级
        try:
            log.warning(f"[console] bootstrap 失败: {e}")
        except Exception:
            pass


def set_console_visible(visible: bool) -> None:
    """显示或隐藏当前进程关联的 DOS 窗口。

    visible=True 时若无控制台（比如 --noconsole 打包的 exe）会先 AllocConsole。
    FreeConsole 之后，再次 set_console_visible(True) 只能在重启后生效。
    """
    global _console_freed
    if not _is_windows():
        return
    try:
        import ctypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        hwnd = kernel32.GetConsoleWindow()

        if visible:
            if not hwnd:
                # 打包版 / pythonw 启动：按需分配
                if _console_freed:
                    log.info("[console] 控制台已 FreeConsole 断开，需重启应用恢复")
                    return
                if ensure_console_allocated():
                    hwnd = kernel32.GetConsoleWindow()
                if not hwnd:
                    return  # 还是没有，放弃
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
        if not hwnd:
            return  # 本来就没有，无需隐藏
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

        # 4. 终极手段：FreeConsole
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
