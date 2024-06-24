from jose import jwt, JWTError
import dotenv
import os
from datetime import datetime, timedelta

secret_key = os.getenv("JWT_SECRET")
algorithm = os.getenv("JWT_ALGORITHM")
expires = os.getenv("JWT_LIFETIME")

def create_access_token(data: dict):
    payload = data.copy()
    expires_in = datetime.now() + timedelta(minutes=int(expires))
    payload.update({"exp": expires_in})
    token = jwt.encode(payload, secret_key, algorithm)
    return token