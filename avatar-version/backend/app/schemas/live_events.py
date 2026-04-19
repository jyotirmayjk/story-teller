from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from app.models.enums import AppMode, VoiceStyle

class DeviceLiveEvent(BaseModel):
    # Base envelope for WS events
    type: str # 'session_start', 'audio_chunk', 'audio_end', 'activity_start', 'activity_end', 'image_frame', 'interrupt', 'heartbeat'
    payload: Optional[Any] = None

class ServerLiveEvent(BaseModel):
    # Base envelope for WS replies
    type: str # 'ack', 'listening', 'speaking', 'audio_out', 'transcript_out', 'fallback', 'turn_complete', 'error'
    payload: Optional[Any] = None

class LiveAudioChunk(BaseModel):
    # PCM 16-bit little-endian base64 chunk
    data_base64: str

class LiveTranscriptEvent(BaseModel):
    text: str
    is_partial: bool
    speaker: str # 'user' or 'agent'
