from jose import jwt, JWTError
import dotenv
import os
from datetime import datetime, timedelta
from app.routers import auth
from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from . import database, models
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

secret_key = os.getenv("JWT_SECRET")
algorithm = os.getenv("JWT_ALGORITHM")
expires = os.getenv("JWT_LIFETIME")

def create_access_token(data: dict):
    payload = data.copy()
    expires_in = datetime.utcnow() + timedelta(seconds=int(expires))
    payload.update({"exp": expires_in})
    token = jwt.encode(payload, secret_key, algorithm)
    return token

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id = payload.get("user_id")
        username = payload.get("username")
        # print(user_id, username)
        # if not user_id or not username:
        #     raise credentials_exception
        token_data = auth.PayloadToken(user_id=user_id, username=username)
        return token_data
    except JWTError:
        raise credentials_exception

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    jwt_token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == jwt_token.user_id).first()
    # print(user)
    return user