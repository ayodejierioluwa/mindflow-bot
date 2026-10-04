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
    username = msg.from_user.username if msg.from_user else None
    first_name = msg.from_user.first_name if msg.from_user else "Friend"
    
    # Track & upsert user in Supabase
    user_profile = None
    if storage.is_configured():
        user_profile = await storage.get_or_create_user(user_id, username, first_name)

    # 1. Handle /start
    if msg.text and msg.text.startswith("/start"):
        welcome_text = (
            f"🌊 **Welcome to Mindflow, {first_name}!**\n"
            "_Speak your mind. We handle the flow._\n\n"
            "Never let a thought, task, or expense slip away.\n\n"
            "**Quick Commands:**\n"
            "• `/tasks` — View your active priorities\n"
            "• `/expenses` — View recent logged expenses\n"
            "• `/briefing` — Get your daily morning agenda\n"
            "• `/notion` — Link your Notion workspace\n\n"
            "**How to capture:**\n"
            "• 🎙 **Voice note:** Hold mic and speak naturally.\n"
            "• 💬 **Text message:** Quick braindump, task, or spend."
        )
        await bot.send_message(chat_id=msg.chat.id, text=welcome_text, parse_mode=ParseMode.MARKDOWN)
        return

    # 2. Handle /tasks
    if msg.text and msg.text.startswith("/tasks"):
        tasks = await storage.get_recent_tasks(user_id)
        if not tasks:
            await bot.send_message(
                chat_id=msg.chat.id, 
                text="✨ **Inbox Zero!** You have no open tasks.\nSend a voice note to add one!"
            )
            return
        
        reply = "📋 **Your Open Priorities:**\n\n"
        for idx, t in enumerate(tasks, 1):
            due = f" *(Due: {t.get('due_date')})*" if t.get('due_date') else ""
            reply += f"{idx}. **{t['title']}**{due}\n   └ 🏷 _{t.get('category', 'Personal')}_ &bull; Priority: {t.get('priority', 'medium').capitalize()}\n"
        
        reply += "\n_Tip: Type or speak a new task anytime to add to this list._"
        await bot.send_message(chat_id=msg.chat.id, text=reply, parse_mode=ParseMode.MARKDOWN)
        return

    # 3. Handle /expenses
    if msg.text and msg.text.startswith("/expenses"):
        expenses = await storage.get_recent_expenses(user_id)
        if not expenses:
            await bot.send_message(
                chat_id=msg.chat.id,
                text="💳 **No expenses recorded yet.**\nTry typing: _\"Spent $24 on lunch at Chipotle\"_"
            )
            return
        
        total = sum(float(e.get('amount', 0)) for e in expenses)
        currency = expenses[0].get('currency', 'USD')
        reply = f"💰 **Recent Expenses (Total: {currency} {total:.2f}):**\n\n"
        for idx, e in enumerate(expenses, 1):
            reply += f"{idx}. **{e['merchant']}** — {e['currency']} {float(e['amount']):.2f} (_{e['category']}_)\n"
        
        await bot.send_message(chat_id=msg.chat.id, text=reply, parse_mode=ParseMode.MARKDOWN)
        return

    # 4. Handle /briefing (Morning Agenda)
    if msg.text and msg.text.startswith("/briefing"):
        tasks = await storage.get_recent_tasks(user_id)
        greeting = f"☀️ **Good day, {first_name}!**\n\nHere is your Mindflow Daily Briefing:\n\n"
        if tasks:
            greeting += "🎯 **Today's Key Focus Areas:**\n"
            for idx, t in enumerate(tasks[:3], 1):
                due = f" ({t.get('due_date')})" if t.get('due_date') else ""
                greeting += f"• **{t['title']}**{due}\n"
        else:
            greeting += "✨ You have a clean slate today! What are you building today?\n"
            
        greeting += "\n_Speak or text me anytime to capture your thoughts on the go._"
        await bot.send_message(chat_id=msg.chat.id, text=greeting, parse_mode=ParseMode.MARKDOWN)
        return

    # 5. Handle /connect_notion <KEY> <DB_ID>
    if msg.text and msg.text.startswith("/connect_notion"):
        parts = msg.text.strip().split()
        if len(parts) < 3:
            await bot.send_message(
                chat_id=msg.chat.id,
                text="⚠️ **Format:** `/connect_notion <NOTION_SECRET_KEY> <DATABASE_ID>`\n\nExample:\n`/connect_notion ntn_12345... 8ab7f89c...`"
            )
            return
        
        n_key = parts[1]
        n_db = parts[2]
        success = await storage.update_user_notion(user_id, n_key, n_db)
        if success:
            await bot.send_message(
                chat_id=msg.chat.id,
                text="✅ **Notion Workspace Linked Successfully!**\nAll your future tasks and notes will automatically sync into your Notion database in real-time."
            )
        else:
            await bot.send_message(chat_id=msg.chat.id, text="⚠️ Error saving your Notion credentials. Please try again.")
        return

    # 6. Handle /notion guide
    if msg.text and msg.text.startswith("/notion"):
        notion_guide = (
            "📓 **Connect Mindflow to Notion in 30 Seconds:**\n\n"
            "1. Duplicate the official **Mindflow Notion Template**:\n"
            "👉 `https://mindflow.so/notion-template`\n\n"
            "2. Create an integration token at [notion.so/my-integrations](https://www.notion.so/my-integrations).\n\n"
            "3. Link it by replying here with:\n"
            "`/connect_notion <YOUR_SECRET_KEY> <DATABASE_ID>`\n\n"
            "_(Tasks will sync directly to your personal Kanban board!)_"
        )
        await bot.send_message(chat_id=msg.chat.id, text=notion_guide, parse_mode=ParseMode.MARKDOWN)
        return

    # 7. Handle Text
    if msg.text:
        try:
            parsed = await router.parse_text(msg.text)
            
            # Persist to Supabase
            if parsed.intent == IntentType.TASK and parsed.task:
                await storage.save_task(user_id, parsed.task.title, parsed.task.due_date, parsed.task.priority, parsed.task.category)
                # Sync to Notion if user connected it
                if user_profile and user_profile.get("notion_api_key") and user_profile.get("notion_database_id"):
                    await notion_service.create_page(
                        user_profile["notion_api_key"],
                        user_profile["notion_database_id"],
                        parsed.task.title,
                        parsed.task.category,
                        parsed.task.due_date,
                        parsed.task.priority
                    )
            elif parsed.intent == IntentType.EXPENSE and parsed.expense:
                await storage.save_expense(user_id, parsed.expense.merchant, parsed.expense.amount, parsed.expense.currency, parsed.expense.category)

            reply = format_output(parsed, original_text=msg.text)
            await bot.send_message(chat_id=msg.chat.id, text=reply, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Error handling text: {e}")
            await bot.send_message(chat_id=msg.chat.id, text=f"⚠️ Error: {str(e)}")
        return

    # 8. Handle Voice
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
            
            # Persist to Supabase
            if parsed.intent == IntentType.TASK and parsed.task:
                await storage.save_task(user_id, parsed.task.title, parsed.task.due_date, parsed.task.priority, parsed.task.category)
                # Sync to Notion if user connected it
                if user_profile and user_profile.get("notion_api_key") and user_profile.get("notion_database_id"):
                    await notion_service.create_page(
                        user_profile["notion_api_key"],
                        user_profile["notion_database_id"],
                        parsed.task.title,
                        parsed.task.category,
                        parsed.task.due_date,
                        parsed.task.priority
                    )
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
