from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_household
from app.models.db_models import Household, Device, ImageContext, Session as DBSession
from app.schemas.devices import DeviceCreate, DeviceResponse

router = APIRouter()

@router.post("/register", response_model=dict)
def register_device(device_in: DeviceCreate, household: Household = Depends(get_current_household), db: Session = Depends(get_db)):
    # Check if already registered
    existing_device = db.query(Device).filter(Device.device_uid == device_in.device_uid).first()
    if existing_device:
        if existing_device.household_id != household.id:
            # Re-assigning to new household
            existing_device.household_id = household.id
            db.commit()
            db.refresh(existing_device)
        return {"data": DeviceResponse.model_validate(existing_device).model_dump()}

    new_device = Device(device_uid=device_in.device_uid, household_id=household.id)
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return {"data": DeviceResponse.model_validate(new_device).model_dump()}

@router.post("/heartbeat", response_model=dict)
def device_heartbeat(device_uid: str, db: Session = Depends(get_db)):
    # Simple ping for hardware to check backend connectivity
    return {"data": {"alive": True, "device_uid": device_uid}}
