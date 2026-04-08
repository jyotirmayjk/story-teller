# Changelog

## Standalone repo follow-up fixes

### Multi-turn Conversation memory

Files:
- `backend/app/services/live_ws.py`
- `backend/app/services/prompt_builders.py`
- `web/src/store/liveStore.ts`
- `web/src/hooks/useLiveSocket.ts`
- `web/src/components/child-facing/ConversationDisplay.tsx`
- `web/src/screens/live/ChildLiveScreen.tsx`

Changes:
- Added a short conversation memory window for `conversation` mode in the backend runtime.
- Passed the last 1-2 child/assistant turns into the conversation prompt.
- Added a 3-turn topic cap so conversation threads stay short and child-friendly.
- Displayed one previous turn in the `Conversation` UI so continuity is visible to the user.

Problems addressed:
- Conversation mode previously behaved like one isolated prompt per turn.
- The assistant could not meaningfully continue a 2-3 turn exchange because it had no short-term context.

Example issue:
- Child: `I saw a dog.`
- Assistant: `A dog. What color was the dog?`
- Child: `Brown.`
- Before this change, the next response could behave like a fresh conversation instead of a continuation.

### STT turn-reset fix

Files:
- `backend/app/services/live_ws.py`
- `web/src/hooks/usePushToTalk.ts`
- `web/src/screens/live/ChildLiveScreen.tsx`

Changes:
- Reset backend turn-local transcript buffers and queued STT events when a new utterance begins.
- Cleared the current visible turn in the frontend when push-to-talk begins.

Problems addressed:
- The second turn of STT could reuse stale transcript state from the previous turn.
- This made later turns feel random or contaminated by earlier speech.

Example issue:
- First turn: `I saw a bus today.`
- Second turn could unexpectedly reuse or blend earlier detected speech if the new utterance was weak.

### Conversation fallback cleanup

Files:
- `backend/app/services/live_ws.py`
- `web/src/store/liveStore.ts`

Changes:
- Replaced the generic fallback `Hello. I am here with you.` for `conversation` mode with a more grounded fallback question.
- Prevented that generic fallback from being stored as a meaningful prior conversation turn in the UI/history.

Problems addressed:
- A non-specific fallback reply was polluting the conversation memory and making previous-turn context misleading.

Example issue:
- Previous turn panel showed:
  - Child: `I saw a bus today.`
  - Assistant: `Hello. I am here with you.`
- That created a bad context window for the next turn.

### Short-answer topic anchoring

Files:
- `backend/app/services/live_ws.py`
- `backend/app/services/prompt_builders.py`

Changes:
- Added a lightweight in-memory topic anchor for each short conversation thread.
- Strengthened the prompt so 1-2 word answers are treated as answers to the previous question, not new scenes.
- For short follow-ups, changed the user message sent to the LLM to include:
  - current subject
  - previous assistant question
  - latest short child answer

Problems addressed:
- Very short STT outputs were being taken too literally and could derail an otherwise coherent thread.

Example issues from runtime logs:
- `I saw a dog.` -> assistant: `You saw a dog. What did the dog do?`
- child follow-up transcribed as `Heating.` -> assistant replied: `What was the dog heating?`
- `Running in the garden.` -> assistant: `Did it see any flowers?`
- child follow-up: `White flower.` -> assistant replied: `You see a white flower. Can you show me the white flower?`

These examples showed that prior turns were being passed correctly, but short fragments still needed stronger subject anchoring.

### JSONL runtime trace

Files:
- `backend/app/core/config.py`
- `backend/app/services/runtime_trace.py`
- `backend/app/services/live_ws.py`

Changes:
- Added a runtime JSONL log that appends one record per completed voice turn.
- Each record captures:
  - STT transcript and language code
  - final LLM reply text
  - TTS text and metadata

Output file:
- `backend/runtime_logs/voice_turns.jsonl`

Problems addressed:
- There was no persistent turn-by-turn trace to inspect STT, LLM, and TTS behavior together.
- Debugging conversation continuity required manually inferring behavior from the UI.

Example use:
- Comparing consecutive entries showed that prompt continuity was working while STT on very short utterances remained the weak link.

## Summary

This document captures the browser live-runtime work completed during the Sarvam voice debugging session. The scope covered a new dedicated `browserbackend` service based on the working Sarvam temp backend, frontend websocket stability, browser playback fixes, and a long debugging pass across STT, LLM, and TTS behavior.

## Main Repository Changes

### Dedicated browser backend

Files:
- `browserbackend/README.md`
- `browserbackend/requirements.txt`
- `browserbackend/app/...`

Changes:
- Added a new `browserbackend` folder and copied over the full working Sarvam browser backend from the temp implementation.
- Preserved the original `backend` folder instead of replacing or rewriting it.
- Brought over the live websocket flow, in-memory session handling, STT/TTS integrations, prompt building, discovery persistence, and browser-facing API/router structure.
- Kept the working Sarvam completions behavior that was validated during debugging, including the request-shape fixes that stopped the model from returning only `reasoning_content`.

Why this was needed:
- The working Sarvam browser backend lived only in `/tmp`, which was not versioned. Creating `browserbackend` made the successful implementation part of the repository without disturbing the existing ADK/Gemini backend.

### Frontend runtime stability and playback fixes

Files:
- `web/src/hooks/useAudioPlayback.ts`
- `web/src/hooks/useBootstrap.ts`
- `web/src/hooks/useLiveSocket.ts`
- `web/src/main.tsx`
- `web/src/screens/home/HomeScreen.tsx`
- `web/src/store/liveStore.ts`
- `web/src/styles/global.css`

Changes:
- Kept the live websocket client stable across renders by storing it in a ref and using up-to-date handler refs instead of reconnecting on broad dependency changes.
- Fixed bootstrap behavior so it runs once per page load instead of repeatedly re-fetching settings and session state.
- Removed `React.StrictMode` from the web entry point to avoid dev-only remount churn during the live audio session.
- Changed audio playback handling to wait for the audio element to actually finish instead of treating `audio.play()` success as playback completion.
- Added a temporary mic debug panel to surface chunk counts, flush counts, last chunk size, and send success for browser-side debugging.

Why this was needed:
- The frontend was reconnecting and reinitializing during live turns, which caused socket instability and made voice playback appear broken.

### Repository hygiene

Files:
- `.gitignore`
- `changelog.md`

Changes:
- Added web build and dependency outputs to `.gitignore`.
- Added ignore rules for `browserbackend/.venv` and cache outputs.
- Added this changelog to preserve the debugging trail and the actual fixes applied.

## Temp Backend Changes Applied During Debugging

These changes were made in the temp backend copy at `/tmp/whimsicalexplorer2_sarvam_streaming_backend`. That directory is not a git repository, so these edits were not committed there directly. They are documented here because they were essential to resolving the live voice path.

Key temp-backend files touched:
- `/tmp/whimsicalexplorer2_sarvam_streaming_backend/app/services/live_ws.py`
- `/tmp/whimsicalexplorer2_sarvam_streaming_backend/app/services/sarvam_llm.py`

### STT flow fixes

Changes:
- Fixed the STT session startup path so the websocket session awaited the STT open call correctly.
- Buffered raw PCM mic chunks during push-to-talk and sent them on flush instead of trying to forward them incorrectly chunk-by-chunk.
- Added route-level and live-session debug prints to confirm arrival of `audio.chunk`, `audio.flush`, `stt.partial`, and `stt.final`.

Symptoms addressed:
- No transcript returned after push-to-talk.
- Sarvam STT websocket closing with `Cannot flush: no audio input has been received.`

### LLM troubleshooting and fallback

Changes:
- Printed the full system prompt and user transcript being sent to the Sarvam chat completions endpoint.
- Printed the full request payload for completions.
- Printed the full raw response body or stream events coming back from Sarvam.
- Added a temporary fallback text of `Hi I will tell you a story` whenever completions returned no assistant content.
- Switched the completion integration from streamed parsing to non-streamed `message.content` parsing to match the documented sample more closely.
- Removed the explicit `max_tokens` field from the Sarvam request payload.

What we found:
- The request shape itself was valid.
- With `max_tokens` set, the model repeatedly returned `reasoning_content` with `content: null` and `finish_reason: "length"`.
- After removing `max_tokens`, the model returned usable assistant text again and the voice response started working.

### TTS and browser playback path

Changes:
- Fixed a server-side bug where TTS chunks were being combined by concatenating base64 strings instead of decoding to bytes first and re-encoding once at the end.
- Buffered TTS chunk bytes on the backend and sent one clean audio payload back to the browser when the stream completed.

Symptoms addressed:
- Playback sounded like it started and then got cut off.

## Troubleshooting Timeline

### 1. Initial symptom

- Browser showed socket connected at times, but no audible Sarvam response was heard.

### 2. Verified backend/frontend mismatch

- Confirmed the browser client expected a Sarvam-oriented browser live runtime that did not match the existing ADK/Gemini backend flow.

### 3. Identified actual running backend

- Checked the earlier thread and found the live frontend was wired against a temp backend under `/tmp/whimsicalexplorer2_sarvam_streaming_backend`.
- Switched debugging to that temp backend so observed behavior matched the running app.

### 4. Verified frontend mic output

- Added mic debug UI.
- Confirmed chunks were being generated, sent successfully, and flushed.

### 5. Fixed STT input handling

- Found that STT flushes were happening before Sarvam accepted audio input.
- Buffered PCM and sent it correctly on flush.
- Confirmed transcript began appearing again.

### 6. Diagnosed empty LLM replies

- Instrumented the completions request and response.
- Confirmed the model was returning only `reasoning_content` and no final `content`.
- Temporary fallback ensured TTS remained testable while debugging continued.

### 7. Fixed TTS assembly bug

- Found backend TTS payload assembly was corrupting MP3 data by joining base64 strings directly.
- Switched to joining decoded bytes.

### 8. Stabilized frontend lifecycle

- Removed websocket reconnect churn caused by render-time instability, bootstrap reruns, and Strict Mode remount behavior.
- Got the socket consistently connected again.

### 9. Found root cause of short spoken fallback

- Compared the actual Sarvam request against the reference sample.
- Switched to non-streaming content parsing.
- Removed `max_tokens`.
- Confirmed the app began returning real assistant content instead of only the fallback.

### 10. Ported the working backend into the repo

- Copied the validated temp backend implementation into `browserbackend/`.
- Left the original `backend/` implementation in place instead of replacing it.

## Current Outcome

- Browser socket connects reliably.
- Push-to-talk audio reaches the backend.
- STT returns transcript text.
- Sarvam completions return usable assistant text after removing `max_tokens`.
- TTS audio is assembled correctly and plays back through the browser.
- The working Sarvam browser backend now exists in the repository under `browserbackend/`.

## Notes

- The temp backend copy under `/tmp` is not a git repository, so it was used as the source of truth and then ported into `browserbackend/`.
- The original `backend/` folder remains in place for the existing implementation.
