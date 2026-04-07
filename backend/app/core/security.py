from fastapi import Depends, HTTPException, Query, WebSocket, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.db_models import Household
from app.repositories.temp_auth import temp_auth_store

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_household(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    household_id = temp_auth_store.get_household_id(token)
    if household_id is None:
        raise credentials_exception

    household = db.query(Household).filter(Household.id == int(household_id)).first()
    if household is None:
        raise credentials_exception
    return household


async def require_ws_household(websocket: WebSocket, db: Session) -> Household:
    token = websocket.query_params.get("token")
    if not token:
        authorization = websocket.headers.get("authorization", "")
        if authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1].strip()

    household_id = temp_auth_store.get_household_id(token or "")
    if household_id is None:
        await websocket.close(code=4401, reason="Unauthorized")
        raise RuntimeError("Unauthorized websocket")

    household = db.query(Household).filter(Household.id == int(household_id)).first()
    if household is None:
        await websocket.close(code=4401, reason="Unauthorized")
        raise RuntimeError("Unauthorized websocket")
    return household
