from fastapi import FastAPI

from api.routes.posts import router as posts_router
from database.base import Base
from database.session import engine
from models.post import Post

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(posts_router)


@app.get("/")
def read_root():
    return {"message": "커뮤니티 게시판 API 메인 페이지."}