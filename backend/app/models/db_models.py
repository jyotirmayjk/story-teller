from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, ARRAY, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from .enums import AppMode, VoiceStyle, SessionStatus, ObjectCategory, ResponseType

Base = declarative_base()

# To ensure all tables are registered under the same Base for generic imports:
from .transcripts import Transcript

class Household(Base):
    __tablename__ = "households"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    settings = relationship("HouseholdSettings", back_populates="household", uselist=False)
    devices = relationship("Device", back_populates="household")
    sessions = relationship("Session", back_populates="household")

class HouseholdSettings(Base):
    __tablename__ = "household_settings"
    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"), unique=True)
    voice_style = Column(SQLEnum(VoiceStyle), default=VoiceStyle.friendly_cartoon)
    default_mode = Column(SQLEnum(AppMode), default=AppMode.conversation)
    allowed_categories = Column(JSON, default=["animals", "vehicles", "toys", "household_objects"])
    
    household = relationship("Household", back_populates="settings")

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    device_uid = Column(String, unique=True, index=True) # Hardware ID
    household_id = Column(Integer, ForeignKey("households.id"))
    registered_at = Column(DateTime, default=datetime.utcnow)
    
    household = relationship("Household", back_populates="devices")
    sessions = relationship("Session", back_populates="device")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))
    
    active_mode = Column(SQLEnum(AppMode))
    voice_style = Column(SQLEnum(VoiceStyle))
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.connecting)
    
    current_image_context_id = Column(Integer, ForeignKey("image_contexts.id"), nullable=True)
    current_object_name = Column(String, nullable=True)
    current_object_category = Column(SQLEnum(ObjectCategory), nullable=True)
    
    adk_session_key = Column(String, index=True, nullable=True)
    transport_connection_id = Column(String, nullable=True)
    resumable = Column(Boolean, default=True)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    household = relationship("Household", back_populates="sessions")
    device = relationship("Device", back_populates="sessions")
    image_context = relationship("ImageContext")
    discoveries = relationship("Discovery", back_populates="session")
    activities = relationship("ActivityEvent", back_populates="session")

class ImageContext(Base):
    __tablename__ = "image_contexts"
    id = Column(Integer, primary_key=True, index=True)
    object_url = Column(String) # Path to object storage
    detected_name = Column(String)
    detected_category = Column(SQLEnum(ObjectCategory))
    confidence = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class Discovery(Base):
    __tablename__ = "discoveries"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    image_context_id = Column(Integer, ForeignKey("image_contexts.id"))

    mode = Column(SQLEnum(AppMode), nullable=True)
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    reply_text = Column(Text, nullable=True)
    detected_object_name = Column(String, nullable=True)
    name = Column(String, nullable=True)
    category = Column(SQLEnum(ObjectCategory), nullable=True)
    is_favorite = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="discoveries")
    image_context = relationship("ImageContext")

class ActivityEvent(Base):
    """
    Log of continuous actions (spoken, discovered, interrupted, modes changes)
    """
    __tablename__ = "activity_events"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    event_type = Column(String) # e.g 'audio_turn_started', 'response_streamed'
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="activities")
