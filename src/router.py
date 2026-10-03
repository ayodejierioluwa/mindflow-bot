import os
import json
import logging
from typing import Optional
from src.config import config
from src.models import ParsedCapture, IntentType

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """
You are an ultra-fast, intelligent Second Brain Executive Assistant.
Your job is to parse unstructured thoughts, voice transcriptions, or receipt descriptions from a user into clean, structured data.

Categorize the input into one of 4 intents:
1. 'task': actionable to-do items, reminders, follow-ups with people.
2. 'expense': money spent, bills paid, receipts, purchases.
3. 'read_later': bookmarks, links, articles to read.
4. 'note': ideas, brainstorming, general thoughts, journal notes.

Rules:
- Generate a warm, concise, professional confirmation message for Telegram with emojis.
- Extract concrete dates or times if mentioned.
- For expenses, accurately extract the amount and merchant.
- Return strictly valid JSON adhering to the ParsedCapture schema.
"""

class IntentRouter:
    def __init__(self):
        self.groq_key = config.GROQ_API_KEY
        self.gemini_key = config.GEMINI_API_KEY
        self.openai_key = config.OPENAI_API_KEY

    async def parse_text(self, text: str) -> ParsedCapture:
        """Parses raw text into structured ParsedCapture model."""
        # Preference: Gemini 1.5 Flash (free tier) or OpenAI / Groq
        if self.gemini_key:
            return await self._parse_with_gemini(text)
        elif self.openai_key:
            return await self._parse_with_openai(text)
        elif self.groq_key:
            return await self._parse_with_groq(text)
        else:
            # Fallback mock for local testing without active API keys
            return self._mock_parse(text)

    async def _parse_with_openai(self, text: str) -> ParsedCapture:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self.openai_key)
        
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            response_format=ParsedCapture,
        )
        return response.choices[0].message.parsed

    async def _parse_with_groq(self, text: str) -> ParsedCapture:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=self.groq_key)
        
        prompt = f"{EXTRACTION_SYSTEM_PROMPT}\n\nSchema:\n{json.dumps(ParsedCapture.model_json_schema())}\n\nInput: {text}\n\nReturn strictly valid JSON only."
        response = await client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return ParsedCapture.model_validate(data)

    async def _parse_with_gemini(self, text: str) -> ParsedCapture:
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        payload = {
            "contents": [{"parts": [{"text": f"{EXTRACTION_SYSTEM_PROMPT}\n\nUser input: {text}"}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "response_schema": ParsedCapture.model_json_schema()
            }
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, json=payload)
            res.raise_for_status()
            res_data = res.json()
            content_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return ParsedCapture.model_validate_json(content_text)

    def _mock_parse(self, text: str) -> ParsedCapture:
        """Heuristic mock for instant testing without API keys configured yet."""
        lower = text.lower()
        if any(w in lower for w in ["spent", "paid", "$", "dollar", "receipt", "bought", "cost"]):
            return ParsedCapture(
                intent=IntentType.EXPENSE,
                summary_message="🧾 Expense logged: Automatically extracted transaction details.",
                expense={
                    "merchant": "Detected Vendor",
                    "amount": 15.0,
                    "currency": "USD",
                    "category": "General",
                    "date": "Today"
                }
            )
        elif any(w in lower for w in ["todo", "remind", "task", "call", "schedule", "tomorrow", "due"]):
            return ParsedCapture(
                intent=IntentType.TASK,
                summary_message="✅ Task captured: Added to your prioritized to-do list.",
                task={
                    "title": text,
                    "due_date": "Next business day",
                    "priority": "medium",
                    "category": "Work"
                }
            )
        else:
            return ParsedCapture(
                intent=IntentType.NOTE,
                summary_message="💡 Idea saved to your Second Brain daily log.",
                note={
                    "title": text[:40] + ("..." if len(text) > 40 else ""),
                    "summary": f"• {text}",
                    "tags": ["quick-note", "inbox"]
                }
            )

router = IntentRouter()
