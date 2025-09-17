from fastapi import APIRouter
from services.auth_service import login_user

router = APIRouter()

@router.post("/login")
def login(email: str, password: str):
    return login_user(email, password)
