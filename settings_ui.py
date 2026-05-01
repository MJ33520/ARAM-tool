# -*- coding: utf-8 -*-
"""ARAM 助手 - ⚙️ 设置对话框

图形界面配置 LLM 提供商与界面语言，设置写入 ~/.aram_tool/settings.json。

保存后行为：
- LLM provider / key / model / endpoint 变更 → 热重载，即时生效（无需重启）
- 语言变更 → 需要重启（按钮 / 文案已渲染到 tkinter 控件，逐个 configure 成本过高）

模型名字段支持「🔄」一键从对应 provider 的 /models 端点拉取可用列表
（Gemini / OpenAI 兼容均支持；自定义后端无标准 API，保留手填）。
"""

import json
import logging
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import config
import llm_client
from config import (
    USER_SETTINGS_DIR, USER_SETTINGS_PATH, LANGUAGE, LOG_FILE,
    LLM_PROVIDER,
    GEMINI_API_KEY, GEMINI_MODEL, GEN_AI_ENDPOINT,
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_API_ENDPOINT,
    CUSTOM_API_KEY, CUSTOM_MODEL, CUSTOM_API_ENDPOINT,
)

log = logging.getLogger("ARAM")

# 本模块内的小型 i18n
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
        "fetch_models": "🔄",
        "fetching": "⏳",
        "fetch_tooltip": "拉取可用模型列表",
        "fetch_err_title": "拉取模型失败",
        "test": "🧪 测试",
        "testing": "⏳ 测试中...",
        "test_ok_title": "连接正常",
        "test_ok_msg": "✅ Provider / Model / Key 均可用\n延迟: {latency_ms} ms\n\n返回片段：\n{reply}",
        "test_err_title": "连接失败",
        "test_err_msg": "❌ 测试失败（延迟 {latency_ms} ms）\n\n{error}",
        "open_log": "📂 打开日志文件",
        "open_log_err": "无法打开日志文件",
        "apexlol_section": "🎲 ApexLol 数据缓存",
        "apexlol_desc": (
            "本地缓存所有英雄的海克斯符文方案与评级（来源：apexlol.info）。\n"
            "• AI 分析时会参考这些数据，避免推荐截图里没有的符文名；\n"
            "• 没填 LLM Key 时，✏️ 纠错按钮也能走「纯数据查表模式」给建议；\n"
            "• 缓存 7 天有效，过期会在启动时自动后台刷新。\n"
            "• 整个爬取约 60 秒，期间可继续游戏。"
        ),
        "apexlol_btn_update": "🔄 立即更新缓存",
        "apexlol_btn_updating": "⏳ 更新中…",
        "apexlol_status_loaded": "已缓存 {count} 英雄 / {age}h 前更新 / 剩余 {remaining}h",
        "apexlol_status_empty": "⚠️ 暂无本地缓存，建议立即更新",
        "apexlol_status_progress": "[{current}/{total}] 爬取: {name}",
        "restart_notice_lang": "语言变更需要重启应用才能生效；LLM 配置改动保存后立即生效。",
        "file_notice": "设置保存至本地文件（含密钥明文）：",
        "save_ok_title": "已保存",
        "save_ok_hot": "设置已保存并已生效，无需重启。\n\n{path}",
        "save_ok_lang_restart": "设置已保存。LLM 配置已生效；\n语言变更需重启应用。\n\n{path}",
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
        "fetch_models": "🔄",
        "fetching": "⏳",
        "fetch_tooltip": "Fetch available models",
        "fetch_err_title": "Fetch failed",
        "test": "🧪 Test",
        "testing": "⏳ Testing...",
        "test_ok_title": "Connection OK",
        "test_ok_msg": "✅ Provider / Model / Key all working\nLatency: {latency_ms} ms\n\nReply preview:\n{reply}",
        "test_err_title": "Connection failed",
        "test_err_msg": "❌ Test failed ({latency_ms} ms)\n\n{error}",
        "open_log": "📂 Open log file",
        "open_log_err": "Cannot open log file",
        "apexlol_section": "🎲 ApexLol data cache",
        "apexlol_desc": (
            "Local cache of every champion's hextech synergies and ratings (source: apexlol.info).\n"
            "• AI uses this data to avoid recommending augments that aren't on screen;\n"
            "• Without an LLM key, the ✏️ Fix button can fall back to data-only lookup;\n"
            "• Cache lives 7 days; auto-refreshes on startup when expired.\n"
            "• A full scrape takes ~60s; you can keep playing in the meantime."
        ),
        "apexlol_btn_update": "🔄 Update cache now",
        "apexlol_btn_updating": "⏳ Updating…",
        "apexlol_status_loaded": "Cached {count} champs / {age}h ago / {remaining}h left",
        "apexlol_status_empty": "⚠️ No local cache yet — update recommended",
        "apexlol_status_progress": "[{current}/{total}] Scraping: {name}",
        "restart_notice_lang": "Language change requires a restart; LLM changes apply instantly on save.",
        "file_notice": "Settings are written locally (plaintext key):",
        "save_ok_title": "Saved",
        "save_ok_hot": "Settings saved and applied — no restart needed.\n\n{path}",
        "save_ok_lang_restart": "Settings saved. LLM changes are live;\nlanguage change needs a restart.\n\n{path}",
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
    """模态设置对话框。保存后通过 config.reload() + llm_client.reset_client() 热生效。"""

    def __init__(self, parent: tk.Misc, app=None):
        self.parent = parent
        self.app = app  # 主 App 实例，用于触发数据缓存更新（None 时按钮禁用）
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
        self.body.pack(fill=tk.X, padx=16, pady=(8, 10))

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
        self._key_entries: list = []
        self._model_combo: ttk.Combobox = None
        self._fetch_btn: tk.Button = None

        self._refresh_fields()

        # ========== ApexLol 数据缓存区 ==========
        self._build_apexlol_section()

        # ========== 底部：提示 + 按钮 ==========
        notice = tk.Frame(self.win, bg="#1a1a2e")
        notice.pack(fill=tk.X, padx=16, pady=(0, 6))
        tk.Label(notice, text="ⓘ " + _t("restart_notice_lang"),
                 bg="#1a1a2e", fg="#ffaa00",
                 font=("Microsoft YaHei UI", 9)).pack(anchor="w")
        tk.Label(notice, text=_t("file_notice") + "\n" + USER_SETTINGS_PATH,
                 bg="#1a1a2e", fg="#888899", justify="left",
                 font=("Microsoft YaHei UI", 8)).pack(anchor="w", pady=(2, 0))

        # 打开日志文件入口（替代旧版 DOS 实时日志）
        tk.Button(notice, text=_t("open_log"), command=self._open_log_file,
                  bg="#1a1a2e", fg="#00d4ff", activebackground="#2a2a4e",
                  activeforeground="#33e0ff", relief=tk.FLAT, cursor="hand2",
                  font=("Microsoft YaHei UI", 9), borderwidth=0,
                  padx=0, pady=2).pack(anchor="w", pady=(4, 0))

        btns = tk.Frame(self.win, bg="#1a1a2e")
        btns.pack(fill=tk.X, padx=16, pady=(6, 14))
        tk.Checkbutton(btns, text=_t("show_key"), variable=self.show_key,
                       command=self._toggle_key_visibility,
                       bg="#1a1a2e", fg="#e0e0e0", selectcolor="#2a2a4e",
                       activebackground="#1a1a2e", activeforeground="#e0e0e0",
                       font=("Microsoft YaHei UI", 9)).pack(side=tk.LEFT)
        self.btn_test = tk.Button(btns, text=_t("test"), command=self._on_test,
                                  bg="#2a2a4e", fg="#ffaa00",
                                  activebackground="#3a3a5e",
                                  activeforeground="#ffcc44", relief=tk.FLAT,
                                  padx=10, pady=4, cursor="hand2",
                                  font=("Microsoft YaHei UI", 9, "bold"))
        self.btn_test.pack(side=tk.LEFT, padx=(12, 0))
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
    def _add_text_row(self, label_text: str, var: tk.StringVar, row: int,
                      is_key: bool = False, hint: str = None):
        tk.Label(self.body, text=label_text, bg="#1a1a2e", fg="#e0e0e0",
                 font=("Microsoft YaHei UI", 10)).grid(row=row, column=0, sticky="e", padx=(0, 8), pady=3)
        entry = tk.Entry(self.body, textvariable=var, width=42,
                         bg="#2a2a4e", fg="#ffffff", insertbackground="#ffffff",
                         relief=tk.FLAT, font=("Microsoft YaHei UI", 10))
        if is_key:
            entry.configure(show="*")
            self._key_entries.append(entry)
        entry.grid(row=row, column=1, sticky="w", pady=3, columnspan=2)
        if hint:
            tk.Label(self.body, text=hint, bg="#1a1a2e", fg="#888899",
                     font=("Microsoft YaHei UI", 8)).grid(
                row=row + 1, column=1, sticky="w", pady=(0, 4), columnspan=2)

    def _add_model_row(self, var: tk.StringVar, row: int, support_fetch: bool):
        """模型名字段：editable Combobox；支持 fetch 时带 🔄 按钮。"""
        tk.Label(self.body, text=_t("model"), bg="#1a1a2e", fg="#e0e0e0",
                 font=("Microsoft YaHei UI", 10)).grid(row=row, column=0, sticky="e", padx=(0, 8), pady=3)
        combo = ttk.Combobox(self.body, textvariable=var, values=[], width=34)
        combo.grid(row=row, column=1, sticky="w", pady=3)
        self._model_combo = combo

        if support_fetch:
            btn = tk.Button(self.body, text=_t("fetch_models"),
                            command=self._on_fetch_models,
                            bg="#2a2a4e", fg="#00d4ff", activebackground="#3a3a5e",
                            activeforeground="#ffffff", relief=tk.FLAT,
                            font=("Microsoft YaHei UI", 10, "bold"),
                            padx=8, pady=2, cursor="hand2")
            btn.grid(row=row, column=2, sticky="w", padx=(6, 0), pady=3)
            self._fetch_btn = btn

    def _refresh_fields(self):
        for w in self.body.winfo_children():
            w.destroy()
        self._key_entries = []
        self._model_combo = None
        self._fetch_btn = None

        p = self.var_provider.get()
        if p == "gemini":
            self._add_text_row(_t("api_key"), self.vars["gemini_api_key"], 0,
                               is_key=True, hint=_t("gemini_hint"))
            self._add_model_row(self.vars["gemini_model"], 2, support_fetch=True)
            self._add_text_row(_t("endpoint") + " " + _t("endpoint_optional"),
                               self.vars["gen_ai_endpoint"], 3)
        elif p == "openai":
            self._add_text_row(_t("api_key"), self.vars["openai_api_key"], 0,
                               is_key=True, hint=_t("openai_hint"))
            self._add_model_row(self.vars["openai_model"], 2, support_fetch=True)
            self._add_text_row(_t("endpoint"), self.vars["openai_api_endpoint"], 3)
        elif p == "custom":
            self._add_text_row(_t("api_key"), self.vars["custom_api_key"], 0,
                               is_key=True, hint=_t("custom_hint"))
            self._add_model_row(self.vars["custom_model"], 2, support_fetch=False)
            self._add_text_row(_t("endpoint"), self.vars["custom_api_endpoint"], 3)

        self._toggle_key_visibility()

    def _toggle_key_visibility(self):
        show_char = "" if self.show_key.get() else "*"
        for e in self._key_entries:
            e.configure(show=show_char)

    # ---------- 拉取模型列表 ----------
    def _on_fetch_models(self):
        if self._fetch_btn is None:
            return
        self._fetch_btn.configure(text=_t("fetching"), state=tk.DISABLED)
        provider = self.var_provider.get()

        # 捕获当前对话框内的值（不是已保存的 config）
        if provider == "gemini":
            key = self.vars["gemini_api_key"].get().strip()
            endpoint = self.vars["gen_ai_endpoint"].get().strip()
            fetch_fn = lambda: llm_client.fetch_gemini_models(key, endpoint)
        elif provider == "openai":
            key = self.vars["openai_api_key"].get().strip()
            endpoint = self.vars["openai_api_endpoint"].get().strip()
            fetch_fn = lambda: llm_client.fetch_openai_models(key, endpoint)
        else:
            self._fetch_btn.configure(text=_t("fetch_models"), state=tk.NORMAL)
            return

        def worker():
            try:
                models = fetch_fn()
                self.win.after(0, lambda: self._on_fetch_done(models, None))
            except Exception as e:
                self.win.after(0, lambda: self._on_fetch_done(None, e))

        threading.Thread(target=worker, daemon=True).start()

    def _on_fetch_done(self, models, err):
        if self._fetch_btn is not None:
            try:
                self._fetch_btn.configure(text=_t("fetch_models"), state=tk.NORMAL)
            except tk.TclError:
                pass  # 对话框已关闭
        if err is not None:
            log.warning(f"[设置] 拉取模型失败: {err}")
            messagebox.showerror(_t("fetch_err_title"), str(err), parent=self.win)
            return
        if self._model_combo is not None:
            try:
                self._model_combo.configure(values=models or [])
                log.info(f"[设置] 已拉取 {len(models or [])} 个模型")
            except tk.TclError:
                pass

    # ---------- 连通性测试 ----------
    def _on_test(self):
        if getattr(self, "btn_test", None) is None:
            return
        self.btn_test.configure(text=_t("testing"), state=tk.DISABLED)

        provider = self.var_provider.get()
        if provider == "gemini":
            key = self.vars["gemini_api_key"].get().strip()
            model = self.vars["gemini_model"].get().strip()
            endpoint = self.vars["gen_ai_endpoint"].get().strip()
        elif provider == "openai":
            key = self.vars["openai_api_key"].get().strip()
            model = self.vars["openai_model"].get().strip()
            endpoint = self.vars["openai_api_endpoint"].get().strip()
        else:
            key = self.vars["custom_api_key"].get().strip()
            model = self.vars["custom_model"].get().strip()
            endpoint = self.vars["custom_api_endpoint"].get().strip()

        def worker():
            result = llm_client.test_provider(provider, key, model, endpoint)
            self.win.after(0, lambda: self._on_test_done(result))

        threading.Thread(target=worker, daemon=True).start()

    def _on_test_done(self, result: dict):
        try:
            self.btn_test.configure(text=_t("test"), state=tk.NORMAL)
        except tk.TclError:
            return  # 对话框已关
        if result.get("ok"):
            reply = (result.get("reply") or "").strip() or "(空回复)"
            log.info(f"[设置] 测试通过，延迟 {result.get('latency_ms')}ms")
            messagebox.showinfo(
                _t("test_ok_title"),
                _t("test_ok_msg").format(
                    latency_ms=result.get("latency_ms", 0),
                    reply=reply[:300],
                ),
                parent=self.win,
            )
        else:
            log.warning(f"[设置] 测试失败: {result.get('error')}")
            messagebox.showerror(
                _t("test_err_title"),
                _t("test_err_msg").format(
                    latency_ms=result.get("latency_ms", 0),
                    error=result.get("error", ""),
                ),
                parent=self.win,
            )

    # ---------- ApexLol 数据缓存 ----------
    def _build_apexlol_section(self):
        """ApexLol 数据缓存区：标题 + 说明 + 状态行 + 立即更新按钮。"""
        # 分隔线
        tk.Frame(self.win, bg="#333355", height=1).pack(fill=tk.X, padx=16, pady=(4, 8))

        section = tk.Frame(self.win, bg="#1a1a2e")
        section.pack(fill=tk.X, padx=16, pady=(0, 8))

        # 标题
        tk.Label(section, text=_t("apexlol_section"),
                 bg="#1a1a2e", fg="#66ff66",
                 font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w")

        # 说明文字
        tk.Label(section, text=_t("apexlol_desc"),
                 bg="#1a1a2e", fg="#888899", justify="left",
                 font=("Microsoft YaHei UI", 8),
                 wraplength=480).pack(anchor="w", pady=(2, 6))

        # 状态行 + 按钮
        row = tk.Frame(section, bg="#1a1a2e")
        row.pack(fill=tk.X)

        self.var_apexlol_status = tk.StringVar(value=self._format_apexlol_status())
        tk.Label(row, textvariable=self.var_apexlol_status,
                 bg="#1a1a2e", fg="#aaaacc",
                 font=("Microsoft YaHei UI", 9)).pack(side=tk.LEFT)

        self.btn_apexlol = tk.Button(
            row, text=_t("apexlol_btn_update"),
            command=self._on_apexlol_update,
            bg="#2a4a2e", fg="#66ff66",
            activebackground="#3a5a3e", activeforeground="#88ff88",
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
            font=("Microsoft YaHei UI", 9, "bold"),
        )
        self.btn_apexlol.pack(side=tk.RIGHT)

        # 没传入 app 实例时禁用按钮（防御性）
        if self.app is None:
            self.btn_apexlol.configure(state=tk.DISABLED)
        elif self.app.is_data_updating():
            # 已有更新在跑（比如启动时的 auto-refresh）
            self.btn_apexlol.configure(text=_t("apexlol_btn_updating"),
                                        state=tk.DISABLED)

    def _format_apexlol_status(self) -> str:
        """读 apexlol_data.get_cache_info 生成状态描述字符串。"""
        try:
            from apexlol_data import get_cache_info
            from config import APEXLOL_CACHE_DIR, APEXLOL_CACHE_TTL_DAYS
            info = get_cache_info(APEXLOL_CACHE_DIR)
            if not info.get("exists"):
                return _t("apexlol_status_empty")
            ttl_h = APEXLOL_CACHE_TTL_DAYS * 24
            age = info.get("age_hours", 0)
            remaining = max(0, ttl_h - age)
            return _t("apexlol_status_loaded").format(
                count=info.get("champion_count", 0),
                age=int(age),
                remaining=int(remaining),
            )
        except Exception as e:
            log.warning(f"[设置] 读 ApexLol 缓存信息失败: {e}")
            return f"⚠️ {e}"

    def _on_apexlol_update(self):
        """点击「立即更新缓存」：调用 app.trigger_data_update。"""
        if self.app is None:
            return

        self.btn_apexlol.configure(text=_t("apexlol_btn_updating"),
                                    state=tk.DISABLED)

        def progress(current, total, name):
            try:
                self.var_apexlol_status.set(_t("apexlol_status_progress").format(
                    current=current, total=total, name=name))
            except tk.TclError:
                pass  # 对话框已关闭

        def on_done(success: bool):
            try:
                self.btn_apexlol.configure(text=_t("apexlol_btn_update"),
                                            state=tk.NORMAL)
                self.var_apexlol_status.set(self._format_apexlol_status())
            except tk.TclError:
                pass  # 对话框已关闭

        started = self.app.trigger_data_update(
            extra_progress=progress, on_done=on_done)
        if not started:
            log.info("[设置] 已有更新在跑，按钮保持禁用直到完成")

    # ---------- 保存 ----------
    def _open_log_file(self):
        """用系统默认应用打开 ~/.aram_tool/aram_debug.log。"""
        try:
            if hasattr(os, "startfile"):  # Windows
                os.startfile(LOG_FILE)  # noqa: S606 — 信任本地常量路径
            else:
                import subprocess
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.Popen([opener, LOG_FILE])
        except Exception as e:
            log.warning(f"[设置] 打开日志失败: {e}")
            messagebox.showerror(_t("open_log_err"), str(e), parent=self.win)

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

            # 热重载：LLM 配置立即生效，语言不热重载
            changed = config.reload()
            llm_client.reset_client()
            log.info(f"[设置] 热重载完成，变更键: {list(changed.keys())}")

            if "LANGUAGE" in changed:
                msg_key = "save_ok_lang_restart"
            else:
                msg_key = "save_ok_hot"
            messagebox.showinfo(
                _t("save_ok_title"),
                _t(msg_key).format(path=USER_SETTINGS_PATH),
                parent=self.win,
            )
            self.win.destroy()
        except Exception as e:
            log.error(f"[设置] 保存失败: {e}")
            messagebox.showerror(_t("save_err_title"), str(e), parent=self.win)


def open_settings_dialog(parent: tk.Misc, app=None) -> None:
    SettingsDialog(parent, app)
