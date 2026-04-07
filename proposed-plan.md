# Story Teller + Conversational Companion With New 3-Screen UI

## Summary
Redesign the app around three persistent interfaces available from a bottom navigation bar:

- `Conversation`
- `Story Teller`
- `Settings`

The primary experience should become a simple, child-facing voice UI with:
- a minimal conversation display at the top
- a large response card in the middle
- a large push-to-talk control at the bottom

Behaviorally:
- `Story Teller` should take the full child transcript, ask the LLM to identify the object being asked about, verify that it falls into a safe-for-children category, then produce an object description followed by a short story
- `Conversation` should act as a calm Montessori-style companion that uses cues from the child’s speech to ask one grounded follow-up question and encourage more response
- `Settings` should expose transcript logs grouped by mode and hold parent-facing controls

The existing websocket/STT/TTS transport should remain unchanged.

## Key Changes

### 1. Replace the current home/control layout with a 3-screen app shell
- Remove the current dashboard-style `HomeScreen` as the primary experience.
- Introduce a persistent bottom nav bar visible across the child-facing app.
- Bottom nav destinations:
  - `Conversation`
  - `Story Teller`
  - `Settings`
- Each screen should be a top-level route/view, but share the same session/live websocket infrastructure.

### 2. Shared child-facing interaction pattern
Both `Conversation` and `Story Teller` should use the same screen structure:

#### A. Conversation Display (Top)
Show:
- last child transcript
- latest assistant response
- optionally 1 previous turn only if space allows

Behavior:
- minimal chat-like layout
- no avatars initially
- very large readable text
- keep only 1-2 previous turns max to avoid clutter
- transcript should feel like “what I heard” rather than a developer transcript log

#### B. Response Panel (Middle)
Show:
- latest assistant response, exactly as spoken
- large rounded high-contrast card
- optional highlighted detected object when relevant, especially in Story Teller

Behavior:
- this is the visual anchor of the screen
- if object is detected, show it prominently near the assistant response
- card should feel calm, simple, and child-readable

#### C. Push-to-Talk Control (Bottom)
Use one large circular control.

States:
- idle: `Tap to Talk`
- pressed: `Listening…`
- processing: subtle animation
- speaking: disabled or glowing

Behavior:
- keep this as the dominant interactive element
- state transitions should be visually obvious and stable
- do not expose technical socket/session badges on these screens

### 3. Story Teller behavior
- Child speaks naturally; no manual object name entry on screen.
- After final STT transcript arrives, pass the full user query string to the LLM.
- In the same instruction set, ask the LLM to:
  - identify the object the child is asking about
  - determine whether the object belongs to a safe-for-children category
  - if safe, begin by describing the object
  - then tell a short story about it
- Do not implement heuristic noun extraction or a first-pass object parser.
- Safe category validation should be LLM-driven in this feature iteration.
- The reply format should be constrained:
  - first part: simple concrete description of the object
  - second part: short story
  - total output: 3-4 short lines or sentences
- If the object is not safe or not appropriate for children:
  - gently redirect to a safe child-appropriate object/topic
  - do not surface category-check logic in technical language
- The UI should optionally highlight the detected object in the response panel.

### 4. Conversational Companion behavior
- Child speaks freely.
- After final transcript arrives, pass the transcript to a dedicated conversational prompt.
- The assistant should:
  - identify one concrete cue from the child’s statement
  - respond in a calm Montessori-style tone
  - ask one follow-up question designed to elicit more speech
- Example:
  - child: `I saw a bus today`
  - assistant: `You saw a bus today. What color was the bus?`
- Prompt rules:
  - use calm Montessori guide language
  - name or reflect one concrete part of the child’s statement
  - ask exactly one follow-up question
  - avoid too many exclamations
  - avoid noisy praise
  - avoid over-talking
  - avoid random fantasy when concrete observation is more appropriate
  - avoid quiz-heavy language
- The assistant should not ask multiple questions in one turn.

### 5. Settings interface
Create a dedicated `Settings` screen for parent-facing oversight.

Settings should show:
- transcript log grouped by mode
- transcript history for:
  - Conversation
  - Story Teller
- assistant replies paired with the corresponding child transcript
- any existing parent/runtime controls that still matter:
  - voice style
  - optional TTS tuning if retained
  - other current runtime/session settings that are still useful

This screen should absorb the current technical/debug-heavy controls so they are removed from the child-facing screens.

### 6. Prompt refactor
Refactor prompt generation into explicit behavior-specific prompt builders.

Recommended builders:
- `build_story_teller_prompt(...)`
- `build_conversational_companion_prompt(...)`

Story Teller prompt must instruct the LLM to:
- inspect the full child query
- determine the object the child is asking about
- ensure the object is in a safe-for-children category
- if safe, describe the object first and then tell a story
- keep output to 3-4 short lines or sentences
- use expressive punctuation and bracketed sound hints when useful

Conversational Companion prompt must instruct the LLM to:
- respond like a calm Montessori guide for toddlers
- reflect one concrete cue from the child’s speech
- ask one simple follow-up question
- avoid:
  - too many exclamations
  - noisy praise every turn
  - over-talking
  - random fantasy when the moment calls for concrete observation
  - quiz-heavy or test-like language

### 7. Backend orchestration changes
Update the current `handle_flush()` flow so it branches by active interface/mode:

- `Story Teller`
  - receive final transcript
  - send full transcript to LLM with object-detection + safe-category + description + story instructions
  - return assistant text
  - TTS the assistant text
  - persist transcript + reply + detected object if returned

- `Conversation`
  - receive final transcript
  - send transcript to LLM with Montessori conversational follow-up instructions
  - return assistant text
  - TTS the assistant text
  - persist transcript + reply

The websocket message types can remain unchanged:
- `transcript.final`
- `llm.delta`
- `llm.completed`
- `tts.chunk`
- `tts.completed`

### 8. Data and logging updates
- Persist transcript logs per mode so `Settings` can display them clearly.
- Discovery/history model may need a mode-aware transcript log structure or filtered view.
- For Story Teller, persist optional `detected_object_name` if the LLM returns it in a structured or parseable way.
- If structured extraction is needed later, add it only after the initial fully-LLM-driven version is working.

## Public Interfaces / Types
- Frontend mode/navigation should move to three interfaces:
  - `conversation`
  - `story_teller`
  - `settings`
- Backend session mode types should be updated to reflect at least:
  - `conversation`
  - `story_teller`
- `settings` is UI-only and should not trigger assistant behavior itself.
- The current `story | learn | explorer` values should be removed or mapped during transition, but the final product should use the new names directly if possible.
- Transcript log structures should support filtering or grouping by mode for the Settings screen.

## Test Plan
- Navigation:
  - bottom nav persists across screens
  - user can switch between Conversation, Story Teller, and Settings reliably
- Story Teller:
  - child says a query mentioning an object
  - LLM identifies the object from the full transcript
  - LLM checks safe-for-children suitability
  - assistant describes the object first, then tells a story
  - object/category does not need to be selected on screen
- Story Teller redirect:
  - child mentions an unsuitable object/topic
  - assistant gently redirects to a safe child-appropriate object/topic
- Conversation:
  - child says a freeform sentence
  - assistant asks one grounded follow-up question based on a cue in the child’s speech
  - no multiple-question or quiz-heavy output
- UI:
  - conversation display shows last child transcript and assistant reply
  - response card shows large readable output
  - push-to-talk button clearly reflects idle/listening/processing/speaking states
- Settings:
  - transcript logs are visible and grouped by mode
  - parent-facing controls remain functional
- Regression:
  - STT final still arrives
  - TTS still plays
  - websocket flow remains stable

## Assumptions
- The redesign should remove manual object/category selection from the child-facing screens entirely.
- Safe-category handling in Story Teller will be delegated to the LLM for this iteration.
- The child-facing screens should remain calm and minimal; all technical/runtime detail belongs in Settings.
- The implementation should prioritize a working end-to-end UX over adding structured extraction schemas unless needed later for reliability.
