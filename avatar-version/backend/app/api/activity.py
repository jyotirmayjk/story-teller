from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.session import get_db
from app.core.security import get_current_household
from app.models.db_models import Household, ActivityEvent, Session as DBSession
from app.schemas.app_data import ActivityEventResponse

router = APIRouter()

@router.get("/", response_model=dict)
def list_activity(household: Household = Depends(get_current_household), db: Session = Depends(get_db)):
    activities = db.query(ActivityEvent).join(DBSession).filter(DBSession.household_id == household.id).order_by(desc(ActivityEvent.created_at)).limit(50).all()
    
    response_items = [ActivityEventResponse.model_validate(a).model_dump() for a in activities]
    return {"data": response_items}
