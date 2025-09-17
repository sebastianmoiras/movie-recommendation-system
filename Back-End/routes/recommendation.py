from fastapi import APIRouter, Depends
from services.dependencies import get_current_user
from services.recommender_service import add_feedback, get_recommendation, get_liked_movies

router = APIRouter()

@router.post("/feedback")
def feedback(movieid: int, rating: int, liked: bool, current_user: dict = Depends(get_current_user)):
    return add_feedback(current_user["userid"], movieid, rating, liked)

@router.get("/recommend")
def recommend(limit: int = 10, current_user: dict = Depends(get_current_user)):
    return get_recommendation(current_user["userid"], limit)

@router.get("/liked-movies")
def liked_movies(limit: int = 50, current_user: dict = Depends(get_current_user)):
    return {"movies": get_liked_movies(current_user["userid"], limit)}
