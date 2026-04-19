import asyncio
import websockets
import json
import httpx
import base64
import argparse

API_BASE = "http://localhost:8000/api/v1"
WS_BASE = "ws://localhost:8000/api/v1"
DEVICE_UID = "TEST_ESP32_001"
TEST_PROMPT = "Tell me a short fun fact about penguins for kids."
RESPONSE_TIMEOUT_SECONDS = 45
HOUSEHOLD_NAME = "Mobile Test Family"
DEFAULT_MODE = "conversation"

async def test_live_websocket(prompt: str, mode: str, timeout: int):
    print("🎯 Goal: Validate Gemini Live on Vertex via ADK by sending a test prompt and waiting for model reply.")
    print("🤖 1. Registering fake toy device...")
    async with httpx.AsyncClient() as client:
        # We need an admin/household token first (mocking login)
        login_res = await client.post(f"{API_BASE}/auth/login", json={"name": HOUSEHOLD_NAME})
        token = login_res.json()["data"]["access_token"]
        
        # Register the device hardware under this family
        reg_res = await client.post(
            f"{API_BASE}/device/register", 
            json={"device_uid": DEVICE_UID},
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"✅ Device Registered: {reg_res.json()}")

    print("\n🔌 2. Connecting to ADK WebSocket Gateway...")
    uri = f"{WS_BASE}/device/live?device_uid={DEVICE_UID}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket Connected!")

            # Test heartbeat
            await websocket.send(json.dumps({
                "type": "heartbeat", 
                "payload": None
            }))
            res = await websocket.recv()
            print(f"📥 Server Reply to Heartbeat: {res}")

            # Test Session Start
            await websocket.send(json.dumps({
                "type": "session_start", 
                "payload": None
            }))
            res = await websocket.recv()
            print(f"📥 Server Reply to Session Start: {res}")
            
            print("\n📝 3. Verifying app-created session context from DB...")
            from app.db.session import SessionLocal
            from app.models.db_models import Session, Device
            
            db = SessionLocal()
            device = db.query(Device).filter(Device.device_uid == DEVICE_UID).first()
            if device:
                active_sess = db.query(Session).filter(Session.device_id == device.id).order_by(Session.id.desc()).first()
                if active_sess:
                    if active_sess.active_mode is None:
                        raise RuntimeError("Active session has no mode. Complete onboarding or change mode in the app before running this test.")
                    if active_sess.active_mode.value != mode:
                        raise RuntimeError(
                            f"Active session mode is '{active_sess.active_mode.value}', but test expected '{mode}'. "
                            "Update the mode in the app or rerun with the matching --mode value."
                        )
                    if active_sess.current_object_name is None or active_sess.current_object_category is None:
                        raise RuntimeError(
                            "Active session is missing object/category context. Use the app flow that sets discovery context before running this test."
                        )
                    print(
                        "✅ Using app-created context -> "
                        f"Mode: {active_sess.active_mode.value}, "
                        f"Object: {active_sess.current_object_name}, "
                        f"Category: {active_sess.current_object_category.value}"
                    )
                else:
                    raise RuntimeError("No active device session found for the test device. Start a session from the app before running this test.")
            else:
                raise RuntimeError("Test device is not registered to the current household.")
            db.close()

            # Now send some fake text over to trigger the LLM to 'look' at the context we set
            print("\n🗣️ 4. Sending test prompt to Gemini Live (Vertex via ADK)...")
            
            await websocket.send(json.dumps({
                "type": "activity_start",
                "payload": None
            }))
            
            await websocket.send(json.dumps({
                "type": "text_message",
                "payload": {"text": prompt}
            }))
            
            await websocket.send(json.dumps({
                "type": "activity_end",
                "payload": None
            }))
            
            # Wait for response (transcript or audio)
            print(f"\n⏳ 5. Waiting for Gemini reply (timeout: {timeout}s)...")
            audio_data = bytearray()
            
            while True:
                try:
                    res = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                except asyncio.TimeoutError:
                    print(f"❌ Timeout: No Gemini response received within {timeout} seconds.")
                    break
                msg = json.loads(res)
                
                if msg.get("type") == "transcript_out":
                    print(f"📖 Vertex AI Transcript: {msg['payload']['text']}")
                elif msg.get("type") == "audio_out":
                    data_b64 = msg['payload']['data_base64']
                    audio_chunk = base64.b64decode(data_b64)
                    audio_data.extend(audio_chunk)
                    print(f"🔊 Received Audio Chunk: {len(audio_chunk)} bytes (Total: {len(audio_data)})")
                elif msg.get("type") == "turn_complete":
                     print("✅ Vertex AI Turn Complete.")
                     break
                elif msg.get("type") == "error":
                     print(f"❌ Error: {msg['payload']}")
                     break
            
            if audio_data:
                with open("output_response.pcm", "wb") as f:
                    f.write(audio_data)
                print(f"\n💾 Saved {len(audio_data)} bytes of raw PCM audio to 'output_response.pcm'")
            
            print("\n🎉 Live socket ADK routing works with the current app mode!")
            
    except Exception as e:
        print(f"❌ Connection failed. Is the server running? Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Gemini Live on Vertex via backend ADK websocket.")
    parser.add_argument(
        "--prompt",
        default=TEST_PROMPT,
        help="Prompt sent as text_message to Gemini Live.",
    )
    parser.add_argument(
        "--mode",
        choices=["conversation", "story_teller"],
        default=DEFAULT_MODE,
        help="Expected app mode for verification only; the test no longer writes mode into DB.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=RESPONSE_TIMEOUT_SECONDS,
        help="Seconds to wait for Gemini reply before timing out.",
    )
    args = parser.parse_args()
    asyncio.run(test_live_websocket(prompt=args.prompt, mode=args.mode, timeout=args.timeout))
