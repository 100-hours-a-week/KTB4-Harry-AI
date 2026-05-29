from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from models.post import Post
from schemas.post import PostBase, SummaryResponse
from services.ai_summary_service import request_ai_summary, stream_ai_summary
from fastapi.responses import StreamingResponse

router = APIRouter()


# 게시글 생성
@router.post("/posts")
def create_post(post: PostBase, db: Session = Depends(get_db)) -> dict:
    new_post = Post(
        title=post.title,
        content=post.content,
        post_date=datetime.now()
    )

    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # 새로 생성된 게시글의 ID 등 자동 생성 값을 가져오기 위해 새로고침

    return {
        "message": "게시물이 성공적으로 등록되었습니다.",
        "post": {
            "id": new_post.id,
            "title": new_post.title,
            "content": new_post.content,
            "postDate": new_post.post_date.strftime("%Y-%m-%d %H:%M"),
            "summary": new_post.summary
        }
    }


# 게시글 목록 조회 - 상세 조회보다 위에 두기(경로 설정)
@router.get("/posts")
def read_post_list(db: Session = Depends(get_db)) -> list:
    posts = db.query(Post).all()
    
    return [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "postDate": post.post_date.strftime("%Y-%m-%d %H:%M"),
            "summary": post.summary
        }
        for post in posts
    ]


# 게시글 하나 조회
@router.get("/posts/{post_id}") 
def read_post(post_id: int, db: Session = Depends(get_db)) -> dict:
    post = db.query(Post).filter(Post.id == post_id).first()
    
    # 예외처리
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    return {
        "id": post_id,
        "title": post.title,
        "content": post.content,
        "postDate": post.post_date.strftime("%Y-%m-%d %H:%M"),
        "summary": post.summary
    }


# 게시글 수정
# 메세지 dict로 수정된거 알려야 하는가 ?
@router.put("/posts/{post_id}") 
async def update_post(post_id: int, updated_post: PostBase
                ,db: Session = Depends(get_db)) -> dict:
    
    post = db.query(Post).filter(Post.id == post_id).first()

    # 예외처리
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    post.title = updated_post.title
    post.content = updated_post.content
    post.post_date = datetime.now()  # 수정 시점으로 날짜 업데이트
    
    # 수정된 본문 기준으로 요약문 재생성
    post.summary = await request_ai_summary(post.title, post.content)

    db.commit()
    db.refresh(post)  # 수정된 게시글 데이터 반영하도록

    return {
        "message": "게시글이 성공적으로 수정되었습니다.",
        "post": {
            "id": post_id,
            "title": post.title,
            "content": post.content,
            "postDate": post.post_date.strftime("%Y-%m-%d %H:%M"),
            "summary": post.summary
        }
    }


# 게시글 삭제
# 메세지 dict로 삭제된거 알려야 하는가 ?
@router.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)) -> dict:
    post = db.query(Post).filter(Post.id == post_id).first()
    
    # 예외처리
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    db.delete(post) # delete()는 세션에서 객체를 삭제하는 메서드
    db.commit()

    return {"message": "게시물이 성공적으로 삭제되었습니다."}


# ------------ AI 요약 기능 연결 ------------


# AI 요약 생성 요청 및 요약문 반환
@router.post("/posts/{post_id}/summary", response_model=SummaryResponse)
async def generate_summary(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()

    # 예외처리
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # request_ai_summary에서 비동기 http 요청을 보내므로 await 키워드 사용
    summary = await request_ai_summary(post.title, post.content) # 여기가 이벤트 루프에서 블로킹되지 않도록 비동기 함수로 구현되어야 함
    post.summary = summary  # 게시글 데이터에 요약 결과 저장

    db.commit()  # 변경사항 데이터베이스에 반영
    db.refresh(post)  # 변경된 게시글 데이터 반영하도록 새로고침

    # summary[:100] 슬라이싱 나중에 
    return {"summary": post.summary}


# AI 요약 조회
@router.get("/posts/{post_id}/summary", response_model=SummaryResponse)
async def summarize_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()

    # 예외처리
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 예외처리
    if post.summary is None:
        raise HTTPException(status_code=404, detail="아직 생성된 요약문이 없습니다.")
    
    return {"summary": f"게시글의 요약된 내용: {post.summary}"}


# AI 요약 스트리밍 요청 및 생성문 반환
@router.post("/posts/{post_id}/summary/stream")
async def generate_stream_summary(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()

    # 예외처리
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    return StreamingResponse(
        stream_ai_summary(post.title, post.content),
        media_type="text/event-stream"
    )
