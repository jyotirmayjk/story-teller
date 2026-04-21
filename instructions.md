# Instructions

## Overview

This repository contains two local development flows:

- Normal app: the screen-based Story Teller experience with `Conversation`, `Story Teller`, and `Settings`.
- Avatar version: an isolated avatar-first version with a duck companion, copied backend/frontend, and a Chrome extension prototype.

The two versions intentionally run on different ports so they can be tested side by side without colliding.

## Prerequisites

You should have:

- Python 3.9 or newer
- Node.js and npm
- A valid Sarvam API key

Local environment files such as `.env`, `.env.local`, virtualenvs, build outputs, and runtime logs should not be committed.

## Normal Version

### Backend

Path:

```text
<project-directory>/backend
```

Install once:

```bash
cd <project-directory>/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Start backend on `8010`:

```bash
cd <project-directory>/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
```

Backend URL:

```text
http://127.0.0.1:8010/
```

### Frontend

Path:

```text
<project-directory>/web
```

Install once:

```bash
cd <project-directory>/web
npm install
cp .env.example .env.local
```

Use these frontend environment values:

```env
VITE_API_BASE_URL=http://127.0.0.1:8010/api/v1
VITE_WS_BASE_URL=ws://127.0.0.1:8010/api/v1
```

Start frontend on `5173`:

```bash
cd <project-directory>/web
npm run dev -- --host 127.0.0.1 --port 5173
```

Open:

```text
http://127.0.0.1:5173/
```

## Avatar Version

### Backend

Path:

```text
<project-directory>/avatar-version/backend
```

Install once:

```bash
cd <project-directory>/avatar-version/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Start avatar backend on `8020`:

```bash
cd <project-directory>/avatar-version/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8020
```

Backend URL:

```text
http://127.0.0.1:8020/
```

### Frontend

Path:

```text
<project-directory>/avatar-version/web
```

Install once:

```bash
cd <project-directory>/avatar-version/web
npm install
cp .env.example .env.local
```

Use these frontend environment values:

```env
VITE_API_BASE_URL=http://127.0.0.1:8020/api/v1
VITE_WS_BASE_URL=ws://127.0.0.1:8020/api/v1
```

Start avatar frontend on `5174`:

```bash
cd <project-directory>/avatar-version/web
npm run dev -- --host 127.0.0.1 --port 5174
```

Open:

```text
http://127.0.0.1:5174/
```

### Chrome Extension

To test the avatar extension:

1. Start the avatar backend on `8020`.
2. Open Chrome Extensions.
3. Enable Developer mode.
4. Choose Load unpacked.
5. Select `<project-directory>/avatar-version/extension`.
6. Open a normal webpage.
7. Click the floating duck to start and stop recording.

The extension bypasses onboarding by creating a temporary backend session and connecting directly to the avatar backend websocket.

## Quick Launch Commands

### Normal backend

```bash
cd <project-directory>/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
```

### Normal frontend

```bash
cd <project-directory>/web
npm run dev -- --host 127.0.0.1 --port 5173
```

### Avatar backend

```bash
cd <project-directory>/avatar-version/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8020
```

### Avatar frontend

```bash
cd <project-directory>/avatar-version/web
npm run dev -- --host 127.0.0.1 --port 5174
```

## Runtime Flow

The browser captures microphone audio as `pcm_s16le` chunks and sends them over the live websocket. The backend sends audio to Sarvam STT, passes the transcript to the Sarvam LLM, streams the reply through Sarvam TTS, and sends the final audio/text back to the frontend or extension.

Core models:

- STT: `saaras:v3`
- LLM: `sarvam-30b`
- TTS: `bulbul:v3`

## Logs

Normal runtime traces:

```text
backend/runtime_logs/voice_turns.jsonl
```

Avatar-version runtime traces:

```text
avatar-version/backend/runtime_logs/voice_turns.jsonl
```

These logs are for local debugging and should stay untracked.
