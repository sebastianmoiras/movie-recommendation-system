import jwt
import datetime
from fastapi import HTTPException, status
#jwt token itu biar user dikasih token, agar website mengenali nih user udah lewat proses login, 
#jadi mau pake fitur apapun di website itu udah gaperlu verifikasi karena ada key yang nempel

#secret key adalah key yang digunakan untuk 'tanda tangan' kepada user yang login, jadi ketika sudah diverified
#user diberikan 1 token untuk memberi tau website bahwa user boleh mengakses website sampai masa token expired
SECRET_KEY = "tokenJonathan2702269633SebastianMoiras"
ALGORITHM = "HS256"

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
