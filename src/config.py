import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    WHISPER_MODEL = "whisper-large-v3"
    GPT_MODEL = "gpt-4.1-mini"

    def __init__(self, config_path: Optional[str] = None):
        self.api_key: Optional[str] = os.getenv("TRANSCRIPTION_API_KEY")
        self.WHISPER_ENDPOINT: str = os.getenv(
            "WHISPER_ENDPOINT",
            "https://llm-server.llmhub.t-systems.net/v2/audio/transcriptions"
        )
        self.GPT_ENDPOINT: str = os.getenv(
            "GPT_ENDPOINT",
            "https://llm-server.llmhub.t-systems.net/v2/chat/completions"
        )
        self.sample_rate: int = int(os.getenv("SAMPLE_RATE", "16000"))
        self.channels: int = int(os.getenv("CHANNELS", "1"))
        self.chunk_duration: float = 0.5

    @property
    def is_valid(self) -> bool:
        return self.api_key is not None and len(self.api_key) > 0

    def get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
