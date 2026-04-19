# Kids Pokédex - App Mode Testing Plan

This document outlines the testing strategy for the three main modes of the Kids Pokédex app (Story, Learn, and Explorer), records the progress made so far, and documents current technical issues.

## 📋 Overall Testing Scope

The goal is to verify the end-to-end "Scan and Speak" loop:
1. **Selection**: User selects a mode on the Mobile App.
2. **Context**: Backend receives the mode and object context (e.g., "Story" + "Penguin").
3. **Simulation**: Simulated or real device connects via WebSocket.
4. **Generation**: Vertex AI Live Agent generates a context-aware response using the Gemini Live BIDI stream.
5. **Output**: Device receives streamed audio and displays transcripts.

---

## ⚡ Steps Taken So Far

### 1. Protocol Alignment
- **ServerLiveEvent**: Updated `websockets.py` to wrap all outgoing messages in the `ServerLiveEvent` envelope required by the ESP32 firmware.
- **WebSocket Gateway**: Refined the `live_request_queue` to handle incoming audio and text messages.

### 2. Backend Bug Fixes
- **ADK Session Initialization**: Fixed a critical bug where the ADK `InMemorySessionService` was not creating a session before `runner.run_live()` was called, leading to "Session not found" errors.
- **Database Corruption**: Resolved a Pydantic/SQLAlchemy crash caused by an invalid enum value ("Mythical Creature") injected during early testing.
- **Text-Fallback Support**: Added a `text_message` handler to the live WebSocket so we can trigger the AI turn using text strings instead of needing high-quality PCM audio files during simulation.

### 3. Environment & Credentials
- **Vertex AI Configuration**: Updated `.env` with real Project ID and specified `GOOGLE_GENAI_USE_VERTEXAI=TRUE`.
- **Startup Injection**: Modified `main.py` to force-set Vertex AI environment variables at application startup to ensure the ADK client picks them up.

---

## 🛑 Current Issues & Blockers

### 1. Vertex AI Model Availability (Close Code 1008)
The primary blocker is finding a model that is both **Live API compatible** and **enabled for your project/region**.
- **`gemini-2.0-flash-exp`**: Deprecated or inaccessible.
- **`gemini-2.5-flash-native-audio-preview-...`**: Returns `policy violation (1008)`. This usually means the model is not yet whitelisted for Vertex AI project-auth in your specific region (`us-central1` or `global`).
- **`gemini-2.5-flash`**: Available in the project but returns `not supported in the live api` when used over WebSockets.

### 2. Audio Format Alignment
- The system is configured for **16kHz 16-bit Mono PCM** input. We need to ensure the firmware (ESP32) and the test scripts send exactly this format to avoid "Static" or "Garbled" AI understanding.

---

## 🚀 Future Testing Steps

### Phase 1: Model Verification (Next Immediate Task)
- [ ] Verify if `gemini-2.0-flash-001` succeeds on Vertex AI.
- [ ] If Vertex AI continues to fail, consider temporary use of **Google AI Studio API Key** to verify logic before returning to Vertex.

### Phase 2: Mode Validation
- [ ] **Story Mode**: Inject "Story" mode + "Penguin" -> Verify AI tells a children's story about a penguin.
- [ ] **Learn Mode**: Inject "Learn" mode + "Car" -> Verify AI teaches 3 facts about cars.
- [ ] **Explorer Mode**: Inject "Explorer" mode + "Tree" -> Verify AI asks engaging questions about nature.

### Phase 3: Hardware Integration
- [ ] Connect the ESP32 firmware to the backend.
- [ ] Test real-time VAD (Voice Activity Detection) triggers.
- [ ] Verify audio playback quality on the I2S speaker.

---

## Model Test Runbook (`test_ws.py` + Backend Server)

This runbook is the concrete plan to validate model behavior end-to-end using the backend WebSocket gateway and `backend/test_ws.py`.

Primary goal:
- Verify Gemini Live on Vertex AI (through ADK `run_live`) by sending a deterministic test prompt and confirming a model reply (`transcript_out` and/or `audio_out`) followed by `turn_complete`.

### 1. Preconditions

- Backend dependencies installed (`pip install -r backend/requirements.txt`).
- Valid model credentials configured in backend env (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, auth).
- Backend starts without errors.
- Database is available and writable.

### 2. Start Backend Server

From project root:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected:
- REST API reachable at `http://localhost:8000/api/v1`.
- WebSocket route reachable at `ws://localhost:8000/api/v1/device/live?device_uid=...`.

### 3. Execute Baseline Script

In a second terminal:

```bash
cd backend
python test_ws.py
```

What this validates:
- Device registration/login flow.
- WebSocket connection and heartbeat ACK.
- Session start ACK.
- Text-triggered model turn via `activity_start -> text_message -> activity_end`.
- Model output events (`transcript_out`, optional `audio_out`, `turn_complete`).

Pass criteria:
- Script reaches `turn_complete` without `error`.
- Non-empty transcript for the active context.
- If audio is emitted, `output_response.pcm` is written with non-zero bytes.

Fail criteria:
- WebSocket close `1008` (model access/policy issue).
- `error` payload from backend or ADK runner.
- No transcript/audio before timeout.

### 4. Mode-by-Mode Validation Plan

Run the same script 3 times, changing the injected DB context in `test_ws.py`:

- Story Mode: `active_mode=story`, object `Happy Little Penguin`.
- Learn Mode: `active_mode=learn`, object `Car`.
- Explorer Mode: `active_mode=explorer`, object `Tree`.

For each run, record:
- Transcript content quality (mode alignment).
- Time to first token/audio.
- Turn completion status.
- Any backend exceptions.

### 5. Suggested Results Template

Use this table for each mode:

| Mode | Prompt | Transcript Matches Mode? | Audio Emitted? | Turn Complete? | Notes |
|------|--------|---------------------------|----------------|----------------|-------|
| Story | What is this? | Yes/No | Yes/No | Yes/No | ... |
| Learn | What is this? | Yes/No | Yes/No | Yes/No | ... |
| Explorer | What is this? | Yes/No | Yes/No | Yes/No | ... |

### 6. Troubleshooting Branches

- If `1008` persists on Vertex:
  - Switch to a known Live-API-compatible model available to the project/region.
  - Re-run baseline script to confirm infra path before mode-quality checks.
- If text works but audio does not:
  - Validate downstream `audio_out` events in backend logs.
  - Confirm PCM handling and file write path in `test_ws.py`.
- If session/device errors appear:
  - Check auth/login response and `device_uid` consistency.
  - Verify DB session row creation in `app/api/websockets.py`.
