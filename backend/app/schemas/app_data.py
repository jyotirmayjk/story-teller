from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.enums import AppMode, ObjectCategory

class DiscoveryBase(BaseModel):
    title: str
    mode: AppMode
    summary: str
    object_name: Optional[str] = None
    object_category: Optional[ObjectCategory] = None
    transcript: Optional[str] = None
    reply_text: Optional[str] = None
    is_favorite: bool = False

class DiscoveryCreate(DiscoveryBase):
    session_id: int
    image_context_id: Optional[int] = None

class DiscoveryResponse(DiscoveryBase):
    id: int
    session_id: int
    detected_object_name: Optional[str] = None
    created_at: datetime
    # Object storage presigned URLs will populate this on demand
    image_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ActivityEventBase(BaseModel):
    event_type: str
    metadata_json: Optional[dict] = None

class ActivityEventCreate(ActivityEventBase):
    session_id: int

class ActivityEventResponse(ActivityEventBase):
    id: int
    session_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
