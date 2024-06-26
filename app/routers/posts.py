from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session
from ..database import SessionLocal, get_db
from ..models import Post, Vote
from typing import Annotated, List, Optional
from datetime import datetime
from app import oauth2
from .auth import ResponseUser

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)
#Classes
class BasePost(BaseModel):
    title: str
    content: str
    published: bool = True

class CreatePost(BasePost):
    pass

class UpdatePost(BasePost):
    pass

class ResponsePost(BasePost):
    id: int
    created_at: datetime
    owner_id: int
    owner: ResponseUser
    class Config:
        from_attributes = True

class VoteResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    owner_id: int
    likes_count: int

    class Config:
        from_attributes = True
# <-------------------------------Classes Finished------------------------------>

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(oauth2.get_current_user)]

@router.get("/all_posts", status_code=status.HTTP_200_OK , response_model=List[VoteResponse])
async def get_all_posts(db: db_dependency, user: user_dependency, limit: int = 10, skip: int=0, search: Optional[str]=""):
    # print(user.username, user.email)
    
    result = db.query(
        Post,
        func.count(Vote.post_id).label("votes")
    ).join(
        Vote, Vote.post_id == Post.id, isouter=True
    ).filter(
        Post.title.contains(search)
    ).group_by(
        Post.id
    ).order_by(
        desc("votes")
    ).limit(
        limit
    ).offset(
        skip
    )
    # print(result)
    response = []
    for post, likes_count in result:
        response.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "owner_id": post.owner_id,
            "likes_count": likes_count
        })
    
    return response
    # return result

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[VoteResponse])
async def get_own_posts(db: db_dependency, user: user_dependency, limit: int = 10, skip: int=0, search: Optional[str]=""):
    # print(user.username, user.email)
    result = db.query(
        Post,
        func.count(Vote.post_id).label("votes")
    ).join(
        Vote, Vote.post_id == Post.id, isouter=True
    ).filter(
        Post.owner_id == user.id
    ).filter(
        Post.title.contains(search)
    ).group_by(
        Post.id
    ).order_by(
        desc("votes")
    ).limit(
        limit
    ).offset(
        skip
    )
    response = []
    for post, likes_count in result:
        response.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "owner_id": post.owner_id,
            "likes_count": likes_count
        })
    
    return response

@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=VoteResponse)
async def get_post(id: int, db: db_dependency, user: user_dependency):
    post = db.query(
        Post,
        func.count(Vote.post_id).label("votes")
    ).join(
        Vote, Vote.post_id == Post.id, isouter=True
    ).filter(
        Post.owner_id == user.id
    ).filter(Post.id == id).group_by(
        Post.id
    ).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} was not found")
    response = {
        "id": post[0].id,
        "title": post[0].title,
        "content": post[0].content,
        "created_at": post[0].created_at,
        "owner_id": post[0].owner_id,
        "likes_count": post[1]
    }
    
    return response

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponsePost)
async def create_post(post: CreatePost, db: db_dependency, user: user_dependency):
    current_user_id = user.id
    new_post = Post(**post.model_dump())
    new_post.owner_id = current_user_id
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: db_dependency, user: user_dependency):
    post = db.query(Post).filter(Post.id == id).filter(Post.owner_id == user.id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} was not found")
    db.delete(post)
    db.commit()
    

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ResponsePost)
async def update_post(id: int, post: UpdatePost, db: db_dependency, user: user_dependency):
    post_query = db.query(Post).filter(Post.id == id).filter(Post.owner_id == user.id)
    updated_post = post_query.first()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} was not found")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()