from sqlalchemy.orm import Session
from typing import Optional
from app.models.transcripts import Transcript
from app.models.enums import AppMode

class TranscriptPersistenceService:
    @staticmethod
    def save_transcript(
        db: Session,
        session_id: int,
        text: str,
        speaker: str,
        discovery_id: int = None,
        mode: Optional[AppMode] = None,
    ) -> Transcript:
        """
        Records the final text chunks spoken by either the User or Agent.
        Partial transcripts are NOT saved, as per specification rules.
        """
        transcript = Transcript(
            session_id=session_id,
            speaker=speaker,
            mode=mode,
            text_content=text,
            discovery_id=discovery_id
        )
        db.add(transcript)
        db.commit()
        db.refresh(transcript)
        return transcript

    @staticmethod
    def get_session_transcripts(db: Session, session_id: int) -> list[Transcript]:
        return db.query(Transcript).filter(Transcript.session_id == session_id).order_by(Transcript.created_at).all()
