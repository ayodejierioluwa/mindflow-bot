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

logger = logging.getLogger(__name__)

bot = Bot(token=config.TELEGRAM_BOT_TOKEN) if config.TELEGRAM_BOT_TOKEN else None
dp = Dispatcher()

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
    
    # Handle /start
    if msg.text and msg.text.startswith("/start"):
        welcome_text = (
            "🌊 **Welcome to Mindflow!**\n"
            "_Speak your mind. We handle the flow._\n\n"
            "Never let a thought, task, or expense slip away.\n\n"
            "**How to use:**\n"
            "• 🎙 **Send a voice note:** Rambling thoughts, tasks, or follow-ups.\n"
            "• 💬 **Send a text message:** Quick tasks or brain-dump.\n"
            "• 🧾 **Send a receipt photo:** (Coming soon) Auto-logs expenses.\n\n"
            "Try sending a voice note or text like: \n"
            "_\"Spent $14 on lunch at Chipotle\"_ or \n"
            "_\"Call dentist to reschedule appointment tomorrow morning\"_"
        )
        await bot.send_message(chat_id=msg.chat.id, text=welcome_text, parse_mode=ParseMode.MARKDOWN)
        return

    # Handle Text
    if msg.text:
        try:
            parsed = await router.parse_text(msg.text)
            reply = format_output(parsed, original_text=msg.text)
            await bot.send_message(chat_id=msg.chat.id, text=reply, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await bot.send_message(chat_id=msg.chat.id, text=f"⚠️ Error: {str(e)}")
        return

    # Handle Voice
    if msg.voice:
        try:
            status_msg = await bot.send_message(chat_id=msg.chat.id, text="🎧 _Listening and transcribing..._", parse_mode=ParseMode.MARKDOWN)
            file_info = await bot.get_file(msg.voice.file_id)
            
            # Temporary download in /tmp (writable in Vercel serverless)
            local_path = f"/tmp/{msg.voice.file_id}.ogg"
            await bot.download_file(file_info.file_path, local_path)
            
            transcript = await transcriber.transcribe(local_path)
            if os.path.exists(local_path):
                os.remove(local_path)
                
            parsed = await router.parse_text(transcript)
            reply = f"📝 *Transcript:*\n_\"{transcript}\"_\n\n" + format_output(parsed, original_text=transcript)
            await bot.edit_message_text(chat_id=msg.chat.id, message_id=status_msg.message_id, text=reply, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
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
