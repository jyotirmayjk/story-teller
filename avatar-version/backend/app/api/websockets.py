import asyncio
import base64
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.db_models import Session as DBSession, Device, HouseholdSettings
from app.schemas.live_events import DeviceLiveEvent, ServerLiveEvent
from app.adk_runtime.run_config_factory import RunConfigFactory

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.errors.already_exists_error import AlreadyExistsError
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.genai import types

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Global proxy for tracking active connections
session_service = InMemorySessionService()

@router.websocket("/live")
async def live_device_endpoint(websocket: WebSocket, device_uid: str, db: Session = Depends(get_db)):
    # 1: Initialization
    print(f"[WS-TRACE] new websocket request device_uid={device_uid}")
    logger.info("live_device_endpoint: new websocket request device_uid=%s", device_uid)
    device = db.query(Device).filter(Device.device_uid == device_uid).first()
    if not device:
        logger.warning("live_device_endpoint: unregistered device_uid=%s", device_uid)
        await websocket.close(code=4003, reason="Unregistered device")
        return

    from app.models.enums import SessionStatus
    active_session = db.query(DBSession).filter(DBSession.device_id == device.id, DBSession.status != SessionStatus.ended).first()
    settings = db.query(HouseholdSettings).filter(HouseholdSettings.household_id == device.household_id).first()
    if not active_session:
        active_session = DBSession(
            device_id=device.id,
            adk_session_key=f"session_{device_uid}",
            status=SessionStatus.active,
            household_id=device.household_id,
            active_mode=settings.default_mode if settings else None,
            voice_style=settings.voice_style if settings else None,
        )
        db.add(active_session)
        db.commit()
    elif settings:
        # Keep device sessions aligned with the latest app-selected household defaults.
        active_session.active_mode = settings.default_mode
        active_session.voice_style = settings.voice_style
        db.add(active_session)
        db.commit()

    await websocket.accept()
    print(f"[WS-TRACE] websocket accepted device_uid={device_uid} session_key={active_session.adk_session_key}")
    logger.info("live_device_endpoint: websocket accepted device_uid=%s session_key=%s", device_uid, active_session.adk_session_key)

    user_id = str(device.household_id)
    session_id = active_session.adk_session_key

    agent, run_config = RunConfigFactory.build_config(active_session, settings)
    
    # Consistent app_name to avoid runner warnings
    runner = Runner(app_name="agents", agent=agent, session_service=session_service)
    live_request_queue = LiveRequestQueue()

    # Create the ADK session in InMemorySessionService so run_live() can find it
    try:
        await session_service.create_session(
            app_name="agents",
            user_id=user_id,
            session_id=session_id,
        )
    except AlreadyExistsError:
        logger.info(
            "live_device_endpoint: reusing existing ADK session device_uid=%s session_id=%s",
            device_uid,
            session_id,
        )

    async def upstream_task():
        """Receives messages from WebSocket and sends to LiveRequestQueue."""
        try:
            while True:
                data = await websocket.receive_json()
                event = DeviceLiveEvent.model_validate(data)
                print(f"[WS-TRACE] upstream event type={event.type} device_uid={device_uid}")
                logger.info("upstream_task: received event type=%s device_uid=%s", event.type, device_uid)

                if event.type == "session_start":
                     await websocket.send_json(ServerLiveEvent(type="ack", payload={"status": "session_started"}).model_dump())
                elif event.type == "audio_chunk":
                     b64 = event.payload.get("data_base64") if event.payload else ""
                     if b64:
                         decoded = base64.b64decode(b64)
                         content = types.Content(parts=[types.Part(inline_data=types.Blob(mime_type="audio/pcm", data=decoded))])
                         live_request_queue.send_content(content)
                elif event.type == "text_message":
                     txt = event.payload.get("text") if event.payload else ""
                     if txt:
                         content = types.Content(parts=[types.Part(text=txt)])
                         live_request_queue.send_content(content)
                elif event.type == "image_frame":
                     b64 = event.payload.get("data_base64") if event.payload else ""
                     if b64:
                         decoded = base64.b64decode(b64)
                         content = types.Content(parts=[types.Part(inline_data=types.Blob(mime_type="image/jpeg", data=decoded))])
                         live_request_queue.send_content(content)
                elif event.type == "activity_start":
                     live_request_queue.send_activity_start()
                elif event.type == "activity_end":
                     live_request_queue.send_activity_end()
                elif event.type == "interrupt":
                     # ADK handles interruption via activity_start generally, 
                     # but we can also signal explicit interrupt if needed.
                     live_request_queue.send_activity_start()
                elif event.type == "heartbeat":
                     await websocket.send_json(ServerLiveEvent(type="ack").model_dump())
                     
        except WebSocketDisconnect:
            print(f"[WS-TRACE] upstream websocket disconnect device_uid={device_uid}")
            logger.info("upstream_task: websocket disconnect device_uid=%s", device_uid)
        except Exception as e:
            print(f"[WS-TRACE] upstream exception device_uid={device_uid}: {e}")
            logger.exception("upstream_task exception device_uid=%s: %s", device_uid, e)

    async def downstream_task():
        """Receives Events from run_live() and sends to WebSocket (wrapped in ServerLiveEvent)."""
        try:
            print(f"[WS-TRACE] downstream starting run_live device_uid={device_uid} session_id={session_id}")
            logger.info("downstream_task: starting runner.run_live device_uid=%s session_id=%s", device_uid, session_id)
            async for adk_event in runner.run_live(
                user_id=user_id,
                session_id=session_id,
                live_request_queue=live_request_queue,
                run_config=run_config
            ):
                print(
                    f"[WS-TRACE] downstream adk_event interrupted={bool(getattr(adk_event, 'interrupted', False))} "
                    f"has_server_content={bool(getattr(adk_event, 'server_content', None))} "
                    f"has_tool_call={bool(getattr(adk_event, 'tool_call', None))}"
                )
                logger.info(
                    "downstream_task: adk_event received interrupted=%s has_server_content=%s has_tool_call=%s",
                    bool(getattr(adk_event, "interrupted", False)),
                    bool(getattr(adk_event, "server_content", None)),
                    bool(getattr(adk_event, "tool_call", None)),
                )
                # 1. Check for global interruption flag (User spoke over Model)
                if hasattr(adk_event, 'interrupted') and adk_event.interrupted:
                    await websocket.send_json(ServerLiveEvent(type="interrupted").model_dump())
                    continue

                if hasattr(adk_event, 'server_content') and adk_event.server_content:
                    sc = adk_event.server_content
                    
                    # 2. Check for content-level interruption
                    if sc.interrupted:
                        await websocket.send_json(ServerLiveEvent(type="interrupted").model_dump())
                    
                    if sc.model_turn:
                        for part in sc.model_turn.parts:
                            # 3. Audio Delivery (24kHz from Gemini)
                            if part.inline_data:
                                audio_b64 = base64.b64encode(part.inline_data.data).decode('utf-8')
                                await websocket.send_json(ServerLiveEvent(
                                    type="audio_out", 
                                    payload={"data_base64": audio_b64}
                                ).model_dump())
                            
                            # 4. Transcripts
                            if part.text:
                                await websocket.send_json(ServerLiveEvent(
                                    type="transcript_out", 
                                    payload={"text": part.text, "is_partial": True, "speaker": "agent"}
                                ).model_dump())

                    if sc.turn_complete:
                        print(f"[WS-TRACE] downstream turn_complete device_uid={device_uid}")
                        logger.info("downstream_task: turn_complete sent device_uid=%s", device_uid)
                        await websocket.send_json(ServerLiveEvent(type="turn_complete").model_dump())
                else:
                    # ADK versions may emit model output on top-level event fields instead of server_content.
                    if getattr(adk_event, "output_transcription", None):
                        transcription = adk_event.output_transcription
                        if getattr(transcription, "text", None):
                            await websocket.send_json(ServerLiveEvent(
                                type="transcript_out",
                                payload={
                                    "text": transcription.text,
                                    "is_partial": not bool(getattr(transcription, "finished", False)),
                                    "speaker": "agent",
                                },
                            ).model_dump())

                    if getattr(adk_event, "content", None) and getattr(adk_event.content, "parts", None):
                        for part in adk_event.content.parts:
                            if getattr(part, "inline_data", None) and getattr(part.inline_data, "data", None):
                                audio_b64 = base64.b64encode(part.inline_data.data).decode("utf-8")
                                await websocket.send_json(ServerLiveEvent(
                                    type="audio_out",
                                    payload={"data_base64": audio_b64},
                                ).model_dump())
                            if getattr(part, "text", None):
                                await websocket.send_json(ServerLiveEvent(
                                    type="transcript_out",
                                    payload={"text": part.text, "is_partial": True, "speaker": "agent"},
                                ).model_dump())

                    if bool(getattr(adk_event, "turn_complete", False)):
                        print(f"[WS-TRACE] downstream turn_complete(top-level) device_uid={device_uid}")
                        logger.info("downstream_task: top-level turn_complete sent device_uid=%s", device_uid)
                        await websocket.send_json(ServerLiveEvent(type="turn_complete").model_dump())

                if hasattr(adk_event, 'tool_call'):
                    # Handle tool calls if any are defined later
                    pass
                
        except Exception as e:
            print(f"[WS-TRACE] downstream exception device_uid={device_uid}: {e}")
            logger.exception("downstream_task exception device_uid=%s: %s", device_uid, e)
            await websocket.send_json(ServerLiveEvent(type="error", payload={"detail": str(e)}).model_dump())

    try:
        print(f"[WS-TRACE] starting upstream/downstream tasks device_uid={device_uid}")
        logger.info("live_device_endpoint: starting upstream/downstream tasks device_uid=%s", device_uid)
        await asyncio.gather(upstream_task(), downstream_task(), return_exceptions=True)
    finally:
        print(f"[WS-TRACE] closing live_request_queue device_uid={device_uid}")
        logger.info("live_device_endpoint: closing live_request_queue device_uid=%s", device_uid)
        live_request_queue.close()
