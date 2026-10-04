import os
import json
import logging
from http.server import BaseHTTPRequestHandler
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton

from src.config import config
from src.router import router
from src.transcriber import transcriber
from src.models import IntentType
from src.storage import storage, FREE_MONTHLY_LIMIT, PRO_PRICE_STARS
from src.notion import notion_service
from src.solana_scanner import solana_scanner, PHANTOM_WALLET

logger = logging.getLogger(__name__)

bot = Bot(token=config.TELEGRAM_BOT_TOKEN) if config.TELEGRAM_BOT_TOKEN else None

TRUST_EVM_WALLET = "0xc51b89d77Efe2D19a6fe7A7cb5a8F587540b6b77"

def format_output(parsed, original_text: str = "", bot_name: str = "Mindflow") -> str:
    msg = f"{parsed.summary_message}\n\n"
    
    # Format all extracted tasks
    if parsed.tasks:
        msg += "📋 **Action Items:**\n"
        for t in parsed.tasks:
            due = f" • _Due: {t.due_date}_" if t.due_date else ""
            msg += f"• **{t.title}**{due} (_{t.category}_)\n"
        msg += "\n"
        
    # Format all extracted expenses
    if parsed.expenses:
        msg += "🧾 **Expenses Logged:**\n"
        for e in parsed.expenses:
            msg += f"• **{e.merchant}**: {e.currency} {e.amount:.2f} (_{e.category}_)\n"
        msg += "\n"
        
    if parsed.note:
        tags = " ".join([f"#{t}" for t in parsed.note.tags])
        msg += (
            f"📌 **Title:** {parsed.note.title}\n"
            f"{parsed.note.summary}\n"
            f"🏷 {tags}\n\n"
        )
        
    msg += f"_⚡ Synced to {bot_name} Inbox_"
    return msg

async def send_paywall(chat_id: int):
    """Sends native Telegram Stars invoice & Crypto payment options"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Pay with Crypto (USDT / $SOL)", callback_data="pay_crypto")]
    ])

    prices = [LabeledPrice(label="Mindflow Pro (Monthly)", amount=PRO_PRICE_STARS)]
    try:
        await bot.send_invoice(
            chat_id=chat_id,
            title="Mindflow Pro (Telegram Stars)",
            description="Unlimited voice captures, Notion sync, and custom naming.",
            payload="mindflow_pro_monthly",
            provider_token="", # Native Telegram Stars
            currency="XTR",
            prices=prices,
            start_parameter="pro_subscription"
        )
        await bot.send_message(chat_id=chat_id, text="Prefer paying with Crypto ($SOL / USDT)?", reply_markup=kb)
    except Exception as e:
        logger.error(f"Error sending paywall: {e}")
        await bot.send_message(chat_id=chat_id, text="💎 **Upgrade to Mindflow Pro ($4.99/mo)**", reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

async def send_crypto_instructions(chat_id: int, user_id: int):
    expected_sol = solana_scanner.get_user_expected_sol(user_id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Verify My Deposit On-Chain", callback_data="verify_sol")]
    ])

    crypto_msg = (
        "💎 **Automated On-Chain Crypto Upgrade ($5.00)**\n\n"
        "To prevent collisions and enable **1-click auto-activation**, your unique deposit amount is:\n\n"
        f"💰 **Exact Amount to Send:** `{expected_sol}` **SOL**\n\n"
        "🟣 **Solana Receiving Address (Phantom):**\n"
        f"`{PHANTOM_WALLET}`\n\n"
        "_(Tap any field to copy)_\n\n"
        "⚡ **Instructions:**\n"
        f"1. Send exactly `{expected_sol}` SOL from Phantom or Solflare.\n"
        "2. Once sent, tap **[ 🔍 Verify My Deposit On-Chain ]** below.\n"
        "3. Mindflow will verify the blockchain and unlock your Pro account instantly with zero wait time!"
    )
    await bot.send_message(chat_id=chat_id, text=crypto_msg, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

async def process_telegram_update(update_dict: dict):
    if not bot:
        return
    
    update = types.Update.model_validate(update_dict)

    # 1. Handle Callback Query (Buttons)
    if update.callback_query:
        cq = update.callback_query
        target_chat_id = cq.message.chat.id if cq.message else cq.from_user.id
        user_id = cq.from_user.id
        
        try:
            if cq.data == "pay_crypto":
                await bot.answer_callback_query(cq.id)
                await send_crypto_instructions(target_chat_id, user_id)
                return

            elif cq.data == "verify_sol":
                await bot.answer_callback_query(cq.id, text="🔍 Scanning Solana blockchain...")
                is_valid, msg_or_sig = await solana_scanner.verify_payment(user_id)
                
                if is_valid:
                    await storage.upgrade_user_to_pro(
                        user_id=user_id,
                        telegram_charge_id=msg_or_sig,
                        provider_charge_id="SOLANA_ON_CHAIN",
                        stars_amount=PRO_PRICE_STARS
                    )
                    success_text = (
                        "⭐️ **Payment Confirmed On-Chain!** ⭐️\n\n"
                        f"Transaction Hash:\n`{msg_or_sig}`\n\n"
                        "Your Mindflow Pro subscription is now **ACTIVE**!\n"
                        "Enjoy unlimited captures, custom naming, and Notion sync."
                    )
                    await bot.send_message(chat_id=target_chat_id, text=success_text, parse_mode=ParseMode.MARKDOWN)
                else:
                    await bot.send_message(
                        chat_id=target_chat_id, 
                        text=f"⚠️ {msg_or_sig}\n\n_If you just sent it, please give Solana 5–10 seconds to confirm and tap verify again!_"
                    )
                return
        except Exception as e:
            logger.error(f"Error handling callback query: {e}")
        return

    # 2. Handle Pre-Checkout Query
    if update.pre_checkout_query:
        await bot.answer_pre_checkout_query(pre_checkout_query_id=update.pre_checkout_query.id, ok=True)
        return

    if not update.message:
        return

    msg = update.message
    user_id = msg.from_user.id if msg.from_user else msg.chat.id
    username = msg.from_user.username if msg.from_user else None
    first_name = msg.from_user.first_name if msg.from_user else "Friend"
    
    # 3. Handle Successful Telegram Stars Payment
    if msg.successful_payment:
        pay = msg.successful_payment
        await storage.upgrade_user_to_pro(
            user_id=user_id,
            telegram_charge_id=pay.telegram_payment_charge_id,
            provider_charge_id=pay.provider_payment_charge_id,
            stars_amount=pay.total_amount
        )
        success_text = (
            "⭐️ **Welcome to Mindflow Pro!** ⭐️\n\n"
            "Your subscription is now active! All capture limits have been unlocked.\n"
            "Enjoy unlimited voice notes, Notion sync, and custom naming."
        )
        await bot.send_message(chat_id=msg.chat.id, text=success_text, parse_mode=ParseMode.MARKDOWN)
        return

    # Fetch user profile & custom bot name
    user_profile = None
    bot_name = "Mindflow"
    if storage.is_configured():
        user_profile = await storage.get_or_create_user(user_id, username, first_name)
        if user_profile and user_profile.get("bot_name"):
            bot_name = user_profile["bot_name"]

    # 4. Handle /start
    if msg.text and msg.text.startswith("/start"):
        welcome_text = (
            f"🌊 **Welcome to {bot_name}, {first_name}!**\n"
            "_Speak your mind. We handle the flow._\n\n"
            "**Quick Commands:**\n"
            "• `/tasks` — View your active priorities\n"
            "• `/expenses` — View recent logged expenses\n"
            "• `/briefing` — Get your daily morning agenda\n"
            "• `/rename <name>` — Give your assistant a personal name\n"
            "• `/upgrade` — Upgrade to Pro (Stars or Crypto)\n"
            "• `/notion` — Link your Notion workspace\n\n"
            "**How to capture:**\n"
            "• 🎙 **Voice note:** Hold mic and speak naturally.\n"
            "• 💬 **Text:** Thoughts, tasks, expenses, or say _\"From now on your name is Jarvis\"_!"
        )
        await bot.send_message(chat_id=msg.chat.id, text=welcome_text, parse_mode=ParseMode.MARKDOWN)
        return

    # 5. Handle /rename <name> shortcut
    if msg.text and msg.text.startswith("/rename"):
        parts = msg.text.strip().split(maxsplit=1)
        if len(parts) > 1:
            new_name = parts[1].strip()
            await storage.update_user_bot_name(user_id, new_name)
            await bot.send_message(chat_id=msg.chat.id, text=f"✨ Done! From now on, call me **{new_name}**. How can I assist you today?")
            return
        else:
            await bot.send_message(chat_id=msg.chat.id, text="Tip: Type `/rename Jarvis` or just say _\"From now on your name is Jarvis\"_!")
            return

    # 6. Handle /upgrade
    if msg.text and msg.text.startswith("/upgrade"):
        await send_paywall(msg.chat.id)
        return

    # 7. Handle /tasks
    if msg.text and msg.text.startswith("/tasks"):
        tasks = await storage.get_recent_tasks(user_id)
        if not tasks:
            await bot.send_message(chat_id=msg.chat.id, text="✨ **Inbox Zero!** You have no open tasks.\nSend a voice note to add one!")
            return
        
        reply = f"📋 **{bot_name}'s Priority Board:**\n\n"
        for idx, t in enumerate(tasks, 1):
            due = f" *(Due: {t.get('due_date')})*" if t.get('due_date') else ""
            reply += f"{idx}. **{t['title']}**{due}\n   └ 🏷 _{t.get('category', 'Personal')}_ • Priority: {t.get('priority', 'medium').capitalize()}\n"
        await bot.send_message(chat_id=msg.chat.id, text=reply, parse_mode=ParseMode.MARKDOWN)
        return

    # 8. Handle /expenses
    if msg.text and msg.text.startswith("/expenses"):
        expenses = await storage.get_recent_expenses(user_id)
        if not expenses:
            await bot.send_message(chat_id=msg.chat.id, text="💳 **No expenses recorded yet.**\nTry: _\"Spent $24 on lunch at Chipotle\"_")
            return
        
        total = sum(float(e.get('amount', 0)) for e in expenses)
        currency = expenses[0].get('currency', 'USD')
        reply = f"💰 **Recent Expenses (Total: {currency} {total:.2f}):**\n\n"
        for idx, e in enumerate(expenses, 1):
            reply += f"{idx}. **{e['merchant']}** — {e['currency']} {float(e['amount']):.2f} (_{e['category']}_)\n"
        await bot.send_message(chat_id=msg.chat.id, text=reply, parse_mode=ParseMode.MARKDOWN)
        return

    # 9. Handle /briefing
    if msg.text and msg.text.startswith("/briefing"):
        tasks = await storage.get_recent_tasks(user_id)
        greeting = f"☀️ **Good day, {first_name}!**\n\nHere is your {bot_name} Daily Briefing:\n\n"
        if tasks:
            greeting += "🎯 **Today's Key Focus Areas:**\n"
            for idx, t in enumerate(tasks[:3], 1):
                due = f" ({t.get('due_date')})" if t.get('due_date') else ""
                greeting += f"• **{t['title']}**{due}\n"
        else:
            greeting += "✨ Clean slate today! What are we conquering?\n"
        greeting += f"\n_{bot_name} is standing by._"
        await bot.send_message(chat_id=msg.chat.id, text=greeting, parse_mode=ParseMode.MARKDOWN)
        return

    # 10. Handle /connect_notion
    if msg.text and msg.text.startswith("/connect_notion"):
        parts = msg.text.strip().split()
        if len(parts) < 3:
            await bot.send_message(chat_id=msg.chat.id, text="⚠️ **Format:** `/connect_notion <NOTION_KEY> <DATABASE_ID>`")
            return
        success = await storage.update_user_notion(user_id, parts[1], parts[2])
        if success:
            await bot.send_message(chat_id=msg.chat.id, text="✅ **Notion Workspace Linked Successfully!**")
        else:
            await bot.send_message(chat_id=msg.chat.id, text="⚠️ Error saving your Notion credentials.")
        return

    # 11. Handle /notion guide
    if msg.text and msg.text.startswith("/notion"):
        notion_guide = (
            "📓 **Connect to Notion in 30 Seconds:**\n\n"
            "1. Duplicate the template: `https://mindflow.so/notion-template`\n"
            "2. Create a token at [notion.so/my-integrations](https://www.notion.so/my-integrations)\n"
            "3. Link by sending:\n"
            "`/connect_notion <YOUR_SECRET_KEY> <DATABASE_ID>`"
        )
        await bot.send_message(chat_id=msg.chat.id, text=notion_guide, parse_mode=ParseMode.MARKDOWN)
        return

    # ----------------------------------------------------
    # QUOTA CHECK (Freemium Paywall Gate)
    # ----------------------------------------------------
    can_execute, current_count, is_pro = await storage.can_user_execute(user_id)
    if not can_execute:
        await send_paywall(msg.chat.id)
        return

    # 12. Handle Text (including natural-language renaming)
    if msg.text:
        try:
            parsed = await router.parse_text(msg.text)
            
            # Handle Persona Rename (if present in compound message)
            if parsed.persona and parsed.persona.name:
                bot_name = parsed.persona.name
                await storage.update_user_bot_name(user_id, bot_name)

            new_count = await storage.increment_usage(user_id)
            
            # Save ALL parsed tasks
            for t in parsed.tasks:
                await storage.save_task(user_id, t.title, t.due_date, t.priority, t.category)
                if user_profile and user_profile.get("notion_api_key") and user_profile.get("notion_database_id"):
                    await notion_service.create_page(
                        user_profile["notion_api_key"], user_profile["notion_database_id"],
                        t.title, t.category, t.due_date, t.priority
                    )
                    
            # Save ALL parsed expenses
            for e in parsed.expenses:
                await storage.save_expense(user_id, e.merchant, e.amount, e.currency, e.category)

            reply = format_output(parsed, original_text=msg.text, bot_name=bot_name)
            if not is_pro and new_count >= 10:
                reply += f"\n_📊 Free Quota: {new_count}/{FREE_MONTHLY_LIMIT} captures used._"
            await bot.send_message(chat_id=msg.chat.id, text=reply, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Error handling text: {e}")
            await bot.send_message(chat_id=msg.chat.id, text=f"⚠️ Error: {str(e)}")
        return

    # 13. Handle Voice (including voice renaming)
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

            # Handle Persona Rename (if present in compound voice note)
            if parsed.persona and parsed.persona.name:
                bot_name = parsed.persona.name
                await storage.update_user_bot_name(user_id, bot_name)

            new_count = await storage.increment_usage(user_id)
            
            # Save ALL parsed tasks
            for t in parsed.tasks:
                await storage.save_task(user_id, t.title, t.due_date, t.priority, t.category)
                if user_profile and user_profile.get("notion_api_key") and user_profile.get("notion_database_id"):
                    await notion_service.create_page(
                        user_profile["notion_api_key"], user_profile["notion_database_id"],
                        t.title, t.category, t.due_date, t.priority
                    )
                    
            # Save ALL parsed expenses
            for e in parsed.expenses:
                await storage.save_expense(user_id, e.merchant, e.amount, e.currency, e.category)

            reply = f"📝 *Transcript:*\n_\"{transcript}\"_\n\n" + format_output(parsed, original_text=transcript, bot_name=bot_name)
            if not is_pro and new_count >= 10:
                reply += f"\n_📊 Free Quota: {new_count}/{FREE_MONTHLY_LIMIT} captures used._"
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
