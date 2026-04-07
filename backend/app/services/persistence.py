from sqlalchemy.orm import Session
from typing import Optional
from app.models.db_models import Discovery, Session as DBSession, ActivityEvent
from app.models.enums import AppMode, ObjectCategory
from app.services.transcript_persistence import TranscriptPersistenceService

class PersistenceService:
    @staticmethod
    def create_discovery(db: Session, session: DBSession) -> Optional[Discovery]:
        """
        Derives a new Discovery securely from the current Session context
        Only creates one if an active image context & valid category exists.
        """
        if not session.current_image_context_id or not session.current_object_name:
            return None
            
        # Optional constraint check: ensure not already discovered recently
        existing = db.query(Discovery).filter(
            Discovery.session_id == session.id,
            Discovery.name == session.current_object_name
        ).first()
        
        if existing:
            return existing

        new_discovery = Discovery(
            session_id=session.id,
            image_context_id=session.current_image_context_id,
            name=session.current_object_name,
            category=session.current_object_category
        )
        
        db.add(new_discovery)
        
        # Log mapping event
        event = ActivityEvent(
            session_id=session.id,
            event_type="discovery_created",
            metadata_json={"object_name": new_discovery.name, "category": new_discovery.category.value}
        )
        db.add(event)
        
        db.commit()
        db.refresh(new_discovery)
        return new_discovery

    @staticmethod
    def create_turn_discovery(
        db: Session,
        session: DBSession,
        transcript_text: str,
        reply_text: str,
        detected_object_name: Optional[str] = None,
        object_category: Optional[ObjectCategory] = None,
    ) -> Discovery:
        safe_mode = session.active_mode or AppMode.conversation
        title = "Story Teller" if safe_mode == AppMode.story_teller else "Conversation"
        summary_source = reply_text.strip() or transcript_text.strip() or "Completed voice turn"
        summary = summary_source[:240]

        discovery = Discovery(
            session_id=session.id,
            image_context_id=session.current_image_context_id,
            mode=safe_mode,
            title=title,
            summary=summary,
            transcript=transcript_text.strip() or None,
            reply_text=reply_text.strip() or None,
            detected_object_name=detected_object_name,
            name=detected_object_name or session.current_object_name,
            category=object_category or session.current_object_category,
        )
        db.add(discovery)
        db.flush()

        if transcript_text.strip():
            TranscriptPersistenceService.save_transcript(
                db=db,
                session_id=session.id,
                text=transcript_text.strip(),
                speaker="user",
                discovery_id=discovery.id,
                mode=safe_mode,
            )
        if reply_text.strip():
            TranscriptPersistenceService.save_transcript(
                db=db,
                session_id=session.id,
                text=reply_text.strip(),
                speaker="agent",
                discovery_id=discovery.id,
                mode=safe_mode,
            )

        event = ActivityEvent(
            session_id=session.id,
            event_type="voice_turn_persisted",
            metadata_json={
                "mode": safe_mode.value,
                "detected_object_name": detected_object_name,
                "object_category": (object_category or session.current_object_category).value
                if (object_category or session.current_object_category)
                else None,
            },
        )
        db.add(event)
        db.commit()
        db.refresh(discovery)
        return discovery
        
    @staticmethod
    def log_activity(db: Session, session_id: int, event_type: str, metadata: dict = None):
         event = ActivityEvent(
             session_id=session_id,
             event_type=event_type,
             metadata_json=metadata or {}
         )
         db.add(event)
         db.commit()
