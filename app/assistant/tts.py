"""ElevenLabs akışlı TTS (PCM 24 kHz, 16-bit mono). Cümle başına bir istek."""
import re
from typing import AsyncIterator

import httpx

SAMPLE_RATE = 24000
_MD = re.compile(r"[*_#`>\[\]]+")
_BULLET = re.compile(r"^\s*([-•]|\d+[.)])\s+", re.M)


def clean_for_speech(text: str) -> str:
    return _MD.sub("", _BULLET.sub("", text)).strip()


class TTSError(Exception):
    pass


class ElevenLabsTTS:
    def __init__(self, api_key: str, voice_id: str, model_id: str, http: httpx.AsyncClient):
        self.api_key, self.voice_id, self.model_id, self.http = api_key, voice_id, model_id, http

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def stream(self, text: str) -> AsyncIterator[bytes]:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"
        async with self.http.stream(
            "POST", url,
            params={"output_format": f"pcm_{SAMPLE_RATE}"},
            headers={"xi-api-key": self.api_key},
            json={"text": text, "model_id": self.model_id, "language_code": "tr"},
        ) as r:
            if r.status_code != 200:
                body = (await r.aread()).decode(errors="ignore")[:300]
                raise TTSError(f"ElevenLabs {r.status_code}: {body}")
            async for chunk in r.aiter_bytes():
                if chunk:
                    yield chunk
