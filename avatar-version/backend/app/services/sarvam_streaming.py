from __future__ import annotations

import asyncio
import base64
import io
import wave
from collections.abc import AsyncIterator
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sarvamai import AsyncSarvamAI

from app.core.config import settings


class SarvamStreamingService:
    def __init__(self) -> None:
        self._client: Optional[AsyncSarvamAI] = None

    @property
    def client(self) -> AsyncSarvamAI:
        if not settings.SARVAM_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SARVAM_API_KEY is not configured",
            )
        if self._client is None:
            self._client = AsyncSarvamAI(api_subscription_key=settings.SARVAM_API_KEY)
        return self._client

    async def open_stt(self):
        return self.client.speech_to_text_streaming.connect(
            model=settings.SARVAM_STT_MODEL,
            mode=settings.SARVAM_STT_MODE,
            language_code=settings.SARVAM_STT_LANGUAGE,
            flush_signal=True,
            high_vad_sensitivity=True,
        )

    async def send_stt_audio(self, ws: Any, *, audio_b64: str, sample_rate: int, encoding: str) -> None:
        normalized_audio = audio_b64
        normalized_encoding = encoding

        if encoding == "pcm_s16le":
            pcm_bytes = base64.b64decode(audio_b64)
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(pcm_bytes)
            normalized_audio = base64.b64encode(wav_buffer.getvalue()).decode("utf-8")
            normalized_encoding = "audio/wav"

        await ws.transcribe(audio=normalized_audio, encoding=normalized_encoding, sample_rate=sample_rate)

    async def flush_stt(self, ws: Any) -> None:
        await ws.flush()

    async def collect_stt_events(self, ws: Any, queue: asyncio.Queue[dict]) -> None:
        try:
            while True:
                message = await ws.recv()
                normalized = self._normalize_stt_message(message)
                if normalized:
                    await queue.put(normalized)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            await queue.put({"kind": "error", "message": str(exc)})

    def _normalize_stt_message(self, message: Any) -> Optional[Dict]:
        if message is None:
            return None

        raw = self._to_dict(message)
        transcript = None
        language_code = None
        is_final = False
        event_type = None

        if isinstance(raw, dict):
            if "transcript" in raw:
                transcript = raw.get("transcript")
                language_code = raw.get("language_code")
            if "data" in raw and isinstance(raw["data"], dict):
                transcript = raw["data"].get("transcript", transcript)
                language_code = raw["data"].get("language_code", language_code)
                event_type = raw["data"].get("event_type") or raw.get("type")
            event_type = event_type or raw.get("event_type") or raw.get("type")
            is_final = bool(
                raw.get("is_final")
                or raw.get("final")
                or event_type in {"final", "end"}
                or raw.get("type") in {"final", "end"}
            )

        if transcript:
            return {
                "kind": "transcript",
                "text": str(transcript).strip(),
                "language_code": language_code,
                "is_final": is_final,
            }
        if event_type in {"final", "end"}:
            return {"kind": "event", "event_type": event_type}
        return None

    async def stream_tts(
        self,
        *,
        text: str,
        target_language_code: str,
        speaker: str,
        pace: float,
    ) -> AsyncIterator[dict]:
        async with self.client.text_to_speech_streaming.connect(
            model=settings.SARVAM_TTS_MODEL,
            send_completion_event=True,
        ) as ws:
            await ws.configure(
                target_language_code=target_language_code,
                speaker=speaker,
                pace=pace,
                output_audio_codec=settings.SARVAM_TTS_CODEC,
            )
            await ws.convert(text)
            await ws.flush()

            async for message in ws:
                raw = self._to_dict(message)
                audio_b64 = self._extract_tts_audio(raw)
                if audio_b64:
                    yield {"kind": "audio", "audio": audio_b64, "codec": settings.SARVAM_TTS_CODEC}
                    continue
                event_type = self._extract_event_type(raw)
                if event_type:
                    yield {"kind": "event", "event_type": event_type, "codec": settings.SARVAM_TTS_CODEC}
                    if event_type == "final":
                        break

    def _extract_tts_audio(self, raw: Any) -> Optional[str]:
        if isinstance(raw, dict):
            data = raw.get("data", raw)
            if isinstance(data, dict):
                audio = data.get("audio")
                if isinstance(audio, str):
                    base64.b64decode(audio, validate=True)
                    return audio
        return None

    def _extract_event_type(self, raw: Any) -> Optional[str]:
        if isinstance(raw, dict):
            data = raw.get("data", raw)
            if isinstance(data, dict):
                event_type = data.get("event_type") or raw.get("event_type")
                if isinstance(event_type, str):
                    return event_type
        return None

    def _to_dict(self, message: Any) -> Any:
        if isinstance(message, dict):
            return message
        if hasattr(message, "model_dump"):
            return message.model_dump()
        if hasattr(message, "dict"):
            return message.dict()
        if hasattr(message, "__dict__"):
            return {
                key: self._to_dict(value)
                for key, value in vars(message).items()
                if not key.startswith("_")
            }
        if isinstance(message, list):
            return [self._to_dict(item) for item in message]
        return message


sarvam_streaming_service = SarvamStreamingService()
