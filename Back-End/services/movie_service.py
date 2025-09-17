from db.connection import get_connection

def get_movie_detail(movieid: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.movieid, m.title, m.release_date, m.overview, 
            m.original_language, m.poster_url,
            g.name AS genre_name
        FROM movies m
        LEFT JOIN movie_genres mg ON m.movieid = mg.movieid
        LEFT JOIN genres g ON mg.genreid = g.genreid
        WHERE m.movieid = %s
    """, (movieid,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return None

    # Baris pertama berisi data film, genre bisa multiple
    movie = {
        "movieid": rows[0][0],
        "title": rows[0][1],
        "release_date": rows[0][2],
        "overview": rows[0][3],
        "language": rows[0][4],
        "poster_url": rows[0][5],
        "genres": [r[6] for r in rows if r[6]]
    }
    return movie
