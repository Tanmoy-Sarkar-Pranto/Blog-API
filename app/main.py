from fastapi import FastAPI
from httpcore import Origin
from . import models
from .database import engine
from .routers import posts, users, auth, votes

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["https://www.google.com", "http://127.0.0.1:3000", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(votes.router)