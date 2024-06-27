from fastapi import FastAPI
from httpcore import Origin
from . import models
from .database import engine
from .routers import posts, users, auth, votes
from fastapi.responses import RedirectResponse

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
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

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")