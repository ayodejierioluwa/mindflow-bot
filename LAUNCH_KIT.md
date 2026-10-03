# 🌊 Mindflow — Marketing & Distribution Launch Kit

---

## 1. Bot Profile Setup (@BotFather)

Run `/setdescription` on `@BotFather` and paste:
> Speak your mind. We handle the flow. 🌊
>
> Mindflow is an AI personal assistant that turns rambling voice notes into organized tasks, expenses, and notes in under 2 seconds.

Run `/setabouttext` and paste:
> Never let a thought or task slip away. Speak naturally while walking or driving, and Mindflow extracts action items and due dates instantly.

Run `/setcommands` and paste:
```text
start - Open Mindflow and get started
tasks - View your recent open priorities
notion - Connect your Notion workspace
```

---

## 2. Reddit Viral Launch Posts

### Subreddit 1: `r/productivity`
* **Title:** Why every task manager failed me (and how talking to Telegram fixed my ADHD friction)
* **Body:**
```text
Like a lot of you, I have an endless cycle with productivity apps:
1. Download a shiny new app (Notion, Todoist, TickTick).
2. Spend 3 hours color-coding tags and categories.
3. 4 days later, abandon it completely because opening a heavy app while walking or driving feels like homework.

The friction was always the CAPTURE step. By the time I type "Buy oat milk", I've forgotten my next thought.

So this weekend I built something purely to solve my own problem: Mindflow, an AI bot inside Telegram.

Whenever an idea or task strikes, I just hold the mic on Telegram and ramble for 15 seconds:
"Need to call the plumber on Monday, still have that meeting with Sandra at 10am, and follow up with Amanda."

In 2 seconds, it transcribes, extracts the due dates/times, and tags them cleanly as prioritized action items.

It's completely free to try right now. If you struggle with ADHD task paralysis or on-the-go friction, I’d love for you to test it and tell me what you think:
👉 https://t.me/usemindflowbot
```

### Subreddit 2: `r/SideProject`
* **Title:** I built an AI "Second Brain" on Telegram that transcribes voice notes to structured tasks in <2s ($0 stack)
* **Body:**
```text
Hey r/SideProject!

Wanted to share a project I bootstrapped this weekend: Mindflow (https://t.me/usemindflowbot).

The Architecture:
- Framework: Python + aiogram (Serverless Webhook)
- Hosting: Vercel ($0 free tier)
- Audio Transcription: Groq Whisper Large (sub-second speeds)
- Structured Intent Extraction: Qwen / Gemini Flash

Would love feedback on:
1. What integrations do you want most? (Google Calendar, Todoist, Notion)
2. How is the transcription accuracy on your accent?
```

---

## 3. Viral X (Twitter) Launch Thread

### Tweet 1 (Hook with Video):
> I hate opening complex productivity apps when I'm on the move.
>
> So I built **Mindflow** — an AI Telegram assistant.
>
> You send a 15-second rambling voice note, and it transcribes, extracts tasks, due dates, and expenses in under 2 seconds.
>
> Here’s a 15s demo: 🧵👇
> [ATTACH YOUR 15-SECOND SCREEN RECORDING]

### Tweet 2:
> How it works behind the scenes:
> • Groq Whisper transcribes your voice in ~0.5s
> • An LLM intent router parses tasks vs expenses vs notes
> • Auto-extracts due dates and priorities
> • Pushes directly to your inbox or Notion

### Tweet 3 (CTA):
> I'm opening free beta access to 50 people today:
>
> 👉 Try it here: https://t.me/usemindflowbot
>
> Let me know your thoughts or what feature you want added next! 🌊
