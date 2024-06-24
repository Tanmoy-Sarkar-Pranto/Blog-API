from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import SessionLocal, get_db
from ..models import Post
from typing import Annotated, List
from datetime import datetime

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

    created_at: datetime
    class Config:
        from_attributes = True

# <-------------------------------Classes Finished------------------------------>

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[ResponsePost])
async def get_posts(db: db_dependency):
    posts = db.query(Post).all()
    return posts

@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=ResponsePost)
async def get_post(id: int, db: db_dependency):
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} was not found")
    return post

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponsePost)
async def create_post(post: CreatePost, db: db_dependency):
    new_post = Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: db_dependency):
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} was not found")
    db.delete(post)
    db.commit()
    

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ResponsePost)
async def update_post(id: int, post: UpdatePost, db: db_dependency):
    post_query = db.query(Post).filter(Post.id == id)
    updated_post = post_query.first()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} was not found")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()