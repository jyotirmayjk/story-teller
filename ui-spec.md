# UI Spec

## Purpose
This document describes the frontend experience for the current `v2` child-facing app on branch `codex/story-conversational-companion-plan`.

It is meant to be the reference for:
- screen structure
- shared UI elements
- interaction states
- content behavior
- parent-facing versus child-facing boundaries

This version is a voice-first product.
There is no image capture flow in scope for this release.

## Product Structure
The app is organized around three top-level screens available through a persistent bottom navigation bar:

- `Conversation`
- `Story Teller`
- `Settings`

The first two are child-facing.
`Settings` is parent-facing.

## Design Direction
The UI should feel:
- calm
- warm
- readable from a distance
- simple enough for repeated toddler use

The visual language is intentionally soft and paper-like:
- warm beige and cream backgrounds
- dark ink text
- muted supporting text
- a terracotta accent for primary action and highlights
- a green speaking state for reassurance and contrast

Typography should feel book-like rather than app-like:
- large serif headlines and response text
- minimal chrome
- no dense dashboards on child screens

## Shared App Shell

### Layout
The app shell has:
- a full-height viewport
- a main content region
- a fixed bottom navigation bar

### Bottom Navigation
The bottom nav is always visible on the three main screens.

Requirements:
- 3 equal-width tabs
- pill-shaped container
- fixed to bottom with safe padding
- active route shown with filled accent-tinted state
- labels only, no icons required in this version

Tabs:
- `Conversation`
- `Story Teller`
- `Settings`

## Child-Facing Screens
`Conversation` and `Story Teller` must share the same overall layout pattern.

### Child Screen Layout
Each child-facing screen has four vertical regions:

1. Header
2. Conversation display
3. Response panel
4. Push-to-talk controls

The layout should prioritize:
- large central reading area
- minimal clutter
- obvious primary action at the bottom

### 1. Header
The header contains:
- an eyebrow label naming the mode
- a large headline
- a short supporting description

Behavior:
- mode-specific copy changes by screen
- this area introduces the purpose of the screen
- it should remain concise and not compete with the response card

#### Conversation Header Copy
- Eyebrow: `Conversation`
- Tone: grounded, calm, reflective
- Message: this mode listens, reflects one real detail, and asks one simple follow-up

#### Story Teller Header Copy
- Eyebrow: `Story Teller`
- Tone: imaginative but still structured
- Message: this mode describes the object first, then tells a short story

### 2. Conversation Display
This is the transcript-style memory area near the top.

Content:
- latest child speech under `What I heard`
- latest assistant reply under `Last reply`

Behavior:
- use plain language, not technical transcript terms
- keep it visually light
- show the current partial transcript while listening if available
- otherwise show the final transcript
- if nothing has happened yet, show a gentle empty-state instruction

Rules:
- no avatars in this version
- no message timestamps on the child-facing screen
- no long scrollback transcript
- at most the most recent turn pair should be visible in the default state

### 3. Response Panel
This is the main visual anchor of the child-facing screen.

Purpose:
- show the assistant’s latest response exactly as spoken
- provide the calmest, largest reading surface on the screen

Visual requirements:
- large rounded card
- high contrast against page background
- centered or gently vertically balanced text
- generous padding
- large serif text

Behavior:
- if no response exists yet, show mode-specific placeholder text
- the content shown here should match the spoken TTS text exactly

#### Story Teller Detected Object
When `Story Teller` has a detected object:
- show a small highlighted line above the response text
- label it as `Detected object`
- emphasize the object name

This object label is optional and should only appear when available.

### 4. Push-to-Talk Controls
The push-to-talk control is the dominant interactive element.

Structure:
- one very large circular button
- one small supporting meta row beneath it

Button requirements:
- circular
- large enough to be the most obvious affordance on the screen
- touch-first
- center-aligned label text

States:
- `idle`
- `listening`
- `processing`
- `speaking`

#### Idle State
Label:
- `Tap to Talk`

Visual:
- terracotta gradient
- high contrast text
- no pulsing needed

#### Listening State
Label:
- `Listening...`

Visual:
- slight scale-up
- soft outer ring or glow
- immediate feedback on press

#### Processing State
Label:
- `Thinking...`

Visual:
- warmer amber-toned treatment
- stable, subtle change from idle
- should not feel alarming

#### Speaking State
Label:
- `Speaking...`

Visual:
- green-toned treatment
- button disabled
- indicates assistant is currently talking

Interaction rules:
- hold/press starts recording
- release ends recording and flushes audio
- leaving the button while pressed should end recording safely
- while speaking, the button should be disabled

### Child Screen Meta Row
Below the push-to-talk button, a small utility row may show:
- current status pill
- `Reset audio` action

Rules:
- keep this secondary
- do not show websocket/debug/session internals here
- this row should not visually compete with the main button

## Conversation Screen

### Functional Intent
This screen is the conversational companion mode.

The assistant behavior should:
- reflect one concrete cue from the child’s speech
- use calm Montessori-style language
- ask exactly one simple follow-up question

### UI Implications
The UI should reinforce groundedness:
- no fantasy-heavy decorative treatment
- response text should feel clear and direct
- placeholder copy should suggest listening and follow-up, not storytelling

### Empty State Copy
Suggested response-panel placeholder:
- `A calm follow-up question will appear here after the child speaks.`

## Story Teller Screen

### Functional Intent
This screen is the object-driven storytelling mode.

The child speaks naturally.
The full transcript is sent to the LLM.
The LLM identifies the object, checks child-appropriateness, describes it briefly, and then tells a short story.

### UI Implications
The screen should feel slightly more expressive than `Conversation`, but still simple.

Rules:
- do not show manual object input
- do not show category selectors
- do not expose safety-check logic
- only surface the detected object if available and useful

### Empty State Copy
Suggested response-panel placeholder:
- `Ask about any child-safe object and the story will appear here.`

## Settings Screen
`Settings` is explicitly parent-facing.

It should absorb the controls and history that do not belong on the child-facing experience.

### Layout
The Settings screen is a stacked page with:

1. Hero section
2. Controls grid
3. Transcript history grouped by mode

### Hero Section
Contains:
- eyebrow: `Settings`
- page title
- short explanation that this area is for parents and transcript review

### Controls Grid
This section contains cards for:
- `Assistant voice`
- `Default screen`

#### Assistant Voice Card
Current control:
- `Voice style`

Options:
- `Friendly Cartoon`
- `Story Narrator`

Behavior:
- updates should save immediately
- muted helper text should confirm save state or describe the effect

#### Default Screen Card
Current control:
- `Default mode`

Options:
- `Conversation`
- `Story Teller`

Behavior:
- updates should save immediately
- helper text should explain that this controls the startup screen for a new session

### Transcript History
Transcript history is grouped into:
- `Conversation`
- `Story Teller`

Each saved item should display:
- object name or fallback label if absent
- favorite toggle
- child transcript
- assistant reply

Rules:
- group by mode, not by date first
- show empty copy when a group has no items
- keep the history readable and scannable

Suggested group empty copy:
- Conversation: `Conversation turns will appear here once the child starts talking.`
- Story Teller: `Story Teller transcripts will appear here after completed story turns.`

## Content and Copy Rules

### Child-Facing Copy
Should be:
- brief
- concrete
- readable aloud
- low-noise

Should avoid:
- technical language
- debug words
- crowded helper text
- celebratory UI noise on every action

### Parent-Facing Copy
Can be slightly more explicit, but should still be simple and product-focused.

Should avoid:
- implementation jargon unless needed for troubleshooting

## Visual System

### Color Roles
Primary tokens in current design direction:
- paper background
- cream card surfaces
- dark ink body text
- muted brown-gray supporting text
- terracotta action/accent
- green speaking state
- warm amber processing state

### Shape
- large radii throughout
- pill forms for nav and status elements
- circular primary talk button

### Elevation
- soft shadows only
- avoid harsh, glossy UI treatments

### Motion
Motion should be minimal and functional:
- hover lift for desktop buttons
- slight scale or glow for listening state
- subtle visual shift between button states

No decorative animation system is required in this version.

## Responsiveness

### Mobile
This is the primary target.

Requirements:
- bottom nav stays reachable
- talk button remains fully visible above nav
- response card stays prominent
- text remains large without forcing horizontal scrolling

### Tablet / Desktop
Requirements:
- preserve centered child-screen feeling
- avoid stretching text lines excessively
- keep response panel visually dominant

### Breakpoint Behavior
At narrower widths:
- multi-column settings layout collapses to one column
- child screen preserves vertical order
- bottom nav remains fixed

## Accessibility
Minimum requirements:
- all interactive elements keyboard reachable
- large text on child-facing screens
- strong color contrast between text and backgrounds
- explicit `aria-label` on push-to-talk button
- disabled speaking state communicated visually and programmatically

## Out of Scope for This Version
The following are not part of this release UI:
- image capture
- object photo recognition
- developer transcript/debug overlays on child screens
- advanced settings panels for technical runtime controls
- avatar-based chat UI
- long scrolling multi-turn chat history on child screens

## Implementation References
Current implementation lives primarily in:
- [`/Users/jk/Code/sarvamai/v2/web/src/app/AppRouter.tsx`](/Users/jk/Code/sarvamai/v2/web/src/app/AppRouter.tsx)
- [`/Users/jk/Code/sarvamai/v2/web/src/app/AppLayout.tsx`](/Users/jk/Code/sarvamai/v2/web/src/app/AppLayout.tsx)
- [`/Users/jk/Code/sarvamai/v2/web/src/components/navigation/AppNav.tsx`](/Users/jk/Code/sarvamai/v2/web/src/components/navigation/AppNav.tsx)
- [`/Users/jk/Code/sarvamai/v2/web/src/screens/live/ChildLiveScreen.tsx`](/Users/jk/Code/sarvamai/v2/web/src/screens/live/ChildLiveScreen.tsx)
- [`/Users/jk/Code/sarvamai/v2/web/src/screens/settings/SettingsScreen.tsx`](/Users/jk/Code/sarvamai/v2/web/src/screens/settings/SettingsScreen.tsx)
- [`/Users/jk/Code/sarvamai/v2/web/src/styles/global.css`](/Users/jk/Code/sarvamai/v2/web/src/styles/global.css)

## Future Additions
Possible later additions, if the product expands:
- richer transcript browsing and filtering
- icons for bottom navigation
- explicit speaking/listening animation system
- parent PIN or lightweight auth
- more voice options
- finer TTS pacing controls
