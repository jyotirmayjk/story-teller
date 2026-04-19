from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DeviceCreate(BaseModel):
    device_uid: str

class DeviceResponse(BaseModel):
    id: int
    device_uid: str
    household_id: int
    registered_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ImageContextBase(BaseModel):
    detected_name: str
    detected_category: str
    confidence: int

class ImageContextResponse(ImageContextBase):
    id: int
    object_url: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
