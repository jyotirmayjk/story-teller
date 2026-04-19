from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from datetime import datetime
from app.models.db_models import Base
from app.models.enums import AppMode

# Adding Transcript Models
class Transcript(Base):
    """
    Stores the textual conversation chunks dynamically associated with sessions.
    Used for parental moderation and the Replay feature.
    """
    __tablename__ = "transcripts"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    discovery_id = Column(Integer, ForeignKey("discoveries.id"), nullable=True)
    
    speaker = Column(String) # 'user' or 'agent'
    mode = Column(SQLEnum(AppMode), nullable=True)
    text_content = Column(Text)
    audio_s3_key = Column(String, nullable=True) # Optional link to offline recorded blob
    
    created_at = Column(DateTime, default=datetime.utcnow)
