from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from services.jwt_service import verify_token

security = HTTPBearer()

def get_current_user(credentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    return payload
