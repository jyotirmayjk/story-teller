from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.security import get_current_household, require_ws_household
from app.db.session import get_db
from app.models.db_models import Household, HouseholdSettings
from app.services.live_ws import AudioChunkPayload, LiveWebSocketSession, SessionUpdatePayload

router = APIRouter()


@router.websocket("/ws")
async def live_ws(websocket: WebSocket, db: Session = Depends(get_db)) -> None:
    await websocket.accept()
    try:
        household = await require_ws_household(websocket, db)
    except RuntimeError:
        return

    settings = db.query(HouseholdSettings).filter(HouseholdSettings.household_id == household.id).first()
    live = LiveWebSocketSession(websocket=websocket, db=db, household=household, settings=settings)
    await live.start()

    try:
        while True:
            message = await websocket.receive_json()
            message_type = message.get("type")
            data = message.get("data", {})

            if message_type == "session.update":
                await live.apply_session_update(SessionUpdatePayload(**data))
            elif message_type == "audio.chunk":
                await live.handle_audio_chunk(AudioChunkPayload(**data))
            elif message_type == "audio.flush":
                await live.handle_flush()
            elif message_type == "ping":
                await websocket.send_json({"type": "pong", "data": {}})
            else:
                await websocket.send_json({"type": "error", "data": {"message": f"Unknown message type: {message_type}"}})
    except WebSocketDisconnect:
        pass
    finally:
        await live.close()
