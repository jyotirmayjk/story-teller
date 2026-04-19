# Prompt Feedback

## Session 2026-04-18

### Issue: Marathi conversation sounded translated instead of spoken
- Transcript / input: `मी आज शाळेत गेलो.`
- Observed output: `ओह, तू आज शाळेत गेलास. मला अधिक सांग.`
- Why it was sub-optimal: The wording sounded formal and translated rather than like a warm caregiver speaking naturally to a small child.
- Detected by: user
- Changes made: Updated the conversation prompt to require natural spoken Marathi and Hindi, added Marathi examples directly into the prompt, and replaced stiff Marathi fallback lines with more natural phrases such as `मला अजून सांग ना` and `मग काय झालं?`
- Status: improved

### Issue: Story Teller asked for transcript even though the spoken request was already available
- Transcript / input: `मला पीटर रॅबिटची स्टोरी सांगणं.`
- Observed output: The model asked the child to share or provide the transcript instead of telling a story.
- Why it was sub-optimal: In this app, the child's transcript is already the source input. Asking for it again breaks the experience and sounds like a generic assistant, not a child-facing storyteller.
- Detected by: both
- Changes made: Tightened the Story Teller prompt to explicitly forbid asking for the transcript, clarified that the spoken request is already the user message, and added Story Teller-specific fallback behavior.
- Status: improved

### Issue: Story Teller sometimes fell back to a generic greeting instead of telling a story
- Transcript / input: `अजून टायगरची स्टोरी सांग ना.`
- Observed output: `Hello. I am here with you.`
- Why it was sub-optimal: The fallback ignored the child's request and broke the storytelling flow entirely.
- Detected by: both
- Changes made: Replaced the generic fallback path with Story Teller-specific fallback replies, including Marathi fallback handling for continuation requests like `अजून`.
- Status: improved

### Issue: Conversation mode over-questioned the child
- Transcript / input: Conversation turns such as `I saw a bus today.` -> `Yellow.` -> `Fast.`
- Observed output: The assistant kept asking follow-up questions on nearly every turn, making the exchange feel like an interview.
- Why it was sub-optimal: The goal is to gently elicit more language, not overwhelm the child with repeated questions.
- Detected by: user
- Changes made: Changed the conversation prompt so a question is optional, added guidance to end many turns with a warm reflection or invitation, and added runtime logic to reduce follow-up questions after short answers or deeper turns in the thread.
- Status: improved

### Issue: Conversation mode lost the active topic when the child gave a short answer
- Transcript / input: `I saw a dog.` -> `Running.` -> `Running in the garden.` -> `White flower.`
- Observed output: Replies drifted into new scenes such as `You see a white flower. Can you show me the white flower?`
- Why it was sub-optimal: One- or two-word replies should usually be treated as continuations of the previous topic, not as brand-new scenes.
- Detected by: both
- Changes made: Added short-answer anchoring in the prompt, introduced a lightweight conversation topic anchor in runtime memory, and passed structured context for short follow-up replies.
- Status: improved

### Issue: Language matching was inconsistent in conversation fallbacks
- Transcript / input: `हेलो आंटी, आप क्या कर रहे हो?`
- Observed output: `I heard you. Can you tell me a little more?`
- Why it was sub-optimal: The child spoke in Hindi, but the assistant fell back to English, making the interaction feel inconsistent and less natural.
- Detected by: both
- Changes made: Added language-code-aware prompt context, explicitly instructed the model to reply in the child's language, and added a Marathi language guard for cases where the model still returned English.
- Status: improved
