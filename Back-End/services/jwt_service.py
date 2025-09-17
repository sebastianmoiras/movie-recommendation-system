import os
import jwt
import datetime
from fastapi import HTTPException, status
from dotenv import load_dotenv

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret") 
ALGORITHM = os.getenv("ALGORITHM", "HS256")

from fastapi import HTTPException, status

def create_token(user_id: int, name: str):
    payload = {
        "userid": user_id,
        "name": name,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


