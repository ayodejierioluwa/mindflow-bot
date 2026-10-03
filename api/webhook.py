import os
import json
import logging
from http.server import BaseHTTPRequestHandler
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

from src.config import config
from src.router import router
from src.transcriber import transcriber
from src.models import IntentType
from src.storage import storage
from src.notion import notion_service

logger = logging.getLogger(__name__)

bot = Bot(token=config.TELEGRAM_BOT_TOKEN) if config.TELEGRAM_BOT_TOKEN else None

def format_output(parsed, original_text: str = "") -> str:
    msg = f"{parsed.summary_message}\n\n"
    if parsed.intent == IntentType.TASK and parsed.task:
        msg += (
            f"📋 **Action Item:** {parsed.task.title}\n"
            f"📅 **Due:** {parsed.task.due_date or 'No date specified'}\n"
            f"🏷 **Category:** {parsed.task.category} | **Priority:** {parsed.task.priority.capitalize()}\n"
        )
    elif parsed.intent == IntentType.EXPENSE and parsed.expense:
        msg += (
            f"💳 **Merchant:** {parsed.expense.merchant}\n"
            f"💰 **Amount:** {parsed.expense.currency} {parsed.expense.amount:.2f}\n"
            f"📂 **Category:** {parsed.expense.category}\n"
        )
    elif parsed.intent == IntentType.NOTE and parsed.note:
        tags = " ".join([f"#{t}" for t in parsed.note.tags])
        msg += (
            f"📌 **Title:** {parsed.note.title}\n"
            f"{parsed.note.summary}\n"
            f"🏷 {tags}\n"
        )
    msg += "\n_⚡ Synced to Mindflow Inbox_"
    return msg

async def process_telegram_update(update_dict: dict):
    if not bot:
        return
    
    update = types.Update.model_validate(update_dict)
    if not update.message:
        return

    msg = update.message
    user_id = msg.from_user.id if msg.from_user else msg.chat.id
    
    # Track user
    if msg.from_user and storage.is_configured():
        await storage.get_or_create_user(user_id, msg.from_user.username, msg.from_user.first_name)

    # Handle /start
    if msg.text and msg.text.startswith("/start"):
        welcome_text = (
            "🌊 **Welcome to Mindflow!**\n"
            "_Speak your mind. We handle the flow._\n\n"
            "Never let a thought, task, or expense slip away.\n\n"
            "**Commands:**\n"
            "• `/tasks` — View your recent open tasks\n"
            "• `/notion` — Connect your Notion workspace\n\n"
            "**How to capture:**\n"
            "• 🎙 **Voice note:** Speak naturally while walking or driving.\n"
            "• 💬 **Text:** Type quick thoughts, expenses, or todos."
        )
        await bot.send_message(chat_id=msg.chat.id, text=welcome_text, parse_mode=ParseMode.MARKDOWN)
        return

    # Handle /tasks
    if msg.text and msg.text.startswith("/tasks"):
        tasks = await storage.get_recent_tasks(user_id)
        if not tasks:
            await bot.send_message(chat_id=msg.chat.id, text="✨ **All clear!** You have no open tasks right now.\nSend a voice note to add one!")
            return
        
        reply = "📋 **Your Open Priorities:**\n\n"
        for idx, t in enumerate(tasks, 1):
            due = f" (Due: {t.get('due_date')})" if t.get('due_date') else ""
            reply += f"{idx}. **{t['title']}**{due} — _{t.get('category', 'Task')}_\n"
        await bot.send_message(chat_id=msg.chat.id, text=reply, parse_mode=ParseMode.MARKDOWN)
        return

    # Handle /notion instructions
    if msg.text and msg.text.startswith("/notion"):
        notion_guide = (
            "📓 **Connect Mindflow to Notion in 30 Seconds:**\n\n"
            "1. Duplicate the official Mindflow Notion Template:\n"
            "👉 `https://notion.so/mindflow-template`\n\n"
            "2. Send your connection details here:\n"
            "`/connect_notion <YOUR_NOTION_KEY> <DATABASE_ID>`\n\n"
            "_(All tasks and notes will automatically sync into your Notion board in real-time!)_"
        )
        await bot.send_message(chat_id=msg.chat.id, text=notion_guide, parse_mode=ParseMode.MARKDOWN)
        return

    # Handle Text
    if msg.text:
        try:
            parsed = await router.parse_text(msg.text)
            
            # Persist to Storage if configured
            if parsed.intent == IntentType.TASK and parsed.task:
                await storage.save_task(user_id, parsed.task.title, parsed.task.due_date, parsed.task.priority, parsed.task.category)
            elif parsed.intent == IntentType.EXPENSE and parsed.expense:
                await storage.save_expense(user_id, parsed.expense.merchant, parsed.expense.amount, parsed.expense.currency, parsed.expense.category)

            reply = format_output(parsed, original_text=msg.text)
            await bot.send_message(chat_id=msg.chat.id, text=reply, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Error handling text: {e}")
            await bot.send_message(chat_id=msg.chat.id, text=f"⚠️ Error: {str(e)}")
        return

    # Handle Voice
    if msg.voice:
        try:
            status_msg = await bot.send_message(chat_id=msg.chat.id, text="🎧 _Listening and transcribing..._", parse_mode=ParseMode.MARKDOWN)
            file_info = await bot.get_file(msg.voice.file_id)
            
            local_path = f"/tmp/{msg.voice.file_id}.ogg"
            await bot.download_file(file_info.file_path, local_path)
            
            transcript = await transcriber.transcribe(local_path)
            if os.path.exists(local_path):
                os.remove(local_path)
                
            parsed = await router.parse_text(transcript)
            
            # Persist to Storage
            if parsed.intent == IntentType.TASK and parsed.task:
                await storage.save_task(user_id, parsed.task.title, parsed.task.due_date, parsed.task.priority, parsed.task.category)
            elif parsed.intent == IntentType.EXPENSE and parsed.expense:
                await storage.save_expense(user_id, parsed.expense.merchant, parsed.expense.amount, parsed.expense.currency, parsed.expense.category)

            reply = f"📝 *Transcript:*\n_\"{transcript}\"_\n\n" + format_output(parsed, original_text=transcript)
            await bot.edit_message_text(chat_id=msg.chat.id, message_id=status_msg.message_id, text=reply, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Error handling voice: {e}")
            await bot.send_message(chat_id=msg.chat.id, text=f"⚠️ Error processing voice: {str(e)}")
        return

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "Mindflow Bot Webhook Active", "ok": True}).encode())

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode('utf-8'))
            asyncio.run(process_telegram_update(data))
        except Exception as e:
            logger.error(f"Error handling webhook request: {e}")

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode())
