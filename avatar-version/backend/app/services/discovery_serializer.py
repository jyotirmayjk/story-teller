from app.models.db_models import Discovery


def serialize_discovery(discovery: Discovery) -> dict:
    object_name = discovery.name or discovery.detected_object_name
    object_category = discovery.category.value if discovery.category else None
    mode = discovery.mode.value if discovery.mode else "conversation"

    return {
        "id": str(discovery.id),
        "title": discovery.title or ("Story Teller" if mode == "story_teller" else "Conversation"),
        "object_name": object_name,
        "object_category": object_category,
        "mode": mode,
        "summary": discovery.summary or discovery.reply_text or discovery.transcript or "Completed voice turn",
        "transcript": discovery.transcript,
        "reply_text": discovery.reply_text,
        "detected_object_name": discovery.detected_object_name,
        "is_favorite": discovery.is_favorite,
        "created_at": discovery.created_at.isoformat() if discovery.created_at else None,
    }
