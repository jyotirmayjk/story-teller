# Future Roadmap

## AI Montessori-Style Companion

### Product Direction
Reframe the product as a calm, object-centered learning companion for toddlers ages 2 to 4. Instead of behaving like a general chatbot or an operator-facing live runtime, the experience should feel like a gentle Montessori-style guide that helps the child explore the real world through naming, observing, repeating, and simple follow-up prompts.

This direction emphasizes:
- real-world objects over abstract content
- simple, precise language
- sensory observation
- repetition and calm pacing
- child-led discovery
- one meaningful next step at a time

### Core Interaction Model
The ideal loop is:
1. the child shows or says something
2. the companion identifies or recognizes it
3. the companion names it clearly
4. the companion offers one observation
5. the companion invites one simple next action or noticing prompt

Examples:
- "This is a spoon."
- "The spoon is shiny and smooth."
- "Can you touch the spoon?"

- "This is a dog."
- "The dog says (woof woof)."
- "Can you point to the dog's ears?"

### Product Personality
The assistant should feel:
- calm
- warm
- precise
- non-overstimulating
- respectful of the child's pace

It should avoid:
- overly noisy praise
- long explanations
- quiz-heavy interaction
- too many prompts at once
- technical or dashboard-like presentation

### Educational Pillars
Potential Montessori-aligned learning areas:
- object naming
- early vocabulary
- colors and shapes
- textures and sensory words
- animals and sounds
- vehicles and motion
- daily routine objects
- sorting and categorization
- nature observation
- simple action words

### UI Direction
The UI should feel quiet, spacious, and object-centered.

Recommended characteristics:
- one main activity on screen at a time
- one dominant talk/listen action
- one large object/result card
- one optional follow-up prompt
- one replay button
- minimal visible controls
- parent settings hidden behind a secondary surface

The main screen should avoid:
- dense transcripts
- multiple technical panels
- socket/session status prominence
- form-heavy controls in the child-facing view

### Feature Ideas
- Object Tray: focus on one real-world object at a time.
- Notice More: offer one sensory or observational follow-up.
- Repeat Calmly: replay the latest response slowly and clearly.
- Find Another: invite the child to find a similar object, color, or shape.
- Routine Moments: guide brushing teeth, tidying, dressing, or eating.
- Nature Walk Mode: calm outdoor observation prompts.
- Parent Shelf: settings, transcript, history, and supervision tools.

### Implementation Notes
- For the current browser-first version, do not require JWT auth for the live voice socket.
- Keep the voice flow simple and local to the app session while the product is still being iterated.
- Defer production auth hardening, household-scoped JWT validation, and websocket token enforcement to a later phase once the child-facing UX is stable.
- Treat JWT-backed auth as future roadmap work, not a requirement for the current end-to-end voice prototype.

### Prompting Direction
The system prompt for this product direction should encourage the assistant to:
- name the object clearly
- offer one concrete observation
- invite one simple follow-up
- use calm, toddler-friendly language
- keep the response short and expressive

Suggested guiding instruction:

> Respond like a calm Montessori guide for toddlers: name the object, offer one concrete observation, and invite one simple next action or noticing prompt.

### Positioning
Potential framing:
- "A calm AI companion that helps toddlers explore the real world through objects, sounds, and simple language."
- "An AI Montessori-style companion for ages 2 to 4."
- "A voice-and-vision guide for toddler discovery."
