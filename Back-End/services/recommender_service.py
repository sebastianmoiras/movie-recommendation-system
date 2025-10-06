import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from db.connection import get_connection


# 1. Tambah / Update Feedback
def add_feedback(userid: int, movieid: int, rating: int, liked: bool):
    if rating < 1 or rating > 5:
        return {"success": False, "message": "Rating harus antara 1 sampai 5"}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM feedback WHERE userid = %s AND movieid = %s", (userid, movieid))
    exists = cursor.fetchone()

    if exists:
        cursor.execute("""
            UPDATE feedback
            SET rating = %s, liked = %s
            WHERE userid = %s AND movieid = %s
        """, (rating, bool(liked), userid, movieid))
    else:
        cursor.execute("""
            INSERT INTO feedback (userid, movieid, rating, liked)
            VALUES (%s, %s, %s, %s)
        """, (userid, movieid, rating, bool(liked)))

    conn.commit()
    conn.close()
    return {"success": True, "message": "Feedback saved!"}


# 2. Skor gabungan rating+like
def compute_score(rating, liked):
    score = rating
    if liked == 1:  # like
        score = min(5, score + 1)
    elif liked == 0:  # dislike
        score = max(1, score - 1)
    return score


# 3. Rekomendasi User-Based
def get_recommendation(userid: int, limit: int = 10, threshold: float = 0.5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT userid, movieid, rating, liked FROM feedback")
    rows = cursor.fetchall()
    if not rows:
        return {"method": "no-feedback", "movies": []}

    df = pd.DataFrame.from_records(rows, columns=["userid", "movieid", "rating", "liked"])
    df["score"] = df.apply(lambda r: compute_score(r["rating"], r["liked"]), axis=1)
    
    user_movie_matrix = df.pivot_table(
        index="userid", columns="movieid", values="score"
    ).fillna(0)

    if userid not in user_movie_matrix.index:
        conn.close()
        return _fallback_preferred_genres(userid, limit)

    # cosine similarity antar user
    sim_matrix = cosine_similarity(user_movie_matrix)
    sim_df = pd.DataFrame(sim_matrix, index=user_movie_matrix.index, columns=user_movie_matrix.index)

    # metadata user
    cursor.execute("SELECT userid, gender, age, nationality FROM users")
    meta_rows = cursor.fetchall()
    user_meta = pd.DataFrame.from_records(meta_rows, columns=["userid", "gender", "age", "nationality"])

    # adjust similarity pakai metadata
    if userid in user_meta.userid.values:
        u1 = user_meta[user_meta.userid == userid].iloc[0]

        for other in sim_df.columns:
            if other == userid or other not in user_meta.userid.values:
                continue
            u2 = user_meta[user_meta.userid == other].iloc[0]

            bonus = 0
            if u1.gender == u2.gender:
                bonus += 0.1
            if u1.nationality == u2.nationality:
                bonus += 0.1
            if abs(u1.age - u2.age) <= 5:
                bonus += 0.1

            sim_df.at[userid, other] += bonus

    # cari user paling mirip
    similar_users = sim_df[userid].drop(userid).sort_values(ascending=False)

    if similar_users.empty or similar_users.iloc[0] < threshold:
        conn.close()
        return _fallback_preferred_genres(userid, limit)

    top_user = similar_users.index[0]

    target_movies = set(df[df.userid == userid].movieid)
    rec_movies = df[(df.userid == top_user) & (~df.movieid.isin(target_movies))]

    if rec_movies.empty:
        conn.close()
        return _fallback_preferred_genres(userid, limit)

    movie_ids = rec_movies.movieid.unique().tolist()
    if not movie_ids: 
        conn.close()
        return _fallback_preferred_genres(userid, limit)

    placeholders = ",".join(["%s"] * len(movie_ids))
    cursor.execute(f"""
        SELECT movieid, title, poster_url
        FROM movies
        WHERE movieid IN ({placeholders})
    """, movie_ids)
    rows = cursor.fetchall()
    movies = [{"movieid": r[0], "title": r[1], "poster_url": r[2]} for r in rows]

    conn.close()
    return {"method": "user+demographic", "movies": movies[:limit]}


# 4. Fallback ke Preferred Genres
def _fallback_preferred_genres(userid: int, limit: int = 10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT genreid FROM user_genres WHERE userid = %s", (userid,))
    genres = [row[0] for row in cursor.fetchall()]

    if genres:
        placeholders = ",".join(["%s"] * len(genres))
        cursor.execute(f"""
            SELECT m.movieid, m.title, m.poster_url
            FROM movies m
            JOIN movie_genres mg ON m.movieid = mg.movieid
            WHERE mg.genreid IN ({placeholders})
            ORDER BY RANDOM()
            LIMIT {limit}
        """, genres)
        rows = cursor.fetchall()
        conn.close()
        return {
            "method": "preferred-genres",
            "movies": [{"movieid": r[0], "title": r[1], "poster_url": r[2]} for r in rows]
        }

    cursor.execute(f"""
        SELECT movieid, title, poster_url
        FROM movies
        ORDER BY RANDOM()
        LIMIT {limit}
    """)
    rows = cursor.fetchall()
    conn.close()
    return {"method": "random", "movies": [{"movieid": r[0], "title": r[1], "poster_url": r[2]} for r in rows]}

def get_liked_movies(userid: int, limit: int = 50):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT m.movieid, m.title, m.poster_url
        FROM feedback f
        JOIN movies m on f.movieid = m.movieid
        WHERE f.userid = %s AND f.liked = TRUE
        ORDER BY f.rating DESC
        LIMIT %s
    """, (userid, limit))
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {"movieid": r[0], "title": r[1], "poster_url": r[2]}
        for r in rows
    ]



