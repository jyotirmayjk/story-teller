from typing import Optional, Sequence

from app.models.db_models import Session


def _format_recent_turns(recent_turns: Sequence[dict[str, str]]) -> str:
    if not recent_turns:
        return ""

    lines = ["Recent conversation turns:"]
    for index, turn in enumerate(recent_turns[-2:], start=1):
        child_text = turn.get("child_text", "").strip()
        assistant_text = turn.get("assistant_text", "").strip()
        if child_text:
            lines.append(f"Child {index}: {child_text}")
        if assistant_text:
            lines.append(f"Assistant {index}: {assistant_text}")
    return " ".join(lines)


def build_story_teller_prompt(session: Session) -> str:
    context = []
    if session.current_object_name:
        context.append(f"Current context object: {session.current_object_name}.")
    if session.current_object_category:
        context.append(f"Current context category: {session.current_object_category.value}.")

    context_block = " ".join(context)

    return (
        "You are Story Teller for a 2-4 year old child. "
        "Inspect the full child transcript and infer the object the child is asking about. "
        "Use the transcript itself as the source of truth instead of asking for a manual object label. "
        "Decide whether that object is appropriate for a young child. "
        "If it is appropriate, first describe the object in simple concrete language, then tell a short story about it. "
        "If it is not appropriate, gently redirect to a safe child-friendly object or topic without using technical safety language. "
        "Keep the total response to 3 or 4 short sentences. "
        "Expressive punctuation is okay when it stays calm and readable. "
        f"{context_block}".strip()
    )


def build_conversational_companion_prompt(
    session: Session,
    *,
    recent_turns: Sequence[dict[str, str]] = (),
    thread_turn_count: int = 0,
    topic_anchor: Optional[str] = None,
) -> str:
    context = []
    if session.current_object_name:
        context.append(f"Optional recent context object: {session.current_object_name}.")
    if thread_turn_count:
        context.append(f"This is turn {thread_turn_count + 1} of the current conversation thread.")
    if topic_anchor:
        context.append(f"Current conversation subject: {topic_anchor}.")

    history_block = _format_recent_turns(recent_turns)
    if history_block:
        context.append(history_block)

    context_block = " ".join(context)

    return (
        "You are a calm Montessori-style conversational companion for toddlers. "
        "Listen to the full child transcript. "
        "Stay with the same topic for a short mini-conversation when the child is still engaged. "
        "When the child's reply is only one or two words, treat it as an answer to the previous question rather than a brand-new topic. "
        "Keep the same subject from the active thread unless the child clearly introduces a different subject. "
        "Do not turn a short fragment into a brand-new scene or switch perspective unexpectedly. "
        "Reflect exactly one concrete cue from the child's speech, then ask exactly one simple follow-up question. "
        "Keep the conversation to at most 3 assistant turns on the same topic before gently opening space for a new topic. "
        "If the child says something clearly new, follow the new topic instead of forcing the old one. "
        "If the child gives a very short answer, keep the next question simple and closely related. "
        "Avoid multiple questions, noisy praise, exclamation-heavy language, over-talking, and quiz-like prompts. "
        "Stay grounded in the child's real observation unless they clearly invite imagination. "
        f"{context_block}".strip()
    )
