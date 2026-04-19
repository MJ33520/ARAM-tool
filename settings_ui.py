# -*- coding: utf-8 -*-
"""ARAM 助手 - ⚙️ 设置对话框

提供图形界面配置 LLM 提供商与界面语言，设置写入 ~/.aram_tool/settings.json。
配置修改后需要重启应用生效（config.py 在启动时读取一次，LLMClient 是模块级单例）。

写入文件使用 0600 权限（在 Unix 上生效；Windows 上无实际影响但不报错）。
"""

import json
import logging
import os
import tkinter as tk
from tkinter import ttk, messagebox

from config import (
    USER_SETTINGS_DIR, USER_SETTINGS_PATH, LANGUAGE,
    LLM_PROVIDER,
    GEMINI_API_KEY, GEMINI_MODEL, GEN_AI_ENDPOINT,
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_API_ENDPOINT,
    CUSTOM_API_KEY, CUSTOM_MODEL, CUSTOM_API_ENDPOINT,
)

log = logging.getLogger("ARAM")

# 本模块内的小型 i18n（不污染 lang.py 的大词表）
_I18N = {
    "zh": {
        "title": "⚙️ ARAM 助手 - 设置",
        "provider": "LLM 提供商",
        "language": "界面语言",
        "api_key": "API 密钥",
        "model": "模型名",
        "endpoint": "API 端点",
        "gemini_hint": "从 https://aistudio.google.com/apikey 获取，以 AIza 开头",
        "openai_hint": "兼容 OpenAI Chat Completions 协议的任何服务",
        "custom_hint": "自定义 POST JSON 后端（{model, prompt, temperature}）",
        "endpoint_optional": "（可选）代理端点",
        "save": "保存",
        "cancel": "取消",
        "show_key": "显示密钥",
        "restart_notice": "保存后需要重启应用才能生效。",
        "file_notice": "设置保存至本地文件（含密钥明文）：",
        "save_ok_title": "已保存",
        "save_ok_msg": "设置已写入：\n{path}\n\n请重启应用使修改生效。",
        "save_err_title": "保存失败",
    },
    "en": {
        "title": "⚙️ ARAM Tool - Settings",
        "provider": "LLM Provider",
        "language": "UI Language",
        "api_key": "API Key",
        "model": "Model",
        "endpoint": "API Endpoint",
        "gemini_hint": "Get from https://aistudio.google.com/apikey (starts with AIza)",
        "openai_hint": "Any service compatible with OpenAI Chat Completions",
        "custom_hint": "Custom POST JSON backend ({model, prompt, temperature})",
        "endpoint_optional": "(optional) proxy endpoint",
        "save": "Save",
        "cancel": "Cancel",
        "show_key": "Show key",
        "restart_notice": "A restart is required for changes to take effect.",
        "file_notice": "Settings are written locally (plaintext key):",
        "save_ok_title": "Saved",
        "save_ok_msg": "Settings written to:\n{path}\n\nPlease restart the app.",
        "save_err_title": "Save failed",
    },
}

PROVIDERS = ["gemini", "openai", "custom"]
LANGS = ["zh", "en"]


def _t(key: str) -> str:
    return _I18N.get(LANGUAGE, _I18N["zh"]).get(key, key)


def save_settings(data: dict) -> None:
    os.makedirs(USER_SETTINGS_DIR, exist_ok=True)
    tmp_path = USER_SETTINGS_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, USER_SETTINGS_PATH)
    try:
        os.chmod(USER_SETTINGS_PATH, 0o600)
    except Exception:
        pass  # Windows 上 chmod 基本无效，不报错


class SettingsDialog:
    """模态设置对话框。不访问任何网络，只读写本地 JSON。"""

    def __init__(self, parent: tk.Misc):
        self.parent = parent
        self.win = tk.Toplevel(parent)
        self.win.title(_t("title"))
        self.win.transient(parent)
        self.win.resizable(False, False)
        self.win.configure(bg="#1a1a2e")
        self.win.grab_set()

        # ========== 顶部：提供商 + 语言 ==========
        top = tk.Frame(self.win, bg="#1a1a2e")
        top.pack(fill=tk.X, padx=16, pady=(14, 6))

        tk.Label(top, text=_t("provider"), bg="#1a1a2e", fg="#e0e0e0",
                 font=("Microsoft YaHei UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.var_provider = tk.StringVar(value=LLM_PROVIDER if LLM_PROVIDER in PROVIDERS else "gemini")
        cb = ttk.Combobox(top, textvariable=self.var_provider, values=PROVIDERS,
                          state="readonly", width=12)
        cb.grid(row=0, column=1, sticky="w")
        cb.bind("<<ComboboxSelected>>", lambda _e: self._refresh_fields())

        tk.Label(top, text=_t("language"), bg="#1a1a2e", fg="#e0e0e0",
                 font=("Microsoft YaHei UI", 10, "bold")).grid(row=0, column=2, sticky="w", padx=(18, 8))
        self.var_language = tk.StringVar(value=LANGUAGE if LANGUAGE in LANGS else "zh")
        ttk.Combobox(top, textvariable=self.var_language, values=LANGS,
                     state="readonly", width=6).grid(row=0, column=3, sticky="w")

        # ========== 中部：provider 相关字段（动态） ==========
        self.body = tk.Frame(self.win, bg="#1a1a2e")
        self.body.pack(fill=tk.X, padx=16, pady=(4, 10))

        # 三组字段独立变量，切换时不丢失已输入内容
        self.vars = {
            "gemini_api_key": tk.StringVar(value=GEMINI_API_KEY),
            "gemini_model": tk.StringVar(value=GEMINI_MODEL),
            "gen_ai_endpoint": tk.StringVar(value=GEN_AI_ENDPOINT),
            "openai_api_key": tk.StringVar(value=OPENAI_API_KEY),
            "openai_model": tk.StringVar(value=OPENAI_MODEL),
            "openai_api_endpoint": tk.StringVar(value=OPENAI_API_ENDPOINT),
            "custom_api_key": tk.StringVar(value=CUSTOM_API_KEY),
            "custom_model": tk.StringVar(value=CUSTOM_MODEL),
            "custom_api_endpoint": tk.StringVar(value=CUSTOM_API_ENDPOINT),
        }
        self.show_key = tk.BooleanVar(value=False)
        self._key_entries: list[tk.Entry] = []

        self._refresh_fields()

        # ========== 底部：提示 + 按钮 ==========
        notice = tk.Frame(self.win, bg="#1a1a2e")
        notice.pack(fill=tk.X, padx=16, pady=(0, 6))
        tk.Label(notice, text="ⓘ " + _t("restart_notice"),
                 bg="#1a1a2e", fg="#ffaa00",
                 font=("Microsoft YaHei UI", 9)).pack(anchor="w")
        tk.Label(notice, text=_t("file_notice") + "\n" + USER_SETTINGS_PATH,
                 bg="#1a1a2e", fg="#888899", justify="left",
                 font=("Microsoft YaHei UI", 8)).pack(anchor="w", pady=(2, 0))

        btns = tk.Frame(self.win, bg="#1a1a2e")
        btns.pack(fill=tk.X, padx=16, pady=(6, 14))
        tk.Checkbutton(btns, text=_t("show_key"), variable=self.show_key,
                       command=self._toggle_key_visibility,
                       bg="#1a1a2e", fg="#e0e0e0", selectcolor="#2a2a4e",
                       activebackground="#1a1a2e", activeforeground="#e0e0e0",
                       font=("Microsoft YaHei UI", 9)).pack(side=tk.LEFT)
        tk.Button(btns, text=_t("cancel"), command=self.win.destroy,
                  bg="#2a2a4e", fg="#e0e0e0", activebackground="#3a3a5e",
                  activeforeground="#ffffff", relief=tk.FLAT, padx=14, pady=4,
                  cursor="hand2").pack(side=tk.RIGHT)
        tk.Button(btns, text=_t("save"), command=self._on_save,
                  bg="#00d4ff", fg="#0a0a1e", activebackground="#33e0ff",
                  activeforeground="#0a0a1e", relief=tk.FLAT, padx=14, pady=4,
                  cursor="hand2", font=("Microsoft YaHei UI", 10, "bold")).pack(side=tk.RIGHT, padx=(0, 8))

        # 居中
        self.win.update_idletasks()
        w, h = self.win.winfo_width(), self.win.winfo_height()
        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        self.win.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    # ---------- 动态字段 ----------
    def _add_row(self, label_text: str, var: tk.StringVar, row: int, is_key: bool = False, hint: str = None):
        tk.Label(self.body, text=label_text, bg="#1a1a2e", fg="#e0e0e0",
                 font=("Microsoft YaHei UI", 10)).grid(row=row, column=0, sticky="e", padx=(0, 8), pady=3)
        entry = tk.Entry(self.body, textvariable=var, width=42,
                         bg="#2a2a4e", fg="#ffffff", insertbackground="#ffffff",
                         relief=tk.FLAT, font=("Microsoft YaHei UI", 10))
        if is_key:
            entry.configure(show="*")
            self._key_entries.append(entry)
        entry.grid(row=row, column=1, sticky="w", pady=3)
        if hint:
            tk.Label(self.body, text=hint, bg="#1a1a2e", fg="#888899",
                     font=("Microsoft YaHei UI", 8)).grid(row=row + 1, column=1, sticky="w", pady=(0, 4))

    def _refresh_fields(self):
        for w in self.body.winfo_children():
            w.destroy()
        self._key_entries = []

        p = self.var_provider.get()
        if p == "gemini":
            self._add_row(_t("api_key"), self.vars["gemini_api_key"], 0, is_key=True, hint=_t("gemini_hint"))
            self._add_row(_t("model"), self.vars["gemini_model"], 2)
            self._add_row(_t("endpoint") + " " + _t("endpoint_optional"),
                          self.vars["gen_ai_endpoint"], 3)
        elif p == "openai":
            self._add_row(_t("api_key"), self.vars["openai_api_key"], 0, is_key=True, hint=_t("openai_hint"))
            self._add_row(_t("model"), self.vars["openai_model"], 2)
            self._add_row(_t("endpoint"), self.vars["openai_api_endpoint"], 3)
        elif p == "custom":
            self._add_row(_t("api_key"), self.vars["custom_api_key"], 0, is_key=True, hint=_t("custom_hint"))
            self._add_row(_t("model"), self.vars["custom_model"], 2)
            self._add_row(_t("endpoint"), self.vars["custom_api_endpoint"], 3)

        self._toggle_key_visibility()

    def _toggle_key_visibility(self):
        show_char = "" if self.show_key.get() else "*"
        for e in self._key_entries:
            e.configure(show=show_char)

    # ---------- 保存 ----------
    def _on_save(self):
        data = {
            "llm_provider": self.var_provider.get(),
            "language": self.var_language.get(),
            "gemini_api_key": self.vars["gemini_api_key"].get().strip(),
            "gemini_model": self.vars["gemini_model"].get().strip(),
            "gen_ai_endpoint": self.vars["gen_ai_endpoint"].get().strip(),
            "openai_api_key": self.vars["openai_api_key"].get().strip(),
            "openai_model": self.vars["openai_model"].get().strip(),
            "openai_api_endpoint": self.vars["openai_api_endpoint"].get().strip(),
            "custom_api_key": self.vars["custom_api_key"].get().strip(),
            "custom_model": self.vars["custom_model"].get().strip(),
            "custom_api_endpoint": self.vars["custom_api_endpoint"].get().strip(),
        }
        try:
            save_settings(data)
            log.info(f"[设置] 已写入 {USER_SETTINGS_PATH}")
            messagebox.showinfo(
                _t("save_ok_title"),
                _t("save_ok_msg").format(path=USER_SETTINGS_PATH),
                parent=self.win,
            )
            self.win.destroy()
        except Exception as e:
            log.error(f"[设置] 保存失败: {e}")
            messagebox.showerror(_t("save_err_title"), str(e), parent=self.win)


def open_settings_dialog(parent: tk.Misc) -> None:
    SettingsDialog(parent)
