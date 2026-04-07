from __future__ import annotations

import asyncio
import base64
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from fastapi import WebSocket
from sqlalchemy.orm import Session

from app.models.db_models import Household, HouseholdSettings, Session as DBSession
from app.models.enums import AppMode, SessionStatus
from app.core.config import settings
from app.services.persistence import PersistenceService
from app.services.prompt_builders import (
    build_conversational_companion_prompt,
    build_story_teller_prompt,
)
from app.services.sarvam_llm import sarvam_llm_service
from app.services.sarvam_streaming import sarvam_streaming_service


@dataclass
class AudioChunkPayload:
    audio: str
    sample_rate: int = 16000
    encoding: str = "pcm_s16le"


@dataclass
class SessionUpdatePayload:
    active_mode: Optional[str] = None
    voice_style: Optional[str] = None
    current_object_name: Optional[str] = None
    current_object_category: Optional[str] = None


class LiveWebSocketSession:
    def __init__(
        self,
        websocket: WebSocket,
        db: Session,
        household: Household,
        settings: Optional[HouseholdSettings],
    ) -> None:
        self.websocket = websocket
        self.db = db
        self.household = household
        self.settings = settings
        self.session = self._get_or_create_session()
        self.stt_context = None
        self.stt_ws = None
        self.stt_task: Optional[asyncio.Task] = None
        self.stt_events: asyncio.Queue[dict] = asyncio.Queue()
        self.last_transcript: str = ""
        self.last_language_code: Optional[str] = None
        self.pending_audio_chunks: List[bytes] = []

    def _serialize_session(self) -> dict:
        return {
            "id": self.session.id,
            "household_id": self.session.household_id,
            "device_id": self.session.device_id,
            "active_mode": self.session.active_mode.value if self.session.active_mode else None,
            "voice_style": self.session.voice_style.value if self.session.voice_style else None,
            "status": self.session.status.value if self.session.status else None,
            "current_object_name": self.session.current_object_name,
            "current_object_category": self.session.current_object_category.value if self.session.current_object_category else None,
            "started_at": self.session.started_at.isoformat() if self.session.started_at else None,
            "last_activity_at": self.session.last_activity_at.isoformat() if self.session.last_activity_at else None,
        }

    def _get_or_create_session(self) -> DBSession:
        session = (
            self.db.query(DBSession)
            .filter(DBSession.household_id == self.household.id, DBSession.status != SessionStatus.ended)
            .order_by(DBSession.id.desc())
            .first()
        )
        if session:
            return session

        session = DBSession(
            household_id=self.household.id,
            active_mode=self.settings.default_mode if self.settings else AppMode.conversation,
            voice_style=self.settings.voice_style if self.settings else None,
            status=SessionStatus.active,
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow(),
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    async def start(self) -> None:
        await self.websocket.send_json({"type": "session.started", "data": self._serialize_session()})

    async def ensure_stt(self) -> bool:
        if self.stt_ws is not None and self.stt_task is not None:
            return True
        try:
            self.stt_context = await sarvam_streaming_service.open_stt()
            self.stt_ws = await self.stt_context.__aenter__()
            self.stt_task = asyncio.create_task(
                sarvam_streaming_service.collect_stt_events(self.stt_ws, self.stt_events)
            )
            return True
        except Exception as exc:
            await self.websocket.send_json({"type": "error", "data": {"message": str(exc)}})
            return False

    async def close(self) -> None:
        if self.stt_task:
            self.stt_task.cancel()
            with suppress(asyncio.CancelledError, Exception):
                await self.stt_task
        if self.stt_context is not None:
            with suppress(asyncio.CancelledError, Exception):
                await self.stt_context.__aexit__(None, None, None)

    async def apply_session_update(self, payload: SessionUpdatePayload) -> None:
        if payload.active_mode is not None:
            self.session.active_mode = AppMode(payload.active_mode)
        if payload.voice_style is not None:
            self.session.voice_style = payload.voice_style
        if payload.current_object_name is not None:
            self.session.current_object_name = payload.current_object_name
        if payload.current_object_category is not None:
            self.session.current_object_category = payload.current_object_category
        self.session.last_activity_at = datetime.utcnow()
        self.db.add(self.session)
        self.db.commit()
        self.db.refresh(self.session)
        await self.websocket.send_json({"type": "session.updated", "data": self._serialize_session()})

    async def handle_audio_chunk(self, payload: AudioChunkPayload) -> None:
        if not await self.ensure_stt():
            return
        if payload.encoding == "pcm_s16le":
            self.pending_audio_chunks.append(base64.b64decode(payload.audio))
            return

        await sarvam_streaming_service.send_stt_audio(
            self.stt_ws,
            audio_b64=payload.audio,
            sample_rate=payload.sample_rate,
            encoding=payload.encoding,
        )
        await self._drain_stt_events(partial_only=True)

    async def handle_flush(self) -> None:
        if not await self.ensure_stt():
            return
        if self.pending_audio_chunks:
            combined_audio = base64.b64encode(b"".join(self.pending_audio_chunks)).decode("utf-8")
            await sarvam_streaming_service.send_stt_audio(
                self.stt_ws,
                audio_b64=combined_audio,
                sample_rate=16000,
                encoding="pcm_s16le",
            )
            self.pending_audio_chunks = []
        await sarvam_streaming_service.flush_stt(self.stt_ws)
        transcript = await self._await_final_transcript()
        if not transcript:
            transcript = self.last_transcript or ""

        self.session.status = SessionStatus.active
        self.session.last_activity_at = datetime.utcnow()
        self.db.add(self.session)
        self.db.commit()

        await self.websocket.send_json({
            "type": "transcript.final",
            "data": {"text": transcript, "language_code": self.last_language_code},
        })

        system_prompt = (
            build_story_teller_prompt(self.session)
            if self.session.active_mode == AppMode.story_teller
            else build_conversational_companion_prompt(self.session)
        )
        user_message = transcript or "The child made a sound but no clear words were transcribed. Reply gently and briefly."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        reply_parts: List[str] = []
        async for delta in sarvam_llm_service.stream_completion(messages=messages):
            reply_parts.append(delta)
            await self.websocket.send_json({"type": "llm.delta", "data": {"text": delta}})
        reply_text = "".join(reply_parts).strip() or "Hello. I am here with you."
        await self.websocket.send_json({"type": "llm.completed", "data": {"text": reply_text}})

        speaker = "roopa" if self.session.voice_style and str(self.session.voice_style) == "story_narrator" else "shruti"
        target_language_code = settings.SARVAM_TTS_LANGUAGE
        tts_audio_parts: List[bytes] = []
        tts_codec = "mp3"
        async for event in sarvam_streaming_service.stream_tts(
            text=reply_text,
            target_language_code=target_language_code,
            speaker=speaker,
            pace=0.75,
        ):
            if event["kind"] == "audio":
                audio_b64 = event.get("audio", "")
                if audio_b64:
                    tts_audio_parts.append(base64.b64decode(audio_b64))
                tts_codec = event.get("codec", tts_codec)
            elif event["kind"] == "event" and event.get("event_type") == "final":
                combined_audio = base64.b64encode(b"".join(tts_audio_parts)).decode("utf-8")
                if combined_audio:
                    await self.websocket.send_json({
                        "type": "tts.chunk",
                        "data": {"audio": combined_audio, "codec": tts_codec, "kind": "audio"},
                    })
                await self.websocket.send_json({"type": "tts.completed", "data": {"codec": event.get("codec", tts_codec)}})

        persisted = PersistenceService.create_turn_discovery(
            db=self.db,
            session=self.session,
            transcript_text=transcript,
            reply_text=reply_text,
            detected_object_name=self.session.current_object_name if self.session.active_mode == AppMode.story_teller else None,
            object_category=self.session.current_object_category,
        )
        await self.websocket.send_json({
            "type": "discovery.created",
            "data": {
                "id": str(persisted.id),
                "title": persisted.title,
                "object_name": persisted.name,
                "object_category": persisted.category.value if persisted.category else None,
                "mode": persisted.mode.value if persisted.mode else "conversation",
                "summary": persisted.summary,
                "transcript": persisted.transcript,
                "reply_text": persisted.reply_text,
                "detected_object_name": persisted.detected_object_name,
                "is_favorite": persisted.is_favorite,
                "created_at": persisted.created_at.isoformat() if persisted.created_at else None,
            },
        })

    async def _drain_stt_events(self, *, partial_only: bool) -> None:
        while True:
            try:
                event = self.stt_events.get_nowait()
            except asyncio.QueueEmpty:
                return
            await self._process_stt_event(event, partial_only=partial_only)

    async def _await_final_transcript(self) -> str:
        latest = self.last_transcript
        deadline = asyncio.get_running_loop().time() + 3.0
        while asyncio.get_running_loop().time() < deadline:
            timeout = max(0.05, deadline - asyncio.get_running_loop().time())
            try:
                event = await asyncio.wait_for(self.stt_events.get(), timeout=timeout)
            except asyncio.TimeoutError:
                break
            final_text = await self._process_stt_event(event, partial_only=False)
            if final_text:
                latest = final_text
                break
        return latest

    async def _process_stt_event(self, event: dict, *, partial_only: bool) -> Optional[str]:
        if event.get("kind") == "error":
            await self.websocket.send_json({"type": "error", "data": {"message": event.get("message", "Unknown STT error")}})
            return None
        if event.get("kind") != "transcript":
            return None

        text = (event.get("text") or "").strip()
        if not text:
            return None
        self.last_transcript = text
        self.last_language_code = event.get("language_code")

        if event.get("is_final") and not partial_only:
            return text

        await self.websocket.send_json({
            "type": "transcript.partial",
            "data": {"text": text, "language_code": self.last_language_code},
        })
        return None
