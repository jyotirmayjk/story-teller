# Kids Pokédex — Backend

This is the active Python FastAPI backend for the browser-first `v2` flow.

## Features
- Browser-facing REST endpoints for login, settings, session state, discoveries, and activity
- Browser-facing live websocket at `/api/v1/app/live/ws`
- Sarvam-based STT, chat completion, and TTS flow for the child-facing voice experience
- Temporary token-store auth for the current prototype
- SQLAlchemy-backed persistence for sessions, discoveries, activity, and transcripts

## Local Development 

### Requirements
- Python 3.9+
- SQLite works by default for local testing
- Sarvam API key

### Setup Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure
Create a `.env` in the root:
```env
PROJECT_NAME="Kids Pokédex"
VERSION="1.0.0"
API_V1_STR="/api/v1"
SECRET_KEY="dev_key_only"
SARVAM_API_KEY="sk_..."
SARVAM_CHAT_MODEL="sarvam-30b"
SARVAM_STT_MODEL="saaras:v3"
SARVAM_STT_MODE="translate"
SARVAM_STT_LANGUAGE="unknown"
SARVAM_TTS_MODEL="bulbul:v3"
SARVAM_TTS_LANGUAGE="mr-IN"
SARVAM_TTS_SPEAKER="anand"
SARVAM_TTS_PACE=0.95
SARVAM_TTS_CODEC="mp3"
SARVAM_LLM_TEMPERATURE=0.2
SARVAM_LLM_MAX_TOKENS=180
SARVAM_LLM_REASONING_EFFORT=""
```

### Run Server
```bash
uvicorn app.main:app --reload --port 8000
```
