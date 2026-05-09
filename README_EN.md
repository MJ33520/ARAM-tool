# ⚔️ ARAM Tool - Hextech Havoc Assistant

> English | **[中文](README.md)**

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![LLM](https://img.shields.io/badge/LLM-Gemini%20%7C%20OpenAI%20%7C%20Custom-orange)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
[![Release](https://img.shields.io/github/v/release/Zayia/ARAM-tool?include_prereleases)](https://github.com/Zayia/ARAM-tool/releases)

A real-time AI assistant for League of Legends ARAM (Hextech Havoc). Supports **Gemini / OpenAI-compatible / custom backends**. Auto-detects team compositions on the loading screen and outputs a complete guide: builds, augments, skill order, playstyle.

## ✨ Features

- 🤖 **Multi-LLM** — Gemini / OpenAI / Azure / LM Studio / Ollama / any OpenAI-compatible gateway / custom JSON POST backend
- ⚙️ **Settings UI** — Switch provider, fill key, ping, pick model. Saved settings apply **instantly, no restart**
- 🧪 **Connection test** — One-click ping before saving
- 🔄 **Model auto-discovery** — Pulls model list from the provider's `/models` endpoint (Gemini & OpenAI)
- 📋 **Full guide output** — Hextech augments, 6-item build, skill order, playstyle, team strategy
- 🖥️ **Overlay** — Always-on-top, draggable
- 📂 **One-click log file** — Open `aram_debug.log` directly from settings
- 🌐 **Bilingual** — Switch UI and AI output between Chinese and English
- ♻️ **Auto-retry** — SSL EOF / 5xx / rate limit / "Post EOF" upstream errors retry automatically

---

## 🚀 Quick Start

### Option A: Download the `.exe` (recommended, no Python needed)

1. Visit [Releases](https://github.com/Zayia/ARAM-tool/releases) and download `ARAM-Assistant-v*.exe`
   - Every push produces a new `v{N}` version, marked as latest
2. **Double-click to run** — no extraction needed
3. On first launch, click `⚙️` on the floating bar to configure your LLM provider and API key
4. [Get a free Gemini key](https://aistudio.google.com/apikey) or use any OpenAI-compatible key

### Option B: Run from source (development / customization)

```cmd
git clone https://github.com/Zayia/ARAM-tool.git
cd ARAM-tool
pip install -r requirements.txt
python main.py
```

After launch, click `⚙️` to configure.

---

## 🎮 How to Use

Floating bar: `⚡Hextech  |  📋Guide  |  ✏️Fix  |  ⚙️  |  ✕`

| Button | Function |
|------|------|
| ⚡ Hextech | Screenshot & analyze the current 3-augment choice; gives a recommendation |
| 📋 Guide | Show / hide the global strategy window |
| ✏️ Fix | Manually specify your champion if auto-detection failed (3-tier fallback: LCU+AI → AI-only → data-only) |
| ⚙️ | Settings dialog (LLM provider, model, key, UI language, ApexLol cache, open log file) |
| ✕ | Quit the program |

**Drag**: right-click-and-hold on any button / separator / status bar to drag the whole bar.
**Realtime log**: Settings → "📂 Open config folder" reveals `~/.aram_tool/aram_debug.log`, `settings.json`, and the ApexLol cache.

> Older versions had a "DOS console" toggle and a `🔄 Data` button — both removed/relocated. When running `python main.py` from a real terminal, you can still type a champion name directly into stdin to trigger an instant pre-game analysis.

---

## 🔧 LLM provider configuration

Three ways, priority: **env var > `~/.aram_tool/settings.json` > code default**

1. **⚙️ UI** (recommended): floating bar → `⚙️` → fill in → save → applies instantly
2. **Env vars**: `set LLM_PROVIDER=openai` / `set OPENAI_API_KEY=...` etc.
3. **Edit `config.py` defaults** (not recommended; risk of accidentally committing keys)

Full parameter list, common scenarios (LM Studio / Ollama / Azure / proxy), and troubleshooting: see [CUSTOM_LLM_SETUP.md](CUSTOM_LLM_SETUP.md).

### Hextech analysis timeout (slow gateways)

Default hard timeouts: image 20s, text 12s. Slow gateways or local LLMs can bump these:

```cmd
set HEXTECH_IMAGE_TIMEOUT=30
set HEXTECH_TEXT_TIMEOUT=20
```

Or in `~/.aram_tool/settings.json`: `{ "hextech_image_timeout": 30, "hextech_text_timeout": 20 }`

---

## 🎲 ApexLol data cache

The tool caches every champion's hextech synergy and rating data from [ApexLol.info](https://apexlol.info). The AI references this data to avoid recommending augments that aren't actually on screen.

- Settings → "ApexLol data cache" shows current state (champion count / age / TTL remaining) plus an "Update now" button
- Cache lives 7 days; auto-refreshes on startup if expired
- Without an LLM key, the ✏️ Fix button can fall back to data-only lookup mode

---

## 📁 File Structure

| File | Description |
|------|-------------|
| `main.py` | Entry point; floating bar + Toplevel windows + LCU monitor |
| `config.py` | Config (env > settings.json > default); `reload()` enables LLM hot-reload |
| `llm_client.py` | Unified LLM adapter (Gemini / OpenAI / custom); retry, ping test, model fetch |
| `gemini_analyzer.py` | 4 analysis modes (full strategy / quick guide / hextech image / hextech text), routed via `LLMClient` |
| `settings_ui.py` | Settings dialog; auto-runs `config.reload()` on save; includes ApexLol cache management & log open button |
| `lang.py` | i18n strings + all AI prompt templates |
| `screenshot.py` | mss screenshot module (crops the central 70%×70% to reduce tokens) |
| `apexlol_scraper.py` / `apexlol_data.py` | Scrape ApexLol.info data + local cache + champion alias resolution |
| `lcu_client.py` | LCU API client (extracts token from LeagueClientUx.exe args; fetches rosters) |
| `launch.bat` / `launch_by_uv.bat` | Windows launchers (default `pythonw`, no DOS window) |
| `build.bat` | Local PyInstaller build script (`--noconsole --onefile`) |
| `.github/workflows/release.yml` | CI: every push produces a `v{run_number}` stable release marked as latest; auto-prunes to keep newest 10 |

---

## 🏗️ Build it yourself

Requires Windows (PyInstaller does not support cross-compilation).

**Local**: double-click `build.bat`; output is `dist\ARAM-Assistant.exe`.

**CI**: every push automatically builds and publishes a `v{run_number}` stable release (marked latest), pruning to keep the newest 10. Manual semver tags work too:
```cmd
git tag -a v1.0.0 -m "release notes"
git push origin v1.0.0
```

---

## 🔧 Requirements

- **OS**: Windows 10/11
- **Python** (source mode only): 3.10+
- **Network**: access to your chosen LLM API endpoint
- **Game**: League of Legends (any region)

---

## 📝 Notes

- Hextech screenshot analysis must be triggered on the **loading screen / hextech selection screen** (cards must be visible)
- Each analysis takes 5–30s depending on provider & network
- The packaged build has no DOS window. To watch live logs, use Settings → "📂 Open config folder"
- `~/.aram_tool/settings.json` contains plaintext API keys; permissions 0600 (Unix only — `chmod` is a no-op on Windows)
- Multi-monitor: screenshots target the primary monitor (`monitors[1]`); playing on a secondary monitor will capture the wrong screen

---

## 📊 Data source acknowledgment

Hextech augment recommendation data is sourced from **[ApexLol.info](https://apexlol.info)**.

- Fetched only when the user actively clicks Settings → ApexLol data cache → Update now, or when the cache has expired — never blindly auto-scraped
- Requests are throttled (0.4s delay) to minimize server load
- Data is cached locally for 7 days to avoid redundant requests
- This project has **no official affiliation** with ApexLol.info; all data copyrights belong to the source
- If ApexLol.info operators have concerns about how data is used here, please file a GitHub issue and we'll address it

---

## ⚠️ Disclaimer

- Personal learning project; provided for reference only with no accuracy guarantee
- Not affiliated with or endorsed by Riot Games / League of Legends
- The tool **does not read or modify any game data**; it only screenshots your screen and uses AI for analysis. However, Riot may still flag third-party tools as violations — **use at your own risk**
- Please comply with the game's terms of service

---

## Contributors

- **[Zayia](https://github.com/Zayia)** - Project logic & review
- **Antigravity (AI) / Claude** - Implementation & Optimization

PRs welcome!

---

## 📄 License

MIT
