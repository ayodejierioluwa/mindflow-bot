import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    NOTION_API_KEY: Optional[str] = os.getenv("NOTION_API_KEY")
    NOTION_DATABASE_ID: Optional[str] = os.getenv("NOTION_DATABASE_ID")

config = Config()
