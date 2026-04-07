from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.db_models import ImageContext, Session as DBSession, ObjectCategory
from app.schemas.devices import ImageContextResponse
import uuid

router = APIRouter()

# Note: typically would be secured by device auth or session token, simplistic for MVP
@router.post("/image", response_model=dict)
async def upload_image_context(
    session_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Active session not found")

    # In a full build, this would route to an Object Storage provider block (S3/Minio)
    # and utilize Gemini 1.5 Pro to verify the image payload against allowed categories
    # For MVP struct, we mock a safe detection:
    
    mock_file_path = f"/mock-storage/{uuid.uuid4()}.jpg"
    
    new_context = ImageContext(
        object_url=mock_file_path,
        detected_name="Teddy Bear",
        detected_category=ObjectCategory.toys,
        confidence=95
    )
    db.add(new_context)
    db.flush() # Get ID
    
    # Anchor the context to the active session
    session.current_image_context_id = new_context.id
    session.current_object_name = new_context.detected_name
    session.current_object_category = new_context.detected_category
    db.commit()
    db.refresh(new_context)
    
    return {"data": ImageContextResponse.model_validate(new_context).model_dump()}
