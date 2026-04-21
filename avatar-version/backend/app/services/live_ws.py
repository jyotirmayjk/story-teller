from __future__ import annotations

import asyncio
import base64
import re
import uuid
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
from app.services.runtime_trace import runtime_trace_service
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


@dataclass
class ConversationTurn:
    child_text: str
    assistant_text: str


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "big", "but", "do", "for", "go", "i", "in", "is", "it",
    "like", "me", "my", "of", "on", "saw", "see", "so", "that", "the", "there", "they", "this", "to",
    "today", "was", "we", "went", "what", "with", "you",
}
GENERIC_FALLBACK_REPLY = "Hello. I am here with you."
DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


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
        self.turn_open = False
        self.conversation_history: List[ConversationTurn] = []
        self.conversation_thread_id: Optional[str] = None
        self.conversation_turn_count = 0
        self.conversation_topic_anchor: Optional[str] = None

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
        if not self.turn_open:
            self._reset_turn_buffers()
            self.turn_open = True
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
        self.turn_open = False

        self.session.status = SessionStatus.active
        self.session.last_activity_at = datetime.utcnow()
        self.db.add(self.session)
        self.db.commit()

        await self.websocket.send_json({
            "type": "transcript.final",
            "data": {"text": transcript, "language_code": self.last_language_code},
        })

        is_conversation_mode = self.session.active_mode == AppMode.conversation
        if is_conversation_mode and self._should_start_new_conversation_thread(transcript):
            self._reset_conversation_thread()

        system_prompt = (
            build_story_teller_prompt(self.session, child_language_code=self.last_language_code)
            if self.session.active_mode == AppMode.story_teller
            else build_conversational_companion_prompt(
                self.session,
                recent_turns=[
                    {"child_text": turn.child_text, "assistant_text": turn.assistant_text}
                    for turn in self.conversation_history
                ],
                thread_turn_count=self.conversation_turn_count,
                topic_anchor=self.conversation_topic_anchor,
                should_ask_question=self._should_ask_follow_up_question(transcript),
                child_language_code=self.last_language_code,
            )
        )
        user_message = self._build_conversation_user_message(transcript) if is_conversation_mode else transcript
        if not user_message:
            user_message = "The child made a sound but no clear words were transcribed. Reply gently and briefly."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        reply_parts: List[str] = []
        async for delta in sarvam_llm_service.stream_completion(messages=messages):
            reply_parts.append(delta)
            await self.websocket.send_json({"type": "llm.delta", "data": {"text": delta}})
        reply_text = "".join(reply_parts).strip()
        if not reply_text:
            reply_text = (
                self._build_conversation_fallback_reply(transcript)
                if is_conversation_mode
                else self._build_story_teller_fallback_reply(transcript)
            )
        elif self.session.active_mode == AppMode.story_teller and self._asks_for_transcript(reply_text):
            reply_text = self._build_story_teller_fallback_reply(transcript)
        if self._should_force_marathi_fallback(reply_text):
            reply_text = (
                self._build_conversation_marathi_fallback_reply(transcript)
                if is_conversation_mode
                else self._build_story_teller_fallback_reply(transcript)
            )
        await self.websocket.send_json({"type": "llm.completed", "data": {"text": reply_text}})

        if is_conversation_mode:
            self._record_conversation_turn(transcript, reply_text)

        speaker = "roopa" if self.session.voice_style and str(self.session.voice_style) == "story_narrator" else "shruti"
        target_language_code = self._resolve_tts_language_code()
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

        runtime_trace_service.append_turn(
            {
                "session_id": self.session.id,
                "mode": self.session.active_mode.value if self.session.active_mode else "conversation",
                "stt": {
                    "transcript": transcript,
                    "language_code": self.last_language_code,
                    "model": settings.SARVAM_STT_MODEL,
                    "mode": settings.SARVAM_STT_MODE,
                },
                "llm": {
                    "reply_text": reply_text,
                    "model": settings.SARVAM_CHAT_MODEL,
                },
                "tts": {
                    "text": reply_text,
                    "model": settings.SARVAM_TTS_MODEL,
                    "speaker": speaker,
                    "target_language_code": target_language_code,
                    "codec": tts_codec,
                    "audio_bytes": sum(len(chunk) for chunk in tts_audio_parts),
                },
            }
        )

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

    def _record_conversation_turn(self, transcript: str, reply_text: str) -> None:
        if not transcript.strip() or not reply_text.strip():
            return
        if reply_text.strip() == GENERIC_FALLBACK_REPLY:
            return
        if not self.conversation_thread_id:
            self.conversation_thread_id = str(uuid.uuid4())

        self.conversation_history.append(
            ConversationTurn(
                child_text=transcript.strip(),
                assistant_text=reply_text.strip(),
            )
        )
        self.conversation_history = self.conversation_history[-3:]
        self.conversation_turn_count = min(self.conversation_turn_count + 1, 3)
        if not self.conversation_topic_anchor:
            self.conversation_topic_anchor = self._extract_topic_anchor(transcript)

    def _reset_conversation_thread(self) -> None:
        self.conversation_thread_id = str(uuid.uuid4())
        self.conversation_turn_count = 0
        self.conversation_history = []
        self.conversation_topic_anchor = None

    def _reset_turn_buffers(self) -> None:
        self.last_transcript = ""
        self.last_language_code = None
        self.pending_audio_chunks = []
        while True:
            try:
                self.stt_events.get_nowait()
            except asyncio.QueueEmpty:
                break

    def _tokenize_topic_words(self, text: str) -> set[str]:
        words = re.findall(r"[a-zA-Z']+", text.lower())
        return {word for word in words if len(word) > 2 and word not in STOPWORDS}

    def _build_conversation_fallback_reply(self, transcript: str) -> str:
        clean = transcript.strip()
        if not clean:
            return "I am listening. What would you like to tell me about?"

        topic_words = list(self._tokenize_topic_words(clean))
        if topic_words:
            subject = topic_words[0]
            return f"You noticed {subject}. What else did you see about it?"
        return "I heard you. Can you tell me a little more?"

    def _build_conversation_marathi_fallback_reply(self, transcript: str) -> str:
        clean = transcript.strip()
        if not clean:
            return "मी ऐकते आहे. मला अजून सांग ना."

        if self._is_short_followup(clean):
            return f"{clean} दिसलं तुला. मग काय झालं?"
        return f"तू म्हणालास, {clean} त्याबद्दल मला अजून सांग ना."

    def _build_story_teller_fallback_reply(self, transcript: str) -> str:
        clean = transcript.strip()
        lower = clean.lower()
        if not clean:
            return "I am listening. Tell me about an animal or object, and I will tell a little story."

        if self.last_language_code == "mr-IN":
            if "अजून" in clean:
                return "ही अजून एक छोटी गोष्ट आहे. एक गोड प्राणी हळूच चालत गेला, त्याला एक चमकदार खेळणे सापडले, आणि तो आनंदाने घरी परतला."
            return "ही एक छोटी, गोड गोष्ट आहे. एक मैत्रीपूर्ण छोटा मित्र सकाळी बाहेर गेला, त्याला काहीतरी छान सापडलं, आणि तो आनंदाने खेळत राहिला."

        if "another" in lower or "more" in lower:
            return "Here is another little story. A cheerful little friend found something bright and special, played with it happily, and then went home smiling."
        return "Here is a little story. A gentle little friend found something special, explored it with care, and ended the day feeling happy and safe."

    def _asks_for_transcript(self, reply_text: str) -> bool:
        lower = reply_text.lower()
        return (
            "share the transcript" in lower
            or "provide the transcript" in lower
            or "repeat the transcript" in lower
            or "clarify the transcript" in lower
            or "transcript" in lower
        )

    def _should_force_marathi_fallback(self, reply_text: str) -> bool:
        if self.last_language_code != "mr-IN":
            return False
        if not reply_text.strip():
            return False
        return DEVANAGARI_RE.search(reply_text) is None

    def _resolve_tts_language_code(self) -> str:
        if self.last_language_code in {"en-IN", "hi-IN", "mr-IN"}:
            return self.last_language_code
        return settings.SARVAM_TTS_LANGUAGE

    def _extract_topic_anchor(self, transcript: str) -> Optional[str]:
        topic_words = list(self._tokenize_topic_words(transcript))
        if topic_words:
            return topic_words[0]
        return None

    def _should_ask_follow_up_question(self, transcript: str) -> bool:
        clean = transcript.strip()
        if not clean:
            return False
        if not self.conversation_history:
            return True
        if self.conversation_turn_count >= 2:
            return False
        if self._is_short_followup(clean):
            return False
        return True

    def _is_short_followup(self, transcript: str) -> bool:
        words = re.findall(r"[a-zA-Z']+", transcript.strip())
        return 0 < len(words) <= 2

    def _build_conversation_user_message(self, transcript: str) -> str:
        clean = transcript.strip()
        if not clean:
            return ""
        if not self.conversation_history or not self._is_short_followup(clean):
            return clean

        last_turn = self.conversation_history[-1]
        anchor = self.conversation_topic_anchor or self._extract_topic_anchor(last_turn.child_text) or "the same subject"
        return (
            f"Current conversation subject: {anchor}\n"
            f"Previous assistant question: {last_turn.assistant_text}\n"
            f"Child's short answer: {clean}\n"
            "Treat this as a continuation of the same conversation and ask one grounded next question."
        )

    def _should_start_new_conversation_thread(self, transcript: str) -> bool:
        if not transcript.strip():
            return False
        if self.conversation_turn_count >= 3:
            return True
        if not self.conversation_history:
            return True

        new_words = self._tokenize_topic_words(transcript)
        if len(new_words) <= 1:
            return False

        previous_words: set[str] = set()
        for turn in self.conversation_history[-2:]:
            previous_words.update(self._tokenize_topic_words(turn.child_text))

        if not previous_words:
            return False

        return new_words.isdisjoint(previous_words)

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
