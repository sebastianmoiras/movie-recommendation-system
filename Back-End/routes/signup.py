from fastapi import APIRouter, Query
from typing import List
from services.auth_service import signup_user

router = APIRouter()

@router.post("/signup")
def signup(
    name: str, 
    email: str, 
    password: str, 
    age: int, 
    nationality: str, 
    gender: str,
    preferred_genres: List[int] = Query(..., min_items=3)
):
    return signup_user(name, email, password, age, nationality, gender, preferred_genres)