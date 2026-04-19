from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_household
from app.db.session import get_db
from app.models.db_models import Household, HouseholdSettings, Session as DBSession
from app.models.enums import AppMode, ObjectCategory, SessionStatus, VoiceStyle

router = APIRouter()


def _serialize_session(session: DBSession) -> dict:
    return {
        "id": session.id,
        "household_id": session.household_id,
        "device_id": session.device_id,
        "active_mode": session.active_mode.value if session.active_mode else None,
        "voice_style": session.voice_style.value if session.voice_style else None,
        "status": session.status.value if session.status else None,
        "current_object_name": session.current_object_name,
        "current_object_category": session.current_object_category.value if session.current_object_category else None,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "last_activity_at": session.last_activity_at.isoformat() if session.last_activity_at else None,
    }


@router.get("/current", response_model=dict)
def get_current_session(
    household: Household = Depends(get_current_household),
    db: Session = Depends(get_db),
):
    current_session = (
        db.query(DBSession)
        .filter(DBSession.household_id == household.id, DBSession.status != SessionStatus.ended)
        .order_by(DBSession.id.desc())
        .first()
    )
    if not current_session:
        raise HTTPException(status_code=404, detail="No active session found")

    return {"data": _serialize_session(current_session)}


@router.post("/start", response_model=dict)
def start_session(
    payload: Optional[dict] = None,
    household: Household = Depends(get_current_household),
    db: Session = Depends(get_db),
):
    payload = payload or {}
    settings = db.query(HouseholdSettings).filter(HouseholdSettings.household_id == household.id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Household settings not found")

    existing_session = (
        db.query(DBSession)
        .filter(DBSession.household_id == household.id, DBSession.status != SessionStatus.ended)
        .order_by(DBSession.id.desc())
        .first()
    )
    if existing_session:
        existing_session.active_mode = settings.default_mode
        existing_session.voice_style = settings.voice_style
        existing_session.last_activity_at = datetime.utcnow()

        if payload.get("current_object_name") is not None:
            existing_session.current_object_name = payload.get("current_object_name")
        if payload.get("current_object_category") is not None:
            category_value = payload.get("current_object_category")
            existing_session.current_object_category = ObjectCategory(category_value) if category_value else None

        db.add(existing_session)
        db.commit()
        db.refresh(existing_session)
        return {"data": _serialize_session(existing_session)}

    category_value = payload.get("current_object_category")
    category = None
    if category_value:
        category = ObjectCategory(category_value)

    session = DBSession(
        household_id=household.id,
        active_mode=settings.default_mode,
        voice_style=settings.voice_style,
        status=SessionStatus.active,
        current_object_name=payload.get("current_object_name"),
        current_object_category=category,
        last_activity_at=datetime.utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"data": _serialize_session(session)}


@router.post("/end", response_model=dict)
def end_session(
    household: Household = Depends(get_current_household),
    db: Session = Depends(get_db),
):
    current_session = (
        db.query(DBSession)
        .filter(DBSession.household_id == household.id, DBSession.status != SessionStatus.ended)
        .order_by(DBSession.id.desc())
        .first()
    )
    if not current_session:
        raise HTTPException(status_code=404, detail="No active session found")

    current_session.status = SessionStatus.ended
    current_session.ended_at = datetime.utcnow()
    current_session.last_activity_at = datetime.utcnow()
    db.add(current_session)
    db.commit()
    db.refresh(current_session)
    return {"data": _serialize_session(current_session)}


@router.patch("/current", response_model=dict)
def update_current_session(
    payload: Optional[dict] = None,
    household: Household = Depends(get_current_household),
    db: Session = Depends(get_db),
):
    current_session = (
        db.query(DBSession)
        .filter(DBSession.household_id == household.id, DBSession.status != SessionStatus.ended)
        .order_by(DBSession.id.desc())
        .first()
    )
    if not current_session:
        raise HTTPException(status_code=404, detail="No active session found")

    payload = payload or {}

    if payload.get("active_mode"):
        current_session.active_mode = AppMode(payload["active_mode"])
    if payload.get("voice_style"):
        current_session.voice_style = VoiceStyle(payload["voice_style"])
    if "current_object_name" in payload:
        current_session.current_object_name = payload.get("current_object_name")
    if "current_object_category" in payload:
        category_value = payload.get("current_object_category")
        current_session.current_object_category = ObjectCategory(category_value) if category_value else None
    if payload.get("status"):
        current_session.status = SessionStatus(payload["status"])

    current_session.last_activity_at = datetime.utcnow()
    db.add(current_session)
    db.commit()
    db.refresh(current_session)
    return {"data": _serialize_session(current_session)}
