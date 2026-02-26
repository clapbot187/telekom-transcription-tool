import json
from pathlib import Path
from typing import Optional

import requests

from .config import Config


class WhisperClient:
    def __init__(self, config: Config):
        self.config = config

    def transcribe(self, audio_path: Path) -> Optional[str]:
        if not self.config.is_valid:
            raise ValueError("API key not configured")

        try:
            with open(audio_path, "rb") as audio_file:
                files = {"file": (audio_path.name, audio_file, "audio/wav")}
                data = {"model": self.config.WHISPER_MODEL}
                headers = {"Authorization": f"Bearer {self.config.api_key}"}

                response = requests.post(
                    self.config.WHISPER_ENDPOINT,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=300
                )
                response.raise_for_status()

                result = response.json()
                return result.get("text", "")
        except requests.exceptions.RequestException as e:
            print(f"Transcription request failed: {e}")
            return None
        except Exception as e:
            print(f"Transcription error: {e}")
            return None


class GPTClient:
    def __init__(self, config: Config):
        self.config = config

    def enhance(self, text: str, prompt_template: Optional[str] = None) -> Optional[str]:
        if not self.config.is_valid:
            raise ValueError("API key not configured")

        system_prompt = prompt_template or (
            "You are a helpful assistant. Improve the following transcription "
            "by fixing grammar, punctuation, and clarity while preserving the original meaning."
        )

        payload = {
            "model": self.config.GPT_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please improve this text: {text}"}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                self.config.GPT_ENDPOINT,
                headers=self.config.get_headers(),
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            result = response.json()
            choices = result.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
            return None
        except requests.exceptions.RequestException as e:
            print(f"Enhancement request failed: {e}")
            return None
        except Exception as e:
            print(f"Enhancement error: {e}")
            return None


class APIClient:
    def __init__(self, config: Config):
        self.whisper = WhisperClient(config)
        self.gpt = GPTClient(config)
