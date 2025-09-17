from sentence_transformers import SentenceTransformer
import chromadb
from db.connection import get_connection

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# init chroma
# simpan vector DB di folder .chroma_db/
chroma_client = chromadb.PersistentClient(path="./.chroma_db")
collection = chroma_client.get_or_create_collection(name="movies")

def build_embeddings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            m.movieid,
            m.title,
            m.overview,
            STRING_AGG(g.name, ', ') AS genres,
            m.poster_url
        FROM movies m
        JOIN movie_genres mg ON m.movieid = mg.movieid
        JOIN genres g ON mg.genreid = g.genreid
        GROUP BY m.movieid, m.title, m.overview, m.poster_url
    """)
    rows = cursor.fetchall()
    conn.close()
    
    for r in rows:
        movieid, title, overview, genres, poster_url = r
        text = f"{title}. {genres}. {overview}"
        embedding = model.encode(text).tolist()
        collection.add(
            ids=[str(movieid).strip()],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "title": title,
                "poster_url": poster_url
            }]
        )
        
def search_by_embedding(query: str, n_results: int = 10):
    embedding = model.encode(query).tolist()
    results = collection.query(query_embeddings=[embedding], n_results=n_results)
    seen = set()
    unique = []

    for idx, md in enumerate(results["metadatas"][0]):
        movieid = results["ids"][0][idx] 
        if md["title"] not in seen:
            seen.add(md["title"])
            unique.append({
                "movieid": int(movieid),
                "title": md["title"],
                "poster_url": md["poster_url"]
            })

        if len(unique) >= n_results:
            break

    return unique

