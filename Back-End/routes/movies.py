from fastapi import APIRouter, Query
from db.connection import get_connection

from services.movie_service import get_movie_detail
from fastapi import HTTPException

router = APIRouter()

# ambil 10 film random
@router.get("/movies")
def get_movies():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT movieid, title, poster_url
        FROM movies
        ORDER BY RANDOM()
        LIMIT 10
    """)
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "movieid": r[0],
            "title": r[1],
            "poster_url": r[2]
        }
        for r in rows
    ]


from services.vector_service import search_by_embedding

@router.get("/search")
def search_movies(query: str = Query(..., min_length=1)):
    return search_by_embedding(query, n_results=10)


@router.get("/movies/{movieid}")
def movie_detail(movieid: int):
    movie = get_movie_detail(movieid)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie
