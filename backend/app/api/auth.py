from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import HouseholdCreate, HouseholdResponse, HouseholdSettingsBase, AuthToken
from app.models.db_models import Household, HouseholdSettings
from app.repositories.temp_auth import temp_auth_store

router = APIRouter()

# Stub out real Password/Household management for MVP
# Creating a naive login that mints a token for a given household name
@router.post("/login", response_model=dict)
def login(household_data: HouseholdCreate, db: Session = Depends(get_db)):
    household = db.query(Household).filter(Household.name == household_data.name).first()
    
    if not household:
        # Auto-provision on first sign-in for demo fluidity
        household = Household(name=household_data.name)
        db.add(household)
        db.flush()
        
        default_settings = HouseholdSettings(household_id=household.id)
        db.add(default_settings)
        db.commit()
        db.refresh(household)
        
    access_token = temp_auth_store.issue_token(
        household_id=household.id,
        household_name=household.name,
    )
    
    return {
         "data": {
             "access_token": access_token,
             "token_type": "bearer",
             "household": {"id": household.id, "name": household.name}
         }
    }
