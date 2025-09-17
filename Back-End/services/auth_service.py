import bcrypt
from db.connection import get_connection
import re
from services.jwt_service import create_token

def signup_user(name, email, password, age, nationality, gender, preferred_genres):
    conn = get_connection()
    cursor = conn.cursor()

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return {"success": False, "message": "Format email tidak valid"}

    cursor.execute("SELECT 1 FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "message": "Email already existed"}

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    cursor.execute("""
        INSERT INTO users (name, email, password_hash, age, nationality, gender)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING userid
    """, (name, email, password_hash, age, nationality, gender))
    userid = cursor.fetchone()[0]

    for gid in preferred_genres:
        cursor.execute("INSERT INTO user_genres (userid, genreid) VALUES (%s, %s)", (userid, gid))

    conn.commit()
    conn.close()

    return {"success": True, "message": "User created!"}

def login_user(email: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT userid, name, password_hash FROM users WHERE email = %s", (email,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"success": False, "message": "User not found"}

    userid, name, password_hash = row

    if not bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
        return {"success": False, "message": "Invalid password"}

    token = create_token(userid, name)
    return {"success": True, "token": token, "userid": userid, "name": name}


