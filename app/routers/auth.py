import logging
from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from app.database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from app.models import User
from passlib.context import CryptContext
from datetime import datetime
from app import oauth2

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db_dependency = Annotated[Session, Depends(get_db)]

# Just to silance the error omitted by bcrypt in passlib about version. it doesn't break anything so no need to worry.
logging.getLogger('passlib').setLevel(logging.ERROR)

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)

# Classes
class LoginUser(BaseModel):
    email: EmailStr
    password: str

class RegisterUser(BaseModel):
    email: EmailStr
    username: str
    password: str

class ResponseUser(BaseModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class PayloadToken(BaseModel):
    user_id: int
    username: str
# Functions

@router.post('/login', status_code=status.HTTP_200_OK, response_model=Token)
async def login(db: db_dependency,user: OAuth2PasswordRequestForm = Depends()):
    registered_user = db.query(User).filter(User.username == user.username).first()
    if not registered_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Credentials")
    
    #Check password
    is_same_password = password_context.verify(user.password, registered_user.password)
    if not is_same_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    
    token = oauth2.create_access_token(data={"user_id": registered_user.id, "username": registered_user.username})
    return {'access_token': token,'token_type':'bearer'}