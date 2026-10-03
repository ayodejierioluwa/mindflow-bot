import os
import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode

from src.config import config
from src.router import router
from src.transcriber import transcriber
from src.models import IntentType

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

dp = Dispatcher()

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

@dp.message(CommandStart())
async def handle_start(message: types.Message):
    welcome_text = (
        "🧠 **Welcome to your AI Second Brain!**\n\n"
        "Never let a thought, task, or expense slip away.\n\n"
        "**How to use:**\n"
        "• 🎙 **Send a voice note:** Rambling thoughts, tasks, or follow-ups.\n"
        "• 💬 **Send a text message:** Quick tasks or braindump.\n"
        "• 🧾 **Send a receipt photo:** (Coming soon) Auto-logs expenses.\n\n"
        "Try sending a voice note or text like: \n"
        "_\"Spent $14 on lunch at Chipotle\"_ or \n"
        "_\"Call dentist to reschedule appointment tomorrow morning\"_"
    )
    await message.answer(welcome_text, parse_mode=ParseMode.MARKDOWN)

@dp.message(F.voice)
async def handle_voice(message: types.Message, bot: Bot):
    status_msg = await message.reply("🎧 _Listening and transcribing..._", parse_mode=ParseMode.MARKDOWN)
    
    try:
        # Download voice file
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        local_path = os.path.join(TEMP_DIR, f"{file_id}.ogg")
        
        await bot.download_file(file.file_path, local_path)
        
        # Transcribe
        await status_msg.edit_text("⚡ _Transcribing with Whisper..._", parse_mode=ParseMode.MARKDOWN)
        transcript = await transcriber.transcribe(local_path)
        
        # Clean up local audio file
        if os.path.exists(local_path):
            os.remove(local_path)
            
        # Parse intent
        await status_msg.edit_text(f"📝 *Transcript:*\n_\"{transcript}\"_\n\n🧠 _Organizing into Second Brain..._", parse_mode=ParseMode.MARKDOWN)
        parsed = await router.parse_text(transcript)
        
        # Format response
        response = _format_output(parsed, original_text=transcript)
        await status_msg.edit_text(response, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Error handling voice note: {e}", exc_info=True)
        await status_msg.edit_text(f"⚠️ Error processing voice note: {str(e)}")

@dp.message(F.text)
async def handle_text(message: types.Message):
    status_msg = await message.reply("🧠 _Processing..._", parse_mode=ParseMode.MARKDOWN)
    try:
        parsed = await router.parse_text(message.text)
        response = _format_output(parsed, original_text=message.text)
        await status_msg.edit_text(response, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error processing text: {e}", exc_info=True)
        await status_msg.edit_text(f"⚠️ Error: {str(e)}")

def _format_output(parsed, original_text: str = "") -> str:
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
    
    msg += "\n_⚡ Synced to Second Brain Inbox_"
    return msg

async def main():
    if not config.TELEGRAM_BOT_TOKEN:
        print("\n❌ Error: TELEGRAM_BOT_TOKEN is not set in .env!")
        print("1. Message @BotFather on Telegram to create your bot.")
        print("2. Copy the token into your .env file.\n")
        return

    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    logger.info("🚀 Second Brain Bot started successfully! Waiting for messages...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
