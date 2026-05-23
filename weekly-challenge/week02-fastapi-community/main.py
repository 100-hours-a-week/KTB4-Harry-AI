from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session


import httpx

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"  # OLLAMA 서버 URL
OLLAMA_MODEL = "gemma4:e2b"  # 사용할 OLLAMA 모델 이름

# 인메모리 -> 데이터베이스로 전환하기 위한 SQLAlchemy 설정
engine = create_engine("sqlite:///./posts.db", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# sqlalchemy 모델 정의
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    post_date = Column(DateTime, nullable=False)
    summary = Column(Text, nullable=True)
    

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# db 연결을 위한 의존성 주입 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 게시글 생성 요청 모델
class PostBase(BaseModel):
    title: str
    content: str
    
    # 서버가 만들어야 하는 값이다.
    # postDate: str = datetime.now().strftime("%Y-%m-%d %H:%M")

# 게시글 응답 모델
# class SummaryRequest(PostBase):
#     pass


# AI 요약 응답 모델
class SummaryResponse(BaseModel):
    summary: str = ""  # AI 요약 결과를 저장해야하는 필드


# 메인 페이지 확인 - 서버 초기 구동 확인용
@app.get("/")
def read_root():
    return {"message": "커뮤니티 게시판 API 메인 페이지."}


# 게시글 생성
@app.post("/posts")
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
@app.get("/posts")
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
@app.get("/posts/{post_id}") 
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
@app.put("/posts/{post_id}") 
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
@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)) -> dict:
    post = db.query(Post).filter(Post.id == post_id).first()
    
    # 예외처리
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    db.delete(post) # delete()는 세션에서 객체를 삭제하는 메서드
    db.commit()

    return {"message": "게시물이 성공적으로 삭제되었습니다."}


# ------------ AI 요약 기능 연결 ------------


# AI 요약 생성 요청 및 요약문 반환 - 게시글 상세 조회보다 아래에 두기(경로 설정)
@app.post("/posts/{post_id}/summary", response_model=SummaryResponse)
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


'''
서버 내부에서 LLM 요청만 담당하는 helper 함수

httpx 비동기 HTTP 클라이언트 라이브러리를 사용해서
실제 LLM API에 요청을 보내는 형태로 구현
'''
async def request_ai_summary(title: str, content: str) -> str:
    # """ 안 들여쓰기 너무 많아서 깔끔하게 정리하는게 좋다는 피드백
    prompt = f"""
                "다음 게시글을 2~3문장으로 요약해줘.\n\n"
                f"제목: {title}\n\n"
                f"내용:\n{content}"
            """
    
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                # system - 모델의 전체 역할, 태도, 규칙을 정함
                "role": "system",
                "content": "너는 커뮤니티 게시글을 간결하게 요약하는 한국어 AI 도우미야. 답변은 최대한 간결하게 해.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        # 스트리밍
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()  # 요청 실패 시 예외 발생

            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    # AI 요약 호출 관련 예외처리
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI 요약 요청 시간이 초과되었습니다.")

    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="AI 모델 서버 응답에 실패했습니다.")

    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="AI 모델 서버에 연결할 수 없습니다.")



# AI 요약 조회 - 게시글 상세 조회보다 아래에 두기(경로 설정)
@app.get("/posts/{post_id}/summary", response_model=SummaryResponse)
async def summarize_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()

    # 예외처리
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 예외처리
    if post.summary is None:
        raise HTTPException(status_code=404, detail="아직 생성된 요약문이 없습니다.")
    
    return {"summary": f"게시글의 요약된 내용: {post.summary}"}

