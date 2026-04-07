from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models.enums import AppMode, VoiceStyle, ObjectCategory

class HouseholdSettingsBase(BaseModel):
    voice_style: VoiceStyle = VoiceStyle.friendly_cartoon
    default_mode: AppMode = AppMode.conversation
    allowed_categories: List[str] = [ObjectCategory.animals.value, ObjectCategory.vehicles.value, ObjectCategory.toys.value, ObjectCategory.household_objects.value]

class HouseholdSettingsUpdate(BaseModel):
    voice_style: Optional[VoiceStyle] = None
    default_mode: Optional[AppMode] = None
    allowed_categories: Optional[List[str]] = None

class HouseholdSettingsResponse(HouseholdSettingsBase):
    id: int
    household_id: int
    model_config = ConfigDict(from_attributes=True)

class HouseholdBase(BaseModel):
    name: str

class HouseholdCreate(HouseholdBase):
    pass

class HouseholdResponse(HouseholdBase):
    id: int
    created_at: datetime
    settings: Optional[HouseholdSettingsResponse] = None
    model_config = ConfigDict(from_attributes=True)

class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
