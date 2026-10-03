# 🌊 Mindflow — AI Voice & Thought Assistant for Telegram

> **"Speak your mind. We handle the flow."**

Mindflow is an AI-powered Telegram personal assistant that transforms voice notes, quick thoughts, and expenses into structured tasks, bookmarks, and records in seconds.

## 🚀 Features
- 🎙 **Voice-to-Text in <1s**: Speak naturally while walking or driving using Groq Whisper.
- ⚡ **Auto-Categorization**: Automatically distinguishes between actionable **Tasks**, **Expenses**, **Notes**, and **Reading list bookmarks**.
- 📋 **Structured Outputs**: Formats dates, due times, merchants, amounts, and tags cleanly.
- 💰 **Zero-Cost Bootstrapped Architecture**: Runs on free/generous tiers ($0/month during launch).

## 🛠 Tech Stack
- **Language**: Python 3.12+
- **Telegram Bot Framework**: `aiogram 3.x` (Async)
- **Transcription**: Groq Whisper / OpenAI Whisper
- **Intelligence**: Gemini 1.5 Flash / GPT-4o-mini
- **Validation**: Pydantic v2

## 📦 Setup Instructions

1. **Clone & Navigate:**
   ```bash
   cd second-brain-bot
   ```

2. **Create Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in:
   - `TELEGRAM_BOT_TOKEN`: Get this from [@BotFather](https://t.me/botfather).
   - `GROQ_API_KEY`: Free lightning-fast transcription key from [Groq Console](https://console.groq.com).
   - `GEMINI_API_KEY`: Generous free multimodal key from [Google AI Studio](https://aistudio.google.com).

4. **Run Offline Test:**
   ```bash
   python3 test_offline.py
   ```

5. **Start the Bot:**
   ```bash
   python3 -m src.main
   ```

## 📈 Distribution & Growth Playbook
- **X / Twitter**: Post 15-second screencasts of voice capture while on the move $\rightarrow$ organized Notion/Todoist board.
- **Reddit**: Share in `r/productivity`, `r/Notion`, `r/ADHD`, and `r/SideProject`.
