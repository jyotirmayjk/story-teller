# Avatar Requirements

## Purpose

Create a child-friendly assistant avatar for the Story Teller + Conversational Companion app. The avatar should make the voice-first experience feel warm, calm, and emotionally safe for children ages 2-4.

The avatar will be used inside the current React web app and may later be reused in a browser extension. It should be designed as a small UI companion, not as a large illustrated scene.

## Product Context

The app has two child-facing modes:

- `Conversation`: a calm companion that listens to the child and gently encourages more speech.
- `Story Teller`: a playful storyteller that describes an object and tells a short child-safe story.

The avatar should work across both modes with the same core identity. Mode-specific styling can be added later, but the first version should focus on one coherent character.

## Personality

The avatar should feel:

- warm
- calm
- safe
- gentle
- curious
- kind
- lightly playful
- emotionally reassuring

The avatar should not feel:

- loud
- hyperactive
- commercial
- overly cartoonish
- uncanny
- scary
- sarcastic
- adult-like
- overstimulating

## Visual Style

Recommended style:

- soft 2D storybook illustration
- rounded shapes
- simple silhouette
- minimal facial detail
- kind eyes
- small warm smile
- soft edges
- subtle texture if useful
- clean enough to read at small mobile UI sizes

Avoid:

- realistic skin rendering
- hard aggressive outlines
- neon colors
- high-detail backgrounds
- complex props
- copyrighted or recognizable children’s characters
- mascot-like brand energy

## Color Direction

The avatar should harmonize with the app’s current warm paper UI.

App palette references:

- warm cream / paper background
- terracotta accent: `#C0573E`
- soft sage / green accents
- muted earthy neutrals
- gentle warm shadows

Suggested avatar palette:

- cream
- warm tan
- soft terracotta
- dusty rose
- sage green
- muted brown

Use bright colors sparingly.

## Required Runtime States

The current app exposes four primary voice states that the avatar should map to:

### 1. Idle

When the app is ready and waiting.

Expression / motion:

- neutral warm smile
- calm breathing loop
- occasional blink
- relaxed posture

### 2. Listening

When the child is holding the push-to-talk button and the app is recording.

Expression / motion:

- attentive eyes
- slight forward lean
- curious listening expression
- subtle bounce or ear/head movement

### 3. Processing

When the child has stopped speaking and the app is thinking.

Expression / motion:

- gentle thinking face
- small head tilt
- slow blink
- optional tiny sparkle or thought cue
- no mouth movement

### 4. Speaking

When the assistant is speaking through TTS.

Expression / motion:

- soft talking mouth loop
- friendly expression
- gentle body bounce
- should feel calm, not noisy

## Sprite Sheet Requirements

Preferred delivery format:

- transparent PNG or WebP sprite sheet
- equal-sized frames
- fixed grid layout
- no background
- no text

Recommended first version:

```text
4 columns x 4 rows
16 total frames
256px x 256px per frame
1024px x 1024px total sheet
```

Frame mapping:

```text
Row 1: idle frames 0-3
Row 2: listening frames 4-7
Row 3: processing frames 8-11
Row 4: speaking frames 12-15
```

If using a different frame size or layout, provide:

- frame width
- frame height
- number of columns
- number of rows
- which frames correspond to each state

## Animation Guidance

Keep animations subtle and child-safe.

Suggested loop behavior:

- `idle`: 4-frame breathing/blink loop
- `listening`: 4-frame attentive loop
- `processing`: 4-frame slow thinking loop
- `speaking`: 4-frame mouth movement loop

Avoid:

- fast flashing
- exaggerated shaking
- sudden jumps
- rapid color changes
- intense facial expressions

Target feel:

- slow
- cozy
- gentle
- readable

## UI Placement Constraints

The avatar will appear in a mobile-first interface with:

- large response panel
- conversation display
- push-to-talk button
- bottom navigation

The avatar must remain readable at:

- 64px
- 96px
- 128px
- 160px

Do not rely on tiny details that disappear at small sizes.

## Accessibility And Safety

The avatar should:

- be emotionally neutral-to-positive
- never appear angry or alarmed
- not use scary eyes, sharp teeth, or intense expressions
- not include weapons, danger symbols, or unsafe objects
- avoid culturally specific stereotypes
- work for children from different backgrounds

## Deliverables

Required:

- one transparent sprite sheet with the four runtime states
- one static preview image of the neutral avatar
- notes describing frame size and frame-state mapping

Optional:

- separate transparent PNGs for each state
- SVG/vector source file
- additional expressions for future use:
  - error / needs help
  - sleepy / paused
  - happy success
  - storytelling sparkle

## Example Image Model Prompt

```text
Create an original child-friendly assistant avatar for a voice-first storytelling and conversation app for ages 2-4. The character should feel warm, calm, safe, and gentle. Use a soft 2D storybook illustration style with rounded shapes, kind eyes, a small warm smile, minimal facial detail, and a soothing presence. Use a muted earthy palette that matches warm cream, terracotta, dusty rose, sage green, and soft brown.

Create a transparent sprite sheet with 4 columns and 4 rows, 16 frames total. Each frame should be 256x256 px. Row 1 is idle with a calm blink/breathing loop. Row 2 is listening with an attentive curious expression. Row 3 is processing with a gentle thinking/head-tilt loop. Row 4 is speaking with a soft mouth movement loop.

Keep the character readable at small mobile UI sizes. No background, no text, no copyrighted character resemblance, no scary or overstimulating expressions.
```
