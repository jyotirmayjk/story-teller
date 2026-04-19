# Instructions

## Overview

This repository now contains two browser-related backend implementations:

- `web/`
  React + Vite browser client
- `browserbackend/`
  Older browser-oriented FastAPI backend kept as a reference implementation

The active browser flow now lives in:

- `backend/`

The `backend/` folder has been updated to expose the browser live socket contract and uses a temporary in-memory token store for the current prototype. Treat `browserbackend/` as reference code, not the primary runtime.

## Folder roles

### Frontend

Path:
- `web/`

Purpose:
- Runs the browser UI
- Connects to REST and WebSocket endpoints exposed by `backend`

### Browser backend

Primary path:
- `backend/`

Purpose:
- Provides login, settings, session, discoveries, and live voice endpoints for the browser app
- Uses Sarvam for:
  - STT
  - chat completions
  - TTS
- Uses a temporary token store for browser auth in this version
- Does not require JWT websocket auth in this version

## Prerequisites

You should have:

- Python 3.9+ or newer
- Node.js and npm
- A valid Sarvam API key

Note:
- `backend` should be run with a Python environment that has the dependencies from `backend/requirements.txt`.

## 1. Start the browser backend

### Backend path

Use:
- `backend/`

### Backend environment

Create:
- `backend/.env`

Example contents:

```env
PROJECT_NAME="Kids Pokédex"
VERSION="1.0.0"
API_V1_STR="/api/v1"

SARVAM_API_KEY=sk_...
SARVAM_CHAT_MODEL=sarvam-30b
SARVAM_STT_MODEL=saaras:v3
SARVAM_STT_MODE=transcribe
SARVAM_STT_LANGUAGE=unknown
SARVAM_TTS_MODEL=bulbul:v3
SARVAM_TTS_LANGUAGE=en-IN
SARVAM_TTS_SPEAKER=anand
SARVAM_TTS_PACE=0.95
SARVAM_TTS_CODEC=mp3
SARVAM_LLM_TEMPERATURE=0.2
SARVAM_LLM_MAX_TOKENS=180
SARVAM_LLM_REASONING_EFFORT=
```

Notes:
- The current browser-first version is voice-only. Image recognition is not part of the active runtime.
- The current backend uses a temporary token store for browser auth instead of JWT websocket validation.

### Backend install

From:
- [backend](/Users/jk/Code/sarvamai/v2/backend)

Run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you see:

```bash
zsh: no such file or directory: .venv/bin/uvicorn
```

it means the virtualenv has not been created yet in `backend/`. Run the install block above first.

If you are using Python `3.9.x`, make sure the environment can install everything in `backend/requirements.txt`.

### Backend launch

From:
- [backend](/Users/jk/Code/sarvamai/v2/backend)

After the virtualenv exists, you can either launch using the full venv path:

```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Or, if you already activated the virtualenv with `source .venv/bin/activate`, you can run:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend URL:
- `http://127.0.0.1:8000`

Validated local launch:
- `browserbackend` was started successfully with Python `3.9.6`
- command:

```bash
cd /Users/jk/Code/sarvamai/kids-pokedex-sarvam/browserbackend
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Important endpoints:
- `POST /api/v1/auth/login`
- `GET/PATCH /api/v1/app/settings/`
- `GET /api/v1/app/session/current`
- `POST /api/v1/app/session/start`
- `PATCH /api/v1/app/session/current`
- `POST /api/v1/app/session/end`
- `GET /api/v1/app/discoveries/`
- `POST /api/v1/app/discoveries/{id}/favorite`
- `POST /api/v1/app/discoveries/{id}/replay`
- `POST /api/v1/app/live/image/recognize`
- `WS /api/v1/app/live/ws?token=<token>`

## 2. Start the Vite frontend

### Frontend environment

Create:
- `web/.env`

Recommended contents:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_WS_BASE_URL=ws://127.0.0.1:8000/api/v1
VITE_DEFAULT_HOUSEHOLD_NAME=Web Explorer Family
```

You can also use `localhost`, but using `127.0.0.1` consistently tends to make local debugging less ambiguous.

### Frontend install

From:
- [web](/Users/jk/Code/sarvamai/kids-pokedex-sarvam/web)

Run:

```bash
npm install
```

### Frontend launch

From:
- [web](/Users/jk/Code/sarvamai/kids-pokedex-sarvam/web)

Run:

```bash
npm run dev -- --host 127.0.0.1 --port 5173
```

Frontend URL:
- `http://127.0.0.1:5173/`

## 3. Recommended launch order

1. Start `browserbackend` on port `8000`
2. Start `web` on port `5173`
3. Open [http://127.0.0.1:5173/](http://127.0.0.1:5173/)
4. Let the app bootstrap and log in
5. Confirm the UI shows:
   - `Socket connected`
6. Test push-to-talk

## 4. Quick run commands

### Terminal 1

```bash
cd /Users/jk/Code/sarvamai/kids-pokedex-sarvam/browserbackend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Terminal 2

```bash
cd /Users/jk/Code/sarvamai/kids-pokedex-sarvam/web
npm run dev -- --host 127.0.0.1 --port 5173
```

## 5. How the browser flow works

### Login and bootstrap

The frontend:
- logs in through `POST /api/v1/auth/login`
- loads settings
- starts or resumes the current app session
- opens the live websocket:
  - `ws://127.0.0.1:8000/api/v1/app/live/ws?token=<token>`

### Push-to-talk

The frontend:
- captures browser mic audio as `pcm_s16le`
- sends repeated `audio.chunk` messages
- sends `audio.flush` when the user stops talking

The backend:
- buffers the PCM chunks
- sends them to Sarvam STT
- gets a transcript
- calls Sarvam chat completions
- synthesizes the final answer with Sarvam TTS
- sends audio back to the browser

## 6. Validated fixes already included

These behaviors are now part of `browserbackend/` and `web/`:

- frontend websocket lifecycle is stabilized
- bootstrap runs once per page load
- React Strict Mode remount churn is removed from the frontend entry point
- browser audio playback waits for actual playback completion
- backend STT buffering/flush behavior matches push-to-talk
- backend TTS chunks are joined correctly as bytes before being returned
- browser backend no longer sends `max_tokens` in the Sarvam completions request

## 7. Troubleshooting

### If the page says `Socket disconnected`

Check:

1. Is the backend running on `127.0.0.1:8000`?
2. Is the frontend running on `127.0.0.1:5173`?
3. Does `web/.env` point to `127.0.0.1:8000`?
4. Refresh the page after restarting either server

Useful checks:

```bash
curl http://127.0.0.1:8000/api/v1/app/settings/
curl -I http://127.0.0.1:5173
```

### If backend startup fails with a type-annotation error

Example:

```bash
TypeError: Unable to evaluate type annotation 'str | None'
```

Status:
- this was fixed in `browserbackend`
- the committed `browserbackend` code now runs on Python `3.9` without requiring Python `3.10+`

If you still see this error:
- make sure you are starting [browserbackend](/Users/jk/Code/sarvamai/kids-pokedex-sarvam/browserbackend), not an older copied folder
- recreate the virtualenv if needed

### If transcript appears but the spoken reply is wrong or too short

Check backend logs in `browserbackend`.

Important clue:
- if Sarvam returns `reasoning_content` but `message.content` is `null`, the assistant may fall back instead of speaking a real answer

The current code avoids the earlier `max_tokens` issue, which was the main cause of that problem during debugging.

### If audio sounds cut off

Check:

1. that the frontend is the current code from `web/`
2. that the backend is the current code from `browserbackend/`
3. that you restarted both servers after code changes

## 8. Which backend to use

For browser work, use:
- [browserbackend](/Users/jk/Code/sarvamai/kids-pokedex-sarvam/browserbackend)

Do not use:
- [backend](/Users/jk/Code/sarvamai/kids-pokedex-sarvam/backend)

unless you specifically intend to work with the original non-browser implementation.

## 9. Related docs

- [changelog.md](/Users/jk/Code/sarvamai/kids-pokedex-sarvam/changelog.md)
- [web/README.md](/Users/jk/Code/sarvamai/kids-pokedex-sarvam/web/README.md)
- [browserbackend/README.md](/Users/jk/Code/sarvamai/kids-pokedex-sarvam/browserbackend/README.md)
