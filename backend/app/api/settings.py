from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_household
from app.models.db_models import Household, HouseholdSettings
from app.schemas.auth import HouseholdSettingsUpdate, HouseholdSettingsResponse

router = APIRouter()

@router.get("/", response_model=dict)
def get_settings(household: Household = Depends(get_current_household), db: Session = Depends(get_db)):
    settings = db.query(HouseholdSettings).filter(HouseholdSettings.household_id == household.id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
        
    # Return within generic `data` envelope
    response_data = HouseholdSettingsResponse.model_validate(settings)
    return {"data": response_data.model_dump()}

@router.patch("/", response_model=dict)
def update_settings(
    settings_in: HouseholdSettingsUpdate, 
    household: Household = Depends(get_current_household), 
    db: Session = Depends(get_db)
):
    settings = db.query(HouseholdSettings).filter(HouseholdSettings.household_id == household.id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
        
    update_data = settings_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
         setattr(settings, field, value)
         
    db.add(settings)
    db.commit()
    db.refresh(settings)
    
    response_data = HouseholdSettingsResponse.model_validate(settings)
    return {"data": response_data.model_dump()}
