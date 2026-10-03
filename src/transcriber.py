import os
import logging
from typing import Optional
from src.config import config

logger = logging.getLogger(__name__)

class AudioTranscriber:
    def __init__(self):
        self.groq_key = config.GROQ_API_KEY
        self.openai_key = config.OPENAI_API_KEY

    async def transcribe(self, file_path: str) -> str:
        """
        Transcribes audio file (.ogg, .mp3, .m4a) to text.
        Prefers Groq (blazing fast <0.5s & free tier) or OpenAI Whisper.
        """
        if self.groq_key:
            return await self._transcribe_groq(file_path)
        elif self.openai_key:
            return await self._transcribe_openai(file_path)
        else:
            return "Mock transcription: 'Remember to review the quarterly marketing budget with Sarah tomorrow at 2 PM and buy coffee beans.'"

    async def _transcribe_groq(self, file_path: str) -> str:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=self.groq_key)
        
        with open(file_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                file=(os.path.basename(file_path), audio_file.read()),
                model="whisper-large-v3-turbo",
                response_format="json",
                language="en",
                temperature=0.0
            )
            return transcription.text

    async def _transcribe_openai(self, file_path: str) -> str:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self.openai_key)
        
        with open(file_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
            )
            return transcription.text

transcriber = AudioTranscriber()
