from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# RDBMS 사용 전 인메모리 저장소
posts_db = []


# 게시글 생성 요청 모델
class PostCreate(BaseModel):
    title: str
    content: str
    
    # 서버가 만들어야 하는 값인지 ?
    postDate: str = datetime.now().strftime("%Y-%m-%d %H:%M")


# 메인 페이지 확인 - 서버 확인용 ?
@app.get("/")
def read_root():
    return {"message": "커뮤니티 게시판 API 메인 페이지."}


# 게시글 생성
@app.post("/posts")
def create_post(post: PostCreate):
    new_post = {
        "title": post.title,
        "content": post.content,
        "postDate": post.postDate
    }
    
    posts_db.append(new_post)

    return {"message": "게시물이 성공적으로 등록되었습니다.", "post": new_post}


# 게시글 목록 조회 - 상세 조회보다 위에 두기(경로 설정)
@app.get("/posts")
def read_post_list():
    return posts_db


# 게시글 조회
@app.get("/posts/{post_id}")
def read_post(post_id: int):
    return posts_db[post_id]


# 게시글 수정
@app.put("/posts/{post_id}")
def update_post(post_id: int, updated_post: PostCreate):
    posts_db[post_id] = {
        "title": updated_post.title,
        "content": updated_post.content,
        "postDate": updated_post.postDate
    }
    return {"message": "게시글이 성공적으로 수정되었습니다.", "post": posts_db[post_id]}


# 게시글 삭제
@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    del posts_db[post_id]
    return {"message": "게시물이 성공적으로 삭제되었습니다."}
