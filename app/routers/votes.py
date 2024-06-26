from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from ..database import SessionLocal, get_db
from ..models import Post, Vote, User
from typing import Annotated, List, Optional
from datetime import datetime
from app import oauth2
from .auth import ResponseUser

router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)

#Classes
class VoteCreate(BaseModel):
    post_id: int
    direction: int = Field(ge=0, le=1) # 0 = dislike, 1 = like
    
# <-------------------------------Classes Finished------------------------------>

# Dependencies
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(oauth2.get_current_user)]
# <-------------------------------Dependencies Finished------------------------------>

@router.post("/", status_code=status.HTTP_201_CREATED)
async def vote(vote: VoteCreate, db: db_dependency, user: user_dependency):
    # Checking if post exists
    post = db.query(Post).filter(Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {vote.post_id} was not found")
    
    # Checking if user exists
    valid_user = db.query(User).filter(User.id == user.id).first()
    if not valid_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {user.id} was not found")
    
    
    vote_query = db.query(Vote).filter(Vote.post_id == vote.post_id).filter(Vote.user_id == user.id)
    found_vote = vote_query.first()
    if vote.direction == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User {user.id} has already Liked on post {vote.post_id}")
        new_vote = Vote(user_id=user.id, post_id=vote.post_id)
        db.add(new_vote)
        db.commit()
        return {"message": "Like added successfully"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Like does not exist for post {vote.post_id} and user {user.id}.")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Like removed successfully"}