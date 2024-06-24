from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..database import SessionLocal, get_db
from ..models import User
from typing import Annotated, List
from datetime import datetime
from passlib.context import CryptContext

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

#Classes
class CreateUser(BaseModel):
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

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponseUser)
async def create_user(user: CreateUser, db: db_dependency):
    old_user_email = db.query(User).filter(User.email == user.email).first()
    if old_user_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User with email: {user.email} already exists")
    
    old_user_username = db.query(User).filter(User.username == user.username).first()
    if old_user_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Username already taken")
    
    hashed_password = password_context.hash(user.password)
    user.password = hashed_password
    
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=ResponseUser)
async def get_user(id: int, db: db_dependency):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} was not found")
    return user