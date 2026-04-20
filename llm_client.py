# -*- coding: utf-8 -*-
"""LLM 统一适配层

支持三种提供商，由 config.LLM_PROVIDER 选择：
- gemini: 官方 Google Gemini（使用 google-genai SDK，支持文本+图像）
- openai: OpenAI 兼容 Chat Completions（支持文本+图像，data URI）
- custom: 自定义后端（文本为主，尝试常见响应字段）

对外只暴露 LLMClient.generate(contents, ...)：
    contents: list[str | bytes | (bytes, mime_type)]
        - str   -> 文本片段
        - bytes -> 图像（默认 image/jpeg）
        - (bytes, "image/png") -> 指定 MIME 的图像
    返回: 响应文本字符串

内置 SSL EOF / 超时自动重试，与旧版 gemini_analyzer._call_with_retry 行为一致。
"""

import base64
import concurrent.futures
import json
import logging
import time as _time

log = logging.getLogger("ARAM")

# ==================== 重试参数 ====================
MAX_RETRIES = 2       # 最多重试2次（共3次尝试）
RETRY_DELAY = 1.0     # 重试前等待秒数


def _is_retryable(exc: Exception) -> bool:
    """判断是否为瞬态错误：SSL EOF / 超时 / 常见网络抖动。"""
    msg = str(exc).lower()
    if isinstance(exc, (concurrent.futures.TimeoutError, TimeoutError)):
        return True
    return (
        "unexpected_eof" in msg
        or "ssleoferror" in msg
        or "eof occurred" in msg
        or "connection reset" in msg
        or "connection aborted" in msg
        or "read timed out" in msg
    )


def _normalize_part(item):
    """把输入项归一化为 ('text', str) 或 ('image', bytes, mime)。"""
    if isinstance(item, str):
        return ("text", item)
    if isinstance(item, bytes):
        return ("image", item, "image/jpeg")
    if isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], (bytes, bytearray)):
        return ("image", bytes(item[0]), item[1])
    raise TypeError(f"Unsupported content part: {type(item)}")


# ==================== Gemini Backend ====================
class _GeminiBackend:
    name = "gemini"

    def __init__(self):
        from google import genai
        from google.genai import types
        from config import GEMINI_API_KEY, GEMINI_MODEL, GEN_AI_ENDPOINT
        self._genai = genai
        self._types = types
        self._model = GEMINI_MODEL
        if GEN_AI_ENDPOINT:
            # 允许自定义代理端点（SDK 支持 http_options.base_url）
            try:
                self._client = genai.Client(
                    api_key=GEMINI_API_KEY,
                    http_options=types.HttpOptions(base_url=GEN_AI_ENDPOINT),
                )
            except Exception:
                # 某些 SDK 版本字段名不同，退回无代理
                log.warning("[Gemini] GEN_AI_ENDPOINT 注入失败，使用默认端点")
                self._client = genai.Client(api_key=GEMINI_API_KEY)
        else:
            self._client = genai.Client(api_key=GEMINI_API_KEY)

    def _to_genai_contents(self, contents):
        parts = []
        for item in contents:
            kind = _normalize_part(item)
            if kind[0] == "text":
                parts.append(kind[1])
            else:
                parts.append(self._types.Part.from_bytes(data=kind[1], mime_type=kind[2]))
        return parts

    def generate(self, contents, temperature):
        response = self._client.models.generate_content(
            model=self._model,
            contents=self._to_genai_contents(contents),
            config=self._types.GenerateContentConfig(temperature=temperature),
        )
        return response.text


# ==================== OpenAI-Compatible Backend ====================
class _OpenAIBackend:
    name = "openai"

    def __init__(self):
        import requests
        from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_API_ENDPOINT
        self._requests = requests
        self._api_key = OPENAI_API_KEY
        self._model = OPENAI_MODEL
        self._endpoint = OPENAI_API_ENDPOINT

    def _build_message_content(self, contents):
        """OpenAI 多模态 content 数组；若全是文本，直接返回拼接字符串。"""
        parts = [_normalize_part(c) for c in contents]
        if all(p[0] == "text" for p in parts):
            return "\n\n".join(p[1] for p in parts)
        out = []
        for p in parts:
            if p[0] == "text":
                out.append({"type": "text", "text": p[1]})
            else:
                b64 = base64.b64encode(p[1]).decode("ascii")
                out.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{p[2]};base64,{b64}"},
                })
        return out

    def generate(self, contents, temperature):
        url = f"{self._endpoint}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": self._build_message_content(contents)}],
            "temperature": temperature,
        }
        resp = self._requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code >= 400:
            raise RuntimeError(f"OpenAI API {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise RuntimeError(f"OpenAI 响应结构异常: {json.dumps(data)[:300]}")


# ==================== Custom Backend ====================
class _CustomBackend:
    """通用自定义 HTTP 后端。

    请求：POST {endpoint}  Content-Type: application/json
        {"model": CUSTOM_MODEL, "prompt": "<所有文本拼接>", "temperature": X}
    响应：按优先级尝试 choices[0].message.content, choices[0].text, text, response, output, content
    图像：当前不支持，仅使用文本片段（会 log 警告）。
    """
    name = "custom"

    def __init__(self):
        import requests
        from config import CUSTOM_API_KEY, CUSTOM_MODEL, CUSTOM_API_ENDPOINT
        self._requests = requests
        self._api_key = CUSTOM_API_KEY
        self._model = CUSTOM_MODEL
        self._endpoint = CUSTOM_API_ENDPOINT

    def generate(self, contents, temperature):
        texts = []
        had_image = False
        for item in contents:
            kind = _normalize_part(item)
            if kind[0] == "text":
                texts.append(kind[1])
            else:
                had_image = True
        if had_image:
            log.warning("[custom] 自定义后端当前不转发图像，已忽略截图部分")

        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        payload = {
            "model": self._model,
            "prompt": "\n\n".join(texts),
            "temperature": temperature,
        }
        resp = self._requests.post(self._endpoint, headers=headers, json=payload, timeout=60)
        if resp.status_code >= 400:
            raise RuntimeError(f"Custom API {resp.status_code}: {resp.text[:300]}")
        try:
            data = resp.json()
        except ValueError:
            return resp.text

        for path in (
            ("choices", 0, "message", "content"),
            ("choices", 0, "text"),
            ("text",),
            ("response",),
            ("output",),
            ("content",),
        ):
            try:
                cur = data
                for k in path:
                    cur = cur[k]
                if isinstance(cur, str):
                    return cur
            except (KeyError, IndexError, TypeError):
                continue
        raise RuntimeError(f"自定义后端响应解析失败: {json.dumps(data)[:300]}")


# ==================== 统一入口 ====================
_BACKENDS = {
    "gemini": _GeminiBackend,
    "openai": _OpenAIBackend,
    "custom": _CustomBackend,
}


class LLMClient:
    def __init__(self, provider=None):
        from config import LLM_PROVIDER
        self.provider = (provider or LLM_PROVIDER).lower()
        if self.provider not in _BACKENDS:
            raise ValueError(f"不支持的 LLM_PROVIDER: {self.provider}")
        self._backend = _BACKENDS[self.provider]()
        log.info(f"[LLM] 已加载提供商: {self.provider}")

    def generate(self, contents, temperature=0.3, label="API",
                 hard_timeout=None, max_retries=MAX_RETRIES):
        """生成文本。带 SSL EOF / 硬超时自动重试。"""
        last_exc = None
        for attempt in range(1 + max_retries):
            try:
                if hard_timeout:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                        future = pool.submit(self._backend.generate, contents, temperature)
                        return future.result(timeout=hard_timeout)
                return self._backend.generate(contents, temperature)
            except Exception as e:
                if _is_retryable(e) and attempt < max_retries:
                    last_exc = e
                    reason = "超时" if isinstance(e, (concurrent.futures.TimeoutError, TimeoutError)) else "瞬态错误"
                    log.warning(f"[{label}] {reason} ({attempt+1}/{max_retries})，{RETRY_DELAY}s 后重试...")
                    _time.sleep(RETRY_DELAY)
                    continue
                raise
        raise last_exc  # 理论不可达


# 模块级单例，供 gemini_analyzer 等模块复用
_default_client = None


def get_client() -> LLMClient:
    global _default_client
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client


def reset_client() -> None:
    """丢弃已缓存的 LLMClient 单例。下次 get_client() 会按当前 config 重建。

    设置对话框保存后调用，实现 provider / key / model / endpoint 的热重载。
    """
    global _default_client
    _default_client = None


# ==================== 模型列表拉取 ====================
def fetch_gemini_models(api_key: str, endpoint: str = "", timeout: float = 15.0) -> list:
    """GET {endpoint}/models?key=... 列出支持 generateContent 的模型。

    endpoint 为空时使用官方 URL；传入自定义代理时自动补齐 /v1beta。
    抛 RuntimeError 表示请求失败；正常返回排序后的模型短名列表。
    """
    import requests
    if not api_key:
        raise RuntimeError("需要填写 API Key 才能拉取模型列表")

    base = (endpoint or "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
    if "/v1beta" not in base and "/v1" not in base:
        base = base + "/v1beta"
    url = f"{base}/models?key={api_key}"

    resp = requests.get(url, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini /models {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    out = []
    for m in data.get("models", []):
        name = m.get("name", "")
        methods = m.get("supportedGenerationMethods", [])
        if "generateContent" in methods:
            short = name.split("/", 1)[-1] if "/" in name else name
            if short:
                out.append(short)
    return sorted(set(out))


def fetch_openai_models(api_key: str, endpoint: str, timeout: float = 15.0) -> list:
    """GET {endpoint}/models（OpenAI / Azure / LM Studio / Ollama 均实现此端点）。"""
    import requests
    if not endpoint:
        raise RuntimeError("需要填写 API Endpoint 才能拉取模型列表")

    url = f"{endpoint.rstrip('/')}/models"
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    resp = requests.get(url, headers=headers, timeout=timeout)
    if resp.status_code >= 400:
        raise RuntimeError(f"OpenAI /models {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    out = [m.get("id") for m in data.get("data", []) if m.get("id")]
    return sorted(set(out))
