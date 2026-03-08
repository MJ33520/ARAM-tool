# ⚔️ ARAM Tool - Hextech Havoc Assistant

> English | **[中文](README.md)**

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Gemini](https://img.shields.io/badge/AI-Gemini-orange?logo=google)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)

A real-time **Gemini AI** powered analysis assistant for League of Legends Hextech Havoc (ARAM). Captures the loading screen, auto-identifies team compositions, and provides complete build, augment, and strategy guides.

## ✨ Features

- 🎮 **One-Click Analysis** — Click the floating button to screenshot & send to Gemini AI
- 🤖 **Smart Champion Detection** — AI reads all champion names from the loading screen and auto-identifies yours
- 📋 **Full Guide Output** — Hextech augments, 6-item builds, skill order, playstyle tips, team strategy
- 🗡️ **Teammate Recommendations** — Augment and build suggestions for every teammate
- 🖥️ **Overlay Display** — Always-on-top guide window with drag & hotkey support
- 🌐 **Bilingual Support** — Switch between Chinese and English with one config change

## 🚀 Quick Start

### 1. Get a Gemini API Key

Visit [Google AI Studio](https://aistudio.google.com/apikey) to get a free API key.

### 2. Set Environment Variable

```cmd
setx GEMINI_API_KEY "your_api_key"
```

### 3. Install Dependencies

```cmd
pip install -r requirements.txt
```

### 4. Launch

Double-click `launch.bat`, or:

```cmd
python main.py
```

## 🎮 How to Use

1. After launching, a floating `[⚔️ Analyze | 📋 Guide]` button appears at the top-left corner
2. On the ARAM loading screen, click **⚔️ Analyze**
3. Wait 15-30 seconds for AI analysis, then the guide overlay pops up automatically
4. Press **Ctrl+F12** to toggle the guide overlay anytime

## 🌐 Language Switch

Edit `config.py` and change the `LANGUAGE` value:

```python
LANGUAGE = "zh"   # Chinese (default)
LANGUAGE = "en"   # English
```

This changes the UI text, console messages, and AI analysis language.

## 📁 File Structure

| File | Description |
|------|-------------|
| `main.py` | Main entry, floating button & overlay |
| `config.py` | Config (API key, language, UI) |
| `lang.py` | i18n strings & prompts (zh/en) |
| `screenshot.py` | Screenshot module |
| `gemini_analyzer.py` | Gemini API module |
| `overlay_ui.py` | Standalone overlay UI (backup) |
| `launch.bat` | Windows launch script |

## 🔧 Requirements

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Network**: Access to Google Gemini API
- **Game**: League of Legends (any region)

## 📝 Notes

- Trigger analysis on the **loading screen** (when all champion cards are visible)
- Each analysis takes ~15-30 seconds depending on network and API response
- Right-click drag to reposition the floating button
- Press Esc to hide the guide overlay, click 📋 to show it again

## 📄 License

MIT
